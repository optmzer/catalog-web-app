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

################ Routs ################
################ Restaurant ################

# Show all restaurants
@app.route('/')
@app.route('/thecatalog/')
def showCatalog():
    catalog = session.query(CatalogItem).all()
    return render_template('index.html', catalog = catalog)

# Create new catalogItem
# TODO assign user id from the form
@app.route('/thecatalog/new-catalog-item/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    # app.debug = True - Means the server will reload itself
    # each time it sees chaneg in code.
    app.secret_key = 'appSecretKey'
    app.debug = True
    # param specifies on port 5000
    app.run(host = '0.0.0.0', port = 5000) 