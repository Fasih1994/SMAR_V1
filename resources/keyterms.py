from flask.views import MethodView
from flask_smorest import Blueprint, abort
from utils import get_terms_openai, get_logger
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from models import KeyTermGenModel, KeyTermSelectModel
from schemas import KeytermGenSchema, KeytermGetDataSchema, KeytermDataFromTable, KeytermSelectSchema

from data365 import get_twitter_posts, get_twitter_comments, get_twitter_data_from_db


blp = Blueprint("Keyterms", "keyterms", description="Operations on Keyterms")

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

            key_terms = KeyTermSelectModel.find_all()
            for term in key_terms:
                terms.extend(term.json()['terms'])
                
            key_terms = KeyTermGenModel.find_all()
            for term in key_terms:
                terms.extend(term.json()['terms'])
            return {'terms': list(set(terms))}

        except SQLAlchemyError as e:
            logger.error(e)
            abort(500, message="An error occurred while inserting the item.")

@blp.route("/keyterm/get_data/twitter")
class KeytermGetData(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(KeytermGetDataSchema)
    @blp.response(201, None)
    def post(self, term_data):
        try:
            platform = term_data['platform']
            if platform != 'twitter':
                return {"message": "Twitter not selected !"}

            terms = term_data.pop('terms')
            term_str = '--|--'.join(terms)
            model = KeyTermSelectModel(text=term_data['text'], keyterms=term_str)
            model.save_to_db()
            for term in terms:
                path = get_twitter_posts(term)
                get_twitter_comments(path=path, key_word=term)

            
            return {'message': "Data extracted successfully!"}
            
        except SQLAlchemyError as e:
            logger.error(e)
            abort(500, message="An error occurred while inserting the item.")
        except Exception as e:
            logger.error(e)
            abort(500, message="An error occurred while inserting the item.")

@blp.route("/keyterm/data/twitter")
class KeytermGetData(MethodView):
    # @jwt_required(fresh=True)
    @blp.arguments(KeytermDataFromTable)#, location='query')
    @blp.response(201, None)
    def get(self, args):
        try:
            
            terms = args['terms']
            posts = get_twitter_data_from_db(terms, table='posts')
            comments = get_twitter_data_from_db(terms, table='comments')
            return {
                'data': {
                    "posts": posts.to_dict(orient='records'),
                    "comments": comments.to_dict(orient='records') 
                }
                }
            
        except SQLAlchemyError as e:
            logger.error(e)
            abort(500, message="An error occurred while Getting data from SQL server.")
        except Exception as e:
            logger.error(e)
            abort(500, message="backend code messed up")