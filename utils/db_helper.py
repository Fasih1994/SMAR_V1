import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import types

load_dotenv()


def get_engine():
    engine = create_engine(f"mssql+pymssql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_INSTANCE']}")
    return engine

def sqlcol(dfparam):

    dtypedict = {}
    for i,j in zip(dfparam.columns, dfparam.dtypes):
        if "object" in str(j):
            dtypedict.update({i: types.NVARCHAR(length=255)})

        if "datetime" in str(j):
            dtypedict.update({i: types.DateTime()})

        if "float" in str(j):
            dtypedict.update({i: types.Float(precision=3, asdecimal=True)})

        if "int" in str(j):
            dtypedict.update({i: types.INT()})

    return dtypedict