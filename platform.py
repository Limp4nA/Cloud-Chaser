import random  # For generating random platform properties

class Platform:
    def __init__(self, x, y, is_moving=False, width=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = 10
        self.is_moving = is_moving
        self.vx = random.choice([-2, 2]) if is_moving else 0
        self.color = "green"  # Default platform color
    def move(self):
        """Move the platform if it's a moving platform."""
        if self.is_moving:
            self.x += self.vx
            if self.x <= 0 or self.x + self.width >= 400:  # Reverse at screen edges
                self.vx = -self.vx

    def toggle_movement(self, enable):
        """Enable or disable platform movement."""
        self.is_moving = enable
        if not enable:
            self.vx = 0  # Stop movement when disabled

    def check_player_collision(self, player):
        """Check if the player lands on this platform."""
        return (
            player.vy > 0 and  # Ensure player is falling
            player.y + player.height >= self.y and  # Players bottom edge is at or below the platforms top
            player.y + player.height <= self.y + self.height and  # Within platforms vertical bounds
            player.x + player.width > self.x and  # Players right edge overlaps platforms left edge
            player.x < self.x + self.width  # Players left edge overlaps platforms right edge
        )

    def draw(self, canvas):
        """Draw the platform on the canvas."""
        canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill=self.color, outline=""
        )

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10  # Radius of the circle
        self.color = "red"  # Default obstacle color
        self.vx = random.choice([-2, 2])  # Horizontal movement speed

    def interact_with_player(self, player):
        """Check for collision with the player."""
        circle_center_x = self.x + self.radius
        circle_center_y = self.y + self.radius
        player_center_x = player.x + player.width / 2
        player_center_y = player.y + player.height / 2

        distance_squared = ((circle_center_x - player_center_x) ** 2 +
                            (circle_center_y - player_center_y) ** 2)

        collision = distance_squared <= (self.radius ** 3)
        if collision:
            print(f"Collision with obstacle!)")  # Debugging
        return collision

    def move(self):
        """Move the obstacle horizontally and reverse direction at screen edges."""
        self.x += self.vx
        if self.x <= 0 or self.x + self.radius * 2 >= 400:  # Reverse direction at edges
            self.vx = -self.vx

    def draw(self, canvas):
        """Draw the obstacle as a red circle on the canvas."""
        canvas.create_oval(
            self.x, self.y,
            self.x + self.radius * 2, self.y + self.radius * 2,
            fill=self.color
        )