import textbox


app = textbox.App()


@app.on_submit
def on_submit(text: str):
    app.print(f"User: ", end="")
    app.print(text.strip())
    app.print("AI: Hello!\n")


@app.command("quit")
def quit(command: str):
    app.print("Quitting...")
    app.stop()


if __name__ == "__main__":
    app.start()
