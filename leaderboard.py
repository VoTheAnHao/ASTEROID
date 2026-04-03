import json
import os
import time


class Leaderboard:
    def __init__(self, filename="leaderboard.json"):
        self.filename = filename

        # nếu chưa có file → tạo file rỗng
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump([], f)

    # ===== LOAD =====
    def load(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except:
            return []

    # ===== SAVE =====
    def save_score(self, score, play_time, name="Unknown"):
        data = self.load()

        data.append({
            "name": name,
            "score": score,
            "time": round(play_time, 2)
        })

        data = sorted(data, key=lambda x: x["score"], reverse=True)

        with open(self.filename, "w") as f:
            json.dump(data[:10], f)
    def get_top(self):
        return self.load()