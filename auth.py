from fastapi import HTTPException, Header
import os
from dotenv import load_dotenv

load_dotenv()
VALID_API_KEYS = os.getenv("API_KEYS").split(",")

def verify_api_key(api_key: str = Header(None)):
    return True
#    if api_key not in VALID_API_KEYS:
#        raise HTTPException(status_code=403, detail="Invalid API Key")