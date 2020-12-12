import flask
import auth
import drive
import os

app = flask.Flask(__name__)
app.register_blueprint(auth.app)
app.register_blueprint(drive.app)

#Set session secret
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)


#routes
@app.route('/')
def index():  
    if auth.isLoggedIn():       
         return flask.render_template('index.html')

    return flask.render_template('login.html')

    
