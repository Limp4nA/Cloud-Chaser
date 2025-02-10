class Leaderboard:
    def __init__(self):
        self.scores = self.load_leaderboard()

    def load_leaderboard(self):
        """Load leaderboard from a file."""
        try:
            with open("leaderboard.txt", "r") as f:
                scores = []
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:  # Ensure there are exactly two parts
                        name, score = parts
                        scores.append((name, int(score)))
                return scores
        except FileNotFoundError:
            print("Leaderboard file not found")
            return []

    def save_leaderboard(self):
        """Save leaderboard to a file."""
        with open("leaderboard.txt", "w") as f:
            for name, score in self.scores:
                f.write(f"{name} {score}\n")

    def update_leaderboard(self, name, score):
        """Add a new score to the leaderboard."""
        self.scores.append((name, score))
        self.scores.sort(key=lambda x: x[1], reverse=True)