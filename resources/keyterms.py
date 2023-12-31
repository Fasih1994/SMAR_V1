from flask.views import MethodView
import json
from flask_smorest import Blueprint, abort
from utils import get_terms_openai, get_logger
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from models import KeyTermGenModel, KeyTermSelectModel
from schemas import KeytermGenSchema, KeytermGetDataSchema, KeytermDataFromTable, KeytermSelectSchema

from data365 import get_twitter_posts, get_twitter_comments, get_twitter_data_from_db


blp = Blueprint("Keyterms", "keyterms", description="Operations on Keyterms",
                url_prefix='/api/flask/')

logger = get_logger('SMAR')

@blp.route("/keyterm/generate")
class Keyterm(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(KeytermGenSchema)
    @blp.response(201, KeytermGenSchema)
    def post(self, term_data):
        text = term_data['text']
        # terms = KeyTermGenModel.find_by_text(text)
        # if terms:
        #     return terms.json()

        key_terms = get_terms_openai(text=text.upper())
        if 'Incorrect API key provided:' in key_terms:
            abort(500, message=key_terms)
        terms = KeyTermGenModel(**term_data, keyterms=key_terms)

        try:
            terms.save_to_db()
        except SQLAlchemyError as e:
            logger.error(e)
            abort(500, message="An error occurred while inserting the item.")

        return terms.json()

@blp.route("/keyterm/save")
class Keyterm(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(KeytermSelectSchema)
    @blp.response(201, None)
    def post(self, term_data):
        terms = '--|--'.join(term_data['terms'])
        terms = KeyTermSelectModel(text='manual select', keyterms=terms)

        try:
            terms.save_to_db()
        except SQLAlchemyError as e:
            logger.error(e)
            abort(500, message="An error occurred while inserting the item.")

        return {"message": "terms saved successfully"}

@blp.route("/keyterm/all")
class Keyterm(MethodView):
    # @jwt_required(fresh=True)
    @blp.response(200, None)
    def get(self):
        terms = []

        try:

            key_terms = KeyTermGenModel.find_all()
            key_terms = [term.json() for term in key_terms]
            key_terms = sorted(key_terms, key=lambda x:x['id'], reverse=True)
            for term in key_terms:
                terms.extend(term['terms'])
            return {'terms': list(set(terms))[:15]}

        except OperationalError as e:
            logger.error(e)
            abort(500, message=str(e))

        except SQLAlchemyError as e:
            logger.error(e)
            abort(500, message="An error occurred accessing the database.")


@blp.route("/keyterm/get_data/twitter")
class KeytermGetData(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(KeytermGetDataSchema)
    @blp.response(201, None)
    def post(self, term_data):
        try:
            platform = term_data.pop('platform')
            if platform != 'twitter':
                return {"message": "Twitter not selected !"}

            terms = term_data.pop('terms')
            term_str = '--|--'.join(terms)
            model = KeyTermSelectModel(text=term_data['text'], keyterms=term_str)
            model.save_to_db()
            for term in terms:
                term = term.lower()
                path = get_twitter_posts(key_word=term, **term_data)

                if path == "":
                    return {'message': "Data not present against these terms!"}, 200
                logger.info(f"New Path is {path}")
                get_twitter_comments(path=path, key_word=term)


            return {'message': "Data extracted successfully!"}

        except SQLAlchemyError as e:
            logger.error(str(e))
            abort(500, message="An error occurred while inserting the item.")
        except Exception as e:
            logger.error(str(e))
            abort(500, message="An error occurred!")

@blp.route("/keyterm/data/twitter")
class KeytermGetData(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(KeytermDataFromTable)
    @blp.response(200, None)
    def post(self, args):
        try:
            terms = args.pop('terms')
            if terms == []:
                raise ValueError("Terms are empty array")
            terms = [term.lower() for term in terms]
            posts = get_twitter_data_from_db(terms, table='posts', **args)
            comments = get_twitter_data_from_db(terms, table='comments', **args)
            return {
                'data': {
                    "posts": posts.to_dict(orient='records',) if not posts.empty else 'Data not available',
                    "comments": comments.to_dict(orient='records') if not comments.empty else 'Data not available'
                }
                }

        except SQLAlchemyError as e:
            logger.error(e)
            abort(500, message="An error occurred while Getting data from SQL server.")

        except ValueError as e:
            abort(400, message="terms must be an array of keyterms not empty or []")

        except Exception as e:
            logger.error(e)
            abort(500, message="backend code messed up")