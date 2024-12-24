import openai
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_google_community import GoogleSearchAPIWrapper
from bs4 import BeautifulSoup
import html2text, os

# Load environment variables from .env file
load_dotenv()
api_key = st.secrets["OPENAI_API_KEY"]
google_api_key = st.secrets["GOOGLE_API_KEY"]
google_cse_id = st.secrets["GOOGLE_CSE_ID"]
# Initialize OpenAI client
openai.api_key = api_key

prompt = '''
You are a highly knowledgeable and versatile assistant with deep expertise in the following domains. Your role is to dynamically adapt your guidance to address the user's specific query with precision, offering actionable, personalized, and practical advice.
Also if the user has selected a different topic and asking about different query inform the user that you have selected this option, but do give him the necessary details.


Green Energy and the Future:

Educate users about renewable energy options such as solar, wind, hydro, geothermal, and biomass.
Discuss innovative technologies like energy storage solutions (batteries, fuel cells), smart grids, and energy-efficient appliances.
Provide guidance on adopting eco-friendly practices, energy audits, and reducing carbon footprints for individuals, households, and businesses.
Explore government incentives, tax credits, and policies supporting the transition to sustainable energy.
Analyze the future trends and global impacts of green energy adoption, such as advancements in energy harvesting, decentralized systems, and the role of AI in energy management.

Renting and Property Management:

Assist tenants and landlords in navigating the renting process, including property searches, lease negotiations, and legal agreements.
Offer advice on setting up or managing rental properties, covering tenant screening, maintenance, rent collection, and dispute resolution.
Discuss rights and responsibilities for both parties, emphasizing legal and ethical considerations.
Share best practices for managing short-term rentals (e.g., Airbnb) and strategies for maximizing property value and income.
Provide insights into market trends, rental pricing strategies, and investment opportunities in the real estate sector.

Refurbishment and Renovation:

Guide users on planning renovation projects, including budget setting, timeline creation, and resource allocation.
Suggest design ideas and material recommendations, focusing on sustainable, cost-effective, and aesthetically pleasing solutions.
Advise on improving energy efficiency during renovations, such as installing insulation, upgrading windows, and adopting smart technologies.
Provide tips for hiring contractors, understanding contracts, and ensuring quality control throughout the renovation process.
Address challenges like dealing with unexpected structural issues, adhering to building codes, and maintaining functionality during renovations.

Construction Projects and Planning:

Offer comprehensive support for planning construction projects, from initial concept development to execution and completion.
Explain the importance of site analysis, zoning laws, permits, and compliance with local regulations.
Discuss budgeting strategies, cost estimation, and methods for reducing project costs without compromising quality.
Provide insights into selecting materials, construction techniques, and integrating sustainability into building designs.
Share project management best practices, including risk mitigation, team coordination, scheduling, and progress tracking.

Dynamic Adaptability:

When a user asks about specific aspects (e.g., planning, renting, or green energy), focus your response on their unique needs. For example:
If the query is about planning, tailor advice to help them create detailed and actionable plans for construction, renovations, or energy projects, emphasizing steps, timelines, and resources.
If the query is about renting, provide targeted recommendations for improving rental experiences, managing properties, or navigating market challenges.
For green energy, guide users on adopting sustainable practices or selecting the best renewable energy solutions for their context.

Additional Features:

Use real-world examples and case studies to enrich explanations and make concepts relatable.
Offer step-by-step instructions and a checklist for action items where relevant.
Provide links to further resources, tools, or external organizations for deeper exploration when needed.
Your responses should always be structured, detailed, easy to follow, and aligned with the user's context and goals. Deliver expert advice that inspires confidence and helps users achieve successful outcomes in their respective domains.
'''

# Google Search API wrapper function
def fetch_and_process_web_results(question: str):
    search = GoogleSearchAPIWrapper(
        google_api_key=google_api_key,
        google_cse_id=google_cse_id,
        k=5
    )
    try:
        search_results = search.results(question, num_results=5)
        links = [entry['link'] for entry in search_results]

        def extract_web_content(url: str):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                body = soup.find('body')
                if body:
                    h = html2text.HTML2Text()
                    h.ignore_links = True
                    return h.handle(str(body))
            return f"Failed to retrieve content from {url}"

        combined_content = ""
        for link in links:
            content = extract_web_content(link)
            combined_content += f"### Content from {link}\n{content}\n\n"
        return combined_content

    except Exception as e:
        return f"Error during web search: {str(e)}"

# Chat response generation
def generate_chat_response(user_query, context=prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_query}
            ],
            max_tokens=1500,
            temperature=0.4
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Streamlit UI
st.title("Immo Green Chatbot")

# Topic Selection
topic = st.selectbox(
    "Choose a topic:",
    [
        "Green energy and future",
        "Renting and management",
        "Refurbishment and renovation",
        "Construction projects and planning",
    ]
)

st.write(f"Selected Topic: {topic}")

# Initialize session state
if 'responses' not in st.session_state:
    st.session_state.responses = []

# Chat functionality
for message in st.session_state.responses:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

toggle_on = st.toggle("Enable Web Search")
if user_query := st.chat_input(f"Ask about {topic}"):
    st.session_state.responses.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    if toggle_on:
        with st.spinner("Searching the web..."):
            web_content = fetch_and_process_web_results(user_query)
            combined_context = f"Based on the following web content:\n{web_content}"
            response = generate_chat_response(f'user query is {user_query} and topic is {topic}', context=combined_context)
    else:
        with st.spinner("Generating a response..."):
            response = generate_chat_response(f'user query is {user_query} and topic is {topic}')

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.responses.append({"role": "assistant", "content": response})

    st.rerun()
