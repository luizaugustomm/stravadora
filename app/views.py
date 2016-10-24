from django.shortcuts import render, redirect
from stravalib.client import Client

from stravadora.settings import DEBUG, SECRET_KEY, CLIENT_ID, CLIENT_SECRET
from app.models import Athlete, Activity

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
    return redirect('home')

def home(request):
    if 'access_token' not in request.session:
        return redirect('auth')
    # Retrieving athlete's data from API
    client = Client(access_token=request.session.get('access_token'))
    athlete = client.get_athlete()
    # Checking if the athlete has already visited the site before
    try:
        db_athlete = Athlete.objects.get(id=athlete.id)
    except Athlete.DoesNotExist:
        db_athlete = Athlete.create(athlete)
        db_athlete.save()
    # Getting the latest activity from the current athlete
    try:
        latest_activity = Activity.objects.filter(athlete=db_athlete).latest('date')
        activities = client.get_activities(after=latest_activity.date)
    except Activity.DoesNotExist:
        activities = client.get_activities()
    # Adding new activities to the database
    for activity in activities:
        stream = client.get_activity_streams(activity.id, types=['latlng'], resolution='medium').get('latlng')
        db_activity = Activity.create(activity, db_athlete, stream.data)
        db_activity.save()
    return render(request, 'home.html', {'athlete': athlete, 'activities': activities, 'act_length': len(list(activities))})

def logout(request):
    request.session.pop('access_token')
    return redirect('auth')
