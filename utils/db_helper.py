import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def get_engine():
    engine = create_engine(f"mssql+pymssql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_INSTANCE']}")
    return engine