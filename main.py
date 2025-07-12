import os
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

app = FastAPI()

env = Environment(loader=FileSystemLoader('/app/templates'))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GRAFANA_API_KEY = "glsa_vGKPhVud2RUO35V5yX4VbI69Hs5DMShf_7402c00b"
GRAFANA_URL = "https://observ-stg.cloud-ng.net"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

chat_history = []

@app.get("/", response_class=HTMLResponse)
async def get_home():
    global chat_history
    chat_history = []  # Clear chat history on each fresh GET
    template = env.get_template("index.html")
    return template.render(chat_history=chat_history)

@app.post("/", response_class=HTMLResponse)
async def post_prompt(request: Request, prompt: str = Form(...)):
    global chat_history

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "You are an intelligent assistant. If the user's question is general knowledge, answer it directly. If it's about Grafana dashboards or metrics, respond accordingly."},
                {"role": "user", "content": prompt}
            ]
        )

        message = response.choices[0].message.content

    except Exception as e:
        message = f"Error: {str(e)}"

    chat_history.append({"prompt": prompt, "response": message})

    template = env.get_template("index.html")
    return template.render(chat_history=chat_history)
