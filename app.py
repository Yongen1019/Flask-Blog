from flaskblog import create_app, db, Users

app = create_app()

if __name__ == '__main__':
    app.run()