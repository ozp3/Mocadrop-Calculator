from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Token fiyatını çekmek için mocadrop.py'deki fonksiyon
def get_token_price(token_id, vs_currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies={vs_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[token_id][vs_currency]
    else:
        return None

# Ana sayfa rotası
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token_name = request.form.get("token_name").lower()
        tokens_offered = int(request.form.get("tokens_offered"))
        your_sp_burn = int(request.form.get("your_sp_burn"))
        total_sp_burnt = int(request.form.get("total_sp_burnt"))

        # Token fiyatını çek
        token_price = get_token_price(token_name)
        if token_price is None:
            return render_template("index.html", error="Token price couldn't be fetched.")

        # Ödülü hesapla
        reward = your_sp_burn * (tokens_offered / total_sp_burnt) * token_price

        return render_template(
            "index.html",
            token_name=token_name.upper(),
            token_price=f"{token_price:.4f}$",
            tokens_offered=f"{tokens_offered:,}",
            your_sp_burn=f"{your_sp_burn:,}",
            total_sp_burnt=f"{total_sp_burnt:,}",
            reward=f"{reward:.2f}$"
        )
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)