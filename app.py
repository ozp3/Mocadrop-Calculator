from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

MOCA_API_URL = "https://api.staking.mocaverse.xyz/api/mocadrop/projects/kip-protocol"

MOCA_TOKEN_NAME = "KIP PROTOCOL"
TOKENS_OFFERED = "50,000,000"

# Function to fetch data from Mocaverse API
def get_pool_data():
    try:
        response = requests.get(MOCA_API_URL)
        response.raise_for_status()
        data = response.json()
        staking_power_burnt = float(data.get("stakingPowerBurnt", 0))
        registration_end_date = data.get("registrationEndDate", "N/A")

        # Format the registration end date
        if registration_end_date != "N/A":
            try:
                dt = datetime.strptime(registration_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                registration_end_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except ValueError:
                registration_end_date = "Invalid date format"

        return staking_power_burnt, registration_end_date
    except Exception as e:
        print(f"Error fetching Mocaverse data: {e}")
        return None, "Error fetching date"

@app.route("/", methods=["GET", "POST"])
def index():
    total_sp_burnt, registration_end_date = get_pool_data()
    if total_sp_burnt is None:
        return render_template(
            "index.html",
            error="Could not fetch Total SP Burnt from Mocaverse API.",
            token_name=MOCA_TOKEN_NAME,
            tokens_offered=TOKENS_OFFERED,
            total_sp_burnt="Error fetching data",
            registration_end_date=registration_end_date,
        )

    if request.method == "POST":
        custom_price = request.form.get("custom_price")
        your_sp_burn = request.form.get("your_sp_burn")

        if not custom_price or not your_sp_burn:
            return render_template(
                "index.html",
                error="All fields are required.",
                token_name=MOCA_TOKEN_NAME,
                tokens_offered=TOKENS_OFFERED,
                total_sp_burnt=f"{total_sp_burnt:,.0f}",
                registration_end_date=registration_end_date,
            )

        try:
            custom_price = float(custom_price)
            your_sp_burn = int(your_sp_burn)
        except ValueError:
            return render_template(
                "index.html",
                error="Invalid input. Please enter numeric values.",
                token_name=MOCA_TOKEN_NAME,
                tokens_offered=TOKENS_OFFERED,
                total_sp_burnt=f"{total_sp_burnt:,.0f}",
                registration_end_date=registration_end_date,
            )

        custom_price_decimals = len(str(custom_price).split(".")[1]) if "." in str(custom_price) else 0

        try:
            reward = your_sp_burn * (int(TOKENS_OFFERED.replace(",", "")) / total_sp_burnt) * custom_price
            tokens_received = your_sp_burn * (int(TOKENS_OFFERED.replace(",", "")) / total_sp_burnt)
        except ZeroDivisionError:
            return render_template(
                "index.html",
                error="Total SP Burnt cannot be zero.",
                token_name=MOCA_TOKEN_NAME,
                tokens_offered=TOKENS_OFFERED,
                total_sp_burnt=f"{total_sp_burnt:,.0f}",
                registration_end_date=registration_end_date,
            )

        return redirect(
            url_for(
                "result",
                token_name=MOCA_TOKEN_NAME,
                tokens_offered=TOKENS_OFFERED,
                total_sp_burnt=f"{total_sp_burnt:,.0f}",
                token_price=f"{custom_price:.{custom_price_decimals}f}$",
                your_sp_burn=f"{your_sp_burn:,}",
                reward=f"{reward:.2f}$",
                tokens_received=f"{tokens_received:,.2f}",
            )
        )

    return render_template(
        "index.html",
        token_name=MOCA_TOKEN_NAME,
        tokens_offered=TOKENS_OFFERED,
        total_sp_burnt=f"{total_sp_burnt:,.0f}",
        registration_end_date=registration_end_date,
    )

@app.route("/result")
def result():
    return render_template(
        "result.html",
        token_name=request.args.get("token_name"),
        tokens_offered=request.args.get("tokens_offered"),
        total_sp_burnt=request.args.get("total_sp_burnt"),
        token_price=request.args.get("token_price"),
        your_sp_burn=request.args.get("your_sp_burn"),
        reward=request.args.get("reward"),
        tokens_received=request.args.get("tokens_received"),
    )

if __name__ == "__main__":
    app.run(debug=True)