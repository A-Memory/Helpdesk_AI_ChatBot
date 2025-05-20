import os
import random
import subprocess
import threading
import time
import flet as ft
import lmstudio as lm

# LM Studio Server setup
IS_LM_RUNNING: bool = False

try:
    lm.configure_default_client("memorylaptop.local:3333")
    model = lm.llm()
    chat = lm.Chat("You're a helpful Helpdesk Assistant for Employee's of a Small Office Company for Basic Help")
    IS_LM_RUNNING = True
except lm.LMStudioWebsocketError:
    pass

# end of LM Studio Server Setup

# Main Flet Loop and Setup
def main(page: ft.Page):
    # important Flet functions section
    def main_background_effect(p, location_gradient, start_index, end_index, speed):
        nonlocal page, dynamic_background_gradient
        print(". . . . running background effect . . . .\n")
        c = ["#310055", "#3c0663", "#4a0a77", "#5a108f", "#6818a5", "#8b2fc9", "#ab51e3", "#bd68ee", "#d283ff", "#dc97ff"]

        # error checking
        if end_index > len(c):
            print(f". . . . end_index {end_index} is too large! (Max Size = {len(c)}) . . . .\n")
            return
        print(f"background config = ( start_index = {start_index}, end_index = {end_index}\n")
        g_object = c[start_index:end_index]

        # top
        while True:
            for g in range(len(g_object)):
                time.sleep(speed)
                dynamic_background_gradient.colors[location_gradient] = g_object[g]
                page.update()
            g_object.reverse()

    # for dragging frameless window
    def frameless_drag(p):
        page.window.start_dragging()

    # ai functions
    def model_response(p, user_response):
        nonlocal model_response_text, user_input_textfield
        global model, chat

        # if model or chat isn't found
        if IS_LM_RUNNING is False:
            model_response_text.value = "LM Studio isn't running!\n1. Close App.\n2. Run LM Studio with Loaded Model.\n3. Re-open App."
            user_input_textfield.value = ""
            return

        # clears previous responses
        user_input_textfield.value = ""
        model_response_text.value = ""

        # displays (streams) response in real time
        for f in model.respond_stream(user_response):
            model_response_text.value += f.content
            page.update()

        # clear context to free memory...
        chat.__dict__.clear()
        # resets Chat prompt
        chat = lm.Chat("You're a helpful Helpdesk Assistant for Employee's of a Small Office Company for Basic Help")

    # main window setup
    page.window.frameless = True
    page.window.width, page.window.height = 400, 600
    page.bgcolor = ft.Colors.TRANSPARENT
    # end of window setup

    # background setup
    dynamic_background_gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[
                "#5a108f",
                "#8b2fc9"
            ]
        )
    page.decoration = ft.BoxDecoration(
        gradient=dynamic_background_gradient
    )
    # end of background setup

    # Moin Window Bar
    page.appbar = ft.CupertinoAppBar(
        # how to use app menu
        leading=ft.Container(
                    content=ft.Icon(
                        name=ft.Icons.BOOK,
                        tooltip="! ! ! ! IMPORTANT ! ! ! !\n"
                                "⚠️ Please send only one message at a time.\n"
                                "Multiple messages are placed in a queue, which can use extra resources "
                                "and may lead to performance issues or unexpected crashes.\n"
                    )
                ),
        # menu option area
        trailing=ft.MenuBar(
            controls=[
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(name=ft.Icons.MINIMIZE, tooltip="Minimize Program"),
                            on_click=lambda _: setattr(page.window, "minimized", True),
                        ),
                        ft.Container(
                            content=ft.Icon(name=ft.Icons.CLOSE_SHARP, tooltip="Exit Program"),
                            on_click=lambda _: page.window.close()
                        )
                    ],
                ),
            ],
        ),

        # drag area
        title=ft.Container(
            on_tap_down=frameless_drag,
            width=page.width + 100,
            height=30,
        ),
    )

    # starts background effect thread
    threading.Thread(target=main_background_effect, args=(page, 0, 0, 4, 0.7), daemon=True).start()
    threading.Thread(target=main_background_effect, args=(page, 1, 2, 10, 0.4), daemon=True).start()

    # begins Listener Thread for if LM Studio is up and off
    def updown_lm():
        global model, chat, IS_LM_RUNNING
        while True:
            os.system("clear")
            ping_server = subprocess.run(["lms server status"], shell=True, capture_output=True, text=True)
            print(ping_server.stderr)
            time.sleep(2)
            if "not" in ping_server.stderr:
                print("not running no more!!!\n")
                IS_LM_RUNNING = False
                # check if up
            if "is running" in ping_server.stderr and IS_LM_RUNNING is False:
                try:
                    lm.configure_default_client("memorylaptop.local:3333")
                except lm.LMStudioClientError:
                    pass
                model = lm.llm()
                chat = lm.Chat("You're a helpful Helpdesk Assistant for Employee's of a Small Office Company for Basic Help")
                IS_LM_RUNNING = True

    threading.Thread(target=updown_lm, daemon=True).start()

    # for AI response display
    model_response_text = ft.TextField(
                value=f"{". . . . waiting for response . . . .":>50}",
            multiline=True,
            text_align=ft.alignment.center,
            scroll_padding=20,
            read_only=True,
            border_width=0
            )

    # the response object filed (flutter)
    model_response_field = ft.Column(
        controls=[ft.Container(
            content=model_response_text,
            border=ft.Border(
                ft.BorderSide(2, color=ft.Colors.PURPLE_ACCENT),
                ft.BorderSide(2, color=ft.Colors.PURPLE_ACCENT),
                ft.BorderSide(2, color=ft.Colors.PURPLE_ACCENT),
                ft.BorderSide(2, color=ft.Colors.PURPLE_ACCENT)
            ),
            width=page.width,
            height=200,
            bgcolor=ft.Colors.TRANSPARENT,
        ),
        ],
        offset=(0, 0.44),
        width=page.width,
        expand=True,
        scroll=ft.ScrollMode.ALWAYS
    )

    # for 'actual' user input
    user_input_textfield = ft.CupertinoTextField(
                    placeholder_text="Ask Away!",
                    bgcolor=ft.Colors.TRANSPARENT,
                    border=ft.Border(
                        ft.BorderSide(0, ft.Colors.TRANSPARENT),
                        ft.BorderSide(0, ft.Colors.TRANSPARENT),
                        ft.BorderSide(0, ft.Colors.TRANSPARENT),
                        ft.BorderSide(0, ft.Colors.TRANSPARENT)
                    ),
                    multiline=True,
                )

    # this is the main user input object box
    # that holds the user input field
    user_input_box = ft.Column(
        controls=[
            ft.Container(
                content=user_input_textfield,
                width=page.width,
                height=50,
                #alignment=ft.alignment.bottom_center,
                expand=True,
            )
        ],
        width=290,
        height=50,
        scroll=ft.ScrollMode.ALWAYS,
    )

    page.add(
        # main helpdesk logo stack
        ft.Stack([
            ft.Container(
                content=
                ft.Image(
                    src="lavender ui.png",
                    scale=2.5,
                ),
                offset=(1.4, 0.6),
                width=100,
                height=100,
                expand=False
            ),
            # logo title
            ft.Text(
                value="Helpdesk AI",
                scale=3,
                offset=(1.9, 11.5),
                italic=True,
                weight=ft.FontWeight.BOLD
            ),
        ]),
        # displays response view
        model_response_field,

        # User Input Field Stack with Button
        ft.Stack([
            # this is ised for the main input background border
            ft.CupertinoTextField(
                width=page.width,
                height=50,
                expand=True,
                bgcolor=ft.Colors.TRANSPARENT
            ),

            # where user actually types response
            user_input_box,

            # Main Send Button
            ft.Button(
                text="Send",
                offset=(4.05, 0.3),
                icon=ft.Icons.CHAT,
                bgcolor="#5a108f",
                color="#ffffff",
                on_click=lambda _: model_response(page, user_input_textfield.value),
            )
        ])
    )

# main program
if __name__ == '__main__':
    ft.app(target=main)