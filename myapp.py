from flask import Flask, render_template, request, send_from_directory
from dotenv import load_dotenv
import os
import base64
import requests

# === Load environment variables ===
load_dotenv()

app = Flask(__name__)

# === Home route ===
@app.route('/')
def index():
    return render_template('index.html')


# === Resume Request Form Handler ===
@app.route('/Access_Resume', methods=["POST"])
def request_resume():
    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return "<h3>❌ Please fill in all fields.</h3>"

    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        return "<h3>❌ Brevo API key missing. Check your environment variables.</h3>"

    approve_link = f"https://sameer-portfolio-ta3w.onrender.com/approve_resume?email={email}&name={name}"
    deny_link = f"mailto:{email}?subject=Regarding%20Resume%20Request"

    # Email content
    html_content = f"""
    <html>
      <body style="font-family: Arial; background-color: #f4f4f4; padding: 20px;">
        <h2>📄 New Resume Access Request</h2>
        <p><strong>👤 Name:</strong> {name}</p>
        <p><strong>📧 Email:</strong> {email}</p>
        <p>👉 Choose how you want to respond:</p>
        <a href="{approve_link}" style="background-color:#0ef;color:#000;padding:12px 22px;text-decoration:none;border-radius:6px;font-weight:bold;margin-right:10px;">✅ Approve & Send Resume</a>
        <a href="{deny_link}" style="background-color:#ff4d4d;color:#fff;padding:12px 22px;text-decoration:none;border-radius:6px;font-weight:bold;">❌ Deny Request</a>
        <br><br>
        <p style="font-size: 0.85rem; color: #777;">This message was generated automatically from your portfolio website.</p>
      </body>
    </html>
    """

    data = {
        "sender": {"email": "shaiksameershubhan71@gmail.com", "name": "Sameer Portfolio"},
        "to": [{"email": "shaiksameershubhan71@gmail.com"}],
        "subject": "📥 Resume Access Request via Portfolio",
        "htmlContent": html_content
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": api_key,
                "Content-Type": "application/json"
            },
            json=data,
            timeout=15
        )
        if response.status_code == 201:
            return render_template('resume_success.html', name=name, email=email)
        else:
            return f"<h3>❌ Brevo API error: {response.status_code} - {response.text}</h3>"
    except Exception as e:
        return f"<h3>❌ Network error while sending email: {str(e)}</h3>"


# === Approve Resume Route ===
@app.route('/approve_resume')
def approve_resume():
    hr_email = request.args.get("email")
    name = request.args.get("name")

    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        return "<h3>❌ Brevo API key missing in environment variables.</h3>"

    resume_path = "static/resume/sameer_resume.pdf"
    if not os.path.exists(resume_path):
        return "<h3>❌ Resume file not found. Please upload it to /static/resume/</h3>"

    with open(resume_path, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode()

    cold_email = f"""
    Dear {name},

    Thank you for showing interest in connecting with me!

    I'm glad to share my resume with you. I hold a strong foundation in AI & Data Science and have applied my skills to projects in facial recognition, disease prediction, and IoT systems.

    Attached is my resume for your review. I look forward to hearing about any opportunities where I can contribute and grow.

    Please feel free to get in touch with any questions!

    Warm regards,  
    Sameer Shaik  
    AI & Data Science Developer  
    📧 shaiksameershubhan71@gmail.com  
    🔗 LinkedIn: https://www.linkedin.com/in/shaik-sameer-shubhan-2598563a0
    💻 GitHub: https://github.com/ShaikSameerShubhan0089
    """

    data = {
        "sender": {"email": "shaiksameershubhan71@gmail.com", "name": "Sameer Shaik"},
        "to": [{"email": hr_email, "name": name}],
        "subject": "📎 Resume from Sameer Shaik",
        "textContent": cold_email,
        "attachment": [
            {"content": pdf_base64, "name": "Sameer_Shaik_Resume.pdf"}
        ]
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": api_key,
                "Content-Type": "application/json"
            },
            json=data,
            timeout=15
        )

        if response.status_code == 201:
            return render_template('resume_sent.html', email=hr_email, name=name)
        else:
            return f"<h3>❌ Failed to send via Brevo API: {response.status_code} - {response.text}</h3>"
    except Exception as e:
        return f"<h3>❌ Network or API Error: {str(e)}</h3>"


