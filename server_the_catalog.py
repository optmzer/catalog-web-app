#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Imports DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

##### TODO Create DB classes and populate catalog
from catalog_db_setup import Base, User, UserItem, CatalogItem

################ Create Flask app ################

app = Flask(__name__)

################ Create Connection to DB ################
# init connection with DB
engine = create_engine('sqlite:///thecatalog.db?check_same_thread=False')

# Connection between class def and corresp table in DB
Base.metadata.bind = engine
# Create delete and other commands Alchemy does via an interface called a Session
DBSession = sessionmaker(bind=engine)

session = DBSession()

#### TODO Tester Methods Delete Before Submission ####

def showUserItemDetails(userItem):
    print("userItem.id = %d", userItem.id)
    print("userItem.created_date = %d", userItem.created_date)
    print("userItem.title = %d", userItem.title)
    print("userItem.description = %d", userItem.description)
    print("userItem.item_picture = %d", userItem.item_picture)
    print("userItem.catalog_item_id = %d", userItem.catalog_item_id)
    print("userItem.user_id = %d", userItem.user_id)


################ Getters/Setters ################

def getCatalogItemsAll():
    return session.query(CatalogItem).all()

def getCatalogItem(catalogItemId):
    """Returns a CatalogItem by its Id"""
    catalogItem = session.query(CatalogItem).filter_by(id = catalogItemId).one()
    # print("L28 CatalogItem = " + catalogItem.title + " ##########")
    return catalogItem

def getUserItems(catalogItemId):
    """Returns all UserItems for that CatalogItem by CatalogItem.id"""
    return session.query(UserItem).filter_by(catalog_item_id = catalogItemId).all()

def getUserItem(catalogItemId, userItemId):
    """Returns UserItem for a particular User Id and for a particular 
    CatalogItem Id"""
    catalogItem = getCatalogItem(catalogItemId)
    userItem = session.query(UserItem).filter_by(catalog_item_id = catalogItem.id, id = userItemId).one()
    # print("L33 userItem " + userItem.title)
    return userItem

def getUser(userId):
    """Returns a User by the Id"""
    user = session.query(User).filter_by(id = userId).one()
    # print("L49 User.id = %d Name: %s ##########" % (user.id, user.name))
    return user

########## Routs ################
########## CatalogItem ##########

# Show all catalog entry
@app.route('/')
@app.route('/thecatalog/')
def showCatalog():
    """Shows fromt page of the catalog"""
    return render_template('index.html', catalog = getCatalogItemsAll())

# Create new catalogItem
# TODO assign user id from the form
@app.route('/thecatalog/catalogitem/new/', methods=['GET', 'POST'])
def newCatalogItem():
    if request.method == 'POST':
        if request.form['catalogItemTitle']:
            catalogItem = CatalogItem(title = request.form['catalogItemTitle'], user_id = 1)
            session.add(catalogItem)
            session.commit()
            flash("CatalogItem: " + catalogItem.title + " added.")
            return redirect(url_for('showCatalog'))
    else:
        return render_template('newcatalogitem.html')

# Edit catalog item
@app.route('/thecatalog/<int:catalogItemId>/edit/', methods=['GET', 'POST'])
def editCatalogItem(catalogItemId):
    # TODO: Add redirect when successful
    catalogItem = getCatalogItem(catalogItemId)
    if request.method == 'POST':
        if request.form['catalogItemTitle']:
            catalogItem.title = request.form['catalogItemTitle']
            message = "New Catalog entry is " + request.form['catalogItemTitle']
            session.add(catalogItem)
            session.commit()
            flash(message)
            ## Redirect
            return redirect(url_for('showCatalog'))
    else:
        return render_template('editcatalogitem.html', catalogItem = catalogItem)


# Delete CatalogItem
@app.route('/thecatalog/<int:catalogItemId>/delete/', methods=['GET', 'POST'])
def deleteCatalogItem(catalogItemId):
    try:
        catalogItem = getCatalogItem(catalogItemId)
        if request.method == 'POST':
            if request.form['reset']:
                return redirect(url_for('showUserItemsInCatalog', catalogItemId=catalogItemId))

            session.delete(catalogItem)
            session.commit()
            flash("CatalogItem " + catalogItem.title + " was deleted")
            ## Redirect
            return redirect(url_for('showCatalog'))
        else:
            return render_template('deletecatalogitem.html', catalogItem = catalogItem)
    except :
        return redirect(url_for('pageNotFound'))


