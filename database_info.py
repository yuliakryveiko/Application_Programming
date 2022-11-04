# Change `sqlalchemy.url` manually in alembic.ini
dbuser = 'postgres'
dbpass = '1'
dbhost = '127.0.0.1'
dbport = '5432'
dbname = 'money_api'
DB_URL = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(dbuser, dbpass, dbhost, dbport, dbname)