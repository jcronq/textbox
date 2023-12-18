import textbox
from textbox import ColorCode


app = textbox.App()


@app.on_submit
def on_submit(text: textbox.Text):
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(textbox.TextSegment("User: ", ColorCode.DARK_BLUE))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)
    app.print(
        textbox.Text(
            [
                textbox.TextLine(
                    textbox.SegmentedTextLine(
                        [
                            textbox.TextSegment("AI: ", ColorCode.DARK_PURPLE),
                            textbox.TextSegment("Hello!", ColorCode.LIGHT_PURPLE),
                        ]
                    )
                ),
                textbox.TextLine(),
            ]
        )
    )


@app.command("quit")
def quit(command: str):
    app.print("Quitting...")
    app.stop()


if __name__ == "__main__":
    app.start()
