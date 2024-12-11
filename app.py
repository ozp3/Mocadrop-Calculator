from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Token fiyatını çekmek için API çağrısı
def get_token_price(token_id, vs_currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies={vs_currency}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get(token_id, {}).get(vs_currency, None)
    except Exception as e:
        print(f"API error: {e}")
    return None

# Ana sayfa rotası
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Form verilerini al
        tokens_offered = int(request.form.get("tokens_offered"))
        your_sp_burn = int(request.form.get("your_sp_burn"))
        total_sp_burnt = int(request.form.get("total_sp_burnt"))

        # Kullanıcının custom price girip girmediğini kontrol et
        custom_price_checkbox = request.form.get("custom_price_checkbox")
        if custom_price_checkbox:  # Custom price seçilmişse
            try:
                custom_price = request.form.get("custom_price")
                if not custom_price:  # Custom price boşsa
                    return render_template("index.html", error="Custom price is required.")
                token_price = float(custom_price)  # Kullanıcının girdiği fiyat
                token_name = "Custom Price"
            except ValueError:
                return render_template("index.html", error="Invalid custom price. Please enter a valid number.")
        else:  # API'den token fiyatını al
            token_name = request.form.get("token_name", "").lower()
            if not token_name:  # Token adı boşsa hata göster
                return render_template("index.html", error="Token name is required.")
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
            reward=f"{reward:.2f}$",
            custom_price_checked=bool(custom_price_checkbox),
        )
    return render_template("index.html")
