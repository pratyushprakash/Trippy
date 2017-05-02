import requests
import csv
from iata_codes import IATACodesClient

IATA_KEY = 'fe8ab715-e164-4262-a508-3e9b5db940df'
APP_ID = 'a3649501'
APP_KEY = '4ef08768f5a9234ce7262fdea9401808'
BASE = "http://developer.goibibo.com/api/"
auth = {'app_id': APP_ID, 'app_key': APP_KEY}

iataClient = IATACodesClient(IATA_KEY)


class entityChecker(object):
    def __init__(self, entities):
        self.entities = entities

    def ifsource(self, entity='location'):
        if entity not in self.entities:
            return None
        val = self.entities[entity][0]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def ifdestination(self, entity='location'):
        if entity not in self.entities:
            return None
        val = self.entities[entity][1]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def iftransport(self, entity='transport'):
        if entity not in self.entities:
            return None
        val = self.entities[entity][0]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def ifdatetime(self, entity='datetime'):
        if entity not in self.entities:
            return None
        val = self.entities[entity][0]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def ifcheckin_checkout(self, entity='datetime'):
        if entity not in self.entities:
            return None
        try:
            val = (self.entities[entity][0]['from']['value'],
                   self.entities[entity][0]['to']['value'])
        except:
            return (None, None)
        if not val:
            return (None, None)
        if isinstance(val[0], dict):
            return (val[0]['value'], val[1]['value'])
        else:
            return val

    def set_entities(self, entities):
        self.entities = entities


class findTransport(object):
    def __init__(self, source, destination, datetime):
        self.source = source
        self.destination = destination
        self.datetime = datetime

    def searchFlight(self):
        codesource = iataClient.get(name=self.source)[0]['code']
        codedest = iataClient.get(name=self.destination)[0]['code']
        DOD = self.datetime[0:4] + self.datetime[5:7] + self.datetime[8:10]
        DOD = int(DOD)
        dateda = "&dateofdeparture=%d" % DOD
        URL = BASE + "search/" + "?format=json" + "&source=%s" % codesource + \
            "&destination=%s" % codedest + dateda + '&app_id=' + APP_ID + \
            '&app_key=' + APP_KEY + \
            '&seatingclass=E&adults=1&children=0&infants=0&counter=100'
        data = requests.get(URL).json()
        data = data['data']['onwardflights'][0]['CINFO']
        url = 'https://www.goibibo.com/flights/' + data

        return url

    def searchBus(self):
        DOD = self.datetime[0:4] + self.datetime[5:7] + self.datetime[8:10]
        URL = BASE + 'bus/search/?format=json' + '&app_id=' + APP_ID + \
            '&app_key=' + APP_KEY + '&source=' + self.source + \
            '&destination=' + self.destination + '&dateofdeparture=' + DOD
        data = requests.get(URL).json()
        data = data['data']['onwardflights']
        src_voyager_id = data[0]['src_voyager_id']
        dest_voyager_id = data[0]['dest_voyager_id']
        url = 'https://www.goibibo.com/bus/#bus-' + \
              self.source + '-' + self.destination + '-' + DOD + \
              '---0-0-' + src_voyager_id + '-' + dest_voyager_id
        return url


class csvParser(object):
    def __init__(self, filename):
        self.filename = filename

    def getData(self):
        with open(self.filename, 'r') as csvfile:
            data = csv.reader(csvfile)
        return data

    def getCityID(self, city):
        data = self.getData()
        for row in data:
            if(str(city.lower()) == str(row[0].lower())):
                return row[1]
        return None


class findHotels(object):
    def __init__(self, location, check_in_date, check_out_date):
        self.location = location
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date

    def search_hotels(self):
        ci = self.check_in_date[0:4] + \
             self.check_in_date[5:7] + self.check_in_date[8:10]
        co = self.check_out_date[0:4] + self.check_out_date[5:7] + \
            self.check_out_date[8:10]
        city_id = csvParser('city_list.csv').getCityID(self.location)

        base_url = 'https://www.goibibo.com/hotels/find-hotels-in-' + \
            self.location.lower() + '/' + city_id + '/' + city_id
        url = base_url + '/%7B"ci":"' + ci + \
            '","co":"' + co + '","r":"1-1_0"%7D/?{}&sec=dom'
        return url
