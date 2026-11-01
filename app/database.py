# CREATE YOUR .env containing your database_url, database_password, database_user and database_name
# IMPORT THE NECESSSARY LIBRARIES(os && dotenv - to get and use the env, create_engine from sqlalchemy)

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)  # pyright:ignore

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
