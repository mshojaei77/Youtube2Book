import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from yt_dlp import YoutubeDL
import re
from openai import OpenAI
import clipboard


OPENROUTER_API_KEY =st.secrets["api_key"]

st.set_page_config(
    page_title="Smart Transcription",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://twitter.com/realshojaei',
        'Report a bug': "https://github.com/mshojaei77/Youtube2Book/issues",
    }
)
st.title('🎥 YouTube Smart Transcription')





transcript_extracted = False

def on_copy_click(text):
    clipboard.copy(text)
    
def extract_video_id(video_url: str) -> str:
    pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.search(pattern, video_url)
    if match is None:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
        return None
    return match.group(6)

def fetch_transcript(video_id: str) -> str:
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

def get_video_info(video_url: str) -> tuple:
    opts = dict()
    with YoutubeDL(opts) as yt:
        info = yt.extract_info(video_url, download=False)
        title = info.get("title", "")
        description = info.get("description", "")
        thumbnails = info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        return title, description, thumbnail_url

def structure_with_mistral(transcript_text: str, video_description: str) -> str:
    prompt = f'''
    rewrite following Video Transcript as a blog post with engaging tone, format the output using Markdown also embed video description in middle of transcript to understand the video better:

        here is the **Video Transcript**:
        """{transcript_text}"""
    
        here is the **Video Description**:
        {video_description}

    - Utilize tables, and code blocks where appropriate to improve the presentation and make the content more dynamic.
    - Make sure all of transcript and video purpose will be covered.
    - Embed URLs from the video description as clickable links within the Markdown document in right place (related to section).
    - Ensure to correct the transcript text if it contains grammar issues or anything wrong.
    '''
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    completion = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{ "role": "user", "content": prompt}]
        )
    return completion.choices[0].message.content

def structure_with_gpt(transcript_text: str, video_description: str, api_key: str) -> str:
    prompt = f'''
    rewrite following Video Transcript as a blog post with engaging tone, format the output using Markdown also embed video description in middle of transcript to understand the video better:

        here is the **Video Transcript**:
        """{transcript_text}"""
    
        here is the **Video Description**:
        {video_description}

    - Utilize tables, and code blocks where appropriate to improve the presentation and make the content more dynamic.
    - Make sure all of transcript and video purpose will be covered.
    - Embed URLs from the video description as clickable links within the Markdown document in right place (related to section).
    - Ensure to correct the transcript text if it contains grammar issues or anything wrong.
    '''
    client = OpenAI(
        api_key=api_key,
    )
    completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[{ "role": "user", "content": prompt}]
        )
    return completion.choices[0].message.content



video_url_input = st.text_input("Enter YouTube Video URL")
method = st.radio(
    "Choose the Extraction method",
    ["Simple", "Mistral",":rainbow[GPT-4]"],
    captions = ["Base Transcript", "Enhance with Mistral AI (free)", "Enhance With GPT-4 (api key required)"])
if method == ':rainbow[GPT-4]':
    OPENAI_API_KEY = st.text_input('OpenAI api key')
submit_button = st.button("Extract Transcript")


    

    

if submit_button and video_url_input:
    video_id = extract_video_id(video_url_input)
    if video_id:
        try:
            video_title, video_description, video_thumbnail = get_video_info(video_url_input)
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            with st.spinner('Fetching transcript...'):
                transcript_text = fetch_transcript(video_id)
                if transcript_text:
                    transcript_extracted = True

            if method == 'Mistral' and transcript_text:
                with st.spinner('Structuring Using Mistral 7b ...'):
                    structured_transcript = structure_with_mistral(transcript_text, video_description)
                    st.button("copy to clipboard", on_click=on_copy_click, args=(structured_transcript))
                    st.markdown(structured_transcript)
            if method == ':rainbow[GPT-4]':
                with st.spinner('Structuring Using GPT-4 ...'):
                    structured_transcript = structure_with_gpt(transcript_text, video_description,OPENAI_API_KEY)
                    st.button("copy to clipboard", on_click=on_copy_click, args=(structured_transcript))
                    st.markdown(structured_transcript)
            if method == 'Simple' and transcript_text:
                st.button("copy to clipboard", on_click=on_copy_click, args=(structured_transcript))
                st.markdown(f" {transcript_text} ")
                        
            with st.sidebar:
                st.markdown(f"## Video Description: ")
                if video_title: st.markdown(f"### [{video_title}]({video_url})")
                if video_thumbnail: st.image(video_thumbnail, use_column_width=True)
                if video_description: st.markdown(f" {video_description}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube video URL.")
