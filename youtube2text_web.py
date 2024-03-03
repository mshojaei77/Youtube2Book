import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
import re
from googletrans import Translator

def extract_video_id(video_url):
    video_id = re.search(r'(?<=v=)[^&#]+', video_url)
    if video_id is None:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
        st.stop()
    return video_id.group()

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "  ".join(entry['text'] for entry in transcript)
    except YouTubeTranscriptApi.NoTranscriptFound:
        st.error("No transcript found for this video.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to fetch transcript: {e}")
        st.stop()

def translate_to_persian(text):
    translator = Translator()
    chunk_size = 5000  # Adjust the chunk size as needed
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    translated_chunks = [translator.translate(chunk, dest='fa').text for chunk in chunks]
    return " ".join(translated_chunks)

def get_video_info(video_url):
    opts = dict()
    with YoutubeDL(opts) as yt:
        info = yt.extract_info(video_url, download=False)
        title = info.get("title", "")
        description = info.get("description", "")
        thumbnails = info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        return title, description, thumbnail_url

st.title('🎥 YouTube Transcript Extractor')

video_url_input = st.text_input("Enter YouTube Video URL", "")
translate_to_persian_checkbox = st.checkbox("Translate Transcript to Persian using Google Translate")
submit_button = st.button("Extract Transcript")

if submit_button and video_url_input:
    try:
        video_id = extract_video_id(video_url_input)
        video_title, video_description, video_thumbnail = get_video_info(video_url_input)
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        with st.spinner('Fetching transcript...'):
            transcript_text = fetch_transcript(video_id)

        if translate_to_persian_checkbox:
            with st.spinner('Translating to Persian...'):
                translated_text = translate_to_persian(transcript_text)
                st.markdown(f'''
                <div dir="rtl" style="text-align: right;">
                    <p style="margin-bottom: 0.5rem;"> </p>
                    <article class="media">
                        <p>{translated_text}</p>
                    </article>
                </div>
                ''', unsafe_allow_html=True)

        else:
            if video_title: st.markdown(f"## {video_title}")
            st.markdown(f" ``` \n{transcript_text}\n ``` ")
        
        with st.sidebar:
            st.markdown(f"## Video Information: ")
            if video_title: st.markdown(f"### [{video_title}]({video_url})")
            if video_thumbnail: st.image(video_thumbnail, use_column_width=True)
            if video_description: st.markdown(f" {video_description}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

