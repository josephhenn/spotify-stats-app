from flask import Flask, render_template, redirect, request, make_response
from urllib.parse import urlencode
from secret import client_id, client_secret
import requests
from flask_mobility import Mobility
app = Flask(__name__)
Mobility(app)

# REDIRECT_URI = "http://127.0.0.1:5000/authorize"
REDIRECT_URI = "https://stats-for-spotify.uc.r.appspot.com/authorize"


def get_tokens(code):
    url = 'https://accounts.spotify.com/api/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(url, data=data)
    access_token = response.json()['access_token']
    refresh_token = response.json()['refresh_token']
    return access_token, refresh_token


@app.route('/')
def index():
    access_token = request.cookies.get('access_token')
    if access_token:
        return render_template('home.html')
    else:
        return render_template('index.html')


@app.route('/login')
def login():
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'user-top-read',
        'show_dialog': 'false'
    }
    url_params = urlencode(params)
    return redirect('https://accounts.spotify.com/authorize/?' + url_params)


@app.route('/authorize')
def authorize():
    try:
        code = request.args.get('code', type=str)
        access, refresh = get_tokens(code)
        resp = make_response(redirect('/'))
        resp.set_cookie('access_token', access)
        resp.set_cookie('refresh_token', refresh)
        return resp
    except:
        return make_response(redirect('/error'))


@app.route('/top_tracks')
def top_tracks():
    return render_template('top_tracks.html')


@app.route('/top_artists')
def top_artists():
    return render_template('top_artists.html')


@app.route('/top_tracks/results')
def top_tracks_results():
    try:
        access_token = request.cookies.get('access_token')
        limit = request.args.get('limit')
        if limit:
            limit = limit
        else:
            limit = 25
        time_range = request.args.get('time')
        if time_range:
            time_range = time_range
        else:
            time_range = 'long_term'
        url = 'https://api.spotify.com/v1/me/top/tracks'
        head = {
            'Authorization': 'Bearer ' + access_token
        }
        params = {
            'limit': limit,
            'time_range': time_range
        }
        resp = requests.get(url, headers=head, params=params)
        tracks = []
        for track in resp.json()['items']:
            artists = [artist['name'] for artist in track['artists']]
            artists = ', '.join(artists)
            name = track['name']
            open_url = track['external_urls']['spotify']
            tracks.append([name, artists, open_url])
        return render_template('top_tracks_results.html', tracks=tracks)
    except:
        resp = make_response(redirect('/'))
        resp.delete_cookie('access_token')
        resp.delete_cookie('refresh_token')
        return resp


@app.route('/top_artists/results')
def top_artists_results():
    try:
        access_token = request.cookies.get('access_token')
        limit = request.args.get('limit')
        if limit:
            limit = limit
        else:
            limit = 25
        time_range = request.args.get('time')
        if time_range:
            time_range = time_range
        else:
            time_range = 'long_term'
        url = 'https://api.spotify.com/v1/me/top/artists'
        head = {
            'Authorization': 'Bearer ' + access_token
        }
        params = {
            'limit': limit,
            'time_range': time_range
        }
        resp = requests.get(url, headers=head, params=params)
        artists = [artist['name'] for artist in resp.json()['items']]
        return render_template('top_artists_results.html', artists=artists)
    except:
        resp = make_response(redirect('/'))
        resp.delete_cookie('access_token')
        resp.delete_cookie('refresh_token')
        return resp


@app.route('/recommended')
def recommended():
    return render_template('recommended.html')


@app.route('/recommended/results')
def recommended_results():
    try:
        access_token = request.cookies.get('access_token')
        time_range = request.args.get('time')
        seed = request.args.get('seed')
        if seed == 'artists':
            url = 'https://api.spotify.com/v1/me/top/artists'
        elif seed == 'tracks':
            url = 'https://api.spotify.com/v1/me/top/tracks'
        head = {
            'Authorization': 'Bearer ' + access_token
        }
        params = {
            'limit': '5',
            'time_range': time_range
        }
        resp = requests.get(url, headers=head, params=params)
        seeds = [seed['id'] for seed in resp.json()['items']]
        seeds = ','.join(seeds)
        url = 'https://api.spotify.com/v1/recommendations'
        if seed == 'artists':
            params = {
                'seed_artists': seeds
            }
        elif seed == 'tracks':
            params = {
                'seed_tracks': seeds
            }
        resp = requests.get(url, headers=head, params=params)
        tracks = []
        for track in resp.json()['tracks']:
            artists = [artist['name'] for artist in track['artists']]
            artists = ', '.join(artists)
            name = track['name']
            open_url = track['external_urls']['spotify']
            tracks.append([name, artists, open_url])
        return render_template('recommended_results.html', tracks=tracks)
    except:
        resp = make_response(redirect('/'))
        resp.delete_cookie('access_token')
        resp.delete_cookie('refresh_token')
        return resp


@app.route('/error')
def error():
    return render_template('error.html')
