import os
from PIL import Image

def scan_images(path):
    files = []
    for root, _, f in os.walk(path):
        for file in f:
            files.append(os.path.join(root, file))
    return files

def detect_format(path):
    try:
        with Image.open(path) as img:
            return img.format
    except:
        return "UNKNOWN"
