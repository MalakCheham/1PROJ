def get_regles(jeu: str) -> str:
    jeu = jeu.lower()

    if jeu == "katarenga":
        return (
            "🎯 Objectif :\n"
            "- Atteindre les deux camps adverses après avoir franchi sa ligne.\n"
            "- Capturer les pions adverses pour l'empêcher.\n\n"
            "🟦 Déplacement selon la couleur :\n"
            "- Bleu : Roi (1 case toutes directions)\n"
            "- Vert : Cavalier (en L)\n"
            "- Jaune : Fou (diagonale, arrêt sur première case jaune)\n"
            "- Rouge : Tour (ligne/colonne, arrêt sur première case rouge)\n\n"
            "⚠️ Captures :\n"
            "- Possibles à partir du 2e tour.\n"
            "- Les pions capturés sont retirés du jeu."
        )

    elif jeu == "congress":
        return (
            "🎯 Objectif :\n"
            "- Rassembler tous vos pions en un seul bloc connexe (orthogonal).\n\n"
            "🟦 Déplacement :\n"
            "- Identique à Katarenga, selon la couleur de la case.\n\n"
            "❌ Pas de capture autorisée.\n"
            "- Les pions ne peuvent pas se superposer.\n"
            "- Le premier joueur à connecter tous ses pions gagne."
        )

    elif jeu == "isolation":
        return (
            "🎯 Objectif :\n"
            "- Être le dernier à pouvoir poser un pion.\n\n"
            "🕹️ Déroulement :\n"
            "- Chaque joueur place un pion à tour de rôle.\n"
            "- Un pion ne peut pas être placé sur une case en prise.\n\n"
            "⚠️ En prise :\n"
            "- Une case est en prise si un pion adverse pourrait y aller selon sa couleur.\n"
            "- Pas de capture, pas de déplacement : uniquement la pose de pions."
        )

    else:
        return "Aucune règle disponible pour ce jeu."
