from core.langues import translate

"""Game rules"""

def get_rules(game: str) -> str:
    game = game.lower()

    if game == "katarenga":
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

    elif game == "congress":
        return (
            f"{translate('objective')}\n"
            f"- {translate('congress_objective_1')}\n\n"
            f"{translate('move')}\n"
            f"- {translate('congress_move')}\n\n"
            f"{translate('no_capture_allowed')}\n"
            f"- {translate('pawns_cannot_overlap')}\n"
            f"- {translate('first_to_connect_wins')}"
        )

    elif game == "isolation":
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
