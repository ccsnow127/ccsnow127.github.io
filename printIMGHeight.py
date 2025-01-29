#print image height
from PIL import Image
import os

folder_path = "/Users/cc/Downloads/Antelope-PNG"
for image_name in os.listdir(folder_path):
    if not image_name.endswith(".png"):
        continue
    image_path = os.path.join(folder_path, image_name)
    image = Image.open(image_path)
    # print(f"{image_name}: {image.size[1]}")
    print(image.size)

