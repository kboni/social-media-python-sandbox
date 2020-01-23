# SocialMedia (Python Flask REST API Sandbox)

## Description
A simple Social Media backend project with basic functionalities:
- 3-step registration
- Login
- 3-step forgotten password recovery
- User profile CRUD
- Post CRUD
- Post comments and subcomments CRUD

**Note:** This is a Flask REST API 'sandbox' project to practice and 
test my Python skills.

## Tech-stack
- Python 3.7
- Flask REST
- SQLAlchemy - Alembic
- PostreSQL 12.1
- Docker, docker-compose
- Postman - Newman

## Project components
- [Auth API](/auth_api)  
    *Authorization server - API for handling registration, login and token refresh*
- [Web API](/web_api)  
    *Main API with CRUD functionalities*
- Database  
    *Main PostgreSQL database*
- Redis  
    *Redis database used as a security feature during registration*
- [Static file server](/static-file-server)  
    *Simple server for uploading and serving static files*

## Dev environment with docker-compose
1. Install docker and docker-compose  
1. cd to project's main folder
1. Run
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -p dev-project up --build --force-recreate
```
1. *docker exec* into dev-project_web_api container
    ```bash
    docker exec -it <container_id> /bin/bash
    ```
1. If it's the first time running the app then initialize, migrate and update database,
   otherwise just upgrade database migrations from the inside of the container
   ```bash
   python manage.py db init
   python manage.py db migrate
   python manage.py db upgrade
   exit
   ```
2. Open http://localhost:1080 in the browser  
(It is the test e-mail client - all outgoing e-mails will be visible there)  
(It will be useful during registration process)

## Integration tests

Running integration tests:

1. Start up test docker-compose
    ```bash
    docker-compose -f docker-compose.yml -f docker-compose.test.yml -p test-project up --build --force-recreate
    ```
1. *docker exec* into test-project_web_api container
    ```bash
    docker exec -it <container_id> /bin/bash
    ```
1. Upgrade database migrations from inside the container
   ```bash
   python manage.py db upgrade
   exit
   ```
1. *docker exec* into test-project_database container
    ```bash
    docker exec -it <container_id> /bin/bash
    ```
1. Connect to database and reset tables
    ```bash
    psql test_db test_un -c 'TRUNCATE "USER" RESTART IDENTITY CASCADE;'
    exit
    ```
1. *docker exec* into test-project_web_api container again
    ```bash
    docker exec -it <container_id> /bin/bash
    ```
1. Upgrade database migrations from inside the container
   ```bash
   python manage_test_db.py db upgrade
   exit
   ```
1. Run docker newman container:
    ```bash
    cd integration_tests/
    docker build -t newman-integration:latest . --no-cache
    docker run --network test-project_default newman-integration:latest
    ```