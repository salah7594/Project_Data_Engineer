from flask import Flask
from app import app

if __name__ == '__main__':
    # threaded equal to true lets the application make use of the available cores of the host machine
    # in order to provide better performances.
    app.run(debug=True, port=1000, host='0.0.0.0', threaded=True) 
