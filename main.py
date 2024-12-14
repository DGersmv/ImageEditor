import requests
from tkinter import Tk, Label, Button, Canvas, filedialog, Entry, StringVar, messagebox, Frame
from PIL import Image, ImageTk, ImageOps
import io
import base64
import cv2
import numpy as np

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Architecture Image Enhancer")
        self.root.geometry("1300x800")  # Увеличим размер окна

        self.image = None
        self.canny_image = None  # Для хранения контурного изображения
        self.server_url = "https://imageeditor-zfwd.onrender.com/process_image"  # URL вашего сервера

        Label(root, text="Architecture Image Enhancer", font=("Arial", 20)).pack(pady=10)

        # Фрейм для холстов
        canvas_frame = Frame(root)
        canvas_frame.pack(pady=10)

        # Canvas для исходного изображения
        self.canvas = Canvas(canvas_frame, width=600, height=400, bg="gray")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Canvas для контурного изображения
        self.canny_canvas = Canvas(canvas_frame, width=600, height=400, bg="gray")
        self.canny_canvas.grid(row=0, column=1, padx=10, pady=10)

        self.load_button = Button(root, text="Загрузить изображение", command=self.load_image, font=("Arial", 12))
        self.load_button.pack(pady=5)

        Label(root, text="Prompt:", font=("Arial", 12)).pack()
        self.prompt_var = StringVar()
        self.prompt_var.set("A photorealistic, ultra-detailed, high-resolution image house surrounded by trees and a rocky lakeshore, warm natural lighting, cinematic atmosphere, ultra-sharp focus, studio-quality rendering.")
        Entry(root, textvariable=self.prompt_var, width=50).pack(pady=5)

        Label(root, text="Negative Prompt:", font=("Arial", 12)).pack()
        self.negative_prompt_var = StringVar()
        self.negative_prompt_var.set("cartoon, low-quality, unrealistic")
        Entry(root, textvariable=self.negative_prompt_var, width=50).pack(pady=5)

        self.process_button = Button(root, text="Отправить на обработку", command=self.send_to_server, font=("Arial", 12))
        self.process_button.pack(pady=10)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return
        self.image = Image.open(file_path)
        self.display_image(self.image, self.canvas)

        # Добавляем кнопку для генерации контуров
        if not hasattr(self, 'canny_button'):
            self.canny_button = Button(self.root, text="Сгенерировать контур (Canny)", command=self.generate_canny, font=("Arial", 12))
            self.canny_button.pack(pady=5)

        # Добавляем кнопку для инверсии маски
        if not hasattr(self, 'invert_button'):
            self.invert_button = Button(self.root, text="Инвертировать контур", command=self.invert_canny, font=("Arial", 12))
            self.invert_button.pack(pady=5)

    def display_image(self, image, canvas_widget):
        # Отображение изображения в заданном Canvas
        img_copy = image.copy()
        img_copy.thumbnail((600, 400))
        tk_image = ImageTk.PhotoImage(img_copy)
        canvas_widget.delete("all")
        canvas_widget.create_image(300, 200, image=tk_image)
        # Сохраняем ссылку на изображение
        if canvas_widget == self.canvas:
            self.tk_image = tk_image
        else:
            self.canny_tk_image = tk_image

    def generate_canny(self):
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение!")
            return

        # Конвертируем PIL Image в OpenCV формат
        img_cv = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # Применим Canny
        edges = cv2.Canny(gray, 100, 200)

        # Конвертируем обратно в PIL Image для отображения
        canny_pil = Image.fromarray(edges)
        self.canny_image = canny_pil
        self.display_image(self.canny_image, self.canny_canvas)

    def invert_canny(self):
        if self.canny_image is None:
            messagebox.showwarning("Предупреждение", "Сначала создайте контур (Canny)!")
            return

        # Инвертируем цвета контурного изображения
        inverted_canny = ImageOps.invert(self.canny_image.convert("L"))
        self.canny_image = inverted_canny  # Обновляем изображение
        self.display_image(self.canny_image, self.canny_canvas)

    def send_to_server(self):
        if self.image is None or self.canny_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение и создайте контур!")
            return

        prompt = self.prompt_var.get().strip()
        negative_prompt = self.negative_prompt_var.get().strip()

        if not prompt:
            messagebox.showwarning("Предупреждение", "Введите промпт для обработки!")
            return

        # Сохраняем исходное изображение в буфер
        buf_image = io.BytesIO()
        self.image.save(buf_image, format="PNG")
        buf_image.seek(0)

        # Сохраняем контурное изображение в буфер
        buf_canny = io.BytesIO()
        self.canny_image.save(buf_canny, format="PNG")
        buf_canny.seek(0)

        # Отправляем оба изображения на сервер
        files = {
            'image': ('image.png', buf_image, 'image/png'),
            'control_image': ('control_image.png', buf_canny, 'image/png')
        }

        data = {
            'prompt': prompt,
            'negative_prompt': negative_prompt
        }

        try:
            messagebox.showinfo("Обработка", "Изображение отправлено на сервер. Подождите...")
            response = requests.post(self.server_url, data=data, files=files, timeout=400)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить запрос: {e}")
            return

        # Получаем результат от сервера
        result_img_data = response.content
        try:
            result_image = Image.open(io.BytesIO(result_img_data))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Сервер вернул некорректное изображение: {e}")
            return

        self.image = result_image
        self.display_image(self.image, self.canvas)

if __name__ == "__main__":
    root = Tk()
    app = ImageEditorApp(root)
    root.mainloop()
