from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import sql
# import sqlalchemy
from database_info import DB_URL

engine = create_engine(DB_URL)
BaseModel = declarative_base()
metadata = BaseModel.metadata

SessionFactory = sessionmaker(bind=engine)
Session = SessionFactory()


class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    firstName = Column(String(30), nullable=False)
    lastName = Column(String(30), nullable=False)
    email = Column(String(254), nullable=False)
    password = Column(String(30), nullable=False)
    phone = Column(String(30))
    birthDate = Column(Date, nullable=False)
    wallet = Column(Float,nullable=False)
    userStatus = Column(Integer,nullable=False)

class Transaction(BaseModel):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    value = Column(Float, nullable=False)
    datePerformed = Column(DateTime,nullable=False)
    sentByUser = Column(Integer, ForeignKey('user.id'))
    sentToUser = Column(Integer, ForeignKey('user.id'))