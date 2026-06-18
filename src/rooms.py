from enum import StrEnum

ONE_HOUR_TTL = 1 * 60 * 60
TWO_HOUR_TTL = 2 * 60 * 60


class RoomStatus(StrEnum):
    """Enum for room status"""

    WAITING = "WAITING"
    PLAYING = "PLAYING"


class GamePhase(StrEnum):
    """Game phases for hearts"""

    PASSING = "PASSING"
    PLAYING = "PLAYING"
    ROUND_END = "ROUND_END"
