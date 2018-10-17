#!/usr/bin/env python3
import os
import random
import string
import json
import httplib2
import requests

from functools import wraps

from flask import Flask
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

# Authentication imports
from flask import session as login_session
from flask import make_response

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Imports DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from sqlalchemy import desc

# Upload file name check
from werkzeug.utils import secure_filename

from .catalog_db_setup import Base
from .catalog_db_setup import CatalogItem
from .catalog_db_setup import User
from .catalog_db_setup import UserItem

# Create Flask app ################
# Upload constants
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10Mb max file size

# OAuth2.0 Google constants
CLIEN_ID = json.loads(
    open('/var/www/thecatalog/thecatalog/client_secrets.json', 'r').read()
)['web']['client_id']
APPLICATION_NAME = "The Catalog"

app = Flask(__name__)

# app.config for Upload constants
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create Connection to DB ################
# init connection with DB
engine = create_engine('postgresql://thecatalog:catalogPass@localhost/thecatalog')

# Connection between class def and corresp table in DB
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


# Login required Wrapper
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in login_session:
            return redirect(url_for('showLoginPage'))
        return f(*args, **kwargs)
    return decorated_function


# Getters/Setters ################
def createUser(login_session):
    """Creates a User and ads it to DB"""
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        avatar=login_session['avatar']
        )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user


def getUserById(userId):
    """Returns a User entry by the Id"""
    user = session.query(User).filter_by(id=userId).one()
    return user


def getUserByEmail(email):
    """Returns a User entry by email"""
    user = None
    try:
        user = session.query(User).filter_by(email=email).one()
    except exc.SQLAlchemyError:
        pass
    return user


def getCatalogItemsAll():
    return session.query(CatalogItem).order_by(CatalogItem.title).all()


def getCatalogItem(catalogItemId):
    """Returns a CatalogItem by its Id"""
    catalogItem = session.query(CatalogItem).filter_by(id=catalogItemId).one()
    return catalogItem


def getUserItemsNewest(howMany):
    return session.query(
                UserItem).order_by(
                    desc(UserItem.created_date)).limit(howMany)


def getUserItems(catalogItemId):
    """Returns all UserItems for that CatalogItem by CatalogItem.id"""
    return session.query(
                UserItem).filter_by(
                    catalog_item_id=catalogItemId).order_by(
                        UserItem.title).all()


def getUserItem(catalogItemId, userItemId):
    """Returns UserItem for a particular User Id and for a particular
    CatalogItem Id"""
    catalogItem = getCatalogItem(catalogItemId)
    userItem = session.query(UserItem).filter_by(
                                        catalog_item_id=catalogItem.id,
                                        id=userItemId).one()
    return userItem


