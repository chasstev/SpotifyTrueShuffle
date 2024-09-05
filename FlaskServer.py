"""
FlaskServer Module

This Flask server module integrates with the Spotify API, allowing users to authenticate with Spotify, manage playback, and interact with their playlists.
"""
from flask import Flask, request, redirect, url_for, jsonify, render_template_string
from random import random
import requests
import os
import random
import time

# Spotify API credentials
client_id = None
client_secret = None
config_file_path = "config.conf"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = ("user-read-private user-read-email "
         "user-modify-playback-state  "
         "user-read-currently-playing "
         "user-read-playback-state "
         "playlist-read-private "
         "playlist-read-collaborative")

user_tokens = {}

# Spotify API endpoints
API_BASE_URL = "https://api.spotify.com/v1"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
QUEUE_URL = f"{API_BASE_URL}/me/player/queue"
SKIP_SONG_URL = f"{API_BASE_URL}/me/player/next"
PAUSE_PLAYBACK_URL = f"{API_BASE_URL}/me/player/pause"
PLAYLISTS_URL = f"{API_BASE_URL}/me/playlists?fields=items(id, name, images)"
PLAYLIST_TRACKS_URL = f"{API_BASE_URL}/playlists/{{playlist_id}}/tracks"
CURRENTLY_PLAYING_TRACK = f"{API_BASE_URL}/me/player/currently-playing"
GET_PLAYBACK_STATE_URL = f"{API_BASE_URL}/me/player"


def update_api_credentials(get_client_id, get_client_secret):
    """
    Receives and updates the Spotify API credentials used for authentication.

    Args:
        get_client_id (str): The client ID for the Spotify API.
        get_client_secret (str): The client secret for the Spotify API.
    """
    global client_id
    global client_secret
    client_id = get_client_id
    client_secret = get_client_secret


app = Flask(__name__)


def run_flask():
    """
    Starts the Flask application.
    """
    app.secret_key = os.urandom(24)
    app.run(debug=False)


def get_auth_url():
    """
    Generates the Spotify authorization URL.

    Returns:
        str: The URL for Spotify authorization.
    """
    auth_query_params = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "client_id": client_id
    }
    return f"{AUTH_URL}?" + "&".join([f"{key}={val}" for key, val in auth_query_params.items()])



def get_access_token(code):
    """
    Exchanges an authorization code for an access token.

    Args:
        code (str): The authorization code received from Spotify.

    Returns:
        dict: The response containing access and refresh tokens.
    """
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    return response.json()


def refresh_access_token(refresh_token):
    """
    Refreshes the access token using a refresh token.

    Args:
        refresh_token (str): The refresh token used to obtain a new access token.

    Returns:
        dict: The response containing the new access token.
    """
    token_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    return response.json()


def get_valid_token():
    """
    Retrieves a valid access token. Refreshes the token if expired.

    Returns:
        str: The access token.
    """
    access_token_info = next(iter(user_tokens.values()))
    if time.time() > access_token_info["expires_at"]:
        response = refresh_access_token(access_token_info["refresh_token"])
        new_access_token = response.get("access_token")
        expires_in = response.get("expires_in")

        access_token_info["access_token"] = new_access_token
        access_token_info["expires_at"] = time.time() + expires_in

    return access_token_info["access_token"]


def clear_user_token():
    """
    Clears all stored user tokens.
    """
    global user_tokens
    user_tokens.clear()


@app.route('/')
def home():
    """
    Redirects to the Spotify authorization URL.

    Returns:
        flask.Response: A redirect response to the authorization URL.
    """
    return redirect(get_auth_url())


@app.route('/callback')
def callback():
    """
    Handles the callback from Spotify after authorization. Exchanges the authorization code for an access token.

    Returns:
        flask.Response: A redirect response to the success or failure page based on authentication result.
    """
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return redirect(url_for("failed_webpage"))

    response = get_access_token(code)

    if "error" in response:
        return redirect(url_for("failed_webpage"))

    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")

    user_tokens[access_token] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": time.time() + expires_in
    }
    return redirect(url_for("success_webpage"))


