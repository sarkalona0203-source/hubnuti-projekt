import requests

url = "http://127.0.0.1:8000/api/vsechna_jidla/"
token = "d4c189ce2486600147eedf64d576cc336ac8f6a8"  # твой токен

headers = {
    "Authorization": f"Token {token}"
}

response = requests.get(url, headers=headers)

print("Status code:", response.status_code)

try:
    print(response.json())
except Exception:
    print("Ответ не JSON")