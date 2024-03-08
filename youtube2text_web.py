import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from yt_dlp import YoutubeDL
import re
import g4f


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

def structure_with_ai(transcript_text: str) -> str:
    request = f'''
        To enhance the readability, engagement, and educational value of the provided YouTube video transcript and description, please reformat the content using Markdown. The goal is to create a structured document that is both informative and accessible to the audience.

        ### Transcript:

        ```
        {transcript_text}
        ```

        ### Video Description:

        ```
        {video_description}
        ```

        ### Instructions for Transformation:

        1. **Structure and Tone**: Organize the content in a manner that aligns with the video's subject matter, ensuring clarity and engagement. Incorporate emojis, tables, and code blocks where relevant to improve the presentation.

        2. **Preservation of Meaning**: Ensure that the original content's essence is preserved during the transformation. Avoid any omission or truncation of crucial information.

        3. **Incorporation of Links**: Embed URLs from the video description as clickable links within the Markdown document. Verify all links are functional and correctly formatted.

        4. **Engagement Elements**: Utilize tables and code blocks to highlight key points and illustrate examples. This strategy will help maintain audience interest and facilitate comprehension.

        5. **Review and Feedback**: Upon completion, review the transformed content to ensure it meets the specified criteria and provide feedback for any necessary modifications.

        ### Final Output Requirements:

        Please submit the final, transformed content in Markdown format, adhering strictly to the guidelines outlined. The aim is to produce a comprehensive, engaging, and educational document that effectively communicates the video's content.

        Additionally, ensure to correct and complete the transcript text if it contains errors, without omitting or altering important information. You may add code examples and additional context as long as it does not compromise the original meaning of the content.
    '''

    # Define the list of providers
    providers = [g4f.Provider.FreeChatgpt, g4f.Provider.Liaobots, g4f.Provider.Koala, g4f.Provider.Llama2, g4f.Provider.ChatForAi]

    for prv in providers:
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
        except Exception as e:
            st.warning(f"Error with provider {prv}: {e}")
            continue  # Try the next provider

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
                    structured_transcript = structure_with_ai(transcript_text)
                    st.markdown(structured_transcript)
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

