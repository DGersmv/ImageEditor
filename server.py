from flask import Flask, request, send_file
from PIL import Image, ImageEnhance
import io

app = Flask(__name__)

@app.route('/process_image', methods=['POST'])
def process_image():
    # Получаем изображение из запроса
    if 'image' not in request.files:
        return "No image uploaded", 400
    image_file = request.files['image']
    image = Image.open(image_file)

    # Улучшаем изображение (пример: увеличиваем яркость)
    enhancer = ImageEnhance.Brightness(image)
    enhanced_image = enhancer.enhance(1.5)

    # Сохраняем обработанное изображение в буфер
    buf = io.BytesIO()
    enhanced_image.save(buf, format="JPEG")
    buf.seek(0)

    # Отправляем обработанное изображение обратно клиенту
    return send_file(buf, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
