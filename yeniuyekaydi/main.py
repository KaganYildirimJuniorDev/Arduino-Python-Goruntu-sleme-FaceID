import cv2
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Kamera başlat
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

save_folder = "C:\\Users\\qroce\\OneDrive\\Belgeler\\gomulu_db"
os.makedirs(save_folder, exist_ok=True)

# Tkinter GUI başlat
root = tk.Tk()
root.title("Resim Kaydetme Uygulaması")
root.geometry("400x350")
root.configure(bg="#f0f0f0")

# Program çalışıyor mu kontrol flag'i
running = True

# Ana panel
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

# Başlık
title_label = tk.Label(
    main_frame,
    text="Resim Kaydetme Uygulaması",
    font=("Helvetica", 16, "bold"),
    bg="#f0f0f0"
)
title_label.pack(pady=10)

# İsim girişi
name_label = tk.Label(main_frame, text="İsim girin:", font=("Helvetica", 12), bg="#f0f0f0")
name_label.pack(pady=5)

name_entry = ttk.Entry(main_frame, font=("Helvetica", 12))
name_entry.pack(pady=5)

# Video etiketi
video_label = tk.Label(main_frame)
video_label.pack(pady=10)

# Durum mesajı
status_label = tk.Label(main_frame, text="", font=("Helvetica", 10), bg="#f0f0f0")
status_label.pack(pady=5)

# Resmi kaydet
def save_image():
    user_name = name_entry.get()
    if not user_name:
        status_label.config(text="Hata: İsim boş bırakılamaz.", fg="red")
        return

    file_path = os.path.join(save_folder, f"{user_name}.jpg")
    success = cv2.imwrite(file_path, roi)

    if success:
        status_label.config(text=f"✓ Kaydedildi: {file_path}", fg="green")
    else:
        status_label.config(text="✗ Kaydetme başarısız", fg="red")

save_button = ttk.Button(main_frame, text="Resmi Kaydet", command=save_image)
save_button.pack(pady=10)

# Kamera + GUI döngüsü
def update_frame():
    global roi

    if not running:
        return

    ret, frame = cap.read()
    if ret:
        h, w = frame.shape[:2]

        roi_w, roi_h = 150, 200
        cx, cy = w // 2, h // 2
        x1, x2 = cx - roi_w // 2, cx + roi_w // 2
        y1, y2 = cy - roi_h // 2, cy + roi_h // 2

        roi = frame[y1:y2, x1:x2]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(img)

        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    root.after(30, update_frame)

# Pencere kapatılırken
def on_close():
    global running
    running = False
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Döngüyü başlat
update_frame()
root.mainloop()
