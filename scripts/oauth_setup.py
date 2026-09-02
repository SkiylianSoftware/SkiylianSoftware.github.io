"""
Standalone OAuth 2.0 setup script for YouTube Analytics.
Run this locally (not in CI) to generate a new refresh token.

Uses a temporary local loopback server to receive the Google redirect
(works with Desktop app credentials, whose redirect is http://localhost).

Usage:
    python3 scripts/oauth_setup.py

It will print a URL. Open it, authorize with Skye's YouTube account.
The local server catches the redirect and exchanges the code for tokens.
Copy the refresh token to the YOUTUBE_REFRESH_TOKEN GitHub secret.
"""

import http.server
import os
import socketserver
import threading
import urllib.parse

import requests


def _load_env():
    """Load .env file if present and env vars are not already set."""
    if os.environ.get("YOUTUBE_CLIENT_ID"):
        return
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())


_load_env()

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/"
MAX_PORT_TRIES = 5

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

received_code = None


class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global received_code
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
        error = qs.get("error", [None])[0]
        if error:
            body = f"<html><body><h2>Error: {error}</h2></body></html>"
            self.send_response(400)
        elif code:
            received_code = code
            body = "<html><body><h2>Authorization successful! You can close this tab.</h2></body></html>"
            self.send_response(200)
        else:
            body = "<html><body><h2>No code received.</h2></body></html>"
            self.send_response(400)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode())
        # Shut down after first request
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, fmt, *args):
        pass


def build_auth_url():
    base = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "authuser": "1",
    }
    return base + "?" + urllib.parse.urlencode(params)


def exchange_code(code, client_id, client_secret):
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Token exchange failed ({resp.status_code}): {resp.text}")
        return None
    return resp.json()


def main():
    global received_code

    if not CLIENT_ID or not CLIENT_SECRET:
        client_id = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
        if not client_id or not client_secret:
            client_id = input("Enter OAuth 2.0 Client ID: ").strip()
            client_secret = input("Enter OAuth 2.0 Client Secret: ").strip()
    else:
        client_id = CLIENT_ID
        client_secret = CLIENT_SECRET

    auth_url = build_auth_url()
    print("\nOpen this URL in a browser and authorize with Skye's YouTube account:\n")
    print("  " + auth_url + "\n")

    # Start local server to catch the redirect, retrying on higher ports
    server = None
    for port in range(REDIRECT_PORT, REDIRECT_PORT + MAX_PORT_TRIES):
        try:
            server = socketserver.TCPServer(("", port), RedirectHandler)
            break
        except OSError:
            continue
    if server is None:
        print("Could not bind any redirect port. Exiting.")
        return
    port_actual = server.server_address[1]
    print(f"Listening on http://localhost:{port_actual}/ for the redirect...")
    server.serve_forever()

    if not received_code:
        print("No authorization code received. Exiting.")
        return

    print("\nAuthorization code received. Exchanging for tokens...")
    tokens = exchange_code(received_code, client_id, client_secret)
    if not tokens:
        return

    refresh_token = tokens.get("refresh_token", "")
    access_token = tokens.get("access_token", "")

    if not refresh_token:
        print("\nWARNING: No refresh_token returned!")
        print("This can happen if the account was already authorized.")
        print("Revoke access at https://myaccount.google.com/permissions")
        print("then run this script again.")
        print("Access token (short-lived):", access_token[:50] + "...")
        return

    print("\n=== SUCCESS ===")
    print(f"Refresh token: {refresh_token}")
    print()
    print("Update GitHub secret:")
    repo = "SkiylianSoftware/SkiylianSoftware.github.io"
    print(f"  gh secret set YOUTUBE_REFRESH_TOKEN --repo {repo} --body '{refresh_token}'")


if __name__ == "__main__":
    main()
