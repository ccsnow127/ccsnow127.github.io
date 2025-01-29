#generate statement to import all the images in the folder
import os

folder_path = "assets/img/Antelope-Island"
print("""<swiper-container keyboard="true" navigation="true" pagination="true" pagination-clickable="true" pagination-dynamic-bullets="true" rewind="true">""")
for image_name in os.listdir(folder_path):
    if not image_name.endswith(".png"):
        continue
    image_path = os.path.join(folder_path, image_name)
    print("""<swiper-slide>{{% include figure.liquid loading="eager" path="{}" class="img-fluid rounded z-depth-1"  %}}</swiper-slide>""".format(image_path))

print("""</swiper-container>""")