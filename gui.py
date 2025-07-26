import flet as ft
import time
import subprocess


class message_box(ft.Column):
    def __init__(self, message: str, alignment: ft.MainAxisAlignment):
        messagebox = ft.Container(
            content= ft.Text(message),
            border= ft.Border(),
            expand= True
        )
        content = [messagebox, ft.Row(alignment= alignment)]
        super().__init__(content)

def get_example_answer(user_input: str):
    fort: str = subprocess.run(["fortune"], capture_output=True, shell=True)
    return {"main_text": fort, "language": "en", "say_text": "мне слишком лень сокращать это"}


def main(page: ft.Page):
    page.title = "ai assistant"
    page.vertical_alignment = ft.VerticalAlignment.CENTER

    _user_input_field = ft.TextField(expand=True, label= "message")

    def send(_e):
        page.update(_user_input_field)
        value = _user_input_field.value
        main_content.controls.insert(0, message_box(value, ft.alignment.bottom_left))
        result = get_example_answer(value)
        main_content.controls.insert(0, message_box(result, ft.alignment.bottom_left))

    user_input = ft.Row(
        [
            _user_input_field,
            ft.IconButton(icon=ft.Icons.SCHEDULE_SEND, expand=False, on_click= send)
        ],
        expand=True
    )

    def align(what_to_align):
        return ft.Container(content=what_to_align, expand=True, alignment=ft.alignment.bottom_left)

    main_content = ft.Column(
            [
                ft.Container(expand= True),
                ft.Container(content=user_input, expand=False,
                             alignment=ft.alignment.bottom_center),
            ],
            alignment=ft.alignment.bottom_center,
            expand=True
        )
    page.add(
        main_content
    )


ft.app(main)
