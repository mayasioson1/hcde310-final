import api_keys
import urllib.parse, urllib.request, urllib.error, json, time

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

api_key = api_keys.fec_key
base_url = "https://api.open.fec.gov/v1"

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

# gets 100 recent indepdendent expenditures that support/oppose a presidential candidate in the 2020 cycle, specified by
# their FEC ID. sorted in descending order by expenditure date. returns the expenditures as a dictionary
def getExpendituresSpecific(fec_id, params={}):
    params["candidate_office"] = "P"
    params["sort"] = "-expenditure_date"
    params["candidate_id"] = fec_id
    params["per_page"] = 100
    params["api_key"] = api_key
    params["cycle"] = "2020"

    url = base_url + "/schedules/schedule_e/?" + urllib.parse.urlencode(params)
    result = safeGet(url)
    resultjson = json.loads(result.read())

    return resultjson

# takes in an expenditure dictionary to filter information and create a new dictionary of total amounts
def makeExpDict(expendituresdict):
    newdict = {}
    for item in expendituresdict["results"]:
        payee = item["payee_name"].replace(",", "")
        amount = float(item["expenditure_amount"])
        support_oppose = item["support_oppose_indicator"]

        if payee in newdict.keys():
            if support_oppose == "S":
                newdict[payee][0] += amount
            else:
                newdict[payee][1] += amount
        else:
            if support_oppose == "S":
                newdict[payee] = [amount, 0]
            else:
                newdict[payee] = [0, amount]

    return newdict

# uses a clean expenditure dictionary to create a csv file for the given presidential candidate
def writecsv(name, expendituresdict):
    f = open(name + ".csv", 'w')
    f.write("payee,amount,support_oppose\n")

    for payee in expendituresdict.keys():
        support_amount = expendituresdict[payee][0]
        oppose_amount = expendituresdict[payee][1]

        if support_amount != 0:
            f.write("%s,%s,%s\n" % (payee, support_amount, "S"))

        if oppose_amount != 0:
            f.write("%s,%s,%s\n" % (payee, oppose_amount, "O"))

candidates = [("bennet", "P00011833"), ("biden", "P80000722"), ("booker", "P00009795"), ("buttigieg", "P00010298"),
            ("castro", "P00009092"), ("delaney", "P00006213"), ("gabbard", "P00009183"), ("klobuchar", "P80006117"),
            ("patrick", "P00014407"), ("sanders", "P60007168"), ("steyer", "P00012716"), ("warren", "P00009621"),
            ("williamson", "P00009910"), ("yang", "P00006486"), ("trump", "P80001571"), ("weld", "P00011239"),
            ("walsh", "P00013276")]

for candidate in candidates:
    name = candidate[0]
    id = candidate[1]

    messydict = getExpendituresSpecific(id)
    cleandict = makeExpDict(messydict)
    writecsv(name, cleandict)

    time.sleep(10) # wait a little to avoid hitting rate limit
