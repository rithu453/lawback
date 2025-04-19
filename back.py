# from fastapi import FastAPI
# from pydantic import BaseModel
# import requests
# from bs4 import BeautifulSoup
# import google.generativeai as genai
# from fastapi.middleware.cors import CORSMiddleware

# # Set up Gemini
# GEMINI_API_KEY = "AIzaSyCwdDvKqc-W9Ucmve5tU2OemneMPvymVEA"
# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel("gemini-pro")




# app = FastAPI()

# # Allow all origins (good for local dev)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Or specify frontend URL e.g. ["http://localhost:3000"]
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class QueryRequest(BaseModel):
#     prompt: str

# # 📍 /query — Chatbot route
# @app.post("/query")
# async def query_gemini(request: QueryRequest):
#     response = model.generate_content(request.query)
#     print(response.text)
#     return {"response": response.text}

# # 🔎 /news — Legal news from TOI
# @app.get("/news")
# async def get_legal_news():
#     url = "https://timesofindia.indiatimes.com/topic/Legal/news"
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, "html.parser")

#     articles = soup.select("._3T5do > a")[:5]  # Update if TOI changes layout
#     news = []
#     for article in articles:
#         title = article.get_text(strip=True)
#         link = "https://timesofindia.indiatimes.com" + article["href"]
#         news.append({"title": title, "link": link})

#     return {"legal_news": news}


from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# Set up Gemini
GEMINI_API_KEY = "AIzaSyCwdDvKqc-W9Ucmve5tU2OemneMPvymVEA"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

# Allow all origins (good for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify frontend URL e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

available_models = genai.list_models()
print(available_models)


# Define the QueryRequest model
class QueryRequest(BaseModel):
    query: str  # Expecting 'query' in the frontend request

# 📍 /query — Chatbot route
@app.post("/query")
async def query_gemini(request: QueryRequest):
    # Define the system prompt to constrain Gemini's responses
    system_prompt = """
    You are LAWRA, a specialized legal assistant focused exclusively on providing information about Indian law and the Indian legal system.

    Guidelines:
    1. Only respond to questions related to Indian law, legal procedures, rights, and the Indian legal system.
    2. If a question is not related to Indian legal matters, politely explain that you can only provide information about Indian legal topics and suggest they rephrase their question.
    3. Do not provide specific legal advice for individual cases - instead, provide general legal information and suggest consulting with a qualified Indian legal professional.
    4. For questions about laws in other jurisdictions, politely redirect to Indian law or decline to answer.
    5. Always cite relevant Indian legal codes, acts, or precedents when appropriate.
    6. When uncertain about a specific legal detail, acknowledge the limitation and suggest reliable Indian legal resources.
    7. Present information in clear, accessible language while maintaining accuracy.

    Remember: You are not a substitute for professional legal counsel. Your purpose is to provide general information about Indian law and the Indian legal system only.
    """
    
    # Combine the system prompt with the user's query
    full_prompt = f"{system_prompt}\n\nUser Query: {request.query}\n\nResponse:"
    
    # Send the combined prompt to Gemini
    response = model.generate_content(full_prompt)
    
    # Return the generated response
    return {"response": response.text}

# 🔎 /news — Legal news from TOI
@app.get("/news")
async def get_legal_news():
    url = "https://timesofindia.indiatimes.com/topic/Legal/news"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we handle failed requests
        soup = BeautifulSoup(response.content, "html.parser")

        # Select the articles correctly (verify selector if needed)
        articles = soup.select("._3T5do > a")[:5]
        news = []
        for article in articles:
            title = article.get_text(strip=True)
            link = "https://timesofindia.indiatimes.com" + article["href"]
            news.append({"title": title, "link": link})

        if not news:
            return {"error": "No legal news found."}

        return {"legal_news": news}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching news: {str(e)}"}
