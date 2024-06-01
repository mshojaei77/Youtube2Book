import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from yt_dlp import YoutubeDL
import re
from openai import OpenAI
from groq import Groq

FREE_API_KEY =st.secrets["api_key"]
sys_prompt =  '''
            You are an AI assistant tasked with taking video transcripts and structuring them into formatted blog posts. Your goal is to take the raw text from a video transcript and transform it into a well-organized, engaging blog post.
            When given a video transcript, you should perform the following steps:

            1. Review the full transcript and identify the key topics, themes, and main points covered in the video. Ensure you fully understand the purpose and context of the video content.
            2. Organize the transcript content into a logical structure for the blog post, including an introduction, body paragraphs, and conclusion. Group related points together into cohesive sections.
            3. Write concise topic sentences and transitions to guide the reader through the blog post flow. Ensure the overall structure covers the full scope and purpose of the original video.
            4. Add section headings, subheadings, and formatting (e.g. bold, italics, bullet lists) to make the content easy to scan and digest. Utilize tables, code blocks, and other dynamic elements where appropriate to improve the presentation.
            5. Condense verbose or repetitive transcript phrasing into more concise, polished writing. Correct any grammar, spelling, or punctuation issues present in the original transcript text.
            6. Incorporate relevant images, screenshots, or other visual elements from the video to supplement the written content.
            7. Embed URLs from the video description as clickable links within the Markdown document, inserting them in the appropriate places related to the section content.
            8. Proofread the full blog post to ensure it is free of any remaining errors or issues.
            9. Provide a title for the blog post that captures the main topic in an engaging way.
            The final blog post should be between 500-800 words, with a clear and cohesive structure that transforms the raw video transcript into an informative and compelling read. Your writing style should be conversational yet authoritative, matching the tone and level of the original video content.
    '''


st.set_page_config(
    page_title="Smart Transcription",
    page_icon="🎥",
    layout="wide",
    menu_items={
        'Get Help': 'https://twitter.com/realshojaei',
        'Report a bug': "https://github.com/mshojaei77/Youtube2Book/issues",
    }
)

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

def structure_free(transcript_text: str, video_description: str) -> str:
    try:
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
        client = Groq(api_key=FREE_API_KEY)
        completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_prompt},
                        {"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                )
        return completion.choices[0].message.content
    except Exception as e :
        return None

def structure_with_gpt(transcript_text: str, video_description: str, api_key: str) -> str:
    prompt = f'''
            rewrite following Video Transcript as a blog post with engaging tone, format the output using Markdown also embed video description in middle of transcript to understand the video better:

                here is the **Video Transcript**:
                """{transcript_text}"""
            
                here is the **Video Description**:
                {video_description}
    '''
    client = OpenAI(
        api_key=api_key,
    )
    completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                { "role": "user", "content": prompt}]
        )
    return completion.choices[0].message.content


with st.sidebar:
  st.header('🎥 YouTube Smart Transcription', divider='gray')
  video_url_input = st.text_input("Enter YouTube Video URL")
  method = st.radio(
      "Choose the Extraction method",
      ["Simple", "Llama",":rainbow[GPT-4o]"],
      captions = ["Base Transcript", "Enhance with Llama 3", "Enhance With GPT-4o (api key required)"])
  if method == ':rainbow[GPT-4o]':
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

            if method == 'Llama' and transcript_text:
                with st.spinner('Structuring Using Llama 3 70b by Groq ...'):
                    structured_transcript = structure_free(transcript_text, video_description)
                    if video_title and  structured_transcript: st.header(video_title, divider='rainbow')
                    if video_thumbnail and  structured_transcript: st.image(video_thumbnail, use_column_width="auto")
                    if structured_transcript:
                        st.markdown(structured_transcript)
                    else:
                        st.markdown("The free version is **limited** , try again after 1 minute or use **GPT-4o** \n __Groq Rate Limit__")
            if method == ':rainbow[GPT-4o]':
                with st.spinner('Structuring Using GPT-4o ...'):
                    structured_transcript = structure_with_gpt(transcript_text, video_description,OPENAI_API_KEY)
                    if video_title: st.header(video_title, divider='rainbow')
                    if video_thumbnail: st.image(video_thumbnail, use_column_width="auto")
                    st.markdown(structured_transcript)
            if method == 'Simple' and transcript_text:
                if video_title: st.header(video_title, divider='rainbow')
                if video_thumbnail: st.image(video_thumbnail,use_column_width="auto",)
                st.markdown(f" {transcript_text} ")
                      
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube video URL.")
