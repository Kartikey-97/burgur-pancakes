# Prompts

> This file contains all AI prompts used to build the Burgur-Pancakes AI Interview Agent over the 48-hour hackathon. Organised by team member. Prompts are listed in the order they were used.

---

## 1) Kshiraj

### AI-layer scaffold — `ai/__init__.py`

Created `ai/__init__.py` as a minimal package marker. No modules, no functionality, no new dependencies — intentionally small first step.

---

### `ai/schemas.py`

```
Now implement only ai/schemas.py.

The current repository has already been inspected and the public integration contract is confirmed.

Person A calls:

    evaluate_and_ask(
        pending_question: str,
        answer: str,
        day_obj: dict,
        candidate_profile: dict,
        theta: float,
        history: list[dict],
    ) -> dict

The combined per-turn result is:

    {
        "score": ...,
        "needs_followup": ...,
        "next_question": ...,
        "notable_quote": ...
    }

This represents ONE LLM operation per interview turn. There is no similar_prior_answer argument. SQLite is the only persistence layer. Do not add Chroma, chromadb, vector stores, or any other database.

At minimum, create a schema for the result of evaluate_and_ask() containing: score, needs_followup, next_question, notable_quote.

Do NOT put any of the following in schemas.py: Gemini/API calls, prompt construction, evaluation logic, question-generation logic, follow-up logic, embedding generation, cosine similarity, question deduplication, confidence/hedging scoring, database access, Chroma/vector-store logic.

The schema for evaluate_and_ask() must NOT contain confidence_flags. Do not create separate public schemas that imply separate LLM calls such as QuestionResponse, EvaluationResponse, FollowupResponse.

Constraints:
1. Inspect existing project/dependencies first.
2. Follow existing Python style.
3. Modify/create ONLY ai/schemas.py.
4. Keep the implementation small and easy to review.
5. Do not modify ai/__init__.py, Person A's files, or any other file.
6. After implementation, run a minimal import/validation test.
```

---

### Codebase inspection before `ai/context.py`

```
Before we do anything, examine the current codebase so that we can make a definition of the next AI-layer increment based on the current code. DO NOT change any code in any file.

Examine:
1. backend/session.py
2. backend/models.py
3. backend/orchestrator.py
4. backend/ai_layer_interface.py
5. ai/schemas.py

I need the structure of: Candidate Profile, Curriculum/Day, Interview History Entry, Theta/Ability Estimate, Pending Question, Answer, The Arguments Passed To evaluate_and_ask().

Also check that:
- ai/schemas.py has NOT been changed since last commit
- evaluate_and_ask() takes in raw history object
- Person A's Orchestrator DOES NOT compute embeddings, similarity, and confidence before calling it
- Chroma Vector Store is NOT being used anywhere

Do not implement ai/context.py just yet. Do not change any code.
```

---

### `ai/off_topic.py`

```
Implement only ai/off_topic.py for the existing Burgur-Pancakes project.

The current public contract is fixed:
    def is_off_topic(user_answer: str) -> bool

Person A calls this synchronously before evaluate_and_ask() on every INTERVIEWING turn.

Ground-truth constraints:
- Input is ONLY the raw answer string. No question, no history, no candidate profile, no curriculum context.
- Must NOT make an LLM/API call. Must NOT use a vector database.
- Keep it fast and deterministic. False positives are more harmful than false negatives.

Implement a conservative local pre-filter that detects obviously invalid/gibberish/spam-like input.

It may detect: empty/whitespace-only, keyboard-mashing/random-character strings, excessive punctuation or symbol-only, digit-only, single character repeated excessively.

It must NOT attempt semantic topic detection. Do NOT classify these as off-topic:
"Yes", "No", "Python", "O(n)", "Caching", "REST", "Transformers", "It depends", "Because it is faster.", "I would use caching here."

Also allow code-heavy answers: "x = 10 + y", "if x == y", "O(n^2) = O(n log n)", "return x == y", "HTTP 200 OK", "top_k = 10"

Requirements:
1. Create only ai/off_topic.py. Use only Python standard-library functionality.
2. Expose exactly: def is_off_topic(user_answer: str) -> bool
3. Keep it small, readable, deterministic, conservative.
4. Must fail safely — unexpected input/errors must not crash the orchestrator.
5. Do not modify backend/, ai/schemas.py, ai/context.py, ai/__init__.py, prompt.md

Validate with test cases (TRUE: "", "   ", "!!!!!!!!", "123456789", "aaaaaaaaaaaaaaaa") and (FALSE: all the allowed examples above plus several normal technical answers).
```

