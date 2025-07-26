from openai import OpenAI
import json

FUNCTIONS = {}

def register_function(func):
    """Decorator to register functions"""
    FUNCTIONS[func.__name__] = func
    return func

def call_function(func_name: str, *args, **kwargs):
    if func_name in FUNCTIONS:
        return FUNCTIONS[func_name](*args, **kwargs)
    else:
        return f"Function '{func_name}' not registered"

@register_function
def get_weather_in(location: str):
    return f"now 25 celsius in {location}"

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
            "description":"language of answer for tts (ru for Russian, en for english, etc)"
        },
        "say_text": {
            "type": "string",
            "description":"text that will voiced by tts (shorter version of main text)"
        },
        "function":{
            "type":"object",
            "properties":{
                "name":{"type":"string", "description":"name of the function you want to call"}
            }
        }
        },
    "required": [
    "main_text",
    "language",
    "say_text"
    ]
}


functions = [
    {
        "name": "get_weather_in",
        "description": "get current weather in location",
        "properties": {
            "location": {"type": "string", "description": "location name, e.g NewYork"}
        }
    }
]

class Model:
    def __init__(self, baseUrl: str = "localhost", apiKey: str = "", model: str = "auto", sysPrompt: str = "use only terminal comppatible formating (NO MARKOWN, LATEX, etc.). all text packed in <> is system or debug and dont need responding.", schema: dict= BASIC_SCHEMA) -> None:
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl)
        if model == "auto":
            try:
                model_list = list(self.client.models.list())
                if model_list:
                    model = model_list[0].id
                else:
                    raise ValueError(
                        "Список моделей пуст. Невозможно выбрать модель автоматически.")
            except Exception as e:
                raise RuntimeError(
                    f"Ошибка при автоматическом выборе модели: {e}")
        self.model = model
        self.sysPrompt = sysPrompt
        self.messages = []

        self.messages.append({"role": "system", "content": f"{self.sysPrompt}, functions that you can call: {functions}"})

        self.schema = schema
        self.function_output = {}

    def get_output(self, message: str) -> dict | None:
        self.messages.append({"role": "user", "content": f"user message : {message}, function result: {self.function_output}"})
        completion = self.client.chat.completions.create(
            model=self.model, messages=self.messages, response_format={"type":"json_schema", "json_schema":{ "name":"response", "schema":self.schema}})
        ai_result = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_result})
        ai_result = json.loads(ai_result) 
        if "function" in ai_result.keys():
            self.function_output = {"name":ai_result["function"], "output":"calling functions is not released yet"}
            self.messages.append({"role": "user", "content": f"user message : <this is system message with function result>, function result: {self.function_output}"})
        else:
            self.function_output = {}
        return ai_result

    def sudo(self, message: str, role: str = "system"):
        self.messages.append({"role": role, "content": message})
        completion = self.client.chat.completions.create(
            model=self.model, messages=self.messages)
        ai_result = completion.choices[0]
        self.messages.append(ai_result)
        return ai_result.message.content

def main():
    llm = Model(baseUrl="http://192.168.10.104:1234/v1/", model="qwen-coder")

    while True:
        user_input = input(">>> ")
        if user_input == "exit":
            break
        print(llm.get_output(user_input))


if __name__ == "__main__":
    main()
