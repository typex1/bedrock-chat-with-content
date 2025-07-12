#!/bin/bash
# Simple wrapper script for testing YouTube URLs

# Check if URL is provided
if [ $# -eq 0 ]; then
    echo "🎬 YouTube Transcript Tester"
    echo "Usage: $0 <youtube_url>"
    echo ""
    echo "Examples:"
    echo "  $0 'https://www.youtube.com/watch?v=-zF1mkBpyf4'"
    echo "  $0 'https://youtu.be/dQw4w9WgXcQ'"
    echo ""
    echo "For more options, use: python3 test_transcript.py --help"
    exit 1
fi

# Run the Python test script
python3 test_transcript.py "$1" --verbose
