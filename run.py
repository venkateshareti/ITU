import os


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'stag'
    os.environ['SECRET_KEY'] = 'SECRET_KEY'

    from wsgi import app

    app.run(debug=True)
