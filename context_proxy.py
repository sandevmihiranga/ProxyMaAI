# proxyMa_AI v5.0
# Infinite Scroll Context Engine
# Aggressive Context Compression + Sliding Memory
# Designed for llama.cpp / OpenAI-compatible APIs

import requests
import json
import threading
import time
from collections import deque

# ================= CONFIG =================
API_URL = "http://127.0.0.1:8080/v1/chat/completions"
MODEL_NAME = "local-model"

SYSTEM_PROMPT = "You are a fast, smart, concise assistant."

# ================= CONTEXT SETTINGS =================
MAX_CONTEXT = 1536

# Trigger shifting when context reaches this %
SHIFT_TRIGGER = 0.82

# AGGRESSIVE shifting
SHIFT_PERCENT = 0.22

# Max recent convo memory
MAX_ACTIVE_MESSAGES = 18

# How many summaries to keep
MAX_SUMMARIES = 6

# Prevent giant replies
MAX_RESPONSE_TOKENS = 700

# ================= MEMORY =================

memory = {
    "messages": deque(maxlen=MAX_ACTIVE_MESSAGES),
    "summaries": deque(maxlen=MAX_SUMMARIES),
    "facts": deque(maxlen=30)
}

# ================= TOKEN ESTIMATION =================

def estimate_tokens(text):
    return max(1, len(text) // 3)


def total_tokens():
    total = 0

    for msg in memory["messages"]:
        total += estimate_tokens(msg["content"])

    for summary in memory["summaries"]:
        total += estimate_tokens(summary)

    return total

# ================= FACT EXTRACTION =================

def extract_facts(text):
    lines = text.split(".")

    important = []

    keywords = [
        "remember",
        "important",
        "goal",
        "task",
        "project",
        "name",
        "working on",
        "using",
        "building",
        "issue",
        "problem"
    ]

    for line in lines:
        low = line.lower()

        if any(k in low for k in keywords):
            cleaned = line.strip()

            if cleaned and cleaned not in memory["facts"]:
                important.append(cleaned)

    for item in important:
        memory["facts"].append(item)

# ================= RESPONSE CLEANER =================

def remove_repetition(text):
    words = text.split()
    cleaned = []

    repeat_limit = 2

    for word in words:
        if len(cleaned) >= repeat_limit:
            if all(w.lower() == word.lower() for w in cleaned[-repeat_limit:]):
                continue

        cleaned.append(word)

    return " ".join(cleaned)

# ================= SMART MEMORY COMPRESSION =================

def compress_old_memory():
    current = total_tokens()

    if current < int(MAX_CONTEXT * SHIFT_TRIGGER):
        return

    print("\n[AGGRESSIVE CONTEXT SHIFT ACTIVATED]")

    remove_target = int(MAX_CONTEXT * SHIFT_PERCENT)
    removed_tokens = 0

    compressed_chunk = []

    while memory["messages"] and removed_tokens < remove_target:
        old_msg = memory["messages"].popleft()

        removed_tokens += estimate_tokens(old_msg["content"])

        role = old_msg["role"].upper()
        content = old_msg["content"][:180]

        compressed_chunk.append(f"{role}: {content}")

    if compressed_chunk:
        summary = " | ".join(compressed_chunk)

        # HARD truncate summaries
        if len(summary) > 1000:
            summary = summary[:1000]

        memory["summaries"].append(summary)

        print(f"[Compressed {removed_tokens} tokens into summary memory]")

# ================= BUILD MESSAGES =================

def build_messages(user_input):
    messages = []

    messages.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })

    # Inject long-term summaries
    if memory["summaries"]:
        summary_text = "\n".join(memory["summaries"])

        messages.append({
            "role": "system",
            "content": f"Conversation memory:\n{summary_text}"
        })

    # Inject extracted important facts
    if memory["facts"]:
        fact_text = "\n".join(memory["facts"])

        messages.append({
            "role": "system",
            "content": f"Important remembered facts:\n{fact_text}"
        })

    # Active rolling memory
    messages.extend(memory["messages"])

    # Current user input
    messages.append({
        "role": "user",
        "content": user_input
    })

    return messages

