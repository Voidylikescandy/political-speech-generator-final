from retriever import search_with_threshold
from text_processing import substitute_template
from config import MODEL, SYSTEMPROMPT
from openai import OpenAI
import json
import re

client_openai = OpenAI(api_key="aMn5STDhSBDorVIhh8u5DalCUceRniQg", base_url="https://api.deepinfra.com/v1/openai")

def generate_response(data: dict) -> str:
    if data.get("political-party") == "other":
        data["political-party"] = data.get("other-party", "")

    query = f"{data.get('candidate-name', '')} {data.get('political-party', '')}"
    data["retrieved_info"] = search_with_threshold(query, threshold=0.50)

    formatted_prompt = substitute_template(data)
    print("🔹 Full Prompt:\n", formatted_prompt)

    message_list = [{"role": "user", "content": formatted_prompt}]

    response = client_openai.chat.completions.create(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "system", "content": SYSTEMPROMPT}, *message_list],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    return re.sub(r'[\x00-\x1F\x7F]', '', content)
