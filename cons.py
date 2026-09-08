# cons.py
import sys
import os
import re
import shutil
import json
import urllib.request
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox,
                               QTabWidget, QMessageBox, QCompleter, QColorDialog,
                               QListWidget, QListWidgetItem, QInputDialog, QSlider,
                               QScrollArea, QSpinBox)
from PySide6.QtCore import Qt, QRect, QUrl, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPainterPath, QPen, QFontDatabase
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
try:
    from PySide6.QtPdf import QPdfDocument
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

class DatabaseManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إدارة قاعدة بيانات القرآن - Mohammed Eto")
        self.resize(1050, 850)
        self.setLayoutDirection(Qt.RightToLeft)
        self.loaded_fonts = []
        fonts_dir = os.path.join("Data", "Fonts")
        if os.path.exists(fonts_dir):
            for f in os.listdir(fonts_dir):
                if f.endswith(".ttf"):
                    font_id = QFontDatabase.addApplicationFont(os.path.join(fonts_dir, f))
                    if font_id != -1:
                        self.loaded_fonts.extend(QFontDatabase.applicationFontFamilies(font_id))
        self.loaded_fonts = sorted(list(set(self.loaded_fonts)))
        if not self.loaded_fonts:
            print("تنبيه: لم يتم العثور على خطوط في مسار Data/Fonts.")
        self.js_file = os.path.join("Data", "cons.js")
        self.en_surahs_file = os.path.join("Data", "cons_surah_en.txt")
        self.ar_surahs_file = os.path.join("Data", "cons_surah_ar.txt")
        self.sheikhs_data = [] 
        self.surahs_data = []
        self.reciters_json_data = []

        self.setup_audio_player()
        self.load_surah_names()
        self.load_reciters_json()
        self.setup_ui()
        self.load_sheikhs()
        self.populate_reciters_combo()
        self.setup_pdf_viewer()

    def load_surah_names(self):
        try:
            with open(self.en_surahs_file, 'r', encoding='utf-8') as f_en, \
                 open(self.ar_surahs_file, 'r', encoding='utf-8') as f_ar:
                en_names = [line.strip() for line in f_en.readlines() if line.strip()]
                ar_names = [line.strip() for line in f_ar.readlines() if line.strip()]
                self.surahs_data = list(zip(en_names, ar_names))
        except Exception as e:
            pass

    def load_reciters_json(self):
        reciters_path = os.path.join("Data", "القرآن", "reciters.json")
        if os.path.exists(reciters_path):
            try:
                with open(reciters_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reciters_json_data = data.get("reciters", [])
            except Exception as e:
                print(f"خطأ أثناء قراءة ملف reciters.json: {e}")

    def setup_audio_player(self):
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        
        self.player.positionChanged.connect(self.on_audio_position_changed)
        self.player.durationChanged.connect(self.on_audio_duration_changed)
        self.player.playbackStateChanged.connect(self.on_playback_state_changed)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        btn_refresh = QPushButton(" تحديث البيانات من الملف")
        btn_refresh.setStyleSheet("""
            QPushButton { background-color: #a6e3a1; color: #11111b; font-weight: bold; padding: 8px; border-radius: 6px; }
            QPushButton:hover { background-color: #94e2d5; border: 1px solid #cdd6f4; }
            QPushButton:pressed { background-color: #74c7ec; }
        """)
        btn_refresh.clicked.connect(self.load_sheikhs)
        main_layout.addWidget(btn_refresh)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tab_quran = QWidget()
        self.setup_quran_tab()
        self.tabs.addTab(self.tab_quran, " المصحف الشريف والاستماع")

        self.tab_sheikh = QWidget()
        sheikh_layout = QVBoxLayout(self.tab_sheikh)
        
        self.s_id_input = QLineEdit()
        self.s_id_input.setPlaceholderText("مثال: sudais")
        self.s_name_input = QLineEdit()
        self.s_name_input.setPlaceholderText("مثال: عبدالرحمن السديس")
        
        sheikh_layout.addWidget(QLabel("ID الشيخ (إنجليزي):"))
        sheikh_layout.addWidget(self.s_id_input)
        sheikh_layout.addWidget(QLabel("اسم الشيخ (عربي):"))
        sheikh_layout.addWidget(self.s_name_input)
        
        btn_add_sheikh = QPushButton("إضافة الشيخ لملف cons.js")
        btn_add_sheikh.clicked.connect(self.add_sheikh)
        sheikh_layout.addWidget(btn_add_sheikh)
        sheikh_layout.addStretch()
        
        self.tab_surah = QWidget()
        surah_layout = QVBoxLayout(self.tab_surah)
        
        self.combo_sheikhs = QComboBox()
        self.combo_surahs = QComboBox()
        
        self.combo_sheikhs.currentIndexChanged.connect(self.update_surahs_dropdown)
            
        self.combo_sheikhs.setEditable(True)
        self.combo_sheikhs.setInsertPolicy(QComboBox.NoInsert)
        sheikh_completer = QCompleter(self.combo_sheikhs.model(), self)
        sheikh_completer.setFilterMode(Qt.MatchContains)
        sheikh_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.combo_sheikhs.setCompleter(sheikh_completer)

        self.combo_surahs.setEditable(True)
        self.combo_surahs.setInsertPolicy(QComboBox.NoInsert)
        surah_completer = QCompleter(self.combo_surahs.model(), self)
        surah_completer.setFilterMode(Qt.MatchContains)
        surah_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.combo_surahs.setCompleter(surah_completer)

        self.surah_url_input = QLineEdit()
        self.surah_url_input.setPlaceholderText("رابط الـ MP3")
        
        url_layout = QHBoxLayout()
        btn_paste = QPushButton("لصق الرابط")
        btn_paste.clicked.connect(lambda: self.surah_url_input.setText(QApplication.clipboard().text()))
        url_layout.addWidget(self.surah_url_input)
        url_layout.addWidget(btn_paste)
        
        surah_layout.addWidget(QLabel("اختر الشيخ:"))
        surah_layout.addWidget(self.combo_sheikhs)
        surah_layout.addWidget(QLabel("اختر السورة:"))
        surah_layout.addWidget(self.combo_surahs)
        surah_layout.addWidget(QLabel("رابط الصوت:"))
        surah_layout.addLayout(url_layout)
        
        btn_add_surah = QPushButton("إضافة السورة لملف cons.js")
        btn_add_surah.clicked.connect(self.add_surah)
        surah_layout.addWidget(btn_add_surah)
        surah_layout.addStretch()

        self.tabs.addTab(self.tab_sheikh, "إضافة شيخ جديد")
        self.tabs.addTab(self.tab_surah, "إضافة سورة جديدة")
        self.tab_image_maker = QWidget()
        maker_layout = QVBoxLayout(self.tab_image_maker)
        
        self.combo_maker_sheikhs = QComboBox()
        self.combo_maker_surahs = QComboBox()
        self.combo_maker_sheikhs.currentIndexChanged.connect(self.update_maker_surahs)
        
        self.bg_color = QColor("#1e1e2e")
        self.text_color = QColor("#cdd6f4")
        self.cover_color = QColor("#313244")
        
        theme_layout = QHBoxLayout()
        self.combo_themes = QComboBox()
        self.combo_themes.addItem("اختر ثيم جاهز...", None)
        self.load_themes() 
        self.combo_themes.currentIndexChanged.connect(self.apply_theme)
        
        btn_toggle_custom = QPushButton(" ألوان مخصصة")
        btn_toggle_custom.setCheckable(True)
        btn_toggle_custom.setStyleSheet("""
            QPushButton { background-color: #fab387; color: #11111b; font-weight: bold; padding: 8px; border-radius: 6px; }
            QPushButton:hover { background-color: #f9e2af; border: 1px solid #cdd6f4; }
            QPushButton:checked { background-color: #f38ba8; color: #11111b; border: 2px solid #cba6f7; }
        """)
        btn_toggle_custom.clicked.connect(self.toggle_custom_colors)
        
        theme_layout.addWidget(QLabel("الثيمات:"))
        theme_layout.addWidget(self.combo_themes)
        theme_layout.addWidget(btn_toggle_custom)
        
        self.custom_colors_widget = QWidget()
        color_layout = QHBoxLayout(self.custom_colors_widget)
        color_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_bg_color = QPushButton("لون الخلفية")
        btn_bg_color.clicked.connect(self.choose_bg_color)
        btn_text_color = QPushButton("لون النص")
        btn_text_color.clicked.connect(self.choose_text_color)
        btn_cover_color = QPushButton("لون الغلاف")
        btn_cover_color.clicked.connect(self.choose_cover_color)
        
        color_layout.addWidget(btn_bg_color)
        color_layout.addWidget(btn_text_color)
        color_layout.addWidget(btn_cover_color)
        self.custom_colors_widget.hide()
        
        self.combo_fonts = QComboBox()
        if hasattr(self, 'loaded_fonts') and self.loaded_fonts:
            self.combo_fonts.addItems(self.loaded_fonts)
            
        maker_layout.addWidget(QLabel("اختر الشيخ:"))
        maker_layout.addWidget(self.combo_maker_sheikhs)
        maker_layout.addWidget(QLabel("اختر السورة:"))
        maker_layout.addWidget(self.combo_maker_surahs)
        maker_layout.addWidget(QLabel("اختر الخط:"))
        maker_layout.addWidget(self.combo_fonts)
        maker_layout.addLayout(theme_layout)
        maker_layout.addWidget(self.custom_colors_widget)
        
        self.preview_label = QLabel("المعاينة ستظهر هنا")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px dashed #89b4fa; border-radius: 15px; margin-top: 15px; background-color: #181825;")
        self.preview_label.setMinimumHeight(220)
        maker_layout.addWidget(self.preview_label)

        btn_generate = QPushButton(" 💾 إنشاء الصورة وحفظها ")
        btn_generate.setStyleSheet("""
            QPushButton { background-color: #cba6f7; color: #11111b; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 6px; }
            QPushButton:hover { background-color: #b4befe; }
        """)
        btn_generate.clicked.connect(lambda: self.generate_image(preview_only=False))
        
        maker_layout.addWidget(btn_generate)
        
        self.combo_maker_sheikhs.currentIndexChanged.connect(lambda *args: self.generate_image(preview_only=True))
        self.combo_maker_surahs.currentIndexChanged.connect(lambda *args: self.generate_image(preview_only=True))
        self.combo_fonts.currentIndexChanged.connect(lambda *args: self.generate_image(preview_only=True))
        
        maker_layout.addStretch()
        self.tabs.addTab(self.tab_image_maker, " صورة السورة")

        self.tab_sync = QWidget()
        sync_layout = QVBoxLayout(self.tab_sync)

        sync_controls = QHBoxLayout()
        self.combo_sync_sheikhs = QComboBox()
        self.combo_sync_surahs = QComboBox()
        self.combo_sync_sheikhs.currentIndexChanged.connect(self.update_sync_surahs)

        btn_fetch = QPushButton("⬇️ جلب الآيات من API")
        btn_fetch.setStyleSheet("""
            QPushButton { background-color: #89b4fa; color: #11111b; font-weight: bold; padding: 8px; border-radius: 6px; }
            QPushButton:hover { background-color: #b4befe; border: 1px solid #cdd6f4; }
            QPushButton:pressed { background-color: #74c7ec; }
        """)
        btn_fetch.clicked.connect(self.fetch_verses)

        sync_controls.addWidget(QLabel("الشيخ:"))
        sync_controls.addWidget(self.combo_sync_sheikhs)
        sync_controls.addWidget(QLabel("السورة:"))
        sync_controls.addWidget(self.combo_sync_surahs)
        sync_controls.addWidget(btn_fetch)

        sync_layout.addLayout(sync_controls)

        self.list_verses = QListWidget()
        self.list_verses.setStyleSheet("""
            QListWidget {
                background-color: #313244; color: #cdd6f4; 
                font-size: 20px; padding: 10px; font-family: 'Amiri Quran', Arial;
                border: 2px solid #45475a; border-radius: 8px; outline: none;
            }
            QListWidget::item { 
                padding: 8px; border-radius: 5px; margin-bottom: 4px; 
            }
            QListWidget::item:hover { 
                background-color: #45475a; 
            }
            QListWidget::item:selected { 
                background-color: #89b4fa; color: #11111b; font-weight: bold; 
            }
            
            QScrollBar:vertical {
                border: none; background-color: #1e1e2e; 
                width: 14px; margin: 2px; border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #585b70; min-height: 40px; border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover { background-color: #89b4fa; }
            QScrollBar::handle:vertical:pressed { background-color: #cba6f7; }
            
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { 
                width: 0px; height: 0px; background: none; 
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        self.list_verses.itemDoubleClicked.connect(self.set_verse_timing)
        sync_layout.addWidget(self.list_verses)

        btn_save_sync = QPushButton(" إنشاء وحفظ ملف التزامن (.js)")
        btn_save_sync.setStyleSheet("""
            QPushButton { background-color: #a6e3a1; color: #11111b; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 6px; }
            QPushButton:hover { background-color: #94e2d5; }
        """)
        btn_save_sync.clicked.connect(self.save_sync_file)
        
        sync_layout.addWidget(btn_save_sync)
        self.tabs.addTab(self.tab_sync, " تزامن الآيات")
        
        self.verses_data = [] 

    def setup_quran_tab(self):
        quran_layout = QVBoxLayout(self.tab_quran)
        
        player_box = QWidget()
        player_box.setStyleSheet("background-color: #313244; border-radius: 10px; padding: 8px;")
        player_layout = QVBoxLayout(player_box)
        
        selectors_layout = QHBoxLayout()
        
        self.combo_quran_reciter = QComboBox()
        self.combo_quran_moshaf = QComboBox()
        self.combo_quran_surah = QComboBox()

        self.combo_quran_reciter.setEditable(True)
        self.combo_quran_reciter.setInsertPolicy(QComboBox.NoInsert)
        reciter_completer = QCompleter(self.combo_quran_reciter.model(), self)
        reciter_completer.setFilterMode(Qt.MatchContains)
        self.combo_quran_reciter.setCompleter(reciter_completer)

        self.combo_quran_surah.setEditable(True)
        self.combo_quran_surah.setInsertPolicy(QComboBox.NoInsert)
        surah_completer = QCompleter(self.combo_quran_surah.model(), self)
        surah_completer.setFilterMode(Qt.MatchContains)
        self.combo_quran_surah.setCompleter(surah_completer)

        self.combo_quran_reciter.currentIndexChanged.connect(self.on_quran_reciter_changed)
        self.combo_quran_moshaf.currentIndexChanged.connect(self.on_quran_moshaf_changed)

        selectors_layout.addWidget(QLabel("الشيخ:"))
        selectors_layout.addWidget(self.combo_quran_reciter, 2)
        selectors_layout.addWidget(QLabel("الرواية/المصحف:"))
        selectors_layout.addWidget(self.combo_quran_moshaf, 2)
        selectors_layout.addWidget(QLabel("السورة:"))
        selectors_layout.addWidget(self.combo_quran_surah, 2)

        player_layout.addLayout(selectors_layout)

        controls_layout = QHBoxLayout()
        self.btn_quran_play = QPushButton("▶ تشغيل")
        self.btn_quran_play.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold; min-width: 90px;")
        self.btn_quran_play.clicked.connect(self.toggle_quran_play)

        self.slider_audio = QSlider(Qt.Horizontal)
        self.slider_audio.setRange(0, 0)
        self.slider_audio.sliderMoved.connect(self.set_audio_position)

        self.lbl_audio_time = QLabel("00:00 / 00:00")
        self.lbl_audio_time.setStyleSheet("color: #89b4fa; font-weight: bold;")

        controls_layout.addWidget(self.btn_quran_play)
        controls_layout.addWidget(self.slider_audio, 1)
        controls_layout.addWidget(self.lbl_audio_time)

        player_layout.addLayout(controls_layout)
        quran_layout.addWidget(player_box)

        pdf_nav_layout = QHBoxLayout()
        self.btn_prev_page = QPushButton("◀ الصفحة التالية")
        self.btn_next_page = QPushButton("الصفحة السابقة ▶")
        
        self.btn_prev_page.clicked.connect(self.next_pdf_page)
        self.btn_next_page.clicked.connect(self.prev_pdf_page)

        self.spin_page = QSpinBox()
        self.spin_page.setRange(1, 1)
        self.spin_page.valueChanged.connect(self.jump_to_pdf_page)
        
        self.lbl_page_count = QLabel("/ 0")

        pdf_nav_layout.addWidget(self.btn_next_page)
        pdf_nav_layout.addStretch()
        pdf_nav_layout.addWidget(QLabel("صفحة رقم:"))
        pdf_nav_layout.addWidget(self.spin_page)
        pdf_nav_layout.addWidget(self.lbl_page_count)
        pdf_nav_layout.addStretch()
        pdf_nav_layout.addWidget(self.btn_prev_page)

        quran_layout.addLayout(pdf_nav_layout)
        self.scroll_pdf = QScrollArea()
        self.scroll_pdf.setWidgetResizable(True)
        self.scroll_pdf.setStyleSheet("QScrollArea { background-color: #181825; border: 2px solid #89b4fa; border-radius: 10px; }")

        self.lbl_pdf_render = QLabel("جاري تحميل المصحف الشريف...")
        self.lbl_pdf_render.setAlignment(Qt.AlignCenter)
        self.lbl_pdf_render.setStyleSheet("background-color: #ffffff; border-radius: 8px; margin: 10px;")

        self.scroll_pdf.setWidget(self.lbl_pdf_render)
        quran_layout.addWidget(self.scroll_pdf, 1)

    def populate_reciters_combo(self):
        self.combo_quran_reciter.clear()
        for reciter in self.reciters_json_data:
            self.combo_quran_reciter.addItem(reciter.get("name", ""), reciter)
        if self.reciters_json_data:
            self.on_quran_reciter_changed()

    def on_quran_reciter_changed(self):
        self.combo_quran_moshaf.clear()
        reciter = self.combo_quran_reciter.currentData()
        if not reciter: return
        for m in reciter.get("moshaf", []):
            self.combo_quran_moshaf.addItem(m.get("name", ""), m)
        if reciter.get("moshaf"):
            self.on_quran_moshaf_changed()

    def on_quran_moshaf_changed(self):
        self.combo_quran_surah.clear()
        moshaf = self.combo_quran_moshaf.currentData()
        if not moshaf: return
        surah_list_str = moshaf.get("surah_list", "")
        surah_ids = [s.strip() for s in surah_list_str.split(",") if s.strip()]

        for i in range(1, 115):
            if str(i) in surah_ids:
                name_ar = self.surahs_data[i-1][1] if i-1 < len(self.surahs_data) else f"سورة {i}"
                self.combo_quran_surah.addItem(f"{i}. {name_ar}", i)

    def get_selected_quran_audio_url(self):
        moshaf = self.combo_quran_moshaf.currentData()
        surah_num = self.combo_quran_surah.currentData()
        if not moshaf or not surah_num: return None
        server = moshaf.get("server", "").replace("https://", "http://")
        if not server.endswith("/"): server += "/"
        return f"{server}{int(surah_num):03d}.mp3"

    def toggle_quran_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            url_str = self.get_selected_quran_audio_url()
            if not url_str:
                QMessageBox.warning(self, "تنبيه", "يرجى اختيار الشيخ والسورة أولاً")
                return
            if self.player.source().toString() != url_str:
                self.player.setSource(QUrl(url_str))
            self.player.play()

    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.btn_quran_play.setText(" إيقاف مؤقت")
            self.btn_quran_play.setStyleSheet("background-color: #f38ba8; color: #11111b; font-weight: bold;")
        else:
            self.btn_quran_play.setText("▶ تشغيل")
            self.btn_quran_play.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold;")

    def on_audio_position_changed(self, pos):
        if not self.slider_audio.isSliderDown():
            self.slider_audio.setValue(pos)
        self.lbl_audio_time.setText(f"{self.format_ms(pos)} / {self.format_ms(self.player.duration())}")

    def on_audio_duration_changed(self, duration):
        self.slider_audio.setMaximum(duration)

    def set_audio_position(self, pos):
        self.player.setPosition(pos)

    def format_ms(self, ms):
        seconds = (ms // 1000) % 60
        minutes = (ms // (1000 * 60)) % 60
        hours = (ms // (1000 * 60 * 60))
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def setup_pdf_viewer(self):
        pdf_path = os.path.join("Data", "القرآن", "القرآن الكريم كاملاً.pdf")
        self.pdf_doc = QPdfDocument(self) if HAS_PDF else None
        self.pdf_current_page = 0
        self.pdf_total_pages = 0

        if self.pdf_doc and os.path.exists(pdf_path):
            self.pdf_doc.load(pdf_path)
            self.pdf_total_pages = self.pdf_doc.pageCount()
            self.lbl_page_count.setText(f"/ {self.pdf_total_pages}")
            self.spin_page.setMaximum(self.pdf_total_pages if self.pdf_total_pages > 0 else 1)
            self.spin_page.setMinimum(1 if self.pdf_total_pages > 0 else 0)
            self.render_pdf_page(0)
        else:
            self.lbl_pdf_render.setText("لم يتم العثور على ملف PDF في المسار المطلوب أو مكتبة PDF غير متاحة.")

    def render_pdf_page(self, page_index):
        if not self.pdf_doc or page_index < 0 or page_index >= self.pdf_total_pages: return
        self.pdf_current_page = page_index
        self.spin_page.blockSignals(True)
        self.spin_page.setValue(page_index + 1)
        self.spin_page.blockSignals(False)

        img = self.pdf_doc.render(page_index, QSize(750, 1050))
        pix = QPixmap.fromImage(img)
        self.lbl_pdf_render.setPixmap(pix)

    def next_pdf_page(self):
        if self.pdf_current_page < self.pdf_total_pages - 1:
            self.render_pdf_page(self.pdf_current_page + 1)

    def prev_pdf_page(self):
        if self.pdf_current_page > 0:
            self.render_pdf_page(self.pdf_current_page - 1)

    def jump_to_pdf_page(self, page_num):
        page_idx = page_num - 1
        if 0 <= page_idx < self.pdf_total_pages:
            self.render_pdf_page(page_idx)

    # ====== باقي الوظائف الأصلية ======
    def read_file(self):
        if not os.path.exists(self.js_file):
            QMessageBox.critical(self, "خطأ", f"ملف {self.js_file} غير موجود داخل مجلد Data!")
            return ""
        with open(self.js_file, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, content):
        if os.path.exists(self.js_file):
            shutil.copy2(self.js_file, self.js_file + ".bak")
            
        with open(self.js_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def load_sheikhs(self):
        content = self.read_file()
        if not content: return
        
        self.combo_sheikhs.clear()
        self.sheikhs_data = []
        matches = re.findall(r'id:\s*"([^"]+)",\s*name:\s*"([^"]+)",\s*image:', content)
        
        self.combo_maker_sheikhs.clear()
        self.combo_sync_sheikhs.clear()
        for m in matches:
            s_id, s_name = m
            self.sheikhs_data.append({"id": s_id, "name": s_name})
            self.combo_sheikhs.addItem(s_name, s_id)
            self.combo_maker_sheikhs.addItem(s_name, s_id)
            self.combo_sync_sheikhs.addItem(s_name, s_id)

    def update_surahs_dropdown(self):
        self.combo_surahs.clear()
        if self.combo_sheikhs.count() == 0:
            return
            
        s_id = self.combo_sheikhs.currentData()
        content = self.read_file()
        
        added_surahs = []
        if content and s_id:
            search_str = f'id: "{s_id}"'
            if search_str in content:
                parts = content.split(search_str, 1)
                next_sheikh_idx = parts[1].find('id: "')
                sheikh_block = parts[1][:next_sheikh_idx] if next_sheikh_idx != -1 else parts[1]
                added_surahs = re.findall(r'id:\s*"([^"]+)"', sheikh_block)

        for en, ar in self.surahs_data:
            if en not in added_surahs:
                self.combo_surahs.addItem(ar, en)

    def add_sheikh(self):
        s_id = self.s_id_input.text().strip()
        s_name = self.s_name_input.text().strip()
        
        if not s_id or not s_name:
            QMessageBox.warning(self, "تنبيه", "يرجى ملء جميع الحقول!")
            return

        if any(s['id'] == s_id for s in self.sheikhs_data):
            QMessageBox.warning(self, "خطأ", f"الشيخ الذي يحمل ID ({s_id}) موجود بالفعل في القاعدة!")
            return

        content = self.read_file()
        if not content: return

        new_block = f"""    {{
        id: "{s_id}",
        name: "{s_name}",
        image: "Data/{s_name}/shiekh.png",
        surahs: []
    }},
"""
        content = content.replace("];", new_block + "];")
        content = re.sub(r',\s*];', '\n];', content)
        
        self.write_file(content)
        
        QMessageBox.information(self, "نجاح", f"تم إضافة الكود الخاص بالشيخ {s_name} في ملف cons.js بنجاح!\n(تم أخذ نسخة احتياطية للملف الأصلي)")
        self.s_id_input.clear()
        self.s_name_input.clear()
        self.load_sheikhs()

    def add_surah(self):
        if self.combo_sheikhs.count() == 0 or self.combo_surahs.count() == 0: return
        
        s_id = self.combo_sheikhs.currentData()
        s_name = self.combo_sheikhs.currentText()
        surah_id = self.combo_surahs.currentData()
        surah_name_full = self.combo_surahs.currentText()
        audio_url = self.surah_url_input.text().strip()
        
        if not all([surah_id, surah_name_full, audio_url]):
            QMessageBox.warning(self, "تنبيه", "يرجى ملء جميع الحقول!")
            return

        surah_clean_name = surah_name_full.replace("سورة ", "").replace("سورة", "").strip()

        expected_img_dir = os.path.join("Data", s_name, surah_clean_name)
        expected_img_path = os.path.join(expected_img_dir, f"{surah_clean_name}.png")
        expected_js_path = os.path.join(expected_img_dir, f"{surah_clean_name}.js")
        
        if not os.path.exists(expected_img_path):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("الصورة مش موجودة يا فنان!")
            msg.setText("لازم تختار أو تصمم صورة للسورة الأول .\nممكن تعمل الصورة بتصميم توحفه من 'هنا'.")
            msg.setStyleSheet("""
                QMessageBox { background-color: #313244; } 
                QLabel { color: #cdd6f4; font-size: 14px; font-weight: bold; } 
                QPushButton { background-color: #89b4fa; color: #11111b; padding: 6px; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #b4befe; }
            """)
            
            btn_make_img = msg.addButton("روح لـ 'هنا' (صانع الصور)", QMessageBox.ActionRole)
            btn_cancel = msg.addButton("إلغاء الإضافة دلوقتي", QMessageBox.RejectRole)
            
            msg.exec()
            
            if msg.clickedButton() == btn_make_img:
                self.tabs.setCurrentIndex(3) 
            return

        if not os.path.exists(expected_js_path):
            os.makedirs(expected_img_dir, exist_ok=True)
            initial_js_content = f"""// Data/{s_name}/{surah_clean_name}/{surah_clean_name}.js
window.currentSurahVerses = [
    // ضيف الآيات بتاعتك هنا باستخدام صفحة التزامن (API جامعة الملك فهد)
];
"""
            with open(expected_js_path, 'w', encoding='utf-8') as js_file:
                js_file.write(initial_js_content)

        content = self.read_file()
        
        search_str = f'id: "{s_id}"'
        if search_str not in content:
            return
            
        parts = content.split(search_str, 1)
        
        next_sheikh_idx = parts[1].find('id: "')
        sheikh_block = parts[1][:next_sheikh_idx] if next_sheikh_idx != -1 else parts[1]
        
        if f'id: "{surah_id}"' in sheikh_block:
            QMessageBox.warning(self, "تنبيه", f"السورة ({surah_name_full}) موجودة بالفعل لهذا الشيخ!")
            return

        surah_index = parts[1].find("surahs: [")
        
        if surah_index == -1:
            QMessageBox.critical(self, "خطأ", "لم يتم العثور على مصفوفة السور لهذا الشيخ!")
            return
            
        insert_pos = surah_index + len("surahs: [")
        
        new_surah = f"""
            {{
                id: "{surah_id}",
                name: "{surah_name_full}",
                audioUrl: "{audio_url}",
                jsFile: "Data/{s_name}/{surah_clean_name}/{surah_clean_name}.js",
                image: "Data/{s_name}/{surah_clean_name}/{surah_clean_name}.png"
            }},"""
            
        new_part2 = parts[1][:insert_pos] + new_surah + parts[1][insert_pos:]
        content = parts[0] + search_str + new_part2
        content = re.sub(r',\s*]', '\n        ]', content)
        self.write_file(content)
        
        msg_text = f"تم إضافة كود {surah_name_full} لملف cons.js بنجاح!"
        if not os.path.exists(expected_js_path):
             msg_text += f"\nوتم إنشاء ملف: {surah_clean_name}.js"
        else:
             msg_text += f"\n(ملف {surah_clean_name}.js كان موجود بالفعل أو تم إنشاؤه)"
             
        QMessageBox.information(self, "نجاح", msg_text + "\n(تم أخذ نسخة احتياطية للملف الأصلي)")
        self.surah_url_input.clear()
        self.update_surahs_dropdown() 

    def update_maker_surahs(self):
        self.combo_maker_surahs.clear()
        for en, ar in self.surahs_data:
            self.combo_maker_surahs.addItem(ar, en)

    def choose_bg_color(self):
        dialog = QColorDialog(self.bg_color, self)
        dialog.setWindowTitle("اختر لون الخلفية")
        dialog.currentColorChanged.connect(self.update_bg_color_live)
        dialog.exec()

    def update_bg_color_live(self, color):
        if color.isValid(): 
            self.bg_color = color
            self.generate_image(preview_only=True)

    def choose_text_color(self):
        dialog = QColorDialog(self.text_color, self)
        dialog.setWindowTitle("اختر لون النص")
        dialog.currentColorChanged.connect(self.update_text_color_live)
        dialog.exec()

    def update_text_color_live(self, color):
        if color.isValid(): 
            self.text_color = color
            self.generate_image(preview_only=True)

    def choose_cover_color(self):
        dialog = QColorDialog(self.cover_color, self)
        dialog.setWindowTitle("اختر لون الغلاف")
        dialog.currentColorChanged.connect(self.update_cover_color_live)
        dialog.exec()

    def update_cover_color_live(self, color):
        if color.isValid(): 
            self.cover_color = color
            self.generate_image(preview_only=True)

    def toggle_custom_colors(self, checked):
        self.custom_colors_widget.setVisible(checked)

    def load_themes(self):
        themes_dir = os.path.join("Data", "cons_themes")
        themes_file = os.path.join(themes_dir, "themes.json")
        self.themes_data = {}
        if os.path.exists(themes_file):
            try:
                with open(themes_file, 'r', encoding='utf-8') as f:
                    self.themes_data = json.load(f)
                for t_name in self.themes_data.keys():
                    self.combo_themes.addItem(t_name, t_name)
            except Exception:
                pass

    def apply_theme(self):
        theme_name = self.combo_themes.currentData()
        if theme_name and theme_name in self.themes_data:
            theme = self.themes_data[theme_name]
            self.bg_color = QColor(theme.get("bg_color", "#1e1e2e"))
            self.text_color = QColor(theme.get("text_color", "#cdd6f4"))
            self.cover_color = QColor(theme.get("cover_color", "#313244"))
            self.generate_image(preview_only=True)

    def generate_image(self, preview_only=False):
        if self.combo_maker_sheikhs.count() == 0 or self.combo_maker_surahs.count() == 0:
            if not preview_only:
                QMessageBox.warning(self, "تنبيه", "تأكد من اختيار الشيخ والسورة!")
            return
            
        s_name = self.combo_maker_sheikhs.currentText()
        surah_name = self.combo_maker_surahs.currentText()
        
        sheikh_img_path = f"Data/{s_name}/shiekh.png"
        if not os.path.exists(sheikh_img_path) and not preview_only:
            QMessageBox.critical(self, "خطأ", f"صورة الشيخ الأساسية مش موجودة في المسار:\n{sheikh_img_path}")
            return
            
        if not preview_only:
            reply = QMessageBox.question(self, 'تأكيد الإنشاء', f"هل أنت متأكد من إنشاء وحفظ صورة سورة {surah_name}؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.No:
                return
            
        width, height = 800, 250
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, 25, 25)
        painter.fillPath(path, QBrush(self.bg_color))
        
        circle_radius = 85
        circle_x = width - (circle_radius * 2) - 40
        circle_y = (height - (circle_radius * 2)) // 2
        
        painter.setBrush(QBrush(getattr(self, 'cover_color', QColor("#313244"))))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(circle_x, circle_y, circle_radius*2, circle_radius*2)
        
        if os.path.exists(sheikh_img_path):
            with open(sheikh_img_path, 'rb') as f:
                img_data = f.read()
            shiekh_pixmap = QPixmap()
            shiekh_pixmap.loadFromData(img_data)
            
            if not shiekh_pixmap.isNull():
                shiekh_pixmap = shiekh_pixmap.scaled(circle_radius*2, circle_radius*2, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                painter.save()
                clip_path = QPainterPath()
                clip_path.addEllipse(circle_x, circle_y, circle_radius*2, circle_radius*2)
                painter.setClipPath(clip_path)
                painter.drawPixmap(circle_x, circle_y, shiekh_pixmap)
                painter.restore()

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.text_color, 4))
        painter.drawEllipse(circle_x, circle_y, circle_radius*2, circle_radius*2)
        
        painter.setPen(QPen(self.text_color))
        selected_font = self.combo_fonts.currentText() if hasattr(self, 'combo_fonts') and self.combo_fonts.count() > 0 else "Amiri Quran"
        font = QFont(selected_font, 48, QFont.Bold)
        painter.setFont(font)
        
        text_rect = QRect(40, 0, width - (circle_radius*2) - 120, height)
        display_name = surah_name if "سورة" in surah_name else f"سورة {surah_name}"
        painter.drawText(text_rect, Qt.AlignCenter, display_name)
        
        painter.end() 
        
        scaled_pixmap = pixmap.scaled(self.preview_label.width() - 20, self.preview_label.height() - 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)
        
        if preview_only:
            return
            
        surah_clean_name = surah_name.replace("سورة ", "").replace("سورة", "").strip()
        save_dir = os.path.join("Data", s_name, surah_clean_name)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{surah_clean_name}.png")
        
        pixmap.save(save_path, "PNG")
        QMessageBox.information(self, "عاش يا فنان", f"تم تصميم الصورة بنجاح وحفظها في:\n{save_path}")

    def update_sync_surahs(self):
        self.combo_sync_surahs.clear()
        for en, ar in self.surahs_data:
            self.combo_sync_surahs.addItem(ar, en)

    def fetch_verses(self):
        surah_idx = self.combo_sync_surahs.currentIndex()
        if surah_idx < 0: return
        surah_number = surah_idx + 1
        
        try:
            url = f"https://api.alquran.cloud/v1/surah/{surah_number}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            ayahs = data['data']['ayahs']
            self.list_verses.clear()
            self.verses_data = []
            
            if surah_number not in [1, 9] and ayahs:
                first_text = ayahs[0]['text']
                bismillah = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
                if first_text.startswith(bismillah):
                    v_id_b = len(self.verses_data)
                    self.verses_data.append({"id": v_id_b, "text": bismillah, "start": 0.0, "end": 0.0, "type": "bismillah"})
                    self.list_verses.addItem(QListWidgetItem(f"[0.0 - 0.0] {bismillah}"))
                    
                    cleaned_first_text = first_text.replace(bismillah, "").strip()
                    ayahs[0] = {'text': cleaned_first_text}

            for ayah in ayahs:
                text = ayah['text']
                if not text:
                    continue
                v_id = len(self.verses_data)
                self.verses_data.append({"id": v_id, "text": text, "start": 0.0, "end": 0.0, "type": "aya"})
                self.list_verses.addItem(QListWidgetItem(f"[0.0 - 0.0] {text}"))
                
            QMessageBox.information(self, "نجاح", "تم جلب الآيات! اضغط مرتين على أي آية لتحديد وقت البداية والنهاية.")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء جلب الآيات:\n{str(e)}")

    def set_verse_timing(self, item):
        row = self.list_verses.row(item)
        verse = self.verses_data[row]
        
        start_time, ok1 = QInputDialog.getDouble(self, "وقت البداية", f"أدخل وقت البداية (بالثواني) للآية {row}:", verse['start'], 0, 10000, 2)
        if not ok1: return
        
        end_time, ok2 = QInputDialog.getDouble(self, "وقت النهاية", f"أدخل وقت النهاية (بالثواني) للآية {row}:", verse['end'] if verse['end'] > 0 else start_time + 3, 0, 10000, 2)
        if not ok2: return
        
        verse['start'] = start_time
        verse['end'] = end_time
        item.setText(f"[{start_time} - {end_time}] {verse['text']}")
        
        if row + 1 < self.list_verses.count():
            self.list_verses.setCurrentRow(row + 1)

    def save_sync_file(self):
        if not self.verses_data:
            QMessageBox.warning(self, "تنبيه", "لا توجد آيات محفوظة! قم بجلب الآيات أولاً.")
            return
            
        s_name = self.combo_sync_sheikhs.currentText()
        surah_name_full = self.combo_sync_surahs.currentText()
        surah_clean_name = surah_name_full.replace("سورة ", "").replace("سورة", "").strip()
        
        save_dir = os.path.join("Data", s_name, surah_clean_name)
        os.makedirs(save_dir, exist_ok=True)
        js_path = os.path.join(save_dir, f"{surah_clean_name}.js")
        
        js_content = f"// {js_path.replace(os.sep, '/')}\nwindow.currentSurahVerses = [\n"
        
        for v in self.verses_data:
            text = v['text'].replace('"', '\\"').replace('\n', ' ').replace('\r', '').strip()
            js_content += f"    {{ id: {v['id']}, start_time: {v['start']}, end_time: {v['end']}, text: \"{text}\", type: \"{v['type']}\" }},\n"
            
        js_content = js_content.rstrip(",\n") + "\n];\n"
        
        try:
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
            QMessageBox.information(self, "عاش يا فنان", f"تم إنشاء ملف السكريبت بنجاح في:\n{js_path}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الملف:\n{str(e)}")

if __name__ == "__main__":
    os.environ["QT_LOGGING_RULES"] = "qt.multimedia.*=false"
    app = QApplication(sys.argv)
    
    font = QFont("Segoe UI", 11)
    app.setFont(font)
    
    app.setStyleSheet("""
        QWidget { background-color: #1e1e2e; color: #cdd6f4; }
        
        QLineEdit, QComboBox, QSpinBox { 
            background-color: #313244; border: 2px solid #45475a; 
            border-radius: 8px; padding: 8px; color: #cdd6f4; 
        }
        QLineEdit:hover, QComboBox:hover, QSpinBox:hover { border: 2px solid #89b4fa; }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #cba6f7; background-color: #181825; }
        
        QPushButton { 
            background-color: #89b4fa; color: #11111b; 
            font-weight: bold; border-radius: 8px; padding: 10px; 
            border: 2px solid transparent;
        }
        QPushButton:hover { 
            background-color: #b4befe; border: 2px solid #cdd6f4; 
        }
        QPushButton:pressed { 
            background-color: #74c7ec; border: 2px solid #11111b; 
        }
        
        QTabWidget::pane { 
            border: 2px solid #89b4fa; border-radius: 8px; top: -2px; 
            background-color: #181825;
        }
        QTabBar::tab { 
            background: #313244; padding: 12px 25px; margin-left: 4px; 
            border-top-left-radius: 10px; border-top-right-radius: 10px;
            color: #a6adc8; font-weight: bold;
            border: 2px solid transparent; border-bottom: none;
        }
        QTabBar::tab:hover { 
            background: #45475a; color: #cdd6f4; 
            border: 2px solid #b4befe; border-bottom: none;
        }
        QTabBar::tab:selected { 
            background: #181825; color: #89b4fa; 
            border: 2px solid #89b4fa; border-bottom: none;
        }
    """)
    
    window = DatabaseManager()
    window.show()
    sys.exit(app.exec())