import os
from SMAR import create_app
from models import * 
from utils import get_logger
from dotenv import load_dotenv

load_dotenv('.flaskenv')

logger = get_logger('SMAR')
app = create_app()



@app.route('/test')
def test_api():
    logger.info('Test API is checked!')
    return {'message': "APIs started successfully!"}, 200

if __name__ == "__main__":
    app.run(host=os.environ["HOST"], port=os.environ["PORT"])  