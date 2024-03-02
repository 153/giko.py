from datetime import datetime, timedelta
import requests

with open("./data/polygonio.key", "r") as apikey:
    apikey = apikey.read().strip()

""" 
!stock <name>
!buy <name> <shares>
!sell <name> <shares>
!portfolio 

!convert <num> <one> <two>
"""

def cmd(player, msg):
    output = []
    msg = msg.split()
    commands = ["!convert", "!stock"]
    if msg[0] in commands:
        if msg[0] == "!convert":
            if len(msg) >= 4:
                output.append(convert(msg[1], msg[2], msg[3]))
            else:
                output.append("Invoke like !convert 100 USD EUR (use 3 letter currency codes)")
        if msg[0] == "!stock":
            if len(msg) >= 2:
                output.append(stocks(msg[1]))
            else:
                output.append("Please enter a valid stock ticker name, like !stock GOOG or !stock MRNA")
    return output

def convert(value=10, currency1="USD", currency2="EUR"):
    codes = ["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD",
             "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF",
             "BMD", "BND", "BOB", "BRL", "BSD", "BTN", "BWP", "BYN",
             "BZD", "CAD", "CDF", "CHF", "CLP", "CNY", "COP", "CRC",
             "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP",
             "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL",
             "GGP", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD",
             "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "IMP", "INR",
             "IQD", "IRR", "ISK", "JEP", "JMD", "JOD", "JPY", "KES",
             "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT",
             "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL",
             "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR",
             "MWK", "MXN", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK",
             "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR",
             "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
             "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SOS",
             "SRD", "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT",
             "TND", "TOP", "TRY", "TTD", "TVD", "TWD", "TZS", "UAH",
             "UGX", "USD", "UYU", "UZS", "VES", "VND", "VUV", "WST",
             "XAF", "XCD", "XDR", "XOF", "XPF", "YER", "ZAR", "ZMW",
             "ZWL"]
    
    try: currency1 = currency1.upper()[:3]
    except: currency1 = "USD"
    try: currency2 = currency2.upper()[:3]
    except: currency2 = "EUR"
    try: value = float(value)
    except: value = 1.0
    if currency1 not in codes: currency1 = "USD"
    if currency2 not in codes: currency2 = "EUR"
        
    url = "https://open.er-api.com/v6/latest/" + currency1
    r = requests.get(url)
    table = r.json()
    convert = round(table["rates"][currency2] * value, 2)
    return f"{value} {currency1} is roughly {convert} {currency2}"

def stocks(corp):
    corp = corp.upper()[:5]
    stock = {}
    yday = datetime.now() - timedelta(2)
    yday = datetime.strftime(yday, "%Y-%m-%d")
    url = "https://api.polygon.io/v2/aggs/ticker/"
    url += corp + "/prev"
    url += "?apiKey=" + apikey
    print(url)
    
    data = requests.get(url).json()
    if not len(data):
        print(data)
        return "Error"

    print(data)

    data = data["results"][0]
    percent = (float(data["c"]) - float(data["o"])) / float(data["o"]) * 100
    percent = round(percent, 2)
    if percent > 0:
        percent = f"+{str(percent)}"
    return f"{yday} {corp} :: ${data['c']} / {percent}%"
    
print("Wealth plugin added")
