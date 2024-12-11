from flask import Flask, render_template, request
import requests
import time

app = Flask(__name__)

# Token fiyatını almak için CoinGecko API çağrısı
def get_token_price(token_id, vs_currency="usd"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies={vs_currency}&ts={int(time.time())}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get(token_id, {}).get(vs_currency, None)
        else:
            print(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return None

# Desteklenen token'ları almak için CoinGecko API çağrısı
def get_supported_tokens():
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return []

# Token'ın desteklenip desteklenmediğini kontrol et
def is_token_supported(token_id, supported_tokens):
    return any(token["id"] == token_id for token in supported_tokens)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        tokens_offered = int(request.form.get("tokens_offered"))
        your_sp_burn = int(request.form.get("your_sp_burn"))
        total_sp_burnt = int(request.form.get("total_sp_burnt"))

        custom_price_checkbox = request.form.get("custom_price_checkbox")
        if custom_price_checkbox:
            try:
                custom_price = request.form.get("custom_price")
                if not custom_price:
                    return render_template("index.html", error="Custom price is required.")
                token_price = float(custom_price)
                token_name = "Custom Price"
            except ValueError:
                return render_template("index.html", error="Invalid custom price. Please enter a valid number.")
        else:
            token_name = request.form.get("token_name", "").lower()
            if not token_name:
                return render_template("index.html", error="Token name is required.")
            
            supported_tokens = get_supported_tokens()
            if not is_token_supported(token_name, supported_tokens):
                return render_template("index.html", error=f"Token '{token_name}' is not supported.")

            token_price = get_token_price(token_name)
            if token_price is None:
                return render_template("index.html", error="Failed to fetch token price. Please try again later.")

        reward = your_sp_burn * (tokens_offered / total_sp_burnt) * token_price

        return render_template(
            "index.html",
            token_name=token_name.upper(),
            token_price=f"{token_price:.4f}$",
            tokens_offered=f"{tokens_offered:,}",
            your_sp_burn=f"{your_sp_burn:,}",
            total_sp_burnt=f"{total_sp_burnt:,}",
            reward=f"{reward:.2f}$",
            custom_price_checked=bool(custom_price_checkbox),
        )
    return render_template("index.html")
