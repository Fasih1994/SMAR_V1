import os
import requests
from typing import Dict
from pprint import pprint

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError

from utils import get_logger
from models import Place, Review
from schemas import GoooglePlaceDataSchema, GoooglePlaceIdSchema, ApiResponseSchema
from db import db

blp = Blueprint("Google", "google", description="Google reviews for places",
                url_prefix='/api/flask/')

logger = get_logger('SMAR')

HEADERS = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': os.environ.get("GOOGLE_API_KEY"),
    'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.types'
}
GOOGLE_PLACE_ID_URL = 'https://places.googleapis.com/v1/places:searchText'
GOOGLE_PLACE_DATA_URL = 'https://maps.googleapis.com/maps/api/place/details/json'


def save_places(
    places_data: Dict = None,
    place_id: str = None,
    category: str = None) -> Place:
    # print(places_data.keys())
    place_data = places_data['result']
    reviews_data = place_data.get('reviews')
    category = category if category else place_data.get('types',[None])[0]
    plus_code = place_data.get('plus_code')
    if plus_code:
        city = " ".join(place_data['plus_code']['compound_code'].split(' ')[1:])
    else:
        city = 'Unknown'

    new_place = Place(
        place_id=place_id,
        formatted_phone_number=place_data.get('formatted_phone_number'),
        name=place_data.get('name'),
        rating=place_data.get('rating'),
        lat=place_data['geometry']['location']['lat'],
        lng=place_data['geometry']['location']['lng'],
        category=category.capitalize(),
        city=city
    )
    new_place.save_to_db()
    if reviews_data:
        for review_data in reviews_data:
            new_review = Review(
                author_name=review_data.get('author_name'),
                rating=review_data.get('rating'),
                text=review_data.get('text'),
                time=review_data.get('time'),
                translated=review_data.get('translated'),
                profile_photo_url=review_data.get('profile_photo_url'),
                relative_time_description=review_data.get('relative_time_description'),
                author_url=review_data.get('author_url'),
                language=review_data.get('language'),
                original_language=review_data.get('original_language'),
                place=new_place
            )
            new_review.save_to_db()

    return new_place



@blp.route("/google/place-id")
class GooglePlaces(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(GoooglePlaceDataSchema)
    @blp.response(200, None)
    def post(self, term_data):
        text = term_data.pop('text')
        category = term_data.get('includedType')
        if category:
            category = category.lower()
            post_data = {
                "textQuery": text + f' {category}',
                "includedType": category
            }
        else:
           post_data = {
                "textQuery": text
            }

        try:
            res = requests.post(
                url=GOOGLE_PLACE_ID_URL,
                headers=HEADERS,
                json=post_data
            )
            # print(res.json())
            if res.status_code != 200:
                raise ValueError
        except ValueError as e:
            logger.error(e)
            abort(500, message="An error occurred on Backend.")

        return res.json()

@blp.route("/google/place-data")
class GooglePlaces(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(GoooglePlaceIdSchema,location='query')
    @blp.response(200, None)
    def get(self, term_data):
        _id = term_data['id']
        includedType = term_data.get('includedType')
        params = {
            'place_id': _id,
            'fields': 'name,rating,formatted_phone_number,reviews,geometry,types,plus_code',
            'key': os.environ.get("GOOGLE_API_KEY")
        }

        try:
            place = Place.find_by_id(place_id=_id)
            if place:
                place.delete_from_db()

            res = requests.get(
                url=GOOGLE_PLACE_DATA_URL,
                params=params
            )

            if res.status_code != 200:
                raise ValueError
            data = res.json()
            # pprint(data)
            place = save_places(data, place_id=_id, category=includedType)


        except ValueError as e:
            print(e)
            logger.error(e)
            abort(500, message="An error occurred on Backend.", error=str(e))

        return ApiResponseSchema().dump({'result': place, 'status': data['status']}), 200
