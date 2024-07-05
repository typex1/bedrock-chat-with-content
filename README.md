# Video Chatter

This app summarizes YouTube videos and makes them conversational.

### The Architecture

![Video Chat Architecture](video-chat-arch.png)

1. A user enters a YouTube video URL to summarize.
2. The Streamlit app takes the URL, parses it to get the video ID, and calls the YouTube API to get the video transcript.
3. The app builds a prompt from the transcript and passes it to Bedrock for summarization using a predefined model.
4. Bedrock summarizes the transcript based on the generated prompt and returns the summary to the user.
5. If users have follow-up questions, the app builds a conversation memory using Langchain and answers follow-up questions based on content from the original transcript.

> Read more about the implementation details in this [blog post](https://community.aws/content/2hPtf0UuIXSLqJk5MKolbOoA7Qv/how-i-built-a-video-chatter-app-with-almost-zero-code).


### Installation

1. **Clone the repo**
   ```sh
   git clone https://github.com/typex1/bedrock-chat-with-content.git

2. **Move to root directory**
   ```sh
   cd video-chat

3. **Install requirements**
   ```sh
   pip install -r requirements.txt

>The code as is works on Streamlit. If you like to change it to work on your local environment, follow steps 4, 5, and 6. Otherwise, jump directly to step 7.


4. **Create .streamlit folder in your home directory**
   ```sh
   mkdir .streamlit

5. **cd into .streamlit directory**  
   ```sh
   cd .aws

6. **Create secrets.toml file and add AWS credentials in the file -  do not forget the quotation marks**
    ```sh
   ACCESS_KEY="<Your AWS Access Key>"
   SECRET_KEY="<Your AWS Secret Access Key>"

7. **From the repo root folder, run the following command to run the application in the browser**
   ```sh
   streamlit run app.py
