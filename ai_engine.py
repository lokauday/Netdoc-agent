# ============================================================
#  AI DOCUMENTATION ENGINE (OpenAI GPT)
# ============================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

# ------------------------------------------------------------
#  LOAD .env FILE
# ------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise Exception("❌ OPENAI_API_KEY missing in .env file")

client = OpenAI(api_key=API_KEY)


# ------------------------------------------------------------
#  BUILD PROMPT
# ------------------------------------------------------------
def build_prompt(parsed):
    return f"""
You are NetDoc AI, an enterprise-grade network engineering assistant.

You are given a parsed Cisco configuration:

PARSED DATA:
{parsed}

Generate the following:

1) Summary  
   - High-level summary of what the device configuration shows  
   - Identify device type (switch/router)  
   - General role (access/core/edge/etc.)

2) Section by Section Explanation  
   Explain:  
     - Interfaces  
     - VLANs  
     - Routing  
     - Security  
     - AAA  
     - STP  
     - CDP/LLDP  

3) Best Practices  
   Provide vendor/industry recommended best practices.

4) Recommendations  
   Provide actionable remediation steps.

IMPORTANT:
- OUTPUT MUST BE STRICT JSON.
- REQUIRED KEYS:
    "summary",
    "explanation",
    "best_practices",
    "recommendations"
"""


# ------------------------------------------------------------
#  CALL OPENAI GPT API
# ------------------------------------------------------------
def generate_ai_docs(parsed):
    prompt = build_prompt(parsed)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are NetDoc AI, a network engineering expert."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=2000
    )

    raw_text = completion.choices[0].message.content

    # Parse JSON safely
    import json

    # Direct JSON result
    try:
        return json.loads(raw_text)
    except:
        pass

    # If model wrapped JSON with extra text
    try:
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        clean = raw_text[start:end]
        return json.loads(clean)
    except:
        return {
            "summary": "Error parsing AI output",
            "explanation": raw_text,
            "best_practices": [],
            "recommendations": []
        }
