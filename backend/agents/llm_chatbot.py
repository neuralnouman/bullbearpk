import os

def call_groq_llm(prompt, system_message=None, model="llama3-70b-8192"):
    import openai
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    openai.api_key = GROQ_API_KEY
    openai.base_url = "https://api.groq.com/openai/v1"
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    client = openai.OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content 