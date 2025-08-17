import json
import re
import requests
from collections import deque

from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# download nltk data
"""
nltk.download('punkt')
nltk.download('stopwords')
"""
# ======== Set stop words ========
STOP_WORDS = set(stopwords.words("french"))

# ======== Config ========
FAQ_FILE = "FAQ.json"
SIMILARITY_THRESHOLD = 0.4  # minimum threshold to consider a match
MEMORY_SIZE = 6  # nombre max de tours gardés en mémoire
OLLAMA_MODEL = "mistral"  # max number of laps kept in memory
OLLAMA_URL = "http://localhost:11434/api/generate"  # endpoint Ollama

# ---------- Init app ----------
app = Flask(__name__)

# ======== LOAD FAQ ========
with open(FAQ_FILE, "r", encoding="utf-8") as f:
    faq_data = json.load(f)

questions = [item["question"] for item in faq_data]
answers = [item["answer"] for item in faq_data]

# ======== PREPROCESS ========
stop_words = set(stopwords.words('french'))

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in stop_words]
    return " ".join(tokens)

preprocessed_questions = [preprocess(q) for q in questions]

# ======== TF-IDF ========
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(preprocessed_questions)

# ======== MEMORY ========
memory = deque(maxlen=MEMORY_SIZE)

# ======== OLLAMA - LLM Helpers - CALL ========
def call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    """Call Ollama local; return text or raise requests.HTTPError."""
    response = requests.post(OLLAMA_URL, json=payload, timeout=90)
    response.raise_for_status()
    return response.json()["response"].strip()

def reformulate_question_with_context(user_msg: str) -> str:
    context = "\n".join([m["role"] + ": " + m["content"] for m in memory])
    prompt = (
        "You are an assistant reformulating a short, clear user question for an FAQ search engine."
        "Don't answer, just rephrase the QUESTION as a single, self-contained sentence, without politeness or quotation marks.\n\n"
        f"Context (recent history):\n{context}\n\n"
        f"User question:\n{user_msg}\n\n"
        "QUESTION rephrased:"
    )
    try:
        x=call_ollama(prompt)
        print(x)
        return x
    except Exception:
        # Fallback: if Ollama fails, just return the original question
        return user_msg


def rewrite_answer_nicely(raw_answer: str, user_msg: str) -> str:
    prompt = (
        "Rewrite the FAQ answer in a natural and polite way, without inventing information."
        "Stay concise and keep the EXACT meaning.\n\n"
        f"User question: {user_msg}\n"
        f"FAQ answer:\n{raw_answer}\n\n"
        "Reworded answer:"
    )
    try:
        return call_ollama(prompt)
    except Exception:
        return raw_answer

def answer_in_outofcontext(user_msg: str) -> str:
    prompt = (
        " Rewrite a natural and polite answer to the following question using only the information available in the FAQ."
        " Don't guess or provide any external information."
        " The FAQ doesn't contain anything useful to this specifically question or message, respond concisely that the answer is not known."
        " User Question: {user_question}"
        " Answer: "
    )
    return call_ollama(prompt)


# ---------- Core search ----------
def search_faq(query: str):
    proc = preprocess(query)
    qvec = vectorizer.transform([proc])
    sims = cosine_similarity(qvec, tfidf_matrix)[0]
    idx = int(sims.argmax())
    return idx, float(sims[idx])


# ---------- Routes ----------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# ======== CHATBOT ========
@app.route("/api/chat", methods=["POST"])
def chatbot_response():

    data = request.get_json(silent=True) or {}
    user_msg = (data.get("message") or "").strip()
    print("user_msg: ", user_msg)
    final_answer = None
    matched_question = None
    if not user_msg:
        return jsonify({"error": "message manquant"}), 400

    #  Search FAQ
    best_match_index, best_sim = search_faq(user_msg)

    # if we are in out of context
    if not (best_sim >= SIMILARITY_THRESHOLD):
        final_answer = answer_in_outofcontext(user_msg)

        return jsonify({
            "reply": final_answer,
            "matched_question": matched_question,
            "similarity": round(best_sim, 3),
            "reformulated": None
        })

    # Add to memory
    memory.append({"role": "user", "content": user_msg})

    # Reformulate with Mistral
    reformulated = reformulate_question_with_context(user_msg)

    print("reformulated: ", reformulated)

    print("best_match_index: ", best_match_index)
    print("best_sim: ", best_sim)

    # if best similarity is found
    if best_sim >= SIMILARITY_THRESHOLD:
        raw_answer = answers[best_match_index]
        # Reformuler réponse
        final_answer = call_ollama(
            f"Rewrite this answer in a natural way while keeping the meaning. : {raw_answer}"
        )
        matched_question = questions[best_match_index]

    # Save response in the memory
    memory.append({"role": "assistant", "content": final_answer})

    return jsonify({
        "reply": final_answer,
        "matched_question": matched_question,
        "similarity": round(best_sim, 3),
        "reformulated": reformulated
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    memory.clear()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
