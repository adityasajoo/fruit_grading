import functools
import os
import flask
from authlib.integrations.requests_client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

#authentication urls
ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

#scopes
SCOPE = 'profile https://www.googleapis.com/auth/drive'

#fetch the credentials from the environment variables
AUTH_REDIRECT_URI = os.environ.get("FN_AUTH_REDIRECT_URI", default=False)

BASE_URI = os.environ.get("FN_BASE_URI", default=False)
CLIENT_ID = os.environ.get("FN_CLIENT_ID", default=False)
CLIENT_SECRET = os.environ.get("FN_CLIENT_SECRET", default=False)

#Variables to hold the access and refresh tokens
AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

app = flask.Blueprint('auth',__name__)

#functions 

#check if the user is logged in
def isLoggedIn():
    return True if AUTH_TOKEN_KEY in flask.session else  False

#Each time you access the google apis, you need to get the access token and refresh the tokens
#Returns new access and refresh tokens to authorize our request
def getAuth():
    if not isLoggedIn():
        return False
    oauthTokens = flask.session[AUTH_TOKEN_KEY]
    return google.oauth2.credentials.Credentials(oauthTokens['access_token'],
                refresh_token=oauthTokens['refresh_token'],
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri=ACCESS_TOKEN_URI)

#ROUTES
@app.route('/google/login')
def login():
    session = OAuth2Session(CLIENT_ID,CLIENT_SECRET,
                            scope = SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    #get the state and uri ,And save state to the session
    uri, state = session.create_authorization_url(AUTHORIZATION_URL)
    flask.session[AUTH_STATE_KEY] = state
    flask.session.permanent = True

    return flask.redirect(uri,code=302)

#redirect url
@app.route('/google/auth')
def google_auth_redirect():
    #get the state from the request
    req_state = flask.request.args.get('state',default=None,type=None)
    #validate the state
    if req_state != flask.session[AUTH_STATE_KEY]:
        response = flask.make_response('State paramenter miss-match',401)
        return response
    #else add the access tokens to the session
    session = OAuth2Session(CLIENT_ID,CLIENT_SECRET,
                            scope=SCOPE,state=flask.session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_REDIRECT_URI)    
    oauth2_tokens = session.fetch_access_token(ACCESS_TOKEN_URI,
                                                authorization_response=flask.request.url)    
    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens
    return flask.redirect(BASE_URI,code=302)


#logout
@app.route('/logout')
def logout():
    flask.session.pop(AUTH_TOKEN_KEY,None)
    flask.session.pop(AUTH_STATE_KEY,None)

    return flask.redirect(BASE_URI,code=302)