class DeckNotDivisibleException(Exception):
    """
    Error thrown when deck dealing logic does not correctly make a leftover pile
    """

    def __init__(self, num_players: int, len_deck: int):
        super().__init__(
            f"Cannot evenly deal {len_deck} cards to {num_players} players. "
        )
