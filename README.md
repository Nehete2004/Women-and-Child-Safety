# 🛡️ ShieldHer — Women Safety Web Application
### Merged & Enhanced from women_safety_web1 + minor_women_1

---

## 🚀 Features
- ✅ **One-Tap SOS** — sends SMS + WhatsApp + Email simultaneously (Twilio)
- ✅ **Live GPS Location** — Leaflet map with real-time tracking
- ✅ **Shake-to-SOS** — hands-free emergency activation
- ✅ **Emergency Siren** — loud alert sound
- ✅ **Personal Contacts** — add/remove emergency contacts per user
- ✅ **Alert History** — log of all SOS events
- ✅ **ShieldBot AI Chatbot** — instant safety guidance
- ✅ **National Helplines** — quick reference (100, 108, 1091, 112...)
- ✅ **Profile + Photo Upload**
- ✅ **Secure Login/Register** (SQLite)
- ✅ **Beautiful Dark UI** — glass morphism, animated SOS button

---

## ⚙️ Setup

```bash
pip install flask twilio
python app.py
```

Open: http://localhost:5000

---

## 🔑 Twilio Configuration (in app.py)

```python
TWILIO_SID     = "ACebcb641a20b21c6f259f51bef9ccc7ed"
TWILIO_AUTH    = "d5af3cb8c31319009de16dbd3da1edcc"
TWILIO_FROM    = "+19068133480"           # Your Twilio number
TWILIO_WA_FROM = "whatsapp:+14155238886" # Twilio WhatsApp sandbox
ALERT_TO_PHONE = "+918180923222"          # Alert recipient phone
ALERT_TO_WA    = "whatsapp:+918180923222" # Alert recipient WhatsApp
```

---

## 📧 Email Configuration (in app.py)

```python
EMAIL_SENDER   = "rohitnehete@gmail.com"
EMAIL_PASSWORD = "ovcv llcc ctry ukki"   # Gmail App Password
EMAIL_RECEIVER = "neheterohit21@gmail.com"
```

---

## 📁 Project Structure

```
women_safety_merged/
├── app.py                  ← Main Flask app (merged)
├── requirements.txt
├── database/
│   └── women_safety.db     ← SQLite (auto-created)
├── static/
│   ├── style.css           ← Enhanced CSS
│   ├── sounds/
│   │   └── siren.mp3       ← Copy from original project
│   └── uploads/            ← Profile photos
└── templates/
    ├── splash.html
    ├── login.html
    ├── register.html
    ├── dashboard.html      ← Main hub with SOS
    ├── location.html       ← Live map + alert
    ├── profile.html
    ├── alerts.html
    ├── about.html
    └── feature.html
```

---

## ⚠️ Notes
- Copy `siren.mp3` from original project to `static/sounds/siren.mp3`
- WhatsApp requires Twilio Sandbox activation at https://console.twilio.com
- For production: hash passwords, use environment variables for secrets
