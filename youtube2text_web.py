import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
from pytube import Playlist, YouTube
import requests
from PIL import Image
from io import BytesIO

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        paragraphs = []
        current_paragraph = ""
        previous_time = None
        time_gap_threshold = 5.0

        for entry in transcript:
            if previous_time is not None:
                time_gap = entry['start'] - previous_time
                if time_gap > time_gap_threshold:
                    if current_paragraph.strip():
                        paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""
            current_paragraph += " " + entry['text']
            previous_time = entry['start']

        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())

        return paragraphs
    except Exception as e:
        st.error(f"Unable to fetch transcript for video ID {video_id}. Error: {str(e)}")
        return ["Transcript not available."]

def get_playlist_info(playlist_url):
    playlist_info = []
    if 'list=' in playlist_url:
        playlist = Playlist(playlist_url)
        for url in playlist.video_urls:
            video = YouTube(url)
            description = video.description if video.description else "\n"
            playlist_info.append({
                'name': playlist.title,
                'title': video.title,
                'description': description,
                'video_id': video.video_id,
                'thumbnail_url': video.thumbnail_url
            })
    else:
        video = YouTube(playlist_url)
        playlist_info.append({
            'name': video.title,
            'title': video.title,
            'description': video.description if video.description else "\n",
            'video_id': video.video_id,
            'thumbnail_url': video.thumbnail_url
        })
    return playlist_info

def create_pdf(playlist_info):
    pdf = FPDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 30)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 60, playlist_info[0]['name'], 0, 1, 'C', True)

    for index, video in enumerate(playlist_info):
        pdf.add_page()
        
        # Download and add thumbnail image
        thumbnail_url = video['thumbnail_url'].replace('sddefault.jpg', 'maxresdefault.jpg')
        response = requests.get(thumbnail_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((160, 90)) # Resize to 16:9 aspect ratio
        img.save('thumbnail.jpg', 'JPEG')
        pdf.image('thumbnail.jpg', x=10, y=10, w=160) # Add thumbnail to PDF

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"{video['title']} \n", 0, 1, 'C')
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, f"{video['description']} \n")
        pdf.ln()
        pdf.set_font("Arial", "", 10)
        transcript = get_transcript(video['video_id'])
        for paragraph in transcript:
            pdf.multi_cell(0, 10, paragraph)
            pdf.ln(10)
        pdf.ln(40)

    pdf_data = pdf.output(dest='S').encode('latin1')
    return pdf_data

st.title('YouTube Playlist to PDF')

input_type = st.selectbox('Select input type', ['Single Video', 'Playlist'])

if input_type == 'Single Video':
    url = st.text_input('Enter YouTube video URL')
    if st.button("Convert to PDF"):
        video_info = get_playlist_info(url)[0] # Extract the single video's info
        pdf_data = create_pdf([video_info]) # Pass it as a list to create_pdf
        st.success("PDF Creation Complete!")
        st.download_button("Download PDF", pdf_data, file_name="YouTubeVideo.pdf", mime="application/pdf")
        # Display transcript in the UI
        transcript = get_transcript(video_info['video_id'])
        for paragraph in transcript:
            st.text(paragraph)
else:
    playlist_url = st.text_input('Enter YouTube playlist URL')
    if st.button("Convert to PDF"):
        playlist_info = get_playlist_info(playlist_url)
        if playlist_info:
            pdf_data = create_pdf(playlist_info)
            st.success("PDF Creation Complete!")
            st.download_button("Download PDF", pdf_data, file_name="YouTubePlaylist.pdf", mime="application/pdf")
            # Display transcript in the UI for the first video as an example
            if playlist_info:
                first_video_transcript = get_transcript(playlist_info[0]['video_id'])
                for paragraph in first_video_transcript:
                    st.text(paragraph)
        else:
            st.error("An error occurred. Please check the URL and try again.")
