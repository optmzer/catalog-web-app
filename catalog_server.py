#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Imports DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

##### TODO Create DB classes and populate catalog
from database_setup import Base, User, UserItem

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

def getRestaurant(restaurantID):
    restaurant = session.query(Restaurant).filter_by(id = restaurantID).one()
    print("L28 restaurant = " + restaurant.name + " ##########")
    return restaurant

def getMenuItems(restaurantID):
    return session.query(MenuItem).filter_by(restaurant_id = restaurantID).all()

def getMenuItem(restaurantID, menuItemID):
    restaurant = getRestaurant(restaurantID)
    menuItem = session.query(MenuItem).filter_by(restaurant_id = restaurant.id, id = menuItemID).one()
    print("L33 MenuItem " + menuItem.name)
    return menuItem

################ Routs ################
################ Restaurant ################

# Show all restaurants
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)

# Create new restaurant
@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        if request.form['name']:
            restaurant = Restaurant(name = request.form['name'], )
            session.add(restaurant)
            session.commit()
            flash("Restaurant: " + restaurant.name + " added.")
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('newrestaurant.html')

# Edit restaurant
@app.route('/restaurant/<int:restaurantID>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurantID):
    # TODO: Add redirect when successful
    restaurant = getRestaurant(restaurantID)
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            message = "New Restaurant name is " + request.form['name']
            session.add(restaurant)
            session.commit()
            flash(message)
            ## Redirect
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant = restaurant)
