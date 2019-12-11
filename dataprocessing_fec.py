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

################################
### INDEPENDENT EXPENDITURES ###
################################

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
        committee_type = item["committee"]["committee_type"]

        if payee in newdict.keys():
            if support_oppose == "S":
                newdict[payee]["S"] += amount
            else:
                newdict[payee]["O"] += amount
        else:
            newdict[payee] = {"committee_type": committee_type, "S": 0, "O": 0}
            if support_oppose == "S":
                newdict[payee]["S"] = amount
            else:
                newdict[payee]["O"] = amount

    return newdict

# uses a clean expenditure dictionary to create a csv file for the given presidential candidate
def writecsv(name, expendituresdict):
    f = open("data/" + name + ".csv", 'w')
    f.write("candidate_name,payee,amount,committee_type,support_oppose\n")

    for payee in expendituresdict.keys():
        support_amount = expendituresdict[payee]["S"]
        oppose_amount = expendituresdict[payee]["O"]
        committee_type = expendituresdict[payee]["committee_type"]

        if support_amount != 0:
            f.write("%s,%s,%s,%s,%s\n" % (name, payee, support_amount, committee_type, "S"))

        if oppose_amount != 0:
            f.write("%s,%s,%s,%s,%s\n" % (name, payee, oppose_amount, committee_type, "O"))

# the independent expenditures endpoint doesn't have data for all candidates, so these are all of the candidates and
# their IDs that it does have data for
candidates = [("biden", "P80000722"), ("booker", "P00009795"), ("buttigieg", "P00010298"), ("castro", "P00009092"),
              ("delaney", "P00006213"), ("sanders", "P60007168"), ("warren", "P00009621"), ("yang", "P00006486"),
              ("trump", "P80001571")]

# create a csv file for each candidate
# for candidate in candidates:
#     name = candidate[0]
#     fec_id = candidate[1]
#
#     messydict = getExpendituresSpecific(fec_id)
#     cleandict = makeExpDict(messydict)
#     writecsv(name, cleandict)
#
#     time.sleep(10) # wait a little to avoid hitting rate limit

#########################
### ITEMIZED RECEIPTS ###
#########################

# get 100 receipts reported by a committee, which is specified by the committee's FEC ID. sorted by amount (descending).
# returns the receipts as a dictionary
def getReceipts(committee_id, params={}):
    params["committee_id"] = committee_id
    params["per_page"] = 100
    params["api_key"] = api_key
    params["two_year_transaction_period"] = "2020"
    params["sort"] = "-contribution_receipt_amount"

    url = base_url + "/schedules/schedule_a/?" + urllib.parse.urlencode(params)
    result = safeGet(url)
    resultjson = json.loads(result.read())

    return resultjson

# gets 1000 contributions reported by the given committee and returns a list of the 10 dictionaries (100 contributions
# per dictionary). calls getReceipts 10 times
def makeContribsList(committee_id):
    dicts = []

    # page through results; fencepost
    d1 = getReceipts(committee_id)
    last_index = d1["pagination"]["last_indexes"]["last_index"]
    last_amount = d1["pagination"]["last_indexes"]["last_contribution_receipt_amount"]
    dicts.append(d1)
    for num in range(9):
        d = getReceipts(committee_id, params={"last_index": last_index, "last_contribution_receipt_amount": last_amount})
        last_index = d["pagination"]["last_indexes"]["last_index"]
        last_amount = d["pagination"]["last_indexes"]["last_contribution_receipt_amount"]
        dicts.append(d)

        time.sleep(2)

    return dicts

# write a csv file for the given candidate using a list of contribs dictionaries (from makeContribsList)
def writeContribsCSV(name, contribslist):
    f = open("data/" + name + ".csv", 'w')
    f.write("candidate_name,contributor_name,amount,entity_type\n")
    for cdict in contribslist:
        for item in cdict["results"]:
            contributor_name = item["contributor_name"].replace(",", "")
            amount = item["contribution_receipt_amount"]
            entity_type = item["entity_type_desc"]

            f.write("%s,%s,%s,%s\n" % (name, contributor_name, amount, entity_type))

    f.close()

# the FEC IDs of primary campaign committees for candidates (not all, since the FEC API is missing data for a few)
committees = [("bennet", "C00705186"), ("biden", "C00703975"), ("booker", "C00695510"), ("buttigieg", "C00697441"),
              ("castro", "C00693044"), ("delaney", "C00508416"), ("gabbard", "C00693713"), ("klobuchar", "C00696419"),
              ("sanders", "C00696948"), ("warren", "C00693234"), ("williamson", "C00696054"), ("yang", "C00659938"),
              ("trump", "C00580100"), ("weld", "C00700906"), ("walsh", "C00717033")]

# create a csv file for each candidate
for committee in committees:
    name = committee[0]
    fec_id = committee[1]

    dictlist = makeContribsList(fec_id)
    writeContribsCSV(name, dictlist)

    time.sleep(5)
