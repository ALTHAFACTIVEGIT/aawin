#!/opt/virtualenv/aavin_admin/bin/python3
import datetime
import pytz
from collections import defaultdict
indian=pytz.timezone('Asia/Kolkata')
from main.models import *
fproducts = ['CU150', 'CURD500', 'BMILK', 'LSI']
mproducts = ['TM500', 'SM500', 'SM250', 'FCM500', 'FCM1000']
cbe_zones = ['NORTH', 'EAST', 'WEST', 'SOUTH', 'CURD Zone', 'POLLACHI', 'MTP']

import requests
payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey' : '622de6e4-91da-4e3b-9fb1-2262df7baff8', 'SenderID' : 'AAVINC', 'fl':'0', 'gwid':'2', 'sid':'AAVINC'}
headers = {}
url     = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'

# send to
payload['msisdn'] = '919003832999,919345702235'

def run():
	date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
	for session in Session.objects.all():
	    for business in Business.objects.filter():
        	if SaleGroup.objects.filter(date=date, business=business, session=session).count() > 1:
	            print(business.code)
        	    for sg in  SaleGroup.objects.filter(date=date, business__code=business.code, session=session):
                        payload['msg'] = "Booth no:{} has a double entry! Shift:{}, Delivery Date:{}, Total Cost:{}, Ordered On:{}, Ordered By:{}".format(business.code, session.name, sg.date, sg.total_cost, sg.time_created.astimezone(indian).strftime("%Y-%m-%d %I:%M %P"), sg.ordered_by.first_name)
                        payload['msisdn'] += ',91' + sg.ordered_by.userprofile.mobile 
                        res = requests.post(url, data=payload, headers=headers)
                        for sale in sg.sale_set.all():
                            print("\tsale id:{} cost:{}\t({}:{})".format(sale.id, sale.cost, sale.product.code, sale.count ))
