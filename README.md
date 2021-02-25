# TutorApp Backend
![example workflow](https://github.com/Southwestern-Higher-Learning/TutorBackEnd/actions/workflows/main.yml/badge.svg)

Built using FastAPI and Docker

## Developing
When using docker-compose, you need to run some tests to ensure the quality of your code:

`docker-compose exec web python -m pytest .`

`docker-compose exec web python -m black .`

`docker-compose exec web python -m isort .`

`docker-compose exec web python -m flake8 .`
Fix whatever you need to fix here