---

### `ai/llm.py`

```
Implement only ai/llm.py for the existing Burgur-Pancakes project. This is the next incremental Person B AI-layer step. DO NOT modify, create, delete, or format any other repository file.

Person A's backend exposes the public integration boundary:
    evaluate_and_ask(pending_question, answer, day_obj, candidate_profile, theta, history) -> dict

This is the LLM wrapper that calls the Gemini API. Expose a single function that takes a prompt string and returns generated text. Keep it thin — no prompt construction logic here, just the API call. Model should be configurable. Handle API errors gracefully.
```

---

### `ai/service.py`

```
Implement only ai/service.py for the existing Burgur-Pancakes project. This is the next incremental Person B AI-layer step. DO NOT modify, create, delete, or format any other repository file.

Current AI-layer state:
    ai/
    ├── __init__.py
    ├── schemas.py
    ├── context.py
    ├── off_topic.py
    └── llm.py

This is the service/context assembly layer. It builds the full prompt from the InterviewContext, calls the LLM wrapper, parses the JSON response, and returns an EvaluateAndAskResult. The public function signature must match Person A's expected evaluate_and_ask() call.
```

---

### `ai/confidence.py`

```
Implement only ai/confidence.py for the existing Burgur-Pancakes project. This is the next incremental Person B AI-layer step. DO NOT modify, create, delete, or format any other repository file.

Current AI-layer state:
    ai/
    ├── __init__.py
    ├── schemas.py
    ├── context.py
    ├── off_topic.py
    ├── llm.py
    └── service.py

This is a local (no LLM) confidence/hedging scorer. It should detect signals like excessive hedging ("I think", "maybe", "not sure"), contradiction patterns, and vague buzzword answers with no specifics. Returns a list of flag strings. Public API: def score_confidence(answer: str) -> list[str]
```

---

### Fix embeddings — replace Gemini API with local model

```
Update only the dependency declaration needed for the Person B local embedding implementation.

IMPORTANT: The existing ai/embeddings.py implementation is currently WRONG because it uses the Gemini embedding API. Do not use or preserve that implementation.

Current backend/requirements.txt:
    fastapi
    uvicorn
    pydantic
    requests

The local Python environment has been verified to support:
- Python 3.13.9 / Apple Silicon arm64
- sentence-transformers 5.7.0 / torch 2.13.0 / numpy 2.5.1 / Apple MPS available

Modify ONLY backend/requirements.txt to add sentence-transformers.
Then rewrite ai/embeddings.py to use the local BAAI/bge-small-en-v1.5 model.
Public API: def embed_text(text: str) -> list[float]
Load the model once at module level. Return 384-dimensional vectors as plain Python lists.
```

---

### `ai/similarity.py`

```
Implement only ai/similarity.py for the existing Burgur-Pancakes project. This is the next incremental Person B AI-layer step. DO NOT modify, create, delete, or format any other repository file.

Current AI-layer state includes ai/embeddings.py now using BAAI/bge-small-en-v1.5 returning 384-dimensional vectors as plain Python lists.

Goal: minimal local semantic similarity utility. Its only responsibility is to compare two already-computed embedding vectors and return their cosine similarity.

Public API:
    def cosine_similarity(
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> float

Use only numpy (already a transitive dependency of sentence-transformers). Do not import torch or sentence-transformers here. Keep it to ~10 lines.
```

