import os
import pprint
import requests
from dotenv import load_dotenv


def main():
    load_dotenv()
    token = os.getenv("DVMN_TOKEN")
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {token}"}
    payload = {}

    while True:
        response = requests.get(url, headers=headers, params=payload)
        lesson_data = response.json()
        pprint.pprint(lesson_data)

        if lesson_data["status"] == "timeout":
            payload["timestamp"] = lesson_data["timestamp_to_request"]
            print("Нет проверенных работ.")
        elif lesson_data["status"] == "found":
            print("Работа вернулась с проверки!")
            break

if __name__ == "__main__":
    main()





