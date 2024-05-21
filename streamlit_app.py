import streamlit as st
import os
from transformers import AutoTokenizer
import replicate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Custom CSS for title
st.markdown(
    """
    <style>
    .title {
        font-size: 48px;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# if 'REPLICATE_API_TOKEN' in st.secrets:
#     #st.success('API token loaded!', icon='✅')
#     replicate_api = st.secrets['REPLICATE_API_TOKEN']
# else:
replicate_api = os.getenv('REPLICATE_API_TOKEN')

@st.cache_resource(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

# Function for generating Snowflake Arctic response
def generate_arctic_response():

    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "top_k": 50,
            "top_p": 0.9,
            "prompt": "Generate a poem about the Python programming language.",
            "temperature": 0.2,
            "max_new_tokens": 512,
            "min_new_tokens": 0,
            "stop_sequences": "<|im_end|>",
            "prompt_template": "<|im_start|>system\nYou're a helpful assistant<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n\n<|im_start|>assistant\n",
            "presence_penalty": 1.15,
            "frequency_penalty": 0.2
        },
    ):
        yield str(event)
        

with st.chat_message("assistant"):
    st.write("Hello 👋")

with st.sidebar:

    # Streamlit app
    st.markdown('<h1 class="title">🍓 NutriJUZZ 🍇</h1>', unsafe_allow_html=True)
    
    # Dynamic input fields
    num_items = st.number_input("Number of items to blend:", min_value=1, max_value=10, value=1)
    items = []
    for i in range(num_items):
        item = st.text_input(f"Enter the name of item {i+1}:", key=f"item_{i}")
        if item:
            items.append(item)

# Calculate nutritional information
if st.sidebar.button("Calculate Nutrition"):
    st.write(get_num_tokens("Generate a poem about the Python programming language."))
    with st.chat_message("assistant"):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
    
    st.write(get_num_tokens(full_response))

