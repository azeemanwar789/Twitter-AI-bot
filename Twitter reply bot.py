from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YourKey")
llm= ChatOpenAI(temperature= 0.3,
                openai_api_key=OPENAI_API_KEY,
                model_name="gpt-3.5-turbo",
                #model_name='gpt-4',
                )
def generate_response(llm, mentioned_parent_tweet_text):
    system_template="""
    You are incredibly wise and smart tech mad scientist from silicon valley,
    Your goal is to give a concise prediction in response to a piece of text from the user.
    % RESPONSE TONE:
    - Your prediction should be given in the active voice and be opinionated
    - Your tone should be seroous w/ a hint of wit and sarcasm
    % RESPONSE FORMAT:
    - Response in under 200 words
    - Respond in one short sentence
    - Do not respond with emojis
    % REPONSE CONTENT:
    - Include specific examples of old tech if they are relevant
    - if you dont have an answer, say, "Sorry, my magic 8 ball isn't working right now
    """
    system_message_prompt= SystemMessagePromptTemplate.from_template(system_template)
    human_template="(text)"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt=ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    final_prompt=chat_prompt.format_prompt(text=mentioned_parent_tweet_text).to_messages()
    response=llm(final_prompt).content
    return response
tweet="""
Most Saas founders i've talked to that are AI-first can't explain to me how what they are doing is defensible
Not looking for a perfect answer, just some of the real insights  """
response = generate_response(llm,tweet)
print(response)


