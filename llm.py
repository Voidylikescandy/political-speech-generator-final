from retriever import search_with_threshold
from text_processing import substitute_template
from config import MODEL, SYSTEMPROMPT, MODEL_URL, OPENAI_API
from openai import OpenAI
import json
import re
from database import table

client_openai = OpenAI(api_key=OPENAI_API, base_url=MODEL_URL)

def generate_response(data: dict) -> str:


    return """{
    "speech": "Namaskaram, Warangal! Mee andariki na hrudayapoorvaka vandanalu!\nMy dear brothers and sisters of this historic city of Warangal, today, I stand before you in this ancient land of the Kakatiyas, where every stone tells a story of greatness. Just as the magnificent Warangal Fort has stood the test of time, the spirit of this region remains unbroken and strong. When I look at Warangal, I see not just a city with a glorious past, but a center with unlimited potential for the future. The same hands that created the intricate carvings of the Thousand Pillar Temple can now weave the fabric of a new India. The same soil that nurtured the Kakatiya dynasty can now nurture a new generation of entrepreneurs, farmers, and innovators.\nFor over a decade as Prime Minister and before that as Chief Minister of Gujarat, I have worked with a single vision: \"Sabka Saath, Sabka Vikas, Sabka Vishwas\" - Together with all, Development for all, Trust of all. This is not just a slogan; it is our sacred commitment to every citizen of India, including each one of you in Warangal.\nThe weavers of Warangal are known across the world for their artistic brilliance. Your handlooms tell stories that words cannot express. But I understand the challenges you face. That is why our government has initiated special programs to modernize the textile industry while preserving your unique traditional skills. We will establish a Textile Park here in Warangal that will connect your extraordinary craftsmanship directly to global markets. Just as threads come together to create beautiful fabric, we must weave together tradition and technology to create prosperity.\nFor our farmers who toil in the fields of Telangana, we have doubled the budget for agriculture. Our PM-KISAN scheme ensures direct financial support, and we are working to improve irrigation facilities across the region. The fertile lands of Telangana deserve the best support, and we are committed to providing it.\nYoung friends, I understand your aspirations. You want quality education and meaningful employment. That is why we are expanding educational institutions in Telangana. We will establish a new center of excellence in Warangal focused on emerging technologies, ensuring that the youth of this region are at the forefront of India's technological revolution. The ancient fort of Warangal attracts visitors from across the country. But we want the world to witness its splendor. We will develop a comprehensive heritage tourism circuit connecting Warangal Fort, Ramappa Temple, and other historical sites. This will not only preserve your cultural heritage but also create thousands of jobs in the tourism sector.\nI remember when I was young, I traveled across our great nation, visiting places like Warangal. I was struck by the richness of our heritage and the warmth of our people. Those journeys shaped my vision for India—a vision where every region preserves its unique identity while moving forward on the path of development. This is not just a political commitment; it is personal for me.\nBrothers and sisters, infrastructure is the backbone of development. We are investing in expanding road networks, improving railway connectivity, and enhancing digital infrastructure. Soon, Warangal will be connected to major economic centers through high-speed corridors, opening new avenues for growth and prosperity. I know there are challenges. The competition from mass-produced textiles threatens your traditional crafts. Water scarcity affects your agriculture. Limited industrial development has restricted job opportunities. But for every challenge, we have a solution. Our government will provide special incentives for handloom products, implement water conservation projects, and establish skill development centers to create employment opportunities.\nSome people ask why the BJP should be trusted in Telangana. I ask them to look at our track record. Wherever we have been given the opportunity to serve, we have delivered development without discrimination. Our only religion is \"India First,\" our only holy book is the Constitution of India, and our only focus is the welfare of 1.4 billion Indians.\nFriends, I ask you this: Can a nation progress if some regions are left behind? Can we claim to be developed if cities like Warangal do not realize their full potential? The answer is clear. The journey of India's development cannot be complete without the development of Telangana, and the development of Telangana cannot be complete without the transformation of historic cities like Warangal.\nToday, I ask for your support not just for the BJP but for a vision that sees Warangal as a model city that perfectly blends its rich heritage with modern development. A city where tradition and technology walk hand in hand. A city that honors its past while embracing the future.\nLet us work together to build a Warangal where our heritage sites become world-class tourist destinations, our weavers receive the recognition and rewards they deserve, our farmers prosper with modern agricultural practices, our youth find quality education and employment opportunities, and our infrastructure supports rapid economic growth. This is not just a dream; it is a roadmap that we will follow with unwavering determination. With your support, we will transform Warangal into a shining example of development that respects tradition.\nI invite each one of you to become ambassadors of change. Speak to your friends, your families, your communities about the vision we share for Warangal and Telangana. Together, we can build a future that makes every resident of this great city proud.\nWarangal ki jai! Telangana ki jai! Bharat Mata ki jai!\nThank you, and may the blessings of the Kakatiyas be with you all.",
    "key_themes": [
        "Economic and infrastructural development of Warangal",
        "Preservation of cultural heritage and tourism promotion",
        "Support for farmers and the agricultural sector",
        "Empowerment of youth through education and employment opportunities",
        "Advancement of Warangal’s textile industry and artisans"
    ],
    "sentiment": {
        "category": "Inspirational",
        "explanation": "The speech conveys a strong sense of pride, optimism, and forward-looking vision. It highlights historical greatness while emphasizing future growth, development, and opportunities. The language is uplifting, aiming to motivate and unite the people toward a collective vision of progress."
    }
}"""


    if data.get("political-party") == "other":
        data["political-party"] = data.get("other-party", "")

    # tone_mapping = {1: "subdued", 2: "neutral", 3: "emotional"}
    # data["tone"] = tone_mapping.get(int(data.get("tone", 2)), "neutral")

    q1 = data.get("candidate-name", "")
    q2 = data.get("bio", "")
    q3 = data.get("political-party", "")
    q4 = data.get("target-demographic", "")
    q5 = data.get("recent-events", "")
    q6  = data.get("primary-concerns", "")

    query = f"{q1} {q3}"
    data["retrieved_info"] = search_with_threshold(table, query, threshold=0.75)

    formatted_prompt = substitute_template(data)
    print("🔹 Full Prompt:\n", formatted_prompt)

    message_list = [
        {
            "role": "user",
            "content": formatted_prompt
        }
    ]

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

    content = response.choices[0].message.content
    return content

    clean_content = re.sub(r'[\x00-\x1F\x7F]', '', content)
    try:
        parsed_data = json.loads(clean_content)
        print("Successfully parsed JSON!")
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return response

    return parsed_data
