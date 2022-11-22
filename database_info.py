# Change `sqlalchemy.url` manually in alembic.ini
dbuser = 'root'
dbpass = '1'
dbhost = 'localhost'
dbport = '3306'
dbname = 'money_transfer'
DB_URL = "mysql+pymysql://{}:{}@{}:{}/{}".format(dbuser, dbpass, dbhost, dbport, dbname)