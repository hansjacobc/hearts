from redis.asyncio import Redis
from src.schemas import StartGameRequest, StartGameResponse


async def handle_start_game(
    request: StartGameRequest, redis: Redis
) -> StartGameResponse:
    """
    Verify enough players joined.
    Create/shuffle deck.
    Deal hands.
    Initialize turn state.
    Mark room as playing.
    """
    pass
