"""
Standalone OAuth 2.0 setup script for YouTube Analytics.
Run this locally (not in CI) to generate a new refresh token.

Usage:
    python3 scripts/oauth_setup.py

This prints a URL. Open it, authorize, and paste the code back here.
The script will exchange it for tokens and print the refresh token.

Copy the refresh token to the YOUTUBE_REFRESH_TOKEN GitHub secret.
"""

import json
import os
import webbrowser

import requests

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]
# Uses the out-of-band (manual copy) redirect for Desktop app credentials
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob:auto"


def build_auth_url():
    import urllib.parse
    scope_encoded = urllib.parse.quote(" ".join(SCOPES), safe="")
    redirect_encoded = urllib.parse.quote(REDIRECT_URI, safe="")
    client_encoded = urllib.parse.quote(CLIENT_ID, safe="")
    return (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code"
        f"&client_id={client_encoded}"
        f"&redirect_uri={redirect_encoded}"
        f"&scope={scope_encoded}"
        f"&access_type=offline"
        f"&prompt=consent"
        f"&authuser=1"
    )


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        client_id = input("Enter your OAuth 2.0 Client ID: ").strip()
        client_secret = input("Enter your OAuth 2.0 Client Secret: ").strip()
    else:
        client_id = CLIENT_ID
        client_secret = CLIENT_SECRET

    auth_url = build_auth_url()
    print("\nOpen this URL in a browser:")
    print("")
    print("  " + auth_url)
    print("")
    print("Authorize with Skye's YouTube account.")
    print("You'll get a code (long string of characters).")
    print("")

    auth_code = input("Paste the authorization code here: ").strip()
    if not auth_code:
        print("No code provided. Exiting.")
        return

    print("\nExchanging code for tokens...")
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"Token exchange failed ({resp.status_code}): {resp.text}")
        return

    tokens = resp.json()
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
    print(f"  gh secret set YOUTUBE_REFRESH_TOKEN --repo SkiylianSoftware/SkiylianSoftware.github.io --body '{refresh_token}'")


if __name__ == "__main__":
    main()
