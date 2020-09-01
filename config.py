
class Config(object):
    SECRET_KEY = "#RemovedForSecurity"
    HOST = "#RemovedForSecurity"

    SHOPIFY_CONFIG = {
        'API_KEY': '#RemovedForSecurity',
        'API_SECRET': '#RemovedForSecurity',
        'APP_HOME': 'http://' + HOST,
        'CALLBACK_URL': 'http://' + HOST + '/install',
        'REDIRECT_URI': 'http://' + HOST + '/connect',
        'SCOPE': 'read_products, read_collection_listings'
    }
