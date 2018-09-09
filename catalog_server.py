#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Imports DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

##### TODO Create DB classes and populate catalog
from catalog_db_setup import Base, User, UserItem

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

# def getCatalogEntry(catalogEntryID):
#     restaurant = session.query(Restaurant).filter_by(id = restaurantID).one()
#     print("L28 restaurant = " + restaurant.name + " ##########")
#     return restaurant

# def getMenuItems(restaurantID):
#     return session.query(MenuItem).filter_by(restaurant_id = restaurantID).all()

# def getMenuItem(restaurantID, menuItemID):
#     restaurant = getCatalogEntry(catalogEntryID)
#     menuItem = session.query(MenuItem).filter_by(restaurant_id = restaurant.id, id = menuItemID).one()
#     print("L33 MenuItem " + menuItem.name)
#     return menuItem

################ Routs ################
################ Restaurant ################

# Show all restaurants
@app.route('/')
@app.route('/thecatalog/')
def showCatalog():
    catalog = session.query(CatalogItem).all()
    return render_template('index.html', catalog = catalog)

# Create new restaurant
@app.route('/thecatalog/new-catalog-entry/', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        if request.form['name']:
            restaurant = Restaurant(name = request.form['name'], )
            session.add(restaurant)
            session.commit()
            flash("Restaurant: " + restaurant.name + " added.")
            return redirect(url_for('showCatalog'))
    else:
        return render_template('newrestaurant.html')

# Edit catalog item
@app.route('/thecatalog/<int:catalogID>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurantID):
    # TODO: Add redirect when successful
    restaurant = getCatalogEntry(catalogEntryID)
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            message = "New Catalog entry is " + request.form['name']
            session.add(restaurant)
            session.commit()
            flash(message)
            ## Redirect
            return redirect(url_for('showCatalog'))
    else:
        return render_template('editcatalogentry.html', catalogEntry = catalogEntry)
