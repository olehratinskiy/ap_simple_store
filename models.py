import os

from sqlalchemy import (
 Column,
 Integer,
 ForeignKey,
 String,
 Enum,
BLOB
)


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
import sys

DB_URI = os.getenv("DB_URI", "mysql://root:A2452756b@127.0.0.1:3306/store")

engine = create_engine(DB_URI)
SessionFactory = sessionmaker(bind=engine)

Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    username = Column(String(45), nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    password = Column(String(2000), nullable=False)


class Img(BaseModel):
    __tablename__ = "img"
    id = Column(Integer, primary_key=True)
    img = Column(BLOB(5000), nullable=False, unique=True)
    name = Column(String(400), nullable=False)
    mimetype = Column(String(400), nullable=False)


class Item(BaseModel):
    __tablename__ = "item"
    item_id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    storage_quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(Enum("sold out", "available"))
    img_id = Column(Integer, ForeignKey('img.id'))
    img = relationship("Img", backref=backref("item", uselist=False))


class Orders(BaseModel):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    user = relationship("User", backref=backref("orders", uselist=False))
    item_id = Column(Integer, ForeignKey('item.item_id'))
    item = relationship("Item", backref=backref("orders", uselist=False))
    item_quantity = Column(Integer, nullable=False)
    price = Column(Integer)





# mysql -u root -p"Yy357131517!" --host localhost --port 3306 simplestore < create_tables.sql

# alembic revision -m "add models" --autogenerate
# alembic upgrade head
