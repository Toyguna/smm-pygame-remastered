import tkinter as tk

import scripts.game as game
import scripts.editor as editor

root = tk.Tk()

icon = tk.PhotoImage(file = "assets/resource/icon.png")
root.iconphoto(False, icon)

def launch_app(id: str):
    root.destroy()

    if id == "game":
        game.start()
    elif id == "editor":
        editor.start()


def main():
    root.resizable(False, False)

    root.title("SMM: Pygame Remastered")
    tk.Label(root, text="Choose the app to launch:").grid(row = 0, column = 0, pady=15, padx = 50)

    tk.Button(root, text="SMM: Pygame Remastered", command=lambda: launch_app("game")).grid(row = 1, column = 0)
    tk.Button(root, text="Editor", command=lambda: launch_app("editor")).grid(row = 2, column = 0, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()