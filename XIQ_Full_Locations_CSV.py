#!/usr/bin/env python3
import requests
import json
import sys
import getpass
import pandas as pd
from requests.exceptions import HTTPError

BASEURL = "https://api.extremecloudiq.com"

HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

print("Enter your XIQ login credentials")
username = input("Email: ")
password = getpass.getpass("Password: ")

print("Make sure the csv file is in the same folder as the python script.")
filename = input("Please enter csv filename: ")


# get access token
def GetaccessToken(username, password):
    url = BASEURL + "/login"
    payload = json.dumps({"username": username, "password": password})
    response = requests.post(url, headers=HEADERS, data=payload)
    if response is None:
        print("ERROR: Not able to login into ExtremeCloudIQ - no response!")
        return -1
    if response.status_code != 200:
        print(f"Error creating building in XIQ - HTTP Status Code: {str(response.status_code)}")
        raise TypeError(response)
    data = response.json()

    if "access_token" in data:
        print("Logged in and Got access token: " + data["access_token"])
        HEADERS["Authorization"] = "Bearer " + data["access_token"]
        return 0

    else:
        raise TypeError("Unknown Error: Unable to gain access token")



# Global Objects
pagesize = '' #Value can be added to set page size. If nothing in quotes default value will be used (500)
totalretries = 5 #Value can be adjusted - this will adjust how many attempts to try each API call

device_list = []
location_tree = []
loc_id = {}
dfapi = pd.DataFrame(columns = ['id', 'name', 'type'])

# Git Shell Coloring - https://gist.github.com/vratiu/9780109
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
YELLOW="\033[0;33m"
RESET = "\033[0;0m"



def GetLocationTree():
    #print("list all locations from XIQ ")
    global location_tree

    url = BASEURL + '/locations/tree'
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
    except HTTPError as http_err:
        sys.stdout.write(RED)
        print(f'HTTP error occurred: {http_err} - on API {url}')  
        sys.stdout.write(RESET)
        print("Script is exiting...")
        raise SystemExit
    except Exception as err:
        sys.stdout.write(RED)
        print(f'Other error occurred: {err}: on API {url}')
        sys.stdout.write(RESET)
        print("Script is exiting...")
        raise SystemExit
    else:
        if response is None:
            sys.stdout.write(RED)
            log_msg = "Error retrieving Location Tree from XIQ - no response!"
            print(log_msg)
            sys.stdout.write(RESET)
            print("Script is exiting...")
            raise SystemExit
        elif response.status_code != 200:
            sys.stdout.write(RED)
            log_msg = f"Error retrieving Location Tree from XIQ - HTTP Status Code: {str(response.status_code)}"
            print(log_msg)
            sys.stdout.write(RESET)
            print("Script is exiting...")
            raise SystemExit

        rawList = response.json()
        if 'error' in rawList:
            if rawList['error_mssage']:
                sys.stdout.write(RED)
                failmsg = (f"Status Code {rawList['error_id']}: {rawList['error_message']}")
                print(f"API Failed with reason: {failmsg} - on API {url}")
                sys.stdout.write(RESET)
                print("Script is exiting...")
                raise SystemExit

    for location in rawList:
        location_tree.append(BuildLocationDic(location))


def BuildLocationDic(location, pdict = {'Global': []}, pname = 'Global'):
    global dfapi
    #print(location['name'])
    if location['parent_id'] == None:
        dfapi = dfapi.append({'id': location['id'], 'name':location['name'], 'type': 'Global', 'parent':pname}, ignore_index=True)
    else:
        dfapi = dfapi.append({'id': location['id'], 'name':location['name'], 'type': location['type'],'parent':pname}, ignore_index=True)     
    r = json.dumps(location['children'])
    if not location['children'] :
        pdict[pname].append(location['name'])
    else:
        parent_name = location['name']
        parent_dic = {parent_name: [] }
        for child in location['children']:
            parent_dic = (BuildLocationDic(child, pdict=parent_dic, pname=parent_name))
        pdict[pname].append(parent_dic)
    return pdict

