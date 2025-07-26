from speech_module.main import TTS
from llm_integration.main import Model
from speech_recognition.main import SpeechRecognition
import os

BASIC_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "main_text": {
            "type": "string",
            "description":"text that will shown in text chat"    
        },
        "language": {
          "type": "string",
            "description":"language of answer for tts (espeak)"
        },
        "say_text": {
            "type": "string",
            "description":"text that will voiced by tts"
        }
        },
    "required": [
    "main_text",
    "language",
    "say_text"
    ]
}

def wait_data(port: int= 8080) -> None:
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    while True:
        data, addr = sock.recvfrom(1024)
        if data:
            break
    return


def main():
    tts = TTS()
    ai = Model(baseUrl="http://192.168.10.104:1234/v1", model="qwen-coder")
    vosk = SpeechRecognition("./vosk_models/medium/")
    print("starting")
    os.system("clear")
    wait_data(port= 8080)
    text = ai.get_output("представься. (ты - голосовой ai ассистент)")
    tts.say(text["say_text"], lang= text["language"])
    while True:
        print("user >>>", end=" ", flush= True)
        text = ""
        while not text:
            text = vosk.listen()
        if text:
            print(text)
            text = ai.get_output(text)
            print("qwen >>>", text["main_text"])
            if text is not None:
                tts.say(text["say_text"], lang= text["language"])


if __name__ == "__main__":
    main()
