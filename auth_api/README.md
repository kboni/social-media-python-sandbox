# Authorization Flask REST API 

## Description
Flask REST API for handling registration, login and token refresh processes.

## Resources
### Register
3-step registration

### Login
Basic username-password login which generates the Access and Refresh tokens

### Password
Changing password in the case of forgotten password

### Token
Refreshing Access token in case of expiration

## Registration process
1. In a JSON body an e-mail is received
   1. Checking if e-mail is already in the main database
   2. Checking if e-mail is already in the Redis database
   3. Generating registration code
   4. Generation token with the email and registration code as payload
   5. Saving the token into Redis as a key-value => email-token
   6. Sending the registration code by e-mail

2. In a JSON body the e-mail and registration code are received
   1. Retrieving the token from Redis by the e-mail as the key
   2. Checking whether the registration codes from the request and token payload are matching
   3. Removing old token
   4. Generating new token with only the e-mail as payload
   5. Saving the token into Redis as a key-value => email-token
   6. Sending the token back to the user as a response

3. In a JSON body the token, username and password are received
   1. Validating token and getting e-mail from the payload
   2. Check if username is available (must be unique)
   3. Delete Redis entry
   4. Create new user in the database
   5. Return user data

## Login process
1. Receive username and password in headers, base64 encoded (Basic Authentication)
2. Check in the database
3. Generate and return Access and Refresh tokens

## Access token refresh process
1. Receive Refresh token in 'Authorization' header
2. Validate refresh token (expiration and signature)
3. Generate and return a new Access Token

## Forgotten password recovery process
1. In a JSON body an e-mail is received
   1. Checking if e-mail is in the main database
   2. Checking if e-mail is in the Redis database
   3. Generating confirmation code
   4. Generation token with the email and confirmation code as payload
   5. Saving the token into Redis as a key-value => email-token
   6. Sending the confirmation code by e-mail

2. In a JSON body the e-mail and confirmation code are received
   1. Retrieving the token from Redis by the e-mail as the key
   2. Checking whether the confirmation codes from the request and token payload are matching
   3. Removing old token
   4. Generating new token with only the e-mail as payload
   5. Saving the token into Redis as a key-value => email-token
   6. Sending the token back to the user as a response

3. In a JSON body the token, username and password are received
   1. Validating token and getting e-mail from the payload
   2. Check if username and e-mail combination exists and is valid
   3. Delete Redis entry
   4. Set new password
   5. Return user data

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