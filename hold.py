import requests
import time

url = "https://net-delia-originalsrijan69-10e42d45.koyeb.app/"

while True:
    try:
        response = requests.get(url)
        print("Status Code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
    
    time.sleep(20)

