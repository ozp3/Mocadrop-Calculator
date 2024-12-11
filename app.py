from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

# Kullanıcı IP'lerine göre zaman damgalarını saklayan sözlük
user_requests = {}

# CoinGecko API üzerinden token fiyatını al
def get_token_price(token_id, vs_currency="usd"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies={vs_currency}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get(token_id, {}).get(vs_currency, None)
        else:
            print(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Request Exception: {e}")
        return None

# Kullanıcı isteklerini kontrol et
def can_user_request(user_ip):
    current_time = time.time()
    if user_ip in user_requests:
        last_request_time = user_requests[user_ip]
        # Eğer kullanıcı bir dakikadan daha önce istek yaptıysa engelle
        if current_time - last_request_time < 60:
            return False
    # Zaman damgasını güncelle
    user_requests[user_ip] = current_time
    return True

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Kullanıcı IP'sini al
        user_ip = request.remote_addr

        # Kullanıcı istek sınırını kontrol et
        if not can_user_request(user_ip):
            return render_template("index.html", error="You can only make one request per minute.")

        token_name = request.form.get("token_name", "").lower()
        tokens_offered = int(request.form.get("tokens_offered"))
        your_sp_burn = int(request.form.get("your_sp_burn"))
        total_sp_burnt = int(request.form.get("total_sp_burnt"))

        # CoinGecko API üzerinden token fiyatını al
        token_price = get_token_price(token_name)
        if token_price is None:
            return render_template("index.html", error=f"Failed to fetch token price for {token_name}. Please check the token name or try again later.")

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
