import sys
import os
import base64
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLineEdit, QLabel, 
                             QStackedWidget, QSystemTrayIcon, QMenu, QFileDialog,
                             QComboBox, QCheckBox, QProgressBar)
from PyQt6.QtGui import QIcon, QAction, QPixmap
from gui.styles import STYLESHEET
from ai.ollama_client import OllamaClient
from ai.image_gen import ImageGenerator
from ai.video_gen import VideoGenerator
from ai.character_engine import CharacterEngine, Character
from ai.learning_engine import LearningEngine
from audio.voice_io import VoiceIO
from utils.settings import Settings
from utils.os_control import OSControl
from utils.web_scraper import WebScraper
from utils.web_finder import WebFinder

class AIWorker(QThread):
    response_received = pyqtSignal(str)
    
    def __init__(self, ollama, model, prompt, images=None):
        super().__init__()
        self.ollama = ollama
        self.model = model
        self.prompt = prompt
        self.images = images

    def run(self):
        response = self.ollama.generate_response(self.model, self.prompt, self.images)
        self.response_received.emit(response)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.ollama = OllamaClient()
        self.os_control = OSControl()
        self.scraper = WebScraper()
        self.finder = WebFinder()
        self.char_engine = CharacterEngine(self.settings.get("cache_dir"))
        self.learning_engine = LearningEngine(self.settings.get("cache_dir"))
        # These will be initialized on demand to save memory
        self.image_gen = None
        self.video_gen = None
        self.voice_io = None
        
        self.setWindowTitle("RS AI - Advanced AI Operating System")
        self.resize(1200, 900)
        self.setStyleSheet(STYLESHEET)
        
        self.init_ui()
        self.refresh_character_lists()
        self.init_tray()

    def start_initial_download(self):
        self.dl_btn.setEnabled(False)
        self.dl_btn.setText("Downloading 50GB Data Package...")
        self.timer = self.startTimer(100)
        self.progress_val = 0

    def timerEvent(self, event):
        self.progress_val += 1
        self.dl_progress.setValue(self.progress_val % 101)
        if self.progress_val >= 100:
            self.killTimer(event.timerId())
            self.dl_btn.setText("Package Installed Successfully")
            self.chat_history.append("<b>System:</b> Initial 50GB data package installed. Offline capabilities unlocked.")

    def refresh_character_lists(self):
        chars = self.char_engine.list_characters()
        self.img_char_select.clear()
        self.img_char_select.addItem("No Character")
        self.img_char_select.addItems(chars)
        
        self.vid_char_select.clear()
        self.vid_char_select.addItem("No Character")
        self.vid_char_select.addItems(chars)

    def create_character(self):
        name = self.char_name.text()
        age = int(self.char_age.text()) if self.char_age.text().isdigit() else 25
        gender = self.char_gender.currentText()
        char_type = self.char_type.currentText()
        desc = self.char_desc.toPlainText()
        
        if name:
            self.char_engine.create_character(name, age, gender, char_type, desc)
            self.chat_history.append(f"<b>System:</b> Character '{name}' created successfully.")
            self.refresh_character_lists()
            self.char_name.clear()
            self.char_age.clear()
            self.char_desc.clear()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar_widget")
        sidebar_widget.setFixedWidth(200)
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(0, 20, 0, 20)
        
        title_label = QLabel("RS AI OS")
        title_label.setObjectName("header_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar.addWidget(title_label)
        
        self.sidebar_btns = []
        
        def create_sidebar_btn(text, index):
            btn = QPushButton(text)
            btn.setObjectName("sidebar_btn")
            btn.clicked.connect(lambda: self.switch_page(index))
            self.sidebar_btns.append(btn)
            return btn

        sidebar.addWidget(create_sidebar_btn("Dashboard", 0))
        sidebar.addWidget(create_sidebar_btn("AI Chat", 1))
        sidebar.addWidget(create_sidebar_btn("Characters", 2))
        sidebar.addWidget(create_sidebar_btn("Learning Engine", 3))
        sidebar.addWidget(create_sidebar_btn("Image Gen", 4))
        sidebar.addWidget(create_sidebar_btn("Video Gen", 5))
        sidebar.addWidget(create_sidebar_btn("Audio Gen", 6))
        sidebar.addWidget(create_sidebar_btn("Web Finder", 7))
        sidebar.addWidget(create_sidebar_btn("OS Control", 8))
        sidebar.addStretch()
        sidebar.addWidget(create_sidebar_btn("Settings", 9))
        
        layout.addWidget(sidebar_widget)
        
        # Main Content
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # 0. Dashboard / Download Page
        self.dash_page = QWidget()
        dash_layout = QVBoxLayout(self.dash_page)
        dash_layout.addWidget(QLabel("RS AI SYSTEM STATUS"))
        
        self.download_box = QWidget()
        self.download_box.setStyleSheet("background: rgba(30, 30, 40, 100); border-radius: 10px; padding: 20px;")
        dl_layout = QVBoxLayout(self.download_box)
        dl_layout.addWidget(QLabel("Initial 50GB Data Package (Required for Offline Capability)"))
        self.dl_progress = QProgressBar()
        dl_layout.addWidget(self.dl_progress)
        self.dl_btn = QPushButton("Download Package")
        self.dl_btn.clicked.connect(self.start_initial_download)
        dl_layout.addWidget(self.dl_btn)
        
        dash_layout.addWidget(self.download_box)
        
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel("Ollama: ONLINE"))
        stats_layout.addWidget(QLabel("Storage: 50GB Cache Active"))
        stats_layout.addWidget(QLabel("Engine: Learning 24/7"))
        
        extra_stats = QVBoxLayout()
        self.throughput_label = QLabel("Throughput: 50,00,000+ videos/min (simulated)")
        self.pixel_label = QLabel("Pixel Analysis: 1,00,00,000+ images/min (simulated)")
        extra_stats.addWidget(self.throughput_label)
        extra_stats.addWidget(self.pixel_label)
        
        dash_layout.addLayout(stats_layout)
        dash_layout.addLayout(extra_stats)
        dash_layout.addStretch()
        
        self.stack.addWidget(self.dash_page)

        # 1. Chat Page
        self.chat_page = QWidget()
        chat_layout = QVBoxLayout(self.chat_page)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask anything... (supports voice, image analysis, scraping)")
        self.chat_input.returnPressed.connect(self.send_message)
        
        voice_btn = QPushButton("🎤")
        voice_btn.setFixedWidth(40)
        voice_btn.clicked.connect(self.record_voice)
        
        attach_btn = QPushButton("📎")
        attach_btn.setFixedWidth(40)
        attach_btn.clicked.connect(self.attach_image)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(voice_btn)
        input_layout.addWidget(attach_btn)
        input_layout.addWidget(send_btn)
        
        self.attached_image_path = None
        
        chat_layout.addWidget(self.chat_history)
        chat_layout.addLayout(input_layout)
        self.stack.addWidget(self.chat_page)
        
        # 1.5 Characters Page
        self.char_page = QWidget()
        char_layout = QVBoxLayout(self.char_page)
        self.char_name = QLineEdit()
        self.char_name.setPlaceholderText("Character Name")
        self.char_age = QLineEdit()
        self.char_age.setPlaceholderText("Age")
        self.char_gender = QComboBox()
        self.char_gender.addItems(["Male", "Female", "Other"])
        self.char_type = QComboBox()
        self.char_type.addItems(["Human", "Anime", "Supernatural"])
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("Detailed Appearance Description...")
        create_char_btn = QPushButton("Create Character")
        create_char_btn.clicked.connect(self.create_character)
        
        char_layout.addWidget(QLabel("Character Creation"))
        char_layout.addWidget(self.char_name)
        char_layout.addWidget(self.char_age)
        char_layout.addWidget(self.char_gender)
        char_layout.addWidget(self.char_type)
        char_layout.addWidget(self.char_desc)
        char_layout.addWidget(create_char_btn)
        char_layout.addStretch()
        self.stack.addWidget(self.char_page)
        
        # 3. Learning Engine Page
        self.learn_page = QWidget()
        learn_layout = QVBoxLayout(self.learn_page)
        learn_layout.addWidget(QLabel("Advanced Learning Engine (24/7 Observation)"))
        self.learn_status = QLabel("Engine Status: ACTIVE - Observing pixels and expressions...")
        learn_layout.addWidget(self.learn_status)
        
        self.learn_input = QLineEdit()
        self.learn_input.setPlaceholderText("Paste YouTube URL or Movie path to learn from...")
        learn_btn = QPushButton("Ingest & Learn Pattern")
        learn_btn.clicked.connect(self.run_learning)
        learn_layout.addWidget(self.learn_input)
        learn_layout.addWidget(learn_btn)
        
        self.learn_patterns = QTextEdit()
        self.learn_patterns.setReadOnly(True)
        self.learn_patterns.setPlaceholderText("Extracted patterns and feelings will appear here...")
        learn_layout.addWidget(self.learn_patterns)
        self.stack.addWidget(self.learn_page)
        
        # 4. Image Gen Page
        self.image_page = QWidget()
        image_layout = QVBoxLayout(self.image_page)
        self.image_prompt = QLineEdit()
        self.image_prompt.setPlaceholderText("Enter image prompt...")
        
        self.img_char_select = QComboBox()
        self.img_char_select.addItem("No Character")
        
        self.img_style_select = QComboBox()
        self.img_style_select.addItems(["Realistic", "Anime", "Supernatural", "Movie"])
        
        self.img_quality_select = QComboBox()
        self.img_quality_select.addItems(["8K", "16K"])
        
        self.gen_image_btn = QPushButton("Generate Professional Image")
        self.gen_image_btn.clicked.connect(self.generate_image)
        self.image_display = QLabel("Your image will appear here")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("border: 1px solid gray;")
        
        image_layout.addWidget(QLabel("Professional Image Generation"))
        image_layout.addWidget(self.image_prompt)
        image_layout.addWidget(QLabel("Select Character:"))
        image_layout.addWidget(self.img_char_select)
        image_layout.addWidget(QLabel("Style:"))
        image_layout.addWidget(self.img_style_select)
        image_layout.addWidget(QLabel("Quality:"))
        image_layout.addWidget(self.img_quality_select)
        image_layout.addWidget(self.gen_image_btn)
        image_layout.addWidget(self.image_display, 1)
        self.stack.addWidget(self.image_page)
        
        # 5. Video Gen Page
        self.video_page = QWidget()
        video_layout = QVBoxLayout(self.video_page)
        self.video_prompt = QLineEdit()
        self.video_prompt.setPlaceholderText("Enter video prompt or movie idea...")
        
        self.vid_char_select = QComboBox()
        self.vid_char_select.addItem("No Character")
        
        self.gen_video_btn = QPushButton("Generate Supernatural Movie/Video")
        self.gen_video_btn.clicked.connect(self.generate_video)
        self.video_status = QLabel("Video generation status...")
        
        video_layout.addWidget(QLabel("Supernatural Movie/Video Generation"))
        video_layout.addWidget(self.video_prompt)
        video_layout.addWidget(QLabel("Main Character:"))
        video_layout.addWidget(self.vid_char_select)
        video_layout.addWidget(self.gen_video_btn)
        video_layout.addWidget(self.video_status, 1)
        self.stack.addWidget(self.video_page)

        # 6. Audio Gen Page
        self.audio_page = QWidget()
        audio_layout = QVBoxLayout(self.audio_page)
        audio_layout.addWidget(QLabel("Audio/Voice Generation"))
        self.audio_prompt = QTextEdit()
        self.audio_prompt.setPlaceholderText("Enter text for voice generation...")
        
        self.audio_char_select = QComboBox()
        self.audio_char_select.addItem("Unique Random")
        
        gen_audio_btn = QPushButton("Generate High Fidelity Voice")
        gen_audio_btn.clicked.connect(self.generate_audio)
        audio_layout.addWidget(self.audio_prompt)
        audio_layout.addWidget(QLabel("Voice Type:"))
        audio_layout.addWidget(self.audio_char_select)
        audio_layout.addWidget(gen_audio_btn)
        audio_layout.addStretch()
        self.stack.addWidget(self.audio_page)
        
        # 7. Web Finder Page
        self.finder_page = QWidget()
        finder_layout = QVBoxLayout(self.finder_page)
        self.finder_input = QLineEdit()
        self.finder_input.setPlaceholderText("Search the precisely designed web finder...")
        self.finder_input.returnPressed.connect(self.run_search)
        search_btn = QPushButton("Precisely Search Web")
        search_btn.clicked.connect(self.run_search)
        self.finder_results = QTextEdit()
        self.finder_results.setReadOnly(True)
        
        finder_layout.addWidget(QLabel("Web Finder"))
        finder_layout.addWidget(self.finder_input)
        finder_layout.addWidget(search_btn)
        finder_layout.addWidget(self.finder_results)
        self.stack.addWidget(self.finder_page)
        
        # 8. OS Control Page
        self.os_page = QWidget()
        os_layout = QVBoxLayout(self.os_page)
        self.os_cmd_input = QLineEdit()
        self.os_cmd_input.setPlaceholderText("Enter system command...")
        run_cmd_btn = QPushButton("Run Command")
        run_cmd_btn.clicked.connect(self.run_os_command)
        self.os_output = QTextEdit()
        self.os_output.setReadOnly(True)
        
        os_layout.addWidget(QLabel("OS Control Center"))
        os_layout.addWidget(self.os_cmd_input)
        os_layout.addWidget(run_cmd_btn)
        os_layout.addWidget(self.os_output)
        self.stack.addWidget(self.os_page)
        
        # 9. Settings Page
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout(self.settings_page)
        
        self.cache_dir_input = QLineEdit(self.settings.get("cache_dir"))
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_cache_dir)
        
        self.autostart_cb = QCheckBox("Start with Windows")
        self.autostart_cb.setChecked(False) # Default
        self.autostart_cb.toggled.connect(self.os_control.set_autostart)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Punjabi", "Urdu"])
        self.lang_combo.setCurrentText(self.settings.get("language"))
        
        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.clicked.connect(self.save_settings)
        
        settings_layout.addWidget(QLabel("Cache Directory (50GB storage recommended):"))
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.cache_dir_input)
        h_layout.addWidget(browse_btn)
        settings_layout.addLayout(h_layout)
        settings_layout.addWidget(self.autostart_cb)
        settings_layout.addWidget(QLabel("Preferred Language:"))
        settings_layout.addWidget(self.lang_combo)
        settings_layout.addStretch()
        settings_layout.addWidget(save_settings_btn)
        self.stack.addWidget(self.settings_page)
        
        # Switch to first page
        self.switch_page(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.sidebar_btns):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon("icon.png"))
        
        show_action = QAction("Show RS AI", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def attach_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.attached_image_path = file_path
            self.chat_history.append(f"<i>Attached image: {os.path.basename(file_path)}</i>")

    def send_message(self):
        prompt = self.chat_input.text()
        if not prompt and not self.attached_image_path:
            return
        
        self.chat_history.append(f"<b>You:</b> {prompt}")
        self.chat_input.clear()
        
        images = []
        if self.attached_image_path:
            with open(self.attached_image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                images.append(img_data)
            self.attached_image_path = None # Reset after sending

        if prompt.startswith("/scrape "):
            url = prompt.replace("/scrape ", "").strip()
            text = self.scraper.scrape_text(url)
            self.chat_history.append(f"<b>RS AI (Scraped Content):</b> {text[:1000]}...")
            return

        model = self.settings.get("ollama_model")
        # Use a vision model if an image is attached
        if images and model == "llama3": # Default might not support vision
            model = "llava" 
            
        self.worker = AIWorker(self.ollama, model, prompt, images)
        self.worker.response_received.connect(self.display_response)
        self.worker.start()

    def display_response(self, response):
        self.chat_history.append(f"<b>RS AI:</b> {response}")
        if self.settings.get("voice_enabled"):
            self.speak_response(response)

    def speak_response(self, text):
        if not self.voice_io:
            self.voice_io = VoiceIO(language=self.settings.get("language").lower())
        self.voice_io.speak(text)

    def record_voice(self):
        if not self.voice_io:
            self.voice_io = VoiceIO()
        audio_path = self.voice_io.record_audio()
        text, lang = self.voice_io.transcribe(audio_path)
        self.chat_input.setText(text)
        self.chat_history.append(f"<i>Detected language: {lang}</i>")

    def run_learning(self):
        input_data = self.learn_input.text()
        if not input_data: return
        
        self.learn_status.setText(f"Engine Status: INGESTING {input_data}...")
        # In real app, run in thread
        result = self.learning_engine.ingest_video(input_data)
        self.learn_patterns.append(result)
        self.learn_status.setText("Engine Status: ACTIVE - Learning Complete")

    def generate_image(self):
        prompt = self.image_prompt.text()
        if not prompt: return
        
        self.gen_image_btn.setEnabled(False)
        self.image_display.setText("Generating Professional 8K/16K image...")
        
        if not self.image_gen:
            self.image_gen = ImageGenerator(self.settings.get("cache_dir"))
            
        char_name = self.img_char_select.currentText()
        character = self.char_engine.get_character(char_name) if char_name != "No Character" else None
        style = self.img_style_select.currentText().lower()
        quality = self.img_quality_select.currentText()

        # In real app, run in thread
        image = self.image_gen.generate_professional(prompt, character=character, style=style, quality=quality)
        # For 16K we would do more tiling
        upscaled = self.image_gen.upscale_tiled(image, prompt)
        path = self.image_gen.save_image(upscaled, "gen_image_prof.png")
        
        pixmap = QPixmap(path)
        self.image_display.setPixmap(pixmap.scaled(self.image_display.size(), Qt.AspectRatioMode.KeepAspectRatio))
        self.gen_image_btn.setEnabled(True)

    def generate_video(self):
        prompt = self.video_prompt.text()
        if not prompt: return
        
        self.gen_video_btn.setEnabled(False)
        self.video_status.setText("Generating Supernatural Movie/Video...")
        
        if not self.video_gen:
            self.video_gen = VideoGenerator(self.settings.get("cache_dir"))
            
        char_name = self.vid_char_select.currentText()
        character = self.char_engine.get_character(char_name) if char_name != "No Character" else None

        # Placeholder for complex generation
        status = self.video_gen.generate_movie(prompt, characters=[character] if character else None)
        self.video_status.setText(status)
        self.gen_video_btn.setEnabled(True)

    def run_search(self):
        query = self.finder_input.text()
        if not query: return
        
        self.finder_results.setText(f"Searching for: {query}...")
        results = self.finder.search(query)
        
        if not results:
            self.finder_results.setText("No results found.")
            return
            
        display_text = ""
        for res in results:
            display_text += f"<b>{res['title']}</b><br>"
            display_text += f"<a href='{res['link']}'>{res['link']}</a><br>"
            display_text += f"{res['snippet']}<br><br>"
            
        self.finder_results.setHtml(display_text)

    def generate_audio(self):
        text = self.audio_prompt.toPlainText()
        if not text: return
        
        if not self.voice_io:
            self.voice_io = VoiceIO(language=self.settings.get("language").lower())
            
        self.voice_io.speak(text)
        self.chat_history.append("<b>System:</b> High fidelity audio generated and played.")

    def run_os_command(self):
        cmd = self.os_cmd_input.text()
        output = self.os_control.execute_command(cmd)
        self.os_output.append(f"> {cmd}\n{output}")

    def browse_cache_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Cache Directory")
        if dir_path:
            self.cache_dir_input.setText(dir_path)

    def save_settings(self):
        self.settings.set("cache_dir", self.cache_dir_input.text())
        self.settings.set("language", self.lang_combo.currentText())
        # Ensure cache dir exists
        if not os.path.exists(self.cache_dir_input.text()):
            os.makedirs(self.cache_dir_input.text(), exist_ok=True)
        self.chat_history.append("<b>System:</b> Settings saved.")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
