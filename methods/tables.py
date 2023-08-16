import os.path

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Integer, String, \
    Column, DateTime, ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


path = '/home/bot/sqlite/'
if not os.path.exists(path):
    path = ''
engine = create_engine(f'sqlite:///{path}sqlite3.db')
connection = Session(bind=engine)


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    chat_id = Column(Integer, nullable=False, unique=True)
    first_name = Column(String(100), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user.pk'),
        UniqueConstraint('username')
    )


class Collocation(Base):
    __tablename__ = 'collocation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('user.chat_id'))
    collocation = Column(String(250), nullable=False)
    explanation = Column(String(300))
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    author = relationship("User")


Base.metadata.create_all(engine, checkfirst=True)

