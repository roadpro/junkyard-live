from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TARGETS = [
    "HONDA ACCORD",
    "FORD F-150",
    "HONDA CIVIC",
    "TOYOTA CAMRY",
    "CHEVROLET SILVERADO"
]

URL = "https://www.pullapart.com/inventory/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

@app.route("/")
def home():
    r = requests.get(URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text().upper()

    found = [v for v in TARGETS if v in text]

    html = "<h2>Cleveland West – Fresh Pull List</h2>"
    if not found:
        html += "<p>No target vehicles detected.</p>"
    for v in found:
        html += f"<p>✅ {v}</p>"

    return html

if __name__ == "__main__":
    app.run()
