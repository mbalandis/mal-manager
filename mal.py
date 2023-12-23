from pathlib import Path
import secrets
import requests
import json
import os
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)

load_dotenv()

# get the absolute path of the directory of the current script
dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

CLIENT_ID = os.environ['MAL_CLIENT_ID']
CLIENT_SECRET = os.environ['MAL_CLIENT_SECRET']

# 1. Generate a new Code Verifier / Code Challenge.


def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)

    with open('code_verifier.txt', 'w') as file:
        json.dump(token, file, indent=4)
        print('Code verifier saved in "code_verifier.txt"')

    return token[:128]

# 2. Print the URL needed to authorise your application.


def print_new_authorisation_url(code_challenge: str):
    global CLIENT_ID

    url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&code_challenge={code_challenge}'
    print(f'Authorise your application by clicking here: {url}\n')

# 3. Once you've authorised your application, you will be redirected to the webpage you've
#    specified in the API panel. The URL will contain a parameter named "code" (the Authorisation
#    Code). You need to feed that code to the application.


def generate_new_token(authorisation_code: str, code_verifier: str) -> dict:
    global CLIENT_ID, CLIENT_SECRET

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorisation_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }

    response = requests.post(url, data)
    response.raise_for_status()  # Check whether the request contains errors

    token = response.json()
    response.close()
    print('Token generated successfully!')

    # Current date and time in UTC
    now = datetime.utcnow()
    expires_in = token['expires_in']
    expires_at = now + timedelta(seconds=expires_in)

    token_expire = {'expires_at': expires_at.timestamp(),
                    'expires_at_h': str(expires_at)}
    token = dict(token_expire, **token)

    with open(dir_path / "token.json", 'w') as file:
        json.dump(token, file, indent=4)

    return token

# 4. Test the API by requesting your profile information


def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers={
        'Authorization': f'Bearer {access_token}'
    })

    response.raise_for_status()
    user = response.json()
    response.close()

    print(Fore.GREEN + f"\n>>> Greetings {user['name']}! <<<")


def refresh_token() -> dict:
    with open(dir_path / "token.json", 'r') as f:
        data = json.load(f)

    now = datetime.utcnow()
    # Set a default for expires_in in case it's not in data
    expires_in = data.get('expires_in', 3600)  # Default to 1 hour

    # Calculate 'expires_at' and 'expires_at_h' if not present in data
    expires_at = data.get('expires_at', (now + timedelta(seconds=expires_in)).timestamp())
    expires_at_h = data.get('expires_at_h', str(now + timedelta(seconds=expires_in)))

    if datetime.utcfromtimestamp(expires_at) <= now:
        print("Token expired, refreshing...")

        url = 'https://myanimelist.net/v1/oauth2/token'
        refresh_data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': data['refresh_token']
        }

        response = requests.post(url, refresh_data)
        response.raise_for_status()

        new_token = response.json()
        response.close()

        # Update the expiration time in the new token
        new_expires_at = now + timedelta(seconds=new_token['expires_in'])
        new_token['expires_at'] = new_expires_at.timestamp()
        new_token['expires_at_h'] = str(new_expires_at)

        with open(dir_path / "token.json", 'w') as file:
            json.dump(new_token, file, indent=4)

        print('Token refreshed successfully!')
        return new_token

    else:
        print("Token is still valid, no need to refresh.")
        # Ensure the existing data has the necessary keys
        data['expires_at'] = expires_at
        data['expires_at_h'] = expires_at_h
        return data


def main():
    parser = argparse.ArgumentParser(
        description="Manage MyAnimeList OAuth tokens.")
    parser.add_argument('--refresh', action='store_true',
                        help="Refresh the OAuth token")

    args = parser.parse_args()

    # Current date and time in UTC
    now = datetime.utcnow()

    if args.refresh:
        token = refresh_token()

        expires_in = token['expires_in']

        expires_at = now + timedelta(seconds=expires_in)

        print("Current date and time in UTC: ",
              now, f'({int(now.timestamp())})')

        print("Expiration date and time in UTC: ",
              expires_at, f'({int(expires_at.timestamp())})')

        print_user_info(token['access_token'])

    else:
        code_verifier = code_challenge = get_new_code_verifier()
        print_new_authorisation_url(code_challenge)

        authorisation_code = input(
            'Copy-paste the Authorisation Code: ').strip()
        token = generate_new_token(authorisation_code, code_verifier)

        print_user_info(token['access_token'])


if __name__ == '__main__':
    main()
