# 📌 Instagram Pending Follow Requests Cleaner

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/Selenium-Automation-green?logo=selenium" />
  <img src="https://img.shields.io/badge/Status-Working-success" />
</p>

---

## ✨ About

Tired of sending too many follow requests on Instagram and not remembering who you sent them to?  
This tool automatically **cancels all your pending follow requests** one by one.

✅ Supports **English & Turkish** Instagram UI  
✅ Detects **Requested / İstek Gönderildi** buttons  
✅ Handles confirmation popups automatically  
✅ Exports a clean result log: `results_cancel_follow_requests.csv`  

---

## 📂 Project Structure

├── cancel_follow_requests.py # Main script
├── pending_follow_requests.csv # Input file (your Instagram data)
├── results_cancel_follow_requests.csv # Output log
└── requirements.txt # Dependencies


---




🔑 Setup

Go to Instagram → Download Your Data → Export pending requests.

Save it as pending_follow_requests.csv (must contain a username column).

Run the script:

python cancel_follow_requests.py

⚠️ Disclaimer
Use responsibly. Instagram may apply rate limits or block automation if abused.

⭐ Contribute

Pull requests are welcome!
If you find new button texts (different languages), feel free to add them.