---

### `ai/memory.py`

```
Implement only ai/memory.py for the existing Burgur-Pancakes project. This is the next incremental Person B AI-layer step. DO NOT modify, create, delete, or format any other repository file.

Current AI-layer state:
    ai/
    ├── __init__.py, schemas.py, context.py, off_topic.py
    ├── llm.py, service.py, confidence.py
    ├── embeddings.py
    └── similarity.py

Existing utilities:
- ai.embeddings.embed_text(text) -> local 384-dim embedding using BAAI/bge-small-en-v1.5
- ai.similarity.cosine_similarity(a, b) -> float
- ai.context.HistoryEntry: {day, question, answer, score, notable_quote}

Goal: Given the candidate's current answer and the existing interview history, find the most semantically similar previous interview answer. This allows evaluate_and_ask() to make callbacks like "Earlier you mentioned X — how does that apply here?"

Public API:
    def find_similar_prior_answer(
        current_answer: str,
        history: list[dict],
    ) -> Optional[dict]

Return the history entry if similarity >= 0.75, else None.
```

---

### `ai/deduplication.py`

```
Implement only ai/deduplication.py for the existing Burgur-Pancakes project. This is the next incremental Person B AI-layer step. DO NOT modify, create, delete, or format any other repository file.

Current AI-layer state:
    ai/
    ├── __init__.py, schemas.py, context.py, off_topic.py
    ├── llm.py, service.py, confidence.py
    ├── embeddings.py, similarity.py
    └── memory.py

Goal: Determine whether a newly generated interview question is semantically too similar to a question already asked. Prevents the interviewer from repeatedly asking the same question with different wording.

Public API:
    def is_duplicate_question(
        new_question: str,
        history: list[dict],
        threshold: float = 0.85,
    ) -> bool

Compare new_question against every entry["question"] in history. Return True if any similarity >= threshold.
```

---

## 2) Kartikey

### Backend architecture planning

```
I want to build an AI Interview Agent for a hackathon. The concept is a 31-day AI engineering cohort (RAG, Vector DBs, Prompt Engineering, Agentic AI, MCP, Deployment). After completing the cohort, learners need to be able to explain the systems they built. I want an agent that conducts personalized technical interviews based on a candidate's learning journey.

We have multiple team members:
- Me (Kartikey): backend API, state machine, session management, AI prompts
- AI team: LLM wrapper, evaluation logic, embeddings  
- Frontend: React/Next.js UI

What should the backend structure look like? I need FastAPI with SSE streaming, SQLite session persistence, and a state machine (INITIALIZING → QUESTIONING → EVALUATING → CLOSING).
```

---

### FastAPI backend setup — `main.py`, `models.py`, `session.py`, `data_loader.py`

```
Let's set up the FastAPI project. I need:
1. main.py — FastAPI app with CORS enabled (allow all for hackathon), /api/health endpoint, and /api/interview_stream POST endpoint returning StreamingResponse with media_type="text/event-stream"
2. models.py — TurnInterviewRequest with sessionId, message, candidate (nested: member, missions, signals), mcq_enabled. Also Feedback model.
3. session.py — SQLite persistence with load_session() and save_session() that serialize state dict as JSON. No ORM needed.
4. data_loader.py — load candidates.json and curriculum JSON at module import time into CANDIDATES and CURRICULUM globals.
```

---

### Orchestrator state machine

```
Build the orchestrator state machine in orchestrator.py. The flow:
1. INITIALIZING: First turn with empty message — select first question based on candidate's passed missions
2. QUESTIONING: Candidate sends answer — evaluate it, decide follow-up or next topic
3. After 8 questions minimum: generate feedback and close

Stream everything via SSE:
- {"type": "text", "content": "..."} for streaming tokens
- {"type": "done", "reply": "...", "done": False, "theta": float} for turn completion
- {"type": "done", "done": True, "feedback": {...}, "history": [...]} for interview end

Use yield f"data: {json.dumps(payload)}\n\n" format throughout.
```

