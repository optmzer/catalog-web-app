#!/usr/bin/env python3
import sys
from sqlalchemy import Column, ForeignKey, Integer, String 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Because I use Vagrant from Udacity SQLAlchemy is 
# already installed on Virtual Machine(VM)
# Base is a declarative Data Base
Base = declarative_base()

########
class User(Base):
    __tablename__ = 'user'
    # Mapper
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    avatar = Column(String(250))


########
class CatalogItem(Base):
    __tablename__ = 'catalog_item'
    # Mapper
    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    # user_id is a foreign key
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title
        }


########
class UserItem(Base):
    __tablename__ = 'user_item'
    # Mapper
    user_item_id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250))
    item_picture = Column(String(250))
    # catalog_item_id is a foreign key
    catalog_item_id = Column(Integer, ForeignKey('catalog_item.id'))
    catalog_item = relationship(CatalogItem)
    # user_id is a foreign key
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'description': self.description,
            'user_item_id': self.user_item_id,
            'item_picture': self.item_picture
        }


########## Insert at the end of the file ##########
engine = create_engine('sqlite:///thecatalog.db')

# Adds classes as new tables in our DB
Base.metadata.create_all(engine)
