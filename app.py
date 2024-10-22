# run.py
from flask import Flask
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # Makes the server externally visible
        port=3000,       # Specify port
        debug=True       # Enable debug mode for development
    )