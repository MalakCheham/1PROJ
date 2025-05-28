def get_regles(jeu: str) -> str:
    from core.langues import traduire
    jeu = jeu.lower()

    if jeu == "katarenga":
        return (
            f"{traduire('objectif')}\n"
            f"- {traduire('objectif_katarenga_1')}\n"
            f"- {traduire('objectif_katarenga_2')}\n\n"
            f"{traduire('deplacement_selon_couleur')}\n"
            f"- {traduire('bleu_roi')}\n"
            f"- {traduire('vert_cavalier')}\n"
            f"- {traduire('jaune_fou')}\n"
            f"- {traduire('rouge_tour')}\n\n"
            f"{traduire('captures')}\n"
            f"- {traduire('captures_2e_tour')}\n"
            f"- {traduire('pions_captures_retires')}"
        )

    elif jeu == "congress":
        return (
            f"{traduire('objectif')}\n"
            f"- {traduire('objectif_congress_1')}\n\n"
            f"{traduire('deplacement')}\n"
            f"- {traduire('deplacement_congress')}\n\n"
            f"{traduire('pas_capture_autorisee')}\n"
            f"- {traduire('pions_pas_superposer')}\n"
            f"- {traduire('premier_connexe_gagne')}"
        )

    elif jeu == "isolation":
        return (
            f"{traduire('objectif')}\n"
            f"- {traduire('objectif_isolation_1')}\n\n"
            f"{traduire('deroulement')}\n"
            f"- {traduire('deroulement_isolation_1')}\n"
            f"- {traduire('deroulement_isolation_2')}\n\n"
            f"{traduire('en_prise')}\n"
            f"- {traduire('en_prise_def')}\n"
            f"- {traduire('pas_capture_pas_deplacement')}"
        )

    else:
        return traduire('aucune_regle')
