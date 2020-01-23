#!/bin/sh

# OPTIONAL: Uncomment for automatic database migration update
# NOTE: For this to work a mechanism should be implemented first, 
#       which senses whether the database is ready.
# if [ ! -d "migrations" ]; then
# 	python manage.py db init
#     python manage.py db migrate
# fi

# python manage.py db upgrade

python app.py