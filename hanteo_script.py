import requests
import json
from jq import jq
from datetime import date
from datetime import timedelta
from datetime import timezone
from datetime import datetime
from http import HTTPStatus
from requests.exceptions import HTTPError

######################################################## THE GET REQUEST ##############################################################################

api_url = "https://siteexample.com/wp-json/wc/v3/orders?consumer_key=ck_xxx&consumer_secret=cs_xxx&status=completed&per_page=100"

# Today's date
today = date.today()
print("Today's date:", today)

# Yesterday date
yesterday = today - timedelta(days = 1)
print("Yesterday was: ", yesterday)

# Concatenate &modified_after=yesterdayT00%3A00%3A00&modified_before=todayT00%3A00%3A00
modified_after = "&modified_after=" + str(yesterday) + "T00%3A00%3A00"
modified_before = "&modified_before=" + str(today) + "T00%3A00%3A00"

api_url = api_url + modified_after + modified_before

retries = 3
retry_codes = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]

print(api_url)

for n in range(retries):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        
        break

    except HTTPError as exc:
        code = exc.response.status_code
        
        if code in retry_codes:
            # retry after n seconds
            time.sleep(n)
            continue

        raise

# response.iter_content to download the content in chunks, in case the server is low on ram
# The "with open" function closes the file automatically so no need to use the close() method
if response.status_code == 200:
    with open("1_response_get.json", "wb") as f_out:
        for chunk in response.iter_content(chunk_size=8192): 
            f_out.write(chunk)
            f_out.flush()


######################################################## THE JQ FILTER FOR THE JSON ##############################################################################

with open('1_response_get.json', 'r') as f:
    data = f.read()
    response2 = jq("[.[] | .line_items | map({name, product_id, quantity, sku, ean})]").transform(text=data, multiple_output=True, text_output=True)
    with open("2_filter_jq_get.json", "w") as f_out:
        f_out.write(response2)
        f_out.flush()


######################################################## HANTEO AUTHORIZATION POST REQUEST ########################################################################

with open('3_hanteo_token.json', 'r') as f_out:
    hanteo_token_access = f_out.read()


######################################################## HANTEO SEND SALES DATA POST REQUEST ##############################################################################

hanteo_sales_url = "https://test.example.com/v4/collect/realtimedata/ALBUM"

headers = {
    "Authorization": "Bearer " + hanteo_token_access,
    "Content-Type": "application/json; charset=utf-8",
}

# Our server timezone is GMT +00:00, so it's the same time as UTC time
unix_timestamp_utc = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())

# From UTC to KTC there's a difference of plus 9 hours(= 32400s)
unix_timestamp_korea = unix_timestamp_utc + 32400

print("UTC Unix Time Stamp: ", unix_timestamp_utc)
print("Korean Unix Time Stamp: ", unix_timestamp_korea)

# Opening JSON file
f = open('2_filter_jq_get.json')

# Returns JSON object as a dictionary
data = json.load(f)


######################################################## TODO: In the future, write response of post one by one inside a file to make a one single post call with all the data, instead of doing a call every time ##############################################################################

# Clearing post_data_hanteo.json file before writing inside
#open('5_post_data_hanteo.json', 'w').close()

# Initialize the file to be a JSON array
#with open("5_post_data_hanteo.json", "w") as f_out:
#    f_out.write("[")
#    f_out.flush()

# Iterating through the json list
#for item in data:
#    for nested in item:
#        data2 = {
#            "familyCode": "youFamilyCode",
#            "branchCode": "youBranchCode",
#            "barcode": nested["ean"],
#            "albumName": nested["name"],
#            "salesVolume": int(nested["quantity"]),
#            "realTime": int(unix_timestamp_korea),
#            "opVal": nested["sku"],
#        }
#        # With the "a" value, it appends the data instead of overwriting the file every time
#        with open("5_post_data_hanteo.json", "a") as f_out:
#                f_out.write("" + json.dumps(data2) + ",")
#                f_out.flush()

# Delete the last "," character and closing the array with "]"
#with open("5_post_data_hanteo.json", "rb+") as fh:
#    fh.seek(-1, 2)
#    fh.truncate() 
    
#with open("5_post_data_hanteo.json", "a") as f_out:
#    f_out.write("]")
#    f_out.flush()

#json_data = open('5_post_data_hanteo.json','rb').read()
#print("json data: ", json_data)


#################################################################################### IDK if it's possible, for now I make a request for every iteration ##########################################################################################################

# It need to return a JSon Array so it needs to be [{ //data in here }, {//data in here}, ... ]
for item in data:
    for nested in item:
        data2 = [
            {
                ### Here we write the data request to the server 
                "familyCode": "youFamilyCode",
                "branchCode": "youBranchCode",
                "albumName": nested["name"],
                "barcode": nested["ean"],
                "salesVolume": int(nested["quantity"]),
                "realTime": int(unix_timestamp_korea),
                "opVal": nested["sku"] + "_" + str(unix_timestamp_korea) + "_" + "KaidoItalia",
            }
        ]
        response4 = requests.post(hanteo_sales_url, headers=headers, json=data2)
        
with open("4_post_request_response_with_any_errors.json", "w") as f_out:
    f_out.write("\nStatus Code: " + str(response4.status_code))
    f_out.write("\n\nJSON Response: " + str(response4.json()))
    f_out.flush()

# Closing the 2_filter_jq_get.json file
f.close()

