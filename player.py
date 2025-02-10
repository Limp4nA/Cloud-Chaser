from PIL import Image, ImageTk  # For resizing the players image
import os

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.gravity = 0.5  # Gravity affecting the player
        self.max_vy = 10  # Maximum fall speed
        self.jump_strength = -15  # Upward velocity during a jump
        self.is_jumping = False

        # Load and resize the player image ghost.png
        try:
            self.original_image = Image.open(os.path.join("assets", "ghost.png"))
            self.resized_image = self.original_image.resize((60, 80), Image.Resampling.LANCZOS)  # Resize ghost
            self.image = ImageTk.PhotoImage(self.resized_image)

            # Set the players dimensions to match the image
            self.width, self.height = self.resized_image.size
        except Exception as e:
            print(f"Error loading players image.")
            self.image = None
            self.width = 40  # Fallback width
            self.height = 40  # Fallback height

    def move(self, direction):
        """Move the player left or right."""
        if direction == "left":
            self.vx = -5
        elif direction == "right":
            self.vx = 5

    def stop_moving(self):
        """Stop horizontal movement."""
        self.vx = 0

    def jump(self):
        """Initiate jump."""
        if not self.is_jumping:  # Allow jumping only if not already in the air
            self.vy = self.jump_strength
            self.is_jumping = True

    def land(self, platform):
        """Handle landing on a platform."""
        self.vy = 0
        self.y = platform.y - self.height
        self.is_jumping = False

    def update(self, auto_jump_enabled=False):
        """Update player position."""
        # Apply gravity only if not at max fall speed
        if self.vy < self.max_vy:
            self.vy += self.gravity

        # Jump automatically if auto jump is enabled and player is not already jumping
        if auto_jump_enabled and not self.is_jumping:
            self.jump()

        # Update position
        self.y += self.vy
        self.x += self.vx

        # Keep the player within screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > 400:
            self.x = 400 - self.width

    def reset_position(self, x, y):
        """Reset the players position and velocities."""
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.is_jumping = False

    def check_fall_off_screen(self):
        """Check if the player falls off the bottom of the screen."""
        if self.y > 600:  # Screen height
            print(f"Player fell off screen.")
            return True
        return False

    def draw(self, canvas):
        """Draw the player on the canvas."""
        if self.image:
            canvas.create_image(self.x, self.y, anchor="nw", image=self.image)