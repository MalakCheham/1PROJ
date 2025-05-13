LANGUE_ACTUELLE = "fr"

def set_langue(langue):
    global LANGUE_ACTUELLE
    if langue in ["fr", "en"]:
        LANGUE_ACTUELLE = langue
