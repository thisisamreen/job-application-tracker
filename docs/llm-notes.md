# LLM Notes — Job Application Tracker

Running notes on the LLM part of this project: what each piece does, why it was chosen,
and what was rejected. Written to be read later by future me, or a peer.

---

## 1. What problem the LLM solves here

Pipeline:

```
Sheet (JD URL)
  -> fetch JD text            (requests + JSON-LD)        no LLM
  -> parse JD into fields     (rules first, LLM second)   LLM
  -> pick resume bullets      (IDs from master file)      LLM
  -> rephrase chosen bullets  (checked by validator)      LLM
  -> render .docx             (resume.py)                 no LLM
  -> write results to Sheet   (gspread)                   no LLM
```

The LLM is used **only** where the input is messy language and there is no labelled data.
Everything with a fixed vocabulary or pattern stays as plain Python.

### What is deliberately NOT used

| Not used | Why |
|---|---|
| Fine-tuning / training a model | Needs hundreds of labelled (JD, ideal output) pairs. We have zero |
| RAG (vector DB, embeddings, retrieval) | RAG solves "too much text to fit in the prompt". Our master bullets are ~2K tokens and fit in every prompt. Adding a vector DB here would be decoration, not engineering |
| Autonomous agents | Nothing here needs the model to decide its own steps. The pipeline is fixed, so ordinary function calls are safer and cheaper |

RAG becomes relevant only if the bullet library grows to hundreds of entries, or if
we start searching across many stored JDs. Note the condition; don't build it early.

---

## 2. Provider choice

| Provider | Status in this project |
|---|---|
| **Google Gemini API** | **In use.** Has a real free tier, enough for ~3 JDs a day |
| Claude API | Best instruction-following, but paid (~$3-5/month at this volume). Likely switch later |
| OpenAI API | Paid. No free tier |
| Ollama (local) | Free, fully private, but a small local model is weaker at schema-constrained output |

**Privacy rule (important):** free tiers may use submitted data to improve their models.
So:

- JD text -> fine to send. It is a public job posting.
- **Master resume bullets -> do not send to a free tier.** They are personal and are the
  thing this repo deliberately keeps out of git.

Consequence: JD parsing runs on Gemini now. Bullet selection and rephrasing wait until
either (a) we pay for an API with no training on inputs, or (b) we run a local model.

**Design rule:** every model call goes through one function so the provider can be swapped
by changing `.env`, not code. This also lets the eval compare providers later.

---

## 3. Vocabulary (what the terms actually mean)

| Term | Meaning here |
|---|---|
| **Token** | ~4 characters of text. Billing and context limits are counted in tokens, not words |
| **Prompt** | Everything sent to the model: system instructions + user content |
| **System prompt** | The standing rules ("you extract fields, never invent"). Sent on every call |
| **Context window** | Max tokens one request can hold. Our whole JD + bullets is far below any modern limit |
| **Structured output** | Asking the model to return JSON matching a schema, instead of prose. Removes text parsing |
| **Schema** | The shape we require back. Defined once with Pydantic and reused for validation |
| **Temperature** | Randomness. For extraction we want it low (deterministic-ish) |
| **Stateless** | The API remembers nothing between calls. Any "memory" is text we resend |
| **Grounding** | Forcing output to come from supplied facts (our bullet IDs), not the model's own knowledge |
| **Hallucination** | Fluent output that isn't true. Handled here by validating, never by trusting |
| **Eval set** | Hand-labelled examples used to measure accuracy. The part that turns a demo into engineering |
| **RAG** | Retrieve relevant chunks from a big corpus, then put them in the prompt. Not needed at our size |

---

## 4. Setup steps

### Step 0 — API key (do this first)

1. Open https://aistudio.google.com/apikey and create an API key.
2. Add it to `.env` (already gitignored):

   ```
   GEMINI_API_KEY=...
   LLM_PROVIDER=gemini
   ```

3. Never print the key, never commit it, never paste it into a chat.

### Step 1 — Install the SDK

```bash
pip install google-genai pydantic requests beautifulsoup4
```

Note: Google has two Python packages historically (`google-generativeai`, older; `google-genai`,
current). Confirm which one the current docs use before writing code against it.

### Step 2 — Confirm the key works and see which models exist

Rather than guessing a model name, ask the API to list what the key can use. Model names
change often; a list call is always accurate.

### Step 3 — First real call (JD -> structured fields)

Input: one JD text file from `data/private/jds/`.
Output: JSON with title, company, location, years required, degree, required skills,
nice-to-have skills.

What to look at in the response:
- Did it match the schema?
- Token counts (input/output) — the basis for any cost claim later.
- Where it guessed instead of leaving a field empty.

### Step 4 — Rules baseline (no LLM)

Extract the same fields with regex and keyword matching against the skills list.
Purpose: a number to compare the LLM against. Without a baseline, "the LLM works" is unmeasurable.

### Step 5 — Eval set

Hand-label 10 JDs. Score rules vs LLM per field (precision/recall). Decide per field
which method wins, and record the result here.

---

## 5. Decisions log

| Date | Decision | Reason |
|---|---|---|
| 2026-09-15 | Master bullets stay out of git, local backup only | Simpler than encryption; content rarely changes |
| 2026-09-15 | Tailored resumes are gitignored, storing IDs + full text | Self-contained record of what was actually sent |
| 2026-09-15 | Tailoring = select + checked rephrase (option B) | Selection alone is safe but doesn't match JD wording; free rewriting invents experience |
| 2026-09-17 | LinkedIn JDs pasted manually | LinkedIn blocks simple fetches; other boards work via JSON-LD or Workday's JSON endpoint |
| 2026-09-17 | Free tier (Gemini) first, not Claude | Zero cost to learn; swap later behind one function |
| 2026-09-17 | No fine-tuning, no RAG | No labelled data; corpus too small for retrieval to help |
| 2026-09-19 | ~20 past tailored resumes become the **gold eval set**, not training data | All built from the same master bullets, so each can be mapped back to bullet IDs. 20 pairs is far too few to fine-tune on, but enough to measure selection accuracy and to beat a keyword baseline. They also carry known outcomes for the predictor later |

---

## 6. Open questions

- Does the Gemini free tier train on submitted data? (Assume yes until confirmed. Governs
  whether bullets can ever be sent.)
- Which fields does the rules baseline handle well enough that the LLM is unnecessary?
- Does rephrasing actually improve response rate? (Needs many applications before it can be answered.)
