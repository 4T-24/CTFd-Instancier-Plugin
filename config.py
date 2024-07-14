from os import environ

def config(app):
    '''
    4TS_INSTANCER_BASE_URL is the base url of the instancer service, this is used to communicate with the instancer service
    '''
    app.config['4TS_INSTANCER_BASE_URL'] = environ.get('4TS_INSTANCER_BASE_URL', None)
    
    '''
    4TS_INSTANCER_TOKEN is used to  communicate with the instancer service, users should not have access to this token
    '''
    app.config['4TS_INSTANCER_TOKEN'] = environ.get('4TS_INSTANCER_TOKEN', None)
    
    '''
    4TS_INSTANCER_RECAPTCHA_SITE_KEY is the public key for the recaptcha service
    '''
    app.config['4TS_INSTANCER_RECAPTCHA_SITE_KEY'] = environ.get('4TS_INSTANCER_RECAPTCHA_SITE_KEY', None)