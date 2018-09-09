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
class CatalogItem(Base):

    __tablename__ = 'catalogItem'

    # Mapper
    catalogItemId = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    # userId is a foreign key
    userId = Column(Integer, ForeignKey('user.userId'))
    userId = relationship(User)

########
class User(Base):

    __tablename__ = 'user'

    # Mapper
    userId = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    userPicture = Column(String(250))


########
class UserItem(Base):

    __tablename__ = 'user_item'

    # Mapper
    userItemId = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250))
    itemPicture = Column(String(250))

    # catalogItemId is a foreign key
    catalogItemId = Column(Integer, ForeignKey('catalogItem.id'))
    catalogItemId = relationship(CatalogItem)
    # userId is a foreign key
    userId = Column(Integer, ForeignKey('user.userId'))
    userId = relationship(User)

    @property
    def serialize(self):
        return {
            'title': self.title,
            'description': self.description,
            'userItemId': self.userItemId,
            'itemPicture': self.itemPicture
        }


########## Insert at the end of the file ##########
engine = create_engine('sqlite:///restaurantmenu.db')

# Adds classes as new tables in our DB
Base.metadata.create_all(engine)
