import tkinter as tk  # For creating and managing UI components
from tkinter import Entry  # For text input fields in UI
from PIL import Image, ImageTk  # Import Image and ImageTk from Pillow
import os

class UI:
    def __init__(self, canvas, main_menu, background_photo):
        self.canvas = canvas
        self.main_menu = main_menu
        self.background_photo = background_photo

    def show_menu(self):
        """Show the main menu and game instructions."""
        self.main_menu.display_menu()
        self.ui.display_instruction()

    def display_game_over_prompt(self, record_callback):
        """Display a prompt asking if the player wants to record their score."""
        print("Displaying game over prompt.")  # Debug log
        self.clear_temp_ui()

        # Draw the rectangular box
        x1, y1, x2, y2 = 100, 200, 300, 350
        self.draw_rounded_rectangle(x1, y1, x2, y2, radius=20, fill="lightblue", outline="white",
                                    tag="game_over_prompt")

        # Add Game Over text
        self.canvas.create_text(200, 240, text="Game Over", font=("Courier", 20), fill="white",
                                tag="game_over_prompt_text")
        self.canvas.create_text(200, 280, text="Record score?", font=("Courier", 14), fill="white",
                                tag="game_over_prompt_text")

        # Add Yes and No buttons
        yes_button = self.canvas.create_rectangle(120, 320, 180, 350, fill="green", outline="", tag="game_over_yes")
        yes_text = self.canvas.create_text(150, 335, text="Yes", font=("Courier", 14), fill="white",
                                           tag="game_over_yes_text")

        no_button = self.canvas.create_rectangle(220, 320, 280, 350, fill="red", outline="", tag="game_over_no")
        no_text = self.canvas.create_text(250, 335, text="No", font=("Courier", 14), fill="white",
                                          tag="game_over_no_text")

        # Bind clicks to the button areas
        self.canvas.tag_bind(yes_button, "<Button-1>", lambda e: record_callback(True))
        self.canvas.tag_bind(yes_text, "<Button-1>", lambda e: record_callback(True))
        self.canvas.tag_bind(no_button, "<Button-1>", lambda e: record_callback(False))
        self.canvas.tag_bind(no_text, "<Button-1>", lambda e: record_callback(False))

    def display_load_prompt(self, load_callback, new_callback):
        """Prompt the user to load a saved game or start a new game."""
        self.clear_temp_ui()

        # Draw prompt box
        x1, y1, x2, y2 = 100, 200, 300, 350
        self.draw_rounded_rectangle(x1, y1, x2, y2, radius=20, fill="lightblue", outline="white", tag="load_prompt_box")

        # Add prompt text
        self.canvas.create_text(200, 240, text="Resume previous game?", font=("Courier", 16), fill="black",
                                tag="load_prompt_text")

        # Add Yes and No buttons
        yes_button = self.canvas.create_rectangle(120, 300, 180, 340, fill="green", outline="", tag="load_yes")
        yes_text = self.canvas.create_text(150, 320, text="Yes", font=("Courier", 14), fill="white",
                                           tag="load_yes_text")

        no_button = self.canvas.create_rectangle(220, 300, 280, 340, fill="red", outline="", tag="load_no")
        no_text = self.canvas.create_text(250, 320, text="No", font=("Courier", 14), fill="white", tag="load_no_text")

        # Bind buttons to callbacks
        self.canvas.tag_bind("load_yes", "<Button-1>", lambda e: load_callback())
        self.canvas.tag_bind("load_yes_text", "<Button-1>", lambda e: load_callback())
        self.canvas.tag_bind("load_no", "<Button-1>", lambda e: new_callback())
        self.canvas.tag_bind("load_no_text", "<Button-1>", lambda e: new_callback())

    def prompt_player_initials(self, finish_callback):
        """Prompt the player to enter their initials."""
        self.clear_temp_ui()

        # Draw the rectangular box
        x1, y1, x2, y2 = 100, 250, 300, 350
        self.draw_rounded_rectangle(x1, y1, x2, y2, radius=20, fill="lightblue", outline="white", tag="initials_prompt")

        # Add Enter Initials text
        self.canvas.create_text(200, 270, text="Enter Initials:", font=("Courier", 14), fill="white",
                                tag="initials_prompt_text")

        # Create a text entry box
        entry = Entry(self.canvas, font=("Courier", 14), justify="center")
        entry_window = self.canvas.create_window(200, 300, width=140, height=30, window=entry,
                                                 tag="initials_prompt_entry")

        # Add Submit button
        submit_button = self.canvas.create_rectangle(150, 320, 250, 350, fill="green", outline="",
                                                     tag="initials_submit")
        self.canvas.create_text(200, 335, text="Submit", font=("Courier", 14), fill="white", tag="initials_submit_text")

        def submit_initials():
            initials = entry.get()[:3].upper()  # Limit to 3 characters
            self.canvas.delete("initials_prompt")
            finish_callback(initials)

        # Bind Submit button action
        self.canvas.tag_bind("initials_submit", "<Button-1>", lambda e: submit_initials())

    def display_leaderboard_box(self, scores):
        """Display the leaderboard in a compact box."""
        self.clear_temp_ui()

        # Track leaderboard elements to clear them later
        self.leaderboard_elements = []

        # Draw the rectangular box
        x1, y1, x2, y2 = 50, 100, 350, 500
        self.leaderboard_elements.append(
            self.draw_rounded_rectangle(x1, y1, x2, y2, radius=20, fill="lightblue", outline="white", tag="leaderboard_box")
        )

        # Add Leaderboard title
        self.leaderboard_elements.append(
            self.canvas.create_text(200, 130, text="Leaderboard", font=("Courier", 20), fill="white",
                                    tag="leaderboard_title")
        )

        # Display top scores
        y_position = 160
        for i, (name, score) in enumerate(scores[:10]):  # Show top 10 scores
            self.leaderboard_elements.append(
                self.canvas.create_text(
                    200, y_position,
                    text=f"{i + 1}. {name}: {score}",
                    font=("Courier", 14),
                    fill="white",
                    tag="leaderboard_entry"
                )
            )
            y_position += 30

        # Add Back to Menu button
        back_button = self.canvas.create_rectangle(150, 450, 250, 480, fill="green", outline="", tag="back_to_menu")
        back_text = self.canvas.create_text(200, 465, text="Back to Menu", font=("Courier", 14), fill="white",
                                            tag="back_to_menu_text")

        # Add elements to leaderboard tracking
        self.leaderboard_elements.append(back_button)
        self.leaderboard_elements.append(back_text)

        # Bind Back to Menu button
        self.canvas.tag_bind("back_to_menu", "<Button-1>", lambda e: self.main_menu.display_menu())
        self.canvas.tag_bind("back_to_menu_text", "<Button-1>", lambda e: self.main_menu.display_menu())

    def clear_leaderboard(self):
        """Clear leaderboard elements."""
        if hasattr(self, "leaderboard_elements"):
            for element in self.leaderboard_elements:
                self.canvas.delete(element)
            self.leaderboard_elements.clear()

    def clear_temp_ui(self):
        """Clear temporary UI elements and redraw background."""
        self.canvas.delete("all")  # Clears everything
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)  # Use the background photo

    def display_score(self, score):
        """Display the score on the screen."""
        self.canvas.delete("score")
        self.canvas.create_text(350, 20, text=f"Score: {score}", tag="score", fill="black", font=("Courier", 16))

    def display_leaderboard(self, scores):
        """Display the leaderboard."""
        y_position = 100
        self.canvas.create_text(
            200, 50, text="Leaderboard", font=("Courier", 24), fill="gold", tag="leaderboard_title"
        )
        for i, (name, score) in enumerate(scores[:10]):  # Display top 10 scores
            self.canvas.create_text(
                200, y_position,
                text=f"{i + 1}. {name}: {score}",
                font=("Courier", 16),
                fill="white",
                tag="leaderboard_entry"
            )
            y_position += 30

    def display_pause_menu(self, back_to_menu_callback):
        """Show the pause menu."""
        self.clear_temp_ui()  # Clear any existing temporary UI

        # Draw pause menu
        x1, y1, x2, y2 = 50, 150, 350, 450
        self.draw_rounded_rectangle(x1, y1, x2, y2, radius=20, fill="lightblue", outline="white", tag="pause_menu")

        # Add pause text
        self.canvas.create_text(200, 180, text="Game Paused", font=("Courier", 20), fill="red", tag="pause_text")
        self.canvas.create_text(200, 220, text="Press 'Escape' to Resume", font=("Courier", 14), fill="black",
                                tag="pause_instructions")

        # Add "Back to Menu" button
        menu_button = self.canvas.create_rectangle(120, 320, 280, 360, fill="orange", outline="",
                                                   tag="pause_menu_button")
        menu_text = self.canvas.create_text(200, 340, text="Back to Menu", font=("Courier", 14), fill="white",
                                            tag="pause_menu_button_text")

        # Bind "Back to Menu" button
        self.canvas.tag_bind("pause_menu_button", "<Button-1>", lambda e: back_to_menu_callback())
        self.canvas.tag_bind("pause_menu_button_text", "<Button-1>", lambda e: back_to_menu_callback())

    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius, fill, outline, tag=None):
        """Draw a rectangle with rounded corners."""
        # Draw corners
        self.canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, fill=fill,
                               outline=outline, tag=tag)
        self.canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, fill=fill, outline=outline,
                               tag=tag)
        self.canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, fill=fill,
                               outline=outline, tag=tag)
        self.canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, fill=fill,
                               outline=outline, tag=tag)

        # Draw edges
        self.canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=fill, outline=outline, tag=tag)
        self.canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=fill, outline=outline, tag=tag)

    def display_game_over(self):
        """Show the game over screen."""
        self.clear_temp_ui()  # Clear any existing temporary UI
        self.canvas.create_text(
            200, 250, text="Game Over",
            tag="game_over", fill="lightblue", font=("Courier", 30), justify="center"
        )
        self.canvas.create_text(
            200, 300, text="Press 'R' to Restart or 'Esc' to Quit",
            tag="game_over", fill="lightblue", font=("Courier", 16), justify="center"
        )

    def clear_temp_ui(self):
        """Clear temporary UI elements and redraw background."""
        self.canvas.delete("all")  # Clears everything
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)  # Use the passed background_photo

    def display_instruction(self):
        """Display game instructions at the start."""
        self.canvas.create_text(
            200, 200, text="How to Play:", tag="instructions_title", font=("Courier", 20), fill="black"
        )
        instructions = (
            "Avoid falling off the screen and obstacles\n"
            "Reach the highest score!"
        )
        self.canvas.create_text(
            200, 235, text=instructions, tag="instructions_text", font=("Courier", 14), fill="black", justify="center"
        )

    def hide_instruction(self):
        """Remove instructions from the screen."""
        self.canvas.delete("instructions_title")
        self.canvas.delete("instructions_text")