---

### Cutoff bug fix

```
There's a bug. On the very last turn (question 8), the session ends immediately after the candidate submits their answer without letting the AI respond. The candidate's final answer gets cut off and we jump straight to results.

The issue: is_final_turn is evaluated before streaming the final AI acknowledgment. Fix it so we stream the AI's final response first, and only THEN yield the done: true event with feedback.
```

---

### Include full history in done event

```
I need to add the full interview history to the done event payload when the interview ends, so the frontend can build a per-question breakdown without an extra API call. Each history entry should have: day, question, answer, score, notable_quote, cheat_flagged.
```

---

### Cheat detection

```
Add cheat detection. If a candidate pastes a giant pre-written answer instead of typing it, the CPS (characters per second) will be impossibly high. Implement a heuristic check in the orchestrator — track last_turn_timestamp in session state, calculate CPS on each turn, flag if CPS > 300 and len(answer) > 100. Store cheat_flagged in the history entry and surface it in results.
```

---

### Interviewer Persona — system prompt for Priya

```
You are Priya Nair, a senior technical interviewer conducting a real, live technical interview. You are warm but rigorous — never robotic, never a quiz show host, never say "Question 1 of 8."

Calibrate your tone and question depth to the candidate:
- yearsExperience >= 10: assume strong fundamentals, ask about trade-offs, scale, failure modes, and "why did you choose X over Y" rather than definitions.
- yearsExperience 3-9: mix of practical "how did you build X" and conceptual depth.
- yearsExperience < 3 or non-technical jobRole (e.g. Business Analyst, Marketing, HR): favor clear, grounded questions about what they built and why it mattered, without dumbing down the subject matter itself.

Never ask about a topic the candidate skipped. You may reference it briefly in closing feedback as a gap, never as a question.

Speak in one short paragraph or less per turn. No bullet lists in the interview itself — this is a conversation, not a form.

Integrate this as the SYSTEM_PROMPT constant in ai_layer_interface.py. Also add: never say "Great answer!" or "That's correct!" — patronizing. Never introduce yourself or explain the format. If candidate says "I don't know", acknowledge briefly and move on.
```

---

### Question generation prompt

```
Context provided: curriculum day (title, tools, objectives), candidate's mission record for that day (attempts, passed), candidate profile, full prior Q&A history so far this session, and whether this is a NEW TOPIC or a FOLLOW-UP.

If NEW TOPIC and there is a relevant earlier answer in history from a different day, open with a natural callback ("Earlier you mentioned X when we talked about embeddings — how does that change when...") before asking the new question. Only do this when there's a genuine conceptual link — don't force it.

If FOLLOW-UP: the candidate's last answer was thin, evasive, or partially correct. Ask ONE targeted follow-up that probes the specific gap — don't repeat the original question in different words.

If attempts >= 4 for this day: gently probe whether their understanding is solid now, e.g. "That one took a few tries during the cohort — walk me through what clicked for you."

Output: a single question, nothing else. No preamble, no "Great, next...".

Also add: question should be answerable in 2-4 sentences — avoid multi-part compound questions. "If the candidate has already answered a highly similar question this session, do not ask it again."
```

---

### Answer evaluation prompt

```
Given: the question asked, the candidate's answer, the day's learning objectives.

Return strict JSON:
{
  "score": 0-4,
  "covers_objective": true/false,
  "needs_followup": true/false,
  "followup_reason": "string or null",
  "notable_quote": "short paraphrase of their strongest point, or null",
  "confidence_flags": []
}

SCORING RUBRIC (apply strictly):
- Score 4: Demonstrates understanding of trade-offs, failure modes, or real-world constraints BEYOND the definition.
- Score 3: Correct and specific, covers the main objective, minor gaps acceptable.
- Score 2: Correct concept, missing specifics.
- Score 1: Knows the name/buzzword only.
- Score 0: Wrong, empty, off-topic, or complete non-answer.

Score generously for correct-but-informally-worded answers. Score down for confident-but-wrong or generic-AI-buzzword answers with no specifics. Never give a 4 unless the answer demonstrates awareness of failure modes or real-world constraints beyond the textbook definition. Return ONLY valid JSON.
```

