# The Catalog

This is a full-stack web development project that includes a server made with
python and Flask, postgreSQL and a front side that includes bootstrapped html and OAuth2.0. (See [Starting it up](#starting-it-up) section)

## Content

Project description:  
- It allowse a user to create entries of their favourite subjects(blogs) in different categories of the catalog.  
- The app stores user entries in the form of a database created with postgreSQL.
- It allows user to upload pictures.
- Implements OAuth2.0. Use is able to sign in using 3rd party identity provider such as Google, Facebook and LinkedIn.

## Folder Structure

After cloning the app should looks like this:
```
catalog/
    static/
        custom/ - Custom css
        vendor/
            bootstrap/ - Standard bootstrap libraries
                css/
                js/ 
            jquery/ - JQuery 3.2.1
    templates/
        catalogitem.html
        deletecatalogitem.html
        editcatalogitem.html
        index.html
        login.html
    README.md
```

## Built With

## Prerequisites

Some sort of VM with python 3 installed (See [Starting it up](#starting-it-up) section)

## Starting it up

//TODO: Add a link to Udacity VM.

## Contributing

This is a study project so contributing is not required. Please consider other projects. Thank you for your interest.

## Versioning

For the versions available, see the tags on this repository.

## Authors

Alexander Frolov - front-end as well as back-end.  
CSS and bootstrap is from here:
- [Start Bootstrap](https://startbootstrap.com/template-overviews/)
- [Bootstrap](https://getbootstrap.com/)