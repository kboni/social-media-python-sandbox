# Main Flask REST API

## Description
Flask REST API for handling user's profile data, posts, comments and subcomments. 

## Resources
All resources require the 'Authoriyation' header containing an Access token

### User
Handling user's private profile information (username, password, name, surname, profile image, ...)

### Post
Handling post information

### Comment
Handling comments related to the posts and users

### SubComment
Handling comments related to the comments and users

## Models
### User
Contains User profile related fields, relationships and CRUD methods
### Post
Contains post related fields, relationships and CRUD methods
### Comment
Contains comment related fields, relationships and insert/delete methods
### SubComment
Contains subcomment related fields, relationships and insert/delete methods

## PEP8 codestyle check

### Docker
```bash
docker exec -it <container_id> /bin/bash
pycodestyle .
```

## Run unit tests

### Docker
```bash
docker exec -it <container_id> /bin/bash
pytest
```