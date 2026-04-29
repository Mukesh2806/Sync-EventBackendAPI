import io
import csv
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app import models, schemas, auth, database
from app.database import engine, get_db
import smtplib
from email.message import EmailMessage
from fastapi import BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import FileResponse
import qrcode
from dotenv import load_dotenv
import base64
from io import BytesIO
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sync API", description="Event Management & Team Sync Platform")
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_path)



@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return current_user



# --- CORE ROUTES: SIGN-UP & SIGN-IN ---

@app.post("/signup", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    load_dotenv()
    MASTER_ADMIN_EMAIL = os.getenv("MASTER_ADMIN_EMAIL")
    hashed_password = auth.get_password_hash(user.password)
    assigned_role = "admin" if user.email == MASTER_ADMIN_EMAIL else "user"
    #used a dummy admin... email:admin123@gmail.com password:hello123
    new_user = models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        role=assigned_role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- ADMIN DATA WRANGLING ROUTES ---
@app.get("/admin-panel")
def serve_admin(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html")

@app.get("/dashboard")
def serve_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="user.html")

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    MASTER_ADMIN_EMAIL = os.getenv("MASTER_ADMIN_EMAIL")
    
    if current_user.email != MASTER_ADMIN_EMAIL and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access Denied: Only the Master Admin can view this."
        )
    return current_user



# 1. View all users
@app.get("/admin/users", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    users = db.query(models.User).all()
    return users

@app.post("/admin/users/{user_id}/toggle-checkin")
def toggle_checkin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_checked_in = not user.is_checked_in 
    db.commit()
    
    return {"message": "Success", "is_checked_in": user.is_checked_in}

# 2. Update a user's status
@app.put("/admin/users/{user_id}/status")
def update_user_status(user_id: int, new_status: str, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.status = new_status
    db.commit()
    db.refresh(user)
    return {"message": f"User {user.email} status updated to {new_status}"}

@app.get("/admin/export")
def export_users_csv(
    background_tasks: BackgroundTasks, # <--- Added this!
    db: Session = Depends(get_db), 
    admin: models.User = Depends(get_current_admin)
):
    users = db.query(models.User).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Email", "Role", "Status", "Team Code"])
    
    for user in users:
        writer.writerow([user.id, user.email, user.role, user.status, user.team_code])
    csv_string_data = output.getvalue()
    background_tasks.add_task(send_csv_email, admin.email, csv_string_data)
    
    output.seek(0)
    return StreamingResponse(
        output, 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=sync_attendees.csv"}
    )
    
# --- HELPER FUNCTION: SEND EMAIL ---
def send_csv_email(admin_email: str, csv_string: str):
    load_dotenv()
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    msg = EmailMessage()
    msg['Subject'] = 'Sync API: Your Attendee Report'
    msg['From'] = SENDER_EMAIL
    msg['To'] = admin_email
    msg.set_content('Hello Admin,\n\nPlease find the latest Sync API attendee report attached to this email.')
    msg.add_attachment(
        csv_string.encode('utf-8'), 
        maintype='text', 
        subtype='csv', 
        filename='sync_attendees.csv'
    )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
            print(f"Success: Email sent to {admin_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        
# --- EXTRA FEATURES: TEAM SYNCING ---
# 1. Attendees can join a team by setting a Team Code
@app.put("/users/me/team", response_model=schemas.UserResponse)
def join_team(team_code: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    current_user.team_code = team_code
    db.commit()
    db.refresh(current_user)
    return current_user

# 2. Admins can view everyone in a specific team
@app.get("/admin/teams/{team_code}", response_model=list[schemas.UserResponse])
def get_team_members(team_code: str, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    team_members = db.query(models.User).filter(models.User.team_code == team_code).all()
    return team_members

# --- QR CODE GENERATOR ---
@app.get("/users/me/qr")
def get_my_qr(current_user: models.User = Depends(get_current_user)):
    qr_data = f"USER_ID:{current_user.id}"
    qr = qrcode.make(qr_data)
    
    buf = BytesIO()
    qr.save(buf, format="PNG")
    img_str = base64.b64encode(buf.getvalue()).decode()
    return {"qr_code": f"data:image/png;base64,{img_str}"}

# --- FEATURES: LIVE ANNOUNCEMENTS ---
@app.post("/admin/announcements")
def post_announcement(content: str, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    new_announcement = models.Announcement(content=content)
    db.add(new_announcement)
    db.commit()
    return {"message": "Announcement posted!"}

@app.get("/announcements")
def get_announcements(db: Session = Depends(get_db)):
    return db.query(models.Announcement).order_by(models.Announcement.timestamp.desc()).all()

# ---TOGGLING---
@app.post("/toggle-checkin/{user_id}")
def toggle_checkin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status == "Checked-In":
        user.status = "Pending"
    else:
        user.status = "Checked-In"      
    db.commit()
    return {"message": "Success", "new_status": user.status}

