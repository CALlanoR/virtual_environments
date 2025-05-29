from flask import Flask
import redis
import os

app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))

r = redis.Redis(host=redis_host, port=redis_port)

@app.route('/')
def hello():
    r.incr('hits')
    hits = r.get('hits').decode('utf-8')
    return f"Hello from Flask! This page has been visited {hits} times."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')