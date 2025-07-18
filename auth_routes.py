from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from database import conn, cur
from auth import hash_password, create_token, verify_password
import psycopg2

router = APIRouter()

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

@router.post("/signup")
def signup(user: SignupRequest):
    try:
        hashed_pw = hash_password(user.password)
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (user.full_name, user.email, hashed_pw)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        token = create_token(user_id)
        return {"token": token, "full_name": user.full_name}
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Email already exists or invalid data.")

@router.post("/login")
async def login_user(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    try:
        cur.execute("SELECT id, full_name, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user_id, full_name, password_hash = user

    if not verify_password(password, password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_token(user_id)
    return {"token": token, "full_name": full_name}
