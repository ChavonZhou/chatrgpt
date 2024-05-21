Setup:
install ngrok to allow host server locally

1. add a .env file based on the .env_sample,
   - get Bot User OAuth Token from https://api.slack.com/apps/A073DEV3TFZ/oauth?success=1
   - get signing secret from https://api.slack.com/apps/A073DEV3TFZ/general? under App Credentials
   - get the azure information from https://relativity.secretservercloud.com/app/#/secrets/1372946/general
      - OPENAI_API_TYPE ==> azure
      - OPENAI_API_BASE ==> resource from secret server
      - OPENAI_API_KEY ==> password from secret server
      - OPENAI_API_VERSION ==> 2023-07-01-preview
3. run virtualenv venv
4. run source venv/bin/activate
5. run pip install -r requirements.txt to install packages
6. run slackbot.py should now start up a server on localhost:5000
7. run ngrok http 5000 (or other port number if the slackbot started on a different port)
8. copy the Forwarding address (ie. something like https://085d-2001-569-5926-2400-9400-bef-a486-630d.ngrok-free.app NOTE: since we are using a free version the address will change each time we restart ngrok)
9. go to Event Subscriptions on slack api for the app (https://api.slack.com/apps/A073DEV3TFZ/event-subscriptions?), under Enable Events paste the forwarding address /slack/events
10. now the bot will repeat anything user sends to the channel/direct message bot
