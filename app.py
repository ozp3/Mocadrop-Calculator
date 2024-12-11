from flask import Flask, render_template, request
import requests
import time

app = Flask(__name__)

CACHE = {}
SUPPORTED_TOKENS = []

# API'den desteklenen token listesini al
def fetch_supported_tokens():
    global SUPPORTED_TOKENS
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            SUPPORTED_TOKENS = response.json()
        else:
            print(f"API Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")

# Token doğrulama
def is_token_supported(token_id):
    return any(token["id"] == token_id for token in SUPPORTED_TOKENS)

# Token fiyatını önbellek ile al
def get_token_price_cached(token_id, vs_currency="usd"):
    current_time = time.time()
    if token_id in CACHE and current_time - CACHE[token_id]["timestamp"] < 60:
        return CACHE[token_id]["price"]

    # API çağrısı
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies={vs_currency}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            price = response.json().get(token_id, {}).get(vs_currency, None)
            if price is not None:
                CACHE[token_id] = {"price": price, "timestamp": current_time}
            return price
        else:
            print(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token_name = request.form.get("token_name", "").lower()
        if not token_name:
            return render_template("index.html", error="Token name is required.")

        # Token doğrulama
        if not is_token_supported(token_name):
            return render_template("index.html", error=f"Token '{token_name}' is not supported.")

        token_price = get_token_price_cached(token_name)
        if token_price is None:
            return render_template("index.html", error="Failed to fetch token price. Please try again later.")

        return render_template("index.html", token_price=f"{token_price:.4f}$")
    return render_template("index.html")

# Uygulama başlatıldığında desteklenen token listesini al
fetch_supported_tokens()
