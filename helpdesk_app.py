import socket
import threading
import time
import flet as ft
import lmstudio as lm

# LM Studio Server setup
IS_LM_RUNNING: bool = False
LM_SERVER_IP: str = "memorylaptop.local"
LM_SERVER_PORT: str = "3333"
IF_CHAT_RUNNING: bool = False

try:
    # put LM Studio Server IP Address Here
    lm.configure_default_client(LM_SERVER_IP + ":" + LM_SERVER_PORT)
    # main model
    model = lm.llm()
    # main chat context
    chat = lm.Chat("You're a helpful Helpdesk Assistant for Employee's of a Small Office Company for Basic Help")
    IS_LM_RUNNING = True
    print(f"LM STUDIO IS RUNNING AT {LM_SERVER_IP}:{LM_SERVER_PORT}\n")
except lm.LMStudioWebsocketError:
    pass


# end of LM Studio Server Setup

def m2(page: ft.Page):
    page.add(ft.TextField(label="test"))
# Main Flet Loop and Setup
def main(page: ft.Page):
    # important globals
    global IS_LM_RUNNING

    # important Flet functions section
    def main_background_effect(p, location_gradient, start_index, end_index, speed):
        nonlocal page, dynamic_background_gradient
        print(". . . . running background effect . . . .\n")
        c = ["#310055", "#3c0663", "#4a0a77", "#5a108f", "#6818a5", "#8b2fc9", "#ab51e3", "#bd68ee", "#d283ff",
             "#dc97ff"]

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

    # begins Listener Thread for if LM Studio is up and off
    def lm_listener():
        global model, chat, IS_LM_RUNNING
        # counter to check timeout
        timeout_check = 0
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # for cooldown
                time.sleep(2)

                # checks for connection
                is_lm_up = s.connect_ex((LM_SERVER_IP, int(LM_SERVER_PORT)))
                if is_lm_up == 0:
                    print("LM Studio is running!!\n")
                elif is_lm_up != 0:
                    print(f"timeout check = {timeout_check}\n")
                    timeout_check += 1
                    if timeout_check > 2:
                        print("LM Studio is down!\n")
                        IS_LM_RUNNING = False
                        return

    # ai functions
    def model_response(p, user_response):
        nonlocal model_response_text, user_input_textfield
        global model, chat, IF_CHAT_RUNNING

        # if another resposne thread is running, safely exit
        if IF_CHAT_RUNNING:
            print("can't chat twice!!!\n")
            return
        # if model or chat isn't found
        if IS_LM_RUNNING is False:
            model_response_text.value = "LM Studio isn't running!\n1. Close App.\n2. Run LM Studio with Loaded Model.\n3. Re-open App."
            user_input_textfield.value = ""
            return

        # clears previous responses
        user_input_textfield.value = ""
        model_response_text.value = ""

        # safely locks chat to prevent double response
        IF_CHAT_RUNNING = True

        # displays (streams) response in real time
        for f in model.respond_stream(user_response):
            model_response_text.value += f.content
            page.update()

        # clear context to free memory...
        chat.__dict__.clear()
        # resets Chat prompt
        chat = lm.Chat("You're a helpful Helpdesk Assistant for Employee's of a Small Office Company for Basic Help")
        IF_CHAT_RUNNING = False

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

    # starts server listener thread
    threading.Thread(target=lm_listener, daemon=True).start()

    # for AI response display
    model_response_text = ft.TextField(
        value=f"{". . . . waiting for response . . . .":>50}",
        multiline=True,
        text_align=ft.alignment.center,
        scroll_padding=20,
        read_only=True,
        border_width=0
    )

    # if LM Studio Server isn't up at startup
    if IS_LM_RUNNING is False:
        model_response_text.value = "LM Studio isn't running!\n1. Close App.\n2. Run LM Studio with Loaded Model.\n3. Re-open App."

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
                # alignment=ft.alignment.bottom_center,
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