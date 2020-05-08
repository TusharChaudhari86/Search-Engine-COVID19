import requests
import json


def makeApiRequestForCountry(country_name):
    url = "https://covid-193.p.rapidapi.com/statistics"
    querystring = {"country": country_name}
    headers = {
        'x-rapidapi-host': "covid-193.p.rapidapi.com",
        'x-rapidapi-key': "f9db7f2f74msh7e26619cf815f89p129535jsn0a6ccf39741a"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    # print(response.text)
    js = json.loads(response.text)
    print("******", js)
    result = js.get('response')[0]
    print(result.get('cases'))
    print("*" * 20)
    return result.get('cases'), result.get('deaths'), result.get('tests')


class Api:
    def __init__(self):
        pass

    def makeApiRequestForCountry(self, country_name):
        url = "https://covid-193.p.rapidapi.com/statistics"
        querystring = {"country": country_name}
        headers = {
            'x-rapidapi-host': "covid-193.p.rapidapi.com",
            'x-rapidapi-key': "f9db7f2f74msh7e26619cf815f89p129535jsn0a6ccf39741a"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        # print(response.text)
        js = json.loads(response.text)
        print("******", js)
        result = js.get('response')[0]
        print(result.get('cases'))
        print("*" * 20)
        return result.get('cases') , result.get('deaths'),result.get('tests')

#
#     def makeApiRequestForIndianStates(self):
#         url = "https://covid19-data.p.rapidapi.com/india"
#         headers = {
#             'x-rapidapi-host': "covid-193.p.rapidapi.com",
#             'x-rapidapi-key': "f9db7f2f74msh7e26619cf815f89p129535jsn0a6ccf39741a"
#         }
#         response = requests.request("GET", url, headers=headers)
#         # print(response.text)
#         js = json.loads(response.text)
#         print("******", js)
#         #result = js.get('list')
#         return js
#
#
#     def makeApiWorldwide(self):
#         url = "https://covid-19-statistics.p.rapidapi.com/reports/total"
#         headers = {
#             'x-rapidapi-host': "covid-193.p.rapidapi.com",
#             'x-rapidapi-key': "f9db7f2f74msh7e26619cf815f89p129535jsn0a6ccf39741a"
#         }
#         response = requests.request("GET", url, headers=headers)
#         # print(response.text)
#         js = json.loads(response.text)
#         print("******", js)
#         result = js.get('data')
#
#         return result
#
