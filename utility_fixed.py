"""
Fixed version of utility.py for testing purposes
This version fixes the transcript download issues
"""

import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import sys

logger = logging.getLogger()
logger.setLevel("WARNING")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
DEBUG = False

content_type = ""

def validate_url(content_url):
    # use "youtu" to capture also "youtu.be" from shared links:
    if "youtu" in content_url:
        return validate_youtube_url(content_url)

def validate_youtube_url(content_url):
    logger.info("Inside validate_url ..")

    watch_param = 'watch?v='
    video_id = content_url.split('/')[-1].strip()
    if video_id == '':
        video_id = content_url.split('/')[-2].strip()
    if watch_param in video_id:
        video_id = video_id[len(watch_param):]

    logger.info("video_id")
    logger.info(video_id)
    content_type = "youtube"
    return video_id, content_type
    
def get_content(id, content_type):
    if content_type == "youtube":
        return get_youtube_transcript(id)

def get_youtube_transcript(video_id):
    """
    Fixed version of get_youtube_transcript that properly handles the API
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Define the order of languages to try (same as original)
        languages_to_try = ['de', 'fr', 'en', 'es']
        
        for lang_code in languages_to_try:
            try:
                # Find and fetch transcript for this language
                transcript = transcript_list.find_transcript([lang_code])
                transcript_data = transcript.fetch()
                
                # Extract just the text from each transcript segment
                transcript_text = [entry['text'] for entry in transcript_data]
                
                # Join all text segments into a single string
                full_transcript = ' '.join(transcript_text)
                
                logger.info(f"Successfully retrieved {lang_code} transcript")
                return full_transcript
                
            except NoTranscriptFound:
                logger.info(f"No {lang_code} transcript found, trying next language")
                continue
        
        # If we get here, no supported language was found
        logger.warning("No transcript found in supported languages (de, fr, en, es)")
        return None

    except TranscriptsDisabled:
        logger.error("Transcripts are disabled for this video")
        return None
    except Exception as e:
        logger.error(f"Error retrieving transcript: {str(e)}")
        return None

def generate_prompt_from_transcript(transcript):
    logger.info("Inside generate_prompt_from_transcript ..")

    prompt = "Summarize the following video:\n"
    prompt += " " + transcript

    if DEBUG:
        logger.info("prompt")
        logger.info(prompt)
    return prompt
