import requests
import time
import threading
import json
import signal
import sys


stop_event = threading.Event()


def read_user_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def signal_handler(sig, frame):
    print("Script stopped by user.")
    stop_event.set()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

def login(username, uid, query_id):
    url = "https://b.bittime.com/exchange-web-gateway/tg-mini-app/login"
    headers, query_params = generate_headers()
    payload = {"initData": query_id, "user": {"id": uid, "username": username, "language_code": "en"}}
    response = requests.post(url, headers=headers, params=query_params, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}) if data.get("code") == "200" else {}
    return {}

def shake(uid, query_id):
    url = "https://b.bittime.com/exchange-web-gateway/tg-mini-app/shake"
    headers, query_params = generate_headers()
    payload = {"initData": query_id, "uid": uid, "shakeNum": 100, "coin": 100}
    response = requests.post(url, headers=headers, params=query_params, json=payload)
    return response.json()

def generate_headers():
    query_params = {
        "appName": "Netscape", "appCodeName": "Mozilla",
        "appVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        "cookieEnabled": "true", "platform": "Win32", "userLanguage": "en-US",
        "vendor": "Google Inc.", "onLine": "true", "product": "Gecko",
        "productSub": "20030107", "mimeTypesLen": "2", "pluginsLen": "5",
        "javaEnbled": "false", "windowScreenWidth": "1920",
        "windowScreenHeight": "1080", "windowColorDepth": "24"
    }
    headers = {
        "accept": "application/json, text/plain, */*", "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9", "content-type": "application/json;charset=UTF-8",
        "origin": "https://palapaminiapp.bittime.com", "referer": "https://palapaminiapp.bittime.com/",
        "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }
    return headers, query_params

def user_process(username, uid, query_id):
    while not stop_event.is_set():
        login_data = login(username, uid, query_id)
        if login_data:
            print(f" {username} | Coin: {login_data.get('coin', 'N/A')} | Max Energy: {login_data.get('maxEnergy', 'N/A')} | Energy: {login_data.get('energy', 'N/A')}")
            if login_data.get('energy', 0) > 0:
                shake_response = shake(uid, query_id)
                
            else:
                print(f"Energy {username} habis. Tunggu 10,000s.")
                time.sleep(10000)  
        else:
            print(f"Gagal login: {username}. Coba dalam 1 menit.")
            time.sleep(60)

        time.sleep(2)

def main():
    users = read_user_data('data.json')
    threads = [threading.Thread(target=user_process, args=(user["username"], user["uid"], user["query_id"])) for user in users]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
