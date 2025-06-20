import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def make_request_with_retries(url, headers, method="GET", data=None, max_retries=3, delay=5):
    """
    Makes an HTTP request with retries in case of failure.
    """
    for attempt in range(1, max_retries + 1):
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError("Unsupported HTTP method")

            if response.status_code == 200:
                #  check Content-Length
                if response.headers.get('Content-Length') != '0':
                    return response.json()
                else:
                    return True
            else:
                print(f"Attempt {attempt}: Server returned status {response.status_code}")
                return False
        except (requests.RequestException, ValueError) as e:
            print(f"Attempt {attempt}: Request failed with error: {e}")
        except Exception as e:
            print(f"Attempt {attempt}: Unexpected error: {e}")

        if attempt < max_retries:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    print("Max retries reached. Request failed.")
    return None

def get_games():
    url = "https://backend.mymg.tn/items/game_level"
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "authorization": "Bearer " + os.environ.get("TOKEN"),
    }
    return make_request_with_retries(url, headers)

def claim_reward(level_index, game_id):
    url = "https://backend.mymg.tn/v2/game/winner-for-game-level"
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "authorization": "Bearer " + os.environ.get("TOKEN"),
        "Content-Type": "application/json"
    }
    payload = {
        "levelIndex": level_index,
        "gameId": game_id
    }
    return make_request_with_retries(url, headers, method="POST", data=payload)

def reveal_box():
    url = "https://backend.mymg.tn/v2/game/reveal-box"
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "authorization": "Bearer " + os.environ.get("TOKEN"),
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers).json()
    print(f"{r.get("data", {}).get("result", {}).get("value", 0)} coins revealed in the box.")

def do_wheel():
    url = "https://backend.mymg.tn/v2/game/winner-for-wheel-item"
    headers = {
        "User-Agent": "okhttp/4.12.0",
        "authorization": "Bearer " + os.environ.get("TOKEN"),
        "Content-Type": "application/json"
    }
    data = {
        "wheelItemId": 3
    }
    r = requests.post(url, headers=headers, json=data)
    print("Successfully did the wheel." if r.status_code == 200 else "Failed to do the wheel.")

def main():
    # Step 1: Fetch all games and levels
    games = get_games()
    if not games:
        print("No games found or failed to fetch games.")
        return

    # Step 2: Loop through each game and level, and claim rewards
    for game in games.get("data", []):
        game_id = game["game"]
        level_index = game["level_index"]
        print(f"Processing Game ID: {game_id}, Level Index: {level_index}")
        response = claim_reward(level_index, game_id)
        if response:
            print(f"Successfully claimed reward: {response}")
        else:
            print(f"Failed to claim reward for Game ID {game_id}, Level Index {level_index}")
    reveal_box()
    do_wheel()

# Run the main function
if __name__ == "__main__":
    main()