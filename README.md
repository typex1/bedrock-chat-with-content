# Video Chatter

This app summarizes YouTube videos and makes them conversational.

### The Architecture

![Video Chat Architecture](video-chat-arch.png)

1. A user enters a YouTube video URL to summarize.
2. The Streamlit app takes the URL, parses it to get the video ID, and calls the YouTube API to get the video transcript.
3. The app builds a prompt from the transcript and passes it to Bedrock for summarization using a predefined model.
4. Bedrock summarizes the transcript based on the generated prompt and returns the summary to the user.
5. If users have follow-up questions, the app builds a conversation memory using Langchain and answers follow-up questions based on content from the original transcript.

Updates:
* Added video transcript support for two further languages, other than **English**, which is **Spanish** and **German**.
* **NEW: Command-Line Test Feature** - Test YouTube URLs from the command line to verify transcript availability before using in the app
* **NEW: LangChain Modernization** - Updated to modern LangChain patterns, eliminating all deprecation warnings
* English example video (20:06 minutes): https://www.youtube.com/watch?v=DgpYiysQjeI "The Future Of AI, According To Former Google CEO Eric Schmidt"
* Spanish example video (3:11 minutes): https://www.youtube.com/watch?v=x2vrg7HuM6g "¿Qué es AWS?"
* German example video (17:43 minutes): https://www.youtube.com/watch?v=5tYG2L7Lwcc "Die Zettelkasten Methode - kurz erklärt"

> Read more about the implementation details in this [blog post](https://community.aws/content/2hPtf0UuIXSLqJk5MKolbOoA7Qv/how-i-built-a-video-chatter-app-with-almost-zero-code).

### Command-Line Test Feature

The v3 version includes a **command-line test feature** that allows you to test YouTube URLs before using them in the Streamlit app:

**Quick Test:**
```bash
python3 test_youtube_url.py "https://www.youtube.com/watch?v=-zF1mkBpyf4"
```

**Batch Testing:**
```bash
python3 test_youtube_url.py --batch sample_test_urls.txt
```

**Interactive Mode:**
```bash
python3 test_youtube_url.py --interactive
```

This feature helps you:
- ✅ Verify transcript availability before running the app
- 🔍 Check language compatibility (English, German, French, Spanish)
- 📊 Get detailed analysis of video accessibility
- 💡 Receive actionable recommendations for problematic URLs

See `CLI_TEST_FEATURE.md` for comprehensive documentation.

### LangChain Modernization

The v4 version includes **modernized LangChain code** that eliminates all deprecation warnings:

**Key Improvements:**
- ✅ **Zero Deprecation Warnings**: Clean console output
- ✅ **Modern Patterns**: Uses `RunnableWithMessageHistory` instead of deprecated `ConversationChain`
- ✅ **Future-Proof**: Compatible with LangChain 1.0+
- ✅ **Better Performance**: Modern execution patterns with `invoke()` method

**Technical Changes:**
- Updated from `ConversationChain` to `RunnableWithMessageHistory`
- Replaced `PromptTemplate` with `ChatPromptTemplate`
- Modern memory management with Streamlit session integration
- Uses `invoke()` instead of deprecated `__call__()` method

See `LANGCHAIN_MODERNIZATION.md` for comprehensive technical details.


### Installation

1. **Clone the repo**
   ```sh
   git clone https://github.com/typex1/bedrock-chat-with-content.git

2. **Move to root directory**
   ```sh
   cd bedrock-chat-with-content

3. **Install requirements**
   ```sh
   pip install -r requirements.txt

>The code as is works on Streamlit. If you like to change it to work on your local environment, follow steps 4, 5, and 6. Otherwise, jump directly to step 6.


4. **Create .streamlit folder in this repository root directory, and cd into it**
   ```sh
   mkdir .streamlit && cd .streamlit

5. **Create a "secrets.toml" file and add AWS credentials in the file -  please keep the quotation marks**
    ```sh
   cat << EoF >> secrets.toml
   ACCESS_KEY="<Your AWS Access Key>"
   SECRET_KEY="<Your AWS Secret Access Key>"
   EoF

6. **From the repository root folder, run the following command to run the application in the browser**
   ```sh
   streamlit run app.py
