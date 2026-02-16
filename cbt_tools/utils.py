import random

def random_coping_skill():
    skills = [
        "Take a walk",
        "Practice deep breathing",
        "Call a friend",
        "Write in a journal",
        "Listen to music",
        "Try a grounding exercise",
        "Drink a glass of water",
        "Do a short meditation",
        "Stretch or do yoga",
        "List 3 things you’re grateful for"
    ]
    return random.choice(skills)
