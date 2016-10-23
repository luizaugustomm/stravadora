
import os

from flask import Flask
from flask import render_template, request, redirect, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from stravalib.client import Client


DEBUG = False

if DEBUG:
    uri = 'http://127.0.0.1:8080/auth_done'
else:
    uri = 'http://stravadora.herokuapp.com/auth_done'

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

app.secret_key = os.environ.get('APP_SECRET')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

db = SQLAlchemy(app)


@app.route('/auth')
def auth():
    client = Client()
    auth_url = client.authorization_url(client_id=CLIENT_ID,
                                        scope='view_private',
                                        redirect_uri=uri)
    return render_template('auth.html', auth_url=auth_url)


@app.route('/auth_done')
def auth_done():
    code = request.args.get('code')
    client = Client()
    access_token = client.exchange_code_for_token(client_id=CLIENT_ID,
                                                  client_secret=CLIENT_SECRET,
                                                  code=code)
    session['access_token'] = access_token
    return redirect('/')

@app.route('/')
def home():
    if 'access_token' not in session:
        return redirect(url_for('auth'))

    client = Client(access_token=session.get('access_token'))
    athlete = client.get_athlete()
    activities = client.get_activities()
    streams = {}
    for activity in activities:
        streams[activity.id] = client.get_activity_streams(activity.id, types=['latlng'], resolution='medium', series_type='time')
    return render_template('home.html', athlete=athlete, streams=streams)


@app.route('/logout')
def logout():
    session.pop('access_token')
    return redirect(url_for('auth'))
