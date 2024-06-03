import tweepy
from airtable import Airtable
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import schedule
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

twitter_api_key = os.getenv("twitter_api_key", "Yourkey")
twitter_api_secret = os.getenv("twitter_api_secret", "Yourkey")
twitter_access_token = os.getenv("twitter_access_token", "Yourkey")
twitter_access_token_secret = os.getenv("twitter_access_token_secret", "Yourkey")
twitter_bearer_token = os.getenv("twitter_bearer_token", "Yourkey")
airtable_api_key = os.getenv("airtable_api_key", "Yourkey")
airtable_base_key = os.getenv("airtable_base_key", "Yourkey")
airtable_table_name = os.getenv("airtable_table_name", "Yourkey")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "Yourkey")

class TwitterBot:
    def __init__(self):
        self.twitter_api = tweepy.Client(
            bearer_token=twitter_bearer_token,
            consumer_key=twitter_api_key,
            consumer_secret=twitter_api_secret,
            access_token=twitter_access_token,
            access_token_secret=twitter_access_token_secret,
            wait_on_rate_limit=True
        )
        self.airtable = Airtable(airtable_base_key, airtable_table_name, airtable_api_key)
        self.twitter_me_id = self.get_me_id()
        self.tweet_response_limit = 35
        self.llm = ChatOpenAI(temperature=0.5, api_key=OPENAI_API_KEY, model_name='gpt-4')
        self.mentions_found = 0
        self.mentions_replied = 0
        self.mentions_replied_errors = 0

    def get_me_id(self):
        user = self.twitter_api.get_user(username="your_twitter_username")  # replace with your username
        return user.data.id

    def generate_response(self, mentioned_conversation_tweet_text):
        system_template = """
        You are incredibly wise and smart tech mad scientist from Silicon Valley.
        Your goal is to give a concise prediction in response to a piece of text from the user.
        
        RESPONSE TONE:
        - Your prediction should be given in the active voice and be opinionated
        - Your tone should be serious with a hint of wit and sarcasm
        
        RESPONSE FORMAT:
        - Response in under 200 words
        - Respond in one short sentence
        - Do not respond with emojis
        
        RESPONSE CONTENT:
        - Include specific examples of old tech if they are relevant
        - If you don't have an answer, say, "Sorry, my magic 8 ball isn't working right now."
        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        final_prompt = chat_prompt.format_prompt(text=mentioned_conversation_tweet_text).to_messages()
        response = self.llm(final_prompt).content
        return response

    def respond_to_mention(self, mention, mentioned_conversation_tweet):
        response_text = self.generate_response(mentioned_conversation_tweet.text)
        try:
            response_tweet = self.twitter_api.create_tweet(text=response_text, in_reply_to_tweet_id=mention.id)
            self.mentions_replied += 1
        except Exception as e:
            print(e)
            self.mentions_replied_errors += 1
            return
        self.airtable.insert({
            'mentioned_conversation_tweet_id': str(mentioned_conversation_tweet.id),
            'mentioned_conversation_tweet_text': mentioned_conversation_tweet.text,
            'tweet_response_id': response_tweet.data['id'],
            'tweet_response_text': response_text,
            'tweet_response_created_at': datetime.utcnow().isoformat(),
            'mentioned_at': mention.created_at.isoformat()
        })
        return True

    def execute_replies(self):
        print(f"Starting job: {datetime.utcnow().isoformat()}")
        self.respond_to_mentions()
        print(f"Finished job: {datetime.utcnow().isoformat()}, found: {self.mentions_found}, replied: {self.mentions_replied}")

    def respond_to_mentions(self):
        # Add the logic to fetch mentions and call respond_to_mention for each mention
        pass

def job():
    print(f"Job executed at {datetime.utcnow().isoformat()}")
    bot = TwitterBot()
    bot.execute_replies()

if __name__ == "__main__":
    schedule.every(5).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
