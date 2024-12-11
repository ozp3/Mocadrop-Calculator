from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Kullanıcıdan token price al
        custom_price = request.form.get("custom_price")
        if not custom_price:
            return render_template("index.html", error="Token price is required.")
        try:
            token_price = float(custom_price)
        except ValueError:
            return render_template("index.html", error="Invalid token price. Please enter a valid number.")

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
