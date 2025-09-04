from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
import hmac, hashlib, time, base64
import requests

# === Load .env Variables ===
load_dotenv()

app = Flask(__name__)

# Helpers for signed tokens
APP_SECRET = os.getenv("APP_SECRET", "change_me")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

def sign_token(email: str, name: str, ttl_secs: int = 3600) -> str:
    ts = int(time.time())
    msg = f"{email}|{name}|{ts}"
    sig = hmac.new(APP_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{msg}|{sig}".encode()).decode()
    return token

def verify_token(token: str, ttl_secs: int = 3600):
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        email, name, ts, sig = raw.split('|')
        if time.time() - int(ts) > ttl_secs:
            return None
        msg = f"{email}|{name}|{ts}"
        expected = hmac.new(APP_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return email, name
    except Exception:
        return None

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mobile-test')
def mobile_test():
    return render_template('mobile_test.html')

# === Resume Request Form Handler ===
@app.route('/request_resume', methods=["POST"])
def request_resume():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if not name or not email:
        return "<h3>❌ Please fill in all fields.</h3>", 400

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = sender_email  # You (Sameer) receive it

    token = sign_token(email, name, ttl_secs=24*3600)
    approve_link = f"{BASE_URL}/approve_resume?token={token}"
    deny_link = f"mailto:{email}?subject=Regarding%20Resume%20Request&body=Hi%20{name},%20thank%20you%20for%20your%20interest.%20Currently%20I’m%20unable%20to%20share%20my%20resume.%20Regards,%20Sameer"

    # Compose the HTML message
    html_content = f"""
    <html>
      <body style="font-family: Arial; background-color: #f4f4f4; padding: 20px;">
        <h2>📄 New Resume Access Request</h2>
        <p><strong>👤 Name:</strong> {name}</p>
        <p><strong>📧 Email:</strong> {email}</p>
        <p>👉 Choose how you want to respond (link valid for 24 hours):</p>
        <a href="{approve_link}" style="background-color:#0ef;color:#000;padding:12px 22px;text-decoration:none;border-radius:6px;font-weight:bold;margin-right:10px;">✅ Approve & Send Resume</a>
        <a href="{deny_link}" style="background-color:#ff4d4d;color:#fff;padding:12px 22px;text-decoration:none;border-radius:6px;font-weight:bold;">❌ Deny Request</a>
        <br><br>
        <p style="font-size: 0.85rem; color: #777;">This message was generated automatically from your portfolio website.</p>
      </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = "📥 Resume Access Request via Portfolio"
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content(f"New resume request from {name} ({email}).")
    msg.add_alternative(html_content, subtype="html")

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        try:
            return render_template('resume_success.html', name=name, email=email)
        except Exception as template_error:
            return f"<h3>✅ Thank you {name}! Sameer will respond shortly to {email}. <br><small>Template Error: {str(template_error)}</small></h3>"
    except Exception as e:
        return f"<h3>❌ Error sending notification email: {str(e)}</h3>", 500


# === Resume Approval Route (token-verified) ===
@app.route('/approve_resume')
def approve_resume():
    token = request.args.get("token", "")
    verified = verify_token(token, ttl_secs=24*3600)
    if not verified:
        return "<h3>❌ Invalid or expired link.</h3>", 400

    hr_email, name = verified

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    resume_path = "static/resume/sameer_resume.pdf"

    cold_email = f"""
Dear {name},

Thank you for showing interest in connecting with me!

I’m glad to share my resume with you. I hold a strong foundation in AI & Data Science and have applied my skills to projects in facial recognition, disease prediction, and IoT systems.

Attached is my resume for your review. I look forward to hearing about any opportunities where I can contribute and grow.

Please feel free to get in touch with any questions!

Warm regards,  
Sameer Shaik  
AI & Data Science Developer  
📧 shaiksameershubhan@gmail.com  
🔗 LinkedIn: https://www.linkedin.com/in/shaik-sameer-69a3422a8  
💻 GitHub: https://github.com/Smr2005
    """

    msg = EmailMessage()
    msg['Subject'] = "📎 Resume from Sameer Shaik"
    msg['From'] = sender_email
    msg['To'] = hr_email
    msg.set_content(cold_email)

    try:
        with open(resume_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="Sameer_Shaik_Resume.pdf"
            )
    except FileNotFoundError:
        return "<h3>❌ Resume file not found. Please upload it to /static/resume/</h3>", 404

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        try:
            return render_template('resume_sent.html', email=hr_email, name=name)
        except Exception as template_error:
            return f"<h3>✅ Resume sent successfully to {hr_email}! <br><small>Template Error: {str(template_error)}</small></h3>"
    except Exception as e:
        return f"<h3>❌ Failed to send resume: {str(e)}</h3>", 500


# === Server-side Chat Proxy (Gemini) ===
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json(silent=True) or {}
    prompt = (data.get('prompt') or '').strip()
    if not prompt:
        return jsonify({ 'error': 'Prompt is required' }), 400

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return jsonify({ 'error': 'Server not configured' }), 500

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        answer = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not answer:
            answer = "I couldn't generate a response right now. Please try again."
        return jsonify({ 'answer': answer })
    except Exception:
        return jsonify({ 'error': 'AI service error' }), 502


# === Start Server ===
if __name__ == "__main__":
    app.run(debug=True)