---

### Scoring is inconsistent — fix anchoring

```
The scoring is still inconsistent. I tested it — the same answer gets a 2 one time and a 4 another time. The model is being too generous. How do I lock it down more?

Rewrite the scoring anchor so it's explicit. Add: "A candidate saying 'I'm not sure but I think...' followed by a correct answer should still score 2-3, not 1." Also add: "If the answer is off-topic, return score=0, needs_followup=false."
```

---

### Feedback synthesis prompt

```
Given: full interview history (all questions, answers, scores, flags) and candidate profile.

Return strict JSON:
{
  "summary": "2-3 sentences, direct, references their actual role/trajectory",
  "strengths": ["specific, tied to a real moment in the interview, not generic"],
  "gaps": ["specific — cite the actual topic and what was missing"],
  "next": ["concrete, actionable — a specific day/topic to revisit or practice"],
  "topicScores": {"<topic>": <float 0.0-4.0>}
}

Every array item must be traceable to something that actually happened in this specific interview. No generic advice. Do NOT include items like "Study more" — every next step must name a specific topic or skill gap. Summary must mention their job role specifically. Only include topics actually tested. Calculate topicScores as the average of all question scores on that topic.
```

---

### MCQ optional format

```
The MCQ feature — if mcq_enabled is True, the AI should occasionally include multiple choice options for some questions. Prompt it to do that naturally without making every question MCQ.

Add to question generation prompt: "MCQ MODE IS ENABLED. For roughly 30-40% of questions (your discretion), you may optionally provide multiple choice options in this exact format immediately after the question:
A) [option]
B) [option]
C) [option]
D) [option]
Only use MCQ format for questions where there is a clearly correct answer. Do NOT use MCQ for open-ended questions about trade-offs, design decisions, or 'walk me through' questions. If you include options, make exactly 3 plausible and 1 clearly wrong but tempting."
```

---

### Frontend setup — Next.js state machine

```
Build the Next.js frontend. I need page.tsx as a state machine for "picker", "chat", and "results" states. Fetch from the SSE endpoint at http://localhost:8000/api/interview_stream. The typing effect isn't working — text dumps all at once instead of streaming character by character.

Implement processStream() using a while(true) loop with reader.read(), split chunks by \n\n delimiter, parse each event, and update React messages state immediately on each text chunk so the typing effect feels instantaneous.
```

---

### Restore streaming typing effect

```
The typing effect still isn't working properly. The text just appears all at once after a delay.

The issue is the TextDecoder and the SSE chunk splitting. Fix processStream in page.tsx to properly handle partial chunks — keep a partialData buffer, split on \n\n, and pop the last incomplete chunk back into the buffer before processing. Update the last message in the messages array on every text event, not at the end.
```

---

### Add MCQ checkbox to CandidatePicker

```
Add a multiple choice toggle to CandidatePicker.tsx. A checkbox labeled "Enable Multiple Choice Questions (Adaptive)". Pass enableMcq state through to the onBegin callback, then include it in the initial POST body as mcq_enabled. Also pass it in every subsequent turn POST.
```

---

### Framer Motion animations in ChatScreen

```
Add Framer Motion animations to ChatScreen.tsx:
1. Each message bubble should animate in with opacity 0 → 1, y: 14 → 0, scale: 0.97 → 1
2. Typing indicator (3 dots) should use staggered bounce animations
3. MCQ option buttons should stagger-animate in with x: 0 → 0, opacity fade
4. MCQ buttons should slide right on hover with translateX(3px)
```

---

### Complete UI/UX overhaul — split panel, live score, adaptive progress tracker

