from groq import Groq

from app.core.config import GROQ_API_KEY
from app.services.data_loader import multi_search, rebuild_index

client = Groq(api_key=GROQ_API_KEY)

MODEL       = "llama-3.3-70b-versatile"
MAX_TOKENS  = 1024
TEMPERATURE = 0.3


# ── Query Expansion ───────────────────────────────────────────────────────────
def expand_query(question: str) -> list[str]:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a query expansion assistant. "
                        "Given a question, return exactly 2 alternative rephrasings "
                        "that mean the same thing but use different words. "
                        "Return ONLY the 2 questions, one per line, no numbering, no explanation."
                    ),
                },
                {"role": "user", "content": question},
            ],
            temperature=0.5,
            max_tokens=100,
        )
        raw      = response.choices[0].message.content.strip()
        variants = [q.strip() for q in raw.split("\n") if q.strip()][:2]
        return [question] + variants
    except Exception:
        return [question]


# ── Conversation Memory ───────────────────────────────────────────────────────
def build_context_query(messages: list[dict]) -> str:
    user_msgs = [m["content"] for m in messages if m["role"] == "user"]
    return " ".join(user_msgs[-3:])


# ── Main Generate Function ────────────────────────────────────────────────────
def generate_answer(messages: list[dict]) -> str:
    latest_question = messages[-1]["content"]
    context_query   = build_context_query(messages)
    queries         = expand_query(context_query)
    context         = multi_search(queries, k=5)

    history = messages[-7:-1] if len(messages) > 6 else messages[:-1]

    system_prompt = f"""You are a helpful and knowledgeable college assistant.

Answer student questions using ONLY the information in the context below.

FORMATTING RULES — follow these strictly:
- Use **bold** for important terms, names, and labels.
- Use markdown tables (with | pipes |) whenever the answer involves fees, schedules, marks, comparisons, or any structured data.
- Use numbered lists (1. 2. 3.) ONLY for step-by-step sequences or procedures.
- Use bullet points (- item) for ALL lists of items, features, clubs, options, or any non-sequential data.
- NEVER repeat the same number (like 1. 1. 1.) — if items are not steps, use bullet points instead.
- Use headings (## Heading) when the answer has multiple distinct sections.
- Keep paragraphs short — maximum 3 lines each.
- Never write a wall of plain text when a table or list would be clearer.

CONTENT RULES:
- If the answer is in the context, answer confidently.
- If the context has partial info, share what you know and say what's missing.
- If the answer is NOT in the context at all, say exactly:
  "I don't have that information in the college database."
- Never make up information.

Retrieved Context:
{context}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": latest_question},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    return response.choices[0].message.content


# ── Utility ───────────────────────────────────────────────────────────────────
def refresh_knowledge_base() -> str:
    rebuild_index()
    return "Knowledge base refreshed successfully."
