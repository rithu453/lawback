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
from typing import List, Optional

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
class NewsHeadline(BaseModel):
    text: str
    link: str
    image: Optional[str] = None

def get_toi_news():
    url = "https://timesofindia.indiatimes.com/topic/law"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for non-200 status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    headlines = []
    for item in soup.find_all('div', class_='uwU81'):
        link_tag = item.find('a')
        if not link_tag:
            continue
            
        headline_text = link_tag.find('span').get_text(strip=True) if link_tag.find('span') else ''
        
        # Handle relative URLs by adding base URL if needed
        headline_link = link_tag['href'] if 'href' in link_tag.attrs else ''
        if headline_link and not headline_link.startswith('http'):
            headline_link = f"https://timesofindia.indiatimes.com{headline_link}"
            
        image_tag = link_tag.find('img')
        image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''
        
        headlines.append({
            'text': headline_text,
            'link': headline_link,
            'image': image_url
        })
    
    print(f"Fetched {len(headlines)} headlines")  # Debug line
    return headlines

@app.get("/news")
async def news():
    """Returns law-related news headlines from Times of India"""
    headlines = get_toi_news()

    formatted_news = [
        {
            "title": item["text"],
            "link": item["link"],
            "image": item.get("image", "")  # Include image, default to empty string
        }
        for item in headlines
    ]

    return {"legal_news": formatted_news}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
