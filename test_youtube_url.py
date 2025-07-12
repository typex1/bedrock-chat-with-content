#!/usr/bin/env python3
"""
Robust YouTube URL tester for the Video Chatter app
Tests URL validation, transcript availability, and provides actionable feedback

Usage:
    python3 test_youtube_url.py <youtube_url>
    python3 test_youtube_url.py --batch <file_with_urls>
    python3 test_youtube_url.py --interactive
"""

import sys
import argparse
import time
from datetime import datetime
import utility
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests


class YouTubeURLTester:
    """Comprehensive YouTube URL tester for the Video Chatter app"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = []
        
    def test_url_accessibility(self, url):
        """Test if the YouTube URL is accessible"""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def extract_video_info(self, url):
        """Extract video information from URL"""
        try:
            # Use the app's utility function
            video_id, content_type = utility.validate_url(url)
            return video_id, content_type
        except Exception as e:
            return None, str(e)
    
    def test_single_url(self, url):
        """Comprehensive test of a single YouTube URL"""
        print(f"\n🎬 Testing YouTube URL")
        print("=" * 60)
        print(f"URL: {url}")
        print("-" * 60)
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'url_accessible': False,
            'video_id': None,
            'content_type': None,
            'transcripts_available': False,
            'transcript_count': 0,
            'supported_languages': [],
            'app_compatible': False,
            'recommendations': [],
            'processing_time': 0
        }
        
        start_time = time.time()
        
        # Step 1: Test URL accessibility
        print("📋 Step 1: Testing URL accessibility...")
        result['url_accessible'] = self.test_url_accessibility(url)
        if result['url_accessible']:
            print("✅ URL is accessible")
        else:
            print("⚠️  URL accessibility check failed (might be network issue)")
            result['recommendations'].append("Check your internet connection")
        
        # Step 2: Extract video ID
        print("\n📋 Step 2: Extracting video ID...")
        video_id, content_type = self.extract_video_info(url)
        
        if video_id:
            result['video_id'] = video_id
            result['content_type'] = content_type
            print(f"✅ Video ID extracted: {video_id}")
            print(f"✅ Content type: {content_type}")
        else:
            print(f"❌ Failed to extract video ID: {content_type}")
            result['recommendations'].append("Check if the URL is a valid YouTube URL")
            result['recommendations'].append("Supported formats: youtube.com/watch?v=... or youtu.be/...")
            return self._finalize_result(result, start_time)
        
        # Step 3: Check transcript availability
        print(f"\n📋 Step 3: Checking transcript availability...")
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcripts = list(transcript_list)
            
            result['transcripts_available'] = len(transcripts) > 0
            result['transcript_count'] = len(transcripts)
            
            if transcripts:
                print(f"✅ Found {len(transcripts)} transcript(s):")
                
                # Check for app-supported languages
                app_supported = ['en', 'de', 'fr', 'es']
                supported_found = []
                
                for transcript in transcripts:
                    lang_code = transcript.language_code
                    lang_name = transcript.language
                    is_generated = transcript.is_generated
                    status = "🤖 Auto-generated" if is_generated else "👤 Manual"
                    
                    print(f"   • {lang_name} ({lang_code}) - {status}")
                    
                    # Check if this language is supported by the app
                    if lang_code in app_supported or lang_code.split('-')[0] in app_supported:
                        supported_found.append(lang_code)
                
                result['supported_languages'] = supported_found
                result['app_compatible'] = len(supported_found) > 0
                
                if result['app_compatible']:
                    print(f"\n✅ App compatibility: COMPATIBLE")
                    print(f"   Supported languages found: {', '.join(supported_found)}")
                else:
                    print(f"\n⚠️  App compatibility: NOT COMPATIBLE")
                    print(f"   App supports: English (en), German (de), French (fr), Spanish (es)")
                    result['recommendations'].append("This video doesn't have transcripts in supported languages")
                    result['recommendations'].append("Try finding a video with English, German, French, or Spanish transcripts")
                
            else:
                print("❌ No transcripts available")
                result['recommendations'].append("This video has no transcripts available")
                result['recommendations'].append("Try a different video with captions/subtitles enabled")
                
        except TranscriptsDisabled:
            print("❌ Transcripts are disabled for this video")
            result['recommendations'].append("Transcripts are disabled by the video owner")
            result['recommendations'].append("Try a different video")
            
        except NoTranscriptFound:
            print("❌ No transcripts found for this video")
            result['recommendations'].append("No transcripts available for this video")
            result['recommendations'].append("Try a video with captions/subtitles")
            
        except Exception as e:
            print(f"❌ Error checking transcripts: {e}")
            result['recommendations'].append(f"Transcript API error: {str(e)}")
            result['recommendations'].append("This might be a temporary YouTube API issue")
        
        # Step 4: Test app integration (if compatible)
        if result['app_compatible']:
            print(f"\n📋 Step 4: Testing app integration...")
            try:
                transcript_content = utility.get_content(video_id, "youtube")
                if transcript_content:
                    word_count = len(transcript_content.split())
                    char_count = len(transcript_content)
                    
                    print(f"✅ App integration successful!")
                    print(f"   📊 Transcript length: {char_count:,} characters")
                    print(f"   📊 Word count: {word_count:,} words")
                    print(f"   📊 Estimated reading time: {word_count // 200} minutes")
                    
                    if self.verbose and char_count > 0:
                        preview_length = 200
                        preview = transcript_content[:preview_length]
                        if len(transcript_content) > preview_length:
                            preview += "..."
                        print(f"\n📖 Content preview:")
                        print(f"   {preview}")
                    
                    result['recommendations'].append("✅ This URL is ready to use in the Video Chatter app!")
                    
                else:
                    print(f"❌ App integration failed - no content retrieved")
                    result['app_compatible'] = False
                    result['recommendations'].append("App couldn't retrieve transcript content")
                    result['recommendations'].append("This might be a temporary issue - try again later")
                    
            except Exception as e:
                print(f"❌ App integration failed: {e}")
                result['app_compatible'] = False
                result['recommendations'].append(f"App integration error: {str(e)}")
        
        return self._finalize_result(result, start_time)
    
    def _finalize_result(self, result, start_time):
        """Finalize the test result"""
        result['processing_time'] = round(time.time() - start_time, 2)
        
        print(f"\n⏱️  Processing time: {result['processing_time']} seconds")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if result['app_compatible']:
            print("✅ READY FOR VIDEO CHATTER APP")
            print("   This URL can be used successfully in your Streamlit app")
        else:
            print("❌ NOT READY FOR VIDEO CHATTER APP")
            print("   This URL cannot be used in your Streamlit app")
        
        # Show recommendations
        if result['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        self.results.append(result)
        return result
    
    def test_batch_urls(self, file_path):
        """Test multiple URLs from a file"""
        print(f"📁 Reading URLs from: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
            if not urls:
                print("❌ No valid URLs found in file")
                return
                
            print(f"🎯 Found {len(urls)} URL(s) to test")
            
            compatible_count = 0
            
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*80}")
                print(f"🧪 Test {i}/{len(urls)}")
                result = self.test_single_url(url)
                
                if result['app_compatible']:
                    compatible_count += 1
                    
            # Summary
            print(f"\n{'='*80}")
            print("📊 BATCH TEST SUMMARY")
            print(f"{'='*80}")
            print(f"Total URLs tested: {len(urls)}")
            print(f"✅ App-compatible URLs: {compatible_count}")
            print(f"❌ Incompatible URLs: {len(urls) - compatible_count}")
            print(f"📊 Compatibility rate: {(compatible_count/len(urls)*100):.1f}%")
            
            if compatible_count > 0:
                print(f"\n🎉 You have {compatible_count} URL(s) ready for the Video Chatter app!")
            else:
                print(f"\n😞 No URLs are currently compatible with the Video Chatter app.")
                print("   Try finding videos with English, German, French, or Spanish transcripts.")
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    def interactive_mode(self):
        """Interactive mode for testing URLs"""
        print("🎮 Interactive YouTube URL Tester")
        print("Enter YouTube URLs to test (type 'quit' to exit)")
        print("-" * 50)
        
        while True:
            try:
                url = input("\n🔗 Enter YouTube URL: ").strip()
                
                if url.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not url:
                    continue
                    
                if 'youtu' not in url:
                    print("⚠️  This doesn't look like a YouTube URL. Try again.")
                    continue
                    
                self.test_single_url(url)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                break


def main():
    parser = argparse.ArgumentParser(
        description="Test YouTube URLs for Video Chatter app compatibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=-zF1mkBpyf4"
  %(prog)s --batch sample_test_urls.txt
  %(prog)s --interactive
  %(prog)s "https://youtu.be/dQw4w9WgXcQ" --verbose
        """
    )
    
    parser.add_argument('url', nargs='?', help='YouTube URL to test')
    parser.add_argument('--batch', '-b', help='File containing URLs to test (one per line)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output with content preview')
    
    args = parser.parse_args()
    
    # Show help if no arguments provided
    if not any([args.url, args.batch, args.interactive]):
        parser.print_help()
        return
    
    print("🎬 YouTube URL Tester for Video Chatter App")
    print("=" * 60)
    print("This tool tests if YouTube URLs will work with your Video Chatter app")
    print("by checking transcript availability and app compatibility.")
    print()
    
    tester = YouTubeURLTester(verbose=args.verbose)
    
    try:
        if args.interactive:
            tester.interactive_mode()
        elif args.batch:
            tester.test_batch_urls(args.batch)
        elif args.url:
            tester.test_single_url(args.url)
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
