import subprocess
import operator
import requests 
import json
import os
import sys

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
		
def bssidlist (ssids):
# This function order the list of MAC addresses by RSSI (signal strenght) and return the top 3

	sorted_keys = sorted(ssids, key=lambda x: (ssids[x]['Signal']), reverse=True)
#	print(sorted_keys)

	aplist = list()
	for x in sorted_keys:
#		print(ssids[x]['BSSID'])
		aplist.append(ssids[x]['BSSID'])
	return aplist[:3]

def fetchUlocation (macaddr):
# This function calls Google Geolocation API based on Wi-Fi Access Points MAC addresses and respective RSSI
	
	# api-endpoint 
	URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=xxxxxxxxxxxxxxxxxxxxxxxxxx"
	
	# data to be sent to api
	
	macdata0 = "{'considerIp': 'false', 'wifiAccessPoints': ["
	macdata1 = "{'macAddress': '"
	macdata2 = "'}, {'macAddress': '".join(macaddr)
	macdata3 = "'}]}"
	macdata = json.dumps(macdata0+macdata1+macdata2+macdata3)
	macdata = macdata.strip('"')
	
#	print(macdata)
	
	#headers
	headers = {"content-type": "application/json charset=utf-8"}
	
	# sending post request and saving response as response object 
	r = requests.post(URL, data = macdata, headers = headers) 
  
	# extracting response text  
	pastebin_url = r.json()
#	print("The pastebin URL is:%s"%pastebin_url)
	return pastebin_url
	
def fetchrooms (user_geoloc):
#This function calls AWS API Gateway endpoint which in turns calls lambda function List_rooms_onlocation, it provides rooms location and #get in return the closest available rooms	

	# api-gateway endpoint 
	URL_APIG = "https://xxxxxxxxxxxxxxxxxxxxxxxxxx"
	
	# data to be sent to api
	
	#user_geoloc = user_geoloc.strip('"')
	
#	print(user_geoloc['location'])

	#params
	params = {'Latitude': user_geoloc['location']['lat'], 'Longitude': user_geoloc['location']['lng']}
	
	#headers
	headers_get = {"content-type": "application/json"}
	
	# sending get request and saving response as response object 
	req = requests.get(URL_APIG, params=params, headers = headers_get) 
  
	# extracting response text  
	resp = req.json()
	return resp

if __name__ == '__main__':		
	results = subprocess.check_output(["wifi", "scan"])
	results = results.decode('utf-8') # needed in python 3
	results = results.replace("\r","")
	ls = results.split("\n")
	ls = ls[4:]
	
	ssids = {}
	ssids_hlist = {}
	x = 0
	y = 0
	r = 0
			
	while x < len(ls):
		if "BSSID" in ls[x]:
			ssids_add = {
						'BSSID'	:	ls[x].replace(" ","")[7:],
						'Signal':	ls[x+1].replace(" ","")[7:]
						}
			ssids[y] = ssids_add
			y += 1
		x += 1
	geoloc = fetchUlocation(bssidlist(ssids))
	list_rooms = fetchrooms(geoloc)

	os.system('cls')  # on windows
	print("\n\n\n")
	for r in list_rooms:
		print(r['Room'],"is available at",int(r['Distance']),"meters")
	print("\n\n\n")
	input('Press any key to exit')