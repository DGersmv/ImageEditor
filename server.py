from flask import Flask, request, send_file, jsonify
from PIL import Image
import io, base64, requests

app = Flask(__name__)

API_KEY = "SG_cbd43a561a52d737"
SEGMIND_ENDPOINT = "https://api.segmind.com/v1/flux-canny-pro"

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.get_json()
    if not data or 'image' not in data or 'prompt' not in data:
        return "Missing data", 400

    image_b64 = data['image']
    prompt = data['prompt']
    # Для flux-canny-pro пример не использует negative_prompt или сложные параметры
    # Можно их убрать или оставить по вашему усмотрению, но лучше убрать для начала.
    
    try:
        image_data = base64.b64decode(image_b64)
        init_image = Image.open(io.BytesIO(image_data))
    except Exception as e:
        return f"Invalid image: {e}", 400

    # Сохраняем изображение во временный буфер для передачи как файл:
    buf = io.BytesIO()
    init_image.save(buf, format="PNG")
    buf.seek(0)

    # Параметры согласно примеру с 'flux-canny-pro':
    # В примере нет упоминания image как base64, а используется либо file, либо URI для control_image.
    # Мы отправим наше изображение как control_image (файл).
    
    data_form = {
        'seed': 965778,
        'steps': 40,
        'prompt': prompt,
        'guidance': 30,
        'output_format': 'jpg',
        'safety_tolerance': 2,
        'prompt_upsampling': 'false'
    }

    # Передаём наше изображение как файл 'control_image'
    files = {
        'control_image': ('control_image.png', buf, 'image/png')
    }

    headers = {
        'x-api-key': API_KEY
    }

    try:
        seg_response = requests.post(SEGMIND_ENDPOINT, data=data_form, files=files, headers=headers, timeout=120)
        seg_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error contacting Segmind: {e}", 500

    result_img_data = seg_response.content
    # Проверяем, можем ли открыть изображение:
    try:
        Image.open(io.BytesIO(result_img_data))
    except Exception as e:
        return f"Segmind returned invalid image: {e}", 500

    return send_file(io.BytesIO(result_img_data), mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
