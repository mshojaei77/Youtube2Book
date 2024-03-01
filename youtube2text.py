#YTplaylist2Book.py

from pytube import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import requests
import os

# Set up logging to stdout
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get playlist info
def get_playlist_info(playlist_url):
    playlist = Playlist(playlist_url)
    playlist_info = []
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
        logging.info(f"Completed fetching fields for video {video.video_id}: Title: {video.title}, Description: {description}")
    return playlist_info

# Function to get transcript
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        logging.warning(f"Unable to fetch transcript for video ID {video_id}. Error: {str(e)}")
        return "Transcript not available."

# Function to create PDF using FPDF
def create_pdf(playlist_info):
    # Create a new FPDF instance with A4 size and portrait orientation
    pdf = FPDF('P', 'mm', 'A4')

    # Set auto page breaks
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add a cover page with the playlist title
    pdf.add_page()
    pdf.set_font("Arial", "B",   30)
    pdf.set_fill_color(230,   230,   230)  # Light grey color for the background
    pdf.cell(0,   60, playlist_info[0]['name'],   0,   1, 'C', True)

    # Add a page for each video
    for index, video in enumerate(playlist_info):
        # Add a new page
        pdf.add_page()

        # Download the thumbnail
        response = requests.get(video['thumbnail_url'])
        thumbnail_path = f"thumbnails/{video['video_id']}.jpg"
        with open(thumbnail_path, 'wb') as f:
            f.write(response.content)

        # Insert the thumbnail
        pdf.image(thumbnail_path, x=10, y=20, w=100, h=100)  # Adjust x, y, w, h as needed

        # Add a line break
        pdf.ln(120)  # Adjust the line break as needed

        # Set the font for the title
        pdf.set_font("Arial", "B",   16)
        pdf.cell(0,   10, f"{video['title']} \n",   0,   1, 'C')

        # Set the font for the description
        pdf.set_font("Arial", "",   12)
        pdf.multi_cell(0,   10, f"{video['description']} \n")

        # Add a line break
        pdf.ln()

        # Set the font for the transcript
        pdf.set_font("Arial", "",   10)
        transcript = get_transcript(video['video_id'])
        pdf.multi_cell(0,   10, f"{transcript} \n")

        # Add a page break
        pdf.ln(40)

    # Save the PDF
    pdf.output(f"{playlist_info[0]['name']}.pdf")


# Ensure the thumbnails directory exists
if not os.path.exists('thumbnails'):
    os.makedirs('thumbnails')

# Replace with your actual YouTube playlist URL
playlist_url = input("Enter the YouTube Playlist URL: ")
try:
    playlist_info = get_playlist_info(playlist_url)
    create_pdf(playlist_info)
except Exception as e:
    logging.error(f"An error occurred: {str(e)}")
