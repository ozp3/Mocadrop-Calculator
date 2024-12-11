from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Binance API üzerinden token fiyatını al
def get_token_price_from_binance(symbol):
    try:
        # Binance API URL (örneğin, BTC -> BTCUSDT)
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}USDT"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return float(data["price"])  # Token fiyatını döndür
        else:
            print(f"API Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token_name = request.form.get("token_name", "").upper()
        tokens_offered = int(request.form.get("tokens_offered"))
        your_sp_burn = int(request.form.get("your_sp_burn"))
        total_sp_burnt = int(request.form.get("total_sp_burnt"))

        # Binance üzerinden token fiyatını al
        token_price = get_token_price_from_binance(token_name)
        if token_price is None:
            return render_template("index.html", error=f"Failed to fetch token price for {token_name}. Please check the token name or try again later.")

        # Ödülü hesapla
        reward = your_sp_burn * (tokens_offered / total_sp_burnt) * token_price

        return render_template(
            "index.html",
            token_name=token_name,
            token_price=f"{token_price:.4f}$",
            tokens_offered=f"{tokens_offered:,}",
            your_sp_burn=f"{your_sp_burn:,}",
            total_sp_burnt=f"{total_sp_burnt:,}",
            reward=f"{reward:.2f}$"
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
