# game.py
import json  # For saving and loading game state
import os  # For file operations
import random  # For random platform generation
import tkinter as tk
from tkinter import simpledialog
from player import Player
from platform import Platform, Obstacle
from ui import UI
from leaderboard import Leaderboard
from ui import MainMenu
from PIL import Image, ImageTk  # For handling and resizing images

class Game:
    SAVE_FILE = "saves.json"  # Define the save file

    def __init__(self):
        self.root = tk.Tk()
        self.key_bindings = {
            "left": "<a>",
            "right": "<d>",
            "jump": "<w>",
        }
        self.root.title("Cloud Chaser")
        self.has_saved_game = False
        self.auto_jump_enabled = False
        self.cheat_codes = {"nomove": False, "nofall": False, "+jump": False}  # Track cheat codes
        self.create_default_save_file()

        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width, window_height = 400, 600
        position_top = int((screen_height - window_height) / 2)
        position_left = int((screen_width - window_width) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

        # Initialize canvas
        self.canvas = tk.Canvas(self.root, width=400, height=600)
        self.canvas.pack()

        # Load and resize the background image
        self.background_image = Image.open(os.path.join("assets", "background.png"))
        self.background_image = self.background_image.resize((400, 600), Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Draw the background once
        self.background = self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        # Initialize other components
        self.running = False
        self.score = 0
        self.platforms = []
        self.obstacles = []
        self.player = Player(200, 500)  # Starting position for the player
        self.leaderboard = Leaderboard()
        self.is_boss_key_active = False  # Track if the boss key is active
        self.setup_boss_key_overlay()

        # Initialize the main menu
        self.main_menu = MainMenu(
            self.canvas,
            self.start_game,
            self.quit_game,
            self.show_settings,
            self.show_leaderboard,
            self.background_photo
        )

        # Initialize the UI
        self.ui = UI(self.canvas, self.main_menu, self.background_photo)

        # Show the main menu
        self.show_menu()
        self.root.mainloop()

    def create_default_save_file(self):
        """Create or reset the default save file if no save exists."""
        # Check if the save file exists
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    state = json.load(f)

                # Validate the save file
                is_valid_save = (
                        not state.get("is_default", True) and
                        isinstance(state.get("score"), int) and state["score"] >= 0 and
                        "player" in state and
                        "platforms" in state and
                        isinstance(state["player"], dict) and
                        "x" in state["player"] and "y" in state["player"]
                )

                if is_valid_save:
                    print("Valid save file found.")
                    self.has_saved_game = True
                    return
                else:
                    print("Invalid or default save file. Resetting save.")
            except (json.JSONDecodeError, IOError, KeyError) as e:
                print(f"Error reading or validating save file: {e}")

        # Create a new default save file if no valid save exists
        default_state = {
            "score": 0,
            "player": {"x": 200, "y": 500, "vy": 0},
            "platforms": [],
            "is_default": True
        }
        try:
            with open(self.SAVE_FILE, "w") as f:
                json.dump(default_state, f)
            self.has_saved_game = False
            print("Default save file created.")
        except IOError as e:
            print(f"Error creating default save file: {e}")

    def show_menu(self):
        """Show the main menu and game instructions."""
        # Redraw the background
        self.canvas.delete("all")  # Clear all elements
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        # Display the main menu
        self.main_menu.display_menu()
        self.ui.display_instruction()  # Show instructions on the main menu

    def show_leaderboard(self):
        """Show the leaderboard."""
        self.ui.display_leaderboard_box(self.leaderboard.scores)

    def show_settings(self):
        """Display the remappable key settings menu."""
        self.ui.clear_temp_ui()
        self.main_menu.hide_menu()

        # Settings menu rectangle dimensions
        x1, y1, x2, y2 = 50, 100, 350, 500
        self.ui.draw_rounded_rectangle(x1, y1, x2, y2, radius=20, fill="lightblue", outline="white",
                                       tag="settings_menu")

        # Add settings text
        self.canvas.create_text(200, 130, text="Remap Keys", font=("Courier", 16), fill="black", tag="settings_menu")

        # Positions for key remapping labels and buttons
        label_x = 160
        button_x = 220
        start_y = 180
        step_y = 50

        # State variable to track which key is being remapped
        self.remapping_key = None

        def create_key_button(action, y_position):
            """Helper function to create a button for remapping a key."""
            # Add label for the action
            self.canvas.create_text(label_x, y_position, text=f"Move {action}:", font=("Courier", 12),
                                    fill="black", anchor="e", tag="settings_menu")

            # Create button with the current key binding
            button = self.canvas.create_rectangle(button_x - 30, y_position - 10, button_x + 30, y_position + 10,
                                                  fill="white", outline="black", tag=f"{action}_button")
            button_text = self.canvas.create_text(button_x, y_position, text=self.key_bindings[action],
                                                  font=("Courier", 12),
                                                  fill="black", tag=f"{action}_button_text")

            # Bind the button to wait for a key press
            def on_button_click(event):
                if self.remapping_key is not None:
                    return  # Prevent remapping multiple keys simultaneously
                self.remapping_key = action
                self.canvas.itemconfig(button_text, text="Press key")  # Update button text
                self.root.bind("<Key>", lambda e: on_key_press(e, action, button_text))  # Wait for key press

            # Add click bindings for both the button rectangle and text
            self.canvas.tag_bind(f"{action}_button", "<Button-1>", on_button_click)
            self.canvas.tag_bind(f"{action}_button_text", "<Button-1>", on_button_click)

        def on_key_press(event, action, button_text):
            """Handle key press and update the binding."""
            new_key = f"<{event.keysym}>"  # Capture the key pressed
            self.key_bindings[action] = new_key  # Update the key binding
            self.canvas.itemconfig(button_text, text=event.keysym)  # Update button to show the new key
            self.remapping_key = None  # Reset remapping state
            self.root.unbind("<Key>")  # Stop listening for key presses
            print(f"Key for '{action}' updated to: {new_key}")

        # Add key remapping buttons for each action
        create_key_button("left", start_y)
        create_key_button("right", start_y + step_y)
        create_key_button("jump", start_y + 2 * step_y)

        # Auto Jump toggle
        self.canvas.create_text(label_x, start_y + 3 * step_y, text="Auto Jump:", font=("Courier", 12), fill="black",
                                anchor="e", tag="settings_menu")
        toggle_color = "green" if self.auto_jump_enabled else "red"
        auto_jump_toggle = self.canvas.create_rectangle(
            button_x - 20, start_y + 3 * step_y - 10,
            button_x + 20, start_y + 3 * step_y + 10,
            fill=toggle_color, tag="auto_jump_toggle"
        )

        # Bind the toggle rectangle to the toggle_auto_jump method
        self.canvas.tag_bind("auto_jump_toggle", "<Button-1>", self.toggle_auto_jump)

        # Back to menu button
        self.canvas.create_rectangle(150, 450, 250, 480, fill="green", tag="back_to_menu_button")
        self.canvas.create_text(200, 465, text="Back to Menu", font=("Courier", 14), fill="white",
                                tag="back_to_menu_text")
        self.canvas.tag_bind("back_to_menu_button", "<Button-1>", lambda e: self.close_settings())
        self.canvas.tag_bind("back_to_menu_text", "<Button-1>", lambda e: self.close_settings())

    def close_settings(self):
        """Close the settings menu and return to the main menu."""
        self.ui.clear_temp_ui()
        self.show_menu()

    def return_to_menu(self):
        """Return to the main menu."""
        if self.running:  # If the game is running, pause it
            self.pause_game()
        else:  # If the game is not running, go back to the main menu
            self.running = False
            self.ui.clear_temp_ui()  # Clear game over or other screens
            self.show_menu()

    def cheat_menu(self):
        """Prompt for a cheat code and apply it."""
        code = simpledialog.askstring("Cheat Code", "Enter cheat code:", parent=self.root)
        if not code:
            return  # Exit if no code is entered

        code = code.strip().lower()

        if code in self.cheat_codes:
            self.cheat_codes[code] = not self.cheat_codes[code]

            if code == "nomove":
                if self.cheat_codes[code]:
                    print("Cheat activated: No moving platforms.")
                    for platform in self.platforms:
                        platform.toggle_movement(False)  # Disable movement for all platforms
                else:
                    print("Cheat deactivated: Moving platforms enabled.")
                    for platform in self.platforms:
                        platform.toggle_movement(True)  # Enable movement for all platforms

            elif code == "nofall":
                if self.cheat_codes[code]:
                    # Add a long platform at the bottom
                    if not any(p.y == 599 and p.width == 400 for p in self.platforms):
                        self.platforms.append(Platform(0, 599, is_moving=False, width=400))
                    print("Cheat activated: No falling.")
                else:
                    # Remove the long platform
                    self.platforms = [p for p in self.platforms if not (p.y == 599 and p.width == 400)]
                    print("Cheat deactivated: Falling possible.")

            elif code == "+jump":
                if self.cheat_codes[code]:
                    self.player.jump_strength = -30  # Double jump strength
                    print("Cheat activated: Double jump height.")
                else:
                    self.player.jump_strength = -15  # Restore default jump strength
                    print("Cheat deactivated: Default jump height restored.")
        elif code:
            print("Invalid cheat code entered.")

            # Create a custom dialog for invalid cheat code
            invalid_dialog = tk.Toplevel(self.root)
            invalid_dialog.title("Invalid Cheat Code")

            # Calculate the center position relative to the game window
            game_x = self.root.winfo_x()
            game_y = self.root.winfo_y()
            game_width = self.root.winfo_width()
            game_height = self.root.winfo_height()
            dialog_width, dialog_height = 300, 150

            # Calculate dialog position to center it in the game window
            center_x = game_x + (game_width // 2) - (dialog_width // 2)
            center_y = game_y + (game_height // 2) - (dialog_height // 2)
            invalid_dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")

            # Set it as a modal dialog
            invalid_dialog.transient(self.root)
            invalid_dialog.grab_set()  # Focus on this dialog

            # Add a label for the invalid cheat code message
            tk.Label(invalid_dialog, text=f"'{code}' is not a valid cheat code.", font=("Arial", 12),
                     wraplength=280).pack(pady=20)

            # Add an OK button to close the dialog
            tk.Button(invalid_dialog, text="OK", width=10, command=invalid_dialog.destroy).pack(pady=10)

            # Keep the dialog open until closed
            invalid_dialog.wait_window(invalid_dialog)

    def start_game(self):
        """Start or resume the game."""
        if self.running:  # Game is already running so return
            return

        # Check if a valid save exists
        if self.has_saved_game:
            self.ui.display_load_prompt(self.resume_from_save, self.start_new_game)
        else:
            self.start_new_game()  # Start a new game directly

    def start_new_game(self):
        """Start a new game without loading saved data."""
        # Reset game state
        self.ui.clear_temp_ui()
        self.platforms.clear()
        self.obstacles.clear()
        self.score = 0
        self.player.reset_position(200, 500)

        # Clear the canvas and redraw the background image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        self.setup_platforms()
        self.bind_keys()
        self.running = True

        self.save_game()  # Save the initial state
        self.update_game()

    def resume_from_save(self):
        try:
            # Open and load the save file
            with open(self.SAVE_FILE, "r") as f:
                state = json.load(f)

            # Check if its a default save file
            if state.get("is_default", True):
                print("Cannot resume from a default save. Starting a new game.")
                self.start_new_game()
                return

            # Additional validation
            if "score" not in state or "player" not in state or "platforms" not in state:
                raise ValueError("Save file is missing required keys.")

            if not isinstance(state["score"], int) or state["score"] < 0:
                raise ValueError("Invalid score in save file.")

            if not isinstance(state["player"], dict) or "x" not in state["player"] or "y" not in state["player"]:
                raise ValueError("Invalid player data in save file.")

            # Restore game state
            self.score = state["score"]
            self.player.x = state["player"]["x"]
            self.player.y = state["player"]["y"]
            self.player.vy = state["player"].get("vy", 0)

            # Clear existing platforms and load them from the save file
            self.platforms.clear()
            for p in state["platforms"]:
                if not isinstance(p, dict) or "x" not in p or "y" not in p:
                    print(f"Skipping invalid platform: {p}")
                    continue
                # Recreate the platform object and restore its attributes
                platform = Platform(p["x"], p["y"], is_moving=p.get("is_moving", False))
                platform.vx = p.get("vx", 0)
                self.platforms.append(platform)

            self.has_saved_game = True
            self.running = True
            self.bind_keys()
            self.update_game()

        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Failed to load save: {e}")
            self.start_new_game()

    def save_game(self):
        """Save the current game state to a file."""
        if self.running:  # Save only if the game is active
            # Save game state
            state = {
                "score": self.score,
                "player": {
                    "x": self.player.x,
                    "y": self.player.y,
                    "vy": self.player.vy
                },
                "platforms": [{"x": p.x, "y": p.y, "is_moving": p.is_moving, "vx": p.vx} for p in self.platforms],
                "is_default": False
            }
            try:
                with open(self.SAVE_FILE, "w") as f:
                    json.dump(state, f)
                self.has_saved_game = True  # Update the save flag
            except IOError as e:
                print(f"Error saving game: {e}")

    def quit_game(self):
        """Handle game quit."""
        if self.running:
            self.save_game()  # Save the game before quitting
        self.root.destroy()
        os._exit(0)

    def update_game(self):
        """Main game loop."""
        self.player.update(auto_jump_enabled=self.auto_jump_enabled)
        self.check_collisions()

        # Stop further updates if the game is over
        if not self.running:
            print("Game is not running. Exiting update loop.")
            return

        self.move_objects()  # Ensure moving platforms and obstacles are updated

        # Scroll objects and update the score
        if self.player.y < 300:
            offset = 300 - self.player.y
            self.player.y = 300
            self.scroll_objects(offset)
            self.score += int(offset // 10)

        # Clear and redraw canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)
        self.player.draw(self.canvas)

        # Draw platforms and obstacles
        for platform in self.platforms:
            platform.draw(self.canvas)
        for obstacle in self.obstacles:
            obstacle.draw(self.canvas)

        # Display score
        self.ui.display_score(self.score)

        # Check for game over
        if self.player.check_fall_off_screen():
            self.game_over()
            return  # Exit loop after game over

        # Progressive difficulty
        self.adjust_difficulty()

        # Continue the game loop
        if self.running:
            self.root.after(16, self.update_game)
            self.save_game()

    def check_collisions(self):
        """Check collisions with platforms and obstacles."""
        for platform in self.platforms:
            if platform.check_player_collision(self.player):
                self.player.land(platform)

        for obstacle in self.obstacles:
            if obstacle.interact_with_player(self.player):
                print(f"Collision with obstacle.)")
                if self.running:  # Ensure game is running
                    self.game_over()  # Trigger game over
                return

    def move_objects(self):
        """Move all objects on the screen."""
        for platform in self.platforms:
            platform.move()  # Move platforms
        for obstacle in self.obstacles:
            obstacle.move()  # Move obstacles

    def scroll_objects(self, offset):
        """Scroll platforms and spawn new ones as the screen scrolls up."""
        # Move all existing platforms and obstacles down by the offset
        for platform in self.platforms:
            if not (self.cheat_codes["nofall"] and platform.width == 400):
                platform.y += offset  # Scroll platforms
        for obstacle in self.obstacles:
            obstacle.y += offset

        # Remove platforms and obstacles that move off the bottom of the screen
        self.platforms = [platform for platform in self.platforms if platform.y < 600]
        self.obstacles = [obstacle for obstacle in self.obstacles if obstacle.y < 600]

        # Spawn new platforms above the screen
        while len(self.platforms) < 10:  # Maintain a minimum of 10 platforms
            # Randomly generate the X,Y coordinate for the new platform within the screen
            x = random.randint(0, 320)
            y = min([platform.y for platform in self.platforms]) - random.randint(self.platform_spacing - 20,
                                                                                  self.platform_spacing)
            is_moving = random.choice([True, False]) and not self.cheat_codes["nomove"]
            self.platforms.append(Platform(x, y, is_moving=is_moving))

            if self.cheat_codes["nofall"]:
                if not any(p.width == 400 and p.y == 599 for p in self.platforms):
                    self.platforms.append(Platform(0, 599, is_moving=False, width=400))
            # Spawn obstacles only if score > 100
            if self.score > 100 and random.random() < min(0.1, 0.02 + self.score / 5000):
                obstacle_x = random.randint(0, 380)
                obstacle_y = y - 20
                self.obstacles.append(Obstacle(obstacle_x, obstacle_y))
                print(f"Obstacle spawned at x={obstacle_x}, y={obstacle_y}")

    def toggle_auto_jump(self, event=None):
        """Toggle the auto jump state."""
        self.auto_jump_enabled = not self.auto_jump_enabled
        toggle_color = "green" if self.auto_jump_enabled else "red"
        self.canvas.itemconfig("auto_jump_toggle", fill=toggle_color)  # Update the color
        print(f"Auto Jump {'enabled' if self.auto_jump_enabled else 'disabled'}")

    def adjust_difficulty(self):
        """Adjust game difficulty based on the score."""
        difficulty_factor = self.score // 100  # Increase difficulty every 100 points

        # Increase platform speed
        for platform in self.platforms:
            if platform.is_moving:
                platform.vx = max(2, 2 + difficulty_factor) * (1 if platform.vx > 0 else -1)

        # Adjust gravity only if +jump is not active
        if not self.cheat_codes["+jump"]:
            self.player.gravity = min(1, 0.5 + 0.05 * difficulty_factor)
        else:
            self.player.gravity = 0.5  # Maintain default gravity if +jump is active

        # Reduce platform spacing
        self.platform_spacing = max(80, 120 - difficulty_factor * 5)

    def setup_platforms(self):
        """Initialize platforms at random positions."""
        # Add a starting platform beneath the player
        starting_platform = Platform(self.player.x - 20, self.player.y + self.player.height + 10, is_moving=False)
        self.platforms.append(starting_platform)

        # Add other random platforms
        for i in range(5):  # Create additional platforms
            x = random.randint(0, 320)
            y = 500 - i * 100  # Space platforms 100px apart vertically
            is_moving = random.choice([True, False]) and not self.cheat_codes["nomove"]
            self.platforms.append(Platform(x, y, is_moving=is_moving))

    def save_key_bindings(self, left_key, right_key, jump_key):
        """Save new key bindings and rebind keys."""
        self.key_bindings["left"] = left_key
        self.key_bindings["right"] = right_key
        self.key_bindings["jump"] = jump_key
        self.bind_keys()  # Rebind keys with the new settings
        print(f"New key bindings: {self.key_bindings}")
        self.close_settings()

    def bind_keys(self):
        """Bind keyboard controls based on user-defined key mappings."""
        # Unbind all previous keys
        for key in self.key_bindings.values():
            self.root.unbind(key)
        self.root.unbind("<KeyRelease>")
        self.root.unbind("<Escape>")
        self.root.unbind("c")
        self.root.unbind("b")

        # Bind new keys for movement
        self.root.bind(self.key_bindings["left"], lambda e: self.player.move("left"))
        self.root.bind(self.key_bindings["right"], lambda e: self.player.move("right"))
        self.root.bind(self.key_bindings["jump"], lambda e: self.player.jump())

        # Automatically handle key release to stop movement
        self.root.bind("<KeyRelease>", lambda e: self.player.stop_moving())

        # Bind key for toggling pause menu
        self.root.bind("<Escape>", lambda e: self.pause_game())

        # Bind keys for cheat menu and boss key
        self.root.bind("c", lambda e: self.cheat_menu())
        self.root.bind("b", lambda e: self.toggle_boss_key())

        print(f"Keys bindings: {self.key_bindings}")

    def unbind_keys(self):
        """Unbind all game keys."""
        # Unbind keys for movement actions
        self.root.unbind(f"<{self.key_bindings['left']}>")  # Unbind Move Left key
        self.root.unbind(f"<{self.key_bindings['right']}>")  # Unbind Move Right key
        self.root.unbind(f"<{self.key_bindings['jump']}>")  # Unbind Jump key

        # Unbind special keys
        self.root.unbind("<Escape>")  # Unbind the Escape key (pause game)
        self.root.unbind("c")  # Unbind the 'c' key (cheat menu)
        self.root.unbind("b")  # Unbind the 'b' key (boss key)

    def toggle_boss_key(self):
        """Toggle the boss key overlay."""
        if self.is_boss_key_active:
            print("Deactivating Boss Key.")
            self.boss_key_window.withdraw()  # Hide the boss key
            self.is_boss_key_active = False
            self.bind_keys()  # Re-enable game keybindings
            self.root.focus_set()  # Set focus back to root window
            print("Boss Key deactivated. Focus returned to root.")
        else:
            print("Activating Boss Key.")
            # Ensure it spans the full width of the screen horizontally
            screen_width = self.boss_key_window.winfo_screenwidth()
            screen_height = self.boss_key_window.winfo_screenheight()

            # Center vertically while covering horizontally
            adjusted_height = int(screen_height * 0.95)
            y_position = (screen_height - adjusted_height) // 2

            self.boss_key_window.geometry(f"{screen_width}x{adjusted_height}+0+{y_position}")
            self.boss_key_window.deiconify()  # Show the boss key
            self.is_boss_key_active = True
            self.unbind_keys()  # Temporarily disable game keybindings
            self.boss_key_window.focus_set()  # Ensure focus is on the boss key
            print("Boss Key activated. Focus set to boss key window.")
    def setup_boss_key_overlay(self):
        """Create the boss key overlay as a fullscreen window."""
        # Create a separate window for the boss key
        self.boss_key_window = tk.Toplevel(self.root)
        self.boss_key_window.withdraw()  # Initially hidden
        self.boss_key_window.overrideredirect(True)  # Remove borders and title bar
        self.boss_key_window.attributes("-fullscreen", True)  # Make it full screen
        self.boss_key_window.configure(bg="black")

        # Add text widget for user input
        self.boss_key_text = tk.Text(
            self.boss_key_window,
            bg="black",
            fg="green",
            font=("Courier", 18),
            wrap="none",
            insertbackground="white",  # Cursor color
        )
        # Insert default text
        if not self.boss_key_text.get("1.0", "end-1c").strip():
            self.boss_key_text.insert(
                "1.0",
                "import os\n"
                "import sys\n"
                "import random\n"
                "import time\n"
                "class GenericClass:\n"
                "    def __init__(self):\n"
                "        self.boss = 'angry'\n"
                "        self.i = 'am'\n"
                "        self.definitely = 'not working'\n\n"
                "    def status(self):\n"
                "        return f\"{self.i.capitalize()} {self.definitely}\"\n\n"
                "generic_instance = GenericClass()\n"
                "print(generic_instance.status())\n"
            )
        self.boss_key_text.pack(fill=tk.BOTH, expand=True)

        # Add custom close button in the top right corner
        close_button = tk.Canvas(self.boss_key_window, width=30, height=30, bg="black", highlightthickness=0)
        close_button.create_oval(5, 5, 25, 25, fill="red", outline="black")
        close_button.create_text(15, 15, text="X", font=("Arial", 10, "bold"), fill="white")
        close_button.place(x=self.boss_key_window.winfo_screenwidth() - 40, y=10)
        close_button.bind("<Button-1>", lambda e: self.toggle_boss_key())


        minimize_button = tk.Canvas(self.boss_key_window, width=30, height=30, bg="black", highlightthickness=0)
        minimize_button.create_oval(5, 5, 25, 25, fill="yellow", outline="black")
        minimize_button.create_text(15, 15, text="_", font=("Arial", 10, "bold"), fill="white")
        minimize_button.place(x=self.boss_key_window.winfo_screenwidth() - 80, y=10)

        fullscreen_button = tk.Canvas(self.boss_key_window, width=30, height=30, bg="black", highlightthickness=0)
        fullscreen_button.create_oval(5, 5, 25, 25, fill="green", outline="black")
        fullscreen_button.create_text(15, 15, text="□", font=("Arial", 10, "bold"), fill="white")
        fullscreen_button.place(x=self.boss_key_window.winfo_screenwidth() - 120, y=10)

    def game_over(self):
        """Handle game over logic."""
        if not self.running:
            return  # Prevent multiple triggers

        print(f"Game over triggered.")
        self.running = False  # Stop the game loop
        self.ui.clear_temp_ui()  # Clear the canvas
        self.unbind_keys()  # Disable controls
        self.ui.display_game_over_prompt(self.record_score)  # Display gameover UI

        # Delete the save file
        if os.path.exists(self.SAVE_FILE):
            os.remove(self.SAVE_FILE)
            print("Save file deleted on game over.")

        self.has_saved_game = False  # Reset the flag to indicate no valid save exists

    def restart_game(self):
        """Restart the game after a game over."""
        # Reset the score and clear all platforms and obstacles
        self.score = 0
        self.platforms.clear()
        self.obstacles.clear()
        self.player.reset_position(200, 500)

        # Delete the save file and recreate a default one
        if os.path.exists(self.SAVE_FILE):
            os.remove(self.SAVE_FILE)
            self.create_default_save_file()

        # Reset the save flag and start a new game
        self.has_saved_game = False
        self.start_new_game()

    def record_score(self, should_record):
        """Handle recording the players score."""
        self.ui.clear_temp_ui()  # Clear the game over prompt
        if should_record:
            self.ui.prompt_player_initials(self.finish_game_over)
        else:
            self.finish_game_over()

    def finish_game_over(self, initials=None):
        """Complete the game over process by showing the leaderboard."""
        if initials:
            # Record the score with player initials
            self.leaderboard.update_leaderboard(initials, self.score)
            self.leaderboard.save_leaderboard()

        # Clear the game over UI
        self.ui.clear_temp_ui()

        # Display the leaderboard instead of going directly to the menu
        self.ui.display_leaderboard_box(self.leaderboard.scores)

    def pause_game(self):
        """Toggle pause/resume."""
        if self.running:  # Pause
            print("Pausing game.")
            self.running = False
            self.ui.display_pause_menu(self.back_to_menu)
        else:  # Resume
            print("Resuming game.")
            self.resume_game()

    def resume_game(self):
        """Resume the game."""
        self.running = True
        self.ui.clear_temp_ui()  # Remove pause menu
        self.update_game()

    def back_to_menu(self):
        """Return to the main menu from the pause menu."""
        self.save_game()  # Auto save the game state
        self.running = False
        self.ui.clear_temp_ui()  # Clear the pause menu
        self.show_menu()