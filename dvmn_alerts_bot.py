import  os
import time
from dotenv import load_dotenv
import asyncio
from telegram import Bot
import requests


async def main():
    load_dotenv()
    dvmn_token = os.getenv("DVMN_TOKEN")
    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {dvmn_token}"}
    payload = {}

    chat_id = os.getenv("BOT_CHAT_ID")
    bot = Bot(token=os.getenv("TG_TOKEN"))
    chat = await bot.get_chat(chat_id)
    name = chat.first_name

    print("Бот работает!")
    while True:
        try:
            response = requests.get(url, headers=headers, params=payload, timeout=130)
            lesson_data = response.json()
            
            if lesson_data["status"] == "timeout":
                payload["timestamp"] = lesson_data["timestamp_to_request"]
                print("Ожидаю работу с проверки...")

            elif lesson_data["status"] == "found":
                for attempt in lesson_data["new_attempts"]:
                    lesson_title = attempt["lesson_title"]
                    lesson_url = attempt["lesson_url"]
                    if attempt["is_negative"]:
                        text = (f"{name}, у вас проверили работу\n"
                                f" '{lesson_title}'\n"
                                f" {lesson_url}\n"
                                f"К сожалению, в работе нашлись ошибки.")
                    else:
                        text = (f"{name}, у вас проверили работу\n"
                                f" '{lesson_title}'\n"
                                f" {lesson_url}\n"
                                f"Преподавателю все понравилось!\n"
                                f"Можно приступать к следующему уроку. ")
                    await bot.send_message(chat_id=chat_id, text=text)
                payload["timestamp"] = lesson_data["last_attempt_timestamp"]

        except requests.exceptions.ReadTimeout:
            print("Сервер не ответил, отправляем запрос заново...")
            continue

        except requests.exceptions.ConnectionError:
            print("Потеряно соединение, отправляем запрос заново...")
            time.sleep(5)
            continue


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка бота...")