```
The UI is still ass. It isn't utilizing the full screen properly. The results are still ass. I need a complete overhaul. Make the scores out of 100 and not 4. Think this through — if you were using this then what things would you need?

Plan:
1. Chat screen: full split-panel layout. Left sidebar (280px) with candidate info, live score gauge 0-100, adaptive progress tracker that adds question bubbles dynamically as questions are asked (not fixed Q1-Q8). Right panel: full-width chat.
2. Results dashboard: hero animated circular score ring (0-100), per-question breakdown table (question, answer preview, score badge green/amber/red, cheat flag), per-day score bars ("Day 16: 71/100"), topic mastery bars, strengths/gaps/next in 3-column layout.
3. Scoring math: (score/4) * 100 on frontend.
4. Pass full history in the done event from orchestrator so frontend has everything.
```

---

### Landing page overhaul — split panel with Priya avatar and custom candidate modal

```
Make the landing screen way better. Remove the emoji mic. First impressions matter. 

Redesign into a full-screen split panel:
- Left panel: Priya Nair hero (proper SVG person icon in gradient square, green online dot), 48px gradient headline "Ace your next technical interview.", feature list with 4 items (Adaptive Questioning, Context Retention, Scored in Real-Time, Detailed Report Card), trust badges (AI Cohort, Claude Powered, IRT Scoring). Decorative radial gradient orbs in background.
- Right panel: clean white form. Replace the select dropdown with a searchable card list — each candidate is a clickable card showing name, role, years, missions passed. "Add New" button opens a slide-in modal. Modal has name/role/experience/education inputs and a day-chip grid for all 31 curriculum days. Custom candidates saved to localStorage. Animated toggle switch instead of checkbox for MCQ. Dynamic CTA button text changes to "Begin Interview with [Name] →".
```

---

### Curriculum days in custom candidate modal should start from Day 1

```
The completed curriculum options should be from Day 1. Currently only showing a subset starting from Day 7. Update the CURRICULUM_DAYS array to include all 31 days from Day 1: VS Code & Python Environment Setup through Day 31: Capstone Project & Final Demo.
```

---

### Deployment environment variable

```
Update the frontend so the API URL is configurable via environment variable for production deployment. Currently hardcoded to http://localhost:8000. The production backend is on Render at https://burgur-pancakes.onrender.com.

Change: const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://burgur-pancakes.onrender.com";

So it defaults to the Render URL in production but can be overridden locally with NEXT_PUBLIC_API_URL=http://localhost:8000.
```

---

## 3) Kunal

### Next.js project setup

```
Set up a new Next.js 14 project with TypeScript inside a frontend-next/ folder. We need App Router, not Pages Router. Install framer-motion as well. The app will be a single-page interview UI that talks to a FastAPI backend via SSE streaming. Don't set up any routing beyond the root page — this is a single-screen state machine app.
```

---

### Background animated particles component

```
Create a BackgroundParticles component in React using a canvas element. It should render soft floating particles in the background — light purple/indigo toned circles that drift slowly and fade in and out. Should be position: fixed, z-index 0, full screen, pointer-events none. Keep it lightweight — no heavy libraries, use requestAnimationFrame directly. Should feel subtle not distracting. Import it in the root layout.
```

---

### CandidatePicker first version

```
Build the CandidatePicker component. This is the first screen the user sees. It should:
- Show a card with an avatar/logo for "Priya" — the AI interviewer
- A headline: "Your personalized technical interview starts here."
- A dropdown select to choose from the list of candidates loaded from candidates.json
- When a candidate is selected, show a preview card with their name, role, years experience, and tags showing missions completed and commit days
- A "Begin Interview →" button that is disabled until a candidate is selected
- Import candidate data directly from @/data/candidates.json

Style it nicely — centered card, clean typography, soft shadows.
```

---

### ChatScreen first version

