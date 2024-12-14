import requests
from tkinter import Tk, Label, Button, Canvas, filedialog, Entry, StringVar, messagebox
from PIL import Image, ImageTk
import io
import base64

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Architecture Image Enhancer")
        self.root.geometry("800x600")

        self.image = None
        # Локальный адрес сервера Flask (если вы работаете локально)
        self.server_url = "https://imageeditor-zfwd.onrender.com/process_image"

        Label(root, text="Architecture Image Enhancer", font=("Arial", 20)).pack(pady=10)

        self.canvas = Canvas(root, width=600, height=400, bg="gray")
        self.canvas.pack(pady=10)

        Button(root, text="Загрузить изображение", command=self.load_image, font=("Arial", 12)).pack(pady=5)

        Label(root, text="Prompt:", font=("Arial", 12)).pack()
        self.prompt_var = StringVar()
        self.prompt_var.set("A cozy wooden house on the shore of a rocky lake, surrounded by pine forest, photorealistic")
        Entry(root, textvariable=self.prompt_var, width=50).pack(pady=5)

        Label(root, text="Negative Prompt:", font=("Arial", 12)).pack()
        self.negative_prompt_var = StringVar()
        self.negative_prompt_var.set("cartoon, low-quality, unrealistic")
        Entry(root, textvariable=self.negative_prompt_var, width=50).pack(pady=5)

        Button(root, text="Отправить на обработку", command=self.send_to_server, font=("Arial", 12)).pack(pady=10)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return
        self.image = Image.open(file_path)
        self.display_image(self.image)

    def display_image(self, image):
        image.thumbnail((600, 400))
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(300, 200, image=self.tk_image)

    def send_to_server(self):
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение!")
            return

        prompt = self.prompt_var.get().strip()
        negative_prompt = self.negative_prompt_var.get().strip()

        if not prompt:
            messagebox.showwarning("Предупреждение", "Введите промпт для обработки!")
            return

        buf = io.BytesIO()
        self.image.save(buf, format="PNG")
        buf.seek(0)
        img_bytes = buf.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        payload = {
            "image": img_base64,
            "prompt": prompt,
            "negative_prompt": negative_prompt
        }

        try:
            messagebox.showinfo("Обработка", "Изображение отправлено на сервер. Подождите...")
            response = requests.post(self.server_url, json=payload, timeout=300)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить запрос: {e}")
            return

        result_img_data = response.content
        try:
            result_image = Image.open(io.BytesIO(result_img_data))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Сервер вернул некорректное изображение: {e}")
            return

        self.image = result_image
        self.display_image(self.image)

if __name__ == "__main__":
    root = Tk()
    app = ImageEditorApp(root)
    root.mainloop()
