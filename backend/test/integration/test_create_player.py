import pytest


@pytest.mark.asyncio
async def test_create_player_endpoint_simple(client):
    response = await client.post(
        "/players",
        json={
            "nickname": "Hans",
        },
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json["nickname"] == "Hans"
    assert len(resp_json["player_id"]) == 6


@pytest.mark.asyncio
async def test_create_player_endpoint_taken_name(client):
    response = await client.post(
        "/players",
        json={
            "nickname": "Hans",
        },
    )

    assert response.status_code == 200

    response2 = await client.post(
        "/players",
        json={
            "nickname": "Hans",
        },
    )

    assert response2.status_code == 409
    resp_json = response2.json()
    assert resp_json["detail"]["code"] == "NICKNAME_TAKEN"
    assert resp_json["detail"]["message"] == "Nickname already taken"
