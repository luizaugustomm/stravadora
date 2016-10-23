from django.shortcuts import render, redirect
from stravalib.client import Client

from stravadora.settings import DEBUG, SECRET_KEY, CLIENT_ID, CLIENT_SECRET

if DEBUG:
    uri = 'http://127.0.0.1:8080/auth_done'
else:
    uri = 'http://stravadora.herokuapp.com/auth_done'

def auth(request):
    client = Client()
    auth_url = client.authorization_url(client_id=CLIENT_ID,
                                        scope='view_private',
                                        redirect_uri=uri)
    return render(request, 'auth.html', {'auth_url': auth_url})

def auth_done(request):
    code = request.GET.get('code')
    client = Client()
    access_token = client.exchange_code_for_token(client_id=CLIENT_ID,
                                                  client_secret=CLIENT_SECRET,
                                                  code=code)
    request.session['access_token'] = access_token
    return redirect('/')

def home(request):
    if 'access_token' not in request.session:
        return redirect('auth')

    client = Client(access_token=request.session.get('access_token'))
    athlete = client.get_athlete()
    activities = client.get_activities()
    streams = {}
    for activity in activities:
        streams[activity.id] = client.get_activity_streams(activity.id, types=['latlng'], resolution='medium', series_type='time')
    return render(request, 'home.html', {'athlete': athlete, 'streams': streams})
