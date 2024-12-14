from flask import Flask, request, send_file, jsonify
from PIL import Image
import io, base64, requests

app = Flask(__name__)

API_KEY = "SG_cbd43a561a52d737"
SEGMIND_ENDPOINT = "https://api.segmind.com/v1/sdxl-img2img"

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.get_json()
    if not data or 'image' not in data or 'prompt' not in data:
        return "Missing data", 400

    image_b64 = data['image']
    prompt = data['prompt']
    negative_prompt = data.get('negative_prompt', 'low-quality, unrealistic')

    # Декодируем входящее изображение
    try:
        image_data = base64.b64decode(image_b64)
        init_image = Image.open(io.BytesIO(image_data))
    except Exception as e:
        return f"Invalid image: {e}", 400

    # Кодируем изображение в base64 для Segmind
    buf = io.BytesIO()
    init_image.save(buf, format="PNG")
    buf.seek(0)
    init_img_b64 = base64.b64encode(buf.read()).decode('utf-8')

    payload = {
        "image": init_img_b64,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "samples": 1,
        "scheduler": "UniPC",
        "base_model": "juggernaut",
        "num_inference_steps": 30,
        "guidance_scale": 6.5,
        "strength": 0.65,
        "seed": 98877465625,
        "base64": False
    }

    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        seg_response = requests.post(SEGMIND_ENDPOINT, json=payload, headers=headers, timeout=120)
        seg_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error contacting Segmind: {e}", 500

    # Segmind возвращает бинарные данные изображения
    result_img_data = seg_response.content
    # Проверим валидность
    try:
        Image.open(io.BytesIO(result_img_data))
    except Exception as e:
        return f"Segmind returned invalid image: {e}", 500

    return send_file(io.BytesIO(result_img_data), mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
