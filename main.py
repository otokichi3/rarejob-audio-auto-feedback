import requests
import os
from bs4 import BeautifulSoup
from openai import OpenAI

FILENAME = "audio.mp3"


def get_audio_content():
    session = requests.Session()

    # ログインする
    rj_id = os.getenv("RJ_ID")
    rj_password = os.getenv("RJ_PASSWORD")
    print(rj_id)
    print(rj_password)
    res_top = session.post(
        url="https://www.rarejob.com/account/login/",
        data={
            "RJ_LoginForm[email]": rj_id,
            "RJ_LoginForm[password]": rj_password,
        },
    )
    soup_top = BeautifulSoup(res_top.text, "html.parser")
    details = soup_top.find_all("a", class_="arrow-link-r")  # a.arrow-link-r は複数ある

    # 詳細を開く
    res_detail = session.get(details[1].get("href"))
    soup_detail = BeautifulSoup(res_detail.text, "html.parser")
    audio_data = soup_detail.find("audio", class_="audioData")

    # mp3をダウンロードする
    content = session.get(audio_data.get("src")).content

    with open(FILENAME, "wb") as f:
        f.write(content)

    with open(FILENAME, "rb") as f:
        client = OpenAI()
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )
        for s in transcription.segments:
            print(s["text"])
    # TODO text to Gemini API to improve student's English


"""
Please identify the speakers and add "tutor:" to the teacher's utterances and "you:" to the student's utterances for the following text.
TODO: add suggestions
"""

if __name__ == "__main__":
    content = get_audio_content()
