import os
from pydantic import BaseModel
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import random
import string
import uvicorn

from pyngrok import ngrok
import torch
from diffusers import StableDiffusionPipeline

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5",
                                               torch_dtype=torch.float16,
                                               revision="fp16")
pipe = pipe.to("cuda")

port = 5000


def setup_ngrok():
    auth_token = os.environ["NGROK_TOKEN"]
    ngrok.set_auth_token(auth_token)
    public_url = ngrok.connect(port).public_url
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))
    return public_url


def generate_image(prompt):
    image = pipe(prompt).images[0]
    img_name = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(32))
    image.save('/tmp/' + img_name, 'JPEG', quality=90)
    return img_name


class TextToImageRequest(BaseModel):
    prompt: str


@app.get("/api/img/{id}")
async def get_img(id):
    return FileResponse('/tmp/' + id)


@app.post("/api/txt2img")
async def txt_to_img(param: TextToImageRequest):
    return {"src": generate_image(param.prompt)}


if __name__ == '__main__':
    setup_ngrok()
    uvicorn.run(app, host="127.0.0.1", port=port)
