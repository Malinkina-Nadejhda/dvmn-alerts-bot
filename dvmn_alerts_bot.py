import  os
import time
import argparse
from dotenv import load_dotenv
import asyncio
from telegram import Bot
import requests


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

    if not dvmn_token or not tg_token:
        print("Ошибка: Токены Девмана или Телеграма не найдены в .env файле.")
        return

    url = "https://dvmn.org/api/long_polling/"
    headers = {"Authorization": f"Token {dvmn_token}"}
    payload = {}
    bot = Bot(token=tg_token)

    if args.chat_id:
        chat_id = args.chat_id
        chat = await bot.get_chat(chat_id)
        name = chat.first_name
    else:
        print("Укажите ваш телеграмм чат id .env файле или через флаг --chat_id")
        return

    print("Бот работает!")
    while True:
        try:
            response = await asyncio.to_thread(
                requests.get, url, headers=headers, params=payload, timeout=130
            )
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


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановка бота...")

