

---

# 🚗 CodeAlpha FAQ Chatbot – README

## 📖 Project Overview

This project is a **Flask-based web application** where users can ask questions about the **automotive domain**.
The chatbot combines:

* A **local LLM** (Mistral via Ollama)
* A predefined **FAQ knowledge base** (JSON file with 100 Q\&A about cars)

to deliver accurate and relevant answers.

---

## 📂 Project Structure

```
project/
│── app.py                # Flask backend
│── static/
│    └── script.js        # Frontend JavaScript
│── templates/
│    └── index.html       # Frontend UI
│── requirements.txt      # Python dependencies
│── FAQ.json              # JSON file with 100 Q&A about cars
│── README.md             # Documentation
```

---

## ⚙️ Installation

1. **Clone the repository**:

```bash
git clone https://github.com/Hamel82/CodeAlpha_Chatbot.git
cd automobile-faq-chatbot
```

2. **Create and activate a virtual environment**:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

---

## 📦 Dependencies (`requirements.txt`)

```txt
Flask==3.0.3
requests
```

> ⚠️ Ollama does not need to be added here (it runs outside Python).

---

## 🚀 Running the Application

1. You can install localy (not in the Virtual environment)Ollama with your browser [here](https://ollama.com/download)
    

2. **Start your local Ollama model** (e.g., Mistral):

```bash
ollama run mistral
```


3. **Run Flask**:

```bash
python app.py
```

4. **Open the app** in your browser:

👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📘 FAQ JSON (`FAQ.json`)

This file contains **100+ questions and answers about cars**.
You can edit it to add, remove, or update entries.

**Example:**

```json
[
  {
    "question": "What does ABS stand for in a car?",
    "answer": "ABS stands for Anti-lock Braking System. It prevents wheels from locking during braking."
  },
  {
    "question": "What is the function of a catalytic converter?",
    "answer": "A catalytic converter reduces harmful emissions by converting exhaust gases into less toxic substances."
  }
]
```

---

## 🌐 How It Works

1. The **user asks a question** in the web UI.
2. Flask **checks the FAQ JSON** for a matching answer.
3. If no match is found, the query is sent to **Mistral (via Ollama)**.
4. The **response is displayed** in the chat interface.

---

## ✨ Features

✔️ 100+ predefined Q\&A in `FAQ.json`
✔️ Flask backend with REST API
✔️ Simple HTML/CSS/JS frontend
✔️ Integration with Ollama (Mistral)
✔️ Easily extendable to other domains

---

## 📌 Customization

* **Add more Q\&A or modify It according to a specific subject:** edit `FAQ.json`.
* **Change the model:** in `app.py`, update:

```python
model = "mistral"
```

to, for example:

```python
model = "llama3"
```

(as long as the model is installed via Ollama).

---

## 👨‍💻 Author

Developed by **Hamel82** 🚀
Passionate about **AI and automobiles**.

---


