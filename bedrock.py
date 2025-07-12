import boto3
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_aws import ChatBedrock
import streamlit as st
from typing import Dict


from botocore.config import Config
retry_config = Config(
        region_name = 'us-east-1',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
)


class SessionChatMessageHistory:
    """Chat message history that stores messages in Streamlit session state"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        if f"chat_history_{session_id}" not in st.session_state:
            st.session_state[f"chat_history_{session_id}"] = ChatMessageHistory()
    
    def get_session_history(self) -> BaseChatMessageHistory:
        return st.session_state[f"chat_history_{self.session_id}"]
    
    def clear(self):
        """Clear the chat history"""
        st.session_state[f"chat_history_{self.session_id}"] = ChatMessageHistory()


def bedrock_chain():
    """Create a modern LangChain conversation chain using RunnableWithMessageHistory"""
    ACCESS_KEY = st.secrets["ACCESS_KEY"]
    SECRET_KEY = st.secrets["SECRET_KEY"]
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    
    bedrock_runtime = session.client("bedrock-runtime", config=retry_config)
    # bedrock model ids: https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html   
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    model_kwargs = { 
        "max_tokens": 4096,  
        "temperature": 0.0,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman"],
    }
    
    model = ChatBedrock(
        client=bedrock_runtime,
        model_id=model_id,
        model_kwargs=model_kwargs,
    )
    
    # Create a modern chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "I want you to provide a comprehensive summary of this text provided, and then list the key points. Finally, write a short conclusion about what the video is about."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    # Create the chain
    chain = prompt | model
    
    # Create session-based message history
    session_id = st.session_state.get("user_id", "default")
    message_history = SessionChatMessageHistory(session_id)
    
    # Create the conversation chain with message history
    conversation_chain = RunnableWithMessageHistory(
        chain,
        lambda session_id: message_history.get_session_history(),
        input_messages_key="input",
        history_messages_key="history",
    )
    
    # Store the message history manager for later use
    conversation_chain._message_history_manager = message_history
    
    return conversation_chain


def run_chain(chain, prompt):
    """Run the chain with the given prompt using the modern invoke method"""
    try:
        # Get the session ID for message history
        session_id = st.session_state.get("user_id", "default")
        
        # Use the modern invoke method instead of the deprecated __call__
        result = chain.invoke(
            {"input": prompt},
            config={"configurable": {"session_id": session_id}}
        )
        
        # Extract the content from the AIMessage response
        if hasattr(result, 'content'):
            return {"response": result.content}
        else:
            return {"response": str(result)}
            
    except Exception as e:
        st.error(f"Error running chain: {str(e)}")
        return {"response": f"Error: {str(e)}"}


def clear_memory(chain):
    """Clear the conversation memory using the modern approach"""
    try:
        if hasattr(chain, '_message_history_manager'):
            chain._message_history_manager.clear()
            return True
        else:
            # Fallback: clear from session state directly
            session_id = st.session_state.get("user_id", "default")
            if f"chat_history_{session_id}" in st.session_state:
                st.session_state[f"chat_history_{session_id}"] = ChatMessageHistory()
            return True
    except Exception as e:
        st.error(f"Error clearing memory: {str(e)}")
        return False
