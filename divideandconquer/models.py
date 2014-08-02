from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    uid = Column(String, primary_key=True)
    name = Column(String)
    password = Column(String)
    salt = Column(String)

class Response(Base):
    __tablename__ = "responses"
    # is_spam is a trinary value
    # 1 is true
    # 2 is false
    # 3 is unknown
    is_spam = Column(Integer)
    json_hash = Column(String, primary_key=True)
    json = Column(String)
    classified_by = Column(ForeignKey('users.uid'))

# this is probably a bad idea...
class JobQueue(Base):
    __tablename__ = "jobqueue"
    json_hash = Column(String, primary_key=True)
    priority = Column(Integer)
