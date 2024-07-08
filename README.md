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
* English example video (20:06 minutes): https://www.youtube.com/watch?v=x2vrg7HuM6g "The Future Of AI, According To Former Google CEO Eric Schmidt"
* Spanish example video (3:11 minutes): https://www.youtube.com/watch?v=x2vrg7HuM6g "¿Qué es AWS?"
* German example video (39:49 minutes): https://www.youtube.com/watch?v=rSV2bUp3eAw "TikTok-Experte: “Das machen ALLE bei Lead-Gewinnung falsch!" (Akin Colak Interview)

> Read more about the implementation details in this [blog post](https://community.aws/content/2hPtf0UuIXSLqJk5MKolbOoA7Qv/how-i-built-a-video-chatter-app-with-almost-zero-code).


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

>The code as is works on Streamlit. If you like to change it to work on your local environment, follow steps 4, 5, and 6. Otherwise, jump directly to step 7.


4. **Create .streamlit folder in this repository root directory**
   ```sh
   mkdir .streamlit

5. **cd into .streamlit directory**  
   ```sh
   cd .streamlit

6. **Create a "secrets.toml" file and add AWS credentials in the file -  please keep the quotation marks**
    ```sh
   cat << EoF >> secrets.toml
   ACCESS_KEY="<Your AWS Access Key>"
   SECRET_KEY="<Your AWS Secret Access Key>"
   EoF

7. **From the repository root folder, run the following command to run the application in the browser**
   ```sh
   streamlit run app.py
