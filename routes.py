from flask import render_template, request, redirect, url_for
from services.project_service import fetch_projects, get_pool_data, check_deadline, fetch_token_price
from datetime import datetime

def setup_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        projects = fetch_projects()

        if not projects:
            return render_template(
                "index.html",
                error="Could not fetch projects from Mocaverse API.",
                projects=[],
                token_name="",
                tokens_offered="",
                total_sp_burnt="",
                registration_end_date="",
                is_ended=False,
                token_price=None,
                mode="flexible",
                tiers=[],
                custom_price=None,
            )

        selected_project_name = request.form.get("project") or projects[0]["name"]
        selected_project = next((p for p in projects if p["name"] == selected_project_name), None)

        if not selected_project:
            return render_template(
                "index.html",
                error="Invalid project selected.",
                projects=projects,
                token_name="",
                tokens_offered="",
                total_sp_burnt="",
                registration_end_date="",
                is_ended=False,
                token_price=None,
                mode="flexible",
                tiers=[],
                custom_price=None,
            )

        # Fetch project data
        pool_data = get_pool_data(selected_project["url"])
        total_sp_burnt = pool_data["staking_power_burnt"]
        registration_end_date = pool_data["registration_end_date"]
        mode = pool_data["mode"]
        tier_config = pool_data["tier_config"]

        is_ended = check_deadline(selected_project["registrationEndDate"])

        # Fetch CoinGecko price regardless of the status
        token_price = None
        if selected_project["tokenTicker"]:
            token_price = fetch_token_price(selected_project["tokenTicker"])

        # Custom Token Price
        custom_price = None
        if request.method == "POST" and "custom_price" in request.form:
            try:
                custom_price = float(request.form.get("custom_price"))
            except ValueError:
                custom_price = None

        # Fixed Mode: Calculate Expected Rewards if Custom Price is provided
        if mode == "fixed" and custom_price:
            for tier in tier_config:
                tokens_per_slot = float(tier.get("tokenAllocation", 0))
                tier["expected_reward"] = round(tokens_per_slot * custom_price, 2)

        # Flexible Mode: Tokens Offered and Total SP Burnt
        if mode == "flexible":
            tokens_offered = selected_project.get("tokensOffered", "0")
            total_sp_burnt_display = f"{total_sp_burnt:,.0f}" if total_sp_burnt else "N/A"
        else:
            tokens_offered = None
            total_sp_burnt_display = None

        return render_template(
            "index.html",
            projects=projects,
            token_name=selected_project["name"],
            tokens_offered=tokens_offered,
            total_sp_burnt=total_sp_burnt_display,
            registration_end_date=registration_end_date,
            is_ended=is_ended,
            token_price=token_price,
            mode=mode,
            tiers=tier_config,
            custom_price=custom_price,
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
