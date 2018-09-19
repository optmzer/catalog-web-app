#!/usr/bin/env python3
import os

from flask import Flask
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

# Imports DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from werkzeug.utils import secure_filename

from catalog_db_setup import Base
from catalog_db_setup import CatalogItem
from catalog_db_setup import User
from catalog_db_setup import UserItem

################ Create Flask app ################
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 10 * 1024 * 1024 # 10Mb max file size

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

################ Create Connection to DB ################
# init connection with DB
engine = create_engine('sqlite:///thecatalog.db?check_same_thread=False')

# Connection between class def and corresp table in DB
Base.metadata.bind = engine
# Create delete and other commands Alchemy does via an interface called a Session
DBSession = sessionmaker(bind=engine)

session = DBSession()

#### TODO Tester Methods Delete Before Submission ####



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

def allowed_file(filename):
    """Checks if file extension is in allowed set"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

########## Routs ################
########## Login OAuth ##########
# @app.route('/thecatalog/login/', methods=['GET', 'POST'])

# @app.route('/thecatalog/logout/', methods=['GET', 'POST'])

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
    TODO update _userId for OAuth
    """
    catalog = getCatalogItemsAll()
    if request.method == 'POST':
        if request.form['userItemTitle']:
            # Get post data
            _title = request.form['userItemTitle']
            _description = request.form['description']
            _userId = 1 # TODO update for OAuth
            _catalogItemId = request.form['catalogItemId']
            # Upload image file, Record image location for DB
            try:
                file = request.files['itemPicture']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                _itemPic = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('.', '', 1)
            except:
                pass

            # Write to DB
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
            _userItem.title = request.form['userItemTitle']
            _userItem.description = request.form['description']
            _userItem.catalog_item_id = request.form['catalogItemId']
            # Upload image file, Record image location for DB
            # If image file is not selected/changed skipp
            try:
                file = request.files['itemPicture']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                _userItem.item_picture = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('.', '', 1)
            except:
                pass
            
            session.add(_userItem)
            session.commit()
            flash("userItem: " + _userItem.title + " was edited.")
            # Go to edited user item
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

########## Routs ################
########## JSON API #############

#JSON APIs to view Restaurant Information
@app.route('/thecatalog/<int:catalogItemId>/items/json')
def catalogItemJSON(catalogItemId):
    """Get all UserItems in a specified CatalogItem"""
    userItems = getUserItems(catalogItemId)
    return jsonify(userItems=[i.serialize for i in userItems])


@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/json')
def userItemJSON(catalogItemId, userItemId):
    """Get specified UserItem based on catalogId and userItemId"""
    userItem = getUserItem(catalogItemId, userItemId)
    return jsonify(userItem = userItem.serialize)


@app.route('/thecatalog/json')
def catalogAllJSON():
    """Get all CatalogItems"""
    catalog = getCatalogItemsAll()
    return jsonify(catalog = [c.serialize for c in catalog])

if __name__ == '__main__':
    # app.debug = True - Means the server will reload itself
    # each time it sees chaneg in code.
    app.secret_key = 'appSecretKey'
    app.debug = True
    # param specifies on port 5000
    app.run(host = '0.0.0.0', port = 5000) 
