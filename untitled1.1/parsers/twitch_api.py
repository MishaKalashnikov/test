import requests

CLIENT_ID = "your_client_id"
TOKEN = "your_oauth_token"

def is_streamer_online(username):
    url = f"https://api.twitch.tv/helix/streams?user_login={username}"
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers).json()
    return bool(response["data"])
