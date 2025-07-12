import uuid
import bedrock
import utility
import streamlit as st


USER_ICON = "images/user-icon.png"
AI_ICON = "images/bedrock.png"

# browser tab title:
# spec: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(page_title="yt bedrock chat")

if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
else:
    user_id = str(uuid.uuid4())
    st.session_state["user_id"] = user_id

if "llm_chain" not in st.session_state:
    st.session_state["llm_app"] = bedrock
    st.session_state["llm_chain"] = bedrock.bedrock_chain()

if "questions" not in st.session_state:
    st.session_state.questions = []
    input_label = "Enter a Youtube Video URL, other content URL or \"S3\"  to Summarize "
    
else:
    input_label = "❗Ask Me Here If You Need More Details.❗" 

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""


def write_top_bar():
    col1, col2, col3 = st.columns([2, 10, 3])
    with col2:
        header = "Chat with content from Youtube or S3 documents!"
        st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)
        description = """
        Summarize content and then ask further questions!            
        example video: https://www.youtube.com/watch?v=-zF1mkBpyf4
        """
        st.write(f"<p class=''>{description}", unsafe_allow_html=True)
    with col3:
        clear = st.button("Start Over")

    return clear


clear = write_top_bar()

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    input_label = "Enter the Youtube url to summarize"
    bedrock.clear_memory(st.session_state["llm_chain"])


def handle_input():
    input = st.session_state.input
    llm_chain = st.session_state["llm_chain"]
    chain = st.session_state["llm_app"]

    question = input
    content_type = ""

    if len(st.session_state.questions)==0:
        video_id, content_type = utility.validate_url(input)

        if content_type == "youtube":
            transcript = utility.get_content(video_id, "youtube")
            if not transcript:
                st.error("The video provided has no English, French, Spanish or German transcript. Sorry I can't help here.")
                st.session_state.input = ""
                return None


        # Generate prompt from transcript
        input = utility.generate_prompt_from_transcript(transcript)
        
        
    result = chain.run_chain(llm_chain, input)

    question_with_id = {
        "question": question,
        "id": len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)

    st.session_state.answers.append(
        {"answer": result, "id": len(st.session_state.questions)}
    )
    st.session_state.input = ""


def write_user_message(md):
    col1, col2 = st.columns([1, 12])

    with col1:
        st.image(USER_ICON, use_container_width="always")
    with col2:
        st.warning(md["question"])


def render_answer(answer):
    col1, col2 = st.columns([1, 12])
    with col1:
        st.image(AI_ICON, use_container_width="always")
    with col2:
        st.info(answer["response"])


def write_chat_message(md):
    chat = st.container()
    with chat:
        render_answer(md["answer"])




with st.container():
    for q, a in zip(st.session_state.questions, st.session_state.answers):
        write_user_message(q)
        write_chat_message(a)


st.markdown("---")

input = st.text_input(
    input_label, key="input", on_change=handle_input
)

st.markdown(
    """
    <style>
        .small-font {
            font-size: 12px;
        }
    </style>
    <div style='position: fixed; bottom: 0; left: 0;'>
        <p class="small-font">Feedback: https://github.com/typex1</p>
        <p class="small-font"> This app doesn't represent my employer</p>
    </div>
    
    """,
    unsafe_allow_html=True
)
