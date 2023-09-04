import uuid
import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
from rembg import remove
from waitress import serve

app = Flask(__name__)


def crop_image(file, width, height, output_filename):
    try:
        image = Image.open(file)
        # Get the dimensions of the image
        img_width, img_height = image.size

        # Calculate the coordinates for cropping the center
        left = (img_width - width) // 2
        top = (img_height - height) // 2
        right = (img_width + width) // 2
        bottom = (img_height + height) // 2
        cropped_image = image.crop((left, top, right, bottom))

        # Generate a random filename
        filename = str(uuid.uuid4()) + '.jpg'
        save_path = os.path.join('./images/', filename)
        cropped_image.save(save_path)

        return save_path
    except Exception as e:
        print(str(e))
        return None


@app.route('/upload', methods=['POST'])
def upload():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    file = request.files['file']
    remove_bg = request.form.get('remove')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check if the file extension is allowed
    if not file.filename.endswith(('.jpg', '.png', '.jpeg')):
        return jsonify({'error': 'File type not allowed'}), 401

    #if image height or width is less than 600px zoom it to 600px

    cropped_file_path = crop_image(file, 600, 600, 'crop_img.jpg')

    if remove_bg == 'true':
        # Remove background using rembg library
        try:
            bg_removed_filename = str(uuid.uuid4()) + '.png'
            with open(cropped_file_path, 'rb') as img_file:
                output_file = remove(img_file.read())
                bg_removed_file_path = os.path.join('./images/', bg_removed_filename)
                with open(bg_removed_file_path, 'wb') as f:
                    f.write(output_file)
            os.remove(cropped_file_path)
            rem = send_file(bg_removed_file_path, as_attachment=True)
            os.remove(bg_removed_file_path)
            return rem
        except Exception as e:
            print(str(e))
            return jsonify({'error': 'Error while removing background'}), 500

    if cropped_file_path:
        send_files = send_file(cropped_file_path, as_attachment=True)
        os.remove(cropped_file_path)
        return send_files
    else:
        return jsonify({'error': 'Error while cropping the image'}), 500

@app.route('/')
def index():
    return "Hello World"

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8081)

