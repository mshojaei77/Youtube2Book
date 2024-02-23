# YouTube Playlist to PDF Converter

## Overview
This application allows you to convert YouTube playlists or video URLs into a comprehensive PDF document. The PDF includes information such as video titles, descriptions, and transcripts.

## Features

- Access videos from a YouTube playlist
- Extracts transcripts from each video
- Creates a PDF document with the playlist's information
- Includes video thumbnails in the PDF
- Logs progress and errors for easy troubleshooting

## Demo
![Application Demo](https://github.com/mshojaei77/Youtube2Book/assets/76538971/2894dda3-0fa9-47dc-a4fa-cc10fef1dbe7)

For example, you can view the [output PDF file](https://github.com/mshojaei77/Youtube2Book/blob/main/Let's%20build%20the%20GPT%20Tokenizer.pdf) generated for [this video](https://www.youtube.com/watch?v=zduSFxRajkE&t=4s) ("Let's build the GPT Tokenizer") from Andrej Karpathy.

## How to Use
1. Download the [Windows version](https://github.com/mshojaei77/Youtube2Book/releases/download/GUI/YTplaylist2Book.exe).
2. Run the executable file.
3. Enter the YouTube playlist or video URL.
4. Click on the "Convert to Book" button.
5. Wait for the process to complete.
6. Save the generated PDF.

## Dependencies
- PySide6
- requests
- PIL
- io
- pytube
- youtube_transcript_api
- fpdf

## Code Structure
The application is built using Python and PySide6. The main functionalities are divided into two classes: `Worker` and `PlaylistToPDFApp`. 

- `Worker`: This class is responsible for fetching information, creating a PDF, and managing the conversion process in a separate thread.

- `PlaylistToPDFApp`: This class handles the GUI components, user input, and interaction with the `Worker` class.

## How to Build
Ensure you have Python installed, and install the required dependencies using:
```bash
pip install PySide6 requests Pillow pytube youtube_transcript_api fpdf
```

Run the application using:
```bash
python your_script_name.py
```

## Notes
- The application uses external libraries to fetch video details, download thumbnails, and retrieve video transcripts.
- Thumbnails are stored in a 'thumbnails' directory.
- Transcript generation is handled by the YouTubeTranscriptApi.

