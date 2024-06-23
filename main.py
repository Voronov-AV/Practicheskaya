import cv2
from tkinter import Tk, Label, Button, filedialog, Entry, Toplevel, messagebox
from PIL import Image, ImageTk
import numpy as np
from pathlib import Path
import os


def load_image():
    global img, original_img
    file_path = filedialog.askopenfilename(
        filetypes=[("Файл изображения", "*.jpg;*.jpeg;*.png")])
    if file_path:
        file_path = Path(file_path).resolve()
        if not os.path.isfile(file_path):
            show_error_message("Ошибка", f"Файл не существует в {file_path}")
            return

        # Загрузить изображение, используя PIL и конвертировать в формат OpenCV
        try:
            pil_image = Image.open(file_path)
            img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            show_error_message("Ошибка", f"Невозможно загрузить изображение из {file_path}: {e}")
            return

        original_img = img.copy()
        show_image(img)
    else:
        print("Файл не выбран")


def capture_image():
    global img, original_img
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        show_error_message("Ошибка", "Невозможно открыть камеру.")
        return
    ret, frame = cap.read()
    cap.release()
    if ret:
        img = frame
        original_img = img.copy()
        show_image(img)
    else:
        show_error_message("Ошибка", "Не получилось сделать снимок.")


def show_image(img):
    global label
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    label.config(image=img_tk)
    label.image = img_tk
    label.pack()


def show_channel(channel):
    global img
    if img is None:
        show_error_message("Ошибка", "Нет изображения")
        return
    if len(img.shape) == 3 and img.shape[2] == 3:
        channel_img = img[:, :, channel]
        show_image(channel_img)
    else:
        show_error_message("Ошибка", "Выбранное изображение не цветное.")


def resize_image():
    global img
    if img is None:
        show_error_message("Ошибка", "Нет изображения")
        return

    def apply_resize():
        global img
        try:
            new_width = int(entry_width.get())
            new_height = int(entry_height.get())
        except ValueError:
            show_error_message("Ошибка", "Неправильный ввод.")
            return

        if new_width <= 0 or new_height <= 0:
            show_error_message("Ошибка", "Числа должны быть целые положительные")
            return

        img = cv2.resize(img, (new_width, new_height))
        show_image(img)
        resize_window.destroy()

    resize_window = Toplevel(root)
    resize_window.title("Изменить размер изображения")

    label_width = Label(resize_window, text="Ширина:")
    label_width.pack()

    entry_width = Entry(resize_window)
    entry_width.pack()

    label_height = Label(resize_window, text="Высота:")
    label_height.pack()

    entry_height = Entry(resize_window)
    entry_height.pack()

    apply_button = Button(resize_window, text="Применить", command=apply_resize)
    apply_button.pack()


def show_original_image():
    global original_img
    if original_img is None:
        show_error_message("Ошибка", "Оригинальное изображение отсутствует")
        return

    show_image(original_img)


def decrease_brightness():
    global img
    if img is None:
        show_error_message("Ошибка", "Нет изображения")
        return

    def apply_brightness_decrease():
        global img
        try:
            decrease_value = int(entry_decrease_value.get())
        except ValueError:
            show_error_message("Ошибка", "Неправильный ввод")
            return

        if decrease_value <= 0:
            show_error_message("Ошибка", "Число должно быть целое и положительное")
            return

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_hsv[..., 2] = np.clip(img_hsv[..., 2] - decrease_value, 0, 255)
        img = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
        show_image(img)
        decrease_window.destroy()

    decrease_window = Toplevel(root)
    decrease_window.title("Уменьшить яркость")

    label_decrease = Label(decrease_window, text="Уменьшить яркость:")
    label_decrease.pack()

    entry_decrease_value = Entry(decrease_window)
    entry_decrease_value.pack()

    apply_button = Button(decrease_window, text="Применить", command=apply_brightness_decrease)
    apply_button.pack()


def draw_rectangle():
    global img
    if img is None:
        show_error_message("Ошибка", "Нет изображения")
        return

    def apply_draw_rectangle():
        try:
            x1 = int(entry_x1.get())
            y1 = int(entry_y1.get())
            x2 = int(entry_x2.get())
            y2 = int(entry_y2.get())
        except ValueError:
            show_error_message("Ошибка", "Неправильный ввод")
            return

        if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0 or x2 > img.shape[1] or y2 > img.shape[0]:
            show_error_message("Ошибка", "Неправильный ввод")
            return

        img_rect = img.copy()
        cv2.rectangle(img_rect, (x1, y1), (x2, y2), (255, 0, 0), 2)
        show_image(img_rect)
        draw_rect_window.destroy()

    draw_rect_window = Toplevel(root)
    draw_rect_window.title("Нарисовать прямоугольник")

    label_x1 = Label(draw_rect_window, text="X1 (мин: 0, макс: {})".format(img.shape[1]))
    label_x1.pack()

    entry_x1 = Entry(draw_rect_window)
    entry_x1.pack()

    label_y1 = Label(draw_rect_window, text="Y1 (мин: 0, макс: {})".format(img.shape[0]))
    label_y1.pack()

    entry_y1 = Entry(draw_rect_window)
    entry_y1.pack()

    label_x2 = Label(draw_rect_window, text="X2 (мин: 0, макс: {})".format(img.shape[1]))
    label_x2.pack()

    entry_x2 = Entry(draw_rect_window)
    entry_x2.pack()

    label_y2 = Label(draw_rect_window, text="Y2 (мин: 0, макс: {})".format(img.shape[0]))
    label_y2.pack()

    entry_y2 = Entry(draw_rect_window)
    entry_y2.pack()

    apply_button = Button(draw_rect_window, text="Применить", command=apply_draw_rectangle)
    apply_button.pack()


def show_error_message(title, message):
    messagebox.showerror(title, message)


root = Tk()
root.title("Практическая")
img = None
original_img = None

load_button = Button(root, text="Загрузить изображжение", command=load_image)
load_button.pack()

capture_btn = Button(root, text="Сделать снимок", command=capture_image)
capture_btn.pack()

resize_button = Button(root, text="Изменить размер изображения", command=resize_image)
resize_button.pack()

show_original_button = Button(root, text="Показать оригинальное изображение", command=show_original_image)
show_original_button.pack()

decrease_brightness_button = Button(root, text="Уменьшить яркость", command=decrease_brightness)
decrease_brightness_button.pack()

red_button = Button(root, text="Показать красный канал", command=lambda: show_channel(2))
red_button.pack()

green_button = Button(root, text="Показать зеленый канал", command=lambda: show_channel(1))
green_button.pack()

blue_button = Button(root, text="Показать голубой канал", command=lambda: show_channel(0))
blue_button.pack()

rectangle_button = Button(root, text="Нарисовать прямоугольник", command=draw_rectangle)
rectangle_button.pack()

label = Label(root)
label.pack()

root.mainloop()
