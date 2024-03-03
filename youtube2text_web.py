import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
import re
from googletrans import Translator

def extract_video_id(video_url):
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})', video_url)
    if match is None:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
        return None
    return match.group(6)

def fetch_transcript(video_id):
    """Fetches the transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry['text'] for entry in transcript)
    except Exception as e:
        if "No transcript found" in str(e):
            st.error("No transcript found for this video.")
        else:
            st.error(f"Failed to fetch transcript: {e}")
        return None

def translate_to_persian(text):
    """Translates text to Persian using Google Translate."""
    translator = Translator()
    chunk_size = 5000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    translated_chunks = [translator.translate(chunk, dest='fa').text for chunk in chunks]
    return " ".join(translated_chunks)

def get_video_info(video_url):
    """Extracts video information using yt-dlp."""
    opts = dict()
    with YoutubeDL(opts) as yt:
        info = yt.extract_info(video_url, download=False)
        title = info.get("title", "")
        description = info.get("description", "")
        thumbnails = info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        return title, description, thumbnail_url

# Include the Vazirmatn font via CDN
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
    """,
    unsafe_allow_html=True
)

st.title('🎥 YouTube Transcript Extractor')

video_url_input = st.text_input("Enter YouTube Video URL", "")
translate_to_persian_checkbox = st.checkbox("Translate Transcript to Persian using Google Translate")
submit_button = st.button("Extract Transcript")

if submit_button and video_url_input:
    video_id = extract_video_id(video_url_input)

    try:
        video_title, video_description, video_thumbnail = get_video_info(video_url_input)
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        with st.spinner('Fetching transcript...'):
            transcript_text = fetch_transcript(video_id)

        if translate_to_persian_checkbox:
            with st.spinner('Translating to Persian...'):
                translated_text = translate_to_persian(transcript_text)
                st.markdown(f'''
                <div dir="rtl" style="text-align: right; font-family: 'Vazirmatn', sans-serif;">
                    <p style="margin-bottom: 0.5rem;"> </p>
                    <article class="media">
                        <p>{translated_text}</p>
                    </article>
                </div>
                ''', unsafe_allow_html=True)

        else:
            if video_title: st.markdown(f"## {video_title}")
            st.markdown(f" {transcript_text} ")
        
        with st.sidebar:
            st.markdown(f"## Video Information: ")
            if video_title: st.markdown(f"### [{video_title}]({video_url})")
            if video_thumbnail: st.image(video_thumbnail, use_column_width=True)
            if video_description: st.markdown(f" {video_description}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
