import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger()
logger.setLevel("INFO")


def get_video_id_from_url(youtube_url):
    logger.info("Inside get_video_id_from_url ..")

    watch_param = 'watch?v='
    video_id = youtube_url.split('/')[-1].strip()
    if video_id == '':
        video_id = youtube_url.split('/')[-2].strip()
    if watch_param in video_id:
        video_id = video_id[len(watch_param):]

    logger.info("video_id")
    logger.info(video_id)
    return video_id

def get_transcript(video_id):
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
