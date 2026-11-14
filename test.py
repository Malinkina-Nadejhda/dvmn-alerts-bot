import os
import pprint
import time
import requests
from dotenv import load_dotenv


def main():
    load_dotenv()
    token = os.getenv("DVMN_TOKEN")
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {token}"}
    payload = {}

    while True:
        try:
            response = requests.get(url, headers=headers, params=payload, timeout=130)
            lesson_data = response.json()
            pprint.pprint(lesson_data)

            if lesson_data["status"] == "timeout":
                payload["timestamp"] = lesson_data["timestamp_to_request"]
                print("Нет проверенных работ.")
            elif lesson_data["status"] == "found":
                print("Работа вернулась с проверки!")
                break
        except requests.exceptions.ReadTimeout:
            print("Сервер не ответил, отправляем запрос заново...")
            continue
        except requests.exceptions.ConnectionError:
            print("Потеряно соединение, отправляем запрос заново...")
            time.sleep(5)
            continue


if __name__ == "__main__":
    main()





