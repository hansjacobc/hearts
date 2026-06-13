from enum import StrEnum


class RoomStatus(StrEnum):
    """Enum for room status"""

    WAITING = "WAITING"
    PLAYING = "PLAYING"


class GamePhase(StrEnum):
    """Game phases for hearts"""

    PASSING = "PASSING"
    PLAYING = "PLAYING"
    ROUND_END = "ROUND_END"
