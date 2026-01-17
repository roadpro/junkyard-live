from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Target vehicles
TARGETS = ["HONDA ACCORD", "FORD F-150", "HONDA CIVIC", "TOYOTA CAMRY", "CHEVROLET SILVERADO"]

# Cleveland West Inventory
INVENTORY_URL = "https://www.pullapart.com/Inventory/Cleveland-West"
HEADERS = {"User-Agent": "Mozilla/5.0 (Junkyard Planner)"}

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Junkyard Pull List</title>
<style>
body { font-family: Arial; padding: 16px; }
h1 { font-size: 22px; }
.vehicle { margin: 12px 0; font-size: 18px; }
.part { margin-left: 16px; font-size: 16px; }
</style>
</head>
<body>
<h1>Cleveland West – Fresh Pull List</h1>
{% if vehicles %}
    {% for v in vehicles %}
      <div class="vehicle">✅ {{ v['name'] }}</div>
      {% for part in v['parts'] %}
        <div class="part">• {{ part }}</div>
      {% endfor %}
    {% endfor %}
{% else %}
<p>No target vehicles detected.</p>
{% endif %}
</body>
</html>
"""

def scrape_vehicle_list():
    """Scrape the Cleveland West inventory page for target vehicles."""
    r = requests.get(INVENTORY_URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    vehicles = []
    for h3 in soup.find_all("h3"):
        text = h3.get_text(strip=True).upper()
        for target in TARGETS:
            if target in text:
                link_tag = h3.find_parent("a")  # link to vehicle detail page
                link = link_tag["href"] if link_tag else None
                vehicles.append({"name": text, "url": link})
    return vehicles

def scrape_parts(vehicle_url):
    """Scrape a vehicle page for parts and prices."""
    if not vehicle_url:
        return ["Parts page not found"]
    r = requests.get(vehicle_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    parts = []
    # Pull-A-Part lists parts inside elements with class "part-name" or similar
    for item in soup.select(".part-name"):
        name = item.get_text(strip=True)
        price_tag = item.find_next(class_="part-price")
        price = price_tag.get_text(strip=True) if price_tag else ""
        parts.append(f"{name} {price}".strip())
    if not parts:
        parts = ["No parts listed / may need manual check"]
    return parts

@app.route("/")
def home():
    vehicles = scrape_vehicle_list()
    # scrape parts only for top N vehicles (to keep load light)
    for v in vehicles[:10]:  # adjust number if needed
        v['parts'] = scrape_parts(v.get("url"))
    return render_template_string(HTML_TEMPLATE, vehicles=vehicles)

if __name__ == "__main__":
    app.run()
