import requests
from datetime import datetime

def fetch_projects():
    """
    Fetch the list of projects from the Mocaverse API.
    """
    try:
        response = requests.get("https://api.staking.mocaverse.xyz/api/mocadrop/projects/")
        response.raise_for_status()
        data = response.json().get("data", [])
        return [
            {
                "name": project["name"],
                "url": f"https://api.staking.mocaverse.xyz/api/mocadrop/projects/{project['urlSlug']}",
                "iconUrl": project.get("iconUrl", ""),  # Proje ikonu
                "tokenIconUrl": project.get("tokenIconUrl", ""),  # Token ikonu
                "tokenTicker": project.get("tokenTicker", ""),
                "tokensOffered": project.get("tokensOffered", "0"),
                "registrationEndDate": project.get("registrationEndDate", "N/A"),
                "mode": project.get("mode", "flexible"),  # Mode: flexible or fixed
            }
            for project in data
        ]
    except Exception as e:
        print(f"Error fetching project list: {e}")
        return []

def get_pool_data(project_url):
    """
    Fetch detailed data for a specific project.
    Handles 'mode: fixed' by returning tier configuration.
    """
    try:
        response = requests.get(project_url)
        response.raise_for_status()
        data = response.json()

        # Ortak veriler
        staking_power_burnt = float(data.get("stakingPowerBurnt", 0))
        registration_end_date = data.get("registrationEndDate", "N/A")

        if registration_end_date != "N/A":
            try:
                dt = datetime.strptime(registration_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                registration_end_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except ValueError:
                registration_end_date = "Invalid date format"

        # Mode kontrolü: fixed ise tierConfig verisini de al
        mode = data.get("mode", "flexible")
        tier_config = data.get("tierConfig", []) if mode == "fixed" else []

        return {
            "staking_power_burnt": staking_power_burnt,
            "registration_end_date": registration_end_date,
            "mode": mode,
            "tier_config": tier_config,
        }
    except Exception as e:
        print(f"Error fetching project data: {e}")
        return {
            "staking_power_burnt": None,
            "registration_end_date": "Error fetching date",
            "mode": "flexible",
            "tier_config": [],
        }

def check_deadline(registration_end_date):
    """
    Check if the registration deadline has passed.
    """
    try:
        deadline = datetime.strptime(registration_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        return datetime.utcnow() > deadline
    except ValueError:
        return False

def fetch_wallet_data(evm_address):
    """
    Fetch wallet data for the given EVM address from the Mocaverse API.
    """
    api_url = f"https://api.staking.mocaverse.xyz/api/power?walletAddress={evm_address}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        wallet_data = response.json()

        # Format numbers with commas
        def format_number(value):
            try:
                return f"{float(value):,.2f}" if value not in [None, "N/A"] else "N/A"
            except ValueError:
                return "N/A"

        # Parse and format data
        return {
            "totalGenerated": format_number(wallet_data.get("totalGenerated", "N/A")),
            "baseRatePerDay": format_number(wallet_data.get("baseRatePerDay", "N/A")),
            "boostRatePerDay": format_number(wallet_data.get("boostRatePerDay", "N/A")),
            "totalBoostPercent": wallet_data.get("totalBoostPercent", "N/A"),  # Percent remains unchanged
            "earlyBonus": format_number(wallet_data.get("earlyBonus", "N/A")),
            "balance": format_number(wallet_data.get("balance", "N/A")),
            "tier": wallet_data.get("tier", wallet_data.get("tierIndex", "N/A")),  # tier veya tierIndex
        }
    except Exception as e:
        print(f"Error fetching wallet data: {e}")
        return {"error": "Unable to fetch wallet data. Please try again."}
