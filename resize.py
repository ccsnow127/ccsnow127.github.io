#write a python script to resize image in an folder to be of the same height
import os
from PIL import Image, ImageOps


#resize the image to be of the same size
def resize_image(image_path, save_folder, width, height):
    try:
        image = Image.open(image_path)
        # Correct the orientation based on EXIF data
        image = ImageOps.exif_transpose(image)
    except Exception as e:
        print(f"Failed to open {image_path}: {e}")
        return
    #for the vertical images
    #padding the image to be of the same size with white color
    if image.size[0] < image.size[1]:
        # Calculate the new height maintaining the aspect ratio
        height_percent = width / image.size[0]
        new_height = int(image.size[1] * height_percent)
        resized_image = image.resize((width, new_height), Image.ANTIALIAS)
        
        # Create a new image with the desired dimensions and paste the resized image
        new_image = Image.new("RGB", (width, height), "white")
        new_image.paste(resized_image, (0, (height - new_height) // 2))
        print(f"Resized vertical images: {image_path} to {new_image.size}")
    else:
        width_percent = height / image.size[1]
        new_width = int(image.size[0] * width_percent)
        new_image = image.resize((new_width, height))
        print(f"Resized horizontal images: {image_path} to {new_image.size}")
    image_name = os.path.basename(image_path)
    image_save_path = os.path.join(save_folder, image_name)
    new_image.save(image_save_path)



folder_path = "/Users/cc/Downloads/Utah-Museum/png"
save_folder = os.path.join(folder_path, "resized")
os.makedirs(save_folder, exist_ok=True)
for image_name in os.listdir(folder_path):
    image_path = os.path.join(folder_path, image_name)
    resize_image(image_path, save_folder, 4024, 3024)
