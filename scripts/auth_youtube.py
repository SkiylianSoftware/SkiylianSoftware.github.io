"""
One-time auth script to get a YouTube refresh token for the Analytics API.

Run this ONCE locally:
  python scripts/auth_youtube.py

It will print a URL. Open it in a browser, authorize with Skye's YouTube account,
then paste the redirected URL back into the terminal.

Save the printed refresh token as YOUTUBE_REFRESH_TOKEN in GitHub secrets.
Also save CLIENT_ID and CLIENT_SECRET as YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET.
"""

import json
import os
import socket
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"
REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/"


class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.server.auth_code = None
        if "code=" in self.path:
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            self.server.auth_code = qs.get("code", [None])[0]
            self.wfile.write(b"<h1>Authorized! You can close this tab.</h1>")
        else:
            self.wfile.write(b"<h1>Authorization failed.</h1>")

    def log_message(self, format, *args):
        pass


def get_auth_code():
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPE}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    print("\nOpen this URL in a browser and authorize with Skye's YouTube account:")
    print(f"\n  {auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", REDIRECT_PORT), RedirectHandler)
    server.auth_code = None
    while server.auth_code is None:
        server.handle_request()
    return server.auth_code


def exchange_code(code):
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET environment variables first.")
        print("\nTo get these:")
        print("  1. Go to https://console.cloud.google.com/apis/credentials")
        print("  2. Create OAuth 2.0 Client ID (Desktop app type)")
        print("  3. Add redirect URI: http://localhost:8080/")
        print("  4. Copy the Client ID and Client Secret")
        sys.exit(1)

    print("=== YouTube Analytics OAuth Setup ===")
    print(f"Client ID: {CLIENT_ID[:20]}...")
    print(f"Redirect URI: {REDIRECT_URI}")

    code = get_auth_code()
    print("\nExchanging auth code for tokens...")
    tokens = exchange_code(code)

    refresh_token = tokens.get("refresh_token", "")
    access_token = tokens.get("access_token", "")
    expires_in = tokens.get("expires_in", 0)

    if not refresh_token:
        print("\nERROR: No refresh_token returned. Try revoking access at")
        print("https://myaccount.google.com/permissions and running again.")
        sys.exit(1)

    print(f"\n=== SUCCESS ===")
    print(f"Access token (expires in {expires_in}s): {access_token[:50]}...")
    print(f"\nAdd these to GitHub repository secrets:")
    print(f"  YOUTUBE_REFRESH_TOKEN: {refresh_token}")
    print(f"  YOUTUBE_CLIENT_ID:     {CLIENT_ID}")
    print(f"  YOUTUBE_CLIENT_SECRET: {CLIENT_SECRET}")


if __name__ == "__main__":
    main()
