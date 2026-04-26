import json
import os

def load_json(filepath, default_data):
    if not os.path.exists(filepath):
        save_json(filepath, default_data)
        return default_data
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_settings():
    default_settings = {"sound": True, "color": "Red", "difficulty": "Medium"}
    return load_json("settings.json", default_settings)

def save_settings(settings):
    save_json("settings.json", settings)

def load_leaderboard():
    return load_json("leaderboard.json", [])

def save_score(name, score, distance):
    lb = load_leaderboard()
    lb.append({"name": name, "score": score, "distance": distance})
    lb = sorted(lb, key=lambda x: x["score"], reverse=True)[:10]
    save_json("leaderboard.json", lb)