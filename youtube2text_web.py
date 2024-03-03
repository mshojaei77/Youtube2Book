import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from yt_dlp import YoutubeDL
import re

# Include the Vazirmatn font via CDN
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
    """,
    unsafe_allow_html=True
)

st.title('🎥 YouTube Transcript Extractor')

def extract_video_id(video_url: str) -> str:
    """Extracts the video ID from a YouTube URL."""
    pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.search(pattern, video_url)
    if match is None:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
        return None
    return match.group(6)

def fetch_transcript(video_id: str) -> str:
    """Fetches the transcript of a YouTube video and formats it using TextFormatter."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        return formatted_transcript
    except Exception as e:
        if "No transcript found" in str(e):
            st.error("No transcript found for this video.")
        else:
            st.error(f"Failed to fetch transcript: {e}")
        return None

def translate_to_persian(video_id: str) -> str:
    """Translates the transcript to Persian using YouTube Transcript API and formats it using TextFormatter."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        translated_transcript = transcript.translate('fa').fetch()
        formatter = TextFormatter()
        formatted_translated_transcript = formatter.format_transcript(translated_transcript)
        return formatted_translated_transcript
    except Exception as e:
        st.error(f"Failed to translate transcript: {e}")
        return None

def get_video_info(video_url: str) -> tuple:
    """Extracts video information using yt-dlp."""
    opts = dict()
    with YoutubeDL(opts) as yt:
        info = yt.extract_info(video_url, download=False)
        title = info.get("title", "")
        description = info.get("description", "")
        thumbnails = info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        return title, description, thumbnail_url

video_url_input = st.text_input("Enter YouTube Video URL", "")
translate_to_persian_checkbox = st.checkbox("Translate Transcript to Persian using YouTube Transcript API")
submit_button = st.button("Extract Transcript")

if submit_button and video_url_input:
    video_id = extract_video_id(video_url_input)

    if video_id:
        try:
            video_title, video_description, video_thumbnail = get_video_info(video_url_input)
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            with st.spinner('Fetching transcript...'):
                transcript_text = fetch_transcript(video_id)

            if translate_to_persian_checkbox:
                with st.spinner('Translating to Persian...'):
                    translated_text = translate_to_persian(video_id)
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
    else:
        st.error("Please enter a valid YouTube video URL.")

st.markdown("""
<div class="footer">
    <p>Powered by: YouTube's Automatic Speech Recognition (ASR) technology.</p>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p>Developer: <a href="https://github.com/mshojaei77" target="_blank">M.Shojaei</a></p>
</div>
""", unsafe_allow_html=True)
