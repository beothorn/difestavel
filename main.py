import os
import threading
from io import BytesIO

from flask import Flask, redirect, url_for, send_file
from pyngrok import ngrok
import torch
from diffusers import StableDiffusionPipeline

pipe_test = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16,
                                                   revision="fp16")
pipe_test = pipe_test.to("cuda")
prompt_test = "a photo of an astronaut riding a horse on mars"
image_test = pipe_test(prompt_test).images[0]
print(image_test)

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


@app.route("/api/astronaut")
def index():
    img_io = BytesIO()
    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16,
                                                   revision="fp16")
    pipe = pipe.to("cuda")
    prompt = "a photo of an astronaut riding a horse on mars"
    image = pipe(prompt).images[0]
    image.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


# Start the Flask server in a new thread
threading.Thread(target=app.run, kwargs={"use_reloader": False}).start()
