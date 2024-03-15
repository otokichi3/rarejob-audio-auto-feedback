import requests
import os
from bs4 import BeautifulSoup
from google.cloud import speech


def get_audio_url():
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

    return audio_data.get("src")


def audio_to_text(url):
    ######################################
    # ここから Speech-to-Text
    # https://cloud.google.com/speech-to-text/docs/transcribe-client-libraries#make_an_audio_transcription_request
    ######################################
    # Instantiates a client
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=url)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")


if __name__ == "__main__":
    audio_url = get_audio_url()
    print(audio_url)
    audio_to_text(audio_url)
    exit()
