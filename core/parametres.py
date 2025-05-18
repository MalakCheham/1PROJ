import os

chemin_langue = os.path.join("assets", "langue.txt")
if os.path.exists(chemin_langue):
    with open(chemin_langue, "r", encoding="utf-8") as f:
        LANGUE_ACTUELLE = f.read().strip()
else:
    LANGUE_ACTUELLE = "fr"

def set_langue(langue):
    global LANGUE_ACTUELLE
    if langue in ["fr", "en"]:
        LANGUE_ACTUELLE = langue
