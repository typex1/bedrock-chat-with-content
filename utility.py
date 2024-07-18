import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import sys

logger = logging.getLogger()
logger.setLevel("INFO")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

content_type = ""

def validate_url(content_url):
    if "youtube" in content_url:
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
    try:
        transcript = YouTubeTranscriptApi.list_transcripts(video_id)

        # Check for German transcript
        try:
            transcript_data=transcript.find_transcript(['de']).fetch()
            # Extract just the text from each transcript segment
            transcript_text = [entry['text'] for entry in transcript_data]
            # Join all text segments into a single string
            full_transcript = ' '.join(transcript_text)
            return full_transcript
        except NoTranscriptFound:
            pass

        # Check for French transcript
        try:
            transcript_data=transcript.find_transcript(['fr']).fetch()
            # Extract just the text from each transcript segment
            transcript_text = [entry['text'] for entry in transcript_data]
            # Join all text segments into a single string
            full_transcript = ' '.join(transcript_text)
            return full_transcript
        except NoTranscriptFound:
            pass
        
        # Check for English transcript
        try:
            transcript_data=transcript.find_transcript(['en']).fetch()
            # Extract just the text from each transcript segment
            transcript_text = [entry['text'] for entry in transcript_data]
            # Join all text segments into a single string
            full_transcript = ' '.join(transcript_text)
            return full_transcript
        except NoTranscriptFound:
            pass

        # Check for Spanish transcript
        try:
            transcript_data=transcript.find_transcript(['es']).fetch()
            # Extract just the text from each transcript segment
            transcript_text = [entry['text'] for entry in transcript_data]
            # Join all text segments into a single string
            full_transcript = ' '.join(transcript_text)
            return full_transcript
        except NoTranscriptFound:
            print("No German, English, or Spanish transcript found.")
            return None

    except TranscriptsDisabled:
        print("Transcripts are disabled for this video.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

    except Exception as e:
        transcript = transcript_list.find_transcript(['en'])
        print("en transcript:{}".format("transcript"))

        # Fetch the actual transcript data
        transcript_data = transcript.fetch()

        # Extract just the text from each transcript segment
        transcript_text = [entry['text'] for entry in transcript_data]

        # Join all text segments into a single string
        full_transcript = ' '.join(transcript_text)

        return full_transcript

    except Exception as e:
        logger.exception(e)
        return None

def generate_prompt_from_transcript(transcript):
    logger.info("Inside generate_prompt_from_transcript ..")

    prompt = "Summarize the following video:\n"
    #for trans in transcript:
        #prompt += " " + trans.get('text', '')
    prompt += " " + transcript

    logger.info("prompt")
    logger.info(prompt)
    return prompt