@app.route('/success_webpage')
def success_webpage():
    """
    Opens the users default browser and displays a webpage showing a success message after successful authentication.

    Returns:
        str: An HTML string indicating successful authentication.
    """
    return render_template_string("<html><body><h1>Successfully Authenticated to Spotify! You can close this tab. </h1></body></html>")


@app.route('/failed_webpage')
def failed_webpage():
    """
    Opens the users default browser and displays a webpage showing a failure message if authentication fails.

    Returns:
        str: An HTML string indicating authentication failure.
    """
    return render_template_string("<html><body><h1>Failed to authenticate to Spotify, Try again!</h1></body></html>")


@app.route('/check_authentication')
def check_authentication():
    """
    Checks if the user is authenticated.

    Returns:
        flask.Response: A JSON response indicating whether authentication was successful.
    """
    if user_tokens:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@app.route('/playlists')
def playlists():
    """
    Retrieves and returns the user's Spotify playlists.

    Returns:
        flask.Response: A JSON response containing the user's playlists or an error message.
    """
    access_token = get_valid_token()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(PLAYLISTS_URL, headers=headers)

    if response.status_code == 200:
        playlists = response.json().get("items", [])
        formatted_playlists = []
        for playlist in playlists:
            formatted_playlists.append({
                "id": playlist["id"],
                "name": playlist["name"],
                "images": playlist["images"]
            })
        return jsonify(formatted_playlists)
    else:
        return "Failed to fetch playlists.", response.status_code


@app.route('/get_queue')
def get_queue():
    """
    Retrieves and returns the current playback queue.

    Returns:
        flask.Response: A JSON response containing the current playback queue or an error message.
    """
    access_token = get_valid_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(QUEUE_URL, headers=headers)

    if response.status_code == 200:
        queue_data = response.json().get("queue", [])
        formatted_queue = []
        for queue in queue_data:
            formatted_queue.append({
                "id": queue["id"],
            })
        return jsonify(formatted_queue)
    else:
        return "Failed to fetch queue.", response.status_code


@app.route('/add_random_song_to_queue/<playlist_id>', methods=["POST"])
def add_random_song_to_queue(playlist_id):
    """
    Adds a random song from the specified playlist to the playback queue.

    Args:
        playlist_id (str): The ID of the playlist from which a random song will be added.

    Returns:
        flask.Response: A message inicating the result of dthe operation.
    """
    access_token = get_valid_token()

    headers = {"Authorization": f"Bearer {access_token}"}
    limit = 100
    offset = 0
    all_tracks = []

    while True:
        response = requests.get(PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id), headers=headers,
                                                           params={"limit": limit, "offset": offset})

        if response.status_code == 200:
            tracks = response.json().get("items", [])
            if not tracks:
                break
            all_tracks.extend(tracks)
            if len(tracks) < limit:
                break
            offset += limit
        else:
            return f"Failed to fetch playlist tracks.", response.status_code

    if not all_tracks:
        return jsonify({"error": "No tracks found in the playlist."})

    random.shuffle(all_tracks)
    random_track = random.choice(all_tracks)
    song_uri = random_track["track"]["uri"]

    response = requests.post(QUEUE_URL, headers=headers, params={"uri": song_uri})

    if response.status_code == 204:
        return "Random song added to queue successfully!"
    else:
        return "Failed to add song to queue.", response.status_code


@app.route('/skip_to_next_song', methods=["POST"])
def skip_to_next_song():
    """
    Skips to the next song in the playback.

    Returns:
        flask.Response: A message indicating the result of the operation.
    """
    access_token = get_valid_token()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(SKIP_SONG_URL, headers=headers)

    if response.status_code == 204:
        return "Skipped to next song successfully!"
    else:
        return "Failed to skip to next song", response.status_code


@app.route('/pause_playback', methods=["PUT"])
def pause_playback():
    """
    Pauses the current playback.

    Returns:
        flask.Response: A message indicating the result of the operation.
    """
    access_token = get_valid_token()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put(PAUSE_PLAYBACK_URL, headers=headers)

    if response.status_code == 204:
        return "Paused song successfully!"
    else:
        return "Failed to pause song", response.status_code