# Reset route expiry time to reference expiry time
# Run by crontab every night at 11 PM
#!/opt/virtualenv/aavin_admin/bin/python3
import datetime
import pytz
from collections import defaultdict
indian=pytz.timezone('Asia/Kolkata')
import requests
payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey' : '622de6e4-91da-4e3b-9fb1-2262df7baff8', 'SenderID' : 'AAVINC', 'fl':'0', 'gwid':'2', 'sid':'AAVINC'}
headers = {}
url = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'

# send to
payload['msisdn'] = '919003832999'
now = datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %H:%M:%S")

from main.models import Route
import logging

def run():
    # routes_to_be_changed = ''
    # logging.basicConfig(filename='static/route.log', level=logging.INFO)
    for route in Route.objects.filter(is_temp_route=False):
        logging.info(route.name)
        route.order_expiry_time = route.reference_order_expiry_time
        route.save()
