import json
import os
import sys
import ctypes
import time
import shutil
import psutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar, QMessageBox, QHBoxLayout,
    QSizePolicy, QGraphicsDropShadowEffect, QFrame, QSizeGrip,
    QSlider, QComboBox, QMenu
)
from PyQt5.QtGui import (
    QIcon, QColor, QCursor, QFont,
    QPainter, QPixmap, QLinearGradient, QBrush,
    QPen, QImage
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QPoint,
    QRect, QEasingCurve, QParallelAnimationGroup,
    QSize, QTimer, QEvent, pyqtSignal
)
try:
    from PyQt5.QtWinExtras import QtWin
    HAS_WINEXTRAS = True
except ImportError:
    HAS_WINEXTRAS = False

# Убираем проблемные настройки окружения
os.environ.pop("QT_QUICK_BACKEND", None)
os.environ.pop("QT_QPA_PLATFORM", None)
os.environ.pop("QT_LOGGING_RULES", None)

class ModernTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(10)
        
        self.title = QLabel("Drk multi lang v1.0")
        self.title.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 600;
            font-family: Arial, sans-serif;
        """)
        
        self.about_btn = QPushButton(self.parent.translate("About"))
        self.about_btn.setFixedSize(100, 28)
        self.about_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border-radius: 4px;
                font-size: 12px;
                font-family: Arial, sans-serif;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        self.about_btn.clicked.connect(self.parent.show_modern_description)
        
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.minimize_btn = QPushButton("—")
        self.close_btn = QPushButton("✕")
        
        for btn in [self.minimize_btn, self.close_btn]:
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    border-radius: 7px;
                    font-size: 14px;
                    font-family: Arial, sans-serif;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background: rgba(255, 255, 255, 0.2);
                }
            """)
        
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.close_btn.clicked.connect(self.parent.close)
        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.about_btn)
        self.layout.addWidget(self.spacer)
        self.layout.addWidget(self.minimize_btn)
        self.layout.addWidget(self.close_btn)
        
        self.drag_pos = None
        self.drag_window_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            self.drag_window_pos = self.parent.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            new_pos = self.drag_window_pos + (event.globalPos() - self.drag_pos)
            self.parent.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        self.drag_window_pos = None
        super().mouseReleaseEvent(event)

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            background-color: rgba(30, 35, 40, 180);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self._bg_color = QColor(0, 120, 215)
        self._text_color = QColor(255, 255, 255)
        
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setColor(QColor(0, 150, 255, 0))
        self.shadow_effect.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow_effect)
        
        self.update_styles()
        
    def update_styles(self):
        style = f"""
        QPushButton {{
            background-color: {self._bg_color.name()};
            color: {self._text_color.name()};
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
            font-size: 12px;
            font-family: Arial, sans-serif;
            border: none;
            text-align: center;
        }}
        QPushButton:hover {{
            background-color: {self._bg_color.lighter(110).name()};
        }}
        QPushButton:pressed {{
            background-color: {self._bg_color.darker(120).name()};
        }}
        """
        self.setStyleSheet(style)
    
    def enterEvent(self, event):
        self._animate_button(QColor(0, 140, 255), QColor(0, 150, 255, 100))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._animate_button(QColor(0, 120, 215), QColor(0, 150, 255, 0))
        super().leaveEvent(event)
    
    def _animate_button(self, bg_color, shadow_color):
        self._bg_color = bg_color
        self.shadow_effect.setColor(shadow_color)
        self.update_styles()

class LanguageComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(36)
        self.setMinimumWidth(120)
        
        self.setStyleSheet("""
            QComboBox {
                background-color: rgba(0, 120, 215, 150);
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 12px;
                font-family: Arial, sans-serif;
                border: none;
            }
            QComboBox:hover {
                background-color: rgba(0, 120, 215, 200);
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(30, 35, 40, 220);
                color: white;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 8px;
                selection-background-color: rgba(0, 120, 215, 150);
                outline: none;
            }
        """)
        
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setColor(QColor(0, 150, 255, 0))
        self.shadow_effect.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow_effect)
        
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hidePopup)
        
        self.addItem("English", "En")
        self.addItem("Русский", "Ru")
        self.addItem("Українська", "Ua")
        self.addItem("Беларуская", "By")
        self.addItem("Қазақша", "Kz")
        self.addItem("Polski", "Pl")         
        self.addItem("Čeština", "Cs")       
        self.addItem("Slovenčina", "Sk")     
        self.addItem("Български", "Bg")       
        self.addItem("Српски", "Sr")         
        self.addItem("Հայերեն", "Hy")        
        self.addItem("ქართული", "Ka")        
        self.addItem("Română", "Ro")         
        self.addItem("Latviešu", "Lv")       
        self.addItem("Lietuvių", "Lt")       
        self.addItem("Eesti", "Et")          
        self.addItem("Türkçe", "Tr")         
        self.addItem("Deutsch", "De")        
        self.addItem("Français", "Fr")        
        self.addItem("Español", "Es")        
        self.setCurrentIndex(0)
        
        self.view().window().setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self.view().window().setAttribute(Qt.WA_TranslucentBackground)
        
    def enterEvent(self, event):
        self.shadow_effect.setColor(QColor(0, 150, 255, 100))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.shadow_effect.setColor(QColor(0, 150, 255, 0))
        super().leaveEvent(event)
    
    def showPopup(self):
        super().showPopup()
        self.hide_timer.start(50000)
    
    def hidePopup(self):
        if self.hide_timer.isActive():
            self.hide_timer.stop()
        super().hidePopup()
    
    def mousePressEvent(self, event):
        if self.hide_timer.isActive():
            self.hide_timer.stop()
        super().mousePressEvent(event)

class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(8)
        self.setTextVisible(False)
        self.setRange(0, 100)
        self.setValue(0)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        bg_rect = QRect(0, 0, self.width(), self.height())
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 35, 40))
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        progress = int((self.value() / (self.maximum() - self.minimum())) * self.width())
        progress_rect = QRect(0, 0, progress, self.height())
        
        gradient = QLinearGradient(0, 0, progress, 0)
        gradient.setColorAt(0, QColor(0, 180, 255))
        gradient.setColorAt(1, QColor(0, 120, 215))
        
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(progress_rect, 4, 4)
        
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 8))
        text = f"{self.value()}%"
        text_rect = painter.fontMetrics().boundingRect(text)
        text_x = (self.width() - text_rect.width()) // 2
        text_y = (self.height() + text_rect.height()) // 2 - 2
        painter.drawText(text_x, text_y, text)

class AboutDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(self.parent.translate("About"))
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 520)
        
        self.background = QWidget(self)
        self.background.setGeometry(self.rect())
        self.background.setStyleSheet("""
            background-color: rgba(30, 35, 40, 220);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        title = QLabel("Drk multi lang v1.0")
        title.setStyleSheet("""
            color: #00b4ff;
            font-size: 20px;
            font-weight: 600;
            font-family: Arial, sans-serif;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel(self.parent.translate("AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS"))
        subtitle.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-family: Arial, sans-serif;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        version = QLabel(self.parent.translate("MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9"))
        version.setStyleSheet("""
            color: #aaaaaa;
            font-size: 12px;
            font-family: Arial, sans-serif;
        """)
        version.setAlignment(Qt.AlignCenter)
        
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setStyleSheet("background: rgba(255,255,255,0.1);")
        
        info_text = QLabel(f"""
        <p style="font-size:13px; color:#ffffff; margin-bottom:8px; font-family:Arial,sans-serif;">
            <b>Drk multi lang</b> - {self.parent.translate("program for automatic translation")}<br>
            {self.parent.translate("of Darmoshark mouse drivers into multiple languages")}.              
        </p>
        <p style="font-size:13px; color:#ffffff; margin-bottom:8px; font-family:Arial,sans-serif;">
            ✔ {self.parent.translate("Fully automatic process")}<br>
            ✔ {self.parent.translate("Security: files remain on your PC")}<br>
            ✔ {self.parent.translate("Ability to roll back to default settings")}
        </p>
        <p style="font-size:13px; color:#ffffff; margin-bottom:8px; font-family:Arial,sans-serif;">
            <b>{self.parent.translate("IMPORTANT:")}</b> {self.parent.translate("The program DOES NOT collect or send your data!")}<br>
            {self.parent.translate("All files are stored strictly on your computer.")}
        </p>
        <p style="font-size:13px; color:#ffffff; margin-bottom:8px; font-family:Arial,sans-serif;">
            • {self.parent.translate("DRIVER UPDATES:")} 
            <a href="https://docs.google.com/spreadsheets/d/1XSOc279P7e8JUpseJtwDvjeJQalX5SEadXpr1AYCQM0/edit?gid=0#gid=0" 
               style="color:#00b4ff; text-decoration:none;">
               {self.parent.translate("Google Sheet")}
            </a>
        </p>
        <p style="font-size:13px; color:#ffffff; margin-bottom:8px; font-family:Arial,sans-serif;">
            • {self.parent.translate("OFFICIAL WEBSITE:")} 
            <a href="https://russifier-drk.ru/" 
               style="color:#00b4ff; text-decoration:none;">
               russifier-drk.ru
            </a>
        </p>
        """)
        info_text.setOpenExternalLinks(True)
        
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background: rgba(255,255,255,0.1);")
        
        dev_info = QLabel(f"""
        <p style="font-size:13px; color:#ffffff; margin-bottom:5px; font-family:Arial,sans-serif;">
            <b>{self.parent.translate("DEVELOPER:")}</b> Saylont (Xanixsl на GitHub)
        </p>
        <p style="font-size:13px; color:#ffffff; margin-bottom:5px; font-family:Arial,sans-serif;">
            <b>{self.parent.translate("SUPPORT THE DEVELOPER:")}</b>
        </p>
        <p style="font-size:13px; color:#ffffff; margin-bottom:5px; font-family:Arial,sans-serif;">
            • <a href="https://www.donationalerts.com/r/saylont" 
               style="color:#00b4ff; text-decoration:none;">
               DonationAlerts
            </a>
        </p>
        <p style="font-size:13px; color:#ffffff; font-family:Arial,sans-serif;">
            • <a href="https://boosty.to/saylontoff/donate" 
               style="color:#00b4ff; text-decoration:none;">
               Boosty
            </a>
        </p>
        <p style="font-size:13px; color:#ffffff; margin-top:10px; font-family:Arial,sans-serif;">
            {self.parent.translate("This is the multi-language version of Russifier Drk v2.0")}<br>
            {self.parent.translate("Original version (Russian only) available on")} 
            <a href="https://github.com/Xanixsl/Russifier-Drk/tree/main" 
               style="color:#00b4ff; text-decoration:none;">
               GitHub
            </a>
        </p>
        """)
        dev_info.setOpenExternalLinks(True)
        
        close_btn = QPushButton(self.parent.translate("Close"))
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 120, 215, 150);
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-family: Arial, sans-serif;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 215, 200);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(version)
        layout.addWidget(separator1)
        layout.addWidget(info_text)
        layout.addWidget(separator2)
        layout.addWidget(dev_info)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        self.drag_pos = None
        self.drag_window_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            self.drag_window_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            new_pos = self.drag_window_pos + (event.globalPos() - self.drag_pos)
            self.move(new_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        self.drag_window_pos = None
        super().mouseReleaseEvent(event)

    def showEvent(self, event):
        parent_widget = self.parentWidget()  # Получаем родительский виджет
        if parent_widget:  # Проверяем, что он существуе
            self.move(
                parent_widget.x() + (parent_widget.width() - self.width()) // 2,
                parent_widget.y() + (parent_widget.height() - self.height()) // 2
            )
        super().showEvent(event)

class ModernRusificatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("ModernRusificator")
        self.current_language = "En"
        self.translations = {
        "En": {
            "About": "About",
            "Blur Intensity": "Blur Intensity",
            "Language": "Language",
            "Ready for translation": "Ready for translation",
            "Start": "START",
            "Rollback Changes": "ROLLBACK CHANGES",
            "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS",
            "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9",
            "program for automatic translation": "program for automatic translation",
            "of Darmoshark mouse drivers into multiple languages": "of Darmoshark mouse drivers into multiple languages",
            "Fully automatic process": "Fully automatic process",
            "Security: files remain on your PC": "Security: files remain on your PC",
            "Ability to roll back to default settings": "Ability to roll back to default settings",
            "IMPORTANT:": "IMPORTANT:",
            "The program DOES NOT collect or send your data!": "The program DOES NOT collect or send your data!",
            "All files are stored strictly on your computer.": "All files are stored strictly on your computer.",
            "DRIVER UPDATES:": "DRIVER UPDATES:",
            "Google Sheet": "Google Sheet",
            "OFFICIAL WEBSITE:": "OFFICIAL WEBSITE:",
            "DEVELOPER:": "DEVELOPER:",
            "SUPPORT THE DEVELOPER:": "SUPPORT THE DEVELOPER:",
            "Close": "Close",
            "This is the multi-language version of Russifier Drk v2.0": "This is the multi-language version of Russifier Drk v2.0",
            "Original version (Russian only) available on": "Original version (Russian only) available on",
            "Searching for application...": "Searching for application...",
            "Success. Closing application...": "Success. Closing application...",
            "Processing language files...": "Processing language files...",
            "Launching application...": "Launching application...",
            "Process completed!": "Process completed!",
            "Application not found!": "Application not found!",
            "Rolling back changes...": "Rolling back changes...",
            "Removing translation files...": "Removing translation files...",
            "Rollback completed!": "Rollback completed!",
            "Loading cached paths...": "Loading cached paths...",
            "Cached paths:": "Cached paths:",
            "Found in cache:": "Found in cache:",
            "Available drives:": "Available drives:",
            "Searching in:": "Searching in:",
            "File found:": "File found:",
            "Checking cache file existence:": "Checking cache file existence:",
            "Cache file found. Loading...": "Cache file found. Loading...",
            "Loaded paths from cache:": "Loaded paths from cache:",
            "Error reading cache file:": "Error reading cache file:",
            "Cache file not found.": "Cache file not found.",
            "Saving path to cache:": "Saving path to cache:",
            "Path saved successfully.": "Path saved successfully.",
            "Error saving path:": "Error saving path:",
            "Creating new cache file:": "Creating new cache file:",
            "Cache file created successfully.": "Cache file created successfully.",
            "Error creating cache file:": "Error creating cache file:",
            "Terminating process:": "Terminating process:",
            "Process terminated successfully:": "Process terminated successfully:",
            "Error terminating process:": "Error terminating process:",
            "Processing files in:": "Processing files in:",
            "Checking directory:": "Checking directory:",
            "Reading libraries...": "Reading libraries...",
            "Library read successfully.": "Library read successfully.",
            "ERROR: Library file not found:": "ERROR: Library file not found:",
            "Please make sure the library file is in the same folder as the program": "Please make sure the library file is in the same folder as the program",
            "Error reading library. x0001": "Error reading library. x0001",
            "No access to modify:": "No access to modify:",
            "File written:": "File written:",
            "Rolling back changes in:": "Rolling back changes in:",
            "Directory does not exist.": "Directory does not exist.",
            "Translation found in files:": "Translation found in files:",
            "File deleted:": "File deleted:",
            "File copied:": "File copied:",
            "File not found:": "File not found:",
            "Launching application:": "Launching application:",
            "Application launched successfully.": "Application launched successfully.",
            "Error launching application:": "Error launching application:",
            "Getting list of available drives...": "Getting list of available drives...",
            "Drives found:": "Drives found:"
        },
        "Pl": { 
        "About": "O programie",
        "Blur Intensity": "Intensywność rozmycia",
        "Language": "Język",
        "Ready for translation": "Gotowy do tłumaczenia",
        "Start": "ROZPOCZNIJ",
        "Rollback Changes": "COFNIJ ZMIANY",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "AUTOMATYCZNE TŁUMACZENIE STEROWNIKÓW DARMOSHARK",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELE M3/M3s/N3 | WERSJE 1.6.5 - 1.8.2.9",
        "program for automatic translation": "program do automatycznego tłumaczenia",
        "of Darmoshark mouse drivers into multiple languages": "sterowników myszy Darmoshark na wiele języków",
        "Fully automatic process": "W pełni automatyczny proces",
        "Security: files remain on your PC": "Bezpieczeństwo: pliki pozostają na Twoim komputerze",
        "Ability to roll back to default settings": "Możliwość przywrócenia ustawień domyślnych",
        "IMPORTANT:": "WAŻNE:",
        "The program DOES NOT collect or send your data!": "Program NIE gromadzi i NIE wysyła Twoich danych!",
        "All files are stored strictly on your computer.": "Wszystkie pliki są przechowywane wyłącznie na Twoim komputerze.",
        "DRIVER UPDATES:": "AKTUALIZACJE STEROWNIKÓW:",
        "Google Sheet": "Arkusz Google",
        "OFFICIAL WEBSITE:": "OFICJALNA STRONA:",
        "DEVELOPER:": "DEWELOPER:",
        "SUPPORT THE DEVELOPER:": "WESPRZYJ DEWELOPERA:",
        "Close": "Zamknij",
        "This is the multi-language version of Russifier Drk v2.0": "To jest wielojęzyczna wersja Russifier Drk v2.0",
        "Original version (Russian only) available on": "Oryginalna wersja (tylko rosyjska) dostępna na",
        "Searching for application...": "Wyszukiwanie aplikacji...",
        "Success. Closing application...": "Sukces. Zamykanie aplikacji...",
        "Processing language files...": "Przetwarzanie plików językowych...",
        "Launching application...": "Uruchamianie aplikacji...",
        "Process completed!": "Proces zakończony!",
        "Application not found!": "Aplikacja nie znaleziona!",
        "Rolling back changes...": "Cofanie zmian...",
        "Removing translation files...": "Usuwanie plików tłumaczenia...",
        "Rollback completed!": "Cofnięcie zakończone!",
        "Loading cached paths...": "Ładowanie zapisanych ścieżek...",
        "Cached paths:": "Zapisane ścieżki:",
        "Found in cache:": "Znaleziono w pamięci podręcznej:",
        "Available drives:": "Dostępne dyski:",
        "Searching in:": "Wyszukiwanie w:",
        "File found:": "Plik znaleziony:",
        "Checking cache file existence:": "Sprawdzanie istnienia pliku pamięci podręcznej:",
        "Cache file found. Loading...": "Plik pamięci podręcznej znaleziony. Ładowanie...",
        "Loaded paths from cache:": "Załadowane ścieżki z pamięci podręcznej:",
        "Error reading cache file:": "Błąd odczytu pliku pamięci podręcznej:",
        "Cache file not found.": "Plik pamięci podręcznej nie znaleziony.",
        "Saving path to cache:": "Zapisywanie ścieżki do pamięci podręcznej:",
        "Path saved successfully.": "Ścieżka zapisana pomyślnie.",
        "Error saving path:": "Błąd zapisywania ścieżki:",
        "Creating new cache file:": "Tworzenie nowego pliku pamięci podręcznej:",
        "Cache file created successfully.": "Plik pamięci podręcznej utworzony pomyślnie.",
        "Error creating cache file:": "Błąd tworzenia pliku pamięci podręcznej:",
        "Terminating process:": "Zakończenie procesu:",
        "Process terminated successfully:": "Proces zakończony pomyślnie:",
        "Error terminating process:": "Błąd kończenia procesu:",
        "Processing files in:": "Przetwarzanie plików w:",
        "Checking directory:": "Sprawdzanie katalogu:",
        "Reading libraries...": "Odczyt bibliotek...",
        "Library read successfully.": "Biblioteka odczytana pomyślnie.",
        "ERROR: Library file not found:": "BŁĄD: Nie znaleziono pliku biblioteki:",
        "Please make sure the library file is in the same folder as the program": "Upewnij się, że plik biblioteki znajduje się w tym samym folderze co program",
        "Error reading library. x0001": "Błąd odczytu biblioteki. x0001",
        "No access to modify:": "Brak dostępu do modyfikacji:",
        "File written:": "Plik zapisany:",
        "Rolling back changes in:": "Cofanie zmian w:",
        "Directory does not exist.": "Katalog nie istnieje.",
        "Translation found in files:": "Znaleziono tłumaczenie w plikach:",
        "File deleted:": "Plik usunięty:",
        "File copied:": "Plik skopiowany:",
        "File not found:": "Plik nie znaleziony:",
        "Launching application:": "Uruchamianie aplikacji:",
        "Application launched successfully.": "Aplikacja uruchomiona pomyślnie.",
        "Error launching application:": "Błąd uruchamiania aplikacji:",
        "Getting list of available drives...": "Pobieranie listy dostępnych dysków...",
        "Drives found:": "Znalezione dyski:"
    },
        "Lv": {  # Latviešu
        "About": "Par programmu",
        "Blur Intensity": "Blur intensitāte",
        "Language": "Valoda",
        "Ready for translation": "Gatavs tulkošanai",
        "Start": "SĀKT",
        "Rollback Changes": "ATCELT IZMAIŅAS",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "DARMOSHARK DRAIVERU AUTOMĀTISKĀ TULKOŠANA",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODEĻI M3/M3s/N3 | VERSIJAS 1.6.5 - 1.8.2.9",
        "program for automatic translation": "programma automātiskai tulkošanai",
        "of Darmoshark mouse drivers into multiple languages": "Darmoshark peles draiveru tulkošanai vairākās valodās",
        "Fully automatic process": "Pilnībā automātisks process",
        "Security: files remain on your PC": "Drošība: faili paliek jūsu datorā",
        "Ability to roll back to default settings": "Iespēja atgriezties pie noklusējuma iestatījumiem",
        "IMPORTANT:": "SVARĪGI:",
        "The program DOES NOT collect or send your data!": "Programma NESAVĀC un NESŪTA jūsu datus!",
        "All files are stored strictly on your computer.": "Visi faili tiek glabāti strikti jūsu datorā.",
        "DRIVER UPDATES:": "DRAIVERU ATJAUNINĀJUMI:",
        "Google Sheet": "Google Tabula",
        "OFFICIAL WEBSITE:": "OFICIĀLĀ TĪMĒKLAPA:",
        "DEVELOPER:": "IZSTRĀDĀTĀJS:",
        "SUPPORT THE DEVELOPER:": "ATBAĻSTIET IZSTRĀDĀTĀJU:",
        "Close": "Aizvērt",
        "This is the multi-language version of Russifier Drk v2.0": "Šī ir daudzvalodu Russifier Drk v2.0 versija",
        "Original version (Russian only) available on": "Oriģinālā versija (tikai krievu valodā) pieejama",
        "Searching for application...": "Meklē programmu...",
        "Success. Closing application...": "Veiksmīgi. Aizver programmu...",
        "Processing language files...": "Apstrādā valodu failus...",
        "Launching application...": "Palaist programmu...",
        "Process completed!": "Process pabeigts!",
        "Application not found!": "Programma nav atrasta!",
        "Rolling back changes...": "Atceļ izmaiņas...",
        "Removing translation files...": "Noņem tulkojuma failus...",
        "Rollback completed!": "Atcelšana pabeigta!",
        "Loading cached paths...": "Ielādē kešatmiņas ceļus...",
        "Cached paths:": "Kešatmiņas ceļi:",
        "Found in cache:": "Atrasts kešatmiņā:",
        "Available drives:": "Pieejamie diski:",
        "Searching in:": "Meklē:",
        "File found:": "Fails atrasts:",
        "Checking cache file existence:": "Pārbauda kešfaila esamību:",
        "Cache file found. Loading...": "Kešfails atrasts. Ielādē...",
        "Loaded paths from cache:": "Ielādētie ceļi no kešatmiņas:",
        "Error reading cache file:": "Kļūda lasot kešfailu:",
        "Cache file not found.": "Kešfails nav atrasts.",
        "Saving path to cache:": "Saglabā ceļu kešatmiņā:",
        "Path saved successfully.": "Ceļš veiksmīgi saglabāts.",
        "Error saving path:": "Kļūda saglabājot ceļu:",
        "Creating new cache file:": "Izveido jaunu kešfailu:",
        "Cache file created successfully.": "Kešfails veiksmīgi izveidots.",
        "Error creating cache file:": "Kļūda izveidojot kešfailu:",
        "Terminating process:": "Pārtrauc procesu:",
        "Process terminated successfully:": "Process veiksmīgi pārtraukts:",
        "Error terminating process:": "Kļūda pārtraucot procesu:",
        "Processing files in:": "Apstrādā failus:",
        "Checking directory:": "Pārbauda direktoriju:",
        "Reading libraries...": "Lasot bibliotēkas...",
        "Library read successfully.": "Bibliotēka veiksmīgi nolasīta.",
        "ERROR: Library file not found:": "KĻŪDA: Bibliotēkas fails nav atrasts:",
        "Please make sure the library file is in the same folder as the program": "Lūdzu, pārliecinieties, ka bibliotēkas fails atrodas tajā pašā mapē kā programma",
        "Error reading library. x0001": "Kļūda lasot bibliotēku. x0001",
        "No access to modify:": "Nav piekļuves modificēšanai:",
        "File written:": "Fails ierakstīts:",
        "Rolling back changes in:": "Atceļ izmaiņas:",
        "Directory does not exist.": "Direktorija neeksistē.",
        "Translation found in files:": "Tulkojums atrasts failos:",
        "File deleted:": "Fails dzēsts:",
        "File copied:": "Fails kopēts:",
        "File not found:": "Fails nav atrasts:",
        "Launching application:": "Palaist programmu:",
        "Application launched successfully.": "Programma veiksmīgi palaista.",
        "Error launching application:": "Kļūda palaižot programmu:",
        "Getting list of available drives...": "Iegūst pieejamo disku sarakstu...",
        "Drives found:": "Atrastie diski:"
    },
    "Lt": {  # Lietuvių
        "About": "Apie programą",
        "Blur Intensity": "Išblukimo intensyvumas",
        "Language": "Kalba",
        "Ready for translation": "Paruošta vertimui",
        "Start": "PALEISTI",
        "Rollback Changes": "ATSTATYTI POKYČIUS",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "DARMOSHARK TVARKYKLIŲ AUTOMATINIS VERTIMAS",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELIAI M3/M3s/N3 | VERSIJOS 1.6.5 - 1.8.2.9",
        "program for automatic translation": "automatinio vertimo programa",
        "of Darmoshark mouse drivers into multiple languages": "Darmoshark pelės tvarkyklių vertimui į kelias kalbas",
        "Fully automatic process": "Visiškai automatinis procesas",
        "Security: files remain on your PC": "Saugumas: failai lieka jūsų kompiuteryje",
        "Ability to roll back to default settings": "Galimybė atstatyti numatytuosius nustatymus",
        "IMPORTANT:": "SVARBU:",
        "The program DOES NOT collect or send your data!": "Programa NERINKO ir NESIUNČIA jūsų duomenų!",
        "All files are stored strictly on your computer.": "Visi failai saugomi griežtai jūsų kompiuteryje.",
        "DRIVER UPDATES:": "TVARKYKLIŲ ATNAUJINIMAI:",
        "Google Sheet": "Google Lentelė",
        "OFFICIAL WEBSITE:": "OFICIALI SVETAINĖ:",
        "DEVELOPER:": "KŪRĖJAS:",
        "SUPPORT THE DEVELOPER:": "PALAIKYKITE KŪRĖJĄ:",
        "Close": "Uždaryti",
        "This is the multi-language version of Russifier Drk v2.0": "Tai daugiakalbė Russifier Drk v2.0 versija",
        "Original version (Russian only) available on": "Originali versija (tik rusų kalba) prieinama",
        "Searching for application...": "Ieškoma programos...",
        "Success. Closing application...": "Pavyko. Uždaroma programa...",
        "Processing language files...": "Apdorojami kalbos failai...",
        "Launching application...": "Paleidžiama programa...",
        "Process completed!": "Procesas baigtas!",
        "Application not found!": "Programa nerasta!",
        "Rolling back changes...": "Atšaukiami pakeitimai...",
        "Removing translation files...": "Šalinami vertimo failai...",
        "Rollback completed!": "Atšaukimas baigtas!",
        "Loading cached paths...": "Įkeliami talpyklos keliai...",
        "Cached paths:": "Talpyklos keliai:",
        "Found in cache:": "Rasta talpykloje:",
        "Available drives:": "Prieinami diskai:",
        "Searching in:": "Ieškoma:",
        "File found:": "Rastas failas:",
        "Checking cache file existence:": "Tikrinama talpyklos failo buvimas:",
        "Cache file found. Loading...": "Talpyklos failas rastas. Įkeliama...",
        "Loaded paths from cache:": "Įkelti keliai iš talpyklos:",
        "Error reading cache file:": "Klaida skaitant talpyklos failą:",
        "Cache file not found.": "Talpyklos failas nerastas.",
        "Saving path to cache:": "Išsaugomas kelias talpykloje:",
        "Path saved successfully.": "Kelias sėkmingai išsaugotas.",
        "Error saving path:": "Klaida išsaugant kelią:",
        "Creating new cache file:": "Kuriamas naujas talpyklos failas:",
        "Cache file created successfully.": "Talpyklos failas sėkmingai sukurtas.",
        "Error creating cache file:": "Klaida kuriant talpyklos failą:",
        "Terminating process:": "Nutraukiamas procesas:",
        "Process terminated successfully:": "Procesas sėkmingai nutrauktas:",
        "Error terminating process:": "Klaida nutraukiant procesą:",
        "Processing files in:": "Apdorojami failai:",
        "Checking directory:": "Tikrinamas katalogas:",
        "Reading libraries...": "Skaitomos bibliotekos...",
        "Library read successfully.": "Biblioteka sėkmingai perskaityta.",
        "ERROR: Library file not found:": "KLAIDA: Bibliotekos failas nerastas:",
        "Please make sure the library file is in the same folder as the program": "Įsitikinkite, kad bibliotekos failas yra toje pačioje aplanke kaip programa",
        "Error reading library. x0001": "Klaida skaitant biblioteką. x0001",
        "No access to modify:": "Nėra prieigos redaguoti:",
        "File written:": "Failas įrašytas:",
        "Rolling back changes in:": "Atšaukiami pakeitimai:",
        "Directory does not exist.": "Katalogas neegzistuoja.",
        "Translation found in files:": "Vertimas rastas failuose:",
        "File deleted:": "Failas ištrintas:",
        "File copied:": "Failas nukopijuotas:",
        "File not found:": "Failas nerastas:",
        "Launching application:": "Paleidžiama programa:",
        "Application launched successfully.": "Programa sėkmingai paleista.",
        "Error launching application:": "Klaida paleidžiant programą:",
        "Getting list of available drives...": "Gaunamas prieinamų diskų sąrašas...",
        "Drives found:": "Rasti diskai:"
    },
    "Et": {  # Eesti
        "About": "Rakendusest",
        "Blur Intensity": "Hägustuse intensiivsus",
        "Language": "Keel",
        "Ready for translation": "Tõlkimiseks valmis",
        "Start": "ALUSTA",
        "Rollback Changes": "TAGASIPÖÖRDUMINE",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "DARMOSHARK DRIVERITE AUTOMAATTÕLGE",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MUDELID M3/M3s/N3 | VERSIOONID 1.6.5 - 1.8.2.9",
        "program for automatic translation": "automaattõlke programm",
        "of Darmoshark mouse drivers into multiple languages": "Darmoshark hiire draiverite tõlkimiseks mitmesse keelde",
        "Fully automatic process": "Täielikult automatiseeritud protsess",
        "Security: files remain on your PC": "Turvalisus: failid jäävad teie arvutisse",
        "Ability to roll back to default settings": "Võimalus taastada vaikesätted",
        "IMPORTANT:": "TÄHIS:",
        "The program DOES NOT collect or send your data!": "Programm EI KOGU ega SAADA teie andmeid!",
        "All files are stored strictly on your computer.": "Kõik failid hoitakse rangelt teie arvutis.",
        "DRIVER UPDATES:": "DRAIVERI UUENDUSED:",
        "Google Sheet": "Google Tabel",
        "OFFICIAL WEBSITE:": "AMETLIK VEBSITE:",
        "DEVELOPER:": "ARENDUSMEESKOND:",
        "SUPPORT THE DEVELOPER:": "TOETA ARENDAJAID:",
        "Close": "Sulge",
        "This is the multi-language version of Russifier Drk v2.0": "See on Russifier Drk v2.0 mitmekeelne versioon",
        "Original version (Russian only) available on": "Originaalversioon (ainult vene keeles) on saadaval",
        "Searching for application...": "Rakenduse otsimine...",
        "Success. Closing application...": "Edu. Rakenduse sulgemine...",
        "Processing language files...": "Keelefailide töötlemine...",
        "Launching application...": "Rakenduse käivitamine...",
        "Process completed!": "Protsess lõpetatud!",
        "Application not found!": "Rakendust ei leitud!",
        "Rolling back changes...": "Muudatuste tagasivõtmine...",
        "Removing translation files...": "Tõlkefailide eemaldamine...",
        "Rollback completed!": "Tagasivõtmine lõpetatud!",
        "Loading cached paths...": "Vahemälu teede laadimine...",
        "Cached paths:": "Vahemälu teed:",
        "Found in cache:": "Leitud vahemälust:",
        "Available drives:": "Saadaolevad kettad:",
        "Searching in:": "Otsin:",
        "File found:": "Fail leitud:",
        "Checking cache file existence:": "Vahemälufaili olemasolu kontrollimine:",
        "Cache file found. Loading...": "Vahemälufail leitud. Laadimine...",
        "Loaded paths from cache:": "Vahemälust laetud teed:",
        "Error reading cache file:": "Viga vahemälufaili lugemisel:",
        "Cache file not found.": "Vahemälufaili ei leitud.",
        "Saving path to cache:": "Tee salvestamine vahemällu:",
        "Path saved successfully.": "Tee edukalt salvestatud.",
        "Error saving path:": "Viga teed salvestades:",
        "Creating new cache file:": "Uue vahemälufaili loomine:",
        "Cache file created successfully.": "Vahemälufail edukalt loodud.",
        "Error creating cache file:": "Viga vahemälufaili loomisel:",
        "Terminating process:": "Protsessi lõpetamine:",
        "Process terminated successfully:": "Protsess edukalt lõpetatud:",
        "Error terminating process:": "Viga protsessi lõpetamisel:",
        "Processing files in:": "Failide töötlemine:",
        "Checking directory:": "Kataloogi kontrollimine:",
        "Reading libraries...": "Raamatukogude lugemine...",
        "Library read successfully.": "Raamatukogu edukalt loetud.",
        "ERROR: Library file not found:": "VIGA: Raamatukogufaili ei leitud:",
        "Please make sure the library file is in the same folder as the program": "Palun veenduge, et raamatukogufail on programmiga samas kaustas",
        "Error reading library. x0001": "Viga raamatukogu lugemisel. x0001",
        "No access to modify:": "Muutmiseks juurdepääs puudub:",
        "File written:": "Fail kirjutatud:",
        "Rolling back changes in:": "Muudatuste tagasivõtmine:",
        "Directory does not exist.": "Kataloogi pole olemas.",
        "Translation found in files:": "Tõlge leitud failidest:",
        "File deleted:": "Fail kustutatud:",
        "File copied:": "Fail kopeeritud:",
        "File not found:": "Faili ei leitud:",
        "Launching application:": "Rakenduse käivitamine:",
        "Application launched successfully.": "Rakendus edukalt käivitatud.",
        "Error launching application:": "Viga rakenduse käivitamisel:",
        "Getting list of available drives...": "Saadaolevate ketaste nimekirja hankimine...",
        "Drives found:": "Leitud kettad:"
    },
    "Tr": {  # Türkçe
        "About": "Hakkında",
        "Blur Intensity": "Bulanıklık Şiddeti",
        "Language": "Dil",
        "Ready for translation": "Çeviriye hazır",
        "Start": "BAŞLAT",
        "Rollback Changes": "DEĞİŞİKLİKLERİ GERİ AL",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "DARMOSHARK SÜRÜCÜLERİNİN OTOMATİK ÇEVİRİSİ",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELLER M3/M3s/N3 | SÜRÜMLER 1.6.5 - 1.8.2.9",
        "program for automatic translation": "otomatik çeviri programı",
        "of Darmoshark mouse drivers into multiple languages": "Darmoshark fare sürücülerinin çoklu dil desteği",
        "Fully automatic process": "Tam otomatik süreç",
        "Security: files remain on your PC": "Güvenlik: dosyalar bilgisayarınızda kalır",
        "Ability to roll back to default settings": "Varsayılan ayarlara dönme yeteneği",
        "IMPORTANT:": "ÖNEMLİ:",
        "The program DOES NOT collect or send your data!": "Program verilerinizi TOPLAMAZ ve GÖNDERMEZ!",
        "All files are stored strictly on your computer.": "Tüm dosyalar yalnızca bilgisayarınızda saklanır.",
        "DRIVER UPDATES:": "SÜRÜCÜ GÜNCELLEMELERİ:",
        "Google Sheet": "Google Tablosu",
        "OFFICIAL WEBSITE:": "RESMİ WEB SİTESİ:",
        "DEVELOPER:": "GELİŞTİRİCİ:",
        "SUPPORT THE DEVELOPER:": "GELİŞTİRİCİYİ DESTEKLE:",
        "Close": "Kapat",
        "This is the multi-language version of Russifier Drk v2.0": "Bu, Russifier Drk v2.0'ın çoklu dil sürümüdür",
        "Original version (Russian only) available on": "Orijinal sürüm (yalnızca Rusça) şu adreste mevcuttur",
        "Searching for application...": "Uygulama aranıyor...",
        "Success. Closing application...": "Başarılı. Uygulama kapatılıyor...",
        "Processing language files...": "Dil dosyaları işleniyor...",
        "Launching application...": "Uygulama başlatılıyor...",
        "Process completed!": "İşlem tamamlandı!",
        "Application not found!": "Uygulama bulunamadı!",
        "Rolling back changes...": "Değişiklikler geri alınıyor...",
        "Removing translation files...": "Çeviri dosyaları kaldırılıyor...",
        "Rollback completed!": "Geri alma tamamlandı!",
        "Loading cached paths...": "Önbelleğe alınmış yollar yükleniyor...",
        "Cached paths:": "Önbellek yolları:",
        "Found in cache:": "Önbellekte bulundu:",
        "Available drives:": "Kullanılabilir sürücüler:",
        "Searching in:": "Aranıyor:",
        "File found:": "Dosya bulundu:",
        "Checking cache file existence:": "Önbellek dosyası varlığı kontrol ediliyor:",
        "Cache file found. Loading...": "Önbellek dosyası bulundu. Yükleniyor...",
        "Loaded paths from cache:": "Önbellekten yüklenen yollar:",
        "Error reading cache file:": "Önbellek dosyası okunurken hata:",
        "Cache file not found.": "Önbellek dosyası bulunamadı.",
        "Saving path to cache:": "Yol önbelleğe kaydediliyor:",
        "Path saved successfully.": "Yol başarıyla kaydedildi.",
        "Error saving path:": "Yol kaydedilirken hata:",
        "Creating new cache file:": "Yeni önbellek dosyası oluşturuluyor:",
        "Cache file created successfully.": "Önbellek dosyası başarıyla oluşturuldu.",
        "Error creating cache file:": "Önbellek dosyası oluşturulurken hata:",
        "Terminating process:": "İşlem sonlandırılıyor:",
        "Process terminated successfully:": "İşlem başarıyla sonlandırıldı:",
        "Error terminating process:": "İşlem sonlandırılırken hata:",
        "Processing files in:": "Dosyalar işleniyor:",
        "Checking directory:": "Dizin kontrol ediliyor:",
        "Reading libraries...": "Kütüphaneler okunuyor...",
        "Library read successfully.": "Kütüphane başarıyla okundu.",
        "ERROR: Library file not found:": "HATA: Kütüphane dosyası bulunamadı:",
        "Please make sure the library file is in the same folder as the program": "Lütfen kütüphane dosyasının programla aynı klasörde olduğundan emin olun",
        "Error reading library. x0001": "Kütüphane okunurken hata. x0001",
        "No access to modify:": "Değiştirme erişimi yok:",
        "File written:": "Dosya yazıldı:",
        "Rolling back changes in:": "Değişiklikler geri alınıyor:",
        "Directory does not exist.": "Dizin mevcut değil.",
        "Translation found in files:": "Dosyalarda çeviri bulundu:",
        "File deleted:": "Dosya silindi:",
        "File copied:": "Dosya kopyalandı:",
        "File not found:": "Dosya bulunamadı:",
        "Launching application:": "Uygulama başlatılıyor:",
        "Application launched successfully.": "Uygulama başarıyla başlatıldı.",
        "Error launching application:": "Uygulama başlatılırken hata:",
        "Getting list of available drives...": "Kullanılabilir sürücülerin listesi alınıyor...",
        "Drives found:": "Bulunan sürücüler:"
    },
    "De": {  # Deutsch
        "About": "Über",
        "Blur Intensity": "Unschärfe-Intensität",
        "Language": "Sprache",
        "Ready for translation": "Bereit für Übersetzung",
        "Start": "START",
        "Rollback Changes": "ÄNDERUNGEN ZURÜCKSETZEN",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "AUTOMATISCHE ÜBERSETZUNG VON DARMOSHARK-TREIBERN",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELLE M3/M3s/N3 | VERSIONEN 1.6.5 - 1.8.2.9",
        "program for automatic translation": "Programm zur automatischen Übersetzung",
        "of Darmoshark mouse drivers into multiple languages": "von Darmoshark-Maustreibern in mehrere Sprachen",
        "Fully automatic process": "Vollautomatischer Prozess",
        "Security: files remain on your PC": "Sicherheit: Dateien bleiben auf Ihrem PC",
        "Ability to roll back to default settings": "Möglichkeit, Standardeinstellungen wiederherzustellen",
        "IMPORTANT:": "WICHTIG:",
        "The program DOES NOT collect or send your data!": "Das Programm sammelt oder sendet KEINE Ihre Daten!",
        "All files are stored strictly on your computer.": "Alle Dateien werden ausschließlich auf Ihrem Computer gespeichert.",
        "DRIVER UPDATES:": "TREIBERAKTUALISIERUNGEN:",
        "Google Sheet": "Google Tabellen",
        "OFFICIAL WEBSITE:": "OFFIZIELLE WEBSITE:",
        "DEVELOPER:": "ENTWICKLER:",
        "SUPPORT THE DEVELOPER:": "ENTWICKLER UNTERSTÜTZEN:",
        "Close": "Schließen",
        "This is the multi-language version of Russifier Drk v2.0": "Dies ist die mehrsprachige Version von Russifier Drk v2.0",
        "Original version (Russian only) available on": "Originalversion (nur Russisch) verfügbar auf",
        "Searching for application...": "Suche nach Anwendung...",
        "Success. Closing application...": "Erfolg. Anwendung wird geschlossen...",
        "Processing language files...": "Verarbeitung von Sprachdateien...",
        "Launching application...": "Anwendung wird gestartet...",
        "Process completed!": "Prozess abgeschlossen!",
        "Application not found!": "Anwendung nicht gefunden!",
        "Rolling back changes...": "Änderungen werden rückgängig gemacht...",
        "Removing translation files...": "Übersetzungsdateien werden entfernt...",
        "Rollback completed!": "Rückgängig machen abgeschlossen!",
        "Loading cached paths...": "Cache-Pfade werden geladen...",
        "Cached paths:": "Cache-Pfade:",
        "Found in cache:": "Im Cache gefunden:",
        "Available drives:": "Verfügbare Laufwerke:",
        "Searching in:": "Suche in:",
        "File found:": "Datei gefunden:",
        "Checking cache file existence:": "Überprüfung der Cache-Datei-Existenz:",
        "Cache file found. Loading...": "Cache-Datei gefunden. Wird geladen...",
        "Loaded paths from cache:": "Pfade aus Cache geladen:",
        "Error reading cache file:": "Fehler beim Lesen der Cache-Datei:",
        "Cache file not found.": "Cache-Datei nicht gefunden.",
        "Saving path to cache:": "Pfad wird im Cache gespeichert:",
        "Path saved successfully.": "Pfad erfolgreich gespeichert.",
        "Error saving path:": "Fehler beim Speichern des Pfads:",
        "Creating new cache file:": "Neue Cache-Datei wird erstellt:",
        "Cache file created successfully.": "Cache-Datei erfolgreich erstellt.",
        "Error creating cache file:": "Fehler beim Erstellen der Cache-Datei:",
        "Terminating process:": "Prozess wird beendet:",
        "Process terminated successfully:": "Prozess erfolgreich beendet:",
        "Error terminating process:": "Fehler beim Beenden des Prozesses:",
        "Processing files in:": "Dateien werden verarbeitet in:",
        "Checking directory:": "Verzeichnis wird überprüft:",
        "Reading libraries...": "Bibliotheken werden gelesen...",
        "Library read successfully.": "Bibliothek erfolgreich gelesen.",
        "ERROR: Library file not found:": "FEHLER: Bibliotheksdatei nicht gefunden:",
        "Please make sure the library file is in the same folder as the program": "Bitte stellen Sie sicher, dass die Bibliotheksdatei im selben Ordner wie das Programm liegt",
        "Error reading library. x0001": "Fehler beim Lesen der Bibliothek. x0001",
        "No access to modify:": "Kein Zugriff zum Ändern:",
        "File written:": "Datei geschrieben:",
        "Rolling back changes in:": "Änderungen werden rückgängig gemacht in:",
        "Directory does not exist.": "Verzeichnis existiert nicht.",
        "Translation found in files:": "Übersetzung in Dateien gefunden:",
        "File deleted:": "Datei gelöscht:",
        "File copied:": "Datei kopiert:",
        "File not found:": "Datei nicht gefunden:",
        "Launching application:": "Anwendung wird gestartet:",
        "Application launched successfully.": "Anwendung erfolgreich gestartet.",
        "Error launching application:": "Fehler beim Starten der Anwendung:",
        "Getting list of available drives...": "Liste der verfügbaren Laufwerke wird abgerufen...",
        "Drives found:": "Gefundene Laufwerke:"
    },
    "Fr": {  # Français
        "About": "À propos",
        "Blur Intensity": "Intensité du flou",
        "Language": "Langue",
        "Ready for translation": "Prêt pour traduction",
        "Start": "DÉMARRER",
        "Rollback Changes": "ANNULER LES MODIFICATIONS",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "TRADUCTION AUTOMATIQUE DES PILOTES DARMOSHARK",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODÈLES M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9",
        "program for automatic translation": "programme de traduction automatique",
        "of Darmoshark mouse drivers into multiple languages": "des pilotes de souris Darmoshark en plusieurs langues",
        "Fully automatic process": "Processus entièrement automatique",
        "Security: files remain on your PC": "Sécurité : les fichiers restent sur votre PC",
        "Ability to roll back to default settings": "Possibilité de revenir aux paramètres par défaut",
        "IMPORTANT:": "IMPORTANT :",
        "The program DOES NOT collect or send your data!": "Le programme NE collecte PAS et NE envoie PAS vos données !",
        "All files are stored strictly on your computer.": "Tous les fichiers sont stockés strictement sur votre ordinateur.",
        "DRIVER UPDATES:": "MISES À JOUR DES PILOTES :",
        "Google Sheet": "Feuille Google",
        "OFFICIAL WEBSITE:": "SITE OFFICIEL :",
        "DEVELOPER:": "DÉVELOPPEUR :",
        "SUPPORT THE DEVELOPER:": "SOUTENEZ LE DÉVELOPPEUR :",
        "Close": "Fermer",
        "This is the multi-language version of Russifier Drk v2.0": "Ceci est la version multilingue de Russifier Drk v2.0",
        "Original version (Russian only) available on": "Version originale (en russe uniquement) disponible sur",
        "Searching for application...": "Recherche de l'application...",
        "Success. Closing application...": "Succès. Fermeture de l'application...",
        "Processing language files...": "Traitement des fichiers de langue...",
        "Launching application...": "Lancement de l'application...",
        "Process completed!": "Processus terminé !",
        "Application not found!": "Application non trouvée !",
        "Rolling back changes...": "Annulation des modifications...",
        "Removing translation files...": "Suppression des fichiers de traduction...",
        "Rollback completed!": "Annulation terminée !",
        "Loading cached paths...": "Chargement des chemins en cache...",
        "Cached paths:": "Chemins en cache :",
        "Found in cache:": "Trouvé dans le cache :",
        "Available drives:": "Lecteurs disponibles :",
        "Searching in:": "Recherche dans :",
        "File found:": "Fichier trouvé :",
        "Checking cache file existence:": "Vérification de l'existence du fichier cache :",
        "Cache file found. Loading...": "Fichier cache trouvé. Chargement...",
        "Loaded paths from cache:": "Chemins chargés depuis le cache :",
        "Error reading cache file:": "Erreur de lecture du fichier cache :",
        "Cache file not found.": "Fichier cache non trouvé.",
        "Saving path to cache:": "Sauvegarde du chemin dans le cache :",
        "Path saved successfully.": "Chemin sauvegardé avec succès.",
        "Error saving path:": "Erreur lors de la sauvegarde du chemin :",
        "Creating new cache file:": "Création d'un nouveau fichier cache :",
        "Cache file created successfully.": "Fichier cache créé avec succès.",
        "Error creating cache file:": "Erreur lors de la création du fichier cache :",
        "Terminating process:": "Terminaison du processus :",
        "Process terminated successfully:": "Processus terminé avec succès :",
        "Error terminating process:": "Erreur lors de la terminaison du processus :",
        "Processing files in:": "Traitement des fichiers dans :",
        "Checking directory:": "Vérification du répertoire :",
        "Reading libraries...": "Lecture des bibliothèques...",
        "Library read successfully.": "Bibliothèque lue avec succès.",
        "ERROR: Library file not found:": "ERREUR : Fichier de bibliothèque non trouvé :",
        "Please make sure the library file is in the same folder as the program": "Veuillez vous assurer que le fichier de bibliothèque est dans le même dossier que le programme",
        "Error reading library. x0001": "Erreur de lecture de la bibliothèque. x0001",
        "No access to modify:": "Pas d'accès pour modifier :",
        "File written:": "Fichier écrit :",
        "Rolling back changes in:": "Annulation des modifications dans :",
        "Directory does not exist.": "Le répertoire n'existe pas.",
        "Translation found in files:": "Traduction trouvée dans les fichiers :",
        "File deleted:": "Fichier supprimé :",
        "File copied:": "Fichier copié :",
        "File not found:": "Fichier non trouvé :",
        "Launching application:": "Lancement de l'application :",
        "Application launched successfully.": "Application lancée avec succès.",
        "Error launching application:": "Erreur lors du lancement de l'application :",
        "Getting list of available drives...": "Obtention de la liste des lecteurs disponibles...",
        "Drives found:": "Lecteurs trouvés :"
    },
    "Es": {  # Español
        "About": "Acerca de",
        "Blur Intensity": "Intensidad de desenfoque",
        "Language": "Idioma",
        "Ready for translation": "Listo para traducción",
        "Start": "INICIAR",
        "Rollback Changes": "REVERTIR CAMBIOS",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "TRADUCCIÓN AUTOMÁTICA DE CONTROLADORES DARMOSHARK",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELOS M3/M3s/N3 | VERSIONES 1.6.5 - 1.8.2.9",
        "program for automatic translation": "programa de traducción automática",
        "of Darmoshark mouse drivers into multiple languages": "de controladores de ratón Darmoshark a múltiples idiomas",
        "Fully automatic process": "Proceso completamente automático",
        "Security: files remain on your PC": "Seguridad: los archivos permanecen en tu PC",
        "Ability to roll back to default settings": "Capacidad de revertir a la configuración predeterminada",
        "IMPORTANT:": "IMPORTANTE:",
        "The program DOES NOT collect or send your data!": "¡El programa NO recopila NI envía tus datos!",
        "All files are stored strictly on your computer.": "Todos los archivos se almacenan estrictamente en tu computadora.",
        "DRIVER UPDATES:": "ACTUALIZACIONES DE CONTROLADORES:",
        "Google Sheet": "Hoja de Google",
        "OFFICIAL WEBSITE:": "SITIO WEB OFICIAL:",
        "DEVELOPER:": "DESARROLLADOR:",
        "SUPPORT THE DEVELOPER:": "APOYA AL DESARROLLADOR:",
        "Close": "Cerrar",
        "This is the multi-language version of Russifier Drk v2.0": "Esta es la versión multilingüe de Russifier Drk v2.0",
        "Original version (Russian only) available on": "Versión original (solo en ruso) disponible en",
        "Searching for application...": "Buscando aplicación...",
        "Success. Closing application...": "Éxito. Cerrando aplicación...",
        "Processing language files...": "Procesando archivos de idioma...",
        "Launching application...": "Iniciando aplicación...",
        "Process completed!": "¡Proceso completado!",
        "Application not found!": "¡Aplicación no encontrada!",
        "Rolling back changes...": "Revirtiendo cambios...",
        "Removing translation files...": "Eliminando archivos de traducción...",
        "Rollback completed!": "¡Reversión completada!",
        "Loading cached paths...": "Cargando rutas en caché...",
        "Cached paths:": "Rutas en caché:",
        "Found in cache:": "Encontrado en caché:",
        "Available drives:": "Unidades disponibles:",
        "Searching in:": "Buscando en:",
        "File found:": "Archivo encontrado:",
        "Checking cache file existence:": "Verificando existencia de archivo caché:",
        "Cache file found. Loading...": "Archivo caché encontrado. Cargando...",
        "Loaded paths from cache:": "Rutas cargadas desde caché:",
        "Error reading cache file:": "Error al leer archivo caché:",
        "Cache file not found.": "Archivo caché no encontrado.",
        "Saving path to cache:": "Guardando ruta en caché:",
        "Path saved successfully.": "Ruta guardada con éxito.",
        "Error saving path:": "Error al guardar ruta:",
        "Creating new cache file:": "Creando nuevo archivo caché:",
        "Cache file created successfully.": "Archivo caché creado con éxito.",
        "Error creating cache file:": "Error al crear archivo caché:",
        "Terminating process:": "Terminando proceso:",
        "Process terminated successfully:": "Proceso terminado con éxito:",
        "Error terminating process:": "Error al terminar proceso:",
        "Processing files in:": "Procesando archivos en:",
        "Checking directory:": "Verificando directorio:",
        "Reading libraries...": "Leyendo bibliotecas...",
        "Library read successfully.": "Biblioteca leída con éxito.",
        "ERROR: Library file not found:": "ERROR: Archivo de biblioteca no encontrado:",
        "Please make sure the library file is in the same folder as the program": "Asegúrate de que el archivo de biblioteca esté en la misma carpeta que el programa",
        "Error reading library. x0001": "Error al leer biblioteca. x0001",
        "No access to modify:": "Sin acceso para modificar:",
        "File written:": "Archivo escrito:",
        "Rolling back changes in:": "Revirtiendo cambios en:",
        "Directory does not exist.": "El directorio no existe.",
        "Translation found in files:": "Traducción encontrada en archivos:",
        "File deleted:": "Archivo eliminado:",
        "File copied:": "Archivo copiado:",
        "File not found:": "Archivo no encontrado:",
        "Launching application:": "Iniciando aplicación:",
        "Application launched successfully.": "Aplicación iniciada con éxito.",
        "Error launching application:": "Error al iniciar aplicación:",
        "Getting list of available drives...": "Obteniendo lista de unidades disponibles...",
        "Drives found:": "Unidades encontradas:"
    },
        "Hy": {  # Հայերեն
        "About": "Ծրագրի մասին",
        "Blur Intensity": "Թափանցիկության մակարդակ",
        "Language": "Լեզու",
        "Ready for translation": "Պատրաստ է թարգմանության",
        "Start": "ՍԿՍԵԼ",
        "Rollback Changes": "Վերականգնել փոփոխությունները",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "DARMOSHARK ՕԳՆԱԿԻ ԻՐԱՎԱՐՏՈՒԹՅՈՒՆՆԵՐԻ ԱՎՏՈՄԱՏ ԹԱՐԳՄԱՆՈՒՄ",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "ՄՈԴԵԼՆԵՐ M3/M3s/N3 | ՏԱՐԲԵՐԱԿՆԵՐ 1.6.5 - 1.8.2.9",
        "program for automatic translation": "ավտոմատ թարգմանության ծրագիր",
        "of Darmoshark mouse drivers into multiple languages": "Darmoshark մկնիկի վարորդների համար բազմալեզու թարգմանություն",
        "Fully automatic process": "Ամբողջությամբ ավտոմատ գործընթաց",
        "Security: files remain on your PC": "Անվտանգություն. ֆայլերը մնում են ձեր համակարգչում",
        "Ability to roll back to default settings": "Հնարավորություն վերականգնել լռելյայն կարգավորումները",
        "IMPORTANT:": "ԿԱՐԵՎՈՐ.",
        "The program DOES NOT collect or send your data!": "ԾրագիրՉԵՄՀԱՎԱՔՈՒՄկամՈՉՇՈՒՏԱԴՐՈՒՄձերտվյալները։",
        "All files are stored strictly on your computer.": "Բոլոր ֆայլերը պահվում են բացառապես ձեր համակարգչում:",
        "DRIVER UPDATES:": "ՎԱՐՈՐԴԻ ԹԱՐՄԱՑՈՒՄՆԵՐ.",
        "Google Sheet": "Google աղյուսակ",
        "OFFICIAL WEBSITE:": "ՊԱՇՏՈՆԱԿԱՆ ԿԱՅՔ.",
        "DEVELOPER:": "ՄԱՍՆԱԳԵՏ.",
        "SUPPORT THE DEVELOPER:": "ԱՋԱԿՑԵՔՄԱՍՆԱԳԵՏԻՆ.",
        "Close": "Փակել",
        "This is the multi-language version of Russifier Drk v2.0": "Սա Russifier Drk v2.0-ի բազմալեզու տարբերակն է",
        "Original version (Russian only) available on": "Բնօրինակ տարբերակը (միայն ռուսերեն) հասանելի է",
        "Searching for application...": "Ծրագրի որոնում...",
        "Success. Closing application...": "Հաջողություն: Փակվում է ծրագիրը...",
        "Processing language files...": "Լեզվական ֆայլերի մշակում...",
        "Launching application...": "Ծրագիրը գործարկվում է...",
        "Process completed!": "Գործընթացն ավարտված է։",
        "Application not found!": "Ծրագիրը չի գտնվել։",
        "Rolling back changes...": "Փոփոխությունների հետգործարկում...",
        "Removing translation files...": "Թարգմանության ֆայլերի հեռացում...",
        "Rollback completed!": "Հետգործարկումն ավարտված է։",
        "Loading cached paths...": "Բեռնվում են քեշավորված ուղիները...",
        "Cached paths:": "Քեշավորված ուղիներ.",
        "Found in cache:": "Գտնվել է քեշում.",
        "Available drives:": "Հասանելի սարքեր.",
        "Searching in:": "Որոնում.",
        "File found:": "Ֆայլը գտնվել է.",
        "Checking cache file existence:": "Ստուգվում է քեշ ֆայլի առկայությունը.",
        "Cache file found. Loading...": "Քեշ ֆայլը գտնվել է։ Բեռնում...",
        "Loaded paths from cache:": "Բեռնված ուղիներ քեշից.",
        "Error reading cache file:": "Սխալ քեշ ֆայլի ընթերցման ժամանակ.",
        "Cache file not found.": "Քեշ ֆայլը չի գտնվել։",
        "Saving path to cache:": "Պահպանվում է ուղին քեշում.",
        "Path saved successfully.": "Ուղին հաջողությամբ պահպանված է։",
        "Error saving path:": "Սխալ ուղին պահպանելիս։",
        "Creating new cache file:": "Ստեղծվում է նոր քեշ ֆայլ։",
        "Cache file created successfully.": "Քեշ ֆայլը հաջողությամբ ստեղծված է։",
        "Error creating cache file:": "Սխալ քեշ ֆայլի ստեղծման ժամանակ։",
        "Terminating process:": "Գործընթացի ավարտ։",
        "Process terminated successfully:": "Գործընթացը հաջողությամբ ավարտված է։",
        "Error terminating process:": "Սխալ գործընթացի ավարտման ժամանակ։",
        "Processing files in:": "Ֆայլերի մշակում.",
        "Checking directory:": "Ստուգվում է թղթապանակը։",
        "Reading libraries...": "Կարդացվում են գրադարանները...",
        "Library read successfully.": "Գրադարանը հաջողությամբ կարդացված է։",
        "ERROR: Library file not found:": "ՍԽԱԼ. Գրադարանի ֆայլը չի գտնվել։",
        "Please make sure the library file is in the same folder as the program": "Խնդրում ենք համոզվել, որ գրադարանի ֆայլը գտնվում է ծրագրի նույն թղթապանակում։",
        "Error reading library. x0001": "Սխալ գրադարանը կարդալիս. x0001",
        "No access to modify:": "Մուտք չկա փոփոխելու համար։",
        "File written:": "Ֆայլը գրված է։",
        "Rolling back changes in:": "Փոփոխությունների հետգործարկում.",
        "Directory does not exist.": "Թղթապանակը գոյություն չունի։",
        "Translation found in files:": "Թարգմանությունը գտնվել է ֆայլերում։",
        "File deleted:": "Ֆայլը ջնջված է։",
        "File copied:": "Ֆայլը պատճենված է։",
        "File not found:": "Ֆայլը չի գտնվել։",
        "Launching application:": "Ծրագիրը գործարկվում է։",
        "Application launched successfully.": "Ծրագիրը հաջողությամբ գործարկված է։",
        "Error launching application:": "Սխալ ծրագիրը գործարկելիս։",
        "Getting list of available drives...": "Ստացվում է հասանելի սարքերի ցանկը...",
        "Drives found:": "Գտնված սարքեր։"
    },
        "Ka": {  # ქართული
        "About": "პროგრამის შესახებ",
        "Blur Intensity": "დაბინდვის ინტენსივობა",
        "Language": "ენა",
        "Ready for translation": "თარგმნისთვის მზადაა",
        "Start": "დაწყება",
        "Rollback Changes": "ცვლილებების გაუქმება",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "DARMOSHARK-ის დრაივერების ავტომატური თარგმანი",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "მოდელები M3/M3s/N3 | ვერსიები 1.6.5 - 1.8.2.9",
        "program for automatic translation": "ავტომატური თარგმნის პროგრამა",
        "of Darmoshark mouse drivers into multiple languages": "Darmoshark-ის მაუსის დრაივერების მრავალენოვან თარგმანში",
        "Fully automatic process": "სრულიად ავტომატური პროცესი",
        "Security: files remain on your PC": "უსაფრთხოება: ფაილები დარჩება თქვენს კომპიუტერზე",
        "Ability to roll back to default settings": "ნაგულისხმევ პარამეტრებზე დაბრუნების შესაძლებლობა",
        "IMPORTANT:": "მნიშვნელოვანი:",
        "The program DOES NOT collect or send your data!": "პროგრამა არ აგროვებს და არ აგზავნის თქვენს მონაცემებს!",
        "All files are stored strictly on your computer.": "ყველა ფაილი მკაცრად თქვენს კომპიუტერზე ინახება.",
        "DRIVER UPDATES:": "დრაივერების განახლებები:",
        "Google Sheet": "Google ცხრილი",
        "OFFICIAL WEBSITE:": "ოფიციალური საიტი:",
        "DEVELOPER:": "დეველოპერი:",
        "SUPPORT THE DEVELOPER:": "მხარი დაუჭირეთ დეველოპერს:",
        "Close": "დახურვა",
        "This is the multi-language version of Russifier Drk v2.0": "ეს არის Russifier Drk v2.0-ის მრავალენოვანი ვერსია",
        "Original version (Russian only) available on": "ორიგინალური ვერსია (მხოლოდ რუსულად) ხელმისაწვდომია",
        "Searching for application...": "აპლიკაციის ძებნა...",
        "Success. Closing application...": "წარმატება. აპლიკაციის დახურვა...",
        "Processing language files...": "ენობრივი ფაილების დამუშავება...",
        "Launching application...": "აპლიკაციის გაშვება...",
        "Process completed!": "პროცესი დასრულებულია!",
        "Application not found!": "აპლიკაცია ვერ მოიძებნა!",
        "Rolling back changes...": "ცვლილებების გაუქმება...",
        "Removing translation files...": "თარგმანის ფაილების წაშლა...",
        "Rollback completed!": "გაუქმება დასრულებულია!",
        "Loading cached paths...": "ქეშირებული გზების ჩატვირთვა...",
        "Cached paths:": "ქეშირებული გზები:",
        "Found in cache:": "ნაპოვნია ქეშში:",
        "Available drives:": "ხელმისაწვდომი დისკები:",
        "Searching in:": "ძებნა:",
        "File found:": "ფაილი ნაპოვნია:",
        "Checking cache file existence:": "ქეშ ფაილის არსებობის შემოწმება:",
        "Cache file found. Loading...": "ქეშ ფაილი ნაპოვნია. ჩატვირთვა...",
        "Loaded paths from cache:": "ჩატვირთული გზები ქეშიდან:",
        "Error reading cache file:": "შეცდომა ქეშ ფაილის წაკითხვისას:",
        "Cache file not found.": "ქეშ ფაილი ვერ მოიძებნა.",
        "Saving path to cache:": "გზის შენახვა ქეშში:",
        "Path saved successfully.": "გზა წარმატებით შეინახა.",
        "Error saving path:": "შეცდომა გზის შენახვისას:",
        "Creating new cache file:": "ახალი ქეშ ფაილის შექმნა:",
        "Cache file created successfully.": "ქეშ ფაილი წარმატებით შეიქმნა.",
        "Error creating cache file:": "შეცდომა ქეშ ფაილის შექმნისას:",
        "Terminating process:": "პროცესის დასრულება:",
        "Process terminated successfully:": "პროცესი წარმატებით დასრულდა:",
        "Error terminating process:": "შეცდომა პროცესის დასრულებისას:",
        "Processing files in:": "ფაილების დამუშავება:",
        "Checking directory:": "დირექტორიის შემოწმება:",
        "Reading libraries...": "ბიბლიოთეკების კითხვა...",
        "Library read successfully.": "ბიბლიოთეკა წარმატებით წაიკითხა.",
        "ERROR: Library file not found:": "შეცდომა: ბიბლიოთეკის ფაილი ვერ მოიძებნა:",
        "Please make sure the library file is in the same folder as the program": "დარწმუნდით, რომ ბიბლიოთეკის ფაილი პროგრამის იმავე საქაღალდეშია",
        "Error reading library. x0001": "შეცდომა ბიბლიოთეკის კითხვისას. x0001",
        "No access to modify:": "შეცვლის უფლება არ არის:",
        "File written:": "ფაილი ჩაწერილია:",
        "Rolling back changes in:": "ცვლილებების გაუქმება:",
        "Directory does not exist.": "დირექტორია არ არსებობს.",
        "Translation found in files:": "თარგმანი ნაპოვნია ფაილებში:",
        "File deleted:": "ფაილი წაშლილია:",
        "File copied:": "ფაილი დაკოპირებულია:",
        "File not found:": "ფაილი ვერ მოიძებნა:",
        "Launching application:": "აპლიკაციის გაშვება:",
        "Application launched successfully.": "აპლიკაცია წარმატებით გაეშვა.",
        "Error launching application:": "შეცდომა აპლიკაციის გაშვებისას:",
        "Getting list of available drives...": "ხელმისაწვდომი დისკების სიის მიღება...",
        "Drives found:": "ნაპოვნი დისკები:"
    },
        "Ro": {  # Română
        "About": "Despre",
        "Blur Intensity": "Intensitate neclaritate",
        "Language": "Limba",
        "Ready for translation": "Gata pentru traducere",
        "Start": "START",
        "Rollback Changes": "ANULEAZĂ MODIFICĂRILE",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "TRADUCERE AUTOMATĂ A DRIVERELOR DARMOSHARK",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELE M3/M3s/N3 | VERSIUNI 1.6.5 - 1.8.2.9",
        "program for automatic translation": "program pentru traducere automată",
        "of Darmoshark mouse drivers into multiple languages": "a driverelor mouse-ului Darmoshark în mai multe limbi",
        "Fully automatic process": "Proces complet automat",
        "Security: files remain on your PC": "Securitate: fișierele rămân pe PC-ul dumneavoastră",
        "Ability to roll back to default settings": "Posibilitatea de a reveni la setările implicite",
        "IMPORTANT:": "IMPORTANT:",
        "The program DOES NOT collect or send your data!": "Programul NU colectează și NU trimite datele dumneavoastră!",
        "All files are stored strictly on your computer.": "Toate fișierele sunt stocate strict pe computerul dumneavoastră.",
        "DRIVER UPDATES:": "ACTUALIZĂRI DRIVERE:",
        "Google Sheet": "Foaie Google",
        "OFFICIAL WEBSITE:": "SITE OFICIAL:",
        "DEVELOPER:": "DEZVOLTATOR:",
        "SUPPORT THE DEVELOPER:": "SPRIJINĂ DEZVOLTATORUL:",
        "Close": "Închide",
        "This is the multi-language version of Russifier Drk v2.0": "Aceasta este versiunea multilingvă a Russifier Drk v2.0",
        "Original version (Russian only) available on": "Versiunea originală (doar în rusă) disponibilă pe",
        "Searching for application...": "Căutare aplicație...",
        "Success. Closing application...": "Succes. Închidere aplicație...",
        "Processing language files...": "Prelucrare fișiere limbă...",
        "Launching application...": "Lansare aplicație...",
        "Process completed!": "Proces finalizat!",
        "Application not found!": "Aplicația nu a fost găsită!",
        "Rolling back changes...": "Revocare modificări...",
        "Removing translation files...": "Ștergere fișiere traducere...",
        "Rollback completed!": "Revocare finalizată!",
        "Loading cached paths...": "Încărcare căi cache...",
        "Cached paths:": "Căi cache:",
        "Found in cache:": "Găsit în cache:",
        "Available drives:": "Unități disponibile:",
        "Searching in:": "Căutare în:",
        "File found:": "Fișier găsit:",
        "Checking cache file existence:": "Verificare existență fișier cache:",
        "Cache file found. Loading...": "Fișier cache găsit. Se încarcă...",
        "Loaded paths from cache:": "Căi încărcate din cache:",
        "Error reading cache file:": "Eroare la citirea fișierului cache:",
        "Cache file not found.": "Fișier cache negăsit.",
        "Saving path to cache:": "Salvare cale în cache:",
        "Path saved successfully.": "Cale salvată cu succes.",
        "Error saving path:": "Eroare la salvarea căii:",
        "Creating new cache file:": "Creare fișier cache nou:",
        "Cache file created successfully.": "Fișier cache creat cu succes.",
        "Error creating cache file:": "Eroare la crearea fișierului cache:",
        "Terminating process:": "Terminare proces:",
        "Process terminated successfully:": "Proces terminat cu succes:",
        "Error terminating process:": "Eroare la terminarea procesului:",
        "Processing files in:": "Prelucrare fișiere în:",
        "Checking directory:": "Verificare director:",
        "Reading libraries...": "Citire biblioteci...",
        "Library read successfully.": "Bibliotecă citită cu succes.",
        "ERROR: Library file not found:": "EROARE: Fișier bibliotecă negăsit:",
        "Please make sure the library file is in the same folder as the program": "Asigurați-vă că fișierul bibliotecii este în același folder cu programul",
        "Error reading library. x0001": "Eroare la citirea bibliotecii. x0001",
        "No access to modify:": "Nu există acces pentru modificare:",
        "File written:": "Fișier scris:",
        "Rolling back changes in:": "Revocare modificări în:",
        "Directory does not exist.": "Directorul nu există.",
        "Translation found in files:": "Traducere găsită în fișiere:",
        "File deleted:": "Fișier șters:",
        "File copied:": "Fișier copiat:",
        "File not found:": "Fișier negăsit:",
        "Launching application:": "Lansare aplicație:",
        "Application launched successfully.": "Aplicație lansată cu succes.",
        "Error launching application:": "Eroare la lansarea aplicației:",
        "Getting list of available drives...": "Obținere listă unități disponibile...",
        "Drives found:": "Unități găsite:"
    },
        "Cs": { 
        "About": "O programu",
        "Blur Intensity": "Intenzita rozostření",
        "Language": "Jazyk",
        "Ready for translation": "Připraveno k překladu",
        "Start": "SPUSTIT",
        "Rollback Changes": "VRÁTIT ZMĚNY",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "AUTOMATICKÝ PŘEKLAD OVLADAČŮ DARMOSHARK",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELY M3/M3s/N3 | VERZE 1.6.5 - 1.8.2.9",
        "program for automatic translation": "program pro automatický překlad",
        "of Darmoshark mouse drivers into multiple languages": "ovladačů myší Darmoshark do více jazyků",
        "Fully automatic process": "Plně automatický proces",
        "Security: files remain on your PC": "Zabezpečení: soubory zůstávají na vašem počítači",
        "Ability to roll back to default settings": "Možnost vrátit výchozí nastavení",
        "IMPORTANT:": "DŮLEŽITÉ:",
        "The program DOES NOT collect or send your data!": "Program NESBÍRÁ a NEPOSÍLÁ vaše data!",
        "All files are stored strictly on your computer.": "Všechny soubory jsou uloženy výhradně na vašem počítači.",
        "DRIVER UPDATES:": "AKTUALIZACE OVLADAČŮ:",
        "Google Sheet": "Tabulka Google",
        "OFFICIAL WEBSITE:": "OFICIÁLNÍ WEB:",
        "DEVELOPER:": "VÝVOJÁŘ:",
        "SUPPORT THE DEVELOPER:": "PODPOŘTE VÝVOJÁŘE:",
        "Close": "Zavřít",
        "This is the multi-language version of Russifier Drk v2.0": "Toto je vícejazyčná verze Russifier Drk v2.0",
        "Original version (Russian only) available on": "Původní verze (pouze ruština) je k dispozici na",
        "Searching for application...": "Vyhledávání aplikace...",
        "Success. Closing application...": "Úspěch. Ukončování aplikace...",
        "Processing language files...": "Zpracování jazykových souborů...",
        "Launching application...": "Spouštění aplikace...",
        "Process completed!": "Proces dokončen!",
        "Application not found!": "Aplikace nebyla nalezena!",
        "Rolling back changes...": "Vracení změn...",
        "Removing translation files...": "Odstraňování překladových souborů...",
        "Rollback completed!": "Vrácení změn dokončeno!",
        "Loading cached paths...": "Načítání uložených cest...",
        "Cached paths:": "Uložené cesty:",
        "Found in cache:": "Nalezeno v mezipaměti:",
        "Available drives:": "Dostupné disky:",
        "Searching in:": "Hledání v:",
        "File found:": "Soubor nalezen:",
        "Checking cache file existence:": "Kontrola existence souboru mezipaměti:",
        "Cache file found. Loading...": "Soubor mezipaměti nalezen. Načítání...",
        "Loaded paths from cache:": "Načtené cesty z mezipaměti:",
        "Error reading cache file:": "Chyba při čtení souboru mezipaměti:",
        "Cache file not found.": "Soubor mezipaměti nebyl nalezen.",
        "Saving path to cache:": "Ukládání cesty do mezipaměti:",
        "Path saved successfully.": "Cesta úspěšně uložena.",
        "Error saving path:": "Chyba při ukládání cesty:",
        "Creating new cache file:": "Vytváření nového souboru mezipaměti:",
        "Cache file created successfully.": "Soubor mezipaměti úspěšně vytvořen.",
        "Error creating cache file:": "Chyba při vytváření souboru mezipaměti:",
        "Terminating process:": "Ukončování procesu:",
        "Process terminated successfully:": "Proces úspěšně ukončen:",
        "Error terminating process:": "Chyba při ukončování procesu:",
        "Processing files in:": "Zpracování souborů v:",
        "Checking directory:": "Kontrola adresáře:",
        "Reading libraries...": "Čtení knihoven...",
        "Library read successfully.": "Knihovna úspěšně přečtena.",
        "ERROR: Library file not found:": "CHYBA: Soubor knihovny nebyl nalezen:",
        "Please make sure the library file is in the same folder as the program": "Ujistěte se, že soubor knihovny je ve stejném adresáři jako program",
        "Error reading library. x0001": "Chyba při čtení knihovny. x0001",
        "No access to modify:": "Žádný přístup k úpravám:",
        "File written:": "Soubor zapsán:",
        "Rolling back changes in:": "Vracení změn v:",
        "Directory does not exist.": "Adresář neexistuje.",
        "Translation found in files:": "Překlad nalezen v souborech:",
        "File deleted:": "Soubor smazán:",
        "File copied:": "Soubor zkopírován:",
        "File not found:": "Soubor nebyl nalezen:",
        "Launching application:": "Spouštění aplikace:",
        "Application launched successfully.": "Aplikace úspěšně spuštěna.",
        "Error launching application:": "Chyba při spouštění aplikace:",
        "Getting list of available drives...": "Získávání seznamu dostupných disků...",
        "Drives found:": "Nalezené disky:"
    },
            "Ru": {
                "About": "О программе",
                "Blur Intensity": "Интенсивность размытия",
                "Language": "Язык",
                "Ready for translation": "Готов к переводу",
                "Start": "НАЧАТЬ",
                "Rollback Changes": "ОТКАТИТЬ ИЗМЕНЕНИЯ",
                "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "АВТОМАТИЧЕСКИЙ ПЕРЕВОД ДРАЙВЕРОВ DARMOSHARK",
                "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "МОДЕЛИ M3/M3s/N3 | ВЕРСИИ 1.6.5 - 1.8.2.9",
                "program for automatic translation": "программа для автоматического перевода",
                "of Darmoshark mouse drivers into multiple languages": "драйверов мыши Darmoshark на несколько языков",
                "Fully automatic process": "Полностью автоматический процесс",
                "Security: files remain on your PC": "Безопасность: файлы остаются на вашем ПК",
                "Ability to roll back to default settings": "Возможность отката к стандартным настройкам",
                "IMPORTANT:": "ВАЖНО:",
                "The program DOES NOT collect or send your data!": "Программа НЕ собирает и НЕ отправляет ваши данные!",
                "All files are stored strictly on your computer.": "Все файлы хранятся строго на вашем компьютере.",
                "DRIVER UPDATES:": "ОБНОВЛЕНИЯ ДРАЙВЕРОВ:",
                "Google Sheet": "Google Таблица",
                "OFFICIAL WEBSITE:": "ОФИЦИАЛЬНЫЙ САЙТ:",
                "DEVELOPER:": "РАЗРАБОТЧИК:",
                "SUPPORT THE DEVELOPER:": "ПОДДЕРЖКА РАЗРАБОТЧИКА:",
                "Close": "Закрыть",
                "This is the multi-language version of Russifier Drk v2.0": "Это мультиязычная версия программы Russifier Drk v2.0",
                "Original version (Russian only) available on": "Оригинальная версия (только русский) доступна на",
                "Searching for application...": "Поиск приложения...",
                "Success. Closing application...": "Успешно. Закрытие приложения...",
                "Processing language files...": "Обработка языковых файлов...",
                "Launching application...": "Запуск приложения...",
                "Process completed!": "Процесс завершен!",
                "Application not found!": "Приложение не найдено!",
                "Rolling back changes...": "Откат изменений...",
                "Removing translation files...": "Удаление файлов перевода...",
                "Rollback completed!": "Откат завершен!",
                "Loading cached paths...": "Загрузка кэшированных путей...",
                "Cached paths:": "Кэшированные пути:",
                "Found in cache:": "Найдено в кэше:",
                "Available drives:": "Доступные диски:",
                "Searching in:": "Поиск в:",
                "File found:": "Файл найден:",
                "Checking cache file existence:": "Проверка существования файла кэша:",
                "Cache file found. Loading...": "Файл кэша найден. Загрузка...",
                "Loaded paths from cache:": "Загружены пути из кэша:",
                "Error reading cache file:": "Ошибка чтения файла кэша:",
                "Cache file not found.": "Файл кэша не найден.",
                "Saving path to cache:": "Сохранение пути в кэш:",
                "Path saved successfully.": "Путь успешно сохранен.",
                "Error saving path:": "Ошибка сохранения пути:",
                "Creating new cache file:": "Создание нового файла кэша:",
                "Cache file created successfully.": "Файл кэша успешно создан.",
                "Error creating cache file:": "Ошибка создания файла кэша:",
                "Terminating process:": "Завершение процесса:",
                "Process terminated successfully:": "Процесс успешно завершен:",
                "Error terminating process:": "Ошибка завершения процесса:",
                "Processing files in:": "Обработка файлов в:",
                "Checking directory:": "Проверка директории:",
                "Reading libraries...": "Чтение библиотек...",
                "Library read successfully.": "Библиотека успешно прочитана.",
                "ERROR: Library file not found:": "ОШИБКА: Файл библиотеки не найден:",
                "Please make sure the library file is in the same folder as the program": "Пожалуйста, убедитесь что файл библиотеки находится в той же папке что и программа",
                "Error reading library. x0001": "Ошибка чтения библиотеки. x0001",
                "No access to modify:": "Нет доступа для изменения:",
                "File written:": "Файл записан:",
                "Rolling back changes in:": "Откат изменений в:",
                "Directory does not exist.": "Директория не существует.",
                "Translation found in files:": "Обнаружен перевод в файлах:",
                "File deleted:": "Файл удален:",
                "File copied:": "Файл скопирован:",
                "File not found:": "Файл не найден:",
                "Launching application:": "Запуск приложения:",
                "Application launched successfully.": "Приложение успешно запущено.",
                "Error launching application:": "Ошибка запуска приложения:",
                "Getting list of available drives...": "Получение списка доступных дисков...",
                "Drives found:": "Найдены диски:"
            },
                "Sk": {  # Словацký
        "About": "O programe",
        "Blur Intensity": "Intenzita rozostrenia",
        "Language": "Jazyk",
        "Ready for translation": "Pripravené na preklad",
        "Start": "SPUSTIŤ",
        "Rollback Changes": "VRÁTIŤ ZMENY",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "AUTOMATICKÝ PREKLAD OVLÁDAČOV DARMOSHARK",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "MODELY M3/M3s/N3 | VERZIE 1.6.5 - 1.8.2.9",
        "program for automatic translation": "program na automatický preklad",
        "of Darmoshark mouse drivers into multiple languages": "ovládačov myši Darmoshark do viacerých jazykov",
        "Fully automatic process": "Plně automatický proces",
        "Security: files remain on your PC": "Bezpečnosť: súbory zostávajú na vašom počítači",
        "Ability to roll back to default settings": "Možnosť vrátiť pôvodné nastavenia",
        "IMPORTANT:": "DÔLEŽITÉ:",
        "The program DOES NOT collect or send your data!": "Program NESBÍRA a NEPOSIELA vaše údaje!",
        "All files are stored strictly on your computer.": "Všetky súbory sú uložené výhradne na vašom počítači.",
        "DRIVER UPDATES:": "AKTUALIZÁCIE OVLÁDAČOV:",
        "Google Sheet": "Google Tabuľka",
        "OFFICIAL WEBSITE:": "OFICIÁLNA WEBSTRÁNKA:",
        "DEVELOPER:": "VÝVOJÁR:",
        "SUPPORT THE DEVELOPER:": "PODPORTE VÝVOJÁRA:",
        "Close": "Zavrieť",
        "This is the multi-language version of Russifier Drk v2.0": "Toto je viacjazyčná verzia Russifier Drk v2.0",
        "Original version (Russian only) available on": "Pôvodná verzia (len v ruštine) je k dispozícii na",
        "Searching for application...": "Hľadanie aplikácie...",
        "Success. Closing application...": "Úspech. Zatváranie aplikácie...",
        "Processing language files...": "Spracovanie jazykových súborov...",
        "Launching application...": "Spúšťanie aplikácie...",
        "Process completed!": "Proces dokončený!",
        "Application not found!": "Aplikácia nenájdená!",
        "Rolling back changes...": "Vračanie zmien...",
        "Removing translation files...": "Odstraňovanie prekladových súborov...",
        "Rollback completed!": "Vrátenie zmien dokončené!",
        "Loading cached paths...": "Načítavanie uložených ciest...",
        "Cached paths:": "Uložené cesty:",
        "Found in cache:": "Nájdené v medzipamäti:",
        "Available drives:": "Dostupné disky:",
        "Searching in:": "Hľadanie v:",
        "File found:": "Súbor nájdený:",
        "Checking cache file existence:": "Kontrola existencie súboru medzipamäte:",
        "Cache file found. Loading...": "Súbor medzipamäte nájdený. Načítavanie...",
        "Loaded paths from cache:": "Načítané cesty z medzipamäte:",
        "Error reading cache file:": "Chyba pri čítaní súboru medzipamäte:",
        "Cache file not found.": "Súbor medzipamäte nenájdený.",
        "Saving path to cache:": "Ukladanie cesty do medzipamäte:",
        "Path saved successfully.": "Cesta úspešne uložená.",
        "Error saving path:": "Chyba pri ukladaní cesty:",
        "Creating new cache file:": "Vytváranie nového súboru medzipamäte:",
        "Cache file created successfully.": "Súbor medzipamäte úspešne vytvorený.",
        "Error creating cache file:": "Chyba pri vytváraní súboru medzipamäte:",
        "Terminating process:": "Ukončovanie procesu:",
        "Process terminated successfully:": "Proces úspešne ukončený:",
        "Error terminating process:": "Chyba pri ukončovaní procesu:",
        "Processing files in:": "Spracovanie súborov v:",
        "Checking directory:": "Kontrola adresára:",
        "Reading libraries...": "Čítanie knižníc...",
        "Library read successfully.": "Knižnica úspešne prečítaná.",
        "ERROR: Library file not found:": "CHYBA: Súbor knižnice nenájdený:",
        "Please make sure the library file is in the same folder as the program": "Uistite sa, že súbor knižnice je v rovnakom priečinku ako program",
        "Error reading library. x0001": "Chyba pri čítaní knižnice. x0001",
        "No access to modify:": "Žiadny prístup k úpravám:",
        "File written:": "Súbor zapísaný:",
        "Rolling back changes in:": "Vračanie zmien v:",
        "Directory does not exist.": "Adresár neexistuje.",
        "Translation found in files:": "Preklad nájdený v súboroch:",
        "File deleted:": "Súbor vymazaný:",
        "File copied:": "Súbor skopírovaný:",
        "File not found:": "Súbor nenájdený:",
        "Launching application:": "Spúšťanie aplikácie:",
        "Application launched successfully.": "Aplikácia úspešne spustená.",
        "Error launching application:": "Chyba pri spúšťaní aplikácie:",
        "Getting list of available drives...": "Získavanie zoznamu dostupných diskov...",
        "Drives found:": "Nájdené disky:"
    },
    "Bg": {  # Български
        "About": "За програмата",
        "Blur Intensity": "Интензивност на размазването",
        "Language": "Език",
        "Ready for translation": "Готов за превод",
        "Start": "СТАРТ",
        "Rollback Changes": "ОБРАТНИ ПРОМЕНИ",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "АВТОМАТИЧЕН ПРЕВОД НА ДРАЙВЕРИТЕ НА DARMOSHARK",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "МОДЕЛИ M3/M3s/N3 | ВЕРСИИ 1.6.5 - 1.8.2.9",
        "program for automatic translation": "програма за автоматичен превод",
        "of Darmoshark mouse drivers into multiple languages": "на драйверите на мишката Darmoshark на множество езици",
        "Fully automatic process": "Напълно автоматичен процес",
        "Security: files remain on your PC": "Сигурност: файловете остават на вашия компютър",
        "Ability to roll back to default settings": "Възможност за връщане към настройките по подразбиране",
        "IMPORTANT:": "ВАЖНО:",
        "The program DOES NOT collect or send your data!": "Програмата НЕ събира и НЕ изпраща вашите данни!",
        "All files are stored strictly on your computer.": "Всички файлове се съхраняват строго на вашия компютър.",
        "DRIVER UPDATES:": "АКТУАЛИЗАЦИИ НА ДРАЙВЕРИТЕ:",
        "Google Sheet": "Google Таблица",
        "OFFICIAL WEBSITE:": "ОФИЦИАЛЕН УЕБСАЙТ:",
        "DEVELOPER:": "РАЗРАБОТЧИК:",
        "SUPPORT THE DEVELOPER:": "ПОДКРЕПЕТЕ РАЗРАБОТЧИКА:",
        "Close": "Затвори",
        "This is the multi-language version of Russifier Drk v2.0": "Това е многоезичната версия на Russifier Drk v2.0",
        "Original version (Russian only) available on": "Оригиналната версия (само на руски) е достъпна на",
        "Searching for application...": "Търсене на приложение...",
        "Success. Closing application...": "Успех. Затваряне на приложението...",
        "Processing language files...": "Обработка на езикови файлове...",
        "Launching application...": "Стартиране на приложението...",
        "Process completed!": "Процесът завършен!",
        "Application not found!": "Приложението не е намерено!",
        "Rolling back changes...": "Връщане на промените...",
        "Removing translation files...": "Премахване на преводните файлове...",
        "Rollback completed!": "Връщането на промените завършено!",
        "Loading cached paths...": "Зареждане на кеширани пътища...",
        "Cached paths:": "Кеширани пътища:",
        "Found in cache:": "Намерено в кеша:",
        "Available drives:": "Налични дискове:",
        "Searching in:": "Търсене в:",
        "File found:": "Файл намерен:",
        "Checking cache file existence:": "Проверка за съществуване на кеш файл:",
        "Cache file found. Loading...": "Кеш файл намерен. Зареждане...",
        "Loaded paths from cache:": "Заредени пътища от кеша:",
        "Error reading cache file:": "Грешка при четене на кеш файл:",
        "Cache file not found.": "Кеш файлът не е намерен.",
        "Saving path to cache:": "Запазване на пътя в кеша:",
        "Path saved successfully.": "Пътят е запазен успешно.",
        "Error saving path:": "Грешка при запазване на пътя:",
        "Creating new cache file:": "Създаване на нов кеш файл:",
        "Cache file created successfully.": "Кеш файлът е създаден успешно.",
        "Error creating cache file:": "Грешка при създаване на кеш файл:",
        "Terminating process:": "Прекратяване на процес:",
        "Process terminated successfully:": "Процесът прекратен успешно:",
        "Error terminating process:": "Грешка при прекратяване на процес:",
        "Processing files in:": "Обработка на файлове в:",
        "Checking directory:": "Проверка на директория:",
        "Reading libraries...": "Четене на библиотеки...",
        "Library read successfully.": "Библиотеката прочетена успешно.",
        "ERROR: Library file not found:": "ГРЕШКА: Файлът на библиотеката не е намерен:",
        "Please make sure the library file is in the same folder as the program": "Моля, уверете се, че файлът на библиотеката е в същата папка като програмата",
        "Error reading library. x0001": "Грешка при четене на библиотека. x0001",
        "No access to modify:": "Няма достъп за промяна:",
        "File written:": "Файл записан:",
        "Rolling back changes in:": "Връщане на промени в:",
        "Directory does not exist.": "Директорията не съществува.",
        "Translation found in files:": "Превод намерен във файлове:",
        "File deleted:": "Файл изтрит:",
        "File copied:": "Файл копиран:",
        "File not found:": "Файл не намерен:",
        "Launching application:": "Стартиране на приложение:",
        "Application launched successfully.": "Приложението стартирано успешно.",
        "Error launching application:": "Грешка при стартиране на приложението:",
        "Getting list of available drives...": "Получаване на списък с налични дискове...",
        "Drives found:": "Намерени дискове:"
    },
    "Sr": {  # Српски
        "About": "О програму",
        "Blur Intensity": "Интензитет замућења",
        "Language": "Језик",
        "Ready for translation": "Спремно за превод",
        "Start": "ПОЧЕТИ",
        "Rollback Changes": "ВРАТИ ПРОМЕНЕ",
        "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "АУТОМАТСКИ ПРЕВОД DARMOSHARK ДРАЈВЕРА",
        "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "МОДЕЛИ M3/M3s/N3 | ВЕРЗИЈЕ 1.6.5 - 1.8.2.9",
        "program for automatic translation": "програм за аутоматски превод",
        "of Darmoshark mouse drivers into multiple languages": "Darmoshark драјвера за миш на више језика",
        "Fully automatic process": "Потпуно аутоматски процес",
        "Security: files remain on your PC": "Безбедност: датотеке остају на вашем рачунару",
        "Ability to roll back to default settings": "Могућност враћања на подразумевана подешавања",
        "IMPORTANT:": "ВАЖНО:",
        "The program DOES NOT collect or send your data!": "Програм НЕ прикупља и НЕ шаље ваше податке!",
        "All files are stored strictly on your computer.": "Све датотеке се чувају строго на вашем рачунару.",
        "DRIVER UPDATES:": "АЖУРИРАЊА ДРАЈВЕРА:",
        "Google Sheet": "Google табела",
        "OFFICIAL WEBSITE:": "ЗВАНИЧНА ВЕБ СТРАНИЦА:",
        "DEVELOPER:": "ПРОГРАМЕР:",
        "SUPPORT THE DEVELOPER:": "ПОДРЖИТЕ ПРОГРАМЕРА:",
        "Close": "Затвори",
        "This is the multi-language version of Russifier Drk v2.0": "Ово је вишејезична верзија Russifier Drk v2.0",
        "Original version (Russian only) available on": "Оригинална верзија (само на руском) доступна на",
        "Searching for application...": "Тражење апликације...",
        "Success. Closing application...": "Успех. Затварање апликације...",
        "Processing language files...": "Обрада језичких датотека...",
        "Launching application...": "Покретање апликације...",
        "Process completed!": "Процес завршен!",
        "Application not found!": "Апликација није пронађена!",
        "Rolling back changes...": "Враћање промена...",
        "Removing translation files...": "Уклањање преводних датотека...",
        "Rollback completed!": "Враћање завршено!",
        "Loading cached paths...": "Учитавање кешираних путања...",
        "Cached paths:": "Кеширане путање:",
        "Found in cache:": "Пронађено у кешу:",
        "Available drives:": "Доступни дискови:",
        "Searching in:": "Претрага у:",
        "File found:": "Датотека пронађена:",
        "Checking cache file existence:": "Провера постојања кеш датотеке:",
        "Cache file found. Loading...": "Кеш датотека пронађена. Учитавање...",
        "Loaded paths from cache:": "Учитане путање из кеша:",
        "Error reading cache file:": "Грешка при читању кеш датотеке:",
        "Cache file not found.": "Кеш датотека није пронађена.",
        "Saving path to cache:": "Чување путање у кеш:",
        "Path saved successfully.": "Путања успешно сачувана.",
        "Error saving path:": "Грешка при чувању путање:",
        "Creating new cache file:": "Креирање нове кеш датотеке:",
        "Cache file created successfully.": "Кеш датотека успешно креирана.",
        "Error creating cache file:": "Грешка при креирању кеш датотеке:",
        "Terminating process:": "Прекидање процеса:",
        "Process terminated successfully:": "Процес успешно прекинут:",
        "Error terminating process:": "Грешка при прекидању процеса:",
        "Processing files in:": "Обрада датотека у:",
        "Checking directory:": "Провера директоријума:",
        "Reading libraries...": "Читање библиотека...",
        "Library read successfully.": "Библиотека успешно прочитана.",
        "ERROR: Library file not found:": "ГРЕШКА: Датотека библиотеке није пронађена:",
        "Please make sure the library file is in the same folder as the program": "Молимо проверите да ли је датотека библиотеке у истој фасцикли као програм",
        "Error reading library. x0001": "Грешка при читању библиотеке. x0001",
        "No access to modify:": "Нема приступа за измену:",
        "File written:": "Датотека записана:",
        "Rolling back changes in:": "Враћање промена у:",
        "Directory does not exist.": "Директоријум не постоји.",
        "Translation found in files:": "Превод пронађен у датотекама:",
        "File deleted:": "Датотека избрисана:",
        "File copied:": "Датотека копирана:",
        "File not found:": "Датотека није пронађена:",
        "Launching application:": "Покретање апликације:",
        "Application launched successfully.": "Апликација успешно покренута.",
        "Error launching application:": "Грешка при покретању апликације:",
        "Getting list of available drives...": "Добијање списка доступних дискова...",
        "Drives found:": "Пронађени дискови:"
    },
            "Ua": {
                "About": "Про програму",
                "Blur Intensity": "Інтенсивність розмиття",
                "Language": "Мова",
                "Ready for translation": "Готовий до перекладу",
                "Start": "ПОЧАТИ",
                "Rollback Changes": "СКАСУВАТИ ЗМІНИ",
                "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "АВТОМАТИЧНИЙ ПЕРЕКЛАД ДРАЙВЕРІВ DARMOSHARK",
                "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "МОДЕЛІ M3/M3s/N3 | ВЕРСІЇ 1.6.5 - 1.8.2.9",
                "program for automatic translation": "програма для автоматичного перекладу",
                "of Darmoshark mouse drivers into multiple languages": "драйверів миші Darmoshark на кілька мов",
                "Fully automatic process": "Повністю автоматичний процес",
                "Security: files remain on your PC": "Безпека: файли залишаються на вашому ПК",
                "Ability to roll back to default settings": "Можливість відкату до стандартних налаштувань",
                "IMPORTANT:": "ВАЖЛИВО:",
                "The program DOES NOT collect or send your data!": "Програма НЕ збирає та НЕ відправляє ваші дані!",
                "All files are stored strictly on your computer.": "Усі файли зберігаються строго на вашому комп'ютері.",
                "DRIVER UPDATES:": "ОНОВЛЕННЯ ДРАЙВЕРІВ:",
                "Google Sheet": "Google Таблиця",
                "OFFICIAL WEBSITE:": "ОФІЦІЙНИЙ САЙТ:",
                "DEVELOPER:": "РОЗРОБНИК:",
                "SUPPORT THE DEVELOPER:": "ПІДТРИМКА РОЗРОБНИКА:",
                "Close": "Закрити",
                "This is the multi-language version of Russifier Drk v2.0": "Це багатомовна версія програми Russifier Drk v2.0",
                "Original version (Russian only) available on": "Оригінальна версія (тільки російська) доступна на",
                "Searching for application...": "Пошук програми...",
                "Success. Closing application...": "Успішно. Закриття програми...",
                "Processing language files...": "Обробка мовних файлів...",
                "Launching application...": "Запуск програми...",
                "Process completed!": "Процес завершено!",
                "Application not found!": "Програму не знайдено!",
                "Rolling back changes...": "Скасування змін...",
                "Removing translation files...": "Видалення файлів перекладу...",
                "Rollback completed!": "Відкат завершено!",
                "Loading cached paths...": "Завантаження кешованих шляхів...",
                "Cached paths:": "Кешовані шляхи:",
                "Found in cache:": "Знайдено в кеші:",
                "Available drives:": "Доступні диски:",
                "Searching in:": "Пошук у:",
                "File found:": "Файл знайдено:",
                "Checking cache file existence:": "Перевірка наявності файлу кешу:",
                "Cache file found. Loading...": "Файл кешу знайдено. Завантаження...",
                "Loaded paths from cache:": "Завантажені шляхи з кешу:",
                "Error reading cache file:": "Помилка читання файлу кешу:",
                "Cache file not found.": "Файл кешу не знайдено.",
                "Saving path to cache:": "Збереження шляху в кеш:",
                "Path saved successfully.": "Шлях успішно збережено.",
                "Error saving path:": "Помилка збереження шляху:",
                "Creating new cache file:": "Створення нового файлу кешу:",
                "Cache file created successfully.": "Файл кешу успішно створено.",
                "Error creating cache file:": "Помилка створення файлу кешу:",
                "Terminating process:": "Завершення процесу:",
                "Process terminated successfully:": "Процес успішно завершено:",
                "Error terminating process:": "Помилка завершення процесу:",
                "Processing files in:": "Обробка файлів у:",
                "Checking directory:": "Перевірка директорії:",
                "Reading libraries...": "Читання бібліотек...",
                "Library read successfully.": "Бібліотеку успішно прочитано.",
                "ERROR: Library file not found:": "ПОМИЛКА: Файл бібліотеки не знайдено:",
                "Please make sure the library file is in the same folder as the program": "Будь ласка, переконайтеся, що файл бібліотеки знаходиться в тому ж каталозі, що й програма",
                "Error reading library. x0001": "Помилка читання бібліотеки. x0001",
                "No access to modify:": "Немає доступу для зміни:",
                "File written:": "Файл записано:",
                "Rolling back changes in:": "Скасування змін у:",
                "Directory does not exist.": "Директорія не існує.",
                "Translation found in files:": "Переклад знайдено у файлах:",
                "File deleted:": "Файл видалено:",
                "File copied:": "Файл скопійовано:",
                "File not found:": "Файл не знайдено:",
                "Launching application:": "Запуск програми:",
                "Application launched successfully.": "Програму успішно запущено.",
                "Error launching application:": "Помилка запуску програми:",
                "Getting list of available drives...": "Отримання списку доступних дисків...",
                "Drives found:": "Знайдено диски:"
            },
            "By": {
                "About": "Аб праграме",
                "Blur Intensity": "Інтэнсіўнасць размыцця",
                "Language": "Мова",
                "Ready for translation": "Гатовы да перакладу",
                "Start": "ПАЧАЦЬ",
                "Rollback Changes": "АДКІНУЦЬ ЗМЕНЫ",
                "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "АЎТАМАТЫЧНЫ ПЕРАКЛАД ДРАЙВЕРАЎ DARMOSHARK",
                "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "МАДЭЛІ M3/M3s/N3 | ВЕРСІІ 1.6.5 - 1.8.2.9",
                "program for automatic translation": "праграма для аўтаматычнага перакладу",
                "of Darmoshark mouse drivers into multiple languages": "драйвераў мышы Darmoshark на некалькі моў",
                "Fully automatic process": "Поўнасьцю аўтаматычны працэс",
                "Security: files remain on your PC": "Бясьпека: файлы застаюцца на вашым ПК",
                "Ability to roll back to default settings": "Магчымасьць адкату да стандартных наладаў",
                "IMPORTANT:": "ВАЖНА:",
                "The program DOES NOT collect or send your data!": "Праграма НЕ зьбірае і НЕ адпраўляе вашыя дадзеныя!",
                "All files are stored strictly on your computer.": "Усе файлы захоўваюцца строга на вашым кампутары.",
                "DRIVER UPDATES:": "АБНАЎЛЕННІ ДРАЙВЕРАЎ:",
                "Google Sheet": "Google Табліца",
                "OFFICIAL WEBSITE:": "АФІЦЫЙНЫ САЙТ:",
                "DEVELOPER:": "РАЗЬБІТЧЫК:",
                "SUPPORT THE DEVELOPER:": "ПАДТРЫМКА РАЗЬБІТЧЫКА:",
                "Close": "Зачыніць",
                "This is the multi-language version of Russifier Drk v2.0": "Гэта шматмоўная вэрсія праграмы Russifier Drk v2.0",
                "Original version (Russian only) available on": "Арыгінальная вэрсія (толькі расейская) даступная на",
                "Searching for application...": "Пошук праграмы...",
                "Success. Closing application...": "Пасьпяхова. Зачыненне праграмы...",
                "Processing language files...": "Апрацоўка моўных файлаў...",
                "Launching application...": "Запуск праграмы...",
                "Process completed!": "Працэс завершаны!",
                "Application not found!": "Праграма не знойдзена!",
                "Rolling back changes...": "Адмена зьменаў...",
                "Removing translation files...": "Выдаленне файлаў перакладу...",
                "Rollback completed!": "Адкат завершаны!",
                "Loading cached paths...": "Загрузка кэшаваных шляхоў...",
                "Cached paths:": "Кэшаваныя шляхі:",
                "Found in cache:": "Знойдзена ў кэшы:",
                "Available drives:": "Даступныя дыскі:",
                "Searching in:": "Пошук у:",
                "File found:": "Файл знойдзены:",
                "Checking cache file existence:": "Праверка наяўнасці файла кэшу:",
                "Cache file found. Loading...": "Файл кэшу знойдзены. Загрузка...",
                "Loaded paths from cache:": "Загружаныя шляхі з кэшу:",
                "Error reading cache file:": "Памылка чытання файла кэшу:",
                "Cache file not found.": "Файл кэшу не знойдзены.",
                "Saving path to cache:": "Захаванне шляху ў кэш:",
                "Path saved successfully.": "Шлях паспяхова захаваны.",
                "Error saving path:": "Памылка захавання шляху:",
                "Creating new cache file:": "Стварэнне новага файла кэшу:",
                "Cache file created successfully.": "Файл кэшу паспяхова створаны.",
                "Error creating cache file:": "Памылка стварэння файла кэшу:",
                "Terminating process:": "Завяршэнне працэсу:",
                "Process terminated successfully:": "Працэс паспяхова завершаны:",
                "Error terminating process:": "Памылка завяршэння працэсу:",
                "Processing files in:": "Апрацоўка файлаў у:",
                "Checking directory:": "Праверка дырэкторыі:",
                "Reading libraries...": "Чытанне бібліятэк...",
                "Library read successfully.": "Бібліятэка паспяхова прачытана.",
                "ERROR: Library file not found:": "ПАМЫЛКА: Файл бібліятэкі не знойдзены:",
                "Please make sure the library file is in the same folder as the program": "Калі ласка, пераканайцеся, што файл бібліятэкі знаходзіцца ў тым жа каталогу, што і праграма",
                "Error reading library. x0001": "Памылка чытання бібліятэкі. x0001",
                "No access to modify:": "Няма доступу для змянення:",
                "File written:": "Файл запісаны:",
                "Rolling back changes in:": "Адмена зьменаў у:",
                "Directory does not exist.": "Дырэкторыя не існуе.",
                "Translation found in files:": "Пераклад знойдзены ў файлах:",
                "File deleted:": "Файл выдалены:",
                "File copied:": "Файл скапіяваны:",
                "File not found:": "Файл не знойдзены:",
                "Launching application:": "Запуск праграмы:",
                "Application launched successfully.": "Праграма паспяхова запушчана.",
                "Error launching application:": "Памылка запуску праграмы:",
                "Getting list of available drives...": "Атрыманне спісу даступных дыскаў...",
                "Drives found:": "Знойдзены дыскі:"
            },
            "Kz": {
                "About": "Бағдарлама туралы",
                "Blur Intensity": "Бұлыңғырлау қарқыны",
                "Language": "Тіл",
                "Ready for translation": "Аударуға дайын",
                "Start": "БАСТАУ",
                "Rollback Changes": "ӨЗГЕРІСТЕРДІ БАС ТАРТУ",
                "AUTOMATIC TRANSLATION OF DARMOSHARK DRIVERS": "DARMOSHARK ДРАЙВЕРЛЕРІН АВТОМАТТЫ ТҮРДЕ АУДАРУ",
                "MODELS M3/M3s/N3 | VERSIONS 1.6.5 - 1.8.2.9": "M3/M3s/N3 МОДЕЛЬДЕРІ | 1.6.5 - 1.8.2.9 НҰСҚАЛАРЫ",
                "program for automatic translation": "автоматты түрде аудару бағдарламасы",
                "of Darmoshark mouse drivers into multiple languages": "Darmoshark тінтуір драйверлерін бірнеше тілге аудару",
                "Fully automatic process": "Толық автоматтандырылған процесс",
                "Security: files remain on your PC": "Қауіпсіздік: файлдар сіздің компьютеріңізде қалады",
                "Ability to roll back to default settings": "Өндірістік параметрлерге оралу мүмкіндігі",
                "IMPORTANT:": "МАҢЫЗДЫ:",
                "The program DOES NOT collect or send your data!": "Бағдарлама сіздің деректеріңізді ЖИНАМАЙДЫ және ЖІБЕРМЕЙДІ!",
                "All files are stored strictly on your computer.": "Барлық файлдар сіздің компьютеріңізде қатаң сақталады.",
                "DRIVER UPDATES:": "ДРАЙВЕРЛЕРДІ ЖАҢАРТУ:",
                "Google Sheet": "Google Кесте",
                "OFFICIAL WEBSITE:": "РЕСМИ САЙТ:",
                "DEVELOPER:": "ӘЗІРЛЕУШІ:",
                "SUPPORT THE DEVELOPER:": "ӘЗІРЛЕУШІНІҢ ҚОЛДАУЫ:",
                "Close": "Жабу",
                "This is the multi-language version of Russifier Drk v2.0": "Бұл Russifier Drk v2.0 бағдарламасының көптілді нұсқасы",
                "Original version (Russian only) available on": "Түпнұсқа нұсқасы (тек орыс тілінде) мына жерден қолжетімді",
                "Searching for application...": "Қолданбаны іздеу...",
                "Success. Closing application...": "Сәтті. Қолданбаны жабу...",
                "Processing language files...": "Тілдік файлдарды өңдеу...",
                "Launching application...": "Қолданбаны іске қосу...",
                "Process completed!": "Процесс аяқталды!",
                "Application not found!": "Қолданба табылмады!",
                "Rolling back changes...": "Өзгерістерді болдырмау...",
                "Removing translation files...": "Аударма файлдарын жою...",
                "Rollback completed!": "Болдырмау аяқталды!",
                "Loading cached paths...": "Кэштелген жолдарды жүктеу...",
                "Cached paths:": "Кэштелген жолдар:",
                "Found in cache:": "Кэште табылды:",
                "Available drives:": "Қолжетімді дискілер:",
                "Searching in:": "Іздеу орны:",
                "File found:": "Файл табылды:",
                "Checking cache file existence:": "Кэш файлының бар екенін тексеру:",
                "Cache file found. Loading...": "Кэш файлы табылды. Жүктеу...",
                "Loaded paths from cache:": "Кэштен жүктелген жолдар:",
                "Error reading cache file:": "Кэш файлын оқу қатесі:",
                "Cache file not found.": "Кэш файлы табылмады.",
                "Saving path to cache:": "Жолды кэшке сақтау:",
                "Path saved successfully.": "Жол сәтті сақталды.",
                "Error saving path:": "Жолды сақтау қатесі:",
                "Creating new cache file:": "Жаңа кэш файлын жасау:",
                "Cache file created successfully.": "Кэш файлы сәтті жасалды.",
                "Error creating cache file:": "Кэш файлын жасау қатесі:",
                "Terminating process:": "Процесті тоқтату:",
                "Process terminated successfully:": "Процес сәтті тоқтатылды:",
                "Error terminating process:": "Процесті тоқтату қатесі:",
                "Processing files in:": "Файлдарды өңдеу:",
                "Checking directory:": "Буманы тексеру:",
                "Reading libraries...": "Кітапханаларды оқу...",
                "Library read successfully.": "Кітапхана сәтті оқылды.",
                "ERROR: Library file not found:": "ҚАТЕ: Кітапхана файлы табылмады:",
                "Please make sure the library file is in the same folder as the program": "Кітапхана файлы бағдарламамен бір бумада екеніне көз жеткізіңіз",
                "Error reading library. x0001": "Кітапхананы оқу қатесі. x0001",
                "No access to modify:": "Өзгертуге қол жеткізу жоқ:",
                "File written:": "Файл жазылды:",
                "Rolling back changes in:": "Өзгерістерді болдырмау:",
                "Directory does not exist.": "Бума жоқ.",
                "Translation found in files:": "Файлдарда аударма табылды:",
                "File deleted:": "Файл жойылды:",
                "File copied:": "Файл көшірілді:",
                "File not found:": "Файл табылмады:",
                "Launching application:": "Қолданбаны іске қосу:",
                "Application launched successfully.": "Қолданба сәтті іске қосылды.",
                "Error launching application:": "Қолданбаны іске қосу қатесі:",
                "Getting list of available drives...": "Қолжетімді дискілер тізімін алу...",
                "Drives found:": "Табылған дискілер:"
            }
        }
        self.initUI()
        self.setup_animations()
    
    def translate(self, text):
        """Translate text based on current language"""
        return self.translations.get(self.current_language, {}).get(text, text)
    
    def initUI(self):
        self.setWindowTitle('Drk multi lang v1.0')
        icon_path = self.resource_path('main.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setFixedSize(800, 650)
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.background = QWidget(self)
        self.background.setGeometry(self.rect())
        self.background.setStyleSheet("background-color: rgba(30, 35, 40, 220);")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = ModernTitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_widget.setStyleSheet("#contentWidget { background: transparent; }")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 15, 20, 20)
        content_layout.setSpacing(15)
        
        control_card = GlassCard()
        control_layout = QHBoxLayout(control_card)
        control_layout.setContentsMargins(15, 12, 15, 12)  # Увеличили отступы
        
        
        blur_layout = QHBoxLayout()
        blur_layout.setSpacing(10)
        
        self.blur_label = QLabel(self.translate("Blur Intensity") + ":")
        self.blur_label.setStyleSheet("color: white; font-size: 12px; font-family: Arial, sans-serif;")
        self.blur_label.setMinimumWidth(120)
        self.blur_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)    

        self.lang_label = QLabel(self.translate("Language") + ":")
        self.lang_label.setStyleSheet("color: white; font-size: 12px; font-family: Arial, sans-serif;")
        self.lang_label.setMinimumWidth(80)
        self.lang_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 100)
        self.blur_slider.setValue(50)
        
        self.blur_value_label = QLabel("50")
        self.blur_value_label.setStyleSheet("color: white; font-size: 12px; font-family: Arial, sans-serif;")
        self.blur_value_label.setFixedWidth(30)
        
        self.blur_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: #00b4ff;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b4ff, stop:1 #0078d7);
                border-radius: 2px;
            }
        """)
        
        self.blur_slider.valueChanged.connect(self.update_blur_intensity)
        
        blur_layout.addWidget(self.blur_label)
        blur_layout.addWidget(self.blur_slider)
        blur_layout.addWidget(self.blur_value_label)
        
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(10)
        
        lang_label = QLabel(self.translate("Language") + ":")
        lang_label.setStyleSheet("color: white; font-size: 12px; font-family: Arial, sans-serif;")
        
        self.language_combo = LanguageComboBox()
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.language_combo)
        
        control_layout.addLayout(blur_layout)
        control_layout.addStretch()
        control_layout.addLayout(lang_layout)
        
        content_layout.addWidget(control_card)
        
        status_card = GlassCard()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(25, 15, 15, 15)
        
        self.status_label = QLabel(self.translate("Ready for translation"))
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 500;
                font-family: Arial, sans-serif;
            }
        """)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = ModernProgressBar()
        status_layout.addWidget(self.progress_bar)
        
        content_layout.addWidget(status_card)
        
        log_card = GlassCard()
        log_card.setMinimumHeight(180)
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(10, 10, 10, 10)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: rgba(20, 25, 30, 150);
                color: #e0e0e0;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                padding: 8px;
                font-family: 'Consolas';
                font-size: 14px;
            }
        """)
        log_layout.addWidget(self.log)
        
        content_layout.addWidget(log_card)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.start_button = ModernButton(self.translate("Start"))
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.start_rusification)
        
        self.rollback_button = ModernButton(self.translate("Rollback Changes"))
        self.rollback_button.setObjectName("rollbackButton")
        self.rollback_button.clicked.connect(self.rollback_changes)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.rollback_button)
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_widget)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)
        
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("""
            QSizeGrip {
                width: 12px;
                height: 12px;
                background: transparent;
            }
        """)
    
    def change_language(self, index):
        """Handle language change"""
        self.current_language = self.language_combo.itemData(index)
        
        # Update all UI elements
        self.title_bar.title.setText("Drk multi lang v1.0")
        self.title_bar.about_btn.setText(self.translate("About"))
        self.status_label.setText(self.translate("Ready for translation"))
        self.start_button.setText(self.translate("Start"))
        self.rollback_button.setText(self.translate("Rollback Changes"))
        
    
    # Обновляем метки "Language" и "Blur Intensity"
        self.blur_label.setText(self.translate("Blur Intensity") + ":")
        self.lang_label.setText(self.translate("Language") + ":")
    
        self.update_status(self.translate("Language changed to") + f": {self.language_combo.itemText(index)}")
    
    def update_blur_intensity(self, value):
        self.blur_value_label.setText(str(value))
        alpha = 180 + int((value / 100) * 40)
        self.background.setStyleSheet(f"background-color: rgba(30, 35, 40, {alpha});")
        
        if HAS_WINEXTRAS:
            try:
                QtWin.enableBlurBehindWindow(self, region=self.background.rect(), enable=True)
            except:
                pass
    
    def setup_animations(self):
        self.status_anim = QPropertyAnimation(self.status_label, b"pos")
        self.status_anim.setDuration(1000)
        self.status_anim.setLoopCount(-1)
        self.status_anim.setEasingCurve(QEasingCurve.Linear)
        self.status_anim.setKeyValueAt(0, QPoint(self.status_label.x(), self.status_label.y()))
        self.status_anim.setKeyValueAt(0.5, QPoint(self.status_label.x(), self.status_label.y() - 1))
        self.status_anim.setKeyValueAt(1, QPoint(self.status_label.x(), self.status_label.y()))
        self.status_anim.start()
    
    def show_modern_description(self):
        self.about_dialog = AboutDialog(self)
        self.about_dialog.show()
    
    def clear_log(self):
        self.log.clear()
    
    def update_status(self, message):
        self.log.append(message)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())
        QApplication.processEvents()
    
    def start_rusification(self):
        self.clear_log()
        self.start_button.setEnabled(False)
        self.update_status('> ' + self.translate("Searching for application..."))
        self.simulate_long_task(1)
        self.progress_bar.setValue(20)
        
        driver_path = self.find_driver()
        if driver_path:
            self.update_status('> ' + self.translate("Success. Closing application..."))
            self.simulate_long_task(1)
            self.progress_bar.setValue(40)
            self.kill_process('DeviceDriver.exe')
            
            self.update_status('> ' + self.translate("Processing language files..."))
            self.simulate_long_task(1)
            self.progress_bar.setValue(60)
            self.process_language_files(driver_path)
            
            self.update_status('> ' + self.translate("Launching application..."))
            self.simulate_long_task(1)
            self.progress_bar.setValue(80)
            self.run_driver(driver_path)
            
            self.update_status('> ' + self.translate("Process completed!"))
            self.progress_bar.setValue(100)
        else:
            self.update_status('> ' + self.translate("Application not found!"))
        
        self.start_button.setEnabled(True)
    
    def rollback_changes(self):
        self.clear_log()
        self.rollback_button.setEnabled(False)
        self.update_status('> ' + self.translate("Rolling back changes..."))
        self.simulate_long_task(1)
        self.progress_bar.setValue(20)
        
        driver_path = self.find_driver()
        if driver_path:
            self.update_status('> ' + self.translate("Success. Closing application..."))
            self.simulate_long_task(1)
            self.progress_bar.setValue(40)
            self.kill_process('DeviceDriver.exe')
            
            self.update_status('> ' + self.translate("Removing translation files..."))
            self.simulate_long_task(1)
            self.progress_bar.setValue(60)
            self.rollback_language_files(driver_path)
            
            self.update_status('> ' + self.translate("Launching application..."))
            self.simulate_long_task(1)
            self.progress_bar.setValue(80)
            self.run_driver(driver_path)
            
            self.update_status('> ' + self.translate("Rollback completed!"))
            self.progress_bar.setValue(100)
        else:
            self.update_status('> ' + self.translate("Application not found!"))
        
        self.rollback_button.setEnabled(True)
    
    def simulate_long_task(self, seconds):
        QApplication.processEvents()
        time.sleep(seconds)
    
    def find_driver(self):
        self.update_status(self.translate("Loading cached paths..."))
        cached_paths = self.load_cached_paths()
        self.update_status(self.translate("Cached paths:") + f" {cached_paths}")
        for path in cached_paths:
            if os.path.exists(os.path.join(path, 'DeviceDriver.exe')):
                self.update_status(self.translate("Found in cache:") + f" {path}")
                return path
        
        drives = self.get_available_drives()
        self.update_status(self.translate("Available drives:") + f" {drives}")
        for drive in drives:
            self.update_status(self.translate("Searching in:") + f" {drive}")
            for root, dirs, files in os.walk(drive):
                if 'DeviceDriver.exe' in files:
                    self.update_status(self.translate("File found:") + f" {root}")
                    self.save_cached_path(root)
                    return root
        return None
    
    def get_available_drives(self):
        self.update_status(self.translate("Getting list of available drives..."))
        drives = [f'{d}:\\' for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f'{d}:\\')]
        self.update_status(self.translate("Drives found:") + f" {drives}")
        return drives
    
    def load_cached_paths(self):
        temp_dir = os.getenv('TEMP')
        cache_file = os.path.join(temp_dir, 'rusificator_cache.json')
        self.update_status(self.translate("Checking cache file existence:") + f" {cache_file}")
        if os.path.exists(cache_file):
            self.update_status(self.translate("Cache file found. Loading..."))
            try:
                with open(cache_file, 'r') as file:
                    paths = json.load(file)
                    if not isinstance(paths, list):
                        raise ValueError("Invalid cache file format")
                    self.update_status(self.translate("Loaded paths from cache:") + f" {paths}")
                    return paths
            except (json.JSONDecodeError, ValueError) as e:
                self.update_status(self.translate("Error reading cache file:") + f" {e}")
                self.recreate_cache_file(cache_file)
        else:
            self.update_status(self.translate("Cache file not found."))
        return []
    
    def save_cached_path(self, path):
        self.update_status(self.translate("Saving path to cache:") + f" {path}")
        temp_dir = os.getenv('TEMP')
        cache_file = os.path.join(temp_dir, 'rusificator_cache.json')
        cached_paths = self.load_cached_paths()
        if path not in cached_paths:
            cached_paths.append(path)
        try:
            with open(cache_file, 'w') as file:
                json.dump(cached_paths, file)
            self.update_status(self.translate("Path saved successfully."))
        except Exception as e:
            self.update_status(self.translate("Error saving path:") + f" {e}")
    
    def recreate_cache_file(self, cache_file):
        self.update_status(self.translate("Creating new cache file:") + f" {cache_file}")
        try:
            with open(cache_file, 'w') as file:
                json.dump([], file)
            self.update_status(self.translate("Cache file created successfully."))
        except Exception as e:
            self.update_status(self.translate("Error creating cache file:") + f" {e}")
    
    def kill_process(self, process_name):
        self.update_status(self.translate("Terminating process:") + f" {process_name}")
        try:
            for proc in psutil.process_iter():
                if proc.name() == process_name:
                    proc.terminate()
                    self.update_status(self.translate("Process terminated successfully:") + f" {process_name}")
                    proc.wait()
        except Exception as e:
            self.update_status(self.translate("Error terminating process:") + f" {process_name}: {e}")
    
    def process_language_files(self, driver_path):
        self.update_status(self.translate("Processing files in:") + f" {driver_path}")
        language_path = os.path.join(driver_path, 'language')
        self.update_status(self.translate("Checking directory:") + f" {language_path}")
        os.makedirs(language_path, exist_ok=True)
        lan_files = ['1033.lan']
        self.update_status(self.translate("Reading libraries..."))
        
        lib_filename = f'lib_{self.current_language}.lib'
        
        if getattr(sys, 'frozen', False):
            lib_path = os.path.join(sys._MEIPASS, lib_filename)
        else:
            lib_path = lib_filename
        
        if not os.path.exists(lib_path):
            self.update_status(self.translate("ERROR: Library file not found:") + f" {lib_path}")
            self.update_status(self.translate("Please make sure the library file is in the same folder as the program"))
            return
        
        try:
            with open(lib_path, 'r', encoding='utf-16') as lib_file:
                content = lib_file.read()
                self.update_status(self.translate("Library read successfully."))
        except UnicodeDecodeError:
            self.update_status(self.translate("Error reading library. x0001"))
            return
        
        for lan_file in lan_files:
            file_path = os.path.join(language_path, lan_file)
            try:
                with open(file_path, 'w', encoding='utf-16') as file:
                    file.write(content)
                    self.update_status(self.translate("File written:") + f" {file_path}")
            except PermissionError:
                self.update_status(self.translate("No access to modify:") + f" {lan_file}")
                return
    
    def rollback_language_files(self, driver_path):
        self.update_status(self.translate("Rolling back changes in:") + f" {driver_path}")
        language_path = os.path.join(driver_path, 'language')
        self.update_status(self.translate("Checking directory:") + f" {language_path}")
        if not os.path.exists(language_path):
            self.update_status(self.translate("Directory does not exist."))
            return
        
        translation_files = []
        for root, _, files in os.walk(language_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-16') as f:
                        if any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for char in f.read()):
                            translation_files.append(file_path)
                except UnicodeDecodeError:
                    continue
        
        if translation_files:
            self.update_status(self.translate("Translation found in files:") + f" {translation_files}")
            for file in translation_files:
                os.remove(file)
                self.update_status(self.translate("File deleted:") + f" {file}")
        
        main_dir = os.path.dirname(os.path.abspath(__file__))
        lan_files = ['1033.lan']
        
        for lan_file in lan_files:
            src = os.path.join(main_dir, lan_file)
            dst = os.path.join(language_path, lan_file)
            if os.path.exists(src):
                shutil.copy(src, dst)
                self.update_status(self.translate("File copied:") + f" {dst}")
            else:
                self.update_status(self.translate("File not found:") + f" {src}")
    
    def run_driver(self, driver_path):
        self.update_status(self.translate("Launching application:") + f" {driver_path}")
        try:
            os.startfile(os.path.join(driver_path, 'DeviceDriver.exe'))
            self.update_status(self.translate("Application launched successfully."))
        except Exception as e:
            self.update_status(self.translate("Error launching application:") + f" {e}")
    
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def resizeEvent(self, event):
        self.background.setGeometry(self.rect())
        self.size_grip.move(self.width() - 16, self.height() - 16)
        super().resizeEvent(event)

def main():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, ' '.join(sys.argv), None, 1
            )
            return

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        font = QFont("Arial", 9)
        app.setFont(font)
        
        app.setStyleSheet("""
            QToolTip {
                background-color: rgba(30, 35, 40, 220);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        rus_app = ModernRusificatorApp()
        rus_app.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Critical error: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()