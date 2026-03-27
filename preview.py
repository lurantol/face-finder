from PIL import Image

def save_preview(img_path, box, out):
    img = Image.open(img_path)
    crop = img.crop(box)
    crop.save(out)
