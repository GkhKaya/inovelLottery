import sys
import os
import json
import random
import time
import logging
import pathlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QFrame, QLineEdit, QSpinBox, QMessageBox,
                            QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
                            QSizePolicy, QTabWidget, QToolButton, QStackedWidget, QTextEdit,
                            QCheckBox, QInputDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QImage, QIcon, QColor

# Log ayarları
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Kullanıcıya özgü veri dizini
def get_data_dir():
    if os.name == 'nt':  # Windows
        data_dir = pathlib.Path(os.getenv('APPDATA')) / "LotteryApp"
    else:  # macOS veya diğer
        data_dir = pathlib.Path.home() / "Library" / "Application Support" / "LotteryApp"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# Global JSON dosya yolu
DATA_DIR = get_data_dir()
JSON_FILE = DATA_DIR / "list.json"

class CountdownThread(QThread):
    signal = pyqtSignal(int)
    finished = pyqtSignal()
    
    def run(self):
        for i in range(3, 0, -1):
            self.signal.emit(i)
            time.sleep(1)
        self.finished.emit()

class LotteryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("INOVEL İSİM ÇEKİLİŞ UYGULAMASI")
        self.setGeometry(100, 100, 1920, 1080)
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Arkaplan ayarla
        self.setup_background("lotterybg.png", opacity=0.3)  # Opaklık %30'a düşürüldü
        
        # Modern stil ayarla
        self.setup_style()
        
        # Başlık bölümü (her ekranda gösterilecek)
        self.create_header()
        
        # Ana içerik bölümü
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.main_layout.addWidget(self.content_widget)
        
        # Footer bölümü (her ekranda gösterilecek)
        self.create_footer()
        
        # Ekranı yükle
        logging.debug(f"Checking for JSON file at: {JSON_FILE}")
        if not JSON_FILE.exists():
            self.open_choose_screen()
        else:
            self.open_draw_screen()
    
    def create_header(self):
        # Başlık container
        header_frame = QFrame()
        header_frame.setMaximumHeight(80)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık
        title_label = QLabel("INOVEL İSİM ÇEKİLİŞ UYGULAMASI")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #fd0700;")  # Turuncu renk
        header_layout.addWidget(title_label)
        
        self.main_layout.addWidget(header_frame)
    
    def create_footer(self):
        # Alt bilgi container
        footer_frame = QFrame()
        footer_frame.setMaximumHeight(30)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 0, 10, 10)
        
        # Boşluk ekle
        footer_layout.addStretch()
        
        # Alt bilgi yazısı
        footer_label = QLabel("made by gkhkaya")
        footer_label.setAlignment(Qt.AlignRight)
        footer_label.setStyleSheet("color: #fd0700; font-style: italic;")  # Turuncu renk
        footer_layout.addWidget(footer_label)
        
        self.main_layout.addWidget(footer_frame)
    
    def setup_style(self):
        # Siyah, gri ve turuncu tema stil ayarları
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: transparent;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #fd0700;  /* Turuncu */
                color: black;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fd0700;  /* Açık turuncu */
            }
            QPushButton:pressed {
                background-color: #fd0700;  /* Koyu turuncu */
            }
            QLineEdit, QSpinBox, QTextEdit {
                background-color: rgba(50, 50, 50, 180);  /* Koyu gri */
                color: white;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
            }
            QFrame {
                background-color: rgba(30, 30, 30, 180);  /* Siyah */
                border-radius: 8px;
            }
            QScrollArea {
                border: none;
            }
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
    
    def setup_background(self, image_path, opacity=0.3):
        try:
            if not os.path.exists(image_path):
                logging.error(f"Background image not found: {image_path}")
                # Eğer dosya bulunamazsa, varsayılan arka plan rengi ayarla
                self.setStyleSheet("background-color: #121212;")  # Koyu siyah
                return
            
            # Arka plan görüntüsü yükle
            background_image = QImage(image_path)
            
            # Opaklık ayarla - Görüntüyü daha saydam yap
            for y in range(background_image.height()):
                for x in range(background_image.width()):
                    color = QColor(background_image.pixelColor(x, y))
                    color.setAlpha(int(255 * opacity))  # %30 opaklık
                    background_image.setPixelColor(x, y, color)
            
            pixmap = QPixmap.fromImage(background_image)
            self.background_image = pixmap.scaled(self.width(), self.height(),
                                                Qt.KeepAspectRatioByExpanding)
            
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(self.background_image))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
            
            logging.debug(f"Background loaded successfully: {image_path}")
        except Exception as e:
            logging.error(f"Background loading error: {str(e)}")
            # Hata durumunda varsayılan arka plan rengi ayarla
            self.setStyleSheet("background-color: #121212;")  # Koyu siyah
    
    def open_choose_screen(self):
        self.clear_content()
        self.choose_screen = ModernChooseScreen(self.content_layout, self.open_draw_screen)
    
    def open_draw_screen(self):
        self.clear_content()
        self.draw_screen = ModernDrawScreen(self.content_layout, self.open_choose_screen)
    
    def clear_content(self):
        # Content layout'u temizle
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def clear_window(self):
        # Tüm layout'u temizle - Başlık ve footer dahil
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class ModernChooseScreen:
    def __init__(self, layout, on_done):
        self.layout = layout
        self.on_done = on_done
        self.lotteries = []
        self.create_widgets()
    
    def create_widgets(self):
        # Başlık container
        title_frame = QFrame()
        title_frame.setMaximumHeight(60)  # Daha küçük başlık alanı
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(5, 5, 5, 5)  # Marginleri azalt
        
        # Başlık
        title_label = QLabel("ÇEKİLİŞ LİSTESİ")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #fd0700;")  # Turuncu renk
        title_layout.addWidget(title_label)
        
        self.layout.addWidget(title_frame)
        
        # Ana container
        main_frame = QFrame()
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(10)  # Boşlukları azalt
        
        # Çekiliş girdileri için scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.entries_layout = QVBoxLayout(scroll_widget)
        self.entries_layout.setSpacing(5)  # Başlıklar arasındaki mesafeyi azalt
        self.entries_layout.setContentsMargins(5, 5, 5, 5)  # Marginleri azalt
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Başlangıç çekiliş satırları
        for _ in range(3):
            self.add_lottery_entry()
        
        # Butonlar için bir konteyner
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)  # Boşlukları azalt
        
        # Yeni satır ekle butonu
        add_button = QPushButton("Yeni Çekiliş Satırı Ekle")
        add_button.clicked.connect(self.add_lottery_entry)
        buttons_layout.addWidget(add_button)
        
        # İsim listesi container
        names_frame = QFrame()
        names_layout = QVBoxLayout(names_frame)
        names_layout.setSpacing(5)  # Boşlukları azalt
        names_layout.setContentsMargins(10, 10, 10, 10)  # Marginleri azalt
        
        names_label = QLabel("İsim Listesi (Excel'den yapıştırın - her isim yeni satırda)")
        names_label.setFont(QFont("Arial", 10, QFont.Bold))
        names_label.setStyleSheet("color: #FF7F00;")  # Turuncu renk
        names_layout.addWidget(names_label)
        
        self.name_entry = QTextEdit()
        self.name_entry.setMinimumHeight(200)  # Daha fazla isim girebilmek için yükseklik artırıldı
        names_layout.addWidget(self.name_entry)
        
        # Örnek veri ekleme butonu
        sample_data_button = QPushButton("Örnek Veri Ekle")
        sample_data_button.clicked.connect(self.add_sample_data)
        names_layout.addWidget(sample_data_button)
        
        buttons_layout.addWidget(names_frame)
        
        # Kaydet butonu
        save_button = QPushButton("Kaydet ve Çekilişe Başla")
        save_button.clicked.connect(self.save_and_exit)
        buttons_layout.addWidget(save_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.layout.addWidget(main_frame)
    
    def add_lottery_entry(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)  # Marginleri azalt
        layout.setSpacing(5)  # İçerideki boşlukları azalt
        
        title_entry = QLineEdit()
        title_entry.setText("Çekiliş Başlığı")
        layout.addWidget(title_entry)
        
        main_count = QSpinBox()
        main_count.setMinimum(1)
        main_count.setMaximum(100)
        main_count.setValue(3)
        layout.addWidget(main_count)
        
        main_label = QLabel("Ana")
        main_label.setStyleSheet("color: #fd0700;")  # Turuncu renk
        layout.addWidget(main_label)
        
        backup_count = QSpinBox()
        backup_count.setMinimum(0)
        backup_count.setMaximum(100)
        backup_count.setValue(2)
        layout.addWidget(backup_count)
        
        backup_label = QLabel("Yedek")
        backup_label.setStyleSheet("color: #fd0700;")  # Turuncu renk
        layout.addWidget(backup_label)
        
        self.entries_layout.addWidget(frame)
        
        self.lotteries.append({
            'frame': frame,
            'title_entry': title_entry,
            'main_count': main_count,
            'backup_count': backup_count
        })
    
    def add_sample_data(self):
        # Excel'den kopyalanmış gibi örnek isim listesi
        sample_names = """Ahmet Yılmaz
Mehmet Kaya
Ayşe Demir
Fatma Çelik
Mustafa Koç
Ali Özkan
Zeynep Şahin
Hüseyin Yıldız
Emine Arslan
Hasan Doğan
Hatice Yalçın
Ömer Aydın
İbrahim Erdoğan
Elif Güneş
Murat Çetin"""
        self.name_entry.setText(sample_names)

    def save_and_exit(self):
        try:
            logging.debug(f"Saving JSON to: {JSON_FILE}")
            final_data = []
            for item in self.lotteries:
                title = item['title_entry'].text().strip()
                main_count = item['main_count'].value()
                backup_count = item['backup_count'].value()
                if not title:
                    QMessageBox.critical(None, "Hata", "Başlık boş bırakılamaz!")
                    return
                final_data.append({
                    'title': title,
                    'main_count': main_count,
                    'backup_count': backup_count
                })
            
            names_text = self.name_entry.toPlainText().strip()
            if not names_text:
                QMessageBox.critical(None, "Hata", "İsim listesi boş olamaz!")
                return
            
            name_list = self.parse_names(names_text)
            if not name_list:
                QMessageBox.critical(None, "Hata", "İsim listesi boş veya hatalı.")
                return
            
            full_data = {'names': name_list, 'draws': final_data}
            with open(JSON_FILE, "w", encoding="utf-8") as file:
                json.dump(full_data, file, ensure_ascii=False, indent=4)
            
            logging.debug("JSON saved successfully")
            QMessageBox.information(None, "Başarılı", f"Çekiliş listesi kaydedildi! Toplam {len(name_list)} isim eklendi.")
            self.on_done()
        except Exception as e:
            logging.error(f"Error saving JSON: {str(e)}")
            QMessageBox.critical(None, "Hata", f"JSON kaydedilirken hata oluştu: {str(e)}")
    
    def parse_names(self, text):
        # Her satırı ayrı bir isim olarak işle
        names = []
        lines = text.strip().split('\n')
        for line in lines:
            name = line.strip()
            if name:  # Boş satırları atlayarak isimleri listeye ekle
                names.append(name)
        
        # Tekrar eden isimleri kontrol et
        unique_names = []
        duplicate_names = []
        for name in names:
            if name not in unique_names:
                unique_names.append(name)
            else:
                if name not in duplicate_names:
                    duplicate_names.append(name)
        
        if duplicate_names:
            message = f"Dikkat: {len(duplicate_names)} tekrar eden isim bulundu:\n"
            message += ", ".join(duplicate_names[:5])
            if len(duplicate_names) > 5:
                message += f" ve {len(duplicate_names)-5} isim daha."
            message += "\n\nBu isimler listede birden fazla yer alacak."
            QMessageBox.warning(None, "Tekrar Eden İsimler", message)
        
        return names if names else None


class ModernDrawScreen:
    def __init__(self, layout, on_reset):
        self.layout = layout
        self.on_reset = on_reset  # Çekiliş sıfırlandığında çağrılacak fonksiyon
        self.load_data()
        self.create_widgets()
        self.current_index = 0
        
        # Her çekiliş için kazananları saklayacak sözlük
        self.winners_history = {}
        
        self.update_draw_info()
        
        self.countdown_thread = None
    
    def load_data(self):
        try:
            logging.debug(f"Loading JSON from: {JSON_FILE}")
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.original_names = data["names"]
                self.names = data["names"].copy()
                self.draws = data["draws"]
            logging.debug("JSON loaded successfully")
        except Exception as e:
            logging.error(f"Error loading JSON: {str(e)}")
            QMessageBox.critical(None, "Hata", f"JSON dosyası yüklenirken hata oluştu: {str(e)}")
            raise
    
    def create_widgets(self):
        # Ana container
        main_frame = QFrame()
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(10)  # Boşlukları azalt
        
        # Kalan katılımcı sayısı
        self.remaining_label = QLabel()
        self.remaining_label.setFont(QFont("Arial", 12))
        self.remaining_label.setAlignment(Qt.AlignCenter)
        self.remaining_label.setStyleSheet("color: #FFFFFF;")
        main_layout.addWidget(self.remaining_label)
        
        # Başlık
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #fd0700;")  # Turuncu renk
        main_layout.addWidget(self.title_label)
        
        # Çekiliş başlat butonu
        self.start_button = QPushButton("ÇEKİLİŞİ BAŞLAT")
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self.start_draw)
        main_layout.addWidget(self.start_button)
        
        # Sayaç etiketi
        self.countdown_label = QLabel()
        self.countdown_label.setFont(QFont("Arial", 60, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("color: #fd0700;")  # Turuncu renk
        self.countdown_label.setMinimumHeight(120)  # Yüksekliği biraz azalt
        main_layout.addWidget(self.countdown_label)
        
        # Sonuç container
        result_frame = QFrame()
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(10, 10, 10, 10)  # Marginleri azalt
        
        # Sonuç etiketi
        self.result_label = QLabel()
        self.result_label.setFont(QFont("Arial", 16))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)  # Uzun isim listeleri için satır kırılımını etkinleştir
        result_layout.addWidget(self.result_label)
        
        main_layout.addWidget(result_frame)
        
        # Butonlar için yatay layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Boşlukları azalt
        
        self.only_main_button = QPushButton("Ana Talihlileri Çıkar ve Diğerine Geç")
        self.only_main_button.clicked.connect(self.remove_main_and_next)
        self.only_main_button.setEnabled(False)
        button_layout.addWidget(self.only_main_button)
        
        self.all_button = QPushButton("Ana + Yedek TalihlTGileri Çıkar ve Diğerine Geç")
        self.all_button.clicked.connect(self.remove_all_and_next)
        self.all_button.setEnabled(False)
        button_layout.addWidget(self.all_button)
        
        main_layout.addLayout(button_layout)
        
        # İsim çıkarma butonu
        self.remove_name_button = QPushButton("BELİRLİ İSMİ LİSTEDEN ÇIKAR")
        self.remove_name_button.clicked.connect(self.remove_specific_name)
        main_layout.addWidget(self.remove_name_button)
        
        # Alt butonlar için yatay layout
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.setSpacing(10)
        
        # İsim listesini göster butonu
        self.show_names_button = QPushButton("KATILIMCI LİSTESİNİ GÖSTER")
        self.show_names_button.clicked.connect(self.show_names)
        bottom_button_layout.addWidget(self.show_names_button)
        
        # Geri dön butonu
        self.back_button = QPushButton("ÖNCEKİ ÇEKİLİŞE DÖN")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        bottom_button_layout.addWidget(self.back_button)
        
        # Çekilişi sıfırla butonu
        self.reset_button = QPushButton("ÇEKİLİŞİ SIFIRLA")
        self.reset_button.clicked.connect(self.reset_lottery)
        bottom_button_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(bottom_button_layout)
        
        self.layout.addWidget(main_frame)
        self.update_remaining_label()
    
    def remove_specific_name(self):
        name, ok = QInputDialog.getText(None, 'İsim Çıkar', 'Listeden çıkarılacak ismi girin:')
        if ok and name:
            if name in self.names:
                self.names.remove(name)
                QMessageBox.information(None, "Başarılı", f"'{name}' ismi listeden çıkarıldı!")
                self.update_remaining_label()
            else:
                QMessageBox.warning(None, "Uyarı", f"'{name}' ismi listede bulunamadı!")
    
    def update_remaining_label(self):
        self.remaining_label.setText(f"Kalan Katılımcı Sayısı: {len(self.names)}")
    
    def update_draw_info(self):
        if self.current_index >= len(self.draws):
            QMessageBox.information(None, "Bitti", "Tüm çekilişler tamamlandı.")
            QApplication.quit()
            return
        
        draw = self.draws[self.current_index]
        self.title_label.setText(draw["title"])
        
        # Eğer bu çekiliş daha önce yapıldıysa sonuçları göster
        if self.current_index in self.winners_history:
            winners = self.winners_history[self.current_index]
            
            result_text = "<b>Ana Talihliler:</b><br>" + "<br>".join(winners['main'])
            
            if winners['backup']:
                result_text += "<br><br><b>Yedek Talihliler:</b><br>" + "<br>".join(winners['backup'])
            
            self.result_label.setText(result_text)
            self.main_winners = winners['main']
            self.backup_winners = winners['backup']
            
            self.only_main_button.setEnabled(True)
            self.all_button.setEnabled(True)
            self.start_button.setText("TEKRAR ÇEK")
        else:
            self.countdown_label.setText("")
            self.result_label.setText("")
            self.start_button.setText("ÇEKİLİŞİ BAŞLAT")
            self.start_button.setEnabled(True)
            self.only_main_button.setEnabled(False)
            self.all_button.setEnabled(False)
        
        self.back_button.setEnabled(self.current_index > 0)
        self.update_remaining_label()
    
    def start_draw(self):
        draw = self.draws[self.current_index]
        total_needed = draw["main_count"] + draw["backup_count"]
        if len(self.names) < total_needed:
            QMessageBox.critical(None, "Hata", "Yeterli katılımcı kalmadı!")
            return
        
        self.start_button.setEnabled(False)
        
        # Sayaç için thread başlat
        self.countdown_thread = CountdownThread()
        self.countdown_thread.signal.connect(self.update_countdown)
        self.countdown_thread.finished.connect(self.perform_draw)
        self.countdown_thread.start()
    
    def update_countdown(self, number):
        self.countdown_label.setText(str(number))
    
    def perform_draw(self):
        draw = self.draws[self.current_index]
        total_needed = draw["main_count"] + draw["backup_count"]
        selected_names = random.sample(self.names, total_needed)
        
        self.main_winners = selected_names[:draw["main_count"]]
        self.backup_winners = selected_names[draw["main_count"]:]
        
        # Çekiliş sonuçlarını geçmişe kaydet
        self.winners_history[self.current_index] = {
            'main': self.main_winners.copy(),
            'backup': self.backup_winners.copy()
        }
        
        result_text = "<b>Ana Talihliler:</b><br>" + "<br>".join(self.main_winners)
        
        if self.backup_winners:
            result_text += "<br><br><b>Yedek Talihliler:</b><br>" + "<br>".join(self.backup_winners)
        
        self.countdown_label.setText("")
        self.result_label.setText(result_text)
        
        self.only_main_button.setEnabled(True)
        self.all_button.setEnabled(True)
        
        self.start_button.setText("TEKRAR ÇEK")
        self.start_button.setEnabled(True)
    
    def remove_main_and_next(self):
        # Mevcut çekilişte çıkan ana talihlileri çıkar
        for name in self.main_winners:
            if name in self.names:  # Güvenlik kontrolü
                self.names.remove(name)
        
        # Sonraki çekilişe geç
        self.current_index += 1
        self.update_draw_info()
    
    def remove_all_and_next(self):
        # Mevcut çekilişte çıkan tüm talihlileri çıkar
        for name in self.main_winners + self.backup_winners:
            if name in self.names:  # Güvenlik kontrolü
                self.names.remove(name)
        
        # Sonraki çekilişe geç
        self.current_index += 1
        self.update_draw_info()
    
    def go_back(self):
        if self.current_index > 0:
            # Önceki çekilişe döndüğümüzde tüm UI elemanlarını ve bilgileri sıfırla
            self.current_index -= 1
            self.countdown_label.setText("")
            self.result_label.setText("")
            self.only_main_button.setEnabled(False)
            self.all_button.setEnabled(False)
            self.start_button.setText("ÇEKİLİŞİ BAŞLAT")
            self.start_button.setEnabled(True)
            self.update_draw_info()
            self.update_remaining_label()
    
    def show_names(self):
        names_dialog = QMessageBox()
        names_dialog.setWindowTitle("Katılımcı Listesi")
        
        # İsimleri daha okunabilir formatta göster (her satırda en fazla 3 isim)
        names_text = ""
        for i, name in enumerate(self.names):
            names_text += name
            if (i + 1) % 3 == 0:
                names_text += "\n"
            else:
                names_text += " | "
        
        names_dialog.setText(f"Toplam {len(self.names)} katılımcı:\n\n{names_text}")
        names_dialog.setStandardButtons(QMessageBox.Ok)
        names_dialog.exec_()
    
    def reset_lottery(self):
        reply = QMessageBox.question(None, 'Çekilişi Sıfırla',
                                   'Çekilişi başlangıç durumuna sıfırlamak istediğinizden emin misiniz?\n'
                                   'Bu işlem mevcut çekiliş listesini silecek ve yeni çekiliş ekleme ekranına yönlendirecektir.',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                logging.debug(f"Removing JSON file: {JSON_FILE}")
                os.remove(JSON_FILE)
                logging.debug("JSON file removed successfully")
                QMessageBox.information(None, "Başarılı", "Çekiliş başarıyla sıfırlandı!")
                self.on_reset()
            except Exception as e:
                logging.error(f"Error removing JSON file: {str(e)}")
                QMessageBox.critical(None, "Hata", f"Dosya silinirken hata oluştu: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Çekiliş uygulaması
    window = LotteryApp()
    
    window.show()
    sys.exit(app.exec_())