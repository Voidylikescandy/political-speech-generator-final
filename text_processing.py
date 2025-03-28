from config import TEMPLATE
import json
import re

def substitute_template(json_data, template_string=TEMPLATE):
    for key, value in json_data.items():
        placeholder = "{" + key + "}"
        if placeholder in template_string:
            template_string = template_string.replace(placeholder, str(value))
    return template_string

def parse_model_response(content):
    # Regex patterns for extracting key-value pairs
    speech_pattern = r'"speech"\s*:\s*"([\s\S]*?)"\s*,\s*"key_themes"'
    key_themes_pattern = r'"key_themes"\s*:\s*\[(.*?)\]'
    sentiment_pattern = r'"sentiment"\s*:\s*\{(.*?)\}'

    # Extract values using regex
    speech_match = re.search(speech_pattern, content)
    key_themes_match = re.search(key_themes_pattern, content, re.DOTALL)
    sentiment_match = re.search(sentiment_pattern, content, re.DOTALL)

    # Process extracted values
    speech = speech_match.group(1) if speech_match else ""

    key_themes = []
    if key_themes_match:
        key_themes = [theme.strip().strip('"') for theme in key_themes_match.group(1).split(",")]

    sentiment = {}
    if sentiment_match:
        sentiment_str = "{" + sentiment_match.group(1) + "}"
        try:
            sentiment = json.loads(sentiment_str.replace("\n", " "))
        except json.JSONDecodeError:
            sentiment = {}

    # Construct the dictionary
    parsed_data = {
        "speech": speech,
        "key_themes": key_themes,
        "sentiment": sentiment
    }

    return parsed_data