from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


connection_string = 'mysql://root:1111@127.0.0.1:3306/money_transfer'
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(bind=engine, autoflush=False)
db = Session()

connection_string_test = 'mysql://root:1111@127.0.0.1:3306/money_transfer_test'
engine = create_engine(connection_string_test, echo=False)
Session = sessionmaker(bind=engine, autoflush=False)
db_test = Session()

def get_db():
    return db_test

def get_db_test():
    return db_test