import os
import pprint
import requests
from dotenv import load_dotenv

def get_lessons(token):
    url = "https://dvmn.org/api/user_reviews/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def main():
    load_dotenv()
    token = os.getenv("DVMN_TOKEN")
    lessons = get_lessons(token)
    pprint.pprint(lessons)

if __name__ == "__main__":
    main()

