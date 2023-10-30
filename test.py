import openai
import nltk
from nltk.corpus import stopwords
import pyodbc

# Replace 'your_api_key' with your actual API key
api_key = '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'

# Initialize the OpenAI API client
openai.api_key = api_key

# Define SQL Server connection details
server_name = 'USAMA'  # Replace with your SQL Server instance
database_name = 'ETL_Configuration'  # Replace with your database name
username = 'sa'  # Replace with your SQL Server username
password = 'Inseyab@321'  # Replace with your SQL Server password
# Establish a connection to SQL Server
connection_string = f"DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password};trusted_Connection='yes';"
connection = pyodbc.connect(connection_string)

# Create a cursor for executing SQL queries
cursor = connection.cursor()

# Define a function to insert data into the SQL Server table
def insert_data(user_input, chatbot_response, main_keywords):
    sql = "INSERT INTO ChatbotOutput (UserInput, ChatbotResponse, MainKeywords) VALUES (?, ?, ?)"
    cursor.execute(sql, (user_input, chatbot_response, ", ".join(main_keywords)))
    connection.commit()

# Define a function to extract keywords from text
def extract_keywords(input_text):
    # Tokenize the input text
    words = nltk.word_tokenize(input_text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.lower() not in stop_words]

    # Return a list of non-stopword keywords
    return filtered_words

# Create a table if it doesn't exist
cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ChatbotOutput')
    CREATE TABLE ChatbotOutput (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        UserInput NVARCHAR(MAX),
        ChatbotResponse NVARCHAR(MAX),
        MainKeywords NVARCHAR(MAX)
    )
''')
connection.commit()
# def chat_with_gpt3(prompt):
#     try:
#         # Generate a response from GPT-3
#         response = openai.Completion.create(
#             engine="gpt-3.5-turbo",  # Choose the appropriate engine
#             prompt=prompt,
#             max_tokens=500,  # Adjust the max_tokens as needed
#             temperature=0.2,  # Adjust the temperature for creativity
#         )

#         return response.choices[0].text.strip()

#     except Exception as e:
#         return str(e)

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
                {"role": "system", "content": "YOUR ASSISTANCE AND ALSO INCLUDE SOCIAL MEDIA HASHTAGS WITH WEB TAGS WITH LOCATIONS."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,  # Adjust the max_tokens as needed
            temperature=0.2,  # Adjust the temperature for creativity
        )       

        # return response.choices[0].text.strip()
        return response['choices'][0]['message']['content']

    except Exception as e:
        return str(e)

# Main loop for chatting
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break

    response = chat_with_gpt3(user_input)
    main_keywords = get_tags(response)

    print("Response: " + response)
    #print("Main Keywords: " + ", ".join(main_keywords))

    # Insert data into the SQL Server table
    insert_data(user_input, response, main_keywords)

# Close the SQL Server connection
connection.close()

def get_tags(string):
    token=string.split()
    tags=[tag for tag in token if tag.startswith('#')]
    return tags

get_tags(response)