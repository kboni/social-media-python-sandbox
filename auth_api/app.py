import flask_init
import models
import resources


if __name__ == '__main__':
    flask_init.app.run(debug=flask_init.app.config['DEBUG'], host='0.0.0.0')
