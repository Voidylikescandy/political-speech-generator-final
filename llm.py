from retriever import search_with_threshold
from text_processing import substitute_template
from config import MODEL, SYSTEMPROMPT, MODEL_URL, OPENAI_API
from openai import OpenAI
import json
import re
from database import table

client_openai = OpenAI(api_key=OPENAI_API, base_url=MODEL_URL)

def generate_response(data: dict) -> str:
    if data.get("political-party") == "other":
        data["political-party"] = data.get("other-party", "")

    query = f"{data.get('candidate-name', '')} {data.get('political-party', '')}"
    data["retrieved_info"] = search_with_threshold(table, query, threshold=0.80)

    formatted_prompt = substitute_template(data)
    print("🔹 Full Prompt:\n", formatted_prompt)

    message_list = [{"role": "user", "content": formatted_prompt}]

    # return "It works bro"

    response = client_openai.chat.completions.create(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "system", "content": SYSTEMPROMPT}, *message_list],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    return re.sub(r'[\x00-\x1F\x7F]', '', content)
