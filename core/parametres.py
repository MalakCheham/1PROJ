import os

current_language = None
language_file_path = os.path.join("assets", "language.txt")

def load_language():
    global current_language
    if current_language is None:
        if os.path.exists(language_file_path):
            with open(language_file_path, 'r', encoding='utf-8') as f:
                current_language = f.read().strip()
        else:
            current_language = 'fr'
    return current_language


def get_language():
    return load_language()


def set_language(lang):
    global current_language
    with open(language_file_path, 'w', encoding='utf-8') as f:
        f.write(lang)
    current_language = lang  # Met à jour la variable globale immédiatement