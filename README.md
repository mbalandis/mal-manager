# MAL Manager

## Features

- Authenticates and generates new token.
- Maintains MyAnimeList access token and refreshes only when necessary.
- Api with Bearer token support.

## Prerequisites

- Python 3.8 or higher or Docker installed.
- API Config on MyAnimeList (see below).
- Domain (if you want to expose it to the Internet).

## How to use

- Clone this repo on your computer or server.

- Copy .env.example to .env and fill the information.
  - `APP_TOKEN=mysupersecuretoken` is just whatever you want and will be used as Bearer for POST request.

- Docker (recommended)
  - `docker compose up -d`
  - `docker exec -i mal-manager python mal.py` (first time auth)

- Local
  - `pip install -r requirements.txt`
  - `python mal.py` (first time auth)

- Refresh token by running one of these:
- `docker exec -i mal-manager python mal.py --refresh`
- `python mal.py --refresh`
- POST request to https://[yourdomain]/mal/refresh (no parameters)

## MyAnimeList Api Config

- MyAnimeList client_id and secret. Go to <https://myanimelist.net/apiconfig> and create an API Config.
- Set App Type: web.
- Add app redirect URL pointing to https://[yourdomain]/mal/redirect in the MAL API Config Configuration.
- Add homepage https://[yourdomain].
- Fill the rest of required fields.
- Click Submit and if all goes well you should get Client ID and Client Secret which you need to put to .env

If you do not own a domain and won't use it you can try setting to something like: `http://localhost:7777/mal/redirect`.

See this blog post: <https://myanimelist.net/blog.php?eid=835707> for additional help.

## Troubleshooting

- If you get: `requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: https://api.myanimelist.net/v2/users/@me` after running `mal.py` command try again and make sure you have no extra spaces when pasting. You may also need to try waiting 5-10s before pasting after clicking Allow Button. Note that even if you do get that error it probably still works.

## SSL Support

- Out of the box this runs on http and can be safely used locally. But if you want it to be exposed to the world it is highly recommended to generate a SSL certificate with which a domain is a requirement. You can buy domain for less than $10 a year.
  - Option 1: <https://letsencrypt.org/> Automatically refreshes using certbot. If this doesn't work with your particular domain try Option 2.
  - Option 2: <https://zerossl.com/>. Should work with any domain as long as you can access the server and verify it. Drawback is that you would need to refresh it manually every 3 months. With a subscription you can automate it.
  - Option 3: Another way is to use <https://www.cloudflare.com/> Zero Trust Tunnel which will automatically give you a SSL certificate and tunnel it to the container. It has a docker support but the default command fails to work properly. You should include additional docker arguments: `-i` and `--network host`.
  - Option 4: Self-sign (not ideal as api calls would probably need to be set to ignore certificates).
