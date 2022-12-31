from django.http import response
from django.shortcuts import render
import calendar 
# authentication
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, logout, login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
# Create your views here.
from django.db.models import Max
from collections import defaultdict, OrderedDict, Counter
# creating views for REST / function based views
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
import random
# import plivo
from main.models import *
from report.models import *
from by_products.models import *
import pandas as pd
from decimal import Decimal
from datetime import timedelta, date
from datetime import datetime
import dateutil.relativedelta
from base64 import b64encode, b64decode
#  Plivo credentials
# import plivo
from random import randint
from base64 import b64decode, b64encode
from django.core.files.base import ContentFile
from django.db.models import Sum, Max
from pytz import timezone
from django.db.models import Sum
import pytz
indian = pytz.timezone('Asia/Kolkata')
from calendar import monthrange, month_name

# canvas
import os
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from main.temp_pdf_generate import generate_pdf_for_merging_temp_with_main
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from main.views import serve_product_and_session_list
from num2words import num2words
from PyPDF2 import PdfFileMerger
import dbf
import math
auth_id = "MAZJZINTYZZTQ4MTG0MT"
auth_token = "NWJkN2Q5MGM2OGI2Njc1MGM3NzMzMmMyZjQyYWIw"
import numpy as np



@api_view(['POST'])
def generate_pdf_code_for_cash_finace_report(request):
    print(request.data)
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(order_category_id=1, payment_option_id=1).order_by('business_type_id').values_list('business_type_id', flat=True))
    data_dict = {
        'counter_wise': {},
        'counter_wise_product':{},
        'product_wise': {}
    }
    counter_obj = Counter.objects.filter(is_included_in_cash_collection_report=True).order_by('id')
    counter_list = list(counter_obj.values_list('id', 'name', 'finance_sub_code'))
    counter_column = ['id', 'counter_name', 'finance_sub_code']
    counter_df = pd.DataFrame(counter_list, columns=counter_column)
    counter_list = counter_df.to_dict('r')
    # finace product with code
    product_finance_map_obj = ProductFinanceCodeMap.objects.filter()
    # main product list
    product_finance_map_main_list = list(product_finance_map_obj.values())

    product_finance_map_list = list(product_finance_map_obj.values_list('id', 'group_name', 'product', 'product__code'))
    product_finance_map_column = ['id', 'group_name', 'product', 'product_name']
    product_finance_map_df = pd.DataFrame(product_finance_map_list, columns=product_finance_map_column)
    product_finance_map_dict = product_finance_map_df.groupby('id').apply(lambda x: x.to_dict('r')).to_dict()
    # group wise product ids
    product_finance_map_sub_list = product_finance_map_df.groupby('id')['product'].apply(list).to_dict()
    # credit_sale_booth__code = ['2682', '82115']

    # calculate total counter wise
    master_dict = {}
    product_wise_total = {'total': 0}
    sale_list = []
    for index, row in counter_df.iterrows():
        if not row['id'] in master_dict:
            master_dict[row['id']] = {}
        counter_employee_trace_ids = list(CounterEmployeeTraceMap.objects.filter(counter_id=row['id'],
                                                                                 collection_date__gte=from_date, collection_date__lte=to_date).values_list(
            'id', flat=True))
        counter_sale_group_ids = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
            counter_employee_trace_id__in=counter_employee_trace_ids).values_list('sale_group', flat=True))
        if not row['id'] == 23:
            sale_obj = Sale.objects.filter(sale_group_id__in=counter_sale_group_ids)
        else:    
            sale_group_ids = list(SaleGroup.objects.filter(time_created__date__gte=from_date, time_created__date__lte=to_date, ordered_via_id__in=[1,3], business_type_id__in=business_type_ids).values_list('id', flat=True))
            sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids)
        # if row['id'] == 8:
        #     sale_obj = sale_obj.filter(sale_group__route_id__in=[119, 118])
        sale_ids_list = list(sale_obj.values_list('id', flat=True))
        sale_list = sale_list + sale_ids_list
        total_cost = 0
        for finance_product in product_finance_map_main_list:
            if not finance_product['id'] in product_wise_total:
                product_wise_total[finance_product['id']] = 0
            if not finance_product['id'] in master_dict[row['id']]:
                master_dict[row['id']][finance_product['id']] = 0
            product_obj = sale_obj.filter(product_id__in=product_finance_map_sub_list[finance_product['id']])
            if not product_obj.aggregate(Sum('cost'))['cost__sum'] is None:
                master_dict[row['id']][finance_product['id']] = product_obj.aggregate(Sum('cost'))['cost__sum']
            if not product_obj.aggregate(Sum('cost'))['cost__sum'] is None:
                total_cost += product_obj.aggregate(Sum('cost'))['cost__sum']
                product_wise_total['total'] += product_obj.aggregate(Sum('cost'))['cost__sum']
                product_wise_total[finance_product['id']] += product_obj.aggregate(Sum('cost'))['cost__sum']
        master_dict[row['id']]['total'] = total_cost

    data_dict['counter_wise'] = master_dict
    data_dict['counter_wise_product'] = product_wise_total

    # calculate total for product group wise
    total_sale_in_litre_wise = {
        'milk': {'total': {'amount': 0, 'litre': 0}},
        'curd': {'total': {'amount': 0, 'litre': 0}, 'wsd': {'total': {'amount': 0, 'litre': 0}}, 'rtd': {'total': {'amount': 0, 'litre': 0}}},
        'butter_milk': {'total': {'amount': 0, 'litre': 0}}
    }
    all_sale_obj = Sale.objects.filter(id__in=sale_list)

    # MILK
    for product_id in product_finance_map_sub_list[1]:
        default_product_obj = Product.objects.get(id=product_id)
        if not product_id in total_sale_in_litre_wise['milk']:
            total_sale_in_litre_wise['milk'][product_id] = {
                'litre': 0,
                'amount': 0
            }
        product_sale_obj = all_sale_obj.filter(product_id=product_id)
        total_quantity = product_sale_obj.aggregate(Sum('count'))['count__sum']
        if total_quantity is None:
            total_quantity = 0
        total_amount = product_sale_obj.aggregate(Sum('cost'))['cost__sum']
        if total_amount is None:
            total_amount = 0
        total_sale_in_litre_wise['milk'][product_id]['litre'] = Decimal(total_quantity) * default_product_obj.quantity / 1000
        total_sale_in_litre_wise['milk'][product_id]['amount'] = total_amount
        total_sale_in_litre_wise['milk']['total']['litre'] += total_sale_in_litre_wise['milk'][product_id]['litre']
        total_sale_in_litre_wise['milk']['total']['amount'] += total_sale_in_litre_wise['milk'][product_id]['amount']

    # CURD
    for curd_product_id in product_finance_map_sub_list[2]:
        default_product_obj = Product.objects.get(id=curd_product_id)
        if not curd_product_id in total_sale_in_litre_wise['curd']['wsd']:
            total_sale_in_litre_wise['curd']['wsd'][curd_product_id] = {
                'litre': 0,
                'amount': 0
            }
        if not curd_product_id in total_sale_in_litre_wise['curd']['rtd']:
            total_sale_in_litre_wise['curd']['rtd'][curd_product_id] = {
                'litre': 0,
                'amount': 0
            }
        if not curd_product_id in total_sale_in_litre_wise['curd']:
            total_sale_in_litre_wise['curd'][curd_product_id] = {
                'litre': 0,
                'amount': 0
            }
        product_sale_obj = all_sale_obj.filter(product_id=curd_product_id)
        wsd_sale_obj = product_sale_obj.filter(sale_group__business__business_type_id=9)
        total_quantity = wsd_sale_obj.aggregate(Sum('count'))['count__sum']
        if total_quantity is None:
            total_quantity = 0
        total_amount = wsd_sale_obj.aggregate(Sum('cost'))['cost__sum']
        if total_amount is None:
            total_amount = 0
        total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['litre'] = Decimal(total_quantity) * default_product_obj.quantity / 1000
        total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['amount'] = total_amount
        total_sale_in_litre_wise['curd']['wsd']['total']['litre'] += total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['litre']
        total_sale_in_litre_wise['curd']['wsd']['total']['amount'] += total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['amount']
        #     retail users
        rtd_sale_obj = product_sale_obj.filter().exclude(sale_group__business__business_type_id=9)
        total_quantity = rtd_sale_obj.aggregate(Sum('count'))['count__sum']
        if total_quantity is None:
            total_quantity = 0
        total_amount = rtd_sale_obj.aggregate(Sum('cost'))['cost__sum']
        if total_amount is None:
            total_amount = 0
        total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['litre'] = Decimal(total_quantity) * default_product_obj.quantity / 1000
        total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['amount'] = total_amount

        total_sale_in_litre_wise['curd']['rtd']['total']['litre'] += total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['litre']
        total_sale_in_litre_wise['curd']['rtd']['total']['amount'] += total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['amount']

        total_sale_in_litre_wise['curd'][curd_product_id]['litre'] = total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['litre'] + total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['litre']
        total_sale_in_litre_wise['curd'][curd_product_id]['amount'] = total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['amount'] + total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['amount']

        # total
        total_sale_in_litre_wise['curd']['total']['litre'] += total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['litre'] + total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['litre']
        total_sale_in_litre_wise['curd']['total']['amount'] += total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['amount'] + total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['amount']

    # BUTTER MILK
    for butter_milk_product_id in product_finance_map_sub_list[3]:
        default_product_obj = Product.objects.get(id=butter_milk_product_id)
        if not butter_milk_product_id in total_sale_in_litre_wise['butter_milk']:
            total_sale_in_litre_wise['butter_milk'][butter_milk_product_id] = {
                'litre': 0,
                'amount': 0
            }
        product_sale_obj = all_sale_obj.filter(product_id=butter_milk_product_id)
        total_quantity = product_sale_obj.aggregate(Sum('count'))['count__sum']
        if total_quantity is None:
            total_quantity = 0
        total_amount = product_sale_obj.aggregate(Sum('cost'))['cost__sum']
        if total_amount is None:
            total_amount = 0
        total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['litre'] = Decimal(total_quantity) * default_product_obj.quantity / 1000
        total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['amount'] = total_amount
        total_sale_in_litre_wise['butter_milk']['total']['litre'] += total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['litre']
        total_sale_in_litre_wise['butter_milk']['total']['amount'] += total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['amount']
    data_dict['product_wise'] = total_sale_in_litre_wise
    data = create_canvas_for_finace_report(from_date, to_date, data_dict, counter_list, product_finance_map_main_list, product_finance_map_dict, request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_for_finace_report(from_date, to_date, data_dict, counter_list, product_finance_map_main_list, product_finance_map_dict, user_name):
    file_name = str(from_date) + '_to_' + str(to_date) + 'counter_sale_summary_cash' + '.pdf'
    indian = pytz.timezone('Asia/Kolkata')
    #     file_path = os.path.join('static/media/route_wise_report/', file_name)
    file_path = os.path.join('static/media/zone_wise_report', file_name)
#     file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.drawCentredString(300, 800, 'Daily Counter Sale Summary For Cash Sale : Total Sales')
    mycanvas.setFont('Helvetica', 12)
   
    x_a4 = 30
   
    mycanvas.drawString(40-x_a4, 770, 'Debit : 10901')
    mycanvas.setFont('Helvetica', 12)
    from_date = datetime.strptime(str(from_date)[:10], '%Y-%m-%d')
    to_date = datetime.strptime(str(to_date)[:10], '%Y-%m-%d')
    mycanvas.drawCentredString(500-x_a4,770, "Sale For DATE : " + str(datetime.strftime(from_date, '%d/%m/%Y'))+" TO "+str(datetime.strftime(to_date, '%d/%m/%Y')))
    mycanvas.setFont('Helvetica', 10)
    mycanvas.line(40-x_a4, 760, 585, 760)
    mycanvas.line(40-x_a4, 730, 585, 730)
    mycanvas.drawString(45-x_a4, 740, 'S No')
    mycanvas.drawString(80-x_a4, 740, 'Counter Name')
    mycanvas.drawString(210-x_a4, 740, 'Acc Code')
    mycanvas.drawString(310-x_a4, 740, 'Milk')
    mycanvas.drawString(400-x_a4, 740, 'Curd')
    mycanvas.drawString(480-x_a4, 740, 'B Milk')
    mycanvas.drawString(570-x_a4, 740, 'Total')


    y_for_counter_name = 710
    serial_number = 0
    for counter in counter_list:
        serial_number += 1
        mycanvas.drawString(50-x_a4, y_for_counter_name, str(serial_number))
        mycanvas.drawString(80-x_a4, y_for_counter_name, str(counter['counter_name']))
        mycanvas.drawString(210-x_a4, y_for_counter_name, str(counter['finance_sub_code']))
        x_for_sale = 448-x_a4
        x_adjust = 0
        for product in product_finance_map_main_list:
            if product['id'] == 3 or product["id"] == '3':
                x_adjust += 20
            mycanvas.drawRightString(x_for_sale-80-20-x_adjust, y_for_counter_name, str(data_dict['counter_wise'][counter['id']][product['id']]))
            x_for_sale += 100
            x_adjust += 10
               
        mycanvas.drawRightString(x_for_sale+12-150, y_for_counter_name, str(data_dict['counter_wise'][counter['id']]['total']))
        y_for_counter_name -= 15
       
    x_for_sale = 448-x_a4
    mycanvas.drawString(300-x_a4-80, y_for_counter_name - 10, 'Total')
    x_adjust = 0
    for product in product_finance_map_main_list:
        if product['id'] == 3 or product["id"] == '3':
            x_adjust += 20
        mycanvas.drawRightString(x_for_sale-80-20-x_adjust, y_for_counter_name - 10, str(data_dict['counter_wise_product'][product['id']]))
        x_for_sale += 100
        x_adjust += 10
    mycanvas.drawRightString(x_for_sale+12-150, y_for_counter_name - 10, str(data_dict['counter_wise_product']['total']))
   
    mycanvas.line(40-x_a4, y_for_counter_name+10, 585, y_for_counter_name+10)
    mycanvas.line(70-x_a4, y_for_counter_name+10, 70-x_a4, 760)
    mycanvas.line(40-x_a4, y_for_counter_name+10, 40-x_a4, 760)
    y_for_counter_name -= 20
    mycanvas.line(200-x_a4, y_for_counter_name, 585, y_for_counter_name)
    mycanvas.line(200-x_a4, y_for_counter_name, 200-x_a4, 760)
    mycanvas.line(350-x_a4-90, y_for_counter_name, 350-x_a4-90, 760)
    mycanvas.line(460-x_a4-105, y_for_counter_name, 460-x_a4-105, 760)
    mycanvas.line(560-x_a4-115, y_for_counter_name, 560-x_a4-115, 760)
    mycanvas.line(660-x_a4-145, y_for_counter_name, 660-x_a4-145, 760)
    mycanvas.line(770-x_a4-155, y_for_counter_name, 770-x_a4-155, 760)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    y_for_counter_name -= 35
    mycanvas.setFont('Helvetica', 13)
    mycanvas.drawCentredString(300, y_for_counter_name, 'Daily Sale Quantity : Milk')
    y_for_counter_name -= 10
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(40-x_a4, y_for_counter_name, 'Milk Sale : 30101')
    mycanvas.setFont('Helvetica', 10)
    y_for_counter_name -= 10
    mycanvas.line(40-x_a4, y_for_counter_name, 590, y_for_counter_name)
    start_of_milk_heading_line = y_for_counter_name
    y_for_counter_name -= 25
    mycanvas.line(40-x_a4, y_for_counter_name, 590, y_for_counter_name)

    y_for_counter_name = y_for_counter_name + 10
    start_x_for_milk_product = 100-x_a4
    x_adjust = 15
    for product in product_finance_map_dict[1]:
        mycanvas.drawString(start_x_for_milk_product+40-x_adjust, y_for_counter_name, str(product['product_name']))
        start_x_for_milk_product += 45
        x_adjust += -5
    mycanvas.drawString(start_x_for_milk_product+55-x_adjust, y_for_counter_name, 'Total')
    #     retaill litre
    y_for_counter_name -= 25
    mycanvas.drawString(15, y_for_counter_name, 'Retail(Litre)')
    start_x_for_milk_product = 220-x_a4
    x_adjust = 15
    for product in product_finance_map_dict[1]:
        mycanvas.drawRightString(start_x_for_milk_product-x_a4-10-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk'][product['product']]['litre']))
        start_x_for_milk_product += 49
        x_adjust += 0
    mycanvas.drawRightString(start_x_for_milk_product-32-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk']['total']['litre']))
    #     retaill amount
    y_for_counter_name -= 20
    mycanvas.drawString(15, y_for_counter_name, 'Retail(Amount)')
    start_x_for_milk_product = 220-x_a4
    x_adjust = 15
    for product in product_finance_map_dict[1]:
        mycanvas.drawRightString(start_x_for_milk_product-x_a4-10-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk'][product['product']]['amount']))
        start_x_for_milk_product += 55
        x_adjust += 5
    mycanvas.drawRightString(start_x_for_milk_product-39-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk']['total']['amount']))
    y_for_counter_name -= 15
   
   
    mycanvas.line(40-x_a4, y_for_counter_name, 590, y_for_counter_name)
    mycanvas.line(40-x_a4, y_for_counter_name, 40-x_a4, start_of_milk_heading_line)
    mycanvas.line(115-x_a4, y_for_counter_name, 115-x_a4, start_of_milk_heading_line)
    start_for_milk_sale_line = 220-x_a4
    x_adjust = 17
    for product in product_finance_map_dict[1]:
        mycanvas.line(start_for_milk_sale_line-x_a4-5-x_adjust, y_for_counter_name, start_for_milk_sale_line-x_a4-5-x_adjust, start_of_milk_heading_line)
        start_for_milk_sale_line += 50
        x_adjust += 0
    mycanvas.line(590, y_for_counter_name, 590, start_of_milk_heading_line)
   
   
#--------------------------------------------------------------------------------------------------------------------------------------------#
    #     Curd
    y_for_counter_name -= 30
    mycanvas.setFont('Helvetica', 13)
    mycanvas.drawCentredString(300, y_for_counter_name, 'Daily Sale Quantity : Curd')
    y_for_counter_name -= 10
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(40-x_a4, y_for_counter_name, 'Curd Sale : 30201')
    mycanvas.setFont('Helvetica', 10)
    y_for_counter_name -= 10
    mycanvas.line(40-x_a4, y_for_counter_name, 600-x_a4, y_for_counter_name)
    start_of_milk_heading_line = y_for_counter_name
    y_for_counter_name -= 25
    mycanvas.line(40-x_a4, y_for_counter_name, 600-x_a4, y_for_counter_name)

    y_for_counter_name = y_for_counter_name + 10
    start_x_for_milk_product = 180-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.drawString(start_x_for_milk_product, y_for_counter_name, str(product['product_name']))
        start_x_for_milk_product += 100
    mycanvas.drawString(start_x_for_milk_product + 10, y_for_counter_name, 'Total')

    y_for_counter_name -= 25
    mycanvas.drawString(50-x_a4, y_for_counter_name, 'Retail(Litre)')
    start_x_for_milk_product = 245-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['rtd'][product['product']]['litre']))
        start_x_for_milk_product += 100
    mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['rtd']['total']['litre']))
    #     retaill amount
    y_for_counter_name -= 20
    mycanvas.drawString(50-x_a4, y_for_counter_name, 'Retail(Amount)')
    start_x_for_milk_product = 245-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['rtd'][product['product']]['amount']))
        start_x_for_milk_product += 100
    mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['rtd']['total']['amount']))
    y_for_counter_name -= 15

    #     WSD
    y_for_counter_name -= 5
    mycanvas.drawString(50-x_a4, y_for_counter_name, 'WSD(Litre)')
    start_x_for_milk_product = 245-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['wsd'][product['product']]['litre']))
        start_x_for_milk_product += 100
    mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['wsd']['total']['litre']))
    #     retaill amount
    y_for_counter_name -= 20
    mycanvas.drawString(50-x_a4, y_for_counter_name, 'WSD(Amount)')
    start_x_for_milk_product = 245-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['wsd'][product['product']]['amount']))
        start_x_for_milk_product += 100
    mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['wsd']['total']['amount']))

    mycanvas.line(40-x_a4, y_for_counter_name-10, 600-x_a4, y_for_counter_name-10)

    y_for_counter_name -= 25
    mycanvas.drawString(50-x_a4, y_for_counter_name, 'Total(Litre)')
    start_x_for_milk_product = 245-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd'][product['product']]['litre']))
        start_x_for_milk_product += 100
    mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['total']['litre']))
    #     retaill amount
    y_for_counter_name -= 20
    mycanvas.drawString(50-x_a4, y_for_counter_name, 'Total(Amount)')
    start_x_for_milk_product = 245-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd'][product['product']]['amount']))
        start_x_for_milk_product += 100
    mycanvas.drawRightString(start_x_for_milk_product, y_for_counter_name, str(data_dict['product_wise']['curd']['total']['amount']))

    y_for_counter_name -= 15
    mycanvas.line(40-x_a4, y_for_counter_name, 40-x_a4, start_of_milk_heading_line)
    mycanvas.line(160-x_a4, y_for_counter_name, 160-x_a4, start_of_milk_heading_line)
    start_for_milk_sale_line = 255-x_a4
    for product in product_finance_map_dict[2]:
        mycanvas.line(start_for_milk_sale_line, y_for_counter_name, start_for_milk_sale_line, start_of_milk_heading_line)
        start_for_milk_sale_line += 100
    mycanvas.line(600-x_a4, y_for_counter_name, 600-x_a4, start_of_milk_heading_line)
    mycanvas.line(40-x_a4, y_for_counter_name, 600-x_a4, y_for_counter_name)

#-----------------------------------------------------------------------------------------------------------------------------------------#
    y_for_counter_name -= 30
    mycanvas.setFont('Helvetica', 13)
    mycanvas.drawString(40-x_a4, y_for_counter_name, 'Daily Sale Quantity : ButterMilk')
    y_for_counter_name -= 25
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(40-x_a4, y_for_counter_name, 'Butter Milk Sale : 30202')
    mycanvas.setFont('Helvetica', 10)
    y_for_counter_name -= 10
    mycanvas.line(40-x_a4, y_for_counter_name, 350-x_a4, y_for_counter_name)
    start_of_milk_heading_line = y_for_counter_name
    y_for_counter_name -= 25
    mycanvas.line(40-x_a4, y_for_counter_name, 350-x_a4, y_for_counter_name)

    y_for_counter_name = y_for_counter_name + 10
    start_x_for_milk_product = 170-x_a4
    for product in product_finance_map_dict[3]:
        mycanvas.drawString(start_x_for_milk_product-30, y_for_counter_name, str(product['product_name']))
        start_x_for_milk_product += 60
    mycanvas.drawString(start_x_for_milk_product-50, y_for_counter_name, 'Total')
    #     retaill litre
    y_for_counter_name -= 30
    mycanvas.drawString(12, y_for_counter_name, 'Retail(Litre)')
    start_x_for_milk_product = 227-x_a4
    for product in product_finance_map_dict[3]:
        mycanvas.drawRightString(start_x_for_milk_product-54, y_for_counter_name, str(data_dict['product_wise']['butter_milk'][product['product']]['litre']))
        start_x_for_milk_product += 60
    mycanvas.drawRightString(start_x_for_milk_product-60, y_for_counter_name, str(data_dict['product_wise']['butter_milk']['total']['litre']))
    #     retaill amount
    y_for_counter_name -= 30
    mycanvas.drawString(12, y_for_counter_name, 'Retail(Amount)')
    start_x_for_milk_product = 213-x_a4
    for product in product_finance_map_dict[3]:
        mycanvas.drawRightString(start_x_for_milk_product-40, y_for_counter_name, str(data_dict['product_wise']['butter_milk'][product['product']]['amount']))
        start_x_for_milk_product += 60
    mycanvas.drawRightString(start_x_for_milk_product-50, y_for_counter_name, str(data_dict['product_wise']['butter_milk']['total']['amount']))
    y_for_counter_name -= 20
    mycanvas.line(40-x_a4, y_for_counter_name, 350-x_a4, y_for_counter_name)
    mycanvas.line(40-x_a4, y_for_counter_name, 40-x_a4, start_of_milk_heading_line)
    mycanvas.line(130-x_a4, y_for_counter_name, 130-x_a4, start_of_milk_heading_line)
    start_for_milk_sale_line = 235-x_a4
    for product in product_finance_map_dict[3]:
        mycanvas.line(start_for_milk_sale_line-40, y_for_counter_name, start_for_milk_sale_line-40, start_of_milk_heading_line)
        start_for_milk_sale_line += 50
    mycanvas.line(350-x_a4, y_for_counter_name, 350-x_a4, start_of_milk_heading_line)
   
   
    # milk_type_wise_total
    mycanvas.setFont('Helvetica', 13)
    x_adj = 150
    mycanvas.drawCentredString(595-x_adj, y_for_counter_name+125, 'Daily Sale Amount : Total')
    mycanvas.setFont('Helvetica', 10)
    mycanvas.line(540-x_adj,y_for_counter_name+110,730-x_adj,y_for_counter_name+110)
    mycanvas.line(540-x_adj,y_for_counter_name+20,730-x_adj,y_for_counter_name+20)
   
    mycanvas.line(540-x_adj,y_for_counter_name+110,540-x_adj,y_for_counter_name+20)
    mycanvas.line(730-x_adj,y_for_counter_name+110,730-x_adj,y_for_counter_name)
   
    mycanvas.line(630-x_adj,y_for_counter_name+110,630-x_adj,y_for_counter_name)
    mycanvas.line(630-x_adj,y_for_counter_name,730-x_adj,y_for_counter_name)
   
    mycanvas.drawString(560-x_adj,y_for_counter_name+85,"30101")
    mycanvas.drawRightString(710-x_adj,y_for_counter_name+85,str(data_dict['product_wise']['milk']['total']['amount']))
   
    mycanvas.drawString(560-x_adj,y_for_counter_name+60,"30201")
    mycanvas.drawRightString(710-x_adj,y_for_counter_name+60,str(data_dict['product_wise']['curd']['total']['amount']))
   
    mycanvas.drawString(560-x_adj,y_for_counter_name+35,"30202")
    mycanvas.drawRightString(710-x_adj,y_for_counter_name+35,str(data_dict['product_wise']['butter_milk']['total']['amount']))
   
    mycanvas.drawRightString(710-x_adj,y_for_counter_name+5,str(data_dict['counter_wise_product']['total']))
   
   
    mycanvas.drawRightString(585, 10, 'Report Generated by: '+str(user_name+", @"+str(datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

    mycanvas.save()
    document = {}
    document['file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document



@api_view(['POST'])
def generate_pdf_code_for_total_milk_sale(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    date_list = pd.date_range(start=from_date,end=to_date)
    data_dict = {
        "product":{
            "tm":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "TIRUPPUR Leakage":0,
                "Returned" : 0,
                "Net Recived" : 0
            },
            "std500":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "TIRUPPUR Leakage":0,
                "Returned" : 0,
                "Net Recived" : 0
            },
            "std250":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "TIRUPPUR Leakage":0,
                "Returned" : 0,
                "Net Recived" : 0
            },
            "fcm":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "TIRUPPUR Leakage":0,
                "Returned" : 0,
                "Net Recived" : 0
            },
            "tmate":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "TIRUPPUR Leakage":0,
                "Returned" : 0,
                "Net Recived" : 0
            },
        },
        "union_sale" : {},
        "Coimbatore Account" : {
            "Agent Cash":{
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            },
            "Agent Card" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            },
            "Union Booth Cash" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            },
            "Union Booth Card" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            },
            "Pvt Institutes" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            },
            "Govt Institutes" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            },
            "Society" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            },
            "Can Milk Buyer" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total": 0
            },
            "Kerala" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total": 0
            },
            "Kerala" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total": 0
            },
            "No Commission Booth" : {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total": 0
            },
        },
        "Costs" : {
            "product":{
                "tm":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0
                },
                "std500":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0
                },
                "std250":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0
                },
                "fcm":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0
                },
                "tmate":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0
                },
            },
            "union_sale" : {},
            "Coimbatore Account" : {
                "Agent Cash":{
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "Agent Card" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "Union Booth Cash" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "Union Booth Card" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "Pvt Institutes" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "Govt Institutes" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total": 0
                },
                "Society" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "Can Milk Buyer" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "Kerala" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
                "No Commission Booth" : {
                    "tm" : 0,
                    "std500" : 0,
                    "std250" : 0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "total":0
                },
            }
        }
    }
    tm_std_fcm_diary_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list)
    tm_std_fcm_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to__in = ["Agent","ICustomer"])
    tm_std_fcm_leake_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to="Leakage").exclude(union="TIRUPPUR Union")
    tm_std_fcm_trp_leake_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to="Leakage",union="TIRUPPUR Union")

    #dairy sale (icus + agent + leakage)
    # for can
    tm_can = tm_std_fcm_diary_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
    std_can = tm_std_fcm_diary_sale_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"]
    fcm_can = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"]
    if tm_can is None:
        tm_can = 0
    if std_can is None:
        std_can = 0
    if fcm_can is None:
        fcm_can = 0

    #for milk
    
    tm_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] 
    std500_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"] 
    std250_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    fcm_sale_500 = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    fcm_sale_1000 = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    tea_sale_500 = tm_std_fcm_diary_sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    tea_sale_1000 = tm_std_fcm_diary_sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if tm_sale is None:
        tm_sale = 0
    if std500_sale is None:
        std500_sale = 0
    if std250_sale is None:
        std250_sale = 0
    if fcm_sale_500 is None:
        fcm_sale_500 = 0
    if fcm_sale_1000 is None:
        fcm_sale_1000 = 0
    if tea_sale_500 is None:
        tea_sale_500 = 0
    if tea_sale_1000 is None:
        tea_sale_1000 = 0    

    fcm_sale = fcm_sale_500 + fcm_sale_1000 
    tea_sale = tea_sale_500 + tea_sale_1000 

    data_dict["product"]["tm"]["Resived From Diary"] = tm_sale + tm_can
    data_dict["product"]["std500"]["Resived From Diary"] = std500_sale + std_can
    data_dict["product"]["std250"]["Resived From Diary"] = std250_sale
    data_dict["product"]["fcm"]["Resived From Diary"] = fcm_sale + fcm_can
    data_dict["product"]["tmate"]["Resived From Diary"] = tea_sale

    #net_recived (icus + agent)
    tm_can = tm_std_fcm_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
    std_can = tm_std_fcm_sale_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"]
    fcm_can = tm_std_fcm_sale_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"]
    if tm_can is None:
        tm_can = 0
    if std_can is None:
        std_can = 0
    if fcm_can is None:
        fcm_can = 0

    tm_sale = tm_std_fcm_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] 
    std500_sale = tm_std_fcm_sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"] 
    std250_sale = tm_std_fcm_sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    fcm_sale_500 = tm_std_fcm_sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    fcm_sale_1000 = tm_std_fcm_sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    tea_sale_500 = tm_std_fcm_sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    tea_sale_1000 = tm_std_fcm_sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if tm_sale is None:
        tm_sale = 0
    if std500_sale is None:
        std500_sale = 0
    if std250_sale is None:
        std250_sale = 0
    if fcm_sale_500 is None:
        fcm_sale_500 = 0
    if fcm_sale_1000 is None:
        fcm_sale_1000 = 0
    if tea_sale_500 is None:
        tea_sale_500 = 0
    if tea_sale_1000 is None:
        tea_sale_1000 = 0    

    tm_sale = tm_sale + tm_can
    std500_sale = std500_sale + std_can

    fcm_sale = fcm_sale_500 + fcm_sale_1000 + fcm_can

    tea_sale = tea_sale_500 + tea_sale_1000

    data_dict["product"]["tm"]["Net Recived"] = tm_sale
    data_dict["product"]["std500"]["Net Recived"] = std500_sale
    data_dict["product"]["std250"]["Net Recived"] = std250_sale
    data_dict["product"]["fcm"]["Net Recived"] = fcm_sale
    data_dict["product"]["tmate"]["Net Recived"] = tea_sale

    #Tiruppur leakage
    trp_lk_tm_sale = tm_std_fcm_trp_leake_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    trp_lk_std500_sale = tm_std_fcm_trp_leake_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    trp_lk_std250_sale = tm_std_fcm_trp_leake_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]

    trp_lk_fcm_sale_500 = tm_std_fcm_trp_leake_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    trp_lk_fcm_sale_1000 = tm_std_fcm_trp_leake_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]

    trp_lk_tea_sale_500 = tm_std_fcm_trp_leake_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    trp_lk_tea_sale_1000 = tm_std_fcm_trp_leake_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]


    if trp_lk_tm_sale is None:
        trp_lk_tm_sale = 0
    if trp_lk_std500_sale is None:
        trp_lk_std500_sale = 0
    if trp_lk_std250_sale is None:
        trp_lk_std250_sale = 0
    if trp_lk_fcm_sale_500 is None:
        trp_lk_fcm_sale_500 = 0
    if trp_lk_fcm_sale_1000 is None:
        trp_lk_fcm_sale_1000 = 0
    if trp_lk_tea_sale_500 is None:
        trp_lk_tea_sale_500 = 0
    if trp_lk_tea_sale_1000 is None:
        trp_lk_tea_sale_1000 = 0


    trp_lk_fcm_sale = trp_lk_fcm_sale_500 + trp_lk_fcm_sale_1000
    trp_lk_tea_sale = trp_lk_tea_sale_500 + trp_lk_tea_sale_1000

    data_dict["product"]["tm"]["TIRUPPUR Leakage"] = trp_lk_tm_sale
    data_dict["product"]["std500"]["TIRUPPUR Leakage"] = trp_lk_std500_sale
    data_dict["product"]["std250"]["TIRUPPUR Leakage"] = trp_lk_std250_sale
    data_dict["product"]["fcm"]["TIRUPPUR Leakage"] = trp_lk_fcm_sale
    data_dict["product"]["tmate"]["TIRUPPUR Leakage"] = trp_lk_tea_sale
   
    #leakage
    lk_tm_sale = tm_std_fcm_leake_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    lk_std500_sale = tm_std_fcm_leake_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    lk_std250_sale = tm_std_fcm_leake_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    lk_fcm_sale_500 = tm_std_fcm_leake_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    lk_fcm_sale_1000 = tm_std_fcm_leake_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    lk_tea_sale_500 = tm_std_fcm_leake_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    lk_tea_sale_1000 = tm_std_fcm_leake_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if lk_tm_sale is None:
        lk_tm_sale = 0
    if lk_std500_sale is None:
        lk_std500_sale = 0
    if lk_std250_sale is None:
        lk_std250_sale = 0
    if lk_fcm_sale_500 is None:
        lk_fcm_sale_500 = 0
    if lk_fcm_sale_1000 is None:
        lk_fcm_sale_1000 = 0
    if lk_tea_sale_500 is None:
        lk_tea_sale_500 = 0
    if lk_tea_sale_1000 is None:
        lk_tea_sale_1000 = 0    

    lk_fcm_sale = lk_fcm_sale_500 + lk_fcm_sale_1000
    lk_tea_sale = lk_tea_sale_500 + lk_tea_sale_1000

    data_dict["product"]["tm"]["Leakage"] = lk_tm_sale
    data_dict["product"]["std500"]["Leakage"] = lk_std500_sale
    data_dict["product"]["std250"]["Leakage"] = lk_std250_sale
    data_dict["product"]["fcm"]["Leakage"] = lk_fcm_sale
    data_dict["product"]["tmate"]["Leakage"] = lk_tea_sale

    union_list = ["COIMBATORE Union","NILGIRIS Union","TIRUPPUR Union","CHENNAI Aavin"]

    for union in union_list:
        if not union in data_dict["union_sale"]:
            data_dict["union_sale"][union] = {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0
            }
        tm_std_fcm_union_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union=union,sold_to__in = ["Agent","ICustomer"])

        # union sale
        if tm_std_fcm_union_obj:
            union_tm_sale = tm_std_fcm_union_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            union_std500_sale = tm_std_fcm_union_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
            union_std250_sale = tm_std_fcm_union_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
            union_fcm_sale = tm_std_fcm_union_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_union_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
            union_tea_sale = tm_std_fcm_union_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_union_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

            data_dict["union_sale"][union]["tm"] = union_tm_sale
            data_dict["union_sale"][union]["std500"] = union_std500_sale
            data_dict["union_sale"][union]["std250"] = union_std250_sale
            data_dict["union_sale"][union]["fcm"] = union_fcm_sale
            data_dict["union_sale"][union]["tmate"] = union_tea_sale

            data_dict["union_sale"][union]["total"] = union_tm_sale + union_std500_sale + union_std250_sale + union_fcm_sale + union_tea_sale

    #1.Agent + Pvt Parlour (cash)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[1,2])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0    
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Coimbatore Account"]["Agent Cash"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #2.Agent + Pvt Parlour (card)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[1,2])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0    
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Coimbatore Account"]["Agent Card"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Agent Card"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Agent Card"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Agent Card"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Agent Card"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Agent Card"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #3.Ownparlour (cash)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union", sold_to = "Agent", business_type_id__in=[3, 16])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0    
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Coimbatore Account"]["Union Booth Cash"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #4.Ownparlour (card)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[3, 16])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0    
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Coimbatore Account"]["Union Booth Card"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #5.Private ins
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[4])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0    
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Coimbatore Account"]["Pvt Institutes"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #5.No commission booth
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[15])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Coimbatore Account"]["No Commission Booth"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["No Commission Booth"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["No Commission Booth"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["No Commission Booth"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["No Commission Booth"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["No Commission Booth"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #6.Govt. ins
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=5)

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] 
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] 
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Coimbatore Account"]["Govt Institutes"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #7.Society
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent"],business_type_id=10)

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    if cbe_tm_sale == None:
        cbe_tm_sale = 0
    if cbe_std500_sale == None:
        cbe_std500_sale = 0
    if cbe_std250_sale == None:
        cbe_std250_sale = 0
    cbe_fcm_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]    
        
    data_dict["Coimbatore Account"]["Society"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Society"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Society"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Society"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Society"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Society"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale
    
    #7.Kerala
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent"],business_type_id=12)

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    if cbe_tm_sale == None:
        cbe_tm_sale = 0
    if cbe_std500_sale == None:
        cbe_std500_sale = 0
    if cbe_std250_sale == None:
        cbe_std250_sale = 0
    cbe_fcm_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
    cbe_tea_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]    
        
    data_dict["Coimbatore Account"]["Kerala"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Kerala"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Kerala"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Kerala"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Kerala"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Kerala"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #8.Can Milk Buyer
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to__in = ["Agent","ICustomer"])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"]
    cbe_std250_sale = 0
    cbe_tea500_sale = 0
    cbe_tea1000_sale = 0
    cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"]
    cbe_tea_sale = cbe_tea500_sale + cbe_tea1000_sale
    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_fcm_sale is None:
        cbe_fcm_sale = 0

    data_dict["Coimbatore Account"]["Can Milk Buyer"]["tm"] = cbe_tm_sale
    data_dict["Coimbatore Account"]["Can Milk Buyer"]["std500"] = cbe_std500_sale
    data_dict["Coimbatore Account"]["Can Milk Buyer"]["std250"] = cbe_std250_sale
    data_dict["Coimbatore Account"]["Can Milk Buyer"]["fcm"] = cbe_fcm_sale
    data_dict["Coimbatore Account"]["Can Milk Buyer"]["tmate"] = cbe_tea_sale
    data_dict["Coimbatore Account"]["Can Milk Buyer"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #-----------------------------Cost---------------------#

    tm_std_fcm_diary_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list)
    tm_std_fcm_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to__in = ["Agent","ICustomer"])
    tm_std_fcm_leake_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to="Leakage")

    #dairy sale (icus + agent + leakage)

    tm_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    std500_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    std250_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    fcm_sale_500 = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] 
    fcm_sale_1000 = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    tea_sale_500 = tm_std_fcm_diary_sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] 
    tea_sale_1000 = tm_std_fcm_diary_sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if tm_sale is None:
        tm_sale = 0
    if std500_sale is None:
        std500_sale = 0
    if std250_sale is None:
        std250_sale = 0
    if fcm_sale_500 is None:
        fcm_sale_500 = 0
    if fcm_sale_1000 is None:
        fcm_sale_1000 = 0
    if tea_sale_500 is None:
        tea_sale_500 = 0
    if tea_sale_1000 is None:
        tea_sale_1000 = 0    
    
    fcm_sale = fcm_sale_1000 + fcm_sale_500
    tea_sale = tea_sale_1000 + tea_sale_500

    data_dict["Costs"]["product"]["tm"]["Resived From Diary"] = tm_sale
    data_dict["Costs"]["product"]["std500"]["Resived From Diary"] = std500_sale
    data_dict["Costs"]["product"]["std250"]["Resived From Diary"] = std250_sale
    data_dict["Costs"]["product"]["fcm"]["Resived From Diary"] = fcm_sale
    data_dict["Costs"]["product"]["tmate"]["Resived From Diary"] = tea_sale

    #net_recived (icus + agent)
    tm_sale = tm_std_fcm_sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    std500_sale = tm_std_fcm_sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    std250_sale = tm_std_fcm_sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    fcm_sale_500 = tm_std_fcm_sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] 
    fcm_sale_1000 = tm_std_fcm_sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    tea_sale_500 = tm_std_fcm_sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] 
    tea_sale_1000 = tm_std_fcm_sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if tm_sale is None:
        tm_sale = 0
    if std500_sale is None:
        std500_sale = 0
    if std250_sale is None:
        std250_sale = 0
    if fcm_sale_500 is None:
        fcm_sale_500 = 0
    if fcm_sale_1000 is None:
        fcm_sale_1000 = 0
    if tea_sale_500 is None:
        tea_sale_500 = 0
    if tea_sale_1000 is None:
        tea_sale_1000 = 0    
    
    fcm_sale = fcm_sale_1000 + fcm_sale_500
    tea_sale = tea_sale_1000 + tea_sale_500

    data_dict["Costs"]["product"]["tm"]["Net Recived"] = tm_sale
    data_dict["Costs"]["product"]["std500"]["Net Recived"] = std500_sale
    data_dict["Costs"]["product"]["std250"]["Net Recived"] = std250_sale
    data_dict["Costs"]["product"]["fcm"]["Net Recived"] = fcm_sale
    data_dict["Costs"]["product"]["tmate"]["Net Recived"] = tea_sale

    #leakage
    lk_tm_sale = tm_std_fcm_leake_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    lk_std500_sale = tm_std_fcm_leake_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    lk_std250_sale = tm_std_fcm_leake_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    lk_fcm_sale_500 = tm_std_fcm_leake_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    lk_fcm_sale_1000 = tm_std_fcm_leake_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    lk_tea_sale_500 = tm_std_fcm_leake_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    lk_tea_sale_1000 = tm_std_fcm_leake_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if lk_tm_sale is None:
        lk_tm_sale = 0
    if lk_std500_sale is None:
        lk_std500_sale = 0
    if lk_std250_sale is None:
        lk_std250_sale = 0
    if lk_fcm_sale_500 is None:
        lk_fcm_sale_500 = 0
    if lk_fcm_sale_1000 is None:
        lk_fcm_sale_1000 = 0
    if lk_tea_sale_500 is None:
        lk_tea_sale_500 = 0
    if lk_tea_sale_1000 is None:
        lk_tea_sale_1000 = 0    
    
    lk_fcm_sale = lk_fcm_sale_500 + lk_fcm_sale_1000
    lk_tea_sale = lk_tea_sale_500 + lk_tea_sale_1000

    data_dict["Costs"]["product"]["tm"]["Leakage"] = lk_tm_sale
    data_dict["Costs"]["product"]["std500"]["Leakage"] = lk_std500_sale
    data_dict["Costs"]["product"]["std250"]["Leakage"] = lk_std250_sale
    data_dict["Costs"]["product"]["fcm"]["Leakage"] = lk_fcm_sale
    data_dict["Costs"]["product"]["tmate"]["Leakage"] = lk_tea_sale

    union_list = ["COIMBATORE Union","NILGIRIS Union","TIRUPPUR Union","CHENNAI Aavin"]

    for union in union_list:
        if not union in data_dict["Costs"]["union_sale"]:
            data_dict["Costs"]["union_sale"][union] = {
                "tm" : 0,
                "std500" : 0,
                "std250" : 0,
                "fcm" : 0,
                "tmate" : 0,
                "total":0,
            }
        tm_std_fcm_union_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union=union,sold_to__in = ["Agent","ICustomer"])

        if tm_std_fcm_union_obj:
            # union sale
            union_tm_sale = tm_std_fcm_union_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
            union_std500_sale = tm_std_fcm_union_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
            union_std250_sale = tm_std_fcm_union_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
            union_fcm_sale = tm_std_fcm_union_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_union_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
            union_tea_sale = tm_std_fcm_union_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_union_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

            data_dict["Costs"]["union_sale"][union]["tm"] = union_tm_sale
            data_dict["Costs"]["union_sale"][union]["std500"] = union_std500_sale
            data_dict["Costs"]["union_sale"][union]["std250"] = union_std250_sale
            data_dict["Costs"]["union_sale"][union]["fcm"] = union_fcm_sale
            data_dict["Costs"]["union_sale"][union]["tmate"] = union_tea_sale
            data_dict["Costs"]["union_sale"][union]["total"] = union_tm_sale + union_std500_sale + union_std250_sale + union_fcm_sale + union_tea_sale

    #1.Agent + Pvt Parlour (cash)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[1,2])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0    
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #2.Agent + Pvt Parlour (card)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[1,2])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0 

    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #3.Ownparlour (cash)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[3, 16])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0 
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #4.Ownparlour (card)
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[3, 16])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0     
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #5.Private ins
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[4])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #5.Private ins
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[15])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0    
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Costs"]["Coimbatore Account"]["No Commission Booth"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["No Commission Booth"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["No Commission Booth"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["No Commission Booth"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["No Commission Booth"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["No Commission Booth"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #6.Govt. ins
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=5)

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    cbe_fcm_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    cbe_fcm_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale_500 = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    cbe_tea_sale_1000 = tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_std250_sale is None:
        cbe_std250_sale = 0
    if cbe_fcm_sale_500 is None:
        cbe_fcm_sale_500 = 0
    if cbe_fcm_sale_1000 is None:
        cbe_fcm_sale_1000 = 0
    if cbe_tea_sale_500 is None:
        cbe_tea_sale_500 = 0
    if cbe_tea_sale_1000 is None:
        cbe_tea_sale_1000 = 0      
    
    cbe_fcm_sale = cbe_fcm_sale_500 + cbe_fcm_sale_1000
    cbe_tea_sale = cbe_tea_sale_500 + cbe_tea_sale_1000

    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #6.Society
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=10)

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    # cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]

    if cbe_tm_sale == None:
        cbe_tm_sale = 0
    if cbe_std500_sale == None:
        cbe_std500_sale = 0
    if cbe_std250_sale == None:
        cbe_std250_sale = 0
    cbe_fcm_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]    

    data_dict["Costs"]["Coimbatore Account"]["Society"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale
    
    #7.Kerala
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent"],business_type_id=12)

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    # cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]

    if cbe_tm_sale == None:
        cbe_tm_sale = 0
    if cbe_std500_sale == None:
        cbe_std500_sale = 0
    if cbe_std250_sale == None:
        cbe_std250_sale = 0
    cbe_fcm_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"] != None:
        cbe_fcm_sale += tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
    cbe_tea_sale = 0
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]
    if tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"] != None:
        cbe_tea_sale += tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Kerala"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Kerala"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Kerala"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Kerala"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Kerala"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Kerala"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    #8.Can Milk Buyer
    tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to__in = ["Agent","ICustomer"])

    # union sale
    cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tmcan_cost'))['tmcan_cost__sum']
    cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('smcan_cost'))["smcan_cost__sum"]
    cbe_std250_sale = 0
    cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcmcan_cost'))["fcmcan_cost__sum"]
    cbe_tea500_sale = 0
    cbe_tea1000_sale = 0

    cbe_tea_sale = cbe_tea500_sale + cbe_tea1000_sale

    if cbe_tm_sale is None:
        cbe_tm_sale = 0
    if cbe_std500_sale is None:
        cbe_std500_sale = 0
    if cbe_fcm_sale is None:
        cbe_fcm_sale = 0


    data_dict["Costs"]["Coimbatore Account"]["Can Milk Buyer"]["tm"] = cbe_tm_sale
    data_dict["Costs"]["Coimbatore Account"]["Can Milk Buyer"]["std500"] = cbe_std500_sale
    data_dict["Costs"]["Coimbatore Account"]["Can Milk Buyer"]["std250"] = cbe_std250_sale
    data_dict["Costs"]["Coimbatore Account"]["Can Milk Buyer"]["fcm"] = cbe_fcm_sale
    data_dict["Costs"]["Coimbatore Account"]["Can Milk Buyer"]["tmate"] = cbe_tea_sale
    data_dict["Costs"]["Coimbatore Account"]["Can Milk Buyer"]["total"] = cbe_tm_sale + cbe_std500_sale + cbe_std250_sale + cbe_fcm_sale + cbe_tea_sale

    # data_dict["user_name"] = "Sunesh"

    print(data_dict)

    data = create_canvas_for_total_milk_sale(data_dict, date_list)

    return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_for_total_milk_sale(data_dict,date_list):
    file_name = "Total_milk_sale_for" + '_(' + str(date_list[0])[:10] + ' to '+str(date_list[-1])[:10] + ')' + '.pdf'
    #     file_path = os.path.join('static/media/zone_wise_report/', file_name)

    file_path = os.path.join('static/media/zone_wise_report', file_name)
#     file_path = os.path.join('static/media/', file_name)

    mycanvas = canvas.Canvas(file_path, pagesize=A4)    
#     pdfmetrics.registerFont(TTFont('Helvetica', 'matrix.ttf'))
    light_color = 0x000000
    dark_color = 0x000000

    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)

    #Date
    from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
    to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
    mycanvas.drawCentredString(300, 800, "Sale For DATE : " + str(datetime.strftime(from_date, '%d/%m/%Y'))+" to "+str(datetime.strftime(to_date, '%d/%m/%Y')))


    mycanvas.drawCentredString(300,780, "Total Milk Sale Liters")
#     mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
    mycanvas.line(406-100-50, 777, 593-200-50, 777)
    # mycanvas.line(406-100-50, 977, 993-300-500, 777)fake


    # Diary Sale
    x_a4 = 60
    mycanvas.setFont('Helvetica', 6)
    y_axis_head = 680+40+20

    mycanvas.drawCentredString(80-x_a4, y_axis_head, "S.NO")
    mycanvas.drawCentredString(132-x_a4, y_axis_head, "Total MIlk Sale")
    mycanvas.drawCentredString(200-x_a4, y_axis_head, "TM")
    # mycanvas.drawCentredString(300-x_a4, y_axis_head+8, "STD")
    mycanvas.drawCentredString(255-x_a4, y_axis_head-5, "500")
    mycanvas.drawCentredString(300-x_a4, y_axis_head-5, "250")
    mycanvas.drawCentredString(390-x_a4, y_axis_head, "FCM")
    mycanvas.drawCentredString(465-x_a4, y_axis_head, "TMATE")
    mycanvas.drawCentredString(530-x_a4, y_axis_head, "TOTAL")
    mycanvas.drawCentredString(610-x_a4, y_axis_head, "G-TOTAL")

    y_axis_line = 698+20+20+20
    y_axis = 645+20+20+30
    x_axis_line = 45-x_a4
    x_axis = 50-x_a4
    
    mycanvas.setFont('Helvetica', 7)
    mycanvas.line(x_axis_line+20, y_axis_line, x_axis_line + 585, y_axis_line)
    mycanvas.line(x_axis_line+20, y_axis_line-25, x_axis_line + 585, y_axis_line-25)

    sl_no = 1
    for diary in data_dict["product"]['tm']:
        if diary == 'Net Recived':
            y_axis -= 5
        if diary != 'Net Recived':
            mycanvas.drawRightString(x_axis+30, y_axis, str(sl_no))
            sl_no += 1
        mycanvas.setFont('Helvetica', 7)
        mycanvas.drawString(x_axis+50, y_axis, str(diary))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawRightString(x_axis+160, y_axis, str(data_dict["product"]["tm"][diary]))
        mycanvas.drawRightString(x_axis+220, y_axis, str(data_dict["product"]['std500'][diary]))
        mycanvas.drawRightString(x_axis+305, y_axis, str(data_dict["product"]['std250'][diary]))
        mycanvas.drawRightString(x_axis+365, y_axis, str(data_dict["product"]["fcm"][diary]))
        mycanvas.drawRightString(x_axis+415, y_axis, str(data_dict["product"]["tmate"][diary]))
        total = data_dict["product"]["tm"][diary] + data_dict["product"]['std500'][diary] + data_dict["product"]['std250'][diary] + data_dict["product"]["fcm"][diary] + data_dict["product"]["tmate"][diary]
        mycanvas.drawRightString(x_axis+515, y_axis, str(total))
        y_axis -= 20
       

    #lines

    mycanvas.line(x_axis_line+20, y_axis+37, x_axis_line + 505, y_axis+37)
    mycanvas.line(x_axis_line+20, y_axis+15, x_axis_line + 505, y_axis+15)
#     mycanvas.line(x_axis_line+50, y_axis+20, x_axis_line + 585, y_axis+20)

    mycanvas.line(x_axis_line+20, y_axis_line, x_axis_line+20, y_axis+37)
    mycanvas.line(x_axis_line+50, y_axis_line, x_axis_line+50, y_axis+20-5)
    
    mycanvas.line(x_axis_line+125, y_axis_line, x_axis_line+125, y_axis+20-5)
    mycanvas.line(x_axis_line+180, y_axis_line, x_axis_line+180, y_axis+20-5)
    mycanvas.line(x_axis_line+240, y_axis_line-13, x_axis_line+240, y_axis+20-5)
    mycanvas.line(x_axis_line+295, y_axis_line-1, x_axis_line+295,y_axis_line-13)

    mycanvas.line(x_axis_line + 315, y_axis_line, x_axis_line + 315, y_axis+20-5)
    mycanvas.line(x_axis_line + 390, y_axis_line, x_axis_line + 390, y_axis+20-5)
    mycanvas.line(x_axis_line + 465, y_axis_line, x_axis_line + 465, y_axis+20-5)
    mycanvas.line(x_axis_line + 535, y_axis_line, x_axis_line + 535, y_axis+20-5)
    mycanvas.line(x_axis_line + 540, y_axis_line, x_axis_line + 540, y_axis+20-5)
    mycanvas.line(x_axis_line + 558, y_axis_line, x_axis_line + 558, y_axis+20-5)
   
   
   
    # union_sale

    y_axis_line = y_axis +25
    y_axis = y_axis
    x_axis_line = 45-x_a4
    x_axis = 40-x_a4

#     mycanvas.line(x_axis_line+20, y_axis_line-25, x_axis_line + 585, y_axis_line-25)
#
    tm_tot = 0
    sm500_tot = 0
    sm250_tot = 0
    fcm_tot = 0
    tea_tot = 0
    total = 0
    for union in data_dict["union_sale"]:
        if union == 'COIMBATORE Union' or union =='NILGIRIS Union':
            pass
        else:
            tm_tot += data_dict["union_sale"][union]["tm"]
            sm500_tot += data_dict["union_sale"][union]['std500']
            sm250_tot += data_dict["union_sale"][union]['std250']
            fcm_tot += data_dict["union_sale"][union]["fcm"]
            tea_tot += data_dict["union_sale"][union]["tmate"]
            total += data_dict["union_sale"][union]["total"]

            if data_dict["union_sale"][union]["total"] == 0:
                pass
            else:             
                mycanvas.drawRightString(x_axis+40, y_axis, str(sl_no))
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawString(x_axis+50, y_axis, str(union))
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawRightString(x_axis+190, y_axis, str(data_dict["union_sale"][union]["tm"]))
                mycanvas.drawRightString(x_axis+270, y_axis, str(data_dict["union_sale"][union]['std500']))
                mycanvas.drawRightString(x_axis+345, y_axis, str(data_dict["union_sale"][union]['std250']))
                mycanvas.drawRightString(x_axis+415, y_axis, str(data_dict["union_sale"][union]["fcm"]))
                mycanvas.drawRightString(x_axis+495, y_axis, str(data_dict["union_sale"][union]["tmate"]))
                mycanvas.drawRightString(x_axis+575, y_axis, str(data_dict["union_sale"][union]["total"]))

                y_axis -= 20
                sl_no += 1

    #lines
    mycanvas.line(x_axis_line+20, y_axis+20-5, x_axis_line + 505, y_axis+20-5)

    mycanvas.line(x_axis_line+20, y_axis_line-5, x_axis_line+20, y_axis+20-5)
    mycanvas.line(x_axis_line+50, y_axis_line, x_axis_line+50, y_axis+20-5)
    
    mycanvas.line(x_axis_line+125, y_axis_line, x_axis_line+125, y_axis+20-5)
    mycanvas.line(x_axis_line+205, y_axis_line, x_axis_line+205, y_axis+20-5)
    mycanvas.line(x_axis_line+285, y_axis_line, x_axis_line+285, y_axis+20-5)
    mycanvas.line(x_axis_line+360, y_axis_line, x_axis_line+360, y_axis+20-5)

    mycanvas.line(x_axis_line + 430, y_axis_line, x_axis_line + 430, y_axis+20-5)
    mycanvas.line(x_axis_line + 505, y_axis_line, x_axis_line + 505, y_axis+20-5)
    mycanvas.line(x_axis_line + 585, y_axis_line, x_axis_line + 585, y_axis+20-5)
    mycanvas.line(x_axis_line + 665, y_axis_line, x_axis_line + 665, y_axis+20-5)
    mycanvas.line(x_axis_line + 725, y_axis_line, x_axis_line + 725, y_axis+20-5)
    mycanvas.line(x_axis_line+50, y_axis-10, x_axis_line + 505, y_axis-10)

    #     mycanvas.line(x_axis_line+50, y_axis-7, x_axis_line + 585, y_axis-7)
    
    mycanvas.drawString(x_axis+50, y_axis+3-5, "Other Union Total")
    
    mycanvas.drawString(x_axis+50, y_axis+3-25, "CBE Union Total")
    
    mycanvas.drawRightString(x_axis+160, y_axis+3-5, str(tm_tot))
    mycanvas.drawRightString(x_axis+250, y_axis+3-5, str(sm500_tot))
    mycanvas.drawRightString(x_axis+325, y_axis+3-5, str(sm250_tot))
    mycanvas.drawRightString(x_axis+385, y_axis+3-5, str(fcm_tot))
    mycanvas.drawRightString(x_axis+425, y_axis+3-5, str(tea_tot))
    mycanvas.drawRightString(x_axis+495, y_axis+3-5, str(total))
    # kabsbjdksbkasdsakj
    # ubklnl.jubilnhuj
    # bhl,ikjunilbu

    
    y_axis -= 60
    mycanvas.line(x_axis_line+10, y_axis-10, x_axis_line + 405, y_axis-10)
    # Coimbatore union account

    y_axis_line = y_axis+20
    y_axis = y_axis-25
    x_axis_line = 45-x_a4
    x_axis = 40-x_a4

    cbe_tm_tot = 0
    cbe_sm250_tot = 0
    cbe_sm500_tot = 0
    cbe_fcm_tot = 0
    cbe_tea_tot = 0
    cbe_total = 0
    for sale in data_dict["Coimbatore Account"]:
        print(sale)

        cbe_tm_tot += data_dict["Coimbatore Account"][sale]["tm"]
        cbe_sm500_tot += data_dict["Coimbatore Account"][sale]['std500']
        cbe_sm250_tot += data_dict["Coimbatore Account"][sale]['std250']
        cbe_fcm_tot += data_dict["Coimbatore Account"][sale]["fcm"]
        cbe_tea_tot += data_dict["Coimbatore Account"][sale]["tmate"]
        cbe_total += data_dict["Coimbatore Account"][sale]["total"]

        if data_dict["Coimbatore Account"][sale]["total"] == 0:
            pass
        else:
            mycanvas.drawRightString(x_axis+40, y_axis, str(sl_no))
            mycanvas.drawString(x_axis+60, y_axis, str(sale))
            mycanvas.drawRightString(x_axis+170, y_axis, str(data_dict["Coimbatore Account"][sale]["tm"]))
            mycanvas.drawRightString(x_axis+240, y_axis, str(data_dict["Coimbatore Account"][sale]['std500']))
            mycanvas.drawRightString(x_axis+295, y_axis, str(data_dict["Coimbatore Account"][sale]['std250']))
            mycanvas.drawRightString(x_axis+375, y_axis, str(data_dict["Coimbatore Account"][sale]["fcm"]))
            mycanvas.drawRightString(x_axis+430, y_axis, str(data_dict["Coimbatore Account"][sale]["tmate"]))
            mycanvas.drawRightString(x_axis+515, y_axis, str(data_dict["Coimbatore Account"][sale]["total"]))

            y_axis -= 20
            sl_no += 1

    cbe_tm_tot += data_dict["union_sale"]["NILGIRIS Union"]["tm"]
    cbe_sm500_tot += data_dict["union_sale"]["NILGIRIS Union"]['std500']
    cbe_sm250_tot += data_dict["union_sale"]["NILGIRIS Union"]['std250']
    cbe_fcm_tot += data_dict["union_sale"]["NILGIRIS Union"]["fcm"]
    cbe_tea_tot += data_dict["union_sale"]["NILGIRIS Union"]["tmate"]
    cbe_total += data_dict["union_sale"]["NILGIRIS Union"]["total"]

    if data_dict["union_sale"]["NILGIRIS Union"]["total"] == 0 :
        pass
    else:
        mycanvas.drawRightString(x_axis+40, y_axis, str(sl_no))
        mycanvas.drawString(x_axis+50, y_axis, str("NILGIRIS Union"))
        mycanvas.drawRightString(x_axis+160, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["tm"]))
        mycanvas.drawRightString(x_axis+220, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]['std500']))
        mycanvas.drawRightString(x_axis+295, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]['std250']))
        mycanvas.drawRightString(x_axis+345, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["fcm"]))
        mycanvas.drawRightString(x_axis+425, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["tmate"]))
        mycanvas.drawRightString(x_axis+495, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["total"]))
        y_axis -= 20
    #lines

    mycanvas.line(x_axis_line+20, y_axis+20-5, x_axis_line + 585, y_axis+20-5)
    mycanvas.line(x_axis_line+50, y_axis+20-30, x_axis_line+585, y_axis+20-30)

    mycanvas.line(x_axis_line+20, y_axis_line-25, x_axis_line+20, y_axis+20-5)
    mycanvas.line(x_axis_line+50, y_axis_line+30, x_axis_line+50, y_axis+20-30)
    
    mycanvas.line(x_axis_line+125, y_axis_line+30, x_axis_line+125, y_axis+20-30)
    mycanvas.line(x_axis_line+180, y_axis_line+30, x_axis_line+180, y_axis+20-30)
    mycanvas.line(x_axis_line+240, y_axis_line+30, x_axis_line+240, y_axis+20-30)

    mycanvas.line(x_axis_line +315, y_axis_line+30, x_axis_line + 315, y_axis+20-30)
    mycanvas.line(x_axis_line + 390, y_axis_line+30, x_axis_line + 390, y_axis+20-30)
    mycanvas.line(x_axis_line + 465, y_axis_line+30, x_axis_line + 465, y_axis+20-30)
    mycanvas.line(x_axis_line + 535, y_axis_line+30, x_axis_line + 535, y_axis+20-30)
    mycanvas.line(x_axis_line + 665, y_axis_line+30, x_axis_line + 665, y_axis+20-30)
    mycanvas.line(x_axis_line + 700, y_axis_line+30, x_axis_line + 700, y_axis+20-30)

    
    mycanvas.drawString(x_axis+50, y_axis+3-5, "CBE Union Total")
    mycanvas.drawRightString(x_axis+170, y_axis+3-5, str(cbe_tm_tot))
    mycanvas.drawRightString(x_axis+230, y_axis+3-5, str(cbe_sm500_tot))
    mycanvas.drawRightString(x_axis+305, y_axis+3-5, str(cbe_sm250_tot))
    mycanvas.drawRightString(x_axis+375, y_axis+3-5, str(cbe_fcm_tot))
    mycanvas.drawRightString(x_axis+425, y_axis+3-5, str(cbe_tea_tot))
    mycanvas.drawRightString(x_axis+515, y_axis+3-5, str(cbe_total))
    
    
    net_total = data_dict["product"]["tm"]['Net Recived'] + data_dict["product"]['std500']['Net Recived'] + data_dict["product"]['std250']['Net Recived'] + data_dict["product"]["fcm"]['Net Recived'] + data_dict["product"]["tmate"]['Net Recived']
    
    mycanvas.drawRightString(x_axis+170, 565, str(data_dict["product"]["tm"]['Net Recived']- tm_tot))
    mycanvas.drawRightString(x_axis+230, 565, str(data_dict["product"]['std500']['Net Recived']- sm500_tot))
    mycanvas.drawRightString(x_axis+305, 565, str(data_dict["product"]['std250']['Net Recived']- sm250_tot))
    mycanvas.drawRightString(x_axis+375, 565, str(data_dict["product"]["fcm"]['Net Recived']- fcm_tot))
    mycanvas.drawRightString(x_axis+425, 565, str(data_dict["product"]["tmate"]['Net Recived']- tea_tot))
    mycanvas.drawRightString(x_axis+515, 565, str(net_total - total))
    
    cash_total = data_dict["Coimbatore Account"]['Agent Cash']["total"] + data_dict["Coimbatore Account"]['Union Booth Cash']["total"] 
    card_total = data_dict["Coimbatore Account"]['Agent Card']["total"] + data_dict["Coimbatore Account"]['Union Booth Card']["total"]
    
    csh_crd_total = cash_total + card_total
    
    mycanvas.drawRightString(x_axis+575, 525, str(cash_total))
    mycanvas.drawRightString(x_axis+575, 485, str(card_total))
    mycanvas.drawRightString(x_axis+575, 385, str(csh_crd_total))
    
    #-----------------------------------------Cost-----------------------------------------#
    mycanvas.setFont('Helvetica', 10)

    mycanvas.drawCentredString(300, 290+4, "Total Milk Sale Amount")
#     mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
    mycanvas.line(406-100-50, 290, 593-200-50, 290)

    y_axis_head = 300-40

    mycanvas.drawCentredString(100-x_a4, y_axis_head, "S.NO")
    mycanvas.drawCentredString(152-x_a4, y_axis_head, "Total MIlk Sale")
    mycanvas.drawCentredString(220-x_a4, y_axis_head, "TM")
    # mycanvas.drawCentredString(300-x_a4, y_axis_head+8, "STD")
    mycanvas.drawCentredString(285-x_a4, y_axis_head, "STD500")
    mycanvas.drawCentredString(345-x_a4, y_axis_head, "STD250")
    mycanvas.drawCentredString(400-x_a4, y_axis_head, "FCM")
    mycanvas.drawCentredString(475-x_a4, y_axis_head, "TMATE")
    mycanvas.drawCentredString(560-x_a4, y_axis_head, "TOTAL")
    mycanvas.drawCentredString(625-x_a4, y_axis_head, "G-TOTAL")
    
    y_axis_line = 398-40-50-30
    y_axis = 345-40-50-20
    x_axis_line = 65-x_a4
    x_axis = 70-x_a4

    mycanvas.line(x_axis_line+20, y_axis_line, x_axis_line + 585, y_axis_line)
    mycanvas.line(x_axis_line+20, y_axis_line-25, x_axis_line + 585, y_axis_line-25)

    sl_no = 1

    tm_tot = 0
    sm500_tot = 0
    sm250_tot = 0
    fcm_tot = 0
    tea_tot = 0
    total = 0
    
    cash_total = round(data_dict['Costs']["Coimbatore Account"]['Agent Cash']["total"])+ round(data_dict['Costs']["Coimbatore Account"]['Union Booth Cash']["total"])
    card_total = round(data_dict['Costs']["Coimbatore Account"]['Agent Card']["total"])+ round(data_dict['Costs']["Coimbatore Account"]['Union Booth Card']["total"])
    csh_crd_total = cash_total + card_total
    
    for sale in data_dict['Costs']["Coimbatore Account"]:

        tm_tot += data_dict['Costs']["Coimbatore Account"][sale]["tm"]
        sm500_tot += data_dict['Costs']["Coimbatore Account"][sale]['std500']
        sm250_tot += data_dict['Costs']["Coimbatore Account"][sale]['std250']
        fcm_tot += data_dict['Costs']["Coimbatore Account"][sale]["fcm"]
        tea_tot += data_dict['Costs']["Coimbatore Account"][sale]["tmate"]
        total += data_dict['Costs']["Coimbatore Account"][sale]["total"]

        if data_dict['Costs']["Coimbatore Account"][sale]["total"] == 0:
            pass
        else:
            mycanvas.drawRightString(x_axis+40, y_axis, str(sl_no))
            mycanvas.setFont('Helvetica', 8)
            mycanvas.drawString(x_axis+50, y_axis, str(sale))
            mycanvas.drawRightString(x_axis+170, y_axis, str(round(data_dict['Costs']["Coimbatore Account"][sale]["tm"]))+'.00')
            mycanvas.drawRightString(x_axis+240, y_axis, str(round(data_dict['Costs']["Coimbatore Account"][sale]['std500']))+'.00')
            mycanvas.drawRightString(x_axis+285, y_axis, str(round(data_dict['Costs']["Coimbatore Account"][sale]['std250']))+'.00')
            mycanvas.drawRightString(x_axis+345, y_axis, str(round(data_dict['Costs']["Coimbatore Account"][sale]["fcm"]))+'.00')
            mycanvas.drawRightString(x_axis+395, y_axis, str(round(data_dict['Costs']["Coimbatore Account"][sale]["tmate"]))+'.00')
            mycanvas.drawRightString(x_axis+475, y_axis, str(round(data_dict['Costs']["Coimbatore Account"][sale]["total"]))+'.00')
            
            if sale == "Union Booth Cash":
                mycanvas.drawRightString(x_axis+570, y_axis, str(round(cash_total))+'.00')
                
            if sale == "Union Booth Card":
                mycanvas.drawRightString(x_axis+570, y_axis, str(round(card_total))+'.00')

            y_axis -= 20
            sl_no += 1

    tm_tot += data_dict['Costs']["union_sale"]["NILGIRIS Union"]["tm"]
    sm500_tot += data_dict['Costs']["union_sale"]["NILGIRIS Union"]['std500']
    sm250_tot += data_dict['Costs']["union_sale"]["NILGIRIS Union"]['std250']
    fcm_tot += data_dict['Costs']["union_sale"]["NILGIRIS Union"]["fcm"]
    tea_tot += data_dict['Costs']["union_sale"]["NILGIRIS Union"]["tmate"]
    total += data_dict['Costs']["union_sale"]["NILGIRIS Union"]["total"]

    if data_dict['Costs']["union_sale"]["NILGIRIS Union"]["total"] == 0:
        pass
    else:
        mycanvas.drawRightString(x_axis+40, y_axis, str(sl_no))
        mycanvas.drawString(x_axis+50, y_axis, str("NILGIRIS Union"))
        mycanvas.drawRightString(x_axis+170, y_axis, str(round(data_dict['Costs']["union_sale"]["NILGIRIS Union"]["tm"]))+'.00')
        mycanvas.drawRightString(x_axis+240, y_axis, str(round(data_dict['Costs']["union_sale"]["NILGIRIS Union"]['std500']))+'.00')
        mycanvas.drawRightString(x_axis+285, y_axis, str(round(data_dict['Costs']["union_sale"]["NILGIRIS Union"]['std250']))+'.00')
        mycanvas.drawRightString(x_axis+345, y_axis, str(round(data_dict['Costs']["union_sale"]["NILGIRIS Union"]["fcm"]))+'.00')
        mycanvas.drawRightString(x_axis+395, y_axis, str(round(data_dict['Costs']["union_sale"]["NILGIRIS Union"]["tmate"]))+'.00')
        mycanvas.drawRightString(x_axis+475, y_axis, str(round(data_dict['Costs']["union_sale"]["NILGIRIS Union"]["total"]))+'.00')
        y_axis -= 20
    #lines

    mycanvas.line(x_axis_line+20, y_axis+20-5, x_axis_line + 585, y_axis+20-5)
    mycanvas.line(x_axis_line+50, y_axis+20-30, x_axis_line + 585, y_axis+20-30)

    mycanvas.line(x_axis_line+20, y_axis_line, x_axis_line+20, y_axis+20-5)
    mycanvas.line(x_axis_line+50, y_axis_line, x_axis_line+50, y_axis+20-30)
    mycanvas.line(x_axis_line+130, y_axis_line, x_axis_line+130, y_axis+20-30)
    mycanvas.line(x_axis_line+195, y_axis_line, x_axis_line+195, y_axis+20-30)
    mycanvas.line(x_axis_line+255, y_axis_line, x_axis_line+255, y_axis+20-30)
    mycanvas.line(x_axis_line+305, y_axis_line, x_axis_line+305, y_axis+20-30)

    mycanvas.line(x_axis_line + 360, y_axis_line, x_axis_line + 360, y_axis+20-30)
    mycanvas.line(x_axis_line + 430, y_axis_line, x_axis_line + 430, y_axis+20-30)
    mycanvas.line(x_axis_line + 510, y_axis_line, x_axis_line + 510, y_axis+20-30)
    mycanvas.line(x_axis_line + 585, y_axis_line, x_axis_line + 585, y_axis+20-30)
    mycanvas.line(x_axis_line + 660, y_axis_line, x_axis_line + 660, y_axis+20-30)
    mycanvas.line(x_axis_line + 725, y_axis_line, x_axis_line + 725, y_axis+20-30)
   
    mycanvas.setFont('Helvetica', 7)
    mycanvas.drawString(x_axis+46, y_axis+3-5, "CBE Union Total Amount")
    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawRightString(x_axis+170, y_axis+3-5, str(round(tm_tot)) + '.00')
    mycanvas.drawRightString(x_axis+230, y_axis+3-5, str(round(sm500_tot)) + '.00')
    mycanvas.drawRightString(x_axis+295, y_axis+3-5, str(round(sm250_tot)) + '.00')
    mycanvas.drawRightString(x_axis+345, y_axis+3-5, str(round(fcm_tot)) + '.00')
    mycanvas.drawRightString(x_axis+415, y_axis+3-5, str(round(tea_tot)) + '.00')
    mycanvas.drawRightString(x_axis+495, y_axis+3-5, str(round(total)) + '.00')
    mycanvas.drawRightString(x_axis+555, y_axis+3-5, str(round(csh_crd_total)) + '.00')
   
    indian = pytz.timezone('Asia/Kolkata')
#     mycanvas.setFont('Times-Italic', 10)
#     mycanvas.drawRightString(585, 5, 'Report Generated by: '+str(data_dict['user_name']+", @"+str(datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

    mycanvas.save()
    document = {}
    document['file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document



@api_view(['POST'])
def generate_pdf_code_for_total_curd_sale(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    date_list = pd.date_range(start=from_date,end=to_date)
    data_dict = {
        "product":{
            "curd500":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "Returned" : 0,
                "Net Recived" : 0,
            },
            "curd150":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "Returned" : 0,
                "Net Recived" : 0,
            },
            "curd100":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "Returned" : 0,
                "Net Recived" : 0,
            },
             "curd5000":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "Returned" : 0,
                "Net Recived" : 0,
            },
            "buttermilk200":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "Returned" : 0,
                "Net Recived" : 0,
            },
            "total":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "Returned" : 0,
                "Net Recived" : 0,
            },
        },
        "union_sale" : {},
        "Coimbatore Account" : {
            "Agent Cash": {
                "curd500" : 0,
                "curd150" : 0,
                "curd100" : 0,
                "curd5000" : 0,
                "buttermilk200" : 0,
                "total": 0
            },
            "Agent Card" : {
                "curd500" : 0,
                "curd150" : 0,
                "curd100" : 0,
                "curd5000" : 0,
                "buttermilk200" : 0,
                "total": 0
            },
            "Union Booth Cash" : {
                "curd500" : 0,
                "curd150" : 0,
                "curd100" : 0,
                "curd5000" : 0,
                "buttermilk200" : 0,
                "total": 0
            },
            "Union Booth Card" : {
                "curd500" : 0,
                "curd150" : 0,
                "curd100" : 0,
                "curd5000" : 0,
                "buttermilk200" : 0,
                "total": 0
            },
            "Pvt Institutes" : {
                "curd500" : 0,
                "curd150" : 0,
                "curd100" : 0,
                "curd5000" : 0,
                "buttermilk200" : 0,
                "total": 0
            },
            "Govt Institutes" : {
                "curd500" : 0,
                "curd150" : 0,
                "curd100" : 0,
                "curd5000" : 0,
                "buttermilk200" : 0,
                "total": 0
            },
            "Society" : {
                "curd500" : 0,
                "curd150" : 0,
                "curd100" : 0,
                "curd5000" : 0,
                "buttermilk200" : 0,
                "total": 0
            },
        },
        "Costs" : {
            "product":{
                "curd500":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0,
                },
                "curd150":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0,
                },
                "curd100":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0,
                },
                "curd5000":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0,
                },
                "buttermilk200":{
                    "Resived From Diary": 0,
                    "Leakage" : 0,
                    "Returned" : 0,
                    "Net Recived" : 0,
                },
                "total":{
                "Resived From Diary": 0,
                "Leakage" : 0,
                "Returned" : 0,
                "Net Recived" : 0,
                },
            },
            "union_sale" : {},
            "Coimbatore Account" : {
                "Agent Cash": {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
                },
                "Agent Card" : {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
                },
                "Union Booth Cash" : {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
                },
                "Union Booth Card" : {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
                },
                "Pvt Institutes" : {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
                },
                "Govt Institutes" : {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
                },
                "Society" : {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
            },
            },
        }
    }
    diary_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list)
    sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to__in = ["Agent","ICustomer"])
    leake_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to="Leakage")
   
    #dairy sale (icus + agent + leakage)
    curd500_sale = diary_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = diary_sale_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = diary_sale_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = diary_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = diary_sale_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]
   
    data_dict["product"]["curd500"]["Resived From Diary"] = curd500_sale
    data_dict["product"]["curd150"]["Resived From Diary"] = curd150_sale
    data_dict["product"]["curd100"]["Resived From Diary"] = curd100_sale
    data_dict["product"]["curd5000"]["Resived From Diary"] = curd5000_sale
    data_dict["product"]["buttermilk200"]["Resived From Diary"] = buttermilk200_sale
    data_dict["product"]["total"]["Resived From Diary"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
    

    #net_recived (icus + agent)
    curd500_sale = sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = sale_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = sale_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = sale_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["product"]["curd500"]["Net Recived"] = curd500_sale
    data_dict["product"]["curd150"]["Net Recived"] = curd150_sale
    data_dict["product"]["curd100"]["Net Recived"] = curd100_sale
    data_dict["product"]["curd5000"]["Net Recived"] = curd5000_sale
    data_dict["product"]["buttermilk200"]["Net Recived"] = buttermilk200_sale
    data_dict["product"]["total"]["Net Recived"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale

    #leakage
    curd500_sale = leake_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = leake_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = leake_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = leake_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = leake_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["product"]["curd500"]["Leakage"] = curd500_sale
    data_dict["product"]["curd150"]["Leakage"] = curd150_sale
    data_dict["product"]["curd100"]["Leakage"] = curd100_sale
    data_dict["product"]["curd5000"]["Leakage"] = curd5000_sale
    data_dict["product"]["buttermilk200"]["Leakage"] = buttermilk200_sale
    data_dict["product"]["total"]["Leakage"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale

    union_list = ["COIMBATORE Union","NILGIRIS Union","TIRUPPUR Union","CHENNAI Aavin"]

    for union in union_list:
        if not union in data_dict["union_sale"]:
            data_dict["union_sale"][union] = {
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    "total": 0
            }
        union_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union=union,sold_to__in = ["Agent","ICustomer"])

        # union sale
        if union_obj:
            curd500_sale = union_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            curd150_sale = union_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
            curd100_sale = union_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
            curd5000_sale = union_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            buttermilk200_sale = union_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

            data_dict["union_sale"][union]["curd500"] = curd500_sale
            data_dict["union_sale"][union]["curd150"] = curd150_sale
            data_dict["union_sale"][union]["curd100"] = curd100_sale
            data_dict["union_sale"][union]["curd5000"] = curd5000_sale
            data_dict["union_sale"][union]["buttermilk200"] = buttermilk200_sale
            data_dict["union_sale"][union]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
       
    #1.Agent + Pvt Parlour (cash)
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to="Agent",business_type_id__in=[1,2,9])

    curd500_sale = cbe_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["Coimbatore Account"]["Agent Cash"]["curd500"] = curd500_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["curd150"] = curd150_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["curd100"] = curd100_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["curd5000"] = curd5000_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["buttermilk200"] = buttermilk200_sale
    data_dict["Coimbatore Account"]["Agent Cash"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale

    #2.Agent + Pvt Parlour (card)
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[1,2,9])

    curd500_sale = cbe_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["Coimbatore Account"]["Agent Card"]["curd500"] = curd500_sale
    data_dict["Coimbatore Account"]["Agent Card"]["curd150"] = curd150_sale
    data_dict["Coimbatore Account"]["Agent Card"]["curd100"] = curd100_sale
    data_dict["Coimbatore Account"]["Agent Card"]["curd5000"] = curd5000_sale
    data_dict["Coimbatore Account"]["Agent Card"]["buttermilk200"] = buttermilk200_sale
    data_dict["Coimbatore Account"]["Agent Card"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #3.Ownparlour (cash)
    # if DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[3, 16]).exists():
        
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[3, 16])
    # print('cbe_obj',cbe_obj)
    curd500_sale = cbe_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]
    # print("curd5000_sale",curd5000_sale)
    data_dict["Coimbatore Account"]["Union Booth Cash"]["curd500"] = curd500_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["curd150"] = curd150_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["curd100"] = curd100_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["curd5000"] = curd5000_sale
    data_dict["Coimbatore Account"]["Union Booth Cash"]["buttermilk200"] = buttermilk200_sale
    # print(curd500_sale, curd150_sale, curd100_sale , curd5000_sale , buttermilk200_sale)
    data_dict["Coimbatore Account"]["Union Booth Cash"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
    
    #4.Ownparlour (card)
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[3, 16])

    curd500_sale = cbe_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["Coimbatore Account"]["Union Booth Card"]["curd500"] = curd500_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["curd150"] = curd150_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["curd100"] = curd100_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["curd5000"] = curd5000_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["buttermilk200"] = buttermilk200_sale
    data_dict["Coimbatore Account"]["Union Booth Card"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #5.Private ins
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=4)

    curd500_sale = cbe_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["Coimbatore Account"]["Pvt Institutes"]["curd500"] = curd500_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["curd150"] = curd150_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["curd100"] = curd100_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["curd5000"] = curd5000_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["buttermilk200"] = buttermilk200_sale
    data_dict["Coimbatore Account"]["Pvt Institutes"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #6.Govt. ins
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=5)

    curd500_sale = cbe_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["Coimbatore Account"]["Govt Institutes"]["curd500"] = curd500_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["curd150"] = curd150_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["curd100"] = curd100_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["curd5000"] = curd5000_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["buttermilk200"] = buttermilk200_sale
    data_dict["Coimbatore Account"]["Govt Institutes"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #7.Society
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent"],business_type_id=10)

    curd500_sale = cbe_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_kgs'))["curd150_kgs__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_kgs'))["cupcurd_kgs__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_litre'))["buttermilk200_litre__sum"]

    data_dict["Coimbatore Account"]["Society"]["curd500"] = curd500_sale
    data_dict["Coimbatore Account"]["Society"]["curd150"] = curd150_sale
    data_dict["Coimbatore Account"]["Society"]["curd100"] = curd100_sale
    data_dict["Coimbatore Account"]["Society"]["curd5000"] = curd5000_sale
    data_dict["Coimbatore Account"]["Society"]["buttermilk200"] = buttermilk200_sale
    data_dict["Coimbatore Account"]["Society"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #-----------------------------Cost---------------------#
   
    tm_std_fcm_diary_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list)
    tm_std_fcm_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to__in = ["Agent","ICustomer"])
    tm_std_fcm_leake_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,sold_to="Leakage")
   
    #dairy sale (icus + agent + leakage)
    curd500_sale = diary_sale_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = diary_sale_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = diary_sale_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = diary_sale_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = diary_sale_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]
   
    data_dict["Costs"]["product"]["curd500"]["Resived From Diary"] = curd500_sale
    data_dict["Costs"]["product"]["curd150"]["Resived From Diary"] = curd150_sale
    data_dict["Costs"]["product"]["curd100"]["Resived From Diary"] = curd100_sale
    data_dict["Costs"]["product"]["curd5000"]["Resived From Diary"] = curd5000_sale
    data_dict["Costs"]["product"]["buttermilk200"]["Resived From Diary"] = buttermilk200_sale
    data_dict["Costs"]["product"]["total"]["Resived From Diary"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale

    #net_recived (icus + agent)
    curd500_sale = sale_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = sale_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = sale_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = sale_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = sale_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["product"]["curd500"]["Net Recived"] = curd500_sale
    data_dict["Costs"]["product"]["curd150"]["Net Recived"] = curd150_sale
    data_dict["Costs"]["product"]["curd100"]["Net Recived"] = curd100_sale
    data_dict["Costs"]["product"]["curd5000"]["Net Recived"] = curd5000_sale
    data_dict["Costs"]["product"]["buttermilk200"]["Net Recived"] = buttermilk200_sale
    data_dict["Costs"]["product"]["total"]["Net Recived"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale +buttermilk200_sale

    #leakage
    curd500_sale = leake_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = leake_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = leake_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = leake_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = leake_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["product"]["curd500"]["Leakage"] = curd500_sale
    data_dict["Costs"]["product"]["curd150"]["Leakage"] = curd150_sale
    data_dict["Costs"]["product"]["curd100"]["Leakage"] = curd100_sale
    data_dict["Costs"]["product"]["curd5000"]["Leakage"] = curd5000_sale
    data_dict["Costs"]["product"]["buttermilk200"]["Leakage"] = buttermilk200_sale
    data_dict["Costs"]["product"]["total"]["Leakage"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale

    union_list = ["COIMBATORE Union","NILGIRIS Union","TIRUPPUR Union","CHENNAI Aavin"]

    for union in union_list:
        if not union in data_dict["Costs"]["union_sale"]:
            data_dict["Costs"]["union_sale"][union] = {
               
                    "curd500" : 0,
                    "curd150" : 0,
                    "curd100" : 0,
                    "curd5000" : 0,
                    "buttermilk200" : 0,
                    'total': 0,
            }
        union_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union=union,sold_to__in = ["Agent","ICustomer"])

        # union sale
        if union_obj:
            curd500_sale = union_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
            curd150_sale = union_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
            curd100_sale = union_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
            curd5000_sale = union_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
            buttermilk200_sale = union_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

            data_dict["Costs"]["union_sale"][union]["curd500"] = curd500_sale
            data_dict["Costs"]["union_sale"][union]["curd150"] = curd150_sale
            data_dict["Costs"]["union_sale"][union]["curd100"] = curd100_sale
            data_dict["Costs"]["union_sale"][union]["curd5000"] = curd5000_sale
            data_dict["Costs"]["union_sale"][union]["buttermilk200"] = buttermilk200_sale
            data_dict["Costs"]["union_sale"][union]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
       
     #1.Agent + Pvt Parlour (cash)
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[1,2,9])

    curd500_sale = cbe_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["curd500"] = curd500_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["curd150"] = curd150_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["curd100"] = curd100_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["curd5000"] = curd5000_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["buttermilk200"] = buttermilk200_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Cash"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #2.Agent + Pvt Parlour (card)
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[1,2,9])

    curd500_sale = cbe_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["curd500"] = curd500_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["curd150"] = curd150_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["curd100"] = curd100_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["curd5000"] = curd5000_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["buttermilk200"] = buttermilk200_sale
    data_dict["Costs"]["Coimbatore Account"]["Agent Card"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #3.Ownparlour (cash)
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[3, 16])

    curd500_sale = cbe_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["curd500"] = curd500_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["curd150"] = curd150_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["curd100"] = curd100_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["curd5000"] = curd5000_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["buttermilk200"] = buttermilk200_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Cash"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #4.Ownparlour (card)
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[3, 16])

    curd500_sale = cbe_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["curd500"] = curd500_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["curd150"] = curd150_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["curd100"] = curd100_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["curd5000"] = curd5000_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["buttermilk200"] = buttermilk200_sale
    data_dict["Costs"]["Coimbatore Account"]["Union Booth Card"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #5.Private ins
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=4)

    curd500_sale = cbe_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["curd500"] = curd500_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["curd150"] = curd150_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["curd100"] = curd100_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["curd5000"] = curd5000_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["buttermilk200"] = buttermilk200_sale
    data_dict["Costs"]["Coimbatore Account"]["Pvt Institutes"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #6.Govt. ins
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=5)

    curd500_sale = cbe_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["curd500"] = curd500_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["curd150"] = curd150_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["curd100"] = curd100_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["curd5000"] = curd5000_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["buttermilk200"] = buttermilk200_sale
    data_dict["Costs"]["Coimbatore Account"]["Govt Institutes"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale
   
    #7.Society
    cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=10)

    curd500_sale = cbe_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']
    curd150_sale = cbe_obj.aggregate(Sum('curd150_cost'))["curd150_cost__sum"]
    curd100_sale = cbe_obj.aggregate(Sum('cupcurd_cost'))["cupcurd_cost__sum"]
    curd5000_sale = cbe_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']
    buttermilk200_sale = cbe_obj.aggregate(Sum('buttermilk200_cost'))["buttermilk200_cost__sum"]

    data_dict["Costs"]["Coimbatore Account"]["Society"]["curd500"] = curd500_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["curd150"] = curd150_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["curd100"] = curd100_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["curd5000"] = curd5000_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["buttermilk200"] = buttermilk200_sale
    data_dict["Costs"]["Coimbatore Account"]["Society"]["total"] = curd500_sale + curd150_sale + curd100_sale + curd5000_sale + buttermilk200_sale

    data_dict["user_name"] = 'Rasathi'

    data = create_canvas_for_total_curd_sale(data_dict, date_list)

    return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_for_total_curd_sale(data_dict,date_list):
    file_name = "Total_fermented_sale_for" + '_(' + str(date_list[0])[:10] + ' to '+str(date_list[-1])[:10] + ')' + '.pdf'
    #     file_path = os.path.join('static/media/zone_wise_report/', file_name)

    file_path = os.path.join('static/media/zone_wise_report', file_name)
#     file_path = os.path.join('static/media/', file_name)

    mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'matrix.ttf'))
    light_color =  0x000000
    dark_color = 0x000000

    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
   
    #Date
    from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
    to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
    mycanvas.drawCentredString(300, 800, "Sale For DATE : " + str(datetime.strftime(from_date, '%d/%m/%Y'))+" to "+str(datetime.strftime(to_date, '%d/%m/%Y')))
   
   
    mycanvas.drawCentredString(300, 780, "Total Fermented Products Sale ")
#     mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
    mycanvas.line(406-100-50, 777, 593-200-50, 777)
   
    x_a4 = 10
    # Diary Sale
   
    mycanvas.setFont('Helvetica', 10)
    y_axis_head = 680+40+20-10
   
    mycanvas.drawCentredString(40-x_a4, y_axis_head, "S.NO")
    mycanvas.drawCentredString(110-x_a4, y_axis_head, "Total Sale")
    mycanvas.drawCentredString(285-80-x_a4, y_axis_head, "Curd500")
    mycanvas.drawCentredString(430-140-x_a4, y_axis_head, "Curd150")
    mycanvas.drawCentredString(550-175-x_a4, y_axis_head, "Curd5000")
    mycanvas.drawCentredString(560-95-x_a4, y_axis_head, "Buttermilk")
    mycanvas.drawCentredString(560-15-x_a4, y_axis_head, "Total")
   
    y_axis_line = 698+20+20+20-10
    y_axis = 645+20+20+20-10
    x_axis_line = 20-x_a4
    x_axis = 30-x_a4
   
    mycanvas.line(x_axis_line, y_axis_line,585, y_axis_line)
    mycanvas.line(x_axis_line, y_axis_line-25, 585, y_axis_line-25)
   
    sl_no = 1
    for diary in data_dict["product"]['curd500']:
        if diary == 'Net Recived':
             y_axis -= 5
        if diary != 'Net Recived':
            mycanvas.drawString(x_axis+10, y_axis, str(sl_no))
        mycanvas.drawString(x_axis+35, y_axis, str(diary))
        mycanvas.drawRightString(x_axis+305-100, y_axis, str(data_dict["product"]["curd500"][diary]))
        mycanvas.drawRightString(x_axis+445-150, y_axis, str(data_dict["product"]['curd150'][diary]))
        mycanvas.drawRightString(x_axis+570-15-170, y_axis, str(data_dict["product"]["curd5000"][diary]))
        mycanvas.drawRightString(x_axis+590+85-220, y_axis, str(data_dict["product"]["buttermilk200"][diary]))
        mycanvas.drawRightString(x_axis+590+85-120, y_axis, str(data_dict["product"]["total"][diary]))
        y_axis -= 25
        sl_no += 1
   
    #lines
   
    mycanvas.line(x_axis_line, y_axis+42, x_axis_line + 575, y_axis+42)
#     mycanvas.line(x_axis_line+50, y_axis+20, x_axis_line + 585, y_axis+20)
   
    mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis+47)
    mycanvas.line(x_axis_line+40, y_axis_line, x_axis_line+40, y_axis+20)
    mycanvas.line(x_axis_line+140, y_axis_line, x_axis_line+140, y_axis+20)
    mycanvas.line(x_axis_line+320-95, y_axis_line, x_axis_line+320-95, y_axis+20)
    mycanvas.line(x_axis_line+405-90, y_axis_line, x_axis_line+405-90, y_axis+20)
    mycanvas.line(x_axis_line + 575-170, y_axis_line, x_axis_line + 575-170, y_axis+20)
    mycanvas.line(x_axis_line + 575-100, y_axis_line, x_axis_line + 575-100, y_axis+20)
    mycanvas.line(x_axis_line + 685-110, y_axis_line, x_axis_line + 685-110, y_axis+20)
   
   
#     print("1",y_axis)
    # union_sale
   
    y_axis_line = 633
    y_axis = 580
    x_axis_line = 20-x_a4
    x_axis = 30-x_a4
   
    mycanvas.line(x_axis_line, y_axis_line-25, x_axis_line + 575, y_axis_line-25)
   
    curd500 = 0
    curd150 = 0
    curd5000 = 0
    buttermilk200 = 0
    total = 0
    for union in data_dict["union_sale"]:
        if union == 'COIMBATORE Union' or union =='NILGIRIS Union':
            pass
        else:
            curd500 += data_dict["union_sale"][union]["curd500"]
            curd150 += data_dict["union_sale"][union]['curd150']
            curd5000 += data_dict["union_sale"][union]["curd5000"]
            buttermilk200 += data_dict["union_sale"][union]["buttermilk200"]
            total += data_dict["union_sale"][union]["total"]
           
            if data_dict["union_sale"][union]["curd500"] == 0 and data_dict["union_sale"][union]['curd150'] == 0  and data_dict["union_sale"][union]["curd5000"] == 0 and data_dict["union_sale"][union]["buttermilk200"] == 0:
                pass
            else:
                mycanvas.drawString(x_axis+10, y_axis, str(sl_no))
                mycanvas.drawString(x_axis+35, y_axis, str(union))
                mycanvas.drawRightString(x_axis+305-100, y_axis, str(data_dict["union_sale"][union]["curd500"]))
                mycanvas.drawRightString(x_axis+445-150, y_axis, str(data_dict["union_sale"][union]['curd150']))
                mycanvas.drawRightString(x_axis+570-15-170, y_axis, str(data_dict["union_sale"][union]["curd5000"]))
                mycanvas.drawRightString(x_axis+590+85-220, y_axis, str(data_dict["union_sale"][union]["buttermilk200"]))
                mycanvas.drawRightString(x_axis+590+85-120, y_axis, str(data_dict["union_sale"][union]["total"]))
                y_axis -= 25
                sl_no += 1
   
    #lines
   
    mycanvas.line(x_axis_line, y_axis+20-5, x_axis_line + 575, y_axis+20-5)
   
    mycanvas.line(x_axis_line, y_axis_line-25, x_axis_line, y_axis+20-5)
    mycanvas.line(x_axis_line+40, y_axis_line-20, x_axis_line+40, y_axis-5)
    mycanvas.line(x_axis_line+140, y_axis_line-20, x_axis_line+140, y_axis-5)
    mycanvas.line(x_axis_line+320-95, y_axis_line-20, x_axis_line+320-95, y_axis-5)
    mycanvas.line(x_axis_line+405-90, y_axis_line-20, x_axis_line+405-90, y_axis-5)
    mycanvas.line(x_axis_line + 575-170, y_axis_line-20, x_axis_line + 575-170, y_axis-5)
    mycanvas.line(x_axis_line + 575-100, y_axis_line-20, x_axis_line + 575-100, y_axis-5)
    mycanvas.line(x_axis_line + 685-110, y_axis_line-20, x_axis_line + 685-110, y_axis-5)
   
#     mycanvas.line(x_axis_line+50, y_axis-7, x_axis_line + 685, y_axis-7)
   
    mycanvas.drawString(x_axis+35, y_axis+3-5, "Other Union Total")
    mycanvas.drawRightString(x_axis+305-100, y_axis+3-5, str(curd500))
    mycanvas.drawRightString(x_axis+445-150, y_axis+3-5, str(curd150))
    mycanvas.drawRightString(x_axis+570-15-170, y_axis+3-5, str(curd5000))
    mycanvas.drawRightString(x_axis+590+85-220, y_axis+3-5, str(buttermilk200))
    mycanvas.drawRightString(x_axis+590+85-120, y_axis+3-5, str(total))
   
   
    # Coimbatore union account
   
    y_axis_line = y_axis+15
    y_axis = y_axis_line - 50
    x_axis_line = 20-x_a4
    x_axis = 30-x_a4

    mycanvas.line(x_axis_line, y_axis_line-25, x_axis_line + 575, y_axis_line-25)
   
    curd500 = 0
    curd150 = 0
    curd5000 = 0
    buttermilk200 = 0
    total = 0
    for sale in data_dict["Coimbatore Account"]:
       
        curd500 += data_dict["Coimbatore Account"][sale]["curd500"]
        curd150 += data_dict["Coimbatore Account"][sale]['curd150']
        curd5000 += data_dict["Coimbatore Account"][sale]["curd5000"]
        buttermilk200 += data_dict["Coimbatore Account"][sale]["buttermilk200"]
        total += data_dict["Coimbatore Account"][sale]["total"]
       
       
        if data_dict["Coimbatore Account"][sale]["curd500"] == 0 and data_dict["Coimbatore Account"][sale]['curd150'] == 0 and data_dict["Coimbatore Account"][sale]["curd5000"] == 0 and data_dict["Coimbatore Account"][sale]["buttermilk200"] == 0:
            continue
        else:
            mycanvas.drawString(x_axis+10, y_axis, str(sl_no))
            mycanvas.drawString(x_axis+35, y_axis, str(sale))
            mycanvas.drawRightString(x_axis+305-100, y_axis, str(data_dict["Coimbatore Account"][sale]["curd500"]))
            mycanvas.drawRightString(x_axis+445-150, y_axis, str(data_dict["Coimbatore Account"][sale]['curd150']))
            mycanvas.drawRightString(x_axis+570-15-170, y_axis, str(data_dict["Coimbatore Account"][sale]["curd5000"]))
            mycanvas.drawRightString(x_axis+590+85-220, y_axis, str(data_dict["Coimbatore Account"][sale]["buttermilk200"]))
            mycanvas.drawRightString(x_axis+590+85-120, y_axis, str(data_dict["Coimbatore Account"][sale]["total"]))
           
            y_axis -= 25
            sl_no += 1
            
   
        curd500 += data_dict["union_sale"]["NILGIRIS Union"]["curd500"]
        curd150 += data_dict["union_sale"]["NILGIRIS Union"]['curd150']
        curd5000 += data_dict["union_sale"]["NILGIRIS Union"]["curd5000"]
        buttermilk200 += data_dict["union_sale"]["NILGIRIS Union"]["buttermilk200"]
        total += data_dict["union_sale"]["NILGIRIS Union"]["total"]
   
    if data_dict["union_sale"]["NILGIRIS Union"]["curd500"] == 0 and data_dict["union_sale"]["NILGIRIS Union"]['curd150'] == 0 and data_dict["union_sale"]["NILGIRIS Union"]["curd5000"] == 0 and data_dict["union_sale"]["NILGIRIS Union"]["buttermilk200"] == 0:
        pass
    else:
        mycanvas.drawString(x_axis+10, y_axis, str(sl_no))
        mycanvas.drawString(x_axis+35, y_axis, str("NILGIRIS Union"))
        mycanvas.drawRightString(x_axis+305-100, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["curd500"]))
        mycanvas.drawRightString(x_axis+445-150, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]['curd150']))
        mycanvas.drawRightString(x_axis+570-15-170, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["curd5000"]))
        mycanvas.drawRightString(x_axis+590+85-220, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["buttermilk200"]))
        mycanvas.drawRightString(x_axis+590+85-120, y_axis, str(data_dict["union_sale"]["NILGIRIS Union"]["total"]))
        y_axis -= 25

    #lines
   
    mycanvas.line(x_axis_line, y_axis+20-5, x_axis_line + 575, y_axis+20-5)
   
    mycanvas.line(x_axis_line, y_axis_line-25, x_axis_line, y_axis+20-5)
    mycanvas.line(x_axis_line+40, y_axis_line-20, x_axis_line+40, y_axis-5)
    mycanvas.line(x_axis_line+140, y_axis_line-20, x_axis_line+140, y_axis-5)
    mycanvas.line(x_axis_line+320-95, y_axis_line-20, x_axis_line+320-95, y_axis-5)
    mycanvas.line(x_axis_line+405-90, y_axis_line-20, x_axis_line+405-90, y_axis-5)
    mycanvas.line(x_axis_line + 575-170, y_axis_line-20, x_axis_line + 575-170, y_axis-5)
    mycanvas.line(x_axis_line + 575-100, y_axis_line-20, x_axis_line + 575-100, y_axis-5)
    mycanvas.line(x_axis_line + 685-110, y_axis_line-20, x_axis_line + 685-110, y_axis-5)
   
    mycanvas.line(x_axis_line+40, y_axis-7, x_axis_line + 575, y_axis-7)
   
    mycanvas.drawString(x_axis+35, y_axis+3-5, "CBE Union Total")
    mycanvas.drawRightString(x_axis+305-100, y_axis+3-5, str(curd500))
    mycanvas.drawRightString(x_axis+445-150, y_axis+3-5, str(curd150))
    mycanvas.drawRightString(x_axis+570-15-170, y_axis+3-5, str(curd5000))
    mycanvas.drawRightString(x_axis+590+85-220, y_axis+3-5, str(buttermilk200))
    mycanvas.drawRightString(x_axis+590+85-120, y_axis+3-5, str(total))

#-----------------------------------------Cost-----------------------------------------#
    mycanvas.setFont('Helvetica', 13)
   
    mycanvas.drawCentredString(300, 280+4, "Total fermented Products Sale Amount")
#     mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
    mycanvas.line(406-100-50, 280, 593-200-50, 280)
   
    y_axis_head = 300-50
   
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawCentredString(40-x_a4, y_axis_head, "S.NO")
    mycanvas.drawCentredString(110-x_a4, y_axis_head, "Total Sale")
    mycanvas.drawCentredString(285-80-x_a4, y_axis_head, "Curd500")
    mycanvas.drawCentredString(430-140-x_a4, y_axis_head, "Curd150")
    mycanvas.drawCentredString(550-175-x_a4, y_axis_head, "Curd5000")
    mycanvas.drawCentredString(560-95-x_a4, y_axis_head, "Buttermilk")
    mycanvas.drawCentredString(560-15-x_a4, y_axis_head, "Total")
   
    y_axis_line = 398-40-50-40
    y_axis = 345-40-50-40
    x_axis_line = 20-x_a4
    x_axis = 30-x_a4
   
    mycanvas.line(x_axis_line, y_axis_line, x_axis_line + 575, y_axis_line)
    mycanvas.line(x_axis_line, y_axis_line-25, x_axis_line + 575, y_axis_line-25)
   
    sl_no = 1
   
    curd500 = 0
    curd150 = 0
    curd5000 = 0
    buttermilk200 = 0
    for sale in data_dict["Costs"]["Coimbatore Account"]:
       
        curd500 += data_dict["Costs"]["Coimbatore Account"][sale]["curd500"]
        curd150 += data_dict["Costs"]["Coimbatore Account"][sale]['curd150']
        curd5000 += data_dict["Costs"]["Coimbatore Account"][sale]["curd5000"]
        buttermilk200 += data_dict["Costs"]["Coimbatore Account"][sale]["buttermilk200"]
        total += data_dict["Costs"]["Coimbatore Account"][sale]["total"]
       
        if data_dict["Costs"]["Coimbatore Account"][sale]["curd500"] == 0 and data_dict["Costs"]["Coimbatore Account"][sale]['curd150'] == 0 and data_dict["Costs"]["Coimbatore Account"][sale]["curd5000"] == 0 and data_dict["Costs"]["Coimbatore Account"][sale]["buttermilk200"] == 0:
            continue
        else:
            mycanvas.drawString(x_axis+10, y_axis, str(sl_no))
            mycanvas.drawString(x_axis+35, y_axis, str(sale))
            mycanvas.drawRightString(x_axis+305-100, y_axis, str(data_dict["Costs"]["Coimbatore Account"][sale]["curd500"]))
            mycanvas.drawRightString(x_axis+445-150, y_axis, str(data_dict["Costs"]["Coimbatore Account"][sale]['curd150']))
            mycanvas.drawRightString(x_axis+570-15-170, y_axis, str(data_dict["Costs"]["Coimbatore Account"][sale]["curd5000"]))
            mycanvas.drawRightString(x_axis+590+85-220, y_axis, str(data_dict["Costs"]["Coimbatore Account"][sale]["buttermilk200"]))
            mycanvas.drawRightString(x_axis+590+85-120, y_axis, str(data_dict["Costs"]["Coimbatore Account"][sale]["total"]))
           
            y_axis -= 25
            sl_no += 1

        curd500 += data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["curd500"]
        curd150 += data_dict["Costs"]["union_sale"]["NILGIRIS Union"]['curd150']
        curd5000 += data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["curd5000"]
        buttermilk200 += data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["buttermilk200"]
        total += data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["total"]
   
    if data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["curd500"] == 0 and data_dict["Costs"]["union_sale"]["NILGIRIS Union"]['curd150'] == 0 and data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["curd5000"] == 0 and data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["buttermilk200"] == 0:
        pass
    else:
        mycanvas.drawString(x_axis+10, y_axis, str(sl_no))
        mycanvas.drawString(x_axis+35, y_axis, str("NILGIRIS Union"))
        mycanvas.drawRightString(x_axis+305-100, y_axis, str(data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["curd500"]))
        mycanvas.drawRightString(x_axis+445-150, y_axis, str(data_dict["Costs"]["union_sale"]["NILGIRIS Union"]['curd150']))
        mycanvas.drawRightString(x_axis+570-15-170, y_axis, str(data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["curd5000"]))
        mycanvas.drawRightString(x_axis+590+85-220, y_axis, str(data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["buttermilk200"]))
        mycanvas.drawRightString(x_axis+590+85-120, y_axis, str(data_dict["Costs"]["union_sale"]["NILGIRIS Union"]["total"]))
        y_axis -= 25
       
    #lines
      
    mycanvas.line(x_axis_line, y_axis+20-5, x_axis_line + 575, y_axis+20-5)
   
    mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis+20-5)
    mycanvas.line(x_axis_line+40, y_axis_line, x_axis_line+40, y_axis-5)
    mycanvas.line(x_axis_line+140, y_axis_line, x_axis_line+140, y_axis-5)
    mycanvas.line(x_axis_line+320-95, y_axis_line, x_axis_line+320-95, y_axis-5)
    mycanvas.line(x_axis_line+405-90, y_axis_line, x_axis_line+405-90, y_axis-5)
    mycanvas.line(x_axis_line + 575-170, y_axis_line, x_axis_line + 575-170, y_axis-5)
    mycanvas.line(x_axis_line + 575-100, y_axis_line, x_axis_line + 575-100, y_axis-5)
    mycanvas.line(x_axis_line + 685-110, y_axis_line, x_axis_line + 685-110, y_axis-5)
   
    mycanvas.line(x_axis_line+40, y_axis-7, x_axis_line + 575, y_axis-7)
   
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(x_axis+35, y_axis+3-5, "CBE Union Total Amount")
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawRightString(x_axis+305-100, y_axis+3-5, str(curd500))
    mycanvas.drawRightString(x_axis+445-150, y_axis+3-5, str(curd150))
    mycanvas.drawRightString(x_axis+570-15-170, y_axis+3-5, str(curd5000))
    mycanvas.drawRightString(x_axis+590+85-220, y_axis+3-5, str(buttermilk200))
    mycanvas.drawRightString(x_axis+590+85-120, y_axis+3-5, str(total))

    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawRightString(585, 5, 'Report Generated by: '+str(data_dict['user_name']+", @"+str(datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

    mycanvas.save()
    document = {}
    document['file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document



# -------------------------------------------------------------------------------------------------------------------------------#
def serve_product_diffrence_list(business_obj, data_for, group_id):
    if data_for == 'product_trace':
        product_trace_obj = ProductTrace.objects.filter(product__group_id=group_id)
        product_trace_list = list(product_trace_obj.values_list('product__short_name', 'mrp', 'start_date', 'end_date'))
        product_trace_column = ['product_name', 'mrp', 'start_date', 'end_date']
        df = pd.DataFrame(product_trace_list, columns=product_trace_column)
        final_dict = df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
        return final_dict
    elif data_for == 'business_type_wise':
        business_type_wise_trace_obj = BusinessTypeWiseProductDiscountTrace.objects.filter(business_type_wise_discount__business_type_id=business_obj.business_type_id, business_type_wise_discount__product__group_id=group_id)
        business_type_wise_trace_list = list(business_type_wise_trace_obj.values_list('business_type_wise_discount__product__short_name', 'discounted_price', 'start_date', 'end_date'))
        business_type_wise_trace_column = ['product_name', 'mrp', 'start_date', 'end_date']
        df = pd.DataFrame(business_type_wise_trace_list, columns=business_type_wise_trace_column)
        final_dict = df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
        return final_dict
    else:
        business_wise_trace_obj = BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount__business_id=business_obj.id, business_wise_discount__product__group_id=group_id)
        business_wise_trace_list = list(business_wise_trace_obj.values_list('business_wise_discount__product__short_name', 'discounted_price', 'start_date', 'end_date'))
        business_wise_trace_column = ['product_name', 'mrp', 'start_date', 'end_date']
        df = pd.DataFrame(business_wise_trace_list, columns=business_wise_trace_column)
        final_dict = df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
        return final_dict


def serve_product_price_for_date_range(business_codes, from_date, to_date, group_id):
    price_per_user_profile_dict = {}
    price_per_user_profile_as_dict_for_gst_bill = {}
    for business_code in business_codes:
        business_obj = Business.objects.get(code=business_code)
        if not business_obj.user_profile.id in price_per_user_profile_dict:
            price_per_user_profile_dict[business_obj.user_profile.id] = []
        if not business_obj.user_profile.id in price_per_user_profile_as_dict_for_gst_bill:
            price_per_user_profile_as_dict_for_gst_bill[business_obj.user_profile.id] = {}
        commission_product_ids = list(BusinessProductConcessionMap.objects.filter(business_type_id=business_obj.business_type_id, product__is_active=True, concession_type_id=1, product__group_id=group_id).values_list('product_id', flat=True))
        discount_product_ids = list(BusinessProductConcessionMap.objects.filter(business_type_id=business_obj.business_type_id, product__is_active=True, concession_type_id=2, product__group_id=group_id).values_list('product_id', flat=True))
        price_per_user_profile_dict[business_obj.user_profile.id] = []
        if len(commission_product_ids) != 0:
            for commission_product_id in commission_product_ids:
                if ProductTrace.objects.filter(product_id=commission_product_id).exists():
                    trace_ids = []
                    for product_trace in ProductTrace.objects.filter(product_id=commission_product_id):
                        date_list = pd.date_range(product_trace.start_date, product_trace.end_date)
                        if from_date in date_list :
                            trace_ids.append(product_trace.id)
                        if to_date in date_list:
                            trace_ids.append(product_trace.id)
                    if len(set(trace_ids)) == 1:
                        product_trace_id = trace_ids[0]
                        product_trace_obj = ProductTrace.objects.get(id=product_trace_id)
                        data_dict = {
                            'product_id': product_trace_obj.product.id,
                            'product_mrp': product_trace_obj.mrp
                        }
                        price_per_user_profile_as_dict_for_gst_bill[business_obj.user_profile.id][product_trace_obj.product.id] = product_trace_obj.mrp
                        price_per_user_profile_dict[business_obj.user_profile.id].append(data_dict)
                    else:
                        print(business_obj.code, commission_product_id)
                        data_dict = {
                            'is_multiple_price': True,
                            'return_data': serve_product_diffrence_list(business_obj, 'product_trace', group_id)
                        }
                        return data_dict
        business_type_id = business_obj.business_type_id
        if len(discount_product_ids) != 0:
            if business_type_id == 1 or business_type_id == 2 or business_type_id == 3 or business_type_id == 9 or business_type_id == 11 or business_type_id == 16:  
                print('check1')
                for discount_product_id in discount_product_ids:
                    if BusinessTypeWiseProductDiscountTrace.objects.filter(business_type_wise_discount__business_type_id=business_type_id, business_type_wise_discount__product_id=discount_product_id).exists():
                        trace_ids = []
                        for product_trace in BusinessTypeWiseProductDiscountTrace.objects.filter(business_type_wise_discount__business_type_id=business_type_id, business_type_wise_discount__product_id=discount_product_id):
                            date_list = pd.date_range(product_trace.start_date, product_trace.end_date)
                            print('business_type_id',business_type_id)
                            print('discount_product_id',discount_product_id)
                            if from_date in date_list :
                                trace_ids.append(product_trace.id)
                            if to_date in date_list:
                                trace_ids.append(product_trace.id)
                        print('id',len(set(trace_ids)),trace_ids)
                        if len(set(trace_ids)) == 1:
                            product_trace_id = trace_ids[0]
                            business_type_wise_trace_obj = BusinessTypeWiseProductDiscountTrace.objects.get(id=product_trace_id)
                            data_dict = {
                                'product_id': business_type_wise_trace_obj.business_type_wise_discount.product.id,
                                'product_mrp': business_type_wise_trace_obj.discounted_price
                            }
                            price_per_user_profile_as_dict_for_gst_bill[business_obj.user_profile.id][business_type_wise_trace_obj.business_type_wise_discount.product.id] = business_type_wise_trace_obj.discounted_price
                            price_per_user_profile_dict[business_obj.user_profile.id].append(data_dict)
                        else:
                            print(business_obj.code, discount_product_id)
                            data_dict = {
                                'is_multiple_price': True,
                                'return_data': serve_product_diffrence_list(business_obj, 'business_type_wise', group_id)
                            }
                            return data_dict
            else:
                print('check2')
                for discount_product_id in discount_product_ids:
                    if BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount__business_id=business_obj.id, business_wise_discount__product_id=discount_product_id).exists():
                        trace_ids = []
                        for product_trace in BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount__business_id=business_obj.id, business_wise_discount__product_id=discount_product_id):
                            date_list = pd.date_range(product_trace.start_date, product_trace.end_date)
                            if from_date in date_list :
                                trace_ids.append(product_trace.id)
                            if to_date in date_list:
                                trace_ids.append(product_trace.id)
                        if len(set(trace_ids)) == 0:
                            continue
                        if len(set(trace_ids)) == 1:
                            product_trace_id = trace_ids[0]
                            business_wise_trace_obj = BusinessWiseProductDiscountTrace.objects.get(id=product_trace_id)
                            data_dict = {
                                'product_id': business_wise_trace_obj.business_wise_discount.product.id,
                                'product_mrp': business_wise_trace_obj.discounted_price
                            }
                            price_per_user_profile_as_dict_for_gst_bill[business_obj.user_profile.id][business_wise_trace_obj.business_wise_discount.product.id] = business_wise_trace_obj.discounted_price
                            price_per_user_profile_dict[business_obj.user_profile.id].append(data_dict)
                        else:
                            print(business_obj.code, discount_product_id)
                            data_dict = {
                                'is_multiple_price': True,
                                'return_data': serve_product_diffrence_list(business_obj, 'business_wise', group_id)
                            }
                            return data_dict
    data_dict = {
        'is_multiple_price': False,
        'return_data': price_per_user_profile_dict,
        'return_data_as_dict': price_per_user_profile_as_dict_for_gst_bill
    }
    return data_dict
    
    
def serve_qty_and_short_name(start_date, end_date):
    product_dict = {}
    for product in Product.objects.filter():
        if not product.id in product_dict:
            product_dict[product.id] = {}
        trace_ids = []
        for product_trace in ProductNameAndQuantityTrace.objects.filter(product_id=product.id):
            date_list = pd.date_range(product_trace.start_date, product_trace.end_date)
            if start_date in date_list :
                trace_ids.append(product_trace.id)
            if end_date in date_list:
                trace_ids.append(product_trace.id)  
        if len(set(trace_ids)) == 0:
            continue            
        if len(set(trace_ids)) == 1:
            product_trace_id = trace_ids[0]
            product_trace_obj = ProductNameAndQuantityTrace.objects.get(id=product_trace_id)
            data_dict = {
                'qty': product_trace_obj.quantity,
                'short_name': product_trace_obj.short_name
            }
            product_dict[product.id] = data_dict
        else:
            data_dict = {
                'is_multiple_qty': True,
            }
            return data_dict
    final_dict = {
        'is_multiple_qty' : False,
        'product_dict': product_dict
    }
    return final_dict


@api_view(['POST'])
def generate_institution_bill_for_milk(request):
    # input part
    print(request.data)
    business_codes = []
    business_types = {}
    business_names = request.data['business_type_list']
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    exclude_booth_code = request.data['exclude_booth_code']

    date_list = pd.date_range(start=from_date, end=to_date)
    if request.data['option_type'] == 'by_business':
      business_codes = request.data['business_code_list']
      business_types['business']= business_codes
      business_names = business_codes
    elif request.data['option_type'] == 'by_business_type':
      for business_type in request.data['business_type_list']:
          if business_type == 'private_institute':
              pvt_business_code_list = list(Business.objects.filter(business_type_id=4).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += pvt_business_code_list
              business_types['private_institute'] = pvt_business_code_list
          elif business_type == 'govt_institute':
              gvt_business_code_list = list(Business.objects.filter(business_type_id=5).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += gvt_business_code_list
              business_types['govt_institute'] = gvt_business_code_list
          elif business_type == 'union_parlour':
            #   ['8105', '8115', '8104', '8101', '8117', '8116', '8109', '8123'] 
            # the above codes are used as static for dynamic purpose moved to DB 
              union_parlour_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=1).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_codes += union_parlour_business_code_list
              business_types['union_parlour'] = union_parlour_business_code_list
          elif business_type == 'union_booth':
            #   ['1', '1999', '2000'] 
              union_booth_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=2).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_types['union_booth'] = union_booth_business_code_list
              business_codes += union_booth_business_code_list
          elif business_type == 'nilgris':
              nilgris_booth_business_code_list = list(Business.objects.filter(zone_id=11).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += nilgris_booth_business_code_list
              business_types['nilgris'] = nilgris_booth_business_code_list
          elif business_type == 'tirupur':
              tirupur_booth_business_code_list = list(Business.objects.filter(zone_id=13).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += tirupur_booth_business_code_list
              business_types['tirupur'] = tirupur_booth_business_code_list
          elif business_type == 'society':
              society_business_code_list = list(Business.objects.filter(business_type_id=10).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += society_business_code_list
              business_types['society'] = society_business_code_list
          elif business_type == 'reliance':
              reliance_business_code_list = list(Business.objects.filter(business_group_id=1).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += reliance_business_code_list
              business_types['reliance'] = reliance_business_code_list
    business_codes_for_check = set(list(DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list, sold_to='Agent', business__code__in=business_codes).values_list('business__code', flat=True)))
    check_dict = serve_product_price_for_date_range(business_codes_for_check, from_date, to_date, 1)

    if check_dict['is_multiple_price']:
        return Response(data=check_dict, status=status.HTTP_200_OK)
    daily_sessionly_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list, sold_to='Agent')

    xlxs_file_name = "all_booth_milk_sale_"+str(date_list[0])[:10]+ " to " +str(date_list[-1])[:10] + f"_{business_names}" + ".xlsx"
    xlxs_file_path = os.path.join('static/media/zone_wise_report/', xlxs_file_name)

    df_dict = {}
    for instution in business_types:
      instution_sale_list = daily_sessionly_obj.filter(business__code__in=business_types[instution]).values_list('business__name', 'tm500_litre', 'tm500_cost', 'std250_litre', 'std250_cost', 'std500_litre', 'std500_cost', 'fcm500_litre', 'fcm500_cost', 'fcm1000_litre', 'fcm1000_cost', 'tea500_litre', 'tea500_cost', 'tea1000_litre', 'tea1000_cost','milk_litre', 'milk_cost')  
      instution_sale_column = ['Business', 'TM500 Litre', 'TM500 Cost', 'SM250 Litre', 'SM250 Cost', 'SM500 Litre', 'SM500 Cost', 'FCM500 Litre', 'FCM500 Cost', 'FCM1000 Litre', 'FCM1000 Cost', 'TMATE500 Litre', 'TMATE500 Cost', 'TMATE1000 Litre', 'TMATE1000 Cost','TOTAL Litre', 'TOTAL Cost']
      instution_sale_df = pd.DataFrame(instution_sale_list, columns=instution_sale_column)
      instution_sale_df = instution_sale_df.groupby('Business').agg({'TM500 Litre': sum, 'TM500 Cost': sum, 'SM250 Litre': sum, 'SM250 Cost': sum, 'SM500 Litre': sum, 'SM500 Cost': sum, 'FCM500 Litre': sum, 'FCM500 Cost': sum, 'FCM1000 Litre': sum, 'FCM1000 Cost': sum,'TMATE500 Litre': sum, 'TMATE500 Cost': sum, 'TMATE1000 Litre': sum, 'TMATE1000 Cost': sum, 'TOTAL Litre': sum, 'TOTAL Cost': sum}).reset_index() 

      instution_sale_df = instution_sale_df.append(instution_sale_df.sum(), ignore_index=True)
      instution_sale_df.iloc[-1, instution_sale_df.columns.get_loc('Business')] = 'Total'

      instution_sale_df = instution_sale_df[instution_sale_df['TOTAL Cost'] != 0]


      for i in list(instution_sale_df.columns)[1:]:
          if i[-5:] != 'Litre':
            instution_sale_df[i] = round(instution_sale_df[i].astype(float))
          else:
            instution_sale_df[i] = instution_sale_df[i].astype(float)


      instution_sale_df = instution_sale_df.reset_index(drop=True)
      instution_sale_df.index += 1
      df_dict[instution] = instution_sale_df

    with pd.ExcelWriter(xlxs_file_path) as writer:  
      for sheet_name in df_dict:
          df_dict[sheet_name].to_excel(writer, sheet_name=sheet_name)

    last_bill_number_count = InstititionBillNumberIdBank.objects.filter(id=1)[0].last_count
    bill_no = int(last_bill_number_count) + 1

    business_code_list = business_codes


    date_list = list(set(list(DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list).values_list('delivery_date', flat=True))))
    date_list =  sorted(date_list)
    
    
        # -----------------------------------------------------------getting data--------------------------------------------------------------------------- #
    
    bill_data_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list, business__code__in=business_code_list, sold_to='Agent' )

    #fill missing date
    date_fill_list = list(set(list(bill_data_obj.values_list('business__name','business_id', 'business__code', 'business__zone__name', 'business__user_profile_id'))))
    date_fill_column = ['business_name', 'business_id', 'business_code', 'zone_name', 'user_profile_id']
    date_fill_df = pd.DataFrame(date_fill_list, columns=date_fill_column)
    date_fill_df = date_fill_df.assign(date =  [date_list for i in date_fill_df.index])
    date_fill_df = date_fill_df.explode('date').reset_index(drop=True)

    #morning_df
    mor_bill_data_list = list(bill_data_obj.filter(session_id=1).values_list('business__name', 'delivery_date', 'tm500_litre', 'std250_litre', 'std500_litre', 'fcm500_litre', 'fcm1000_litre','tea500_litre', 'tea1000_litre'))
    mor_bill_data_column = ['business_name', 'date', 'tm500_mor', 'std250_mor', 'std500_mor', 'fcm500_mor', 'fcm1000_mor','tea500_mor', 'tea1000_mor']
    # print('mor_bill_data_column',mor_bill_data_column)
    mor_bill_data_df = pd.DataFrame(mor_bill_data_list, columns=mor_bill_data_column)
    print('check2',mor_bill_data_df)

    mor_group_by_df = mor_bill_data_df.groupby(['business_name', 'date']).agg({'tm500_mor': sum, 'std250_mor': sum, 'std500_mor': sum, 'fcm500_mor': sum, 'fcm1000_mor': sum, 'tea500_mor': sum, 'tea1000_mor': sum, }).reset_index()                 


    #evening_df
    eve_bill_data_list = list(bill_data_obj.filter(session_id=2).values_list('business__name', 'delivery_date', 'tm500_litre', 'std250_litre', 'std500_litre', 'fcm500_litre', 'fcm1000_litre','tea500_litre', 'tea1000_litre'))
    eve_bill_data_column = ['business_name', 'date', 'tm500_eve', 'std250_eve', 'std500_eve', 'fcm500_eve', 'fcm1000_eve','tea500_eve', 'tea1000_eve']

    eve_bill_data_df = pd.DataFrame(eve_bill_data_list, columns=eve_bill_data_column)


    eve_group_by_df = eve_bill_data_df.groupby(['business_name', 'date']).agg({'tm500_eve': sum, 'std250_eve': sum, 'std500_eve': sum, 'fcm500_eve': sum, 'fcm1000_eve': sum,'tea500_eve': sum, 'tea1000_eve': sum}).reset_index()                 

    # merg mor and eve df
    if mor_group_by_df.empty:
        mor_group_by_df = pd.DataFrame(mor_bill_data_list, columns=mor_bill_data_column, index=['null'])

    if eve_group_by_df.empty:
        eve_group_by_df = pd.DataFrame(eve_bill_data_list, columns=eve_bill_data_column, index=['null'])
    print('check3',mor_group_by_df)
    bill_df = pd.merge(mor_group_by_df, eve_group_by_df, left_on=['business_name', 'date'], right_on=['business_name', 'date'], how='outer')
    print('bill_df',bill_df['tea500_eve'])
    # bill_df.drop('null')

    # bill df and datefill_df
    bill_df = pd.merge(date_fill_df, bill_df, left_on=['business_name', 'date'], right_on=['business_name', 'date'], how='outer')

    bill_df = bill_df.fillna(Decimal("0.000"))
    print('check1',bill_df)
    bill_df["mor_total"] = bill_df['tm500_mor'] + bill_df['std250_mor'] + bill_df['std500_mor'] + bill_df['fcm500_mor'] + bill_df['fcm1000_mor'] + bill_df['tea500_mor'] + bill_df['tea1000_mor'] 
    print('a',bill_df["mor_total"])
    bill_df["eve_total"] = bill_df['tm500_eve'] + bill_df['std250_eve'] + bill_df['std500_eve'] + bill_df['fcm500_eve'] + bill_df['fcm1000_eve'] + bill_df['tea500_eve'] + bill_df['tea1000_eve']

    bill_filter_df = bill_df.groupby(['business_name']).agg({'mor_total': sum, 'eve_total':sum}).reset_index()
    bill_filter_df = bill_filter_df[(bill_filter_df['mor_total'] != 0) | (bill_filter_df['eve_total'] != 0)]
    valied = bill_df['business_name'].isin(bill_filter_df['business_name'])
    bill_df = bill_df[valied]

    bill_df_dict = bill_df.groupby(['business_name']).apply(lambda x:x.to_dict('r')).to_dict()
    
    
    # ----------------------------------------------------pdf part-------------------------------------------------------- #
    
    file_name = "all_booth_milk_sale_"+str(date_list[0])[:10]+ " to " +str(date_list[-1])[:10] + ".pdf"
    #     file_path = os.path.join('static/media', file_name)
    file_path = os.path.join('static/media/zone_wise_report', file_name)

    from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
    to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
    
    mycanvas = canvas.Canvas(file_path, pagesize=A4) 
    light_color = 0x000000
    dark_color = 0x000000

    route_obj = RouteBusinessMap.objects.all()

    zone_num_dict = {
              "EAST": "(94890 43713)",
              "WEST": "(94890 43711)",
              "SOUTH": "(94890 43708)",
              "POLLACHI": "(94890 43708)",
              "NORTH": "(94890 43700)",
              "MTP": "(94890 43711)",
              "NILGIRIS": "",
              "MPCS": "",
              "TIRUPPUR": "",
              "CURD Zone": "",
              "CHENNAI Aavin": "",
          }

    for datas in bill_df_dict:
        if BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=bill_df_dict[datas][0]['business_id'], product_group_type_id=1).exists():
          temp_bill_number = BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=bill_df_dict[datas][0]['business_id'], product_group_type_id=1)[0].bill_number
        else:
          temp_bill_number = bill_no
          business_wise_bill_number = BusinessWiseBillNumber(from_date=from_date, to_date=to_date, business_id=bill_df_dict[datas][0]['business_id'], bill_number=temp_bill_number, created_by=request.user, product_group_type_id=1)
          business_wise_bill_number.save()
          bill_no +=1
        business_code = bill_df_dict[datas][0]['business_code']
        business_name = bill_df_dict[datas][0]['business_name']
        business_zone = bill_df_dict[datas][0]['zone_name']
        user_profile_id = bill_df_dict[datas][0]['user_profile_id']
        bill_no_of = temp_bill_number

        product_dict = check_dict['return_data'][user_profile_id]

        tm500 = 0
        sm250 = 0
        sm500 = 0
        fcm500 = 0
        fcm1000 = 0
        tea500 = 0
        tea1000 = 0

        for product in product_dict:
            if product["product_id"] == 1:
                tm500 = product["product_mrp"] * 2
            if product["product_id"] == 3:
                sm250 = product["product_mrp"] * 4
            if product["product_id"] == 2:
                sm500 = product["product_mrp"] * 2
            if product["product_id"] == 4:
                fcm500 = product["product_mrp"] * 2
            if product["product_id"] == 6:
                fcm1000 = product["product_mrp"]
            if product["product_id"] == 33:
                tea500 = product["product_mrp"] * 2
            if product["product_id"] == 34:
                tea1000 = product["product_mrp"]    

        route_name = route_obj.filter(business__code=business_code).order_by('route__session_id')[0].route.name[:-4]

        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 13)
        mycanvas.setFillColor(HexColor(dark_color))
        # mycanvas.drawCentredString(500-150, 560+ 40+200+2, str(business_name.upper()))
        mycanvas.setDash(6,3)
        mycanvas.setLineWidth(0)
    #     mycanvas.line(406-150, 557+ 40+200+2, 593-150, 557+ 40+200+2)
        mycanvas.drawCentredString(300, 560+ 41+200+1, 'GST NO.: ' + str("33AAAAT7787L2ZU"))

        # top_double_line
        mycanvas.line(10, 530+ 40+ 10+200+15, 585, 530+ 40+ 10+200+15)
    #     mycanvas.line(10, 527+ 40+ 10+200-5, 710, 527+ 40+ 10+200-5)
        # under_double_line
    #     mycanvas.line(10, 510+ 40+ 10+200-5, 710, 510+ 40+ 10+200-5)
        mycanvas.line(10, 507+ 40+ 10+200+15, 585, 507+ 40+ 10+200+15)


    #     # BILL FOR THE SUPPLY OF MILK
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawString(10,514+ 60+ 10+200-5,"BILL FOR THE SUPPLY OF MILK ") 

        mycanvas.drawRightString(450,514+ 60+ 10+200-5,"ROUTE : "+str(route_name))

        mycanvas.drawRightString(585,514+ 60+ 10+200-5,"Bill No.: "+str(bill_no_of))


        mycanvas.drawRightString(585,507+ 40+ 10+200-8,"  PERIOD : FROM "+str(datetime.strftime(from_date, '%d/%m/%Y'))+" TO "+str(datetime.strftime(to_date, '%d/%m/%Y')))


        mycanvas.setFont('Helvetica', 13)
        mycanvas.drawString(10, 507+ 40+ 10+200-8, str(business_name.upper()))
    #         mycanvas.drawString(100, 507+ 40+ 10+200-8, str(route_name))
        mycanvas.setFont('Helvetica', 10)

        # UNDER BILL FOR THE SUPPLY OF MILK
        mycanvas.line(10, 475+ 40+ 10+200+10, 585, 475+ 40+ 10+200+10)
        mycanvas.line(10, 473+ 40+ 10+200+10, 585, 473+ 40+ 10+200+10)


        x_axis_line = 10
        y_axis_line = 473+ 40+ 10+200+10
        y_axis = 443+ 40+ 10+200+10
        # Heading
        handy = 50

        mycanvas.drawString(x_axis_line+5,y_axis-3,"Date")
        x_adjust = 33
        head_list = ["TM500","SM250","SM500","FCM500","FCM1000","TMT500","TMT1000","TOTAL"]
        for head in head_list:
            mycanvas.drawString(x_axis_line +x_adjust,y_axis-3,"Mor")
            x_adjust += 35
            mycanvas.drawCentredString(x_axis_line +x_adjust-20,y_axis+15,str(head))
            mycanvas.drawString(x_axis_line +x_adjust,y_axis-3,"Eve")
            x_adjust += 34

        mycanvas.line(x_axis_line, y_axis+11, 585, y_axis + 11)
        mycanvas.line(x_axis_line, y_axis-8, 585, y_axis-8)
        mycanvas.line(x_axis_line, y_axis-10, 585, y_axis-10)

        tm500_mor = 0
        std250_mor = 0
        std500_mor = 0
        fcm500_mor = 0
        fcm1000_mor = 0
        tea500_mor = 0
        tea1000_mor = 0
        tm500_eve = 0
        std250_eve = 0
        std500_eve = 0
        fcm500_eve = 0
        fcm1000_eve = 0
        tea500_eve = 0
        tea1000_eve = 0
        mor_total = 0
        eve_total = 0

        x_adjust = -7

        for value in bill_df_dict[datas]:
            mycanvas.setFont('Helvetica', 8)

            mycanvas.drawString(x_axis_line+10 +x_adjust,y_axis-25,str(value['date'])[-2:])
            x_adjust += 35

            if value['tm500_mor'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['tm500_mor'],3)))
                tm500_mor += value['tm500_mor']
            x_adjust += 35

            if value['tm500_eve'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['tm500_eve'],3)))
                tm500_eve += value['tm500_eve']
            x_adjust += 35

            if value['std250_mor'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['std250_mor'],3)))
                std250_mor += value['std250_mor']
            x_adjust += 35

            if value['std250_eve'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['std250_eve'],3)))
                std250_eve += value['std250_eve']
            x_adjust += 35

            if value['std500_mor'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['std500_mor'],3)))
                std500_mor += value['std500_mor']
            x_adjust += 35

            if value['std500_eve'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['std500_eve'],3)))
                std500_eve += value['std500_eve']
            x_adjust += 35

            if value['fcm500_mor'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['fcm500_mor'],3)))
                fcm500_mor += value['fcm500_mor']
            x_adjust += 35

            if value['fcm500_eve'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['fcm500_eve'],3)))
                fcm500_eve += value['fcm500_eve']
            x_adjust += 35

            if value['fcm1000_mor'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['fcm1000_mor'],3)))
                fcm1000_mor += value['fcm1000_mor']
            x_adjust += 35

            if value['fcm1000_eve'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['fcm1000_eve'],3)))
                fcm1000_eve += value['fcm1000_eve']
            x_adjust += 35

            if value['tea500_mor'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['tea500_mor'],3)))
                tea500_mor += value['tea500_mor']
            x_adjust += 33

            if value['tea500_eve'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['tea500_eve'],3)))
                tea500_eve += value['tea500_eve']
            x_adjust += 35

            if value['tea1000_mor'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['tea1000_mor'],3)))
                tea1000_mor += value['tea1000_mor']
            x_adjust += 33

            if value['tea1000_eve'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['tea1000_eve'],3)))
                tea1000_eve += value['tea1000_eve']
            x_adjust += 35
            if value['mor_total'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['mor_total'],3)))
                mor_total += value['mor_total']
            x_adjust += 35

            if value['eve_total'] !=0:
                mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-25,str(round(value['eve_total'],3)))
                eve_total += value['eve_total']
            x_adjust += 35



            y_axis -=12
            x_adjust = 0
    #     mycanvas.setFont('Helvetica', 8)
        x_adjust = 40
        y_axis -=5
        mycanvas.setFont('Helvetica', 8)

        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-65, "MRP Rs")
        mycanvas.drawRightString(x_axis_line +x_adjust+14,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-25,str(round(tm500_mor,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-45,str(round(tm500_eve + tm500_mor,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-65,str(round(tm500,2)))
        tm500_cost = (tm500_eve + tm500_mor) * tm500
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-85,str(round(tm500_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+5,y_axis-25,str(round(tm500_eve,3)))
        x_adjust += 33


        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-65, "MRP Rs")
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-25,str(round(std250_mor,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-45,str(round(std250_eve + std250_mor,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-65,str(round(sm250,2)))
        sm250_cost = (std250_eve + std250_mor) * sm250
        mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-85,str(round(sm250_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+5,y_axis-25,str(round(std250_eve,3)))
        x_adjust += 33


        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-65, "MRP Rs")
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-25,str(round(std500_mor,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-45,str(round(std500_eve + std500_mor,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-65,str(round(sm500,2)))
        sm500_cost = (std500_eve + std500_mor) * sm500
        mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-85,str(round(sm500_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+5,y_axis-25,str(round(std500_eve,3)))
        x_adjust += 33


        mycanvas.drawRightString(x_axis_line +x_adjust+17,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+24,y_axis-65, "MRP Rs")
        mycanvas.drawRightString(x_axis_line +x_adjust+17,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-25,str(round(fcm500_mor,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-45,str(round(fcm500_eve + fcm500_mor,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-65,str(round(fcm500,2)))
        fcm500_cost = (fcm500_eve + fcm500_mor) * fcm500
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-85,str(round(fcm500_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+10,y_axis-25,str(round(fcm500_eve,3)))
        x_adjust += 33


        mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+27,y_axis-65, "MRP Rs")
        mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+28,y_axis-25,str(round(fcm1000_mor,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-45,str(round(fcm1000_eve + fcm1000_mor,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-65,str(round(fcm1000,2)))
        fcm1000_cost = (fcm1000_eve + fcm1000_mor) * fcm1000
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-85,str(round(fcm1000_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-25,str(round(fcm1000_eve,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+24,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+31,y_axis-65, "MRP Rs")
        mycanvas.drawRightString(x_axis_line +x_adjust+24,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+31,y_axis-25,str(round(tea500_mor,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+30,y_axis-45,str(round(tea500_eve + tea500_mor,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-65,str(round(tea500,2)))
        tea500_cost = (tea500_eve + tea500_mor) * tea500
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-85,str(round(tea500_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-25,str(round(tea500_eve,3)))
        x_adjust += 33


        mycanvas.drawRightString(x_axis_line +x_adjust+28,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+35,y_axis-65, "MRP Rs")
        mycanvas.drawRightString(x_axis_line +x_adjust+28,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+36,y_axis-25,str(round(tea1000_mor,3)))
        x_adjust += 33

        mycanvas.drawRightString(x_axis_line +x_adjust+32,y_axis-45,str(round(tea1000_eve + tea1000_mor,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-65,str(round(tea1000,2)))
        tea1000_cost = (tea1000_eve + tea1000_mor) * tea1000
        mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-85,str(round(tea1000_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-25,str(round(tea1000_eve,3)))
        x_adjust += 33


        mycanvas.drawRightString(x_axis_line +x_adjust+32,y_axis-45, "LITRE")
        mycanvas.drawRightString(x_axis_line +x_adjust+32,y_axis-85, "COST")
        mycanvas.drawRightString(x_axis_line +x_adjust+35,y_axis-25,str(round(mor_total,3)))
        x_adjust += 33

        total_cost = tea1000_cost + tea500_cost + fcm1000_cost + fcm500_cost + sm500_cost + sm250_cost + tm500_cost
        mycanvas.drawRightString(x_axis_line +x_adjust+32,y_axis-45,str(round(eve_total + mor_total,3)))
        mycanvas.drawRightString(x_axis_line +x_adjust+30,y_axis-85,str(round(total_cost)))
        mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-25,str(round(eve_total,3)))

        x_adjust = 33
        y_axis +=5

        mycanvas.line(x_axis_line, y_axis-17, x_axis_line+575, y_axis-17)
        mycanvas.line(x_axis_line, y_axis-37, x_axis_line+575, y_axis-37)
        mycanvas.line(x_axis_line, y_axis-57, x_axis_line+575, y_axis-57)
        mycanvas.line(x_axis_line, y_axis-77, x_axis_line+575, y_axis-77)
        mycanvas.line(x_axis_line, y_axis-97, x_axis_line+575, y_axis-97)
        #--lines--
        mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+50-20, y_axis_line, x_axis_line+50-20, y_axis-17-40-20)
        mycanvas.line(x_axis_line+90-30, y_axis_line-20, x_axis_line+90-30, y_axis-17-20)
        mycanvas.line(x_axis_line+150-60, y_axis_line, x_axis_line+150-60, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+125, y_axis_line-20, x_axis_line+125, y_axis-17-20)
        mycanvas.line(x_axis_line+160, y_axis_line, x_axis_line+160, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+198, y_axis_line-20, x_axis_line+198, y_axis-17-20)
        mycanvas.line(x_axis_line+230, y_axis_line, x_axis_line+230, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+270, y_axis_line-20, x_axis_line+270, y_axis-17-20)
        mycanvas.line(x_axis_line+300, y_axis_line, x_axis_line+300, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+335, y_axis_line-20, x_axis_line+335, y_axis-17-20)
        mycanvas.line(x_axis_line+370, y_axis_line, x_axis_line+370, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+405, y_axis_line-20, x_axis_line+405, y_axis-17-20)
        mycanvas.line(x_axis_line+440, y_axis_line, x_axis_line+440, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+475, y_axis_line-20, x_axis_line+475, y_axis-17-20)
        mycanvas.line(x_axis_line+502, y_axis_line, x_axis_line+502, y_axis-17-40-20-20)
        mycanvas.line(x_axis_line+540, y_axis_line-20, x_axis_line+540, y_axis-17-20)
        mycanvas.line(585, y_axis_line,585, y_axis-17-40-20-20)


        words = num2words(round(total_cost), lang='en_IN')
        mycanvas.setFont('Helvetica', 11)
        mycanvas.drawString(x_axis_line,y_axis-37-40-20-20,"GST=0% " + "  Rupees  "+str(words.upper())+" "+"Only")
        mycanvas.drawString(x_axis_line,y_axis-57-40-25+2-20,"Terms and Conditions:")
        mycanvas.drawRightString(585,y_axis-57-40-25+2-20,"for GENERAL MANAGER")
        mycanvas.line(x_axis_line, y_axis-57-45-25+2-20, x_axis_line + 130, y_axis-57-45-25+2-20)
        mycanvas.drawString(x_axis_line,y_axis-67-45-7-25+2-20,"1. The bills should be settled within 15 days of the receipt of bill.")
        mycanvas.drawString(x_axis_line,y_axis-77-50-9-25+2-20,"2. Any difference in the bill should be informed immediately to Zonal DM. " + str(zone_num_dict[business_zone]) +",")
        mycanvas.drawString(x_axis_line,y_axis-87-55-11-25+2-20,"    or to this office 0422-2607971,0422-2544777, aavincbemkg@gmail.com")
        mycanvas.drawString(x_axis_line,y_axis-97-60-13-25+2-20,"3. Enclose the payment slip alongwith the payment without fail.")
        mycanvas.drawString(x_axis_line,y_axis-107-65-15-25+2-20,"E & OE")

        #Payement Slip double line
        mycanvas.line(10, y_axis-107-65-5-25-20+2-20, 710, y_axis-107-65-5-25-20+2-20)
        mycanvas.line(10, y_axis-107-65-5-25-22+2-20, 710, y_axis-107-65-5-25-22+2-20)

        mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-42+4-20,"P  A  Y  M  E  N  T    S  L  I  P     T  0     A  A  V  I  N     -  C  O  I  M  B  A  T  O  R  E")
        mycanvas.line(10, y_axis-107-65-5-25-45+4-20, 500-80, y_axis-107-65-5-25-45+4-20)

        mycanvas.setFont('Helvetica', 11)
        mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-15+4-20,"Code                                         :     " +str(business_code))
        mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-30+4-20,"Name of the institution             :     "+str(business_name))
        mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-45+4-20,"Bill No/Month/Amount              :     "+str(bill_no_of)+" / "+str(datetime.strftime(from_date, '%b-%Y'))+ " / "+"Rs. "+str(round(total_cost)))     
        mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-60+4-20,"Details of Payment                    :      "+"Ch.No.: "+"                 "+"Date :")
        mycanvas.setFont('Helvetica', 11)

        mycanvas.showPage()

    mycanvas.save()

    bill_idbank_obj = InstititionBillNumberIdBank.objects.filter(id=1)[0]
    bill_idbank_obj.last_count = int(bill_no) - 1
    bill_idbank_obj.save()

    document = {}
    document['file_name'] = file_name
    document['excel_file_name'] = xlxs_file_name
    document['is_multiple_price'] = check_dict['is_multiple_price']
    try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['pdf'] = encoded_image
    except Exception as err:
      print(err)
    
    try:
      image_path = xlxs_file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
    except Exception as err:
      print(err)

    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def generate_institution_bill_for_curd(request):
    print(request.data)
    business_codes = []
    business_types = {}
    business_names = request.data['business_type_list']
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    exclude_booth_code = request.data['exclude_booth_code']
    date_list = pd.date_range(start=from_date, end=to_date)
    if request.data['option_type'] == 'by_business':
      business_codes = request.data['business_code_list']
      business_types['business']= business_codes
      business_names = business_codes
    elif request.data['option_type'] == 'by_business_type':
      for business_type in request.data['business_type_list']:
          if business_type == 'private_institute':
              pvt_business_code_list = list(Business.objects.filter(business_type_id=4).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += pvt_business_code_list
              business_types['private_institute'] = pvt_business_code_list
          elif business_type == 'govt_institute':
              gvt_business_code_list = list(Business.objects.filter(business_type_id=5).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += gvt_business_code_list
              business_types['govt_institute'] = gvt_business_code_list
          elif business_type == 'union_parlour':
            #   ['8105', '8115', '8104', '8101', '8117', '8116', '8109', '8123'] 
            # the above codes are used as static for dynamic purpose moved to DB 
              union_parlour_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=1).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_codes += union_parlour_business_code_list
              business_types['union_parlour'] = union_parlour_business_code_list
          elif business_type == 'union_booth':
            #   ['1', '1999', '2000'] 
              union_booth_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=2).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_types['union_booth'] = union_booth_business_code_list
              business_codes += union_booth_business_code_list
          elif business_type == 'nilgris':
              nilgris_booth_business_code_list = list(Business.objects.filter(zone_id=11).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += nilgris_booth_business_code_list
              business_types['nilgris'] = nilgris_booth_business_code_list
          elif business_type == 'tirupur':
              tirupur_booth_business_code_list = list(Business.objects.filter(zone_id=13).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += tirupur_booth_business_code_list
              business_types['tirupur'] = tirupur_booth_business_code_list
          elif business_type == 'society':
              society_business_code_list = list(Business.objects.filter(business_type_id=10).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += society_business_code_list
              business_types['society'] = society_business_code_list
          elif business_type == 'reliance':
              reliance_business_code_list = list(Business.objects.filter(business_group_id=1).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += reliance_business_code_list
              business_types['reliance'] = reliance_business_code_list
    business_codes_for_check = set(list(DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list, sold_to='Agent', business__code__in=business_codes).values_list('business__code', flat=True)))

    check_dict = serve_product_price_for_date_range(business_codes_for_check, from_date, to_date, 2)
    if check_dict['is_multiple_price']:
        return Response(data=check_dict, status=status.HTTP_200_OK)

    product_quantity_check_dict = serve_qty_and_short_name(from_date, to_date)
    if product_quantity_check_dict['is_multiple_qty']:
        return Response(data=document, status=status.HTTP_404_NOT_FOUND)


        
    daily_sessionly_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list, sold_to='Agent')

    xlxs_file_name = "all_booth_curd_sale_"+str(date_list[0])[:10]+ " to " +str(date_list[-1])[:10] + f"_{business_names}" + ".xlsx"
    xlxs_file_path = os.path.join('static/media/zone_wise_report/', xlxs_file_name)

    df_dict = {}
    for instution in business_types:
        instution_sale_list = daily_sessionly_obj.filter(business__code__in=business_types[instution]).values_list('business__name', 'curd500_kgs', 'curd500_cost', 'curd150_kgs', 'curd150_cost', 
                                                                                                                    'curd5000_kgs', 'curd5000_cost', 'buttermilk200_litre', 'buttermilk200_cost', 'curd_kgs', 
                                                                                                                    'curd_cost', 'buttermilk_litre', 'buttermilk_cost', 'bm_jar200_litre', 'bm_jar200_cost')  

        instution_sale_column = ['Business', 'CURD500 Kgs', 'CURD500 Cost', 'CURD150 Kgs', 'CURD150 Cost', 'CUPCURD Kgs', 'CUPCURD Cost', 'BUTTERMILK200 Litre', 'BUTTERMILK200 Cost', 'CURD Kgs', 'CURD Cost', 'BUTTERMILK Litre', 'BUTTERMILK Cost', 'BMJAR Litre', 'BMJAR Cost']  
        instution_sale_df = pd.DataFrame(instution_sale_list, columns=instution_sale_column)
        instution_sale_df = instution_sale_df.groupby('Business').agg({'CURD500 Kgs': sum, 'CURD500 Cost': sum, 'CURD150 Kgs': sum, 'CURD150 Cost': sum, 'CURD500 Kgs': sum, 'CURD500 Cost': sum, 'BUTTERMILK200 Litre': sum, 'BUTTERMILK200 Cost': sum, 'CURD Kgs': sum, 'CURD Cost': sum, 'BUTTERMILK Litre': sum, 'BUTTERMILK Cost': sum, 'BMJAR Litre': sum, 'BMJAR Cost': sum}).reset_index() 

        instution_sale_df['TOTAL Kgs'] = instution_sale_df['BUTTERMILK Litre'] + instution_sale_df['CURD Kgs']
        instution_sale_df['TOTAL Cost'] = instution_sale_df['BUTTERMILK Cost'] + instution_sale_df['CURD Cost']

        instution_sale_df = instution_sale_df.drop(columns=['BUTTERMILK Litre', 'BUTTERMILK Cost', 'CURD Kgs', 'CURD Cost'])

        instution_sale_df = instution_sale_df.append(instution_sale_df.sum(), ignore_index=True)
        instution_sale_df.iloc[-1, instution_sale_df.columns.get_loc('Business')] = 'Total'

        instution_sale_df = instution_sale_df[instution_sale_df['TOTAL Cost'] != 0]
        for i in list(instution_sale_df.columns)[1:]:
            if i[-3:] != 'Kgs' and i[-5:] != 'Litre':
                instution_sale_df[i] = round(instution_sale_df[i].astype(float))
            else:
                instution_sale_df[i] = instution_sale_df[i].astype(float)

        instution_sale_df = instution_sale_df.reset_index(drop=True)
        instution_sale_df.index += 1
        df_dict[instution] = instution_sale_df

    with pd.ExcelWriter(xlxs_file_path) as writer:  
        for sheet_name in df_dict:
            df_dict[sheet_name].to_excel(writer, sheet_name=sheet_name)

    last_bill_number_count = InstititionBillNumberIdBank.objects.filter(id=1)[0].last_count
    bill_no = int(last_bill_number_count) + 1

    business_code_list = business_codes

    date_list = list(set(list(DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list).values_list('delivery_date', flat=True))))
    date_list =  sorted(date_list)

    #----------------------------------input getting---------------------------------------------#
    bill_data_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list, business__code__in=business_code_list, sold_to='Agent' )

    #fill missing date
    date_fill_list = list(set(list(bill_data_obj.values_list('business__name','business_id', 'business__code', 'business__zone__name', 'business__user_profile_id'))))
    date_fill_column = ['business_name', 'business_id', 'business_code', 'zone_name', 'user_profile_id']
    date_fill_df = pd.DataFrame(date_fill_list, columns=date_fill_column)
    date_fill_df = date_fill_df.assign(date =  [date_list for i in date_fill_df.index])
    date_fill_df = date_fill_df.explode('date').reset_index(drop=True)

    #morning_df
    mor_bill_data_list = list(bill_data_obj.filter(session_id=1).values_list('business__name', 'delivery_date', 'curd500_kgs', 'curd150_kgs', 'curd5000_kgs', 'buttermilk200_litre', 'bm_jar200_litre'))
    mor_bill_data_column = ['business_name', 'date', 'curd500_mor', 'curd150_mor', 'curd5000_mor', 'buttermilk200_mor', 'bm_jar200_mor']

    mor_bill_data_df = pd.DataFrame(mor_bill_data_list, columns=mor_bill_data_column)

    if mor_bill_data_df.empty:
        mor_group_by_df = mor_bill_data_df
    else:
        mor_group_by_df = mor_bill_data_df.groupby(['business_name', 'date']).agg({'curd500_mor': sum, 'curd150_mor': sum, 'curd5000_mor': sum, 'buttermilk200_mor': sum, 'bm_jar200_mor': sum}).reset_index()                 

    #evening_df
    eve_bill_data_list = list(bill_data_obj.filter(session_id=2).values_list('business__name', 'delivery_date', 'curd500_kgs', 'curd150_kgs', 'curd5000_kgs', 'buttermilk200_litre', 'bm_jar200_litre'))
    eve_bill_data_column = ['business_name', 'date', 'curd500_eve', 'curd150_eve', 'curd5000_eve', 'buttermilk200_eve', 'bm_jar200_eve']
    eve_bill_data_df = pd.DataFrame(eve_bill_data_list, columns=eve_bill_data_column)
    
    if eve_bill_data_df.empty:
        if not mor_group_by_df.empty:
            eve_bill_data_df['business_name'] = mor_group_by_df['business_name']
            eve_bill_data_df['date'] = mor_group_by_df['date']
            eve_bill_data_df = eve_bill_data_df.fillna(0)
            eve_group_by_df = eve_bill_data_df.groupby(['business_name', 'date']).agg({'curd500_eve': sum, 'curd150_eve': sum, 'curd5000_eve': sum, 'buttermilk200_eve': sum, 'bm_jar200_eve': sum}).reset_index()              
        else:
            eve_group_by_df = eve_bill_data_df
    else:
        eve_group_by_df = eve_bill_data_df.groupby(['business_name', 'date']).agg({'curd500_eve': sum, 'curd150_eve': sum, 'curd5000_eve': sum, 'buttermilk200_eve': sum, 'bm_jar200_eve': sum}).reset_index()              

    if mor_group_by_df.empty and eve_group_by_df.empty:
        return Response(data=False, status=status.HTTP_200_OK)
    else:
        # merg mor and eve df
        bill_df = pd.merge(mor_group_by_df, eve_group_by_df, left_on=['business_name', 'date'], right_on=['business_name', 'date'], how='outer')
        # bill df and datefill_df
        bill_df = pd.merge(date_fill_df, bill_df, left_on=['business_name', 'date'], right_on=['business_name', 'date'], how='outer')

        bill_df = bill_df.fillna(Decimal("0.000"))

        bill_df["mor_total"] = bill_df['curd500_mor'] + bill_df['curd150_mor'] + bill_df['curd5000_mor'] + bill_df['buttermilk200_mor'] + bill_df['bm_jar200_mor']
        bill_df["eve_total"] = bill_df['curd500_eve'] + bill_df['curd150_eve'] + bill_df['curd5000_eve'] + bill_df['buttermilk200_eve'] + bill_df['bm_jar200_eve']
        
        bill_df['mor_total'] = bill_df['mor_total'].astype(float)
        bill_df['eve_total'] = bill_df['eve_total'].astype(float)
        
        bill_filter_df = bill_df.groupby(['business_name']).agg({'mor_total': sum, 'eve_total':sum}).reset_index()
        bill_filter_df = bill_filter_df[(bill_filter_df['mor_total'] != 0) | (bill_filter_df['eve_total'] != 0)]
        valied = bill_df['business_name'].isin(bill_filter_df['business_name'])
        bill_df = bill_df[valied]

        bill_df_dict = bill_df.groupby(['business_name']).apply(lambda x:x.to_dict('r')).to_dict()

        #---------------------------------------------------------------pdf-----------------------------------------------------------------------------------#

        file_name = "all_booth_curd_sale_"+str(date_list[0])[:10]+ " to " +str(date_list[-1])[:10] + ".pdf"
        # file_path = os.path.join('static/media', file_name)
        file_path = os.path.join('static/media/zone_wise_report/', file_name)

        mycanvas = canvas.Canvas(file_path, pagesize=A4)

        route_obj = RouteBusinessMap.objects.all()

        zone_num_dict = {
                "EAST": "(94890 43713)",
                "WEST": "(94890 43711)",
                "SOUTH": "(94890 43708)",
                "POLLACHI": "(94890 43708)",
                "NORTH": "(94890 43700)",
                "MTP": "(94890 43711)",
                "NILGIRIS": "",
                "MPCS": "",
                "TIRUPPUR": "",
                "CURD Zone": "",
                "CHENNAI Aavin": "",
            }

        light_color = 0x000000
        dark_color = 0x000000
        for datas in bill_df_dict:
            if BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=bill_df_dict[datas][0]['business_id'], product_group_type_id=2).exists():
                temp_bill_number = BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=bill_df_dict[datas][0]['business_id'], product_group_type_id=2)[0].bill_number
            else:
                temp_bill_number = bill_no
                business_wise_bill_number = BusinessWiseBillNumber(from_date=from_date, to_date=to_date, business_id=bill_df_dict[datas][0]['business_id'], bill_number=temp_bill_number, created_by=request.user, product_group_type_id=2)
                business_wise_bill_number.save()
                bill_no +=1

            business_code = bill_df_dict[datas][0]['business_code']
            business_name = bill_df_dict[datas][0]['business_name']
            business_zone = bill_df_dict[datas][0]['zone_name']
            user_profile_id = bill_df_dict[datas][0]['user_profile_id']
            bill_no_of = temp_bill_number
            curd500 = 0
            curd150 = 0
            curd_150_one_packet_cost = 0
            curd5000 = 0
            butter_milk = 0
            butter_milk_jar = 0
            product_dict = check_dict['return_data'][user_profile_id]
            product_quantity_dict = product_quantity_check_dict['product_dict']
            for product in product_dict:
                if product["product_id"] == 25:
                    product_qty = product_quantity_dict[25]['qty']
                    one_gram_price = product["product_mrp"] / product_qty
                    one_kg_price = one_gram_price * 1000
                    curd500 = one_kg_price
                    # curd500 = product["product_mrp"] * 2
                if product["product_id"] == 7:
                    product_qty = product_quantity_dict[7]['qty']
                    one_gram_price = product["product_mrp"] / product_qty
                    one_kg_price = one_gram_price * 1000
                    curd150 = one_kg_price
                    curd_150_one_packet_cost =  product["product_mrp"]
                if product["product_id"] == 32:
                    curd5000 = product["product_mrp"] / 5
                if product["product_id"] == 8:
                    butter_milk = product["product_mrp"] * 5 
                if product["product_id"] == 26:
                    butter_milk_jar = product["product_mrp"] * 5

            route_name = route_obj.filter(business__code=business_code).order_by('route__session_id')[0].route.name[:-4]

            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)
            # mycanvas.drawCentredString(500-150, 560+ 40+200+2, str(business_name.upper()))

            mycanvas.setDash(6,3)
            mycanvas.setLineWidth(0)
        #     mycanvas.line(406-150, 557+ 40+200+2, 593-150, 557+ 40+200+2)
            mycanvas.drawCentredString(300, 560+ 41+200+1, 'GST NO.: ' + str("33AAAAT7787L2ZU"))

            # top_double_line
            mycanvas.line(10, 530+ 40+ 10+200+15, 585, 530+ 40+ 10+200+15)
        #     mycanvas.line(10, 527+ 40+ 10+200-5, 710, 527+ 40+ 10+200-5)
            # under_double_line
        #     mycanvas.line(10, 510+ 40+ 10+200-5, 710, 510+ 40+ 10+200-5)
            mycanvas.line(10, 507+ 40+ 10+200+15, 585, 507+ 40+ 10+200+15)

            from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
            to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')

        #     # BILL FOR THE SUPPLY OF MILK
            mycanvas.setFont('Helvetica', 12)
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawString(10,514+ 60+ 10+200-5,"BILL FOR THE SUPPLY OF CURD & BUTTER MILK ")

            mycanvas.drawRightString(450,514+ 60+ 10+200-5,"ROUTE : "+str(route_name))

            mycanvas.drawRightString(585,514+ 60+ 10+200-5,"Bill No.: "+str(bill_no_of))

            mycanvas.drawRightString(585,507+ 40+ 10+200-8,"  PERIOD : FROM "+str(datetime.strftime(from_date, '%d/%m/%Y'))+" TO "+str(datetime.strftime(to_date, '%d/%m/%Y')))


            mycanvas.setFont('Helvetica', 13)
            mycanvas.drawString(10, 507+ 40+ 10+200-8, str(business_name.upper()))
            mycanvas.setFont('Helvetica', 8)

            # UNDER BILL FOR THE SUPPLY OF MILK
            mycanvas.line(10, 475+ 40+ 10+200+10, 585, 475+ 40+ 10+200+10)
            mycanvas.line(10, 473+ 40+ 10+200+10, 585, 473+ 40+ 10+200+10)


            x_axis_line = 10
            y_axis_line = 473+ 40+ 10+200+10
            y_axis = 443+ 40+ 10+200+10

            # Heading
            mycanvas.drawString(x_axis_line+5,y_axis-3,"Date")
            x_adjust = 45
            head_list = ["CURD500","CURD150","CURD5000","BUTTER MILK","BM JAR", "TOTAL"]
            i = 0
            for head in head_list:
                mycanvas.drawString(x_axis_line +x_adjust,y_axis-3,"Mor")
                x_adjust += 45
                mycanvas.drawCentredString(x_axis_line +x_adjust-15,y_axis+15,str(head))
                mycanvas.drawString(x_axis_line +x_adjust,y_axis-3,"Eve")
                x_adjust += 45

            mycanvas.line(x_axis_line, y_axis+11, x_axis_line+575, y_axis + 11)
            mycanvas.line(x_axis_line, y_axis-8, x_axis_line+575, y_axis-8)
            mycanvas.line(x_axis_line, y_axis-10, x_axis_line+575, y_axis-10)

            curd500_mor = 0
            curd150_mor = 0
            curd5000_mor = 0
            buttermilk200_mor = 0
            bm_jar200_mor = 0

            curd500_eve = 0
            curd150_eve = 0
            curd5000_eve = 0
            buttermilk200_eve = 0
            bm_jar200_eve = 0
            mor_total = 0
            eve_total = 0

            x_adjust = 0
            for value in bill_df_dict[datas]:
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawString(x_axis_line+10 +x_adjust,y_axis-25,str(value['date'])[-2:])
                x_adjust += 45


                if value['curd500_mor'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['curd500_mor'],3)))
                    curd500_mor += value['curd500_mor']
                x_adjust += 45

                if value['curd500_eve'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['curd500_eve'],3)))
                    curd500_eve += value['curd500_eve']
                x_adjust += 45

                if value['curd150_mor'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['curd150_mor'],3)))
                    curd150_mor += value['curd150_mor']
                x_adjust += 45

                if value['curd150_eve'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['curd150_eve'],3)))
                    curd150_eve += value['curd150_eve']
                x_adjust += 45


                if value['curd5000_mor'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(value['curd5000_mor'],3)))
                    curd5000_mor += value['curd5000_mor']
                x_adjust += 45

                if value['curd5000_eve'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-25,str(round(value['curd5000_eve'],3)))
                    curd5000_eve += value['curd5000_eve']
                x_adjust += 45

                if value['buttermilk200_mor'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-25,str(round(value['buttermilk200_mor'],3)))
                    buttermilk200_mor += value['buttermilk200_mor']
                x_adjust += 45

                if value['buttermilk200_eve'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-25,str(round(value['buttermilk200_eve'],3)))
                    buttermilk200_eve += value['buttermilk200_eve']
                x_adjust += 45

                if value['bm_jar200_mor'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-25,str(round(value['bm_jar200_mor'],3)))
                    bm_jar200_mor += value['bm_jar200_mor']
                x_adjust += 45

                if value['bm_jar200_eve'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-25,str(round(value['bm_jar200_eve'],3)))
                    bm_jar200_eve += value['bm_jar200_eve']
                x_adjust += 45

                if value['mor_total'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-25,str(round(value['mor_total'],3)))
                    mor_total += value['mor_total']
                x_adjust += 45

                if value['eve_total'] !=0:
                    mycanvas.drawRightString(x_axis_line +x_adjust+29,y_axis-25,str(round(value['eve_total'],3)))
                    eve_total += value['eve_total']
                x_adjust += 45


                y_axis -=12
                x_adjust = 0
            mycanvas.setFont('Helvetica', 7)
            x_adjust = 45

            y_axis -=5
            mycanvas.drawRightString(x_axis_line +x_adjust,y_axis-45, "KGs")
            mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-65, "MRP Rs")
            mycanvas.drawRightString(x_axis_line +x_adjust+7,y_axis-85, "COST")
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(curd500_mor,3)))
            x_adjust += 45

            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-45,str(round(curd500_mor + curd500_eve,3)))
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-65,str(round(curd500,2)))
            curd500_cost = (curd500_mor + curd500_eve) * curd500
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-85,str(round(curd500_cost)))
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(curd500_eve,3)))
            x_adjust += 45

            mycanvas.drawRightString(x_axis_line +x_adjust,y_axis-45, "KGs")
            mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-65, "MRP Rs")
            mycanvas.drawRightString(x_axis_line +x_adjust+7,y_axis-85, "COST")
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(curd150_mor,3)))
            x_adjust += 45


            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-45,str(round(curd150_eve + curd150_mor,3)))
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-65,str(round(curd150,2)))
            curd150_cost = (curd150_eve + curd150_mor) * curd150
            # curd150_cost = Decimal((float(curd150_eve + curd150_mor) / float(curd_150_obj/1000)) * float(curd_150_one_packet_cost))
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-85,str(round(curd150_cost)))
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(curd150_eve,3)))
            x_adjust += 45


            mycanvas.drawRightString(x_axis_line +x_adjust,y_axis-45, "KGs")
            mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-65, "MRP Rs")
            mycanvas.drawRightString(x_axis_line +x_adjust+7,y_axis-85, "COST")
            mycanvas.drawRightString(x_axis_line +x_adjust+25,y_axis-25,str(round(curd5000_mor,3)))
            x_adjust += 45

            mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-45,str(round(curd5000_mor + curd5000_eve,3)))
            mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-65,str(round(curd5000,2)))
            curd5000_cost = (curd5000_mor + curd5000_eve) * curd5000
            mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-85,str(round(curd5000_cost)))
            mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-25,str(round(curd5000_eve,3)))
            x_adjust += 45


            mycanvas.drawRightString(x_axis_line +x_adjust,y_axis-45, "KGs")
            mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-65, "MRP Rs")
            mycanvas.drawRightString(x_axis_line +x_adjust+7,y_axis-85, "COST")
            mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-25,str(round(buttermilk200_mor,3)))
            x_adjust += 45


            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-45,str(round(buttermilk200_eve + buttermilk200_mor,3)))
            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-65,str(round(butter_milk,2)))
            buttermilk200_cost = (buttermilk200_eve + buttermilk200_mor) * butter_milk
            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-85,str(round(buttermilk200_cost)))
            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-25,str(round(buttermilk200_eve,3)))
            x_adjust += 45


            mycanvas.drawRightString(x_axis_line +x_adjust,y_axis-45, "KGs")
            mycanvas.drawRightString(x_axis_line +x_adjust+15,y_axis-65, "MRP Rs")
            mycanvas.drawRightString(x_axis_line +x_adjust+7,y_axis-85, "COST")
            mycanvas.drawRightString(x_axis_line +x_adjust+23,y_axis-25,str(round(bm_jar200_mor,3)))
            x_adjust += 45

            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-45,str(round(bm_jar200_eve + bm_jar200_mor,3)))
            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-65,str(round(butter_milk_jar,2)))
            buttermilk200jar_cost = (bm_jar200_eve + bm_jar200_mor) * butter_milk_jar
            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-85,str(round(buttermilk200jar_cost)))
            mycanvas.drawRightString(x_axis_line +x_adjust+22,y_axis-25,str(round(bm_jar200_eve,3)))
            x_adjust += 45


            mycanvas.drawRightString(x_axis_line +x_adjust,y_axis-45, "KGs")
            mycanvas.drawRightString(x_axis_line +x_adjust+7,y_axis-85, "COST")
            mycanvas.drawRightString(x_axis_line +x_adjust+20,y_axis-25,str(round(mor_total,3)))
            x_adjust += 45


            total_cost = curd500_cost + curd150_cost + curd5000_cost + buttermilk200_cost+buttermilk200jar_cost
            mycanvas.drawRightString(x_axis_line +x_adjust+29,y_axis-45,str(round(eve_total + mor_total,3)))
            mycanvas.drawRightString(x_axis_line +x_adjust+29,y_axis-85,str(round(total_cost)))
            mycanvas.drawRightString(x_axis_line +x_adjust+29,y_axis-25,str(round(eve_total,3)))

            y_axis +=5


            mycanvas.line(x_axis_line, y_axis-17, x_axis_line+575, y_axis-17)
            mycanvas.line(x_axis_line, y_axis-37, x_axis_line+575, y_axis-37)
            mycanvas.line(x_axis_line, y_axis-57, x_axis_line+575, y_axis-57)
            mycanvas.line(x_axis_line, y_axis-77, x_axis_line+575, y_axis-77)
            mycanvas.line(x_axis_line, y_axis-97, x_axis_line+575, y_axis-97)

            #--lines--
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis-17-40-20-20)
            mycanvas.line(x_axis_line+50-20, y_axis_line, x_axis_line+50-20, y_axis-17-40)
            mycanvas.line(x_axis_line+132-25-32, y_axis_line-20, x_axis_line+132-25-32, y_axis-17-20)
            mycanvas.line(x_axis_line+213-35-60, y_axis_line, x_axis_line+213-35-60, y_axis-17-40-20-20)

            mycanvas.line(x_axis_line+294-55-76, y_axis_line-20, x_axis_line+294-55-76, y_axis-17-20)
            mycanvas.line(x_axis_line+375-60-107, y_axis_line, x_axis_line+375-60-107, y_axis-17-40-20-20)
            mycanvas.line(x_axis_line+456-65-136, y_axis_line-20, x_axis_line+456-65-136, y_axis-17-20)

            mycanvas.line(x_axis_line+537-80-159, y_axis_line, x_axis_line+537-80-159, y_axis-17-40-20-20)
            mycanvas.line(x_axis_line+618-95-182, y_axis_line-20, x_axis_line+618-95-182, y_axis-17-20)
            mycanvas.line(x_axis_line+699-100-213, y_axis_line, x_axis_line+699-100-213, y_axis-17-40-20-20)

            mycanvas.line(x_axis_line+700-113-155, y_axis_line-20, x_axis_line+700-113-155, y_axis-17-40+20)
            mycanvas.line(x_axis_line+700-69-155, y_axis_line, x_axis_line+700-69-155, y_axis-17-40-20-20)
            mycanvas.line(x_axis_line+700-180, y_axis_line-20, x_axis_line+700-180, y_axis-17-40+20)

            mycanvas.line(585, y_axis_line,585, y_axis-17-40-20-20)



            words = num2words(round(total_cost), lang='en_IN')
            mycanvas.setFont('Helvetica', 11)
            mycanvas.drawString(x_axis_line,y_axis-37-40-20-15-5,"GST=0%, " + "  Rupees.  "+str(words.upper())+" "+"Only")
            mycanvas.drawString(x_axis_line,y_axis-57-40-25+2-15,"Terms and Conditions:")
            mycanvas.drawRightString(585,y_axis-57-40-25+2-15,"for GENERAL MANAGER")
            mycanvas.line(x_axis_line, y_axis-57-45-25+2-15, x_axis_line + 130, y_axis-57-45-25+2-15)
            mycanvas.drawString(x_axis_line,y_axis-67-45-7-25+2-5-10,"1. The bills should be settled within 15 days of the receipt of bill.")
            mycanvas.drawString(x_axis_line,y_axis-77-50-9-25+2-10,"2. Any difference in the bill should be informed immediately to Zonal DM. " + str(zone_num_dict[business_zone]) +",")
            mycanvas.drawString(x_axis_line,y_axis-87-55-11-25+2-5-5,"    or to this office 0422-2607971,0422-2544777, aavincbemkg@gmail.com")
            mycanvas.drawString(x_axis_line,y_axis-97-60-13-25+2-5,"3. Enclose the payment slip alongwith the payment without fail.")
            mycanvas.drawString(x_axis_line,y_axis-107-65-15-25+2-5,"E & OE")

            #Payement Slip double line
            mycanvas.line(10, y_axis-107-65-5-25-20+2, 585, y_axis-107-65-5-25-20+2)
            mycanvas.line(10, y_axis-107-65-5-25-22+2, 585, y_axis-107-65-5-25-22+2)

            mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-42+4,"P  A  Y  M  E  N  T     S  L  I  P     T  0     A  A  V  I  N     -  C  O  I  M  B  A  T  O  R  E")
            mycanvas.line(10, y_axis-107-65-5-25-45+4, 500-80, y_axis-107-65-5-25-45+4)

            mycanvas.setFont('Helvetica', 11)
            mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-15+4,"Code                                         :     " +str(business_code))
            # mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-30+4,"Name of the institution             :     "+str(business_name))
            # route = RouteBusinessMap.objects.filter(business__code=business_code, route__session_id=1)[0].route.name[:-4]
            mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-30+4,"Name of the institution             :     "+str(business_name))
            mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-45+4,"Bill No/Month/Amount              :     "+str(bill_no_of)+" / "+str(datetime.strftime(from_date, '%b-%Y'))+ " / "+"Rs. "+str(round(total_cost)))
            mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-60+4,"Details of Payment                    :      "+"Ch.No.: "+"                 "+"Date :")
            mycanvas.setFont('Helvetica', 11)
            mycanvas.drawString(x_axis_line,y_axis-107-65-5-25-45-75+4,str(datetime.strftime(datetime.now(timezone('Asia/Kolkata')), '%d/%m/%Y - %I:%M %p')))
            mycanvas.showPage()

        mycanvas.save() 

        bill_idbank_obj = InstititionBillNumberIdBank.objects.filter(id=1)[0]
        bill_idbank_obj.last_count = int(bill_no) - 1
        bill_idbank_obj.save()

        document = {}
        document['file_name'] = file_name
        document['excel_file_name'] = xlxs_file_name
        document['is_file_available'] = True
        document['is_multiple_price'] = check_dict['is_multiple_price']

        try:
            image_path = file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)

        try:
            image_path = xlxs_file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['excel'] = encoded_image
        except Exception as err:
            print(err)

        return Response(data=document, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_tray_count_report(request):
  data_dict = {
      "grand_total":{
          "mor": 0,
          "eve": 0,
          "total": 0,
      },
      "date_wise": {},    
  }
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  date_list = pd.date_range(start=from_date, end=to_date)
  for date in date_list:
      date = str(date)[:10]
      format_date = datetime.strptime(date,'%Y-%m-%d')
      date_for= str(datetime.strftime(format_date, '%d-%m-%Y'))
      data_dict["date_wise"][date_for] = {
          "mor": 0,
          "eve": 0,
          "total": 0,
      }
      mornig_tray_obj = RouteTraceWiseSaleSummary.objects.filter(route_trace__date=date,route_trace__session_id=1)
      evenig_tray_obj = RouteTraceWiseSaleSummary.objects.filter(route_trace__date=date,route_trace__session_id=2)
    #   print('a',mornig_tray_obj)
    #   print('b',evenig_tray_obj)
      mor_trays = mornig_tray_obj.aggregate(Sum("tray_count"))["tray_count__sum"]
      print('c',mor_trays)
      eve_trays = evenig_tray_obj.aggregate(Sum("tray_count"))["tray_count__sum"]
      print('d',eve_trays)
      total_trays = mor_trays + eve_trays
      print('e',total_trays)
      
      data_dict["date_wise"][date_for]["mor"] = mor_trays
      data_dict["date_wise"][date_for]["eve"] = eve_trays
      data_dict["date_wise"][date_for]["total"] = total_trays
      
      #grand_total
      
      data_dict["grand_total"]["mor"] += mor_trays
      data_dict["grand_total"]["eve"] += eve_trays
      data_dict["grand_total"]["total"] += total_trays
      
  data_dict["user_name"] = request.user.first_name
  
  data = create_canvas_report_for_tray_count(data_dict,date_list)
  return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_report_for_tray_count(data_dict,date_list):
  file_name = "monthly_tray_count_for" + '_(' + str(date_list[0])[:10] + ' to '+str(date_list[-1])[:10] + ')' + '.pdf'
  file_path = os.path.join('static/media/route_wise_report/', file_name)
#     file_path = os.path.join('static/media/', file_name)

  mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))
  light_color = 0x000000
  dark_color = 0x000000
  x_a4 = 70
  y_a4 = 25
  mycanvas.setDash(6,3)
  mycanvas.setLineWidth(0)

  mycanvas.setFillColor(HexColor(dark_color))
  mycanvas.setFont('Helvetica', 12.5)
  mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
  mycanvas.setFont('Helvetica', 13)

  #Date
  from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
  to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
  mycanvas.drawCentredString(300, 795, "TRAY  CLEANING  DETAILS  FOR  DATE : " + str(datetime.strftime(from_date, '%d/%m/%Y'))+"  TO  "+str(datetime.strftime(to_date, '%d/%m/%Y')))

  mycanvas.drawCentredString(360-x_a4,720+20+y_a4,"NO.  OF  MILK  TRAYS  CLEANED")
  mycanvas.drawCentredString(120-x_a4,700-10+20+y_a4,"S.No")
  mycanvas.drawCentredString(120+70-x_a4,700-10+20+y_a4,"Date")
  mycanvas.drawCentredString(100+210-x_a4,700-10+20+y_a4,"MORNING")
  mycanvas.drawCentredString(100+330-x_a4,700-10+20+y_a4,"EVENING")
  mycanvas.drawCentredString(60+500-x_a4,700-10+20+y_a4,"TOTAL TRAYS")

  x_axis_line = 100-x_a4
  x_axis = 120-x_a4
  y_axis = 680+y_a4
  y_axis_line = 730+y_a4
  sl_no = 1
  mycanvas.setFont('Helvetica', 12)
  mycanvas.line(x_axis_line, y_axis_line+30, x_axis_line + 530, y_axis_line+30)
  mycanvas.line(x_axis_line, y_axis_line, x_axis_line + 530, y_axis_line)
  mycanvas.line(x_axis_line, y_axis_line-30, x_axis_line + 530, y_axis_line-30)

  for data in data_dict["date_wise"]:
      mycanvas.drawCentredString(x_axis,y_axis,str(sl_no))
      mycanvas.drawCentredString(x_axis+70,y_axis,str(data))
      mycanvas.drawRightString(x_axis+170+70,y_axis,str(data_dict["date_wise"][data]['mor']))
      mycanvas.drawRightString(x_axis+270+100,y_axis,str(data_dict["date_wise"][data]['eve']))
      mycanvas.drawRightString(x_axis+370+130,y_axis,str(data_dict["date_wise"][data]['total']))
      sl_no += 1
      y_axis -= 17

  #lines
  mycanvas.line(x_axis_line, y_axis, x_axis_line + 530, y_axis)
  mycanvas.line(x_axis_line, y_axis-20, x_axis_line + 530, y_axis-20)

  mycanvas.line(x_axis_line, y_axis_line+30, x_axis_line, y_axis-20)
  mycanvas.line(x_axis_line+40, y_axis_line, x_axis_line+40, y_axis)
  mycanvas.line(x_axis_line+140, y_axis_line, x_axis_line+140, y_axis-20)
  mycanvas.line(x_axis_line+270, y_axis_line, x_axis_line+270, y_axis-20)
  mycanvas.line(x_axis_line+400, y_axis_line, x_axis_line+400, y_axis-20)
  mycanvas.line(x_axis_line+530, y_axis_line+30, x_axis_line+530, y_axis-20)

  mycanvas.drawCentredString(x_axis+50,y_axis-15,"T  O  T  A  L")

  mycanvas.drawRightString(x_axis+170+70,y_axis-15,str(data_dict["grand_total"]['mor']))
  mycanvas.drawRightString(x_axis+270+100,y_axis-15,str(data_dict["grand_total"]['eve']))
  mycanvas.drawRightString(x_axis+370+130,y_axis-15,str(data_dict["grand_total"]['total']))

  mycanvas.drawRightString(x_axis+70,y_axis-45,"C E R T I F I C A T E")
  mycanvas.drawString(x_axis+10,y_axis-65,"1) Certified  that  the  above  mentioned  milk  trays  have  been  cleaned  ")
  mycanvas.drawString(x_axis+10,y_axis-85,"   by  the  contractor  for  the  month  _______________. ")

  mycanvas.drawCentredString(x_axis+50-30,y_axis-125,"DM(Dairy)")
  mycanvas.drawCentredString(300,y_axis-125,"M(Dairy)")
  mycanvas.drawCentredString(550-30,y_axis-125,"AGM(Dairy)")
  mycanvas.line(x_axis_line, y_axis-49, x_axis_line+100, y_axis-49)
#   mycanvas.setFont('Times-Italic', 10)
#   mycanvas.drawRightString(585, 5, 'Report Generated by: '+str(data_dict['user_name']+", @"+str(datetime.strftime(datetime.now(timezone('Asia/Kolkata')), '%d-%m-%Y, %I:%M %p'))))
  mycanvas.save()
  document = {}
  document['file_name'] = file_name
  try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['pdf'] = encoded_image
  except Exception as err:
      print(err)
  return document



@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_route_for_leakage_allowance_details(request):
    route_group_list = list(RouteGroupMap.objects.filter(mor_route_id__in=[85,99,145,143,241,123,126,147,149,151,153,136, 256, 250, 262, 270]).values('id', 'name'))
    eve_route_group_list = list(RouteGroupMap.objects.filter(eve_route_id__in=[86,100,144,146,127,120,148,150,154,152,134, 258, 252, 264, 272]).values('id', 'name'))
    route_group_list.extend(eve_route_group_list)
    print(route_group_list)
    route_group_list = list({value['id']: value for value in route_group_list}.values())
    print(route_group_list)
    return Response(data=route_group_list, status=status.HTTP_200_OK)

def serve_product_diffrence_list_for_l1(group_id):
    product_trace_obj = ProductTrace.objects.filter(product__group_id=group_id)
    product_trace_list = list(product_trace_obj.values_list('product__short_name', 'mrp', 'start_date', 'end_date'))
    product_trace_column = ['product_name', 'mrp', 'start_date', 'end_date']
    df = pd.DataFrame(product_trace_list, columns=product_trace_column)
    final_dict = df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
    return final_dict


def serve_product_price_for_date_range_for_l1(from_date, to_date, group_id):
    product_dict = {}
    for product in Product.objects.filter(group_id=group_id):
        if ProductTrace.objects.filter(product_id=product.id).exists():
            trace_ids = []
            for product_trace in ProductTrace.objects.filter(product_id=product.id):
                date_list = pd.date_range(product_trace.start_date, product_trace.end_date)
                if from_date in date_list :
                    trace_ids.append(product_trace.id)
                if to_date in date_list:
                    trace_ids.append(product_trace.id)
            if len(set(trace_ids)) == 1:
                product_trace_id = trace_ids[0]
                product_trace_obj = ProductTrace.objects.get(id=product_trace_id)
                if not product.id in product_dict:
                    product_dict[product.id] = product_trace_obj.mrp
            else:
                data_dict = {
                    'is_multiple_price': True,
                    'return_data': serve_product_diffrence_list_for_l1(group_id)
                }
                return data_dict
    data_dict = {
        'is_multiple_price': False,
        'return_data': product_dict
    }
    return data_dict


@api_view(['POST'])
def serve_leakage_allowance_details(request):
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  check_dict = serve_product_price_for_date_range_for_l1(from_date, to_date, 1)
  if check_dict['is_multiple_price']:
      return Response(data=check_dict, status=status.HTTP_200_OK)
  route_df = pd.DataFrame(request.data['route_list'])
  route_group_obj = RouteGroupMap.objects.filter(id__in=route_df['id'])
  mor_route_list = list(route_group_obj.values_list('mor_route_id', flat=True))
  eve_route_list = list(route_group_obj.values_list('eve_route_id', flat=True))
  final_route_list = mor_route_list + eve_route_list
  mor_route_obj = Route.objects.filter(is_temp_route=False,session_id=1, id__in=mor_route_list).order_by("name")
  eve_route_obj = Route.objects.filter(is_temp_route=False,session_id=2, id__in=eve_route_list).order_by("name")
  data_dict={
      "final_dict" : {
          "tm500":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
          "sm250":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
          "sm500":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
          "fcm500":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
          "fcm1000":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
          "tea500":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
          "tea1000":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
          "total":{
              "qty":0,
              "rate":0,
              "liter":0,
              "cost":0,
          },
      }
  }
  date_list = pd.date_range(start=from_date, end=to_date)


  for date in date_list:
      dates = str(date)[:10]
      for route in mor_route_obj:
          sale_obj = DailySessionllyBusinessllySale.objects.filter(sold_to="Leakage",route_id=route.id,delivery_date=dates)
          if sale_obj:
              format_date = datetime.strptime(dates,'%Y-%m-%d')
              date = str(datetime.strftime(format_date, '%d-%m-%Y'))
              
              if not route.name[:-4] in data_dict:
                  data_dict[route.name[:-4]] = {
                      "grand_total":0,
                  }
              if not date in data_dict[route.name[:-4]]:
                data_dict[route.name[:-4]][date] = {
                    "tm500": 0,
                    "sm250": 0,
                    "sm500": 0,
                    "fcm500": 0,
                    "fcm1000": 0,
                    "tea500": 0,
                    "tea1000": 0,
                    "total" : 0,
                }
              tm500 = sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
              sm250 = sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
              sm500 = sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
              fcm500 = sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
              fcm1000 = sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
              tea500 = sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
              tea1000 = sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
              
              data_dict[route.name[:-4]]["grand_total"] += tm500 + sm250 + sm500 + fcm500 + fcm1000 + tea500 + tea1000
              
              data_dict[route.name[:-4]][date]["tm500"] += sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
              data_dict[route.name[:-4]][date]["sm250"] += sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
              data_dict[route.name[:-4]][date]["sm500"] += sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
              data_dict[route.name[:-4]][date]["fcm500"] += sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
              data_dict[route.name[:-4]][date]["fcm1000"] += sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
              data_dict[route.name[:-4]][date]["tea500"] += sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
              data_dict[route.name[:-4]][date]["tea1000"] += sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
              data_dict[route.name[:-4]][date]["total"] += tm500+sm250+sm500+fcm500+fcm1000+tea500+tea1000
              
      for route in eve_route_obj:
          sale_obj = DailySessionllyBusinessllySale.objects.filter(sold_to="Leakage",route_id=route.id,delivery_date=dates)
          if sale_obj:
              format_date = datetime.strptime(dates,'%Y-%m-%d')
              date = str(datetime.strftime(format_date, '%d-%m-%Y'))
              if not route.name[:-4] in data_dict:
                  data_dict[route.name[:-4]] = {
                      "grand_total":0,
                  }
              if not date in data_dict[route.name[:-4]]:
                data_dict[route.name[:-4]][date] = {
                    "tm500": 0,
                    "sm250": 0,
                    "sm500": 0,
                    "fcm500": 0,
                    "fcm1000": 0,
                    "tea500": 0,
                    "tea1000": 0,
                    "total" : 0,
                }

              tm500 = sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
              sm250 = sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
              sm500 = sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
              fcm500 = sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
              fcm1000 = sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
              tea500 = sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
              tea1000 = sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
              
              data_dict[route.name[:-4]]["grand_total"] += tm500 + sm250 + sm500 + fcm500 + fcm1000 + tea500 + tea1000

              data_dict[route.name[:-4]][date]["tm500"] += sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
              data_dict[route.name[:-4]][date]["sm250"] += sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
              data_dict[route.name[:-4]][date]["sm500"] += sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
              data_dict[route.name[:-4]][date]["fcm500"] += sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
              data_dict[route.name[:-4]][date]["fcm1000"] += sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
              data_dict[route.name[:-4]][date]["tea500"] += sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
              data_dict[route.name[:-4]][date]["tea1000"] += sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
              data_dict[route.name[:-4]][date]["total"] += tm500+sm250+sm500+fcm500+fcm1000+tea500+tea1000

  product_price_dict = check_dict['return_data']
  final_obj = DailySessionllyBusinessllySale.objects.filter(sold_to="Leakage",delivery_date__in=date_list,route_id__in=final_route_list)

  data_dict["final_dict"]["tm500"]["qty"] = final_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
  data_dict["final_dict"]["tm500"]["rate"] = product_price_dict[1]
  data_dict["final_dict"]["tm500"]["liter"] = final_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
  data_dict["final_dict"]["tm500"]["cost"] = final_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum'] * product_price_dict[1]
  
  data_dict["final_dict"]["sm250"]["qty"] = final_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
  data_dict["final_dict"]["sm250"]["rate"] = product_price_dict[3]
  data_dict["final_dict"]["sm250"]["liter"] = final_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
  data_dict["final_dict"]["sm250"]["cost"] = final_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum'] * product_price_dict[3]
  
  data_dict["final_dict"]["sm500"]["qty"] = final_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
  data_dict["final_dict"]["sm500"]["rate"] = product_price_dict[2]
  data_dict["final_dict"]["sm500"]["liter"] = final_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
  data_dict["final_dict"]["sm500"]["cost"] = final_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum'] * product_price_dict[2]
  
  data_dict["final_dict"]["fcm500"]["qty"] = final_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
  data_dict["final_dict"]["fcm500"]["rate"] = product_price_dict[4]
  data_dict["final_dict"]["fcm500"]["liter"] = final_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
  data_dict["final_dict"]["fcm500"]["cost"] = final_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum'] * product_price_dict[4]
  
  data_dict["final_dict"]["fcm1000"]["qty"] = final_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
  data_dict["final_dict"]["fcm1000"]["rate"] = product_price_dict[6]
  data_dict["final_dict"]["fcm1000"]["liter"] = final_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
  data_dict["final_dict"]["fcm1000"]["cost"] = final_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum'] * product_price_dict[6]

  data_dict["final_dict"]["tea500"]["qty"] = final_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
  data_dict["final_dict"]["tea500"]["rate"] = product_price_dict[33]
  data_dict["final_dict"]["tea500"]["liter"] = final_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
  data_dict["final_dict"]["tea500"]["cost"] = final_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum'] * product_price_dict[33]
  
  data_dict["final_dict"]["tea1000"]["qty"] = final_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
  data_dict["final_dict"]["tea1000"]["rate"] = product_price_dict[34]
  data_dict["final_dict"]["tea1000"]["liter"] = final_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
  data_dict["final_dict"]["tea1000"]["cost"] = final_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum'] * product_price_dict[34]
  
  data_dict["final_dict"]["total"]["qty"] = final_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum'] + final_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum'] + final_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum'] + final_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum'] + final_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']  + final_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum'] + final_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
  data_dict["final_dict"]["total"]["rate"] = 0
  data_dict["final_dict"]["total"]["liter"] = final_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] + final_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] + final_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] + final_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] + final_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] + final_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] + final_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
  data_dict["final_dict"]["total"]["cost"] = data_dict["final_dict"]["tm500"]["cost"] + data_dict["final_dict"]["sm250"]["cost"] + data_dict["final_dict"]["sm500"]["cost"] + data_dict["final_dict"]["fcm500"]["cost"] + data_dict["final_dict"]["fcm1000"]["cost"] + data_dict["final_dict"]["tea500"]["cost"] + data_dict["final_dict"]["tea1000"]["cost"]
  
  data_dict["user_name"] = request.user.first_name
  data = create_canvas_report_for_leakage_allowance(data_dict,date_list)
  return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_report_for_leakage_allowance(data_dict,date_list):
  file_name = "monthly_leakage_allowance_for" + '_(' + str(date_list[0])[:10] + ' to '+str(date_list[-1])[:10] + ')' + '.pdf'
  file_path = os.path.join('static/media/route_wise_report/', file_name)
  mycanvas = canvas.Canvas(file_path, pagesize=A4)
  light_color = 0x000000
  dark_color = 0x000000

  mycanvas.setDash(6,3)
  mycanvas.setLineWidth(0)

  mycanvas.setFillColor(HexColor(dark_color))
  mycanvas.setFont('Helvetica', 12.5)
  mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
  mycanvas.setFont('Helvetica', 13)
  
  y_a4 = 30
  x_a4 = 10
  #Date
  from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
  to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
  mycanvas.drawCentredString(300, 795, "Leakage Allowance For DATE : " + str(datetime.strftime(from_date, '%d/%m/%Y'))+" TO "+str(datetime.strftime(to_date, '%d/%m/%Y')))

  y_axis_head = 730 + y_a4
  mycanvas.setFont('Helvetica', 10)
  
  mycanvas.drawCentredString(30-x_a4, y_axis_head, "S.NO")
  mycanvas.drawCentredString(80-x_a4, y_axis_head, "Date")
  mycanvas.drawCentredString(295-160-x_a4, y_axis_head, "TM500")
  mycanvas.drawCentredString(355-160-x_a4, y_axis_head, "STD250")
  mycanvas.drawCentredString(415-160-x_a4, y_axis_head, "STD500")
  mycanvas.drawCentredString(485-160-x_a4, y_axis_head, "FCM500")
  mycanvas.drawCentredString(565-160-x_a4, y_axis_head, "FCM1000")
  mycanvas.drawCentredString(625-160-x_a4, y_axis_head, "Tea500")
  mycanvas.drawCentredString(510+60-55-x_a4, y_axis_head, "Tea1000")
  mycanvas.drawCentredString(440+190-65-x_a4, y_axis_head, "Total")

  y_axis_line = 698+20+20+20-10 + y_a4
  y_axis = 645+20+20+20-10 + y_a4
  x_axis_line = 20-x_a4
  x_axis = 30-x_a4

  mycanvas.line(x_axis_line, y_axis_line, x_axis_line + 580, y_axis_line)
  mycanvas.line(x_axis_line, y_axis_line-25, x_axis_line + 580, y_axis_line-25)

  for data in data_dict:
      if data == "final_dict" or data == "user_name":
          pass
      else:
          if data_dict[data]["grand_total"] == 0:
              pass
          else:
              mycanvas.setFont('Helvetica', 12)
              mycanvas.drawCentredString(x_axis+30, y_axis, str(data))
              mycanvas.setFont('Helvetica', 10)
              mycanvas.setDash(6,3)
              mycanvas.setLineWidth(0)
              y_axis -= 25
              sl_no = 1
              tm500 = 0
              sm250 = 0
              sm500 = 0
              fcm500 = 0
              fcm1000 = 0
              tea500 = 0
              tea1000 = 0
              total = 0
              for date_leak in data_dict[data]:
                  if date_leak == "grand_total":
                      pass
                  else:
                      
                      if y_axis <= 30 :
                          mycanvas.showPage()
                          mycanvas.setFillColor(HexColor(dark_color))
                          mycanvas.setFont('Helvetica', 12.5)
                          mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                          mycanvas.setFont('Helvetica', 13)
                        #Date
                          from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
                          to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
                          mycanvas.drawCentredString(500-150, 795, "Leakage Allowance For DATE : " + str(datetime.strftime(from_date, '%d/%m/%Y'))+" to "+str(datetime.strftime(to_date, '%d/%m/%Y')))

                          y_axis_head = 730 + y_a4
                          mycanvas.setFont('Helvetica', 10)
                          mycanvas.drawCentredString(30-x_a4, y_axis_head, "S.NO")
                          mycanvas.drawCentredString(80-x_a4, y_axis_head, "Date")
                          mycanvas.drawCentredString(295-160-x_a4, y_axis_head, "TM500")
                          mycanvas.drawCentredString(355-160-x_a4, y_axis_head, "STD250")
                          mycanvas.drawCentredString(415-160-x_a4, y_axis_head, "STD500")
                          mycanvas.drawCentredString(485-160-x_a4, y_axis_head, "FCM500")
                          mycanvas.drawCentredString(565-160-x_a4, y_axis_head, "FCM1000")
                          mycanvas.drawCentredString(625-160-x_a4, y_axis_head, "Tea500")
                          mycanvas.drawCentredString(510+60-55-x_a4, y_axis_head, "Tea1000")
                          mycanvas.drawCentredString(440+190-65-x_a4, y_axis_head, "Total")

                          y_axis_line = 698+20+20+20-10+ y_a4
                          y_axis = 645+20+20+20-10+ y_a4
                          mycanvas.setDash(6,3)
                          mycanvas.setLineWidth(0)
                      
                      
                      mycanvas.setFont('Helvetica', 10)
                      tm500 += data_dict[data][date_leak]["tm500"]
                      sm250 += data_dict[data][date_leak]["sm250"]
                      sm500 += data_dict[data][date_leak]["sm500"]
                      fcm500 += data_dict[data][date_leak]["fcm500"]
                      fcm1000 += data_dict[data][date_leak]["fcm1000"]
                      fcm500 += data_dict[data][date_leak]["tea500"]
                      fcm1000 += data_dict[data][date_leak]["tea1000"]


                      total += data_dict[data][date_leak]["total"]

                      mycanvas.drawCentredString(x_axis, y_axis, str(sl_no))
                      mycanvas.drawCentredString(x_axis+40, y_axis, str(date_leak))
                      if data_dict[data][date_leak]["tm500"] != 0:
                          mycanvas.drawRightString(x_axis+129-3, y_axis, str(data_dict[data][date_leak]["tm500"]))

                      if data_dict[data][date_leak]["sm250"] != 0:
                          mycanvas.drawRightString(x_axis+190-6, y_axis, str(data_dict[data][date_leak]["sm250"]))

                      if data_dict[data][date_leak]["sm500"] != 0:
                          mycanvas.drawRightString(x_axis+250-9, y_axis, str(data_dict[data][date_leak]["sm500"]))

                      if data_dict[data][date_leak]["fcm500"] != 0:
                          mycanvas.drawRightString(x_axis+325-12, y_axis, str(data_dict[data][date_leak]["fcm500"]))

                      if data_dict[data][date_leak]["fcm1000"] != 0:
                          mycanvas.drawRightString(x_axis+400-15, y_axis, str(data_dict[data][date_leak]["fcm1000"]))

                      if data_dict[data][date_leak]["tea500"] != 0:
                          mycanvas.drawRightString(x_axis+465-18, y_axis, str(data_dict[data][date_leak]["tea500"]))

                      if data_dict[data][date_leak]["tea1000"] != 0:
                          mycanvas.drawRightString(x_axis+525-21, y_axis, str(data_dict[data][date_leak]["tea1000"]))

                      mycanvas.drawRightString(x_axis+580-24, y_axis, str(data_dict[data][date_leak]["total"]))

                    #lines
                      mycanvas.line(x_axis_line, y_axis+30, x_axis_line, y_axis-40)
                      mycanvas.line(x_axis_line+575, y_axis+30, x_axis_line+575, y_axis-40)

                      mycanvas.line(x_axis_line+20, y_axis+15, x_axis_line+20, y_axis-40)
                      mycanvas.line(x_axis_line+80, y_axis+15, x_axis_line+80, y_axis-40)
                      mycanvas.line(x_axis_line+160, y_axis+15, x_axis_line+160, y_axis-40)
                      mycanvas.line(x_axis_line+235, y_axis+15, x_axis_line+235, y_axis-40)
                      mycanvas.line(x_axis_line+323, y_axis+15, x_axis_line+323, y_axis-40)
                      mycanvas.line(x_axis_line+410-2, y_axis+15, x_axis_line+410-2, y_axis-40)
                      mycanvas.line(x_axis_line+500-5, y_axis+15, x_axis_line+500-5, y_axis-40)
                      mycanvas.line(x_axis_line+590-2, y_axis+15, x_axis_line+590-2, y_axis-40)
                      mycanvas.line(x_axis_line+670-5, y_axis+15, x_axis_line+670-5, y_axis-40)

                      
                          

                      y_axis -= 15
                      sl_no += 1
              
              
              mycanvas.drawCentredString(x_axis+40, y_axis-20, "T O T A L")
              mycanvas.drawRightString(x_axis+129-3, y_axis-20, str(tm500))
              mycanvas.drawRightString(x_axis+190-6, y_axis-20, str(sm250))
              mycanvas.drawRightString(x_axis+250-9, y_axis-20, str(sm500))
              mycanvas.drawRightString(x_axis+325-12, y_axis-20, str(fcm500))
              mycanvas.drawRightString(x_axis+400-15, y_axis-20, str(fcm1000))
              mycanvas.drawRightString(x_axis+465-18, y_axis-20, str(tea500))
              mycanvas.drawRightString(x_axis+525-21, y_axis-20, str(tea1000))
              mycanvas.drawRightString(x_axis+580-24, y_axis-20, str(total))

                # line
              mycanvas.line(x_axis_line, y_axis-5, x_axis_line + 575, y_axis-5)
              mycanvas.line(x_axis_line, y_axis-25, x_axis_line + 575, y_axis-25)

              mycanvas.line(x_axis_line, y_axis_line, x_axis_line + 575, y_axis_line)
              mycanvas.line(x_axis_line, y_axis_line-25, x_axis_line + 575, y_axis_line-25)
              y_axis -= 45

  # for grand total
  mycanvas.drawCentredString(x_axis+40, y_axis, "G T O T A L")
  mycanvas.drawRightString(x_axis+129-3, y_axis, str(round(Decimal(data_dict["final_dict"]["tm500"]["liter"]),3)))
  mycanvas.drawRightString(x_axis+190-6, y_axis, str(round(Decimal(data_dict["final_dict"]["sm250"]["liter"]),3)))
  mycanvas.drawRightString(x_axis+250-9, y_axis, str(round(Decimal(data_dict["final_dict"]["sm500"]["liter"]),3)))
  mycanvas.drawRightString(x_axis+325-12, y_axis, str(round(Decimal(data_dict["final_dict"]["fcm500"]["liter"]),3)))
  mycanvas.drawRightString(x_axis+400-15, y_axis, str(round(Decimal(data_dict["final_dict"]["fcm1000"]["liter"]),3)))
  mycanvas.drawRightString(x_axis+465-18, y_axis, str(round(Decimal(data_dict["final_dict"]["tea500"]["liter"]),3)))
  mycanvas.drawRightString(x_axis+525-21, y_axis, str(round(Decimal(data_dict["final_dict"]["tea1000"]["liter"]),3)))
  mycanvas.drawRightString(x_axis+580-24, y_axis, str(round(Decimal(data_dict["final_dict"]["total"]["liter"]),3)))

  # line
  mycanvas.line(x_axis_line, y_axis-5+20, x_axis_line + 575, y_axis-5+20)
  mycanvas.line(x_axis_line, y_axis-25+20, x_axis_line + 575, y_axis-25+20)



  #final_report
  mycanvas.showPage()
  
  mycanvas.setDash(6,3)
  mycanvas.setLineWidth(0)

  mycanvas.setFillColor(HexColor(dark_color))
  mycanvas.setFont('Helvetica', 12.5)
  mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
  mycanvas.setFont('Helvetica', 13)
  
  y_a4 = 80
  x_a4 = 50
  #Date
  from_date = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
  to_date = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
  mycanvas.drawCentredString(300, 795, "Leakage Allowance For DATE : " + str(datetime.strftime(from_date, '%d/%m/%Y'))+" TO "+str(datetime.strftime(to_date, '%d/%m/%Y')))

  y_axis = 645+20+20+20-10 + y_a4
  mycanvas.setFont('Helvetica', 10)
  
  mycanvas.line(x_axis_line+80-x_a4, y_axis-5-20, x_axis_line + 630-40-x_a4, y_axis-5-20)
  mycanvas.line(x_axis_line+80-x_a4, y_axis-25-20, x_axis_line + 630-40-x_a4, y_axis-25-20)

  mycanvas.drawCentredString(x_axis+70+50-x_a4, y_axis-20-20, "DESCRIPTION")
  mycanvas.drawCentredString(x_axis+70+100+50-x_a4, y_axis-20-20, "QUANTITY")
  mycanvas.drawCentredString(x_axis+70+200+50-x_a4, y_axis-20-20, "RATE")
  mycanvas.drawCentredString(x_axis+70+300+50-x_a4, y_axis-20-20, "TOTAL Lit")
  mycanvas.drawCentredString(x_axis+70+400+50-x_a4, y_axis-20-20, "TOTAL VALUE")

  for data in data_dict["final_dict"]:
      mycanvas.drawCentredString(x_axis+70+50-x_a4, y_axis-20-20-25, str(data.upper()))
      mycanvas.drawRightString(x_axis+70+100+50+20+20-x_a4, y_axis-20-20-25, str(data_dict["final_dict"][data]["qty"]))
      if data != "total":
          mycanvas.drawRightString(x_axis+70+200+50+20+20-x_a4, y_axis-20-20-25, str(data_dict["final_dict"][data]["rate"]))
      mycanvas.drawRightString(x_axis+70+300+50+20+20-x_a4, y_axis-20-20-25, str(data_dict["final_dict"][data]["liter"]))
      mycanvas.drawRightString(x_axis+70+400+50+20+20+10-x_a4, y_axis-20-20-25, str(data_dict["final_dict"][data]["cost"]))

      mycanvas.line(x_axis_line+80-x_a4, y_axis-20-5, x_axis_line+80-x_a4 , y_axis-20-20-25)
      mycanvas.line(x_axis_line+80+100-x_a4, y_axis-20-5, x_axis_line+80+100-x_a4 , y_axis-20-20-25)
      mycanvas.line(x_axis_line+80+200-x_a4, y_axis-20-5, x_axis_line+80+200-x_a4 , y_axis-20-20-25)
      mycanvas.line(x_axis_line+80+300-x_a4, y_axis-20-5, x_axis_line+80+300-x_a4 , y_axis-20-20-25)
      mycanvas.line(x_axis_line+80+400-x_a4, y_axis-20-5, x_axis_line+80+400-x_a4 , y_axis-20-20-25)
      mycanvas.line(x_axis_line+80+500+10-x_a4, y_axis-20-5, x_axis_line+80+500+10-x_a4 , y_axis-20-20-25)

      y_axis -= 20

  mycanvas.line(x_axis_line+80-x_a4, y_axis-10-20, x_axis_line + 630-40-x_a4, y_axis-10-20)
  mycanvas.line(x_axis_line+80-x_a4, y_axis-30-20, x_axis_line + 630-40-x_a4, y_axis-30-20)

  # mycanvas.setFont('Times-Italic', 10)
  # mycanvas.drawRightString(585, 5, 'Report Generated by: '+str(data_dict['user_name']+", @"+str(datetime.strftime(datetime.now(timezone('Asia/Kolkata')), '%d-%m-%Y, %I:%M %p'))))
  mycanvas.save()
  document = {}
  document['file_name'] = file_name
  try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['pdf'] = encoded_image
  except Exception as err:
      print(err)
  return document




@api_view(['POST'])
def generate_monthly_institution_bill_abstract(request):
  business_codes = []
  data_dict = {}
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  product_type = request.data['product_type']
  date_list = pd.date_range(start=from_date, end=to_date)
  if request.data['option_type'] == 'by_business':
      business_codes = request.data['business_code_list']
  elif request.data['option_type'] == 'by_business_type':
      for business_type in request.data['business_type_list']:
          if business_type == 'private_institute':
              pvt_business_code_list = list(Business.objects.filter(business_type_id=4).values_list('code', flat=True))
              business_codes += pvt_business_code_list
          elif business_type == 'govt_institute':
              gvt_business_code_list = list(Business.objects.filter(business_type_id=5).values_list('code', flat=True))
              business_codes += gvt_business_code_list
          elif business_type == 'union_parlour':
              union_parlour_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=1).values_list('business__code', flat=True))
              business_codes += union_parlour_business_code_list
          elif business_type == 'union_booth':
              union_booth_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=2).values_list('business__code', flat=True))
              business_codes += union_booth_business_code_list
          elif business_type == 'nilgris':
              nilgris_booth_business_code_list = list(Business.objects.filter(zone_id=11).values_list('code', flat=True))
              business_codes += nilgris_booth_business_code_list
          elif business_type == 'tirupur':
              tirupur_booth_business_code_list = list(Business.objects.filter(zone_id=13).values_list('code', flat=True))
              business_codes += tirupur_booth_business_code_list
          elif business_type == 'society':
              society_business_code_list = list(Business.objects.filter(business_type_id=10).values_list('code', flat=True))
              business_codes += society_business_code_list
          elif business_type == 'others':
              employee_obj = Employee.objects.get(user_profile__user=request.user)
              if employee_obj.business_group is not None:
                other_business_code_list = list(Business.objects.filter(business_group_id= employee_obj.business_group.id).values_list('code', flat=True))
                business_codes += other_business_code_list

  business_codes = list(map(int, business_codes))
  business_codes.sort() 
  for business_code in business_codes:
      milk_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__in=date_list,business__code=business_code, sold_to='Agent')
      business = Business.objects.get(code=business_code)
      if RouteBusinessMap.objects.filter(business_id=business.id,route__session_id=1).exists():
          morning_route = RouteBusinessMap.objects.get(business_id=business.id,route__session_id=1).route.name
      if RouteBusinessMap.objects.filter(business_id=business.id,route__session_id=2).exists():
          evening_route = RouteBusinessMap.objects.get(business_id=business.id,route__session_id=2).route.name
      
      if milk_sale_obj:
          data_dict[business.code] = {
              "description" : business.name,
              "morning_route": morning_route,
              "evening_route": evening_route,
              "total_amount":0
          }
          if product_type == 'milk':
              product_tot = milk_sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum'] + \
                                        milk_sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"] + \
                                        milk_sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"] + \
                                        milk_sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + \
                                        milk_sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"] + \
                                        milk_sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + \
                                        milk_sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]
              data_dict[business.code]["total_amount"] = product_tot
          if product_type == 'curd':
              product_tot = milk_sale_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum'] + \
                            milk_sale_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum'] + \
                                    milk_sale_obj.aggregate(Sum('curd150_cost'))['curd150_cost__sum'] + \
                                    milk_sale_obj.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum']
              data_dict[business.code]["total_amount"] = product_tot
          if product_type == "buttermilk":
              product_tot = milk_sale_obj.aggregate(Sum('buttermilk200_cost'))['buttermilk200_cost__sum'] + milk_sale_obj.aggregate(Sum('bm_jar200_cost'))['bm_jar200_cost__sum']
              data_dict[business.code]["total_amount"] = product_tot
  data_dict["user_name"] = request.user.first_name
  data = instution_bll_abstract_pdf_gen(data_dict,date_list,product_type)
  return Response(data=data, status=status.HTTP_200_OK)


def instution_bll_abstract_pdf_gen(data_dict,date_list,product_type):
   
    indian = pytz.timezone('Asia/Kolkata')
    file_name = "instution_bill_abstract_for_the_perion_from_"+str(date_list[0])[:10] + ' to ' + str(date_list[-1])[:10]+"_"+str(product_type)+'.pdf'
    file_path = os.path.join('static/media/monthly_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize= A4)
   
    light_color = 0x9b9999
    dark_color = 0x000000
   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 11)
   
    form_date_formate = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
    to_date_formate = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')
   
    from_date = datetime.strftime(form_date_formate, '%d-%m-%Y')
    to_date = datetime.strftime(to_date_formate, '%d-%m-%Y')
   
    mycanvas.drawCentredString(300, 795,'INSTITUTION BILL ABSTRACT FOR THE PERIOD FROM  ('+str(from_date)+ "  to  "+str(to_date)+" )")
    mycanvas.drawCentredString(300, 780,"( " + str(product_type.upper()) +" )")
    mycanvas.setFont('Helvetica', 13)
   
    x_line = 35
    y_line = 690+80
   
    x_data = 50
    y_data = 640+80
   
    mycanvas.setFont('Helvetica', 9)
    mycanvas.drawCentredString(50,670+80,"S.No")
    mycanvas.drawCentredString(85,670+80,"CODE")
    mycanvas.drawCentredString(200,670+80,"DISCRIPTION")
    mycanvas.drawCentredString(350,670+80,"MORNING ROUTE")
    mycanvas.drawCentredString(440,670+80,"EVENING ROUTE")
    mycanvas.drawCentredString(520,670+80,'TOTAL AMT.')
   
    # hedder_top_line
    mycanvas.setLineWidth(0)
    mycanvas.line(x_line,y_line,x_line+520,y_line)
    mycanvas.line(x_line,y_line-30,x_line+520,y_line-30)
    sl_no = 1
    grand_total = 0
    for data in data_dict:
        if data == "user_name" or data_dict[data]["total_amount"] == 0:
            pass
        else:
            mycanvas.setFont('Helvetica', 7)
            mycanvas.drawString(x_data-10,y_data,str(sl_no))
            mycanvas.drawString(x_data+25,y_data,str(data))
            mycanvas.drawString(x_data+70,y_data,str(data_dict[data]["description"]))
            mycanvas.drawString(x_data+255,y_data,str(data_dict[data]["morning_route"])[:-4])
            mycanvas.drawString(x_data+350,y_data,str(data_dict[data]["evening_route"])[:-4])
            mycanvas.drawRightString(x_data+500,y_data,str(round(data_dict[data]["total_amount"])))
           
            grand_total += round(data_dict[data]["total_amount"])
           
            #lines
            mycanvas.line(x_line,y_line,x_line,y_data-10)
            mycanvas.line(x_line+30,y_line,x_line+30,y_data-10)
            mycanvas.line(x_line+70,y_line,x_line+70,y_data-10)
            mycanvas.line(x_line+265,y_line,x_line+265,y_data-10)
            mycanvas.line(x_line+360,y_line,x_line+360,y_data-10)
            mycanvas.line(x_line+450,y_line,x_line+450,y_data-10)
            mycanvas.line(x_line+520,y_line,x_line+520,y_data-10)
           
            if sl_no % 34 == 0:
                mycanvas.line(x_line,y_data-10,x_line+520,y_data-10)
                mycanvas.showPage()
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica', 12.5)
                mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Helvetica', 11)

                form_date_formate = datetime.strptime(str(date_list[0])[:10], '%Y-%m-%d')
                to_date_formate = datetime.strptime(str(date_list[-1])[:10], '%Y-%m-%d')

                from_date = datetime.strftime(form_date_formate, '%d-%m-%Y')
                to_date = datetime.strftime(to_date_formate, '%d-%m-%Y')

                mycanvas.drawCentredString(300, 795,'INSTITUTION BILL ABSTRACT FOR THE PERIOD FROM  ('+str(from_date)+ "  to  "+str(to_date)+" )")
                mycanvas.drawCentredString(300, 780,"( " + str(product_type.upper()) +" )")
                mycanvas.setFont('Helvetica', 13)

                x_line = 35
                y_line = 690+80

                x_data = 50
                y_data = 640+100

                mycanvas.setFont('Helvetica', 9)
                mycanvas.drawCentredString(50,670+80,"S.No")
                mycanvas.drawCentredString(85,670+80,"CODE")
                mycanvas.drawCentredString(200,670+80,"DISCRIPTION")
                mycanvas.drawCentredString(350,670+80,"MORNING ROUTE")
                mycanvas.drawCentredString(440,670+80,"EVENING ROUTE")
                mycanvas.drawCentredString(520,670+80,'TOTAL AMT.')

                # hedder_top_line
                mycanvas.setLineWidth(0)
                mycanvas.line(x_line,y_line,x_line+520,y_line)
                mycanvas.line(x_line,y_line-30,x_line+520,y_line-30)
            sl_no += 1
            y_data -= 20
    mycanvas.line(x_line,y_data+10-20,x_line+520,y_data+10-20)
    mycanvas.line(x_line,y_data+30-20,x_line+520,y_data+30-20)
   
    mycanvas.line(x_line,y_data+30-20,x_line,y_data+10-20)
    mycanvas.line(x_line+520,y_data+30-20,x_line+520,y_data+10-20)
   
    mycanvas.line(x_line+450,y_data+30-20,x_line+450,y_data+10-20)
   
    mycanvas.drawString(x_data+360,y_data+15-20,"GRAND TOTAL")
    mycanvas.drawRightString(x_data+500,y_data+15-20,str(grand_total))
   
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawString(340, 10,'Report Generated by: ' + str(data_dict["user_name"] + ", @" + str(datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))
   
    mycanvas.save()
    document = {}
    document['file_name'] = file_name
    document["is_data_available"] = True
    if sl_no == 1:
        document["is_data_available"] = False
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document



@api_view(['POST'])
def serve_bulk_customer_card_data(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    date_range = pd.date_range(start=from_date, end=to_date)
    business_code = request.data['entered_booth_code']
    report_option = request.data['selected_report_type']
    order_via_option = request.data['selected_order_type']
    zone = request.data['selected_zone_id']
    route = request.data['selected_route_id']

    if order_via_option == 'online':
        ordered_via_list = [1, 3]
    else:
        ordered_via_list = [2]
    selected_month = request.data['selected_month']
    if report_option == 'zone_wise':
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(time_created__date__in=date_range, date__month=selected_month['month_in_integer'] + 1, date__year=selected_month['year'],
                                                                     ordered_via_id__in=ordered_via_list,
                                                                     zone_id=zone).order_by("business_id")
        zone_name = Zone.objects.get(id=zone).name
    elif report_option == 'route_wise':
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(time_created__date__in=date_range,
                                                                     date__month=selected_month['month_in_integer'] + 1,
                                                                     date__year=selected_month['year'],
                                                                     ordered_via_id__in=ordered_via_list,
                                                                     route_id=route).order_by("business_id")
    else:
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(time_created__date__in=date_range, date__month=selected_month['month_in_integer'] + 1, date__year=selected_month['year'],
                                                                     ordered_via_id__in=ordered_via_list,
                                                                     business__code=business_code).order_by(
            "business_id")
    data_dict = {}
    for sale_group in icustomer_sale_group_obj:
        if not sale_group.icustomer_id in data_dict:
            if not ICustomerSerialNumberMap.objects.filter(month=sale_group.date.month, year=sale_group.date.year,
                                                           icustomer_id=sale_group.icustomer_id).exists():
                if ICustomerCardSerialNumberIdBank.objects.filter(business_id=sale_group.business.id,
                                                                  month=sale_group.date.month,
                                                                  year=sale_group.date.year).exists():
                    icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank.objects.get(
                        business_id=sale_group.business.id, month=sale_group.date.month, year=sale_group.date.year)
                else:
                    icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank(business_id=sale_group.business.id,
                                                                                   month=sale_group.date.month,
                                                                                   year=sale_group.date.year,
                                                                                   counter_last_count=0,
                                                                                   online_last_count=0)
                    icustomer_serial_bank_id_obj.save()
                icustomer_serial_number_map = ICustomerSerialNumberMap(icustomer_id=sale_group.icustomer_id,
                                                                       business_id=sale_group.business.id,
                                                                       month=sale_group.date.month,
                                                                       year=sale_group.date.year)
                serial_number = icustomer_serial_bank_id_obj.counter_last_count + 1
                icustomer_serial_number_map.serial_number = serial_number
                icustomer_serial_number_map.save()
                # update serail number in ID bank
                icustomer_serial_bank_id_obj.counter_last_count = serial_number
                icustomer_serial_bank_id_obj.online_last_count = serial_number
                icustomer_serial_bank_id_obj.save()
            if sale_group.ordered_via_id == 2:
                serial_number_format = 'Z - '
            else:
                serial_number_format = 'O - '
            data_dict[sale_group.icustomer_id] = {
                "card_no": ICustomerMonthlyOrderTransaction.objects.get(icustomer_id=sale_group.icustomer_id,
                                                                        month=sale_group.date.month,
                                                                        year=sale_group.date.year).milk_card_number,
                "booth": sale_group.business.code,
                "zone": sale_group.zone.name,
                "zoner_mobile": EmployeeZoneResponsibility.objects.get(
                    zone_id=sale_group.zone_id).employee.user_profile.mobile,
                "customer_name": sale_group.icustomer.user_profile.user.first_name + ' ' +str(sale_group.icustomer.user_profile.user.last_name),
                "customer_id": sale_group.icustomer.customer_code,
                "month": sale_group.date.month,
                "year": sale_group.date.year,
                "sl_no": ICustomerSerialNumberMap.objects.get(month=sale_group.date.month, year=sale_group.date.year,
                                                              icustomer_id=sale_group.icustomer_id).serial_number,
                "serial_number_format": serial_number_format,
                "amount": 0,
                "morning": {},
                "evening": {},
                'time_created': sale_group.time_created,
                'order_placed_by': sale_group.ordered_by.first_name + ' ' +str(sale_group.ordered_by.last_name)
            }
        if sale_group.session_id == 1:
            icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group_id=sale_group.id)
            for sale in icustomer_sale_obj:
                if not sale.product.short_name in data_dict[sale_group.icustomer_id]["morning"]:
                    data_dict[sale_group.icustomer_id]["morning"][sale.product.short_name] = 0
                data_dict[sale_group.icustomer_id]["morning"][sale.product.short_name] += sale.count
                data_dict[sale_group.icustomer_id]["amount"] += sale.cost_for_month
        if sale_group.session_id == 2:
            icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group_id=sale_group.id)
            for sale in icustomer_sale_obj:
                if not sale.product.short_name in data_dict[sale_group.icustomer_id]["evening"]:
                    data_dict[sale_group.icustomer_id]["evening"][sale.product.short_name] = 0
                data_dict[sale_group.icustomer_id]["evening"][sale.product.short_name] += sale.count
                data_dict[sale_group.icustomer_id]["amount"] += sale.cost_for_month
    final_data_dict = {
        'data_dict': data_dict,
        'customer_ids': data_dict.keys()
    }
    final_data_dict['document_data'] = generate_bulk_pdf_for_card_customer(data_dict,order_via_option,date_range)
    return Response(data=final_data_dict, status=status.HTTP_200_OK)


def generate_bulk_pdf_for_card_customer(data_dict,order_via_option,date_range):
    file_name = str(order_via_option) + '_customser_card_full_for_( '  + "-" + str(date_range[0])[
                                                                                            :10] + "_to_" + str(
        date_range[-1])[:10] + ' ).pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)  # (20*inch,20*inch)
    mycanvas.setLineWidth(0)
    for data in data_dict:
        month = data_dict[data]["month"]
        year = data_dict[data]["year"]
        days = monthrange(year, month)
        datetime_object = datetime.strptime(str(month), "%m")
        month_name = datetime_object.strftime("%b")

        y = 790

        list1 = ["Validity", "Booth", "Customer Code", "Date"]
        list2 = ["Card No", "Sl No", "Name", "Amount"]

        mycanvas.setFont("Times-Roman", 10)
        for i in range(4):
            # harizonal line
            mycanvas.line(260, y + 12, 396, y + 12)  # 585
            mycanvas.line(400, y + 12, 545, y + 12)

            mycanvas.line(260, y - 4, 396, y - 4)
            mycanvas.line(400, y - 4, 545, y - 4)

            mycanvas.line(260, y + 12, 260, y - 4)
            mycanvas.line(332, y + 12, 332, y - 4)
            mycanvas.line(396, y + 12, 396, y - 4)
            mycanvas.line(400, y + 12, 400, y - 4)
            mycanvas.line(442, y + 12, 442, y - 4)
            mycanvas.line(545, y + 12, 545, y - 4)

            mycanvas.drawString(265, y, str(list1[i]))
            mycanvas.drawString(405, y, str(list2[i]))
            y -= 20
        #         mycanvas.line(300,y+12,585,y+12)

        y = 790
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawString(335, y, str(month_name) + " - " + str(year))
        mycanvas.drawString(165, y - 13, str(data_dict[data]['zone']))
        mycanvas.drawString(335, y - 20, str(data_dict[data]['booth']))
        mycanvas.drawString(335, y - 40, str(data_dict[data]["customer_id"]))
        mycanvas.drawString(335, y - 60, str(data_dict[data]['time_created'].astimezone(timezone('Asia/Kolkata')).strftime("%d-%m-%Y")))

        mycanvas.drawString(445, y, str(data_dict[data]['card_no']))
        mycanvas.drawString(445, y - 20, str(data_dict[data]["serial_number_format"]) + str(data_dict[data]["sl_no"]))
        mycanvas.drawString(445, y - 40, str(data_dict[data]["customer_name"])[:17])
        mycanvas.drawString(445, y - 60, str(data_dict[data]["amount"]))

        mycanvas.setFont('Helvetica', 10)
        mycanvas.drawString(390, y - 80, "Zonal Officer Mobile : " + str(data_dict[data]["zoner_mobile"]))

        mycanvas.setFont("Times-Roman", 10)
        y2 = 690
        # for product table
        for i in range(3):
            if i == 0:
                mycanvas.drawString(338, y2 - 5, "Milk Type")
                mycanvas.drawString(338, y2 - 32, "Morning")
                mycanvas.drawString(338, y2 - 53, "Evening")
                mycanvas.line(330, y2 + 5, 545, y2 + 5)
            else:
                mycanvas.line(330, y2, 545, y2)
            mycanvas.line(330, y2 + 5, 330, y2 - 20)
            mycanvas.line(390 - 5, y2 + 5, 390 - 5, y2 - 20)
            mycanvas.line(430 - 5, y2 + 5, 430 - 5, y2 - 20)
            mycanvas.line(470 - 5, y2 + 5, 470 - 5, y2 - 20)
            mycanvas.line(510 - 5, y2 + 5, 510 - 5, y2 - 20)
            mycanvas.line(545, y2 + 5, 545, y2 - 20)
            y2 -= 20
        mycanvas.line(330, y2, 545, y2)

        x = 400
        y2 = 690
        # ---------------------------
        product_list = []

        for products in data_dict[data]["morning"]:
            product_list.append(products)
        for products in data_dict[data]["evening"]:
            product_list.append(products)

        product_list = set(product_list)
        product_list = list(product_list)

        for product in product_list:
            mycanvas.setFont("Times-Roman", 10)
            mycanvas.drawString(x - 13, y2 - 5, str(product))
            mycanvas.drawString(x - 3, y2 - 15, "ml")

            mycanvas.setFont('Helvetica-Bold', 10)
            if product in data_dict[data]["morning"]:
                mycanvas.drawRightString(x + 2, y2 - 32, str(int(data_dict[data]["morning"][product])))
            else:
                mycanvas.drawRightString(x + 2, y2 - 32, '-')

            if product in data_dict[data]["evening"]:
                mycanvas.drawRightString(x + 2, y2 - 53, str(int(data_dict[data]["evening"][product])))
            else:
                mycanvas.drawRightString(x + 2, y2 - 53, '-')
            x += 40
        mycanvas.drawString(280, y2 - 51, "Manager")
        mycanvas.drawString(270, y2 - 61, "(Marketing)")

        img_file = os.path.join('static/media/', "agm_sign4.png")
        mycanvas.drawInlineImage(img_file, 275, y2 - 41, (.5 * inch), (.320 * inch))

        mycanvas.showPage()
    mycanvas.save()
    document = {}
    document['file_name'] = file_name
    if len(data_dict.keys()) != 0:
        document['data_available'] = True
    else:
        document['data_available'] = False
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document



@api_view(['POST'])
def serve_customer_order_statement_selected_booth(request):
    data_dict = {}
    year = request.data['year']
    month = request.data['month']
    booth_code = request.data['booth_code']
    icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(date__year=year, date__month=month,
                                                                 business__code=booth_code)
    for sale_group in icustomer_sale_group_obj:
        if not sale_group.icustomer_id in data_dict:
            serial_number = ICustomerSerialNumberMap.objects.get(month=month, year=year,
                                                                 icustomer_id=sale_group.icustomer_id).serial_number
            if sale_group.ordered_via_id == 2:
                serial_number_format = 'Z - '
            else:
                serial_number_format = 'O - '
            data_dict[sale_group.icustomer_id] = {
                "card_no" : ICustomerMonthlyOrderTransaction.objects.get(icustomer_id=sale_group.icustomer_id, month=month, year=year).milk_card_number,
                "sl_no": serial_number,
                'order_via_type': serial_number_format,
                "customer_name": sale_group.icustomer.user_profile.user.first_name + " " + sale_group.icustomer.user_profile.user.last_name,
                "customer_id": sale_group.icustomer.customer_code,
                "TM 500": 0,
                "STD 500": 0,
                "STD 250": 0,
                "FCM 500": 0,
                "Tea 500": 0,
                "TM 500 EVE": 0,
                "STD 500 EVE": 0,
                "STD 250 EVE": 0,
                "FCM 500 EVE": 0,
                "Tea 500 EVE": 0,
            }
        for sale in ICustomerSale.objects.filter(icustomer_sale_group_id=sale_group.id,
                                                 icustomer_sale_group__session_id=1):
            if not sale.product.short_name in data_dict[sale_group.icustomer_id]:
                data_dict[sale_group.icustomer_id][sale.product.short_name] = 0
            data_dict[sale_group.icustomer_id][sale.product.short_name] += sale.count

        for sale in ICustomerSale.objects.filter(icustomer_sale_group_id=sale_group.id,
                                                 icustomer_sale_group__session_id=2):
            if not sale.product.short_name + " EVE" in data_dict[sale_group.icustomer_id]:
                data_dict[sale_group.icustomer_id][sale.product.short_name + " EVE"] = 0
            data_dict[sale_group.icustomer_id][sale.product.short_name + " EVE"] += sale.count

    # data_dict["user_name"] = request.user.first_name
    # user_name = request.user.first_name
    data = generate_customer_order_statement_for_selected_booth(data_dict, month, year, booth_code)
    return Response(data=data, status=status.HTTP_200_OK)


def generate_customer_order_statement_for_selected_booth(data_dict,month,year,booth_code):
    month = month
    year = year
    days = monthrange(year, month)
    datetime_object = datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%B")

    file_name = "boothwise_customer_card_details_for ( " + str(month_name) + "-" + str(year) + " )" + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setLineWidth(0)

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawString(30, 795, 'Boothwise Customer Card Details')
    mycanvas.drawCentredString(300, 795, str(month_name) + "-" + str(year))
    mycanvas.drawRightString(565, 795, "Booth No : " + str(booth_code))

    # heading
    mycanvas.setFont('Helvetica', 8)
    head_y = 745
    head_x = 15

    mycanvas.drawString(head_x, head_y, "Sl")
    mycanvas.drawString(head_x, head_y - 15, "No")
    mycanvas.drawString(head_x + 27, head_y, "Card")
    mycanvas.drawString(head_x + 33, head_y - 15, "NO")

    mycanvas.drawString(head_x + 75, head_y, "Card")
    mycanvas.drawString(head_x + 75, head_y - 15, "Sl No")

    mycanvas.drawString(head_x + 130, head_y, "Name")
    mycanvas.drawString(head_x + 210, head_y, "Customer Id")

    # morning
    mycanvas.drawString(head_x + 354, head_y + 23, "MORNING")

    mycanvas.drawString(head_x + 275, head_y, "TM")
    mycanvas.drawString(head_x + 277, head_y - 15, "500")

    mycanvas.drawString(head_x + 300, head_y, "STD")
    mycanvas.drawString(head_x + 307, head_y - 15, "500")

    mycanvas.drawString(head_x + 335, head_y, "STD")
    mycanvas.drawString(head_x + 338, head_y - 15, "250")

    mycanvas.drawString(head_x + 365, head_y, "FCM")
    mycanvas.drawString(head_x + 367, head_y - 15, "500")

    mycanvas.drawString(head_x + 395, head_y, "Tea")
    mycanvas.drawString(head_x + 397, head_y - 15, "500")

    # evening
    mycanvas.drawString(head_x + 422, head_y, "TM")
    mycanvas.drawString(head_x + 423, head_y - 15, "500")

    mycanvas.drawString(head_x + 451, head_y, "STD")
    mycanvas.drawString(head_x + 452, head_y - 15, "500")

    mycanvas.drawString(head_x + 480, head_y, "STD")
    mycanvas.drawString(head_x + 482, head_y - 15, "250")

    mycanvas.drawString(head_x + 512, head_y, "FCM")
    mycanvas.drawString(head_x + 514, head_y - 15, "500")

    mycanvas.drawString(head_x + 541, head_y, "Tea")
    mycanvas.drawString(head_x + 546, head_y - 15, "500")

    mycanvas.drawString(head_x + 485, head_y + 23, "EVENING")

    # heading_top & Bottom Line

    mycanvas.line(head_x - 5, head_y + 15, head_x + 570, head_y + 15)
    mycanvas.line(head_x - 5, head_y - 22, head_x + 570, head_y - 22)

    mycanvas.line(head_x + 270, head_y + 35, head_x + 670, head_y + 35)
    mycanvas.line(head_x + 270, head_y + 35, head_x + 270, head_y)
    mycanvas.line(head_x + 413, head_y + 35, head_x + 413, head_y)
    mycanvas.line(head_x + 570, head_y + 35, head_x + 570, head_y)

    # table_content
    x_axis = 15
    y_axis = 705
    sl_no = 1
    tm500 = 0
    std500 = 0
    std250 = 0
    fcm500 = 0
    tea500 = 0

    tm500_eve = 0
    std500_eve = 0
    std250_eve = 0
    fcm500_eve = 0
    tea500_eve = 0

    sorted_list = sorted(data_dict, key=lambda x: data_dict[x]['sl_no'])
    print(sorted_list)
    for data in sorted_list:
        if data != "user_name":
            mycanvas.setFont('Helvetica', 8)
            mycanvas.drawRightString(x_axis + 15, y_axis, str(sl_no))
            mycanvas.drawString(x_axis + 28, y_axis, str(data_dict[data]["card_no"]))
            mycanvas.drawRightString(x_axis + 95, y_axis,
                                     str(data_dict[data]["order_via_type"]) + str(data_dict[data]["sl_no"]))

            mycanvas.drawString(x_axis + 115, y_axis, str(data_dict[data]["customer_name"])[:21].upper())
            mycanvas.drawString(x_axis + 210, y_axis, str(data_dict[data]["customer_id"]))

            if data_dict[data]["TM 500"] != 0:
                mycanvas.drawRightString(x_axis + 285, y_axis, str(int(data_dict[data]["TM 500"])))
                tm500 += int(data_dict[data]["TM 500"])
            if data_dict[data]["STD 500"] != 0:
                mycanvas.drawRightString(x_axis + 310, y_axis, str(int(data_dict[data]["STD 500"])))
                std500 += int(data_dict[data]["STD 500"])
            if data_dict[data]["STD 250"] != 0:
                mycanvas.drawRightString(x_axis + 345, y_axis, str(int(data_dict[data]["STD 250"])))
                std250 += int(data_dict[data]["STD 250"])
            if data_dict[data]["FCM 500"] != 0:
                mycanvas.drawRightString(x_axis + 380, y_axis, str(int(data_dict[data]["FCM 500"])))
                fcm500 += int(data_dict[data]["FCM 500"])
            if data_dict[data]["Tea 500"] != 0:
                mycanvas.drawRightString(x_axis + 410, y_axis, str(int(data_dict[data]["Tea 500"])))
                tea500 += int(data_dict[data]["Tea 500"])
    

            if data_dict[data]["TM 500 EVE"] != 0:
                mycanvas.drawRightString(x_axis + 460, y_axis, str(int(data_dict[data]["TM 500 EVE"])))
                tm500_eve += int(data_dict[data]["TM 500 EVE"])
            if data_dict[data]["STD 500 EVE"] != 0:
                mycanvas.drawRightString(x_axis + 500, y_axis, str(int(data_dict[data]["STD 500 EVE"])))
                std500_eve += int(data_dict[data]["STD 500 EVE"])
            if data_dict[data]["STD 250 EVE"] != 0:
                mycanvas.drawRightString(x_axis + 540, y_axis, str(int(data_dict[data]["STD 250 EVE"])))
                std250_eve += int(data_dict[data]["STD 250 EVE"])
            if data_dict[data]["FCM 500 EVE"] != 0:
                mycanvas.drawRightString(x_axis + 580, y_axis, str(int(data_dict[data]["FCM 500 EVE"])))
                fcm500_eve += int(data_dict[data]["FCM 500 EVE"])
            if data_dict[data]["Tea 500 EVE"] != 0:
                mycanvas.drawRightString(x_axis + 610, y_axis, str(int(data_dict[data]["Tea 500 EVE"])))
                tea500_eve += int(data_dict[data]["Tea 500 EVE"])    

            # lines
            mycanvas.line(x_axis - 5, y_axis + 55, x_axis - 5, y_axis - 15)
            mycanvas.line(x_axis + 20, y_axis + 55, x_axis + 20, y_axis - 15)
            mycanvas.line(x_axis + 70, y_axis + 55, x_axis + 70, y_axis - 15)
            mycanvas.line(x_axis + 110, y_axis + 55, x_axis + 110, y_axis - 15)
            mycanvas.line(x_axis + 205, y_axis + 55, x_axis + 205, y_axis - 15)
            mycanvas.line(x_axis + 270, y_axis + 55, x_axis + 270, y_axis - 15)

            mycanvas.line(x_axis + 300, y_axis + 55, x_axis + 300, y_axis - 15)
            mycanvas.line(x_axis + 325, y_axis + 55, x_axis + 325, y_axis - 15)
            mycanvas.line(x_axis + 355, y_axis + 55, x_axis + 355, y_axis - 15)
            mycanvas.line(x_axis + 385, y_axis + 55, x_axis + 385, y_axis - 15)

            mycanvas.line(x_axis + 413, y_axis + 55, x_axis + 413, y_axis - 15)
            mycanvas.line(x_axis + 440, y_axis + 55, x_axis + 440, y_axis - 15)
            mycanvas.line(x_axis + 470, y_axis + 55, x_axis + 470, y_axis - 15)
            mycanvas.line(x_axis + 500, y_axis + 55, x_axis + 500, y_axis - 15)
            mycanvas.line(x_axis + 530, y_axis + 55, x_axis + 530, y_axis - 15)
            mycanvas.line(x_axis + 570, y_axis + 55, x_axis + 570, y_axis - 15)


            if sl_no % 32 == 0:
                mycanvas.line(head_x - 5, y_axis - 15, head_x + 535, y_axis - 15)
                mycanvas.showPage()
                mycanvas.setFont('Helvetica', 12.5)
                mycanvas.drawCentredString(300, 820,
                                           'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Helvetica', 11)
                mycanvas.drawString(30, 795, 'Boothwise Customer Card Details')
                mycanvas.drawCentredString(300, 795, str(month_name) + "-" + str(year))
                mycanvas.drawRightString(565, 795, "Booth No : " + str(booth_code))

                # heading
                mycanvas.setFont('Helvetica', 10)
                head_y = 745
                head_x = 15

                mycanvas.drawString(head_x, head_y, "Sl")
                mycanvas.drawString(head_x, head_y - 15, "No")
                mycanvas.drawString(head_x + 30, head_y, "Card")
                mycanvas.drawString(head_x + 35, head_y - 15, "NO")

                mycanvas.drawString(head_x + 80, head_y, "Card")
                mycanvas.drawString(head_x + 80, head_y - 15, "Sl No")

                mycanvas.drawString(head_x + 170, head_y, "Name")
                mycanvas.drawString(head_x + 265, head_y, "Customer Id")

                # morning
                mycanvas.drawString(head_x + 364, head_y + 23, "MORNING")

                mycanvas.drawString(head_x + 335, head_y, "TM")
                mycanvas.drawString(head_x + 334, head_y - 15, "500")

                mycanvas.drawString(head_x + 365, head_y, "STD")
                mycanvas.drawString(head_x + 367, head_y - 15, "500")

                mycanvas.drawString(head_x + 395, head_y, "STD")
                mycanvas.drawString(head_x + 397, head_y - 15, "250")

                mycanvas.drawString(head_x + 425, head_y, "FCM")
                mycanvas.drawString(head_x + 428, head_y - 15, "500")

                # evening
                mycanvas.drawString(head_x + 458, head_y, "TM")
                mycanvas.drawString(head_x + 457, head_y - 15, "500")

                mycanvas.drawString(head_x + 486, head_y, "STD")
                mycanvas.drawString(head_x + 487, head_y - 15, "500")

                mycanvas.drawString(head_x + 516, head_y, "STD")
                mycanvas.drawString(head_x + 517, head_y - 15, "250")

                mycanvas.drawString(head_x + 545, head_y, "FCM")
                mycanvas.drawString(head_x + 547, head_y - 15, "500")

                mycanvas.drawString(head_x + 485, head_y + 23, "EVENING")

                # heading_top & Bottom Line

                mycanvas.line(head_x - 5, head_y + 15, head_x + 570, head_y + 15)
                mycanvas.line(head_x - 5, head_y - 22, head_x + 570, head_y - 22)

                mycanvas.line(head_x + 330, head_y + 35, head_x + 570, head_y + 35)
                mycanvas.line(head_x + 330, head_y + 35, head_x + 330, head_y)
                mycanvas.line(head_x + 450, head_y + 35, head_x + 450, head_y)
                mycanvas.line(head_x + 570, head_y + 35, head_x + 570, head_y)

                # table_content
                x_axis = 15
                y_axis = 705

        y_axis -= 20
        sl_no += 1
    y_axis -= 20
    mycanvas.line(head_x - 5, y_axis + 25, head_x + 570, y_axis + 25)
    mycanvas.line(head_x + 270, y_axis + 5, head_x + 570, y_axis + 5)

    mycanvas.line(x_axis + 300, y_axis + 25, x_axis + 300, y_axis + 5)

    mycanvas.line(x_axis + 270, y_axis + 25, x_axis + 270, y_axis + 5)
    mycanvas.line(x_axis + 325, y_axis + 25, x_axis + 325, y_axis + 5)
    mycanvas.line(x_axis + 355, y_axis + 25, x_axis + 355, y_axis + 5)
    mycanvas.line(x_axis + 385, y_axis + 25, x_axis + 385, y_axis + 5)
    mycanvas.line(x_axis + 413, y_axis + 25, x_axis + 413, y_axis + 5)

    mycanvas.line(x_axis + 440, y_axis + 25, x_axis + 440, y_axis + 5)
    mycanvas.line(x_axis + 470, y_axis + 25, x_axis + 470, y_axis + 5)
    mycanvas.line(x_axis + 500, y_axis + 25, x_axis + 500, y_axis + 5)
    mycanvas.line(x_axis + 530, y_axis + 25, x_axis + 530, y_axis + 5)
    mycanvas.line(x_axis + 570, y_axis + 25, x_axis + 570, y_axis + 5)
    mycanvas.line(x_axis + 600, y_axis + 25, x_axis + 600, y_axis + 5)

    mycanvas.drawRightString(x_axis + 225, y_axis + 8, "G R A N D   T O T A L")

    mycanvas.drawRightString(x_axis + 275, y_axis + 8, str(tm500))
    mycanvas.drawRightString(x_axis + 305, y_axis + 8, str(std500))
    mycanvas.drawRightString(x_axis + 335, y_axis + 8, str(std250))
    mycanvas.drawRightString(x_axis + 365, y_axis + 8, str(fcm500))
    mycanvas.drawRightString(x_axis + 395, y_axis + 8, str(tea500))

    mycanvas.drawRightString(x_axis + 425, y_axis + 8, str(tm500_eve))
    mycanvas.drawRightString(x_axis + 465, y_axis + 8, str(std500_eve))
    mycanvas.drawRightString(x_axis + 495, y_axis + 8, str(std250_eve))
    mycanvas.drawRightString(x_axis + 525, y_axis + 8, str(fcm500_eve))
    mycanvas.drawRightString(x_axis + 565, y_axis + 8, str(tea500_eve))

    # mycanvas.showPage()
    mycanvas.setFont('Times-Italic', 10)
    indian = pytz.timezone('Asia/Kolkata')
    # mycanvas.drawRightString(580, 10, 'Report Generated by: ' + str(
    #     data_dict["user_name"] + ", @" + str(datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

    mycanvas.save()
    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document


@api_view(['POST'])
def server_bulk_customer_booth_statement(request):
    business_code = request.data['entered_booth_code']
    report_option = request.data['selected_report_type']
    zone = request.data['selected_zone_id']
    route = request.data['selected_route_id']

    selected_month = request.data['selected_month']
    if report_option == 'zone_wise':
        # name = "Zone name:"
        # zone_name = Zone.objects.get(id=zone).name
        booth_codes = list(Business.objects.filter(zone_id=zone).values_list('code', flat=True))
    elif report_option == 'route_wise':
        booth_codes = list(RouteBusinessMap.objects.filter(route_id=route).values_list('business__code', flat=True))
    else:
        booth_codes = [business_code]
    icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(date__month=selected_month['month_in_integer'] + 1,
                                                                 date__year=selected_month['year']).order_by("business_id")
    data_dict = {}
    for booth_code in booth_codes:
        if icustomer_sale_group_obj.filter(business__code=booth_code).exists():
            if not booth_code in data_dict:
                data_dict[booth_code] = {}
            icustomer_sale_group_booth_obj = icustomer_sale_group_obj.filter(business__code=booth_code)
            for sale_group in icustomer_sale_group_booth_obj:
                if not ICustomerSerialNumberMap.objects.filter(month=sale_group.date.month, year=sale_group.date.year,
                                                               icustomer_id=sale_group.icustomer_id).exists():
                    if ICustomerCardSerialNumberIdBank.objects.filter(business_id=sale_group.business.id,
                                                                      month=sale_group.date.month,
                                                                      year=sale_group.date.year).exists():
                        icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank.objects.get(
                            business_id=sale_group.business.id, month=sale_group.date.month, year=sale_group.date.year)
                    else:
                        icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank(
                            business_id=sale_group.business.id,
                            month=sale_group.date.month,
                            year=sale_group.date.year,
                            counter_last_count=0,
                            online_last_count=0)
                        icustomer_serial_bank_id_obj.save()
                    icustomer_serial_number_map = ICustomerSerialNumberMap(icustomer_id=sale_group.icustomer_id,
                                                                           business_id=sale_group.business.id,
                                                                           month=sale_group.date.month,
                                                                           year=sale_group.date.year)
                    serial_number = icustomer_serial_bank_id_obj.counter_last_count + 1
                    icustomer_serial_number_map.serial_number = serial_number
                    icustomer_serial_number_map.save()
                    # update serail number in ID bank
                    icustomer_serial_bank_id_obj.counter_last_count = serial_number
                    icustomer_serial_bank_id_obj.online_last_count = serial_number
                    icustomer_serial_bank_id_obj.save()
                if not sale_group.icustomer_id in data_dict[booth_code]:
                    if sale_group.ordered_via_id == 2:
                        serial_number_format = 'Z - '
                    else:
                        serial_number_format = 'O - '

                    data_dict[booth_code][sale_group.icustomer_id] = {
                        "card_no": ICustomerMonthlyOrderTransaction.objects.get(
                            month=selected_month['month_in_integer'] + 1, year=selected_month['year'],
                            icustomer_id=sale_group.icustomer_id).milk_card_number,
                        "sl_no": ICustomerSerialNumberMap.objects.get(month=selected_month['month_in_integer'] + 1,
                                                                      year=selected_month['year'],
                                                                      icustomer_id=sale_group.icustomer_id).serial_number,
                        'order_via_type': serial_number_format,
                        "customer_name": sale_group.icustomer.user_profile.user.first_name + " " + sale_group.icustomer.user_profile.user.last_name,
                        "customer_id": sale_group.icustomer.customer_code,
                        "TM 500": 0,
                        "STD 500": 0,
                        "STD 250": 0,
                        "FCM 500": 0,
                        "Tea 500" : 0,
                        "TM 500 EVE": 0,
                        "STD 500 EVE": 0,
                        "STD 250 EVE": 0,
                        "FCM 500 EVE": 0,
                        "Tea 500 EVE": 0,
                    }
                for sale in ICustomerSale.objects.filter(icustomer_sale_group_id=sale_group.id,
                                                         icustomer_sale_group__session_id=1):
                    if not sale.product.short_name in data_dict[booth_code][sale_group.icustomer_id]:
                        data_dict[booth_code][sale_group.icustomer_id][sale.product.short_name] = 0
                    data_dict[booth_code][sale_group.icustomer_id][sale.product.short_name] += sale.count

                for sale in ICustomerSale.objects.filter(icustomer_sale_group_id=sale_group.id,
                                                         icustomer_sale_group__session_id=2):
                    if not sale.product.short_name + " EVE" in data_dict[booth_code][sale_group.icustomer_id]:
                        data_dict[booth_code][sale_group.icustomer_id][sale.product.short_name + " EVE"] = 0
                    data_dict[booth_code][sale_group.icustomer_id][sale.product.short_name + " EVE"] += sale.count

    # data_dict["user_name"] = request.user.first_name
    month = selected_month['month_in_integer'] + 1
    year = selected_month['year']
    final_data_dict = {
        'data_dict': data_dict,
    }
    final_data_dict['document_data'] = generate_customer_order_statement_for_bulk_booth(data_dict, month, year)
    data_available = True
    data_list = []
    if len(data_dict.keys()) == 0:
        data_available = False
    else:
        for data in data_dict.keys():
            temp_dict = {
                'booth_code': data,
                'agent_name': BusinessAgentMap.objects.get(business__code=data).agent.first_name,
                'customer_count': len(data_dict[data].keys()),
                'month': month,
                'year': year,
                'loader': False
            }
            data_list.append(temp_dict)
    final_data_dict['data_list'] = data_list
    final_data_dict['document_data']['data_available'] = data_available
    return Response(data=final_data_dict, status=status.HTTP_200_OK)


def generate_customer_order_statement_for_bulk_booth(data_dict, month, year):
    month = month
    year = year
    days = monthrange(year, month)
    datetime_object = datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%B")

    file_name = "boothwise_customer_card_details for ( " + str(month_name) + "-" + str(year) + " )" + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setLineWidth(0)
    for data in data_dict:
        if data != "user_name":
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820,
                                       'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 11)
            mycanvas.drawString(30, 795, 'Boothwise Customer Card Details')
            mycanvas.drawCentredString(300, 795, str(month_name) + "-" + str(year))
            mycanvas.drawRightString(500, 795, "Booth No : " + str(data))
            # mycanvas.drawString(30, 765, name + str(zone_name))
            # heading
            mycanvas.setFont('Helvetica', 8)
            head_y = 745
            head_x = 15

            mycanvas.drawString(head_x, head_y, "Sl")
            mycanvas.drawString(head_x, head_y - 15, "No")
            mycanvas.drawString(head_x + 27, head_y, "Card")
            mycanvas.drawString(head_x + 33, head_y - 15, "NO")

            mycanvas.drawString(head_x + 75, head_y, "Card")
            mycanvas.drawString(head_x + 75, head_y - 15, "Sl No")

            mycanvas.drawString(head_x + 130, head_y, "Name")
            mycanvas.drawString(head_x + 210, head_y, "Customer Id")

            # morning
            mycanvas.drawString(head_x + 354, head_y + 23, "MORNING")

            mycanvas.drawString(head_x + 275, head_y, "TM")
            mycanvas.drawString(head_x + 277, head_y - 15, "500")

            mycanvas.drawString(head_x + 300, head_y, "STD")
            mycanvas.drawString(head_x + 307, head_y - 15, "500")

            mycanvas.drawString(head_x + 335, head_y, "STD")
            mycanvas.drawString(head_x + 338, head_y - 15, "250")

            mycanvas.drawString(head_x + 365, head_y, "FCM")
            mycanvas.drawString(head_x + 367, head_y - 15, "500")

            mycanvas.drawString(head_x + 395, head_y, "Tea")
            mycanvas.drawString(head_x + 397, head_y - 15, "500")

            # evening
            mycanvas.drawString(head_x + 422, head_y, "TM")
            mycanvas.drawString(head_x + 423, head_y - 15, "500")

            mycanvas.drawString(head_x + 451, head_y, "STD")
            mycanvas.drawString(head_x + 452, head_y - 15, "500")

            mycanvas.drawString(head_x + 480, head_y, "STD")
            mycanvas.drawString(head_x + 482, head_y - 15, "250")

            mycanvas.drawString(head_x + 512, head_y, "FCM")
            mycanvas.drawString(head_x + 514, head_y - 15, "500")

            mycanvas.drawString(head_x + 541, head_y, "Tea")
            mycanvas.drawString(head_x + 546, head_y - 15, "500")

            mycanvas.drawString(head_x + 485, head_y + 23, "EVENING")

            # heading_top & Bottom Line

            mycanvas.line(head_x - 5, head_y + 15, head_x + 570, head_y + 15)
            mycanvas.line(head_x - 5, head_y - 22, head_x + 570, head_y - 22)

            mycanvas.line(head_x + 270, head_y + 35, head_x + 670, head_y + 35)
            mycanvas.line(head_x + 270, head_y + 35, head_x + 270, head_y)
            mycanvas.line(head_x + 413, head_y + 35, head_x + 413, head_y)
            mycanvas.line(head_x + 570, head_y + 35, head_x + 570, head_y)

            # table_content
            x_axis = 15
            y_axis = 705
            sl_no = 1
            tm500 = 0
            std500 = 0
            std250 = 0
            fcm500 = 0
            tea500 = 0

            tm500_eve = 0
            std500_eve = 0
            std250_eve = 0
            fcm500_eve = 0
            tea500_eve = 0

            sorted_list = sorted(data_dict[data], key=lambda x: data_dict[data][x]['sl_no'])

            for datas in sorted_list:
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawRightString(x_axis + 15, y_axis, str(sl_no))
                mycanvas.drawString(x_axis + 28, y_axis, str(data_dict[data][datas]["card_no"]))
                mycanvas.drawRightString(x_axis + 95, y_axis, str(data_dict[data][datas]["order_via_type"]) + str(
                    data_dict[data][datas]["sl_no"]))

                mycanvas.drawString(x_axis + 115, y_axis, str(data_dict[data][datas]["customer_name"])[:21].upper())
                mycanvas.drawString(x_axis + 210, y_axis, str(data_dict[data][datas]["customer_id"]))

                if data_dict[data][datas]["TM 500"] != 0:
                    mycanvas.drawRightString(x_axis + 285, y_axis, str(int(data_dict[data][datas]["TM 500"])))
                    tm500 += int(data_dict[data][datas]["TM 500"])

                if data_dict[data][datas]["STD 500"] != 0:
                    mycanvas.drawRightString(x_axis + 310, y_axis, str(int(data_dict[data][datas]["STD 500"])))
                    std500 += int(data_dict[data][datas]["STD 500"])

                if data_dict[data][datas]["STD 250"] != 0:
                    mycanvas.drawRightString(x_axis + 345, y_axis, str(int(data_dict[data][datas]["STD 250"])))
                    std250 += int(data_dict[data][datas]["STD 250"])

                if data_dict[data][datas]["FCM 500"] != 0:
                    mycanvas.drawRightString(x_axis + 380, y_axis, str(int(data_dict[data][datas]["FCM 500"])))
                    fcm500 += int(data_dict[data][datas]["FCM 500"])

                if data_dict[data][datas]["Tea 500"] != 0:
                    mycanvas.drawRightString(x_axis + 410, y_axis, str(int(data_dict[data][datas]["Tea 500"])))
                    tea500 += int(data_dict[data][datas]["Tea 500"])    

                if data_dict[data][datas]["TM 500 EVE"] != 0:
                    mycanvas.drawRightString(x_axis + 460, y_axis, str(int(data_dict[data][datas]["TM 500 EVE"])))
                    tm500_eve += int(data_dict[data][datas]["TM 500 EVE"])

                if data_dict[data][datas]["STD 500 EVE"] != 0:
                    mycanvas.drawRightString(x_axis + 500, y_axis, str(int(data_dict[data][datas]["STD 500 EVE"])))
                    std500_eve += int(data_dict[data][datas]["STD 500 EVE"])

                if data_dict[data][datas]["STD 250 EVE"] != 0:
                    mycanvas.drawRightString(x_axis + 540, y_axis, str(int(data_dict[data][datas]["STD 250 EVE"])))
                    std250_eve += int(data_dict[data][datas]["STD 250 EVE"])

                if data_dict[data][datas]["FCM 500 EVE"] != 0:
                    mycanvas.drawRightString(x_axis + 580, y_axis, str(int(data_dict[data][datas]["FCM 500 EVE"])))
                    fcm500_eve += int(data_dict[data][datas]["FCM 500 EVE"])

                if data_dict[data][datas]["Tea 500 EVE"] != 0:
                    mycanvas.drawRightString(x_axis + 610, y_axis, str(int(data_dict[data][datas]["Tea 500 EVE"])))
                    tea500_eve += int(data_dict[data][datas]["Tea 500 EVE"])    

                # lines
                mycanvas.line(x_axis - 5, y_axis + 55, x_axis - 5, y_axis - 15)
                mycanvas.line(x_axis + 20, y_axis + 55, x_axis + 20, y_axis - 15)
                mycanvas.line(x_axis + 70, y_axis + 55, x_axis + 70, y_axis - 15)
                mycanvas.line(x_axis + 110, y_axis + 55, x_axis + 110, y_axis - 15)
                mycanvas.line(x_axis + 205, y_axis + 55, x_axis + 205, y_axis - 15)
                mycanvas.line(x_axis + 270, y_axis + 55, x_axis + 270, y_axis - 15)

                mycanvas.line(x_axis + 300, y_axis + 55, x_axis + 300, y_axis - 15)
                mycanvas.line(x_axis + 325, y_axis + 55, x_axis + 325, y_axis - 15)
                mycanvas.line(x_axis + 355, y_axis + 55, x_axis + 355, y_axis - 15)
                mycanvas.line(x_axis + 385, y_axis + 55, x_axis + 385, y_axis - 15)

                mycanvas.line(x_axis + 413, y_axis + 55, x_axis + 413, y_axis - 15)
                mycanvas.line(x_axis + 440, y_axis + 55, x_axis + 440, y_axis - 15)
                mycanvas.line(x_axis + 470, y_axis + 55, x_axis + 470, y_axis - 15)
                mycanvas.line(x_axis + 500, y_axis + 55, x_axis + 500, y_axis - 15)
                mycanvas.line(x_axis + 530, y_axis + 55, x_axis + 530, y_axis - 15)
                mycanvas.line(x_axis + 570, y_axis + 55, x_axis + 570, y_axis - 15)

                if sl_no % 32 == 0:
                    mycanvas.line(head_x - 5, y_axis - 15, head_x + 535, y_axis - 15)
                    mycanvas.showPage()
                    mycanvas.setFont('Helvetica', 12.5)
                    mycanvas.drawCentredString(300, 820,
                                               'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                    mycanvas.setFont('Helvetica', 11)
                    mycanvas.drawString(30, 795, 'Boothwise Customer Card Details')
                    mycanvas.drawCentredString(300, 795, str(month_name) + "-" + str(year))
                    # mycanvas.drawString(500, 795, "Booth No : " + str(data))
                    # mycanvas.drawRightString(30, 785, name + str(zone_name))

                    # heading
                    mycanvas.setFont('Helvetica', 10)
                    head_y = 745
                    head_x = 15

                    mycanvas.drawString(head_x, head_y, "Sl")
                    mycanvas.drawString(head_x, head_y - 15, "No")
                    mycanvas.drawString(head_x + 27, head_y, "Card")
                    mycanvas.drawString(head_x + 33, head_y - 15, "NO")

                    mycanvas.drawString(head_x + 75, head_y, "Card")
                    mycanvas.drawString(head_x + 75, head_y - 15, "Sl No")

                    mycanvas.drawString(head_x + 130, head_y, "Name")
                    mycanvas.drawString(head_x + 210, head_y, "Customer Id")

                    # morning
                    mycanvas.drawString(head_x + 354, head_y + 23, "MORNING")

                    mycanvas.drawString(head_x + 275, head_y, "TM")
                    mycanvas.drawString(head_x + 277, head_y - 15, "500")
 
                    mycanvas.drawString(head_x + 300, head_y, "STD")
                    mycanvas.drawString(head_x + 307, head_y - 15, "500")

                    mycanvas.drawString(head_x + 335, head_y, "STD")
                    mycanvas.drawString(head_x + 338, head_y - 15, "250")

                    mycanvas.drawString(head_x + 365, head_y, "FCM")
                    mycanvas.drawString(head_x + 367, head_y - 15, "500")

                    mycanvas.drawString(head_x + 395, head_y, "Tea")
                    mycanvas.drawString(head_x + 397, head_y - 15, "500")

                    # evening
                    mycanvas.drawString(head_x + 422, head_y, "TM")
                    mycanvas.drawString(head_x + 423, head_y - 15, "500")

                    mycanvas.drawString(head_x + 451, head_y, "STD")
                    mycanvas.drawString(head_x + 452, head_y - 15, "500")

                    mycanvas.drawString(head_x + 480, head_y, "STD")
                    mycanvas.drawString(head_x + 482, head_y - 15, "250")

                    mycanvas.drawString(head_x + 512, head_y, "FCM")
                    mycanvas.drawString(head_x + 514, head_y - 15, "500")

                    mycanvas.drawString(head_x + 541, head_y, "Tea")
                    mycanvas.drawString(head_x + 546, head_y - 15, "500")

                    mycanvas.drawString(head_x + 485, head_y + 23, "EVENING")
                    # heading_top & Bottom Line

                    mycanvas.line(head_x - 5, head_y + 15, head_x + 570, head_y + 15)
                    mycanvas.line(head_x - 5, head_y - 22, head_x + 570, head_y - 22)

                    mycanvas.line(head_x + 270, head_y + 35, head_x + 670, head_y + 35)
                    mycanvas.line(head_x + 270, head_y + 35, head_x + 270, head_y)
                    mycanvas.line(head_x + 413, head_y + 35, head_x + 413, head_y)
                    mycanvas.line(head_x + 570, head_y + 35, head_x + 570, head_y)

                    # table_content
                    x_axis = 15
                    y_axis = 705

                y_axis -= 20
                sl_no += 1
            y_axis -= 20
            mycanvas.line(head_x - 5, y_axis + 25, head_x + 570, y_axis + 25)
            mycanvas.line(head_x + 270, y_axis + 5, head_x + 570, y_axis + 5)

            mycanvas.line(x_axis + 300, y_axis + 25, x_axis + 300, y_axis + 5)
        
            mycanvas.line(x_axis + 270, y_axis + 25, x_axis + 270, y_axis + 5)
            mycanvas.line(x_axis + 325, y_axis + 25, x_axis + 325, y_axis + 5)
            mycanvas.line(x_axis + 355, y_axis + 25, x_axis + 355, y_axis + 5)
            mycanvas.line(x_axis + 385, y_axis + 25, x_axis + 385, y_axis + 5)
            mycanvas.line(x_axis + 413, y_axis + 25, x_axis + 413, y_axis + 5)

            mycanvas.line(x_axis + 440, y_axis + 25, x_axis + 440, y_axis + 5)
            mycanvas.line(x_axis + 470, y_axis + 25, x_axis + 470, y_axis + 5)
            mycanvas.line(x_axis + 500, y_axis + 25, x_axis + 500, y_axis + 5)
            mycanvas.line(x_axis + 530, y_axis + 25, x_axis + 530, y_axis + 5)
            mycanvas.line(x_axis + 570, y_axis + 25, x_axis + 570, y_axis + 5)
            mycanvas.line(x_axis + 600, y_axis + 25, x_axis + 600, y_axis + 5)

            mycanvas.drawRightString(x_axis + 225, y_axis + 8, "G R A N D   T O T A L")

            mycanvas.drawRightString(x_axis + 275, y_axis + 8, str(tm500))
            mycanvas.drawRightString(x_axis + 305, y_axis + 8, str(std500))
            mycanvas.drawRightString(x_axis + 335, y_axis + 8, str(std250))
            mycanvas.drawRightString(x_axis + 365, y_axis + 8, str(fcm500))
            mycanvas.drawRightString(x_axis + 395, y_axis + 8, str(tea500))

            mycanvas.drawRightString(x_axis + 425, y_axis + 8, str(tm500_eve))
            mycanvas.drawRightString(x_axis + 465, y_axis + 8, str(std500_eve))
            mycanvas.drawRightString(x_axis + 495, y_axis + 8, str(std250_eve))
            mycanvas.drawRightString(x_axis + 525, y_axis + 8, str(fcm500_eve))
            mycanvas.drawRightString(x_axis + 565, y_axis + 8, str(tea500_eve))

            mycanvas.showPage()
    # mycanvas.setFont('Times-Italic', 10)
    # indian = pytz.timezone('Asia/Kolkata')
    # mycanvas.drawRightString(580, 10, 'Report Generated by: ' + str(
    #     data_dict["user_name"] + ", @" + str(datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

    mycanvas.save()
    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document


@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_years_list_for_comparision_five(request):
    year = datetime.today().year
    data = [year - i for i in range(6)]
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_comparision_five_data(request):
    print(request.data)
    data_dict = {}
    session_ids = []
    if request.data['selected_session'] == "all":
        session_ids = [1, 2]
        sess_name = "Both_Shifts"
    else:
        session_ids.append(int(request.data['selected_session']))
        if request.data['selected_session'] == '1':
            sess_name = "Morning_Shifts"
        else:
            sess_name = "Evening_Shifts"

    business_type_list = request.data['selected_booth_type_list']
    if request.data['selected_inp_type'] == "Month":
        datas = []
        year = request.data['selected_year']
        months = request.data['selected_month_list']
        for month in months:
            datetime_object = datetime.strptime(month, "%B")
            datas.append(datetime_object.month)

        business_ids = list(DailySessionllyBusinessllySale.objects.filter(business_type_id__in=business_type_list,
                                                                          delivery_date__month__in=datas,
                                                                          delivery_date__year=year,
                                                                          session_id__in=session_ids).order_by(
            'zone_id').values_list("business_id", flat=True))
        business_ids = set(business_ids)
        business_ids = list(business_ids)
        title_name = str(datas) + "-" + str(year)
    else:
        datas = pd.date_range(start=request.data['selected_from_date'], end=request.data['selected_to_date'])
        business_ids = list(DailySessionllyBusinessllySale.objects.filter(business_type_id__in=business_type_list,
                                                                          delivery_date__in=datas,
                                                                          session_id__in=session_ids).order_by(
            'zone_id').values_list("business_id", flat=True))
        business_ids = set(business_ids)
        business_ids = list(business_ids)
        title_name = str(request.data['selected_from_date']) + "-to-" + str(request.data['selected_to_date'])

    for data in datas:
        for business in Business.objects.filter(id__in=business_ids).order_by('zone_id'):
            if not business.code in data_dict:
                data_dict[business.code] = {
                    "Zone": business.zone.name,
                    "Booth Name": business.user_profile.user.first_name + '' + business.user_profile.user.last_name,
                    # business.name[7:],
                    "business_type": business.business_type_id
                }
            if request.data['selected_inp_type'] == "Month":
                month = data
                year = year
                days = monthrange(int(year), int(month))
                datetime_object = datetime.strptime(str(month), "%m")
                mon_name = datetime_object.strftime("%b")
                if not str(mon_name) + "-" + str(year) in data_dict[business.code]:
                    data_dict[business.code][str(mon_name) + "-" + str(year)] = 0
                milk_lit = DailySessionllyBusinessllySale.objects.filter(business_id=business.id,
                                                                         delivery_date__month=data,
                                                                         delivery_date__year=year,
                                                                         sold_to__in=["Agent", "ICustomer"],
                                                                         session_id__in=session_ids)
            else:
                date = datetime.strftime(data, "%d-%m-%Y")
                if not date in data_dict[business.code]:
                    data_dict[business.code][date] = 0
                milk_lit = DailySessionllyBusinessllySale.objects.filter(business_id=business.id, delivery_date=data,
                                                                         sold_to__in=["Agent", "ICustomer"],
                                                                         session_id__in=session_ids)

            if milk_lit:
              milk_tot = milk_lit.aggregate(Sum('milk_litre'))['milk_litre__sum']
            else:
              milk_tot = 0
            if request.data['selected_inp_type'] == "Month":
                data_dict[business.code][str(mon_name) + "-" + str(year)] = milk_tot
            else:
                data_dict[business.code][date] = milk_tot

    df = pd.DataFrame(data_dict)
    document = {}
    if not df.empty:
      data_avaliable = True
      df_t = df.T
      file_name = "pvt_and_govt_ins_milk_report" + str(title_name) + "_for_" + sess_name + ".xlsx"
      file_path = os.path.join('static/media', file_name)
      df_t.to_excel(os.path.join('static/media', file_name))

      df_t = pd.read_excel(file_path, header=None)

      excel_file_name = "pvt_and_govt_ins_milk_report" + str(title_name) + "_for_" + sess_name + ".xlsx"
      excel_file_path = os.path.join('static/media', excel_file_name)

      df_t = df_t.fillna('')

      with pd.ExcelWriter(excel_file_path) as writer:
          for business_type in BusinessType.objects.filter(id__in=business_type_list):
              filtered_df = df_t[(df_t[3] == "business_type") | (df_t[3] == '') | (df_t[3] == business_type.id)]
              if filtered_df.shape[0] > 2:
                  new_header = filtered_df.iloc[0]
                  filtered_df = filtered_df[1:]
                  filtered_df.columns = new_header
                  filtered_df = filtered_df.rename(columns={'': 'Booth Code'})
                  filtered_df = filtered_df.drop(columns=['business_type'])

                  for columns in filtered_df.columns[3:]:
                      filtered_df[columns] = pd.to_numeric(filtered_df[columns])
                  filtered_df[["Booth Code"]] = filtered_df[["Booth Code"]].astype(int).astype(str)
                  filtered_df.to_excel(writer, sheet_name=str(business_type.name), index=False)

      document['file_name'] = excel_file_name
      image_path = excel_file_path
      try:
        image_path = excel_file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
      except Exception as err:
         print(err)
    else:
        data_avaliable = False
    
    document['data_avaliable'] = data_avaliable
    
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_monthly_bill_abstact(request):
    data_dict = {}
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    data_range = pd.date_range(start=from_date, end=to_date)
    for business_id in [3, 6, 5, 4, 10, 16, 15]:
        if business_id == 15:
            data = BusinessType.objects.get(id=4)
            print(data)
        else:
            data = BusinessType.objects.get(id=business_id)
        if not data.finance_main_code in data_dict:
            data_dict[data.finance_main_code] = {}
        if business_id == 3:
            data_dict["20234"] = {}
        if business_id == 4:
            data_dict["10901"] = {}
    thirupur_booths = []
    for data in data_dict:
        data_dict[data][str(data) + " Sub Total"] = {
            "sub_tm_ltr": 0,
            "sub_tm_amt": 0,
            "sub_std_ltr": 0,
            "sub_std_amt": 0,
            "sub_fcm_ltr": 0,
            "sub_fcm_amt": 0,
            "sub_tea_ltr": 0,
            "sub_tea_amt": 0,
            "sub_mlk_qty": 0,
            "sub_mlk_amt": 0,
            "btmlk_ltr": 0,
            "btmlk_amt": 0,
            "curd_kgs": 0,
            "curd_amt": 0,
        }
        print(data)
        if data == "20234":
            sale_booths = list(
                DailySessionllyBusinessllySale.objects.filter(business__code__in=[1999, 2000]).order_by('business__code').values_list(
                    "business_id", flat=True))
            sale_booths = set(sale_booths)
            sale_booths = sorted(list(sale_booths))
        elif data == "10901":
            sale_booths = list(
                BusinessAgentMap.objects.filter(agent__agent_code__in=["2135", "2677"]).order_by('business__code').values_list(
                    "business_id", flat=True))
            sale_booths = set(sale_booths)
            sale_booths = sorted(list(sale_booths))
            sale_booths.append(33390)
        elif BusinessType.objects.filter(finance_main_code=data)[0].id == 6:
            sale_booths = []
            # thirupur_booths = list(DailySessionllyBusinessllySale.objects.filter(business_type__finance_main_code=data,
            #                                                                      delivery_date__in=data_range,
            #                                                                      union="TIRUPPUR Union").order_by('business__code').values_list("business_id", flat=True))
            # thirupur_booths = set(thirupur_booths)
            # thirupur_booths = sorted(list(thirupur_booths))
            thirupur_booths = [70506]
            sale_booths.extend(thirupur_booths)

            other_booths = list(DailySessionllyBusinessllySale.objects.filter(business_type__finance_main_code=data,
                                                                              delivery_date__in=data_range).order_by('business__code').exclude(
                union="TIRUPPUR Union").values_list("business_id", flat=True))
            other_booths = set(other_booths)
            other_booths = sorted(list(other_booths))
            sale_booths.extend(other_booths)
        else:
            sale_booths = list(DailySessionllyBusinessllySale.objects.filter(business_type__finance_main_code=data,
                                                                             delivery_date__in=data_range).order_by('business__code').exclude(
                business__code__in=[1999, 2000, 1]).values_list("business_id", flat=True))
            sale_booths = set(sale_booths)
            sale_booths = sorted(list(sale_booths))

        for booth_id in sorted(list(sale_booths)):
            if booth_id in thirupur_booths:
                sale_obj = DailySessionllyBusinessllySale.objects.filter(union="TIRUPPUR Union",
                                                                         delivery_date__in=data_range).order_by('business__code')
            elif booth_id == 33390:
                print("hii",booth_id)
                prp_booths = list(
                BusinessAgentMap.objects.filter(agent__agent_code__in=["33390", "9031WSD"]).order_by('business__code').values_list(
                    "business_id", flat=True))
                prp_booths = set(prp_booths)
                prp_booths = sorted(list(prp_booths))
                sale_obj = DailySessionllyBusinessllySale.objects.filter(business_id__in=prp_booths,
                                                                        delivery_date__in=data_range,
                                                                        sold_to__in=["Agent", "Icustomer"]).order_by('business__code')
                booth_name = "P.R.P. Enterprises P"
                booth_code = "33390"
            else:
                sale_obj = DailySessionllyBusinessllySale.objects.filter(business_id=booth_id,
                                                                         delivery_date__in=data_range,
                                                                         sold_to__in=["Agent", "Icustomer"]).exclude(business_type_id=15).order_by('business__code')
            if data in ["10901", "20258", "20234"]:
                if booth_id != 33390:
                    booth_name = Business.objects.get(
                        id=booth_id).user_profile.user.first_name + " " + Business.objects.get(
                        id=booth_id).user_profile.user.last_name
                    booth_code = Business.objects.get(id=booth_id).code
                if data == "10901":
                    if booth_id != 33390:
                        booth_code = BusinessAgentMap.objects.get(business_id=booth_id).agent.agent_code

            else:
                if booth_id == 70506:
                    booth_name = "Tirtppur"
                    booth_code = 70506
                elif booth_id == 2536:
                    booth_name = Business.objects.get(id=booth_id).name[7:]
                    booth_code = 70403
                else:
                    booth_name = Business.objects.get(id=booth_id).name[7:]
                    booth_code = Business.objects.get(id=booth_id).code

            data_dict[data][booth_id] = {
                "booth_code": str(booth_code),
                "booth_name": booth_name,
                "tm_ltr": 0,
                "tm_amt": 0,
                "std_ltr": 0,
                "std_amt": 0,
                "fcm_ltr": 0,
                "fcm_amt": 0,
                "tea_ltr": 0,
                "tea_amt": 0,
                "total_milk_ltr": 0,
                "total_mlk_amt": 0,
                "btmlk_ltr": 0,
                "btmlk_amt": 0,
                "curd_kgs": 0,
                "curd_cost": 0,
            }

            tm_ltr = 0
            tm_amt = 0
            std_ltr = 0
            std_amt = 0
            fcm_ltr = 0
            fcm_amt = 0
            tea_ltr = 0
            tea_amt = 0

            btmlk_ltr = 0
            btmlk_amt = 0
            curd_kgs = 0
            curd_amt = 0

            milk_lit = 0
            milk_amt = 0
            if not sale_obj.count() == 0:
              if not sale_obj[0].union == 'TIRUPPUR Union':
                # tm
                if not sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] is None:
                    tm_ltr += sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']

                if not sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum'] is None:
                    tm_amt += sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']

                # std
                if not sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"] is None:
                    std_ltr += sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]

                if not sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"] is None:
                    std_ltr += sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]

                if not sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"] is None:
                    std_amt += sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]

                if not sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"] is None:
                    std_amt += sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]

                # fcm
                if not sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] is None:
                    fcm_ltr += sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"]

                if not sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"] is None:
                    fcm_ltr += sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]

                if not sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] is None:
                    fcm_amt += sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]

                if not sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"] is None:
                    fcm_amt += sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]

                # tmate
                if not sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] is None:
                    tea_ltr += sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"]

                if not sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"] is None:
                    tea_ltr += sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

                if not sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] is None:
                    tea_amt += sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"]

                if not sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"] is None:
                    tea_amt += sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]    

                # btmlk
                if not sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum'] is None:
                    btmlk_ltr += sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']

                if not sale_obj.aggregate(Sum('buttermilk200_cost'))['buttermilk200_cost__sum'] is None:
                    btmlk_amt += sale_obj.aggregate(Sum('buttermilk200_cost'))['buttermilk200_cost__sum']
                    
                # btmlk_jar
                if not sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum'] is None:
                    btmlk_ltr += sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']

                if not sale_obj.aggregate(Sum('bm_jar200_cost'))['bm_jar200_cost__sum'] is None:
                    btmlk_amt += sale_obj.aggregate(Sum('bm_jar200_cost'))['bm_jar200_cost__sum']

              # curd
              if not sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] is None:
                  curd_kgs += sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']

              if not sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum'] is None:
                  curd_kgs += sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']

              if not sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] is None:
                  curd_kgs += sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']

              if not sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] is None:
                  curd_kgs += sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']

              if not sale_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum'] is None:
                  curd_amt += sale_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum']

              if not sale_obj.aggregate(Sum('curd150_cost'))['curd150_cost__sum'] is None:
                  curd_amt += sale_obj.aggregate(Sum('curd150_cost'))['curd150_cost__sum']

              if not sale_obj.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum'] is None:
                  curd_amt += sale_obj.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum']

            data_dict[data][booth_id]["tm_ltr"] = tm_ltr
            data_dict[data][booth_id]["tm_amt"] = round(tm_amt)
            data_dict[data][booth_id]["std_ltr"] = std_ltr
            data_dict[data][booth_id]["std_amt"] = round(std_amt)
            data_dict[data][booth_id]["fcm_ltr"] = fcm_ltr
            data_dict[data][booth_id]["fcm_amt"] = round(fcm_amt)
            data_dict[data][booth_id]["tea_ltr"] = tea_ltr
            data_dict[data][booth_id]["tea_amt"] = round(tea_amt)

            data_dict[data][booth_id]["btmlk_ltr"] = btmlk_ltr
            data_dict[data][booth_id]["btmlk_amt"] = round(btmlk_amt)
            data_dict[data][booth_id]["curd_kgs"] = curd_kgs
            data_dict[data][booth_id]["curd_cost"] = round(curd_amt)

            milk_lit += tm_ltr + std_ltr + fcm_ltr + tea_ltr
            milk_amt += tm_amt + std_amt + fcm_amt + tea_amt

            data_dict[data][booth_id]["total_milk_ltr"] = milk_lit
            data_dict[data][booth_id]["total_mlk_amt"] = round(milk_amt)

            data_dict[data][str(data) + " Sub Total"]["sub_tm_ltr"] += tm_ltr
            data_dict[data][str(data) + " Sub Total"]["sub_tm_amt"] += round(tm_amt)
            data_dict[data][str(data) + " Sub Total"]["sub_std_ltr"] += std_ltr
            data_dict[data][str(data) + " Sub Total"]["sub_std_amt"] += round(std_amt)
            data_dict[data][str(data) + " Sub Total"]["sub_fcm_ltr"] += fcm_ltr
            data_dict[data][str(data) + " Sub Total"]["sub_fcm_amt"] += round(fcm_amt)
            data_dict[data][str(data) + " Sub Total"]["sub_tea_ltr"] += tea_ltr
            data_dict[data][str(data) + " Sub Total"]["sub_tea_amt"] += round(tea_amt)
            data_dict[data][str(data) + " Sub Total"]["sub_mlk_qty"] += milk_lit
            data_dict[data][str(data) + " Sub Total"]["sub_mlk_amt"] += round(milk_amt)
            data_dict[data][str(data) + " Sub Total"]["btmlk_ltr"] += btmlk_ltr
            data_dict[data][str(data) + " Sub Total"]["btmlk_amt"] += round(btmlk_amt)
            data_dict[data][str(data) + " Sub Total"]["curd_kgs"] += curd_kgs
            data_dict[data][str(data) + " Sub Total"]["curd_amt"] += round(curd_amt)
    data = month_wise_inistitution_bill_abstract_pdf_gen(data_dict, data_range)
    return Response(data=data, status=status.HTTP_200_OK)


def month_wise_inistitution_bill_abstract_pdf_gen(data_dict, data_range):
    #     month_name = datetime.date(2020, month, 1).strftime('%B')
    file_name = "month_wise_inistitution_bill_abstract ( " + str(data_range[0])[:10] + "_to_" + str(data_range[-1])[
                                                                                                :10] + " )" + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=(15 * inch, 12 * inch))

    # ________Head_lines________#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))

    mycanvas.setFont('Helvetica', 15)
    mycanvas.drawCentredString(520, 840,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 11)
    mycanvas.setFillColor(HexColor(dark_color))

    from_date = datetime.strptime(str(data_range[0])[:10], '%Y-%m-%d')
    from_date = datetime.strftime(from_date, '%d-%m-%Y')
    
    to_date = datetime.strptime(str(data_range[-1])[:10], '%Y-%m-%d')
    to_date = datetime.strftime(to_date, '%d-%m-%Y')

    mycanvas.drawCentredString(520, 825,'Monthly Institution Bill Abstract - ' + str(from_date) + "_to_" + str(to_date))
    mycanvas.setFont('Helvetica-Bold', 8)
    mycanvas.setLineWidth(0)

    head_x = 25
    head_y = 785

    x_axis = 30
    y_axis = 745

    x_ad = -5
    # heading
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(head_x, head_y, "Code")
    mycanvas.drawString(head_x + 47, head_y, "Description")
    mycanvas.drawString(head_x + 125 + x_ad, head_y, "FCM")
    mycanvas.drawString(head_x + 215 - 25 + x_ad, head_y, "FCM Amt")
    mycanvas.drawString(head_x + 295 - 15 + x_ad, head_y, "STD")
    mycanvas.drawString(head_x + 345 - 15 + x_ad, head_y, "STD Amt")
    mycanvas.drawString(head_x + 415 - 10 + x_ad, head_y, "TM")
    mycanvas.drawString(head_x + 475 + x_ad, head_y, "TM Amt")
    mycanvas.drawString(head_x + 545 + x_ad, head_y, "TMT")
    mycanvas.drawString(head_x + 615 + x_ad, head_y, "TMT Amt")
    mycanvas.drawString(head_x + 685 + x_ad, head_y, "Ttl Qty")
    mycanvas.drawString(head_x + 740 + x_ad, head_y, "Ttl Amt")

    mycanvas.drawString(head_x + 810 + x_ad, head_y, "BM")
    mycanvas.drawString(head_x + 875 + x_ad, head_y, "BM amt")
    mycanvas.drawString(head_x + 925 + x_ad, head_y, "Curd")
    mycanvas.drawString(head_x + 985 + x_ad, head_y, "Curd amt")

    # top header lines
    mycanvas.line(head_x - 5, head_y + 20, head_x + 1035, head_y + 20)
    mycanvas.line(head_x - 5, head_y - 15, head_x + 1035, head_y - 15)

    mycanvas.line(x_axis - 10, head_y + 20, x_axis - 10, head_y - 15)  # 1

    mycanvas.line(x_axis + 40, head_y + 20, x_axis + 40, head_y - 15)  # 2

    mycanvas.line(x_axis + 100 + x_ad, head_y + 20, x_axis + 100 + x_ad, head_y - 15)  # 3
    mycanvas.line(x_axis + 195 + x_ad - 25, head_y + 20, x_axis + 195 + x_ad - 25, head_y - 15)  # 4
    mycanvas.line(x_axis + 255 + x_ad - 15, head_y + 20, x_axis + 255 + x_ad - 15, head_y - 15)  # 5
    mycanvas.line(x_axis + 320 + x_ad - 15, head_y + 20, x_axis + 320 + x_ad - 15, head_y - 15)  # 6
    mycanvas.line(x_axis + 385 + x_ad - 10, head_y + 20, x_axis + 385 + x_ad - 10, head_y - 15)  # 7
    mycanvas.line(x_axis + 450 + x_ad, head_y + 20, x_axis + 450 + x_ad, head_y - 15)  # 8
    mycanvas.line(x_axis + 515 + x_ad, head_y + 20, x_axis + 515 + x_ad, head_y - 15)  # 9

    mycanvas.line(x_axis + 595 + x_ad, head_y + 20, x_axis + 595 + x_ad, head_y - 15)  # 10
    mycanvas.line(x_axis + 655 + x_ad, head_y + 20, x_axis + 655 + x_ad, head_y - 15)  # 11
    mycanvas.line(x_axis + 725 + x_ad, head_y + 20, x_axis + 725 + x_ad, head_y - 15)  # 12
    mycanvas.line(x_axis + 795 + x_ad, head_y + 20, x_axis + 795 + x_ad, head_y - 15)  # 13
    mycanvas.line(x_axis + 855 + x_ad, head_y + 20, x_axis + 855 + x_ad, head_y - 15)  # 14
    mycanvas.line(x_axis + 915 + x_ad, head_y + 20, x_axis + 915 + x_ad, head_y - 15)  # 15
    mycanvas.line(x_axis + 975 + x_ad, head_y + 20, x_axis + 975 + x_ad, head_y - 15)  # 16

    mycanvas.line(x_axis + 1030, head_y + 20, x_axis + 1030, head_y - 15)  # 17

    main_name = ""
    for data in data_dict:
        if data == "20258":
            main_name = data + " UNION PARLOUR"
        if data == "20234":
            main_name = data + " S.DR. UNION STAFF"
        if data == "20233":
            main_name = data + " S.DR. OTHER UNION"
        if data == "20201":
            main_name = data + " S.DR. (GOVT. INSTITUTION)"
        if data == "10961":
            main_name = data + " MILK SUPPLY(PVT. INSTITUTION)"
        if data == "10901":
            main_name = data + " MILK SALES"
        if data == "20238":
            main_name = data + " SOCIETY"

        mycanvas.setFont('Helvetica', 10)
        mycanvas.drawString(x_axis, y_axis, main_name)

        mycanvas.setFont('Helvetica', 10)

        y_axis -= 30
        mycanvas.line(x_axis - 10, y_axis + 15, x_axis + 1030, y_axis + 15)
        for value in data_dict[data]:
            if value == str(data) + " Sub Total":
                sub_total = value
            else:
                if data_dict[data][value]["total_mlk_amt"] + data_dict[data][value]["btmlk_amt"] + data_dict[data][value]["curd_cost"] != 0:
                    mycanvas.setFont('Helvetica', 10)
                    if data == "10901":
                        mycanvas.setFont('Helvetica', 10)
                        mycanvas.drawString(x_axis - 8, y_axis, str(data_dict[data][value]["booth_code"]).lower())
                    elif data == "20201" or data == "10961":
                        mycanvas.setFont('Helvetica', 10)
                        if len(str(data_dict[data][value]["booth_code"]).lower()) == 4:
                            mycanvas.drawString(x_axis - 5, y_axis, "5" + str(data_dict[data][value]["booth_code"]).lower())
                        else:
                            mycanvas.drawString(x_axis - 5, y_axis, str(data_dict[data][value]["booth_code"]).lower())
                    else:
                        mycanvas.setFont('Helvetica', 10)
                        mycanvas.drawString(x_axis - 5, y_axis, str(data_dict[data][value]["booth_code"]).lower())
                    mycanvas.drawString(x_axis + 38, y_axis, data_dict[data][value]["booth_name"][:20].title())
                    if data_dict[data][value]["fcm_ltr"] != 0:
                        mycanvas.drawRightString(x_axis + 200 + x_ad - 25, y_axis, str(data_dict[data][value]["fcm_ltr"]))
                    if data_dict[data][value]["fcm_amt"] != 0:
                        mycanvas.drawRightString(x_axis + 270 + x_ad - 15, y_axis, str(data_dict[data][value]["fcm_amt"]))
                    if data_dict[data][value]["std_ltr"] != 0:
                        mycanvas.drawRightString(x_axis + 345 + x_ad - 15, y_axis, str(data_dict[data][value]["std_ltr"]))
                    if data_dict[data][value]["std_amt"] != 0:
                        mycanvas.drawRightString(x_axis + 420 + x_ad - 10, y_axis, str(data_dict[data][value]["std_amt"]))
                    if data_dict[data][value]["tm_ltr"] != 0:
                        mycanvas.drawRightString(x_axis + 480 + x_ad, y_axis, str(data_dict[data][value]["tm_ltr"]))
                    if data_dict[data][value]["tm_amt"] != 0:
                        mycanvas.drawRightString(x_axis + 550 + x_ad, y_axis, str(data_dict[data][value]["tm_amt"]))
                    if data_dict[data][value]["tea_ltr"] != 0:
                        mycanvas.drawRightString(x_axis + 630 + x_ad, y_axis, str(data_dict[data][value]["tea_ltr"]))
                    if data_dict[data][value]["tea_amt"] != 0:
                        mycanvas.drawRightString(x_axis + 720 + x_ad, y_axis, str(data_dict[data][value]["tea_amt"]))    
                    if data_dict[data][value]["total_milk_ltr"] != 0:
                        mycanvas.drawRightString(x_axis + 775 + x_ad, y_axis, str(data_dict[data][value]["total_milk_ltr"]))
                    if data_dict[data][value]["total_mlk_amt"] != 0:
                        mycanvas.drawRightString(x_axis + 830 + x_ad, y_axis, str(data_dict[data][value]["total_mlk_amt"]))
                    if data_dict[data][value]["btmlk_ltr"] != 0:
                        mycanvas.drawRightString(x_axis + 900 + x_ad, y_axis, str(data_dict[data][value]["btmlk_ltr"]))
                    if data_dict[data][value]["btmlk_amt"] != 0:
                        mycanvas.drawRightString(x_axis + 970 + x_ad, y_axis, str(data_dict[data][value]["btmlk_amt"]))
                    if data_dict[data][value]["curd_kgs"] != 0:
                        mycanvas.drawRightString(x_axis + 1020 + x_ad, y_axis, str(data_dict[data][value]["curd_kgs"]))
                    if data_dict[data][value]["curd_cost"] != 0:
                        mycanvas.drawRightString(x_axis + 1070 + x_ad, y_axis, str(data_dict[data][value]["curd_cost"]))

                    # lines
                    mycanvas.line(x_axis - 10, y_axis + 15, x_axis - 10, y_axis - 10)  # 1

                    mycanvas.line(x_axis + 35, y_axis + 15, x_axis + 35, y_axis - 10)  # 2

                    mycanvas.line(x_axis + 100 + x_ad, y_axis + 15, x_axis + 100 + x_ad, y_axis - 10)  # 3
                    mycanvas.line(x_axis + 205 + x_ad - 25, y_axis + 15, x_axis + 205 + x_ad - 25, y_axis - 10)  # 4
                    mycanvas.line(x_axis + 275 + x_ad - 15, y_axis + 15, x_axis + 275 + x_ad - 15, y_axis - 10)  # 5
                    mycanvas.line(x_axis + 350 + x_ad - 15, y_axis + 15, x_axis + 350 + x_ad - 15, y_axis - 10)  # 6
                    mycanvas.line(x_axis + 425 + x_ad - 10, y_axis + 15, x_axis + 425 + x_ad - 10, y_axis - 10)  # 7
                    mycanvas.line(x_axis + 485 + x_ad, y_axis + 15, x_axis + 485 + x_ad, y_axis - 10)  # 8
                    mycanvas.line(x_axis + 555 + x_ad, y_axis + 15, x_axis + 555 + x_ad, y_axis - 10)  # 9
                    mycanvas.line(x_axis + 635 + x_ad, y_axis + 15, x_axis + 635 + x_ad, y_axis - 10)  # 10
                    mycanvas.line(x_axis + 725 + x_ad, y_axis + 15, x_axis + 725 + x_ad, y_axis - 10)  # 11
                    mycanvas.line(x_axis + 780 + x_ad, y_axis + 15, x_axis + 780 + x_ad, y_axis - 10)  # 12
                    mycanvas.line(x_axis + 835 + x_ad, y_axis + 15, x_axis + 835 + x_ad, y_axis - 10)  # 13
                    mycanvas.line(x_axis + 905 + x_ad, y_axis + 15, x_axis + 905 + x_ad, y_axis - 10)  # 14
                    mycanvas.line(x_axis + 955 + x_ad, y_axis + 20, x_axis + 955 + x_ad, y_axis - 10)  # 13
                    mycanvas.line(x_axis + 1020 + x_ad, y_axis + 20, x_axis + 1020 + x_ad, y_axis - 10)  # 14

                    mycanvas.line(x_axis + 1080, y_axis + 15, x_axis + 1080, y_axis - 10)  # 15
                    y_axis -= 15
                    if y_axis + 15 <= 80:
                        mycanvas.line(x_axis - 10, y_axis + 5, x_axis + 1030, y_axis + 5)
                        mycanvas.showPage()
                        mycanvas.setFont('Helvetica', 15)
                        mycanvas.drawCentredString(520, 840,
                                                'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                        mycanvas.setFont('Helvetica', 14)
                        mycanvas.setFillColor(HexColor(dark_color))
                        mycanvas.drawCentredString(520, 825, 'Monthly Institution Bill Abstract - ' + str(from_date) + "_to_" + str(to_date))
                        mycanvas.setFont('Helvetica-Bold', 10)
                        mycanvas.setLineWidth(0)

                        head_x = 25
                        head_y = 785

                        x_axis = 30
                        y_axis = 760

                        # heading
                        mycanvas.setFont('Helvetica', 10)
                        mycanvas.drawString(head_x, head_y, "Code")
                        mycanvas.drawString(head_x + 47, head_y, "Description")
                        mycanvas.drawString(head_x + 125 + x_ad, head_y, "FCM")
                        mycanvas.drawString(head_x + 215 - 25 + x_ad, head_y, "FCM Amt")
                        mycanvas.drawString(head_x + 295 - 15 + x_ad, head_y, "STD")
                        mycanvas.drawString(head_x + 345 - 15 + x_ad, head_y, "STD Amt")
                        mycanvas.drawString(head_x + 415 - 10 + x_ad, head_y, "TM")
                        mycanvas.drawString(head_x + 475 + x_ad, head_y, "TM Amt")
                        mycanvas.drawString(head_x + 545 + x_ad, head_y, "TMT")
                        mycanvas.drawString(head_x + 615 + x_ad, head_y, "TMT Amt")
                        mycanvas.drawString(head_x + 685 + x_ad, head_y, "Ttl Qty")
                        mycanvas.drawString(head_x + 740 + x_ad, head_y, "Ttl Amt")

                        mycanvas.drawString(head_x + 810 + x_ad, head_y, "BM")
                        mycanvas.drawString(head_x + 875 + x_ad, head_y, "BM amt")
                        mycanvas.drawString(head_x + 925 + x_ad, head_y, "Curd")
                        mycanvas.drawString(head_x + 985 + x_ad, head_y, "Curd amt")



                        # top header lines
                        mycanvas.line(head_x - 5, head_y + 20, head_x + 1035, head_y + 20)
                        mycanvas.line(head_x - 5, head_y - 15, head_x + 1035, head_y - 15)

                        mycanvas.line(x_axis - 10, head_y + 20, x_axis - 10, head_y - 15)  # 1

                        mycanvas.line(x_axis + 40, head_y + 20, x_axis + 40, head_y - 15)  # 2

                        mycanvas.line(x_axis + 100 + x_ad, head_y + 20, x_axis + 100 + x_ad, head_y - 15)  # 3
                        mycanvas.line(x_axis + 195 + x_ad - 25, head_y + 20, x_axis + 195 + x_ad - 25, head_y - 15)  # 4
                        mycanvas.line(x_axis + 255 + x_ad - 15, head_y + 20, x_axis + 255 + x_ad - 15, head_y - 15)  # 5
                        mycanvas.line(x_axis + 320 + x_ad - 15, head_y + 20, x_axis + 320 + x_ad - 15, head_y - 15)  # 6
                        mycanvas.line(x_axis + 385 + x_ad - 10, head_y + 20, x_axis + 385 + x_ad - 10, head_y - 15)  # 7
                        mycanvas.line(x_axis + 450 + x_ad, head_y + 20, x_axis + 450 + x_ad, head_y - 15)  # 8
                        mycanvas.line(x_axis + 515 + x_ad, head_y + 20, x_axis + 515 + x_ad, head_y - 15)  # 9

                        mycanvas.line(x_axis + 595 + x_ad, head_y + 20, x_axis + 595 + x_ad, head_y - 15)  # 10
                        mycanvas.line(x_axis + 655 + x_ad, head_y + 20, x_axis + 655 + x_ad, head_y - 15)  # 11
                        mycanvas.line(x_axis + 725 + x_ad, head_y + 20, x_axis + 725 + x_ad, head_y - 15)  # 12
                        mycanvas.line(x_axis + 795 + x_ad, head_y + 20, x_axis + 795 + x_ad, head_y - 15)  # 13
                        mycanvas.line(x_axis + 855 + x_ad, head_y + 20, x_axis + 855 + x_ad, head_y - 15)  # 14
                        mycanvas.line(x_axis + 915 + x_ad, head_y + 20, x_axis + 915 + x_ad, head_y - 15)  # 15
                        mycanvas.line(x_axis + 975 + x_ad, head_y + 20, x_axis + 975 + x_ad, head_y - 15)  # 16

                        mycanvas.line(x_axis + 1030, head_y + 20, x_axis + 1030, head_y - 15)  # 17

                        mycanvas.setLineWidth(0)
        y_axis -= 15
        mycanvas.line(x_axis - 10, y_axis + 20, x_axis + 1030, y_axis + 20)
        mycanvas.line(x_axis - 10, y_axis - 10, x_axis + 1030, y_axis - 10)

        # lines
        mycanvas.line(x_axis - 10, y_axis + 20, x_axis - 10, y_axis - 10)  # 1
        #         mycanvas.line(x_axis+35,y_axis+20,x_axis+35,y_axis-10) #2
        mycanvas.line(x_axis + 100 + x_ad, y_axis + 20, x_axis + 100 + x_ad, y_axis - 10)  # 3
        mycanvas.line(x_axis + 194 + x_ad - 25, y_axis + 20, x_axis + 194 + x_ad - 25, y_axis - 10)  # 4
        mycanvas.line(x_axis + 255 + x_ad - 15, y_axis + 20, x_axis + 255 + x_ad - 15, y_axis - 10)  # 5
        mycanvas.line(x_axis + 325 + x_ad - 15, y_axis + 20, x_axis + 325 + x_ad - 15, y_axis - 10)  # 6
        mycanvas.line(x_axis + 385 + x_ad - 10, y_axis + 20, x_axis + 385 + x_ad - 10, y_axis - 10)  # 7
        mycanvas.line(x_axis + 452 + x_ad, y_axis + 20, x_axis + 452 + x_ad, y_axis - 10)  # 8
        mycanvas.line(x_axis + 515 + x_ad, y_axis + 20, x_axis + 515 + x_ad, y_axis - 10)  # 9
        mycanvas.line(x_axis + 595 + x_ad, y_axis + 20, x_axis + 595 + x_ad, y_axis - 10)  # 10
        mycanvas.line(x_axis + 655 + x_ad, y_axis + 20, x_axis + 655 + x_ad, y_axis - 10)  # 11
        mycanvas.line(x_axis + 722 + x_ad, y_axis + 20, x_axis + 722 + x_ad, y_axis - 10)  # 12 
        mycanvas.line(x_axis + 795 + x_ad, y_axis + 20, x_axis + 795 + x_ad, y_axis - 10)  # 13
        mycanvas.line(x_axis + 855 + x_ad, y_axis + 20, x_axis + 855 + x_ad, y_axis - 10)  # 14
        mycanvas.line(x_axis + 920 + x_ad, y_axis + 20, x_axis + 920 + x_ad, y_axis - 10)  # 13
        mycanvas.line(x_axis + 975 + x_ad, y_axis + 20, x_axis + 975 + x_ad, y_axis - 10)  # 14
        mycanvas.line(x_axis + 1030, y_axis + 20, x_axis + 1030, y_axis - 10)  # 15

        # sub_Totals
        mycanvas.drawString(x_axis + 12, y_axis, sub_total)
        mycanvas.drawRightString(x_axis + 165 + x_ad - 25, y_axis, str(data_dict[data][sub_total]["sub_fcm_ltr"]))
        mycanvas.drawRightString(x_axis + 230 + x_ad - 15, y_axis, str(data_dict[data][sub_total]["sub_fcm_amt"]))
        mycanvas.drawRightString(x_axis + 300 + x_ad - 15, y_axis, str(data_dict[data][sub_total]["sub_std_ltr"]))
        mycanvas.drawRightString(x_axis + 360 + x_ad - 10, y_axis, str(data_dict[data][sub_total]["sub_std_amt"]))
        mycanvas.drawRightString(x_axis + 420 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tm_ltr"]))
        mycanvas.drawRightString(x_axis + 490 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tm_amt"]))
        mycanvas.drawRightString(x_axis + 555 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tea_ltr"]))
        mycanvas.drawRightString(x_axis + 635 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tea_amt"]))
        mycanvas.drawRightString(x_axis + 697 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_mlk_qty"]))
        mycanvas.drawRightString(x_axis + 765 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_mlk_amt"]))
        mycanvas.drawRightString(x_axis + 825 + x_ad, y_axis, str(data_dict[data][sub_total]["btmlk_ltr"]))
        mycanvas.drawRightString(x_axis + 890 + x_ad, y_axis, str(data_dict[data][sub_total]["btmlk_amt"]))
        mycanvas.drawRightString(x_axis + 950 + x_ad, y_axis, str(data_dict[data][sub_total]["curd_kgs"]))
        mycanvas.drawRightString(x_axis + 1010 + x_ad, y_axis, str(data_dict[data][sub_total]["curd_amt"]))

        y_axis -= 35

    # summary
    # if y_axis <= 200:
    #     #                 mycanvas.line(x_axis-10,y_axis+5,x_axis+1030,y_axis+5)
    #     mycanvas.showPage()
    #     mycanvas.setFont('Helvetica', 15)
    #     mycanvas.drawCentredString(520, 840,
    #                                'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    #     mycanvas.setFont('Helvetica', 14)
    #     mycanvas.setFillColor(HexColor(dark_color))
    #     mycanvas.drawCentredString(520, 825,'Monthly Institution Bill Abstract - ' + str(from_date) + "_to_" + str(to_date))
    #     mycanvas.setFont('Helvetica-Bold', 10)
    #     mycanvas.setLineWidth(0)

    #     head_x = 25
    #     head_y = 785

    #     x_axis = 30
    #     y_axis = 760

    #     # heading
    #     mycanvas.setFont('Helvetica', 14)
    #     mycanvas.drawString(head_x, head_y, "Code")
    #     mycanvas.drawString(head_x + 65, head_y, "Description")
    #     mycanvas.drawString(head_x + 125 + x_ad, head_y, "FCM")
    #     mycanvas.drawString(head_x + 215 - 25 + x_ad, head_y, "FCM Amt")
    #     mycanvas.drawString(head_x + 305 - 15 + x_ad, head_y, "STD")
    #     mycanvas.drawString(head_x + 365 - 15 + x_ad, head_y, "STD Amt")
    #     mycanvas.drawString(head_x + 450 - 10 + x_ad, head_y, "TM")
    #     mycanvas.drawString(head_x + 505 + x_ad, head_y, "TM Amt")
    #     mycanvas.drawString(head_x + 570 + x_ad, head_y, "Total Qty")
    #     mycanvas.drawString(head_x + 650 + x_ad, head_y, "Total Amt")

    #     mycanvas.drawString(head_x + 745 + x_ad, head_y, "BM")
    #     mycanvas.drawString(head_x + 790 + x_ad, head_y, "BM amt")
    #     mycanvas.drawString(head_x + 860 + x_ad, head_y, "Curd")
    #     mycanvas.drawString(head_x + 915 + x_ad, head_y, "Curd amt")

    #     # top header lines
    #     mycanvas.line(head_x - 5, head_y + 20, head_x + 1035, head_y + 20)
    #     mycanvas.line(head_x - 5, head_y - 15, head_x + 1035, head_y - 15)

    #     mycanvas.line(x_axis - 10, head_y + 20, x_axis - 10, head_y - 15)  # 1

    #     mycanvas.line(x_axis + 35, head_y + 20, x_axis + 35, head_y - 15)  # 2

    #     mycanvas.line(x_axis + 100 + x_ad, head_y + 20, x_axis + 100 + x_ad, head_y - 15)  # 3
    #     mycanvas.line(x_axis + 205 + x_ad - 25, head_y + 20, x_axis + 205 + x_ad - 25, head_y - 15)  # 4
    #     mycanvas.line(x_axis + 275 + x_ad - 15, head_y + 20, x_axis + 275 + x_ad - 15, head_y - 15)  # 5
    #     mycanvas.line(x_axis + 350 + x_ad - 15, head_y + 20, x_axis + 350 + x_ad - 15, head_y - 15)  # 6
    #     mycanvas.line(x_axis + 425 + x_ad - 10, head_y + 20, x_axis + 425 + x_ad - 10, head_y - 15)  # 7
    #     mycanvas.line(x_axis + 485 + x_ad, head_y + 20, x_axis + 485 + x_ad, head_y - 15)  # 8
    #     mycanvas.line(x_axis + 555 + x_ad, head_y + 20, x_axis + 555 + x_ad, head_y - 15)  # 9

    #     mycanvas.line(x_axis + 635 + x_ad, head_y + 20, x_axis + 635 + x_ad, head_y - 15)  # 10
    #     mycanvas.line(x_axis + 725 + x_ad, head_y + 20, x_axis + 725 + x_ad, head_y - 15)  # 11
    #     mycanvas.line(x_axis + 780 + x_ad, head_y + 20, x_axis + 780 + x_ad, head_y - 15)  # 12
    #     mycanvas.line(x_axis + 835 + x_ad, head_y + 20, x_axis + 835 + x_ad, head_y - 15)  # 13
    #     mycanvas.line(x_axis + 905 + x_ad, head_y + 20, x_axis + 905 + x_ad, head_y - 15)  # 14

    #     mycanvas.line(x_axis + 1030, head_y + 20, x_axis + 1030, head_y - 15)  # 15

    #     mycanvas.setLineWidth(0)

    y_axis = 800 - 80
    mycanvas.showPage()
    mycanvas.setFont('Helvetica', 15)
    mycanvas.drawCentredString(520, 840,
                                'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 14)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(520, 825,'Monthly Institution Bill Abstract - ' + str(from_date) + "_to_" + str(to_date))
    mycanvas.setFont('Helvetica-Bold', 10)


    head_x = 25
    head_y = 755

    x_ad = -5
    # heading
    # mycanvas.setFont('Helvetica', 14)     
    # mycanvas.drawCentredString(520, y_axis + 80, "A B S T R A C T")

    # # mycanvas.drawString(head_x, head_y, "Code")
    # mycanvas.drawString(head_x + 45, head_y, "Description")
    # mycanvas.drawString(head_x + 125 + x_ad, head_y, "FCM")
    # mycanvas.drawString(head_x + 215 - 25 + x_ad, head_y, "FCM Amt")
    # mycanvas.drawString(head_x + 305 - 15 + x_ad, head_y, "STD")
    # mycanvas.drawString(head_x + 365 - 15 + x_ad, head_y, "STD Amt")
    # mycanvas.drawString(head_x + 450 - 10 + x_ad, head_y, "TM")
    # mycanvas.drawString(head_x + 505 + x_ad, head_y, "TM Amt")
    # mycanvas.drawString(head_x + 570 + x_ad, head_y, "TMATE")
    # mycanvas.drawString(head_x + 650 + x_ad, head_y, "TMATE Amt")
    # mycanvas.drawString(head_x + 745 + x_ad, head_y, "Total Qty")
    # mycanvas.drawString(head_x + 790 + x_ad, head_y, "Total Amt")

    # mycanvas.drawString(head_x + 860 + x_ad, head_y, "BM")
    # mycanvas.drawString(head_x + 915 + x_ad, head_y, "BM amt")
    # mycanvas.drawString(head_x + 1060 + x_ad, head_y, "Curd")
    # mycanvas.drawString(head_x + 1100 + x_ad, head_y, "Curd amt")


    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawCentredString(520, y_axis + 80, "A B S T R A C T")
    # mycanvas.drawString(head_x, head_y, "Code")
    mycanvas.drawString(head_x + 47, head_y, "Description")
    mycanvas.drawString(head_x + 125 + x_ad, head_y, "FCM")
    mycanvas.drawString(head_x + 215 - 25 + x_ad, head_y, "FCM Amt")
    mycanvas.drawString(head_x + 295 - 15 + x_ad, head_y, "STD")
    mycanvas.drawString(head_x + 345 - 15 + x_ad, head_y, "STD Amt")
    mycanvas.drawString(head_x + 415 - 10 + x_ad, head_y, "TM")
    mycanvas.drawString(head_x + 475 + x_ad, head_y, "TM Amt")
    mycanvas.drawString(head_x + 545 + x_ad, head_y, "TMT")
    mycanvas.drawString(head_x + 615 + x_ad, head_y, "TMT Amt")
    mycanvas.drawString(head_x + 685 + x_ad, head_y, "Ttl Qty")
    mycanvas.drawString(head_x + 740 + x_ad, head_y, "Ttl Amt")

    mycanvas.drawString(head_x + 810 + x_ad, head_y, "BM")
    mycanvas.drawString(head_x + 875 + x_ad, head_y, "BM amt")
    mycanvas.drawString(head_x + 925 + x_ad, head_y, "Curd")
    mycanvas.drawString(head_x + 985 + x_ad, head_y, "Curd amt")

    mycanvas.line(head_x - 5, head_y + 20, head_x + 1035, head_y + 20)
    mycanvas.line(head_x - 5, head_y - 15, head_x + 1035, head_y - 15)

    mycanvas.line(x_axis - 10, head_y + 20, x_axis - 10, head_y - 15)  # 1

    mycanvas.line(x_axis + 40, head_y + 20, x_axis + 40, head_y - 15)  # 2

    mycanvas.line(x_axis + 100 + x_ad, head_y + 20, x_axis + 100 + x_ad, head_y - 15)  # 3
    mycanvas.line(x_axis + 195 + x_ad - 25, head_y + 20, x_axis + 195 + x_ad - 25, head_y - 15)  # 4
    mycanvas.line(x_axis + 255 + x_ad - 15, head_y + 20, x_axis + 255 + x_ad - 15, head_y - 15)  # 5
    mycanvas.line(x_axis + 320 + x_ad - 15, head_y + 20, x_axis + 320 + x_ad - 15, head_y - 15)  # 6
    mycanvas.line(x_axis + 385 + x_ad - 10, head_y + 20, x_axis + 385 + x_ad - 10, head_y - 15)  # 7
    mycanvas.line(x_axis + 450 + x_ad, head_y + 20, x_axis + 450 + x_ad, head_y - 15)  # 8
    mycanvas.line(x_axis + 515 + x_ad, head_y + 20, x_axis + 515 + x_ad, head_y - 15)  # 9

    mycanvas.line(x_axis + 595 + x_ad, head_y + 20, x_axis + 595 + x_ad, head_y - 15)  # 10
    mycanvas.line(x_axis + 655 + x_ad, head_y + 20, x_axis + 655 + x_ad, head_y - 15)  # 11
    mycanvas.line(x_axis + 725 + x_ad, head_y + 20, x_axis + 725 + x_ad, head_y - 15)  # 12
    mycanvas.line(x_axis + 795 + x_ad, head_y + 20, x_axis + 795 + x_ad, head_y - 15)  # 13
    mycanvas.line(x_axis + 855 + x_ad, head_y + 20, x_axis + 855 + x_ad, head_y - 15)  # 14
    mycanvas.line(x_axis + 915 + x_ad, head_y + 20, x_axis + 915 + x_ad, head_y - 15)  # 15
    mycanvas.line(x_axis + 975 + x_ad, head_y + 20, x_axis + 975 + x_ad, head_y - 15)  # 16

    mycanvas.line(x_axis + 1030, head_y + 20, x_axis + 1030, head_y - 15)  # 17

    # mycanvas.setLineWidth(0)

    # top header lines
    # mycanvas.line(head_x - 5, head_y + 20, head_x + 1035, head_y + 20)
    # mycanvas.line(head_x - 5, head_y - 15, head_x + 1035, head_y - 15)

    # mycanvas.line(x_axis - 10, head_y + 20, x_axis - 10, head_y - 15)  # 1

    # mycanvas.line(x_axis + 35, head_y + 20, x_axis + 35, head_y - 15)  # 2

    # mycanvas.line(x_axis + 100 + x_ad, head_y + 20, x_axis + 100 + x_ad, head_y - 15)  # 3
    # mycanvas.line(x_axis + 205 + x_ad - 25, head_y + 20, x_axis + 205 + x_ad - 25, head_y - 15)  # 4
    # mycanvas.line(x_axis + 275 + x_ad - 15, head_y + 20, x_axis + 275 + x_ad - 15, head_y - 15)  # 5
    # mycanvas.line(x_axis + 350 + x_ad - 15, head_y + 20, x_axis + 350 + x_ad - 15, head_y - 15)  # 6
    # mycanvas.line(x_axis + 425 + x_ad - 10, head_y + 20, x_axis + 425 + x_ad - 10, head_y - 15)  # 7
    # mycanvas.line(x_axis + 485 + x_ad, head_y + 20, x_axis + 485 + x_ad, head_y - 15)  # 8
    # mycanvas.line(x_axis + 555 + x_ad, head_y + 20, x_axis + 555 + x_ad, head_y - 15)  # 9

    # mycanvas.line(x_axis + 635 + x_ad, head_y + 20, x_axis + 635 + x_ad, head_y - 15)  # 10
    # mycanvas.line(x_axis + 725 + x_ad, head_y + 20, x_axis + 725 + x_ad, head_y - 15)  # 11
    # mycanvas.line(x_axis + 780 + x_ad, head_y + 20, x_axis + 780 + x_ad, head_y - 15)  # 12
    # mycanvas.line(x_axis + 835 + x_ad, head_y + 20, x_axis + 835 + x_ad, head_y - 15)  # 13
    # mycanvas.line(x_axis + 905 + x_ad, head_y + 20, x_axis + 905 + x_ad, head_y - 15)  # 14
    # mycanvas.line(x_axis + 955 + x_ad, head_y + 20, x_axis + 955 + x_ad, head_y - 15)  # 13
    # mycanvas.line(x_axis + 1015 + x_ad, head_y + 20, x_axis + 1015 + x_ad, head_y - 15)  # 14

    # mycanvas.line(x_axis + 1080, head_y + 20, x_axis + 1080, head_y - 15)  # 15




    # mycanvas.setFont('Helvetica', 14)
    # mycanvas.drawCentredString(520, y_axis + 30, "A B S T R A C T")
    mycanvas.setFont('Helvetica', 8)
    mycanvas.line(x_axis - 10, y_axis + 20, x_axis + 1030, y_axis + 20)

    fcm = 0
    fcm_amt = 0
    tea = 0
    tea_amt = 0
    std = 0
    std_amt = 0
    tm = 0
    tm_amt = 0
    tot_qty = 0
    tot_amt = 0
    btmlk = 0
    btmlk_amt = 0
    curd = 0
    curd_amt = 0

    main_name = ""
    for data in data_dict:
        if data == "20258":
            main_name = data + " UNION PARLOUR"
        if data == "20234":
            main_name = data + " S.DR. UNION STAFF"
        if data == "20233":
            main_name = data + " S.DR. OTHER UNION"
        if data == "20201":
            main_name = data + " S.DR. (GOVT. INSTITUTION)"
        if data == "10961":
            main_name = data + " MILK SUPPLY(PVT. INSTITUTION)"
        if data == "10901":
            main_name = data + " MILK SALES"
        if data == "20238":
            main_name = data + " SOCIETY"

        for value in data_dict[data]:
            if data != "20258":
                if value == str(data) + " Sub Total":
                    sub_total = value
                    mycanvas.drawString(x_axis - 5, y_axis, main_name[:30])
                    mycanvas.drawRightString(x_axis + 230 + x_ad - 25, y_axis,
                                             str(data_dict[data][sub_total]["sub_fcm_ltr"]))
                    mycanvas.drawRightString(x_axis + 290 + x_ad - 15, y_axis,
                                             str(data_dict[data][sub_total]["sub_fcm_amt"]))
                    mycanvas.drawRightString(x_axis + 355 + x_ad - 15, y_axis,
                                             str(data_dict[data][sub_total]["sub_std_ltr"]))
                    mycanvas.drawRightString(x_axis + 420 + x_ad - 10, y_axis,
                                             str(data_dict[data][sub_total]["sub_std_amt"]))
                    mycanvas.drawRightString(x_axis + 480 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tm_ltr"]))
                    mycanvas.drawRightString(x_axis + 550 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tm_amt"]))
                    mycanvas.drawRightString(x_axis + 630 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tea_ltr"]))
                    mycanvas.drawRightString(x_axis + 690 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tea_amt"]))
                    mycanvas.drawRightString(x_axis + 755 + x_ad, y_axis,
                                             str(data_dict[data][sub_total]["sub_mlk_qty"]))
                    mycanvas.drawRightString(x_axis + 830 + x_ad, y_axis,
                                             str(data_dict[data][sub_total]["sub_mlk_amt"]))
                    mycanvas.drawRightString(x_axis + 890 + x_ad, y_axis, str(data_dict[data][sub_total]["btmlk_ltr"]))
                    mycanvas.drawRightString(x_axis + 945 + x_ad, y_axis, str(data_dict[data][sub_total]["btmlk_amt"]))
                    mycanvas.drawRightString(x_axis + 1000 + x_ad, y_axis, str(data_dict[data][sub_total]["curd_kgs"]))
                    mycanvas.drawRightString(x_axis + 140 + x_ad, y_axis, str(data_dict[data][sub_total]["curd_amt"]))

                    fcm += data_dict[data][sub_total]["sub_fcm_ltr"]
                    fcm_amt += data_dict[data][sub_total]["sub_fcm_amt"]
                    std += data_dict[data][sub_total]["sub_std_ltr"]
                    std_amt += data_dict[data][sub_total]["sub_std_amt"]
                    tm += data_dict[data][sub_total]["sub_tm_ltr"]
                    tm_amt += data_dict[data][sub_total]["sub_tm_amt"]
                    tea += data_dict[data][sub_total]["sub_tea_ltr"]
                    tea_amt += data_dict[data][sub_total]["sub_tea_amt"]
                    tot_qty += data_dict[data][sub_total]["sub_mlk_qty"]
                    tot_amt += data_dict[data][sub_total]["sub_mlk_amt"]
                    btmlk += data_dict[data][sub_total]["btmlk_ltr"]
                    btmlk_amt += data_dict[data][sub_total]["btmlk_amt"]
                    curd += data_dict[data][sub_total]["curd_kgs"]
                    curd_amt += data_dict[data][sub_total]["curd_amt"]

                    # lines
                    mycanvas.line(x_axis - 10, y_axis + 20, x_axis - 10, y_axis - 10)  # 1
                    #         mycanvas.line(x_axis+35,y_axis+20,x_axis+35,y_axis-10) #2
                    # mycanvas.line(x_axis + 100 + x_ad, y_axis + 20, x_axis + 100 + x_ad, y_axis - 10)  # 3
                    # mycanvas.line(x_axis + 205 + x_ad - 25, y_axis + 20, x_axis + 205 + x_ad - 25, y_axis - 10)  # 4
                    mycanvas.line(x_axis +255 + x_ad - 15, y_axis + 20, x_axis + 255 + x_ad - 15, y_axis - 10)  # 5
                    mycanvas.line(x_axis + 320 + x_ad - 15, y_axis + 20, x_axis + 320 + x_ad - 15, y_axis - 10)  # 6
                    mycanvas.line(x_axis + 385 + x_ad - 10, y_axis + 20, x_axis + 385 + x_ad - 10, y_axis - 10)  # 7
                    mycanvas.line(x_axis + 450 + x_ad, y_axis + 20, x_axis + 450 + x_ad, y_axis - 10)  # 8
                    mycanvas.line(x_axis + 515 + x_ad, y_axis + 20, x_axis + 515 + x_ad, y_axis - 10)  # 9
                    mycanvas.line(x_axis + 595 + x_ad, y_axis + 20, x_axis + 595 + x_ad, y_axis - 10)  # 10
                    # mycanvas.line(x_axis + 700 + x_ad, y_axis + 20, x_axis + 700 + x_ad, y_axis - 10)  # 11
                    mycanvas.line(x_axis + 655 + x_ad, y_axis + 20, x_axis + 655 + x_ad, y_axis - 10)  # 12
                    mycanvas.line(x_axis + 725 + x_ad, y_axis + 20, x_axis + 725 + x_ad, y_axis - 10)  # 10
                    
                    mycanvas.line(x_axis + 795 + x_ad, y_axis + 20, x_axis + 795 + x_ad, y_axis - 10)  # 13
                    mycanvas.line(x_axis + 855 + x_ad, y_axis + 20, x_axis + 855 + x_ad, y_axis - 10)  # 14
                    mycanvas.line(x_axis + 915 + x_ad, y_axis + 20, x_axis + 915 + x_ad, y_axis - 10)  # 13
                    mycanvas.line(x_axis + 975 + x_ad, y_axis + 20, x_axis + 975 + x_ad, y_axis - 10)  # 14
                    mycanvas.line(x_axis + 1030, y_axis + 20, x_axis + 1030, y_axis - 10)  # 15

                    y_axis -= 15
    y_axis -= 15
    mycanvas.line(x_axis - 10, y_axis + 20, x_axis + 1030, y_axis + 20)
    mycanvas.line(x_axis - 10, y_axis - 10, x_axis + 1030, y_axis - 10)

    # lines
    mycanvas.line(x_axis - 10, y_axis + 20, x_axis - 10, y_axis - 10)  # 1
    #         mycanvas.line(x_axis+35,y_axis+20,x_axis+35,y_axis-10) #2
    mycanvas.line(x_axis + 100 + x_ad, y_axis + 20, x_axis + 100 + x_ad, y_axis - 10)  # 3
    mycanvas.line(x_axis + 193 + x_ad - 25, y_axis + 20, x_axis + 193 + x_ad - 25, y_axis - 10)  # 4
    mycanvas.line(x_axis + 255 + x_ad - 15, y_axis + 20, x_axis + 255 + x_ad - 15, y_axis - 10)  # 5
    mycanvas.line(x_axis + 320 + x_ad - 15, y_axis + 20, x_axis + 320 + x_ad - 15, y_axis - 10)  # 6
    mycanvas.line(x_axis + 385 + x_ad - 10, y_axis + 20, x_axis + 385 + x_ad - 10, y_axis - 10)  # 7
    mycanvas.line(x_axis + 450 + x_ad, y_axis + 20, x_axis + 450 + x_ad, y_axis - 10)  # 8
    mycanvas.line(x_axis + 515 + x_ad, y_axis + 20, x_axis + 515 + x_ad, y_axis - 10)  # 9
    mycanvas.line(x_axis + 595 + x_ad, y_axis + 20, x_axis + 595 + x_ad, y_axis - 10)  # 10
    mycanvas.line(x_axis + 725 + x_ad, y_axis + 20, x_axis + 725 + x_ad, y_axis - 10)  # 11
    mycanvas.line(x_axis + 655 + x_ad, y_axis + 20, x_axis + 655 + x_ad, y_axis - 10)  # 12
    mycanvas.line(x_axis + 795 + x_ad, y_axis + 20, x_axis + 795 + x_ad, y_axis - 10)  # 13
    mycanvas.line(x_axis + 855 + x_ad, y_axis + 20, x_axis + 855 + x_ad, y_axis - 10)  # 14
    mycanvas.line(x_axis + 915 + x_ad, y_axis + 20, x_axis + 915 + x_ad, y_axis - 10)  # 13
    mycanvas.line(x_axis + 975 + x_ad, y_axis + 20, x_axis + 975 + x_ad, y_axis - 10)  # 14
    mycanvas.line(x_axis + 1030, y_axis + 20, x_axis + 1030, y_axis - 10)  # 15

    # sub total

    mycanvas.drawString(x_axis - 5, y_axis, " S U B  T O T A L ")
    mycanvas.drawRightString(x_axis + 160 + x_ad - 25, y_axis, str(fcm))
    mycanvas.drawRightString(x_axis + 220 + x_ad - 15, y_axis, str(fcm_amt))
    mycanvas.drawRightString(x_axis + 290 + x_ad - 15, y_axis, str(std))
    mycanvas.drawRightString(x_axis + 350 + x_ad - 10, y_axis, str(std_amt))
    mycanvas.drawRightString(x_axis + 420 + x_ad, y_axis, str(tm))
    mycanvas.drawRightString(x_axis + 550 + x_ad, y_axis, str(tm_amt))
    mycanvas.drawRightString(x_axis + 630 + x_ad, y_axis, str(tea))
    mycanvas.drawRightString(x_axis + 700 + x_ad, y_axis, str(tea_amt))
    mycanvas.drawRightString(x_axis + 765 + x_ad, y_axis, str(tot_qty))
    mycanvas.drawRightString(x_axis + 820 + x_ad, y_axis, str(tot_amt))
    mycanvas.drawRightString(x_axis + 930 + x_ad, y_axis, str(btmlk))
    mycanvas.drawRightString(x_axis + 890 + x_ad, y_axis, str(btmlk_amt))
    mycanvas.drawRightString(x_axis + 1020 + x_ad, y_axis, str(curd))
    mycanvas.drawRightString(x_axis + 480 + x_ad, y_axis, str(curd_amt))

    # grdand total
    y_axis -= 70
    mycanvas.line(x_axis - 10, y_axis + 20, x_axis + 1030, y_axis + 20)
    main_name = ""
    for data in data_dict:
        if data == "20258":
            main_name = data + " UNION PARLOUR"
        if data == "20234":
            main_name = data + " S.DR. UNION STAFF"
        if data == "20233":
            main_name = data + " S.DR. OTHER UNION"
        if data == "20201":
            main_name = data + " S.DR. (GOVT. INSTITUTION)"
        if data == "10961":
            main_name = data + " MILK SUPPLY(PVT. INSTITUTION)"
        if data == "10901":
            main_name = data + " MILK SALES"
        if data == "20238":
            main_name = data + " SOCIETY"

        for value in data_dict[data]:
            if data == "20258":
                if value == str(data) + " Sub Total":
                    sub_total = value
                    mycanvas.drawString(x_axis - 5, y_axis, main_name[:28])
                    mycanvas.drawRightString(x_axis + 160 + x_ad - 25, y_axis,
                                             str(data_dict[data][sub_total]["sub_fcm_ltr"]))
                    mycanvas.drawRightString(x_axis + 220 + x_ad - 15, y_axis,
                                             str(data_dict[data][sub_total]["sub_fcm_amt"]))
                    mycanvas.drawRightString(x_axis + 288 + x_ad - 15, y_axis,
                                             str(data_dict[data][sub_total]["sub_std_ltr"]))
                    mycanvas.drawRightString(x_axis + 350 + x_ad - 10, y_axis,
                                             str(data_dict[data][sub_total]["sub_std_amt"]))
                    mycanvas.drawRightString(x_axis + 415 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tm_ltr"]))
                    mycanvas.drawRightString(x_axis + 480 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tm_amt"]))
                    mycanvas.drawRightString(x_axis + 550 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tea_ltr"]))
                    mycanvas.drawRightString(x_axis + 630 + x_ad, y_axis, str(data_dict[data][sub_total]["sub_tea_amt"]))
                    mycanvas.drawRightString(x_axis + 700 + x_ad, y_axis,
                                             str(data_dict[data][sub_total]["sub_mlk_qty"]))
                    mycanvas.drawRightString(x_axis + 760 + x_ad, y_axis,
                                             str(data_dict[data][sub_total]["sub_mlk_amt"]))
                    mycanvas.drawRightString(x_axis + 830 + x_ad, y_axis, str(data_dict[data][sub_total]["btmlk_ltr"]))
                    mycanvas.drawRightString(x_axis + 890 + x_ad, y_axis, str(data_dict[data][sub_total]["btmlk_amt"]))
                    mycanvas.drawRightString(x_axis + 950 + x_ad, y_axis, str(data_dict[data][sub_total]["curd_kgs"]))
                    mycanvas.drawRightString(x_axis + 1010 + x_ad, y_axis, str(data_dict[data][sub_total]["curd_amt"]))

                    fcm += data_dict[data][sub_total]["sub_fcm_ltr"]
                    fcm_amt += data_dict[data][sub_total]["sub_fcm_amt"]
                    std += data_dict[data][sub_total]["sub_std_ltr"]
                    std_amt += data_dict[data][sub_total]["sub_std_amt"]
                    tm += data_dict[data][sub_total]["sub_tm_ltr"]
                    tm_amt += data_dict[data][sub_total]["sub_tm_amt"]
                    tea += data_dict[data][sub_total]["sub_tea_ltr"]
                    tea_amt += data_dict[data][sub_total]["sub_tea_amt"]
                    tot_qty += data_dict[data][sub_total]["sub_mlk_qty"]
                    tot_amt += data_dict[data][sub_total]["sub_mlk_amt"]
                    btmlk += data_dict[data][sub_total]["btmlk_ltr"]
                    btmlk_amt += data_dict[data][sub_total]["btmlk_amt"]
                    curd += data_dict[data][sub_total]["curd_kgs"]
                    curd_amt += data_dict[data][sub_total]["curd_amt"]

                    # lines
                    mycanvas.line(x_axis - 10, y_axis + 20, x_axis - 10, y_axis - 10)  # 1
                    #         mycanvas.line(x_axis+35,y_axis+20,x_axis+35,y_axis-10) #2
                    mycanvas.line(x_axis + 100 + x_ad, y_axis + 20, x_axis + 100 + x_ad, y_axis - 10)  # 3
                    mycanvas.line(x_axis + 195 + x_ad - 25, y_axis + 20, x_axis + 195 + x_ad - 25, y_axis - 10)  # 4
                    mycanvas.line(x_axis + 255 + x_ad - 15, y_axis + 20, x_axis + 255 + x_ad - 15, y_axis - 10)  # 5
                    mycanvas.line(x_axis + 320 + x_ad - 15, y_axis + 20, x_axis + 320 + x_ad - 15, y_axis - 10)  # 6
                    mycanvas.line(x_axis + 385 + x_ad - 10, y_axis + 20, x_axis + 385 + x_ad - 10, y_axis - 10)  # 7
                    mycanvas.line(x_axis + 445 + x_ad, y_axis + 20, x_axis + 445 + x_ad, y_axis - 10)  # 8
                    mycanvas.line(x_axis + 515 + x_ad, y_axis + 20, x_axis + 515 + x_ad, y_axis - 10)  # 9
                    mycanvas.line(x_axis + 595 + x_ad, y_axis + 20, x_axis + 595 + x_ad, y_axis - 10)  # 10
                    mycanvas.line(x_axis + 655 + x_ad, y_axis + 20, x_axis + 655 + x_ad, y_axis - 10)  # 11
                    mycanvas.line(x_axis + 725 + x_ad, y_axis + 20, x_axis + 725 + x_ad, y_axis - 10)  # 12
                    mycanvas.line(x_axis + 795 + x_ad, y_axis + 20, x_axis + 795 + x_ad, y_axis - 10)  # 13
                    mycanvas.line(x_axis + 855 + x_ad, y_axis + 20, x_axis + 855 + x_ad, y_axis - 10)  # 14
                    mycanvas.line(x_axis + 915 + x_ad, y_axis + 20, x_axis + 915 + x_ad, y_axis - 10)  # 13
                    mycanvas.line(x_axis + 975 + x_ad, y_axis + 20, x_axis + 975 + x_ad, y_axis - 10)  # 14
                    mycanvas.line(x_axis + 1030, y_axis + 20, x_axis + 1030, y_axis - 10)  # 15

                    y_axis -= 15
    y_axis -= 15

    mycanvas.line(x_axis - 10, y_axis + 20, x_axis + 1030, y_axis + 20)
    mycanvas.line(x_axis - 10, y_axis - 10, x_axis + 1030, y_axis - 10)

    # lines
    mycanvas.line(x_axis - 10, y_axis + 20, x_axis - 10, y_axis - 10)  # 1
    #         mycanvas.line(x_axis+35,y_axis+20,x_axis+35,y_axis-10) #2
    mycanvas.line(x_axis + 100 + x_ad, y_axis + 20, x_axis + 100 + x_ad, y_axis - 10)  # 3
    mycanvas.line(x_axis + 195 + x_ad - 25, y_axis + 20, x_axis + 195 + x_ad - 25, y_axis - 10)  # 4
    mycanvas.line(x_axis + 255 + x_ad - 15, y_axis + 20, x_axis + 255 + x_ad - 15, y_axis - 10)  # 5
    mycanvas.line(x_axis + 320 + x_ad - 15, y_axis + 20, x_axis + 320 + x_ad - 15, y_axis - 10)  # 6
    mycanvas.line(x_axis + 385 + x_ad - 10, y_axis + 20, x_axis + 385 + x_ad - 10, y_axis - 10)  # 7
    mycanvas.line(x_axis + 445 + x_ad, y_axis + 20, x_axis + 445 + x_ad, y_axis - 10)  # 8
    mycanvas.line(x_axis + 515 + x_ad, y_axis + 20, x_axis + 515 + x_ad, y_axis - 10)  # 9
    mycanvas.line(x_axis + 595 + x_ad, y_axis + 20, x_axis + 595 + x_ad, y_axis - 10)  # 10
    mycanvas.line(x_axis + 655 + x_ad, y_axis + 20, x_axis + 655 + x_ad, y_axis - 10)  # 11
    mycanvas.line(x_axis + 725 + x_ad, y_axis + 20, x_axis + 725 + x_ad, y_axis - 10)  # 12
    mycanvas.line(x_axis + 793 + x_ad, y_axis + 20, x_axis + 793 + x_ad, y_axis - 10)  # 13
    mycanvas.line(x_axis + 853 + x_ad, y_axis + 20, x_axis + 853 + x_ad, y_axis - 10)  # 14
    mycanvas.line(x_axis + 915 + x_ad, y_axis + 20, x_axis + 915 + x_ad, y_axis - 10)  # 13
    mycanvas.line(x_axis + 975 + x_ad, y_axis + 20, x_axis + 975 + x_ad, y_axis - 10)  # 14
    mycanvas.line(x_axis + 1030, y_axis + 20, x_axis + 1030, y_axis - 10)  # 15

    # grand total

    mycanvas.drawString(x_axis - 5, y_axis, " G R A N D  T O T A L ")
    mycanvas.drawRightString(x_axis + 160 + x_ad - 25, y_axis, str(fcm))
    mycanvas.drawRightString(x_axis + 220 + x_ad - 15, y_axis, str(fcm_amt))
    mycanvas.drawRightString(x_axis + 290 + x_ad - 15, y_axis, str(std))
    mycanvas.drawRightString(x_axis + 350 + x_ad - 10, y_axis, str(std_amt))
    mycanvas.drawRightString(x_axis + 415 + x_ad, y_axis, str(tm))
    mycanvas.drawRightString(x_axis + 480 + x_ad, y_axis, str(tm_amt))
    mycanvas.drawRightString(x_axis + 550 + x_ad, y_axis, str(tm))
    mycanvas.drawRightString(x_axis + 630 + x_ad, y_axis, str(tm_amt))
    mycanvas.drawRightString(x_axis + 700 + x_ad, y_axis, str(tot_qty))
    mycanvas.drawRightString(x_axis + 760 + x_ad, y_axis, str(tot_amt))
    mycanvas.drawRightString(x_axis + 830 + x_ad, y_axis, str(btmlk))
    mycanvas.drawRightString(x_axis + 890 + x_ad, y_axis, str(btmlk_amt))
    mycanvas.drawRightString(x_axis + 950 + x_ad, y_axis, str(curd))
    mycanvas.drawRightString(x_axis + 1010 + x_ad, y_axis, str(curd_amt))
    mycanvas.save()
    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document


@api_view(['POST'])
def serve_institution_bill_as_dbf(request): 
    print(request.data)
    data_dict = {}
    month = request.data['selected_month'] # input month
    year = request.data['selected_year'] # input year
    product = request.data['selected_product'] # input products ----> 1.milk..2.curd..3.butter milk
   
    product = product.lower()
    if product == "milk":
        product_type_code = "01300420"
    elif product == "curd":
        product_type_code = "0130041"
    else:
        product_type_code = "0130040"
    days = monthrange(year,month)
    datetime_object = datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%B")

    product_detail = product.upper() + " SUPPLIED - "+str(month_name)+" - "+str(year)

    business_ids = list(DailySessionllyBusinessllySale.objects.filter(delivery_date__month=month, delivery_date__year=year, sold_to='Agent').values_list("business_id",flat=True).exclude(union__in=["TIRUPPUR Union","NILGIRIS Union"]).exclude(business__business_type_id__in=[1,2,9,12]))
    business_ids = list(set(business_ids))
   
    other_union_business_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__month=month, delivery_date__year=year, sold_to='Agent',union__in=["TIRUPPUR Union","NILGIRIS Union"]).exclude(business__business_type_id__in=[1,2,9,12])
   
    # prp_business_ids = list(BusinessAgentMap.objects.filter(agent__agent_code__in=["33390","9031WSD", "2135"]).values_list("business_id",flat=True))
   
    # print(prp_business_ids)
   
    prp_business_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__month=month, delivery_date__year=year, sold_to='Agent',business__code__in=['2682', '9031', '5524'])
    day = str(days[1])+"/"+str(month)+"/"+str(year)

    for business in business_ids:
        if business == None:
            continue
           
        code = ''
        if Business.objects.get(id=business).code in ["1999","2000"]:
            finance_code = str(20234)
            code = BusinessAgentMap.objects.get(business_id=business).business.code
        else:
            finance_code = Business.objects.get(id=business).business_type.finance_main_code
            if finance_code == str(20233):
                if len(str(Business.objects.get(id=business).code)) < 5:
                    code = "7"+str(BusinessAgentMap.objects.get(business_id=business).agent.agent_code)
                elif len(str(Business.objects.get(id=business).code)) > 5:
                    code = str(BusinessAgentMap.objects.get(business_id=business).agent.agent_code)[1:]
                else:
                     code = str(BusinessAgentMap.objects.get(business_id=business).agent.agent_code)
            elif finance_code == str(10901):
                if len(str(Business.objects.get(id=business).code)) < 5:
                    code = "3"+str(BusinessAgentMap.objects.get(business_id=business).agent.agent_code)
                elif len(str(Business.objects.get(id=business).code)) > 5:
                    code = str(BusinessAgentMap.objects.get(business_id=business).agent.agent_code)[1:]
                else:
                     code = str(BusinessAgentMap.objects.get(business_id=business).agent.agent_code)
            elif finance_code in ["20258","20201","10961"]:
                if len(str(Business.objects.get(id=business).code)) < 5:
                    code = "5"+str(Business.objects.get(id=business).code)
                elif len(str(Business.objects.get(id=business).code)) > 5:
                    code = str(Business.objects.get(id=business).code)[1:]
                else:
                     code = str(Business.objects.get(id=business).code)
            else:
                code = str(Business.objects.get(id=business).code)
        milk_total = 0
        data_dict[business] = {
            "GT_DATE": datetime.strptime(day,'%d/%m/%Y'),
            "GT_ACODE": '',
            "GT_MCODE": '',
            "GT_DETL": product_detail,
            "GT_RP": "P",
            "GT_CA": "A",
            "GT_AMT" : 0,
            "GT_REFR" : 50,
            "GT_CQNO": '',
            "GT_LF": '',
            "GT_POST": '',
           
        }
               
        data_dict[business]["GT_MCODE"] = finance_code
        data_dict[business]["GT_ACODE"] = code
        sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__month=month,delivery_date__year=year,business_id=business, sold_to='Agent')
       
        if product == "milk":
            milk_total = sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum'] + \
                        sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"] + \
                        sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"] + \
                        sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + \
                        sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"] + \
                        sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + \
                        sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]
           
        elif product == "curd":
            milk_total = sale_obj.aggregate(Sum('curd500_cost'))['curd500_cost__sum'] + \
                        sale_obj.aggregate(Sum('curd150_cost'))['curd150_cost__sum'] + \
                        sale_obj.aggregate(Sum('cupcurd_cost'))['cupcurd_cost__sum'] +\
                        sale_obj.aggregate(Sum('curd5000_cost'))['curd5000_cost__sum']    
        elif product == "butter milk":
                milk_total += sale_obj.aggregate(Sum('buttermilk200_cost'))['buttermilk200_cost__sum']
               
        data_dict[business]["GT_AMT"] = round(milk_total)
       
    #----------------other union------------
   
    for sale in other_union_business_obj:
        if sale.union == "TIRUPPUR Union":
            if product == "milk":
                continue
            else:
                business = BusinessAgentMap.objects.get(business__code=6005).agent.agent_code
            # print(business)
        elif sale.union == "NILGIRIS Union":
            business = BusinessAgentMap.objects.get(business__code=6010).agent.agent_code
        if not business in data_dict:
            data_dict[business] = {
                "GT_DATE": datetime.strptime(day,'%d/%m/%Y'),
                "GT_ACODE": "7"+str(business),
                "GT_MCODE": str(20233),
                "GT_DETL": product_detail,
                "GT_RP": "P",
                "GT_CA": "A",
                "GT_AMT" : 0,
                "GT_REFR" : 50,
                "GT_CQNO": '',
                "GT_LF": '',
                "GT_POST": '',

            }
        if product == "milk":
            if sale.union != "TIRUPPUR Union":
            #      milk_total = 0
            # else:
                milk_total = sale.tm500_cost + sale.std250_cost +sale.std500_cost + sale.fcm500_cost + sale.fcm1000_cost
           
        elif product == "curd":
            milk_total = sale.curd500_cost + sale.curd5000_cost + sale.curd150_cost + sale.cupcurd_cost
        elif product == "butter milk":
                milk_total = sale.buttermilk200_cost
               
        data_dict[business]["GT_AMT"] += round(milk_total)
       
    #-----------------PRP--------------------
    for sale in prp_business_obj:
        if not sale.business_id in data_dict:
            data_dict[sale.business_id] = {
                "GT_DATE": datetime.strptime(day,'%d/%m/%Y'),
                "GT_ACODE": str(BusinessAgentMap.objects.get(business_id=sale.business_id).agent.agent_code),
                "GT_MCODE": str(10901),
                "GT_DETL": product_detail,
                "GT_RP": "P",
                "GT_CA": "A",
                "GT_AMT" : 0,
                "GT_REFR" : 50,
                "GT_CQNO": '',
                "GT_LF": '',
                "GT_POST": '',

            }
        if product == "milk":
            if sale.union != "TIRUPPUR Union":
                milk_total = sale.tm500_cost + sale.std250_cost +sale.std500_cost + sale.fcm500_cost + sale.fcm1000_cost
        elif product == "curd":
            milk_total = sale.curd500_cost + sale.curd5000_cost + sale.curd150_cost + sale.cupcurd_cost
        elif product == "butter milk":
            milk_total = sale.buttermilk200_cost
               
        data_dict[sale.business_id]["GT_AMT"] += round(milk_total)


    file_name = product_type_code+".dbf"
    dbf_file_path = os.path.join('static/media/zone_wise_report/', file_name)

    table = dbf.Table(dbf_file_path,'GT_DATE D; GT_ACODE C(100); GT_MCODE C(100); GT_DETL C(100); GT_RP C(1); GT_CA C(1); GT_AMT N(19,2); GT_REFR N(7,0); GT_CQNO C(7); GT_LF C(5); GT_POST C(2)')

    # print('db definition created with field names:', table.field_names)

    table = table.open(dbf.READ_WRITE)

    for datas in data_dict:
        field_list = []
        if data_dict[datas]["GT_AMT"] == 0:
            continue
        for data in data_dict[datas]:
            field_list.append(data_dict[datas][data])
            # print(data_dict[datas][data])
        field_list = tuple(field_list)
        table.append(field_list)


    document = {}
    document['file_name'] = file_name
    try:
      image_path = dbf_file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['dbf'] = encoded_image
    except Exception as err:
        print(err)

    return Response(data=document, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_monthly_dairy_summary_as_report_three(request):
    month = request.data['selected_month'] # input month
    year = request.data['selected_year'] # input year
    num_days = calendar.monthrange(year, month)[1]
    # date_list = [(str(year)+'-'+ str(month) +'-' +str(day)) for day in range(1, num_days+1)]
    date_list = list(set(list(DailySessionllyBusinessllySale.objects.filter(delivery_date__month=month, delivery_date__year=year).order_by('delivery_date').values_list('delivery_date', flat=True))))
    print(date_list)
    date_list = sorted(date_list)
    print(date_list)
    data_dict = {}
    for date in date_list:
        dates = str(date)[:10]
        if not dates in data_dict:
            data_dict[dates] = {
                "product":{
                    "tm":{
                        "Resived From Diary": 0,
                        "Leakage" : 0,
                        "Returned" : 0,
                        "Net Recived" : 0
                    },
                    "std500":{
                        "Resived From Diary": 0,
                        "Leakage" : 0,
                        "Returned" : 0,
                        "Net Recived" : 0
                    },
                    "std250":{
                        "Resived From Diary": 0,
                        "Leakage" : 0,
                        "Returned" : 0,
                        "Net Recived" : 0
                    },
                    "fcm":{
                        "Resived From Diary": 0,
                        "Leakage" : 0,
                        "Returned" : 0,
                        "Net Recived" : 0
                    },
                    "tmate":{
                        "Resived From Diary": 0,
                        "Leakage" : 0,
                        "Returned" : 0,
                        "Net Recived" : 0
                    },
                    "smcan":{
                        "Resived From Diary": 0,
                        "Leakage" : 0,
                        "Returned" : 0,
                        "Net Recived" : 0
                    },
                    "fcmcan":{
                        "Resived From Diary": 0,
                        "Leakage" : 0,
                        "Returned" : 0,
                        "Net Recived" : 0
                    },
                },
                "union_sale" : {},
                "Coimbatore Account" : {
                    "Agent Cash":{
                        "tm" : 0,
                        "std500" : 0,
                        "std250" : 0,
                        "fcm" : 0,
                        "tmate" : 0,
                        "smcan" : 0,
                        "fcmcan" : 0
                    },
                    "Agent Card" : {
                        "tm" : 0,
                        "std500" : 0,
                        "std250" : 0,
                        "fcm" : 0,
                        "tmate" : 0,
                        "smcan" : 0,
                        "fcmcan" : 0
                    },
                    "Union Booth Cash" : {
                        "tm" : 0,
                        "std500" : 0,
                        "std250" : 0,
                        "fcm" : 0,
                        "tmate" : 0,
                        "smcan" : 0,
                        "fcmcan" : 0

                    },
                    "Union Booth Card" : {
                        "tm" : 0,
                        "std500" : 0,
                        "std250" : 0,
                        "fcm" : 0,
                        "tmate" : 0,
                        "smcan" : 0,
                        "fcmcan" : 0
                    },
                    "Pvt Institutes" : {
                        "tm" : 0,
                        "std500" : 0,
                        "std250" : 0,
                        "fcm" : 0,
                        "tmate" : 0,
                        "smcan" : 0,
                        "fcmcan" : 0
                    },
                    "Govt Institutes" : {
                        "tm" : 0,
                        "std500" : 0,
                        "std250" : 0,
                        "fcm" : 0,
                        "tmate" : 0,
                        "smcan" : 0,
                        "fcmcan" : 0
                    },
                    "Society" : {
                        "tm" : 0,
                        "std500" : 0,
                        "std250" : 0,
                        "fcm" : 0,
                        "tmate" : 0,
                        "smcan" : 0,
                        "fcmcan" : 0
                    }
                },
                "Costs" : {
                    "product":{
                        "tm":{
                            "Resived From Diary": 0,
                            "Leakage" : 0,
                            "Returned" : 0,
                            "Net Recived" : 0
                        },
                        "std500":{
                            "Resived From Diary": 0,
                            "Leakage" : 0,
                            "Returned" : 0,
                            "Net Recived" : 0
                        },
                        "std250":{
                            "Resived From Diary": 0,
                            "Leakage" : 0,
                            "Returned" : 0,
                            "Net Recived" : 0
                        },
                        "fcm":{
                            "Resived From Diary": 0,
                            "Leakage" : 0,
                            "Returned" : 0,
                            "Net Recived" : 0
                        },
                        "tmate":{
                            "Resived From Diary": 0,
                            "Leakage" : 0,
                            "Returned" : 0,
                            "Net Recived" : 0
                        },
                        "smcan":{
                            "Resived From Diary": 0,
                            "Leakage" : 0,
                            "Returned" : 0,
                            "Net Recived" : 0
                        },
                        "fcmcan":{
                            "Resived From Diary": 0,
                            "Leakage" : 0,
                            "Returned" : 0,
                            "Net Recived" : 0
                        },
                    },
                    "union_sale" : {},
                    "Coimbatore Account" : {
                        "Agent Cash":{
                            "tm" : 0,
                            "std500" : 0,
                            "std250" : 0,
                            "fcm" : 0,
                            "tmate" : 0
                        },
                        "Agent Card" : {
                            "tm" : 0,
                            "std500" : 0,
                            "std250" : 0,
                            "fcm" : 0,
                            "tmate" : 0,
                            "smcan" : 0,
                            "fcmcan" : 0
                        },
                        "Union Booth Cash" : {
                            "tm" : 0,
                            "std500" : 0,
                            "std250" : 0,
                            "fcm" : 0,
                            "tmate" : 0,
                            "smcan" : 0,
                            "fcmcan" : 0
                        },
                        "Union Booth Card" : {
                            "tm" : 0,
                            "std500" : 0,
                            "std250" : 0,
                            "fcm" : 0,
                            "tmate" : 0,
                            "smcan" : 0,
                            "fcmcan" : 0
                        },
                        "Pvt Institutes" : {
                            "tm" : 0,
                            "std500" : 0,
                            "std250" : 0,
                            "fcm" : 0,
                            "tmate" : 0,
                            "smcan" : 0,
                            "fcmcan" : 0
                        },
                        "Govt Institutes" : {
                            "tm" : 0,
                            "std500" : 0,
                            "std250" : 0,
                            "fcm" : 0,
                            "tmate" : 0,
                            "smcan" : 0,
                            "fcmcan" : 0
                        },
                        "Society" : {
                            "tm" : 0,
                            "std500" : 0,
                            "std250" : 0,
                            "fcm" : 0,
                            "tmate" : 0,
                            "smcan" : 0,
                            "fcmcan" : 0
                        }
                    }
                }
            }
            
        tm_std_fcm_diary_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date)
        tm_std_fcm_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,sold_to__in = ["Agent","ICustomer"])
        tm_std_fcm_leake_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,sold_to="Leakage")

        #dairy sale (icus + agent + leakage)
        tm_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        std500_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        std250_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        fcm_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        tea_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_diary_sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]
        smcan_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"]
        fcmcan_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"]

        data_dict[dates]["product"]["tm"]["Resived From Diary"] = tm_sale
        data_dict[dates]["product"]["std500"]["Resived From Diary"] = std500_sale
        data_dict[dates]["product"]["std250"]["Resived From Diary"] = std250_sale
        data_dict[dates]["product"]["fcm"]["Resived From Diary"] = fcm_sale
        data_dict[dates]["product"]["tmate"]["Resived From Diary"] = tea_sale
        data_dict[dates]["product"]["smcan"]["Resived From Diary"] = smcan_sale
        data_dict[dates]["product"]["fcmcan"]["Resived From Diary"] = fcmcan_sale
        
        

        #net_recived (icus + agent)
        tm_sale = tm_std_fcm_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        std500_sale = tm_std_fcm_sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        std250_sale = tm_std_fcm_sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        fcm_sale = tm_std_fcm_sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        tea_sale = tm_std_fcm_sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]
        smcan_sale = tm_std_fcm_sale_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"]
        fcmcan_sale = tm_std_fcm_sale_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"]

        data_dict[dates]["product"]["tm"]["Net Recived"] = tm_sale
        data_dict[dates]["product"]["std500"]["Net Recived"] = std500_sale
        data_dict[dates]["product"]["std250"]["Net Recived"] = std250_sale
        data_dict[dates]["product"]["fcm"]["Net Recived"] = fcm_sale
        data_dict[dates]["product"]["tmate"]["Net Recived"] = tea_sale
        data_dict[dates]["product"]["smcan"]["Net Recived"] = smcan_sale
        data_dict[dates]["product"]["fcmcan"]["Net Recived"] = fcmcan_sale

        #leakage
        lk_tm_sale = tm_std_fcm_leake_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        lk_std500_sale = tm_std_fcm_leake_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        lk_std250_sale = tm_std_fcm_leake_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        lk_fcm_sale = tm_std_fcm_leake_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_leake_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        lk_tea_sale = tm_std_fcm_leake_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_leake_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]


        data_dict[dates]["product"]["tm"]["Leakage"] = lk_tm_sale
        data_dict[dates]["product"]["std500"]["Leakage"] = lk_std500_sale
        data_dict[dates]["product"]["std250"]["Leakage"] = lk_std250_sale
        data_dict[dates]["product"]["fcm"]["Leakage"] = lk_fcm_sale
        data_dict[dates]["product"]["tmate"]["Leakage"] = lk_tea_sale

        union_list = ["COIMBATORE Union","NILGIRIS Union","TIRUPPUR Union","CHENNAI Aavin"]

        for union in union_list:
            if not union in data_dict[dates]["union_sale"]:
                data_dict[dates]["union_sale"][union] = {
                    "tm" : 0,
                    "std500" : 0,
                    "std250":0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "can" : 0
                }
            tm_std_fcm_union_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union=union,sold_to__in = ["Agent","ICustomer"])

            # union sale
            if tm_std_fcm_union_obj:
                union_tm_sale = tm_std_fcm_union_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
                union_std500_sale = tm_std_fcm_union_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
                union_std250_sale = tm_std_fcm_union_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
                union_fcm_sale = tm_std_fcm_union_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_union_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
                union_tea_sale = tm_std_fcm_union_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_union_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

                data_dict[dates]["union_sale"][union]["tm"] = union_tm_sale
                data_dict[dates]["union_sale"][union]["std500"] = union_std500_sale
                data_dict[dates]["union_sale"][union]["std250"] = union_std250_sale
                data_dict[dates]["union_sale"][union]["fcm"] = union_fcm_sale
                data_dict[dates]["union_sale"][union]["tmate"] = union_tea_sale

        #1.Agent + Pvt Parlour (cash)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[1,2,11])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]
        cbe_smcan_sale = tm_std_fcm_cbe_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"]
        cbe_fcmcan_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"]
        data_dict[dates]["Coimbatore Account"]["Agent Cash"]["tm"] = cbe_tm_sale
        data_dict[dates]["Coimbatore Account"]["Agent Cash"]["std500"] = cbe_std500_sale
        data_dict[dates]["Coimbatore Account"]["Agent Cash"]["std250"] = cbe_std250_sale
        data_dict[dates]["Coimbatore Account"]["Agent Cash"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Coimbatore Account"]["Agent Cash"]["tmate"] = cbe_tea_sale
        data_dict[dates]["Coimbatore Account"]["Agent Cash"]["smcan"] = cbe_smcan_sale
        data_dict[dates]["Coimbatore Account"]["Agent Cash"]["fcmcan"] = cbe_fcmcan_sale

        #2.Agent + Pvt Parlour (card)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[1,2])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

        data_dict[dates]["Coimbatore Account"]["Agent Card"]["tm"] = cbe_tm_sale
        data_dict[dates]["Coimbatore Account"]["Agent Card"]["std500"] = cbe_std500_sale
        data_dict[dates]["Coimbatore Account"]["Agent Card"]["std250"] = cbe_std250_sale
        data_dict[dates]["Coimbatore Account"]["Agent Card"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Coimbatore Account"]["Agent Card"]["tea"] = cbe_tea_sale

        #3.Ownparlour (cash)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[3,16])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

        data_dict[dates]["Coimbatore Account"]["Union Booth Cash"]["tm"] = cbe_tm_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Cash"]["std500"] = cbe_std500_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Cash"]["std250"] = cbe_std250_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Cash"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Cash"]["tmate"] = cbe_tea_sale

        #4.Ownparlour (card)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[3,16])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]


        data_dict[dates]["Coimbatore Account"]["Union Booth Card"]["tm"] = cbe_tm_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Card"]["std500"] = cbe_std500_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Card"]["std250"] = cbe_std250_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Card"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Coimbatore Account"]["Union Booth Card"]["tmate"] = cbe_tea_sale

        #5.Private ins
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[4, 15])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

        data_dict[dates]["Coimbatore Account"]["Pvt Institutes"]["tm"] = cbe_tm_sale
        data_dict[dates]["Coimbatore Account"]["Pvt Institutes"]["std500"] = cbe_std500_sale
        data_dict[dates]["Coimbatore Account"]["Pvt Institutes"]["std250"] = cbe_std250_sale
        data_dict[dates]["Coimbatore Account"]["Pvt Institutes"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Coimbatore Account"]["Pvt Institutes"]["tmate"] = cbe_tea_sale

        #6.Govt. ins
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[10,5])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]

        data_dict[dates]["Coimbatore Account"]["Govt Institutes"]["tm"] = cbe_tm_sale
        data_dict[dates]["Coimbatore Account"]["Govt Institutes"]["std500"] = cbe_std500_sale
        data_dict[dates]["Coimbatore Account"]["Govt Institutes"]["std250"] = cbe_std250_sale
        data_dict[dates]["Coimbatore Account"]["Govt Institutes"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Coimbatore Account"]["Govt Institutes"]["tmate"] = cbe_tea_sale

        # #6.Sosity
        # tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to__in = ["Agent"],business_type_id=10)

        # # union sale
        # cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
        # cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
        # cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
        # cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]

        # data_dict[dates]["Coimbatore Account"]["Society"]["tm"] = cbe_tm_sale
        # data_dict[dates]["Coimbatore Account"]["Society"]["std500"] = cbe_std500_sale
        # data_dict[dates]["Coimbatore Account"]["Society"]["std250"] = cbe_std250_sale
        # data_dict[dates]["Coimbatore Account"]["Society"]["fcm"] = cbe_fcm_sale


        #-----------------------------Cost---------------------#

        tm_std_fcm_diary_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date)
        tm_std_fcm_sale_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,sold_to__in = ["Agent","ICustomer"])
        tm_std_fcm_leake_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,sold_to="Leakage")

        #dairy sale (icus + agent + leakage)
        tm_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        std500_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        std250_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        fcm_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_diary_sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        tea_sale = tm_std_fcm_diary_sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_diary_sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]


        data_dict[dates]["Costs"]["product"]["tm"]["Resived From Diary"] = tm_sale
        data_dict[dates]["Costs"]["product"]["std500"]["Resived From Diary"] = std500_sale
        data_dict[dates]["Costs"]["product"]["std250"]["Resived From Diary"] = std250_sale
        data_dict[dates]["Costs"]["product"]["fcm"]["Resived From Diary"] = fcm_sale
        data_dict[dates]["Costs"]["product"]["tmate"]["Resived From Diary"] = tea_sale

        #net_recived (icus + agent)
        tm_sale = tm_std_fcm_sale_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        std500_sale = tm_std_fcm_sale_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        std250_sale = tm_std_fcm_sale_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        fcm_sale = tm_std_fcm_sale_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_sale_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        tea_sale = tm_std_fcm_sale_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_sale_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

        data_dict[dates]["Costs"]["product"]["tm"]["Net Recived"] = tm_sale
        data_dict[dates]["Costs"]["product"]["std500"]["Net Recived"] = std500_sale
        data_dict[dates]["Costs"]["product"]["std250"]["Net Recived"] = std250_sale
        data_dict[dates]["Costs"]["product"]["fcm"]["Net Recived"] = fcm_sale
        data_dict[dates]["Costs"]["product"]["tmate"]["Net Recived"] = tea_sale

        #leakage
        lk_tm_sale = tm_std_fcm_leake_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        lk_std500_sale = tm_std_fcm_leake_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        lk_std250_sale = tm_std_fcm_leake_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        lk_fcm_sale = tm_std_fcm_leake_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_leake_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        lk_tea_sale = tm_std_fcm_leake_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_leake_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

        data_dict[dates]["Costs"]["product"]["tm"]["Leakage"] = lk_tm_sale
        data_dict[dates]["Costs"]["product"]["std500"]["Leakage"] = lk_std500_sale
        data_dict[dates]["Costs"]["product"]["std250"]["Leakage"] = lk_std250_sale
        data_dict[dates]["Costs"]["product"]["fcm"]["Leakage"] = lk_fcm_sale
        data_dict[dates]["Costs"]["product"]["tmate"]["Leakage"] = lk_tea_sale

        union_list = ["COIMBATORE Union","NILGIRIS Union","TIRUPPUR Union","CHENNAI Aavin"]

        for union in union_list:
            if not union in data_dict[dates]["Costs"]["union_sale"]:
                data_dict[dates]["Costs"]["union_sale"][union] = {
                    "tm" : 0,
                    "std500" : 0,
                    "std250":0,
                    "fcm" : 0,
                    "tmate" : 0,
                    "smcan" : 0,
                    "fcmcan" : 0
                }
            tm_std_fcm_union_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union=union,sold_to__in = ["Agent","ICustomer"])

            if tm_std_fcm_union_obj:
                # union sale
                union_tm_sale = tm_std_fcm_union_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
                union_std500_sale = tm_std_fcm_union_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
                union_std250_sale = tm_std_fcm_union_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
                union_fcm_sale = tm_std_fcm_union_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_union_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
                union_tea_sale = tm_std_fcm_union_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_union_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

                data_dict[dates]["Costs"]["union_sale"][union]["tm"] = union_tm_sale
                data_dict[dates]["Costs"]["union_sale"][union]["std500"] = union_std500_sale
                data_dict[dates]["Costs"]["union_sale"][union]["std250"] = union_std250_sale
                data_dict[dates]["Costs"]["union_sale"][union]["fcm"] = union_fcm_sale
                data_dict[dates]["Costs"]["union_sale"][union]["tmate"] = union_tea_sale

        #1.Agent + Pvt Parlour (cash)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[1,2,11])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]
        cbe_smcan_sale = tm_std_fcm_cbe_obj.aggregate(Sum('smcan_cost'))["smcan_cost__sum"]
        cbe_fcmcan_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcmcan_cost'))["fcmcan_cost__sum"]

        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Cash"]["tm"] = cbe_tm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Cash"]["std500"] = cbe_std500_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Cash"]["std250"] = cbe_std250_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Cash"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Cash"]["tmate"] = cbe_tea_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Cash"]["smcan"] = cbe_smcan_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Cash"]["fcmcan"] = cbe_fcmcan_sale

        #2.Agent + Pvt Parlour (card)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[1,2])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Card"]["tm"] = cbe_tm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Card"]["std500"] = cbe_std500_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Card"]["std250"] = cbe_std250_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Card"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Agent Card"]["tmate"] = cbe_tea_sale

        #3.Ownparlour (cash)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "Agent",business_type_id__in=[3,16])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Cash"]["tm"] = cbe_tm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Cash"]["std500"] = cbe_std500_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Cash"]["std250"] = cbe_std250_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Cash"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Cash"]["tmate"] = cbe_tea_sale

        #4.Ownparlour (card)
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to = "ICustomer",business_type_id__in=[3,16])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Card"]["tm"] = cbe_tm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Card"]["std500"] = cbe_std500_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Card"]["std250"] = cbe_std250_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Card"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Union Booth Card"]["tmate"] = cbe_tea_sale

        #5.Private ins
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[4, 15])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

        data_dict[dates]["Costs"]["Coimbatore Account"]["Pvt Institutes"]["tm"] = cbe_tm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Pvt Institutes"]["std500"] = cbe_std500_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Pvt Institutes"]["std250"] = cbe_std250_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Pvt Institutes"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Pvt Institutes"]["tmate"] = cbe_tea_sale

        #6.Govt. ins
        tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id__in=[10,5])

        # union sale
        cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
        cbe_tea_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tea500_cost'))["tea500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('tea1000_cost'))["tea1000_cost__sum"]

        data_dict[dates]["Costs"]["Coimbatore Account"]["Govt Institutes"]["tm"] = cbe_tm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Govt Institutes"]["std500"] = cbe_std500_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Govt Institutes"]["std250"] = cbe_std250_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Govt Institutes"]["fcm"] = cbe_fcm_sale
        data_dict[dates]["Costs"]["Coimbatore Account"]["Govt Institutes"]["tmate"] = cbe_tea_sale

        # #6.Society
        # tm_std_fcm_cbe_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,union="COIMBATORE Union",sold_to__in = ["Agent","ICustomer"],business_type_id=10)

        # # union sale
        # cbe_tm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
        # cbe_std500_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
        # cbe_std250_sale = tm_std_fcm_cbe_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
        # cbe_fcm_sale = tm_std_fcm_cbe_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"] + tm_std_fcm_cbe_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]

        # data_dict[dates]["Costs"]["Coimbatore Account"]["Society"]["tm"] = cbe_tm_sale
        # data_dict[dates]["Costs"]["Coimbatore Account"]["Society"]["std500"] = cbe_std500_sale
        # data_dict[dates]["Costs"]["Coimbatore Account"]["Society"]["std250"] = cbe_std250_sale
        # data_dict[dates]["Costs"]["Coimbatore Account"]["Society"]["fcm"] = cbe_fcm_sale


    data_dict["user_name"] = "sunesh"
    data = create_canvas_for_report_three(data_dict, date_list)
    return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_for_report_three(data_dict, date_list):

  file_name = 'monthly_report_three.pdf'
#     file_path = os.path.join('static/media/zone_wise_report/', file_name)

  file_path = os.path.join('static/media/monthly_report/', file_name)
   
  mycanvas = canvas.Canvas(file_path, pagesize=(15 * inch, 12 * inch))
  # pdfmetrics.registerFont(TTFont('dot', 'dots.ttf'))
  light_color = 0x9b9999
  dark_color = 0x000000

  
  
  mycanvas.setFillColor(HexColor(dark_color))
  mycanvas.setFont('Helvetica-Bold', 15)
#     mycanvas.drawString(1000, 740+80,"C1")
  mycanvas.setFont('Helvetica', 15)
  mycanvas.drawCentredString(560, 740+100, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
  mycanvas.drawCentredString(560, 720+100, 'Report 3')
  
#     mycanvas.setDash(6,3)
  mycanvas.setLineWidth(0)
  
  x_total_len = 1060
  x_axis = 40
  x_axis_line = 10
  y_axis = 670+120
  y_axis_line = 690+120
  key_no = 0
  mycanvas.setFont('Helvetica', 11)
  head_list = ["Date","Milk","Resived From Diary","Leakage","Return","Net Recived","Tiruppur","Chennai","Other Union Total","Agent Cash","Agent Card","Union Booth Cash","Union Booth Card","Pvt Ins","Govt Ins","Nilgiris","CBE Union Total","Agent Cash Amount","Agent Card Amount","Union Booth Cash Amount","Union Booth Card Amount","Pvt Ins Amount","Govt Ins Amount","Nilgiris Union Amount","CBE Union Total Amount"]
  len_adjust=len(head_list)
      
  
  diary_tot = 0
  leak = 0
  rtnd = 0
  net_rec = 0
  trp_uni = 0
  chni_uni = 0
  oth_uni = 0
  agnt_csh = 0
  agnt_crd = 0
  uni_bth_csh = 0
  uni_bth_crd = 0
  pvt_ins = 0
  gvt_ins = 0
  nils_uni = 0
  cbe_uni = 0
  agnt_csh_amt = 0
  agnt_crd_amt = 0
  uni_bth_csh_amt = 0
  uni_bth_crd_amt = 0
  pvt_ins_amt = 0
  gvt_ins_amt = 0
  nils_uni_amt = 0
  cbe_uni_amt = 0
  
  #tm_
  tm_diary_tot = 0
  tm_leak = 0
  tm_rtnd = 0
  tm_net_rec = 0
  tm_trp_uni = 0
  tm_chni_uni = 0
  tm_oth_uni = 0
  tm_agnt_csh = 0
  tm_agnt_crd = 0
  tm_uni_bth_csh = 0
  tm_uni_bth_crd = 0
  tm_pvt_ins = 0
  tm_gvt_ins = 0
  tm_nils_uni = 0
  tm_cbe_uni = 0
  tm_agnt_csh_amt = 0
  tm_agnt_crd_amt = 0
  tm_uni_bth_csh_amt = 0
  tm_uni_bth_crd_amt = 0
  tm_pvt_ins_amt = 0
  tm_gvt_ins_amt = 0
  tm_nils_uni_amt = 0
  tm_cbe_uni_amt = 0
  
  #std500
  sm500_diary_tot = 0
  sm500_leak = 0
  sm500_rtnd = 0
  sm500_net_rec = 0
  sm500_trp_uni = 0
  sm500_chni_uni = 0
  sm500_oth_uni = 0
  sm500_agnt_csh = 0
  sm500_agnt_crd = 0
  sm500_uni_bth_csh = 0
  sm500_uni_bth_crd = 0
  sm500_pvt_ins = 0
  sm500_gvt_ins = 0
  sm500_nils_uni = 0
  sm500_cbe_uni = 0
  sm500_agnt_csh_amt = 0
  sm500_agnt_crd_amt = 0
  sm500_uni_bth_csh_amt = 0
  sm500_uni_bth_crd_amt = 0
  sm500_pvt_ins_amt = 0
  sm500_gvt_ins_amt = 0
  sm500_nils_uni_amt = 0
  sm500_cbe_uni_amt = 0
  
  #std250
  sm250_diary_tot = 0
  sm250_leak = 0
  sm250_rtnd = 0
  sm250_net_rec = 0
  sm250_trp_uni = 0
  sm250_chni_uni = 0
  sm250_oth_uni = 0
  sm250_agnt_csh = 0
  sm250_agnt_crd = 0
  sm250_uni_bth_csh = 0
  sm250_uni_bth_crd = 0
  sm250_pvt_ins = 0
  sm250_gvt_ins = 0
  sm250_nils_uni = 0
  sm250_cbe_uni = 0
  sm250_agnt_csh_amt = 0
  sm250_agnt_crd_amt = 0
  sm250_uni_bth_csh_amt = 0
  sm250_uni_bth_crd_amt = 0
  sm250_pvt_ins_amt = 0
  sm250_gvt_ins_amt = 0
  sm250_nils_uni_amt = 0
  sm250_cbe_uni_amt = 0
  smcan_cbe_uni = 0
  smcan_cbe_uni_amt = 0
  
  #fcm
  fcm_diary_tot = 0
  fcm_leak = 0
  fcm_rtnd = 0
  fcm_net_rec = 0
  fcm_trp_uni = 0
  fcm_chni_uni = 0
  fcm_oth_uni = 0
  fcm_agnt_csh = 0
  fcm_agnt_crd = 0
  fcm_uni_bth_csh = 0
  fcm_uni_bth_crd = 0
  fcm_pvt_ins = 0
  fcm_gvt_ins = 0
  fcm_nils_uni = 0
  fcm_cbe_uni = 0
  fcm_agnt_csh_amt = 0
  fcm_agnt_crd_amt = 0
  fcm_uni_bth_csh_amt = 0
  fcm_uni_bth_crd_amt = 0
  fcm_pvt_ins_amt = 0
  fcm_gvt_ins_amt = 0
  fcm_nils_uni_amt = 0
  fcm_cbe_uni_amt = 0
  fcmcan_cbe_uni = 0
  fcmcan_cbe_uni_amt = 0

  sm_can_diary_tot = 0
  fcm_can_diary_tot = 0
  sm_can_net_tot = 0
  fcm_can_net_tot = 0
  
 #tmate
  tea_diary_tot = 0
  tea_leak = 0
  tea_rtnd = 0
  tea_net_rec = 0
  tea_trp_uni = 0
  tea_chni_uni = 0
  tea_oth_uni = 0
  tea_agnt_csh = 0
  tea_agnt_crd = 0
  tea_uni_bth_csh = 0
  tea_uni_bth_crd = 0
  tea_pvt_ins = 0
  tea_gvt_ins = 0
  tea_nils_uni = 0
  tea_cbe_uni = 0
  tea_agnt_csh_amt = 0
  tea_agnt_crd_amt = 0
  tea_uni_bth_csh_amt = 0
  tea_uni_bth_crd_amt = 0
  tea_pvt_ins_amt = 0
  tea_gvt_ins_amt = 0
  tea_nils_uni_amt = 0
  tea_cbe_uni_amt = 0
 
  
# for tabe header
  
  mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
  mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
  # print(len(head_list))
  for stock_name in head_list:
      data_name = ""
      data_2nd_name = ""
      data_3rd_name = ""
      data = stock_name.split(" ")

      if data[0] == "" :
          data.remove(data[0])

      if data[-1] == "":
          data.remove(data[-1])

      if len(data) == 1:
          data_name += data[0]

      if len(data) == 2:
          data_name += data[0]
          data_2nd_name += data[1]

      if len(data) == 3:
          data_name += data[0]
          data_2nd_name += data[1]
          data_3rd_name += data[-1]

      if len(data) == 4:
          data_name += data[0]
          data_2nd_name += data[1]
          data_3rd_name += data[2]
      mycanvas.setFont('Helvetica', 10)
      
      if stock_name == "Milk":
          mycanvas.drawCentredString(x_axis-17,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-17,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-17,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Resived From Diary":
          mycanvas.drawCentredString(x_axis-25,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-25,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-25,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Leakage":
          mycanvas.drawCentredString(x_axis-25,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-25,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-25,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Return":
          mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Net Recived":
          mycanvas.drawCentredString(x_axis-34,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-34,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-34,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Tiruppur":
          mycanvas.drawCentredString(x_axis-30+1,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-30+1,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-30+1,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Chennai":
          mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Other Union Total":
          mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Agent Cash":
          mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Agent Card":
          mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Union Booth Cash":
          mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Union Booth Card":
          mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Pvt Ins":
          mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-30,str('NCB'))
          
      elif stock_name == "Govt Ins":
          mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))
                      
      elif stock_name == "Nilgiris":
          mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "CBE Union Total":
          mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Agent Cash Amount":
          mycanvas.drawCentredString(x_axis-27,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-27,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-27,y_axis-30,str(data_3rd_name))
          
      elif stock_name == "Agent Card Amount":
          mycanvas.drawCentredString(x_axis-15,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-15,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-15,y_axis-30,str(data_3rd_name))

      elif stock_name == "Union Booth Cash Amount":
          mycanvas.drawCentredString(x_axis-15,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-15,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-15,y_axis-30,str(data_3rd_name))

      elif stock_name == "Union Booth Card Amount":
          mycanvas.drawCentredString(x_axis-15,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-15,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-15,y_axis-30,str(data_3rd_name))

      elif stock_name == "Pvt Ins Amount":
          mycanvas.drawCentredString(x_axis-20,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-20,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-20,y_axis-30,str(data_3rd_name))

      elif stock_name == "Govt Ins Amount":
          mycanvas.drawCentredString(x_axis-20,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-20,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-20,y_axis-30,str(data_3rd_name))

      elif stock_name == "Nilgiris Union Amount":
          mycanvas.drawCentredString(x_axis-17,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-17,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-17,y_axis-30,str(data_3rd_name))

      elif stock_name == "CBE Union Total Amount":
          mycanvas.drawCentredString(x_axis-17,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-17,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-17,y_axis-30,str(data_3rd_name))

      else:
          mycanvas.drawCentredString(x_axis-5,y_axis,str(data_name))
          mycanvas.drawCentredString(x_axis-5,y_axis-15,str(data_2nd_name))
          mycanvas.drawCentredString(x_axis-5,y_axis-30,str(data_3rd_name))
          
      x_axis += (x_total_len/len_adjust)
      
#for data inside table
  sl_no = 1
  for data in data_dict:
      x_axis = 40
      if data == "user_name":
          pass
      else:
          for stock_name in head_list:
              if stock_name == "Date":  
                  mycanvas.setFont('Helvetica', 7)
                  data_formate = datetime.strptime(data, '%Y-%m-%d')
                  date_data = datetime.strftime(data_formate, '%d-%m-%Y')
                  mycanvas.drawCentredString(x_axis-7,y_axis-60,str(date_data))
                  mycanvas.setFont('Helvetica', 11)
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-28,y_axis+20,x_axis-28,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Milk":
                  mycanvas.setFont('Helvetica', 6)
                  mycanvas.drawString(x_axis-25,y_axis-60,"TM")
                  mycanvas.drawString(x_axis-25,y_axis-75,"SM500")
                  mycanvas.drawString(x_axis-25,y_axis-90,"SM250")
                  mycanvas.drawString(x_axis-25,y_axis-105,"FCM")
                  mycanvas.drawString(x_axis-25,y_axis-120,"TMATE")
                  mycanvas.drawString(x_axis-25,y_axis-135,"SMCAN")
                  mycanvas.drawString(x_axis-25,y_axis-150,"FCMCAN")
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-48,y_axis+20,x_axis-48,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Resived From Diary":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-2,y_axis-60,str(data_dict[data]["product"]["tm"]['Resived From Diary']))
                  mycanvas.drawRightString(x_axis-2,y_axis-75,str(data_dict[data]["product"]["std500"]['Resived From Diary']))
                  mycanvas.drawRightString(x_axis-2,y_axis-90,str(data_dict[data]["product"]["std250"]['Resived From Diary']))
                  mycanvas.drawRightString(x_axis-2,y_axis-105,str(data_dict[data]["product"]["fcm"]['Resived From Diary']))
                  mycanvas.drawRightString(x_axis-2,y_axis-120,str(data_dict[data]["product"]["tmate"]['Resived From Diary']))
                  mycanvas.drawRightString(x_axis-2,y_axis-135,str(data_dict[data]["product"]["smcan"]['Resived From Diary']))
                  mycanvas.drawRightString(x_axis-2,y_axis-150,str(data_dict[data]["product"]["fcmcan"]['Resived From Diary']))

                  
                  diary_tot += data_dict[data]["product"]["tm"]['Resived From Diary'] + data_dict[data]["product"]["std500"]['Resived From Diary']+data_dict[data]["product"]["std250"]['Resived From Diary'] + data_dict[data]["product"]["fcm"]['Resived From Diary']+ data_dict[data]["product"]["smcan"]['Resived From Diary']+ data_dict[data]["product"]["fcmcan"]['Resived From Diary']
                  tm_diary_tot += data_dict[data]["product"]["tm"]['Resived From Diary']
                  sm500_diary_tot += data_dict[data]["product"]["std500"]['Resived From Diary']
                  sm250_diary_tot += data_dict[data]["product"]["std250"]['Resived From Diary']
                  fcm_diary_tot += data_dict[data]["product"]["fcm"]['Resived From Diary']
                  tea_diary_tot += data_dict[data]["product"]["tmate"]['Resived From Diary']
                  sm_can_diary_tot += data_dict[data]["product"]["smcan"]['Resived From Diary']
                  fcm_can_diary_tot += data_dict[data]["product"]["fcmcan"]['Resived From Diary']
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-43,y_axis+20,x_axis-43,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Leakage":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-8,y_axis-60,str(data_dict[data]["product"]["tm"]['Leakage']))
                  mycanvas.drawRightString(x_axis-8,y_axis-75,str(data_dict[data]["product"]["std500"]['Leakage']))
                  mycanvas.drawRightString(x_axis-8,y_axis-90,str(data_dict[data]["product"]["std250"]['Leakage']))
                  mycanvas.drawRightString(x_axis-8,y_axis-105,str(data_dict[data]["product"]["fcm"]['Leakage']))
                  mycanvas.drawRightString(x_axis-8,y_axis-125,str(data_dict[data]["product"]["tmate"]['Leakage']))

                  leak += data_dict[data]["product"]["tm"]['Leakage'] + data_dict[data]["product"]["std250"]['Leakage'] +data_dict[data]["product"]["std500"]['Leakage'] + data_dict[data]["product"]["fcm"]['Leakage'] +data_dict[data]["product"]["tmate"]['Leakage']
                  
                  tm_leak += data_dict[data]["product"]["tm"]['Leakage']
                  sm500_leak += data_dict[data]["product"]["std500"]['Leakage']
                  sm250_leak += data_dict[data]["product"]["std250"]['Leakage']
                  fcm_leak += data_dict[data]["product"]["fcm"]['Leakage']
                  tea_leak += data_dict[data]["product"]["tmate"]['Leakage']
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-48,y_axis+20,x_axis-48,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Return":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-19,y_axis-60,str(data_dict[data]["product"]["tm"]['Returned']))
                  mycanvas.drawRightString(x_axis-19,y_axis-75,str(data_dict[data]["product"]["std500"]['Returned']))
                  mycanvas.drawRightString(x_axis-19,y_axis-90,str(data_dict[data]["product"]["std250"]['Returned']))
                  mycanvas.drawRightString(x_axis-19,y_axis-105,str(data_dict[data]["product"]["fcm"]['Returned']))
                  mycanvas.drawRightString(x_axis-19,y_axis-125,str(data_dict[data]["product"]["tmate"]['Returned']))
                  
                  rtnd += data_dict[data]["product"]["tm"]['Returned'] + data_dict[data]["product"]["std500"]['Returned'] + data_dict[data]["product"]["std250"]['Returned'] + data_dict[data]["product"]["fcm"]['Returned']
                  
                  tm_rtnd += data_dict[data]["product"]["tm"]['Returned']
                  sm500_rtnd += data_dict[data]["product"]["std500"]['Returned']
                  sm250_rtnd += data_dict[data]["product"]["std250"]['Returned']
                  fcm_rtnd += data_dict[data]["product"]["fcm"]['Returned']
                  tea_rtnd += data_dict[data]["product"]["tmate"]['Returned']
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-59,y_axis+20,x_axis-59,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Net Recived":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-12,y_axis-60,str(data_dict[data]["product"]["tm"]['Net Recived']))
                  mycanvas.drawRightString(x_axis-12,y_axis-75,str(data_dict[data]["product"]["std500"]['Net Recived']))
                  mycanvas.drawRightString(x_axis-12,y_axis-90,str(data_dict[data]["product"]["std250"]['Net Recived']))
                  mycanvas.drawRightString(x_axis-12,y_axis-105,str(data_dict[data]["product"]["fcm"]['Net Recived']))
                  mycanvas.drawRightString(x_axis-12,y_axis-120,str(data_dict[data]["product"]["tmate"]['Net Recived']))
                  mycanvas.drawRightString(x_axis-12,y_axis-135,str(data_dict[data]["product"]["smcan"]['Net Recived']))
                  mycanvas.drawRightString(x_axis-12,y_axis-150,str(data_dict[data]["product"]["fcmcan"]['Net Recived']))
                  
                  net_rec += data_dict[data]["product"]["tm"]['Net Recived'] + data_dict[data]["product"]["std500"]['Net Recived']+data_dict[data]["product"]["std250"]['Net Recived'] + data_dict[data]["product"]["fcm"]['Net Recived'] + data_dict[data]["product"]["tmate"]['Net Recived'] + data_dict[data]["product"]["smcan"]['Net Recived'] + data_dict[data]["product"]["fcmcan"]['Net Recived']
                  
                  tm_net_rec += data_dict[data]["product"]["tm"]['Net Recived']
                  sm500_net_rec += data_dict[data]["product"]["std500"]['Net Recived']
                  sm250_net_rec += data_dict[data]["product"]["std250"]['Net Recived']
                  fcm_net_rec += data_dict[data]["product"]["fcm"]['Net Recived']
                  tea_net_rec += data_dict[data]["product"]["tmate"]['Net Recived']
                  sm_can_net_tot += data_dict[data]["product"]["smcan"]['Net Recived']
                  fcm_can_net_tot += data_dict[data]["product"]["fcmcan"]['Net Recived']
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-52,y_axis+20,x_axis-52,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              # union_sale
              elif stock_name == "Tiruppur":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-10,y_axis-60,str(data_dict[data]['union_sale']['TIRUPPUR Union']["tm"]))
                  mycanvas.drawRightString(x_axis-10,y_axis-75,str(data_dict[data]['union_sale']['TIRUPPUR Union']["std500"]))
                  mycanvas.drawRightString(x_axis-10,y_axis-90,str(data_dict[data]['union_sale']['TIRUPPUR Union']["std250"]))
                  mycanvas.drawRightString(x_axis-10,y_axis-105,str(data_dict[data]['union_sale']['TIRUPPUR Union']["fcm"]))
                  
                  trp_uni += data_dict[data]['union_sale']['TIRUPPUR Union']["tm"] + data_dict[data]['union_sale']['TIRUPPUR Union']["std500"] + data_dict[data]['union_sale']['TIRUPPUR Union']["std250"] + data_dict[data]['union_sale']['TIRUPPUR Union']["fcm"]
                  
                  tm_trp_uni += data_dict[data]['union_sale']['TIRUPPUR Union']["tm"]
                  sm500_trp_uni += data_dict[data]['union_sale']['TIRUPPUR Union']["std500"]
                  sm250_trp_uni += data_dict[data]['union_sale']['TIRUPPUR Union']["std250"]
                  fcm_trp_uni += data_dict[data]['union_sale']['TIRUPPUR Union']["fcm"]
                  tea_trp_uni += data_dict[data]['union_sale']['TIRUPPUR Union']["tmate"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-50,y_axis+20,x_axis-50,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              elif stock_name == "Chennai":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-11,y_axis-60,str(data_dict[data]['union_sale']['CHENNAI Aavin']["tm"]))
                  mycanvas.drawRightString(x_axis-11,y_axis-75,str(data_dict[data]['union_sale']['CHENNAI Aavin']["std500"]))
                  mycanvas.drawRightString(x_axis-11,y_axis-90,str(data_dict[data]['union_sale']['CHENNAI Aavin']["std250"]))
                  mycanvas.drawRightString(x_axis-11,y_axis-105,str(data_dict[data]['union_sale']['CHENNAI Aavin']["fcm"]))
                  mycanvas.drawRightString(x_axis-11,y_axis-120,str(data_dict[data]['union_sale']['CHENNAI Aavin']["tmate"]))
                  
                  chni_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["tm"] + data_dict[data]['union_sale']['CHENNAI Aavin']["std500"] + data_dict[data]['union_sale']['CHENNAI Aavin']["std250"] + data_dict[data]['union_sale']['CHENNAI Aavin']["fcm"] + data_dict[data]['union_sale']['CHENNAI Aavin']["tmate"]
                  
                  tm_chni_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["tm"]
                  sm500_chni_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["std500"]
                  sm250_chni_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["std250"]
                  fcm_chni_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["fcm"]
                  tea_chni_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["tmate"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-52,y_axis+20,x_axis-52,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Other Union Total":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-12,y_axis-60,str(data_dict[data]['union_sale']['CHENNAI Aavin']["tm"]+data_dict[data]['union_sale']['TIRUPPUR Union']["tm"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-75,str(data_dict[data]['union_sale']['CHENNAI Aavin']["std500"]+data_dict[data]['union_sale']['TIRUPPUR Union']["std500"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-90,str(data_dict[data]['union_sale']['CHENNAI Aavin']["std250"]+data_dict[data]['union_sale']['TIRUPPUR Union']["std250"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-105,str(data_dict[data]['union_sale']['CHENNAI Aavin']["fcm"]+data_dict[data]['union_sale']['TIRUPPUR Union']["fcm"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-120,str(data_dict[data]['union_sale']['CHENNAI Aavin']["tmate"]+data_dict[data]['union_sale']['TIRUPPUR Union']["tmate"]))

                  
                  oth_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["tm"]+data_dict[data]['union_sale']['TIRUPPUR Union']["tm"] + data_dict[data]['union_sale']['CHENNAI Aavin']["std250"]+data_dict[data]['union_sale']['TIRUPPUR Union']["std250"] + data_dict[data]['union_sale']['CHENNAI Aavin']["std500"]+data_dict[data]['union_sale']['TIRUPPUR Union']["std500"] + data_dict[data]['union_sale']['CHENNAI Aavin']["fcm"]+data_dict[data]['union_sale']['TIRUPPUR Union']["tmate"]
                  
                  tm_oth_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["tm"]+data_dict[data]['union_sale']['TIRUPPUR Union']["tm"]
                  sm500_oth_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["std500"]+data_dict[data]['union_sale']['TIRUPPUR Union']["std500"]
                  sm250_oth_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["std250"]+data_dict[data]['union_sale']['TIRUPPUR Union']["std250"]
                  fcm_oth_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["fcm"]+data_dict[data]['union_sale']['TIRUPPUR Union']["fcm"]
                  tea_oth_uni += data_dict[data]['union_sale']['CHENNAI Aavin']["tmate"]+data_dict[data]['union_sale']['TIRUPPUR Union']["tmate"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-52,y_axis+20,x_axis-52,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              # coimbatore_union
              elif stock_name == "Agent Cash":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-9,y_axis-60,str(data_dict[data]['Coimbatore Account']['Agent Cash']["tm"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-75,str(data_dict[data]['Coimbatore Account']['Agent Cash']["std500"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-90,str(data_dict[data]['Coimbatore Account']['Agent Cash']["std250"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-105,str(data_dict[data]['Coimbatore Account']['Agent Cash']["fcm"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-120,str(data_dict[data]['Coimbatore Account']['Agent Cash']["tmate"]))
                  
                  agnt_csh += data_dict[data]['Coimbatore Account']['Agent Cash']["tm"] + data_dict[data]['Coimbatore Account']['Agent Cash']["std500"] + data_dict[data]['Coimbatore Account']['Agent Cash']["std250"] + data_dict[data]['Coimbatore Account']['Agent Cash']["fcm"] + data_dict[data]['Coimbatore Account']['Agent Cash']["tmate"]
                  
                  tm_agnt_csh += data_dict[data]['Coimbatore Account']['Agent Cash']["tm"]
                  sm500_agnt_csh += data_dict[data]['Coimbatore Account']['Agent Cash']["std500"]
                  sm250_agnt_csh += data_dict[data]['Coimbatore Account']['Agent Cash']["std250"]
                  fcm_agnt_csh += data_dict[data]['Coimbatore Account']['Agent Cash']["fcm"]
                  tea_agnt_csh += data_dict[data]['Coimbatore Account']['Agent Cash']["tmate"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-50,y_axis+20,x_axis-50,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              elif stock_name == "Agent Card":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-9,y_axis-60,str(data_dict[data]['Coimbatore Account']['Agent Card']["tm"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-75,str(data_dict[data]['Coimbatore Account']['Agent Card']["std500"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-90,str(data_dict[data]['Coimbatore Account']['Agent Card']["std250"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-105,str(data_dict[data]['Coimbatore Account']['Agent Card']["fcm"]))
                  mycanvas.drawRightString(x_axis-9,y_axis-125,str(data_dict[data]['Coimbatore Account']['Agent Card']["tmate"]))
                  
                  agnt_crd += data_dict[data]['Coimbatore Account']['Agent Card']["tm"] + data_dict[data]['Coimbatore Account']['Agent Card']["std500"] + data_dict[data]['Coimbatore Account']['Agent Card']["std250"] + data_dict[data]['Coimbatore Account']['Agent Card']["fcm"] + data_dict[data]['Coimbatore Account']['Agent Card']["tmate"]
                  
                  tm_agnt_crd += data_dict[data]['Coimbatore Account']['Agent Card']["tm"]
                  sm500_agnt_crd += data_dict[data]['Coimbatore Account']['Agent Card']["std500"]
                  sm250_agnt_crd += data_dict[data]['Coimbatore Account']['Agent Card']["std250"]
                  fcm_agnt_crd += data_dict[data]['Coimbatore Account']['Agent Card']["fcm"]
                  tea_agnt_crd += data_dict[data]['Coimbatore Account']['Agent Card']["tea"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-50,y_axis+20,x_axis-50,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Union Booth Cash":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-12,y_axis-60,str(data_dict[data]['Coimbatore Account']['Union Booth Cash']["tm"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-75,str(data_dict[data]['Coimbatore Account']['Union Booth Cash']["std500"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-90,str(data_dict[data]['Coimbatore Account']['Union Booth Cash']["std250"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-105,str(data_dict[data]['Coimbatore Account']['Union Booth Cash']["fcm"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-120,str(data_dict[data]['Coimbatore Account']['Union Booth Cash']["tmate"]))

                  
                  uni_bth_csh += data_dict[data]['Coimbatore Account']['Union Booth Cash']["tm"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["std500"] ++ data_dict[data]['Coimbatore Account']['Union Booth Cash']["std250"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["fcm"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["tmate"]
                  
                  tm_uni_bth_csh += data_dict[data]['Coimbatore Account']['Union Booth Cash']["tm"]
                  sm500_uni_bth_csh += data_dict[data]['Coimbatore Account']['Union Booth Cash']["std500"]
                  sm250_uni_bth_csh += data_dict[data]['Coimbatore Account']['Union Booth Cash']["std250"]
                  fcm_uni_bth_csh += data_dict[data]['Coimbatore Account']['Union Booth Cash']["fcm"]
                  tea_uni_bth_csh += data_dict[data]['Coimbatore Account']['Union Booth Cash']["tmate"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-52,y_axis+20,x_axis-52,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Union Booth Card":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-12,y_axis-60,str(data_dict[data]['Coimbatore Account']['Union Booth Card']["tm"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-75,str(data_dict[data]['Coimbatore Account']['Union Booth Card']["std500"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-90,str(data_dict[data]['Coimbatore Account']['Union Booth Card']["std250"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-105,str(data_dict[data]['Coimbatore Account']['Union Booth Card']["fcm"]))
                  mycanvas.drawRightString(x_axis-12,y_axis-120,str(data_dict[data]['Coimbatore Account']['Union Booth Card']["tmate"]))
                  
                  uni_bth_crd += data_dict[data]['Coimbatore Account']['Union Booth Card']["tm"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["std250"]+ data_dict[data]['Coimbatore Account']['Union Booth Card']["std500"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["fcm"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["tmate"]
                  
                  tm_uni_bth_crd += data_dict[data]['Coimbatore Account']['Union Booth Card']["tm"]
                  sm500_uni_bth_crd += data_dict[data]['Coimbatore Account']['Union Booth Card']["std500"]
                  sm250_uni_bth_crd += data_dict[data]['Coimbatore Account']['Union Booth Card']["std250"]
                  fcm_uni_bth_crd += data_dict[data]['Coimbatore Account']['Union Booth Card']["fcm"]
                  tea_uni_bth_crd += data_dict[data]['Coimbatore Account']['Union Booth Card']["tmate"]
              
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-52,y_axis+20,x_axis-52,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Pvt Ins":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-14,y_axis-60,str(data_dict[data]['Coimbatore Account']['Pvt Institutes']["tm"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-75,str(data_dict[data]['Coimbatore Account']['Pvt Institutes']["std500"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-90,str(data_dict[data]['Coimbatore Account']['Pvt Institutes']["std250"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-105,str(data_dict[data]['Coimbatore Account']['Pvt Institutes']["fcm"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-120,str(data_dict[data]['Coimbatore Account']['Pvt Institutes']["tmate"]))
                  
                  pvt_ins += data_dict[data]['Coimbatore Account']['Pvt Institutes']["tm"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["std500"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["std250"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["fcm"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["tmate"]
                  
                  tm_pvt_ins += data_dict[data]['Coimbatore Account']['Pvt Institutes']["tm"]
                  sm500_pvt_ins += data_dict[data]['Coimbatore Account']['Pvt Institutes']["std500"]
                  sm250_pvt_ins += data_dict[data]['Coimbatore Account']['Pvt Institutes']["std250"]
                  fcm_pvt_ins += data_dict[data]['Coimbatore Account']['Pvt Institutes']["fcm"]
                  tea_pvt_ins += data_dict[data]['Coimbatore Account']['Pvt Institutes']["tmate"]

                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-54,y_axis+20,x_axis-54,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Govt Ins":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-14,y_axis-60,str(data_dict[data]['Coimbatore Account']['Govt Institutes']["tm"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-75,str(data_dict[data]['Coimbatore Account']['Govt Institutes']["std500"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-90,str(data_dict[data]['Coimbatore Account']['Govt Institutes']["std250"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-105,str(data_dict[data]['Coimbatore Account']['Govt Institutes']["fcm"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-120,str(data_dict[data]['Coimbatore Account']['Govt Institutes']["tmate"]))
                  
                  gvt_ins += data_dict[data]['Coimbatore Account']['Govt Institutes']["tm"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["std500"] +data_dict[data]['Coimbatore Account']['Govt Institutes']["std250"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["fcm"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["tmate"]
                  
                  tm_gvt_ins += data_dict[data]['Coimbatore Account']['Govt Institutes']["tm"]
                  sm500_gvt_ins += data_dict[data]['Coimbatore Account']['Govt Institutes']["std500"]
                  sm250_gvt_ins += data_dict[data]['Coimbatore Account']['Govt Institutes']["std250"]
                  fcm_gvt_ins += data_dict[data]['Coimbatore Account']['Govt Institutes']["fcm"]
                  tea_gvt_ins += data_dict[data]['Coimbatore Account']['Govt Institutes']["tmate"]

                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-54,y_axis+20,x_axis-54,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              elif stock_name == "Nilgiris":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-14,y_axis-60,str(data_dict[data]['union_sale']['NILGIRIS Union']["tm"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-75,str(data_dict[data]['union_sale']['NILGIRIS Union']["std500"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-90,str(data_dict[data]['union_sale']['NILGIRIS Union']["std250"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-105,str(data_dict[data]['union_sale']['NILGIRIS Union']["fcm"]))
                  mycanvas.drawRightString(x_axis-14,y_axis-120,str(data_dict[data]['union_sale']['NILGIRIS Union']["tmate"]))
                  
                  nils_uni += data_dict[data]['union_sale']['NILGIRIS Union']["tm"] + data_dict[data]['union_sale']['NILGIRIS Union']["std250"]+ data_dict[data]['union_sale']['NILGIRIS Union']["std500"] + data_dict[data]['union_sale']['NILGIRIS Union']["fcm"] + data_dict[data]['union_sale']['NILGIRIS Union']["tmate"]
                  
                  tm_nils_uni += data_dict[data]['union_sale']['NILGIRIS Union']["tm"]
                  sm500_nils_uni += data_dict[data]['union_sale']['NILGIRIS Union']["std500"]
                  sm250_nils_uni += data_dict[data]['union_sale']['NILGIRIS Union']["std250"]
                  fcm_nils_uni += data_dict[data]['union_sale']['NILGIRIS Union']["fcm"]
                  tea_nils_uni += data_dict[data]['union_sale']['NILGIRIS Union']["tmate"]

                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-54,y_axis+20,x_axis-54,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              elif stock_name == "CBE Union Total":
                  mycanvas.setFont('Helvetica', 7)
                  
                  tm = data_dict[data]['Coimbatore Account']['Agent Cash']["tm"] + data_dict[data]['Coimbatore Account']['Agent Card']["tm"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["tm"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["tm"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["tm"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["tm"] + data_dict[data]['union_sale']['NILGIRIS Union']["tm"]
                  std500 = data_dict[data]['Coimbatore Account']['Agent Cash']["std500"] + data_dict[data]['Coimbatore Account']['Agent Card']["std500"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["std500"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["std500"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["std500"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["std500"] + data_dict[data]['union_sale']['NILGIRIS Union']["std500"]
                  std250 = data_dict[data]['Coimbatore Account']['Agent Cash']["std250"] + data_dict[data]['Coimbatore Account']['Agent Card']["std250"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["std250"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["std250"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["std250"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["std250"] + data_dict[data]['union_sale']['NILGIRIS Union']["std250"]
                  fcm = data_dict[data]['Coimbatore Account']['Agent Cash']["fcm"] + data_dict[data]['Coimbatore Account']['Agent Card']["fcm"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["fcm"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["fcm"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["fcm"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["fcm"] + data_dict[data]['union_sale']['NILGIRIS Union']["fcm"]
                  tea = data_dict[data]['Coimbatore Account']['Agent Cash']["tmate"] + data_dict[data]['Coimbatore Account']['Agent Card']["tmate"] + data_dict[data]['Coimbatore Account']['Union Booth Cash']["tmate"] + data_dict[data]['Coimbatore Account']['Union Booth Card']["tmate"] + data_dict[data]['Coimbatore Account']['Pvt Institutes']["tmate"] + data_dict[data]['Coimbatore Account']['Govt Institutes']["tmate"] + data_dict[data]['union_sale']['NILGIRIS Union']["tmate"]
                  smcan = data_dict[data]['Coimbatore Account']['Agent Cash']["smcan"]
                  fcmcan = data_dict[data]['Coimbatore Account']['Agent Cash']["fcmcan"]

                  cbe_uni += tm+std500+std250+fcm+fcmcan+smcan+tea
                  tm_cbe_uni += tm
                  sm500_cbe_uni += std500
                  sm250_cbe_uni += std250
                  fcm_cbe_uni += fcm
                  tea_cbe_uni += tea
                  smcan_cbe_uni += smcan
                  fcmcan_cbe_uni += fcmcan
                  
                  mycanvas.drawRightString(x_axis-9,y_axis-60,str(tm))
                  mycanvas.drawRightString(x_axis-9,y_axis-75,str(std500))
                  mycanvas.drawRightString(x_axis-9,y_axis-90,str(std250))
                  mycanvas.drawRightString(x_axis-9,y_axis-105,str(fcm))
                  mycanvas.drawRightString(x_axis-9,y_axis-120,str(tea))
                  mycanvas.drawRightString(x_axis-9,y_axis-135,str(smcan))
                  mycanvas.drawRightString(x_axis-9,y_axis-150,str(fcmcan))
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-50,y_axis+20,x_axis-50,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
  
              # cbe union amount
              
              elif stock_name == "Agent Cash Amount":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-5+6,y_axis-60,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tm"]))
                  mycanvas.drawRightString(x_axis-5+6,y_axis-75,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std500"]))
                  mycanvas.drawRightString(x_axis-5+6,y_axis-90,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std250"]))
                  mycanvas.drawRightString(x_axis-5+6,y_axis-105,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["fcm"]))
                  mycanvas.drawRightString(x_axis-5+6,y_axis-120,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tmate"]))

                  agnt_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tmate"]
                  
                  tm_agnt_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tm"]
                  sm500_agnt_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std500"]
                  sm250_agnt_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std250"]
                  fcm_agnt_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["fcm"]
                  tea_agnt_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tmate"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-46+6,y_axis+20,x_axis-46+6,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              elif stock_name == "Agent Card Amount":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-3+8,y_axis-60,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tm"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-75,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std500"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-90,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std250"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-105,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["fcm"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-120,str(data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tmate"]))
                  
                  agnt_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tmate"]
                  
                  tm_agnt_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tm"]
                  sm500_agnt_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std500"]
                  sm250_agnt_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std250"]
                  fcm_agnt_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["fcm"]
                  tea_agnt_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tmate"]

                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-44+8,y_axis+20,x_axis-44+8,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Union Booth Cash Amount":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-3+8,y_axis-60,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tm"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-75,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std500"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-90,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std250"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-105,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["fcm"]))
                  mycanvas.drawRightString(x_axis-3+8,y_axis-120,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tmate"]))

                  uni_bth_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std500"]+ data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tmate"]
                  
                  tm_uni_bth_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tm"]
                  sm500_uni_bth_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std500"]
                  sm250_uni_bth_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std250"]
                  fcm_uni_bth_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["fcm"]
                  tea_uni_bth_csh_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tmate"]

                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-44+8,y_axis+20,x_axis-44+8,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Union Booth Card Amount":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-9+8,y_axis-60,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tm"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-75,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std500"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-90,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std250"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-105,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["fcm"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-120,str(data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tmate"]))

                  uni_bth_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tmate"]
                  
                  tm_uni_bth_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tm"]
                  sm500_uni_bth_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std500"]
                  sm250_uni_bth_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std250"]
                  fcm_uni_bth_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["fcm"]
                  tea_uni_bth_crd_amt += data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tmate"]

                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-50+8,y_axis+20,x_axis-50+8,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Pvt Ins Amount":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-9+8,y_axis-60,str(data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tm"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-75,str(data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std500"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-90,str(data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std250"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-105,str(data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["fcm"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-120,str(data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tmate"]))
                  
                  pvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tmate"]
                  
                  tm_pvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tm"]
                  sm500_pvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std500"]
                  sm250_pvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std250"]
                  fcm_pvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["fcm"]
                  tea_pvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tmate"]

                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-50+8,y_axis+20,x_axis-50+8,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
                  
              elif stock_name == "Govt Ins Amount":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-9+8,y_axis-60,str(data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tm"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-75,str(data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std500"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-90,str(data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std250"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-105,str(data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["fcm"]))
                  mycanvas.drawRightString(x_axis-9+8,y_axis-120,str(data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tmate"]))
                  
                  gvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tmate"]
                  
                  tm_gvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tm"]
                  sm500_gvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std500"]
                  sm250_gvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std250"]
                  fcm_gvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["fcm"]
                  tea_gvt_ins_amt += data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tmate"]
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-50+8,y_axis+20,x_axis-50+8,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              elif stock_name == "Nilgiris Union Amount":
                  mycanvas.setFont('Helvetica', 7)
                  mycanvas.drawRightString(x_axis-7+8,y_axis-60,str(data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tm"]))
                  mycanvas.drawRightString(x_axis-7+8,y_axis-75,str(data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std500"]))
                  mycanvas.drawRightString(x_axis-7+8,y_axis-90,str(data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std250"]))
                  mycanvas.drawRightString(x_axis-7+8,y_axis-105,str(data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["fcm"]))
                  mycanvas.drawRightString(x_axis-7+8,y_axis-120,str(data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tmate"]))
                  
                  nils_uni_amt += data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tm"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std500"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std250"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["fcm"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tmate"]
                  
                  tm_nils_uni_amt += data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tm"]
                  sm500_nils_uni_amt += data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std500"]
                  sm250_nils_uni_amt += data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std250"]
                  fcm_nils_uni_amt += data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["fcm"]
                  tea_nils_uni_amt += data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tmate"]

                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-40,y_axis+20,x_axis-40,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              elif stock_name == "CBE Union Total Amount":
                  mycanvas.setFont('Helvetica', 7)
                  
                  tm = data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tm"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tm"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tm"]
                  std500 = data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std500"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std500"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std500"]
                  std250 = data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["std250"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["std250"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["std250"]
                  fcm = data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["fcm"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["fcm"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["fcm"]
                  tea = data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["tmate"] + data_dict[data]["Costs"]['Coimbatore Account']['Agent Card']["tmate"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Cash']["tmate"] + data_dict[data]["Costs"]['Coimbatore Account']['Union Booth Card']["tmate"] + data_dict[data]["Costs"]['Coimbatore Account']['Pvt Institutes']["tmate"] + data_dict[data]["Costs"]['Coimbatore Account']['Govt Institutes']["tmate"] + data_dict[data]["Costs"]['union_sale']['NILGIRIS Union']["tmate"]
                  smcan = data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["smcan"]
                  fcmcan = data_dict[data]["Costs"]['Coimbatore Account']['Agent Cash']["fcmcan"]

                  cbe_uni_amt += tm + std500 +std250 + fcm + smcan + fcmcan + tea
                  
                  tm_cbe_uni_amt += tm
                  sm500_cbe_uni_amt += std500
                  sm250_cbe_uni_amt += std250
                  fcm_cbe_uni_amt += fcm
                  tea_cbe_uni_amt += tea
                  smcan_cbe_uni_amt += smcan
                  fcmcan_cbe_uni_amt += fcmcan
                  
                  mycanvas.drawRightString(x_axis+12,y_axis-60,str(tm))
                  mycanvas.drawRightString(x_axis+12,y_axis-75,str(std500))
                  mycanvas.drawRightString(x_axis+12,y_axis-90,str(std250))
                  mycanvas.drawRightString(x_axis+12,y_axis-105,str(fcm))
                  mycanvas.drawRightString(x_axis+12,y_axis-120,str(tea))
                  mycanvas.drawRightString(x_axis+12,y_axis-135,str(smcan))
                  mycanvas.drawRightString(x_axis+12,y_axis-150,str(fcmcan))
                  
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-28,y_axis+20,x_axis-28,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)
              
              else:
                  x_axis += (x_total_len/len_adjust)
                  mycanvas.line(x_axis-28,y_axis+20,x_axis-28,y_axis-145)
                  mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-145)  
          y_axis -= 95
          if sl_no % 7 == 0:
              mycanvas.line(x_axis_line,y_axis-50,x_total_len+10,y_axis-50)
              mycanvas.showPage()
              
              mycanvas.setFont('Helvetica', 15)
              mycanvas.drawCentredString(560, 740+100, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
              mycanvas.drawCentredString(560, 720+100, 'Report 3')
              
              mycanvas.setLineWidth(0)
              x_total_len = 1060
              x_axis = 40
              x_axis_line = 10
              y_axis = 670+120
              y_axis_line = 690+120
              key_no = 0
              mycanvas.setFont('Helvetica', 11)
#                 head_list = ["Date","Milk","Resived From Diary","Leak Ltr","Returnd","Net Recived","Tiruppur Union","Chennai Union","Other Union Total","Agent Cash","Agent Card","Union Booth Cash","Union Booth Card","Pvt Ins","Govt Ins","Nilgiris Union","CBE Union Total","Agent Cash Amount","Agent Card Amount","Union Booth Cash Amount","Union Booth Card Amount","Pvt Ins Amount","Govt Ins Amount","Nilgiris Union Amount","CBE Union Total Amount"]
              len_adjust=len(head_list)


          # for tabe header

              mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
              mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
              for stock_name in head_list:
                  data_name = ""
                  data_2nd_name = ""
                  data_3rd_name = ""
                  data = stock_name.split(" ")

                  if data[0] == "" :
                      data.remove(data[0])

                  if data[-1] == "":
                      data.remove(data[-1])

                  if len(data) == 1:
                      data_name += data[0]

                  if len(data) == 2:
                      data_name += data[0]
                      data_2nd_name += data[1]

                  if len(data) == 3:
                      data_name += data[0]
                      data_2nd_name += data[1]
                      data_3rd_name += data[-1]

                  if len(data) == 4:
                      data_name += data[0]
                      data_2nd_name += data[1]
                      data_3rd_name += data[2]
                  mycanvas.setFont('Helvetica', 11)

                  if stock_name == "Milk":
                      mycanvas.drawCentredString(x_axis-17,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-17,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-17,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Resived From Diary":
                      mycanvas.drawCentredString(x_axis-25,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-25,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-25,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Leakage":
                      mycanvas.drawCentredString(x_axis-25,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-25,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-25,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Return":
                      mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Net Recived":
                      mycanvas.drawCentredString(x_axis-34,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-34,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-34,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Tiruppur":
                      mycanvas.drawCentredString(x_axis-30+1,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-30+1,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-30+1,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Chennai":
                      mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Other Union Total":
                      mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Agent Cash":
                      mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Agent Card":
                      mycanvas.drawCentredString(x_axis-30,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-30,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Union Booth Cash":
                      mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Union Booth Card":
                      mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Pvt Ins":
                      mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-30,str('NCB'))

                  elif stock_name == "Govt Ins":
                      mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Nilgiris":
                      mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))

                  elif stock_name == "CBE Union Total":
                      mycanvas.drawCentredString(x_axis-32,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-32,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Agent Cash Amount":
                      mycanvas.drawCentredString(x_axis-27,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-27,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-27,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Agent Card Amount":
                      mycanvas.drawCentredString(x_axis-15,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-15,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-15,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Union Booth Cash Amount":
                      mycanvas.drawCentredString(x_axis-15,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-15,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-15,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Union Booth Card Amount":
                      mycanvas.drawCentredString(x_axis-15,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-15,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-15,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Pvt Ins Amount":
                      mycanvas.drawCentredString(x_axis-20,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-20,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-20,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Govt Ins Amount":
                      mycanvas.drawCentredString(x_axis-20,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-20,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-20,y_axis-30,str(data_3rd_name))

                  elif stock_name == "Nilgiris Union Amount":
                      mycanvas.drawCentredString(x_axis-17,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-17,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-17,y_axis-30,str(data_3rd_name))

                  elif stock_name == "CBE Union Total Amount":
                      mycanvas.drawCentredString(x_axis-17,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-17,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-17,y_axis-30,str(data_3rd_name))

                  else:
                      mycanvas.drawCentredString(x_axis-5,y_axis,str(data_name))
                      mycanvas.drawCentredString(x_axis-5,y_axis-15,str(data_2nd_name))
                      mycanvas.drawCentredString(x_axis-5,y_axis-30,str(data_3rd_name))

                  x_axis += (x_total_len/len_adjust)
          sl_no +=1
          
          
          
  #sub totals
  # lines_between_total
  
  mycanvas.line(x_axis_line,y_axis-50,x_total_len+12,y_axis-50)
  mycanvas.line(x_axis_line,y_axis-50,x_axis_line,y_axis-140)
  mycanvas.line(x_total_len+12,y_axis-50,x_total_len+12,y_axis-140)
#     mycanvas.line(x_axis_line,y_axis-70,x_total_len+12,y_axis-70)
  
  mycanvas.setFont('Helvetica', 12)
  mycanvas.drawString(x_axis_line+5,y_axis-65,"TM")
  mycanvas.drawString(x_axis_line+5,y_axis-80,"STD500")
  mycanvas.drawString(x_axis_line+5,y_axis-95,"STD250")
  mycanvas.drawString(x_axis_line+5,y_axis-110,"FCM")
  mycanvas.drawString(x_axis_line+5,y_axis-125,"TMATE")
  mycanvas.drawString(x_axis-25,y_axis-140,"SMCAN")
  mycanvas.drawString(x_axis-25,y_axis-150,"FCMCAN")
  mycanvas.setFont('Helvetica', 7)
  
  mycanvas.line(x_axis_line+66.5,y_axis-50,x_axis_line+66.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-65,str(tm_diary_tot))
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-80,str(sm500_diary_tot))
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-95,str(sm250_diary_tot))
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-110,str(fcm_diary_tot))
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-125,str(tea_diary_tot))
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-140,str(sm_can_diary_tot ))
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-150,str(fcm_can_diary_tot))
  
  mycanvas.line(x_axis_line+114.5,y_axis-50,x_axis_line+114.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+149,y_axis-65,str(tm_leak))
  mycanvas.drawRightString(x_axis_line+149,y_axis-80,str(sm500_leak))
  mycanvas.drawRightString(x_axis_line+149,y_axis-95,str(sm250_leak))
  mycanvas.drawRightString(x_axis_line+149,y_axis-110,str(fcm_leak))
  mycanvas.drawRightString(x_axis_line+149,y_axis-125,str(tea_leak))
  
  mycanvas.line(x_axis_line+151.5,y_axis-50,x_axis_line+151.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+181,y_axis-65,str(tm_rtnd))
  mycanvas.drawRightString(x_axis_line+181,y_axis-80,str(sm500_rtnd))
  mycanvas.drawRightString(x_axis_line+181,y_axis-95,str(sm250_rtnd))
  mycanvas.drawRightString(x_axis_line+181,y_axis-110,str(fcm_rtnd))
  mycanvas.drawRightString(x_axis_line+181,y_axis-125,str(tea_rtnd))
  
  mycanvas.line(x_axis_line+183,y_axis-50,x_axis_line+183,y_axis-140)
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-65,str(tm_net_rec))
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-80,str(sm500_net_rec))
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-95,str(sm250_net_rec))
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-110,str(fcm_net_rec))
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-125,str(tea_net_rec))
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-140,str(sm_can_net_tot ))
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-155,str(fcm_can_net_tot))
  
  mycanvas.line(x_axis_line+232.5,y_axis-50,x_axis_line+232.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+275.5,y_axis-65,str(tm_trp_uni))
  mycanvas.drawRightString(x_axis_line+275.5,y_axis-80,str(sm500_trp_uni))
  mycanvas.drawRightString(x_axis_line+275.5,y_axis-95,str(sm250_trp_uni))
  mycanvas.drawRightString(x_axis_line+275.5,y_axis-110,str(fcm_trp_uni))
  mycanvas.drawRightString(x_axis_line+275.5,y_axis-125,str(tea_trp_uni))
  
  mycanvas.line(x_axis_line+276.5,y_axis-50,x_axis_line+276.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+316.5,y_axis-65,str(tm_chni_uni))
  mycanvas.drawRightString(x_axis_line+316.5,y_axis-80,str(sm500_chni_uni))
  mycanvas.drawRightString(x_axis_line+316.5,y_axis-95,str(sm250_chni_uni))
  mycanvas.drawRightString(x_axis_line+316.5,y_axis-110,str(fcm_chni_uni))
  mycanvas.drawRightString(x_axis_line+316.5,y_axis-125,str(tea_chni_uni))
  
  mycanvas.line(x_axis_line+317.5,y_axis-50,x_axis_line+317.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+358.5,y_axis-65,str(tm_oth_uni))
  mycanvas.drawRightString(x_axis_line+358.5,y_axis-80,str(sm500_oth_uni))
  mycanvas.drawRightString(x_axis_line+358.5,y_axis-95,str(sm250_oth_uni))
  mycanvas.drawRightString(x_axis_line+358.5,y_axis-110,str(fcm_oth_uni))
  mycanvas.drawRightString(x_axis_line+358.5,y_axis-125,str(tea_oth_uni))
  
  mycanvas.line(x_axis_line+359.5,y_axis-50,x_axis_line+359.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+403,y_axis-65,str(tm_agnt_csh))
  mycanvas.drawRightString(x_axis_line+403,y_axis-80,str(sm500_agnt_csh))
  mycanvas.drawRightString(x_axis_line+403,y_axis-95,str(sm250_agnt_csh))
  mycanvas.drawRightString(x_axis_line+403,y_axis-110,str(fcm_agnt_csh))
  mycanvas.drawRightString(x_axis_line+403,y_axis-125,str(tea_agnt_csh))
  
  mycanvas.line(x_axis_line+404,y_axis-50,x_axis_line+404,y_axis-140)
  mycanvas.drawRightString(x_axis_line+445.5,y_axis-65,str(tm_agnt_crd))
  mycanvas.drawRightString(x_axis_line+445.5,y_axis-80,str(sm500_agnt_crd))
  mycanvas.drawRightString(x_axis_line+445.5,y_axis-95,str(sm250_agnt_crd))
  mycanvas.drawRightString(x_axis_line+445.5,y_axis-110,str(fcm_agnt_crd))
  mycanvas.drawRightString(x_axis_line+445.5,y_axis-125,str(tea_agnt_crd))
  
  mycanvas.line(x_axis_line+446.5,y_axis-50,x_axis_line+446.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+486,y_axis-65,str(tm_uni_bth_csh))
  mycanvas.drawRightString(x_axis_line+486,y_axis-80,str(sm500_uni_bth_csh))
  mycanvas.drawRightString(x_axis_line+486,y_axis-95,str(sm250_uni_bth_csh))
  mycanvas.drawRightString(x_axis_line+486,y_axis-110,str(fcm_uni_bth_csh))
  mycanvas.drawRightString(x_axis_line+486,y_axis-125,str(tea_uni_bth_csh))
  
  mycanvas.line(x_axis_line+487,y_axis-50,x_axis_line+487,y_axis-140)
  mycanvas.drawRightString(x_axis_line+528,y_axis-65,str(tm_uni_bth_crd))
  mycanvas.drawRightString(x_axis_line+528,y_axis-80,str(sm500_uni_bth_crd))
  mycanvas.drawRightString(x_axis_line+528,y_axis-95,str(sm250_uni_bth_crd))
  mycanvas.drawRightString(x_axis_line+528,y_axis-110,str(fcm_uni_bth_crd))
  mycanvas.drawRightString(x_axis_line+528,y_axis-125,str(tea_uni_bth_crd))
  
  mycanvas.line(x_axis_line+529,y_axis-50,x_axis_line+529,y_axis-140)
  mycanvas.drawRightString(x_axis_line+568.5,y_axis-65,str(tm_pvt_ins))
  mycanvas.drawRightString(x_axis_line+568.5,y_axis-80,str(sm500_pvt_ins))
  mycanvas.drawRightString(x_axis_line+568.5,y_axis-95,str(sm250_pvt_ins))
  mycanvas.drawRightString(x_axis_line+568.5,y_axis-110,str(fcm_pvt_ins))
  mycanvas.drawRightString(x_axis_line+568.5,y_axis-125,str(tea_pvt_ins))
  
  mycanvas.line(x_axis_line+569.5,y_axis-50,x_axis_line+569.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+611,y_axis-65,str(tm_gvt_ins))
  mycanvas.drawRightString(x_axis_line+611,y_axis-80,str(sm500_gvt_ins))
  mycanvas.drawRightString(x_axis_line+611,y_axis-95,str(sm250_gvt_ins))
  mycanvas.drawRightString(x_axis_line+611,y_axis-110,str(fcm_gvt_ins))
  mycanvas.drawRightString(x_axis_line+611,y_axis-125,str(tea_gvt_ins))

  mycanvas.line(x_axis_line+612,y_axis-50,x_axis_line+612,y_axis-140)
  mycanvas.drawRightString(x_axis_line+653.5,y_axis-65,str(tm_nils_uni))
  mycanvas.drawRightString(x_axis_line+653.5,y_axis-80,str(sm500_nils_uni))
  mycanvas.drawRightString(x_axis_line+653.5,y_axis-95,str(sm250_nils_uni))
  mycanvas.drawRightString(x_axis_line+653.5,y_axis-110,str(fcm_nils_uni))
  mycanvas.drawRightString(x_axis_line+653.5,y_axis-125,str(tea_nils_uni))

  
  mycanvas.line(x_axis_line+654.5,y_axis-50,x_axis_line+654.5,y_axis-140)
  mycanvas.drawRightString(x_axis_line+700,y_axis-65,str(tm_cbe_uni))
  mycanvas.drawRightString(x_axis_line+700,y_axis-80,str(sm500_cbe_uni))
  mycanvas.drawRightString(x_axis_line+700,y_axis-95,str(sm250_cbe_uni))
  mycanvas.drawRightString(x_axis_line+700,y_axis-110,str(fcm_cbe_uni))
  mycanvas.drawRightString(x_axis_line+700,y_axis-125,str(tea_cbe_uni))
  mycanvas.drawRightString(x_axis_line+700,y_axis-140,str(smcan_cbe_uni))
  mycanvas.drawRightString(x_axis_line+700,y_axis-150,str(fcmcan_cbe_uni))
  
  mycanvas.line(x_axis_line+701,y_axis-50,x_axis_line+701,y_axis-140)
  mycanvas.drawRightString(x_axis_line+746+6,y_axis-65,str(tm_agnt_csh_amt))
  mycanvas.drawRightString(x_axis_line+746+6,y_axis-80,str(sm500_agnt_csh_amt))
  mycanvas.drawRightString(x_axis_line+746+6,y_axis-95,str(sm250_agnt_csh_amt))
  mycanvas.drawRightString(x_axis_line+746+6,y_axis-110,str(fcm_agnt_csh_amt))
  mycanvas.drawRightString(x_axis_line+746+6,y_axis-125,str(tea_agnt_csh_amt))

  mycanvas.line(x_axis_line+747+6,y_axis-50,x_axis_line+747+6,y_axis-140)
  mycanvas.drawRightString(x_axis_line+790.5+8,y_axis-65,str(tm_agnt_crd_amt))
  mycanvas.drawRightString(x_axis_line+790.5+8,y_axis-80,str(sm500_agnt_crd_amt))
  mycanvas.drawRightString(x_axis_line+790.5+8,y_axis-95,str(sm250_agnt_crd_amt))
  mycanvas.drawRightString(x_axis_line+790.5+8,y_axis-110,str(fcm_agnt_crd_amt))
  mycanvas.drawRightString(x_axis_line+790.5+8,y_axis-125,str(tea_agnt_crd_amt))
  
  mycanvas.line(x_axis_line+791.5+8,y_axis-50,x_axis_line+791.5+8,y_axis-140)
  mycanvas.drawRightString(x_axis_line+833+8,y_axis-65,str(uni_bth_csh_amt))
  
  mycanvas.line(x_axis_line+834+8,y_axis-50,x_axis_line+834+8,y_axis-140)
  mycanvas.drawRightString(x_axis_line+869.5+8,y_axis-65,str(tm_uni_bth_crd_amt))
  mycanvas.drawRightString(x_axis_line+869.5+8,y_axis-80,str(sm500_uni_bth_crd_amt))
  mycanvas.drawRightString(x_axis_line+869.5+8,y_axis-95,str(sm250_uni_bth_crd_amt))
  mycanvas.drawRightString(x_axis_line+869.5+8,y_axis-110,str(fcm_uni_bth_crd_amt))
  mycanvas.drawRightString(x_axis_line+869.5+8,y_axis-125,str(tea_uni_bth_crd_amt))
  
  mycanvas.line(x_axis_line+870.5+8,y_axis-50,x_axis_line+870.5+8,y_axis-140)
  mycanvas.drawRightString(x_axis_line+911.5+8,y_axis-65,str(tm_pvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+911.5+8,y_axis-80,str(sm500_pvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+911.5+8,y_axis-95,str(sm250_pvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+911.5+8,y_axis-110,str(fcm_pvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+911.5+8,y_axis-125,str(tea_pvt_ins_amt))
  
  mycanvas.line(x_axis_line+912.5+8,y_axis-50,x_axis_line+912.5+8,y_axis-140)
  mycanvas.drawRightString(x_axis_line+954.5+8,y_axis-65,str(tm_gvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+954.5+8,y_axis-80,str(sm500_gvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+954.5+8,y_axis-95,str(sm250_gvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+954.5+8,y_axis-110,str(fcm_gvt_ins_amt))
  mycanvas.drawRightString(x_axis_line+954.5+8,y_axis-125,str(tea_gvt_ins_amt))

  mycanvas.line(x_axis_line+955.5+8,y_axis-50,x_axis_line+955.5+8,y_axis-140)
  mycanvas.drawRightString(x_axis_line+998.5+8,y_axis-65,str(tm_nils_uni_amt))
  mycanvas.drawRightString(x_axis_line+998.5+8,y_axis-80,str(sm500_nils_uni_amt))
  mycanvas.drawRightString(x_axis_line+998.5+8,y_axis-95,str(sm250_nils_uni_amt))
  mycanvas.drawRightString(x_axis_line+998.5+8,y_axis-110,str(fcm_nils_uni_amt))
  mycanvas.drawRightString(x_axis_line+998.5+8,y_axis-125,str(tea_nils_uni_amt))

  mycanvas.line(x_axis_line+999.5+8,y_axis-50,x_axis_line+999.5+8,y_axis-140)
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-65,str(tm_cbe_uni_amt))
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-80,str(sm500_cbe_uni_amt))
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-95,str(sm250_cbe_uni_amt))
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-110,str(fcm_cbe_uni_amt))
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-125,str(tea_cbe_uni_amt))
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-140,str(smcan_cbe_uni_amt))
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-150,str(fcmcan_cbe_uni_amt))
  
  
  #------------------------------------
  y_axis -= 95
  #line_total
  mycanvas.line(x_axis_line,y_axis-50,x_total_len+12,y_axis-50)
  mycanvas.line(x_axis_line,y_axis-50,x_axis_line,y_axis-70)
  mycanvas.line(x_total_len+12,y_axis-50,x_total_len+12,y_axis-70)
  mycanvas.line(x_axis_line,y_axis-70,x_total_len+12,y_axis-70)
  
  
  # lines_between_total
  mycanvas.setFont('Helvetica', 11)
  mycanvas.drawRightString(x_axis_line+50,y_axis-65,"Total")
  mycanvas.setFont('Helvetica', 7)
  
  mycanvas.line(x_axis_line+66.5,y_axis-50,x_axis_line+66.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+113.5,y_axis-65,str(diary_tot))
  
  mycanvas.line(x_axis_line+114.5,y_axis-50,x_axis_line+114.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+149,y_axis-65,str(leak))
  
  mycanvas.line(x_axis_line+151.5,y_axis-50,x_axis_line+151.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+181,y_axis-65,str(rtnd))
  
  mycanvas.line(x_axis_line+183,y_axis-50,x_axis_line+183,y_axis-70)
  mycanvas.drawRightString(x_axis_line+231.5,y_axis-65,str(net_rec))
  
  mycanvas.line(x_axis_line+232.5,y_axis-50,x_axis_line+232.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+275.5,y_axis-65,str(trp_uni))
  
  mycanvas.line(x_axis_line+276.5,y_axis-50,x_axis_line+276.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+316.5,y_axis-65,str(chni_uni))
  
  mycanvas.line(x_axis_line+317.5,y_axis-50,x_axis_line+317.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+358.5,y_axis-65,str(oth_uni))
  
  mycanvas.line(x_axis_line+359.5,y_axis-50,x_axis_line+359.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+403,y_axis-65,str(agnt_csh))
  
  mycanvas.line(x_axis_line+404,y_axis-50,x_axis_line+404,y_axis-70)
  mycanvas.drawRightString(x_axis_line+445.5,y_axis-65,str(agnt_crd))
  
  mycanvas.line(x_axis_line+446.5,y_axis-50,x_axis_line+446.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+486,y_axis-65,str(uni_bth_csh))
  
  mycanvas.line(x_axis_line+487,y_axis-50,x_axis_line+487,y_axis-70)
  mycanvas.drawRightString(x_axis_line+528,y_axis-65,str(uni_bth_crd))
  
  mycanvas.line(x_axis_line+529,y_axis-50,x_axis_line+529,y_axis-70)
  mycanvas.drawRightString(x_axis_line+568.5,y_axis-65,str(pvt_ins))
  
  mycanvas.line(x_axis_line+569.5,y_axis-50,x_axis_line+569.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+611,y_axis-65,str(gvt_ins))
  
  mycanvas.line(x_axis_line+612,y_axis-50,x_axis_line+612,y_axis-70)
  mycanvas.drawRightString(x_axis_line+653.5,y_axis-65,str(nils_uni))
  
  mycanvas.line(x_axis_line+654.5,y_axis-50,x_axis_line+654.5,y_axis-70)
  mycanvas.drawRightString(x_axis_line+700,y_axis-65,str(cbe_uni))
  
  mycanvas.line(x_axis_line+701,y_axis-50,x_axis_line+701,y_axis-70)
  mycanvas.drawRightString(x_axis_line+746+6,y_axis-65,str(agnt_csh_amt))
  
  mycanvas.line(x_axis_line+747+6,y_axis-50,x_axis_line+747+6,y_axis-70)
  mycanvas.drawRightString(x_axis_line+790.5+8,y_axis-65,str(agnt_crd_amt))
  
  mycanvas.line(x_axis_line+791.5+8,y_axis-50,x_axis_line+791.5+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+833+8,y_axis-65,str(uni_bth_csh_amt))
  
  mycanvas.line(x_axis_line+834+8,y_axis-50,x_axis_line+834+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+869.5+8,y_axis-65,str(uni_bth_crd_amt))
  
  mycanvas.line(x_axis_line+870.5+8,y_axis-50,x_axis_line+870.5+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+911.5+8,y_axis-65,str(pvt_ins_amt))
  
  mycanvas.line(x_axis_line+912.5+8,y_axis-50,x_axis_line+912.5+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+954.5+8,y_axis-65,str(gvt_ins_amt))
  
  mycanvas.line(x_axis_line+955.5+8,y_axis-50,x_axis_line+955.5+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+998.5+8,y_axis-65,str(nils_uni_amt))
  
  mycanvas.line(x_axis_line+999.5+8,y_axis-50,x_axis_line+999.5+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+1060.5,y_axis-65,str(cbe_uni_amt))

  mycanvas.line(x_axis_line+1050.5+8,y_axis-50,x_axis_line+1050.5+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+1095.5+8,y_axis-65,str(nils_uni_amt))
  
  mycanvas.line(x_axis_line+1100.5+8,y_axis-50,x_axis_line+1100.5+8,y_axis-70)
  mycanvas.drawRightString(x_axis_line+1155.5,y_axis-65,str(cbe_uni_amt))
  
  mycanvas.save()

  document = {}
  document['file_name'] = file_name
  try:
    image_path = file_path
    with open(image_path, 'rb') as image_file:
        encoded_image = b64encode(image_file.read())
        document['pdf'] = encoded_image
  except Exception as err:
      print(err)
  return document



@api_view(['POST'])
def serve_account_section_online_payment_report(request):
  print(request.data)
  date = request.data['selected_date']
  if request.data['selected_session_id'] == 'both':
    session_list = [1,2]
  else:
    print([request.data['selected_session_id']])
    session_list = [request.data['selected_session_id']]
  
  data_dict = {}
  data_dict2 = {}
  
  date_time_obj = datetime.strptime(date,'%Y-%m-%d')
  next_date = date_time_obj + timedelta(days=1)
  next_date = str(next_date)[:10]
                 
  sale_groups = SaleGroup.objects.filter(time_created__date=date,session_id__in=session_list,business__business_type_id__in=[1,2,9,11,12,15],ordered_via_id__in=[1,3]).order_by("business__zone","business__id",'date')
  dates = []
  for sale_group in sale_groups:
      if not sale_group.date in data_dict:
          data_dict[sale_group.date] = {}
          dates.append(sale_group.date)
      if not sale_group.business_id in data_dict[sale_group.date]:
          data_dict[sale_group.date][sale_group.business_id] = {
              "business_code": sale_group.business.code,
              "zone":sale_group.zone.name,
              "agent_code" : BusinessAgentMap.objects.get(business_id=sale_group.business_id).agent.agent_code,
              "agent_name" : BusinessAgentMap.objects.get(business_id=sale_group.business_id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=sale_group.business_id).agent.last_name,
              "sale_for_date": sale_group.date,
              "total_cost" : 0,
          }
      data_dict[sale_group.date][sale_group.business_id]["total_cost"] += sale_group.total_cost
      
      
  next_day_sale_groups = SaleGroup.objects.filter(date=next_date,session_id__in=session_list,business__business_type_id__in=[1,2,9,11,12,15],ordered_via_id__in=[1,3]).order_by("business__zone","business__id",'date').exclude(time_created__date=date)
  
  for sale_group in next_day_sale_groups:
      if not sale_group.business_id in data_dict2:
          data_dict2[sale_group.business_id] = {
              "business_code": sale_group.business.code,
              "zone":sale_group.zone.name,
              "agent_code" : BusinessAgentMap.objects.get(business_id=sale_group.business_id).agent.agent_code,
              "agent_name" : BusinessAgentMap.objects.get(business_id=sale_group.business_id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=sale_group.business_id).agent.last_name,
              "sale_for_date": sale_group.time_created.strftime("%d-%m-%Y"),
              "total_cost" : 0,
          }
      data_dict2[sale_group.business_id]["total_cost"] += sale_group.total_cost
  
  data = create_canvas_report_for_account_section_online_payment_report(date,session_list,data_dict,data_dict2,next_date)
  return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_report_for_account_section_online_payment_report(date,session_list,data_dict,data_dict2,next_date):
    session_name = ''
   
    if len(session_list) == 2:
        session_name = "Both"
    else:
        for session in session_list:
            if session == 1 or session == '1':
                session_name += "Morning"
            else:
                session_name += "Evening"
           
   
    file_name = "sale_for_date" + '_( ' + str(date)+ ' ).pdf'
    file_path = os.path.join('static/media/', file_name)

    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    light_color = 0x000000
    dark_color = 0x000000

    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)

    #Date
    mycanvas.setLineWidth(0)
    date = datetime.strptime(date, '%Y-%m-%d')
    sale_date = datetime.strftime(date, '%d/%m/%Y')
    mycanvas.drawString(15, 800, "Accounts : 1" )
    mycanvas.line(15, 797, 85, 797)
    mycanvas.line(15, 796, 85, 796)
    
    mycanvas.drawCentredString(300, 800, "Agent Online Order On : " + str(sale_date) +" - "+str(session_name)+" "+"Shift")

    
    mycanvas.line(406-100-150, 797, 593-200+50, 797)
   
    #Header
    head_y = 770
    head_x = 40
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(head_x-18,head_y,"Sl.")
    mycanvas.drawString(head_x-18,head_y-15,"No")
   
    mycanvas.drawString(head_x+12,head_y,"Booth")
    mycanvas.drawString(head_x+12,head_y-15,"Code")
   
    mycanvas.drawString(head_x+70,head_y,"Zone")
   
    mycanvas.drawString(head_x+135,head_y,"Agent")
    mycanvas.drawString(head_x+135,head_y-15,"Code")
   
    mycanvas.drawString(head_x+250,head_y,"Agent Name")
#     mycanvas.drawString(head_x+240,head_y-15,"Name")
   
    mycanvas.drawString(head_x+385,head_y,"Delivery For")
#     mycanvas.drawString(head_x+362,head_y-15,"   Date")
   
    mycanvas.drawString(head_x+480,head_y,"Amount")
   
    mycanvas.line(head_x-25,head_y+15,head_x+545,head_y+15)
    mycanvas.line(head_x-25,head_y-20,head_x+545,head_y-20)
   
    x = 60
    y = 750
    sl_no = 1
    total = 0
   
    for dates in data_dict:
        # date = datetime.strptime(dates,'%Y-%m-%d')
        date = str(dates)[:10]
        if date == next_date:
            for data in data_dict[dates]:
                if data_dict[dates][data]["total_cost"] == 0:
                    continue
                mycanvas.setFont('Helvetica', 10)
                mycanvas.drawRightString(x-20,y-20,str(sl_no))
                mycanvas.drawString(x-10,y-20,str(data_dict[dates][data]["business_code"]))
                mycanvas.drawString(x+45,y-20,str(data_dict[dates][data]["zone"])[:8])
                mycanvas.drawString(x+100,y-20,str(data_dict[dates][data]["agent_code"]))
                mycanvas.drawString(x+180,y-20,str(data_dict[dates][data]["agent_name"])[:28])
            
                order_for_date = datetime.strptime(str(data_dict[dates][data]["sale_for_date"]), '%Y-%m-%d')
            
                mycanvas.drawString(x+375,y-20,str(datetime.strftime(order_for_date, '%d-%m-%Y')))
                mycanvas.drawRightString(x+515,y-20,str(data_dict[dates][data]["total_cost"]))
            
                total += data_dict[dates][data]["total_cost"]
            
                #line
                mycanvas.line(head_x-25,y+35,head_x-25,y-25)
                mycanvas.line(head_x+5,y+35,head_x+5,y-25)
                mycanvas.line(head_x+55,y+35,head_x+55,y-25)
                mycanvas.line(head_x+115,y+35,head_x+115,y-25)
                mycanvas.line(head_x+195,y+35,head_x+195,y-25)
                mycanvas.line(head_x+375,y+35,head_x+375,y-25)
                mycanvas.line(head_x+465,y+35,head_x+465,y-25)
                mycanvas.line(head_x+545,y+35,head_x+545,y-25)
            
            
                if sl_no % 35 == 0:
                    mycanvas.line(head_x-25,y-25,head_x+545,y-25)
                    mycanvas.showPage()
                
                
                    mycanvas.setFillColor(HexColor(dark_color))
                    mycanvas.setFont('Helvetica', 12.5)
                    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                    mycanvas.setFont('Helvetica', 13)
                    
                    mycanvas.setLineWidth(0)
                    mycanvas.drawString(15, 800, "Accounts : 1" )
                    mycanvas.line(15, 797, 85, 797)
                    mycanvas.line(15, 796, 85, 796)
                    
                    mycanvas.drawCentredString(300, 800, "Agent Online Order On : " + str(sale_date) +" - "+str(session_name)+" "+"Shift")

                    mycanvas.setLineWidth(0)
                    mycanvas.line(406-100-150, 797, 593-200+50, 797)

                    #Header
                    head_y = 770
                    head_x = 40
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawString(head_x-18,head_y,"Sl.")
                    mycanvas.drawString(head_x-18,head_y-15,"No")

                    mycanvas.drawString(head_x+12,head_y,"Booth")
                    mycanvas.drawString(head_x+12,head_y-15,"Code")

                    mycanvas.drawString(head_x+70,head_y,"Zone")

                    mycanvas.drawString(head_x+135,head_y,"Agent")
                    mycanvas.drawString(head_x+135,head_y-15,"Code")

                    mycanvas.drawString(head_x+250,head_y,"Agent Name")
                #     mycanvas.drawString(head_x+240,head_y-15,"Name")

                    mycanvas.drawString(head_x+385,head_y,"Delivery For")
                #     mycanvas.drawString(head_x+362,head_y-15,"   Date")

                    mycanvas.drawString(head_x+480,head_y,"Amount")

                    mycanvas.line(head_x-25,head_y+15,head_x+545,head_y+15)
                    mycanvas.line(head_x-25,head_y-20,head_x+545,head_y-20)

                    x = 60
                    y = 730+40
                
            
            
                sl_no += 1
                y -=20
        
    mycanvas.line(head_x-25,y-5,head_x+545,y-5)
    mycanvas.line(head_x+465,y-25,head_x+545,y-25)
   
    mycanvas.drawString(head_x+390,y-20,"Grand Total")
   
    mycanvas.drawRightString(x+515,y-20,str(total))
   
    mycanvas.line(head_x+465,y+35,head_x+465,y-25)
    mycanvas.line(head_x+545,y+35,head_x+545,y-25)
   
   
    # same delivery date but ordered date is different
   
    mycanvas.showPage()
    next_date = datetime.strptime(next_date, '%Y-%m-%d')
    next_date = datetime.strftime(next_date, '%d-%m-%Y')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    
    mycanvas.setLineWidth(0)
    mycanvas.drawString(15, 800, "Accounts : 2" )
    mycanvas.line(15, 797, 85, 797)
    mycanvas.line(15, 796, 85, 796)
   
    mycanvas.drawCentredString(300, 800, "Agent Online Delivery For : " + str(next_date) +" - "+str(session_name)+" "+"Shift")

    mycanvas.setLineWidth(0)
    mycanvas.line(406-100-150, 797, 593-200+50, 797)
   
    #Header
    head_y = 770
    head_x = 40
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(head_x-18,head_y,"Sl.")
    mycanvas.drawString(head_x-18,head_y-15,"No")
   
    mycanvas.drawString(head_x+12,head_y,"Booth")
    mycanvas.drawString(head_x+12,head_y-15,"Code")
   
    mycanvas.drawString(head_x+70,head_y,"Zone")
   
    mycanvas.drawString(head_x+135,head_y,"Agent")
    mycanvas.drawString(head_x+135,head_y-15,"Code")
   
    mycanvas.drawString(head_x+250,head_y,"Agent Name")
#     mycanvas.drawString(head_x+240,head_y-15,"Name")
   
    mycanvas.drawString(head_x+385,head_y,"Orderd On")
#     mycanvas.drawString(head_x+362,head_y-15,"   Date")
   
    mycanvas.drawString(head_x+480,head_y,"Amount")
   
    mycanvas.line(head_x-25,head_y+15,head_x+545,head_y+15)
    mycanvas.line(head_x-25,head_y-20,head_x+545,head_y-20)
   
    x = 60
    y = 750
    sl_no = 1
    total2 = 0
   
    for data in data_dict2:
        if data_dict2[data]["total_cost"] == 0:
            continue
        mycanvas.setFont('Helvetica', 10)
        mycanvas.drawRightString(x-20,y-20,str(sl_no))
        mycanvas.drawString(x-10,y-20,str(data_dict2[data]["business_code"]))
        mycanvas.drawString(x+45,y-20,str(data_dict2[data]["zone"])[:8])
        mycanvas.drawString(x+100,y-20,str(data_dict2[data]["agent_code"]))
        mycanvas.drawString(x+180,y-20,str(data_dict2[data]["agent_name"])[:28])

        order_for_date = data_dict2[data]["sale_for_date"]

        mycanvas.drawString(x+375,y-20,str(order_for_date))
        mycanvas.drawRightString(x+515,y-20,str(data_dict2[data]["total_cost"]))

        total2 += data_dict2[data]["total_cost"]

        #line
        mycanvas.line(head_x-25,y+35,head_x-25,y-25)
        mycanvas.line(head_x+5,y+35,head_x+5,y-25)
        mycanvas.line(head_x+55,y+35,head_x+55,y-25)
        mycanvas.line(head_x+115,y+35,head_x+115,y-25)
        mycanvas.line(head_x+195,y+35,head_x+195,y-25)
        mycanvas.line(head_x+375,y+35,head_x+375,y-25)
        mycanvas.line(head_x+465,y+35,head_x+465,y-25)
        mycanvas.line(head_x+545,y+35,head_x+545,y-25)


        if sl_no % 35 == 0:
            mycanvas.line(head_x-25,y-25,head_x+545,y-25)
            mycanvas.showPage()


            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)
            
            mycanvas.setLineWidth(0)
            mycanvas.drawString(15, 800, "Accounts : 2" )
            mycanvas.line(15, 797, 85, 797)
            mycanvas.line(15, 796, 85, 796)

            #Date
#                 date = datetime.datetime.strptime(date, '%Y-%m-%d')

            mycanvas.drawCentredString(300, 800, "Agent Online Delivery For : " + str(next_date) +" - "+str(session_name)+" "+"Shift")

            mycanvas.setLineWidth(0)
            mycanvas.line(406-100-150, 797, 593-200+50, 797)

            #Header
            head_y = 770
            head_x = 40
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(head_x-18,head_y,"Sl.")
            mycanvas.drawString(head_x-18,head_y-15,"No")

            mycanvas.drawString(head_x+12,head_y,"Booth")
            mycanvas.drawString(head_x+12,head_y-15,"Code")

            mycanvas.drawString(head_x+70,head_y,"Zone")

            mycanvas.drawString(head_x+135,head_y,"Agent")
            mycanvas.drawString(head_x+135,head_y-15,"Code")

            mycanvas.drawString(head_x+250,head_y,"Agent Name")
        #     mycanvas.drawString(head_x+240,head_y-15,"Name")

            mycanvas.drawString(head_x+380,head_y,"Orderd On")
        #     mycanvas.drawString(head_x+362,head_y-15,"   Date")

            mycanvas.drawString(head_x+480,head_y,"Amount")

            mycanvas.line(head_x-25,head_y+15,head_x+545,head_y+15)
            mycanvas.line(head_x-25,head_y-20,head_x+545,head_y-20)

            x = 60
            y = 730+40

        sl_no += 1
        y -=20
       
    mycanvas.line(head_x-25,y-5,head_x+545,y-5)
    mycanvas.line(head_x+465,y-25,head_x+545,y-25)
   
    mycanvas.drawString(head_x+390,y-20,"Grand Total")
   
    mycanvas.drawRightString(x+515,y-20,str(total2))
   
    mycanvas.line(head_x+465,y+35,head_x+465,y-25)
    mycanvas.line(head_x+545,y+35,head_x+545,y-25)
   
   
    #different delevery date for same ordered date
   
    mycanvas.showPage()
   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    
    # mycanvas.setLineWidth(0)
    # mycanvas.drawString(15, 800, "Accounts : 3" )
    # mycanvas.line(15, 797, 85, 797)
    # mycanvas.line(15, 796, 85, 796)

    #Date
    # next_date = datetime.strptime(next_date, '%Y-%m-%d')
    # next_date = datetime.strftime(next_date, '%d-%m-%Y')
    mycanvas.drawString(20, 800, "Delivery Date : "+str(next_date))

    
    # mycanvas.line(406-90, 797, 593-200-100, 797)

    head_y = 750
    head_x = 40
    mycanvas.line(head_x+155, head_y+15, head_x+155, head_y-90)
    mycanvas.line(head_x+360, head_y+15, head_x+360, head_y-90)
    mycanvas.line(head_x+255, head_y+15, head_x+255, head_y-90)

    mycanvas.line(head_x+155, head_y+15, head_x+360, head_y+15)
    mycanvas.drawString(head_x+175,head_y,"Account")
    mycanvas.drawString(head_x+305,head_y,"Total")
    mycanvas.line(head_x+155, head_y-10, head_x+360, head_y-10)

    head_y -= 10
    mycanvas.drawString(head_x+165,head_y-20,"Account 1")
    mycanvas.drawRightString(head_x+355,head_y-20, str(total))

    mycanvas.drawString(head_x+165,head_y-40,"Account 2")
    mycanvas.drawRightString(head_x+355,head_y-40, str(total2))

    head_y -= 30
    mycanvas.line(head_x+155, head_y-20, head_x+360, head_y-20)
    mycanvas.drawString(head_x+165,head_y-40,"Grand Total")
    mycanvas.drawRightString(head_x+355,head_y-40, str(total2 + total))
    mycanvas.line(head_x+155, head_y-50, head_x+360, head_y-50)
    
    #Header
#     head_y = 770
#     head_x = 40
#     mycanvas.setFont('Helvetica', 12)
#     mycanvas.drawString(head_x-18,head_y,"Sl.")
#     mycanvas.drawString(head_x-18,head_y-15,"No")
   
#     mycanvas.drawString(head_x+12,head_y,"Booth")
#     mycanvas.drawString(head_x+12,head_y-15,"Code")
   
#     mycanvas.drawString(head_x+70,head_y,"Zone")
   
#     mycanvas.drawString(head_x+135,head_y,"Agent")
#     mycanvas.drawString(head_x+135,head_y-15,"Code")
   
#     mycanvas.drawString(head_x+250,head_y,"Agent Name")
# #     mycanvas.drawString(head_x+240,head_y-15,"Name")
   
#     mycanvas.drawString(head_x+385,head_y,"Delivery For")
# #     mycanvas.drawString(head_x+362,head_y-15,"   Date")
   
#     mycanvas.drawString(head_x+480,head_y,"Amount")
   
#     mycanvas.line(head_x-25,head_y+15,head_x+545,head_y+15)
#     mycanvas.line(head_x-25,head_y-20,head_x+545,head_y-20)
   
#     x = 60
#     y = 750
#     sl_no = 1
#     total = 0
   
#     for dates in data_dict:
       
#         if str(dates) == str(next_date):
#             continue
#         for data in data_dict[dates]:
#             if data_dict[dates][data]["total_cost"] == 0:
#                 continue
#             mycanvas.setFont('Helvetica', 10)
#             mycanvas.drawRightString(x-20,y-20,str(sl_no))
#             mycanvas.drawString(x-10,y-20,str(data_dict[dates][data]["business_code"]))
#             mycanvas.drawString(x+45,y-20,str(data_dict[dates][data]["zone"])[:8])
#             mycanvas.drawString(x+100,y-20,str(data_dict[dates][data]["agent_code"]))
#             mycanvas.drawString(x+180,y-20,str(data_dict[dates][data]["agent_name"])[:28])
           
#             order_for_date = datetime.strptime(str(data_dict[dates][data]["sale_for_date"]), '%Y-%m-%d')
           
#             mycanvas.drawString(x+375,y-20,str(datetime.strftime(order_for_date, '%d-%m-%Y')))
#             mycanvas.drawRightString(x+515,y-20,str(data_dict[dates][data]["total_cost"]))
           
#             total += data_dict[dates][data]["total_cost"]
           
#             #line
#             mycanvas.line(head_x-25,y+35,head_x-25,y-25)
#             mycanvas.line(head_x+5,y+35,head_x+5,y-25)
#             mycanvas.line(head_x+55,y+35,head_x+55,y-25)
#             mycanvas.line(head_x+115,y+35,head_x+115,y-25)
#             mycanvas.line(head_x+195,y+35,head_x+195,y-25)
#             mycanvas.line(head_x+375,y+35,head_x+375,y-25)
#             mycanvas.line(head_x+465,y+35,head_x+465,y-25)
#             mycanvas.line(head_x+545,y+35,head_x+545,y-25)
           
           
#             if sl_no % 35 == 0:
#                 mycanvas.line(head_x-25,y-25,head_x+545,y-25)
#                 mycanvas.showPage()
               
               
#                 mycanvas.setFillColor(HexColor(dark_color))
#                 mycanvas.setFont('Helvetica', 12.5)
#                 mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
#                 mycanvas.setFont('Helvetica', 13)

#                 #Date
# #                 date = datetime.datetime.strptime(date, '%Y-%m-%d')
#                 mycanvas.drawCentredString(300, 800, "Agent Online Order On : " + str(sale_date) +" - "+str(session_name)+" "+"Shift")

#                 mycanvas.setLineWidth(0)
#                 mycanvas.line(406-100-150, 797, 593-200+50, 797)

#                 #Header
#                 head_y = 770
#                 head_x = 40
#                 mycanvas.setFont('Helvetica', 12)
#                 mycanvas.drawString(head_x-18,head_y,"Sl.")
#                 mycanvas.drawString(head_x-18,head_y-15,"No")

#                 mycanvas.drawString(head_x+12,head_y,"Booth")
#                 mycanvas.drawString(head_x+12,head_y-15,"Code")

#                 mycanvas.drawString(head_x+70,head_y,"Zone")

#                 mycanvas.drawString(head_x+135,head_y,"Agent")
#                 mycanvas.drawString(head_x+135,head_y-15,"Code")

#                 mycanvas.drawString(head_x+250,head_y,"Agent Name")
#             #     mycanvas.drawString(head_x+240,head_y-15,"Name")

#                 mycanvas.drawString(head_x+385,head_y,"Delivery For")
#             #     mycanvas.drawString(head_x+362,head_y-15,"   Date")

#                 mycanvas.drawString(head_x+480,head_y,"Amount")

#                 mycanvas.line(head_x-25,head_y+15,head_x+545,head_y+15)
#                 mycanvas.line(head_x-25,head_y-20,head_x+545,head_y-20)

#                 x = 60
#                 y = 730+40
               
           
           
#             sl_no += 1
#             y -=20
#     mycanvas.line(head_x-25,y-5,head_x+545,y-5)
#     mycanvas.line(head_x+465,y-25,head_x+545,y-25)
   
#     mycanvas.drawString(head_x+390,y-20,"Grand Total")
   
#     mycanvas.drawRightString(x+515,y-20,str(total))
   
#     mycanvas.line(head_x+465,y+35,head_x+465,y-25)
#     mycanvas.line(head_x+545,y+35,head_x+545,y-25)
   
#     print(file_name)
           
    mycanvas.save()
    document = {}
    document['file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document


@api_view(['POST'])
def serve_incentive_report(request):
    
    data = request.data
    from_date = data['from_date']
    to_date = data['to_date']
    option = data["option_type"]
    option_value = float(data["option_value"])
    incentive_for = data["selected_incentive_for"]

    if incentive_for == "agent":
        incentive_for = ['Agent']
    elif incentive_for == "icustomer":
        incentive_for = ["ICustomer"]
    else:
        incentive_for = ["Agent","ICustomer"]

    tds_ded = data["tds_deduction"]
    tds_val = float(data["tds_value"])
    
    data_list = []
    total_dict = {
        "milk":0,
        "cost":0,
        "incen":0,
    }
    
    if(tds_ded):
        total_dict["tds"] = 0
        total_dict["netincen"] = 0
    
    daily_litter_ids = list(DailySessionllyBusinessllySale.objects.filter(delivery_date__range=[from_date,to_date],sold_to__in=incentive_for,business_type_id__in=[1,2]).order_by('zone_id').values_list("business_id",flat=True))
    daily_litter_ids = list(set(daily_litter_ids))
    
    for ids in daily_litter_ids:
        data = DailySessionllyBusinessllySale.objects.filter(delivery_date__range=[from_date,to_date],sold_to__in=incentive_for,business_id=ids)
        business_agent_obj = BusinessAgentMap.objects.get(business_id=ids)
        data_dict = {
            "AgentCode":business_agent_obj.agent.agent_code,
            "AgentName":business_agent_obj.agent.first_name.title() +" "+ business_agent_obj.agent.last_name.title(),
            "BoothCode":str(business_agent_obj.business.code),
            "TotalMilkLiter":Decimal(data.aggregate(Sum('milk_litre'))['milk_litre__sum']),
            "TotalMilkCost":round(data.aggregate(Sum('milk_cost'))['milk_cost__sum'],2),
            "TotalIncentive":0,
        } 
        
        if option == "amount":
            data_dict["TotalIncentive"] = round(data_dict["TotalMilkLiter"] * Decimal(option_value),2)
        else:
            data_dict["TotalIncentive"] = round(data_dict["TotalMilkCost"] * Decimal(option_value/100),2)
            
        total_dict["milk"] += data_dict["TotalMilkLiter"]
        total_dict["cost"] += data_dict["TotalMilkCost"]
        total_dict["incen"] += data_dict["TotalIncentive"]
            
        if (tds_ded):
            data_dict["TdsAmount"] = round(data_dict["TotalIncentive"] * Decimal(tds_val/100),2)
            data_dict["NetIncentive"] = round(data_dict["TotalIncentive"] - data_dict["TdsAmount"],2)
            total_dict["tds"] += data_dict["TdsAmount"]
            total_dict["netincen"] += data_dict["NetIncentive"]
            
        data_list.append(data_dict)
        
    insentive_df = pd.DataFrame(data_list)
    
    excel_file_name = 'incentive_report' + str(from_date) + '_to_' + str(to_date) + ".xlsx"
    excel_file_path = os.path.join('static/media/monthly_report/', excel_file_name)
    insentive_df.index = insentive_df.index + 1
    insentive_df.to_excel(excel_file_path)
    
    df_ex = pd.read_excel(excel_file_path)
    df_ex = df_ex.rename(columns={"Unnamed: 0": "Sl.No"})
    df_ex.to_excel(excel_file_path)
    
    data_dict = df_ex.to_dict('r')
    
#-----------Canvas--------------#

    file_name = 'incentive_report' + str(from_date) + '_to_' + str(to_date) + ".pdf"
    file_path = os.path.join('static/media/monthly_report/', file_name)
   
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    
    mycanvas.setLineWidth(0)
    
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')

    from_date = datetime.strftime(from_date, '%d/%m/%Y')
    to_date = datetime.strftime(to_date, '%d/%m/%Y')
    
    if option == "amount":
        incentives = "Incentive Amount Rs.: "+str(option_value)
    else:
        incentives = "Incentive Precentage : "+str(option_value) +" % "
    

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 805, 'Incentive Report - ( '+from_date+" to "+to_date+' )')
    mycanvas.setFont('Helvetica', 9)
    mycanvas.drawString(5, 795, str(incentives))
    if(tds_ded):
        mycanvas.drawRightString(590, 795, "Tax Precentage : "+str(tds_val)+" %")
    
    
    x = 5
    y = 790
    x_total_len = 590
    len_adjust = len(data_dict[0])
    
    mycanvas.line(x,y,x_total_len,y)
    mycanvas.line(x,y-20,x_total_len,y-20)
    
    for data in data_dict[0]:
        mycanvas.drawCentredString(x+32,y-15,data)
        x += (x_total_len/len_adjust) 
        
    x = 5 
    sl_no = 0
    mlk_ltr = 0
    mlk_cst = 0
    tot_icen = 0
    for datas in data_dict:
        mycanvas.setLineWidth(0)
        for data in data_dict[0]:
            if data == "Sl.No":
                sl_no = datas[data]
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(datas[data]))
            elif data == list(data_dict[0])[-1]: 
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-10,y-35,str(round(Decimal(datas[data]),2)))
            elif data == 'AgentCode':
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(datas[data]))
            elif data == 'BoothCode':
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(datas[data]))
            elif data == 'AgentName':
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawString(x+3,y-35,str(datas[data])[:13])
                mycanvas.setFont('Helvetica', 9)
            elif data == 'TotalMilkLiter':
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(round(Decimal(datas[data]),3)))
            else:
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(round(Decimal(datas[data]),2)))
            mycanvas.line(x,y,x,y-40)
            
            x += (x_total_len/len_adjust)
            
        x = 5
        mycanvas.line(x,y,x,y-40)
        mycanvas.line(x_total_len,y,x_total_len,y-40)
        y -= 15
            
        if sl_no % 49 == 0:
            mycanvas.setLineWidth(0)
            x = 5
            mycanvas.line(x,y-25,x_total_len,y-25)
            mycanvas.showPage()
            y = 790
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 805, 'Incentive Report - ( '+from_date+" to "+to_date+' )')
            mycanvas.setFont('Helvetica', 9)
            mycanvas.drawString(5, 795, str(incentives))
            if(tds_ded):
                mycanvas.drawRightString(590, 795, "Tax Precentage : "+str(tds_val)+" %")
            mycanvas.setLineWidth(0)
            mycanvas.line(x,y,x_total_len,y)
            mycanvas.line(x,y-20,x_total_len,y-20)

            for data in data_dict[0]: 
                mycanvas.drawCentredString(x+32,y-15,data)
                x += (x_total_len/len_adjust) 
            x = 5
            
    mycanvas.line(x,y-25,x_total_len,y-25)
#     mycanvas.line(x+263,y-45,x_total_len,y-45)
    mycanvas.line(x_total_len,y-25,x_total_len,y-45)
    
    x = 5
    for data in total_dict:
        if total_dict[data] == 0:
            continue
        if data == "milk":
            mycanvas.drawRightString(x+(x_total_len/len_adjust)*4-5,y-40,"Grand Total")
            mycanvas.drawRightString(x+(x_total_len/len_adjust)*5-5,y-40,str(round(Decimal(total_dict[data]),3)))
        elif data == list(total_dict)[-1]:
            mycanvas.drawRightString(x+(x_total_len/len_adjust)*5-10,y-40,str(round(Decimal(total_dict[data]),2)))
        else:
            mycanvas.drawRightString(x+(x_total_len/len_adjust)*5-5,y-40,str(round(Decimal(total_dict[data]),2)))
        mycanvas.line(x+(x_total_len/len_adjust)*4,y-25,x+(x_total_len/len_adjust)*4,y-45)
        mycanvas.line(x+(x_total_len/len_adjust)*4,y-45,x+(x_total_len/len_adjust)*5,y-45)
        x += (x_total_len/len_adjust)
        
    
    mycanvas.save()
    
    df_ex = pd.read_excel(excel_file_path)
    df_ex = df_ex.rename(columns={"Unnamed: 0": "Sl.No"})
    df_ex.drop("Sl.No",inplace = True,axis=1)
    df_ex.index = insentive_df.index 
    df_ex.to_excel(excel_file_path)

    print(df_ex)
    document = {}
    document['excel_file_name'] = excel_file_name
    document['pdf_file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    try:
        image_path = excel_file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)

    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_transaction_log(request):
    print(request.data)
    date = request.data['date']
    data_list = []
    business_agent_user_ids = list(BusinessAgentMap.objects.filter(business__business_type_id__in=[1,2,9]).values_list('business__user_profile__user_id', flat=True))
    transacted_user_ids = list(TransactionLog.objects.filter(date=date,transacted_by_id__in=business_agent_user_ids, transaction_status_id=2).values_list('transacted_by_id', flat=True))
    business_agent_map_obj = BusinessAgentMap.objects.filter(business__business_type_id__in=[1,2,9], business__user_profile__user_id__in=transacted_user_ids).order_by("business_id")
    for business_agent in business_agent_map_obj:
        transaction_log_obj_list = list(TransactionLog.objects.filter(date=date,transacted_by_id=business_agent.business.user_profile.user_id, transaction_status_id=2).order_by("time_created"))
        if transaction_log_obj_list:
            data_dict = {
                "AgentCode": business_agent.agent.agent_code,
                "BoothCode": business_agent.business.code,
                "OpeaningBalance": transaction_log_obj_list[0].wallet_balance_before_this_transaction,
                "IncomingAmount": '',
                "OutgoingAmount": '',
                "ClosingBalance":transaction_log_obj_list[-1].wallet_balance_after_transaction_approval
            }
            
            for transaction in transaction_log_obj_list:
                if transaction.transaction_direction_id == 3:
                    time = transaction.time_created
                    time_now = time.astimezone(timezone('Asia/Kolkata'))
                    time_created = time_now.strftime("%I:%M:%p")
                    
                    amount_plus_time = "( "+str(transaction.amount)+ " , " + str(time_created)+" )/"
                    data_dict["IncomingAmount"] += amount_plus_time
                if transaction.transaction_direction_id == 2:
                    time = transaction.time_created
                    time_now = time.astimezone(timezone('Asia/Kolkata'))
                    time_created = time_now.strftime("%I:%M:%p")
                    
                    amount_plus_time = "( "+str(transaction.amount)+ " , " + str(time_created)+" )/"
                    data_dict["OutgoingAmount"] += amount_plus_time
            
            data_list.append(data_dict)
            
    transaction_df = pd.DataFrame(data_list)
    
    excel_file_name = 'transation_log_report_for' + str(date) +".xlsx"
    excel_file_path = os.path.join('static/media/', excel_file_name)
    transaction_df.index = transaction_df.index + 1
    transaction_df.to_excel(excel_file_path)
    
    pdf_df = pd.read_excel(excel_file_path)
    pdf_df = pdf_df.rename(columns={"Unnamed: 0": "Sl.No"})
    pdf_df.to_excel(excel_file_path)
    pdf_df = pdf_df.fillna('')
    data_dict = pdf_df.to_dict('r')
    
    
    #-----------Canvas--------------#

    file_name = 'transation_log_report_for' + str(date) + ".pdf"
    file_path = os.path.join('static/media/', file_name)
   
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    
    mycanvas.setLineWidth(0)
    
    date = datetime.strptime(date, '%Y-%m-%d')
#     to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')

    date = datetime.strftime(date, '%d/%m/%Y')
#     to_date = datetime.datetime.strftime(to_date, '%d/%m/%Y')
    
    
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 805, 'Wallet Amount Transaction Details For - '+(date))
    mycanvas.setFont('Helvetica', 9)
    
    x = 5
    y = 790
    x_total_len = 590
    len_adjust = len(data_dict[0])
    
    mycanvas.line(x,y,x_total_len,y)
    mycanvas.line(x,y-20,x_total_len,y-20)
    
    for data in data_dict[0]:
        mycanvas.drawCentredString(x+42,y-15,data)
        x += (x_total_len/len_adjust) 
        
    x = 5 
    sl_no = 0
    mlk_ltr = 0
    mlk_cst = 0
    tot_icen = 0
    for datas in data_dict:
        mycanvas.setLineWidth(0)
        for data in data_dict[0]:
            if data == "Sl.No":
                sl_no = datas[data]
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(datas[data]))
            elif data == list(data_dict[0])[-1]: 
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-10,y-35,str(round(Decimal(datas[data]),2)))
            elif data == 'AgentCode':
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(datas[data]))
            elif data == 'BoothCode':
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(datas[data]))
            elif data == 'IncomingAmount':    
                value_list = datas[data].split("/")
                if len(value_list) > 2:
                    for value in value_list[:-1]:
                        mycanvas.setFont('Helvetica', 8)
                        mycanvas.drawString(x+3,y-35,str(value))
                        mycanvas.setFont('Helvetica', 9)
                        y -= 15
                    y += 15
                else:
                    mycanvas.setFont('Helvetica', 8)
                    mycanvas.drawString(x+3,y-35,str(value_list[0]))
                    mycanvas.setFont('Helvetica', 9)
            elif data == 'OutgoingAmount':
                value_list = datas[data].split("/")
                if len(value_list) > 2:
                    for value in value_list[:-1]:
                        mycanvas.setFont('Helvetica', 8)
                        mycanvas.drawString(x+3,y-35,str(value))
                        mycanvas.setFont('Helvetica', 9)
                        y -= 15
                    y += 15
                else:
                    mycanvas.setFont('Helvetica', 8)
                    mycanvas.drawString(x+3,y-35,str(value_list[0]))
                    mycanvas.setFont('Helvetica', 9)
            else:
                mycanvas.drawRightString(x+(x_total_len/len_adjust)-5,y-35,str(round(Decimal(datas[data]),2)))
            mycanvas.line(x,y,x,y-40)
            
            x += (x_total_len/len_adjust)
            
        x = 5
        mycanvas.line(x,y,x,y-40)
        mycanvas.line(x_total_len,y,x_total_len,y-40)
        y -= 15
            
        if y <= 50:
            mycanvas.setLineWidth(0)
            x = 5
            mycanvas.line(x,y-25,x_total_len,y-25)
            mycanvas.showPage()
            y = 790
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 805, 'Wallet Amount Transaction Details For - '+(date))
            mycanvas.setFont('Helvetica', 9)
            mycanvas.setLineWidth(0)
            mycanvas.line(x,y,x_total_len,y)
            mycanvas.line(x,y-20,x_total_len,y-20)

            for data in data_dict[0]: 
                mycanvas.drawCentredString(x+42,y-15,data)
                x += (x_total_len/len_adjust) 
            x = 5
            
    mycanvas.line(x,y-25,x_total_len,y-25)
    mycanvas.save()

    df_ex = pd.read_excel(excel_file_path)
    df_ex = df_ex.rename(columns={"Unnamed: 0": "Sl.No"})
    df_ex.drop("Sl.No",inplace = True,axis=1)
    df_ex.index = transaction_df.index 
    df_ex.to_excel(excel_file_path)

    print(df_ex)
    document = {}
    document['excel_file_name'] = excel_file_name
    document['pdf_file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    try:
        image_path = excel_file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)

    return Response(data=document, status=status.HTTP_200_OK)

# monthly milk abstract
@api_view(['POST'])
def serve_milk_abstract_for_month(request):
    print(request.data)
    data_dict = {}
    selected_option = request.data['selected_inp_type']
    
    if selected_option == 'Date Range':
        # month = request.data['selected_month']['month_in_integer']
        # year = request.data['selected_month']['year']
        my_date = datetime.strptime(request.data['selected_from_date'], "%Y-%m-%d")
        month = my_date.month
        year = my_date.year
        from_date = request.data['selected_from_date']
        to_date = request.data['selected_to_date']
        date_range = pd.date_range(start=from_date,end=to_date)
        days = monthrange(year, month)
        data = request.data
    else:
        month = request.data['selected_month']['month_in_integer']
        year = request.data['selected_month']['year']
        days = monthrange(year, month)
        data = request.data
    
    for zone in Zone.objects.all():
        if selected_option == 'Date Range':
            Icustomer_sale_group = ICustomerSaleGroup.objects.filter(date__in=date_range,zone_id=zone.id).exclude(icustomer__customer_type_id__in=[2,3])
            total_sale = ICustomerSale.objects.filter(icustomer_sale_group__in=Icustomer_sale_group)
        else:
            Icustomer_sale_group = ICustomerSaleGroup.objects.filter(date__month=month,date__year=year,zone_id=zone.id).exclude(icustomer__customer_type_id__in=[2,3])
            total_sale = ICustomerSale.objects.filter(icustomer_sale_group__in=Icustomer_sale_group)
            
            
        if Icustomer_sale_group.aggregate(Sum('total_cost_for_month'))['total_cost_for_month__sum'] is None or 0:
            pass
        else:
            data_dict[zone.name] = {
                'FCM 500':{
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                },
                'STD 250':{
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                },
                'STD 500':{
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                },
                'TM 500':{
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                },
                'Tea 500':{
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                },
            }

            for sale in total_sale:
                if not sale.product.short_name in data_dict[zone.name]:
                    data_dict[zone.name][sale.product.short_name] = {
                        "mor": 0,
                        "eve": 0,
                        "mor_cost": 0,
                        "eve_cost": 0,
                    }
                if sale.icustomer_sale_group.session_id == 1:
                    data_dict[zone.name][sale.product.short_name]["mor"] += sale.count*days[1]
                    data_dict[zone.name][sale.product.short_name]["mor_cost"] += sale.cost_for_month

                if sale.icustomer_sale_group.session_id == 2:
                    data_dict[zone.name][sale.product.short_name]["eve"] += sale.count*days[1]
                    data_dict[zone.name][sale.product.short_name]["eve_cost"] += sale.cost_for_month
                 
                
    if selected_option == 'Date Range':           
    # EX STAFF
        ex_customer_sale_group = ICustomerSaleGroup.objects.filter(time_created__date__in=date_range,icustomer__customer_type_id=2,date__month=month,date__year=year)
        ex_total_sale = ICustomerSale.objects.filter(icustomer_sale_group__in=ex_customer_sale_group)

        #STAFF
        staff_Icustomer_sale_group = ICustomerSaleGroup.objects.filter(time_created__date__in=date_range,icustomer__customer_type_id=3,date__month=month,date__year=year)
        staff_total_sale = ICustomerSale.objects.filter(icustomer_sale_group__in=staff_Icustomer_sale_group)
    
    else:
        # EX STAFF
        ex_customer_sale_group = ICustomerSaleGroup.objects.filter(date__month=month,date__year=year,icustomer__customer_type_id=2)
        ex_total_sale = ICustomerSale.objects.filter(icustomer_sale_group__in=ex_customer_sale_group)

        #STAFF
        staff_Icustomer_sale_group = ICustomerSaleGroup.objects.filter(date__month=month,date__year=year,icustomer__customer_type_id=3)
        staff_total_sale = ICustomerSale.objects.filter(icustomer_sale_group__in=staff_Icustomer_sale_group)
    
    
    
    # EX_staff
    if ex_customer_sale_group.aggregate(Sum('total_cost_for_month'))['total_cost_for_month__sum'] is None or 0:
        pass
    else:
        data_dict["EX STAFF"] = {
            'FCM 500':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'STD 250':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'STD 500':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'TM 500':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'Tea 500':{
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                },
        }

        for sale in ex_total_sale:
            if not sale.product.short_name in data_dict["EX STAFF"]:
                data_dict["EX STAFF"][sale.product.short_name] = {
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                }
            if sale.icustomer_sale_group.session_id == 1:
                data_dict["EX STAFF"][sale.product.short_name]["mor"] += sale.count*days[1]
                data_dict["EX STAFF"][sale.product.short_name]["mor_cost"] += sale.cost_for_month

            if sale.icustomer_sale_group.session_id == 2:
                data_dict["EX STAFF"][sale.product.short_name]["eve"] += sale.count*days[1]
                data_dict["EX STAFF"][sale.product.short_name]["eve_cost"] += sale.cost_for_month
    
    #Staff
    if staff_Icustomer_sale_group.aggregate(Sum('total_cost_for_month'))['total_cost_for_month__sum'] is None or 0:
        pass
    else:
        data_dict["STAFF"] = {
            'FCM 500':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'STD 250':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'STD 500':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'TM 500':{
                "mor": 0,
                "eve": 0,
                "mor_cost": 0,
                "eve_cost": 0,
            },
            'Tea 500':{
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                },
        }

        for sale in staff_total_sale:
            if not sale.product.short_name in data_dict["STAFF"]:
                data_dict["STAFF"][sale.product.short_name] = {
                    "mor": 0,
                    "eve": 0,
                    "mor_cost": 0,
                    "eve_cost": 0,
                }
            if sale.icustomer_sale_group.session_id == 1:
                data_dict["STAFF"][sale.product.short_name]["mor"] += sale.count*days[1]
                data_dict["STAFF"][sale.product.short_name]["mor_cost"] += sale.cost_for_month

            if sale.icustomer_sale_group.session_id == 2:
                data_dict["STAFF"][sale.product.short_name]["eve"] += sale.count*days[1]
                data_dict["STAFF"][sale.product.short_name]["eve_cost"] += sale.cost_for_month
    
    data_dict["user_name"] = request.user.first_name
    data = serve_milk_abstract_for_month_pdf_gen(data_dict,data,selected_option)
    print(data_dict)
    return Response(data=data, status=status.HTTP_200_OK)

def serve_milk_abstract_for_month_pdf_gen(data_dict,data,selected_option):
    
    if selected_option == 'Date Range':
        
        file_name = "monthly_milk_abstract_for( " +str(data['selected_from_date'])+"-to-"+ str(data['selected_to_date'])+' ).pdf'
    else:
        file_name = "monthly_milk_abstract_for( " +str(data['selected_month']['month_in_string'])+" - "+str(data['selected_month']['year'])+' ).pdf'
    file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 12.5)
    
    if selected_option == 'Date Range':
        from_date = datetime.strptime(data['selected_from_date'], '%Y-%m-%d')
        from_date = datetime.strftime(from_date, '%d/%m/%Y')

        to_date = datetime.strptime(data['selected_to_date'], '%Y-%m-%d')
        to_date = datetime.strftime(to_date, '%d/%m/%Y')

        mycanvas.drawCentredString(300, 805, 'Monthly Milk Abstract - '+str(from_date +"-to-"+ to_date))
    else:
        mycanvas.drawCentredString(300, 805, 'Monthly Milk Abstract - '+str(data['selected_month']['month_in_string'])+" - "+str(data['selected_month']['year']))
    
    
    mycanvas.setLineWidth(0)
    
    x_head = 23
    y_head = 730
    mycanvas.drawCentredString(300, y_head+50, 'TOTAL MILK POCKETS')
    
    x=20
    y = y_head-25
    #heading
    
    mycanvas.drawString(x_head,y_head+25,"Zone")
    mycanvas.drawString(x_head+70,y_head+25,"FCM500")
    mycanvas.drawString(x_head+170,y_head+25,"STD250")
    mycanvas.drawString(x_head+270,y_head+25,"STD500")
    mycanvas.drawString(x_head+370,y_head+25,"TM500")
    mycanvas.drawString(x_head+470,y_head+25,"TEA500")
    
    
    mycanvas.drawString(x_head+65,y_head,"Mor")
    mycanvas.drawString(x_head+120-5,y_head,"Eve")
    mycanvas.drawString(x_head+170-10,y_head,"Mor")
    mycanvas.drawString(x_head+225-15,y_head,"Eve")
    mycanvas.drawString(x_head+285-20,y_head,"Mor")
    mycanvas.drawString(x_head+330-25,y_head,"Eve")
    mycanvas.drawString(x_head+390-30,y_head,"Mor")
    mycanvas.drawString(x_head+450-35 ,y_head,"Eve")
    mycanvas.drawString(x_head+500-40,y_head,"Mor")
    mycanvas.drawString(x_head+560-45 ,y_head,"Eve")
    
#     lines
    mycanvas.line(x_head-15,y_head+40,x_head+562,y_head+40)
    mycanvas.line(x_head-15,y_head+15,x_head+562,y_head+15)
    mycanvas.line(x_head-15,y_head-10,x_head+562,y_head-10)
    
    
    # for datas 
    
    fcm500_mor = 0
    fcm500_eve = 0
    std250_mor = 0
    std250_eve = 0
    std500_mor = 0
    std500_eve = 0
    tm500_mor = 0
    tm500_eve = 0
    tea500_mor = 0
    tea500_eve = 0
    
    for data in data_dict:
        if data == "user_name":
            continue
        data_name = data
        if data == 'CHENNAI Aavin':
            data_name = 'CHENNAI'
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(x-5,y,str(data_name))
        if data_dict[data]['FCM 500']['mor'] is not None:
            mycanvas.drawRightString(x+90,y,str(round(data_dict[data]['FCM 500']['mor'])))
            fcm500_mor += data_dict[data]['FCM 500']['mor']
            
        if data_dict[data]['FCM 500']['eve'] is not None:
            mycanvas.drawRightString(x+95+45,y,str(round(data_dict[data]['FCM 500']['eve'])))
            fcm500_eve += data_dict[data]['FCM 500']['eve']
            
        if data_dict[data]['STD 250']['mor'] is not None:
            mycanvas.drawRightString(x+95+45*2,y,str(round(data_dict[data]['STD 250']['mor'])))
            std250_mor += data_dict[data]['STD 250']['mor']
            
        if data_dict[data]['STD 250']['eve'] is not None:
            mycanvas.drawRightString(x+95+45*3,y,str(round(data_dict[data]['STD 250']['eve'])))
            std250_eve += data_dict[data]['STD 250']['eve']
            
        if data_dict[data]['STD 500']['mor'] is not None:
            mycanvas.drawRightString(x+95+45*4,y,str(round(data_dict[data]['STD 500']['mor'])))
            std500_mor += data_dict[data]['STD 500']['mor']
            
        if data_dict[data]['STD 500']['eve'] is not None:
            mycanvas.drawRightString(x+95+45*5,y,str(round(data_dict[data]['STD 500']['eve'])))
            std500_eve += data_dict[data]['STD 500']['eve']
            
        if data_dict[data]['TM 500']['mor'] is not None:
            mycanvas.drawRightString(x+95+47*6,y,str(round(data_dict[data]['TM 500']['mor'])))
            tm500_mor += data_dict[data]['TM 500']['mor']
            
        if data_dict[data]['TM 500']['eve'] is not None:
            mycanvas.drawRightString(x+95+47*7,y,str(round(data_dict[data]['TM 500']['eve'])))
            tm500_eve += data_dict[data]['TM 500']['eve']

        if data_dict[data]['Tea 500']['mor'] is not None:
            mycanvas.drawRightString(x+95+47*8,y,str(round(data_dict[data]['Tea 500']['mor'])))
            tea500_mor += data_dict[data]['Tea 500']['mor']
            
        if data_dict[data]['Tea 500']['eve'] is not None:
            mycanvas.drawRightString(x+95+47*9,y,str(round(data_dict[data]['Tea 500']['eve'])))
            tea500_eve += data_dict[data]['Tea 500']['eve']    
            
        
        #lines
        mycanvas.line(x-10,y+65,x-10,y-25)
        mycanvas.line(x+40,y+65,x+40,y-25)
        mycanvas.line(x+95,y+40,x+95,y-25)
        mycanvas.line(x+95+50,y+65,x+95+50,y-25)
        mycanvas.line(x+95+50*2,y+40,x+95+50*2,y-25)
        mycanvas.line(x+95+50*3,y+65,x+95+50*3,y-25)
        mycanvas.line(x+95+50*4,y+40,x+95+50*4,y-25)
        mycanvas.line(x+95+50*5,y+65,x+95+50*5,y-25)
        mycanvas.line(x+95+50*6,y+40,x+95+50*6,y-25)
        mycanvas.line(x+95+50*7,y+65,x+95+50*7,y-25)
        mycanvas.line(x+95+50*8,y+40,x+95+50*8,y-25)
        mycanvas.line(x+95+50*9,y+65,x+95+50*9,y-25)
        
        y -= 25
        
    #lines
    mycanvas.line(x_head-15,y+20,x_head+562,y+20)
    mycanvas.line(x_head-15,y,x_head+562,y)
    
    #totals
    mycanvas.drawString(x-5,y+7,"Grand Total")
    mycanvas.drawRightString(x+95,y+7,str(round(fcm500_mor)))
    mycanvas.drawRightString(x+95+50,y+7,str(round(fcm500_eve)))
    mycanvas.drawRightString(x+95+50*2,y+7,str(round(std250_mor)))
    mycanvas.drawRightString(x+95+50*3,y+7,str(round(std250_eve)))
    mycanvas.drawRightString(x+95+50*4,y+7,str(round(std500_mor)))
    mycanvas.drawRightString(x+95+50*5,y+7,str(round(std500_eve)))
    mycanvas.drawRightString(x+95+50*6,y+7,str(round(tm500_mor)))
    mycanvas.drawRightString(x+95+50*7,y+7,str(round(tm500_eve)))
    mycanvas.drawRightString(x+95+50*8,y+7,str(round(tea500_mor)))
    mycanvas.drawRightString(x+95+50*9,y+7,str(round(tea500_eve)))
    
    #------------------------------------------------for_cost--------------------------------------------------
    
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.setLineWidth(0)
    
    x_head = 23
    y_head2 = y_head-380
    
    mycanvas.drawCentredString(300, y_head2+50, 'MILK TOTAL IN COST')
    x=20
    y = y_head2-25
    #heading
    
    # mycanvas.drawString(x_head,y_head2+25,"Zone")
    # mycanvas.drawString(x_head+80,y_head2+25,"FCM500")
    # mycanvas.drawString(x_head+210,y_head2+25,"STD250")
    # mycanvas.drawString(x_head+345,y_head2+25,"STD500")
    # mycanvas.drawString(x_head+470,y_head2+25,"TM500")
    # mycanvas.drawString(x_head+470,y_head2+25,"TM500")
    
    
    # mycanvas.drawString(x_head+70,y_head2,"Mor")
    # mycanvas.drawString(x_head+140-5,y_head2,"Eve")
    # mycanvas.drawString(x_head+210-10,y_head2,"Mor")
    # mycanvas.drawString(x_head+280-15,y_head2,"Eve")
    # mycanvas.drawString(x_head+350-20,y_head2,"Mor")
    # mycanvas.drawString(x_head+420-25,y_head2,"Eve")
    # mycanvas.drawString(x_head+490-30,y_head2,"Mor")
    # mycanvas.drawString(x_head+560-35 ,y_head2,"Eve")
    

    mycanvas.drawString(x_head,y_head2+25,"Zone")
    mycanvas.drawString(x_head+70,y_head2+25,"FCM500")
    mycanvas.drawString(x_head+170,y_head2+25,"STD250")
    mycanvas.drawString(x_head+270,y_head2+25,"STD500")
    mycanvas.drawString(x_head+370,y_head2+25,"TM500")
    mycanvas.drawString(x_head+470,y_head2+25,"TEA500")
    
    
    mycanvas.drawString(x_head+65,y_head2,"Mor")
    mycanvas.drawString(x_head+120-5,y_head2,"Eve")
    mycanvas.drawString(x_head+170-10,y_head2,"Mor")
    mycanvas.drawString(x_head+225-15,y_head2,"Eve")
    mycanvas.drawString(x_head+285-20,y_head2,"Mor")
    mycanvas.drawString(x_head+330-25,y_head2,"Eve")
    mycanvas.drawString(x_head+390-30,y_head2,"Mor")
    mycanvas.drawString(x_head+450-35 ,y_head2,"Eve")
    mycanvas.drawString(x_head+500-40,y_head2,"Mor")
    mycanvas.drawString(x_head+560-45 ,y_head2,"Eve")
    
#     lines
    mycanvas.line(x_head-13,y_head2+40,x_head+562,y_head2+40)
    mycanvas.line(x_head-13,y_head2+15,x_head+562,y_head2+15)
    mycanvas.line(x_head-13,y_head2-10,x_head+562,y_head2-10)
    
    # mycanvas.line(x_head-15,y_head+40,x_head+562,y_head+40)
    # mycanvas.line(x_head-15,y_head+15,x_head+562,y_head+15)
    # mycanvas.line(x_head-15,y_head-10,x_head+562,y_head-10)

    # for datas 
    
    fcm500_mor = 0
    fcm500_eve = 0
    std250_mor = 0
    std250_eve = 0
    std500_mor = 0
    std500_eve = 0
    tm500_mor = 0
    tm500_eve = 0
    tea500_mor = 0
    tea500_eve = 0
    
    for data in data_dict:
        if data == "user_name":
            continue
        data_name = data
        if data == 'CHENNAI Aavin':
            data_name = 'CHENNAI'
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(x-5,y,str(data_name))
        if data_dict[data]['FCM 500']['mor_cost'] is not None:
            mycanvas.drawRightString(x+90,y,str(data_dict[data]['FCM 500']['mor_cost']))
            fcm500_mor += data_dict[data]['FCM 500']['mor_cost']
            
        if data_dict[data]['FCM 500']['eve_cost'] is not None:
            mycanvas.drawRightString(x+95+45,y,str(data_dict[data]['FCM 500']['eve_cost']))
            fcm500_eve += data_dict[data]['FCM 500']['eve_cost']
            
        if data_dict[data]['STD 250']['mor_cost'] is not None:
            mycanvas.drawRightString(x+95+45*2,y,str(data_dict[data]['STD 250']['mor_cost']))
            std250_mor += data_dict[data]['STD 250']['mor_cost']
            
        if data_dict[data]['STD 250']['eve_cost'] is not None:
            mycanvas.drawRightString(x+95+48*3,y,str(data_dict[data]['STD 250']['eve_cost']))
            std250_eve += data_dict[data]['STD 250']['eve_cost']
            
        if data_dict[data]['STD 500']['mor_cost'] is not None:
            mycanvas.drawRightString(x+95+48*4,y,str(data_dict[data]['STD 500']['mor_cost']))
            std500_mor += data_dict[data]['STD 500']['mor_cost']
            
        if data_dict[data]['STD 500']['eve_cost'] is not None:
            mycanvas.drawRightString(x+95+48*5,y,str(data_dict[data]['STD 500']['eve_cost']))
            std500_eve += data_dict[data]['STD 500']['eve_cost']
            
        if data_dict[data]['TM 500']['mor_cost'] is not None:
            mycanvas.drawRightString(x+95+49*6,y,str(data_dict[data]['TM 500']['mor_cost']))
            tm500_mor += data_dict[data]['TM 500']['mor_cost']
            
        if data_dict[data]['TM 500']['eve_cost'] is not None:
            mycanvas.drawRightString(x+95+49*7,y,str(data_dict[data]['TM 500']['eve_cost']))
            tm500_eve += data_dict[data]['TM 500']['eve_cost']

        if data_dict[data]['Tea 500']['mor_cost'] is not None:
            mycanvas.drawRightString(x+95+49*8,y,str(data_dict[data]['Tea 500']['mor_cost']))
            tea500_mor += data_dict[data]['Tea 500']['mor_cost']
            
        if data_dict[data]['Tea 500']['eve_cost'] is not None:
            mycanvas.drawRightString(x+95+49*9,y,str(data_dict[data]['Tea 500']['eve_cost']))
            tea500_eve += data_dict[data]['Tea 500']['eve_cost']    
            
        
        #lines
        # mycanvas.line(x-10,y+65,x-10,y-25)
        # mycanvas.line(x+45,y+65,x+45,y-25)
        # mycanvas.line(x+110,y+40,x+110,y-25)
        # mycanvas.line(x+110+65,y+65,x+110+65,y-25)
        # mycanvas.line(x+110+65*2,y+40,x+110+65*2,y-25)
        # mycanvas.line(x+110+65*3,y+65,x+110+65*3,y-25)
        # mycanvas.line(x+110+65*4,y+40,x+110+65*4,y-25)
        # mycanvas.line(x+110+65*5,y+65,x+110+65*5,y-25)
        # mycanvas.line(x+110+65*6,y+40,x+110+65*6,y-25)
        # mycanvas.line(x+110+65*7,y+65,x+110+65*7,y-25)

        mycanvas.line(x-10,y+65,x-10,y-25)
        mycanvas.line(x+40,y+65,x+40,y-25)
        mycanvas.line(x+95,y+40,x+95,y-25)
        mycanvas.line(x+95+50,y+65,x+95+50,y-25)
        mycanvas.line(x+95+50*2,y+40,x+95+50*2,y-25)
        mycanvas.line(x+95+50*3,y+65,x+95+50*3,y-25)
        mycanvas.line(x+95+50*4,y+40,x+95+50*4,y-25)
        mycanvas.line(x+95+50*5,y+65,x+95+50*5,y-25)
        mycanvas.line(x+95+50*6,y+40,x+95+50*6,y-25)
        mycanvas.line(x+95+50*7,y+65,x+95+50*7,y-25)
        mycanvas.line(x+95+50*8,y+40,x+95+50*8,y-25)
        mycanvas.line(x+95+50*9,y+65,x+95+50*9,y-25)
        
        y -= 25
        
    #lines
    mycanvas.line(x_head-13,y+20,x_head+562,y+20)
    mycanvas.line(x_head-13,y,x_head+562,y)
 
    #totals
    # mycanvas.drawString(x-5,y+7,"Grand Total")
    # mycanvas.drawRightString(x+105,y+7,str(fcm500_mor))
    # mycanvas.drawRightString(x+105+65,y+7,str(fcm500_eve))
    # mycanvas.drawRightString(x+105+65*2,y+7,str(std250_mor))
    # mycanvas.drawRightString(x+105+65*3,y+7,str(std250_eve))
    # mycanvas.drawRightString(x+105+65*4,y+7,str(std500_mor))
    # mycanvas.drawRightString(x+105+65*5,y+7,str(std500_eve))
    # mycanvas.drawRightString(x+105+65*6,y+7,str(tm500_mor))
    # mycanvas.drawRightString(x+105+65*7,y+7,str(tm500_eve))
    
    mycanvas.drawString(x-5,y+7,"Grand Total")
    mycanvas.drawRightString(x+95,y+7,str(round(fcm500_mor)))
    mycanvas.drawRightString(x+95+50,y+7,str(round(fcm500_eve)))
    mycanvas.drawRightString(x+95+50*2,y+7,str(round(std250_mor)))
    mycanvas.drawRightString(x+95+50*3,y+7,str(round(std250_eve)))
    mycanvas.drawRightString(x+95+50*4,y+7,str(round(std500_mor)))
    mycanvas.drawRightString(x+95+50*5,y+7,str(round(std500_eve)))
    mycanvas.drawRightString(x+95+50*6,y+7,str(round(tm500_mor)))
    mycanvas.drawRightString(x+95+50*7,y+7,str(round(tm500_eve)))
    mycanvas.drawRightString(x+95+50*8,y+7,str(round(tea500_mor)))
    mycanvas.drawRightString(x+95+50*9,y+7,str(round(tea500_eve)))
    

    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawRightString(585, 10,'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
    
    mycanvas.save()

    document = {
    'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document

@api_view(['POST'])
def serve_monthly_supplied_milk_for_card_customer(request):
    month = request.data['selected_month']
    year = request.data['selected_year']

    days = monthrange(year, month)[1]
    
    #-------------------------------------- Datas For Customers ---------------------------------------
    icustomer_sale_group = ICustomerSaleGroup.objects.filter(date__month=month,date__year=year,icustomer__customer_type_id__in=[1,5])

    customer_list = list(icustomer_sale_group.values_list('icustomersale__count', 'icustomersale__cost', 'icustomersale__cost_for_month', 'session_id', 'icustomersale__product_id', 'icustomersale__product__short_name', 'icustomersale__product__quantity', 'icustomer__union_for_icustomer_id', 'icustomer__union_for_icustomer__name', 'icustomer__customer_type__id'))
    customer_columns = ['count', 'cost', 'cost_for_month', 'session_id', 'product_id', 'product_name', 'product_quantity', 'customer_union_id', 'customer_union_name', 'customer_type_id']
    customer_df = pd.DataFrame(customer_list, columns=customer_columns)
    customer_df = customer_df.fillna('')

    customer_df['customer_code'] = ''
    customer_df['from_date'] = ''
    customer_df['to_date'] = ''
    customer_df['total_days'] = days
    customer_df['am'] = ''
    customer_df['pm'] = ''
    customer_df = customer_df.groupby(['product_id', 'product_name', 'product_quantity', 'customer_union_id', 'customer_union_name', 'session_id', 'customer_code', 'from_date', 'to_date', 'total_days', 'am', 'pm']).agg({'count':sum, 'cost':sum, 'cost_for_month':sum}).reset_index()                                                                               

    # customer_df['product_cost'] = cost

    final_df = customer_df[customer_df['session_id'] == 1]
    final_df = final_df.reset_index(drop=True)
    final_df.index += 1

    customer_eve = customer_df[customer_df['session_id'] == 2]
    customer_eve = customer_eve.reset_index(drop=True)
    customer_eve.index += 1

    for index,value  in customer_eve.iterrows():
        final_df.loc[(final_df['customer_union_name'] == value['customer_union_name'])&(final_df['product_name'] == value['product_name']) , ['pm']] = value['count']
        final_df.loc[(final_df['customer_union_name'] == value['customer_union_name'])&(final_df['product_name'] == value['product_name']), ['cost_for_month']] += value['cost_for_month']
        final_df.loc[(final_df['customer_union_name'] == value['customer_union_name'])&(final_df['product_name'] == value['product_name']), ['cost']] += value['cost']

    final_df['am'] = final_df['count']
    final_df = final_df.fillna(0)
    final_df = final_df.replace('',0)

    final_df['product_cost'] = final_df['cost'].astype(float)/(final_df['am'].astype(float) + final_df['pm'].astype(float))
    final_df['total_pockets_per_day'] = final_df['am'] + final_df['pm']
    final_df['pockets_per_ltr'] = 1000/final_df['product_quantity'].astype(float)
    final_df['total_ltrs_per_day'] = final_df['total_pockets_per_day'].astype(float) / final_df['pockets_per_ltr'].astype(float)
    final_df['total_ltrs_per_month'] = final_df['total_ltrs_per_day'].astype(float) * final_df['total_days']
    final_df = final_df.drop(columns=['count', 'session_id'])
    card_sales_dict = final_df.to_dict('r')

    #------------------------------- Datas For Employees and Ex-Employees -------------------------------

    exclude_sale_list = list(EmployeeOrderChangeLog.objects.filter(date_of_delivery__month=month, date_of_delivery__year=year, employee_order_change_mode_id=2).values_list('icustomer_sale_id', flat=True))

    icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(date__month=month,date__year=year,icustomer__customer_type_id__in=[2,3]).exclude(icustomersale__id__in=exclude_sale_list)

    icustomer_salegroup_list = list(icustomer_sale_group_obj.values_list('icustomersale__count', 'icustomersale__cost', 'icustomersale__cost_for_month', 'session_id', 'icustomersale__product_id', 'icustomersale__product__short_name', 'icustomersale__product__quantity', 'icustomer__union_for_icustomer_id', 'icustomer__union_for_icustomer__name', 'icustomer__customer_type__id'))                              
    icustomer_salegroup_columns = ['count', 'cost', 'cost_for_month', 'session_id', 'product_id', 'product_name', 'product_quantity', 'customer_union_id', 'customer_union_name', 'customer_type_id']
    customer_salegroup_df = pd.DataFrame(icustomer_salegroup_list, columns=icustomer_salegroup_columns)
    customer_salegroup_df['customer_code'] = ''
    customer_salegroup_df['from_date'] = ''
    customer_salegroup_df['to_date'] = ''
    customer_salegroup_df['total_days'] = days
    customer_salegroup_df['am'] = ''
    customer_salegroup_df['pm'] = ''
    customer_salegroup_df = customer_salegroup_df.groupby(['product_id', 'product_name', 'product_quantity', 'customer_union_id', 'customer_union_name', 'session_id', 'customer_code', 'from_date', 'to_date', 'total_days', 'am', 'pm']).agg({'count':sum, 'cost':sum, 'cost_for_month':sum}).reset_index()                                                                               
    customer_salegroup_df = customer_salegroup_df.fillna(0)

    final_df = customer_salegroup_df[customer_salegroup_df['session_id'] == 1]
    customer_salegroup_df_eve = customer_salegroup_df[customer_salegroup_df['session_id'] == 2]

    for index,value  in customer_salegroup_df_eve.iterrows():
        final_df.loc[(final_df['customer_union_name'] == value['customer_union_name'])&(final_df['product_name'] == value['product_name']), ['pm']] = value['count']
        final_df.loc[(final_df['customer_union_name'] == value['customer_union_name'])&(final_df['product_name'] == value['product_name']), ['cost_for_month']] += value['cost_for_month']
        final_df.loc[(final_df['customer_union_name'] == value['customer_union_name'])&(final_df['product_name'] == value['product_name']), ['cost']] += value['cost']

    final_df['am'] = final_df['count']
    final_df = final_df.fillna(0)
    final_df = final_df.replace('',0)

    final_df['product_cost'] = final_df['cost'].astype(float)/(final_df['am'].astype(float) + final_df['pm'].astype(float))
    final_df['total_pockets_per_day'] = final_df['am'] + final_df['pm']
    final_df['pockets_per_ltr'] = 1000/final_df['product_quantity'].astype(float)
    final_df['total_ltrs_per_day'] = final_df['total_pockets_per_day'].astype(float) / final_df['pockets_per_ltr'].astype(float)
    final_df['total_ltrs_per_month'] = final_df['total_ltrs_per_day'].astype(float) * final_df['total_days']
    final_df = final_df.drop(columns=['count', 'session_id'])

    #--------------------------------------- Edited Order/ New Order/ Deleted Order from employee order change log------------
    employee_order_change_log_obj = EmployeeOrderChangeLog.objects.filter(date_of_delivery__month=month, date_of_delivery__year=year)
    employee_order_change_list = list(employee_order_change_log_obj.values_list('total_days', 'from_date', 'to_date', 'employee_order_change_mode_id', 'employee_order_change_mode__name', 'icustomer__customer_code', 'icustomer__union_for_icustomer_id', 'icustomer__union_for_icustomer__name', 'product__short_name', 'product__quantity', 'cost_per_quantity', 'count', 'total_cost', 'icustomer_sale_id', 'session_id', 'time_created'))                                                               
    employee_order_change_columns = ['total_days', 'from_date', 'to_date', 'mode_id', 'mode_name', 'customer_code', 'customer_union_id', 'customer_union_name', 'product_name', 'product_quantity','cost', 'count', 'cost_for_month', 'icustomer_sale_id', 'session_id', 'time_created']
    employee_order_change_df = pd.DataFrame(employee_order_change_list,columns=employee_order_change_columns)
    employee_order_change_df["am"] = ''
    employee_order_change_df["pm"] = ''
    employee_order_change_df = employee_order_change_df.fillna(0)

    employee_order_change_df_mor = employee_order_change_df[employee_order_change_df['session_id'] == 1]
    employee_order_change_df_eve = employee_order_change_df[employee_order_change_df['session_id'] == 2]
    employee_order_change_df_mor['am'] = employee_order_change_df_mor['count']
    employee_order_change_df_eve['pm'] = employee_order_change_df_eve['count']
    employee_order_change_df = pd.concat([employee_order_change_df_mor, employee_order_change_df_eve], sort=True)

    employee_order_change_df = employee_order_change_df.fillna(0)
    employee_order_change_df = employee_order_change_df.replace('',0)

    employee_order_change_df = employee_order_change_df.sort_values(by=['time_created'])

    employee_order_change_df = employee_order_change_df.drop(columns=['mode_id', 'mode_name', 'count', 'session_id', 'time_created'])

    employee_order_change_df['product_cost'] = employee_order_change_df['cost'].astype(float)/(employee_order_change_df['am'].astype(float) + employee_order_change_df['pm'].astype(float))

    employee_order_change_df = pd.concat([final_df, employee_order_change_df], sort=True)
    employee_order_change_df = employee_order_change_df.drop(columns=['product_id', 'icustomer_sale_id'])
    employee_order_change_df = employee_order_change_df.fillna(0)

    employee_order_change_df['total_pockets_per_day'] = employee_order_change_df['am'] + employee_order_change_df['pm']
    employee_order_change_df['pockets_per_ltr'] = 1000/employee_order_change_df['product_quantity'].astype(float)
    employee_order_change_df['total_ltrs_per_day'] = employee_order_change_df['total_pockets_per_day'].astype(float) / employee_order_change_df['pockets_per_ltr'].astype(float)
    employee_order_change_df['total_ltrs_per_month'] = employee_order_change_df['total_ltrs_per_day'].astype(float) * employee_order_change_df['total_days']

    final_dict = employee_order_change_df.groupby('customer_union_name').apply(lambda x: x.to_dict('r')).to_dict()

    data_dict = {}
    data_dict['employees'] = final_dict
    data_dict['Card Sales'] = card_sales_dict
    data = generate_monthly_supplied_milk_for_card_customer_pdf(data_dict, month, year)
#   return data_dict
    return Response(data=data, status=status.HTTP_200_OK)

def generate_monthly_supplied_milk_for_card_customer_pdf(data_dict, month, year):
    month = month
    year = year
    datetime_object = datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%B")

    datetime_object = datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%B")

    file_name = "monthly_supplied_milk_for_card_customer for ( " + str(month_name) + "-" + str(year) + " )" + '.pdf'
    file_path = os.path.join('static/media', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=(inch*14,inch*12))

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(520, 840,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawCentredString(520, 815, 'Monthly Supplied Milk For Card Customer - ' + str(month_name) + "-" + str(year))

    x_head = 20
    y_head = 790


    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(x_head,y_head,"PARTICULARS")
    mycanvas.drawString(x_head+90,y_head,"MILK TYPE")
    mycanvas.drawString(x_head+170,y_head,"AM")
    mycanvas.drawString(x_head+230,y_head,"PM")
    mycanvas.drawString(x_head+290,y_head,"TOTAL")
    mycanvas.drawString(x_head+360,y_head,"QTY/DAY")
    mycanvas.drawString(x_head+430,y_head,"DAYS")
    mycanvas.drawString(x_head+480,y_head,"TOT.QTY")
    mycanvas.drawString(x_head+545,y_head,"RATE/ltr")
    mycanvas.drawString(x_head+600,y_head,"TOTAL VALUE")

    mycanvas.drawString(x_head+690,y_head,"CUSTOMER CODE")
    mycanvas.drawString(x_head+810,y_head,"FROM DATE")
    mycanvas.drawString(x_head+910,y_head,"TO DATE")

    mycanvas.setLineWidth(0)

    #lines
    mycanvas.line(x_head-5,y_head+15,x_head+980,y_head+15)
    mycanvas.line(x_head-5,y_head-5,x_head+980,y_head-5)

    x = 30
    y = 765


    mycanvas.setFont('Helvetica', 10)
    # mycanvas.drawString(x,y,str(data))
    am = 0
    pm = 0
    total = 0
    qty_day = 0
    total_qty = 0
    total_value = 0
    mycanvas.drawString(x-12,y,str('Card Sales'))
    for datas in data_dict['Card Sales']:
        mycanvas.drawString(x+90,y,str(datas['product_name']))
        mycanvas.drawRightString(x+200,y,str(round(datas['am'])))
        am += datas['am']

        mycanvas.drawRightString(x+260,y,str(round(datas['pm'])))
        pm += datas['pm']

        mycanvas.drawRightString(x+330,y,str(round(datas['total_pockets_per_day'])))
        total += datas['total_pockets_per_day']

        mycanvas.drawRightString(x+410,y,str(round(Decimal(datas['total_ltrs_per_day']), 3)))
        qty_day += datas['total_ltrs_per_day']

        mycanvas.drawRightString(x+450,y,str(datas['total_days']))
        mycanvas.drawRightString(x+530,y,str(round(Decimal(datas['total_ltrs_per_month']), 3)))
        total_qty += datas['total_ltrs_per_month']

        mycanvas.drawRightString(x+570,y,str(round(Decimal(datas['product_cost']), 2)))
        mycanvas.drawRightString(x+665,y,str(round(Decimal(datas['cost_for_month']), 2)))
        total_value += datas['cost_for_month']


        if datas['customer_code'] != 0:
            mycanvas.drawCentredString(x+725,y,str(datas['customer_code']))

        if datas['from_date'] != 0:
                from_date = datetime.strftime(datas['from_date'], '%d-%m-%Y')
                mycanvas.drawCentredString(x+830,y,str(from_date))

        if datas['to_date'] != 0:
            to_date = datetime.strftime(datas['to_date'], '%d-%m-%Y')
            mycanvas.drawCentredString(x+925,y,str(to_date))


        #lines
        mycanvas.setLineWidth(0)
        mycanvas.line(x+70,y-5,x+970,y-5)

        mycanvas.line(x-15,y+40,x-15,y-25)
        mycanvas.line(x+70,y+40,x+70,y-25)
        mycanvas.line(x+140,y+40,x+140,y-25)

        mycanvas.line(x+205,y+40,x+205,y-25)
        mycanvas.line(x+265,y+40,x+265,y-25)
        mycanvas.line(x+335,y+40,x+335,y-25)
        mycanvas.line(x+415,y+40,x+415,y-25)
        mycanvas.line(x+455,y+40,x+455,y-25)
        mycanvas.line(x+535,y+40,x+535,y-25)
        mycanvas.line(x+575,y+40,x+575,y-25)
        mycanvas.line(x+670,y+40,x+670,y-25)

        mycanvas.line(x+780,y+40,x+780,y-25)
        mycanvas.line(x+875,y+40,x+875,y-25)
        mycanvas.line(x+970,y+40,x+970,y-25)

        y -= 20
    mycanvas.line(x-15,y+15,x+70,y+15)
    mycanvas.line(x_head-5,y-5,x_head+980,y-5)
    mycanvas.drawString(x-10,y,"S U B T O T A L")

    mycanvas.drawRightString(x+200,y,str(round(am)))
    mycanvas.drawRightString(x+260,y,str(round(pm)))
    mycanvas.drawRightString(x+330,y,str(round(total)))
    mycanvas.drawRightString(x+410,y,str(round(Decimal(qty_day), 3)))
    mycanvas.drawRightString(x+530,y,str(round(Decimal(total_qty), 3)))
    mycanvas.drawRightString(x+665,y,str(round(Decimal(total_value), 2)))
    y -= 20
    #employees
    am1 = 0
    pm1 = 0
    total1 = 0
    qty_day1 = 0
    total_qty1 = 0
    total_value1 = 0
    for data in data_dict["employees"]:
        mycanvas.setFont('Helvetica', 9)
        headding_split = data.split(' ')
        if len(headding_split) >= 4:
            data1 = headding_split[0] + ' '+ headding_split[1] +' '+ headding_split[2]
            data2 = headding_split[3]
            mycanvas.drawString(x-12,y,str(data1))
            mycanvas.drawString(x-12,y-15,str(data2))
        else:
            mycanvas.drawString(x-12,y,str(data))
        mycanvas.setFont('Helvetica', 10)
        for datas in data_dict["employees"][data]:
            if datas['cost_for_month'] == 0:
                continue
            mycanvas.drawString(x+90,y,str(datas['product_name']))
            mycanvas.drawRightString(x+200,y,str(round(datas['am'])))
            am1 += datas['am']

            mycanvas.drawRightString(x+260,y,str(round(datas['pm'])))
            pm1 += datas['pm']

            mycanvas.drawRightString(x+330,y,str(round(datas['total_pockets_per_day'])))
            total1 += datas['total_pockets_per_day']

            mycanvas.drawRightString(x+410,y,str(round(Decimal(datas['total_ltrs_per_day']), 3)))
            qty_day1 += datas['total_ltrs_per_day']

            mycanvas.drawRightString(x+450,y,str(datas['total_days']))
            mycanvas.drawRightString(x+530,y,str(round(Decimal(datas['total_ltrs_per_month']), 3)))
            total_qty1 += datas['total_ltrs_per_month']

            mycanvas.drawRightString(x+570,y,str(round(Decimal(datas['product_cost']), 2)))
            mycanvas.drawRightString(x+665,y,str(round(Decimal(datas['cost_for_month']), 2)))
            total_value1 += datas['cost_for_month']

            if datas['customer_code'] != 0:
                mycanvas.drawCentredString(x+725,y,str(datas['customer_code']))

            if datas['from_date'] != 0:
                from_date = datetime.strftime(datas['from_date'], '%d-%m-%Y')
                mycanvas.drawCentredString(x+830,y,str(from_date))

            if datas['to_date'] != 0:
                to_date = datetime.strftime(datas['to_date'], '%d-%m-%Y')
                mycanvas.drawCentredString(x+925,y,str(to_date))

            #lines
            mycanvas.setLineWidth(0)
            mycanvas.line(x+70,y-5,x+970,y-5)

            mycanvas.line(x-15,y+40,x-15,y-45)
            mycanvas.line(x+70,y+40,x+70,y-45)
            mycanvas.line(x+140,y+40,x+140,y-45)

            mycanvas.line(x+205,y+40,x+205,y-45)
            mycanvas.line(x+265,y+40,x+265,y-45)
            mycanvas.line(x+335,y+40,x+335,y-45)
            mycanvas.line(x+415,y+40,x+415,y-45)
            mycanvas.line(x+455,y+40,x+455,y-45)
            mycanvas.line(x+535,y+40,x+535,y-45)
            mycanvas.line(x+575,y+40,x+575,y-45)
            mycanvas.line(x+670,y+40,x+670,y-45)

            mycanvas.line(x+780,y+40,x+780,y-25)
            mycanvas.line(x+875,y+40,x+875,y-25)
            mycanvas.line(x+970,y+40,x+970,y-25)

            y -= 20
        mycanvas.line(x-15,y+15,x+70,y+15)
    mycanvas.setLineWidth(0)
    mycanvas.line(x-15,y+15,x+70,y+15)
    mycanvas.line(x_head-5,y-5,x_head+980,y-5)
    mycanvas.drawString(x-10,y,"S U B T O T A L")

    mycanvas.drawRightString(x+200,y,str(round(am1)))
    mycanvas.drawRightString(x+260,y,str(round(pm1)))
    mycanvas.drawRightString(x+330,y,str(round(total1)))
    mycanvas.drawRightString(x+410,y,str(round(Decimal(qty_day1), 3)))
    mycanvas.drawRightString(x+530,y,str(round(Decimal(total_qty1), 3)))
    mycanvas.drawRightString(x+665,y,str(round(Decimal(total_value1), 2)))

    #total
    mycanvas.drawRightString(x+200,y-20,str(round(am+am1)))
    mycanvas.drawRightString(x+260,y-20,str(round(pm+pm1)))
    mycanvas.drawRightString(x+330,y-20,str(round(total+total1)))
    mycanvas.drawRightString(x+410,y-20,str(round(Decimal(qty_day+qty_day1), 3)))
    mycanvas.drawRightString(x+530,y-20,str(round(Decimal(total_qty+total_qty1), 3)))
    mycanvas.drawRightString(x+665,y-20,str(round(Decimal(float(total_value)+float(total_value1)), 2)))
    mycanvas.line(x_head-5,y-25,x_head+680,y-25)
    mycanvas.drawString(x-10,y-20,"T O T A L")
    mycanvas.save()

    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document

def serve_day_wise_tray_total_count_both_shift(frm_date, to_date, route, session_id):
    if route == 'temp':
        route_obj = Route.objects.filter(is_temp_route = True)
    elif route == 'route':
        route_obj = Route.objects.filter(is_temp_route = False)
    else:
        route_obj = Route.objects.filter()

    route_list = route_obj.filter(is_active=True, session_id__in=session_id, routetrace__date__range=[frm_date, to_date]).order_by('id').values_list('name', 'routetrace__routetracewisesalesummary__tray_count', 'session_id', 'routetrace__routetracewisesalesummary__product_id')
    route_column = ["route", 'tray_count', 'session', 'product_id']
    tray_count_df = pd.DataFrame(route_list, columns=route_column)

    mor_tray_count_df = tray_count_df[tray_count_df['session'] == 1]
    mor_tray_count_df = mor_tray_count_df[(tray_count_df['product_id'] != 10) & (tray_count_df['product_id'] != 26)]
    mor_tray_count_df = mor_tray_count_df.fillna(0).groupby('route').agg({'tray_count':sum}).reset_index().rename(columns={'tray_count': 'morning'})
    mor_tray_count_df = mor_tray_count_df.fillna(0)
    tray_total1 = 0
    for index,route in mor_tray_count_df.iterrows():
        if route.route[-4:] == 'temp':
            mor_tray_count_df.loc[mor_tray_count_df['route'] == route.route, ['route']] = route.route[:-8] + 'TEMP'
            tray_total1 += route.morning
        else:
            mor_tray_count_df.loc[mor_tray_count_df['route'] == route.route, ['route']] = route.route[:-4]
            tray_total1 += route.morning

    mor_tray_count_df.loc[len(mor_tray_count_df)] = ['Grand Total', tray_total1]


    eve_tray_count_df = tray_count_df[tray_count_df['session'] == 2]
    eve_tray_count_df = eve_tray_count_df[(tray_count_df['product_id'] != 10) & (tray_count_df['product_id'] != 26)]
    eve_tray_count_df = eve_tray_count_df.fillna(0).groupby('route').agg({'tray_count':sum}).reset_index().rename(columns={'tray_count': 'evening'})
    eve_tray_count_df = eve_tray_count_df.fillna(0)
    tray_total2 = 0
    for index,route in eve_tray_count_df.iterrows():
        if route.route[-4:] == 'temp':
            eve_tray_count_df.loc[eve_tray_count_df['route'] == route.route, ['route']] = route.route[:-8] + 'TEMP'
            tray_total2 += route.evening
        else:
            eve_tray_count_df.loc[eve_tray_count_df['route'] == route.route, ['route']] = route.route[:-4]
            tray_total2 += route.evening

    eve_tray_count_df.loc[len(eve_tray_count_df)] = ['Grand Total', tray_total2]

    tray_count_df = pd.merge(mor_tray_count_df, eve_tray_count_df, left_on='route', right_on='route', how='outer')

    tray_count_df = tray_count_df.fillna(0)
    tray_count_df['total'] = tray_count_df['morning'] + tray_count_df['evening'] 
    tray_count_df.index += 1

    print(tray_count_df)
    # tray_count_df.to_excel('tray_count.xlsx')
    tray_count_dict = tray_count_df.to_dict('r')

    # canvas

    date_given = datetime.strptime(frm_date, '%Y-%m-%d')
    date_given2 = datetime.strptime(to_date, '%Y-%m-%d')
    
    from_date = datetime.strftime(date_given, '%d/%m/%Y')
    to_date = datetime.strftime(date_given2, '%d/%m/%Y')

    session = 'Both'

    file_name = "daily_tray_despatch_details_for" + '_(' + str(date_given)+'-'+ str(date_given2)+ '-' +str(session) + ')_'+'.pdf'
    file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)

    mycanvas.setLineWidth(0)

    mycanvas.drawCentredString(300, 800, 'Daily Tray Despatch Details For ('+str(from_date) + ' to '+str(to_date) + ') - '+str(session))
    mycanvas.line(190, 796, 410, 796)

    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(60-30,740,'Sl_No')
    mycanvas.drawString(160-20,740,'Route')
    mycanvas.drawString(280-20,740,'Morning')
    mycanvas.drawString(380,740,'Evenig')
    mycanvas.drawString(500,740,'Total')

    mycanvas.line(20, 755, 570, 755)
    mycanvas.line(20, 730, 570, 730)

    mycanvas.setFont('Helvetica', 10)
    x = 55
    y = 715
    count = 1
    for data in tray_count_dict:
        if data != tray_count_dict[-1]:
            mycanvas.drawRightString(x,y,str(count))
            mycanvas.line(x+10, 755, x+10, y-5)
        else:
            mycanvas.line(x+10, 755, x+10, y+15)

        mycanvas.drawString(x+30,y,str(data['route']))
        mycanvas.drawRightString(x+260,y,str(data['morning']))
        mycanvas.drawRightString(x+380,y,str(data['evening']))
        mycanvas.drawRightString(x+500,y,str(data['total']))
        mycanvas.line(x-35, 755, x-35, y-5)
        mycanvas.line(x+170, 755, x+170, y-5)
        mycanvas.line(x+280, 755, x+280, y-5)
        mycanvas.line(x+400, 755, x+400, y-5)
        mycanvas.line(x+280, 755, x+280, y-5)
        mycanvas.line(x+515, 755, x+515, y-5)
        mycanvas.line(20, y+13, 570, y+13)
        if count % 39 == 0:
            mycanvas.line(20, y-5, 570, y-5)
            mycanvas.showPage()
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)

            #Date
            mycanvas.setLineWidth(0)

            mycanvas.drawCentredString(300, 800, 'Daily Tray Despatch Details For ('+str(from_date) + ' to '+str(to_date) + ') - '+str(session))
            mycanvas.line(190, 796, 410, 796)

            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(60-30,740,'Sl_No')
            mycanvas.drawString(160-20,740,'Route')
            mycanvas.drawString(280-20,740,'Morning')
            mycanvas.drawString(380,740,'Evenig')
            mycanvas.drawString(500,740,'Total')

            mycanvas.line(20, 755, 570, 755)
            mycanvas.line(20, 730, 570, 730)

            x = 55
            y = 710 + 20

        y -= 18.3
        count += 1

    mycanvas.line(20, y+13, 570, y+13)
    mycanvas.line(20, y+32, 570, y+32)    
    mycanvas.save()

    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document

@api_view(['POST'])
def serve_day_wise_tray_total_count(request):
    data_dict = request.data
    frm_date = data_dict['selected_from_date']
    to_date = data_dict['selected_to_date']
    session_id = data_dict['selected_session_id']
    route = data_dict['route']
    if session_id == 'both':
       data = serve_day_wise_tray_total_count_both_shift(frm_date, to_date,route, session_id=[1,2])
       return Response(data=data, status=status.HTTP_200_OK)

    if route == 'temp':
        route_obj = Route.objects.filter(is_temp_route = True)
    elif route == 'route':
        route_obj = Route.objects.filter(is_temp_route = False)
    else:
        route_obj = Route.objects.filter()
    
    route_list = route_obj.filter(is_active=True, session_id=session_id, routetrace__date__range=[frm_date, to_date]).order_by('id').values_list('name', 'routetrace__routetracewisesalesummary__tray_count', 'session_id', 'routetrace__routetracewisesalesummary__product_id')
    route_column = ["route", 'tray_count', 'session', 'product_id']
    tray_count_df = pd.DataFrame(route_list, columns=route_column)
    tray_count_df = tray_count_df[(tray_count_df['product_id'] != 10) & (tray_count_df['product_id'] != 26) & (tray_count_df['product_id'] != 22) & (tray_count_df['product_id'] != 23) & (tray_count_df['product_id'] != 24)]
    tray_count_df = tray_count_df.fillna(0).groupby('route').agg({'tray_count':sum}).reset_index()

    tray_total = 0
    for index,route in tray_count_df.iterrows():
        if route.route[-4:] == 'temp':
            tray_count_df.loc[tray_count_df['route'] == route.route, ['route']] = route.route[:-8] + 'TEMP'
            tray_total += route.tray_count
        else:
            tray_count_df.loc[tray_count_df['route'] == route.route, ['route']] = route.route[:-4]
            tray_total += route.tray_count

    tray_count_df.loc[len(tray_count_df)] = ['Grand Total', tray_total]

    # tray_count_df.to_excel('tray_count.xlsx')
    tray_count_dict = tray_count_df.to_dict('r')

    # canvas

    date_given1 = datetime.strptime(frm_date, '%Y-%m-%d')
    date_given2 = datetime.strptime(to_date, '%Y-%m-%d')
    from_date = datetime.strftime(date_given1, '%d/%m/%Y')
    to_date = datetime.strftime(date_given2, '%d/%m/%Y')

    if session_id == 1:
        session = 'Mor'
    else:
        session = 'Eve'

    file_name = "daily_tray_despatch_details_for" + '_(' + str(date_given1)+ ' to  ' + str(date_given2)+ '-'+str(session) + ')_.pdf'
    file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)

    mycanvas.setLineWidth(0)

    mycanvas.drawCentredString(300, 800, "Daily Tray Despatch Details For For ("+str(from_date) + ' to'  +str(to_date) + ')' +'-' + str(session)  )
    mycanvas.line(190, 796, 410, 796)

    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(60,740,'Sl_No')
    mycanvas.drawString(160,740,'Route')
    mycanvas.drawString(280,740,'Tray Count')

    mycanvas.line(55, 755, 370, 755)
    mycanvas.line(55, 730, 370, 730)

    mycanvas.setFont('Helvetica', 10)
    x = 90
    y = 715
    count = 1
    for data in tray_count_dict:
        if data != tray_count_dict[-1]:
            mycanvas.drawRightString(x,y,str(count))
            mycanvas.line(x+10, 755, x+10, y-5)
        else:
            mycanvas.line(x+10, 755, x+10, y+15)

        mycanvas.drawString(x+30,y,str(data['route']))
        mycanvas.drawRightString(x+260,y,str(data['tray_count']))
        mycanvas.line(x-35, 755, x-35, y-5)
        mycanvas.line(x+160, 755, x+160, y-5)
        mycanvas.line(x+280, 755, x+280, y-5)

        if count % 39 == 0:
            mycanvas.line(55, y-5, 370, y-5)
            mycanvas.showPage()
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)

            #Date
            mycanvas.setLineWidth(0)

            mycanvas.drawCentredString(300, 800, "Daily Tray Despatch Details For For ("+str(from_date) + ' to'  +str(to_date) + ')' +'-' + str(session))
            mycanvas.line(190, 796, 410, 796)

            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(60,740,'Sl_No')
            mycanvas.drawString(160,740,'Route')
            mycanvas.drawString(280,740,'Tray Count')

            mycanvas.line(55, 755, 370, 755)
            mycanvas.line(55, 730, 370, 730)

            x = 90
            y = 710 + 20

        y -= 18.3
        count += 1

    mycanvas.line(55, y+13, 370, y+13)
    mycanvas.line(55, y+32, 370, y+32)    

    mycanvas.save()

    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_monthly_counter_wise_report(request):
    print(request.data)
    counter = request.data['counter_id']
    month = request.data['selected_month']
    year = request.data['selected_year']

    counter_obj = Counter.objects.get(id=counter)
    if counter != 24:
        both_counter_sale_obj = CounterEmployeeTraceMap.objects.filter(collection_date__month=month, collection_date__year=year, counter_id=counter)
        mor_counter_sale_obj = CounterEmployeeTraceMap.objects.filter(collection_date__month=month, collection_date__year=year, counter_id=counter, counteremployeetracesalegroupmap__icustomer_sale_group__session_id=1)
        eve_counter_sale_obj = CounterEmployeeTraceMap.objects.filter(collection_date__month=month, collection_date__year=year, counter_id=counter, counteremployeetracesalegroupmap__icustomer_sale_group__session_id=2)

        #employees 
        employee_list =list(both_counter_sale_obj.values_list('employee__user_profile__user__first_name', flat=True))
        employee_list = list(set(employee_list))

        #for sale data
        both_product_pkt_list = list(both_counter_sale_obj.values_list('collection_date', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__product__short_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count'))

        #mor
        mor_product_pkt_list = list(mor_counter_sale_obj.values_list('collection_date', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__product__short_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count'))
        mor_product_cost_list = list(mor_counter_sale_obj.values_list('collection_date', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__cost_for_month'))

        #eve
        eve_product_pkt_list = list(eve_counter_sale_obj.values_list('collection_date', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__product__short_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count'))
        eve_product_cost_list = list(eve_counter_sale_obj.values_list('collection_date', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__cost_for_month'))


    else:
        both_counter_sale_obj = ICustomerSaleGroup.objects.filter(time_created__month=month, time_created__year=year, ordered_via_id__in=[1, 3])
        mor_counter_sale_obj = ICustomerSaleGroup.objects.filter(time_created__month=month, time_created__year=year, ordered_via_id__in=[1, 3], session_id=1)
        eve_counter_sale_obj = ICustomerSaleGroup.objects.filter(time_created__month=month, time_created__year=year, ordered_via_id__in=[1, 3], session_id=2)

        #employees
        employee_list = ['Online']

         #for sale data
        both_product_pkt_list = list(both_counter_sale_obj.values_list('time_created', 'icustomersale__product__short_name', 'icustomersale__count'))

        #mor
        mor_product_pkt_list = list(mor_counter_sale_obj.values_list('time_created', 'icustomersale__product__short_name', 'icustomersale__count'))
        mor_product_cost_list = list(mor_counter_sale_obj.values_list('time_created', 'icustomersale__count', 'icustomersale__cost_for_month'))

        #eve
        eve_product_pkt_list = list(eve_counter_sale_obj.values_list('time_created', 'icustomersale__product__short_name', 'icustomersale__count'))
        eve_product_cost_list = list(eve_counter_sale_obj.values_list('time_created', 'icustomersale__count', 'icustomersale__cost_for_month'))


    #--------------------------for individual product total count moring + eve----------------------#
    if not both_counter_sale_obj.exists():
        date_list = list(both_counter_sale_obj.values_list('collection_date', flat=True))
        both_product_pkt_df = pd.DataFrame(columns=['date', 'FCM 500', 'STD 250', 'STD 500', 'TM 500','Tea 500'])
        for i in date_list:
            both_product_pkt_df = both_product_pkt_df.append({'date': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0,'Tea 500':0}, ignore_index=True)
    else:
        product_obj = Product.objects.all()
        both_product_pkt_column = ['date', 'product_name', 'count']
        both_product_pkt_df = pd.DataFrame(both_product_pkt_list, columns=both_product_pkt_column)

        if counter == 24:
            for i in list(both_product_pkt_df['date']):
                both_product_pkt_df.loc[both_product_pkt_df['date'] == i, ['date']] = str(i)[:10]

        both_product_pkt_df = both_product_pkt_df.groupby(['date', 'product_name']).agg({'count': sum}).reset_index()

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        both_product_pkt_df = pd.pivot_table(both_product_pkt_df, index='date', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        both_product_pkt_df.columns = both_product_pkt_df.columns.droplevel(0) #remove amount
        both_product_pkt_df.columns.name = None  #remove categories
        both_product_pkt_df = both_product_pkt_df.reset_index() #index to columns

        for i in list(both_product_pkt_df.columns)[1:]:
            both_product_pkt_df[i] = round((both_product_pkt_df[i] * float(product_obj.get(short_name=i).quantity)) / 1000, 3)


    #----------------------for morning counter sale---------------#
    if not mor_counter_sale_obj.exists():
        date_list = list(both_counter_sale_obj.values_list('collection_date', flat=True))
        mor_counter_df = pd.DataFrame(columns=['date', 'FCM 500', 'STD 250', 'STD 500', 'TM 500', 'Tea 500' ,  'count', 'cost'])
        for i in date_list:
            mor_counter_df = mor_counter_df.append({'date': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0, 'Tea 500':0 ,'count': 0, 'cost': 0}, ignore_index=True)
    else:
        #morning_counter_sale_product_pkt_df 
        mor_product_pkt_column = ['date', 'product_name', 'count']
        mor_product_pkt_df = pd.DataFrame(mor_product_pkt_list, columns=mor_product_pkt_column)

        if counter == 24:
            for i in list(mor_product_pkt_df['date']):
                mor_product_pkt_df.loc[mor_product_pkt_df['date'] == i, ['date']] = str(i)[:10]

        mor_product_pkt_df = mor_product_pkt_df.groupby(['date', 'product_name']).agg({'count': sum}).reset_index()

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        mor_product_pkt_df = pd.pivot_table(mor_product_pkt_df, index='date', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        mor_product_pkt_df.columns = mor_product_pkt_df.columns.droplevel(0) #remove amount
        mor_product_pkt_df.columns.name = None  #remove categories
        mor_product_pkt_df = mor_product_pkt_df.reset_index() #index to columns
        #--

        #morning_counter_sale_product_cost_df
        mor_product_cost_column = ['date', 'count', 'cost']
        mor_product_cost_df = pd.DataFrame(mor_product_cost_list, columns=mor_product_cost_column)

        if counter == 24:
            for i in list(mor_product_cost_df['date']):
                mor_product_cost_df.loc[mor_product_cost_df['date'] == i, ['date']] = str(i)[:10]

        mor_product_cost_df = mor_product_cost_df.groupby('date').agg({'count': 'sum', 'cost': 'sum'}).reset_index()
        #--

        mor_counter_df = pd.merge(mor_product_pkt_df, mor_product_cost_df, left_on='date', right_on='date', how='left')

    #----------------------for evening counter sale---------------#
    if not eve_counter_sale_obj.exists():
        date_list = list(both_counter_sale_obj.values_list('collection_date', flat=True))
        eve_counter_df = pd.DataFrame(columns=['date', 'FCM 500', 'STD 250', 'STD 500', 'TM 500', 'Tea 500' , 'count', 'cost'])
        for i in date_list:
            eve_counter_df = eve_counter_df.append({'date': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0, 'Tea 500':0, 'count': 0, 'cost': 0}, ignore_index=True)

    else:
        #evening_counter_sale_product_pkt_df 
        eve_product_pkt_column = ['date', 'product_name', 'count']
        eve_product_pkt_df = pd.DataFrame(eve_product_pkt_list, columns=eve_product_pkt_column)

        if counter == 24:
            for i in list(eve_product_pkt_df['date']):
                eve_product_pkt_df.loc[eve_product_pkt_df['date'] == i, ['date']] = str(i)[:10]

        eve_product_pkt_df = eve_product_pkt_df.groupby(['date', 'product_name']).agg({'count': 'sum'}).reset_index()

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        eve_product_pkt_df = pd.pivot_table(eve_product_pkt_df, index='date', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        eve_product_pkt_df.columns = eve_product_pkt_df.columns.droplevel(0) #remove amount
        eve_product_pkt_df.columns.name = None  #remove categories
        eve_product_pkt_df = eve_product_pkt_df.reset_index() #index to columns
        #--

        #evening_counter_sale_product_cost_df
        eve_product_cost_column = ['date', 'count', 'cost']
        eve_product_cost_df = pd.DataFrame(eve_product_cost_list, columns=eve_product_cost_column)

        if counter == 24:
            for i in list(eve_product_cost_df['date']):
                eve_product_cost_df.loc[eve_product_cost_df['date'] == i, ['date']] = str(i)[:10]

        eve_product_cost_df = eve_product_cost_df.groupby('date').agg({'count': 'sum', 'cost': 'sum'}).reset_index()
        #--

        eve_counter_df = pd.merge(eve_product_pkt_df, eve_product_cost_df, left_on='date', right_on='date', how='left')
        eve_counter_df = eve_counter_df.reindex(columns=list(mor_counter_df.columns)).fillna(0)

    final_df = pd.merge(mor_counter_df, eve_counter_df, left_on='date', right_on='date', how='left').fillna(0)

    final_df = pd.merge(final_df, both_product_pkt_df, left_on='date', right_on='date', how='left').fillna(0)
    head_dict = {}
    for i in list(final_df.columns):
        if i[-1] == 'x':
            head_dict[i] = i[:-1]+'mor'
        elif i[-1] == 'y':
            head_dict[i] = i[:-1]+'eve'
        elif i != 'date' and  i[-1] != 'x' and i[-1] != 'y':
            head_dict[i] = i+'_total'

    final_df = final_df.rename(columns=head_dict)
    final_df['cost_mor'] = final_df['cost_mor'].astype(float)
    final_df['cost_eve'] = final_df['cost_eve'].astype(float)
    final_df = final_df.append(final_df.sum(), ignore_index=True)
    final_df.iloc[-1, final_df.columns.get_loc('date')] = 'Total'
    final_df.index += 1
    print(final_df.iloc[-1])

    # #-------------------------------------for_pdf----------------------------------------------------------------# 

    file_name = f"month_wise_counter_sale_for_{counter_obj.name} - ({month_name[month] +'-'+ str(year)})" + '.pdf'
    file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=(15 * inch, 12 * inch))

    # # ________Head_lines________#

    mycanvas.setFont('Helvetica', 15)
    mycanvas.drawCentredString(520, 840,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 14)

    mycanvas.drawCentredString(520, 825, str(f"Monthly Conter Wise Report for - {month_name[month] +'-'+ str(year)}"))
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.setLineWidth(0)

    x_axis = 30
    y_axis = 765

    employee_name = ''
    for employee in employee_list:
        employee_name += employee +', '
    mycanvas.drawString(x_axis, y_axis+30 , 'SALES MAN NAME : '+ str(employee_name))
    mycanvas.drawRightString(x_axis+1015, y_axis+30 , 'COUNTER : ' + f'{str(counter_obj.name)}')

    mycanvas.drawString(x_axis, y_axis, 'Sl No')
    mycanvas.line(x_axis-5, y_axis+20, x_axis-5, y_axis-30)
    mycanvas.drawString(x_axis+45, y_axis, 'Date')
    mycanvas.line(x_axis+30, y_axis+20, x_axis+30, y_axis-30)

    mycanvas.drawString(x_axis+120, y_axis, 'TM Packets')
    mycanvas.drawString(x_axis+100, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+145, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+185, y_axis-25, 'TOTAL Ltr')
    mycanvas.line(x_axis+90, y_axis+20, x_axis+90, y_axis-30)
    mycanvas.line(x_axis+240, y_axis+20, x_axis+240, y_axis-30)

    mycanvas.drawString(x_axis+255, y_axis, 'SM500 Packets')
    mycanvas.drawString(x_axis+250, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+290, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+335, y_axis-25, 'TOTAL Ltr')
    mycanvas.line(x_axis+390, y_axis+20, x_axis+390, y_axis-30)

    mycanvas.drawString(x_axis+400, y_axis, 'SM250 Packets')
    mycanvas.drawString(x_axis+410, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+450, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+485, y_axis-25, 'TOTAL Ltr')
    mycanvas.line(x_axis+535, y_axis+20, x_axis+535, y_axis-30)

    mycanvas.drawString(x_axis+555, y_axis, 'FCM500 Packets')
    mycanvas.drawString(x_axis+550, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+590, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+615, y_axis-25, 'TOTAL Ltr')
    mycanvas.line(x_axis+664, y_axis+20, x_axis+664, y_axis-30)

    mycanvas.drawString(x_axis+685, y_axis, 'TEA500 Packets')
    mycanvas.drawString(x_axis+680, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+720, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+750, y_axis-25, 'TOTAL Ltr')
    mycanvas.line(x_axis+800, y_axis+20, x_axis+800, y_axis-30)

    mycanvas.drawString(x_axis+845, y_axis, 'Total Litre')
    # mycanvas.drawString(x_axis+800, y_axis-25, 'AM')
    # mycanvas.drawString(x_axis+850, y_axis-25, 'PM')
    mycanvas.line(x_axis+905, y_axis+20, x_axis+905, y_axis-60)

    mycanvas.drawString(x_axis+955, y_axis, 'Total Value')
    # mycanvas.drawString(x_axis+915, y_axis-25, 'AM')
    # mycanvas.drawString(x_axis+975, y_axis-25, 'PM')
    mycanvas.line(x_axis+1020, y_axis+20, x_axis+1020, y_axis-30)

    mycanvas.line(x_axis-5, y_axis+20, x_axis+1020, y_axis+20)
    mycanvas.line(x_axis-5, y_axis-10, x_axis+1020, y_axis-10)

    mycanvas.line(x_axis-5, y_axis-30, x_axis+1020, y_axis-30)

    for index,i in final_df.iterrows():
        if i.date == 'Total':
            date = "Total"
        else:
            date = i.date
            if counter == 24:
                date = datetime.strptime(date, '%Y-%m-%d')
            date = datetime.strftime(date, '%d-%m-%Y')
            mycanvas.drawRightString(x_axis+20,y_axis-50,str(index))
        mycanvas.drawRightString(x_axis+85,y_axis-50,str(date))

        mycanvas.drawRightString(x_axis+120,y_axis-50,str(round(i['TM 500_mor'])))
        mycanvas.drawRightString(x_axis+175,y_axis-50,str(round(i['TM 500_eve'])))
        mycanvas.drawRightString(x_axis+235,y_axis-50,str(round(Decimal(i['TM 500_total']), 3)))

        mycanvas.drawRightString(x_axis+280,y_axis-50,str(round(i['STD 500_mor'])))
        mycanvas.drawRightString(x_axis+330,y_axis-50,str(round(i['STD 500_eve'])))
        mycanvas.drawRightString(x_axis+390,y_axis-50,str(round(Decimal(i['STD 500_total']), 3)))

        mycanvas.drawRightString(x_axis+430,y_axis-50,str(round(i['STD 250_mor'])))
        mycanvas.drawRightString(x_axis+470,y_axis-50,str(round(i['STD 250_eve'])))
        mycanvas.drawRightString(x_axis+520,y_axis-50,str(round(Decimal(i['STD 250_total']), 3)))

        mycanvas.drawRightString(x_axis+560,y_axis-50,str(round(i['FCM 500_mor'])))
        mycanvas.drawRightString(x_axis+600,y_axis-50,str(round(i['FCM 500_eve'])))
        mycanvas.drawRightString(x_axis+650,y_axis-50,str(round(Decimal(i['FCM 500_total']), 3)))

        mycanvas.drawRightString(x_axis+690,y_axis-50,str(round(i['Tea 500_mor'])))
        mycanvas.drawRightString(x_axis+730,y_axis-50,str(round(i['Tea 500_eve'])))
        mycanvas.drawRightString(x_axis+790,y_axis-50,str(round(Decimal(i['Tea 500_total']), 3)))

    #     mycanvas.drawRightString(x_axis+825,y_axis-50,str(round(i['count_mor'])))
        mycanvas.drawRightString(x_axis+865,y_axis-50,str(round(Decimal(i['TM 500_total'] + i['STD 500_total'] + i['STD 250_total'] + i['FCM 500_total'] + i['Tea 500_total']), 3)))
    #     mycanvas.drawRightString(x_axis+945,y_axis-50,str(round(i['cost_mor'])))
        mycanvas.drawRightString(x_axis+975,y_axis-50,str(round(Decimal(float(i['cost_eve']) + float(i['cost_mor'])), 2)))
        print(float(i['cost_eve']) + float(i['cost_mor']))
        #lines
        mycanvas.line(x_axis-5, y_axis+20, x_axis-5, y_axis-60)
        mycanvas.line(x_axis+30, y_axis+20, x_axis+30, y_axis-60)

        mycanvas.line(x_axis+90, y_axis+20, x_axis+90, y_axis-60)
        mycanvas.line(x_axis+135, y_axis-10, x_axis+135, y_axis-60)
        mycanvas.line(x_axis+185, y_axis-10, x_axis+185, y_axis-60)

        mycanvas.line(x_axis+240, y_axis+20, x_axis+240, y_axis-60)
        mycanvas.line(x_axis+285, y_axis-10, x_axis+285, y_axis-60)
        mycanvas.line(x_axis+335, y_axis-10, x_axis+335, y_axis-60)

        mycanvas.line(x_axis+390, y_axis+20, x_axis+390, y_axis-60)
        mycanvas.line(x_axis+435, y_axis-10, x_axis+435, y_axis-60)
        mycanvas.line(x_axis+480, y_axis-10, x_axis+480, y_axis-60)

        mycanvas.line(x_axis+535, y_axis+20, x_axis+535, y_axis-60)
        mycanvas.line(x_axis+575, y_axis-10, x_axis+575, y_axis-60)
        mycanvas.line(x_axis+610, y_axis-10, x_axis+610, y_axis-60)

        mycanvas.line(x_axis+665, y_axis+20, x_axis+665, y_axis-60)
        mycanvas.line(x_axis+710, y_axis-10, x_axis+710, y_axis-60)
        mycanvas.line(x_axis+750, y_axis-10, x_axis+750, y_axis-60)

        mycanvas.line(x_axis+800, y_axis+20, x_axis+800, y_axis-60)
    #     mycanvas.line(x_axis+835, y_axis-10, x_axis+835, y_axis-60)

        mycanvas.line(x_axis+1020, y_axis+20, x_axis+1020, y_axis-60)
    #     mycanvas.line(x_axis+955, y_axis-10, x_axis+955, y_axis-60)

        mycanvas.line(x_axis+1080, y_axis+20, x_axis+1080, y_axis-60)

        y_axis -= 22

    mycanvas.line(x_axis-5, y_axis-15, x_axis+1020, y_axis-15)
    mycanvas.line(x_axis-5, y_axis-37, x_axis+1020, y_axis-37)

    mycanvas.save()

    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_counter_employe_sale_for_date(request):
    counter_id_list = [4, 6, 7, 21, 25]
    date = request.data['selected_date']

    counter_employee_list = list(CounterEmployeeTraceMap.objects.filter(collection_date=date, counter_id__in=counter_id_list).values_list('counter__name', 'employee__user_profile__user__first_name'))
    counter_employee_column = ['counter', 'employee']
    counter_employee_df = pd.DataFrame(counter_employee_list, columns=counter_employee_column)
    counter_employee_df = counter_employee_df.drop_duplicates()

    counter_employee_df = counter_employee_df.groupby('employee').agg({'counter': list}).reset_index()
    counter_employee_dict = counter_employee_df.groupby('employee').apply(lambda x:x.to_dict('r')[0]).to_dict()
    counter_employee_dict

    #---------------------------------------------------

    both_counter_sale_obj = CounterEmployeeTraceMap.objects.filter(collection_date=date, counter_id__in=counter_id_list)
    mor_counter_sale_obj = both_counter_sale_obj.filter(counteremployeetracesalegroupmap__icustomer_sale_group__session_id=1)
    eve_counter_sale_obj = both_counter_sale_obj.filter(counteremployeetracesalegroupmap__icustomer_sale_group__session_id=2)

    #------------morning_evening-----#
    if not both_counter_sale_obj.exists():
        counter_list = list(both_counter_sale_obj.values_list('counter__name', flat=True))
        both_product_pkt_df = pd.DataFrame(columns=['date', 'FCM 500', 'STD 250', 'STD 500', 'TM 500','Tea 500'])
        for i in counter_list:
            both_product_pkt_df = both_product_pkt_df.append({'date': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0, 'Tea 500':0}, ignore_index=True)
    else:
        product_obj = Product.objects.all()
        both_product_pkt_list = list(both_counter_sale_obj.values_list('employee__user_profile__user__first_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__product__short_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count'))
        both_product_pkt_column = ['employee', 'product_name', 'count']
        both_product_pkt_df = pd.DataFrame(both_product_pkt_list, columns=both_product_pkt_column)
        both_product_pkt_df = both_product_pkt_df.groupby(['employee', 'product_name']).agg({'count': sum})

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        both_product_pkt_df = pd.pivot_table(both_product_pkt_df, index='employee', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        both_product_pkt_df.columns = both_product_pkt_df.columns.droplevel(0) #remove amount
        both_product_pkt_df.columns.name = None  #remove categories
        both_product_pkt_df = both_product_pkt_df.reset_index() #index to columns

        for i in list(both_product_pkt_df.columns)[1:]:
            both_product_pkt_df[i] = round((both_product_pkt_df[i] * float(product_obj.get(short_name=i).quantity)) / 1000, 3)

    #----------------------for morning counter sale---------------#

    if not mor_counter_sale_obj.exists():
        counter_list = list(both_counter_sale_obj.values_list('counter__name', flat=True))
        mor_counter_df = pd.DataFrame(columns=['employee', 'FCM 500', 'STD 250', 'STD 500', 'TM 500', 'Tea 500' ,'count', 'cost'])
        for i in counter_list:
            mor_counter_df = mor_counter_df.append({'counter': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0, 'Tea 500':0, 'count': 0, 'cost': 0}, ignore_index=True)
    else:
        #morning_counter_sale_product_pkt_df 
        mor_product_pkt_list = list(mor_counter_sale_obj.values_list('employee__user_profile__user__first_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__product__short_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count'))
        mor_product_pkt_column = ['employee', 'product_name', 'count']
        mor_product_pkt_df = pd.DataFrame(mor_product_pkt_list, columns=mor_product_pkt_column)
        mor_product_pkt_df = mor_product_pkt_df.groupby(['employee', 'product_name']).agg({'count': sum})

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        mor_product_pkt_df = pd.pivot_table(mor_product_pkt_df, index='employee', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        mor_product_pkt_df.columns = mor_product_pkt_df.columns.droplevel(0) #remove amount
        mor_product_pkt_df.columns.name = None  #remove categories
        mor_product_pkt_df = mor_product_pkt_df.reset_index() #index to columns
        #--

        #morning_counter_sale_product_cost_df
        mor_product_cost_list = list(mor_counter_sale_obj.values_list('employee__user_profile__user__first_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__cost_for_month'))
        mor_product_cost_column = ['employee', 'count', 'cost']
        mor_product_cost_df = pd.DataFrame(mor_product_cost_list, columns=mor_product_cost_column)
        mor_product_cost_df = mor_product_cost_df.groupby('employee').agg({'count': 'sum', 'cost': 'sum'}).reset_index()
        #--

        mor_counter_df = pd.merge(mor_product_pkt_df, mor_product_cost_df, left_on='employee', right_on='employee', how='left')


    #----------------------for evening counter sale---------------#

    if not eve_counter_sale_obj.exists():
        counter_list = list(both_counter_sale_obj.values_list('counter__name', flat=True))
        eve_counter_df = pd.DataFrame(columns=['employee', 'FCM 500', 'STD 250', 'STD 500', 'TM 500', 'Tea 500', 'count', 'cost'])
        for i in counter_list:
            eve_counter_df = eve_counter_df.append({'employee': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0, 'Tea 500':0, 'count': 0, 'cost': 0}, ignore_index=True)

    else:
        #evening_counter_sale_product_pkt_df 
        eve_product_pkt_list = list(eve_counter_sale_obj.values_list('employee__user_profile__user__first_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__product__short_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count'))
        eve_product_pkt_column = ['employee', 'product_name', 'count']
        eve_product_pkt_df = pd.DataFrame(eve_product_pkt_list, columns=eve_product_pkt_column)
        eve_product_pkt_df = eve_product_pkt_df.groupby(['employee', 'product_name']).agg({'count': 'sum'})

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        eve_product_pkt_df = pd.pivot_table(eve_product_pkt_df, index='employee', columns='product_name', aggfunc=min, fill_value=0)

        # convert_pivot_table_to_normal_df
        eve_product_pkt_df.columns = eve_product_pkt_df.columns.droplevel(0) #remove amount
        eve_product_pkt_df.columns.name = None  #remove categories
        eve_product_pkt_df = eve_product_pkt_df.reset_index() #index to columns
        #--

        #evening_counter_sale_product_cost_df
        eve_product_cost_list = list(eve_counter_sale_obj.values_list('employee__user_profile__user__first_name', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__count', 'counteremployeetracesalegroupmap__icustomer_sale_group__icustomersale__cost_for_month'))
        eve_product_cost_column = ['employee', 'count', 'cost']
        eve_product_cost_df = pd.DataFrame(eve_product_cost_list, columns=eve_product_cost_column)
        eve_product_cost_df = eve_product_cost_df.groupby('employee').agg({'count': 'sum', 'cost': 'sum'}).reset_index()
        #--

        eve_counter_df = pd.merge(eve_product_pkt_df, eve_product_cost_df, left_on='employee', right_on='employee', how='left')
        eve_counter_df = eve_counter_df.reindex(columns=list(mor_counter_df.columns)).fillna(0)

    final_df = pd.merge(mor_counter_df, eve_counter_df, left_on='employee', right_on='employee', how='left').fillna(0)

    final_df = pd.merge(final_df, both_product_pkt_df, left_on='employee', right_on='employee', how='left').fillna(0)


    #---------------------------------------------------for online --------------------------------------#

    both_counter_sale_obj = ICustomerSaleGroup.objects.filter(time_created__date=date, ordered_via_id__in=[1, 3])
    mor_counter_sale_obj = both_counter_sale_obj.filter(session_id=1)
    eve_counter_sale_obj = both_counter_sale_obj.filter(session_id=2)

    counter_list = ['Online']

    #--------------------------for individual product total count moring + eve----------------------#
    if not both_counter_sale_obj.exists():
        both_product_pkt_df = pd.DataFrame(columns=['employee', 'FCM 500', 'STD 250', 'STD 500', 'TM 500','Tea 500'])
        for i in counter_list:
            both_product_pkt_df = both_product_pkt_df.append({'employee': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0,'Tea 500':0,}, ignore_index=True)
    else:
        product_obj = Product.objects.all()
        both_product_pkt_list = list(both_counter_sale_obj.values_list('session_id', 'icustomersale__product__short_name', 'icustomersale__count'))
        both_product_pkt_column = ['employee', 'product_name', 'count']
        both_product_pkt_df = pd.DataFrame(both_product_pkt_list, columns=both_product_pkt_column)
        both_product_pkt_df['employee'] = 'Online'

        both_product_pkt_df = both_product_pkt_df.groupby(['employee', 'product_name']).agg({'count': sum})

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        both_product_pkt_df = pd.pivot_table(both_product_pkt_df, index='employee', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        both_product_pkt_df.columns = both_product_pkt_df.columns.droplevel(0) #remove amount
        both_product_pkt_df.columns.name = None  #remove categories
        both_product_pkt_df = both_product_pkt_df.reset_index() #index to columns

        for i in list(both_product_pkt_df.columns)[1:]:
            both_product_pkt_df[i] = round((both_product_pkt_df[i] * float(product_obj.get(short_name=i).quantity)) / 1000, 3)


    #----------------------for morning counter sale---------------#
    #morning_counter_sale_product_pkt_df 
    if not mor_counter_sale_obj.exists():
        mor_counter_df = pd.DataFrame(columns=['employee', 'FCM 500', 'STD 250', 'STD 500', 'TM 500', 'Tea 500', 'count', 'cost'])
        for i in counter_list:
            mor_counter_df = mor_counter_df.append({'employee': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0, 'Tea 500':0, 'count': 0, 'cost': 0}, ignore_index=True)
    else:
        mor_product_pkt_list = list(mor_counter_sale_obj.values_list('session_id', 'icustomersale__product__short_name', 'icustomersale__count'))
        mor_product_pkt_column = ['employee', 'product_name', 'count']
        mor_product_pkt_df = pd.DataFrame(mor_product_pkt_list, columns=mor_product_pkt_column)
        mor_product_pkt_df['employee'] = 'Online'
        mor_product_pkt_df = mor_product_pkt_df.groupby(['employee', 'product_name']).agg({'count': sum})

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        mor_product_pkt_df = pd.pivot_table(mor_product_pkt_df, index='employee', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        mor_product_pkt_df.columns = mor_product_pkt_df.columns.droplevel(0) #remove amount
        mor_product_pkt_df.columns.name = None  #remove categories
        mor_product_pkt_df = mor_product_pkt_df.reset_index() #index to columns
        #--

        #morning_counter_sale_product_cost_df
        mor_product_cost_list = list(mor_counter_sale_obj.values_list('session_id', 'icustomersale__count', 'icustomersale__cost_for_month'))
        mor_product_cost_column = ['employee', 'count', 'cost']
        mor_product_cost_df = pd.DataFrame(mor_product_cost_list, columns=mor_product_cost_column)
        mor_product_cost_df['employee'] = 'Online'
        mor_product_cost_df = mor_product_cost_df.groupby('employee').agg({'count': 'sum', 'cost': 'sum'}).reset_index()
        #--

        mor_counter_df = pd.merge(mor_product_pkt_df, mor_product_cost_df, left_on='employee', right_on='employee', how='left')

    #----------------------for evening counter sale---------------#
    #evening_counter_sale_product_pkt_df 
    if not eve_counter_sale_obj.exists():
        eve_counter_df = pd.DataFrame(columns=['employee', 'FCM 500', 'STD 250', 'STD 500', 'TM 500', 'Tea 500', 'count', 'cost'])
        for i in counter_list:
            eve_counter_df = eve_counter_df.append({'employee': i, 'FCM 500':0, 'STD 250':0, 'STD 500':0, 'TM 500':0, 'Tea 500':0, 'count': 0, 'cost': 0}, ignore_index=True)
    else:
        eve_product_pkt_list = list(eve_counter_sale_obj.values_list('session_id', 'icustomersale__product__short_name', 'icustomersale__count'))
        eve_product_pkt_column = ['employee', 'product_name', 'count']
        eve_product_pkt_df = pd.DataFrame(eve_product_pkt_list, columns=eve_product_pkt_column)
        eve_product_pkt_df['employee'] = 'Online'
        eve_product_pkt_df = eve_product_pkt_df.groupby(['employee', 'product_name']).agg({'count': 'sum'})

        #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        eve_product_pkt_df = pd.pivot_table(eve_product_pkt_df, index='employee', columns='product_name', aggfunc=min, fill_value=0)

        #convert_pivot_table_to_normal_df
        eve_product_pkt_df.columns = eve_product_pkt_df.columns.droplevel(0) #remove amount
        eve_product_pkt_df.columns.name = None  #remove categories
        eve_product_pkt_df = eve_product_pkt_df.reset_index() #index to columns
        #--

        #evening_counter_sale_product_cost_df
        eve_product_cost_list = list(eve_counter_sale_obj.values_list('session_id', 'icustomersale__count', 'icustomersale__cost_for_month'))
        eve_product_cost_column = ['employee', 'count', 'cost']
        eve_product_cost_df = pd.DataFrame(eve_product_cost_list, columns=eve_product_cost_column)
        eve_product_cost_df['employee'] = 'Online'
        eve_product_cost_df = eve_product_cost_df.groupby('employee').agg({'count': 'sum', 'cost': 'sum'}).reset_index()
        #--

        eve_counter_df = pd.merge(eve_product_pkt_df, eve_product_cost_df, left_on='employee', right_on='date', how='left')
        eve_counter_df = eve_counter_df.reindex(columns=list(mor_counter_df.columns)).fillna(0)

    final_df2 = pd.merge(mor_counter_df, eve_counter_df, left_on='employee', right_on='employee', how='left').fillna(0)
    final_df2 = pd.merge(final_df2, both_product_pkt_df, left_on='employee', right_on='employee', how='left').fillna(0)

    #final_df
    final_df = pd.concat([final_df, final_df2], ignore_index=True)
    head_dict = {}
    for i in list(final_df.columns):
        if i[-1] == 'x':
            head_dict[i] = i[:-1]+'mor'
        elif i[-1] == 'y':
            head_dict[i] = i[:-1]+'eve'
        elif i != 'employee' and  i[-1] != 'x' and i[-1] != 'y':
            head_dict[i] = i+'_total'

    final_df = final_df.rename(columns=head_dict)
    final_df = final_df.append(final_df.sum(), ignore_index=True)
    final_df.iloc[-1, final_df.columns.get_loc('employee')] = 'Total'
    final_df.index += 1


    # # #-------------------------------------for_pdf----------------------------------------------------------------# 

    date = datetime.strptime(date, '%Y-%m-%d')
    date = datetime.strftime(date, '%d-%m-%Y')

    file_name = f"date_wise_counter_sale_for({date})" + '.pdf'
    file_path = os.path.join('static/media/counter_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=(15 * inch, 12 * inch))

    # # ________Head_lines________#

    mycanvas.setFont('Helvetica', 15)
    mycanvas.drawCentredString(520, 840,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 14)

    mycanvas.drawCentredString(520, 825, str(f"Daily Conter Wise Report for - {date}"))
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.setLineWidth(0)

    x_axis = 30
    y_axis = 745

    # mycanvas.drawString(x_axis, y_axis+30 , 'SALES MAN NAME : '+ str(*employee_list))
    # mycanvas.drawRightString(x_axis+1015, y_axis+30 , 'COUNTER : ' + f'{str(counter_obj.name)}')

    mycanvas.drawString(x_axis, y_axis, 'Sl No')
    mycanvas.line(x_axis-5, y_axis+20, x_axis-5, y_axis-30)
    mycanvas.drawString(x_axis+40, y_axis, 'Employee')
    mycanvas.line(x_axis+30, y_axis+20, x_axis+30, y_axis-30)

    mycanvas.drawString(x_axis+160, y_axis, 'TM Packets')
    mycanvas.drawString(x_axis+120, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+170, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+220, y_axis-25, 'TOTAL')
    mycanvas.line(x_axis+100, y_axis+20, x_axis+100, y_axis-30)
    mycanvas.line(x_axis+270, y_axis+20, x_axis+270, y_axis-30)

    mycanvas.drawString(x_axis+320, y_axis, 'SM500 Packets')
    mycanvas.drawString(x_axis+290, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+340, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+390, y_axis-25, 'TOTAL')
    mycanvas.line(x_axis+440, y_axis+20, x_axis+440, y_axis-30)

    mycanvas.drawString(x_axis+490, y_axis, 'SM250 Packets')
    mycanvas.drawString(x_axis+460, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+510, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+560, y_axis-25, 'TOTAL')
    mycanvas.line(x_axis+610, y_axis+20, x_axis+610, y_axis-30)

    mycanvas.drawString(x_axis+660, y_axis, 'FCM500 Packets')
    mycanvas.drawString(x_axis+630, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+680, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+730, y_axis-25, 'TOTAL')
    mycanvas.line(x_axis+780, y_axis+20, x_axis+780, y_axis-30)

    mycanvas.drawString(x_axis+840, y_axis, 'TEA500 Packets')
    mycanvas.drawString(x_axis+810, y_axis-25, 'AM')
    mycanvas.drawString(x_axis+860, y_axis-25, 'PM')
    mycanvas.drawString(x_axis+910, y_axis-25, 'TOTAL')
    mycanvas.line(x_axis+960, y_axis+20, x_axis+960, y_axis-30)

    mycanvas.drawString(x_axis+985, y_axis, 'Total Litre')
    # mycanvas.drawString(x_axis+800, y_axis-25, 'AM')
    # mycanvas.drawString(x_axis+850, y_axis-25, 'PM')
    mycanvas.line(x_axis+1070, y_axis+20, x_axis+1070, y_axis-30)

    mycanvas.drawString(x_axis+1100, y_axis, 'Total Value')
    # mycanvas.drawString(x_axis+915, y_axis-25, 'AM')
    # mycanvas.drawString(x_axis+975, y_axis-25, 'PM')
    mycanvas.line(x_axis+1200, y_axis+20, x_axis+1200, y_axis-30)

    mycanvas.line(x_axis-5, y_axis+20, x_axis+1200, y_axis+20)
    mycanvas.line(x_axis-5, y_axis-10, x_axis+1200, y_axis-10)

    mycanvas.line(x_axis-5, y_axis-30, x_axis+1200, y_axis-30)

    for index,i in final_df.iterrows():

        if i.employee == 'Total':
            employee = "Total"
        else:
            employee = i.employee
            mycanvas.drawRightString(x_axis+20,y_axis-50,str(index))

        mycanvas.setFont('Helvetica', 9)
        mycanvas.drawString(x_axis+32,y_axis-50,str(employee)[:13])
        mycanvas.setFont('Helvetica', 10)
    #     if i.date != 'Online' and i.date != 'Total':
    #         for counter in counter_employee_dict[i.date]['counter']:
    #             mycanvas.drawRightString(x_axis+95,y_axis-70,str(counter))
    #             y_axis -= 20
        mycanvas.drawRightString(x_axis+150,y_axis-50,str(round(i['TM 500_mor'])))
        mycanvas.drawRightString(x_axis+200,y_axis-50,str(round(i['TM 500_eve'])))
        mycanvas.drawRightString(x_axis+265,y_axis-50,str(round(Decimal(i['TM 500_total']), 3)))

        mycanvas.drawRightString(x_axis+315,y_axis-50,str(round(i['STD 500_mor'])))
        mycanvas.drawRightString(x_axis+370,y_axis-50,str(round(i['STD 500_eve'])))
        mycanvas.drawRightString(x_axis+435,y_axis-50,str(round(Decimal(i['STD 500_total']), 3)))

        mycanvas.drawRightString(x_axis+485,y_axis-50,str(round(i['STD 250_mor'])))
        mycanvas.drawRightString(x_axis+535,y_axis-50,str(round(i['STD 250_eve'])))
        mycanvas.drawRightString(x_axis+605,y_axis-50,str(round(Decimal(i['STD 250_total']), 3)))

        mycanvas.drawRightString(x_axis+655,y_axis-50,str(round(i['FCM 500_mor'])))
        mycanvas.drawRightString(x_axis+705,y_axis-50,str(round(i['FCM 500_eve'])))
        mycanvas.drawRightString(x_axis+775,y_axis-50,str(round(Decimal(i['FCM 500_total']), 3)))

        mycanvas.drawRightString(x_axis+825,y_axis-50,str(round(i['Tea 500_mor'])))
        mycanvas.drawRightString(x_axis+875,y_axis-50,str(round(i['Tea 500_eve'])))
        mycanvas.drawRightString(x_axis+940,y_axis-50,str(round(Decimal(i['Tea 500_total']), 3)))

    #     mycanvas.drawRightString(x_axis+825,y_axis-50,str(round(i['count_mor'])))
        mycanvas.drawRightString(x_axis+1040,y_axis-50,str(round(Decimal(i['TM 500_total'] + i['STD 500_total'] + i['STD 250_total'] + i['FCM 500_total'] + i['Tea 500_total']), 3)))

    #     mycanvas.drawRightString(x_axis+945,y_axis-50,str(round(i['cost_mor'])))
        mycanvas.drawRightString(x_axis+1170,y_axis-50,str(round(Decimal(i['cost_eve'] + i['cost_mor']), 2)))

        #lines
        mycanvas.line(x_axis-5, y_axis+20, x_axis-5, y_axis-60)
        mycanvas.line(x_axis+30, y_axis+20, x_axis+30, y_axis-60)

        mycanvas.line(x_axis+100, y_axis+20, x_axis+100, y_axis-60)
        mycanvas.line(x_axis+160, y_axis-10, x_axis+160, y_axis-60)
        mycanvas.line(x_axis+210, y_axis-10, x_axis+210, y_axis-60)

        mycanvas.line(x_axis+270, y_axis+20, x_axis+270, y_axis-60)
        mycanvas.line(x_axis+325, y_axis-10, x_axis+325, y_axis-60)
        mycanvas.line(x_axis+380, y_axis-10, x_axis+380, y_axis-60)

        mycanvas.line(x_axis+440, y_axis+20, x_axis+440, y_axis-60)
        mycanvas.line(x_axis+495, y_axis-10, x_axis+495, y_axis-60)
        mycanvas.line(x_axis+550, y_axis-10, x_axis+550, y_axis-60)

        mycanvas.line(x_axis+610, y_axis+20, x_axis+610, y_axis-60)
        mycanvas.line(x_axis+670, y_axis-10, x_axis+670, y_axis-60)
        mycanvas.line(x_axis+720, y_axis-10, x_axis+720, y_axis-60)

        mycanvas.line(x_axis+780, y_axis+20, x_axis+780, y_axis-60)
        mycanvas.line(x_axis+840, y_axis-10, x_axis+840, y_axis-60)
        mycanvas.line(x_axis+890, y_axis-10, x_axis+890, y_axis-60)

        mycanvas.line(x_axis+950, y_axis+20, x_axis+950, y_axis-60)
    #     mycanvas.line(x_axis+835, y_axis-10, x_axis+835, y_axis-60)

        mycanvas.line(x_axis+1060, y_axis+20, x_axis+1060, y_axis-60)
    #     mycanvas.line(x_axis+955, y_axis-10, x_axis+955, y_axis-60)

        mycanvas.line(x_axis+1150, y_axis+20, x_axis+1150, y_axis-60)

        y_axis -= 22

    mycanvas.line(x_axis-5, y_axis-15, x_axis+1150, y_axis-15)
    mycanvas.line(x_axis-5, y_axis-37, x_axis+1150, y_axis-37)

    mycanvas.save()

    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def booth_wise_agent_details(request):
        # for business agent 
    other_union_list = []
    input_type = request.data['input_type']

    if input_type.lower() == 'business':
        business_code = request.data['business_code']
        business_agent_map_obj = BusinessAgentMap.objects.filter(business__code=business_code)
        route_business_list = list(RouteBusinessMap.objects.filter(business__code=business_code).values_list('business__code', 'route__name', 'route__session_id'))
    else:
        business_type_list = request.data['selected_business_type']
        if 6 in business_type_list:
            business_type_list.remove(6)
            other_union_list.append(6)
        if 7 in business_type_list:
            business_type_list.remove(7)
            other_union_list.append(7)
        zone_list = request.data['selected_zone']
        business_agent_map_obj = BusinessAgentMap.objects.filter(business__business_type_id__in=business_type_list, business__zone_id__in=zone_list)
        route_business_list = list(RouteBusinessMap.objects.filter(business__business_type_id__in=business_type_list, business__zone_id__in=zone_list).values_list('business__code', 'route__name', 'route__session_id'))

    business_agent_list = business_agent_map_obj.values_list('business__code', 'business__name', 'business__business_type__name', 'business__zone__name', 
                                                             'agent__agent_code', 'agent__first_name', 'agent__last_name', 'agent__agent_profile__mobile', 'agent__email', 'agent__aadhar_number', 
                                                             'agent__pan_number', 'agent__ration_card_number', 'agent__communication_address', 'agent__agentbankdetail__bank', 
                                                             'agent__agentbankdetail__branch', 'agent__agentbankdetail__ifsc_code', 'agent__agentbankdetail__account_holder_name', 
                                                             'agent__agentbankdetail__account_number')

    business_agent_columns = ['Booth Code', 'Booth Name', 'Booth Type', 'Zone', 'Agent Code', 
                              'First Name', 'Last Name', 'Mobile', 'Email', 'Aadhar Number', 'Pan Number', 
                              'Ration Card Number', 'Address', 'Bank', 'Bank Branch', 'IFSC Code', 
                              'Account Holder Name', 'Account Number']

    business_agent_df = pd.DataFrame(business_agent_list, columns=business_agent_columns)

    #Root business map
    route_business_column = ['Booth Code', 'Route Name', 'Session']
    route_business_df = pd.DataFrame(route_business_list, columns=route_business_column)

    mor_route_df = route_business_df[route_business_df['Session'] ==1].rename(columns = {'Route Name': 'Morning Route'}).drop(columns=['Session'])
    mor_route_df['Morning Route'] = mor_route_df['Morning Route'].str[:-4]
    eve_route_df = route_business_df[route_business_df['Session'] ==2].rename(columns = {'Route Name': 'Evening Route'}).drop(columns=['Session'])
    eve_route_df['Evening Route'] = eve_route_df['Evening Route'].str[:-4]

    route_business_df = pd.merge(mor_route_df, eve_route_df, left_on='Booth Code', right_on='Booth Code', how='outer')

    #booth_agent_route_df
    final_df = pd.merge(business_agent_df, route_business_df, left_on='Booth Code', right_on='Booth Code', how='left')

    if len(other_union_list) != 0:
        other_union_agent_map_obj = BusinessAgentMap.objects.filter(business__business_type_id__in=other_union_list)
        route_business_list = list(RouteBusinessMap.objects.filter(business__business_type_id__in=other_union_list).values_list('business__code', 'route__name', 'route__session_id'))
        other_union_agent_list = other_union_agent_map_obj.values_list('business__code', 'business__name', 'business__business_type__name', 'business__zone__name', 
                                                             'agent__agent_code', 'agent__first_name', 'agent__last_name', 'agent__agent_profile__mobile', 'agent__email', 'agent__aadhar_number', 
                                                             'agent__pan_number', 'agent__ration_card_number', 'agent__communication_address', 'agent__agentbankdetail__bank', 
                                                             'agent__agentbankdetail__branch', 'agent__agentbankdetail__ifsc_code', 'agent__agentbankdetail__account_holder_name', 
                                                             'agent__agentbankdetail__account_number')

        other_union_agent_columns = ['Booth Code', 'Booth Name', 'Booth Type', 'Zone', 'Agent Code', 
                                'First Name', 'Last Name', 'Mobile', 'Email', 'Aadhar Number', 'Pan Number', 
                                'Ration Card Number', 'Address', 'Bank', 'Bank Branch', 'IFSC Code', 
                                'Account Holder Name', 'Account Number']

        business_agent_df = pd.DataFrame(other_union_agent_list, columns=other_union_agent_columns)

        #Root business map
        route_business_column = ['Booth Code', 'Route Name', 'Session']
        route_business_df = pd.DataFrame(route_business_list, columns=route_business_column)

        mor_route_df = route_business_df[route_business_df['Session'] ==1].rename(columns = {'Route Name': 'Morning Route'}).drop(columns=['Session'])
        mor_route_df['Morning Route'] = mor_route_df['Morning Route'].str[:-4]
        eve_route_df = route_business_df[route_business_df['Session'] ==2].rename(columns = {'Route Name': 'Evening Route'}).drop(columns=['Session'])
        eve_route_df['Evening Route'] = eve_route_df['Evening Route'].str[:-4]

        route_business_df = pd.merge(mor_route_df, eve_route_df, left_on='Booth Code', right_on='Booth Code', how='outer')

        other_union_df = pd.merge(business_agent_df, route_business_df, left_on='Booth Code', right_on='Booth Code', how='left')
    
        final_df = pd.concat([final_df, other_union_df],  ignore_index=True)
    # print(final_df)
    final_df = final_df.fillna('')
    final_df.index += 1
    if input_type.lower() == 'business':
        file_name = f'agent_details_for_booth_{business_code}.xlsx'
    else:
        booth_typs = list(set(list(final_df['Booth Type'])))
        file_name = f'agent_details_for_{booth_typs}.xlsx'

    file_path = os.path.join('static/media', file_name)
    final_df.to_excel(file_path)
    print(file_name)

    document = {
        'file_name': file_name
    }
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def customer_details(request):
    input_type = request.data['input_type']
    document = {
        'data_availble': True
    }

    if input_type.lower() == 'booth code':
        if not Business.objects.filter(code=request.data['business_code']).exists():
            document['data_availble'] = False
            document['alert'] = 'Entered Booth Code is Not Valid'
            return Response(data=document, status=status.HTTP_200_OK)
        business_code = request.data['business_code']
        icustomer_obj = ICustomer.objects.filter(business__code=business_code)
        file_name = f'customer_details_for_booth_{business_code}.xlsx'

    elif input_type.lower() == 'customer code':
        print(request.data['customer_code'])
        if not ICustomer.objects.filter(customer_code=request.data['customer_code']).exists():
            document['data_availble'] = False
            document['alert'] = 'Entered Customer Code is Not Valid'
            return Response(data=document, status=status.HTTP_200_OK)
        customer_code = request.data['customer_code']
        
        icustomer_obj = ICustomer.objects.filter(customer_code=customer_code)
        file_name = f'customer_details_for_customer_{customer_code}.xlsx'

    else:
        customer_type_list = request.data['selected_customer_type']
        icustomer_obj = ICustomer.objects.filter(customer_type_id__in=customer_type_list)
        file_title_list = list(set(list(icustomer_obj.values_list('customer_type__name', flat=True))))
        file_name = f'customer_details_for_customer_type_{file_title_list}.xlsx'

    customer_data_list = list(icustomer_obj.values_list('customer_code', 'business__code', 'customer_type_id', 'customer_type__name', 'user_profile__user__first_name',
                                              'user_profile__user__last_name', 'aadhar_number', 'user_profile__mobile', 'user_profile__street',
                                              'user_profile__pincode', 'union_for_icustomer__name'))

    customer_data_column = ['Customer Code', 'Business Code', 'Customer Type Id', 'Customer Type', 'First Name', 'Last Name', 'Aadhar Number', 'Phone Number', 
                            'Address', 'Pin Code', 'Customer Union']

    customer_data_df = pd.DataFrame(customer_data_list, columns=customer_data_column) 
    customer_data_df = customer_data_df.fillna('')
    customer_data_df.loc[(customer_data_df['Customer Type Id'] == 1) | (customer_data_df['Customer Type Id'] == 5), 'Customer Union'] = 'CBE'

    customer_data_df = customer_data_df.drop(columns='Customer Type Id')

    customer_data_df.index += 1

    #xlsx
    file_path = os.path.join('static/media', file_name)
    customer_data_df.to_excel(file_path)
    print(file_name)

    document['file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)

@api_view(['POST'])
def serve_excel_for_society_bill(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']

    society_sale_list = list(DailySessionllyBusinessllySale.objects.filter(delivery_date__range=[from_date, to_date], business_type_id=10).values_list('business__code', 'business__name', 'total_cost'))
    society_columns = ["Code no", "Name Of Working Society", 'Amount']
    society_df = pd.DataFrame(society_sale_list, columns=society_columns)
    society_df = society_df.groupby(['Code no', 'Name Of Working Society']).agg({'Amount':sum}).reset_index()
    society_df.index += 1
    society_df["Amount"] = round(society_df["Amount"].astype(float))
    society_df.loc['Total', :]= society_df.iloc[:, 2:].sum(axis=0)

    file_name = 'society_total_sale_for ('+str(from_date)+" - "+str(to_date)+").xlsx"
    file_path = os.path.join('static/media/monthly_report/', file_name)
    society_df.to_excel(file_path)

    #xlsx
    document = {}
    document['file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_excel_for_employee_and_exemployee_product_and_quandity_details(request):
    print(request.data)
    year = request.data['year']
    month = request.data['month']
    month_name = calendar.month_abbr[month]
    customer_type_id = request.data['customer_type_id']
    show_alert = False

    icustomer_obj = ICustomer.objects.filter(customer_type_id__in=customer_type_id, icustomersalegroup__date__year=year, icustomersalegroup__date__month=month)
    if icustomer_obj.exists():
        customer_type = icustomer_obj[0].customer_type.name
    else:
        customer_type = ''
        
    icustomer_details_list = list(icustomer_obj.order_by('id').values_list('customer_code', 'user_profile__user__first_name', 'union_for_icustomer__name', 'icustomersalegroup__icustomersale__product__name', 'icustomersalegroup__icustomersale__count','business__code'))
    icustomer_details_columns = ['customer_code', 'customer_name', 'customer_union', 'product', 'count','booth_code']
    customer_df = pd.DataFrame(icustomer_details_list, columns=icustomer_details_columns)

    file_name = str(customer_type) + '_sale_for ('+str(month_name)+" - "+str(year)+").xlsx"
    file_path = os.path.join('static/media/monthly_report/', file_name)
    customer_df.to_excel(file_path)
    

    document = {}

    if customer_df.empty:
        show_alert = True
        document['alert'] = 'There is no data for this month !!!'
    
    document['file_name'] = file_name
    document['show_alert'] = show_alert
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_date_range_wise_sale_and_transaction(request):
    print(request.data)
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    business_code = request.data['business_code']

    sale_list  = list(SaleGroup.objects.filter(date__range=[from_date, to_date], business__code=business_code).order_by('sale__product__display_ordinal').values_list('date', 'sale__product__short_name', 'sale__product__quantity', 'sale__count', 'sale__cost', 'total_cost', 'session', 'id', 'time_created', 'time_modified', 'ordered_via__name'))                                               
    sale_column = ['date', 'product', 'quantity', 'count', 'cost', 'total_cost', 'session', 'sale_group_id', 'time_created', 'time_modified', 'ordered_via']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    # here i was changing liter to count but. i did not change key word litre it will cause error in follwing code. 
    # sale_df['litre'] = (sale_df['quantity'].astype(float)/1000)*sale_df['count'].astype(float)
    sale_df['litre'] = sale_df['count']
    sale_df = sale_df.groupby(['date', 'product', 'session']).agg({'quantity': 'first', 'count': sum, 'cost': sum, 'litre': sum, 'total_cost': 'first', 'sale_group_id':'first', 'time_created':'first', 'time_modified':'first', 'ordered_via': 'first'}).reset_index()


    # sale_df = sale_df[sale_df['date'].astype(str) == '2021-05-05']

    final_dict = {}

    for index,value in sale_df.iterrows():
        date = str(value['date'])
        session = str(value['session'])
        count = value['count']
        cost = value['cost']
        litre = value['litre']
        quantity = value['quantity']
        product = value['product']
        time_crested = value['time_created']
        time_modified = value['time_created']
        ordered_via = value['ordered_via']
        sale_group_id = value['sale_group_id']
        
        if not date in final_dict:
            final_dict[date] = {
                'sale': {},
                'total_amount': 0,
                
                'mor_order_time_created': '',
                'mor_order_time_modified': '',
                'mor_ordered_via': '',
                'mor_sale': 0,
                'mor_rid': None,

                'eve_order_time_created': '',
                'eve_order_time_modified': '',
                'eve_ordered_via': '',
                'eve_sale': 0,
                'eve_rid': None,
                
            }
        
            for products in Product.objects.all().exclude(id__in=[21,22]):
                if not products.short_name in final_dict[date]['sale']:
                    final_dict[date]['sale'][products.short_name] = {
                        'mor':{
                            'quantity': 0,
                            'count': 0,
                            'cost': 0,
                            'litre': 0
                        },
                        'eve':{
                            'quantity': 0,
                            'count': 0,
                            'cost': 0,
                            'litre': 0
                        }
                    } 

        if session == "1":
            final_dict[date]['sale'][product]['mor']['count'] = count
            final_dict[date]['sale'][product]['mor']['cost'] = cost
            final_dict[date]['sale'][product]['mor']['litre'] = litre
            final_dict[date]['sale'][product]['mor']['quantity'] = quantity
            final_dict[date]['total_amount'] += cost
            
            final_dict[date]['mor_order_time_created'] = time_crested
            final_dict[date]['mor_order_time_modified'] = time_modified
            final_dict[date]['mor_ordered_via'] = ordered_via
            final_dict[date]['mor_sale'] += cost

            if SuperSaleGroup.objects.filter(mor_sale_group_id=sale_group_id).exists():
                super_sale_group_id = SuperSaleGroup.objects.get(mor_sale_group_id=sale_group_id).id
                if SaleGroupTransactionTrace.objects.filter(super_sale_group_id=super_sale_group_id)[0].bank_transaction_id != None:
                    final_dict[date]['mor_rid'] = SaleGroupTransactionTrace.objects.filter(super_sale_group_id=super_sale_group_id)[0].bank_transaction.transaction_id
        
        if session == '2':
            final_dict[date]['sale'][product]['eve']['count'] = count
            final_dict[date]['sale'][product]['eve']['cost'] = cost
            final_dict[date]['sale'][product]['eve']['litre'] = litre
            final_dict[date]['sale'][product]['eve']['quantity'] = quantity
            final_dict[date]['total_amount'] += cost
            
            final_dict[date]['eve_order_time_created'] = time_crested
            final_dict[date]['eve_order_time_modified'] = time_modified
            final_dict[date]['eve_ordered_via'] = ordered_via
            final_dict[date]['eve_sale'] += cost

            if SuperSaleGroup.objects.filter(eve_sale_group_id=sale_group_id).exists():
                super_sale_group_id = SuperSaleGroup.objects.get(eve_sale_group_id=sale_group_id).id
                if SaleGroupTransactionTrace.objects.filter(super_sale_group_id=super_sale_group_id)[0].bank_transaction_id != None:
                    final_dict[date]['eve_rid'] = SaleGroupTransactionTrace.objects.filter(super_sale_group_id=super_sale_group_id)[0].bank_transaction.transaction_id

    return Response(data=final_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def validate_and_serve_data_for_mismatch(request):
    print(request.data)
    route_id = request.data['route_id']
    date = request.data['date']
    is_route_or_order_available = False
    if RouteTrace.objects.filter(route_id=route_id, date=date).exists():
        is_route_or_order_available = True
        route_close_time = RouteTrace.objects.get(route_id=route_id, date=date).indent_prepare_date_time
        if SaleGroup.objects.filter(date=date, route_id=route_id, time_modified__gte=route_close_time).exists():
            is_route_or_order_available = True
            sale_group_ids = list(SaleGroup.objects.filter(date=date, route_id=route_id, time_modified__gte=route_close_time).values_list('id', flat=True))
        else:
            is_route_or_order_available = False
    if is_route_or_order_available:
        sale_group_obj = SaleGroup.objects.filter(id__in=sale_group_ids)
        sale_group_list = list(sale_group_obj.values_list('id', 'business__code', 'total_cost', 'time_created', 'time_modified', 'ordered_by__first_name', 'ordered_via__name'))
        sale_group_column = ['id', 'booth_code', 'total_cost', 'time_created', 'time_modified', 'ordered_by', 'ordered_via_name']
        sale_group_df = pd.DataFrame(sale_group_list, columns=sale_group_column)
        data_dict = {
            'is_data_available': True,
            'mismatch_data': sale_group_df.to_dict('r')
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict = {
            'is_data_available': False,
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)


def find_base_price_from_gst(mrp, total_gst):
    whole_gst = (total_gst / 100) + 1
    base_price = mrp / whole_gst
    return round(base_price, 2)

def find_base_price_from_total_cost(total_cost, total_gst):
    whole_gst = (total_gst / 100) + 1
    base_price = Decimal(total_cost) / whole_gst
    return round(base_price, 2)


def find_the_gst_value(value, total_gst):
    gst = total_gst / 100
    return round(value * float(gst), 2)             


def data_in_format_function(date_in_string):
    date_in_format = datetime.strptime(str(date_in_string), '%Y-%m-%d')
    date = datetime.strftime(date_in_format, '%d-%m-%y')
    return date


@api_view(['POST'])
def generate_institution_bill_with_gst(request):
    print(request.data)
    business_codes = []
    business_types = {}
    business_names = request.data['business_type_list']
    route_ids = request.data['route_ids']
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    exclude_booth_code = request.data['exclude_booth_code']
    date_list = pd.date_range(start=from_date, end=to_date)
    if request.data['option_type'] == 'by_business':
      business_codes = request.data['business_code_list']
      business_types['business']= business_codes
      business_names = business_codes
    elif request.data['option_type'] == 'by_business_type':
      for business_type in request.data['business_type_list']:
          if business_type == 'private_institute':
              pvt_business_code_list = list(Business.objects.filter(business_type_id=4).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += pvt_business_code_list
              business_types['private_institute'] = pvt_business_code_list
          elif business_type == 'govt_institute':
              gvt_business_code_list = list(Business.objects.filter(business_type_id=5).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += gvt_business_code_list
              business_types['govt_institute'] = gvt_business_code_list
          elif business_type == 'union_parlour':
              union_parlour_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=1).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_codes += union_parlour_business_code_list
              business_types['union_parlour'] = union_parlour_business_code_list
          elif business_type == 'union_booth':
              union_booth_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=2).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_types['union_booth'] = union_booth_business_code_list
              business_codes += union_booth_business_code_list
          elif business_type == 'nilgris':
              nilgris_booth_business_code_list = list(Business.objects.filter(zone_id=11).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += nilgris_booth_business_code_list
              business_types['nilgris'] = nilgris_booth_business_code_list
          elif business_type == 'tirupur':
              tirupur_booth_business_code_list = list(Business.objects.filter(zone_id=13).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += tirupur_booth_business_code_list
              business_types['tirupur'] = tirupur_booth_business_code_list
          elif business_type == 'society':
              society_business_code_list = list(Business.objects.filter(business_type_id=10).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += society_business_code_list
              business_types['society'] = society_business_code_list
          elif business_type == 'booth':
              booth_business_code_list = list(Business.objects.filter(business_type_id__in=[1,2]).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += booth_business_code_list
              business_types['booth'] = booth_business_code_list
          elif business_type == 'wsd':
              wsd_business_code_list = list(Business.objects.filter(business_type_id=9).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += wsd_business_code_list
              business_types['wsd'] = wsd_business_code_list

    # check_dict = serve_product_price_for_date_range(business_codes, from_date, to_date, 2)
    # if check_dict['is_multiple_price']:
    #     return Response(data=check_dict, status=status.HTTP_200_OK)

    product_quantity_check_dict = serve_qty_and_short_name(from_date, to_date)
    if product_quantity_check_dict['is_multiple_qty']:
        return Response(data=document, status=status.HTTP_404_NOT_FOUND)

    sale_obj = Sale.objects.filter(sale_group__business__code__in=business_codes, sale_group__business__routebusinessmap__route_id__in=route_ids, sale_group__date__gte=from_date, sale_group__date__lte=to_date, product__group_id=2).exclude(product_id=28)
    sale_list = list(sale_obj.values_list('id', 'sale_group__business__user_profile_id','sale_group__business_id', 'sale_group__business__code', 'product_id', 'count', 'product__cgst_percent', 'product__sgst_percent', 'cost', 'product__hsn_code'))
    sale_column = ['id', 'user_profile_id', 'business_id', 'business_code', 'product_id', 'count', 'cgst_percent', 'sgst_percent' ,'cost', 'hsn_code']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)

    # price_from_trace = check_dict['return_data_as_dict']
    sale_df = sale_df.groupby(['business_id', 'product_id']).agg({'count': sum, 'user_profile_id': 'first', 'business_code': 'first', 'cgst_percent': 'first', 'sgst_percent': 'first', 'cost': sum, 'hsn_code': 'first'}).reset_index()
    short_name_and_qty = product_quantity_check_dict['product_dict']
    # write to pdf
    file_name = f"{from_date} - {to_date}-gst_bill.pdf"
    file_path = os.path.join('static/media/route_wise_report/', file_name)
    last_bill_number_count = InstititionBillNumberIdBank.objects.filter(id=1).first().last_count
    bill_no = int(last_bill_number_count) + 1
    print(sale_df.shape)
    document = {}
    if not sale_df.empty:
        sale_df['cost'] = sale_df['cost'].astype(float)
        sale_df['mrp'] = sale_df['cost'] / sale_df['count']
        sale_df['product_quantity'] = sale_df.apply(lambda x: short_name_and_qty[x['product_id']]['qty'], axis=1)
        sale_df['product_short_name'] = sale_df.apply(lambda x: short_name_and_qty[x['product_id']]['short_name'], axis=1)
        sale_df['cost_by_base_price'] = sale_df.apply(lambda x: find_base_price_from_total_cost(x['cost'], x['cgst_percent'] + x['sgst_percent']), axis=1)
        sale_df['cost_by_base_price'] = sale_df['cost_by_base_price'].astype(float)
        sale_df['base_price'] = sale_df['cost_by_base_price'] / sale_df['count']
        sale_df['product_quantity'] = sale_df['product_quantity'].astype(float)
        sale_df['total_gst_for_base_price'] = sale_df['cost'] - sale_df['cost_by_base_price']
        sale_df['qty_in_whole'] = (sale_df['count'] * sale_df['product_quantity']) / 1000

        

        mycanvas = canvas.Canvas(file_path, pagesize=A4)
        light_color = 0x000000
        dark_color = 0x000000

        for business in business_codes:
            business_obj = Business.objects.get(code=business)
            business_wise_sale_df = sale_df[sale_df['business_id'] == business_obj.id].reset_index()
            if business_wise_sale_df.empty:
                continue
            business_agent_map = BusinessAgentMap.objects.get(business_id=business_obj.id)
            if BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=business_obj.id, product_group_type_id=2).exists():
                temp_bill_number = BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=business_obj.id, product_group_type_id=2).first().bill_number
            else:
                temp_bill_number = bill_no
                business_wise_bill_number = BusinessWiseBillNumber(from_date=from_date, to_date=to_date, business_id=business_obj.id, bill_number=temp_bill_number, created_by_id=1, product_group_type_id=2)
                business_wise_bill_number.save()
                bill_no +=1
            x_a4 = 70
            y_a4 = 25
            mycanvas.setLineWidth(0)

            mycanvas.drawCentredString(300, 820,'Tax Invoice')
            mycanvas.line(15, 815, 570, 815)
            mycanvas.line(15, 610, 15, 815)

            mycanvas.setFont('Helvetica', 11)
            mycanvas.drawString(20, 800, "The Coimbatore Dist. Coop. Milk Producer's union Ltd.")
            mycanvas.drawString(20, 780, 'Pachapalayam, kalampalayam (PO), Coimbatore - 641010')
            mycanvas.drawString(20, 760, 'Ph: 0422-2607971, 2544777')
            mycanvas.drawString(20, 740, 'GSTIN/UIN: 33AAAAT7787L2ZU')
            mycanvas.drawString(20, 720, 'E-Mail: aavincbemkg@gmail.com')
            
            mycanvas.drawString(330, 800, 'Invoice No:')
            mycanvas.drawString(390, 800, str(temp_bill_number))
            mycanvas.drawString(440, 800, 'Date:')
            mycanvas.drawString(480, 800, data_in_format_function(to_date))
            
            
            mycanvas.drawString(330, 780, 'Item supplied period:')
            mycanvas.drawString(450, 780, data_in_format_function(from_date) + ' to ' + data_in_format_function(to_date))
            
            mycanvas.drawString(330, 760, 'Delivery Note:')
            
            mycanvas.drawString(330, 740, 'Despatch Document No:')
            mycanvas.drawString(330, 720, 'Delivery Note Date:')
            mycanvas.line(15, 712, 570, 712)
            mycanvas.line(320, 610, 320, 815)
            # buyer details
            
            address = business_agent_map.agent.agent_profile.street
            pincode = business_agent_map.agent.agent_profile.pincode
            communication_address = business_agent_map.agent.communication_address
            agent_first_name = business_agent_map.agent.first_name
            buyer_string = f"Buyer - {agent_first_name} ( {business_obj.code} )"
            mycanvas.drawString(20, 700, buyer_string)

            if communication_address is None:
                communication_address = ""
            if address is None:
                address = ""
            pan_number = business_agent_map.agent.pan_number
            if pan_number is None:
                pan_number = ""
            buyer_gst_number = business_agent_map.agent.agent_profile.gst_number
            if buyer_gst_number is None:
                buyer_gst_number = ""
            if pincode is None:
                pincode = ""

            mycanvas.drawString(20, 680, str(communication_address)+ ' ' + str(address))
            mycanvas.drawString(20, 660, str(pincode))
            
            mycanvas.drawString(20, 640, 'GST No : ' + str(buyer_gst_number))
            mycanvas.drawString(20, 620, 'PAN No : ' + str(pan_number))
            
            
            # route and vehile number
            morning_route = RouteBusinessMap.objects.filter(route__session_id=1, business_id=business_obj.id).first().route
            vehicle_number = RouteVehicleMap.objects.filter(route_id=morning_route.id).first().vehicle.licence_number
            
            mycanvas.drawString(330, 700, 'Despatched through')
            mycanvas.drawCentredString(380, 680, 'PVT Vehicle')
            mycanvas.drawCentredString(380, 660, str(vehicle_number))
            mycanvas.line(470, 712, 470, 610)
            mycanvas.drawString(480, 700, 'Destination')
            mycanvas.drawString(480, 670, str(morning_route.name[:-4]))
            mycanvas.line(15, 610, 570, 610)
            mycanvas.line(570, 610, 570, 815)
            
            x = 50
            y = 580
            mycanvas.line(15, y+10, 575, y+10)
            y_for_start_table = y+10
            # To Write headers
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawCentredString(x-15, y, "S.No")
            mycanvas.drawCentredString(x+40, y, "Description")
            mycanvas.drawCentredString(x+40, y-10, "of Goods")
            mycanvas.drawCentredString(x+105, y, "HSN")
            mycanvas.drawCentredString(x+160, y, "SGST")
            mycanvas.drawCentredString(x+160, y-10, "Rate")
            mycanvas.drawCentredString(x+240, y, "CGST")
            mycanvas.drawCentredString(x+240, y-10, "Rate")
            mycanvas.drawCentredString(x+300, y, "Quantity")
            mycanvas.drawCentredString(x+300, y-10, "(in Bags)")
            mycanvas.drawCentredString(x+360, y,"Quantity")
            mycanvas.drawCentredString(x+360, y-10, "(in Kgs)")
            mycanvas.drawCentredString(x+425, y, "Basic")
            mycanvas.drawCentredString(x+425, y-10, "Rate")
            mycanvas.drawCentredString(x+495, y, "Amount")
            mycanvas.drawCentredString(x+495, y-10, "(in Rs)")
            mycanvas.line(15, y-15, 570, y-15)
            mycanvas.setFont('Helvetica', 10)
            y = y - 30
            total_base_price = 0
            total_sgst_price = 0
            total_cgst_price = 0
            for sale_index, sale in business_wise_sale_df.iterrows():
                mycanvas.drawRightString(x-15, y, str(sale_index+1))
                mycanvas.drawCentredString(x+45, y, str(sale['product_short_name']))
                mycanvas.drawRightString(x+115, y, str(sale['hsn_code']))
                mycanvas.drawRightString(x+175, y, str(sale['sgst_percent']))
                mycanvas.drawRightString(x+255, y, str(sale['cgst_percent']))
                mycanvas.drawRightString(x+315, y, str(int(sale['count'])))
                mycanvas.drawRightString(x+375, y, str('%.2f' % sale['qty_in_whole']))
                mycanvas.drawRightString(x+440, y, str('%.2f' % sale['base_price']))
                mycanvas.drawRightString(x+520, y, str('%.2f' % sale['cost_by_base_price']))
                total_base_price += sale['cost_by_base_price']
                total_sgst_price += sale['total_gst_for_base_price'] / 2
                total_cgst_price += sale['total_gst_for_base_price'] / 2
                y -= 20
            
            total_mrp = total_base_price + total_sgst_price + total_cgst_price
            total_after_round_off = math.ceil(total_mrp)
            round_off_value = total_after_round_off - total_mrp
            if round(round_off_value) >= 1:
                round_off_value = 0
                total_after_round_off -= 1
            mycanvas.line(15, y+10, 575, y+10)
            y -= 5
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(x+25, y, 'Total')
            mycanvas.drawRightString(x+520, y, str('%.2f' % total_base_price))
            mycanvas.setFont('Helvetica', 10)
            y -= 20
            mycanvas.line(15, y+14, 575, y+14)
            mycanvas.drawString(x+25, y, 'Output SGST')
            mycanvas.drawRightString(x+520, y, str('%.2f' % total_sgst_price))
            y -= 20
            mycanvas.drawString(x+25, y, 'Output CGST')
            mycanvas.drawRightString(x+520, y, str('%.2f' % total_cgst_price))
            y -= 20
            mycanvas.drawString(x+25, y, 'Rounding off')
            mycanvas.drawRightString(x+520, y, str('%.2f' % round_off_value))
            y -= 20
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(x+25, y, 'Grand Total')
            mycanvas.drawRightString(x+520, y, str('%.2f' % total_after_round_off))
            mycanvas.setFont('Helvetica', 10)
            mycanvas.line(15, y-5, 575, y-5)
            mycanvas.line(15, y-5, 15, y_for_start_table)
            mycanvas.line(575, y-5, 575, y_for_start_table)
            
            y -= 30
            mycanvas.drawString(20, y, 'Amount Chargeable (in words)')
            y -= 20
            words = num2words(total_after_round_off, lang='en_IN')
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(20, y, words.upper())
            mycanvas.setFont('Helvetica', 10)
            y -= 30
            x += 40
            mycanvas.line(15, y+15, 575, y+15)
            y_for_second_table = y + 15
            hsn_wise_df = business_wise_sale_df.groupby('hsn_code').agg({'cgst_percent': 'first',  'sgst_percent': 'first', 'cost_by_base_price': sum, 'total_gst_for_base_price': sum}).reset_index()
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawCentredString(x-60, y, "S.No")
            mycanvas.drawCentredString(x-15, y, "HSN")
            mycanvas.drawCentredString(x+40, y, "Taxable")
            mycanvas.drawCentredString(x+40, y-10, "Value")
            mycanvas.drawCentredString(x+105, y, "SGST")
            mycanvas.drawCentredString(x+105, y-10, "Rate")
            mycanvas.drawCentredString(x+170, y, "SGST")
            mycanvas.drawCentredString(x+170, y-10, "Amount")
            mycanvas.drawCentredString(x+240, y, "CGST")
            mycanvas.drawCentredString(x+240, y-10, "Rate")
            mycanvas.drawCentredString(x+320, y, "CGST")
            mycanvas.drawCentredString(x+320, y-10, "Amount")
            mycanvas.drawCentredString(x+400, y, "Tax")
            mycanvas.drawCentredString(x+400, y-10, "Amount")
            mycanvas.setFont('Helvetica', 10)
            mycanvas.line(15, y-15, 575, y-15)
            y -= 30
            total_taxable = 0
            total_gst = 0
            for index, hsn_wise in hsn_wise_df.iterrows():
                spit_gst = hsn_wise['total_gst_for_base_price'] / 2
                mycanvas.drawCentredString(x-60, y, str(index+1))
                mycanvas.drawCentredString(x-25, y, str(hsn_wise['hsn_code']))
                mycanvas.drawRightString(x+60, y, str('%.2f' % hsn_wise['cost_by_base_price']))
                mycanvas.drawRightString(x+115, y, str(hsn_wise['cgst_percent']))
                mycanvas.drawRightString(x+195, y, str('%.2f' % spit_gst))
                mycanvas.drawRightString(x+255, y, str(hsn_wise['sgst_percent']))
                mycanvas.drawRightString(x+335, y, str('%.2f' % spit_gst))
                mycanvas.drawRightString(x+420, y, str('%.2f' % hsn_wise['total_gst_for_base_price']))
                total_taxable += hsn_wise['cost_by_base_price']
                total_gst += hsn_wise['total_gst_for_base_price']
                y -= 20
                
            y -= 5
            mycanvas.line(15, y+15, 575, y+15)
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(x-40, y, 'Total')
            mycanvas.drawRightString(x+60, y, str('%.2f' % total_taxable))
            mycanvas.drawRightString(x+420, y, str('%.2f' % total_gst))
            mycanvas.setFont('Helvetica', 10)
            y -= 30
            mycanvas.line(15, y+20, 575, y+20)
            mycanvas.line(15, y+20, 15, y_for_second_table)
            mycanvas.line(575, y+20, 575, y_for_second_table)
            mycanvas.drawString(20, y, 'Amount Chargeable (in words)')
            y -= 20
            words = num2words(round(total_gst), lang='en_IN')
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(20, y, words.upper())
            mycanvas.setFont('Helvetica', 10)
            
            
            y -= 30
            mycanvas.drawString(20, 120, "Company's PAN:")
            mycanvas.drawString(120, 120, "AAAAT7787L")
            
            mycanvas.drawString(420, 120, "For C.D.C.M.P.U.Ltd.,")
            mycanvas.drawString(420, 60, "Authorised Signature")
            
            mycanvas.drawString(20, 100, "Declaration")
            mycanvas.drawString(20, 80, "1. The rates are subject to revision from time to time")
            mycanvas.drawString(20, 60, "2. Goods once sold cannot be taken back")
            mycanvas.showPage()
        mycanvas.save()
        bill_idbank_obj = InstititionBillNumberIdBank.objects.filter(id=1).first()
        bill_idbank_obj.last_count = int(bill_no) - 1
        bill_idbank_obj.save()
        document = {}
        document['file_name'] = file_name
        document['is_file_available'] = True
        try:
            image_path = file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)
    return Response(data=document, status=status.HTTP_200_OK)

@api_view(['POST'])
def serve_json_fermented_products_govt_upload(request):
    print(request.data)
    business_codes = []
    business_types = {}
    business_names = request.data['business_type_list']
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    exclude_booth_code = request.data['exclude_booth_code']
    date_list = pd.date_range(start=from_date, end=to_date)
    if request.data['option_type'] == 'by_business':
      business_codes = request.data['business_code_list']
      business_types['business']= business_codes
      business_names = business_codes
    elif request.data['option_type'] == 'by_business_type':
      for business_type in request.data['business_type_list']:
          if business_type == 'private_institute':
              pvt_business_code_list = list(Business.objects.filter(business_type_id=4).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += pvt_business_code_list
              business_types['private_institute'] = pvt_business_code_list
          elif business_type == 'govt_institute':
              gvt_business_code_list = list(Business.objects.filter(business_type_id=5).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += gvt_business_code_list
              business_types['govt_institute'] = gvt_business_code_list
          elif business_type == 'union_parlour':
              union_parlour_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=1).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_codes += union_parlour_business_code_list
              business_types['union_parlour'] = union_parlour_business_code_list
          elif business_type == 'union_booth':
              union_booth_business_code_list = list(BusinessOwnParlourTypeMap.objects.filter(own_parlour_type_id=2).values_list('business__code', flat=True).exclude(business__code__in=exclude_booth_code))
              business_types['union_booth'] = union_booth_business_code_list
              business_codes += union_booth_business_code_list
          elif business_type == 'nilgris':
              nilgris_booth_business_code_list = list(Business.objects.filter(zone_id=11).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += nilgris_booth_business_code_list
              business_types['nilgris'] = nilgris_booth_business_code_list
          elif business_type == 'tirupur':
              tirupur_booth_business_code_list = list(Business.objects.filter(zone_id=13).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += tirupur_booth_business_code_list
              business_types['tirupur'] = tirupur_booth_business_code_list
          elif business_type == 'society':
              society_business_code_list = list(Business.objects.filter(business_type_id=10).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += society_business_code_list
              business_types['society'] = society_business_code_list
          elif business_type == 'booth':
              booth_business_code_list = list(Business.objects.filter(business_type_id__in=[1,2]).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += booth_business_code_list
              business_types['booth'] = booth_business_code_list
          elif business_type == 'wsd':
              wsd_business_code_list = list(Business.objects.filter(business_type_id=9).values_list('code', flat=True).exclude(code__in=exclude_booth_code))
              business_codes += wsd_business_code_list
              business_types['wsd'] = wsd_business_code_list
    product_quantity_check_dict = serve_qty_and_short_name(from_date, to_date)
    if product_quantity_check_dict['is_multiple_qty']:
        return Response(data=document, status=status.HTTP_404_NOT_FOUND)
    sale_obj = Sale.objects.filter(sale_group__business__code__in=business_codes, sale_group__date__gte=from_date, sale_group__date__lte=to_date, product__group_id=2).exclude(product_id=28)
    sale_list = list(sale_obj.values_list('id', 'sale_group__business__user_profile_id','sale_group__business_id', 'sale_group__business__code', 'product_id', 'count', 'product__cgst_percent', 'product__sgst_percent', 'cost', 'product__hsn_code'))
    sale_column = ['id', 'user_profile_id', 'business_id', 'business_code', 'product_id', 'count', 'cgst_percent', 'sgst_percent' ,'cost', 'hsn_code']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)

    sale_df = sale_df.groupby(['business_id', 'product_id']).agg({'count': sum, 'user_profile_id': 'first', 'business_code': 'first', 'cgst_percent': 'first', 'sgst_percent': 'first', 'cost': sum, 'hsn_code': 'first'}).reset_index()
    short_name_and_qty = product_quantity_check_dict['product_dict']
    
    print(sale_df.shape)
    document = {}
    final_list = []
    if not sale_df.empty:
        sale_df['cost'] = sale_df['cost'].astype(float)
        sale_df['mrp'] = sale_df['cost'] / sale_df['count']
        sale_df['product_quantity'] = sale_df.apply(lambda x: short_name_and_qty[x['product_id']]['qty'], axis=1)
        sale_df['product_short_name'] = sale_df.apply(lambda x: short_name_and_qty[x['product_id']]['short_name'], axis=1)
        sale_df['cost_by_base_price'] = sale_df.apply(lambda x: find_base_price_from_total_cost(x['cost'], x['cgst_percent'] + x['sgst_percent']), axis=1)
        sale_df['cost_by_base_price'] = sale_df['cost_by_base_price'].astype(float)
        sale_df['base_price'] = sale_df['cost_by_base_price'] / sale_df['count']
        sale_df['product_quantity'] = sale_df['product_quantity'].astype(float)
        sale_df['total_gst_for_base_price'] = sale_df['cost'] - sale_df['cost_by_base_price']
        sale_df['qty_in_whole'] = (sale_df['count'] * sale_df['product_quantity']) / 1000 

        for business_code in business_codes:
        #     print(business_code)
            business_obj = Business.objects.get(code=business_code)
            business_wise_sale_df = sale_df[sale_df['business_id'] == business_obj.id].reset_index()
            if business_wise_sale_df.empty:
                continue
            business_agent_map = BusinessAgentMap.objects.get(business_id=business_obj.id)
            if BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=business_obj.id, product_group_type_id=2).exists():
                temp_bill_number = BusinessWiseBillNumber.objects.filter(from_date=from_date, to_date=to_date, business_id=business_obj.id, product_group_type_id=2).first().bill_number
        #         print(temp_bill_number)
                buyer_gst_number = business_agent_map.agent.agent_profile.gst_number
                if buyer_gst_number is not None:
                    #print('buyer_gst_number', buyer_gst_number)
                    main_dict = {
                        "version": "1.1",
                        "TranDtls": {},
                        "DocDtls": {},
                        "SellerDtls": {},
                        "BuyerDtls": {},
                        "ValDtls": {},
                        "ItemList": []
                    }
                    transaction_details = {
                        "TaxSch":"GST",
                        "SupTyp":"B2B",
                        "IgstOnIntra":"N",
                        "RegRev":"N",
                        "EcmGstin": None
                    }
                    main_dict["TranDtls"] = transaction_details
                    
                    bill_number = temp_bill_number
                    date_in_format = datetime.strptime(str(to_date), '%Y-%m-%d')
                    bill_date_in_format = datetime.strftime(date_in_format, '%d/%m/%Y')            
                    doc_details = {
                        "Typ":"INV",
                        "No": str(bill_number),
                        "Dt": bill_date_in_format
                    }
                    main_dict["DocDtls"] = doc_details
                    
                    seller_details = {
                        "Gstin": "33AAAAT7787L2ZU",
                        "LglNm": "THE COIMBATORE DISTRICT CO OPERATIVE MILK PRODUCER'S UNION LTD., E.D.912",
                        "TrdNm": None,
                        "Addr1":"PACHAPALAYAM,",
                        "Addr2":"KALAMPALAYAM (P.O)",
                        "Loc": "COIMBATORE",
                        "Pin": 641001,
                        "Stcd": "33",
                        "Ph": None,
                        "Em": None
                    }
                    main_dict["SellerDtls"] = seller_details
                    
                    buyer_gst_number = business_agent_map.agent.agent_profile.gst_number
                    agent_first_name = business_agent_map.agent.first_name
                    booth_number = business_agent_map.business.code
                    pincode = business_agent_map.agent.agent_profile.pincode
                    district = business_agent_map.agent.agent_profile.district.name
                    address = business_agent_map.agent.agent_profile.street
                    pan_number = business_agent_map.agent.pan_number
                    # if buyer_gst_number is not None:
                    #     buyer_gst_number = 'NA'
                    buyer_details = {
                        "Gstin": buyer_gst_number,
                        "LglNm": str(agent_first_name) + ' (' + str(booth_number) + ') (PAN NO ' + str(pan_number) + ')',
                        "TrdNm": None,
                        "Pos": "33",
                        "Addr1": address,
                        "Addr2": None,
                        "Loc": district.upper(),
                        "Pin": pincode,
                        "Stcd": "33",
                        "Ph": None,
                        "Em": None
                    }
                    main_dict["BuyerDtls"] = buyer_details
                    
                    total_gst_amount = business_wise_sale_df['total_gst_for_base_price'].sum()
                    total_basic_cost = business_wise_sale_df['cost_by_base_price'].sum()
                    total_cgst_cost = total_gst_amount/2
                    total_sgst_cost = total_gst_amount/2
                    total_cost = total_gst_amount + total_basic_cost
                    total_cost_round = math.ceil(total_cost)
                    rounded_value = total_cost_round - total_cost
                    if round(rounded_value) >= 1:
                        rounded_value = 0
                        total_cost_round -= 1
                    value_details = {
                        "AssVal": round(float(total_basic_cost), 2),
                        "IgstVal": 0,
                        "CgstVal": round(float(total_cgst_cost), 2),
                        "SgstVal": round(float(total_sgst_cost), 2),
                        "CesVal": 0,
                        "StCesVal": 0,
                        "Discount": 0,
                        "OthChrg": 0,
                        "RndOffAmt": round(float(rounded_value), 2), 
                        "TotInvVal": round(float(total_cost_round), 2)
                    }
                    main_dict["ValDtls"] = value_details
                    
                    s_no = 1
                    item_list = []
                    for index, sale in business_wise_sale_df.iterrows():
                        
                        unit_price = sale['mrp']
                        Discount = 0
                        PreTaxVal = 0
                        ass_amount = sale['cost_by_base_price'] - Discount - PreTaxVal
                        product_obj = Product.objects.get(id=sale['product_id'])
                        total_gst_percentage = product_obj.cgst_percent + product_obj.sgst_percent
                        
                        total_basic_cost = sale['cost_by_base_price']
                        total_gst_amount = sale['total_gst_for_base_price']
                        total_cgst_cost = total_gst_amount/2
                        total_sgst_cost = total_gst_amount/2
                        total_cost = total_gst_amount + total_basic_cost
                        
                        item_dict = {
                            "SlNo": str(s_no),
                            "PrdDesc": str(sale['product_short_name']),
                            "IsServc": "N",
                            "HsnCd": str(product_obj.hsn_code),
                            "Qty": int(sale['count']),
                            "Unit": "PAC",
                            "UnitPrice": round(float(unit_price), 2),
                            "TotAmt": round(float(total_basic_cost), 2),
                            "Discount": 0,
                            "PreTaxVal": 0,
                            "AssAmt": round(float(ass_amount), 2),
                            "GstRt": round(float(total_gst_percentage), 2),
                            "IgstAmt": 0,
                            "CgstAmt": round(float(total_cgst_cost), 2),
                            "SgstAmt": round(float(total_sgst_cost), 2),
                            "CesRt":0,
                            "CesAmt":0,
                            "CesNonAdvlAmt":0,
                            "StateCesRt":0,
                            "StateCesAmt":0,
                            "StateCesNonAdvlAmt":0,
                            "OthChrg":0,
                            "TotItemVal": round(float(total_cost), 2)
                        }
                        s_no += 1
                        item_list.append(item_dict)
                    main_dict["ItemList"] = item_list
                    final_list.append(main_dict)
    return Response(data=final_list, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_govt_jst_bill_summary(request):
    print(request.data)
    selected_business_type_ids = request.data['selected_business_type_id']
    start_date = request.data['start_date']
    end_date = request.data['end_date']
    business_codes = list(Business.objects.filter(business_type_id__in=selected_business_type_ids).values_list('code', flat=True))

    business_wise_bill = BusinessWiseBillNumber.objects.filter(business__code__in=business_codes, from_date=start_date, to_date=end_date,product_group_type=2)
    business_wise_bill_list = list(business_wise_bill.values_list('business_id', 'bill_number'))
    business_wise_bill_columns = ['business_id', 'bill_number']
    business_wise_bill_df = pd.DataFrame(business_wise_bill_list, columns=business_wise_bill_columns)

    date_in_format = datetime.strptime(str(end_date), '%Y-%m-%d')
    date = datetime.strftime(date_in_format, '%d-%b-%Y')
    product_quantity_check_dict = serve_qty_and_short_name(start_date, end_date)
    sale_obj = Sale.objects.filter(sale_group__business__code__in=business_codes, sale_group__date__gte=start_date, sale_group__date__lte=end_date, product__group_id=2).exclude(product_id=28)
    sale_list = list(sale_obj.values_list('id', 'sale_group__business__user_profile_id','sale_group__business_id', 'sale_group__business__code', 'product_id', 'count', 'product__cgst_percent', 'product__sgst_percent', 'cost', 'product__hsn_code', 'sale_group__business__businessagentmap__agent__first_name', 'sale_group__business__businessagentmap__agent__agent_profile__gst_number'))
    sale_column = ['id', 'user_profile_id', 'business_id', 'business_code', 'product_id', 'count', 'cgst_percent', 'sgst_percent' ,'cost', 'hsn_code', 'agent_name', 'gst_number']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)

    sale_df = sale_df.groupby(['business_id', 'product_id']).agg({'count': sum, 'user_profile_id': 'first', 'business_code': 'first', 'cgst_percent': 'first', 'sgst_percent': 'first', 'cost': sum, 'hsn_code': 'first', 'agent_name': 'first', 'gst_number': 'first'}).reset_index()
    short_name_and_qty = product_quantity_check_dict['product_dict']

    if sale_df.empty:
        document = {}
        document['is_data_available'] = False
        return Response(data=document, status=status.HTTP_200_OK)
    sale_df['cost'] = sale_df['cost'].astype(float)
    sale_df['mrp'] = sale_df['cost'] / sale_df['count']
    sale_df['product_quantity'] = sale_df.apply(lambda x: short_name_and_qty[x['product_id']]['qty'], axis=1)
    sale_df['product_short_name'] = sale_df.apply(lambda x: short_name_and_qty[x['product_id']]['short_name'], axis=1)
    sale_df['cost_by_base_price'] = sale_df.apply(lambda x: find_base_price_from_total_cost(x['cost'], x['cgst_percent'] + x['sgst_percent']), axis=1)
    sale_df['cost_by_base_price'] = sale_df['cost_by_base_price'].astype(float)
    sale_df['base_price'] = sale_df['cost_by_base_price'] / sale_df['count']
    sale_df['product_quantity'] = sale_df['product_quantity'].astype(float)
    sale_df['total_gst_for_base_price'] = sale_df['cost'] - sale_df['cost_by_base_price']
    sale_df['qty_in_whole'] = (sale_df['count'] * sale_df['product_quantity']) / 1000
    sale_df['total_gst'] = sale_df['cgst_percent'] + sale_df['sgst_percent']
    sale_df['total_cost'] = (sale_df['cost_by_base_price'] + sale_df['total_gst_for_base_price'])

    sale_df = sale_df.merge(business_wise_bill_df, how="left", on="business_id")
    sale_df = sale_df[sale_df['bill_number'] != ""]
    # sale_df = sale_df.fillna("")
    # sheet 1
    grouped_sale_df = sale_df.groupby(['business_id', 'total_gst']).agg({'agent_name': 'first','gst_number': 'first','bill_number': 'first', 'total_cost': 'sum','cost_by_base_price': sum , 'total_gst_for_base_price': sum}).reset_index()
    grouped_sale_df['total_cost_rounded'] = grouped_sale_df['total_cost'].astype(float)
    grouped_sale_df['cgst_value'] = grouped_sale_df['total_gst_for_base_price'] / 2
    grouped_sale_df['sgst_value'] = grouped_sale_df['total_gst_for_base_price'] / 2
    grouped_sale_df['bill_date'] = date

    b2b_df = grouped_sale_df[pd.notnull(grouped_sale_df.gst_number)]
    # print('sheet111-----------',b2b_df.count())
    b2b_df = b2b_df.fillna("")
    b2cs_df = grouped_sale_df[pd.isnull(grouped_sale_df.gst_number)]
    # print('sheet222-----------',b2cs_df.count())
    b2cs_df = b2cs_df.fillna("")
    
    final_df = b2b_df.rename(columns = {'gst_number': 'GSTIN_UINOFRECIPIENT', 'agent_name': 'NAME', 'bill_number': 'INVOICENO', 'bill_date' : 'INVOICEDATE', 'total_cost_rounded': 'INVOICEVALUE', 'total_gst': 'RATE', 'cost_by_base_price': 'TAXABLEVALUE', 'cgst_value': 'CGST', 'sgst_value': 'SGST'})
    final_df['PLACEOFSUPPLY'] = ''
    final_df['REVERSECHARGE'] = ''
    final_df['INVOICETYPE'] = ''
    final_df['IGST'] = 0
    final_df = final_df[['GSTIN_UINOFRECIPIENT', 'NAME', 'INVOICENO', 'INVOICEDATE', 'INVOICEVALUE', 'PLACEOFSUPPLY', 'REVERSECHARGE', 'INVOICETYPE', 'RATE', 'TAXABLEVALUE', 'CGST', 'SGST', 'IGST']]
    
    final_df2 = b2cs_df.rename(columns = {'gst_number': 'GSTIN_UINOFRECIPIENT', 'agent_name': 'NAME', 'bill_number': 'INVOICENO', 'bill_date' : 'INVOICEDATE', 'total_cost_rounded': 'INVOICEVALUE', 'total_gst': 'RATE', 'cost_by_base_price': 'TAXABLEVALUE', 'cgst_value': 'CGST', 'sgst_value': 'SGST'})
    final_df2['PLACEOFSUPPLY'] = ''
    final_df2['REVERSECHARGE'] = ''
    final_df2['INVOICETYPE'] = ''
    final_df2['IGST'] = 0
    final_df2 = final_df2[['GSTIN_UINOFRECIPIENT', 'NAME', 'INVOICENO', 'INVOICEDATE', 'INVOICEVALUE', 'PLACEOFSUPPLY', 'REVERSECHARGE', 'INVOICETYPE', 'RATE', 'TAXABLEVALUE', 'CGST', 'SGST', 'IGST']]
    
    # sheet 2
    # product_wise_df = sale_df
    # product_wise_df['bill_date'] = date
    # product_wise_df['cgst_value'] = product_wise_df['total_gst_for_base_price'] / 2
    # product_wise_df['sgst_value'] = product_wise_df['total_gst_for_base_price'] / 2
    # product_wise_df['ISGT'] = 0.000
    # product_wise_df = product_wise_df.rename(columns={'agent_name': 'AGENT', 'gst_number': 'BTAXNO', 'product_short_name': 'PRODUCT', 'bill_number': 'INVNO', 'bill_date': 'INVDATE', 'sgst_value': 'SGST','cgst_value': 'CGST', 'total_cost': 'NETAMOUNT', 'hsn_code': 'HSNCODE', 'total_gst': 'GST', 'mrp': 'RATE'})
    # final_df_2 = product_wise_df[['AGENT', 'BTAXNO', 'PRODUCT', 'INVNO', 'INVDATE', 'RATE', 'GST', 'SGST', 'CGST', 'ISGT','NETAMOUNT', 'HSNCODE']]

    file_name = f"static/media/monthly_report/{start_date} - {end_date} - GVT Fermented GST Bill Summary.xlsx"
    writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
    sheet_name1 = "B2B"
    sheet_name2 = "B2CS"
    final_df.to_excel(writer, sheet_name=sheet_name1, index=False)
    final_df2.to_excel(writer, sheet_name=sheet_name2, index=False)
    writer.save()
    document = {}
    document['is_data_available'] = True
    document['file_name'] = f"{start_date} - {end_date} - GVT Fermented GST Bill Summary.xlsx"
    try:
        image_path = file_name
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)
        document = {}
    return Response(data=document, status=status.HTTP_200_OK)
    
    