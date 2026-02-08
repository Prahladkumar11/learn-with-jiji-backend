from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User's learning query")

class Resource(BaseModel):
    title: str
    type: str
    url: str

class QueryResponse(BaseModel):
    answer: str
    resources: List[Resource]

class SignUpRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    name: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user: dict
