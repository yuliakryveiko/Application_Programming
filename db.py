from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = 'temp_init_holder'

def db_init():
    global db
    connection_string = 'mysql+pymysql://root:1111@localhost:3306/money_transfer'
    engine = create_engine(connection_string, echo=True)
    Session = sessionmaker(bind=engine, autoflush=False)
    db = Session()

def get_db():
    return db
