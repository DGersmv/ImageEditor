import requests
from tkinter import Tk, Label, Button, Canvas, filedialog, Entry, StringVar
from PIL import Image, ImageTk
import io

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloud Image Editor")
        self.root.geometry("800x600")

        # Переменные
        self.image = None  # Исходное изображение
        self.processed_image = None  # Обработанное изображение
        self.server_url = "http://127.0.0.1:5000/process_image"  # URL сервера

        # Интерфейс
        Label(root, text="Cloud Image Editor", font=("Arial", 20)).pack(pady=10)

        self.canvas = Canvas(root, width=600, height=400, bg="gray")
        self.canvas.pack(pady=10)

        Button(root, text="Загрузить изображение", command=self.load_image, font=("Arial", 12)).pack(pady=5)

        Button(root, text="Отправить на обработку", command=self.send_to_server, font=("Arial", 12)).pack(pady=10)

    def load_image(self):
        """Загрузить изображение"""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return

        # Загрузка изображения
        self.image = Image.open(file_path)
        self.display_image(self.image)

    def display_image(self, image):
        """Отобразить изображение на Canvas"""
        image.thumbnail((600, 400))
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(300, 200, image=self.tk_image)

    def send_to_server(self):
        """Отправить изображение на сервер"""
        if self.image is None:
            print("Сначала загрузите изображение!")
            return

        # Сохраняем изображение во временный буфер
        buf = io.BytesIO()
        self.image.save(buf, format="JPEG")
        buf.seek(0)

        # Отправляем изображение на сервер
        response = requests.post(self.server_url, files={"image": buf})
        if response.status_code == 200:
            # Получаем обработанное изображение
            processed_image = Image.open(io.BytesIO(response.content))
            self.processed_image = processed_image
            self.display_image(self.processed_image)
        else:
            print(f"Ошибка сервера: {response.status_code}")

if __name__ == "__main__":
    root = Tk()
    app = ImageEditorApp(root)
    root.mainloop()
