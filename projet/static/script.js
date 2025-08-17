const chat = document.getElementById("chat");
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");
const debug = document.getElementById("debug");

// Option: afficher infos techniques (similarité, question reformulée)
const SHOW_DEBUG = true;

function addMessage(role, text){
    const wrap = document.createElement("div");
    wrap.className = `msg ${role}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    wrap.appendChild(bubble);
    chat.appendChild(wrap);
    chat.scrollTop = chat.scrollHeight;
}

function addTyping(){
    const wrap = document.createElement("div");
    wrap.className = "msg assistant";
    wrap.id = "typing";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    const dots = document.createElement("span");
    dots.className = "typing";
    bubble.appendChild(dots);
    wrap.appendChild(bubble);
    chat.appendChild(wrap);
    chat.scrollTop = chat.scrollHeight;
}
function removeTyping(){
    const t = document.getElementById("typing");
    if (t) t.remove();
}

async function sendMessage(message){
    addMessage("user", message);
    addTyping();
    sendBtn.disabled = true; input.disabled = true;

    try{
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({ message })
        });
        const data = await res.json();

        removeTyping();
        if (data.error){
            addMessage("assistant", "Erreur: " + data.error);
        }else{
            addMessage("assistant", data.reply || "(réponse vide)");
            if (SHOW_DEBUG){
                debug.classList.remove("hidden");
                debug.textContent = `match: ${data.matched_question ?? "aucun"} | sim: ${data.similarity} | reformulée: ${data.reformulated}`;
            }
        }
    }catch(e){
        removeTyping();
        addMessage("assistant", "Erreur réseau. Vérifie que le backend et Ollama tournent.");
    }finally{
        sendBtn.disabled = false; input.disabled = false; input.focus();
    }
}

form.addEventListener("submit", (e)=>{
    e.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;
    input.value = "";
    sendMessage(msg);
});

resetBtn.addEventListener("click", async ()=>{
    await fetch("/api/reset", { method: "POST" });
    addMessage("assistant", "Mémoire réinitialisée. Repartons de zéro !");
    debug.classList.add("hidden");
    debug.textContent = "";
});

window.addEventListener("load", ()=>{
    addMessage("assistant", "Bonjour 👋 Posez votre question (ex.: horaires, paiement, support…).");
    input.focus();
});
