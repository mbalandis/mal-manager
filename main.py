import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import PlainTextResponse
import uvicorn
from mal import refresh_token
import json

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello From Rimuwu Amazon EC2"}

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

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=7777)
