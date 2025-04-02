from pydantic import BaseModel, Field, model_validator
from typing import List,Dict,Optional

class CookieItem(BaseModel):
    domain: str
    expirationDate: Optional[float] = None
    hostOnly: Optional[bool] = None
    httpOnly: Optional[bool] = None
    name: str
    path: str
    sameSite: Optional[str] = None
    secure: Optional[bool] = None
    session: Optional[bool] = None
    storeId: Optional[str] = None
    value: str
    
class UsernameRequest(BaseModel):
    username: str
    cookie: List[CookieItem]
