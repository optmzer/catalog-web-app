#!/usr/bin/env python3
import sys
import datetime
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """Defines User table"""
    __tablename__ = 'user'
    # Mapper
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    avatar = Column(String(250))
    # If I delete user I do not need to cascade all their entries
    # catalog_item_id is a foreign key
    catalog_item = relationship('CatalogItem', backref="user")
    # user_item_id
    user_item = relationship('UserItem', backref="user")


class CatalogItem(Base):
    """Defines CatalogItem table"""
    __tablename__ = 'catalog_item'
    # Mapper
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    # user_item_id
    user_item = relationship('UserItem',
                             cascade="all,delete",
                             backref="catalog_item")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'created_date': self.created_date,
            'title': self.title
        }


class UserItem(Base):
    """Defines UserItem table"""
    __tablename__ = 'user_item'
    # Mapper
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    item_picture = Column(String(250))
    # catalog_item_id is a foreign key
    catalog_item_id = Column(Integer, ForeignKey('catalog_item.id'))
    # user_id is a foreign key
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'created_date': self.created_date,
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'item_picture': self.item_picture
        }


# Insert at the end of the file ##########
engine = create_engine('sqlite:///thecatalog.db')

# Adds classes as new tables in our DB
Base.metadata.create_all(engine)
