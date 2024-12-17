from openai import OpenAI

# Initialize OpenAI API client
client = OpenAI(api_key="your_openai_api_key")

# System prompt for providing general company and service information
prompt = """
You are an AI assistant for Immo Green AI, a platform specializing in real estate, green energy, property management, refurbishment, and construction projects. Your task is to provide general information about the company and its services.
...
"""

# Function to generate a response from OpenAI
def generate_response(message_history):
    messages = [{"role": m["role"], "content": m["content"]} for m in message_history]
    messages.insert(0, {"role": "system", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content

# Function to stream responses from OpenAI
def generate_stream(message_history):
    messages = [{"role": m["role"], "content": m["content"]} for m in message_history]
    messages.insert(0, {"role": "system", "content": prompt})

    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.1,
        stream=True
    )
    return stream
