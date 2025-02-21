import requests


CLIENT_ID = "gp762nuuoqcoxypju8c569th9wz7q5"
TOKEN = "oauth:b1clnc3xiwl61eccxo1y1h6cgbw5wy"

def is_streamer_online(username):
    url = f"https://api.twitch.tv/helix/streams?user_login={username}"
    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers).json()
    return bool(response["data"])
