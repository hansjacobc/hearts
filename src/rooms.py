from enum import StrEnum

TEN_MIN_TTL = 10 * 60
ONE_HOUR_TTL = 1 * 60 * 60
TWO_HOUR_TTL = 2 * 60 * 60


class RoomStatus(StrEnum):
    """Enum for room status"""

    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"


class GamePhase(StrEnum):
    """Game phases for hearts"""

    PASSING = "PASSING"
    PLAYING = "PLAYING"
    ROUND_END = "ROUND_END"
