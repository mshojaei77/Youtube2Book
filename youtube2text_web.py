import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import re

def extract_video_id(video_url):
    video_id = re.search(r'(?<=v=)[^&#]+', video_url)
    if video_id is None:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
        st.stop()
    return video_id.group()

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join(entry['text'] for entry in transcript)
    except YouTubeTranscriptApi.NoTranscriptFound:
        st.error("No transcript found for this video.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to fetch transcript: {e}")
        st.stop()

def get_video_thumbnail(video_url):
    video_id = extract_video_id(video_url)
    yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
    return yt.thumbnail_url

st.title('YouTube Transcript Extractor')

video_url_input = st.text_input("Enter YouTube Video URL", "")
submit_button = st.button("Extract Transcript")

if submit_button and video_url_input:
    try:
        video_id = extract_video_id(video_url_input)
        yt = YouTube(video_url_input)
        video_title = yt.title
        video_description = yt.description
        video_url = yt.watch_url
        video_thumbnail = get_video_thumbnail(video_url)

        with st.spinner('Fetching transcript...'):
            transcript_text = fetch_transcript(video_id)

        st.markdown(f"## [{video_title}]({video_url})")
        st.image(video_thumbnail, caption="Video Thumbnail", use_column_width=True)
        if video_description: st.markdown(f"### {video_description}")
        st.markdown(transcript_text)

    except Exception as e:
        st.error(f"An error occurred: {e}")