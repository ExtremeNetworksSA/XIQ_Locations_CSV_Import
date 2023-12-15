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
dfapi = pd.DataFrame(columns = ['id', 'name', 'type', 'parent'])
def_columns =["site_group_1_name(if necessary)","site_group_2_name(if necessary)","site_name","building_name","address","city","state","postal_code","country_code","floor_name","environment","attenuation","measurement","height","map_width","map_height","map_name(if available)"]

# Git Shell Coloring - https://gist.github.com/vratiu/9780109
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
YELLOW="\033[0;33m"
RESET = "\033[0;0m"



def GetLocationTree():
    #print("list all locations from XIQ ")

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
        BuildLocationDic(location)


def BuildLocationDic(location, pname = 'Global'): 
    global dfapi
    #print(location['name'])
    if 'parent_id' not in location:
        temp_df = pd.DataFrame([{'id': location['id'], 'name':location['name'], 'type': 'Global', 'parent':pname}])
        dfapi = pd.concat([dfapi, temp_df], ignore_index=True)
    else:
        temp_df = pd.DataFrame([{'id': location['id'], 'name':location['name'], 'type': location['type'], 'parent':pname}])
        dfapi = pd.concat([dfapi, temp_df], ignore_index=True)   
    r = json.dumps(location['children'])
    if location['children']:
            parent_name = location['name']
            for child in location['children']:
                BuildLocationDic(child, pname=parent_name)

