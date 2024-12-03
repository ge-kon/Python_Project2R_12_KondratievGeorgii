from flask import Flask
import requests


api_key = 'wV5H0MQlbLQmiiZlDFz809FpAned4Rz7'

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)