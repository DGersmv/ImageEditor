from flask import Flask, request, send_file
from PIL import Image
import io
import requests
import random

app = Flask(__name__)

API_KEY = "SG_cbd43a561a52d737"
SEGMIND_ENDPOINT = "https://api.segmind.com/v1/flux-canny-pro"

@app.route('/process_image', methods=['POST'])
def process_image():
    # Проверяем наличие данных от клиента
    if 'control_image' not in request.files or 'prompt' not in request.form:
        return "Missing required data: 'control_image' or 'prompt'", 400

    try:
        # Получаем контрольное изображение (контур) и prompt
        control_image_file = request.files['control_image']
        prompt = request.form['prompt']

        # Читаем изображение из запроса
        control_image = Image.open(control_image_file)

        # Сохраняем изображение во временный буфер
        buf_control_image = io.BytesIO()
        control_image.save(buf_control_image, format="PNG")
        buf_control_image.seek(0)
    except Exception as e:
        return f"Invalid image data: {e}", 400

    # Генерируем случайный seed для каждой обработки
    seed = random.randint(0, 1000000)

    # Подготовка данных для отправки в flux-canny-pro
    data_form = {
        'seed': seed,
        'steps': 50,  # Увеличенные шаги для более качественного результата
        'prompt': prompt,
        'guidance': 20,  # Оптимальное значение для строгого следования prompt
        'output_format': 'jpg',
        'safety_tolerance': 2,
        'prompt_upsampling': True  # Используем логическое значение, а не строку
    }

    # Файлы для отправки
    files = {
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
