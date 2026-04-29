from pydantic import BaseModel
from typing import Optional

# What we expect when someone registers or logs in
class UserCreate(BaseModel):
    email: str
    password: str

# What we safely send back to the frontend (Notice: NO password here!)
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    status: str
    team_code: Optional[str] = None
    is_checked_in: bool
    requested_team: Optional[str] = None

    class Config:
        from_attributes = True  # Allows Pydantic to read from your SQLite DB easily
        
# For the JWT login token
class Token(BaseModel):
    access_token: str
    token_type: str