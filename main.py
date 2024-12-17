import streamlit as st
import openai # Import the OpenAI API client

# Streamlit UI setup
st.set_page_config(
    page_title="Immo Green AI",
    page_icon="🏡",
    menu_items={
        'About': "This app is a prototype made for demo purposes. It is not meant for real life use. Do not take anything from this app as advice."
    }
)
st.title("Immo Green AI")

# Prompt for system to provide general company and service information
prompt = """
You are an AI assistant for Immo Green AI, a platform specializing in real estate, green energy, property management, refurbishment, and construction projects. Your task is to provide general information about the company and its services. Below is an outline of your responses:

Company Overview:
- Immo Green AI is a platform designed to assist users with real estate, green energy, future technologies, and related services.
- It provides access to a range of services including buying or selling real estate, property management, renovation, and construction planning.
- The platform also integrates AI-driven features to help users search for properties and receive tailored advice.

General Information:
- Immo Green AI offers both real estate and green energy solutions, catering to private and business customers.
- The platform provides tools for real estate searches, advice, and a variety of services such as refurbishment, renovation, and future-focused building solutions.
- Users can engage in a live chat with consultants or receive automated AI-generated responses for general inquiries.

Available Features Without Registration:
- Answering general questions about the company and its services.
- Providing basic information and guidance on how to use the platform.
- Offering an interactive chat for quick inquiries about real estate and green energy.

Contacting Consultants:
- For more specific inquiries or property searches, users will be directed to register and log in to access personalized advice and services.
- If a user wants detailed advice or has specific questions, they will be notified that a consultant will respond within a set time frame.

Chat Availability:
- The chat function is available across all pages, providing assistance and general information about how the platform works and the services offered.
- A welcome message in the chat will greet users and offer guidance: “How can we help you? Please log in or register to experience the full AI system.”
"""

# Function to generate a response from OpenAI
def generate_response(message_history, api_key):
    openai.api_key = api_key  # Set the API key provided by the user
    messages = [{"role": m["role"], "content": m["content"]} for m in message_history]
    messages.insert(0, {"role": "system", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Specify the model you want to use
        messages=messages
    )
    return response['choices'][0]['message']['content']

# Function to stream responses from OpenAI
def generate_stream(message_history, api_key):
    openai.api_key = api_key  # Set the API key provided by the user
    messages = [{"role": m["role"], "content": m["content"]} for m in message_history]
    messages.insert(0, {"role": "system", "content": prompt})

    stream = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the model you want to use
        messages=messages,
        temperature=0.1,
        stream=True
    )
    return stream

# Input field for the user to enter their OpenAI API key
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if api_key:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        response = generate_response(st.session_state.messages, api_key)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(name="assistant", avatar="👨‍⚕️"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Accept user input for the chat
    if prompt := st.chat_input("Message Chief-GPT"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message(name="assistant", avatar="👨‍⚕️"):
            stream = generate_stream(st.session_state.messages, api_key)
            response = st.write_stream(stream)

        # Append assistant response to session history
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.warning("Please enter your OpenAI API key to use the service.")