class MainMenu:
    def __init__(self, canvas, start_callback, quit_callback, settings_callback, leaderboard_callback, background_photo):
        self.canvas = canvas
        self.start_callback = start_callback
        self.quit_callback = quit_callback
        self.settings_callback = settings_callback
        self.leaderboard_callback = leaderboard_callback
        self.background_photo = background_photo  # Store the background photo
        self.menu_items = []  # To track displayed elements

    def display_menu(self):
        """Display the main menu items."""
        # Clear all canvas elements
        self.canvas.delete("all")

        # Redraw the background
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        self.menu_items.append(self.canvas.create_text(
            200, 150, text="Welcome to Cloud Chaser", font=("Courier", 25, "bold"), fill="black"))

        # Start button
        start_button = self.canvas.create_rectangle(150, 300, 250, 340, fill="blue", outline="")
        start_text = self.canvas.create_text(200, 320, text="Start", font=("Courier", 14), fill="white")

        # Settings button
        settings_button = self.canvas.create_rectangle(150, 360, 250, 400, fill="orange", outline="")
        settings_text = self.canvas.create_text(200, 380, text="Settings", font=("Courier", 14), fill="white")

        # Quit button
        quit_button = self.canvas.create_rectangle(150, 420, 250, 460, fill="red", outline="")
        quit_text = self.canvas.create_text(200, 440, text="Quit", font=("Arial", 14), fill="white")

        # Load and resize leaderboard icon using Pillow
        leaderboard_icon_path = os.path.join("assets", "leaderboard.png")
        leaderboard_image = Image.open(leaderboard_icon_path)
        leaderboard_image = leaderboard_image.resize((60, 60), Image.Resampling.LANCZOS) # Resizing leaderboard.png
        leaderboard_photo = ImageTk.PhotoImage(leaderboard_image)

        # Add leaderboard icon to bottom right corner
        leaderboard_button = self.canvas.create_image(370, 570, anchor="center", image=leaderboard_photo,
                                                      tag="leaderboard_icon")
        self.canvas.image = leaderboard_photo

        # Bind buttons to actions
        self.canvas.tag_bind(start_button, "<Button-1>", lambda e: self.start_callback())
        self.canvas.tag_bind(start_text, "<Button-1>", lambda e: self.start_callback())

        self.canvas.tag_bind(settings_button, "<Button-1>", lambda e: self.settings_callback())
        self.canvas.tag_bind(settings_text, "<Button-1>", lambda e: self.settings_callback())

        self.canvas.tag_bind(quit_button, "<Button-1>", lambda e: self.quit_callback())
        self.canvas.tag_bind(quit_text, "<Button-1>", lambda e: self.quit_callback())

        # Bind leaderboard icon click
        self.canvas.tag_bind("leaderboard_icon", "<Button-1>", lambda e: self.leaderboard_callback())

        # Track menu items for easy removal later
        self.menu_items.extend(
            [start_button, start_text, settings_button, settings_text, quit_button, quit_text, leaderboard_button])

    def hide_menu(self):
        """Remove the main menu items."""
        for item in self.menu_items:
            self.canvas.delete(item)
        self.menu_items.clear()
