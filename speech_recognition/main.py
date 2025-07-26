import pyaudio
import vosk
import json
import os
import subprocess
from vosk import SetLogLevel
SetLogLevel(-1)
# use max cores
cores = subprocess.check_output("nproc", shell=True, text=True)
os.environ["OMP_NUM_THREADS"] = cores
os.environ["OPENBLAS_NUM_THREADS"] = cores
os.environ["MKL_NUM_THREADS"] = cores


class SpeechRecognition:
    def __init__(self, model_path="../vosk_models/medium/"):
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )
        self.stream.start_stream()

    def listen(self):
        result = ""
        while True:
            data = self.stream.read(4096)  # Read audio data from mic
            if self.recognizer.AcceptWaveform(data):
                res = json.loads(self.recognizer.Result())
                text = res.get("text", "")
                if text:
                    result += text + " "
                else:
                    break
            else:
                # Partial result can be obtained using self.recognizer.PartialResult()
                pass
        final_res = json.loads(self.recognizer.FinalResult())
        final_text = final_res.get("text", "")
        result += final_text
        return result.strip()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()


def main():
    rec = SpeechRecognition()
    print("start")
    try:
        while True:
            text = rec.listen()
            print(text)
    except KeyboardInterrupt:
        print("\nterminating")
    finally:
        rec.stop()


if __name__ == "__main__":
    main()
