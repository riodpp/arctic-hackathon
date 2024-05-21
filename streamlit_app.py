import streamlit as st
import os
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

replicate_api = os.getenv('REPLICATE_API_TOKEN')

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

        Don't ask following question to me, just count the nutrition facts

        Make the output like these format:
        
        | Nutrient | Amount | Daily Value |
        |----------|--------|-------------|

        Can you help me calculate the nutritional information?

        Thank you!
    """
    return prompt

@st.experimental_dialog("Result")
def show_dialog(response):
    with st.spinner('Wait for it...'):
        st.write(response)

st.title("🍓 NutriJUZZ 🍇")
st.subheader("Welcome to NutriJUZZ, Your AI-Powered Nutrition Counter")

st.text("""
    Unlock the full potential of your homemade juices with NutriJuice, 
    the revolutionary app designed to transform your juicing experience. 
    Powered by advanced AI technology, NutriJuice effortlessly calculates the nutritional value of every sip, 
    ensuring you stay informed and healthy.
""")

tab_main, tab_how_to = st.tabs(["🍊 Juice it", "❔ How to Use"])

with tab_main:
    # Dynamic input fields
    num_items = st.number_input("Number of items to blend:", min_value=1, max_value=5, value=1)
    items = []
    for i in range(num_items):
        item = st.text_input(f"Enter the name of item {i+1}:", key=f"item_{i}")
        if item:
            items.append(item)

    # # Calculate nutritional information
    if st.button("Calculate Nutrition"):
        response = generate_arctic_response(generate_prompt(items))
        show_dialog(response)

    

with tab_how_to:
    st.markdown("""
        ### How to Use NutriJUZZ
        1. Enter the name of the food items you want to blend. You can enter up to 5 items.
        2. Click the 'Calculate Nutrition' button.
        3. NutriJUZZ will calculate the nutritional information for you.
                
        ### Note
        - If the list is more than one, NutriJUZZ will calculate the result of blending all the food.
        - If there is an item that is not a food, NutriJUZZ will ignore it in the calculation.
        - You can enter the amount of each item in the name, e.g., 'Apple 200g', '1 pcs of banana'.
        - If there is no information about the serving size, NutriJUZZ will assume it as 100g.
    """)

# with st.sidebar:

#     # Streamlit app
#     st.markdown('<h1 class="title">🍓 NutriJUZZ 🍇</h1>', unsafe_allow_html=True)
    
#     # Dynamic input fields
#     num_items = st.number_input("Number of items to blend:", min_value=1, max_value=5, value=1)
#     items = []
#     for i in range(num_items):
#         item = st.text_input(f"Enter the name of item {i+1}:", key=f"item_{i}")
#         if item:
#             items.append(item)

# # Calculate nutritional information
# if st.sidebar.button("Calculate Nutrition"):
#     with st.chat_message("assistant"):
#         response = generate_arctic_response(generate_prompt(items))
#         full_response = st.write_stream(response)

