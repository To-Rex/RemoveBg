import os
import uuid
from flask import Flask, request, send_file, jsonify
from PIL import Image
from rembg import remove

app = Flask(__name__)

# Construct the absolute path to the 'images' directory
images_directory = os.path.join(os.path.dirname(__file__), 'images')


def crop_and_save_image(file, width, height, output_filename):
    try:
        image = Image.open(file)
        img_width, img_height = image.size

        # Calculate cropping coordinates for the center
        left = (img_width - width) // 2
        top = (img_height - height) // 2
        right = (img_width + width) // 2
        bottom = (img_height + height) // 2

        cropped_image = image.crop((left, top, right, bottom))

        # Generate a random filename
        filename = str(uuid.uuid4()) + '.jpg'
        save_path = os.path.join(images_directory, filename)
        cropped_image.save(save_path)

        return save_path
    except Exception as e:
        print(str(e))
        return None


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    file = request.files['file']
    remove_bg = request.form.get('remove')

    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith(('.jpg', '.png', '.jpeg')):
        return jsonify({'error': 'File type not allowed'}), 401

    cropped_file_path = crop_and_save_image(file, 600, 600, 'crop_img.jpg')

    if remove_bg == 'true':
        try:
            with open(cropped_file_path, 'rb') as img_file:
                output_file = remove(img_file.read())
                bg_removed_filename = str(uuid.uuid4()) + '.png'
                bg_removed_file_path = os.path.join(images_directory, bg_removed_filename)
                with open(bg_removed_file_path, 'wb') as f:
                    f.write(output_file)

            os.remove(cropped_file_path)
            return send_file(bg_removed_file_path, as_attachment=True)
        except Exception as e:
            print(str(e))
            return jsonify({'error': 'Error while removing background'}), 500

    if cropped_file_path:
        try:
            return send_file(cropped_file_path, as_attachment=True)
        finally:
            print("ssasaas")
            #os.remove(cropped_file_path)
            if os.path.exists(cropped_file_path):
                os.remove(cropped_file_path)
            else:
                print("The file does not exist")

    else:
        return jsonify({'error': 'Error while cropping the image'}), 500


@app.route('/')
def index():
    return "Hello World"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)