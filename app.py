import os
import shutil
import markdown
from fastapi import FastAPI, Request, UploadFile, File, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles 
from database import get_db_connection
import hashlib
import sqlite3
import random 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from parser import extract_text
from nlp_clean import extract_skills, extract_phone, extract_email, extract_linkedin, extract_address 
from similarity import calculate_ats_score, calculate_match_score
from recommender import get_missing_skills, generate_advanced_roadmap, recommend_best_roles
import secrets

# Create the FastAPI server
app = FastAPI(title="CareerLens AI API")

#CSS files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
 
# Landing Page

@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse(request=request, name="landing.html")


# The Signup Page

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")



# The Login UI Page

@app.get("/login", response_class=HTMLResponse)
def login_view(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


# Applicant Dashboard

@app.get("/applicant")
def applicant_dashboard(request: Request, session_email: str = Cookie(None)):
    if session_email is None:
        return RedirectResponse(url="/login", status_code=303)
        
    conn, cursor = get_db_connection()
    cursor.execute("SELECT name, role FROM users WHERE email = ?", (session_email,))
    user = cursor.fetchone()
    
    return templates.TemplateResponse(
        request=request, 
        name="applicant.html", 
        context={"user_name": user[0], "user_role": user[1]}
    )

# The Logout Button

@app.get("/logout")
def logout():
    # Send them to the Landing page...
    response = RedirectResponse(url="/", status_code=303)
    # ...and rip up their ID badge!
    response.delete_cookie(key="session_email")
    return response


# The Email Sender
load_dotenv()
def send_verification_email(receiver_email, secret_code):
    # 1. Your Email Settings
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")
    
    # 2. Build the Email Envelope
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Your CareerLens Verification Code"
    
    # 3. Write the HTML Email Body
    html_content = f"""
    <html>
      <body>
        <h2 style='color: #2c3e50;'>Welcome to CareerLens!</h2>
        <p>Thank you for creating an account. Here is your secret verification code:</p>
        <h1 style='color: #27ae60; background-color: #e2f0d9; padding: 10px; width: fit-content; border-radius: 5px;'>{secret_code}</h1>
        <p>Please type this code into the browser to activate your account.</p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_content, "html"))
    
    # 4. Connect to Google's Mail Server and Send!
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"✅ Real email successfully sent to {receiver_email}!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Send Password Reset Email

def send_password_reset_email(receiver_email, reset_token):
    sender_email = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Reset Your CareerLens Password"
    
    reset_link = f"http://127.0.0.1:8000/reset-password?token={reset_token}"
    
    html_content = f"""
    <html>
      <body>
        <h2 style='color: #2c3e50;'>CareerLens Password Reset</h2>
        <p>You requested to reset your password. Click the secure link below to create a new one:</p>
        <a href='{reset_link}' style='display: inline-block; padding: 10px 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;'>Reset My Password</a>
        <p><small>If you did not request this, please ignore this email.</small></p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_content, "html"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"✅ Password reset email sent to {receiver_email}!")
    except Exception as e:
        print(f"❌ Failed to send reset email: {e}")

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# The Signup Logic

@app.post("/signup")
async def process_signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...) 
):
    # 1. Check if the passwords match!
    if password != confirm_password:
        return templates.TemplateResponse(request=request, name="signup.html", context={"error": "Passwords do not match!"})
    
    # 2. Scramble the password so hackers can't read it
    scrambled_password = hash_password(password)
    
        # 3. Connect to the Vault and save the user
    conn, cursor = get_db_connection()
    try:
        # Generate a random 6 digit code!
        secret_code = str(random.randint(100000, 999999))
        
        # We now save their role AND their secret_code. is_verified defaults to 0 (False).
        cursor.execute("INSERT INTO users (name, email, password_hash, role, phone, verification_code) VALUES (?, ?, ?, ?, ?, ?)", 
                       (name, email, scrambled_password, role, "", secret_code))
        conn.commit()
        
        # ACTUALLY SEND THE REAL EMAIL!
        send_verification_email(email, secret_code)


        
    except sqlite3.IntegrityError:
        return templates.TemplateResponse(request=request, name="signup.html", context={"error": "Email is already registered!"})
    
    # 4. Success! Send them to the Verify page (and pass the email along)
    return templates.TemplateResponse(request=request, name="verify.html", context={"email": email})

#The Verification Check

