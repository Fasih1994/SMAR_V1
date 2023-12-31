import os
from utils import get_logger
from utils.db_helper import get_engine
import openai
import pandas as pd
from dotenv import load_dotenv


load_dotenv('.flaskenv')
openai.api_key = os.environ['OPENAI_API_KEY']

logger = get_logger("SMAR")


sys_propmt = """Generate 5 to 8 keywords for social media (twitter, facebook, linkedin, instagram, tiktok) searches for the usecase provide in the following format:
keyword1--|--keyword2--|--keyword3--|--keywordN

UseCase:
"""

sys_propmt_sentiment = """analyze the text provided, give it's sentiment (positive, negative or neutral) and tone in the following format:
positive--|--playful

- Consider everything in tripple back-tiks as one text if the text is in list format provide single sentiment whole list
Example List text:
1. These schools have many entitled kids, so look at their anti-bullying policies.
2. Is the fees affordable 3yrs down the road with current income, a downgrade later may affect the child mentally
3. Extracurricular & networking opportunities
4. Is it a school first or a business

Result:
negative--|--neutral

- If sentiment analysis not posible then return
"neutral--|--neutral"
"""

def chat_with_gpt3(prompt):
    try:
        # # Generate a response from GPT-3
        # response = openai.Completion.create(
        #     engine="gpt-3.5-turbo",  # Choose the appropriate engine
        #     prompt=prompt,
        #     max_tokens=50,  # Adjust the max_tokens as needed
        #     temperature=0.2,  # Adjust the temperature for creativity
        # )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_propmt},
                {"role": "user", "content": f"```{prompt}```"},
            ],
            max_tokens=500,  # Adjust the max_tokens as needed
            temperature=0,  # Adjust the temperature for creativity
        )

        # return response.choices[0].text.strip()
        return response['choices'][0]['message']['content']

    except Exception as e:

        return str(e)

def analize_text(text:str = None):
    try:

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_propmt_sentiment},
                {"role": "user", "content": text},
            ],
            max_tokens=500,  # Adjust the max_tokens as needed
            temperature=0,  # Adjust the temperature for creativity
        )

        # return response.choices[0].text.strip()
        return response['choices'][0]['message']['content']

    except Exception as e:

        return str(e)

def get_terms_openai(text:str = None):
    logger.info(f"getting terms against '{text}'")
    terms = chat_with_gpt3(text)
    logger.info(f"generated terms are '{terms}'")
    return terms


if __name__ == '__main__':
    text = "love that everyone’s rock bottom is registering for a data analytics course"
    sentiment,tone = analize_text(text=text).split('--|--')
    print(sentiment, tone)