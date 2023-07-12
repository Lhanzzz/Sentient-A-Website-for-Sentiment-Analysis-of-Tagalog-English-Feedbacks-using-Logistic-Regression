import re
import json
import requests
import pandas as pd



url = "https://shopee.ph/S6U-s10u-Portable-Mini-LED-Bluetooth-Speaker-i.146669569.2258912700?sp_atk=828d3110-06e8-43bf-a2c9-02cee45c8e96&xptdk=828d3110-06e8-43bf-a2c9-02cee45c8e96"
b=0
insert = 0
error = 0
r = re.search(r"i\.(\d+)\.(\d+)", url)
shop_id, item_id = r[1], r[2]
ratings_url = "https://shopee.my/api/v4/item/get_ratings?filter=0&flag=0&itemid={item_id}&limit=40&offset={offset}&shopid={shop_id}&type=0"

print(ratings_url)
below3word = 0
offset = 0
d = {"username": [], "comment": []}
while True:
    data = requests.get(
        ratings_url.format(shop_id=shop_id, item_id=item_id, offset=offset)
    ).json()

    if data["data"]["ratings"] is not None:
       
        for i, rating in enumerate(data["data"]["ratings"], 1):
            val = len(rating["comment"].split())
            if rating["comment"] == "":
                b += 1
            else:
                if val > 3:
                    insert += 1 
                    d["username"].append(rating["author_username"])
                    d["comment"].append(rating["comment"])
                    print(rating["author_username"])
                    print(rating["comment"])
                    print("-" * 100)
                else:
                    below3word+=1
    else:
        print("No ratings data found for offset", offset)
        break

    if i % 20:
        break

    offset += 20
   
print(str(b)+"blank")
print(str(below3word)+"belowwords")
print(str(insert) +"Insert Data")
# print(str(error) +"Error")
df = pd.DataFrame(d)
print(df)
df.to_csv("data.csv", index=False)


   # if i == len(rating["comment"]) - 2:
        #    break
        # else:
        #     if rating["comment"] == "":
        #         b+=1
        #     else:
        #         insert+=1
        #         d["username"].append(rating["author_username"])
        #         d["comment"].append(rating["comment"])
        #         print(rating["author_username"])
        #         print(rating["comment"])
        #         print("-" * 100)
print(ratings_url)
print(shop_id,item_id)