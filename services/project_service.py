import requests
from datetime import datetime, timedelta

# Global önbellek
token_price_cache = {}

def fetch_projects():
    try:
        response = requests.get("https://api.staking.mocaverse.xyz/api/mocadrop/projects/")
        response.raise_for_status()
        data = response.json().get("data", [])
        return [
            {
                "name": project["name"],
                "url": f"https://api.staking.mocaverse.xyz/api/mocadrop/projects/{project['urlSlug']}",
                "icon": project.get("iconUrl", ""),
                "tokenTicker": project.get("tokenTicker", ""),
                "tokensOffered": project.get("tokensOffered", "0"),
                "registrationEndDate": project.get("registrationEndDate", "N/A"),
            }
            for project in data
        ]
    except Exception as e:
        print(f"Error fetching project list: {e}")
        return []

def get_pool_data(project_url):
    try:
        response = requests.get(project_url)
        response.raise_for_status()
        data = response.json()
        staking_power_burnt = float(data.get("stakingPowerBurnt", 0))
        registration_end_date = data.get("registrationEndDate", "N/A")

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

def check_deadline(registration_end_date):
    try:
        deadline = datetime.strptime(registration_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        return datetime.utcnow() > deadline
    except ValueError:
        return False

def fetch_token_price(token_ticker):
    """
    Fetch the current price of a token from the CoinGecko API with 1-minute caching.
    """
    global token_price_cache

    # Eğer token zaten önbellekte varsa ve süre dolmamışsa direkt döndür
    if token_ticker in token_price_cache:
        cached_price, timestamp = token_price_cache[token_ticker]
        if datetime.utcnow() - timestamp < timedelta(seconds=5):  # 1 dakikalık önbellek
            return cached_price

    try:
        # CoinGecko API endpoint
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_ticker.lower()}&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if the token exists in the response
        if token_ticker.lower() in data:
            current_price = data[token_ticker.lower()]["usd"]
            # Fiyatı ve zaman damgasını önbelleğe kaydet
            token_price_cache[token_ticker] = (current_price, datetime.utcnow())
            return current_price
        else:
            print(f"Token {token_ticker} not found on CoinGecko.")
            return None
    except Exception as e:
        print(f"Error fetching token price for {token_ticker}: {e}")
        return None
