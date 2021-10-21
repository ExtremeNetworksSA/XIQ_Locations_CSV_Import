import json
import getpass
import requests

URL = "https://api.extremecloudiq.com"

print("Enter your XIQ login credentials")
username = input("Email: ")
password = getpass.getpass("Password: ")

headers = {"Accept": "application/json", "Content-Type": "application/json"}

# get access token
def GetaccessToken(username, password):
    url = URL + "/login"
    payload = json.dumps({"username": username, "password": password})
    response = requests.post(url, headers=headers, data=payload)
    if response is None:
        print("ERROR: Not able to login into ExtremeCloudIQ - no response!")
        return -1
    if response.status_code != 200:
        print(f"ERROR: Not able to login into ExtremeCloudIQ - HTTP Status Code: {str(response.status_code)}")
        raise TypeError(response)
    data = response.json()

    if "access_token" in data:
        print("Logged in and Got access token: " + data["access_token"])
        headers["Authorization"] = "Bearer " + data["access_token"]
        return 0

    else:
        raise TypeError("Unknown Error: Unable to gain access token")

def GetDeviceIDs(curlocID):
    print("Getting all Device IDs from XIQ, please wait..." )
    allDeviceIDs = []

    url = URL+'/devices?page=1&limit=100&locationId='+str(curlocID)
    response = requests.get(url, headers=headers, verify = True)
    if response is None:
        print("Error retrieving DeviceIDs from XIQ - no response!")
        return

    if response.status_code != 200:
        print("Error retrieving DeviceIDs from XIQ - HTTP Status Code: " +
              str(response.status_code))
        print(response)
        return

    rawList = response.json()
    #rawList stores all devices found on currentlocID
    #print(rawList)
    allDeviceIDs = rawList.get("data")
    return(allDeviceIDs)

def GetALLLocationTree(location_id):
    alllocations = []

    url = URL+'/locations/tree?parentId=' + str(location_id) + '&expandChildren=true'
    response = requests.get(url, headers=headers, verify = True)
    if response is None:
        print("Error retrieving locations from XIQ - no response!")
        return

    if response.status_code != 200:
        print("Error retrieving locations from XIQ - HTTP Status Code: " +
              str(response.status_code))
        print(response)
        return

    all_locations = response.json()
    #    for location in all_locations: # commentato il 31 luglio 2021
    #        print(location)    # commentato il 31 luglio 2021

    return all_locations

def getcurrentAPlocation(AP_ID):
    #print("\nlist AP location information from XIQ " )
    url = URL +'/devices/' + AP_ID + '/location'
    response = requests.get(url, headers=headers, verify = True)
    if response is None:
        print("Error retrieving locations from XIQ - no response!")
        return

    if response.status_code != 200:
        print("Error retrieving locations from XIQ - HTTP Status Code: " +
              str(response.status_code))
        print(response)
        return

    APlocation = response.json()
    APlocationx = APlocation['x']
    APlocationy = APlocation['y']
    APlocation_name=APlocation['location_name']
    APparentID = APlocation['parent_id']
    print('x= ' + str(APlocationx))
    print('y= ' + str(APlocationy))
    print('AP-locname= ' + str(APlocation_name))
    print('parentID= ' + str(APparentID))

    return APlocation

def Assignlocation(AP_ID,APlocation,floorID):
    #print("\ntrying to assign AP location")

    url = URL +'/devices/' + AP_ID + '/location'
    payload = json.dumps({  "location_id": floorID,
                            "x":APlocation['x'],
                            "y":APlocation['y'],
                            "latitude":"null",
                            "longitude":"null"
                            })

    response = requests.put(url, headers=headers,data=payload, verify = True)
    print(payload)
    if response is None:
        print("Error assigning location to AP in XIQ - no response!")
        return

    if response.status_code != 200:
        print("Error assigning location to AP in XIQ - HTTP Status Code: " +
              str(response.status_code))
        print(response)
        return

    return response

def process_ap(ap_id):
    ap_location = getcurrentAPlocation(ap_id)
    print("\nCurrent AP Location:")
    print(ap_location)
    #floor_id = 723491536092388
    print (floor_id)
    try:
        AssignAP = Assignlocation(ap_id,ap_location,floor_id)
    except TypeError as e:
        print(e)

try:
    login = GetaccessToken(username, password)
except TypeError as e:
    print(e)
    raise SystemExit
except:
    print("Unknown Error: Failed to generate token")
    raise SystemExit

#currentlocID is the location where we want to move the AP from the location to the floor
#currentlocID = 723491536092313
currentlocID = int(input("Enter the location ID where the devices are currently: "))
floor_id = int(input("Enter the floor ID where the devices will be moved to: "))

loc_id2 = GetDeviceIDs(currentlocID)
for AP in loc_id2:
    ap_id = str(AP['id'])
    process_ap(ap_id)
    print(ap_id)