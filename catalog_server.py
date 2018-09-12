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

################ Getters/Setters ################

def getCatalogItem(catalogItemId):
    """Returns a CatalogItem by its Id"""
    catalogItem = session.query(CatalogItem).filter_by(id = catalogItemId).one()
    print("L28 CatalogItem = " + catalogItem.title + " ##########")
    return catalogItem

def getUserItems(catalogItemId):
    """Returns all UserItems for that CatalogItem by CatalogItem.id"""
    return session.query(UserItem).filter_by(catalog_item_id = catalogItemId).all()

def getUserItem(catalogItemId, userItemId):
    """Returns UserItem for a particular User Id and for a particular 
    CatalogItem Id"""
    catalogItem = getCatalogItem(catalogItemId)
    userItem = session.query(UserItem).filter_by(catalog_item_id = catalogItem.id, id = userItemId).one()
    print("L33 userItem " + userItem.title)
    return userItem

def getUser(userId):
    """Returns a User by the Id"""
    user = session.query(User).filter_by(id = userId).one()
    print("L49 User.id = %d Name: %s ##########" % (user.id, user.name))
    return user

########## Routs ################
########## CatalogItem ##########

# Show all restaurants
@app.route('/')
@app.route('/thecatalog/')
def showCatalog():
    """Shows fromt page of the catalog"""
    catalog = session.query(CatalogItem).all()
    return render_template('index.html', catalog = catalog)

# Create new catalogItem
# TODO assign user id from the form
@app.route('/thecatalog/catalogitem/new/', methods=['GET', 'POST'])
def newCatalogItem():
    if request.method == 'POST':
        if request.form['name']:
            catalogItem = CatalogItem(title = request.form['name'], userId = 1)
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
        if request.form['name']:
            catalogItem.title = request.form['name']
            message = "New Catalog entry is " + request.form['name']
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
    catalogItem = getCatalogItem(catalogItemId)
    if request.method == 'POST':
        session.delete(catalogItem)
        session.commit()
        flash("CatalogItem " + catalogItem.title + " was deleted")
        ## Redirect
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deletecatalogitem.html', catalogItem = catalogItem)


########## Routs ################
########## UserItem #############


# Show UserItems in CatalogItem
@app.route('/thecatalog/<int:catalogItemId>/items/', methods=['GET', 'POST'])
def showUserItemsInCatalog(catalogItemId):
    """Shows list of UserItems in this category(CatalogItem)"""
    catalogItem = getCatalogItem(catalogItemId)
    userItems = getUserItems(catalogItemId)
    print("############### Show UserItems in CatalogItem  ###############")
    print("CatalogItem = %s" % catalogItem.title)
    return render_template("catalogitem.html", catalogItem=catalogItem, userItems=userItems)


# Show a UserItem
@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/')
def showUserItem(catalogItemId, userItemId):
    """Displays UserItem from Catalog"""
    catalogItem = getCatalogItem(catalogItemId)
    userItem = getUserItem(catalogItemId, userItemId)
    user = getUser(userItem.user_id)
    print("############### Show UserItem  ###############")
    print("CatalogItem = %s" % catalogItem.title)
    return render_template("useritem.html", catalogItem=catalogItem, userItem=userItem, user=user)


if __name__ == '__main__':
    # app.debug = True - Means the server will reload itself
    # each time it sees chaneg in code.
    app.secret_key = 'appSecretKey'
    app.debug = True
    # param specifies on port 5000
    app.run(host = '0.0.0.0', port = 5000) 