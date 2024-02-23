import sys
import os
import logging
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QProgressBar, QStatusBar, QFileDialog
from PySide6.QtCore import Slot, QThread, Signal, Qt
from PIL import Image
import io
from pytube import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class Worker(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool)

    def __init__(self, playlist_url):
        QThread.__init__(self)
        self.playlist_url = playlist_url
        self.num_videos_processed = 0
        self.total_videos = 0
        self.playlist_info = []
        self.hasErrorOccurred = False

    def run(self):
        try:
            self.playlist_info = self.get_playlist_info(self.playlist_url)
            self.total_videos = len(self.playlist_info)
            self.create_pdf(self.playlist_info)
            if not self.hasErrorOccurred:
                self.finished.emit(True)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            self.status.emit("An error occurred. Please check the URL and try again.")
            self.hasErrorOccurred = True
            self.finished.emit(False)

    def get_playlist_info(self, playlist_url):
        if 'list=' in playlist_url:
            playlist = Playlist(playlist_url)
            for url in playlist.video_urls:
                video = YouTube(url)
                description = video.description if video.description else "\n"
                self.playlist_info.append({
                    'name': playlist.title,
                    'title': video.title,
                    'description': description,
                    'video_id': video.video_id,
                    'thumbnail_url': video.thumbnail_url
                })
        else:
            video = YouTube(playlist_url)
            self.playlist_info.append({
                'name': video.title,
                'title': video.title,
                'description': video.description if video.description else "\n",
                'video_id': video.video_id,
                'thumbnail_url': video.thumbnail_url
            })
        return self.playlist_info

    def create_pdf(self, playlist_info):
        try:
            pdf = FPDF('P', 'mm', 'A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 30)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 60, playlist_info[0]['name'], 0, 1, 'C', True)

            # Use sys._MEIPASS for PyInstaller
            thumbnails_dir = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__))), 'thumbnails')
            os.makedirs(thumbnails_dir, exist_ok=True)

            for index, video in enumerate(playlist_info):
                self.num_videos_processed += 1
                progress = (self.num_videos_processed / self.total_videos) * 100
                self.progress.emit(int(progress))
                self.status.emit(f"Processing video {self.num_videos_processed} of {self.total_videos}: {video['title']}")
                pdf.add_page()
                response = requests.get(video['thumbnail_url'])
                thumbnail_path = os.path.join(thumbnails_dir, f"{video['video_id']}.jpg")
                with open(thumbnail_path, 'wb') as f:
                    f.write(response.content)
                with Image.open(io.BytesIO(response.content)) as img:
                    width, height = img.size
                aspect_ratio_width = 170
                aspect_ratio_height = aspect_ratio_width * 9 / 16
                pdf.image(thumbnail_path, x=10, y=20, w=aspect_ratio_width, h=aspect_ratio_height)
                pdf.ln(120)
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, f"{video['title']} \n", 0, 1, 'C')
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 10, f"{video['description']} \n")
                pdf.ln()
                pdf.set_font("Arial", "", 10)
                transcript = self.get_transcript(video['video_id'])
                for paragraph in transcript:
                    pdf.multi_cell(0, 10, paragraph)
                    pdf.ln(10)
                pdf.ln(40)

            self.pdf_data = pdf.output(dest='S').encode('latin1')
        except Exception as e:
            logging.error(f"Error creating PDF: {str(e)}")
            self.status.emit("Oops! We couldn't create the PDF. Please try again later.")
            self.hasErrorOccurred = True

    def get_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            paragraphs = []
            current_paragraph = ""
            previous_time = None
            time_gap_threshold = 5.0

            for entry in transcript:
                if previous_time is not None:
                    time_gap = entry['start'] - previous_time
                    if time_gap > time_gap_threshold:
                        if current_paragraph.strip():
                            paragraphs.append(current_paragraph.strip())
                        current_paragraph = ""
                current_paragraph += " " + entry['text']
                previous_time = entry['start']

            if current_paragraph.strip():
                paragraphs.append(current_paragraph.strip())

            return paragraphs
        except Exception as e:
            logging.warning(f"Unable to fetch transcript for video ID {video_id}. Error: {str(e)}")
            return ["Transcript not available."]

class PlaylistToPDFApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Playlist to PDF')
        self.setGeometry(100, 100, 800, 100)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.label = QLabel("Enter the YouTube Playlist or Video URL:")
        layout.addWidget(self.label)

        self.input_url = QLineEdit()
        layout.addWidget(self.input_url)

        self.process_button = QPushButton("Convert to Book")
        self.process_button.clicked.connect(self.process_playlist)
        layout.addWidget(self.process_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        central_widget.setLayout(layout)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.worker = Worker("")
        self.worker.finished.connect(self.on_finished, Qt.UniqueConnection)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)

    @Slot()
    def process_playlist(self):
        self.statusBar.clearMessage()
        self.progress_bar.setValue(0)
        playlist_url = self.input_url.text()
        self.worker.playlist_url = playlist_url
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.statusBar.showMessage(status)

    @Slot(bool)
    def on_finished(self, success):
        if success:
            self.progress_bar.setValue(100)
            self.statusBar.showMessage("PDF Creation Complete!")
            self.save_pdf()
        else:
            self.statusBar.showMessage("An error occurred during PDF creation. Please check the logs for more details.")

    def save_pdf(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # Set the file name to the playlist name or a default name if not available
        playlist_name = self.worker.playlist_info[0]['name'] if self.worker.playlist_info else "YouTubePlaylist"
        default_file_name = f"{playlist_name}.pdf"
        fileName, _ = QFileDialog.getSaveFileName(self, "Save PDF As", default_file_name, "PDF Files (*.pdf);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'wb') as f:
                f.write(self.worker.pdf_data)
            self.statusBar.showMessage(f"PDF saved at: {fileName}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlaylistToPDFApp()
    ex.show()
    sys.exit(app.exec())
