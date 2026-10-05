#CREATE YOUR .env containing your database_url, database_password, database_user and database_name
#IMPORT THE NECESSSARY LIBRARIES(os && dotenv - to get and use the env, create_engine from sqlalchemy)

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)