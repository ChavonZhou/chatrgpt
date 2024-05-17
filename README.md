Setup:
install ngrok to allow host server locally

1. add a .env file based on the .env_sample,
   get Bot User OAuth Token from https://api.slack.com/apps/A073DEV3TFZ/oauth?success=1
   get signing secret from https://api.slack.com/apps/A073DEV3TFZ/general? under App Credentials
2. run virtualenv venv
3. run source venv/bin/activate
4. run pip install -r requirements.txt to install packages
5. run slackbot.py should now start up a server on localhost:5000
6. run ngrok http 5000 (or other port number if the slackbot started on a different port)
7. copy the Forwarding address (ie. something like https://085d-2001-569-5926-2400-9400-bef-a486-630d.ngrok-free.app NOTE: since we are using a free version the address will change each time we restart ngrok)
8. go to Event Subscriptions on slack api for the app (https://api.slack.com/apps/A073DEV3TFZ/event-subscriptions?), under Enable Events paste the forwarding address /slack/events
9. now the bot will repeat anything user sends to the channel/direct message bot
