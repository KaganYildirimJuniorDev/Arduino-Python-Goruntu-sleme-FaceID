from deepface import DeepFace
import cv2
import os
import tensorflow as tf
import numpy as np
import datetime
import xlwings as xw
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import serial
import time as t

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yüz Tanıma ve Canlılık Tespit Sistemi")
        self.root.geometry("1200x750")
        self.root.configure(bg='#2c3e50')

        try:
            self.arduino = serial.Serial("COM9", 9600, timeout=1)
            t.sleep(2) 
            print("Arduino Bağlantısı Başarılı")
        except Exception as e:
            print(f"Arduino Bağlantı Hatası: {e}")
            self.arduino = None           
        
        # Ana frame
        main_frame = tk.Frame(root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RIDGE, bd=2)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="YÜZ TANIMA VE CANLILIK TESPİT SİSTEMİ", 
                               font=('Arial', 20, 'bold'), bg='#34495e', fg='#ecf0f1', pady=15)
        title_label.pack()
        
        # İçerik frame'i
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel - Kamera görüntüsü
        left_frame = tk.Frame(content_frame, bg='#34495e', relief=tk.RIDGE, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        camera_title = tk.Label(left_frame, text="KAMERA GÖRÜNTÜSÜ", 
                               font=('Arial', 14, 'bold'), bg='#34495e', fg='#ecf0f1', pady=10)
        camera_title.pack()
        
        self.camera_label = tk.Label(left_frame, bg='#000000')
        self.camera_label.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        
        # Sağ panel - Bilgiler ve kontroller
        right_frame = tk.Frame(content_frame, bg='#34495e', relief=tk.RIDGE, bd=2, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Tarih ve Saat bilgisi
        info_frame = tk.LabelFrame(right_frame, text="Sistem Bilgileri", 
                                   font=('Arial', 12, 'bold'), bg='#34495e', 
                                   fg='#ecf0f1', relief=tk.GROOVE, bd=2)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.date_label = tk.Label(info_frame, text="Tarih: --/--/----", 
                                   font=('Arial', 11), bg='#34495e', fg='#ecf0f1', anchor='w')
        self.date_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.time_label = tk.Label(info_frame, text="Saat: --:--", 
                                   font=('Arial', 11), bg='#34495e', fg='#ecf0f1', anchor='w')
        self.time_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Durum bilgisi
        status_frame = tk.LabelFrame(right_frame, text="Durum", 
                                     font=('Arial', 12, 'bold'), bg='#34495e', 
                                     fg='#ecf0f1', relief=tk.GROOVE, bd=2)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(status_frame, text="● Sistem Hazır", 
                                     font=('Arial', 11), bg='#34495e', 
                                     fg='#2ecc71', anchor='w')
        self.status_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Kayıt edilen kişi bilgisi
        person_frame = tk.LabelFrame(right_frame, text="Son Tanınan Kişi", 
                                     font=('Arial', 12, 'bold'), bg='#34495e', 
                                     fg='#ecf0f1', relief=tk.GROOVE, bd=2)
        person_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.person_label = tk.Label(person_frame, text="Henüz kimse tanınmadı", 
                                     font=('Arial', 11), bg='#34495e', 
                                     fg='#ecf0f1', wraplength=300)
        self.person_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Kontrol butonları
        button_frame = tk.Frame(right_frame, bg='#34495e')
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        self.save_button = tk.Button(button_frame, text="KAYDET (S)", 
                                     font=('Arial', 11, 'bold'), bg='#27ae60', 
                                     fg='white', relief=tk.RAISED, bd=3,
                                     cursor='hand2', padx=20, pady=10,
                                     command=self.manual_save)
        self.save_button.pack(fill=tk.X, pady=5)
        
        self.reset_button = tk.Button(button_frame, text="SIFIRLA (R)", 
                                      font=('Arial', 11, 'bold'), bg='#3498db', 
                                      fg='white', relief=tk.RAISED, bd=3,
                                      cursor='hand2', padx=20, pady=10,
                                      command=self.reset_data)
        self.reset_button.pack(fill=tk.X, pady=5)
        
        quit_button = tk.Button(button_frame, text="ÇIKIŞ (Q)", 
                               font=('Arial', 11, 'bold'), bg='#c0392b', 
                               fg='white', relief=tk.RAISED, bd=3,
                               cursor='hand2', padx=20, pady=10,
                               command=self.quit_app)
        quit_button.pack(fill=tk.X, pady=5)
        
        # Değişkenler
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.model = tf.keras.models.load_model("liveness.model")
        
        try:
            self.workbook = xw.Book('loglar.xlsx')
        except:
            self.workbook = xw.Book()
            self.workbook.save('loglar.xlsx')
            
        self.sheet_name = datetime.datetime.now().strftime("%d_%m_%Y")
        
        try:
            self.worksheet = self.workbook.sheets(self.sheet_name)
        except:
            self.worksheet = self.workbook.sheets.add(self.sheet_name)
        
        self.worksheet.range('A1').value = 'NAME'
        self.worksheet.range('B1').value = 'DATE'
        self.worksheet.range('C1').value = 'TIME'
        
        self.employee_names = []
        self.s = 2
        self.t0 = datetime.datetime.now().day
        self.current_name = None
        self.current_liveness = 0
        
        self.update_frame()
        self.root.bind('<s>', lambda e: self.manual_save())
        self.root.bind('<r>', lambda e: self.reset_data())
        self.root.bind('<q>', lambda e: self.quit_app())
        
    def manual_save(self):
        if self.current_name and self.current_liveness == 1:
            moment = datetime.datetime.now()
            date = f"{moment.day:02d}/{moment.month:02d}/{moment.year}"
            time = f"{moment.hour:02d}:{moment.minute:02d}"
            
            if self.current_name not in self.employee_names:
                # Excel Kayıt
                self.worksheet.range(f'A{self.s}').value = self.current_name
                self.worksheet.range(f'B{self.s}').value = date
                self.worksheet.range(f'C{self.s}').value = time
                self.employee_names.append(self.current_name)
                self.s += 1
                
                # Arayüz Güncelleme
                self.status_label.config(text=f"● {self.current_name} kaydedildi!", fg='#2ecc71')
                self.person_label.config(text=f"{self.current_name}\n{date} - {time}")

                # Arduino İşlemleri
                if self.arduino:
                    # Pin 8 Aktif
                    self.arduino.write(b"P9:1\n") # Yeşil Led
                    self.arduino.write(b"P10:1\n") # Buzzer
                    t.sleep(0.2)
                    self.arduino.write(b"P9:0\n") # Yeşil Led
                    self.arduino.write(b"P10:0\n") # Buzzer
                    t.sleep(0.2)
                    self.arduino.write(b"P9:1\n") # Yeşil Led
                    self.arduino.write(b"P10:1\n") # Buzzer
                    t.sleep(0.2)
                    self.arduino.write(b"P9:0\n") # Yeşil Led
                    self.arduino.write(b"P10:0\n") # Buzzer
                    t.sleep(0.2)
                    self.arduino.write(b"P9:1\n") # Yeşil Led
                    self.arduino.write(b"P10:1\n") # Buzzer
                    t.sleep(0.2)
                    self.arduino.write(b"P9:0\n") # Yeşil Led
                    self.arduino.write(b"P10:0\n") # Buzzer
                    t.sleep(0.2)
                    self.arduino.write(b"P9:1\n") # Yeşil Led
                    self.arduino.write(b"P10:1\n") # Buzzer
                    t.sleep(0.2)
                    self.arduino.write(b"P9:0\n") # Yeşil Led
                    self.arduino.write(b"P10:0\n") # Buzzer
                    t.sleep(0.2)
                    # LCD Formatlama
                    ust = self.current_name[:16]
                    alt1 = date[:10]
                    alt2 = time[:5]
                    gonder = f"{ust}|{alt1}|{alt2}\n"
                    self.arduino.write(gonder.encode())
                    
                    # 2 saniye sonra pini kapat (Sistemi dondurmadan)
                    self.root.after(2000, lambda: self.arduino.write(b"P8:0\n") if self.arduino else None)
                    self.root.after(2000, lambda: self.arduino.write(b"P9:0\n") if self.arduino else None)
                    self.root.after(2000, lambda: self.arduino.write(b"P10:0\n") if self.arduino else None)
                    self.root.after(2000, lambda: self.arduino.write(b"P11:0\n") if self.arduino else None)
                    self.root.after(2000, lambda: self.arduino.write(b"P12:0\n") if self.arduino else None)


        elif self.current_name and self.current_liveness == 0:
                    # Geri sayım başladığı andaki ismi sabitleyelim
                    target_name = self.current_name 

                    def start_explosion_sequence(step):
                        if not self.arduino:
                            return

                        if step > 0:
                            display_name = "İzinsiz Giris"[:16]
                            
                            alt1 = "PATLAMAYA SON"
                            alt2 = f"{step} SANIYE"
                            gonder = f"{display_name}|{alt1}|{alt2}\n"
                            
                            try:
                                self.arduino.write(b"P8:1\n")
                                # 100ms sonra buzzerı kapat ve LCD bilgisini gönder
                                self.root.after(100, lambda: self.arduino.write(b"P8:0\n"))
                                self.root.after(100, lambda: self.arduino.write(b"P10:0\n"))
                                self.root.after(200, lambda: self.arduino.write(gonder.encode()))
                                
                                # Sonraki adıma geç
                                self.root.after(1000, lambda: start_explosion_sequence(step - 1))
                            except Exception as e:
                                print(f"Seri port hatası: {e}")
                        else:
                            # BOM Aşaması
                            try:
                                self.arduino.write(b"P8:1\n")
                                final_name = "      BOMBA ATILDI"[:16]
                                final_msg = f"{final_name}|     BOM!      |!!! PATLADI !!!\n"
                                self.arduino.write(final_msg.encode())
                                
                                self.root.after(1500, lambda: self.arduino.write(b"P8:0\n") if self.arduino else None)
                            except Exception as e:
                                print(f"Final mesaj hatası: {e}")

                    # Geri sayımı başlat
                    start_explosion_sequence(3)



                
    def reset_data(self):
        self.current_name = None
        self.current_liveness = 0
        self.employee_names = []
        self.s = 2
        
        # Excel dosyasındaki verileri temizle
        try:
            last_row = self.worksheet.used_range.last_cell.row
            if last_row > 1:
                self.worksheet.range(f'A2:C{last_row}').clear_contents()
            self.workbook.save()
        except Exception as e:
            print(f"Excel temizleme hatası: {e}")
        
        self.status_label.config(text="● Sistem Sıfırlandı", fg='#f39c12')
        self.person_label.config(text="Henüz kimse tanınmadı")
        

    def quit_app(self):
        if self.arduino:
            self.arduino.close()
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()
        
    def update_frame(self):
        moment = datetime.datetime.now()
        date = f"{moment.day:02d}/{moment.month:02d}/{moment.year}"
        time = f"{moment.hour:02d}:{moment.minute:02d}"
        
        self.date_label.config(text=f"Tarih: {date}")
        self.time_label.config(text=f"Saat: {time}")
        
        ret, frame = self.cap.read()
        if ret:
            try:
                res = DeepFace.find(frame, db_path=r"C:\\Users\\qroce\\OneDrive\\Belgeler\\gomulu_db", 
                                    enforce_detection=False, model_name="Facenet512", silent=True)
            except:
                res = []
            
            if isinstance(res, list) and len(res) > 0 and len(res[0]) > 0:
                identity_path = res[0].iloc[0]['identity']
                name = os.path.basename(identity_path).split(".")[0]
                
                xmin, ymin, w, h = int(res[0].iloc[0]['source_x']), int(res[0].iloc[0]['source_y']), \
                                   int(res[0].iloc[0]['source_w']), int(res[0].iloc[0]['source_h'])
                
                face_img = cv2.resize(frame[ymin:ymin+h, xmin:xmin+w], (32, 32)).astype("float") / 255.0
                face_img = np.expand_dims(tf.keras.preprocessing.image.img_to_array(face_img), axis=0)
                
                liveness = np.argmax(self.model.predict(face_img, verbose=0)[0])
                color = (0, 255, 0) if liveness == 1 else (0, 0, 255)
                
                cv2.rectangle(frame, (xmin, ymin), (xmin+w, ymin+h), color, 2)
                cv2.putText(frame, f"{name} - {'Canli' if liveness == 1 else 'Cansiz'}", 
                            (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                self.current_name = name
                self.current_liveness = liveness
                self.status_label.config(text=f"● {name} Tespit Edildi", fg='#2ecc71' if liveness == 1 else '#e74c3c')
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                self.current_name = None
                self.current_liveness = 0

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb).resize((640, 480)))
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        
        self.root.after(10, self.update_frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()