#!/opt/virtualenv/aavin_admin/bin/python3
import re
import requests
import pytz
indian=pytz.timezone('Asia/Kolkata')
import time
from report.models import *
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime, timedelta

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    from io import BytesIO

import requests
payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey' : '622de6e4-91da-4e3b-9fb1-2262df7baff8', 'SenderID' : 'AAVINC', 'fl':'0', 'gwid':'2', 'sid':'AAVINC'}
headers = {}
url = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'

# send to
payload['msisdn'] = '919003832999'

# dates = ['2020-06-13']


# Script to upload Agent data from main.models into report.model.DailySessionllyBusinessllySale
# this uploads only agent data. icustomer data uploders is below

def upload_daily_sale_for_agent_per_date(date, session):
    # loop thru salegroup, sales for given date, given session
    for sg in SaleGroup.objects.filter(date=date, session=session):

        # Find out the union
        print(sg.date)
        union = 'COIMBATORE Union'
        if sg.business.zone.name == 'NILGIRIS':
            union = 'NILGIRIS Union'
        elif sg.business.zone.name == 'TIRUPPUR':
            union = 'TIRUPPUR Union'
        elif sg.business.zone.name == 'CHENNAI Aavin':
            union = 'CHENNAI Aavin'
        else:
            union = 'COIMBATORE Union'

        # get route via route business map
        #         route=RouteBusinessMap.objects.filter(business=sg.business, route__session=sg.session)[0].route

        # Create an User table entry for this Agent
        dsbs_inpkts, created = DailySessionllyBusinessllySale.objects.update_or_create(
            delivery_date=sg.date,
            session=sg.session,
            business=sg.business,
            route=sg.route,
            zone=sg.zone,
            business_type=sg.business.business_type,
            union=union,
            sold_to='Agent',
            defaults={
                'created_by': User.objects.get(username='kutobot'),
                'modified_by': User.objects.get(username='kutobot'),
                'total_cost': sg.total_cost,
            }

        )
        if created:
            print("\tRow Created: {}\t{}\t{}".format(dsbs_inpkts.delivery_date, dsbs_inpkts.session,
                                                     dsbs_inpkts.business.code))
        else:
            print("\tRow Exists: {}\t{}\t{}".format(dsbs_inpkts.delivery_date, dsbs_inpkts.session,
                                                    dsbs_inpkts.business.code))

        # Now loop thru sales for that salegroup
        for sale in sg.sale_set.all():
            print("\t", sale)
            # here total litre changed to decimal because one day error occur cannor add float into decimal I don't know where the sale.count converted as float.
            dsbs_inpkts.total_litre = Decimal(dsbs_inpkts.total_litre)
            if sale.product.code == 'TM500':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.tm500_pkt = sale.count
                dsbs_inpkts.tm500_litre = sale_litre
                dsbs_inpkts.tm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.tm500_cost = sale.cost
                dsbs_inpkts.tm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre


            elif sale.product.code == 'SM250':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.std250_pkt = sale.count
                dsbs_inpkts.std250_litre = sale_litre
                dsbs_inpkts.sm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.std250_cost = sale.cost
                dsbs_inpkts.sm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre

            elif sale.product.code == 'SM500':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.std500_pkt = sale.count
                dsbs_inpkts.sm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.std500_litre = sale_litre
                dsbs_inpkts.std500_cost = sale.cost
                dsbs_inpkts.sm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre

            elif sale.product.code == 'FCM500':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.fcm500_pkt = sale.count
                dsbs_inpkts.fcm500_litre = sale_litre
                dsbs_inpkts.fcm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.fcm500_cost = sale.cost
                dsbs_inpkts.fcm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre

            elif sale.product.code == 'FCM1000':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.fcm1000_pkt = sale.count
                dsbs_inpkts.fcm1000_litre = sale_litre
                dsbs_inpkts.fcm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.fcm1000_cost = sale.cost
                dsbs_inpkts.fcm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre

            elif sale.product.code == 'TMT500':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.tea500_pkt = sale.count
                dsbs_inpkts.tea500_litre = sale_litre
                dsbs_inpkts.tea_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.tea500_cost = sale.cost
                dsbs_inpkts.tea_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre

            elif sale.product.code == 'TMT1000':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.tea1000_pkt = sale.count
                dsbs_inpkts.tea1000_litre = sale_litre
                dsbs_inpkts.tea_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.tea1000_cost = sale.cost
                dsbs_inpkts.tea_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre
    

            elif sale.product.code == 'TNCAN':
                sale_litre = Decimal(sale.count)
                dsbs_inpkts.tmcan = sale.count / 40
                dsbs_inpkts.tmcan_litre = sale_litre
                dsbs_inpkts.tm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.tmcan_cost = sale.cost
                dsbs_inpkts.tm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre

            elif sale.product.code == 'SMCAN':
                sale_litre = Decimal(sale.count)
                dsbs_inpkts.smcan = sale.count / 40
                dsbs_inpkts.smcan_litre = sale_litre
                dsbs_inpkts.sm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.smcan_cost = sale.cost
                dsbs_inpkts.sm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre

            elif sale.product.code == 'FCMCAN':
                sale_litre = Decimal(sale.count)
                dsbs_inpkts.fcmcan = sale.count / 40
                dsbs_inpkts.fcmcan_litre = sale_litre
                dsbs_inpkts.fcm_litre += sale_litre
                dsbs_inpkts.milk_litre += sale_litre
                dsbs_inpkts.fcmcan_cost = sale.cost
                dsbs_inpkts.fcm_cost += sale.cost
                dsbs_inpkts.milk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre


            elif sale.product.code == 'CURD500':
                sale_kgs = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.curd500_pkt = sale.count
                dsbs_inpkts.curd500_kgs = sale_kgs
                dsbs_inpkts.curd500_cost = sale.cost
                dsbs_inpkts.curd_kgs += sale_kgs
                dsbs_inpkts.curd_cost += sale.cost
                dsbs_inpkts.total_litre += sale_kgs
                dsbs_inpkts.fermented_products_litre += sale_kgs
                dsbs_inpkts.fermented_products_cost += sale.cost

            elif sale.product.code == 'CURD5000':
                sale_kgs = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.curd5000_pkt = sale.count
                dsbs_inpkts.curd5000_kgs = sale_kgs
                dsbs_inpkts.curd5000_cost = sale.cost
                dsbs_inpkts.curd_kgs += sale_kgs
                dsbs_inpkts.curd_cost += sale.cost
                dsbs_inpkts.total_litre += sale_kgs
                dsbs_inpkts.fermented_products_litre += sale_kgs
                dsbs_inpkts.fermented_products_cost += sale.cost    

            elif sale.product.code == 'CU150':
                sale_kgs = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.curd150_pkt = sale.count
                dsbs_inpkts.curd150_kgs = sale_kgs
                dsbs_inpkts.curd150_cost = sale.cost
                dsbs_inpkts.curd_kgs += sale_kgs
                dsbs_inpkts.curd_cost += sale.cost
                dsbs_inpkts.total_litre += sale_kgs
                dsbs_inpkts.fermented_products_litre += sale_kgs
                dsbs_inpkts.fermented_products_cost += sale.cost

            elif sale.product.code == 'CPCU':
                sale_kgs = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.cupcurd_box = sale.count / 12
                dsbs_inpkts.cupcurd_count = sale.count
                dsbs_inpkts.cupcurd_kgs = sale_kgs
                dsbs_inpkts.cupcurd_cost = sale.cost
                dsbs_inpkts.curd_kgs += sale_kgs
                dsbs_inpkts.curd_cost += sale.cost
                dsbs_inpkts.total_litre += sale_kgs
                dsbs_inpkts.fermented_products_litre += sale_kgs
                dsbs_inpkts.fermented_products_cost += sale.cost

            elif sale.product.code == 'CC!KG':
                sale_kgs = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.curd_bucket = sale.count
                dsbs_inpkts.curd_bucket_kgs = sale_kgs
                dsbs_inpkts.curd_bucket_cost = sale.cost
                dsbs_inpkts.curd_kgs += sale_kgs
                dsbs_inpkts.curd_cost += sale.cost
                dsbs_inpkts.total_litre += sale_kgs
                dsbs_inpkts.fermented_products_litre += sale_kgs
                dsbs_inpkts.fermented_products_cost += sale.cost

            elif sale.product.code == 'LSI':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.lassi200_pkt = sale.count
                dsbs_inpkts.lassi200_kgs = sale_litre
                dsbs_inpkts.lassi200_cost = sale.cost
                dsbs_inpkts.lassi_litre += sale_litre
                dsbs_inpkts.lassi_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre
                dsbs_inpkts.fermented_products_litre += sale_litre
                dsbs_inpkts.fermented_products_cost += sale.cost


            elif sale.product.code == 'BMILK':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.buttermilk200_pkt = sale.count
                dsbs_inpkts.buttermilk200_litre = sale_litre
                dsbs_inpkts.buttermilk200_cost = sale.cost
                dsbs_inpkts.buttermilk_litre += sale_litre
                dsbs_inpkts.buttermilk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre
                dsbs_inpkts.fermented_products_litre += sale_litre
                dsbs_inpkts.fermented_products_cost += sale.cost


            elif sale.product.code == 'BMJar':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.bm_jar200_pkt = sale.count
                dsbs_inpkts.bm_jar200_litre = sale_litre
                dsbs_inpkts.bm_jar200_cost = sale.cost
                dsbs_inpkts.buttermilk_litre += sale_litre
                dsbs_inpkts.buttermilk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre
                dsbs_inpkts.fermented_products_litre += sale_litre
                dsbs_inpkts.fermented_products_cost += sale.cost


            elif sale.product.code == 'BMJF':
                sale_litre = (Decimal(sale.count) * sale.product.quantity) / 1000
                dsbs_inpkts.bmjf200_pkt = sale.count
                dsbs_inpkts.bmjf200_litre = sale_litre
                dsbs_inpkts.bmjf200_cost = sale.cost
                dsbs_inpkts.buttermilk_litre += sale_litre
                dsbs_inpkts.buttermilk_cost += sale.cost
                dsbs_inpkts.total_litre += sale_litre
                dsbs_inpkts.fermented_products_litre += sale_litre
                dsbs_inpkts.fermented_products_cost += sale.cost

        dsbs_inpkts.save()

