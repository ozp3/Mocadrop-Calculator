from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Mocaverse API URL
MOCA_API_URL = "https://api.staking.mocaverse.xyz/api/mocadrop/projects/kip-protocol"

# Function to fetch the pool data from Mocaverse API
def get_pool_data():
    try:
        # Make a GET request to the Mocaverse API
        response = requests.get(MOCA_API_URL)
        response.raise_for_status()  # Raise error for HTTP issues
        data = response.json()  # Parse JSON response
        
        # Extract the stakingPowerBurnt value
        staking_power_burnt = float(data.get("stakingPowerBurnt", 0))
        return staking_power_burnt
    except Exception as e:
        print(f"Error fetching Mocaverse data: {e}")
        return None

# Placeholder data for now
MOCA_TOKEN_NAME = "KIP PROTOCOL"
TOKENS_OFFERED = "50,000,000"

@app.route("/", methods=["GET", "POST"])
def index():
    # Fetch Total SP Burnt from API
    total_sp_burnt = get_pool_data()
    if total_sp_burnt is None:
        return render_template(
            "index.html",
            error="Could not fetch Total SP Burnt from Mocaverse API.",
            token_name=MOCA_TOKEN_NAME,
            tokens_offered=TOKENS_OFFERED,
            total_sp_burnt="Error fetching data",
        )
    
    if request.method == "POST":
        # User input fields
        custom_price = request.form.get("custom_price")
        your_sp_burn = request.form.get("your_sp_burn")

        if not custom_price or not your_sp_burn:
            return render_template(
                "index.html",
                error="All fields are required.",
                token_name=MOCA_TOKEN_NAME,
                tokens_offered=TOKENS_OFFERED,
                total_sp_burnt=f"{total_sp_burnt:,.0f}",
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
            )

        # Determine the number of decimals entered by the user
        custom_price_decimals = len(str(custom_price).split(".")[1]) if "." in str(custom_price) else 0

        # Calculate reward and tokens received
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
