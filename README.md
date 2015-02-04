# Tornado-OAuth2
A oauth2 provider server by tornado


### Get the project

    $ git clone https://github.com/rsj217/Tornado-OAuth2.git
    
### Create the environment

    $ cd Tornado-OAuth2
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    
### Install the Mongodb

ubuntu

    $ sudo apt-get install mongodb-org 
    
Mac OS
    
    $ brew install mongodb
    
### Run the Project

    $ python run.py --env=dev
    

### Test

#### resource owner password credentials

    $ cd app/legacyserver
    $ python models
    
browser the [http://localhost/legacy/client](http://localhost/legacy/client) to register a clinet, keep secret the 
`clinet_id` and `client_secret`
    
    $ python tests.py
    
enjoy


### Document

please read the [wiki](https://github.com/rsj217/Tornado-OAuth2/wiki/%E4%B8%80-%E9%A1%B9%E7%9B%AE%E7%AE%80%E4%BB%8B) 


### Feature

* 0.0.1 support resource owner password credentials