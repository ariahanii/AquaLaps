"""
src/generate.py

Takes a user profile, retrieves relevant chunks from the paper corpus,
and prompts Gemini to generate a structured JSON training plan grounded
in those chunks.

Run with: python src/generate.py
(after ingest.py and embed.py have been run)
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from retrieve import retrieve_chunks, format_chunks_for_prompt

# ---- Config ----
GEMINI_MODEL = "gemini-3.6-flash"
OUTPUT_DIR = Path("data/output")
TOP_K_CHUNKS = 6

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# A hardcoded profile for now — this becomes user input once the UI exists.
SAMPLE_USER_PROFILE = {
    "goal": "improve 100m freestyle race time",
    "current_level": "intermediate",
    "days_per_week": 4,
    "session_length_minutes": 60,
    "notes": "comfortable swimmer, wants to build speed and race-pace endurance",
}


SYSTEM_INSTRUCTIONS = """You are a swim training program assistant. You generate structured, \
evidence-informed weekly training plans based ONLY on the research excerpts provided to you.

Rules:
- Ground your plan in the provided excerpts. If an excerpt supports a specific choice \
(e.g. an interval structure, an intensity zone), reflect that in the plan.
- Do not invent physiological claims that aren't supported by the excerpts or general, \
well-established swim training knowledge.
- Output ONLY valid JSON matching the schema you're given. No prose, no markdown fences.
- This tool is educational/portfolio software, not medical or professional coaching advice. \
Keep volumes and intensities conservative and appropriate for the stated level.
"""


def build_prompt(user_profile: dict, retrieved_context: str) -> str:
    schema_description = """
{
  "goal": string,
  "overview": string,               // 2-3 sentence summary of the plan's approach
  "weeks": [
    {
      "week_number": int,
      "focus": string,              // e.g. "aerobic base", "race pace"
      "sessions": [
        {
          "day": string,            // e.g. "Monday"
          "focus": string,
          "warm_up": string,
          "main_set": string,
          "cool_down": string,
          "total_distance_m": int
        }
      ]
    }
  ],
  "sources_used": [string]          // list of paper filenames actually drawn on
}
"""

    return f"""User profile:
{json.dumps(user_profile, indent=2)}

Research excerpts retrieved for this goal:
{retrieved_context}

Generate a 2-week training plan for this user, following this exact JSON schema:
{schema_description}

Return ONLY the JSON object, nothing else.
"""


def generate_plan(user_profile: dict) -> dict:
    """Retrieve relevant context and generate a structured training plan."""
    query = user_profile["goal"]
    chunks = retrieve_chunks(query, top_k=TOP_K_CHUNKS)
    context = format_chunks_for_prompt(chunks)

    prompt = build_prompt(user_profile, context)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTIONS,
            "response_mime_type": "application/json",
        },
    )

    try:
        plan = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model did not return valid JSON. Raw output:\n{response.text}"
        ) from e

    return plan


def save_plan(plan: dict, filename: str = "sample_plan.json"):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    print(f"Plan saved to {output_path}")


if __name__ == "__main__":
    print(f"Generating plan for: {SAMPLE_USER_PROFILE['goal']}\n")
    plan = generate_plan(SAMPLE_USER_PROFILE)
    save_plan(plan)
    print(json.dumps(plan, indent=2))