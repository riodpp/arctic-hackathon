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
def generate_arctic_response(prompt):

    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "top_k": 50,
            "top_p": 0.9,
            "prompt": prompt,
            "temperature": 0.2,
            "max_new_tokens": 512,
            "min_new_tokens": 0,
            "stop_sequences": "<|im_end|>",
            # "prompt_template": "<|im_start|>system\nYou're a helpful assistant<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n\n<|im_start|>assistant\n",
            "presence_penalty": 1.15,
            "frequency_penalty": 0.2
        },
    ):
        yield str(event)
        
def generate_prompt(user_input):
    user_input_string = ",".join(user_input)
    prompt = f"""
        You're a Nutrition Expert,
        Below is the food that I want you to count the nutritional information:
        {user_input_string}
        If the list is more than one please count for the result of blending all the food.
        If there is an item that not a food, please ignore it in calculation and tell me.
        if there is no information about the serving size, please assume it as 100g.

        Make the output like these format:
        
        | Nutrient | Amount | Daily Value |
        |----------|--------|-------------|

        Don't ask following question to me, just count the nutrition facts
        Can you help me calculate the nutritional information?

        Thank you!
    """
    return prompt


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm Arctic, a new, efficient, intelligent, and truly open language model created by Snowflake AI Research. Ask me anything."}]

with st.chat_message("assistant"):
    st.write("Hello 👋, I'm your nutrition advisor, Please fill the field in the left.")

with st.sidebar:

    # Streamlit app
    st.markdown('<h1 class="title">🍓 NutriJUZZ 🍇</h1>', unsafe_allow_html=True)
    
    # Dynamic input fields
    num_items = st.number_input("Number of items to blend:", min_value=1, max_value=5, value=1)
    items = []
    for i in range(num_items):
        item = st.text_input(f"Enter the name of item {i+1}:", key=f"item_{i}")
        if item:
            items.append(item)

# Calculate nutritional information
if st.sidebar.button("Calculate Nutrition"):
    clear_chat_history()
    st.write(get_num_tokens("Generate a poem about the Python programming language."))
    with st.chat_message("assistant"):
        response = generate_arctic_response(generate_prompt(items))
        full_response = st.write_stream(response)
    
    st.write(get_num_tokens(full_response))

