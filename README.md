# YouTube Transcript Extractor

## Overview

The YouTube Transcript Extractor is a dual-platform application designed to extract transcripts from YouTube videos, providing both a web-based interface through Streamlit and a desktop application built with PySide6. This tool is useful for individuals who need to access the content of YouTube videos without watching them or for those who wish to analyze the content programmatically.

## Features

- **Extract Transcripts**: Automatically fetches the transcript of a given YouTube video URL.
- **Display Video Details**: Shows the video title, description, and thumbnail.
- **Markdown Formatting**: Displays the transcript in a structured and readable format using Markdown.
- **Error Handling**: Provides clear error messages for invalid URLs or videos without transcripts.
- **Web-Based Interface**: Accessible via web browsers, ideal for users without the need for desktop applications.
- **Desktop Application**: A standalone Windows application for users who prefer a desktop interface.
- **PDF Output**: Generates a PDF report of the extracted transcript for offline use or sharing.

## Web App

### Demo

You can access a live demo of the YouTube Transcript Extractor at [https://youtube2text.streamlit.app/](https://youtube2text.streamlit.app/).

### Installation

To run the web app locally, ensure you have Python and Streamlit installed. If not, install them using pip:

```bash
pip install streamlit youtube_transcript_api pytube
```

Then, clone the repository and run the app:

```bash
streamlit run app.py
```

This command will launch the app in your default web browser.

## Desktop Application

### Download

For Windows users, a standalone executable is available for download. Simply visit the following link to download the application:

[Download YouTube2Text Desktop Windows App](https://github.com/mshojaei77/Youtube2Book/releases/download/GUI/YTplaylist2Book.exe)

### Installation

If you wish to run the application from source, ensure you have Python installed and then install the required packages using pip:

```bash
pip install PySide6 pytube youtube_transcript_api fpdf
```

### PDF Output

The desktop application allows users to generate a PDF report of the extracted transcript. This feature is particularly useful for users who need to share the transcript with others or use it offline.
[Output Example](https://github.com/mshojaei77/Youtube2Book/blob/main/Let's%20build%20the%20GPT%20Tokenizer.pdf)

## Usage

### Web App

1. Enter the YouTube video URL in the input field.
2. Click the "Extract Transcript" button.
3. The app will fetch the video details and transcript, displaying them in a structured format.

### Desktop Application

1. Launch the application by running `youtube2text_Desktop.py`.
2. Enter the YouTube Playlist or Video URL in the provided field.
3. Click the "Convert to Book" button to start the conversion process.
4. Save the generated PDF to your preferred location.

## Development

This application is built using Python, Streamlit for the web app, and PySide6 for the desktop application. It leverages `pytube` for downloading video thumbnails, `youtube_transcript_api` for fetching video transcripts, and `fpdf` for generating PDF documents in the desktop application.

## Contributing

Contributions are welcome! If you've found a bug or have a feature request, please open an issue on GitHub. If you'd like to contribute code, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions, comments, or suggestions, please feel free to reach out at [your-email@example.com](mailto:your-email@example.com).

---

The YouTube Transcript Extractor is a versatile tool that bridges the gap between online content and offline accessibility, making YouTube content more accessible for those who prefer to read in a more traditional format. Whether you're a developer looking to integrate YouTube content analysis into your projects or a user seeking a convenient way to access YouTube video transcripts, this tool is designed to meet your needs.
