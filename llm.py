from retriever import search_with_threshold
from text_processing import substitute_template, parse_model_response
from config import MODEL, SYSTEMPROMPT, MODEL_URL, OPENAI_API
from openai import OpenAI, OpenAIError, ConflictError, NotFoundError, APIStatusError, RateLimitError, APITimeoutError, BadRequestError, APIConnectionError, AuthenticationError, InternalServerError, PermissionDeniedError, LengthFinishReasonError, UnprocessableEntityError, APIResponseValidationError, ContentFilterFinishReasonError, _AmbiguousModuleClientUsageError
from database import table
from logger import logger

client_openai = OpenAI(api_key=OPENAI_API, base_url=MODEL_URL)

def generate_response(data: dict) -> str:


#     content =  """{
#     "speech": "Namaskaram, Warangal! Mee andariki na hrudayapoorvaka vandanalu!\nMy dear brothers and sisters of this historic city of Warangal, today, I stand before you in this ancient land of the Kakatiyas, where every stone tells a story of greatness. Just as the magnificent Warangal Fort has stood the test of time, the spirit of this region remains unbroken and strong. When I look at Warangal, I see not just a city with a glorious past, but a center with unlimited potential for the future. The same hands that created the intricate carvings of the Thousand Pillar Temple can now weave the fabric of a new India. The same soil that nurtured the Kakatiya dynasty can now nurture a new generation of entrepreneurs, farmers, and innovators.\nFor over a decade as Prime Minister and before that as Chief Minister of Gujarat, I have worked with a single vision: \"Sabka Saath, Sabka Vikas, Sabka Vishwas\" - Together with all, Development for all, Trust of all. This is not just a slogan; it is our sacred commitment to every citizen of India, including each one of you in Warangal.\nThe weavers of Warangal are known across the world for their artistic brilliance. Your handlooms tell stories that words cannot express. But I understand the challenges you face. That is why our government has initiated special programs to modernize the textile industry while preserving your unique traditional skills. We will establish a Textile Park here in Warangal that will connect your extraordinary craftsmanship directly to global markets. Just as threads come together to create beautiful fabric, we must weave together tradition and technology to create prosperity.\nFor our farmers who toil in the fields of Telangana, we have doubled the budget for agriculture. Our PM-KISAN scheme ensures direct financial support, and we are working to improve irrigation facilities across the region. The fertile lands of Telangana deserve the best support, and we are committed to providing it.\nYoung friends, I understand your aspirations. You want quality education and meaningful employment. That is why we are expanding educational institutions in Telangana. We will establish a new center of excellence in Warangal focused on emerging technologies, ensuring that the youth of this region are at the forefront of India's technological revolution. The ancient fort of Warangal attracts visitors from across the country. But we want the world to witness its splendor. We will develop a comprehensive heritage tourism circuit connecting Warangal Fort, Ramappa Temple, and other historical sites. This will not only preserve your cultural heritage but also create thousands of jobs in the tourism sector.\nI remember when I was young, I traveled across our great nation, visiting places like Warangal. I was struck by the richness of our heritage and the warmth of our people. Those journeys shaped my vision for India—a vision where every region preserves its unique identity while moving forward on the path of development. This is not just a political commitment; it is personal for me.\nBrothers and sisters, infrastructure is the backbone of development. We are investing in expanding road networks, improving railway connectivity, and enhancing digital infrastructure. Soon, Warangal will be connected to major economic centers through high-speed corridors, opening new avenues for growth and prosperity. I know there are challenges. The competition from mass-produced textiles threatens your traditional crafts. Water scarcity affects your agriculture. Limited industrial development has restricted job opportunities. But for every challenge, we have a solution. Our government will provide special incentives for handloom products, implement water conservation projects, and establish skill development centers to create employment opportunities.\nSome people ask why the BJP should be trusted in Telangana. I ask them to look at our track record. Wherever we have been given the opportunity to serve, we have delivered development without discrimination. Our only religion is \"India First,\" our only holy book is the Constitution of India, and our only focus is the welfare of 1.4 billion Indians.\nFriends, I ask you this: Can a nation progress if some regions are left behind? Can we claim to be developed if cities like Warangal do not realize their full potential? The answer is clear. The journey of India's development cannot be complete without the development of Telangana, and the development of Telangana cannot be complete without the transformation of historic cities like Warangal.\nToday, I ask for your support not just for the BJP but for a vision that sees Warangal as a model city that perfectly blends its rich heritage with modern development. A city where tradition and technology walk hand in hand. A city that honors its past while embracing the future.\nLet us work together to build a Warangal where our heritage sites become world-class tourist destinations, our weavers receive the recognition and rewards they deserve, our farmers prosper with modern agricultural practices, our youth find quality education and employment opportunities, and our infrastructure supports rapid economic growth. This is not just a dream; it is a roadmap that we will follow with unwavering determination. With your support, we will transform Warangal into a shining example of development that respects tradition.\nI invite each one of you to become ambassadors of change. Speak to your friends, your families, your communities about the vision we share for Warangal and Telangana. Together, we can build a future that makes every resident of this great city proud.\nWarangal ki jai! Telangana ki jai! Bharat Mata ki jai!\nThank you, and may the blessings of the Kakatiyas be with you all.",
#     "key_themes": [
#         "Economic and infrastructural development of Warangal",
#         "Preservation of cultural heritage and tourism promotion",
#         "Support for farmers and the agricultural sector",
#         "Empowerment of youth through education and employment opportunities",
#         "Advancement of Warangal’s textile industry and artisans"
#     ],
#     "sentiment": {
#         "category": "Inspirational",
#         "explanation": "The speech conveys a strong sense of pride, optimism, and forward-looking vision. It highlights historical greatness while emphasizing future growth, development, and opportunities. The language is uplifting, aiming to motivate and unite the people toward a collective vision of progress."
#     }
# }"""

    if not isinstance(data, dict):
        logger.error("Invalid input: data must be a dictionary")
        return {"error": "ERR_INVALID_INPUT", "message": "Input data must be a dictionary"}

    if data.get("political-party") == "other":
        data["political-party"] = data.get("other-party", "")
        if not data["political-party"]:
            logger.warning("Other party selected but no party name provided")

    # tone_mapping = {1: "subdued", 2: "neutral", 3: "emotional"}
    # data["tone"] = tone_mapping.get(int(data.get("tone", 2)), "neutral")

    q1 = data.get("candidate-name", "")
    if not q1:
        logger.error("Missing required field: candidate-name")
        return {"error": "ERR_MISSING_FIELD", "message": "Candidate name is required"}
        
    q2 = data.get("bio", "")
    q3 = data.get("political-party", "")
    q4 = data.get("target-demographic", "")
    q5 = data.get("recent-events", "")
    q6 = data.get("primary-concerns", "")

    query = f"{q1} {q3}"
    logger.info(f"Performing search with the query : {query}")
    
    try:
        data["retrieved_info"] = search_with_threshold(table, query, threshold=0.75)
        logger.info("Retrieved information successfully")
    except Exception as e:
        logger.error(f"Search operation failed: {e}")
        return {"error": "ERR_SEARCH_FAILED", "message": f"Failed to retrieve information: {str(e)}"}

    try:
        formatted_prompt = substitute_template(data)
        logger.info("Formatted prompt successfully")
        logger.debug(f"Full Prompt:\n {formatted_prompt}")
    except Exception as e:
        logger.error(f"Template substitution failed: {e}")
        return {"error": "ERR_TEMPLATE_FAILED", "message": f"Failed to format prompt: {str(e)}"}

    message_list = [
        {
            "role": "user",
            "content": formatted_prompt
        }
    ]

    try: 
        logger.info("Calling OpenAI API for response generation")
        response = client_openai.chat.completions.create(
            model=MODEL,
            max_tokens=16000,
            messages=[
                {"role": "system", "content": SYSTEMPROMPT},
                *message_list
            ],
            # tools=openai_tool_evaluation,
            # tool_choice='required',
            
            temperature=0.0,
            response_format={"type":"json_object"}
        )
        logger.info("Successfully received response from OpenAI API")
    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Rate limit exceeded. Please try again later: {str(e)}"}
    except APITimeoutError as e:
        logger.error(f"API request timed out: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Request to OpenAI API timed out: {str(e)}"}
    except APIConnectionError as e:
        logger.error(f"Connection error with OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Failed to connect to OpenAI API. Check your network connection: {str(e)}"}
    except AuthenticationError as e:
        logger.error(f"Authentication error with OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Authentication failed. Check your API key: {str(e)}"}
    except PermissionDeniedError as e:
        logger.error(f"Permission denied by OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Permission denied to access the requested resource: {str(e)}"}
    except BadRequestError as e:
        logger.error(f"Bad request to OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Invalid request parameters sent to OpenAI API: {str(e)}"}
    except NotFoundError as e:
        logger.error(f"Resource not found in OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"The requested resource was not found. Check model name: {str(e)}"}
    except ConflictError as e:
        logger.error(f"Conflict error with OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Request conflicts with current state of the server: {str(e)}"}
    except InternalServerError as e:
        logger.error(f"Internal server error from OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"OpenAI API experienced an internal error. Try again later: {str(e)}"}
    except UnprocessableEntityError as e:
        logger.error(f"Unprocessable entity error from OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"The request was well-formed but unable to be processed: {str(e)}"}
    except ContentFilterFinishReasonError as e:
        logger.error(f"Content filter triggered in OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Response was filtered due to content safety policies: {str(e)}"}
    except LengthFinishReasonError as e:
        logger.error(f"Response length limit reached in OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Response was truncated due to token limit constraints: {str(e)}"}
    except APIResponseValidationError as e:
        logger.error(f"API response validation error from OpenAI: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"OpenAI API response failed validation: {str(e)}"}
    except APIStatusError as e:
        logger.error(f"API status error from OpenAI: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"OpenAI API returned an unexpected status code: {str(e)}"}
    except _AmbiguousModuleClientUsageError as e:
        logger.error(f"Ambiguous module client usage with OpenAI API: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Ambiguous usage of OpenAI client: {str(e)}"}
    except OpenAIError as e:
        logger.error(f"General OpenAI API error: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"An error occurred with the OpenAI API: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error occurred while generating response: {e}")
        return {"error": "ERR_API_FAILURE", "message": f"Failed to get response from OpenAI API: {str(e)}"}

    content = response.choices[0].message.content
    logger.debug(f"Raw response : {content}")
    
    if not content:
        logger.error("Received empty response from API")
        return {"error": "ERR_EMPTY_RESPONSE", "message": "Received empty response from API"}
        
    try:
        return parse_model_response(content)
    except Exception as e:
        logger.error(f"Failed to parse model response: {e}")
        return {"error": "ERR_PARSING_FAILURE", "message": f"Failed to parse model response: {str(e)}"}
