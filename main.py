import os
import threading

from flask import Flask, redirect, url_for
from pyngrok import ngrok

os.environ["FLASK_DEBUG"] = "1"

app = Flask(__name__, static_folder='web/static')
port = 5000

auth_token = os.environ["NGROK_TOKEN"]
ngrok.set_auth_token(auth_token)

# Open a ngrok tunnel to the HTTP server
public_url = ngrok.connect(port).public_url
print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

# Update any base URLs to use the public ngrok URL
app.config["BASE_URL"] = public_url

# ... Update inbound traffic via APIs to use the public-facing ngrok URL


# Define Flask routes
@app.route("/")
def index():
    return redirect(url_for('static', filename='index.html'))

# Start the Flask server in a new thread
threading.Thread(target=app.run, kwargs={"use_reloader": False}).start()