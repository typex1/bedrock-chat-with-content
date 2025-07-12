#!/usr/bin/env python3
"""
Command-line test tool for YouTube transcript downloads
Tests if video transcripts can be downloaded successfully before using in the Streamlit app

Usage:
    python3 test_transcript.py <youtube_url>
    python3 test_transcript.py --batch <file_with_urls>
    python3 test_transcript.py --interactive

Examples:
    python3 test_transcript.py "https://www.youtube.com/watch?v=-zF1mkBpyf4"
    python3 test_transcript.py --batch test_urls.txt
    python3 test_transcript.py --interactive
"""

import sys
import argparse
import time
from datetime import datetime
import utility
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


class TranscriptTester:
    """Class to handle YouTube transcript testing"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = []
        
    def test_single_url(self, url):
        """Test a single YouTube URL for transcript availability"""
        print(f"\n🔍 Testing URL: {url}")
        print("-" * 60)
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'video_id': None,
            'available_languages': [],
            'transcript_length': 0,
            'error': None,
            'processing_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Validate and extract video ID
            print("📋 Step 1: Validating URL and extracting video ID...")
            video_id, content_type = utility.validate_url(url)
            
            if not video_id or content_type != "youtube":
                result['error'] = "Invalid YouTube URL or unable to extract video ID"
                print(f"❌ {result['error']}")
                return result
                
            result['video_id'] = video_id
            print(f"✅ Video ID extracted: {video_id}")
            
            # Step 2: Check available transcripts
            print("\n📋 Step 2: Checking available transcripts...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            available_languages = []
            for transcript in transcript_list:
                lang_code = transcript.language_code
                lang_name = transcript.language
                is_generated = transcript.is_generated
                available_languages.append({
                    'code': lang_code,
                    'name': lang_name,
                    'generated': is_generated
                })
                
            result['available_languages'] = available_languages
            
            if available_languages:
                print(f"✅ Found {len(available_languages)} available transcript(s):")
                for lang in available_languages:
                    status = "🤖 Auto-generated" if lang['generated'] else "👤 Manual"
                    print(f"   • {lang['name']} ({lang['code']}) - {status}")
            else:
                result['error'] = "No transcripts available for this video"
                print(f"❌ {result['error']}")
                return result
            
            # Step 3: Test transcript download using app's method
            print(f"\n📋 Step 3: Testing transcript download (using app's method)...")
            try:
                transcript_content = utility.get_content(video_id, "youtube")
                
                if transcript_content:
                    result['transcript_length'] = len(transcript_content)
                    result['success'] = True
                    
                    word_count = len(transcript_content.split())
                    print(f"✅ Transcript downloaded successfully!")
                    print(f"   📊 Length: {result['transcript_length']:,} characters")
                    print(f"   📊 Words: {word_count:,} words")
                    print(f"   📊 Estimated reading time: {word_count // 200} minutes")
                    
                    if self.verbose:
                        preview_length = 200
                        preview = transcript_content[:preview_length]
                        if len(transcript_content) > preview_length:
                            preview += "..."
                        print(f"\n📖 Content preview:")
                        print(f"   {preview}")
                        
                else:
                    result['error'] = "Transcript download failed - no supported language found"
                    print(f"❌ {result['error']}")
                    print("   💡 App supports: English (en), German (de), French (fr), Spanish (es)")
                    
            except Exception as e:
                result['error'] = f"App method failed: {str(e)}"
                print(f"❌ {result['error']}")
                
                # Step 3b: Try direct method as fallback
                print(f"\n📋 Step 3b: Trying direct transcript download...")
                try:
                    # Try to download transcript directly with supported languages
                    supported_languages = ['en', 'de', 'fr', 'es']
                    transcript_content = None
                    used_language = None
                    
                    for lang in supported_languages:
                        try:
                            transcript_data = transcript_list.find_transcript([lang]).fetch()
                            transcript_text = [entry['text'] for entry in transcript_data]
                            transcript_content = ' '.join(transcript_text)
                            used_language = lang
                            break
                        except NoTranscriptFound:
                            continue
                    
                    if transcript_content:
                        result['transcript_length'] = len(transcript_content)
                        result['success'] = True
                        result['error'] = f"App method failed, but direct method worked with {used_language}"
                        
                        word_count = len(transcript_content.split())
                        print(f"✅ Direct download successful using {used_language}!")
                        print(f"   📊 Length: {result['transcript_length']:,} characters")
                        print(f"   📊 Words: {word_count:,} words")
                        print(f"   ⚠️  Note: App utility.py may need fixing")
                        
                        if self.verbose:
                            preview_length = 200
                            preview = transcript_content[:preview_length]
                            if len(transcript_content) > preview_length:
                                preview += "..."
                            print(f"\n📖 Content preview:")
                            print(f"   {preview}")
                    else:
                        print(f"❌ Direct method also failed - no supported languages available")
                        
                except Exception as e2:
                    print(f"❌ Direct method also failed: {str(e2)}")
                
        except TranscriptsDisabled:
            result['error'] = "Transcripts are disabled for this video"
            print(f"❌ {result['error']}")
            
        except NoTranscriptFound:
            result['error'] = "No transcript found for this video"
            print(f"❌ {result['error']}")
            
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            print(f"❌ {result['error']}")
            
        finally:
            result['processing_time'] = round(time.time() - start_time, 2)
            print(f"\n⏱️  Processing time: {result['processing_time']} seconds")
            
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
            
            successful = 0
            failed = 0
            
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*60}")
                print(f"🧪 Test {i}/{len(urls)}")
                result = self.test_single_url(url)
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    
            # Summary
            print(f"\n{'='*60}")
            print("📊 BATCH TEST SUMMARY")
            print(f"{'='*60}")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📊 Success rate: {(successful/len(urls)*100):.1f}%")
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    def interactive_mode(self):
        """Interactive mode for testing URLs"""
        print("🎮 Interactive Mode")
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
    
    def generate_report(self, output_file=None):
        """Generate a detailed test report"""
        if not self.results:
            print("No test results to report")
            return
            
        report_lines = []
        report_lines.append("YouTube Transcript Test Report")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total tests: {len(self.results)}")
        
        successful = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - successful
        
        report_lines.append(f"Successful: {successful}")
        report_lines.append(f"Failed: {failed}")
        report_lines.append(f"Success rate: {(successful/len(self.results)*100):.1f}%")
        report_lines.append("")
        
        for i, result in enumerate(self.results, 1):
            report_lines.append(f"Test {i}: {'✅ PASS' if result['success'] else '❌ FAIL'}")
            report_lines.append(f"  URL: {result['url']}")
            report_lines.append(f"  Video ID: {result['video_id'] or 'N/A'}")
            report_lines.append(f"  Processing time: {result['processing_time']}s")
            
            if result['success']:
                report_lines.append(f"  Transcript length: {result['transcript_length']:,} characters")
                report_lines.append(f"  Available languages: {len(result['available_languages'])}")
            else:
                report_lines.append(f"  Error: {result['error']}")
                
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(report_content)
                print(f"📄 Report saved to: {output_file}")
            except Exception as e:
                print(f"❌ Error saving report: {e}")
        else:
            print("\n" + report_content)


def main():
    parser = argparse.ArgumentParser(
        description="Test YouTube video transcript downloads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=-zF1mkBpyf4"
  %(prog)s --batch test_urls.txt
  %(prog)s --interactive
  %(prog)s "https://youtu.be/dQw4w9WgXcQ" --verbose --report results.txt
        """
    )
    
    parser.add_argument('url', nargs='?', help='YouTube URL to test')
    parser.add_argument('--batch', '-b', help='File containing URLs to test (one per line)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output with content preview')
    parser.add_argument('--report', '-r', help='Save detailed report to file')
    
    args = parser.parse_args()
    
    # Show help if no arguments provided
    if not any([args.url, args.batch, args.interactive]):
        parser.print_help()
        return
    
    print("🎬 YouTube Transcript Tester")
    print("=" * 50)
    print("This tool tests if YouTube video transcripts can be downloaded")
    print("successfully before using them in the Video Chatter app.")
    print()
    
    tester = TranscriptTester(verbose=args.verbose)
    
    try:
        if args.interactive:
            tester.interactive_mode()
        elif args.batch:
            tester.test_batch_urls(args.batch)
        elif args.url:
            tester.test_single_url(args.url)
            
        # Generate report if requested
        if args.report and tester.results:
            tester.generate_report(args.report)
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
