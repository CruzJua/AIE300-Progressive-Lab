// All visuals where done by claude Sonnet 4.6
const API_URL_CHAT = "http://localhost:8000/chat";

const chatWidget   = document.getElementById("chat-widget");
const chatToggle   = document.getElementById("chat-toggle");
const chatWindow   = document.getElementById("chat-window");
const chatInput    = document.getElementById("chat-input");
const chatSendBtn  = document.getElementById("chat-send-btn");
const chatSendLbl  = document.getElementById("chat-send-label");

// ── Toggle open / collapsed ───────────────────────────────────────────────────
chatToggle.addEventListener("click", () => {
    const isCollapsed = chatWidget.classList.toggle("collapsed");
    chatToggle.setAttribute("aria-expanded", String(!isCollapsed));
    // Focus the input when opening so the user can type immediately
    if (!isCollapsed) {
        setTimeout(() => {
            chatInput.focus();
            scrollToBottom();
        }, 310);
    }
});

// Persists the full conversation so multi-turn context works
let conversationHistory = [];

// ── Send message on button click ──────────────────────────────────────────────
chatSendBtn.addEventListener("click", sendMessage);

// ── Send message on Enter (Shift+Enter inserts newline) ───────────────────────
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// ── Auto-grow the textarea ────────────────────────────────────────────────────
chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
});

// ── Core send logic ───────────────────────────────────────────────────────────
async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Render the user bubble immediately
    appendMessage("user", text);
    chatInput.value = "";
    chatInput.style.height = "auto";

    // Show loading state
    setLoading(true);
    const loadingBubble = appendLoadingIndicator();

    try {
        const res = await fetch(API_URL_CHAT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: text,
                conversation_history: conversationHistory,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();

        conversationHistory = data.conversation_history;

        loadingBubble.remove();
        appendMessage("ai", data.reply);
    } catch (err) {
        loadingBubble.remove();
        appendMessage("ai", `⚠️ Error: ${err.message}`);
    } finally {
        setLoading(false);
    }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Append a user or AI message bubble and scroll into view. */
function appendMessage(role, text) {
    const bubble = document.createElement("div");
    bubble.classList.add("chat-msg", role === "user" ? "user" : "ai");
    bubble.textContent = text;
    chatWindow.appendChild(bubble);
    scrollToBottom();
    return bubble;
}

/** Append the animated three-dot loading bubble. */
function appendLoadingIndicator() {
    const bubble = document.createElement("div");
    bubble.classList.add("chat-msg", "loading");
    bubble.innerHTML = `
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
    `;
    chatWindow.appendChild(bubble);
    scrollToBottom();
    return bubble;
}

/** Toggle the send button's disabled / spinner state. */
function setLoading(isLoading) {
    chatSendBtn.disabled = isLoading;
    chatSendLbl.textContent = isLoading ? "…" : "Send";
    chatSpinner.hidden = !isLoading;
}

/** Scroll the chat window to the very bottom. */
function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
