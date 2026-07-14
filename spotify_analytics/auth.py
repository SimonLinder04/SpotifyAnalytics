import base64
import hashlib
import json
import os
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from spotify_analytics.config import (
    AUTHORIZE_URL,
    REDIRECT_URI,
    SCOPES,
    TOKEN_CACHE,
    TOKEN_URL,
    save_client_id,
    spotify_client_id,
)


def load_cached_token():
    if not TOKEN_CACHE.exists():
        return None
    try:
        return json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def save_token(token_data, previous_refresh_token=None):
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600) - 60
    if previous_refresh_token and "refresh_token" not in token_data:
        token_data["refresh_token"] = previous_refresh_token
    TOKEN_CACHE.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
    return token_data


def request_token(parameters):
    response = requests.post(
        TOKEN_URL,
        data=parameters,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def refresh_access_token(client_id, cached_token):
    refresh_token = cached_token.get("refresh_token")
    if not refresh_token:
        return None

    token_data = request_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        }
    )
    return save_token(token_data, refresh_token)


def create_code_challenge(code_verifier):
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def wait_for_authorization_code(expected_state):
    callback_values = {}
    callback_path = urlparse(REDIRECT_URI).path

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_request = urlparse(self.path)
            if parsed_request.path != callback_path:
                self.send_error(404)
                return

            callback_values.update(
                {key: values[0] for key, values in parse_qs(parsed_request.query).items()}
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<h1>Spotify authorization complete</h1>"
                b"<p>You can close this browser tab and return to VS Code.</p>"
            )

        def log_message(self, format_string, *args):
            return

    try:
        server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    except OSError as error:
        raise RuntimeError(f"Could not start the Spotify callback server: {error}") from error

    with server:
        server.timeout = 180
        server.handle_request()

    if not callback_values:
        raise RuntimeError("Spotify sign-in timed out after 3 minutes.")
    if callback_values.get("state") != expected_state:
        raise RuntimeError("Spotify sign-in returned an invalid state value.")
    if "error" in callback_values:
        raise RuntimeError(f"Spotify sign-in failed: {callback_values['error']}")
    if "code" not in callback_values:
        raise RuntimeError("Spotify sign-in did not return an authorization code.")
    return callback_values["code"]


def authorize_user(client_id):
    code_verifier = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(24)
    authorization_parameters = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "code_challenge_method": "S256",
        "code_challenge": create_code_challenge(code_verifier),
        "state": state,
    }
    authorization_url = f"{AUTHORIZE_URL}?{urlencode(authorization_parameters)}"

    print("Opening Spotify in your browser for authorization...")
    print(f"If the browser does not open, visit:\n{authorization_url}")
    webbrowser.open(authorization_url)
    authorization_code = wait_for_authorization_code(state)

    token_data = request_token(
        {
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        }
    )
    return save_token(token_data)


def get_access_token(force_login=False):
    client_id = spotify_client_id()
    if client_id:
        cached_token = None if force_login else load_cached_token()
        if cached_token and cached_token.get("expires_at", 0) > time.time():
            return cached_token["access_token"]
        if cached_token and cached_token.get("refresh_token"):
            return refresh_access_token(client_id, cached_token)["access_token"]
        return authorize_user(client_id)["access_token"]

    manual_token = os.getenv("SPOTIFY_ACCESS_TOKEN", "").strip()
    if manual_token:
        return manual_token

    raise RuntimeError(
        "Set SPOTIFY_CLIENT_ID in .env. Create the app at developer.spotify.com "
        f"and register {REDIRECT_URI} as its redirect URI."
    )


def sign_in():
    client_id = spotify_client_id()
    if not client_id:
        print("Create or open your app at https://developer.spotify.com/dashboard")
        print(f"Register this exact Redirect URI: {REDIRECT_URI}")
        client_id = input("Paste your Spotify app Client ID: ").strip()
        if not client_id or client_id == "put_your_spotify_client_id_here":
            raise RuntimeError("A valid Spotify app Client ID is required.")
        save_client_id(client_id)

    print(f"Spotify dashboard Redirect URI must be: {REDIRECT_URI}")
    get_access_token(force_login=True)
    print("Spotify user authorization completed successfully.")