# Show UserItems in CatalogItem
@app.route('/thecatalog/<int:catalogItemId>/items/', methods=['GET', 'POST'])
def showUserItemsInCatalog(catalogItemId):
    """Shows list of UserItems in this category(CatalogItem)"""
    catalogItem = getCatalogItem(catalogItemId)
    userItems = getUserItems(catalogItemId)
    return render_template("catalogitem.html", catalogItem=catalogItem, userItems=userItems)


########## Routs ################
########## UserItem #############


# Show a UserItem
@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/')
def showUserItem(catalogItemId, userItemId):
    """
    Displays UserItems from CatalogItem
    If nothing found returns 404 page
    """
    try:
        catalog = getCatalogItemsAll()
        catalogItem = getCatalogItem(catalogItemId)
        userItem = getUserItem(catalogItemId, userItemId)
        user = getUser(userItem.user_id)
        return render_template("useritem.html", catalog=catalog, catalogItem=catalogItem, userItem=userItem, user=user)
    except:
        return redirect(url_for('pageNotFound'))


# Create new UserItem
@app.route('/thecatalog/useritem/new/', methods=['GET', 'POST'])
def createNewUserItem():
    """
    Creates new UserItem
    TODO make list of categories in the catalog to choose from
    """
    catalog = getCatalogItemsAll()
    if request.method == 'POST':
        if request.form['userItemTitle']:
            _title = request.form['userItemTitle']
            _description = request.form['description']
            _itemPic = request.form['itemPicture']
            _userId = 1
            _catalogItemId = request.form['catalogItemId']
            userItem = UserItem(title = _title, description= _description, item_picture=_itemPic, user_id = _userId, catalog_item_id = _catalogItemId)
            session.add(userItem)
            session.commit()
            flash("CatalogItem: " + userItem.title + " added.")
            return redirect(url_for('showUserItemsInCatalog', catalogItemId=_catalogItemId))
    else:
        return render_template('newuseritem.html', catalog=catalog)


# Edit a UserItem
@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/edit/', methods=['GET', 'POST'])
def editUserItem(catalogItemId, userItemId):
    _catalog = getCatalogItemsAll()
    _catalogItem = getCatalogItem(catalogItemId)
    _userItem = getUserItem(catalogItemId, userItemId)
    _user = getUser(_userItem.user_id)
    if request.method == 'POST':
        if request.form['userItemTitle']:
            # If fields are empty do not change them
            print("========== OLD VALUES ==========")
            showUserItemDetails(_userItem)

            _userItem.title = request.form['userItemTitle']
            _userItem.description = request.form['description']
            _userItem.item_picture = request.form['itemPicture']
            _userItem.catalog_item_id = request.form['catalogItemId']
            session.add(_userItem)
            session.commit()
            flash("userItem: " + _userItem.title + " was edited.")
            # Go to edited user item
            print("========== NEW VALUES ==========")
            showUserItemDetails(_userItem)

            return redirect(url_for('showUserItem', catalogItemId=_userItem.catalog_item_id, userItemId=_userItem.id))
    else:
        return render_template('edituseritem.html', catalog=_catalog, catalogItem = _catalogItem, userItem = _userItem, user = _user )


# Delete a UserItem
@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/delete/', methods=['GET', 'POST'])
def deleteUserItem(catalogItemId, userItemId):
    try:
        catalogItem = getCatalogItem(catalogItemId)
        userItem = getUserItem(catalogItemId, userItemId)
        user = getUser(userItem.user_id)
        if request.method == 'POST':
            session.delete(userItem)
            session.commit()
            flash("CatalogItem " + userItem.title + " was deleted")
            ## Redirect
            return redirect(url_for('showUserItemsInCatalog'))
        else:
            return render_template('deleteuseritem.html', catalogItem = catalogItem, userItem=userItem, user=user)
    except :
        return redirect(url_for('pageNotFound'))


@app.route('/thecatalog/pagenotfound/', methods=['GET'])
def pageNotFound():
    return render_template('pagenotfound.html')


if __name__ == '__main__':
    # app.debug = True - Means the server will reload itself
    # each time it sees chaneg in code.
    app.secret_key = 'appSecretKey'
    app.debug = True
    # param specifies on port 5000
    app.run(host = '0.0.0.0', port = 5000) 