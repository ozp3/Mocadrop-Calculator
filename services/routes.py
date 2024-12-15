from flask import render_template, request, redirect, url_for
from services.project_service import fetch_projects, get_pool_data, check_deadline
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
                mode="flexible",
                tiers=[],
                custom_price=None,
                expected_reward=None,
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
                mode="flexible",
                tiers=[],
                custom_price=None,
                expected_reward=None,
            )

        # Fetch project data
        pool_data = get_pool_data(selected_project["url"])
        total_sp_burnt = pool_data["staking_power_burnt"]
        registration_end_date = pool_data["registration_end_date"]
        mode = pool_data["mode"]
        tier_config = pool_data["tier_config"]

        is_ended = check_deadline(selected_project["registrationEndDate"])

        # Default Values
        custom_price = None
        your_sp_burned = None
        expected_reward = None

        # Flexible Mode: Calculate Expected Reward
        if mode == "flexible" and request.method == "POST" and "calculate_flexible" in request.form:
            try:
                # Get user inputs
                custom_price = float(request.form.get("custom_price", 0))
                your_sp_burned = float(request.form.get("sp_burned", 0))
                tokens_offered = float(selected_project.get("tokensOffered", 0))

                # Calculate Expected Reward
                if total_sp_burnt > 0 and custom_price > 0 and your_sp_burned > 0:
                    expected_reward = round(
                        (tokens_offered / total_sp_burnt) * your_sp_burned * custom_price,
                        2,
                    )
            except ValueError:
                expected_reward = None

        # Fixed Mode: Calculate Expected Rewards if Custom Price is provided
        if mode == "fixed" and request.method == "POST" and "calculate_fixed" in request.form:
            try:
                custom_price = float(request.form.get("custom_price", 0))
                for tier in tier_config:
                    tokens_per_slot = float(tier.get("tokenAllocation", 0))
                    tier["expected_reward"] = round(tokens_per_slot * custom_price, 2)
            except ValueError:
                pass

        # Flexible Mode: Tokens Offered and Total SP Burnt
        tokens_offered = selected_project.get("tokensOffered", "0")
        total_sp_burnt_display = f"{total_sp_burnt:,.0f}" if total_sp_burnt else "N/A"

        return render_template(
            "index.html",
            projects=projects,
            token_name=selected_project["name"],
            tokens_offered=tokens_offered,
            total_sp_burnt=total_sp_burnt_display,
            registration_end_date=registration_end_date,
            is_ended=is_ended,
            mode=mode,
            tiers=tier_config,
            custom_price=custom_price,
            expected_reward=expected_reward,
        )
