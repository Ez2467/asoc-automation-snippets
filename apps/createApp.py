#!/usr/bin/env python3
#############################################################################################################################
#  ©  Copyright HCL Technologies Ltd. 2017.  All Rights Reserved.
#  LICENSE: Apache License, Version 2.0 https://www.apache.org/licenses/LICENSE-2.0
#
#  This script demonstrates how to excercise the ASoC REST API to create applications. 
#  See the REST API Doc here: https://appscan.ibmcloud.com/swagger/ui/index 
#  
#    Usage: createApp.py <API Key ID> <API Key Secret> <Application Name>
#  
#  Notes: 
#    - Applications are created in the user's default AssetGroup. 
#    - No application attributes (other than "Name") are used when creating an app. In real-world automation, 
#      other attributes like Business Impact could be easily set by updating the createApp() method below
#  
#############################################################################################################################
import requests, json, sys	

# The ASoC REST APIs used in this script: 
REST_APIKEYLOGIN = "https://appscan.ibmcloud.com/api/v2/Account/ApiKeyLogin"
REST_ASSETGROUPS = "https://appscan.ibmcloud.com/api/V2/AssetGroups"
REST_APPS        = "https://appscan.ibmcloud.com/api/v2/Apps"

#############################################################################################################################
#  main() - Create an ASoC application with the given name if it doesn't already exist and print the application ID
#############################################################################################################################
def main():
    #Process arguments.
	if len(sys.argv) != 4:
		print("\nUsage: createApp.py <API Key ID> <API Key Secret> <Application Name>\n")
		sys.exit(1);
	keyid     = sys.argv[1]
	keysecret = sys.argv[2]
	appName   = sys.argv[3]
	
	# login to ASoC and get the bearer token
	token = getToken(keyid, keysecret)

	# If the app already exists just return its ID.  If not, then create the app and return the ID
	appId = findApp(token, appName)                    
	if appId is None:
		assetGroupId = getDefaultAssetGroupId(token)
		appId = createApp(token, assetGroupId, appName)
	print (appId)

	
#############################################################################################################################
#  getToken(keyId, keySecret) - Authenticate using the API Key ID/Secret. Return a Bearer Token used for all other REST APIs
#   
#  REST call and example JSON:
#    POST https://appscan.ibmcloud.com/api/v2/Account/ApiKeyLogin
#    json: { "KeyId" : "aaa" , "KeySecret" : "bbb" }
#############################################################################################################################
def getToken(keyId,keySecret):
	try:
		jsonData = {"KeyId":keyId,"KeySecret":keySecret}
		request = requests.post(REST_APIKEYLOGIN,json=jsonData)
		if (request.status_code != 200):
			print("Error: Unsuccessful call to " + REST_APIKEYLOGIN + ",Status Code=" + str(request.status_code) + "\n" + request.text);
			sys.exit(1)
		jsonData = json.loads(request.text)
		return jsonData['Token']
	except requests.exceptions.RequestException as e: 
		print("Error in getToken():\n" + e)
		sys.exit(1)

		
#############################################################################################################################	
#  getDefaultAssetGroupId(token) - Get the ID for the default AssetGroup
#
#  REST call:
#    GET https://appscan.ibmcloud.com/api/V2/AssetGroups  
#    params: "$filter=IsDefault eq true"
#	 headers: "Authorization=Bearer <token>" 
#############################################################################################################################
def getDefaultAssetGroupId(token):
	try:
		headers = {"Authorization":"Bearer " + token}
		params = { "$filter": "IsDefault eq true"}
		request = requests.get(REST_ASSETGROUPS,headers=headers,params=params)
		if (request.status_code != 200):
			print("Error: Unsuccessful call to " + REST_ASSETGROUPS + ",Status Code=" + str(request.status_code)  + "\n" + request.text);
			sys.exit(1)
		jsonData = json.loads(request.text)
		return jsonData[0]['Id']
	except requests.exceptions.RequestException as e: 
		print("Error in getDefaultAssetGroupId():\n" + e)
		sys.exit(1)

		
#############################################################################################################################
#  findApp(token, appName) - Find an application and return its ID or return None if it doesn't exist
#
#  REST call:
#    GET https://appscan.ibmcloud.com/api/v2/Apps
#    params: "$filter=Name eq '<appName>'"
#    headers: "Authorization=Bearer <token>" 
#############################################################################################################################
def findApp(token, appName):
	try:
		headers = {"Authorization":"Bearer " + token}
		params = {"$filter": "Name eq '" + appName + "'"}
		request = requests.get(REST_APPS,headers=headers,params=params)
		if (request.status_code == 200):
			jsonData = json.loads(request.text)
			if (len(jsonData) == 1):
				return jsonData[0]['Id']
		return None
	except requests.exceptions.RequestException as e: 
		print("Error in findApp():\n" + e)
		sys.exit(1)	

#############################################################################################################################	
# createApp(token, assetGroupId, appName) - Create an application and return its ID
# 
# REST call and example JSON:
#   POST https://appscan.ibmcloud.com/api/v2/Apps
#     headers: "Authorization=Bearer <token>"
#     json: { "Name" : "myApp" , "AssetGroupId" : "aaa" }
#############################################################################################################################
def createApp(token, assetGroupId, appName):
	try:
		headers = {"Authorization":"Bearer " + token}
		jsonData = {"Name": appName,"AssetGroupId": assetGroupId}
		request = requests.post(REST_APPS,headers=headers,json=jsonData)
		if (request.status_code != 201):
			print("Error in createApp(): Unsuccessful call to " + REST_APPS + ",Status Code=" + str(request.status_code) + "\n" + request.text);
			sys.exit(1)
		jsonData = json.loads(request.text)
		return jsonData['Id']
	except requests.exceptions.RequestException as e: 
		print("Error in createApp():\n" + e)
		sys.exit(1)	

		
# Python sugar for making the main() call work		
if __name__ == "__main__":
	main()
