import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'landslide_project.settings')
django.setup()

from predictions.fetch_satellite import fetch_satellite_image

img_path, scene_name = fetch_satellite_image(13.222834, 76.277590)
print("Image saved to:", img_path)
print("Scene:", scene_name)