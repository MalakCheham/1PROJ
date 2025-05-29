from core.langues import translate

"""
    Les règles des jeux
"""

def get_regles(jeu: str) -> str:
    jeu = jeu.lower()

    if jeu == "katarenga":
        return (
            f"{translate('objective')}\n"
            f"- {translate('katarenga_objective_1')}\n"
            f"- {translate('katarenga_objective_2')}\n\n"
            f"{translate('move_according_to_color')}\n"
            f"- {translate('blue_king')}\n"
            f"- {translate('green_knight')}\n"
            f"- {translate('yellow_bishop')}\n"
            f"- {translate('red_rook')}\n\n"
            f"{translate('captures')}\n"
            f"- {translate('captures_from_2nd_turn')}\n"
            f"- {translate('captured_pawns_removed')}"
        )

    elif jeu == "congress":
        return (
            f"{translate('objective')}\n"
            f"- {translate('congress_objective_1')}\n\n"
            f"{translate('move')}\n"
            f"- {translate('congress_move')}\n\n"
            f"{translate('no_capture_allowed')}\n"
            f"- {translate('pawns_cannot_overlap')}\n"
            f"- {translate('first_connected_wins')}"
        )

    elif jeu == "isolation":
        return (
            f"{translate('objective')}\n"
            f"- {translate('isolation_objective_1')}\n\n"
            f"{translate('how_to_play')}\n"
            f"- {translate('isolation_how_to_play_1')}\n"
            f"- {translate('isolation_how_to_play_2')}\n\n"
            f"{translate('threatened')}\n"
            f"- {translate('threatened_definition')}\n"
            f"- {translate('no_capture_no_movement')}"
        )

    else:
        return translate('no_rules_available')
