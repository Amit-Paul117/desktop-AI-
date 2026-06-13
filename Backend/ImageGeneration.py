import asyncio
from random import randint
from PIL import Image
import requests
from time import sleep
import os
from io import BytesIO

def open_images(prompt):
    folder_path = r"Data"
    prompt_safe = prompt.replace(" ", "_")
    Files = [f"{prompt_safe}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

async def query(url):
    return await asyncio.to_thread(requests.get, url, {"timeout": 15})

async def generate_images(prompt: str):
    prompt_safe = prompt.replace(" ", "_")
    os.makedirs("Data", exist_ok=True)

    for i in range(4):
        seed = randint(0, 1000000)
        print(f"Downloading image {i+1}...")
        url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&width=512&height=512"

        for attempt in range(3):  # Retry up to 3 times
            try:
                img_data = requests.get(url, timeout=15).content
                Image.open(BytesIO(img_data)).verify()  # Check if valid image
                with open(fr"Data\{prompt_safe}{i+1}.jpg", "wb") as f:
                    f.write(img_data)
                break
            except Exception as e:
                print(f"Retry {attempt+1} for image {i+1} failed: {e}")
                sleep(2)

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read().strip()

        Prompt, status = Data.split(",")
        Prompt = Prompt.strip()
        status = status.strip()

        if status.lower() == "true":
            print(f"Generating Images for: {Prompt} ...")
            GenerateImages(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")
            break
        else:
            sleep(1)
    except Exception as e:
        print(e)
        sleep(1)




