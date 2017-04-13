import sys
from wit import Wit
from utility import ifsource, ifdestination, ifdatetime, iftransport, ifcheckin_checkout, searchFlight, searchBus , search_hotels


access_token = 'XL7BFW47QBDKM5T6KE47KXA2TNQYLPBN'


def send(request, response):
    print(response['text'])

def searchTransport(request):
    
    context = request['context']
    entities = request['entities']

    source = ifsource(entities)
    destination = ifdestination(entities)
    datetime = ifdatetime(entities)
    transport_type = iftransport(entities)

    if source and destination and datetime:

        if transport_type == 'flights':
            url = searchFlight(source, destination, datetime)
        elif transport_type == 'buses':
            url = searchBus(source, destination, datetime)
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
    
    check_in,check_out = ifcheckin_checkout(entities)
    location = ifsource(entities)

    if check_in and check_out and location:
        url = search_hotels(location,check_in,check_out)
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
    'send': send,
    'searchTransport': searchTransport,
    'searchHotels': searchHotels
}

client = Wit(access_token=access_token, actions=actions)
client.interactive()
