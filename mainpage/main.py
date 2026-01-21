
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import threading
import serial
import time

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)



class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yönetim Sistemi")
        self.root.geometry("1000x650")
        self.root.configure(bg="#1a1a2e")

        # Kameranın çalışıp çalışmadığını kontrol eden flag
        self.camera_running = True

        # ===================== BAŞLIK =====================
        header_frame = tk.Frame(root, bg="#16213e", height=80)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="🎥 Kişi Tanıma Yönetim Sistemi",
            font=("Arial", 24, "bold"),
            bg="#16213e",
            fg="#00d4ff"
        )
        title_label.pack(pady=20)

        # ===================== ANA ALAN =====================
        main_frame = tk.Frame(root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ===================== KAMERA =====================
        camera_container = tk.Frame(main_frame, bg="#1a1a2e")
        camera_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        camera_title = tk.Label(
            camera_container,
            text="📹 Canlı Görünüm",
            font=("Arial", 14, "bold"),
            bg="#1a1a2e",
            fg="#00d4ff"
        )
        camera_title.pack(pady=(0, 10))

        camera_frame = tk.Frame(
            camera_container,
            bg="#0f3460",
            highlightbackground="#00d4ff",
            highlightthickness=3,
            width=500,
            height=450
        )
        camera_frame.pack(fill=tk.BOTH, expand=True)
        camera_frame.pack_propagate(False)

        self.camera_label = tk.Label(camera_frame, bg="#000000")
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # ===================== BUTONLAR =====================
        buttons_container = tk.Frame(main_frame, bg="#1a1a2e")
        buttons_container.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)

        tk.Button(
            buttons_container,
            text="🔍 Kişiyi Bul",
            command=self.find_person,
            font=("Arial", 13, "bold"),
            bg="#00d4ff",
            fg="#1a1a2e",
            width=22,
            height=3
        ).pack(pady=10)

        tk.Button(
            buttons_container,
            text="👤 Yeni Üye Kaydı",
            command=self.new_member_registration,
            font=("Arial", 13, "bold"),
            bg="#e94560",
            fg="white",
            width=22,
            height=3
        ).pack(pady=10)

        tk.Button(
            buttons_container,
            text="❌ Çıkış",
            command=self.exit_app,
            font=("Arial", 12, "bold"),
            bg="#555555",
            fg="white",
            width=22,
            height=2
        ).pack(pady=20)

        # ===================== KAMERA BAŞLAT =====================
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.update_camera()
        

    # Kameradan sürekli görüntü alma döngüsü
    def update_camera(self):
        if not self.camera_running:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (500, 450))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face_img = frame[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (32, 32))
                face_img = face_img.astype("float") / 255.0
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    "Insan",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(img)

            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        self.root.after(30, self.update_camera)

    # Kişi bul butonu (şimdilik boş)
    def find_person(self):
        messagebox.showinfo("Bilgi", "Kişi tanıma sistemi çalışıyor.")

        # Kamerayı güvenli şekilde durdur
        self.camera_running = False
        self.cap.release()

        thread = threading.Thread(target=self.run_sub_app2)
        thread.start()
    # Yeni üye kaydı butonu
    def new_member_registration(self):
        messagebox.showinfo("Bilgi", "Yeni üye kaydı başlatılıyor...")

        # Kamera güvenli şekilde durduruluyor
        self.camera_running = False
        self.cap.release()

        # arduino = serial.Serial(
        #     port="COM9",
        #     baudrate=9600,
        #     timeout=1
        # )

        # arduino.write(b"P8_ON\n")
        # arduino.close()

        # Alt uygulamayı ayrı thread içinde çalıştır
        thread = threading.Thread(target=self.run_sub_app)
        thread.start()


    # Alt uygulamayı çalıştıran fonksiyon
    def run_sub_app(self):
        subprocess.run([
            "python",
            "C:\\Users\\qroce\\OneDrive\\Masaüstü\\Gömülü Sistemler Ödev\\thebest\\yeniuyekaydi\\main.py"
        ])

        # Alt uygulama kapandıktan sonra ana thread'e geri dön
        self.root.after(0, self.restart_camera)
    def run_sub_app2(self):
        subprocess.run([
            "python",
            "C:\\Users\\qroce\\OneDrive\\Masaüstü\\Gömülü Sistemler Ödev\\thebest\\kisibulma\\main.py"
        ])

        # Alt uygulama kapandıktan sonra ana thread'e geri dön
        self.root.after(0, self.restart_camera)

    # Kamerayı tekrar başlatan fonksiyon
    def restart_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.camera_running = True
        self.update_camera()

    # Programdan çıkış
    def exit_app(self):
        self.camera_running = False
        self.cap.release()
        self.root.destroy()


# Program başlangıç noktası
if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
