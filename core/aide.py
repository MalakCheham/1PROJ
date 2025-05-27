from core.parametres import get_language


def get_regles(jeu: str) -> list:
    """
    Retourne une liste de tuples (texte, is_emoji) pour chaque ligne, pour affichage ligne à ligne avec gestion des emojis.
    """
    lang = get_language()
    jeu = jeu.lower()
    if jeu == "katarenga":
        if lang == "en":
            lines = [
                ("🎯 Objective:", True),
                ("- Reach both opponent camps after crossing your own line.", False),
                ("- Capture opponent pawns to prevent them.", False),
                ("", False),
                ("🟦 Movement by color:", True),
                ("- Blue: King (1 square any direction)", False),
                ("- Green: Knight (L-shape)", False),
                ("- Yellow: Bishop (diagonal, stops on first yellow square)", False),
                ("- Red: Rook (row/column, stops on first red square)", False),
                ("", False),
                ("⚠️ Captures:", True),
                ("- Possible from the 2nd turn.", False),
                ("- Captured pawns are removed from the game.", False),
            ]
        else:
            lines = [
                ("🎯 Objectif :", True),
                ("- Atteindre les deux camps adverses après avoir franchi sa ligne.", False),
                ("- Capturer les pions adverses pour l'empêcher.", False),
                ("", False),
                ("🟦 Déplacement selon la couleur :", True),
                ("- Bleu : Roi (1 case toutes directions)", False),
                ("- Vert : Cavalier (en L)", False),
                ("- Jaune : Fou (diagonale, arrêt sur première case jaune)", False),
                ("- Rouge : Tour (ligne/colonne, arrêt sur première case rouge)", False),
                ("", False),
                ("⚠️ Captures :", True),
                ("- Possibles à partir du 2e tour.", False),
                ("- Les pions capturés sont retirés du jeu.", False),
            ]
    elif jeu == "congress":
        if lang == "en":
            lines = [
                ("🎯 Objective:", True),
                ("- Gather all your pawns into a single connected block (orthogonal).", False),
                ("", False),
                ("🟦 Movement:", True),
                ("- Same as Katarenga, according to the color of the square.", False),
                ("", False),
                ("❌ No captures allowed.", True),
                ("- Pawns cannot overlap.", False),
                ("- The first player to connect all their pawns wins.", False),
            ]
        else:
            lines = [
                ("🎯 Objectif :", True),
                ("- Rassembler tous vos pions en un seul bloc connexe (orthogonal).", False),
                ("", False),
                ("🟦 Déplacement :", True),
                ("- Identique à Katarenga, selon la couleur de la case.", False),
                ("", False),
                ("❌ Pas de capture autorisée.", True),
                ("- Les pions ne peuvent pas se superposer.", False),
                ("- Le premier joueur à connecter tous ses pions gagne.", False),
            ]
    elif jeu == "isolation":
        if lang == "en":
            lines = [
                ("🎯 Objective:", True),
                ("- Be the last to be able to place a pawn.", False),
                ("", False),
                ("🕹️ Gameplay:", True),
                ("- Each player places a pawn in turn.", False),
                ("- A pawn cannot be placed on a threatened square.", False),
                ("", False),
                ("⚠️ Threatened:", True),
                ("- A square is threatened if an opponent's pawn could go there according to its color.", False),
                ("- No capture, no movement: only pawn placement.", False),
            ]
        else:
            lines = [
                ("🎯 Objectif :", True),
                ("- Être le dernier à pouvoir poser un pion.", False),
                ("", False),
                ("🕹️ Déroulement :", True),
                ("- Chaque joueur place un pion à tour de rôle.", False),
                ("- Un pion ne peut pas être placé sur une case en prise.", False),
                ("", False),
                ("⚠️ En prise :", True),
                ("- Une case est en prise si un pion adverse pourrait y aller selon sa couleur.", False),
                ("- Pas de capture, pas de déplacement : uniquement la pose de pions.", False),
            ]
    else:
        lines = [("No rules available for this game." if lang == "en" else "Aucune règle disponible pour ce jeu.", False)]
    return lines
