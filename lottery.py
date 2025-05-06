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
        self.setWindowTitle("İNOVEL İSİM ÇEKİLİŞ UYGULAMASI")
        self.setGeometry(100, 100, 1920, 1080)
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Arkaplan ayarla
        self.setup_background("lotterybg.png", opacity=0.4)
        
        # Modern stil ayarla
        self.setup_style()
        
        # Başlık bölümü
        self.create_header()
        
        # Ana içerik bölümü
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.main_layout.addWidget(self.content_widget, stretch=1)
        
        # Footer bölümü
        self.create_footer()
        
        # Ekranı yükle
        logging.debug(f"Checking for JSON file at: {JSON_FILE}")
        if not JSON_FILE.exists():
            self.open_choose_screen()
        else:
            self.open_draw_screen()
    
    def create_header(self):
        header_frame = QFrame()
        header_frame.setMaximumHeight(100)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(20)
        
        # İnovel logosu (solda)
        inovel_logo_label = QLabel()
        inovel_pixmap = QPixmap("inovellogo.png")
        if not inovel_pixmap.isNull():
            inovel_pixmap = inovel_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            inovel_logo_label.setPixmap(inovel_pixmap)
        else:
            logging.error("Inovel logo not found: inovellogo")
            inovel_logo_label.setText("Logo Yok")
        inovel_logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(inovel_logo_label)
        
        # Başlık
        title_label = QLabel("İNOVEL ÇEKİLİŞ UYGULAMASI")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        header_layout.addWidget(title_label, stretch=1)
        
        # DPU logosu (sağda)
        dpu_logo_label = QLabel()
        dpu_pixmap = QPixmap("dpulogo.png")
        if not dpu_pixmap.isNull():
            dpu_pixmap = dpu_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            dpu_logo_label.setPixmap(dpu_pixmap)
        else:
            logging.error("DPU logo not found: dpulogo")
            dpu_logo_label.setText("Logo Yok")
        dpu_logo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(dpu_logo_label)
        
        self.main_layout.addWidget(header_frame)
    
    def create_footer(self):
        footer_frame = QFrame()
        footer_frame.setMaximumHeight(50)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        footer_layout.addStretch()
        
        footer_label = QLabel("Made by gkhkaya")
        footer_label.setAlignment(Qt.AlignRight)
        footer_label.setStyleSheet("color: #BBBBBB; font-style: italic; font-size: 14px;")
        footer_layout.addWidget(footer_label)
        
        self.main_layout.addWidget(footer_frame)
    
    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: transparent;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #FF0000; /* Kırmızı */
                color: #FFFFFF;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                transition: all 0.3s;
            }
            QPushButton:hover {
                background-color: #FF3333; /* Daha açık kırmızı */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed {
                background-color: #CC0000; /* Daha koyu kırmızı */
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
            }
            QLineEdit, QSpinBox, QTextEdit {
                background-color: rgba(40, 40, 40, 0.9);
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QFrame {
                background-color: rgba(30, 30, 30, 0.95);
                border-radius: 12px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QCheckBox {
                color: #FFFFFF;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #FF0000; /* Kırmızı */
                border-radius: 4px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #FF3333; /* Daha açık kırmızı */
            }
        """)
    
    def setup_background(self, image_path, opacity=0.4):
        try:
            if not os.path.exists(image_path):
                logging.error(f"Background image not found: {image_path}")
                # Varsayılan gradyan arka plan
                self.setStyleSheet("""
                    QMainWindow {
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:1,
                            stop:0 #1E1E2E, stop:1 #2E2E4E
                        );
                    }
                """)
                return
            
            background_image = QImage(image_path)
            for y in range(background_image.height()):
                for x in range(background_image.width()):
                    color = QColor(background_image.pixelColor(x, y))
                    color.setAlpha(int(255 * opacity))
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
            self.setStyleSheet("""
                QMainWindow {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1E1E2E, stop:1 #2E2E4E
                    );
                }
            """)
    
    def open_choose_screen(self):
        self.clear_content()
        self.choose_screen = ModernChooseScreen(self.content_layout, self.open_draw_screen)
    
    def open_draw_screen(self):
        self.clear_content()
        self.draw_screen = ModernDrawScreen(self.content_layout, self.open_choose_screen)
    
    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def clear_window(self):
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
        title_frame = QFrame()
        title_frame.setMaximumHeight(80)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("ÇEKİLİŞ LİSTESİ")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        title_layout.addWidget(title_label)
        
        self.layout.addWidget(title_frame)
        
        main_frame = QFrame()
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.entries_layout = QVBoxLayout(scroll_widget)
        self.entries_layout.setSpacing(10)
        self.entries_layout.setContentsMargins(10, 10, 10, 10)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, stretch=1)
        
        for _ in range(3):
            self.add_lottery_entry()
        
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        
        add_button = QPushButton("Yeni Çekiliş Satırı Ekle")
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.clicked.connect(self.add_lottery_entry)
        buttons_layout.addWidget(add_button)
        
        names_frame = QFrame()
        names_layout = QVBoxLayout(names_frame)
        names_layout.setSpacing(10)
        names_layout.setContentsMargins(15, 15, 15, 15)
        
        names_label = QLabel("İsim Listesi")
        names_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        names_label.setStyleSheet("color: #FFFFFF;")
        names_layout.addWidget(names_label)
        
        self.name_entry = QTextEdit()
        self.name_entry.setMinimumHeight(250)
        names_layout.addWidget(self.name_entry, stretch=1)
        
        sample_data_button = QPushButton("Örnek Veri Ekle")
        sample_data_button.setIcon(QIcon.fromTheme("document-new"))
        sample_data_button.clicked.connect(self.add_sample_data)
        names_layout.addWidget(sample_data_button)
        
        buttons_layout.addWidget(names_frame)
        
        save_button = QPushButton("Kaydet ve Çekilişe Başla")
        save_button.setIcon(QIcon.fromTheme("document-save"))
        save_button.clicked.connect(self.save_and_exit)
        buttons_layout.addWidget(save_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.layout.addWidget(main_frame, stretch=2)
    
    def add_lottery_entry(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        title_entry = QLineEdit()
        title_entry.setText("Çekiliş Başlığı")
        title_entry.setPlaceholderText("Çekiliş başlığını girin")
        layout.addWidget(title_entry, stretch=3)
        
        main_count = QSpinBox()
        main_count.setMinimum(1)
        main_count.setMaximum(100)
        main_count.setValue(3)
        layout.addWidget(main_count, stretch=1)
        
        main_label = QLabel("Ana")
        main_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        layout.addWidget(main_label)
        
        backup_count = QSpinBox()
        backup_count.setMinimum(0)
        backup_count.setMaximum(100)
        backup_count.setValue(2)
        layout.addWidget(backup_count, stretch=1)
        
        backup_label = QLabel("Yedek")
        backup_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        layout.addWidget(backup_label)
        
        delete_button = QPushButton("Sil")
        delete_button.setIcon(QIcon.fromTheme("edit-delete"))
        delete_button.setFixedWidth(80)
        delete_button.clicked.connect(lambda: self.delete_lottery_entry(frame, title_entry, main_count, backup_count))
        layout.addWidget(delete_button)
        
        self.entries_layout.addWidget(frame)
        
        self.lotteries.append({
            'frame': frame,
            'title_entry': title_entry,
            'main_count': main_count,
            'backup_count': backup_count
        })
    
    def delete_lottery_entry(self, frame, title_entry, main_count, backup_count):
        if len(self.lotteries) <= 1:
            QMessageBox.warning(None, "Uyarı", "En az bir çekiliş satırı kalmalı!")
            return
        
        for item in self.lotteries:
            if item['frame'] == frame:
                self.lotteries.remove(item)
                break
        
        frame.deleteLater()
        self.entries_layout.removeWidget(frame)
        logging.debug("Lottery entry deleted successfully")
    
    def add_sample_data(self):
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
        names = []
        lines = text.strip().split('\n')
        for line in lines:
            name = line.strip()
            if name:
                names.append(name)
        
        unique_names = []
        duplicate_names = []
        for name in names:
            if name not in unique_names:
                unique_names.append(name)
            else:
                duplicate_names.append(name)
        
        if duplicate_names:
            message = f"Dikkat: {len(duplicate_names)} tekrar eden isim bulundu ve listeden çıkarıldı:\n"
            message += ", ".join(duplicate_names[:5])
            if len(duplicate_names) > 5:
                message += f" ve {len(duplicate_names)-5} isim daha."
            QMessageBox.information(None, "Tekrar Eden İsimler Kaldırıldı", message)
    
        return unique_names if unique_names else None


class ModernDrawScreen:
    def __init__(self, layout, on_reset):
        self.layout = layout
        self.on_reset = on_reset
        self.load_data()
        self.create_widgets()
        self.current_index = 0
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
        main_frame = QFrame()
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.remaining_label = QLabel()
        self.remaining_label.setFont(QFont("Segoe UI", 14))
        self.remaining_label.setAlignment(Qt.AlignCenter)
        self.remaining_label.setStyleSheet("color: #BBBBBB; background: transparent;")
        main_layout.addWidget(self.remaining_label)
        
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        main_layout.addWidget(self.title_label)
        
        self.start_button = QPushButton("ÇEKİLİŞİ BAŞLAT")
        self.start_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_button.setMinimumHeight(60)
        self.start_button.clicked.connect(self.start_draw)
        main_layout.addWidget(self.start_button)
        
        self.countdown_label = QLabel()
        self.countdown_label.setFont(QFont("Segoe UI", 72, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        self.countdown_label.setMinimumHeight(100)
        main_layout.addWidget(self.countdown_label)
        
        result_frame = QFrame()
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(15, 15, 15, 15)
        
        self.result_label = QLabel()
        self.result_label.setFont(QFont("Segoe UI", 16))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        result_layout.addWidget(self.result_label)
        
        main_layout.addWidget(result_frame, stretch=1)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.only_main_button = QPushButton("Ana Talihlileri Çıkar ve Diğerine Geç")
        self.only_main_button.setIcon(QIcon.fromTheme("go-next"))
        self.only_main_button.clicked.connect(self.remove_main_and_next)
        self.only_main_button.setEnabled(False)
        button_layout.addWidget(self.only_main_button)
        
        self.all_button = QPushButton("Ana + Yedek Talihlileri Çıkar ve Diğerine Geç")
        self.all_button.setIcon(QIcon.fromTheme("go-next"))
        self.all_button.clicked.connect(self.remove_all_and_next)
        self.all_button.setEnabled(False)
        button_layout.addWidget(self.all_button)
        
        main_layout.addLayout(button_layout)
        
        self.remove_name_button = QPushButton("BELİRLİ İSMİ LİSTEDEN ÇIKAR")
        self.remove_name_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.remove_name_button.clicked.connect(self.remove_specific_name)
        main_layout.addWidget(self.remove_name_button)
        
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.setSpacing(15)
        
        self.show_names_button = QPushButton("KATILIMCI LİSTESİNİ GÖSTER")
        self.show_names_button.setIcon(QIcon.fromTheme("view-list"))
        self.show_names_button.clicked.connect(self.show_names)
        bottom_button_layout.addWidget(self.show_names_button)
        
        self.back_button = QPushButton("ÖNCEKİ ÇEKİLİŞE DÖN")
        self.back_button.setIcon(QIcon.fromTheme("go-previous"))
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        bottom_button_layout.addWidget(self.back_button)
        
        self.reset_button = QPushButton("ÇEKİLİŞİ SIFIRLA")
        self.reset_button.setIcon(QIcon.fromTheme("view-refresh"))
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
        
        if self.current_index in self.winners_history:
            winners = self.winners_history[self.current_index]
            
            # Ana talihlileri yan yana göster
            result_text = "<b>Ana Talihliler:</b> " + " - ".join(winners['main'])            
            # Yedek talihliler varsa, onları da yan yana göster
            if winners['backup']:
                result_text += "<br><br><b>Yedek Talihliler:</b> " + " - ".join(winners['backup'])            
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
        
        self.winners_history[self.current_index] = {
            'main': self.main_winners.copy(),
            'backup': self.backup_winners.copy()
        }
        
        # Ana talihlileri yan yana, - ayrılmış şekilde göster
        result_text = "<b>Ana Talihliler:</b> " + " - ".join(self.main_winners)        
        # Yedek talihliler varsa, onları da yan yana göster
        if self.backup_winners:
            result_text += "<br><br><b>Yedek Talihliler:</b> " + " - ".join(self.backup_winners)
        
        self.countdown_label.setText("")
        self.result_label.setText(result_text)
        
        self.only_main_button.setEnabled(True)
        self.all_button.setEnabled(True)
        
        self.start_button.setText("TEKRAR ÇEK")
        self.start_button.setEnabled(True)
    
    def remove_main_and_next(self):
        for name in self.main_winners:
            if name in self.names:
                self.names.remove(name)
        
        self.current_index += 1
        self.update_draw_info()
    
    def remove_all_and_next(self):
        for name in self.main_winners + self.backup_winners:
            if name in self.names:
                self.names.remove(name)
        
        self.current_index += 1
        self.update_draw_info()
    
    def go_back(self):
        if self.current_index > 0:
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
    
    window = LotteryApp()
    
    window.show()
    sys.exit(app.exec_())