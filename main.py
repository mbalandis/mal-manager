import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import PlainTextResponse
import uvicorn
from mal import refresh_token
import json
from dotenv import load_dotenv
import logging
import platform

load_dotenv()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "MAL Token Manager"}


@app.get("/mal/redirect", response_class=PlainTextResponse)
async def read_item(code):
    return code

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != os.environ['APP_TOKEN']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@app.post("/mal/token/refresh")
def refresh_mal_token(token: str = Depends(get_current_user)):
    token = refresh_token()

    return {'access_token': token['access_token'], 'expires_at': token['expires_at'], 'expires_at_h': token['expires_at_h']}


SERVER_PORT = os.getenv('SERVER_PORT_GUEST', 7777)


@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("uvicorn")
    logger.info(f'Running on: {platform.system()}')
    logger.info(
        f"http://localhost:{SERVER_PORT} (Windows)")

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=int(SERVER_PORT))