def allowed_file(filename):
    """Checks if file extension is in allowed set
    of types for upload
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routs ################
# Login OAuth ##########
@app.route('/thecatalog/login/', methods=['GET', 'POST'])
def showLoginPage():
    """Create anti forgery request token.
    Store it in the login_session for later validation"""
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state

    # Sent state to STATE property in html page
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Connects to Google API to access user
    Credentials. On success loggs in user into the app.
    """
    # Validate state token
    if(request.args.get('state') != login_session['state']):
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError as flow_error:
        print('Failed to upgrade the authorization code. error = '
              + flow_error)
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid
    access_token = credentials.access_token
    url = (
          'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
          % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if(result.get('error') is not None):
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if(result['user_id'] != gplus_id):
        response = make_response(
            json.dumps("Token's user ID does not match given user ID."), 401
        )
        print("Token's user ID does not match given user ID.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that access token is valid for this app.
    if(result['issued_to'] != CLIEN_ID):
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401
        )
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check if user is already connected
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if(stored_access_token is not None and gplus_id == stored_gplus_id):
        response = make_response(
            json.dumps("Current user is already connected"), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Added provider id
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['avatar'] = data['picture']
    login_session['email'] = data['email']

    # See if user entry exists, if it doesn't make a new one
    user = getUserByEmail(login_session['email'])
    if user is None:
        user = createUser(login_session)
    login_session['user_id'] = user.id

    # Send mesage to login.html on success.
    output = """
    <h4>Welcome, {}</h4>
    <img
        src="{}"
        style="width: 50px; height: 50px;border-radius: 25px;"
        alt="avatar"
    >
    """.format(login_session['username'], login_session['avatar'])
    return output


@app.route('/gdisconnect', methods=['POST', 'GET'])
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ("https://accounts.google.com/o/oauth2/revoke?token="
           + access_token)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    h = httplib2.Http()
    result = h.request(url, 'GET', headers=headers)
    if(result[0]['status'] == '200'):
        response = make_response(json.dumps("Successfully disconnected"), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        if(result[1] is not None):
            data = json.loads(result[1])
            err = data['error']
            err_desc = data['error_description']
        response = make_response(
                    json.dumps(
                        """Failed to revoke token for given user. Error: {},
                        Error Description: {}
                        """.format(err, err_desc)), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect', methods=['POST', 'GET'])
def disconnect():
    """
    Google disconnect. Required for OAuth2.0
    to logout user from the app
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['state']
        # if login_session['provider'] == 'facebook':
        #     fbdisconnect()
        #     del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['avatar']
        del login_session['user_id']
        del login_session['provider']
        flash("You have been logged out successfully.")
        return redirect(url_for('showCatalog'))
    else:
        flash("Cannot find your session details or you were not logged in.")
        return redirect(url_for('showCatalog'))


# Routs ################
# CatalogItem ##########


# Show all catalog entry
@app.route('/')
@app.route('/thecatalog/')
def showCatalog():
    """Shows fromt page of the catalog"""
    return render_template('index.html',
                           catalog=getCatalogItemsAll(),
                           userItems=getUserItemsNewest(3),
                           login_session=login_session)


# Create new catalogItem
# TODO assign user id from the form
@app.route('/thecatalog/catalogitem/new/', methods=['GET', 'POST'])
@login_required
def newCatalogItem():
    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('showCatalog'))

        if 'email' in login_session:
            try:
                user = getUserByEmail(login_session['email'])
            except exc.SQLAlchemyError:
                pass
        if request.form['catalogItemTitle']:
            catalogItem = CatalogItem(
                            title=request.form['catalogItemTitle'],
                            user_id=user.id)
            session.add(catalogItem)
            session.commit()
            return redirect(url_for('showCatalog'))
    else:
        return render_template('newcatalogitem.html',
                               login_session=login_session)


# Edit catalog item
@app.route('/thecatalog/<int:catalogItemId>/edit/', methods=['GET', 'POST'])
@login_required
def editCatalogItem(catalogItemId):
    try:
        catalogItem = getCatalogItem(catalogItemId)
        owner = getUserById(catalogItem.user_id)
        # if catalogItem is yours you can edit it
        # else redirect to public public
        if owner.email != login_session['email']:
            flash("You have no rights to modify entries of another user")
            return redirect(url_for('showCatalog'))

        if request.method == 'POST':
            # reset/cancel was pressed
            if 'reset' in request.form:
                    return redirect(url_for(
                                'showUserItemsInCatalog',
                                catalogItemId=catalogItemId))

            if request.form['catalogItemTitle']:
                catalogItem.title = request.form['catalogItemTitle']
                session.add(catalogItem)
                session.commit()
                # Redirect
                return redirect(url_for('showCatalog'))
        else:
            return render_template('editcatalogitem.html',
                                   catalogItem=catalogItem,
                                   login_session=login_session)
    except exc.SQLAlchemyError:
        return redirect(url_for('pageNotFound'))


# Delete CatalogItem
@app.route('/thecatalog/<int:catalogItemId>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCatalogItem(catalogItemId):
    # TODO Check if user is the owner of the catalogItem
    try:
        catalogItem = getCatalogItem(catalogItemId)
        owner = getUserById(catalogItem.user_id)
        # if catalogItem is yours you can edit it
        # else redirect to public public

        # If user id != userItem.user_id then redirect
        if owner.email != login_session['email']:
            flash("You have no rights to modify entries of another user")
            return redirect(url_for('showCatalog'))

        if request.method == 'POST':
            if 'reset' in request.form:
                return redirect(url_for(
                            'showUserItemsInCatalog',
                            catalogItemId=catalogItemId))

            session.delete(catalogItem)
            session.commit()
            # Redirect
            return redirect(url_for('showCatalog'))
        else:
            return render_template('deletecatalogitem.html',
                                   catalogItem=catalogItem,
                                   login_session=login_session)
    except exc.SQLAlchemyError:
        return redirect(url_for('pageNotFound'))


# Show UserItems in CatalogItem
@app.route('/thecatalog/<int:catalogItemId>/items/', methods=['GET', 'POST'])
def showUserItemsInCatalog(catalogItemId):
    """Shows list of UserItems in this category(CatalogItem)"""
    catalogItem = getCatalogItem(catalogItemId)
    userItems = getUserItems(catalogItemId)
    return render_template("catalogitem.html",
                           catalogItem=catalogItem,
                           userItems=userItems,
                           login_session=login_session)


# Routs ################
# UserItem #############


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
        user = getUserById(userItem.user_id)
        return render_template("useritem.html",
                               catalog=catalog,
                               catalogItem=catalogItem,
                               userItem=userItem,
                               user=user,
                               login_session=login_session)
    except exc.SQLAlchemyError:
        return redirect(url_for('pageNotFound'))


# Create new UserItem
@app.route('/thecatalog/useritem/new/', methods=['GET', 'POST'])
@login_required
def createNewUserItem():
    """
    Creates new UserItem
    TODO update _userId for OAuth
    """
    catalog = getCatalogItemsAll()
    if 'email' in login_session:
        try:
            user = getUserByEmail(login_session['email'])
        except exc.SQLAlchemyError:
            pass
    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('showCatalog'))

        if request.form['userItemTitle']:
            # Get post data
            _title = request.form['userItemTitle']
            _description = request.form['description']
            # Get id from DataBase.
            _userId = user.id
            _catalogItemId = request.form['catalogItemId']
            # Upload image file, Record image location for DB
            try:
                file = request.files['itemPicture']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(
                                app.config['UPLOAD_FOLDER'],
                                filename))
                _itemPic = os.path.join(
                                app.config['UPLOAD_FOLDER'],
                                filename).replace('.', '', 1)
            except Exception:
                _itemPic = "http://placehold.it/900x300"

            # Write to DB
            userItem = UserItem(title=_title,
                                description=_description,
                                item_picture=_itemPic,
                                user_id=_userId,
                                catalog_item_id=_catalogItemId)
            session.add(userItem)
            session.commit()
            return redirect(url_for('showUserItemsInCatalog',
                                    catalogItemId=_catalogItemId))
    else:
        return render_template('newuseritem.html',
                               catalog=catalog,
                               login_session=login_session)


# Edit a UserItem
@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/edit/',
           methods=['GET', 'POST'])
@login_required
def editUserItem(catalogItemId, userItemId):
    try:
        _catalog = getCatalogItemsAll()
        _catalogItem = getCatalogItem(catalogItemId)
        _userItem = getUserItem(catalogItemId, userItemId)
        _user = getUserById(_userItem.user_id)
    except exc.SQLAlchemyError:
        return redirect(url_for('pageNotFound'))
    # If user id != userItem.user_id then redirect
    if _user.email != login_session['email']:
        flash("You have no rights to modify entries of another user")
        return redirect(url_for('showUserItem',
                                catalogItemId=_userItem.catalog_item_id,
                                userItemId=_userItem.id))

    # If cancel button pressed redirect.
    if 'reset' in request.form:
        return redirect(url_for('showUserItem',
                                catalogItemId=_userItem.catalog_item_id,
                                userItemId=_userItem.id))

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
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                           filename))
                _userItem.item_picture = os.path.join(
                                            app.config['UPLOAD_FOLDER'],
                                            filename).replace('.', '', 1)
            except Exception:
                pass

            session.add(_userItem)
            session.commit()
            # Go to edited user item
            return redirect(url_for('showUserItem',
                            catalogItemId=_userItem.catalog_item_id,
                            userItemId=_userItem.id))
    else:
        return render_template('edituseritem.html',
                               catalog=_catalog,
                               catalogItem=_catalogItem,
                               userItem=_userItem,
                               user=_user,
                               login_session=login_session)


# Delete a UserItem
@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteUserItem(catalogItemId, userItemId):

    try:
        catalogItem = getCatalogItem(catalogItemId)
        userItem = getUserItem(catalogItemId, userItemId)
        user = getUserById(userItem.user_id)

        # If user id != userItem.user_id then redirect
        if user.email != login_session['email']:
            flash("You have no rights to modify entries of another user")
            return redirect(url_for('showUserItem',
                            catalogItemId=userItem.catalog_item_id,
                            userItemId=userItem.id))

        # If cancel button pressed redirect.
        if 'reset' in request.form:
            return redirect(url_for('showUserItem',
                            catalogItemId=userItem.catalog_item_id,
                            userItemId=userItem.id))

        if request.method == 'POST':
            session.delete(userItem)
            session.commit()
            # Redirect
            return redirect(url_for('showUserItemsInCatalog',
                                    catalogItemId=catalogItemId))
        else:
            return render_template('deleteuseritem.html',
                                   catalogItem=catalogItem,
                                   userItem=userItem,
                                   user=user,
                                   login_session=login_session)
    except exc.SQLAlchemyError:
        return redirect(url_for('pageNotFound'))


@app.route('/thecatalog/pagenotfound/', methods=['GET'])
def pageNotFound():
    return render_template('pagenotfound.html')


# Routs ################
# JSON API #############


# JSON APIs to view Restaurant Information
@app.route('/thecatalog/<int:catalogItemId>/items/JSON')
def catalogItemJSON(catalogItemId):
    """Get all UserItems in a specified CatalogItem"""
    userItems = getUserItems(catalogItemId)
    return jsonify(userItems=[i.serialize for i in userItems])


@app.route('/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/JSON')
def userItemJSON(catalogItemId, userItemId):
    """Get specified UserItem based on catalogId and userItemId"""
    userItem = getUserItem(catalogItemId, userItemId)
    return jsonify(userItem=userItem.serialize)


@app.route('/thecatalog/JSON')
def catalogAllJSON():
    """Get all CatalogItems"""
    catalog = getCatalogItemsAll()
    return jsonify(catalog=[c.serialize for c in catalog])


if __name__ == '__main__':
    # app.debug = True - Means the server will reload itself
    # each time it sees chaneg in code.
    # 64bit random key
    #app.secret_key = """SuperSecretString"""
    # Remove app.debug and change app.run(host='0.0.0.0', port=8080)
    # to app.run()
    #app.debug = True
    # param specifies on port 5000
    #app.run(host='0.0.0.0', port=5000)
    app.run()
