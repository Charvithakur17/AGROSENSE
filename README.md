# 🌱 AgroSense: Intelligent Soil Monitoring System

AgroSense is an IoT-based smart agriculture prototype that monitors soil moisture, temperature, humidity, and light in real time.

It uses an ESP32 to send sensor data to a Flask server, which stores it in SQLite and displays it on a live dashboard.

---

## 🚀 Features

- Real-time sensor data collection (ESP32)
- Soil moisture detection (DRY / NORMAL / WET)
- Temperature & humidity monitoring (DHT11)
- Light detection using LDR
- Flask API for data handling
- Live dashboard with charts (Chart.js)
- SQLite database for history

---

## 🧠 Tech Stack

- Hardware: ESP32, DHT11, Soil Moisture Sensor, LDR
- Backend: Flask (Python)
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Charts: Chart.js

---

## 📁 Project Structure

AGROSENSE/
├── arduino_code/
│   └── AGROSENSE/
│       └── AGROSENSE.ino
├── flask_code/
│   └── server.py
├── docs/
│   ├── dashboardimg.jpeg
│   └── dbbrowserimg.jpeg
├── README.md
└── .gitignore

---

## ⚙️ How It Works

1. ESP32 reads sensor data  
2. Sends data to Flask server (POST request)  
3. Flask stores data in SQLite  
4. Dashboard fetches:
   - /latest → current data  
   - /history → past records  
5. Charts display real-time trends  

---

## 🖼️ Preview

### Dashboard
![Dashboard](docs/dashboardimg.jpeg)

### Database
![Database](docs/dbbrowserimg.jpeg)

---

## 🛠️ How to Run

1. Install Flask  
   pip install flask  

2. Run server  
   python flask_code/server.py  

3. Open browser  
   http://localhost:5000  

4. Upload Arduino code to ESP32  
   (Add your WiFi + server IP first)

---

## ⚠️ Limitations

- SQLite is not scalable  
- No authentication yet  
- Runs on local server only  

---

## 🔮 Future Improvements

- Cloud deployment  
- Mobile app  
- Auto irrigation  
- Alerts system  

---

Built as an IoT + Web integration project.
