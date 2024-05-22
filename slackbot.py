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
    messages = [
        {
            "role": "system",
            "content": (
                "Providing you can access spark UI by the following steps:\n"
                "// To access spark manager UI at localhost:8080\n"
                "kubectl port-forward deployment/spark-manager-<client>-<project> 8080\n"
                "// To access spark worker UI at localhost:8081 or localhost:8082\n"
                "kubectl port-forward deployment/spark-worker0-<client>-<project> 8081\n"
                "kubectl port-forward deployment/spark-worker1-<client>-<project> 8082\n"
                "// To access spark application UI at localhost:4040\n"
                "kubectl port-forward deployment/privacy-<client>-<project> 4040\n"
                "kubectl port-forward deployment/privacy-normalizer-<client>-<project> 4040"
            )
        },
        {
            "role": "system",
            "content": (
                "Providing you can connect to MongoDB Compass to Prod instance with the following steps:\n"
                "1. Port forward your MongoDB pod:\n"
                "   kubectl port-forward deployment/mongo-ctus010192-t004-xxx 27017\n"
                "2. Get your MongoDB secret in /run/secrets/mongo/mongo\n"
                "3. Use the username and password to authenticate into MongoDB Compass:\n"
                "   Username: mongoadmin\n"
                "   Password: the mongo secret (edited)"
            )
        },
        {
            "role": "system",
            "content": (
                "Providing you can scale up Spark by:\n"
                "The list of Spark workers to consider using is the privacy.scalable.deployments list in the release. For all releases, this includes all the Spark workers.\n"
                "Privacy checks for deployment.spec.template.metadata.annotations['textiq.scalable.deployment'] = true on each Spark worker.\n"
                "The releases folder sets those with Quasimodo.6.1/services/spark-worker11/deployment.yml: textiq.scalable.deployment: $$SPARK_WORKER_XL_REPLICAS_SCALING_ENABLED$$\n"
                "To flip this on for a project, edit the instance and instance.spec.propertyOverrides add an entry, `SPARK_WORKER_XL_REPLICAS_SCALING_ENABLED: 'true'`"
            )
        },
        {
            "role": "system",
            "content": (
                "Providing when running Install-TestVm, I keep getting the following errors, even though I do have Connect VPN:\n"
                "PS C:\\kerryTextIq\\setupNuGet> Install-TestVm -ID aio-april-24.4\n"
                "Install-TestVm : Failed to setup private network for TestVm. This step must be done to support TestVms with static IP addresses. Try this command again and contact Tools support if this error persists.\n"
                "For more information, see the logs located at C:\\Users\\kerry.xue\\AppData\\Local\\GadgetsTvm.\n"
                "You can resolve it by:\n"
                "Reinstall Hyper-V through Program and Features(Control Panel) -> Turn Windows features on or off on the panel to the left -> unmark Hyper-V and click OK to uninstall -> Restart laptop -> do the same but tick Hyper-V again to reinstall -> Restart Laptop -> The VM should appear."
            )
        },
        {
            "role": "system",
            "content": (
                "Providing image promotion for MT services has been moved from the helm-textiq-privacy repo to the service repo. You can trigger a promotion by running a Continuous Integration github action from the service repo.\n"
                "To promote the pidetectionmanager, use the following link to trigger the Continuous Integration action:\n"
                "https://github.com/relativityone/privacy-pidetectionmanager/actions/workflows/continuous_integration.yml"
            )
        },
        {
            "role": "system",
            "content": (
                "If you can't fine the answer in the system context, you should reply 'I could not find an answer'."
            )
        }
    ]

    messages.append({"role": "user", "content": prompt})
    completion = azure_openai_client.chat.completions.create(
        model="gpt-35-turbo-0301",
        messages=messages,
        n=1, # Ensures that only one completion is generated
        max_tokens = 200
    )

    return completion.choices[0].message.content.strip()

@slack_event_adapter.on('message')
def message(payload):
  event = payload.get('event', {})
  channel_id = event.get('channel')
  user_id = event.get('user')
  text = event.get('text')
  thread_ts = event.get('thread_ts') or event.get('ts')
  bot_id = event.get('bot_id', None)

  if bot_id or (user_id == BOT_ID):
      print("Ignoring bot message or self-message.")
      return

  if thread_ts not in responded_threads :
    responded_threads.add(thread_ts)
    response_text = get_chatgpt_response(text)
    client.chat_postMessage(
        channel=channel_id,
        thread_ts=thread_ts,
        text=response_text
    )

if __name__ == "__main__":
  app.run(debug=True)