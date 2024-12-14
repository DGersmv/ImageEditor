from flask import Flask, request, send_file
from PIL import Image
import io
import requests

app = Flask(__name__)

API_KEY = "SG_cbd43a561a52d737"
SEGMIND_ENDPOINT = "https://api.segmind.com/v1/flux-canny-pro"

@app.route('/process_image', methods=['POST'])
def process_image():
    # Проверяем наличие данных от клиента
    if 'image' not in request.files or 'control_image' not in request.files or 'prompt' not in request.form:
        return "Missing required data: 'image', 'control_image', or 'prompt'", 400

    try:
        # Получаем изображение и контрольное изображение (контур)
        image_file = request.files['image']
        control_image_file = request.files['control_image']
        prompt = request.form['prompt']

        # Читаем изображения из запроса
        init_image = Image.open(image_file)
        control_image = Image.open(control_image_file)

        # Сохраняем изображения во временные буферы
        buf_image = io.BytesIO()
        init_image.save(buf_image, format="PNG")
        buf_image.seek(0)

        buf_control_image = io.BytesIO()
        control_image.save(buf_control_image, format="PNG")
        buf_control_image.seek(0)
    except Exception as e:
        return f"Invalid image data: {e}", 400

    # Подготовка данных для отправки в flux-canny-pro
    data_form = {
        'seed': 965778,
        'steps': 50,
        'prompt': prompt,
        'guidance': 15,
        'output_format': 'jpg',
        'safety_tolerance': 2,
        'prompt_upsampling': 'true'
    }

    # Файлы для отправки
    files = {
        'image': ('image.png', buf_image, 'image/png'),
        'control_image': ('control_image.png', buf_control_image, 'image/png')
    }

    headers = {
        'x-api-key': API_KEY
    }

    # Отправляем запрос на Segmind API
    try:
        seg_response = requests.post(SEGMIND_ENDPOINT, data=data_form, files=files, headers=headers, timeout=120)
        seg_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error contacting Segmind: {e}", 500

    # Получаем результат обработки
    result_img_data = seg_response.content
    try:
        result_image = Image.open(io.BytesIO(result_img_data))
    except Exception as e:
        return f"Segmind returned invalid image: {e}", 500

    # Возвращаем результат обратно клиенту
    return send_file(io.BytesIO(result_img_data), mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
