const AGENT_API_URL = "http://localhost:8000/agent";

const agentTaskInput = document.getElementById("agent-task-input");
const agentSubmitBtn = document.getElementById("agent-submit-btn");
const agentLoading = document.getElementById("agent-loading");
const agentConfirmModal = document.getElementById("agent-confirmation-modal");
const agentToolNameSpan = document.getElementById("tool-name-span");
const agentToolArgsPre = document.getElementById("tool-args-pre");
const agentConfirmBtn = document.getElementById("agent-confirm-btn");
const agentDenyBtn = document.getElementById("agent-deny-btn");
const agentTraceDrawer = document.getElementById("agent-trace-drawer");
const agentTraceList = document.getElementById("agent-trace-list");
const agentTraceCount = document.getElementById("agent-trace-count");
const agentConversationWindow = document.getElementById("agent-conversation-window");

let currentAgentMessages = [];
let pendingToolCallId    = null;

// ── Submit handler ────────────────────────────────────────────────────────────
agentSubmitBtn.addEventListener("click", () => {
    const task = agentTaskInput.value.trim();
    if (!task) return;

    appendAgentBubble("user", task);

    agentTraceList.innerHTML = "";
    agentTraceCount.textContent = "0";
    agentTraceDrawer.removeAttribute("open");

    currentAgentMessages = [];
    runAgent(task);
});

agentTaskInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        agentSubmitBtn.click();
    }
})

// ── Confirmation handlers ─────────────────────────────────────────────────────
agentConfirmBtn.addEventListener("click", () => {
    currentAgentMessages.push({
        role: "user",
        content: [{
            type: "tool_result",
            tool_use_id: pendingToolCallId,
            content: "User confirmed action. Please proceed with the tool execution in your next turn or output final message."
        }]
    });
    runAgent(agentTaskInput.value, currentAgentMessages);
});

agentDenyBtn.addEventListener("click", () => {
    currentAgentMessages.push({
        role: "user",
        content: [{
            type: "tool_result",
            tool_use_id: pendingToolCallId,
            content: "User DENIED action. Do NOT execute the tool. Inform user."
        }]
    });
    runAgent(agentTaskInput.value, currentAgentMessages);
});

function appendAgentBubble(role, text) {
    const div = document.createElement("div");
    div.classList.add("chat-msg", role === "user" ? "user" : "ai");
    div.textContent = text;
    agentConversationWindow.appendChild(div);
    agentConversationWindow.scrollTop = agentConversationWindow.scrollHeight;
}

// ── Core agent fetch ──────────────────────────────────────────────────────────
async function runAgent(task, messages = []) {
    agentTaskInput.value   = "";
    agentLoading.style.display  = "block";
    agentConfirmModal.style.display = "none";
    agentSubmitBtn.disabled = true;

    try {
        const response = await fetch(AGENT_API_URL, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ task, messages })
        });
        const data = await response.json();

        agentLoading.style.display = "none";

        if (data.steps && data.steps.length > 0) {
            agentTraceDrawer.open = true;
            data.steps.forEach(step => {
                const li = document.createElement("li");
                li.innerHTML =
                    `<strong>${step.tool}</strong>:<br>` +
                    `Input: <code>${JSON.stringify(step.input)}</code><br>` +
                    `Output: <em>${step.output}</em>`;
                agentTraceList.appendChild(li);
            });
            agentTraceCount.textContent = agentTraceList.children.length;
        }

        if (data.status === "requires_confirmation") {
            currentAgentMessages = data.messages;
            pendingToolCallId = data.tool_call_to_confirm.id;
            agentToolNameSpan.textContent = data.tool_call_to_confirm.name;
            agentToolArgsPre.textContent  = JSON.stringify(data.tool_call_to_confirm.input, null, 2);
            agentConfirmModal.style.display = "block";

        } else if (data.status === "complete" || data.status === "error") {
            appendAgentBubble("agent", data.result ?? "No response.");
            renderItems();
        }

    } catch (err) {
        agentLoading.style.display = "none";
        appendAgentBubble("agent", "Error: " + err.message);
    } finally {
        agentSubmitBtn.disabled = false;
    }
}