# Script to upload ICustomer data from main.models into report.model.DailySessionllyBusinessllySale
# this uploads only icustomer data. agent data uploders is above
def upload_daily_sale_for_icustomer_per_date(date, session):
    requested_month = datetime.strptime(date, '%Y-%m-%d').month
    requested_year = datetime.strptime(date, '%Y-%m-%d').year

    for route in Route.objects.filter(session=session):
        print('Upload started for route: {}'.format(route.name))
        route_business_ids = list(RouteBusinessMap.objects.filter(route=route).values_list('business__id', flat=True))
        for business_id in route_business_ids:
            business = Business.objects.get(id=business_id)
            union = 'COIMBATORE Union'
            if business.zone.name == 'NILGIRIS':
                union = 'NILGIRIS Union'
            elif business.zone.name == 'TIRUPPUR':
                union = 'TIRUPPUR Union'
            elif business.zone.name == 'CHENNAI Aavin':
                union = 'CHENNAI Aavin'
            else:
                union = 'COIMBATORE Union'

            # get all icustomer sale objects for business, for the month, year
            icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__business=business,
                                                              icustomer_sale_group__date__month=requested_month,
                                                              icustomer_sale_group__date__year=requested_year,
                                                              icustomer_sale_group__session=session)
            if icustomer_sale_obj.count() > 0:
                dsbs_inpkts, created = DailySessionllyBusinessllySale.objects.update_or_create(
                    delivery_date=date,
                    session=session,
                    business=business,
                    zone=business.zone,
                    business_type=business.business_type,
                    union=union,
                    route=route,
                    sold_to='ICustomer',
                    defaults={
                        'created_by': User.objects.get(username='kutobot'),
                        'modified_by': User.objects.get(username='kutobot'),
                        'total_cost': icustomer_sale_obj.aggregate(Sum('cost'))['cost__sum'],

                    }

                )
                if created:
                    print("\tRow Created: {}\t{}\t{}".format(dsbs_inpkts.delivery_date, dsbs_inpkts.session,
                                                             dsbs_inpkts.business.code))
                else:
                    print("\tRow Exists: {}\t{}\t{}".format(dsbs_inpkts.delivery_date, dsbs_inpkts.session,
                                                            dsbs_inpkts.business.code))

                TM500_sale_obj = icustomer_sale_obj.filter(product__code='TM500')
                if not TM500_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.tm500_pkt = TM500_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.tm500_pkt) * Product.objects.get(code='TM500').quantity) / 1000
                    dsbs_inpkts.tm500_litre = sale_litre
                    dsbs_inpkts.tm500_cost = TM500_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.tm_litre += sale_litre
                    dsbs_inpkts.tm_cost += TM500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += TM500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                SM250_sale_obj = icustomer_sale_obj.filter(product__code='SM250')
                if not SM250_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.std250_pkt = SM250_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.std250_pkt) * Product.objects.get(code='SM250').quantity) / 1000
                    dsbs_inpkts.std250_litre = sale_litre
                    dsbs_inpkts.std250_cost = SM250_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.sm_litre += sale_litre
                    dsbs_inpkts.sm_cost += SM250_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += SM250_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                SM500_sale_obj = icustomer_sale_obj.filter(product__code='SM500')
                if not SM500_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.std500_pkt = SM500_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.std500_pkt) * Product.objects.get(code='SM500').quantity) / 1000
                    dsbs_inpkts.std500_litre = sale_litre
                    dsbs_inpkts.std500_cost = SM500_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.sm_litre += sale_litre
                    dsbs_inpkts.sm_cost += SM500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += SM500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                FCM500_sale_obj = icustomer_sale_obj.filter(product__code='FCM500')
                if not FCM500_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.fcm500_pkt = FCM500_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.fcm500_pkt) * Product.objects.get(code='FCM500').quantity) / 1000
                    dsbs_inpkts.fcm500_litre = sale_litre
                    dsbs_inpkts.fcm500_cost = FCM500_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.fcm_litre += sale_litre
                    dsbs_inpkts.fcm_cost += FCM500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += FCM500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                FCM1000_sale_obj = icustomer_sale_obj.filter(product__code='FCM1000')
                if not FCM1000_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.fcm1000_pkt = FCM1000_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.fcm1000_pkt) * Product.objects.get(
                        code='FCM1000').quantity) / 1000
                    dsbs_inpkts.fcm1000_litre = sale_litre
                    dsbs_inpkts.fcm1000_cost = FCM1000_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.fcm_litre += sale_litre
                    dsbs_inpkts.fcm_cost += FCM1000_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += FCM1000_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                TMT500_sale_obj = icustomer_sale_obj.filter(product__code='Tea500')
                if not TMT500_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.tea500_pkt = TMT500_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.tea500_pkt) * Product.objects.get(code='Tea500').quantity) / 1000
                    dsbs_inpkts.tea500_litre = sale_litre
                    dsbs_inpkts.tea500_cost = TMT500_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.tea_litre += sale_litre
                    dsbs_inpkts.tea_cost += TMT500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += TMT500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                TMT1000_sale_obj = icustomer_sale_obj.filter(product__code='Tea1000')
                if not TMT1000_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.tea1000_pkt = TMT1000_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.tea1000_pkt) * Product.objects.get(
                        code='Tea1000').quantity) / 1000
                    dsbs_inpkts.tea1000_litre = sale_litre
                    dsbs_inpkts.tea1000_cost = TMT1000_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.tea_litre += sale_litre
                    dsbs_inpkts.tea_cost += TMT1000_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += TMT1000_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                TNCAN_sale_obj = icustomer_sale_obj.filter(product__code='TNCAN')
                if not TNCAN_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    sale_litre = TNCAN_sale_obj.aggregate(Sum('count'))['count__sum']
                    dsbs_inpkts.tmcan = TNCAN_sale_obj.aggregate(Sum('count'))['count__sum'] / 40
                    dsbs_inpkts.tmcan_litre = sale_litre
                    dsbs_inpkts.tmcan_cost = TNCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.tm_litre += sale_litre
                    dsbs_inpkts.tm_cost += TNCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += TNCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                SMCAN_sale_obj = icustomer_sale_obj.filter(product__code='SMCAN')
                if not SMCAN_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    sale_litre = SMCAN_sale_obj.aggregate(Sum('count'))['count__sum']
                    dsbs_inpkts.smcan = SMCAN_sale_obj.aggregate(Sum('count'))['count__sum'] / 40
                    dsbs_inpkts.smcan_litre = sale_litre
                    dsbs_inpkts.smcan_cost = SMCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.sm_litre += sale_litre
                    dsbs_inpkts.sm_cost += SMCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += SMCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                FCMCAN_sale_obj = icustomer_sale_obj.filter(product__code='FCMCAN')
                if not FCMCAN_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    sale_litre = FCMCAN_sale_obj.aggregate(Sum('count'))['count__sum']
                    dsbs_inpkts.fcmcan = FCMCAN_sale_obj.aggregate(Sum('count'))['count__sum'] / 40
                    dsbs_inpkts.fcmcan_litre = sale_litre
                    dsbs_inpkts.fcmcan_cost = FCMCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.fcm_litre += sale_litre
                    dsbs_inpkts.fcm_cost += FCMCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_cost += FCMCAN_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.milk_litre += sale_litre
                    dsbs_inpkts.total_litre += sale_litre

                CURD500_sale_obj = icustomer_sale_obj.filter(product__code='CURD500')
                if not CURD500_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.curd500_pkt = CURD500_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_kgs = (Decimal(dsbs_inpkts.curd500_pkt) * Product.objects.get(code='CURD500').quantity) / 1000
                    dsbs_inpkts.curd500_kgs = sale_kgs
                    dsbs_inpkts.curd500_cost = CURD500_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.curd_kgs += sale_kgs
                    dsbs_inpkts.curd_cost += CURD500_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_kgs
                    dsbs_inpkts.fermented_products_litre += sale_kgs
                    dsbs_inpkts.fermented_products_cost += CURD500_sale_obj.aggregate(Sum('cost'))['cost__sum']

                CURD5000_sale_obj = icustomer_sale_obj.filter(product__code='CURD5000')
                if not CURD5000_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.curd5000_pkt = CURD5000_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_kgs = (Decimal(dsbs_inpkts.curd5000_pkt) * Product.objects.get(code='CURD5000').quantity) / 1000
                    dsbs_inpkts.curd5000_kgs = sale_kgs
                    dsbs_inpkts.curd5000_cost = CURD5000_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.curd_kgs += sale_kgs
                    dsbs_inpkts.curd_cost += CURD5000_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_kgs
                    dsbs_inpkts.fermented_products_litre += sale_kgs
                    dsbs_inpkts.fermented_products_cost += CURD5000_sale_obj.aggregate(Sum('cost'))['cost__sum']    

                CU150_sale_obj = icustomer_sale_obj.filter(product__code='CU150')
                if not CU150_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.curd150_pkt = CU150_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_kgs = (Decimal(dsbs_inpkts.curd150_pkt) * Product.objects.get(code='CU150').quantity) / 1000
                    dsbs_inpkts.curd150_kgs = sale_kgs
                    dsbs_inpkts.curd150_cost = CU150_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.curd_kgs += sale_kgs
                    dsbs_inpkts.curd_cost += CU150_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_kgs
                    dsbs_inpkts.fermented_products_litre += sale_kgs
                    dsbs_inpkts.fermented_products_cost += CU150_sale_obj.aggregate(Sum('cost'))['cost__sum']

                CPCU_sale_obj = icustomer_sale_obj.filter(product__code='CPCU')
                if not CPCU_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.cupcurd = CPCU_sale_obj.aggregate(Sum('count'))['count__sum'] / 12
                    sale_kgs = (Decimal(dsbs_inpkts.cupcurd_count) * Product.objects.get(code='CPCU').quantity) / 1000
                    dsbs_inpkts.cupcurd_count = CPCU_sale_obj.aggregate(Sum('count'))['count__sum']
                    dsbs_inpkts.cupcurd_kgs = sale_kgs
                    dsbs_inpkts.cupcurd_cost = CPCU_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.curd_kgs += sale_kgs
                    dsbs_inpkts.curd_cost += CPCU_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_kgs
                    dsbs_inpkts.fermented_products_litre += sale_kgs
                    dsbs_inpkts.fermented_products_cost += CPCU_sale_obj.aggregate(Sum('cost'))['cost__sum']

                CCKG_sale_obj = icustomer_sale_obj.filter(product__code='CC!KG')
                if not CCKG_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.curd_bucket = CCKG_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_kgs = (Decimal(dsbs_inpkts.curd_bucket) * Product.objects.get(code='CC!KG').quantity) / 1000
                    dsbs_inpkts.curd_bucket_kgs = sale_kgs
                    dsbs_inpkts.curd_bucket_cost = CCKG_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.curd_kgs += sale_kgs
                    dsbs_inpkts.curd_cost += CCKG_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_kgs
                    dsbs_inpkts.fermented_products_litre += sale_kgs
                    dsbs_inpkts.fermented_products_cost += CCKG_sale_obj.aggregate(Sum('cost'))['cost__sum']

                LSI_sale_obj = icustomer_sale_obj.filter(product__code='LSI')
                if not LSI_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.lassi200_pkt = LSI_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.lassi200_pkt) * Product.objects.get(code='LSI').quantity) / 1000
                    dsbs_inpkts.lassi200_kgs = sale_litre
                    dsbs_inpkts.lassi200_cost = LSI_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.lassi_litre += sale_litre
                    dsbs_inpkts.lassi_cost += LSI_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_litre
                    dsbs_inpkts.fermented_products_litre += sale_litre
                    dsbs_inpkts.fermented_products_cost += LSI_sale_obj.aggregate(Sum('cost'))['cost__sum']

                BMILK_sale_obj = icustomer_sale_obj.filter(product__code='BMILK')
                if not BMILK_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.buttermilk200_pkt = BMILK_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.buttermilk200_pkt) * Product.objects.get(
                        code='BMILK').quantity) / 1000
                    dsbs_inpkts.buttermilk200_litre = sale_litre
                    dsbs_inpkts.buttermilk200_cost = BMILK_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.buttermilk_litre += sale_litre
                    dsbs_inpkts.buttermilk_cost += BMILK_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_litre
                    dsbs_inpkts.fermented_products_litre += sale_litre
                    dsbs_inpkts.fermented_products_cost += BMILK_sale_obj.aggregate(Sum('cost'))['cost__sum']


                BMILK_jar_sale_obj = icustomer_sale_obj.filter(product__code='BMJar')
                if not BMILK_jar_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.bm_jar200_pkt = BMILK_jar_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.bm_jar200_pkt) * Product.objects.get(
                        code='BMJar').quantity) / 1000
                    dsbs_inpkts.bm_jar200_litre = sale_litre
                    dsbs_inpkts.bm_jar200_cost = BMILK_jar_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.buttermilk_litre += sale_litre
                    dsbs_inpkts.buttermilk_cost += BMILK_jar_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_litre
                    dsbs_inpkts.fermented_products_litre += sale_litre
                    dsbs_inpkts.fermented_products_cost += BMILK_jar_sale_obj.aggregate(Sum('cost'))['cost__sum']


                BMJF_sale_obj = icustomer_sale_obj.filter(product__code='BMJF')
                if not BMJF_sale_obj.aggregate(Sum('count'))['count__sum'] is None:
                    dsbs_inpkts.bmjf200_pkt = BMJF_sale_obj.aggregate(Sum('count'))['count__sum']
                    sale_litre = (Decimal(dsbs_inpkts.bmjf200_pkt) * Product.objects.get(
                        code='BMJF').quantity) / 1000
                    dsbs_inpkts.bmjf200_litre = sale_litre
                    dsbs_inpkts.bmjf200_cost = BMJF_sale_obj.aggregate(Sum('cost'))['cost__sum']

                    dsbs_inpkts.buttermilk_litre += sale_litre
                    dsbs_inpkts.buttermilk_cost += BMJF_sale_obj.aggregate(Sum('cost'))['cost__sum']
                    dsbs_inpkts.total_litre += sale_litre
                    dsbs_inpkts.fermented_products_litre += sale_litre
                    dsbs_inpkts.fermented_products_cost += BMJF_sale_obj.aggregate(Sum('cost'))['cost__sum']

                dsbs_inpkts.save()
        print('Upload completed for route: {}'.format(route.name))


