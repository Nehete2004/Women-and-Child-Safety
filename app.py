from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from twilio.rest import Client
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================
#  WOMEN SAFETY WEB APPLICATION - MERGED
#  Combines: women_safety_web1 + minor_women_1
# ============================================================

app = Flask(__name__)
app.secret_key = "womensafety_secret_2025"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- TWILIO CONFIG ----------------
TWILIO_SID    = "ACebcb641a20b21c6f259f51bef9ccc7ed"
TWILIO_AUTH   = "a8b3c95b6c8bd0fc0a7f09a5cbc2fe43"
TWILIO_FROM   = "+19068133480"                  # Your Twilio SMS number
#TWILIO_WA_FROM = "whatsapp:+14155238886"        # Twilio WhatsApp sandbox
ALERT_TO_PHONE = "+918180923222"                # Registered phone
#ALERT_TO_WA    = "whatsapp:+918180923222"       # Verified WhatsApp

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

# ---------------- EMAIL CONFIG ----------------
EMAIL_SENDER   = "rohitnehete21@gmail.com"
EMAIL_PASSWORD = "ovcv llcc ctry ukki"          # App password
EMAIL_RECEIVER = "neheterohit21@gmail.com"

# ============================================================
#  DATABASE SETUP  (SQLite - single file)
# ============================================================

DB_PATH = "database/women_safety.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    os.makedirs("database", exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email    TEXT UNIQUE,
            password TEXT NOT NULL,
            phone    TEXT,
            image    TEXT
        )
    """)

    # Emergency contacts (per user)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name    TEXT,
            phone   TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # SOS / alert log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            username  TEXT,
            latitude  REAL,
            longitude REAL,
            location  TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

create_tables()

# ============================================================
#  HELPERS
# ============================================================

def current_user():
    return session.get("user_id")

def send_email_alert(username, location_link):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🚨 SOS Emergency Alert - Women Safety App"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER
        body = f"""
🚨 EMERGENCY ALERT 🚨

User {username} may be in danger!

Live Location:
{location_link}

👉 Click the link above to track location on Google Maps.