# ================= DUPLICATE PREVENTION =================

def prevent_duplicate_user_input(user_input):
    recent = list(memory["messages"])[-6:]

    for msg in recent:
        if msg["role"] == "user":
            if msg["content"].strip().lower() == user_input.strip().lower():
                return True

    return False

# ================= STREAM WATCHDOG =================

class StreamWatchdog:
    def __init__(self):
        self.last_token_time = time.time()
        self.running = True

    def heartbeat(self):
        self.last_token_time = time.time()

    def monitor(self):
        while self.running:
            time.sleep(5)

            if time.time() - self.last_token_time > 30:
                print("\n[Stream stalled]")
                self.running = False
                break

# ================= MODEL CALL =================

def call_model(user_input):
    messages = build_messages(user_input)

    watchdog = StreamWatchdog()

    monitor_thread = threading.Thread(target=watchdog.monitor)
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        response = requests.post(
            API_URL,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.45,
                "top_p": 0.82,
                "repeat_penalty": 1.28,
                "presence_penalty": 0.15,
                "frequency_penalty": 0.10,
                "stream": True,
                "cache_prompt": True,
                "n_predict": MAX_RESPONSE_TOKENS
            },
            stream=True,
            timeout=300
        )

        full_response = ""

        print("\nAI: ", end="", flush=True)

        for line in response.iter_lines():
            if not watchdog.running:
                break

            if line:
                decoded = line.decode("utf-8")

                if decoded.startswith("data: "):
                    decoded = decoded[6:]

                if decoded == "[DONE]":
                    break

                try:
                    data = json.loads(decoded)

                    delta = data["choices"][0]["delta"]

                    if "content" in delta:
                        token = delta["content"]

                        watchdog.heartbeat()

                        print(token, end="", flush=True)

                        full_response += token

                        # LIVE SHIFTING DURING GENERATION
                        if total_tokens() >= int(MAX_CONTEXT * SHIFT_TRIGGER):
                            compress_old_memory()

                        # HARD response limiter
                        if estimate_tokens(full_response) >= MAX_RESPONSE_TOKENS:
                            print("\n\n[Response capped]")
                            break

                except:
                    continue

        watchdog.running = False

        print("\n")

        return full_response

    except Exception as e:
        watchdog.running = False
        return f"[ERROR] {e}"

# ================= POST PROCESS =================

def post_process(reply):
    reply = remove_repetition(reply)

    words = reply.split()

    if len(words) > MAX_RESPONSE_TOKENS:
        reply = " ".join(words[:MAX_RESPONSE_TOKENS])

    return reply

# ================= MEMORY INSERT =================

def store_conversation(user_input, reply):
    memory["messages"].append({
        "role": "user",
        "content": user_input
    })

    memory["messages"].append({
        "role": "assistant",
        "content": reply
    })

    extract_facts(user_input)
    extract_facts(reply)

# ================= STATUS PANEL =================

def print_stats():
    print("\n============================")
    print(f"Active messages : {len(memory['messages'])}")
    print(f"Summaries       : {len(memory['summaries'])}")
    print(f"Stored facts    : {len(memory['facts'])}")
    print(f"Estimated tokens: {total_tokens()}")
    print("============================\n")

# ================= MAIN LOOP =================

print("\nproxyMa_AI v5.0 Started")
print("Infinite Scroll Context Engine Enabled")
print("Aggressive Sliding Memory Active")
print("Type 'stats' to view memory status")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    if user_input.lower() == "stats":
        print_stats()
        continue

    if prevent_duplicate_user_input(user_input):
        print("[Duplicate prompt ignored]\n")
        continue

    # PRE-SHIFT
    compress_old_memory()

    reply = call_model(user_input)

    reply = post_process(reply)

    store_conversation(user_input, reply)

    # POST-SHIFT
    compress_old_memory()