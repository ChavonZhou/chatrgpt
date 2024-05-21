import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from openai import AzureOpenAI

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_BOT_USER_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

azure_openai_client = AzureOpenAI(
    api_version=os.environ['OPENAI_API_VERSION'],
    api_key=os.environ['OPENAI_API_KEY'],
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
)

responded_threads = set()

def get_chatgpt_response(prompt):
    completion = azure_openai_client.chat.completions.create(
        model="gpt-4-turbo-0125-preview",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content.strip()

@slack_event_adapter.on('message')
def message(payload):
  print(payload)
  event = payload.get('event', {})
  channel_id = event.get('channel')
  user_id = event.get('user')
  text = event.get('text')
  thread_ts = event.get('thread_ts') or event.get('ts')

  if user_id != BOT_ID and thread_ts not in responded_threads :

    response_text = get_chatgpt_response(text)
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text=response_text
    )
    responded_threads.add(thread_ts)


if __name__ == "__main__":
  app.run(debug=True)