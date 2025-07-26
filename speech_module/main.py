from os import umask
import time
from typing import List
import subprocess
import re

class TokenEnum:
    PAUSE = "PAUSE"
    SPEECH = "SPEECH"


class Token:
    def __init__(self, type, value: str | float) -> None:
        self.type = type
        self.value = value


class TTS:
    def __init__(self, language: str = "ru"):  # Используем корректный код языка
        self.language = language
        self.url_pattern = r'<(https?://[^>\s]+)>'
    def _parse(self, text: str) -> List[Token]:
        pauses = {",": 0.4, ".": 0.8, "?": 0.8, "!": 0.7}
        result = []
        current_string = ""
        is_special_token = False
        spec_characters = ",."
        text = self._preprocess_markdown_links(text)

        for letter in text:
            if letter not in spec_characters:
                current_string += letter
            else:
                if not is_special_token:
                    if current_string.strip():
                        result.append(Token(type=TokenEnum.SPEECH, value=current_string.strip()))
                    current_string = ""
                    
                    if letter in pauses:
                        result.append(Token(type=TokenEnum.PAUSE, value=pauses[letter]))
                        continue
                        
                if letter == "<":
                    if is_special_token:
                        raise SyntaxError("Неправильное использование специальных токенов")
                    is_special_token = True
                    
                elif letter == ">":
                    if not is_special_token:
                        raise SyntaxError("Неожиданный символ '>'")
                    try:
                        pause_value = float(current_string)
                        result.append(Token(type=TokenEnum.PAUSE, value=pause_value))
                    except ValueError:
                        raise SyntaxError("Неверное значение паузы")
                    current_string = ""
                    is_special_token = False

        if current_string.strip():
            result.append(Token(type=TokenEnum.SPEECH, value=current_string.strip()))
            
        return result

    def _preprocess_markdown_links(self, text: str) -> str:
        """Удаляет угловые скобки из markdown ссылок"""
        return re.sub(r'<(https?://[^>\s]+)>', r'\1', text)
    def say(self, text: str, lang: str= "ru") -> None:
        tokens = self._parse(text)
        for token in tokens:
            if token.type == TokenEnum.SPEECH:
                result = subprocess.run([
                    'espeak-ng',
                    token.value,
                    '-v', lang,
                    '--stdout'
                ], capture_output=True, check=True)
                try:
                    subprocess.run(['aplay', '-q'], input=result.stdout, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    print(f"exception: {e}")
            elif token.type == TokenEnum.PAUSE:
                time.sleep(token.value)


def main():
    tts = TTS()
    text = "Привет, как дела. чем я могу быть полезен? тут будет пауза в 0.9 секунды <0.9> пауза прошла"
    tts.say(text)


if __name__ == "__main__":
    main()