def CreateLocation(payload):
    #print("Trying to create the new  Location")
    url = BASEURL + "/locations"
    try:
        response = requests.post(url, headers=HEADERS, data=payload, verify=True)
    except HTTPError as http_err:
        raise HTTPError (f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            log_msg = "Error Creating Location in XIQ - no response!"
            raise TypeError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error Creating Location in XIQ - HTTP Status Code: {str(response.status_code)}"
            try:
                rawList = response.json()
                log_msg += json.dumps(rawList)
                raise TypeError(log_msg)
            except:
                raise TypeError(log_msg)     
        locationid1 = response.json().get("id")
        return locationid1


def CreateBuilding(payload):
    #print("Trying to create the new  Building")
    url = BASEURL + "/locations/building"
    try:
        response = requests.post(url, headers=HEADERS, data=payload, verify=True)
    except HTTPError as http_err:
        raise HTTPError (f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            log_msg = "Error Creating Building in XIQ - no response!"
            raise TypeError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error Creating Building in XIQ - HTTP Status Code: {str(response.status_code)}"
            try:
                rawList = response.json()
                log_msg += json.dumps(rawList)
                raise TypeError(log_msg)
            except:
                raise TypeError(log_msg)    
        buildingid1 = response.json().get("id")
        return buildingid1

def CreateFloor(payload):
    #print("Trying to create the new Floor")
    url = BASEURL + "/locations/floor"
    try:
        response = requests.post(url, headers=HEADERS, data=payload, verify=True)
    except HTTPError as http_err:
        raise HTTPError (f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            log_msg = "Error Creating Floor in XIQ - no response!"
            raise TypeError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error Creating Floor in XIQ - HTTP Status Code: {str(response.status_code)}"
            try:
                rawList = response.json()
                log_msg += json.dumps(rawList)
                raise TypeError(log_msg)
            except:
                raise TypeError(log_msg)    
        floorid1 = response.json().get("id")
        return floorid1
    

def main():
    global dfapi
    global location_tree
    try:
        login = GetaccessToken(username, password)
    except TypeError as e:
        print(e)
        raise SystemExit
    except:
        print("Unknown Error: Failed to generate token")
        raise SystemExit
    GetLocationTree()
    dfcsv = pd.read_csv(filename)
    dfcsv['map_name'] = dfcsv['map_name'].fillna('')
    for k,v in (location_tree[0]['Global'][0]).items():
        filt = (dfapi['name'] == k)
        glob_id = dfapi.loc[filt, 'id'].values[0]
        glob_name = dfapi.loc[filt, 'name'].values[0]
        data = v
   #print(dfapi)

    for index, row in dfcsv.iterrows():
        #print(row)
        sys.stdout.write(BLUE)
        print(f"\nStarting row {index}")
        sys.stdout.write(RESET)
        if pd.isnull(dfcsv.loc[index,'loc_name']):
            sys.stdout.write(RED)
            print("There is no location defined in row " + str(index))
            sys.stdout.write(RESET)
            print(f"Skipping row {str(index)}")
            continue
        # Check if location exists, create if not
        if row['loc_name'] in dfapi['name'].values:
            loc_filt = (dfapi['name'] == row['loc_name']) & (dfapi['type'] == 'Location')
            loc_id = dfapi.loc[loc_filt, 'id']
            if not loc_id.empty:
                print(f"Location {row['loc_name']} already exists... Attemping Building")
                loc_id = loc_id.values[0]
            else:
                loc_filt = (dfapi['name'] == row['loc_name'])
                loc_type = dfapi.loc[loc_filt, 'type'].values[0]
                sys.stdout.write(RED)
                print(f"{row['loc_name']} Location was found but is defined as a {loc_type}")
                sys.stdout.write(RESET)
                print(f"Skipping row {str(index)}")
                continue
        else:
            # Create Location
            location_payload = json.dumps(
                {"parent_id": glob_id,
                 "name": row['loc_name'],
                 "address": row['address']}
            )
            print(f"create Location {row['loc_name']}")
            try:
                loc_id = CreateLocation(location_payload)
            except HTTPError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping line {str(index)}")
                continue
            except TypeError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping line {str(index)}")
                continue
            except:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping line {str(index)}")
                continue
            dfapi = dfapi.append({'id':loc_id,'name':row['loc_name'], 'type':'Location', 'parent': glob_name }, ignore_index=True)

        
        # Check if build exists, create if not
        if row['building_name'] in dfapi['name'].values:
            build_filt = (dfapi['name'] == row['building_name']) & (dfapi['type'] == 'BUILDING')
            build_id = dfapi.loc[build_filt, 'id']
            build_prt = dfapi.loc[build_filt, 'parent']
            
            if not build_id.empty:
                if build_prt.values[0] == row['loc_name']:
                    print(f"Building {row['building_name']} already exists in {build_prt.values[0]}... Attemping Floor")
                else:
                    sys.stdout.write(RED)
                    print(f"\nBuilding {row['building_name']} was found in {build_prt.values[0]} instead of {row['loc_name']}!!!")
                    sys.stdout.write(RESET)
                    print(f"Skipping rest of the row {str(index)}\n")
                    continue
                build_id = build_id.values[0]
            else:
                sys.stdout.write(RED)
                build_filt = (dfapi['name'] == row['building_name'])
                build_type = dfapi.loc[build_filt, 'type'].values[0]
                print(f"{row['building_name']} Building was found but is defined as a {build_type}")
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(index)}")
                continue
        else:
            # Create Building
            building_payload = json.dumps(
                {"parent_id": loc_id,
                 "name": row['building_name'],
                 "address": row['address']}
            )
            print(f"creating Building {row['building_name']}")
            try:
                build_id = CreateBuilding(building_payload)
            except HTTPError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(index)}")
                continue
            except TypeError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(index)}")
                continue
            except:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(index)}")
                continue
            dfapi = dfapi.append({'id':build_id,'name':row['building_name'], 'type':'BUILDING', 'parent': row['loc_name']}, ignore_index=True)

        createFloor = True
        # Check if floor exists in building, create if not
        if row['floor_name'] in dfapi['name'].values:
            flr_filt = (dfapi['name'] == row['floor_name']) & (dfapi['type'] == 'FLOOR') & (dfapi['parent'] == row['building_name'])
            flr_id = dfapi.loc[flr_filt, 'id']
            if not flr_id.empty:
                sys.stdout.write(YELLOW)
                print(f"Floor {row['floor_name']} already exists in {row['building_name']}")
                sys.stdout.write(RESET)
                createFloor = True
                continue
        if createFloor:
            # Create Floor
            floor_payload = json.dumps(
                {
                    "parent_id": build_id,
                    "name": row['floor_name'],
                    "environment": row["environment"],
                    "db_attenuation": row['attenuation'],
                    "measurement_unit": row['measurement'],
                    "installation_height": row['height'],
                    "map_size_width": row['map_width'],
                    "map_size_height": row['map_height'],
                    "map_name": row['map_name']
                }
            )
            #print(floor_payload)
            print(f"create Floor {row['floor_name']}")
            try:
                floor_id = CreateFloor(floor_payload)
            except HTTPError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Failed creating Floor on row {str(index)}. Attempting next row.")
                continue
            except TypeError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Failed creating Floor on row {str(index)}. Attempting next row.")
                continue
            except:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Failed creating Floor on row {str(index)}. Attempting next row.")
                continue
            dfapi = dfapi.append({'id':floor_id,'name':row['floor_name'], 'type':'FLOOR', 'parent': row['building_name']}, ignore_index=True)
    
        


if __name__ == '__main__':
	main()