# Script to upload Leakage allowence data from main.models(routetracewisesummary) into report.model.DailySessionllyBusinessllySale
# this uploads only Leakage data. icustomer data and agent data uploders are above
def upload_daily_leakage_allowence_for_each_route_per_session_given_date(date, session):
    print("Processing Leakage allowance. RouteWise")
    # loop thru RouteTrace, RouteTraceSummary for given date, given session
    for rt in RouteTrace.objects.filter(date=date, session=session):
        rtss = rt.routetracewisesalesummary_set.all()
        print("{}\t{}\t{}\t{}".format(rt.route.name, rt.date, rt.session, rtss.count()))
        if rt.route.is_temp_route == False:
          if rtss.count() > 0:
              # Hari how can we not hard code this?
              union = 'COIMBATORE Union'
              if rt.route.name == 'NILGIRIS_MOR':
                  union = 'NILGIRIS Union'
              elif rt.route.name == 'NILGIRIS1_MOR':
                  union = 'NILGIRIS Union'
              elif rt.route.name == 'O - TIRUPP_MOR':
                  union = 'TIRUPPUR Union'
              elif rt.route.name == 'O1 - TIRUP_MOR':
                  union = 'TIRUPPUR Union'
              elif rt.route.name == 'O2 - TIRUP_MOR':
                  union = 'TIRUPPUR Union'
              elif rt.route.name == 'O3 - TIRUP_MOR':
                  union = 'TIRUPPUR Union'
              elif rt.route.name == 'O4 - TIRUP_MOR':
                  union = 'TIRUPPUR Union'
              elif rt.route.name == 'O5 - TIRUP_MOR':
                  union = 'TIRUPPUR Union'
              elif rt.route.name == 'O6 - TIRUP_MOR':
                  union = 'TIRUPPUR Union'
              elif rt.route.name == 'TCMPS-CHENNAI_MOR':
                  union = 'CHENNAI Aavin'
              else:
                  union = 'COIMBATORE Union'

              # Find out the zone
              print('{} route is executing'.format(rt.route.name))
              if RouteBusinessMap.objects.filter(route=rt.route).exists():
                guesstimated_zone = RouteBusinessMap.objects.filter(route=rt.route)[0].business.zone
              else:
                continue

              dsbs_inpkts, created = DailySessionllyBusinessllySale.objects.update_or_create(
                  delivery_date=date,
                  session=session,
                  # business=business,
                  zone=guesstimated_zone,
                  # business_type=business.business_type,
                  union=union,
                  route=rt.route,
                  sold_to='Leakage',
                  defaults={
                      'created_by': User.objects.get(username='kutobot'),
                      'modified_by': User.objects.get(username='kutobot'),
                      'total_cost': 0,

                  }

              )
              if created:
                  print("\tRow Created: {}\t{}\t{}".format(dsbs_inpkts.delivery_date, dsbs_inpkts.session,
                                                          dsbs_inpkts.sold_to))
              else:
                  print("\tRow Exists: {}\t{}\t{}".format(dsbs_inpkts.delivery_date, dsbs_inpkts.session,
                                                          dsbs_inpkts.sold_to))

              for rts in rtss:
                  print("\t{},{},{},{}".format(rts.product.code, rts.leak_packet_count, rts.tray_count,
                                              rts.loose_packet_count))

                  # if none type recieved for leakpacket count set it to zero
                  if rts.leak_packet_count == None:
                      rts.leak_packet_count = 0

                  if rts.product.code == 'TM500':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.tm500_pkt = rts.leak_packet_count
                      dsbs_inpkts.tm500_litre = sale_litre
                      dsbs_inpkts.tm500_cost = 0

                      dsbs_inpkts.tm_litre += sale_litre
                      dsbs_inpkts.tm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'SM250':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.std250_pkt = rts.leak_packet_count
                      dsbs_inpkts.std250_litre = sale_litre
                      dsbs_inpkts.std250_cost = 0

                      dsbs_inpkts.sm_litre += sale_litre
                      dsbs_inpkts.sm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'SM500':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.std500_pkt = rts.leak_packet_count
                      dsbs_inpkts.std500_litre = sale_litre
                      dsbs_inpkts.std500_cost = 0

                      dsbs_inpkts.sm_litre += sale_litre
                      dsbs_inpkts.sm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'FCM500':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.fcm500_pkt = rts.leak_packet_count
                      dsbs_inpkts.fcm500_litre = sale_litre
                      dsbs_inpkts.fcm500_cost = 0

                      dsbs_inpkts.fcm_litre += sale_litre
                      dsbs_inpkts.fcm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'FCM1000':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.fcm1000_pkt = rts.leak_packet_count
                      dsbs_inpkts.fcm1000_litre = sale_litre
                      dsbs_inpkts.fcm1000_cost = 0

                      dsbs_inpkts.fcm_litre += sale_litre
                      dsbs_inpkts.fcm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'Tea500':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.tea500_pkt = rts.leak_packet_count
                      dsbs_inpkts.tea500_litre = sale_litre
                      dsbs_inpkts.tea500_cost = 0

                      dsbs_inpkts.tea_litre += sale_litre
                      dsbs_inpkts.tea_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'Tea1000':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.tea1000_pkt = rts.leak_packet_count
                      dsbs_inpkts.tea1000_litre = sale_litre
                      dsbs_inpkts.tea1000_cost = 0

                      dsbs_inpkts.tea_litre += sale_litre
                      dsbs_inpkts.tea_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre
    

                  elif rts.product.code == 'TNCAN':
                      sale_litre = rts.leak_packet_count
                      dsbs_inpkts.tmcan = rts.leak_packet_count / 40
                      dsbs_inpkts.tmcan_litre = sale_litre
                      dsbs_inpkts.tmcan_cost = 0

                      dsbs_inpkts.tm_litre += sale_litre
                      dsbs_inpkts.tm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'SMCAN':
                      sale_litre = rts.leak_packet_count
                      dsbs_inpkts.smcan = rts.leak_packet_count / 40
                      dsbs_inpkts.smcan_litre = sale_litre
                      dsbs_inpkts.smcan_cost = 0

                      dsbs_inpkts.sm_litre += sale_litre
                      dsbs_inpkts.sm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'FCMCAN':
                      sale_litre = rts.leak_packet_count
                      dsbs_inpkts.fcmcan = rts.leak_packet_count / 40
                      dsbs_inpkts.fcmcan_litre = sale_litre
                      dsbs_inpkts.fcmcan_cost = 0

                      dsbs_inpkts.fcm_litre += sale_litre
                      dsbs_inpkts.fcm_cost += 0
                      dsbs_inpkts.milk_cost += 0
                      dsbs_inpkts.milk_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'CURD500':
                      sale_kgs = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.curd500_pkt = rts.leak_packet_count
                      dsbs_inpkts.curd500_kgs = sale_kgs
                      dsbs_inpkts.curd500_cost = 0

                      dsbs_inpkts.curd_kgs += sale_kgs
                      dsbs_inpkts.curd_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_kgs
                      dsbs_inpkts.total_litre += sale_kgs

                  elif rts.product.code == 'CURD5000':
                      sale_kgs = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.curd5000_pkt = rts.leak_packet_count
                      dsbs_inpkts.curd5000_kgs = sale_kgs
                      dsbs_inpkts.curd5000_cost = 0

                      dsbs_inpkts.curd_kgs += sale_kgs
                      dsbs_inpkts.curd_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_kgs
                      dsbs_inpkts.total_litre += sale_kgs

                  elif rts.product.code == 'CU150':
                      sale_kgs = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.curd150_pkt = rts.leak_packet_count
                      dsbs_inpkts.curd150_kgs = sale_kgs
                      dsbs_inpkts.curd150_cost = 0

                      dsbs_inpkts.curd_kgs += sale_kgs
                      dsbs_inpkts.curd_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_kgs
                      dsbs_inpkts.total_litre += sale_kgs

                  elif rts.product.code == 'CPCU':
                      sale_kgs = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.cupcurd_box = rts.leak_packet_count / 12
                      dsbs_inpkts.cupcurd_count = rts.leak_packet_count
                      dsbs_inpkts.cupcurd_kgs = sale_kgs
                      dsbs_inpkts.cupcurd_cost = 0

                      dsbs_inpkts.curd_kgs += sale_kgs
                      dsbs_inpkts.curd_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_kgs
                      dsbs_inpkts.total_litre += sale_kgs

                  elif rts.product.code == 'CC!KG':
                      sale_kgs = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.curd_bucket = rts.leak_packet_count
                      dsbs_inpkts.curd_bucket_kgs = sale_kgs
                      dsbs_inpkts.curd_bucket_cost = 0

                      dsbs_inpkts.curd_kgs += sale_kgs
                      dsbs_inpkts.curd_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_kgs
                      dsbs_inpkts.total_litre += sale_kgs

                  elif rts.product.code == 'LSI':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.lassi200_pkt = rts.leak_packet_count
                      dsbs_inpkts.lassi200_kgs = sale_litre
                      dsbs_inpkts.lassi200_cost = 0

                      dsbs_inpkts.lassi_litre += sale_litre
                      dsbs_inpkts.lassi_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'BMILK':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.buttermilk200_pkt = rts.leak_packet_count
                      dsbs_inpkts.buttermilk200_litre = sale_litre
                      dsbs_inpkts.buttermilk200_cost = 0

                      dsbs_inpkts.buttermilk_litre += sale_litre
                      dsbs_inpkts.buttermilk_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'BMJar':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.bm_jar200_pkt = rts.leak_packet_count
                      dsbs_inpkts.bm_jar200_litre = sale_litre
                      dsbs_inpkts.bm_jar200_cost = 0

                      dsbs_inpkts.buttermilk_litre += sale_litre
                      dsbs_inpkts.buttermilk_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

                  elif rts.product.code == 'BMJF':
                      sale_litre = (Decimal(rts.leak_packet_count) * rts.product.quantity) / 1000
                      dsbs_inpkts.bmjf200_pkt = rts.leak_packet_count
                      dsbs_inpkts.bmjf200_litre = sale_litre
                      dsbs_inpkts.bmjf200_cost = 0

                      dsbs_inpkts.buttermilk_litre += sale_litre
                      dsbs_inpkts.buttermilk_cost += 0
                      dsbs_inpkts.fermented_products_cost += 0
                      dsbs_inpkts.fermented_products_litre += sale_litre
                      dsbs_inpkts.total_litre += sale_litre

              dsbs_inpkts.save()




