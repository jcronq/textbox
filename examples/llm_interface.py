import textbox
from textbox import ColorCode
from textbox.colored import dark_blue, dark_purple, light_purple


app = textbox.App()


@app.on_submit
def on_submit(text: textbox.Text):
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("User: "))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)
    app.print(
        [
            textbox.TextLine([dark_purple("AI: "), light_purple("Hello!")]),
            textbox.TextLine(),
        ]
    )


@app.command("quit")
def quit(command: str):
    app.print("Quitting...")
    app.stop()


@app.command("load")
def load(command: str):
    character = command.split(" ")[1]
    app.print(f"Loading {character}...")


if __name__ == "__main__":
    app.start()
