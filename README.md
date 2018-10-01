# The Catalog

This is a full-stack web development project that includes a server made with
python and Flask, SQLAlchemy and a front side that includes bootstrapped html and OAuth2.0 from Google+ API.
The app needs internet connection and access to your account at Google for OAuth2.0 to work.

## Content

Project description:  
- It allows a user to create entries of their favourite subjects(blogs) in different categories of the catalog.  
- The app stores user entries in the form of a database created with postgreSQL.
- It allows user to upload pictures.
- Implements OAuth2.0. Use is able to sign in using 3rd party identity provider such as Google, Facebook and LinkedIn.

## Folder Structure

After cloning the app should looks like this:
```
catalog/
    static/
        img/ - Stores avatars for users with no pictures
        uploads/ - Sores uploaded images
        custom/ - Custom css
        vendor/
            bootstrap/ - Standard bootstrap libraries
                css/
                js/ 
            jquery/ - JQuery 3.2.1
    templates/
        catalogitem.html
        deletecatalogitem.html
        deleteuseritem.html
        editcatalogitem.html
        edituseritem.html
        index.html
        login.html
        newcatalogitem.html
        newuseritem.html
        pagenotfound.html
        useritem.html
    README.md
    catalog_db_setup.py - Sets up DB. Run this first.
    populate_db.py - Optional. Contains 2 posts.
    server_the_catalog.py - This is server.
    client_secrest.json - must be created manually for OAuth2.0 to work.
```

## Prerequisites

Obtain credentials from Google+ API and put them in client_secrets.json file in /catalog/client_secrets.json
File content will look like this:
YOUR_CLIENT_ID_FROM_GOOGLE_API, YOUR_PROJECT_ID, CLIENT_SECRET_GOES_HERE are all available from Google+.


```
{
    "web":{
        "client_id":"YOUR_CLIENT_ID_FROM_GOOGLE_API",
        "project_id":"YOUR_PROJECT_ID",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://www.googleapis.com/oauth2/v3/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":"CLIENT_SECRET_GOES_HERE",
        "redirect_uris":["http://localhost:5000/thecatalog/"],
        "javascript_origins":["http://localhost:5000"]
    }
}
```

1.  Install [Vagrant](https://www.vagrantup.com/) and VirtualBox
2.  Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) to get preinstalled version of Ubantu and python
3.  Navigate to /vagrant directory and launch the Vagrant VM by `$ vagrant up`
4.  Then ssh to running virtual machine by `$ vagrant ssh`
5.  Clone this project in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
6. cd to `/vagrant/catalog` directory
7.  Run your application within the VM 
`$ python catalog_db_setup.py` - Sets up your local db.
`$ python populate_db.py` - Optional. Contains 2 default posts.
`$ python /vagrant/catalog/server_the_catalog.py` - Runs the server.
8.  Access the application by visiting http://localhost:5000 locally in your browser.
  
>NOTE:  
>- to logout from vagrant either `ctrl+d` or `ctrl+c` in terminal window  
>- to stop your virtual machine `$ vagrant halt` in /vagrant directory


## JSON endpoints

1. `/thecatalog/json`  
returns list of json object of catalog items in the catalog.

2. `/thecatalog/<int:catalogItemId>/items/json`  
returns list of json object of all user items in a single catalogitem  

3. `/thecatalog/<int:catalogItemId>/useritem/<int:userItemId>/json`  
returns json object of this particular user item.


## Contributing

This is a study project so contributing is not required. Please consider other projects. Thank you for your interest.

## Versioning

For the versions available, see the tags on this repository.

## Authors

Alexander Frolov - front-end as well as back-end.  
CSS and bootstrap is from here:
- [Start Bootstrap Blog post theme](https://blackrockdigital.github.io/startbootstrap-blog-post/)
- [Bootstrap](https://getbootstrap.com/)