— Women Safety System
"""
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email error:", e)
        return False

def get_user_contacts(user_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT name, phone FROM contacts WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def normalize_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+91" + phone
    return phone

def send_twilio_sms(username, location_link, user_id=None):
    sms_body = (
        f"\U0001f6a8 EMERGENCY ALERT!\n"
        f"User '{username}' needs help!\n"
        f"\U0001f4cd Location: {location_link}\n"
        f"\u2014 ShieldHer Safety App"
    )
    sent_count = 0
    try:
        twilio_client.messages.create(body=sms_body, from_=TWILIO_FROM, to=ALERT_TO_PHONE)
        sent_count += 1
        print(f"SMS -> admin {ALERT_TO_PHONE}")
    except Exception as e:
        print(f"SMS admin failed: {e}")
    if user_id:
        for c in get_user_contacts(user_id):
            try:
                phone = normalize_phone(c["phone"])
                twilio_client.messages.create(body=sms_body, from_=TWILIO_FROM, to=phone)
                sent_count += 1
                print(f"SMS -> {c['name']} ({phone})")
            except Exception as e:
                print(f"SMS {c['name']} failed: {e}")
    return sent_count > 0

def send_twilio_whatsapp(username, location_link, user_id=None):
    wa_body = (
        f"\U0001f6a8 EMERGENCY ALERT!\n"
        f"{username} may be in danger!\n\n"
        f"Live Location: {location_link}\n\n"
        f"Sent by ShieldHer Safety App"
    )
    sent_count = 0
    try:
        twilio_client.messages.create(body=wa_body, from_=TWILIO_WA_FROM, to=ALERT_TO_WA)
        sent_count += 1
        print("WhatsApp -> admin")
    except Exception as e:
        print(f"WhatsApp admin failed: {e}")
    if user_id:
        for c in get_user_contacts(user_id):
            try:
                phone = normalize_phone(c["phone"])
                twilio_client.messages.create(body=wa_body, from_=TWILIO_WA_FROM, to=f"whatsapp:{phone}")
                sent_count += 1
                print(f"WhatsApp -> {c['name']} ({phone})")
            except Exception as e:
                print(f"WhatsApp {c['name']} failed: {e}")
    return sent_count > 0

# ============================================================
#  ROUTES - AUTH
# ============================================================

@app.route("/")
def splash():
    if current_user():
        return redirect("/dashboard")
    return render_template("splash.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        email    = request.form.get("email","").strip()
        password = request.form.get("password","")

        if not username or not password:
            flash("⚠️ Username & Password required")
            return redirect("/register")

        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone():
            conn.close()
            flash("⚠️ Username already taken")
            return redirect("/register")

        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (?,?,?)",
            (username, email, password)
        )
        conn.commit()
        conn.close()
        flash("✅ Registered! Please login.")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")

        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"]   = user["id"]
            session["username"]  = user["username"]
            return redirect("/dashboard")
        else:
            flash("❌ Invalid credentials")
            return redirect("/login")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ============================================================
#  ROUTES - MAIN
# ============================================================

@app.route("/dashboard")
def dashboard():
    if not current_user():
        return redirect("/login")

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE user_id=?", (current_user(),))
    contacts = cur.fetchall()
    conn.close()

    return render_template("dashboard.html",
                           username=session.get("username"),
                           contacts=contacts)

@app.route("/profile", methods=["GET","POST"])
def profile():
    if not current_user():
        return redirect("/login")

    conn = get_db()
    cur  = conn.cursor()

    if request.method == "POST":
        name  = request.form.get("name","")
        phone = request.form.get("phone","")
        cur.execute("UPDATE users SET username=?, phone=? WHERE id=?",
                    (name, phone, current_user()))
        conn.commit()
        session["username"] = name
        flash("✅ Profile updated!")
        return redirect("/profile")

    cur.execute("SELECT * FROM users WHERE id=?", (current_user(),))
    user = cur.fetchone()
    conn.close()
    return render_template("profile.html", user=user)

@app.route("/upload_image", methods=["POST"])
def upload_image():
    if not current_user():
        return redirect("/login")
    if "image" not in request.files:
        return redirect("/profile")
    file = request.files["image"]
    if file.filename == "":
        return redirect("/profile")
    filename = f"user_{current_user()}_{file.filename}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    conn = get_db()
    conn.execute("UPDATE users SET image=? WHERE id=?", (filename, current_user()))
    conn.commit()
    conn.close()
    return redirect("/profile")

@app.route("/add_contact", methods=["POST"])
def add_contact():
    if not current_user():
        return redirect("/login")
    name  = request.form.get("name","")
    phone = request.form.get("phone","")
    conn  = get_db()
    conn.execute("INSERT INTO contacts (user_id,name,phone) VALUES (?,?,?)",
                 (current_user(), name, phone))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/delete_contact/<int:cid>")
def delete_contact(cid):
    if not current_user():
        return redirect("/login")
    conn = get_db()
    conn.execute("DELETE FROM contacts WHERE id=? AND user_id=?", (cid, current_user()))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# ============================================================
#  ROUTES - SOS / ALERTS
# ============================================================

@app.route("/location")
def location_page():
    if not current_user():
        return redirect("/login")
    return render_template("location.html", username=session.get("username"))

@app.route("/send_alert")
def send_alert():
    """Called from location.html - sends SMS + WhatsApp + saves to DB"""
    if not current_user():
        return redirect("/login")

    username = session.get("username")
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    if not lat or not lng:
        return "❌ Location not available."
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except ValueError:
        return "❌ Invalid coordinates."

    location_link = f"https://www.google.com/maps?q={lat},{lng}"

    # Save to DB
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO alerts (user_id, username, latitude, longitude, location) VALUES (?,?,?,?,?)",
            (current_user(), username, lat_f, lng_f, location_link)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB error:", e)

    results = []
    if send_email_alert(username, location_link):
        results.append("Email ✅")
    else:
        results.append("Email ❌")

    if send_twilio_sms(username, location_link, user_id=current_user()):
        results.append("SMS ✅")
    else:
        results.append("SMS ❌")

    if send_twilio_whatsapp(username, location_link, user_id=current_user()):
        results.append("WhatsApp ✅")
    else:
        results.append("WhatsApp ❌")

    return f"🚨 Alert sent — {' | '.join(results)}"

@app.route("/send_sos_email", methods=["POST"])
def send_sos_email():
    """AJAX endpoint called from dashboard SOS button"""
    if not current_user():
        return jsonify({"error": "Unauthorized"})

    data = request.get_json()
    if not data or "location" not in data:
        return jsonify({"error": "No location"})

    location = data["location"]
    username = session.get("username")

    # Save
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO alerts (user_id, username, location) VALUES (?,?,?)",
            (current_user(), username, location)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB error:", e)

    ok_email = send_email_alert(username, location)
    ok_sms   = send_twilio_sms(username, location, user_id=current_user())
    ok_wa    = send_twilio_whatsapp(username, location, user_id=current_user())

    return jsonify({
        "status": "sent",
        "email": ok_email,
        "sms": ok_sms,
        "whatsapp": ok_wa
    })

@app.route("/alerts")
def view_alerts():
    if not current_user():
        return redirect("/login")
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 50")
    alerts = cur.fetchall()
    conn.close()
    return render_template("alerts.html", alerts=alerts)

# ============================================================
#  ROUTES - MISC
# ============================================================

@app.route("/about")
def about():
    if not current_user():
        return redirect("/login")
    return render_template("about.html")

@app.route("/feature/<n>")
def feature_page(n):
    return render_template("feature.html", feature=n)

# ============================================================
#  RUN
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
