import argparse
import asyncio
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import InvalidToken, TelegramError


async def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description=r"""
        Телеграм бот для отправки уведомлений с сайта https://dvmn.org/
        о проверенных работах.
        Пример ввода:
        python .\dvmn_alerts_bot.py # Запуск бота, если chat_id указан в .env
        python .\dvmn_alerts_bot.py --chat_id 10856956789 # Запуск бота у указанием chat_id
        """,
        epilog="""
        Для работы бота требуется файл .env
        с переменными DVMN_TOKEN, BOT_CHAT_ID и TG_TOKEN.
        Внесите BOT_CHAT_ID в .env файл или используйте флаг --chat_id
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter

    )
    parser.add_argument(
        "--chat_id",
        type=str,
        default=os.getenv("BOT_CHAT_ID"),
        help="Укажите ваш личный id чата.\n"
             "Получить его можно у @userinfobot"
    )
    args = parser.parse_args()


    dvmn_token = os.environ["DVMN_TOKEN"]
    tg_token = os.environ["TG_TOKEN"]


    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {dvmn_token}"}
    payload = {}
    try:
        bot = Bot(token=tg_token)
    except InvalidToken:
        print("Ошибка: Укажите токен Телеграм-бота (TG_TOKEN) в .env.")
        return

    if args.chat_id:
        chat_id = args.chat_id
        try:
            chat = await bot.get_chat(chat_id)
            name = chat.first_name
        except InvalidToken:
            print("Ошибка: Токен Телеграм-бота недействителен.")
            return
        except TelegramError as err:
            print(f"Ошибка Телеграма: {err}. Убедитесь, что chat_id правильный.")
            return
    else:
        print("Укажите ваш телеграмм чат id .env файле или через флаг --chat_id")
        return

    print("Бот работает!")
    while True:
        try:
            response = await asyncio.to_thread(
                requests.get, url, headers=headers, params=payload, timeout=130
            )
            response.raise_for_status()
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
            print("Сервер не ответил, отправляю запрос заново...")
            continue

        except requests.exceptions.ConnectionError:
            print("Потеряно соединение, отправляю запрос заново...")
            time.sleep(5)
            continue

        except requests.exceptions.HTTPError as error:
            if error.response.status_code == 401:
                print("Ошибка: Неверный токен Девмана (DVMN_TOKEN). Проверьте настройки.")
                return


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка бота...")

