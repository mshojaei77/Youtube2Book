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
read following YouTube Video Transcript and explain it to me in engaging tone, format the output using Markdown also use video description to understand the video better:

        
            **Video Transcript:**
            ```transcript
            {transcript_text}
            ```
            **Video Description:**
            ```description
            {video_description}
            ```
        
- please Expand and Complete the content to a full tutorial of the video's subject matter. Utilize emojis, tables, and code blocks where appropriate to improve the presentation and make the content more dynamic.
- also make sure all of transcript and video purpose will be covered.
- Embed URLs from the video description as clickable links within the Markdown document in right place (related to section). 
- Additionally, ensure to correct and complete the transcript text if it contains grammar issues or anything wrong, You should add examples and additional context from your own knowledge.
- the final output most be a clean and engaging Markdown.
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