```
Build the ChatScreen component. Props: candidateName, messages (array of {role: "interviewer"|"candidate", content: string}), isTyping boolean, onSendMessage callback, qCount number.

Layout:
- Header bar showing "Technical Interview" title and a question counter pill showing "Q {qCount}"
- Scrollable messages area taking up most of the screen
- Interviewer messages on the left with an avatar, candidate messages on the right in a dark bubble
- Typing indicator (3 animated dots) when isTyping is true
- Input area at the bottom: a textarea that sends on Enter (Shift+Enter for newline), a send button

Messages should auto-scroll to bottom when new ones arrive. Use useRef and scrollIntoView.
```

---

### Parse MCQ options from message content

```
The backend sometimes returns messages with multiple choice options formatted like:
A) Some option here
B) Another option
C) Third option
D) Fourth option

In ChatScreen, detect when a message contains these options and render them as clickable buttons instead of just plain text. The question text should still show above the buttons. When a button is clicked it should call onSendMessage with the full option text. Buttons should be disabled once an option has been selected or when isTyping is true.
```

---

### ResultsDashboard first version

```
Build a ResultsDashboard component. It receives feedback (summary, strengths, gaps, next, topicScores) and a theta score. Display:
- A top summary section with the candidate's name and the summary text
- Three columns: Strengths (green), Gaps to Address (red), Next Steps (amber) — each as a list of items with a colored icon
- A radar/spider chart showing topicScores — use a simple SVG polygon chart, no chart library needed
- A "Start Another Interview" button that calls onRestart

Keep the design clean and readable. This is what the candidate sees at the end so it needs to look professional.
```

---

### Improve ResultsDashboard — make scores feel meaningful

```
The results dashboard looks okay but the scores feel wrong. The topicScores come back as 0-4 floats but displaying "3.5 / 4" looks weird. Convert everything to percentages out of 100. Also the radar chart looks broken on some screen sizes. Replace it with horizontal progress bars — one per topic, labeled with the topic name and score like "RAG: 87%". Use green for >= 70, amber for 40-70, red for below 40.
```

---

### Add smooth page transitions between screens

```
Right now when switching between picker, chat, and results screens the transition is instant and jarring. Add AnimatePresence from framer-motion so each screen fades in with opacity 0 → 1 and a slight upward slide (y: 20 → 0) over 0.3s. The outgoing screen should fade out simultaneously. Wrap the conditional rendering in page.tsx with AnimatePresence and add motion.div wrappers around each screen component.
```

---

### Mobile responsiveness pass

```
The app is currently only designed for desktop. Do a responsiveness pass:
- On screens < 768px, the chat sidebar should collapse/hide
- The messages area should use full width on mobile
- The candidate picker card should be full width with reduced padding
- The results dashboard columns should stack vertically on mobile
- Input textarea should be slightly smaller on mobile

Don't break the desktop layout — use media queries or Tailwind responsive prefixes.
```

---

### globals.css design tokens and typography

```
Set up globals.css with a proper design system using CSS custom properties. I want:
- A light theme with a soft blue-grey background (#f0f4ff)
- Accent color: indigo (#6366f1) with light variant rgba(99,102,241,0.12)
- Text colors: primary (#0f172a), light (#475569), muted (#94a3b8)
- Status colors: green (#10b981), amber (#f59e0b), red (#ef4444) each with light variants
- Border: rgba(0,0,0,0.06) for subtle, rgba(0,0,0,0.12) for stronger
- Surface colors: rgba(255,255,255,0.92) for glass, #ffffff for solid
- Typography: import Inter from Google Fonts, set it as the body font with -webkit-font-smoothing antialiased
- Base body styles: overflow hidden, height 100vh, background var(--bg)
```

---

### Fix chat input auto-resize

```
The textarea in the chat input area doesn't resize as the user types multiple lines. It stays at one line height which is annoying for longer answers. Make it auto-resize:
- Start at 1 row height
- Grow up to a max of about 120px as the user types
- Reset back to 1 row after sending a message
- Don't show a scrollbar while it's expanding

Use a useEffect on the textarea ref that sets height to "auto" then to scrollHeight on every value change.
```

---

