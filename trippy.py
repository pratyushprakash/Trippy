from wit import Wit
from utility import entityChecker, findTransport, findHotels
from bottle import Bottle, request, debug
import requests

access_token = 'XL7BFW47QBDKM5T6KE47KXA2TNQYLPBN'
# Messenger API parameters
FB_PAGE_TOKEN = 'EAAbVZBwxcNqMBAPO34udy542bZCXSlHhgX'
'Xae3Am0rokHcWrWIF95DWbtijwJ52ldUm1NJVPZCLZCZAZAIPiQ0'
'P4LFGtsYxSexFbvmhDMpJTZCBzErKKxOWmDkML4hKNaZAIEygibdR'
'17g7nlZB9fboKoCokDLB4NkZAFadVdOy7prkAZDZD'

# A user secret to verify webhook get request.
FB_VERIFY_TOKEN = 'sample_verify_token'

# Setup Bottle Server
debug(True)
app = Bottle()


# Facebook Messenger GET Webhook
@app.get('/webhook')
def messenger_webhook():
    """
    A webhook to return a challenge
    """
    verify_token = request.query.get('hub.verify_token')
    # check whether the verify tokens match
    if verify_token == FB_VERIFY_TOKEN:
        # respond with the challenge to confirm
        challenge = request.query.get('hub.challenge')
        return challenge
    else:
        return 'Invalid Request or Verification Token'


# Facebook Messenger POST Webhook
@app.post('/webhook')
def messenger_post():
    """
    Handler for webhook (currently for postback and messages)
    """
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            messages = entry['messaging']
            if messages[0]:
                # Get the first message
                message = messages[0]
                # Yay! We got a new message!
                # We retrieve the Facebook user ID of the sender
                fb_id = message['sender']['id']
                # We retrieve the message content
                text = message['message']['text']
                # Let's forward the message to the Wit.ai Bot Engine
                # We handle the response in the function send()
                client.run_actions(session_id=fb_id, message=text)
    else:
        # Returned another event
        return 'Received Different Event'
    return None


def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content


def send(request, response):
    """
    Sender function
    """
    # We use the fb_id as equal to session_id
    fb_id = request['session_id']
    text = response['text']
    # send message
    fb_message(fb_id, text)


def send2(requests, response):
    print(response['text'].decode('utf-8'))


def searchTransport(request):

    context = request['context']
    entities = request['entities']

    checker = entityChecker(entities)

    source = checker.ifsource(entities)
    destination = checker.ifdestination(entities)
    datetime = checker.ifdatetime(entities)
    transport_type = checker.iftransport(entities)
    transportHelper = findTransport(source, destination, datetime)
    if source and destination and datetime:

        if transport_type == 'flights':
            url = transportHelper.searchFlight()
        elif transport_type == 'buses':
            url = transportHelper.searchBus()
        context['transportList'] = url
        try:
            del context['missingDateTime']
            del context['missingLocation']
        except:
            pass

    elif datetime is None:
        context['missingDateTime'] = True
        try:
            del context['missingLocation']
            del context['transportList']
        except:
            pass

    else:
        context['missingLocation'] = True
        try:
            del context['missingDateTime']
            del context['transportList']
        except:
            pass
    # print(context)
    return context


def searchHotels(request):
    context = request['context']
    entities = request['entities']

    checker = entityChecker(entities)

    check_in, check_out = checker.ifcheckin_checkout(entities)
    location = checker.ifsource(entities)

    if check_in and check_out and location:
        url = findHotels(location, check_in, check_out).search_hotels()
        context['hotelList'] = url

        try:
            del context['missingDateTime']
            del context['missingLocation']
        except:
            pass

    elif location is None:
        context['missingLocation'] = True

        try:
            del context['missingDateTime']
            del context['hotelList']
        except:
            pass

    else:
        context['missingDateTime'] = True

        try:
            del context['hotelList']
            del context['missingLocation']
        except:
            pass

    return context


actions = {
    'send': send2,
    'searchTransport': searchTransport,
    'searchHotels': searchHotels
}

client = Wit(access_token=access_token, actions=actions)

if __name__ == '__main__':
    # Run Server
    # app.run(host='0.0.0.0', port=argv[1])
    client.interactive()
