# YouTube Transcript Extractor

## Overview

The YouTube Transcript Extractor is a Streamlit web application designed to extract and display the transcripts of YouTube videos directly within the app. This tool is useful for individuals who need to access the content of YouTube videos without watching them or for those who wish to analyze the content programmatically.

## Demo

You can access a live demo of the YouTube Transcript Extractor at [https://youtube2text.streamlit.app/](https://youtube2text.streamlit.app/).

## Features

- **Extract Transcripts**: Automatically fetches the transcript of a given YouTube video URL.
- **Display Video Details**: Shows the video title, description, and thumbnail.
- **Markdown Formatting**: Displays the transcript in a structured and readable format using Markdown.
- **Error Handling**: Provides clear error messages for invalid URLs or videos without transcripts.

## Getting Started

### Prerequisites

Ensure you have Python installed on your system. If not, download and install it from [https://www.python.org/downloads/](https://www.python.org/downloads/).

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/youtube-transcript-extractor.git
cd youtube-transcript-extractor
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

### Running the Application

To start the Streamlit app, run the following command in your terminal:

```bash
streamlit run app.py
```

This command will launch the app in your default web browser.

## Usage

1. Enter the YouTube video URL in the input field.
2. Click the "Extract Transcript" button.
3. The app will fetch the video details and transcript, displaying them in a structured format.

## Contributing

Contributions are welcome! If you've found a bug or have a feature request, please open an issue on GitHub. If you'd like to contribute code, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Streamlit for providing an easy way to build web applications with Python.
- `youtube_transcript_api` for enabling the extraction of YouTube video transcripts.
- `pytube` for fetching video details and thumbnails.

## Contact

For any questions, comments, or suggestions, please feel free to reach out at [your-email@example.com](mailto:your-email@example.com).

## Future Enhancements

- Support for more languages and transcript formats.
- Improved error handling and user interface.
- Integration with other video platforms.

---

This README is designed to provide a comprehensive overview of the YouTube Transcript Extractor application, including installation instructions, usage details, and information on contributing to the project.
