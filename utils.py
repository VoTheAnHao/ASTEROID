import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS

        # 🔥 FIX CHUẨN MAC
        base_path = os.path.abspath(
            os.path.join(base_path, "..", "Resources")
        )

    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)