def CheckCountryCode(country_code):
    url = BASEURL + "/countries/" + str(country_code) + "/:validate"
    try:
        response = requests.get(url, headers=HEADERS, verify=True)
    except HTTPError as http_err:
        raise HTTPError (f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            log_msg = "Error Checking Country Code in XIQ - no response!"
            raise TypeError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error Checking Country Code in XIQ - HTTP Status Code: {str(response.status_code)}"
            try:
                rawList = response.json()
                log_msg += json.dumps(rawList)
                raise TypeError(log_msg)
            except:
                raise TypeError(log_msg)  

    return response.text

def CreateLocation(payload, site=False):
    #print("Trying to create the new  Site Group")
    if site:
        url = BASEURL + "/locations/site"
    else:
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
    try:
        login = GetaccessToken(username, password)
    except TypeError as e:
        print(e)
        raise SystemExit
    except:
        print("Unknown Error: Failed to generate token")
        raise SystemExit
    GetLocationTree()
    try:
        dfcsv = pd.read_csv(filename)
    except FileNotFoundError as e:
        print(e)
        raise SystemExit
    columns = list(dfcsv.columns)
    if columns != def_columns:
        print("The columns in the csv file have been edited. Please use correct column names.")
        raise SystemExit
    dfcsv['map_name(if available)'] = dfcsv['map_name(if available)'].fillna('')
    dfcsv['site_group_1_name(if necessary)'] = dfcsv['site_group_1_name(if necessary)'].fillna('')
    dfcsv['site_group_2_name(if necessary)'] = dfcsv['site_group_2_name(if necessary)'].fillna('')
    filt = dfapi['type'] == 'Global'
    glob_id = dfapi.loc[filt, 'id'].values[0]
    glob_name = dfapi.loc[filt, 'name'].values[0]
    

    for index, row in dfcsv.iterrows():
        rownum = index + 2
        #print(row)
        sys.stdout.write(BLUE)
        print(f"\nStarting row {rownum}")
        sys.stdout.write(RESET)
        # Check for Site Groups in csv file - if not move on to site
        if row.isnull().values.any():
            missing = []
            for index,frame in row.isnull().items():
                if frame:
                    missing.append(index)
            sys.stdout.write(RED)
            print("Row " + str(rownum) + " is missing the following elements: " + ", ".join(missing))
            sys.stdout.write(RESET)
            print(f"Skipping row {str(rownum)}")
            continue
        
        # Validate Country Code
        cc_response = CheckCountryCode(row['country_code'])
        if cc_response == 'false':
            sys.stdout.write(RED)
            print("Could not validate the Country Code for row "  + str(rownum))
            sys.stdout.write(RESET)
            print(f"Skipping row {str(rownum)}")
            continue
            
    
        parent_name = glob_name
        parent_id = glob_id
        skiprow = False
        for site_group in 'site_group_1_name(if necessary)','site_group_2_name(if necessary)':
            if dfcsv.loc[index,site_group]:
                print(row[site_group])
                print(f"Checking Site Group {row[site_group]}")
                # Check if location exists, create if not
                if row[site_group] in dfapi['name'].values:
                    site_group_filt = (dfapi['name'] == row[site_group]) & (dfapi['type'] == 'Site_Group')
                    site_group_id = dfapi.loc[site_group_filt, 'id']
                    real_parent_name = dfapi.loc[site_group_filt, "parent"].values[0]
                    if not site_group_id.empty:
                        if real_parent_name == parent_name:
                            sys.stdout.write(YELLOW)
                            print(f"Site Group {row[site_group]} already exists...")
                            sys.stdout.write(RESET)
                            parent_name = row[site_group]
                            parent_id = site_group_id.values[0]
                        else:
                            sys.stdout.write(RED)
                            print(f"Site Group {row[site_group]} exists under {real_parent_name} CSV has it under {parent_name}")
                            sys.stdout.write(RESET)
                            skiprow = True
                            break
                    else: 
                        site_group_filt = (dfapi['name'] == row[site_group])
                        site_group_type = dfapi.loc[site_group_filt, 'type'].values[0]
                        sys.stdout.write(RED)
                        print(f"Site Group {row[site_group]} was found but is defined as a {site_group_type}")
                        sys.stdout.write(RESET)
                        skiprow = True
                        break
                else:
                    # Create Location
                    location_payload = json.dumps(
                        {"parent_id": parent_id,
                         "name": row[site_group]}
                    )
                    print(f"create Site Group {row[site_group]} under {parent_name}")
                    try:
                        parent_id = CreateLocation(location_payload)
                    except HTTPError as e:
                        sys.stdout.write(RED)
                        print(e)
                        sys.stdout.write(RESET)
                        skiprow = True
                        break
                    except TypeError as e:
                        sys.stdout.write(RED)
                        print(e)
                        sys.stdout.write(RESET)
                        skiprow = True
                        break
                    except:
                        sys.stdout.write(RED)
                        print(e)
                        sys.stdout.write(RESET)
                        skiprow = True
                        break
                    temp_df = pd.DataFrame([{'id': parent_id, 'name':row[site_group], 'type': 'Site_Group', 'parent':parent_name}])
                    dfapi = pd.concat([dfapi, temp_df], ignore_index=True)
                    parent_name = row[site_group]

        # Skip the row if Site Groups are incorrect
        if skiprow:
            print(f"Skipping line {str(rownum)}")
            continue

        # Check if site exists, create if not
        if row['site_name'] in dfapi['name'].values:
            site_filt = (dfapi['name'] == row['site_name']) & (dfapi['type'] == 'SITE')
            site_id = dfapi.loc[site_filt, 'id']
            if not site_id.empty:
                sys.stdout.write(YELLOW)
                print(f"Site {row['site_name']} already exists...")
                site_id = site_id.values[0]
                sys.stdout.write(RESET)
            else:
                site_filt = (dfapi['name'] == row['site_name'])
                loc_type = dfapi.loc[site_filt, 'type'].values[0]
                sys.stdout.write(RED)
                print(f"{row['site_name']} Site was found but is defined as a {loc_type}")
                sys.stdout.write(RESET)
                print(f"Skipping row {str(rownum)}")
                continue
        else:
            # Create site
            site_payload = json.dumps(
                {"parent_id": parent_id, 
                 "name": row['site_name'],
                 "address": {
                   "address": row['address'],
                   "city": row['city'],
                   "state": row['state'],
                   "postal_code": str(int(row['postal_code']))
                 },
                 "country_code": row['country_code']
                }
            )
            print(f"Create Site {row['site_name']}")
            print(site_payload)
            try:
                site_id = CreateLocation(site_payload, site=True)
            except HTTPError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping line {str(rownum)}")
                continue
            except TypeError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping line {str(rownum)}")
                continue
            except:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping line {str(rownum)}")
                continue
            temp_df = pd.DataFrame([{'id': site_id, 'name':row['site_name'], 'type': 'SITE', 'parent':parent_name}])
            dfapi = pd.concat([dfapi, temp_df], ignore_index=True) 

        # Check if build exists, create if not
        print("Attemping Building")
        if row['building_name'] in dfapi['name'].values:
            build_filt = (dfapi['name'] == row['building_name']) & (dfapi['type'] == 'BUILDING')
            build_id = dfapi.loc[build_filt, 'id']
            build_prt = dfapi.loc[build_filt, 'parent']
            
            if not build_id.empty:
                if build_prt.values[0] == parent_name:
                    sys.stdout.write(YELLOW)
                    print(f"Building {row['building_name']} already exists in {build_prt.values[0]}... Attempting Floor")
                    sys.stdout.write(RESET)
                else:
                    sys.stdout.write(RED)
                    print(f"\nBuilding {row['building_name']} was found in {build_prt.values[0]} instead of {parent_name}!!!")
                    sys.stdout.write(RESET)
                    print(f"Skipping rest of the row {str(rownum)}\n")
                    continue
                build_id = build_id.values[0]
            else:
                sys.stdout.write(RED)
                build_filt = (dfapi['name'] == row['building_name'])
                build_type = dfapi.loc[build_filt, 'type'].values[0]
                print(f"{row['building_name']} Building was found but is defined as a {build_type}")
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(rownum)}")
                continue
        else:
            # Create Building
            building_payload = json.dumps({
                "parent_id": site_id,
                "name": row['building_name'],
                "address": {
                    "address": row['address'],
                    "city": row['city'],
                    "state": row['state'],
                    "postal_code": str(int(row['postal_code']))
                }
            })
            print(f"creating Building {row['building_name']}")
            print(building_payload)
            try:
                build_id = CreateBuilding(building_payload)
            except HTTPError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(rownum)}")
                continue
            except TypeError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(rownum)}")
                continue
            except:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Skipping the rest of the row {str(rownum)}")
                continue
            temp_df = pd.DataFrame([{'id': build_id, 'name':row['building_name'], 'type': 'BUILDING', 'parent':parent_name}])
            dfapi = pd.concat([dfapi, temp_df], ignore_index=True) 

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
            data = {
                    "parent_id": build_id,
                    "name": row['floor_name'],
                    "environment": row["environment"],
                    "db_attenuation": row['attenuation'],
                    "measurement_unit": row['measurement'],
                    "installation_height": row['height'],
                    "map_size_width": row['map_width'],
                    "map_size_height": row['map_height']
                }
            if row['map_name(if available)']:
                data['map_name'] = row['map_name(if available)']
            floor_payload = json.dumps(data)
            #print(floor_payload)
            print(f"create Floor {row['floor_name']}")
            try:
                floor_id = CreateFloor(floor_payload)
            except HTTPError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Failed creating Floor on row {str(rownum)}. Attempting next row.")
                continue
            except TypeError as e:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Failed creating Floor on row {str(rownum)}. Attempting next row.")
                continue
            except:
                sys.stdout.write(RED)
                print(e)
                sys.stdout.write(RESET)
                print(f"Failed creating Floor on row {str(rownum)}. Attempting next row.")
                continue
            temp_df = pd.DataFrame([{'id': floor_id, 'name':row['floor_name'], 'type': 'FLOOR', 'parent':row['building_name']}])
            dfapi = pd.concat([dfapi, temp_df], ignore_index=True) 
    
    #print(dfapi)


if __name__ == '__main__':
	main()