def run(*args):
    dates = [(datetime.now().astimezone(indian).strftime('%Y-%m-%d'))]
    if args[0]:
        (key, date_string) = args[0].split('=')
        dates = date_string.split(',')
    else:
        print("Falling back to today {}".format(dates))


    print("Data will be ported from Main to Reports module for dates {}".format(dates))
    time.sleep(5)


    # Master Script to upload Agent, icustomer data from main.models into report.model.DailySessionllyBusinessllySale
    # This simply calls both the functions above for a given date
    agent_and_icustomer_scripts = [upload_daily_sale_for_agent_per_date, upload_daily_sale_for_icustomer_per_date,
                                   upload_daily_leakage_allowence_for_each_route_per_session_given_date]

    for date in dates:
        for session in Session.objects.filter():
            if DailySessionllyBusinessllySale.objects.filter(delivery_date=date, session=session).exists():
                DailySessionllyBusinessllySale.objects.filter(delivery_date=date, session=session).delete()
                print("Order deleted for date {}".format(date))
            for script in agent_and_icustomer_scripts:
                if SaleGroup.objects.filter(date=date, session=session).exists():
                    print("entry available for {} - {} in sale group. Proceeding to process date {}".format(date,
                                                                                                             session.name,
                                                                                                             date))
                    script(date, session)
                    print("Done processing date {} - {}".format(date, session.name))

                else:
                    print("NO entries available for {} - {} in sale group. Skipping {}".format(date, session.name, date))

    # Business Typelly
    # jupy_update_DailySessionllyBusinessTypellySale_from_DSBSale
    #
    # Leakage row is not included in this table
    sold_to_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('sold_to', flat=True)))
    union_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('union', flat=True)))
    for date in dates:
        for session in Session.objects.filter():
            if DailySessionllyBusinessTypellySale.objects.filter(delivery_date=date, session=session).exists():
                DailySessionllyBusinessTypellySale.objects.filter(delivery_date=date, session=session).delete()
                print("Order deleted for date {} - {}".format(date, session.name))
            for sold_to in sold_to_list:
                for union in union_list:
                    print("Working on {} : {} : {} entries".format(union, sold_to, session))
                    for business_type in BusinessType.objects.all():
                        print("\tWorking on {}: {} business type".format(union, business_type.name))
                        # GET ALL business type WISE SALES
                        bt_sales = DailySessionllyBusinessllySale.objects.filter(delivery_date=date, session=session,
                                                                                 business_type=business_type,
                                                                                 union=union, sold_to=sold_to)
                        print(bt_sales)
                        # Create an User table entry for this Agent
                        if bt_sales.count() > 0:
                            dsbts, created = DailySessionllyBusinessTypellySale.objects.update_or_create(
                                delivery_date=date,
                                session=session,
                                union=union,
                                business_type=business_type,
                                sold_to=sold_to,
                                defaults={
                                    'created_by': User.objects.get(username='kutobot'),
                                    'modified_by': User.objects.get(username='kutobot'),
                                    'total_cost': bt_sales.aggregate(Sum('total_cost'))['total_cost__sum']
                                }
                            )
                            if created:
                                print("\tRow Created: {}\t{}\t{}\t{}".format(dsbts.delivery_date, dsbts.session,
                                                                             dsbts.union, dsbts.business_type))
                            else:
                                print("\tRow Exists: {}\t{}\t{}\t{}".format(dsbts.delivery_date, dsbts.session,
                                                                            dsbts.union, dsbts.business_type))

                            # Now fill the route wise sum

                            # Milk
                            if getattr(DailySessionllyBusinessTypellySale, 'tm500_pkt', True):
                                dsbts.tm500_pkt = bt_sales.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
                                dsbts.tm500_litre = bt_sales.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
                                dsbts.tm500_cost = bt_sales.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
                                dsbts.tm500_unit_price = bt_sales.aggregate(Sum('tm500_unit_price'))[
                                    'tm500_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'std250_pkt', True):
                                dsbts.std250_pkt = bt_sales.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
                                dsbts.std250_litre = bt_sales.aggregate(Sum('std250_litre'))['std250_litre__sum']
                                dsbts.std250_cost = bt_sales.aggregate(Sum('std250_cost'))['std250_cost__sum']
                                dsbts.std250_unit_price = bt_sales.aggregate(Sum('std250_unit_price'))[
                                    'std250_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'std500_pkt', True):
                                dsbts.std500_pkt = bt_sales.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
                                dsbts.std500_litre = bt_sales.aggregate(Sum('std500_litre'))['std500_litre__sum']
                                dsbts.std500_cost = bt_sales.aggregate(Sum('std500_cost'))['std500_cost__sum']
                                dsbts.std500_unit_price = bt_sales.aggregate(Sum('std500_unit_price'))[
                                    'std500_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'fcm500_pkt', True):
                                dsbts.fcm500_pkt = bt_sales.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
                                dsbts.fcm500_litre = bt_sales.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
                                dsbts.fcm500_cost = bt_sales.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum']
                                dsbts.fcm500_unit_price = bt_sales.aggregate(Sum('fcm500_unit_price'))[
                                    'fcm500_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'fcm1000_pkt', True):
                                dsbts.fcm1000_pkt = bt_sales.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
                                dsbts.fcm1000_litre = bt_sales.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
                                dsbts.fcm1000_cost = bt_sales.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum']
                                dsbts.fcm1000_unit_price = bt_sales.aggregate(Sum('fcm1000_unit_price'))[
                                    'fcm1000_unit_price__sum']
                                
                            if getattr(DailySessionllyBusinessTypellySale, 'tea500_pkt', True):
                                dsbts.tea500_pkt = bt_sales.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
                                dsbts.tea500_litre = bt_sales.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
                                dsbts.tea500_cost = bt_sales.aggregate(Sum('tea500_cost'))['tea500_cost__sum']
                                dsbts.tea500_unit_price = bt_sales.aggregate(Sum('tea500_unit_price'))[
                                    'tea500_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'tea1000_pkt', True):
                                dsbts.tea1000_pkt = bt_sales.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
                                dsbts.tea1000_litre = bt_sales.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
                                dsbts.tea1000_cost = bt_sales.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum']
                                dsbts.tea1000_unit_price = bt_sales.aggregate(Sum('tea1000_unit_price'))[
                                    'tea1000_unit_price__sum']    

                            if getattr(DailySessionllyBusinessTypellySale, 'tmcan', True):
                                dsbts.tmcan = bt_sales.aggregate(Sum('tmcan'))['tmcan__sum']
                                dsbts.tmcan_litre = bt_sales.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
                                dsbts.tmcan_cost = bt_sales.aggregate(Sum('tmcan_cost'))['tmcan_cost__sum']
                                dsbts.tmcan_unit_price = bt_sales.aggregate(Sum('tmcan_unit_price'))[
                                    'tmcan_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'smcan', True):
                                dsbts.smcan = bt_sales.aggregate(Sum('smcan'))['smcan__sum']
                                dsbts.smcan_litre = bt_sales.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
                                dsbts.smcan_cost = bt_sales.aggregate(Sum('smcan_cost'))['smcan_cost__sum']
                                dsbts.smcan_unit_price = bt_sales.aggregate(Sum('smcan_unit_price'))[
                                    'smcan_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'fcmcan', True):
                                dsbts.fcmcan = bt_sales.aggregate(Sum('fcmcan'))['fcmcan__sum']
                                dsbts.fcmcan_litre = bt_sales.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
                                dsbts.fcmcan_cost = bt_sales.aggregate(Sum('fcmcan_cost'))['fcmcan_cost__sum']
                                dsbts.fcmcan_unit_price = bt_sales.aggregate(Sum('fcmcan_unit_price'))[
                                    'fcmcan_unit_price__sum']

                            # Curd
                            if getattr(DailySessionllyBusinessTypellySale, 'curd500_pkt', True):
                                dsbts.curd500_pkt = bt_sales.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
                                dsbts.curd500_kgs = bt_sales.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
                                dsbts.curd500_cost = bt_sales.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
                                dsbts.curd500_unit_price = bt_sales.aggregate(Sum('curd500_unit_price'))[
                                    'curd500_unit_price__sum']
                            
                            if getattr(DailySessionllyBusinessTypellySale, 'curd5000_pkt', True):
                                dsbts.curd5000_pkt = bt_sales.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
                                dsbts.curd5000_kgs = bt_sales.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
                                dsbts.curd5000_cost = bt_sales.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
                                dsbts.curd5000_unit_price = bt_sales.aggregate(Sum('curd5000_unit_price'))[
                                    'curd5000_unit_price__sum']    

                            if getattr(DailySessionllyBusinessTypellySale, 'curd150_pkt', True):
                                dsbts.curd150_pkt = bt_sales.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
                                dsbts.curd150_kgs = bt_sales.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
                                dsbts.curd150_cost = bt_sales.aggregate(Sum('curd150_cost'))['curd150_cost__sum']
                                dsbts.curd150_unit_price = bt_sales.aggregate(Sum('curd150_unit_price'))[
                                    'curd150_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'cupcurd_box', True):
                                dsbts.cupcurd_box = bt_sales.aggregate(Sum('cupcurd_box'))['cupcurd_box__sum']
                                dsbts.cupcurd_count = bt_sales.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
                                dsbts.cupcurd_kgs = bt_sales.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
                                dsbts.cupcurd_cost = bt_sales.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum']
                                dsbts.cupcurd_unit_price = bt_sales.aggregate(Sum('cupcurd_unit_price'))[
                                    'cupcurd_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'curd_bucket', True):
                                dsbts.curd_bucket = bt_sales.aggregate(Sum('curd_bucket'))['curd_bucket__sum']
                                dsbts.curd_bucket_kgs = bt_sales.aggregate(Sum('curd_bucket_kgs'))[
                                    'curd_bucket_kgs__sum']
                                dsbts.curd_bucket_cost = bt_sales.aggregate(Sum('curd_bucket_cost'))[
                                    'curd_bucket_cost__sum']
                                dsbts.curd_bucket_unit_price = bt_sales.aggregate(Sum('curd_bucket_unit_price'))[
                                    'curd_bucket_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'lassi200_pkt', True):
                                dsbts.lassi200_pkt = bt_sales.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
                                dsbts.lassi200_kgs = bt_sales.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
                                dsbts.lassi200_cost = bt_sales.aggregate(Sum('lassi200_cost'))['lassi200_cost__sum']
                                dsbts.lassi200_unit_price = bt_sales.aggregate(Sum('lassi200_unit_price'))[
                                    'lassi200_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'buttermilk200_pkt', True):
                                dsbts.buttermilk200_pkt = bt_sales.aggregate(Sum('buttermilk200_pkt'))[
                                    'buttermilk200_pkt__sum']
                                dsbts.buttermilk200_litre = bt_sales.aggregate(Sum('buttermilk200_litre'))[
                                    'buttermilk200_litre__sum']
                                dsbts.buttermilk200_cost = bt_sales.aggregate(Sum('buttermilk200_cost'))[
                                    'buttermilk200_cost__sum']
                                dsbts.buttermilk200_unit_price = bt_sales.aggregate(Sum('buttermilk200_unit_price'))[
                                    'buttermilk200_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'bm_jar200_pkt', True):
                                dsbts.bm_jar200_pkt = bt_sales.aggregate(Sum('bm_jar200_pkt'))[
                                    'bm_jar200_pkt__sum']
                                dsbts.bm_jar200_litre = bt_sales.aggregate(Sum('bm_jar200_litre'))[
                                    'bm_jar200_litre__sum']
                                dsbts.bm_jar200_cost = bt_sales.aggregate(Sum('bm_jar200_cost'))[
                                    'bm_jar200_cost__sum']
                                dsbts.bm_jar200_unit_price = bt_sales.aggregate(Sum('bm_jar200_unit_price'))[
                                    'bm_jar200_unit_price__sum']

                            if getattr(DailySessionllyBusinessTypellySale, 'bmjf200_pkt', True):
                                dsbts.bmjf200_pkt = bt_sales.aggregate(Sum('bmjf200_pkt'))[
                                    'bmjf200_pkt__sum']
                                dsbts.bmjf200_litre = bt_sales.aggregate(Sum('bmjf200_litre'))[
                                    'bmjf200_litre__sum']
                                dsbts.bmjf200_cost = bt_sales.aggregate(Sum('bmjf200_cost'))[
                                    'bmjf200_cost__sum']
                                dsbts.bmjf200_unit_price = bt_sales.aggregate(Sum('bmjf200_unit_price'))[
                                    'bmjf200_unit_price__sum']

                            dsbts.tm_litre = bt_sales.aggregate(Sum('tm_litre'))['tm_litre__sum']
                            dsbts.tm_cost = bt_sales.aggregate(Sum('tm_cost'))['tm_cost__sum']
                            dsbts.sm_litre = bt_sales.aggregate(Sum('sm_litre'))['sm_litre__sum']
                            dsbts.sm_cost = bt_sales.aggregate(Sum('sm_cost'))['sm_cost__sum']
                            dsbts.fcm_litre = bt_sales.aggregate(Sum('fcm_litre'))['fcm_litre__sum']
                            dsbts.fcm_cost = bt_sales.aggregate(Sum('fcm_cost'))['fcm_cost__sum']
                            dsbts.tea_litre = bt_sales.aggregate(Sum('tea_litre'))['tea_litre__sum']
                            dsbts.tea_cost = bt_sales.aggregate(Sum('tea_cost'))['tea_cost__sum']
                            dsbts.milk_litre = bt_sales.aggregate(Sum('milk_litre'))['milk_litre__sum']
                            dsbts.milk_cost = bt_sales.aggregate(Sum('milk_cost'))['milk_cost__sum']
                            dsbts.curd_kgs = bt_sales.aggregate(Sum('curd_kgs'))['curd_kgs__sum']
                            dsbts.curd_cost = bt_sales.aggregate(Sum('curd_cost'))['curd_cost__sum']
                            dsbts.buttermilk_cost = bt_sales.aggregate(Sum('buttermilk_cost'))['buttermilk_cost__sum']
                            dsbts.buttermilk_litre = bt_sales.aggregate(Sum('buttermilk_litre'))[
                                'buttermilk_litre__sum']
                            dsbts.lassi_litre = bt_sales.aggregate(Sum('lassi_litre'))['lassi_litre__sum']
                            dsbts.lassi_cost = bt_sales.aggregate(Sum('lassi_cost'))['lassi_cost__sum']
                            dsbts.fermented_products_litre = bt_sales.aggregate(Sum('fermented_products_litre'))[
                                'fermented_products_litre__sum']
                            dsbts.fermented_products_cost = bt_sales.aggregate(Sum('fermented_products_cost'))[
                                'fermented_products_cost__sum']
                            dsbts.total_litre = bt_sales.aggregate(Sum('total_litre'))['total_litre__sum']

                            dsbts.save()

    # Routelly
    # jupy_update_DailySessionllyRoutellySale_from_DSBSale
    #
    sold_to_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('sold_to', flat=True)))
    union_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('union', flat=True)))

    for date in dates:
        for session in Session.objects.filter():
            if DailySessionllyRoutellySale.objects.filter(delivery_date=date, session=session).exists():
                DailySessionllyRoutellySale.objects.filter(delivery_date=date, session=session).delete()
                print("Order deleted for date {} - {}".format(date, session.name))
            for sold_to in sold_to_list:
                for route in Route.objects.filter(session=session):
                    route_sales = DailySessionllyBusinessllySale.objects.filter(delivery_date=date, route=route,
                                                                                sold_to=sold_to)
                    # Create an User table entry for this Agent
                    if route_sales.count() > 0:
                        dsrs, created = DailySessionllyRoutellySale.objects.update_or_create(
                            delivery_date=date,
                            session=session,
                            route=route,
                            sold_to=sold_to,
                            defaults={
                                'created_by': User.objects.get(username='kutobot'),
                                'modified_by': User.objects.get(username='kutobot'),
                                'total_cost': route_sales.aggregate(Sum('total_cost'))['total_cost__sum'],
                            }

                        )
                        if created:
                            print("\tRow Created: {}\t{}\t{}".format(dsrs.delivery_date, dsrs.session, dsrs.route.name))
                        else:tea500_pkt
                        if getattr(DailySessionllyRoutellySale, 'tm500_pkt', True):
                            dsrs.tm500_pkt = route_sales.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
                            dsrs.tm500_litre = route_sales.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
                            dsrs.tm500_cost = route_sales.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
                            dsrs.tm500_unit_price = route_sales.aggregate(Sum('tm500_unit_price'))[
                                'tm500_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'std250_pkt', True):
                            dsrs.std250_pkt = route_sales.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
                            dsrs.std250_litre = route_sales.aggregate(Sum('std250_litre'))['std250_litre__sum']
                            dsrs.std250_cost = route_sales.aggregate(Sum('std250_cost'))['std250_cost__sum']
                            dsrs.std250_unit_price = route_sales.aggregate(Sum('std250_unit_price'))[
                                'std250_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'std500_pkt', True):
                            dsrs.std500_pkt = route_sales.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
                            dsrs.std500_litre = route_sales.aggregate(Sum('std500_litre'))['std500_litre__sum']
                            dsrs.std500_cost = route_sales.aggregate(Sum('std500_cost'))['std500_cost__sum']
                            dsrs.std500_unit_price = route_sales.aggregate(Sum('std500_unit_price'))[
                                'std500_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'fcm500_pkt', True):
                            dsrs.fcm500_pkt = route_sales.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
                            dsrs.fcm500_litre = route_sales.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
                            dsrs.fcm500_cost = route_sales.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum']
                            dsrs.fcm500_unit_price = route_sales.aggregate(Sum('fcm500_unit_price'))[
                                'fcm500_unit_price__sum']

                        if getattr(DailySessionllyBusinessTypellySale, 'fcm1000_pkt', True):
                            dsrs.fcm1000_pkt = route_sales.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
                            dsrs.fcm1000_litre = route_sales.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
                            dsrs.fcm1000_cost = route_sales.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum']
                            dsrs.fcm1000_unit_price = route_sales.aggregate(Sum('fcm1000_unit_price'))[
                                'fcm1000_unit_price__sum']
                            
                        if getattr(DailySessionllyRoutellySale, 'tea500_pkt', True):
                            dsrs.tea500_pkt = route_sales.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
                            dsrs.tea500_litre = route_sales.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
                            dsrs.tea500_cost = route_sales.aggregate(Sum('tea500_cost'))['tea500_cost__sum']
                            dsrs.tea500_unit_price = route_sales.aggregate(Sum('tea500_unit_price'))[
                                'tea500_unit_price__sum']

                        if getattr(DailySessionllyBusinessTypellySale, 'tea1000_pkt', True):
                            dsrs.tea1000_pkt = route_sales.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
                            dsrs.tea1000_litre = route_sales.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
                            dsrs.tea1000_cost = route_sales.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum']
                            dsrs.tea1000_unit_price = route_sales.aggregate(Sum('tea1000_unit_price'))[
                                'tea1000_unit_price__sum']    

                        if getattr(DailySessionllyRoutellySale, 'tmcan', True):
                            dsrs.tmcan = route_sales.aggregate(Sum('tmcan'))['tmcan__sum']
                            dsrs.tmcan_litre = route_sales.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
                            dsrs.tmcan_cost = route_sales.aggregate(Sum('tmcan_cost'))['tmcan_cost__sum']
                            dsrs.tmcan_unit_price = route_sales.aggregate(Sum('tmcan_unit_price'))[
                                'tmcan_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'smcan', True):
                            dsrs.smcan = route_sales.aggregate(Sum('smcan'))['smcan__sum']
                            dsrs.smcan_litre = route_sales.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
                            dsrs.smcan_cost = route_sales.aggregate(Sum('smcan_cost'))['smcan_cost__sum']
                            dsrs.smcan_unit_price = route_sales.aggregate(Sum('smcan_unit_price'))[
                                'smcan_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'fcmcan', True):
                            dsrs.fcmcan = route_sales.aggregate(Sum('fcmcan'))['fcmcan__sum']
                            dsrs.fcmcan_litre = route_sales.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
                            dsrs.fcmcan_cost = route_sales.aggregate(Sum('fcmcan_cost'))['fcmcan_cost__sum']
                            dsrs.fcmcan_unit_price = route_sales.aggregate(Sum('fcmcan_unit_price'))[
                                'fcmcan_unit_price__sum']

                        # Curd
                        if getattr(DailySessionllyRoutellySale, 'curd500_pkt', True):
                            dsrs.curd500_pkt = route_sales.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
                            dsrs.curd500_kgs = route_sales.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
                            dsrs.curd500_cost = route_sales.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
                            dsrs.curd500_unit_price = route_sales.aggregate(Sum('curd500_unit_price'))[
                                'curd500_unit_price__sum']
                        
                        if getattr(DailySessionllyRoutellySale, 'curd5000_pkt', True):
                            dsrs.curd5000_pkt = route_sales.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
                            dsrs.curd5000_kgs = route_sales.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
                            dsrs.curd5000_cost = route_sales.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
                            dsrs.curd5000_unit_price = route_sales.aggregate(Sum('curd5000_unit_price'))[
                                'curd5000_unit_price__sum']    

                        if getattr(DailySessionllyRoutellySale, 'curd150_pkt', True):
                            dsrs.curd150_pkt = route_sales.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
                            dsrs.curd150_kgs = route_sales.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
                            dsrs.curd150_cost = route_sales.aggregate(Sum('curd150_cost'))['curd150_cost__sum']
                            dsrs.curd150_unit_price = route_sales.aggregate(Sum('curd150_unit_price'))[
                                'curd150_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'cupcurd_box', True):
                            dsrs.cupcurd_box = route_sales.aggregate(Sum('cupcurd_box'))['cupcurd_box__sum']
                            dsrs.cupcurd_count = route_sales.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
                            dsrs.cupcurd_kgs = route_sales.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
                            dsrs.cupcurd_cost = route_sales.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum']
                            dsrs.cupcurd_unit_price = route_sales.aggregate(Sum('cupcurd_unit_price'))[
                                'cupcurd_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'curd_bucket', True):
                            dsrs.curd_bucket = route_sales.aggregate(Sum('curd_bucket'))['curd_bucket__sum']
                            dsrs.curd_bucket_kgs = route_sales.aggregate(Sum('curd_bucket_kgs'))['curd_bucket_kgs__sum']
                            dsrs.curd_bucket_cost = route_sales.aggregate(Sum('curd_bucket_cost'))[
                                'curd_bucket_cost__sum']
                            dsrs.curd_bucket_unit_price = route_sales.aggregate(Sum('curd_bucket_unit_price'))[
                                'curd_bucket_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'lassi200_pkt', True):
                            dsrs.lassi200_pkt = route_sales.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
                            dsrs.lassi200_kgs = route_sales.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
                            dsrs.lassi200_cost = route_sales.aggregate(Sum('lassi200_cost'))['lassi200_cost__sum']
                            dsrs.lassi200_unit_price = route_sales.aggregate(Sum('lassi200_unit_price'))[
                                'lassi200_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'buttermilk200_pkt', True):
                            dsrs.buttermilk200_pkt = route_sales.aggregate(Sum('buttermilk200_pkt'))[
                                'buttermilk200_pkt__sum']
                            dsrs.buttermilk200_litre = route_sales.aggregate(Sum('buttermilk200_litre'))[
                                'buttermilk200_litre__sum']
                            dsrs.buttermilk200_cost = route_sales.aggregate(Sum('buttermilk200_cost'))[
                                'buttermilk200_cost__sum']
                            dsrs.buttermilk200_unit_price = route_sales.aggregate(Sum('buttermilk200_unit_price'))[
                                'buttermilk200_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'bm_jar200_pkt', True):
                            dsrs.bm_jar200_pkt = route_sales.aggregate(Sum('bm_jar200_pkt'))[
                                'bm_jar200_pkt__sum']
                            dsrs.bm_jar200_litre = route_sales.aggregate(Sum('bm_jar200_litre'))[
                                'bm_jar200_litre__sum']
                            dsrs.bm_jar200_cost = route_sales.aggregate(Sum('bm_jar200_cost'))[
                                'bm_jar200_cost__sum']
                            dsrs.bm_jar200_unit_price = route_sales.aggregate(Sum('bm_jar200_unit_price'))[
                                'bm_jar200_unit_price__sum']

                        if getattr(DailySessionllyRoutellySale, 'bmjf200_pkt', True):
                            dsrs.bmjf200_pkt = route_sales.aggregate(Sum('bmjf200_pkt'))[
                                'bmjf200_pkt__sum']
                            dsrs.bmjf200_litre = route_sales.aggregate(Sum('bmjf200_litre'))[
                                'bmjf200_litre__sum']
                            dsrs.bmjf200_cost = route_sales.aggregate(Sum('bmjf200_cost'))[
                                'bmjf200_cost__sum']
                            dsrs.bmjf200_unit_price = route_sales.aggregate(Sum('bmjf200_unit_price'))[
                                'bmjf200_unit_price__sum']

                        dsrs.tm_litre = route_sales.aggregate(Sum('tm_litre'))['tm_litre__sum']
                        dsrs.tm_cost = route_sales.aggregate(Sum('tm_cost'))['tm_cost__sum']
                        dsrs.sm_litre = route_sales.aggregate(Sum('sm_litre'))['sm_litre__sum']
                        dsrs.sm_cost = route_sales.aggregate(Sum('sm_cost'))['sm_cost__sum']
                        dsrs.fcm_litre = route_sales.aggregate(Sum('fcm_litre'))['fcm_litre__sum']
                        dsrs.fcm_cost = route_sales.aggregate(Sum('fcm_cost'))['fcm_cost__sum']
                        dsrs.tea_litre = route_sales.aggregate(Sum('tea_litre'))['tea_litre__sum']
                        dsrs.tea_cost = route_sales.aggregate(Sum('tea_cost'))['tea_cost__sum']
                        dsrs.milk_litre = route_sales.aggregate(Sum('milk_litre'))['milk_litre__sum']
                        dsrs.milk_cost = route_sales.aggregate(Sum('milk_cost'))['milk_cost__sum']
                        dsrs.curd_kgs = route_sales.aggregate(Sum('curd_kgs'))['curd_kgs__sum']
                        dsrs.curd_cost = route_sales.aggregate(Sum('curd_cost'))['curd_cost__sum']
                        dsrs.buttermilk_cost = route_sales.aggregate(Sum('buttermilk_cost'))['buttermilk_cost__sum']
                        dsrs.buttermilk_litre = route_sales.aggregate(Sum('buttermilk_litre'))['buttermilk_litre__sum']
                        dsrs.lassi_litre = route_sales.aggregate(Sum('lassi_litre'))['lassi_litre__sum']
                        dsrs.lassi_cost = route_sales.aggregate(Sum('lassi_cost'))['lassi_cost__sum']
                        dsrs.fermented_products_litre = route_sales.aggregate(Sum('fermented_products_litre'))[
                            'fermented_products_litre__sum']
                        dsrs.fermented_products_cost = route_sales.aggregate(Sum('fermented_products_cost'))[
                            'fermented_products_cost__sum']
                        dsrs.total_litre = route_sales.aggregate(Sum('total_litre'))['total_litre__sum']

                        dsrs.save()

                print(sold_to)




    # Unionlly
    # jupy_update_DailySessionllyUnionllySale_from_DSBSale
    #

    sold_to_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('sold_to', flat=True)))
    union_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('union', flat=True)))

    for date in dates:
        for session in Session.objects.filter():
            if DailySessionllyUnionllySale.objects.filter(delivery_date=date, session=session).exists():
                DailySessionllyUnionllySale.objects.filter(delivery_date=date, session=session).delete()
                print("Order deleted for date {} - {}".format(date, session.name))
            for sold_to in sold_to_list:
                print(sold_to)
                for union in union_list:
                    print(union)

                    # GET ALL UNION WISE SALES
                    union_sales = DailySessionllyBusinessllySale.objects.filter(delivery_date=date, session=session,
                                                                                union=union, sold_to=sold_to)
                    print(union_sales)
                    print("{}, {}, {}".format(date, union, union_sales.count()))

                    # Create an User table entry for this Agent
                    if union_sales.count() > 0:
                        print("Union sales count is more than zero")
                        dsus, created = DailySessionllyUnionllySale.objects.update_or_create(
                            delivery_date=date,
                            session=session,
                            union=union,
                            sold_to=sold_to,

                            defaults={
                                'created_by': User.objects.get(username='kutobot'),
                                'modified_by': User.objects.get(username='kutobot'),
                                'total_cost': union_sales.aggregate(Sum('total_cost'))['total_cost__sum']
                            }

                        )
                        if created:
                            print("\tRow Created: {}\t{}\t{}".format(dsus.delivery_date, dsus.session, dsus.union))
                        else:
                            print("\tRow Exists: {}\t{}\t{}".format(dsus.delivery_date, dsus.session, dsus.union))

                        # Now fill the route wise sum

                        # Milk
                        if getattr(DailySessionllyUnionllySale, 'tm500_pkt', True):
                            dsus.tm500_pkt = union_sales.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
                            dsus.tm500_litre = union_sales.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
                            dsus.tm500_cost = union_sales.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
                            dsus.tm500_unit_price = union_sales.aggregate(Sum('tm500_unit_price'))[
                                'tm500_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'std250_pkt', True):
                            dsus.std250_pkt = union_sales.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
                            dsus.std250_litre = union_sales.aggregate(Sum('std250_litre'))['std250_litre__sum']
                            dsus.std250_cost = union_sales.aggregate(Sum('std250_cost'))['std250_cost__sum']
                            dsus.std250_unit_price = union_sales.aggregate(Sum('std250_unit_price'))[
                                'std250_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'std500_pkt', True):
                            dsus.std500_pkt = union_sales.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
                            dsus.std500_litre = union_sales.aggregate(Sum('std500_litre'))['std500_litre__sum']
                            dsus.std500_cost = union_sales.aggregate(Sum('std500_cost'))['std500_cost__sum']
                            dsus.std500_unit_price = union_sales.aggregate(Sum('std500_unit_price'))[
                                'std500_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'fcm500_pkt', True):
                            dsus.fcm500_pkt = union_sales.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
                            dsus.fcm500_litre = union_sales.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
                            dsus.fcm500_cost = union_sales.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum']
                            dsus.fcm500_unit_price = union_sales.aggregate(Sum('fcm500_unit_price'))[
                                'fcm500_unit_price__sum']

                        if getattr(DailySessionllyBusinessTypellySale, 'fcm1000_pkt', True):
                            dsus.fcm1000_pkt = union_sales.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
                            dsus.fcm1000_litre = union_sales.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
                            dsus.fcm1000_cost = union_sales.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum']
                            dsus.fcm1000_unit_price = union_sales.aggregate(Sum('fcm1000_unit_price'))[
                                'fcm1000_unit_price__sum']
                            
                        if getattr(DailySessionllyUnionllySale, 'tea500_pkt', True):
                            dsus.tea500_pkt = union_sales.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
                            dsus.tea500_litre = union_sales.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
                            dsus.tea500_cost = union_sales.aggregate(Sum('tea500_cost'))['tea500_cost__sum']
                            dsus.tea500_unit_price = union_sales.aggregate(Sum('tea500_unit_price'))[
                                'tea500_unit_price__sum']

                        if getattr(DailySessionllyBusinessTypellySale, 'tea1000_pkt', True):
                            dsus.tea1000_pkt = union_sales.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
                            dsus.tea1000_litre = union_sales.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
                            dsus.tea1000_cost = union_sales.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum']
                            dsus.tea1000_unit_price = union_sales.aggregate(Sum('tea1000_unit_price'))[
                                'tea1000_unit_price__sum']    

                        if getattr(DailySessionllyUnionllySale, 'tmcan', True):
                            dsus.tmcan = union_sales.aggregate(Sum('tmcan'))['tmcan__sum']
                            dsus.tmcan_litre = union_sales.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
                            dsus.tmcan_cost = union_sales.aggregate(Sum('tmcan_cost'))['tmcan_cost__sum']
                            dsus.tmcan_unit_price = union_sales.aggregate(Sum('tmcan_unit_price'))[
                                'tmcan_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'smcan', True):
                            dsus.smcan = union_sales.aggregate(Sum('smcan'))['smcan__sum']
                            dsus.smcan_litre = union_sales.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
                            dsus.smcan_cost = union_sales.aggregate(Sum('smcan_cost'))['smcan_cost__sum']
                            dsus.smcan_unit_price = union_sales.aggregate(Sum('smcan_unit_price'))[
                                'smcan_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'fcmcan', True):
                            dsus.fcmcan = union_sales.aggregate(Sum('fcmcan'))['fcmcan__sum']
                            dsus.fcmcan_litre = union_sales.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
                            dsus.fcmcan_cost = union_sales.aggregate(Sum('fcmcan_cost'))['fcmcan_cost__sum']
                            dsus.fcmcan_unit_price = union_sales.aggregate(Sum('fcmcan_unit_price'))[
                                'fcmcan_unit_price__sum']

                        # Curd
                        if getattr(DailySessionllyUnionllySale, 'curd500_pkt', True):
                            dsus.curd500_pkt = union_sales.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
                            dsus.curd500_kgs = union_sales.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
                            dsus.curd500_cost = union_sales.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
                            dsus.curd500_unit_price = union_sales.aggregate(Sum('curd500_unit_price'))[
                                'curd500_unit_price__sum']
                            
                        if getattr(DailySessionllyUnionllySale, 'curd5000_pkt', True):
                            dsus.curd5000_pkt = union_sales.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
                            dsus.curd5000_kgs = union_sales.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
                            dsus.curd5000_cost = union_sales.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
                            dsus.curd5000_unit_price = union_sales.aggregate(Sum('curd5000_unit_price'))[
                                'curd5000_unit_price__sum']    

                        if getattr(DailySessionllyUnionllySale, 'curd150_pkt', True):
                            dsus.curd150_pkt = union_sales.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
                            dsus.curd150_kgs = union_sales.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
                            dsus.curd150_cost = union_sales.aggregate(Sum('curd150_cost'))['curd150_cost__sum']
                            dsus.curd150_unit_price = union_sales.aggregate(Sum('curd150_unit_price'))[
                                'curd150_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'cupcurd_box', True):
                            dsus.cupcurd_box = union_sales.aggregate(Sum('cupcurd_box'))['cupcurd_box__sum']
                            dsus.cupcurd_count = union_sales.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
                            dsus.cupcurd_kgs = union_sales.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
                            dsus.cupcurd_cost = union_sales.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum']
                            dsus.cupcurd_unit_price = union_sales.aggregate(Sum('cupcurd_unit_price'))[
                                'cupcurd_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'curd_bucket', True):
                            dsus.curd_bucket = union_sales.aggregate(Sum('curd_bucket'))['curd_bucket__sum']
                            dsus.curd_bucket_kgs = union_sales.aggregate(Sum('curd_bucket_kgs'))['curd_bucket_kgs__sum']
                            dsus.curd_bucket_cost = union_sales.aggregate(Sum('curd_bucket_cost'))[
                                'curd_bucket_cost__sum']
                            dsus.curd_bucket_unit_price = union_sales.aggregate(Sum('curd_bucket_unit_price'))[
                                'curd_bucket_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'lassi200_pkt', True):
                            dsus.lassi200_pkt = union_sales.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
                            dsus.lassi200_kgs = union_sales.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
                            dsus.lassi200_cost = union_sales.aggregate(Sum('lassi200_cost'))['lassi200_cost__sum']
                            dsus.lassi200_unit_price = union_sales.aggregate(Sum('lassi200_unit_price'))[
                                'lassi200_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'buttermilk200_pkt', True):
                            dsus.buttermilk200_pkt = union_sales.aggregate(Sum('buttermilk200_pkt'))[
                                'buttermilk200_pkt__sum']
                            dsus.buttermilk200_litre = union_sales.aggregate(Sum('buttermilk200_litre'))[
                                'buttermilk200_litre__sum']
                            dsus.buttermilk200_cost = union_sales.aggregate(Sum('buttermilk200_cost'))[
                                'buttermilk200_cost__sum']
                            dsus.buttermilk200_unit_price = union_sales.aggregate(Sum('buttermilk200_unit_price'))[
                                'buttermilk200_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'bm_jar200_pkt', True):
                            dsus.bm_jar200_pkt = union_sales.aggregate(Sum('bm_jar200_pkt'))[
                                'bm_jar200_pkt__sum']
                            dsus.bm_jar200_litre = union_sales.aggregate(Sum('bm_jar200_litre'))[
                                'bm_jar200_litre__sum']
                            dsus.bm_jar200_cost = union_sales.aggregate(Sum('bm_jar200_cost'))[
                                'bm_jar200_cost__sum']
                            dsus.bm_jar200_unit_price = union_sales.aggregate(Sum('bm_jar200_unit_price'))[
                                'bm_jar200_unit_price__sum']

                        if getattr(DailySessionllyUnionllySale, 'bmjf200_pkt', True):
                            dsus.bmjf200_pkt = union_sales.aggregate(Sum('bmjf200_pkt'))[
                                'bmjf200_pkt__sum']
                            dsus.bmjf200_litre = union_sales.aggregate(Sum('bmjf200_litre'))[
                                'bmjf200_litre__sum']
                            dsus.bmjf200_cost = union_sales.aggregate(Sum('bmjf200_cost'))[
                                'bmjf200_cost__sum']
                            dsus.bmjf200_unit_price = union_sales.aggregate(Sum('bmjf200_unit_price'))[
                                'bmjf200_unit_price__sum']

                        dsus.tm_litre = union_sales.aggregate(Sum('tm_litre'))['tm_litre__sum']
                        dsus.tm_cost = union_sales.aggregate(Sum('tm_cost'))['tm_cost__sum']
                        dsus.sm_litre = union_sales.aggregate(Sum('sm_litre'))['sm_litre__sum']
                        dsus.sm_cost = union_sales.aggregate(Sum('sm_cost'))['sm_cost__sum']
                        dsus.fcm_litre = union_sales.aggregate(Sum('fcm_litre'))['fcm_litre__sum']
                        dsus.fcm_cost = union_sales.aggregate(Sum('fcm_cost'))['fcm_cost__sum']
                        dsus.tea_litre = union_sales.aggregate(Sum('tea_litre'))['tea_litre__sum']
                        dsus.tea_cost = union_sales.aggregate(Sum('tea_cost'))['tea_cost__sum']
                        dsus.milk_litre = union_sales.aggregate(Sum('milk_litre'))['milk_litre__sum']
                        dsus.milk_cost = union_sales.aggregate(Sum('milk_cost'))['milk_cost__sum']
                        dsus.curd_kgs = union_sales.aggregate(Sum('curd_kgs'))['curd_kgs__sum']
                        dsus.curd_cost = union_sales.aggregate(Sum('curd_cost'))['curd_cost__sum']
                        dsus.buttermilk_cost = union_sales.aggregate(Sum('buttermilk_cost'))['buttermilk_cost__sum']
                        dsus.buttermilk_litre = union_sales.aggregate(Sum('buttermilk_litre'))['buttermilk_litre__sum']
                        dsus.lassi_litre = union_sales.aggregate(Sum('lassi_litre'))['lassi_litre__sum']
                        dsus.lassi_cost = union_sales.aggregate(Sum('lassi_cost'))['lassi_cost__sum']
                        dsus.fermented_products_litre = union_sales.aggregate(Sum('fermented_products_litre'))[
                            'fermented_products_litre__sum']
                        dsus.fermented_products_cost = union_sales.aggregate(Sum('fermented_products_cost'))[
                            'fermented_products_cost__sum']
                        dsus.total_litre = union_sales.aggregate(Sum('total_litre'))['total_litre__sum']

                        dsus.save()


    # Zonally
    # jupy_update_DailySessionllyZonallySale_from_DSBSale
    #

    sold_to_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('sold_to', flat=True)))
    union_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('union', flat=True)))
    sold_to_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('sold_to', flat=True)))
    union_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('union', flat=True)))
    for date in dates:
        for session in Session.objects.filter():
            if DailySessionllyZonallySale.objects.filter(delivery_date=date, session=session).exists():
                DailySessionllyZonallySale.objects.filter(delivery_date=date, session=session).delete()
                print("Order deleted for date {} - {}".format(date, session.name))
            for sold_to in sold_to_list:
                print(sold_to)
                for zone in Zone.objects.all():

                    # Find out the union
                    union = 'COIMBATORE Union'
                    if zone.name == 'NILGIRIS':
                        union = 'NILGIRIS Union'
                    elif zone.name == 'TIRUPPUR':
                        union = 'TIRUPPUR Union'
                    elif zone.name == 'CHENNAI Aavin':
                        union = 'CHENNAI Aavin'
                    else:
                        union = 'COIMBATORE Union'

                    # GET ALL UNION WISE SALES
                    zone_sales = DailySessionllyBusinessllySale.objects.filter(delivery_date=date, session=session,
                                                                               zone=zone, sold_to=sold_to)

                    # Create an User table entry for this Agent
                    if zone_sales.count() > 0:
                        dszs, created = DailySessionllyZonallySale.objects.update_or_create(
                            delivery_date=date,
                            session=session,
                            zone=zone,
                            union=union,
                            sold_to=sold_to,
                            defaults={
                                'created_by': User.objects.get(username='kutobot'),
                                'modified_by': User.objects.get(username='kutobot'),
                                'total_cost': zone_sales.aggregate(Sum('total_cost'))['total_cost__sum']
                            }

                        )
                        if created:
                            print("\tRow Created: {}\t{}\t{}".format(dszs.delivery_date, dszs.session, dszs.zone.name))
                        else:
                            print("\tRow Exists: {}\t{}\t{}".format(dszs.delivery_date, dszs.session, dszs.zone.name))

                        # Now fill the route wise sum

                        # Milk
                        if getattr(DailySessionllyZonallySale, 'tm500_pkt', True):
                            dszs.tm500_pkt = zone_sales.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
                            dszs.tm500_litre = zone_sales.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
                            dszs.tm500_cost = zone_sales.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
                            dszs.tm500_unit_price = zone_sales.aggregate(Sum('tm500_unit_price'))[
                                'tm500_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'std250_pkt', True):
                            dszs.std250_pkt = zone_sales.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
                            dszs.std250_litre = zone_sales.aggregate(Sum('std250_litre'))['std250_litre__sum']
                            dszs.std250_cost = zone_sales.aggregate(Sum('std250_cost'))['std250_cost__sum']
                            dszs.std250_unit_price = zone_sales.aggregate(Sum('std250_unit_price'))[
                                'std250_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'std500_pkt', True):
                            dszs.std500_pkt = zone_sales.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
                            dszs.std500_litre = zone_sales.aggregate(Sum('std500_litre'))['std500_litre__sum']
                            dszs.std500_cost = zone_sales.aggregate(Sum('std500_cost'))['std500_cost__sum']
                            dszs.std500_unit_price = zone_sales.aggregate(Sum('std500_unit_price'))[
                                'std500_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'fcm500_pkt', True):
                            dszs.fcm500_pkt = zone_sales.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
                            dszs.fcm500_litre = zone_sales.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
                            dszs.fcm500_cost = zone_sales.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum']
                            dszs.fcm500_unit_price = zone_sales.aggregate(Sum('fcm500_unit_price'))[
                                'fcm500_unit_price__sum']

                        if getattr(DailySessionllyBusinessTypellySale, 'fcm1000_pkt', True):
                            dszs.fcm1000_pkt = zone_sales.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
                            dszs.fcm1000_litre = zone_sales.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
                            dszs.fcm1000_cost = zone_sales.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum']
                            dszs.fcm1000_unit_price = zone_sales.aggregate(Sum('fcm1000_unit_price'))[
                                'fcm1000_unit_price__sum']
                            
                        if getattr(DailySessionllyZonallySale, 'tea500_pkt', True):
                            dszs.tea500_pkt = zone_sales.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
                            dszs.tea500_litre = zone_sales.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
                            dszs.tea500_cost = zone_sales.aggregate(Sum('tea500_cost'))['tea500_cost__sum']
                            dszs.tea500_unit_price = zone_sales.aggregate(Sum('tea500_unit_price'))[
                                'tea500_unit_price__sum']

                        if getattr(DailySessionllyBusinessTypellySale, 'tea1000_pkt', True):
                            dszs.tea1000_pkt = zone_sales.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
                            dszs.tea1000_litre = zone_sales.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
                            dszs.tea1000_cost = zone_sales.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum']
                            dszs.tea1000_unit_price = zone_sales.aggregate(Sum('tea1000_unit_price'))[
                                'tea1000_unit_price__sum']    

                        if getattr(DailySessionllyZonallySale, 'tmcan', True):
                            dszs.tmcan = zone_sales.aggregate(Sum('tmcan'))['tmcan__sum']
                            dszs.tmcan_litre = zone_sales.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
                            dszs.tmcan_cost = zone_sales.aggregate(Sum('tmcan_cost'))['tmcan_cost__sum']
                            dszs.tmcan_unit_price = zone_sales.aggregate(Sum('tmcan_unit_price'))[
                                'tmcan_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'smcan', True):
                            dszs.smcan = zone_sales.aggregate(Sum('smcan'))['smcan__sum']
                            dszs.smcan_litre = zone_sales.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
                            dszs.smcan_cost = zone_sales.aggregate(Sum('smcan_cost'))['smcan_cost__sum']
                            dszs.smcan_unit_price = zone_sales.aggregate(Sum('smcan_unit_price'))[
                                'smcan_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'fcmcan', True):
                            dszs.fcmcan = zone_sales.aggregate(Sum('fcmcan'))['fcmcan__sum']
                            dszs.fcmcan_litre = zone_sales.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
                            dszs.fcmcan_cost = zone_sales.aggregate(Sum('fcmcan_cost'))['fcmcan_cost__sum']
                            dszs.fcmcan_unit_price = zone_sales.aggregate(Sum('fcmcan_unit_price'))[
                                'fcmcan_unit_price__sum']

                        # Curd
                        if getattr(DailySessionllyZonallySale, 'curd500_pkt', True):
                            dszs.curd500_pkt = zone_sales.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
                            dszs.curd500_kgs = zone_sales.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
                            dszs.curd500_cost = zone_sales.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
                            dszs.curd500_unit_price = zone_sales.aggregate(Sum('curd500_unit_price'))[
                                'curd500_unit_price__sum']
                            
                        if getattr(DailySessionllyZonallySale, 'curd5000_pkt', True):
                            dszs.curd5000_pkt = zone_sales.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
                            dszs.curd5000_kgs = zone_sales.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
                            dszs.curd5000_cost = zone_sales.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
                            dszs.curd5000_unit_price = zone_sales.aggregate(Sum('curd5000_unit_price'))[
                                'curd5000_unit_price__sum']    

                        if getattr(DailySessionllyZonallySale, 'curd150_pkt', True):
                            dszs.curd150_pkt = zone_sales.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
                            dszs.curd150_kgs = zone_sales.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
                            dszs.curd150_cost = zone_sales.aggregate(Sum('curd150_cost'))['curd150_cost__sum']
                            dszs.curd150_unit_price = zone_sales.aggregate(Sum('curd150_unit_price'))[
                                'curd150_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'cupcurd_box', True):
                            dszs.cupcurd_box = zone_sales.aggregate(Sum('cupcurd_box'))['cupcurd_box__sum']
                            dszs.cupcurd_count = zone_sales.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
                            dszs.cupcurd_kgs = zone_sales.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
                            dszs.cupcurd_cost = zone_sales.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum']
                            dszs.cupcurd_unit_price = zone_sales.aggregate(Sum('cupcurd_unit_price'))[
                                'cupcurd_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'curd_bucket', True):
                            dszs.curd_bucket = zone_sales.aggregate(Sum('curd_bucket'))['curd_bucket__sum']
                            dszs.curd_bucket_kgs = zone_sales.aggregate(Sum('curd_bucket_kgs'))['curd_bucket_kgs__sum']
                            dszs.curd_bucket_cost = zone_sales.aggregate(Sum('curd_bucket_cost'))[
                                'curd_bucket_cost__sum']
                            dszs.curd_bucket_unit_price = zone_sales.aggregate(Sum('curd_bucket_unit_price'))[
                                'curd_bucket_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'lassi200_pkt', True):
                            dszs.lassi200_pkt = zone_sales.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
                            dszs.lassi200_kgs = zone_sales.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
                            dszs.lassi200_cost = zone_sales.aggregate(Sum('lassi200_cost'))['lassi200_cost__sum']
                            dszs.lassi200_unit_price = zone_sales.aggregate(Sum('lassi200_unit_price'))[
                                'lassi200_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'buttermilk200_pkt', True):
                            dszs.buttermilk200_pkt = zone_sales.aggregate(Sum('buttermilk200_pkt'))[
                                'buttermilk200_pkt__sum']
                            dszs.buttermilk200_litre = zone_sales.aggregate(Sum('buttermilk200_litre'))[
                                'buttermilk200_litre__sum']
                            dszs.buttermilk200_cost = zone_sales.aggregate(Sum('buttermilk200_cost'))[
                                'buttermilk200_cost__sum']
                            dszs.buttermilk200_unit_price = zone_sales.aggregate(Sum('buttermilk200_unit_price'))[
                                'buttermilk200_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'bm_jar200_pkt', True):
                            dszs.bm_jar200_pkt = zone_sales.aggregate(Sum('bm_jar200_pkt'))[
                                'bm_jar200_pkt__sum']
                            dszs.bm_jar200_litre = zone_sales.aggregate(Sum('bm_jar200_litre'))[
                                'bm_jar200_litre__sum']
                            dszs.bm_jar200_cost = zone_sales.aggregate(Sum('bm_jar200_cost'))[
                                'bm_jar200_cost__sum']
                            dszs.bm_jar200_unit_price = zone_sales.aggregate(Sum('bm_jar200_unit_price'))[
                                'bm_jar200_unit_price__sum']

                        if getattr(DailySessionllyZonallySale, 'bmjf200_pkt', True):
                            dszs.bmjf200_pkt = zone_sales.aggregate(Sum('bmjf200_pkt'))[
                                'bmjf200_pkt__sum']
                            dszs.bmjf200_litre = zone_sales.aggregate(Sum('bmjf200_litre'))[
                                'bmjf200_litre__sum']
                            dszs.bmjf200_cost = zone_sales.aggregate(Sum('bmjf200_cost'))[
                                'bmjf200_cost__sum']
                            dszs.bmjf200_unit_price = zone_sales.aggregate(Sum('bmjf200_unit_price'))[
                                'bmjf200_unit_price__sum']

                        dszs.tm_litre = zone_sales.aggregate(Sum('tm_litre'))['tm_litre__sum']
                        dszs.tm_cost = zone_sales.aggregate(Sum('tm_cost'))['tm_cost__sum']
                        dszs.sm_litre = zone_sales.aggregate(Sum('sm_litre'))['sm_litre__sum']
                        dszs.sm_cost = zone_sales.aggregate(Sum('sm_cost'))['sm_cost__sum']
                        dszs.fcm_litre = zone_sales.aggregate(Sum('fcm_litre'))['fcm_litre__sum']
                        dszs.fcm_cost = zone_sales.aggregate(Sum('fcm_cost'))['fcm_cost__sum']
                        dszs.tea_litre = zone_sales.aggregate(Sum('tea_litre'))['tea_litre__sum']
                        dszs.tea_cost = zone_sales.aggregate(Sum('tea_cost'))['tea_cost__sum']
                        dszs.milk_litre = zone_sales.aggregate(Sum('milk_litre'))['milk_litre__sum']
                        dszs.milk_cost = zone_sales.aggregate(Sum('milk_cost'))['milk_cost__sum']
                        dszs.curd_kgs = zone_sales.aggregate(Sum('curd_kgs'))['curd_kgs__sum']
                        dszs.curd_cost = zone_sales.aggregate(Sum('curd_cost'))['curd_cost__sum']
                        dszs.buttermilk_cost = zone_sales.aggregate(Sum('buttermilk_cost'))['buttermilk_cost__sum']
                        dszs.buttermilk_litre = zone_sales.aggregate(Sum('buttermilk_litre'))['buttermilk_litre__sum']
                        dszs.lassi_litre = zone_sales.aggregate(Sum('lassi_litre'))['lassi_litre__sum']
                        dszs.lassi_cost = zone_sales.aggregate(Sum('lassi_cost'))['lassi_cost__sum']
                        dszs.fermented_products_litre = zone_sales.aggregate(Sum('fermented_products_litre'))[
                            'fermented_products_litre__sum']
                        dszs.fermented_products_cost = zone_sales.aggregate(Sum('fermented_products_cost'))[
                            'fermented_products_cost__sum']
                        dszs.total_litre = zone_sales.aggregate(Sum('total_litre'))['total_litre__sum']

                        dszs.save()

