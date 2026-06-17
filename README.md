# Hearts!

## Project Overview
I decided to build this because I was playing this game a lot with friends
during a surf trip in Mexico and I thought it would be a fun challenge to
code this game. I purposely did not throw claude at this because while I'm sure
could have done it faster, this project is for fun and learning.

## Architecture
This is a fairly simple python backend service that exposes restful style endpoints
and websockets through FastAPI, and uses redis as a persistence store for players,
game rooms, game state, and more.

