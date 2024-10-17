#write script to transform heic to png
import os
import subprocess
from PIL import Image

def heic2png(heic_path):
    png_folder = os.path.join(os.path.dirname(heic_path), "png")
    os.makedirs(png_folder, exist_ok=True)
    png_name = os.path.splitext(os.path.basename(heic_path))[0] + ".png"
    png_path = os.path.join(png_folder, png_name)
    subprocess.run(["sips", "-s", "format", "png", heic_path, "--out", png_path])


folder_path = "/Users/cc/Downloads/Utah-Museum"
for heic_name in os.listdir(folder_path):
    heic_path = os.path.join(folder_path, heic_name)
    heic2png(heic_path)