@app.post("/verify")
async def process_verification(
    request: Request,
    email: str = Form(...),
    code: str = Form(...)
):
    conn, cursor = get_db_connection()
    
    # 1. Look up the exact verification code we saved for this email
    cursor.execute("SELECT verification_code FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    # 2. Check if the code they typed matches the vault!
    if user and user[0] == code:
        # SUCCESS! Upgrade their account to Verified!
        cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
        conn.commit()
        
        # Send them to the Login page now that their account is activated
        return RedirectResponse(url="/login", status_code=303)
    else:
        # FAILURE! Wrong code! Send them back to the verify page with an error.
        return templates.TemplateResponse(request=request, name="verify.html", context={"email": email, "error": "Invalid verification code!"})


# The Real Login & ID Badge System

@app.post("/login")
async def process_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    scrambled_password = hash_password(password)
    conn, cursor = get_db_connection()
    
    # 1. We ask the database for their verification status AND their role!
    cursor.execute("SELECT is_verified, role FROM users WHERE email = ? AND password_hash = ?", 
                   (email, scrambled_password))
    user = cursor.fetchone()
    
    if user:
        is_verified = user[0]
        actual_role = user[1] 
        
        # 2. Did they verify their email?
        if is_verified == 0:
            return templates.TemplateResponse(request=request, name="login.html", context={"error": "Please verify your email first!"})
        
        # 3. SUCCESS! Send them to the right dashboard based on their Vault role!
        if actual_role == "applicant":
            response = RedirectResponse(url="/applicant", status_code=303)
        else:        
            response = RedirectResponse(url="/recruiter", status_code=303)
            
        # 4. Tape a secure "Cookie" (ID Badge) to their browser before sending them!
        response.set_cookie(key="session_email", value=email)
        return response
    else:
        # 5. FAILURE: Wrong email or password
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Incorrect email or password!"})

# Feature 1 (Target a Specific Job)

@app.post("/analyze-job")
async def analyze_resume(
    request: Request, 
    resume: UploadFile = File(...), 
    job_description: str = Form(...),
    session_email: str = Cookie(None)
):
    print("Running Feature 1: Job Match...")
    file_location = f"temp_{resume.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
        
    resume_text = extract_text(file_location)
    found_skills = extract_skills(resume_text)
    
    # EXTRACT AND SAVE DETAILS TO THE NEW TABLE!
    phone_number = extract_phone(resume_text)
    resume_email = extract_email(resume_text)
    linkedin_url = extract_linkedin(resume_text)
    address = extract_address(resume_text)
    
    if session_email:
        conn, cursor = get_db_connection()
        # Save the extracted details to the dedicated resume_details table
        cursor.execute(
            "INSERT INTO resume_details (user_email, phone, resume_email, linkedin_url, address) VALUES (?, ?, ?, ?, ?)", 
            (session_email, phone_number, resume_email, linkedin_url, address)
        )
        conn.commit()
        print(f"✅ Saved resume details for {session_email}!")
    
    
    ats_score = calculate_ats_score(resume_text, found_skills)
    match_score = calculate_match_score(resume_text, job_description)
    
    missing_skills = get_missing_skills(found_skills, job_description)
    career_roadmap = generate_advanced_roadmap(missing_skills, "Target Role")
    roadmap_html = markdown.markdown(career_roadmap)
    
    os.remove(file_location)
    
    return templates.TemplateResponse(
        request=request, 
        name="results.html", 
        context={
            "ats_score": ats_score,
            "match_score": match_score,
            "skills_found": found_skills,
            "roadmap": roadmap_html
        }
    )


# Feature 2 (Discover Best Roles)

@app.post("/discover-roles")
async def discover_roles(
    request: Request,
    resume: UploadFile = File(...)
):
    print("Running Feature 2: Role Discovery...")
    file_location = f"temp_{resume.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
        
    resume_text = extract_text(file_location)
    found_skills = extract_skills(resume_text)
    
    best_roles = recommend_best_roles(found_skills)
    roles_html = markdown.markdown(best_roles)
    
    os.remove(file_location)
    
    return templates.TemplateResponse(
        request=request, 
        name="discover_results.html", 
        context={
            "skills_found": found_skills,
            "roles": roles_html
        }
    )


# Recruiter Dashboard (SECURED)

@app.get("/recruiter")
def recruiter_dashboard(request: Request, session_email: str = Cookie(None)):
    if session_email is None:
        return RedirectResponse(url="/login", status_code=303)
        
    # NEW: Fetch their Name and Role from the Vault!
    conn, cursor = get_db_connection()
    cursor.execute("SELECT name, role FROM users WHERE email = ?", (session_email,))
    user = cursor.fetchone()
        
    return templates.TemplateResponse(
        request=request, 
        name="recruiter.html", 
        context={"user_name": user[0], "user_role": user[1]}
    )

# Feature 4 Bulk AI Ranking
@app.post("/rank-resumes")
async def rank_resumes(
    request: Request,
    job_description: str = Form(...),
    resumes: list[UploadFile] = File(...),
    session_email: str = Cookie(None)
):
    if session_email is None:
        return RedirectResponse(url="/login", status_code=303)
        
    print(f"Recruiter uploaded {len(resumes)} resumes for ranking!")
    
    rankings = []
    
    # Loop through every single PDF they uploaded!
    for resume in resumes:
        # 1. Save file temporarily
        file_location = f"temp_{resume.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
            
        # 2. Extract text and all candidate details!
        resume_text = extract_text(file_location)
        phone = extract_phone(resume_text)
        email = extract_email(resume_text)
        linkedin = extract_linkedin(resume_text)
        address = extract_address(resume_text)
        
        # 3. Calculate Score
        match_score = calculate_match_score(resume_text, job_description)
        
        # 4. Clean up file
        os.remove(file_location)
        
        # 5. Add candidate to our leaderboard list
        rankings.append({
            "filename": resume.filename,
            "score": int(match_score),
            "phone": phone,
            "email": email,
            "linkedin": linkedin,
            "address": address
        })
        
    # 6. Sort the leaderboard from highest score to lowest score!
    rankings = sorted(rankings, key=lambda x: x['score'], reverse=True)
    
    # 7. Send the sorted leaderboard back to the UI!
    return templates.TemplateResponse(
        request=request, 
        name="recruiter.html", 
        context={"rankings": rankings}
    )

# Forgot Password

@app.get("/forgot-password")
def forgot_password_page(request: Request):
    # Note: Using your exact spelling 'forget_password.html'!
    return templates.TemplateResponse(request=request, name="forget_password.html")


@app.post("/forgot-password")
async def process_forgot_password(request: Request, email: str = Form(...)):
    conn, cursor = get_db_connection()
    
    # 1. Check if the user exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user:
        # 2. Generate a secure, 32-character random token (e.g., 'a8f9b2...')
        reset_token = secrets.token_hex(16)
        
        # 3. Save the token to their database row!
        cursor.execute("UPDATE users SET reset_token = ? WHERE email = ?", (reset_token, email))
        conn.commit()
        
        # 4. Email them the link!
        send_password_reset_email(email, reset_token)
        
        # Even if they exist, we show a generic message
        return templates.TemplateResponse(
            request=request, 
            name="forget_password.html", 
            context={"success": "If that email exists, a reset link has been sent to it!"}
        )
    else:
        # We show the exact same success message even if it failed.
        return templates.TemplateResponse(
            request=request, 
            name="forget_password.html", 
            context={"success": "If that email exists, a reset link has been sent to it!"}
        )

# Reset Password

@app.get("/reset-password")
def reset_password_page(request: Request, token: str):
    # Pass the token from the URL directly into the HTML template!
    return templates.TemplateResponse(request=request, name="reset_password.html", context={"token": token})


@app.post("/reset-password")
async def process_reset_password(
    request: Request, 
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    # 1. Did they type the same password twice?
    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request, name="reset_password.html", 
            context={"token": token, "error": "Passwords do not match!"}
        )
        
    conn, cursor = get_db_connection()
    
    # 2. Look in the database for the exact secret token!
    cursor.execute("SELECT email FROM users WHERE reset_token = ?", (token,))
    user = cursor.fetchone()
    
    if user:
        # 3. They match! Hash the new password...
        scrambled_password = hash_password(new_password)
        email = user[0]
        
        # 4. Update the password and SHRED the token so it can never be used again!
        cursor.execute("UPDATE users SET password_hash = ?, reset_token = NULL WHERE email = ?", (scrambled_password, email))
        conn.commit()
        
        # 5. Send them back to the login page!
        return RedirectResponse(url="/login", status_code=303)
    else:
        # Hackers! Invalid or expired token!
        return templates.TemplateResponse(
            request=request, name="reset_password.html", 
            context={"token": token, "error": "Invalid or expired reset link!"}
        )
