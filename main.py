import os
import sys
import argparse
import urllib.request
import tempfile
from PIL import Image, ImageOps, ImageEnhance


def apply_xray_effect(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')

    gray = ImageOps.grayscale(image)
    inverted = ImageOps.invert(gray)

    enhancer = ImageEnhance.Contrast(inverted)
    inverted = enhancer.enhance(2.0)

    enhancer = ImageEnhance.Brightness(inverted)
    inverted = enhancer.enhance(1.2)

    return inverted


def get_image_files(folder):
    extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')
    files = []
    for f in os.listdir(folder):
        if f.lower().endswith(extensions):
            files.append(os.path.join(folder, f))
    return sorted(files)


def download_image(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
            suffix = os.path.splitext(url)[1]
            if not suffix:
                suffix = '.png'
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(data)
                return tmp.name
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def is_url(path):
    return path.startswith('http://') or path.startswith('https://')


def convert_folder(input_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if is_url(input_path):
        print(f"Downloading image from: {input_path}")
        tmp_file = download_image(input_path)
        if not tmp_file:
            print("Failed to download image")
            return
        
        xray_image = apply_xray_effect(Image.open(tmp_file))
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        if not base_name:
            base_name = "image"
        output_path = os.path.join(output_folder, f"{base_name}_xray.png")
        xray_image.save(output_path, "PNG")
        os.unlink(tmp_file)
        print(f"Saved: {output_path}")
        return

    if not os.path.exists(input_path):
        print(f"Input folder does not exist: {input_path}")
        return

    image_files = get_image_files(input_path)
    if not image_files:
        print("No images found in input folder")
        return

    print(f"Found {len(image_files)} images")

    for i, image_path in enumerate(image_files, 1):
        xray_image = apply_xray_effect(Image.open(image_path))
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_folder, f"{base_name}_xray.png")
        xray_image.save(output_path, "PNG")
        print(f"Converted {i}/{len(image_files)}: {base_name}_xray.png")

    print(f"Done! Saved {len(image_files)} images to {output_folder}")


def main():
    parser = argparse.ArgumentParser(description='X-Ray Image Converter')
    parser.add_argument('input', help='Input folder or URL to image')
    parser.add_argument('output', help='Output folder for converted images')
    args = parser.parse_args()

    convert_folder(args.input, args.output)


if __name__ == "__main__":
    main()