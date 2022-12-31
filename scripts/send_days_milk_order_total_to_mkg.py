#!/opt/virtualenv/aavin_admin/bin/python3
import datetime
import pytz
from collections import defaultdict
indian=pytz.timezone('Asia/Kolkata')
from main.models import *
fproducts = ['CU150', 'CURD500', 'BMILK', 'LSI']
mproducts = ['TM500', 'SM500', 'SM250', 'FCM500', 'FCM1000']
import requests
payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey' : '622de6e4-91da-4e3b-9fb1-2262df7baff8', 'SenderID' : 'AAVINC', 'fl':'0', 'gwid':'2', 'sid':'AAVINC'}
headers = {}
url     = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'


def run():
	dates = [datetime.datetime.now().astimezone(indian).strftime('%Y-%m-%d')]
	check_time = datetime.datetime.now().astimezone(indian).strftime('%H:%M %p')
	data = defaultdict(dict)
	# print("{},\t,{},{},{},{},{},{}".format('date', 'Cash Sale Morning', 'Cash Sale Evening', 'Cash Sale Total', 'Card Sale Morning', 'Card Sale Evening', 'Card Sale Evening', 'Days Total Sale'))
	for date in dates:
	    data['total_cash_sale'] = 0
	    data['total_card_sale'] = 0
	    data['days_total_sale'] = 0
    
	    for session in Session.objects.all():
        	data[session.name]['cash_sale'] = 0
	        data[session.name]['card_sale'] = 0
        	data[session.name]['total_sale'] = 0
            
	        for sg in SaleGroup.objects.filter(date=date, session=session):
        	    for sale in sg.sale_set.all():
                	if sale.product.code in mproducts:
	                    # print(sale.product.code)
        	            qty_in_lits = (sale.count * float(sale.product.quantity))/1000
                	    data[session.name]['cash_sale'] += qty_in_lits
	        for icsg in ICustomerSaleGroup.objects.filter(date='2020-05-01', session=session):
        	    for sale in icsg.icustomersale_set.all():
                	if sale.product.code in mproducts:
	                    # print(sale.product.code)
        	            qty_in_lits = (sale.count * float(sale.product.quantity))/1000
                	    data[session.name]['card_sale'] += qty_in_lits

	            data[session.name]['total_sale'] = data[session.name]['cash_sale'] + data[session.name]['card_sale']
            
    
	data['total_cash_sale'] = data['Morning']['cash_sale'] + data['Evening']['cash_sale']
	data['total_card_sale'] = data['Morning']['card_sale'] + data['Evening']['card_sale']
	data['days_total_sale'] = data['total_cash_sale'] + data['days_total_sale'] 
	print("{},\t,{},{},{},{},{},{}".format(date, data['Morning']['cash_sale'], data['Evening']['cash_sale'], data['total_cash_sale'], data['Morning']['card_sale'],data['Evening']['card_sale'], data['total_card_sale'],  data['days_total_sale']))
	payload['msg'] = "For {}, as of {}, {} lits of Milk has been ordered by/for agents (Mor-Cash {} Lits; Eve-Cash {} Lits). And {} Lits by card customers)".format(date, check_time, data['total_cash_sale'], data['Morning']['cash_sale'], data['Evening']['cash_sale'], data['total_card_sale'])

	payload['msisdn'] = '919043740499,919003832999'
	print(payload['msg'])
	print(payload)
	res = requests.post(url, data=payload, headers=headers)
    
    
