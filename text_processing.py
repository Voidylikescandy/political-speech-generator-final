from config import TEMPLATE
import json
import re
from logger import logger

def substitute_template(json_data, template_string=TEMPLATE):
    try:
        logger.info(f"Substituting template with {len(json_data)} key-value pairs")
        if not json_data:
            logger.warning("Empty JSON data provided for template substitution")
            return template_string
            
        for key, value in json_data.items():
            placeholder = "{" + key + "}"
            if placeholder in template_string:
                logger.debug(f"Replacing placeholder '{placeholder}' with value")
                template_string = template_string.replace(placeholder, str(value))
            else:
                logger.debug(f"Placeholder '{placeholder}' not found in template")
                
        logger.info("Template substitution completed successfully")
        return template_string
    except Exception as e:
        logger.error(f"Error during template substitution: {str(e)}")
        logger.debug("Stack trace for template substitution error", exc_info=True)
        raise Exception(f"Failed to substitute template: {str(e)}")

def parse_model_response(content):
    try:
        logger.info("Parsing model response")
        if not content or not isinstance(content, str):
            logger.error(f"Invalid content provided: {type(content)}")
            raise ValueError("Content must be a non-empty string")
            
        # Regex patterns for extracting key-value pairs
        speech_pattern = r'"speech"\s*:\s*"([\s\S]*?)"\s*,\s*"key_themes"'
        key_themes_pattern = r'"key_themes"\s*:\s*\[(.*?)\]'
        sentiment_pattern = r'"sentiment"\s*:\s*\{(.*?)\}'

        logger.debug("Extracting values using regex patterns")
        # Extract values using regex
        speech_match = re.search(speech_pattern, content)
        key_themes_match = re.search(key_themes_pattern, content, re.DOTALL)
        sentiment_match = re.search(sentiment_pattern, content, re.DOTALL)

        # Process extracted values
        if speech_match:
            speech = speech_match.group(1)
            logger.debug(f"Successfully extracted speech text ({len(speech)} chars)")
        else:
            speech = ""
            logger.warning("No speech content found in model response")

        key_themes = []
        if key_themes_match:
            logger.debug("Processing key themes from match")
            key_themes = [theme.strip().strip('"') for theme in key_themes_match.group(1).split(",")]
            logger.info(f"Extracted {len(key_themes)} key themes")
        else:
            logger.warning("No key themes found in model response")

        sentiment = {}
        if sentiment_match:
            logger.debug("Processing sentiment data from match")
            sentiment_str = "{" + sentiment_match.group(1) + "}"
            try:
                sentiment = json.loads(sentiment_str.replace("\n", " "))
                logger.info(f"Successfully parsed sentiment data with {len(sentiment)} keys")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse sentiment JSON: {str(e)}")
                sentiment = {}
        else:
            logger.warning("No sentiment data found in model response")

        # Construct the dictionary
        parsed_data = {
            "speech": speech,
            "key_themes": key_themes,
            "sentiment": sentiment
        }

        logger.info("Successfully parsed model response")
        return parsed_data
    except Exception as e:
        logger.error(f"Error parsing model response: {str(e)}")
        logger.debug("Stack trace for parse_model_response error", exc_info=True)
        raise Exception(f"Failed to parse model response: {str(e)}")