# === Chat API Route ===
@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        if data is None:
            return {"error": "Invalid JSON or missing Content-Type header"}, 400
        
        question = data.get('question', '').strip()
        
        if not question:
            return {"error": "No question provided"}, 400
    except Exception as e:
        return {"error": f"Request parsing error: {str(e)}"}, 400
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return {"error": "Groq API key not configured"}, 500
    
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    sameer_facts = """
PERSONAL INFORMATION:
- Name: Shaik Sameer
- Email: shaiksameershubhan71@gmail.com
- LinkedIn: https://www.linkedin.com/in/shaik-sameer-shubhan-2598563a0
- GitHub: https://github.com/ShaikSameerShubhan0089
- Phone: +91 9652879470
- Location: India

EDUCATION:
- B.Tech in AI & Data Science from Aditya College of Engineering (2021–2026)
- Intermediate in Maths, Physics, Chemistry at Vidyanikethan Junior College (2020–2022)

TECHNICAL SKILLS:
- Programming Languages: Python, JavaScript, HTML, CSS
- Frameworks & Libraries: Flask, Streamlit, OpenCV, Pandas, NumPy
- Databases: MySQL
- Tools & Technologies: Power BI, Git, GitHub, VS Code
- AI/ML: Computer Vision, Data Analysis, Machine Learning

PROJECTS:
1. CarbonSphere AI - Enterprise Geospatial AI platform for forest carbon credit estimation using satellite imagery (Sentinel-2) and HSV-based tree segmentation. Implements IPCC Tier 1 biomass models.
2. QueryVault AI - AI-powered Database Query Optimization Platform that analyzes SQL queries using 4 intelligent agents (Optimizer, Cost, Schema, Data) for real-time recommendations. Built with FastAPI, MariaDB, and Groq.
3. RISE (Risk Identification System for Early Detection) - AI-powered Clinical Decision Support System (CDSS) for early autism detection in children (0-6y) using XGBoost and SHAP explainability (ROC-AUC: 0.92).
4. Facial Recognition System - OpenCV and Python for real-time face detection and recognition.
5. Disease Prediction App - ML application for predicting multiple diseases based on symptoms.
6. Personal Portfolio Website - Modern 3D portfolio with AI chatbot integration.
7. IoT Gas Leak Detection System - IoT-based safety system for detecting gas leaks.
8. AutoFeel - Car Sentiment Analyzer using NLP for car brands.

INTERNSHIPS & EXPERIENCE:
- AI Intern at TechSaksham Edunet Foundation
- Data Science Intern at SkillDzire Technologies
- Data Analytics Intern at APSCHE x SmartBridge
Job Roles:
- IT Exective at Agile CAS
"""
    
    system_prompt = f"""You are Laddu, Sameer's friendly AI assistant for his personal portfolio website. You should act as Sameer's enthusiastic and professional assistant, answering questions about him with personality and charm.

Use only the facts below to answer questions about Sameer. If someone asks something not covered in the facts, politely redirect them to ask about Sameer's skills, projects, education, or experience.

Keep responses conversational, helpful, and professional. Always refer to Sameer in third person. Keep responses concise but informative. Do not mention the hyperlinks or URLs unless specifically asked.

FACTS ABOUT SAMEER:
{sameer_facts}
"""
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"Groq API Response Status: {response.status_code}")
        print(f"Groq API Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            reply = data['choices'][0]['message']['content']
            return {"reply": reply}
        else:
            error_detail = response.text
            print(f"Groq API Error: {error_detail}")
            return {"error": f"Groq API error: {response.status_code} - {error_detail}"}, response.status_code
    
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return {"error": f"Chat error: {str(e)}"}, 500


# === Favicon Routes ===
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/images', 'favicon.ico')


# === Start Flask App ===
if __name__ == "__main__":
    app.run(debug=True)



