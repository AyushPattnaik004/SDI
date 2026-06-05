

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


args = {
    "host": "db-campaign-analytics.postgres.database.azure.com",
    "port": 5432,
    "user": "devuser",
    "password": "Sentimentanalysis@123",
    "dbname": "bls"
}



_postgres_engine = create_engine('postgresql+psycopg2://', connect_args=args, pool_size=50)
BLS_DB = sessionmaker(bind=_postgres_engine)