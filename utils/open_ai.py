import os
from utils import get_logger
import openai
from dotenv import load_dotenv

load_dotenv('.flaskenv')
openai.api_key = os.environ['OPENAI_API_KEY']

logger = get_logger("SMAR")


sys_propmt = """Generate 5 to 8 keywords for social media (twitter, facebook, linkedin, instagram, tiktok) searches for the usecase provide in the following format:
keyword1--|--keyword2--|--keyword3--|--keywordN

UseCase:
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
                {"role": "user", "content": prompt},
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
    text = "I want to get the financial new of cricket"
    terms = get_terms_openai(text=text)
    print(terms)