# Note: TODO - rewrite for catalog item
# I had to add restaurant_id as python compiler come back with an error 
# MenuItem does not have prop restaurant. prop restaurant had to be changed to restaurant_id
# to compile and work properly.
# Otherwise Works OK

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from catalog_db_setup import Base, User, UserItem, CatalogItem
 
engine = create_engine('sqlite:///thecatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# User 1
user01 = User(name = "User01 Mock", email = "user01@email.com", avatar = "../img/img_avatar.png")
session.add(user01)

# User 2
user02 = User(name = "User02 Mock", email = "user02@email.com", avatar = "../img/avatar6.png")
session.add(user02)
session.commit()

#CatalogItem 1
catalogItem01 = CatalogItem(title = "Street Shops", userId = user01.userId)
session.add(catalogItem01)

# CatalogItem 2
catalogItem02 = CatalogItem(title = "Coders...", userId = user02.userId)
session.add(catalogItem02)
session.commit()

# UserItem1

# UserItem2
menuItem2 = MenuItem(name = "Veggie Burger", description = "Juicy grilled veggie patty with tomato mayo and lettuce", price = "$7.50", course = "Entree", restaurant_id = restaurant1.id)

session.add(menuItem2)
session.commit()


menuItem1 = MenuItem(name = "French Fries", description = "with garlic and parmesan", price = "$2.99", course = "Appetizer", restaurant_id = restaurant1.id)

session.add(menuItem1)
session.commit()


