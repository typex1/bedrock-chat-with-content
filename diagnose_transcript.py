#!/usr/bin/env python3
"""
Simple diagnostic tool to check YouTube transcript API issues
"""

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import sys

def diagnose_video(video_id):
    print(f"🔍 Diagnosing video ID: {video_id}")
    print("-" * 40)
    
    try:
        # Get transcript list
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("✅ Successfully retrieved transcript list")
        
        # List all available transcripts
        transcripts = list(transcript_list)
        print(f"📋 Found {len(transcripts)} transcript(s):")
        
        for i, transcript in enumerate(transcripts):
            print(f"  {i+1}. Language: {transcript.language} ({transcript.language_code})")
            print(f"     Generated: {transcript.is_generated}")
            print(f"     Translatable: {transcript.is_translatable}")
            
            # Try to fetch this transcript
            try:
                print(f"     🔄 Attempting to fetch...")
                data = transcript.fetch()
                print(f"     ✅ Fetch successful! Got {len(data)} entries")
                
                if data:
                    # Show first few entries
                    print(f"     📖 First entry: {data[0]}")
                    if len(data) > 1:
                        print(f"     📖 Second entry: {data[1]}")
                    
                    # Try to extract text
                    text_parts = [entry['text'] for entry in data[:5]]  # First 5 entries
                    sample_text = ' '.join(text_parts)
                    print(f"     📝 Sample text: {sample_text[:100]}...")
                    
            except Exception as e:
                print(f"     ❌ Fetch failed: {e}")
            
            print()
    
    except TranscriptsDisabled:
        print("❌ Transcripts are disabled for this video")
    except NoTranscriptFound:
        print("❌ No transcripts found for this video")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 diagnose_transcript.py <video_id>")
        print("Example: python3 diagnose_transcript.py DgpYiysQjeI")
        return
    
    video_id = sys.argv[1]
    
    # Handle full URLs
    if 'youtube.com' in video_id or 'youtu.be' in video_id:
        if 'watch?v=' in video_id:
            video_id = video_id.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in video_id:
            video_id = video_id.split('youtu.be/')[1].split('?')[0]
    
    diagnose_video(video_id)

if __name__ == "__main__":
    main()
