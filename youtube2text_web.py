import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from yt_dlp import YoutubeDL
import re
import g4f
import time
from requests.exceptions import HTTPError


# Include the Vazirmatn font via CDN
st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" type="text/css" />
    """,
    unsafe_allow_html=True
)

st.title('🎥 YouTube Transcript Extractor')

transcript_extracted = False

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

def translate_to_persian(video_id: str) -> str:
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
    opts = dict()
    with YoutubeDL(opts) as yt:
        info = yt.extract_info(video_url, download=False)
        title = info.get("title", "")
        description = info.get("description", "")
        thumbnails = info.get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None
        return title, description, thumbnail_url

def structure_with_ai(transcript_text: str, video_description: str) -> str: 
    request = f'''
transform the provided YouTube video transcript and description into a structured, engaging, and educational format using Markdown:

        **Video Description:**
            ```
            {video_description}
            ```Description
        **Video Transcript:**
            ```Transcript
            {transcript_text}
            ```
        
- Expand the content to align with the video's subject matter. Utilize emojis, tables, and code blocks where appropriate to improve the presentation and make the content more dynamic. aldo Avoid omitting or truncating important information. 

- Embed URLs from the video description as clickable links within the Markdown document in right place (related to section). 

- Additionally, ensure to correct and complete the transcript text if it contains grammar issues or anything wrong, You may add examples and additional context from your own knowledge.            
    ''' 



    providers = [g4f.Provider.FreeChatgpt, g4f.Provider.Liaobots, g4f.Provider.Koala, g4f.Provider.Llama2, g4f.Provider.ChatForAi]

    max_retries = 3
    backoff_factor = 2

    for prv in providers:
        retries = 0
        while retries < max_retries:
            try:
                response = g4f.ChatCompletion.create(
                    model=g4f.models.gpt_4,
                    provider=prv,
                    messages=[
                        {"role": "user", "content": request}
                    ]
                )
                messages = "".join(response)
                return messages  # Return the response if successful
            except HTTPError as http_err:
                if http_err.response.status_code >= 500:  # Retry only on server errors
                    retries += 1
                    time.sleep((backoff_factor ** retries) / 10)
                    st.warning(f"Retry {retries}/{max_retries} for provider {prv} due to server error.")
                else:
                    break  # Don't retry on client errors
            except Exception as e:
                st.warning(f"Error with provider {prv}: {e}")
                break  # Break and try the next provider
        else:
            st.error(f"Provider {prv} failed after {max_retries} retries.")

    # If all providers fail, display an error message
    st.error("Failed to structure the transcript with all providers.")
    return None


video_url_input = st.text_input("Enter YouTube Video URL", "")
structure_with_ai_checkbox = st.checkbox("✨ Structure to Markdown format with AI")
translate_to_persian_checkbox = st.checkbox("🌏 Extract Persian Transcript")
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

            if translate_to_persian_checkbox and transcript_text:
                with st.spinner('Translating to Persian...'):
                    translated_text = translate_to_persian(video_id)
                    translated_bytes = translated_text.encode('utf-8')
                    st.download_button(
                        label="Download Translation",
                        data=translated_bytes,
                        file_name='Translation.txt',
                        mime='text/plain',
                    )
                    st.markdown(f'''
                    <div dir="rtl" style="text-align: right; font-family: 'Vazirmatn', sans-serif;">
                        <p style="margin-bottom: 0.5rem;"> </p>
                        <article class="media">
                            <p>{translated_text}</p>
                        </article>
                    </div>
                    ''', unsafe_allow_html=True)
                                    


            if structure_with_ai_checkbox and transcript_text:
                with st.spinner('Structuring Using AI... (may take a while)'):
                    structured_transcript = structure_with_ai(transcript_text, video_description)
                    structured_bytes = structured_transcript.encode('utf-8')
                    st.download_button(
                        label="Download Markdown",
                        data=structured_bytes,
                        file_name='Markdown.txt',
                        mime='text/plain',
                    )
                    st.markdown(structured_transcript)
            else:
                if video_title: st.markdown(f"## {video_title}")
                st.markdown(f" {transcript_text} ")
                        
            with st.sidebar:
                transcript_bytes = transcript_text.encode('utf-8')
                st.download_button(
                        label="Download Transcript",
                        data=transcript_bytes,
                        file_name='Transcript.txt',
                        mime='text/pdf',
                )
                st.markdown(f"## Video Information: ")
                if video_title: st.markdown(f"### [{video_title}]({video_url})")
                if video_thumbnail: st.image(video_thumbnail, use_column_width=True)
                if video_description: st.markdown(f" {video_description}")


        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube video URL.")
