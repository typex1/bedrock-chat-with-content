#!/usr/bin/env python3
"""
Enhanced command-line test tool for YouTube transcript downloads
Tests both original and fixed utility methods

Usage:
    python3 test_transcript_enhanced.py <youtube_url>
    python3 test_transcript_enhanced.py --batch <file_with_urls>
    python3 test_transcript_enhanced.py --interactive
"""

import sys
import argparse
import time
from datetime import datetime
import utility
import utility_fixed
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


class EnhancedTranscriptTester:
    """Enhanced class to test both original and fixed utility methods"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = []
        
    def test_single_url(self, url):
        """Test a single YouTube URL with multiple methods"""
        print(f"\n🔍 Testing URL: {url}")
        print("-" * 60)
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'video_id': None,
            'available_languages': [],
            'original_utility': {'success': False, 'error': None, 'length': 0},
            'fixed_utility': {'success': False, 'error': None, 'length': 0},
            'direct_method': {'success': False, 'error': None, 'length': 0},
            'processing_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Validate and extract video ID
            print("📋 Step 1: Validating URL and extracting video ID...")
            video_id, content_type = utility.validate_url(url)
            
            if not video_id or content_type != "youtube":
                print("❌ Invalid YouTube URL or unable to extract video ID")
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
                print("❌ No transcripts available for this video")
                return result
            
            # Step 3: Test original utility method
            print(f"\n📋 Step 3: Testing original utility.py method...")
            try:
                transcript_content = utility.get_content(video_id, "youtube")
                if transcript_content:
                    result['original_utility']['success'] = True
                    result['original_utility']['length'] = len(transcript_content)
                    word_count = len(transcript_content.split())
                    print(f"✅ Original utility method successful!")
                    print(f"   📊 Length: {len(transcript_content):,} characters")
                    print(f"   📊 Words: {word_count:,} words")
                else:
                    result['original_utility']['error'] = "No supported language found"
                    print(f"❌ Original utility method failed: {result['original_utility']['error']}")
            except Exception as e:
                result['original_utility']['error'] = str(e)
                print(f"❌ Original utility method failed: {e}")
            
            # Step 4: Test fixed utility method
            print(f"\n📋 Step 4: Testing fixed utility_fixed.py method...")
            try:
                transcript_content = utility_fixed.get_content(video_id, "youtube")
                if transcript_content:
                    result['fixed_utility']['success'] = True
                    result['fixed_utility']['length'] = len(transcript_content)
                    word_count = len(transcript_content.split())
                    print(f"✅ Fixed utility method successful!")
                    print(f"   📊 Length: {len(transcript_content):,} characters")
                    print(f"   📊 Words: {word_count:,} words")
                    
                    if self.verbose and transcript_content:
                        preview_length = 200
                        preview = transcript_content[:preview_length]
                        if len(transcript_content) > preview_length:
                            preview += "..."
                        print(f"\n📖 Content preview:")
                        print(f"   {preview}")
                else:
                    result['fixed_utility']['error'] = "No supported language found"
                    print(f"❌ Fixed utility method failed: {result['fixed_utility']['error']}")
            except Exception as e:
                result['fixed_utility']['error'] = str(e)
                print(f"❌ Fixed utility method failed: {e}")
            
            # Step 5: Test direct API method
            print(f"\n📋 Step 5: Testing direct API method...")
            try:
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
                    result['direct_method']['success'] = True
                    result['direct_method']['length'] = len(transcript_content)
                    word_count = len(transcript_content.split())
                    print(f"✅ Direct API method successful using {used_language}!")
                    print(f"   📊 Length: {len(transcript_content):,} characters")
                    print(f"   📊 Words: {word_count:,} words")
                else:
                    result['direct_method']['error'] = "No supported languages available"
                    print(f"❌ Direct API method failed: {result['direct_method']['error']}")
                    
            except Exception as e:
                result['direct_method']['error'] = str(e)
                print(f"❌ Direct API method failed: {e}")
                
        except TranscriptsDisabled:
            error_msg = "Transcripts are disabled for this video"
            result['original_utility']['error'] = error_msg
            result['fixed_utility']['error'] = error_msg
            result['direct_method']['error'] = error_msg
            print(f"❌ {error_msg}")
            
        except NoTranscriptFound:
            error_msg = "No transcript found for this video"
            result['original_utility']['error'] = error_msg
            result['fixed_utility']['error'] = error_msg
            result['direct_method']['error'] = error_msg
            print(f"❌ {error_msg}")
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            result['original_utility']['error'] = error_msg
            result['fixed_utility']['error'] = error_msg
            result['direct_method']['error'] = error_msg
            print(f"❌ {error_msg}")
            
        finally:
            result['processing_time'] = round(time.time() - start_time, 2)
            print(f"\n⏱️  Processing time: {result['processing_time']} seconds")
            
            # Summary
            print(f"\n📊 SUMMARY:")
            methods = [
                ("Original utility.py", result['original_utility']),
                ("Fixed utility_fixed.py", result['fixed_utility']),
                ("Direct API", result['direct_method'])
            ]
            
            for method_name, method_result in methods:
                status = "✅ PASS" if method_result['success'] else "❌ FAIL"
                print(f"   {method_name}: {status}")
                if method_result['success']:
                    print(f"      Length: {method_result['length']:,} characters")
                elif method_result['error']:
                    print(f"      Error: {method_result['error']}")
            
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
            
            method_stats = {
                'original_utility': {'success': 0, 'fail': 0},
                'fixed_utility': {'success': 0, 'fail': 0},
                'direct_method': {'success': 0, 'fail': 0}
            }
            
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*60}")
                print(f"🧪 Test {i}/{len(urls)}")
                result = self.test_single_url(url)
                
                # Update stats
                for method in method_stats:
                    if result[method]['success']:
                        method_stats[method]['success'] += 1
                    else:
                        method_stats[method]['fail'] += 1
                    
            # Final Summary
            print(f"\n{'='*60}")
            print("📊 BATCH TEST SUMMARY")
            print(f"{'='*60}")
            print(f"Total URLs tested: {len(urls)}")
            print()
            
            for method_name, stats in method_stats.items():
                total = stats['success'] + stats['fail']
                success_rate = (stats['success'] / total * 100) if total > 0 else 0
                print(f"{method_name.replace('_', ' ').title()}:")
                print(f"  ✅ Successful: {stats['success']}")
                print(f"  ❌ Failed: {stats['fail']}")
                print(f"  📊 Success rate: {success_rate:.1f}%")
                print()
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    def interactive_mode(self):
        """Interactive mode for testing URLs"""
        print("🎮 Enhanced Interactive Mode")
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
        description="Enhanced YouTube video transcript download tester",
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
    
    print("🎬 Enhanced YouTube Transcript Tester")
    print("=" * 50)
    print("This tool tests YouTube transcript downloads using multiple methods:")
    print("• Original utility.py (from your app)")
    print("• Fixed utility_fixed.py (corrected version)")
    print("• Direct API method (reference implementation)")
    print()
    
    tester = EnhancedTranscriptTester(verbose=args.verbose)
    
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
