import requests
import os
from datetime import datetime, timedelta
import libhoney
import time

def timestamp_string(minutesAgo=0):
    current_time = datetime.now()
    ts = current_time - timedelta(minutes=minutesAgo)
    formatted_ts = ts.strftime('%Y-%m-%dT%H:%M:%SZ')
    return formatted_ts

def flatten_json(json_obj, parent_key='', flattened_dict=None):
    if flattened_dict is None:
        flattened_dict = {}

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            flatten_json(value, new_key, flattened_dict)
    elif isinstance(json_obj, list):
        for i, item in enumerate(json_obj):
            new_key = f"{parent_key}.{i}" if parent_key else str(i)
            flatten_json(item, new_key, flattened_dict)
    else:
        flattened_dict[parent_key] = json_obj

    return flattened_dict

def flightsFromResponse(payload): 
    flights = []
    arrivalsPayload = payload['arrivals']
    for flight in arrivalsPayload:
        flattened_arrival = flatten_json(flight)
        flights.append(flattened_arrival)
    
    departuresPayload = payload['departures']
    for flight in departuresPayload:
        flattened_departure = flatten_json(flight)
        flights.append(flight)

    return flights

def report_to_honeycomb(flights):
    honeycomb_api_key = os.environ['HONEYCOMB_API_KEY']
    libhoney.init(writekey=honeycomb_api_key, dataset="airport-stats-ksea", send_frequency=0, debug=True)
    for flight in flights: 
        print(flight)
        event = libhoney.new_event()     
        event.add(flight)
        event.send()
    libhoney.close()

aeroapi_key = os.environ['AEROAPI_KEY']
apiUrl = "https://aeroapi.flightaware.com/aeroapi/"

sixMinAgo = timestamp_string(6)
now = timestamp_string()
print('Retrieving all flights since {}'.format(sixMinAgo))
airport = 'KSEA'
payload = {
    'max_pages': 2,
    'type': 'Airline',
    'start': sixMinAgo,
    'end': now
}

print('Parameters: {}'.format(payload))
auth_header = {'x-apikey':aeroapi_key}

response = requests.get(apiUrl + f"airports/{airport}/flights",
    params=payload, headers=auth_header)

if response.status_code == 200:
    jsonResponse = response.json()
    flights = flightsFromResponse(jsonResponse)
    print('{} flights received.'.format(len(flights)))
    report_to_honeycomb(flights)
    time.sleep(2) # sleep for a 2 seconds to give honeycomb push time to complete

else:
    print("Error executing request")
    print(response.request.url)
    print(response.request.body)
