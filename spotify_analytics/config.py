import os
from pathlib import Path


API_BASE_URL = "https://api.spotify.com/v1"
AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = (
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-top-read",
    "user-read-recently-played",
)

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
ENVIRONMENT_FILE = PROJECT_DIRECTORY / ".env"
TOKEN_CACHE = PROJECT_DIRECTORY / ".spotify_token.json"


def load_environment_file():
    if not ENVIRONMENT_FILE.exists():
        return

    for line in ENVIRONMENT_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def spotify_client_id():
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
    if not client_id or client_id == "put_your_spotify_client_id_here":
        return None
    return client_id


def save_client_id(client_id):
    lines = []
    client_id_saved = False
    if ENVIRONMENT_FILE.exists():
        lines = ENVIRONMENT_FILE.read_text(encoding="utf-8").splitlines()

    for index, line in enumerate(lines):
        if line.strip().startswith("SPOTIFY_CLIENT_ID="):
            lines[index] = f"SPOTIFY_CLIENT_ID={client_id}"
            client_id_saved = True
            break

    if not client_id_saved:
        lines.append(f"SPOTIFY_CLIENT_ID={client_id}")

    ENVIRONMENT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ["SPOTIFY_CLIENT_ID"] = client_id
