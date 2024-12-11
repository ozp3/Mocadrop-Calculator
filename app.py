from flask import Flask, render_template, request
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
def can_user_request(user_ip, interval):
    current_time = time.time()
    if user_ip in user_requests:
        last_request_time = user_requests[user_ip]
        # Eğer belirli bir süre geçmemişse engelle
        if current_time - last_request_time < interval:
            return False
    # Zaman damgasını güncelle
    user_requests[user_ip] = current_time
    return True

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Kullanıcı IP'sini al
        user_ip = request.remote_addr

        # Custom seçimi kontrol et
        custom_price_checkbox = request.form.get("custom_price_checkbox")
        if custom_price_checkbox:  # Kullanıcı custom seçmişse sınırlandırma yok
            custom_price = request.form.get("custom_price")
            if not custom_price:
                return render_template("index.html", error="Custom price is required.")
            try:
                token_price = float(custom_price)
                token_name = "Custom Price"
            except ValueError:
                return render_template("index.html", error="Invalid custom price. Please enter a valid number.")
        else:  # Kullanıcı custom seçmemişse API isteği sınırlandırılır
            token_name = request.form.get("token_name", "").lower()
            if not token_name:
                return render_template("index.html", error="Token name is required.")

            # 10 saniye limiti
            if not can_user_request(user_ip, interval=10):
                return render_template("index.html", error="You can only make a request every 10 seconds.")

            # CoinGecko API üzerinden token fiyatını al
            token_price = get_token_price(token_name)
            if token_price is None:
                return render_template("index.html", error=f"Failed to fetch token price for {token_name}. Please check the token name or try again later.")

        # Diğer hesaplamalar
        tokens_offered = int(request.form.get("tokens_offered"))
        your_sp_burn = int(request.form.get("your_sp_burn"))
        total_sp_burnt = int(request.form.get("total_sp_burnt"))

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
