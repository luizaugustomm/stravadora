
from flask import Flask
from flask import render_template, request, redirect, session, url_for

from stravalib.client import Client

from config import *

app = Flask(__name__)
app.secret_key = APP_SECRET


@app.route('/auth')
def auth():
    client = Client()
    auth_url = client.authorization_url(client_id=CLIENT_ID,
                                        scope='view_private',
                                        redirect_uri='http://127.0.0.1:8080/auth_done')
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
    streams = client.get_activity_streams(athlete.id, types=['time', 'latlng', 'altitude'], resolution='medium')
    return render_template('home.html', athlete=athlete, streams=streams)


@app.route('/logout')
def logout():
    session.pop('access_token')
    return redirect(url_for('auth'))
