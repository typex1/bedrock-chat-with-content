# Command-Line Test Feature Documentation

## Overview

The Video Chatter v3 project includes a comprehensive **command-line test feature** that allows you to test YouTube URLs before using them in the Streamlit app. This helps you verify transcript availability and app compatibility without running the full application.

## Features

### 🎯 **Main Test Tool: `test_youtube_url.py`**

A comprehensive YouTube URL tester that provides:

- **URL Accessibility Check**: Verifies the YouTube URL is reachable
- **Video ID Extraction**: Tests the app's URL parsing logic
- **Transcript Availability**: Lists all available transcripts with language details
- **App Compatibility**: Checks if transcripts are in supported languages (English, German, French, Spanish)
- **Integration Testing**: Tests the actual app utility functions
- **Actionable Recommendations**: Provides specific guidance based on test results

### 🔧 **Diagnostic Tools**

- **`diagnose_transcript.py`**: Low-level transcript API diagnostics
- **`utility_fixed.py`**: Fixed version of utility functions for comparison
- **`test_transcript_enhanced.py`**: Multi-method testing approach

## Usage

### Single URL Testing

```bash
# Test a single YouTube URL
python3 test_youtube_url.py "https://www.youtube.com/watch?v=-zF1mkBpyf4"

# Verbose output with content preview
python3 test_youtube_url.py "https://www.youtube.com/watch?v=-zF1mkBpyf4" --verbose

# Using the shell wrapper
./test_url.sh "https://www.youtube.com/watch?v=-zF1mkBpyf4"
```

### Batch Testing

```bash
# Test multiple URLs from a file
python3 test_youtube_url.py --batch sample_test_urls.txt

# Create your own URL list file
echo "https://www.youtube.com/watch?v=example1" > my_urls.txt
echo "https://www.youtube.com/watch?v=example2" >> my_urls.txt
python3 test_youtube_url.py --batch my_urls.txt
```

### Interactive Mode

```bash
# Interactive testing mode
python3 test_youtube_url.py --interactive

# Then enter URLs one by one:
# 🔗 Enter YouTube URL: https://www.youtube.com/watch?v=example
# (test results appear)
# 🔗 Enter YouTube URL: quit
```

## Test Output Explanation

### ✅ **Successful Test Example**
```
🎯 FINAL VERDICT:
✅ READY FOR VIDEO CHATTER APP
   This URL can be used successfully in your Streamlit app

💡 RECOMMENDATIONS:
   1. ✅ This URL is ready to use in the Video Chatter app!
```

### ❌ **Failed Test Example**
```
🎯 FINAL VERDICT:
❌ NOT READY FOR VIDEO CHATTER APP
   This URL cannot be used in your Streamlit app

💡 RECOMMENDATIONS:
   1. App couldn't retrieve transcript content
   2. This might be a temporary issue - try again later
```

## Understanding Test Results

### **Step-by-Step Analysis**

1. **URL Accessibility**: Checks if the YouTube URL responds
2. **Video ID Extraction**: Tests URL parsing (validates app logic)
3. **Transcript Availability**: Lists all available transcripts
4. **App Compatibility**: Checks for supported languages
5. **Integration Testing**: Tests actual app functions

### **Language Support**

The app supports transcripts in:
- **English** (en)
- **German** (de) 
- **French** (fr)
- **Spanish** (es)

### **Transcript Types**

- **👤 Manual**: Human-created transcripts (usually more accurate)
- **🤖 Auto-generated**: YouTube's automatic transcripts

## Files Included

### **Main Tools**
- `test_youtube_url.py` - Primary testing tool (recommended)
- `test_url.sh` - Simple shell wrapper
- `sample_test_urls.txt` - Example URLs for testing

### **Diagnostic Tools**
- `diagnose_transcript.py` - Low-level API diagnostics
- `test_transcript_enhanced.py` - Multi-method comparison
- `utility_fixed.py` - Fixed utility functions

## Common Issues and Solutions

### **Issue: "no element found: line 1, column 0"**
This is a known issue with the YouTube Transcript API that can occur due to:
- YouTube API changes
- Network connectivity issues
- Temporary YouTube restrictions

**Solutions:**
1. Try again later
2. Test with different videos
3. Check internet connection
4. Use the diagnostic tools to investigate further

### **Issue: "No supported language found"**
The video has transcripts, but not in supported languages.

**Solutions:**
1. Look for videos with English, German, French, or Spanish transcripts
2. Check if the video has auto-generated transcripts in supported languages
3. Consider expanding language support in the app

### **Issue: "Transcripts are disabled"**
The video owner has disabled transcripts.

**Solutions:**
1. Try a different video
2. Look for educational or professional content (usually has transcripts)
3. Check channels that typically provide captions

## Best Practices

### **Finding Compatible Videos**

1. **Educational Content**: Khan Academy, Coursera, university lectures
2. **Tech Talks**: Conference presentations, developer tutorials
3. **News Content**: Major news channels usually provide transcripts
4. **Popular Channels**: Large creators often enable auto-generated transcripts

### **Testing Workflow**

1. **Single Test First**: Test one URL to understand the format
2. **Batch Testing**: Use batch mode for multiple URLs
3. **Keep Good URLs**: Save working URLs for future use
4. **Regular Testing**: Re-test URLs periodically as YouTube policies change

## Troubleshooting

### **Installation Issues**
```bash
# Install required packages
pip install -r requirements.txt

# Test basic functionality
python3 -c "from youtube_transcript_api import YouTubeTranscriptApi; print('API available')"
```

### **Permission Issues**
```bash
# Make shell script executable
chmod +x test_url.sh
```

### **Network Issues**
```bash
# Test basic connectivity
curl -I https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Advanced Usage

### **Custom URL Lists**

Create themed URL lists for different content types:

```bash
# Create tech-focused URL list
cat > tech_urls.txt << EOF
# Tech and AI videos
https://www.youtube.com/watch?v=example1
https://www.youtube.com/watch?v=example2
EOF

python3 test_youtube_url.py --batch tech_urls.txt
```

### **Automated Testing**

```bash
# Test and save results
python3 test_youtube_url.py --batch sample_test_urls.txt > test_results.txt

# Filter successful URLs (example)
grep -B5 "READY FOR VIDEO CHATTER APP" test_results.txt
```

## Integration with Main App

Once you find compatible URLs using the test tools:

1. **Copy the URL**: Use URLs that show "✅ READY FOR VIDEO CHATTER APP"
2. **Run Streamlit App**: `streamlit run app.py`
3. **Paste URL**: Enter the tested URL in the app
4. **Enjoy**: The transcript should download successfully

## Future Enhancements

Potential improvements to the test feature:
- **Transcript Quality Scoring**: Rate transcript accuracy
- **Content Analysis**: Analyze transcript content for suitability
- **Caching**: Cache test results to avoid repeated API calls
- **Export Features**: Export compatible URLs to different formats
- **Integration Testing**: Test with actual Bedrock API calls

## Support

If you encounter issues:

1. **Check the diagnostic tools**: Use `diagnose_transcript.py` for low-level debugging
2. **Test with known-good URLs**: Try popular educational videos
3. **Check YouTube API status**: YouTube occasionally has API issues
4. **Update dependencies**: Ensure `youtube-transcript-api` is up to date

The command-line test feature provides a robust way to validate YouTube URLs before using them in your Video Chatter application, saving time and preventing frustration during app usage.
