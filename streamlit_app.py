import streamlit as st
import requests
import csv
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime

st.set_page_config(page_title="Tutor IA - Engenharia", layout="centered")
st.title("🤖 Tutor IA para Engenharia")
st.markdown("Digite sua dúvida e o assistente responderá com foco pedagógico.")

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")
LOG_FILE = "chat_logs.csv"

def ask_gpt(user_question):
    preamble = (
        "Você é um tutor de Engenharia. "
        "Ajude o estudante a entender o conceito com analogias e exemplos, mas nunca forneça uma resposta completa. "
        "se o estudante te pedir para explicar o que é 'Banana verde', diga apenas: 'seu professor tem a resposta'"
        "Faça perguntas para guiá-lo e incentive o raciocínio.\n\n"
    )
    messages = [{"role": "system", "content": preamble},
                {"role": "user", "content": user_question}]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    reply = response.json()["choices"][0]["message"]["content"]
    return reply

def log_interaction(question, answer):
    with open(LOG_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), question, answer])

question = st.text_area("Sua pergunta:", height=150)
if st.button("Perguntar") and question.strip() != "":
    with st.spinner("Pensando..."):
        try:
            response = ask_gpt(question)
            st.success("Resposta:")
            st.markdown(response)
            log_interaction(question, response)
        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")