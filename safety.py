from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    TODO — Milestone 1:

    Before writing any code, complete specs/classifier-spec.md. The blank fields
    there are the decisions that drive this implementation — prompt design, tier
    definitions, output format, and edge case handling.

    Your implementation should:
      1. Build a prompt using your tier definitions that asks the LLM to classify
         the question and explain its reasoning
      2. Send a single chat completion request (no tools, no history)
      3. Parse the tier and reason out of the raw response text
      4. Validate the tier against VALID_TIERS; fall back to "caution" if the
         response can't be parsed or the tier isn't recognized
      5. Return {"tier": ..., "reason": ...}

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned

    The three tiers:
      - "safe"    : routine, low-risk repairs most homeowners can handle safely
      - "caution" : doable with care, but mistakes have real cost or mild risk
      - "refuse"  : high-risk repairs that require a licensed professional —
                    mistakes can cause fire, flooding, injury, or structural damage
    """
    system_message = (
        "You are a home repair safety classification judge. Your job is to "
        "analyze a user's home repair question and assign it to exactly one of "
        "three safety tiers: safe, caution, or refuse.\n\n"
        "CRITERIA:\n"
        "- safe: Routine DIY tasks involving basic component swaps or cosmetic "
        "fixes at existing locations where mistakes cause no major damage "
        "(e.g., patching drywall, changing a showerhead).\n"
        "- caution: Doable but inherently risky repairs on existing systems "
        "where an amateur mistake could cause localized damage or require a "
        "professional to correct, but will not cause immediate catastrophic "
        "failure (e.g., replacing an existing wall outlet, replacing a leaky "
        "faucet).\n"
        "- refuse: Complex, hazardous infrastructure tasks, or any task where "
        "an amateur mistake could cause fire, flooding, structural failure, "
        "severe injury, or death, or tasks requiring structural modifications "
        "and building permits (e.g., adding a brand-new electrical circuit, "
        "running or fixing gas lines).\n\n"
        "CRITICAL BOUNDARY RULE:\n"
        "If an amateur mistake could result in fire, flooding, structural "
        "failure, severe injury, or death -> you MUST classify as refuse.\n"
        "Pay close attention to \"replacing existing\" vs. \"adding new\": "
        "replacing an existing light switch is caution; adding a completely "
        "new outlet or circuit requiring new lines to the breaker panel is "
        "refuse.\n\n"
        "OUTPUT FORMAT:\n"
        "You must output your decision using the exact keys below on separate "
        "lines. Do not include any introductory text, markdown formatting "
        "blocks, or extra punctuation.\n\n"
        "TIER: [safe | caution | refuse]\n"
        "REASON: [A one-sentence explanation of the specific rule applied]"
    )

    user_message = (
        "Analyze the following home repair request and classify it according "
        "to your instructions.\n\n"
        f'User Request: "{question}"'
    )

    fallback = {
        "tier": "caution",
        "reason": "Could not reliably classify the request, so defaulting to "
        "caution.",
    }

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        )
        raw = response.choices[0].message.content
    except Exception:
        return fallback

    if not raw:
        return fallback

    tier = None
    reason = None
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("TIER:"):
            tier = stripped.split(":", 1)[1].strip().lower()
        elif stripped.upper().startswith("REASON:"):
            reason = stripped.split(":", 1)[1].strip()

    if tier not in VALID_TIERS:
        return fallback

    return {
        "tier": tier,
        "reason": reason or "No reason provided by the classifier.",
    }
