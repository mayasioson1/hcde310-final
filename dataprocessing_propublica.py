import api_keys
import urllib.parse, urllib.request, urllib.error, json, time

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

propublica_key = api_keys.propublica_key
base_url = "https://api.propublica.org/campaign-finance/v1/"

def safeGet(request):
    try:
        return urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print("The server couldn't fulfill the request.")
            print("Error code: %s" % e.code)
        elif hasattr(e, "reason"):
            print("We failed to reach a server.")
            print("Reason: " + e.reason)
        return None

# gets information about a candidate from the given cycle using their FEC ID and returns the result as a dictionary.
# default cycle is 2020
def getCandidate(fec_id, cycle = "2020"):
    url = base_url + cycle + "/candidates/" + fec_id + ".json"
    request = urllib.request.Request(url, headers={"X-API-Key": propublica_key})
    result = safeGet(request)
    resultjson = json.loads(result.read())

    return resultjson

# gets the 200 most recent independent expenditures that support or oppose candidates and returns them as a dictionary.
# default cycle is 2020
def getExpenditures(cycle = "2020"):
    url = base_url + cycle + "/president/independent_expenditures.json"
    request = urllib.request.Request(url, headers={"X-API-Key": propublica_key})
    result = safeGet(request)
    expendituresjson = json.loads(result.read())

    return expendituresjson

# gets the 200 most recent indepedent expenditures that support or oppose a specific candidate using their FEC ID and
# returns the result as a dictionary. setting the offset to multiples of 20 allows you to page through the results
def getExpendituresSpecific(fec_id, offset=0):
    params = {"offset": offset}
    url = base_url + "2020/candidates/" + fec_id + "/independent_expenditures.json?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"X-API-Key":propublica_key})
    result = safeGet(request)
    resultjson = json.loads(result.read())

    return resultjson

sanders = []
for n in range(0, 200, 20):
    print(n)
    result = getExpendituresSpecific("P60007168", n)
    sanders.append(result)
    time.sleep(30) # wait between calls to avoid hitting the rate limit

f = open("sanders.csv", 'w')
f.write("amount,payee,support_oppose\n")
for result in sanders:
    items = result["results"]
    for expenditure in items:
        amount = expenditure["amount"]
        payee = expenditure["payee"]
        support_oppose = expenditure["support_or_oppose"]

        f.write("%s,%s,%s\n" % (amount, payee, support_oppose))
f.close()

# sanders = getCandidate("P60007168")
# print(pretty(sanders))

# sanders0 = getExpendituresSpecific("P60007168")
# sanders20 = getExpendituresSpecific("P60007168", offset=20)
# print(pretty(sanders0))
# trump0 = getExpendituresSpecific("P80001571")

# create a dictionary of only the data that I need
# expenditures = getExpenditures()
# candidates = {}
# for transaction in expenditures["results"]:
#     amount = float(transaction["amount"])
#     name = transaction["candidate_name"].lower()
#     payee = transaction["payee"]
#     support_oppose = transaction["support_or_oppose"]
#
#     # [support, oppose]
#     if name in candidates.keys():
#         if payee in candidates[name].keys():
#             if support_oppose == "S":
#                 candidates[name][payee][0] += amount
#             else:
#                 candidates[name][payee][1] += amount
#         else:
#             if support_oppose == "S":
#                 candidates[name][payee] = [amount, 0]
#             else:
#                 candidates[name][payee] = [0, amount]
#     else:
#         if support_oppose == "S":
#             candidates[name] = {payee: [amount, 0]}
#         else:
#             candidates[name] = {payee: [0, amount]}

# some candidates have multiple entries; combine all of them
# alt_names_trump = ["donald j. trump", "donald j trump", " donald trump"]
# for name in alt_names_trump:
#     for payee in candidates[name].keys():
#         candidates["donald trump"][payee] = candidates[name][payee]
#     del candidates[name]
#
# for payee in candidates["joe r biden"]:
#     candidates["joseph biden"][payee] = candidates["joe r biden"][payee]
# del candidates["joe r biden"]

# write to a csv file
# f = open("expenditures.csv", 'w')
# f.write("candidate,amount,payee,support_oppose")
# for candidate in candidates.keys():
#     for payee in candidates[candidate].keys():
#         support_amount = candidates[candidate][payee][0]
#         oppose_amount = candidates[candidate][payee][1]
#
#         if support_amount != 0:
#             f.write("%s,%s,%s,%s\n" % (candidate, support_amount, payee, "S"))
#
#         if oppose_amount != 0:
#             f.write("%s,%s,%s,%s\n" % (candidate, oppose_amount, payee, "O"))