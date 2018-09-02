# The Catalog

This is a full-stack web development project that includes a server made with
python and Flask, postgreSQL and a front side that includes bootstrapped html and OAuth2.0.

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

1.  Install [Vagrant](https://www.vagrantup.com/) and VirtualBox
2.  Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) to get preinstalled version of Ubantu and python
3.  Navigate to /vagrant directory and launch the Vagrant VM by `$ vagrant up`
4.  Then ssh to running virtual machine by `$ vagrant ssh`
5.  Clone this project in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
6.  Run your application within the VM `$ python /vagrant/catalog/server.py`
7.  Access the application by visiting http://localhost:5000 locally in your browser.
  
>NOTE:  
>- to logout from vagrant either `ctrl+d` or `ctrl+c` in terminal window  
>- to stop your virtual machine `$ vagrant halt` in /vagrant directory

## Contributing

This is a study project so contributing is not required. Please consider other projects. Thank you for your interest.

## Versioning

For the versions available, see the tags on this repository.

## Authors

Alexander Frolov - front-end as well as back-end.  
CSS and bootstrap is from here:
- [Start Bootstrap](https://startbootstrap.com/template-overviews/)
- [Bootstrap](https://getbootstrap.com/)