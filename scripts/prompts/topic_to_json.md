You are assisting in building a beginner Tamil phrase deck for a flashcard app.

TASK: Given a TOPIC, produce a JSON array of 15–30 phrase objects.
FIELDS per object (strict):
- id: integer (unique within this batch, start at 1)
- category: short snake_case category within the topic (e.g., "basics", "shopping")
- tamil: the phrase in Tamil script
- translit: a simple, readable Latin transliteration (ASCII only; lowercase preferred)
- english: concise English gloss

STYLE/CONSTRAINTS:
- Aim for CEFR A1–A2 difficulty; short and high‑utility phrases.
- Use respectful/formal forms when appropriate in Tamil.
- Do NOT include commentary; output only raw JSON.

TOPIC: {{topic}}
