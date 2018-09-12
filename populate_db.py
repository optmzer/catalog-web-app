# Note: TODO - rewrite for catalog item
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
user01 = User(name = "User01 Mock", email = "user01@email.com", avatar = "/static/img/img_avatar.png")
session.add(user01)
session.commit()

# User 2
user02 = User(name = "User02 Mock", email = "user02@email.com", avatar = "/static/img/avatar6.png")
session.add(user02)
session.commit()

#CatalogItem 1
catalogItem01 = CatalogItem(title = "Street Shops", user_id = user01.id)
session.add(catalogItem01)
session.commit()

# CatalogItem 2
catalogItem02 = CatalogItem(title = "Coders...", user_id = user02.id)
session.add(catalogItem02)
session.commit()

# UserItem1
userItem1 = UserItem(title = "Shopping in Middle East", description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", item_picture= "../img/pexel-photo-160107.jpeg", catalog_item_id = catalogItem01.id, user_id = user01.id)
session.add(userItem1)
session.commit()

# UserItem2
userItem2 = UserItem(title = "Coders Life Before and After", description = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum." , item_picture= "../img/pexel-photo-1394841.jpeg", catalog_item_id = catalogItem02.id, user_id = user02.id)
session.add(userItem2)
session.commit()
