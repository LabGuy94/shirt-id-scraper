from requests import session
import json
from threading import Thread
import random
from time import sleep

config = json.loads(open('config.json').read())
requests = session()
shirtidfile = open("shirtids.txt", "a")
proxies = open('proxies.txt','r').read().splitlines()
proxies = [{'https':'http://'+proxy} for proxy in proxies]

cookies = {
    ".ROBLOSECURITY": config["cookie"],
}
xcsrf = requests.post("https://auth.roblox.com/v2/logout", cookies=cookies).headers["x-csrf-token"]
headers = {
    'X-CSRF-TOKEN': xcsrf,
    'Content-Type': 'application/json'
}


frontpage = requests.get("https://catalog.roblox.com/v1/search/items?category=Clothing&cursor=2_1_ebe070af2c87386a00202b3f4b0f9316&limit=60&subcategory=ClassicShirts").json()


def scrapegroup(groupid, cursor=None):
    if(cursor != None):
        response = requests.get(f"https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor={cursor}&limit=50&sortOrder=Desc&sortType=Updated", headers=headers, cookies=cookies, proxies=random.choice(proxies)).json()
        if 'errors' in response:
            print('Delaying for 30 seconds due to rate limitation')
            sleep(30)
            return scrapegroup(groupid, cursor)
        for asset in response["data"]:
            shirtidfile.write(str(asset["id"])+"\n")
        if(response["nextPageCursor"] != None):
            scrapegroup(groupid, response["nextPageCursor"])
    else:
        response = requests.get(f"https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor=&limit=50&sortOrder=Desc&sortType=Updated", headers=headers, cookies=cookies, proxies=random.choice(proxies)).json()
        if 'errors' in response:
            print('Delaying for 30 seconds due to rate limitation')
            sleep(30)
            return scrapegroup(groupid)
        for asset in response["data"]:
            shirtidfile.write(str(asset["id"])+"\n")
        if(response["nextPageCursor"] != None):
            scrapegroup(groupid, response["nextPageCursor"])
        

assetjsondata = {"items": []}
for i in range(0, len(frontpage["data"])):
    if frontpage["data"][i]["itemType"] == "Asset":
        assetjsondata["items"].append({ "id": int(frontpage["data"][i]["id"]), "itemType": "Asset", "key": "Asset_"+str(frontpage["data"][i]["id"]), "thumbnailType": "Asset" })
threads = []
assetdata = requests.post("https://catalog.roblox.com/v1/catalog/items/details", json=assetjsondata, cookies=cookies, headers=headers).json()
for asset in assetdata["data"]:
    shirtidfile.write(str(asset["id"])+"\n")
    if asset["creatorType"] == "Group":
        t = Thread(target=scrapegroup, args=(asset["creatorTargetId"],)).start()
        threads.append(t)
        sleep(5)
for i in range(0, len(threads)):
    threads[i].join()
print("Finished and got " + str(len(shirtidfile.readlines())) + " shirts ids!")