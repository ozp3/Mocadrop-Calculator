from flask import Flask, render_template, request
import time

app = Flask(__name__)

# Kullanıcı IP'lerine göre zaman damgalarını saklayan sözlük
user_requests = {}

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

        # Kullanıcı her zaman token price girebilir
        custom_price = request.form.get("custom_price")
        if not custom_price:
            return render_template("index.html", error="Token price is required.")
        try:
            token_price = float(custom_price)
        except ValueError:
            return render_template("index.html", error="Invalid token price. Please enter a valid number.")

        # 10 saniye limiti
        if not can_user_request(user_ip, interval=10):
            return render_template("index.html", error="You can only make a request every 10 seconds.")

        # Diğer hesaplamalar
        tokens_offered = int(request.form.get("tokens_offered"))
        your_sp_burn = int(request.form.get("your_sp_burn"))
        total_sp_burnt = int(request.form.get("total_sp_burnt"))

        reward = your_sp_burn * (tokens_offered / total_sp_burnt) * token_price

        return render_template(
            "index.html",
            token_price=f"{token_price:.4f}$",
            tokens_offered=f"{tokens_offered:,}",
            your_sp_burn=f"{your_sp_burn:,}",
            total_sp_burnt=f"{total_sp_burnt:,}",
            reward=f"{reward:.2f}$"
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
