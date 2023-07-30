import tkinter as tk

class DefinePlayer:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.root = tk.Tk()
        self.root.title("Player Name Entry")
        self.player_name = None

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate x and y coordinates for the window
        x = (screen_width // 2) - (self.w // 2)
        y = (screen_height // 2) - (self.h // 2)

        # Set the position and size of the window
        self.root.geometry(f"{self.w}x{self.h}+{x}+{y}")
        #self.root.geometry(f"{self.w}x{self.h}")
        self.create_widgets()
        self.run()

    def create_widgets(self):
        # Frame to hold the widgets
        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        # Label to display the text "Enter player name"
        label = tk.Label(frame, text="Enter player name", font=("Helvetica", 30))
        label.pack(pady=10)

        # Entry field for player name input
        self.player_name_entry = tk.Entry(frame)
        self.player_name_entry.pack(pady=5)

        # Button to start playing
        play_button = tk.Button(frame, text="Play", command=self.play)
        play_button.pack(pady=10)

        # Center the frame
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def play(self):
        self.player_name = self.player_name_entry.get()
        #print(f"Player name entered: {self.player_name}")  # You can replace this with the actual game logic
        
        # Close the window
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
   window = DefinePlayer()
   window.run()