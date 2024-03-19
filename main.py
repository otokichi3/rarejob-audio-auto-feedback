import requests
import os
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
from bs4 import BeautifulSoup
from openai import OpenAI

FILENAME = "audio.mp3"



def get_audio_text():
    session = requests.Session()

    # ログインする
    rj_id = os.getenv("RJ_ID")
    rj_password = os.getenv("RJ_PASSWORD")
    res_top = session.post(
        url=os.getenv("LOGIN_URL"),
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

    # mp3を取得する
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
        text = ""
        for s in transcription.segments:
            text += s["text"]

    return text


def get_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

def get_imporved_sentences(text: str) -> str:
    vertexai.init(project=os.getenv("PROJECT_ID"), location=os.getenv("LOCATION"))
    model = GenerativeModel("gemini-1.0-pro")
    chat = model.start_chat()

    prompt_identified = "Please identify the speakers and add \"tutor:\" to the teacher's utterances and add \"you:\" to the student's utterances for the following text."
    prompt_identified = prompt_identified + "\n" + "---" + "\n"
    prompt_identified = prompt_identified + text
    text_identified = get_chat_response(chat, prompt_identified)

    prompt_improved = "Please improve the following sentences to be more natural with reason for revision. Please keep an original sentence while appending an improved sentence in each line."
    prompt_improved = prompt_improved + "\n" + "---" + "\n"
    prompt_improved = prompt_improved + text_identified
    return get_chat_response(chat, prompt_improved)

if __name__ == "__main__":
    text = get_audio_text()
    # text = ""
    # with open("transcription_short.txt", "r") as f:
    #     text = f.read()
    res = get_imporved_sentences(text)
    print(res)

