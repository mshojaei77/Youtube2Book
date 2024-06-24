import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from yt_dlp import YoutubeDL
import re
from openai import OpenAI
from groq import Groq

FREE_API_KEY =st.secrets["api_key"]
sys_prompt =  '''
You are an expert AI content creator specializing in transforming video transcripts into comprehensive, in-depth blog posts. Your task is to take raw video transcript text and craft it into a thorough, long-form article that captures every detail from the original content. Your goal is to create the most informative and valuable resource possible on the topic. Follow these detailed steps:

1. Clear and Concise Writing:
   - Meticulously review the entire transcript, ensuring no detail is overlooked.
   - Transform the transcript into polished, engaging prose that is easy to understand.
   - Use plain language and avoid unnecessary jargon.
   - Break down complex concepts into digestible chunks.
   - Use short paragraphs and sentences for readability.
   - Incorporate detailed analogies or metaphors to explain complex concepts.

2. Practical Examples and Code Snippets:
   - Include multiple relevant code blocks, technical diagrams, or step-by-step tutorials where applicable.
   - Provide real-world examples to illustrate concepts.
   - Use syntax highlighting for better code readability.
   - Ensure all code snippets are functional and well-explained.
   - Include multiple relevant statistics, expert quotes, and real-world applications for each main point.

3. Well-Structured Content:
   - Develop an extensive content outline that covers every aspect of the video and expands on each point.
   - Create a comprehensive table of contents to navigate the long-form content.
   - Use a hierarchical structure of headings to organize the extensive content.
   - If time stamps are provided in the video description, use them to create the hierarchical structure.
   - Organize the body content into multiple main sections and subsections, each thoroughly exploring a topic or theme.
   - Provide a comprehensive glossary of all technical terms used in the article.
   - Create detailed appendices for additional technical information or data.

4. Step-by-Step Instructions:
   - For any processes or tutorials mentioned in the transcript, provide clear, sequential steps.
   - Include detailed explanations for each step.
   - Anticipate and address potential issues or errors that might occur during the process.
   - Use numbered lists for easy following of instructions.
   - Address potential questions or counterarguments related to each topic.

5. Visual Aids:
   - Create multiple lists, tables, and visual elements to break up text and present information in different ways.
   - Design custom infographics or diagrams to illustrate complex processes or data.
   - Include a high number of relevant images, screenshots, or visualizations, all properly credited and captioned.
   - Use visual aids to support and enhance the written content, not replace it.

6. Quality Assurance:
   - Ensure all information from the original transcript is included and expanded upon.
   - Verify and double-check all additional facts, figures, and references for accuracy.
   - Maintain consistent depth and detail across all sections of the article.
   - The output must be in Markdown format.

The final blog post should be as long as necessary to cover all aspects of the topic exhaustively, typically ranging from 3,000 to 10,000 words or more. Your writing should be authoritative, detailed, and accessible, catering to readers seeking the most comprehensive resource on the subject. Ensure that no information from the original transcript is omitted, and each point is expanded upon to create a definitive, encyclopedic article on the topic.
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
                
                    here is the **Video Description**:
                    {video_description}
                
                     here is the **Video Transcript**:
                      """{transcript_text}"""
                
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
            rewrite following Raw Video Transcript as a blog post with engaging tone, format the output using Markdown also embed video description in middle of transcript to understand the video better:


                here is the **Video Description**:
                {video_description}
                
               here is the **Video Transcript**:
                """{transcript_text}"""
            
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
      captions = ["Raw Transcript", "Enhance with Llama 3 (Groq)", "Enhance With GPT-4o (api key required)"])
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
                transcript_text = str(fetch_transcript(video_id)).replace("/n"," ")
                if transcript_text:
                    transcript_extracted = True

            if method == 'Llama' and transcript_text:
                with st.spinner('Structuring Using Llama 3 70b by Groq ...'):
                    structured_transcript = structure_free(transcript_text, video_description)
                    if video_title and  structured_transcript: st.header(video_title, divider='rainbow')
                    if video_thumbnail and  structured_transcript: st.image(video_thumbnail, use_column_width="auto")
                    if structured_transcript:
                        st.markdown(structured_transcript)
                        st.sidebar.download_button(label="Download Text",data=structured_transcript,file_name=f"{video_title}.txt",mime="application/txt")

                    else:
                        st.markdown("The free version is **limited** , try again after 1 minute or use **GPT-4o** \n __Groq Rate Limit__")
            if method == ':rainbow[GPT-4o]':
                with st.spinner('Structuring Using GPT-4o ...'):
                    structured_transcript = structure_with_gpt(transcript_text, video_description,OPENAI_API_KEY)
                    if video_title: st.header(video_title, divider='rainbow')
                    if video_thumbnail: st.image(video_thumbnail, use_column_width="auto")
                    st.markdown(structured_transcript)
                    st.sidebar.download_button(label="Download Text",data=structured_transcript,file_name=f"{video_title}.txt",mime="application/txt")


           
            if method == 'Simple' and transcript_text:
                if video_title: st.header(video_title, divider='rainbow')
                if video_thumbnail: st.image(video_thumbnail,use_column_width="auto",)
                st.markdown(transcript_text)
                st.sidebar.download_button(label="Download Text",data=transcript_text,file_name=f"{video_title}.txt",mime="application/txt")


                         
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube video URL.")
