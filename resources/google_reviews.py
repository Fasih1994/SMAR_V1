from flask.views import MethodView
import os
import requests
from flask_smorest import Blueprint, abort
from utils import get_logger
from schemas import GoooglePlaceDataSchema, GoooglePlaceIdSchema

blp = Blueprint("Google", "google", description="Google reviews for places")

logger = get_logger('SMAR')

HEADERS = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': os.environ.get("GOOGLE_API_KEY"),
    'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress'
}
GOOGLE_PLACE_ID_URL = 'https://places.googleapis.com/v1/places:searchText'
GOOGLE_PLACE_DATA_URL = 'https://maps.googleapis.com/maps/api/place/details/json'


@blp.route("/keyterm/google/place-id")
class GooglePlaces(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(GoooglePlaceDataSchema)
    @blp.response(200, None)
    def post(self, term_data):
        text = term_data['text']
        post_data = {
            "textQuery" : text
        }

        try:
            res = requests.post(
                url=GOOGLE_PLACE_ID_URL,
                headers=HEADERS,
                json=post_data
            )
            print(res.json())
            if res.status_code != 200:
                raise ValueError
        except ValueError as e:
            logger.error(e)
            abort(500, message="An error occurred on Backend.")

        return res.json()

@blp.route("/keyterm/google/place-data")
class GooglePlaces(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(GoooglePlaceIdSchema,location='query')
    @blp.response(200, None)
    def get(self, term_data):
        _id = term_data['id']
        params = {
            'place_id': _id,
            'fields': 'name,rating,formatted_phone_number,reviews',
            'key': os.environ.get("GOOGLE_API_KEY")
        }

        try:
            res = requests.get(
                url=GOOGLE_PLACE_DATA_URL,
                params=params
            )
            # print(res.json())
            if res.status_code != 200:
                raise ValueError
        except ValueError as e:
            print(e)
            logger.error(e)
            abort(500, message="An error occurred on Backend.")

        return res.json()