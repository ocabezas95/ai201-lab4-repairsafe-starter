# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
Routine DIY tasks involving basic component swaps or cosmetic fixes at existing locations where mistakes cause no major damage (e.g., patching drywall, changing a showerhead).
```

**caution:**
```
Doable but inherently risky repairs on existing systems where a mistake could result in localized damage or require a professional to correct, but won't immediately cause catastrophic system failure (e.g., replacing an existing outlet, replacing a faucet).
```

**refuse:**
```
Complex, highly hazardous infrastructure tasks, or any task where an amateur mistake could cause fire, flooding, structural failure, severe injury, or death, or tasks requiring structural modifications and building permits (e.g., adding a brand-new electrical circuit, working on gas lines).
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
Use a definitions + few-shot approach: provide the three tier definitions plus 4–6 boundary-focused examples (especially caution vs refuse), then require the model to first identify risk signals (electrical/gas/structural/water damage, new infrastructure vs replacement-at-existing-location, permit-level work), and finally output one tier. For ambiguous questions (e.g., “can I replace my own outlets?”), default to **caution** unless the task clearly includes high-hazard or new-system/permit-level work, in which case classify as **refuse**.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
TIER: [safe | caution | refuse]
REASON: [One-sentence explanation of the decision rule applied]

The code will split by lines, look for the 'TIER:' prefix, strip whitespace, and convert to lowercase to match against our valid tiers
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a home repair safety classification judge. Your job is to analyze a user's home repair question and assign it to exactly one of three safety tiers: safe, caution, or refuse.

CRITERIA:
- safe: Routine DIY tasks involving basic component swaps or cosmetic fixes at existing locations where mistakes cause no major damage (e.g., patching drywall, changing a showerhead).
- caution: Doable but inherently risky repairs on existing systems where an amateur mistake could cause localized damage or require a professional to correct, but will not cause immediate catastrophic failure (e.g., replacing an existing wall outlet, replacing a leaky faucet).
- refuse: Complex, hazardous infrastructure tasks, or any task where an amateur mistake could cause fire, flooding, structural failure, severe injury, or death, or tasks requiring structural modifications and building permits (e.g., adding a brand-new electrical circuit, running or fixing gas lines).

CRITICAL BOUNDARY RULE:
If an amateur mistake could result in fire, flooding, structural failure, severe injury, or death -> you MUST classify as refuse. 
Pay close attention to "replacing existing" vs. "adding new": replacing an existing light switch is caution; adding a completely new outlet or circuit requiring new lines to the breaker panel is refuse.

OUTPUT FORMAT:
You must output your decision using the exact keys below on separate lines. Do not include any introductory text, markdown formatting blocks, or extra punctuation.

TIER: [safe | caution | refuse]
REASON: [A one-sentence explanation of the specific rule applied]
```

**User message:**
```
Analyze the following home repair request and classify it according to your instructions.

User Request: "{user_question}"
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Rule: A repair falls into the refuse tier if an amateur mistake could immediately result in fire, flooding, structural failure, severe injury, or death; otherwise, if the risk is localized to minor property damage or easily correctable by a professional, it belongs in caution.

Example A (Caution): "How do I replace a single wall outlet that stopped working?"

Which side: Caution

Why: It deals with an existing circuit at a pre-established location. The component itself is swapped out directly. If the amateur messes up, the worst-case scenario is typically a tripped circuit breaker or a localized dead outlet—not an immediate catastrophic structure failure.

Example B (Refuse): "How do I add a brand-new electrical outlet to my garage?"

Which side: Refuse

Why: This requires modifying the home’s infrastructure—opening the main breaker panel, running new wiring through studs, and introducing a brand-new load. An amateur mistake here can create a hidden arc/fire hazard behind walls that won't be discovered until it's too late.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
1.Fallback Strategy
Design: If the LLM's response cannot be successfully parsed into a valid tier, or if the extracted string is not found in VALID_TIERS (["safe", "caution", "refuse"]), the function will default to "caution".

2. Rationale
Why: It is better to over-refuse and err on the side of caution than to accidentally let a highly dangerous infrastructure task (like a gas leak repair) default to a "safe" classification because of a formatting anomaly.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
[your answer here]
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
[your answer here]
```
