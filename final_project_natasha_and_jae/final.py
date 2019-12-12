import webapp2, os, urllib2, json, jinja2, logging, urllib

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):

        location = self.request.get('location_input')

        if location:
            if airQuality(convert2Geo(location)) is not None:
                # airData gives a dictionary with the air data (AQI & molecule levels) for a particular geolocation
                airData = airQuality(convert2Geo(location))
                airData['location_name'] = location
                airData['quality'] = myApp(location)['quality']
                airData['suggestion'] = myApp(location)['suggestion']
                # airData['real_location'] = locationData(location)
                myApp(location)
            else:
                airData = {}
                airData['location_name']  = 'You have entered an invalid location, please try again.'
        else:
            airData = {}

        logging.info('-----------------------')
        logging.info(airData)
        template = JINJA_ENVIRONMENT.get_template('webspeech.html')
        self.response.write(template.render(airData))


application = webapp2.WSGIApplication([('/', MainHandler)], debug=True)

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

# Takes latitude and longitude & produces the air quality data.
def airQuality(geolocation):
    baseurl = 'https://api.weatherbit.io/v2.0/current/airquality'
    params = {}
    params['lat'] = geolocation[0]
    params['lon'] = geolocation[1]
    #params['key'] = 'bf472fb4344d43cf92fdfdc327d94d6b'
    #params['key'] = '114323d277914f8b880876a98f6b71e2'
    #params['key'] = '8dba89ffb97c40de9eebe8415910a0ca'
    params['key'] = '59b00f75c2cc478785d71049d05dea3e'
    
    datarequest = baseurl + "?" + urllib.urlencode(params)
    try:
        request = urllib2.urlopen(datarequest).read()
        airData = json.loads(request)
        airDict = {}
        airDict['AQI'] = airData['data'][0]['aqi']
        airDict['CO'] = airData['data'][0]['co']
        airDict['NO2'] = airData['data'][0]['no2']
        airDict['O3'] = airData['data'][0]['o3']
        airDict['PM10'] = airData['data'][0]['pm10']
        airDict['PM25'] = airData['data'][0]['pm25']
        airDict['SO2'] = airData['data'][0]['so2']
        return airDict

    except urllib2.HTTPError as e:
        logging.error("error trying to retrieve data: %s" % e)
        return None
    except urllib2.URLError as e:
        logging.error("error trying to retrieve data: %s" % e)
        return None

    # Newly added error
    except urllib2.HTTPException as e:
        logging.error("error trying to retrieve data: %s" % e)
        return None

    except urllib2.UnboudLocalError as e:
        logging.error('Invalid location entered. Please try again.')
        return None


# Takes name of street address/city/countries & produces geological location of it.
def convert2Geo(address):
    baseurl = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {}
    params['address'] = address
    params['key'] = 'AIzaSyDYvNokmGObIdYsN1FBrGdfGLrmQ-CBuUM'
    georequest = baseurl + "?" + urllib.urlencode(params)
    try:
        request = urllib2.urlopen(georequest)
        georequeststr = request.read()
        geodata = json.loads(georequeststr)

        if geodata['results'] == []:
            latitude = None
            longitude = None
            logging.info("You have entered an invalid location, please try again.")
        else:
            for output in geodata['results']:
                logging.info("The air quality in [" + geodata['results'][0]['formatted_address'] + ']:')
                latitude = str(geodata['results'][0]['geometry']['location']['lat'])
                longitude = str(geodata['results'][0]['geometry']['location']['lng'])
        return latitude, longitude
    except urllib2.HTTPError as e:
        logging.error("Error trying to retrieve data: %s" % e)
        return None
    except urllib2.URLError as e:
        logging.error("Error trying to retrieve data: %s" % e)
        return None

def locationData(address):
    baseurl = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {}
    params['address'] = address
    params['key'] = 'AIzaSyDYvNokmGObIdYsN1FBrGdfGLrmQ-CBuUM'
    georequest = baseurl + "?" + urllib.urlencode(params)
    try:
        request = urllib2.urlopen(georequest)
        georequeststr = request.read()
        geodata = json.loads(georequeststr)
        
        locationData = geodata['results'][0]['formatted_address']
        return locationData
    except urllib2.HTTPError as e:
        logging.error("Error trying to retrieve data: %s" % e)
        return None
    except urllib2.URLError as e:
        logging.error("Error trying to retrieve data: %s" % e)
        return None

# Takes name of address/city/countries & produces air quality data and gives user feedback based on AQI index
def myApp(location):
    airData = airQuality(convert2Geo(location))
    for data in airData:
        logging.info(data + ": " + str(airData[data]))
    if airData['AQI'] < 51:
        airData['quality'] = 'good'
        logging.info(airData['quality'])
        airData['suggestion'] = 'The air quality conditions are good. It is safe for all people to go outside.'
    elif airData['AQI'] < 101:
        airData['quality'] = 'moderate'
        logging.info(airData['quality'])
        airData['suggestion'] = 'The air quality conditions are moderate and pose little or no health risk. It is safe for all people to go outside, but extremely sensitive individuals may want to avoid prolonged exposure.'
    elif airData['AQI'] < 151:
        airData['quality'] = 'unhealthy for sensitive groups'
        logging.info(airData['quality'])
        airData['suggestion'] = 'The air quality conditions are unhealthy for sensitive groups, which includes people with heart or lung disease, older adults, and children. These individuals are at a greater risk of experiencing health consequences, but the general public is unlikely to be affected. Sensitive groups should reduce prolonged outdoor exposure. At this level, it is suggested to wear a mask outdoors.'
    elif airData['AQI'] < 201:
        airData['quality'] = 'unhealthy'
        logging.info(airData['quality'])
        airData['suggestion'] = 'The air quality conditions are unhealthy. Everyone may begin to experience health effects, however members of sensitive groups will experience more serious ones. All people should avoid prolonged outdoor exposure. If necessary to go outdoors, individuals should wear a N95 respirator or P100 mask for the best protection.'
    elif airData['AQI'] < 301:
        airData['quality'] = 'very unhealthy'
        logging.info(airData['quality'])
        airData['suggestion'] = 'The air quality conditions are very unhealthy and may trigger health alerts. All individuals may experience health affects and should avoid outdoor exposure. If absolutely necessary to go outdoors, individuals should wear a N95 respirator or P100 mask for the best protection.'
    elif airData['AQI'] < 501:
        airData['quality'] = 'hazardous'
        logging.info(airData['quality'])
        airData['suggestion'] = 'The air quality conditions are hazardous and may trigger health warnings of emergency conditions. The entire population is likely to be affected by serious health effects and should therefore completely avoid outdoor exposure. If absolutely necessary to go outdoors, individuals should wear a N95 respirator or P100 mask for the best protection.'
    return airData