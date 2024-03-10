import requests
import os
from bs4 import BeautifulSoup
from google.cloud import speech


if __name__ == '__main__':
    session = requests.Session()

    # ログインする
    res_top = session.post(
        url = 'https://www.rarejob.com/account/login/',
        data = {
            "RJ_LoginForm[email]": os.getenv("RJ_ID"),
            "RJ_LoginForm[password]": os.getenv("RJ_PASSWORD"),
        }
    )
    soup_top = BeautifulSoup(res_top.text, "html.parser")
    details = soup_top.find_all("a", class_="arrow-link-r")

    # 詳細を開く
    res_detail = session.get(details[1].get("href"))
    soup_detail = BeautifulSoup(res_detail.text, "html.parser")
    audio_data = soup_detail.find("audio", class_="audioData")

    # GCS音声データURL出力
    print(audio_data.get("src"))

    
    ######################################
    # ここから Speech-to-Text
    # https://cloud.google.com/speech-to-text/docs/transcribe-client-libraries#make_an_audio_transcription_request
    ######################################
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    # gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
    gcs_uri = audio_data.get("src")

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")