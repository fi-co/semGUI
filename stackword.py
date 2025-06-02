import tkinter as tk

class StackWord:
    """
    A class representing a word in the stack (left sidebar) of the GUI. 
    """
    def __init__(self, container, word, on_select, bg="gray", fg="white"):
        self.container = container
        self.word = word
        self.on_select = on_select

        self.frame = tk.Frame(container, bg=bg, padx=5, pady=5, cursor="hand2")
        self.frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.label = tk.Label(self.frame, text=word, bg=bg, fg=fg, font=("Arial", 10, "bold"))
        self.label.pack(pady=3, fill=tk.X)

        self.frame.bind("<ButtonRelease-1>", self.on_click)
        self.label.bind("<ButtonRelease-1>", self.on_click)

    def on_click(self, event):
        """Handle click event on the word in the stack: remove the word and 
        add it to the canvas."""
        self.on_select(self.word)
        self.frame.destroy()
