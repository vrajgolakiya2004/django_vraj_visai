import os
import groq
from . import retriever

# Load API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Initialize Groq client
client = groq.Client(api_key=GROQ_API_KEY)
 
def generate_response(user_query, user_data=None):
    """Generate a short and accurate LLM response based on retrieved PDF data and optional user data."""
    retrieved_context = retriever.retrieve_similar(user_query, top_k=3)
    print("Retrieved Context for Query:", user_query)
    print("Context:", retrieved_context)
   
    if not retrieved_context.strip():
        print("Warning: Retrieved context is empty!")
 
    user_info = "" if not user_data else "\n".join(
        [f"{key}: {value}" for key, value in user_data.items() if value]
    )
 
    prompt = f"""
    You are a helpful and professional marketing assistant.
    You MUST use ONLY the information in 'Retrieved Knowledge' to answer. Do NOT provide generic or external advice (e.g., buying templates) unless explicitly in the knowledge.
    Keep the response short, accurate, and helpful (2–4 sentences max). Avoid repetition and extra explanation.
 
    If the answer is not available in 'Retrieved Knowledge', reply: "I'm sorry, I don't have enough information to answer that."
 
    ---
    User Query: {user_query}
 
    User Data:
    {user_info}
 
    Retrieved Knowledge:
    {retrieved_context}
    """
 
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a concise marketing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=120,
        top_p=0.8,
    )
 
    return response.choices[0].message.content.strip()
 
 
# Local test
if __name__ == "__main__":
    query = "What is internet marketing success?"
    user_data = {"business_type": "e-commerce", "experience_level": "beginner"}
    response = generate_response(query, user_data)
    print(f"\nResponse: {response}")
 
 