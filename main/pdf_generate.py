from django.shortcuts import render
# authendication
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
# from datetime import datetime
import datetime
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
from calendar import monthrange, month_name
import pytz
indian = pytz.timezone('Asia/Kolkata')

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
from num2words import num2words

auth_id = "MAZJZINTYZZTQ4MTG0MT"
auth_token = "NWJkN2Q5MGM2OGI2Njc1MGM3NzMzMmMyZjQyYWIw"


def drawMyRulerForCanvas(pdf):
    pdf.drawString(100,810, 'x100')
    pdf.drawString(200,810, 'x200')
    pdf.drawString(300,810, 'x300')
    pdf.drawString(400,810, 'x400')
    pdf.drawString(500,810, 'x500')

    pdf.drawString(10,100, 'y100')
    pdf.drawString(10,200, 'y200')
    pdf.drawString(10,300, 'y300')
    pdf.drawString(10,400, 'y400')
    pdf.drawString(10,500, 'y500')
    pdf.drawString(10,600, 'y600')
    pdf.drawString(10,700, 'y700')
    pdf.drawString(10,800, 'y800')


def findout_tray_count(count, product_defalut_count, product_id):
    loose_milk_ids = [22, 23, 24]
    if not product_defalut_count == 0:
        remainder_of_tray_count = count % product_defalut_count
        coefieient_of_tray_count = count // product_defalut_count
    else:
        remainder_of_tray_count = 0
        coefieient_of_tray_count = 0
    if not remainder_of_tray_count == 0:
        if not product_id in loose_milk_ids:
            if remainder_of_tray_count > (product_defalut_count / 2):
                return coefieient_of_tray_count + 1
            else:
                return coefieient_of_tray_count
        else:
            if remainder_of_tray_count > 0:
                return coefieient_of_tray_count + 1
            else:
                return coefieient_of_tray_count
    else:
        return coefieient_of_tray_count


def findout_packet_count(count, product_defalut_count, product_id):
    loose_milk_ids = [22, 23, 24]
    if not product_id in loose_milk_ids:
        if not product_defalut_count == 0:
            remainder_of_tray_count = count % product_defalut_count
        else:
            remainder_of_tray_count = 0
        if not remainder_of_tray_count == 0:
            if remainder_of_tray_count <= (product_defalut_count / 2):
                return remainder_of_tray_count
            else:
                return 0
        else:
            return remainder_of_tray_count
    else:
        return 0


def findout_packet_count_in_negative(count, product_defalut_count, tray_count, product_id):
    loose_milk_ids = [22, 23, 24]
    if not tray_count == 0:
        if not product_defalut_count == 0:
            remainder_of_tray_count = count % product_defalut_count
            # coefieient_of_tray_count = count // product_defalut_count
        else:
            remainder_of_tray_count = 0
            # coefieient_of_tray_count = 0
        if not product_id in loose_milk_ids:
            if remainder_of_tray_count > (product_defalut_count / 2):
                return product_defalut_count - remainder_of_tray_count
            else:
                return 0
        else:
            if not remainder_of_tray_count == 0:
                return product_defalut_count - remainder_of_tray_count
            else:
                return 0
    else:
        return 0


def find_leak_packet_percentage(product_id, leak_percentage, count):
    milk_product_ids = list(Product.objects.filter(group_id__in=[1, 3], is_active=True).values_list('id', flat=True))
    if product_id in milk_product_ids:
        return leak_percentage * count
    else:
        return 0


# If any changes in this function need to change to temp_pdf_generate.py file also
def gatepass_data(route_id, date, session_id):
    route_id = route_id
    # date = datetime.datetime.strptime(request.data['date'], '%m/%d/%Y')
    date = date
    session_id = session_id
    data = {
        'route_supervisor': '',
        'route_name': '',
        'date': '',
        'vehicle_number': '',
        'session': '',
        'sales': {},
        'milk': {},
        'fermented': {},
        'other': {}
    }
    # get vehicle details
    data['vehicle_number'] = RouteVehicleMap.objects.get(route_id=route_id).vehicle.licence_number
    data['route_supervisor'] = RouteVehicleMap.objects.get(route_id=route_id).vehicle.driver_name
    data['date'] = date
    data['session'] = Session.objects.get(id=session_id).display_name

    route = Route.objects.get(id=route_id)
    leak_percentage = route.leak_packet_in_percentage
    data['route_name'] = route.name
    business_ids = RouteBusinessMap.objects.filter(route=route).values_list('business', flat=True)
    sale_group = SaleGroup.objects.filter(business_id__in=business_ids, date=date, session_id=session_id)
    sale_values = Sale.objects.filter(sale_group__in=sale_group, product__is_active=True).values_list('product_id',
                                                                                                      'count')
    sale_columns = ['product_id', 'count']
    sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)

    icustomer_sale_group = ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date.month,
                                                             date__year=date.year, session_id=session_id)
    icustomer_sale_values = ICustomerSale.objects.filter(icustomer_sale_group__in=icustomer_sale_group).values_list(
        'product_id', 'count')
    icustomer_sale_columns = ['product_id', 'count']
    icustomer_sale_df = pd.DataFrame(list(icustomer_sale_values), columns=icustomer_sale_columns)

    combined_df = sale_df.append(icustomer_sale_df)

    product_values = Product.objects.filter(is_active=True).order_by('display_ordinal').values_list('id', 'short_name',
                                                                                                    'unit', 'quantity')
    product_columns = ['id', 'product_short_name', 'unit', 'quantity']
    product_df = pd.DataFrame(list(product_values), columns=product_columns)

    if not combined_df.empty:
        total_sale_df = combined_df.groupby(['product_id'])['count'].sum().reset_index()
        # data['sales'] = dict(zip(total_sale_df['product_id'], total_sale_df['count']))
        merged_df = pd.merge(total_sale_df, product_df, how='left', left_on='product_id', right_on='id')

        # find litre
        data['sales'] = merged_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
        # milk_product_ids = [1, 2, 3, 4, 6, 22, 23, 24]
        # curd_product_ids = [7, 10, 21, 25]
        milk_product_ids = list(
            Product.objects.filter(group_id__in=[1, 3], is_active=True).values_list('id', flat=True))
        curd_product_ids = list(Product.objects.filter(group_id__in=[2], is_active=True).values_list('id', flat=True))
        # find milk total and net total
        data['milk_total_count'] = merged_df[merged_df['id'].isin(milk_product_ids)]['count'].sum()
        data['net_total_count'] = merged_df['count'].sum()
       # find tray count and pocket count
        tray_config_values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id', 'tray_count', 'product_count')
        print('tray_config_values',tray_config_values)
        tray_config_columns = ['product_id', 'p_c_tray_count', 'p_c_product_count']
        tray_config_df = pd.DataFrame(list(tray_config_values), columns=tray_config_columns)
        tray_config_merge_df = pd.merge(merged_df, tray_config_df, how='left', left_on='id', right_on='product_id')

        # finding the tray count based on the defalut product tray count
        tray_config_merge_df['calculated_tray_count'] = tray_config_merge_df.apply(
            lambda x: findout_tray_count(x['count'], x['p_c_product_count'], x['id']), axis=1)
        tray_config_merge_df['calculated_pocket_count'] = tray_config_merge_df.apply(
            lambda x: findout_packet_count(x['count'], x['p_c_product_count'], x['id']), axis=1)
        tray_config_merge_df['calculated_pocket_count_in_negative'] = tray_config_merge_df.apply(
            lambda x: findout_packet_count_in_negative(x['count'], x['p_c_product_count'], x['calculated_tray_count'],
                                                       x['id']), axis=1)
        tray_config_merge_df = tray_config_merge_df.fillna(0)

        # choose coloumn
        tray_config_merge_df = tray_config_merge_df[
            ['id', 'count', 'quantity', 'calculated_tray_count', 'calculated_pocket_count', 'product_short_name',
             'calculated_pocket_count_in_negative']]
        # tray_config_merge_df['leak_packet'] = ((float(leak_percentage) / 100) * tray_config_merge_df['count'])
        tray_config_merge_df['count'] = tray_config_merge_df['count'].astype(int)
        tray_config_merge_df['leak_packet'] = tray_config_merge_df.apply(
            lambda x: find_leak_packet_percentage(x['id'], leak_percentage, x['count']), axis=1)

        # Check 80 pockets for routes
        allowance_business_ids = list(
            BusinessWiseLeakageAllowanceAsPacket.objects.filter(session_id=route.session_id, product__is_active=True).values_list('business_id', flat=True))
        if RouteBusinessMap.objects.filter(route_id=route.id, business_id__in=allowance_business_ids).exists():
            route_business_ids = list(
                RouteBusinessMap.objects.filter(route_id=route.id).values_list('business_id', flat=True))
            allowance_business_obj = BusinessWiseLeakageAllowanceAsPacket.objects.filter(product__is_active=True,
                business_id__in=route_business_ids)
            for allowance_business in allowance_business_obj:
                if not len(tray_config_merge_df[tray_config_merge_df['id'] == allowance_business.product.id]) == 0:
                    tray_config_merge_df.loc[
                        tray_config_merge_df['id'] == allowance_business.product.id, 'leak_packet'] = \
                        tray_config_merge_df['leak_packet'] + allowance_business.packet_count
                else:
                    new_list = [allowance_business.product.id, '0', allowance_business.product.quantity, '0', '0',
                                allowance_business.product.short_name, '0', allowance_business.packet_count]
                    to_index = len(tray_config_merge_df)
                    tray_config_merge_df.loc[to_index] = new_list

        tray_config_merge_df['leak_packet'] = tray_config_merge_df['leak_packet'].astype(int)
        tray_config_merge_df['litre'] = (tray_config_merge_df['quantity'] / 1000) * (
                tray_config_merge_df['count'] + tray_config_merge_df['leak_packet'])
        tray_config_merge_df['calculated_tray_count'] = tray_config_merge_df['calculated_tray_count'].astype(int)
        tray_config_merge_df['calculated_pocket_count'] = tray_config_merge_df['calculated_pocket_count'].astype(int)
        tray_config_merge_df['calculated_pocket_count_in_negative'] = tray_config_merge_df[
            'calculated_pocket_count_in_negative'].astype(int)
        tray_config_merge_df['leak_packet'] = tray_config_merge_df['leak_packet'].astype(int)

        # make total count
        data['total_product_count'] = tray_config_merge_df['count'].sum()
        data['total_tray_count'] = tray_config_merge_df['calculated_tray_count'].sum()
        data['total_packet_count'] = tray_config_merge_df['calculated_pocket_count'].sum()
        data['total_packet_count_in_negative'] = tray_config_merge_df['calculated_pocket_count_in_negative'].sum()
        data['total_leak_packet_count'] = tray_config_merge_df['leak_packet'].sum()
        data['total_litre_count'] = tray_config_merge_df['litre'].sum()
        data['sales'] = tray_config_merge_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()

        # milk product details
        milk_df = tray_config_merge_df[tray_config_merge_df['id'].isin(milk_product_ids)]
        data['milk'] = milk_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
        data['total_milk_product_count'] = milk_df['count'].sum()
        df_without_losse_milk = milk_df[(milk_df['id'] != 22) & ( milk_df['id'] != 23) & ( milk_df['id'] != 24)]
        data['total_milk_tray_count'] = df_without_losse_milk['calculated_tray_count'].sum()
        data['total_milk_packet_count'] = milk_df['calculated_pocket_count'].sum()
        data['total_milk_packet_count_in_negative'] = milk_df['calculated_pocket_count_in_negative'].sum()
        data['total_milk_leak_packet_count'] = milk_df['leak_packet'].sum()
        data['total_milk_litre_count'] = milk_df['litre'].sum()

        # curd product details
        curd_df = tray_config_merge_df[tray_config_merge_df['id'].isin(curd_product_ids)]
        data['curd'] = curd_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
        data['total_curd_product_count'] = curd_df['count'].sum()
        df_without_cup_curd = curd_df[(curd_df['id'] != 10) & (curd_df['id'] != 26) & (curd_df['id'] != 28)]
        data['total_curd_tray_count'] = df_without_cup_curd['calculated_tray_count'].sum()
        data['total_curd_packet_count'] = curd_df['calculated_pocket_count'].sum()
        data['total_curd_packet_count_in_negative'] = curd_df['calculated_pocket_count_in_negative'].sum()
        data['total_curd_leak_packet_count'] = curd_df['leak_packet'].sum()
        data['total_curd_litre_count'] = curd_df['litre'].sum()

        other_df = tray_config_merge_df[~tray_config_merge_df['id'].isin(milk_product_ids)]
        other_df = other_df.fillna(0)
        data['other'] = other_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    pdf = generate_pdf(data, route_id, session_id, date)
    data_dict = {
        'pdf_data': pdf,
        'data': data
    }
    return data_dict


def generate_pdf(data, route_id, session_id, date):
    prod_ids = data['milk'].keys()

    if 'curd' in data:
        curd_ids = data['curd'].keys()
    else:
        curd_ids = []

    new_date = datetime.datetime.strftime(date, '%d-%b-%Y')
    directory = 'new'
    session = 'Morning'
    if session_id == 2:
        session = 'Evening'

    file_name = str(date) + '_' + str(route_id) + '_' + str(session) + '.pdf'

    try:
        path = os.path.join('static/media/indent_document/', str(date), session, str(route_id))
        os.makedirs(path)
    except FileExistsError:
        print('already created')
    file_path = os.path.join(
        'static/media/indent_document/' + str(date) + '/' + session + '/' + str(route_id) + '/',
        file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    #     #     -------------------------first page -------------------
    y_axis = 0
    y_for_table2 = 0
    new_y_axis = 0
    loose_milk_ids = [22, 23, 24]
    last_count_for_gate_pass = IndentCodeBank.objects.get(code_for='gate_pass')
    serial_number = int(last_count_for_gate_pass.last_code) + 1
    if serial_number == 999999:
        last_count_for_gate_pass.last_code = 0
    else:
        last_count_for_gate_pass.last_code = serial_number
    last_count_for_gate_pass.save()
    for i in range(2):
        mycanvas.setDash(12)
        net_total_count = 0
        net_total_tray_count = 0
        net_total_packet_positive_count = 0
        net_total_packet_negative_count = 0
        net_total_packet_negative_count = 0
        net_total_leak_packet_count = 0
        route_supervisor = data['route_supervisor']
        route_date = datetime.datetime.strftime(data['date'], '%d-%m-%Y')
        session_name = data['session']
        route_name = data['route_name']
        vehicle_number = data['vehicle_number']
        mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 810 - y_for_table2,
                                   'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 790 - y_for_table2, 'DAIRY GATEPASS FOR MILK')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.line(200, 785 - y_for_table2, 400, 785 - y_for_table2)

        # row 1
        mycanvas.setStrokeColor(colors.black)
        mycanvas.drawString(20, 765 - y_for_table2, 'S.No' + ' ' + ':' + ' ' + str(serial_number).zfill(5))
        mycanvas.line(95, 762 - y_for_table2, 95, 778 - y_for_table2)
        mycanvas.drawString(105, 765 - y_for_table2,
                            'Date ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name))
        mycanvas.line(253, 762 - y_for_table2, 253, 778 - y_for_table2)
        mycanvas.drawString(263, 765 - y_for_table2, 'Route ' + ' ' + ':' + ' ' + str(route_name))
        mycanvas.line(423, 762 - y_for_table2, 423, 778 - y_for_table2)
        mycanvas.drawString(433, 765 - y_for_table2, 'Vehicle ' + ' ' + ':' + ' ' + str(vehicle_number))
        mycanvas.setStrokeColor(colors.lightgrey)
       
        # ------------table header----------
        mycanvas.line(20, 745 - y_for_table2, 570, 745 - y_for_table2)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.line(20, 720 - y_for_table2, 570, 720 - y_for_table2)

        # ----------table heading-----------
        # sl.no
        mycanvas.drawString(25, 728 - y_for_table2, 'S.No')
        # item particulars
        mycanvas.drawString(80, 728 - y_for_table2, 'Products')
        mycanvas.drawString(180, 728 - y_for_table2, 'Packet')
        # no of trays, pkt
        mycanvas.drawString(240, 728 - y_for_table2, 'Tray / Can')
        mycanvas.drawString(310, 728 - y_for_table2, 'Pkt (+)')
        mycanvas.drawString(360, 728 - y_for_table2, 'Pkt (-)')
       
       
        # Leak Pkt
        mycanvas.drawString(415, 728 - y_for_table2, 'Leak')

        # Quantity of milk
        mycanvas.drawString(500, 728 - y_for_table2, 'Qty (Ltr)')

        # horizontal lines
        y_axis = 700 - y_for_table2
        end_axis = 683 - y_for_table2
        last_index = 0
        mycanvas.setFont('Helvetica', 12)
        for index, prod_id in enumerate(prod_ids, start=1):
            # sl.no
            mycanvas.drawString(30, y_axis, str(index))
            # item particulars data
            mycanvas.drawString(70, y_axis, str(data['milk'][prod_id]['product_short_name']))
            if not prod_id in loose_milk_ids:
                mycanvas.drawRightString(210, y_axis, str(data['milk'][prod_id]['count']))
            else:
                mycanvas.drawRightString(210, y_axis, str(str(data['milk'][prod_id]['count']) + 'L'))
            # tray data
            if not data['milk'][prod_id]['calculated_tray_count'] == 0:
                mycanvas.drawRightString(280, y_axis, str(data['milk'][prod_id]['calculated_tray_count']))
            # pkt
            if not data['milk'][prod_id]['calculated_pocket_count'] == 0:
                mycanvas.drawRightString(335, y_axis, str(data['milk'][prod_id]['calculated_pocket_count']))
            if not data['milk'][prod_id]['calculated_pocket_count_in_negative'] == 0:
                if not prod_id in loose_milk_ids:
                    mycanvas.drawRightString(380, y_axis, str(-data['milk'][prod_id]['calculated_pocket_count_in_negative']))
                else:
                    mycanvas.drawRightString(380, y_axis, str(-data['milk'][prod_id]['calculated_pocket_count_in_negative']) + 'L')
            # leak pkt
            if not data['milk'][prod_id]['leak_packet'] == 0:
                mycanvas.drawRightString(435, y_axis, str(data['milk'][prod_id]['leak_packet']))
               
            # qty of milk
            mycanvas.drawRightString(550, y_axis, str(data['milk'][prod_id]['litre']))
            last_index = index

            y_axis -= 15
            end_axis -= 15

        # After Milk entry line
        mycanvas.line(20, int(y_axis + 10), 570, int(y_axis + 10))
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(70, y_axis - 3, 'Milk Total')

        # mycanvas.setFont('Helvetica', 12)
        mycanvas.drawRightString(210, y_axis - 3, str(int(data['milk_total_count'])))
        if not data['total_milk_tray_count'] == 0:
            mycanvas.drawRightString(280, y_axis - 3, str(data['total_milk_tray_count']))
        if not data['total_milk_packet_count'] == 0:
            mycanvas.drawRightString(335, y_axis - 3, str(data['total_milk_packet_count']))
        if not data['total_milk_packet_count_in_negative'] == 0:
            mycanvas.drawRightString(380, y_axis - 3, str(-data['total_milk_packet_count_in_negative']))
        if not data['total_milk_leak_packet_count'] == 0:
            mycanvas.drawRightString(435, y_axis - 3, str(data['total_milk_leak_packet_count']))
        mycanvas.drawRightString(550, y_axis - 3, str(data['total_milk_litre_count']))

        # After Milk total line
        mycanvas.line(20, int(y_axis - 10), 570, int(y_axis - 10))

        y_axis -= 15
        mycanvas.setFont('Helvetica', 12)
        if data['total_curd_product_count'] != 0:
            for c_index, curd_id in enumerate(curd_ids, start=last_index):
                mycanvas.drawString(30, y_axis - 10, str(c_index + 1))
                mycanvas.drawString(70, y_axis - 10, str(data['curd'][curd_id]['product_short_name']))
                mycanvas.drawRightString(210, y_axis - 10, str(data['curd'][curd_id]['count']))
                if not data['curd'][curd_id]['calculated_tray_count'] == 0:
                    mycanvas.drawRightString(280, y_axis - 10, str(data['curd'][curd_id]['calculated_tray_count']))
                if not data['curd'][curd_id]['calculated_pocket_count'] == 0:
                    mycanvas.drawRightString(335, y_axis - 10, str(data['curd'][curd_id]['calculated_pocket_count']))
                if not data['curd'][curd_id]['calculated_pocket_count_in_negative'] == 0:
                    mycanvas.drawRightString(380, y_axis - 10,
                                        str(-data['curd'][curd_id]['calculated_pocket_count_in_negative']))
                if not data['curd'][curd_id]['leak_packet'] == 0:
                    mycanvas.drawRightString(435, y_axis - 10, str(data['curd'][curd_id]['leak_packet']))

                mycanvas.drawRightString(550, y_axis - 10, str(data['curd'][curd_id]['litre']))
                y_axis -= 15
                end_axis -= 15

            mycanvas.setFont('Helvetica', 12)
            # Above Curd total
            mycanvas.line(20, int(y_axis), 570, int(y_axis))
            #     y_axis -= 20
            #     end_axis -= 15
            mycanvas.drawString(70, int(y_axis) - 15, str('Curd Total'))
            mycanvas.drawRightString(210, int(y_axis) - 15, str(data['total_curd_product_count']))
            if not data['total_curd_tray_count'] == 0:
                mycanvas.drawRightString(280, int(y_axis) - 15, str(data['total_curd_tray_count']))
            if not data['total_curd_packet_count'] == 0:
                mycanvas.drawRightString(335, int(y_axis) - 15, str(data['total_curd_packet_count']))
            if not data['total_curd_packet_count_in_negative'] == 0:
                mycanvas.drawRightString(380, y_axis - 15, str(-data['total_curd_packet_count_in_negative']))
            if not data['total_curd_leak_packet_count'] == 0:
                mycanvas.drawRightString(435, int(y_axis) - 15, str(data['total_curd_leak_packet_count']))

            mycanvas.drawRightString(550, int(y_axis) - 15, str(data['total_curd_litre_count']))

            end_axis = end_axis - 30
            # --------lines--------
            # end line
            mycanvas.line(20, int(end_axis + 13), 570, int(end_axis + 13))

        # Net total
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(70, int(end_axis-5), str('Net Total'))
        net_total_count = data['milk_total_count'] + data['total_curd_product_count']
        mycanvas.drawRightString(210, int(end_axis - 5), str(int(net_total_count)))
        net_total_tray_count = data['total_milk_tray_count'] + data['total_curd_tray_count']
        mycanvas.drawRightString(280, int(end_axis - 5), str(net_total_tray_count))
        net_total_packet_positive_count = data['total_milk_packet_count'] + data['total_curd_packet_count']
        mycanvas.drawRightString(335, int(end_axis - 5), str(net_total_packet_positive_count))
        net_total_packet_negative_count = data['total_milk_packet_count_in_negative'] + data[
            'total_curd_packet_count_in_negative']
        mycanvas.drawRightString(380, int(end_axis - 5), str(-net_total_packet_negative_count))
        net_total_leak_packet_count = data['total_milk_leak_packet_count'] + data['total_curd_leak_packet_count']
        if not net_total_leak_packet_count == 0:
            mycanvas.drawRightString(435, int(end_axis - 5), str(net_total_leak_packet_count))
        net_total_litre = data['total_milk_litre_count'] + data['total_curd_litre_count']
        mycanvas.drawRightString(550, int(end_axis - 5), str(net_total_litre))

        mycanvas.line(20, int(end_axis - 8), 570, int(end_axis - 8))

        # right and left border
        mycanvas.line(20, 745 - y_for_table2, 20, int(end_axis - 8))
        mycanvas.line(570, 745 - y_for_table2, 570, int(end_axis - 8))
        # data borders
        mycanvas.line(60, 745 - y_for_table2, 60, int(end_axis - 8))
        mycanvas.line(160, 745 - y_for_table2, 160, int(end_axis - 8))
        mycanvas.line(230, 745 - y_for_table2, 230, int(end_axis - 8))
        mycanvas.line(300, 745 - y_for_table2, 300, int(end_axis - 8))
        mycanvas.line(350, 745 - y_for_table2, 350, int(end_axis - 8))
        mycanvas.line(400, 745 - y_for_table2, 400, int(end_axis - 8))
        mycanvas.line(450, 745 - y_for_table2, 450, int(end_axis - 8))

        mycanvas.setFont('Helvetica', 12)
        y_axis = y_axis - 40
        mycanvas.drawString(20, int(end_axis - 40), str('Dist.Assistant/M.M.O.'))
        mycanvas.drawString(230, int(end_axis - 40), str('Counting Officer'))
        mycanvas.drawString(470, int(end_axis - 40), str('Route Supervisor'))
        # if i == 0:
        #     mycanvas.setDash(6,6)
        #     mycanvas.line(10, end_axis - 110, 580, int(end_axis - 110))
        y_for_table2 = end_axis - 120
       
       
     #    -------------------------second page -------------------
    route_wise_data = route_wise_business_data(route_id, session_id, date)
    mycanvas.showPage()
    #     mycanvas.setLineWidth(0)
    mycanvas.setStrokeColor(colors.lightgrey)
    # HEADER
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(20, 810, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 795, 'ROUTEWISE MILK DISTRIBUTION STATEMENT')
    mycanvas.line(170, 792, 410, 792)
    # basic head
    # row 1
    #     get the last count number
    last_count_for_route_wise_business = IndentCodeBank.objects.get(code_for='route_wise_business')
    indent_number = int(last_count_for_route_wise_business.last_code) + 1
    if indent_number == 999999:
        last_count_for_route_wise_business.last_code = 0
    else:
        last_count_for_route_wise_business.last_code = indent_number
    last_count_for_route_wise_business.save()
    page_number = 1
    route_name = route_wise_data['route_name']
    vehicle_number = route_wise_data['vehicle_number']
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(290, 775, 'No.' + ' ' + ':' + ' ' + str(indent_number).zfill(5) +"  |  "+'Route ' + ' ' + ':' + ' ' + str(route_name) + "  |  " + 'Vehicle ' + ' ' + ':' + ' ' + str(vehicle_number) +"  |  "+'Date ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name))

    x_ad = 4
    # # ----------table heading-----------
    mycanvas.setFont('Helvetica', 9)
    mycanvas.drawString(10-x_ad, 665+85, 'S.No')
    mycanvas.drawString(35-x_ad, 665+85, 'Type')
    mycanvas.drawString(70-x_ad, 665+85, 'Booth')
    mycanvas.drawString(105-x_ad, 665+85,'Agent')
    # product name on heading
    product_x_axis = 133
    line_product_x_axis = 144
    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
    for product in products:
        # product short name
        if product.short_name == 'CBUK' or product.short_name == 'FMcan' or product.short_name == 'SMcan':
            mycanvas.drawString(product_x_axis-x_ad, 665+85, str(product.short_name[:6]))
        else:
            mycanvas.drawString(product_x_axis+9-x_ad, 670+85, str(product.short_name[:-4]))
            mycanvas.drawString(product_x_axis+9-x_ad, 660+85, str(product.short_name[-4:]))

             
        product_x_axis += 36
        line_product_x_axis += 38

    # ------------table header----------
    # table head up line
    mycanvas.line(10-x_ad, 680+85, product_x_axis -6, 680+85)
    # table head bottom line
    mycanvas.line(10-x_ad, 655+85, product_x_axis - 6, 655+85)

    y_data = 640+85
    #     value_axis = 30
    line_product_x_axis = 165
    serial_number = 0
    serial_number_duplicate = 1
    page_number = 1
    booth_types = route_wise_data['booth_types'].keys()
   
    for booth_type_index, booth_type in enumerate(booth_types, start=1):
        for booth_index, business in enumerate(route_wise_data['booth_types'][booth_type]['booth_ids'], start=1):
            value_axis = 162
            mycanvas.setFont('Helvetica', 10)
            mycanvas.drawString(12-x_ad, y_data, str(serial_number+1))
           
            mycanvas.setFont('Helvetica', 10)

            booth = BusinessType.objects.get(id=booth_type).name
            booth_srt = ''
            if booth == 'Booth' or booth == 'Private Parlour':
                booth_srt = 'BO'
            elif booth == 'Parlour' or booth == "Own parlour":
                booth_srt = "UNI"
            elif booth == 'Private Institute':
                booth_srt = "PVT"
            elif booth == 'Govt Institute':
                booth_srt = "GVT"
            elif booth == "Other unions":
                booth_srt = "O-UNI"
            elif booth == "Other State":
                booth_srt = "O-ST"
            mycanvas.setFont('Helvetica', 9)
            mycanvas.drawCentredString(47-x_ad, y_data, str(booth_srt))
            mycanvas.setFont('Helvetica', 10)
            mycanvas.drawString(68-x_ad, y_data,
                                str(route_wise_data['booth_types'][booth_type][business]['business_code']))
            mycanvas.setFont('Helvetica', 10)
            mycanvas.drawString(100-x_ad , y_data,
                                str(route_wise_data['booth_types'][booth_type][business]['agent_name'][:5]).title())
           
            mycanvas.setFont('Helvetica', 10)

            for product in products:
                if product.id in route_wise_data['booth_types'][booth_type][business]['product']:
                    mycanvas.drawRightString(value_axis-x_ad, y_data, str(
                        int(route_wise_data['booth_types'][booth_type][business]['product'][product.id])))
                value_axis = value_axis + 36
            if route_wise_data['total_booth'] >= 24:
                y_data -= 28
            else:
                y_data -= 23
            value_axis = 160
            mycanvas.line(line_product_x_axis-x_ad, 300, line_product_x_axis-x_ad, 300)
            line_product_x_axis += 35

            if serial_number_duplicate % 24 == 0:
                if route_wise_data['total_booth'] >= 24:
                    page_number += 1
                    mycanvas.line(5, 680+85, 5, y_data)
                    mycanvas.line(29, 680+85, 29, y_data)
                    mycanvas.line(59, 680+85, 59, y_data)
                    mycanvas.line(93, 680+85, 93, y_data)
                    x_data = 132

                    for product in products:
                        # line after short name of the product
                        mycanvas.line(x_data-x_ad, 680+85, x_data, y_data)
                        x_data += 36

                    # line after 1st page
                    mycanvas.line(5, y_data, x_data, y_data)

                    # neext
                    mycanvas.showPage()
                    mycanvas.setStrokeColor(colors.lightgrey)

                    # HEADER
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawString(20, 810, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(300, 795, 'ROUTEWISE MILK DISTRIBUTION STATEMENT')
                    mycanvas.line(170, 792, 410, 792)
                    # basic head
                    # row 1
                    page_number = page_number
                    route_name = route_wise_data['route_name']
                    vehicle_number = route_wise_data['vehicle_number']

                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(290, 775, 'No.' + ' ' + ':' + ' ' + str(indent_number).zfill(5) +"  |  "+'Route ' + ' ' + ':' + ' ' + str(route_name) + "  |  " + 'Vehicle ' + ' ' + ':' + ' ' + str(vehicle_number) +"  |  "+'Date ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name))

                    x_ad = 4
                    # # ----------table heading-----------
                    mycanvas.setFont('Helvetica', 9)
                    mycanvas.drawString(10-x_ad, 665+85, 'S.No')
                    mycanvas.drawString(35-x_ad, 665+85, 'Type')
                    mycanvas.drawString(70-x_ad, 665+85, 'Booth')
                    mycanvas.drawString(105-x_ad, 665+85,'Agent')
                    # product name on heading
                    product_x_axis = 133
                    line_product_x_axis = 144
                    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
                    for product in products:
                        # product short name
                        if product.short_name == 'CBUK' or product.short_name == 'FMcan' or product.short_name == 'SMcan':
                            mycanvas.drawString(product_x_axis-x_ad, 665+85, str(product.short_name[:6]))
                        else:
                            mycanvas.drawString(product_x_axis+9-x_ad, 670+85, str(product.short_name[:-4]))
                            mycanvas.drawString(product_x_axis+9-x_ad, 660+85, str(product.short_name[-4:]))

                        product_x_axis += 36
                        line_product_x_axis += 38

                    # ------------table header----------
                    # table head up line
                    mycanvas.line(10-x_ad, 680+85, product_x_axis -6, 680+85)
                    # table head bottom line
                    mycanvas.line(10-x_ad, 655+85, product_x_axis - 6, 655+85)
                    #  next
                    y_data = 645 + 60
                    value_axis = 162
    #                 line_product_x_axis = 165

            serial_number += 1
            serial_number_duplicate += 1

    # bottom border
    y_data -= 25
    mycanvas.line(10-x_ad, y_data, product_x_axis - 6, y_data)
    mycanvas.line(10-x_ad, y_data + 25, product_x_axis - 6, y_data + 25)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(10, y_data + 11, str('Grand Total'))
    mycanvas.setFont('Helvetica', 10)
    value_axis = 162
   
    for product in products:
        if not route_wise_data['total'][product.id] == 0:
            mycanvas.drawRightString(value_axis-x_ad, y_data + 11, str(int(route_wise_data['total'][product.id])))
        value_axis = value_axis + 36

    #     Total tray
    y_data = y_data - 25
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(10, y_data + 11, str('Total Tray'))
    mycanvas.setFont('Helvetica', 10)
    value_axis = 162
    total_tray = 0
    for product in products:
        if product.id in data['sales']:
            if not data['sales'][product.id]['calculated_tray_count'] == 0:
                mycanvas.drawRightString(value_axis-x_ad, y_data + 11,
                                         str(int(data['sales'][product.id]['calculated_tray_count'])))
                if product.id != 10 or product.id != 26 or product.id != 28:
                    total_tray += data['sales'][product.id]['calculated_tray_count']
        value_axis = value_axis + 36
    mycanvas.line(9-x_ad, y_data, product_x_axis - 6, y_data)

    #   Extra packet
    y_data = y_data - 25
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(10, y_data + 11, str('Loose Packets'))
    mycanvas.setFont('Helvetica', 10)
    value_axis = 162
    total_packet = 0
    for product in products:
        if product.id in data['sales']:
            if not data['sales'][product.id]['calculated_pocket_count'] == 0:
                mycanvas.drawRightString(value_axis-x_ad, y_data + 11,
                                         str(int(data['sales'][product.id]['calculated_pocket_count'])))
                total_packet += data['sales'][product.id]['calculated_pocket_count']
            if not data['sales'][product.id]['calculated_pocket_count_in_negative'] == 0:
                mycanvas.drawRightString(value_axis-x_ad, y_data + 11,
                                         str(-data['sales'][product.id]['calculated_pocket_count_in_negative']))
        value_axis = value_axis + 36
    mycanvas.line(9-x_ad, y_data, product_x_axis - 6, y_data)

    #   leakage packet
    y_data = y_data - 25
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(10, y_data + 11, str('Leak Packets'))
    mycanvas.setFont('Helvetica', 10)
    value_axis = 162
    for product in products:
        if product.id in data['sales']:
            if not data['sales'][product.id]['leak_packet'] == 0:
                mycanvas.drawRightString(value_axis-x_ad, y_data + 11,
                                         str(int(data['sales'][product.id]['leak_packet'])))
        value_axis = value_axis + 36
    mycanvas.line(9-x_ad, y_data, product_x_axis - 6, y_data)

# lines after products
    x_axis_data = 166
    for product in products:
        mycanvas.line(x_axis_data-x_ad, 680+85, x_axis_data-x_ad, y_data)
        if product == products[0]:
            mycanvas.line(x_axis_data-33-x_ad, 680+85, x_axis_data-33-x_ad, y_data)  
        x_axis_data += 36
    mycanvas.line(5, 680+85, 5, y_data-25)
    mycanvas.line(34-x_ad, 680+85, 34-x_ad, y_data+102-25)
    mycanvas.line(64-x_ad, 680+85, 64-x_ad, y_data+102-25)
    mycanvas.line(99-x_ad, 680+85, 99-x_ad, y_data-25)

    #     tray and extra pocket
    y_data = y_data - 25
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(10, y_data + 11, str('Total tray : '))
    mycanvas.drawString(110-x_ad, y_data + 11, str(total_tray))
    mycanvas.drawString(180-x_ad, y_data + 11, str('Total Loose Packet : '))
    mycanvas.drawString(330-x_ad, y_data + 11, str(total_packet))
    mycanvas.line(5, y_data,  product_x_axis - 7, y_data)
    mycanvas.line( product_x_axis - 7, y_data, product_x_axis - 7, y_data + 25)

    mycanvas.drawString(450, y_data-30, str('Route Supervisor'))

    #     -----------------------third page-------------------
    business_ids = get_business_ids(route_id, session_id, date)
    mycanvas.showPage()
    mycanvas.setLineWidth(0)
    mycanvas.setStrokeColor(colors.lightgrey)
    x_new = 50
    temp = 1
    for business_id in business_ids:
        business_data = get_individual_business_data(business_id, session_id, date)
        last_count_for_business_bill = IndentCodeBank.objects.get(code_for='business_bill')
        bill_number = int(last_count_for_business_bill.last_code) + 1
        if bill_number == 999999:
            last_count_for_business_bill.last_code = 0
        else:
            last_count_for_business_bill.last_code = bill_number
        last_count_for_business_bill.save()
        if temp == 1:
            third_y = 820
            # HEADER
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(110 + x_new, third_y + 5, str('CDCMPU - Delivery Note'))
            mycanvas.drawString(x_new - 40, third_y - 15, str(business_data['route_name']) + ' '+ ' | ' + ' ' + str('No' + ' : ' + str(bill_number).zfill(6)) + ' '+ ' | ' + ' ' + str(route_date + '/' + business_data['session']))
            key_id = list(business_data['sales'].keys())
            # second line
            mycanvas.drawString(x_new - 40, third_y - 35, str('Booth: '))
            mycanvas.drawString(45, third_y - 35, str(' ' + business_data['business_code']) + ' '+ ' | ' + ' ' )
            # third line
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(90, third_y - 35, ' ' + str(
                business_data['agent_first_name'][:25] + ' [' + business_data[
                    'agent_code'] + ']'))
            mycanvas.setFont('Helvetica', 12)
            third_y = third_y + 20
            #         mycanvas.drawString(200,third_y-55, str(route_date +'/'+ business_data['session']))
            # loop 1 table top line
            mycanvas.line(x_new - 40, third_y - 65, 300 + x_new-55, third_y - 65)
            # loop 1 line aftr table header
            mycanvas.line(x_new - 40, third_y - 85, 300 + x_new-55, third_y - 85)

            mycanvas.drawString(x_new - 35, third_y - 80, str('No'))

            # product
            mycanvas.drawString(5 + x_new-15, third_y - 80, str('Product'))

            # Cash
            mycanvas.drawString(90 + x_new-40, third_y - 80, str('Cash'))

            # Card
            mycanvas.drawString(145 + x_new-40, third_y - 80, str('Card'))

            # Trays
            mycanvas.drawString(192 + x_new-40, third_y - 80, str('Trays'))

            # pkts
            mycanvas.drawString(250 + x_new-40, third_y - 80, str('Pkts'))

            # order products
            mycanvas.setFont('Helvetica', 12)
            product_axis = third_y - 100
            for sale_index, sale in enumerate(business_data['sales'], start=1):
                mycanvas.drawString(x_new - 30, product_axis, str(sale_index))
                mycanvas.drawString(x_new -10, product_axis, str(business_data['sales'][sale]['product_short_name']))
                mycanvas.drawRightString(135 + x_new-50, product_axis, str(int(business_data['sales'][sale]['count'])))
                mycanvas.drawRightString(185 + x_new-45, product_axis,
                                         str(int(business_data['sales'][sale]['icustomer_count'])))
                mycanvas.drawRightString(240 + x_new-50, product_axis,
                                         str(int(business_data['sales'][sale]['calculated_tray_count'])))
                mycanvas.drawRightString(295 + x_new-55, product_axis,
                                         str(int(business_data['sales'][sale]['calculated_pocket_count'])))
                product_axis -= 15
            # border
            product_axis += 5
            mycanvas.line(x_new - 40, product_axis - 20, x_new - 40, third_y - 65)
            mycanvas.line(300 + x_new-55, product_axis - 20, 300 + x_new-55, third_y - 65)
            # inner lines
            mycanvas.line(x_new - 40, product_axis, 300 + x_new- 55, product_axis)

            mycanvas.line(x_new-15, product_axis, x_new-15, third_y - 65)
            mycanvas.line(85 + x_new-40, product_axis, 85 + x_new-40, third_y - 65)
            mycanvas.line(140 + x_new-40, product_axis, 140 + x_new-40, third_y - 65)
            mycanvas.line(190 + x_new-40, product_axis, 190 + x_new-40, third_y - 65)
            mycanvas.line(245 + x_new-40, product_axis, 245 + x_new-40, third_y - 65)

            # total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(x_new - 35, product_axis - 15, str('Milk(Cash Sales)'))
            mycanvas.drawString(150 + x_new, product_axis - 15, 'Rs. ' +  str(business_data['total_cost']))
            mycanvas.line(x_new - 40, product_axis - 20, 300 + x_new-55, product_axis - 20)

            mycanvas.drawString(100 + x_new, product_axis - 50, str('Receiver\'s Signature'))
            temp += 1
           
        elif temp == 2:
            # TOP RIGHT
            # HEADER
            x_adjust = 8
            third_y = 820
            third_right_y = third_y
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(480 + x_new-60-x_adjust, third_right_y + 5, str('CDCMPU - Delivery Note'))

            mycanvas.drawString(330 + x_new-60-x_adjust, third_right_y - 15, str(business_data['route_name']) + ' '+ ' | ' + ' ' + str('No' + ' : ' + str(bill_number).zfill(6)) + ' '+ ' | ' + ' ' + str(route_date + '/' + business_data['session']))
            key_id = list(business_data['sales'].keys())
            # second line
            mycanvas.drawString(310, third_right_y - 35, str('Booth:'))
            mycanvas.drawString(350, third_right_y - 35, str(business_data['business_code']) + ' '+ ' | ' + ' ')

            mycanvas.drawString(400, third_right_y - 35,  str(business_data['agent_first_name'][:25] + ' [' +
                business_data['agent_code'] + ']'))
            mycanvas.setFont('Helvetica', 12)
            third_y = third_y + 20
            third_right_y = third_y
            mycanvas.line(320 + x_new-50-x_adjust, third_right_y - 65, 660 + x_new-50-x_adjust-65, third_right_y - 65)
            mycanvas.line(320 + x_new-50-x_adjust, third_right_y - 85, 660 + x_new-50-x_adjust-65, third_right_y - 85)

            mycanvas.drawString(323 + x_new-50-x_adjust, third_y - 80, str('No'))

            # product
            mycanvas.drawString(360 + x_new-60-x_adjust, third_y - 80, str('Product'))

            # Cash
            mycanvas.drawString(448 + x_new-90-x_adjust, third_y - 80, str('Cash'))

            # Card
            mycanvas.drawString(500 + x_new-90-x_adjust, third_y - 80, str('Card'))

            # Trays
            mycanvas.drawString(550 + x_new-90-x_adjust, third_y - 80, str('Trays'))

            # pkts
            mycanvas.drawString(615 + x_new-100-x_adjust, third_y - 80, str('Pkts'))
            mycanvas.setFont('Helvetica', 12)
            right_product_axis = third_y - 100
            for sale_index, sale in enumerate(business_data['sales'], start=1):
                mycanvas.drawString(330 + x_new-50-x_adjust, right_product_axis, str(sale_index))
                mycanvas.drawString(352 + x_new-55-x_adjust, right_product_axis,
                                    str(business_data['sales'][sale]['product_short_name']))
                mycanvas.drawRightString(490 + x_new-100-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['count'])))
                mycanvas.drawRightString(535 + x_new-95-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['icustomer_count'])))
                mycanvas.drawRightString(600 + x_new-105-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['calculated_tray_count'])))
                mycanvas.drawRightString(655 + x_new-115-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['calculated_pocket_count'])))
                right_product_axis -= 15

            right_product_axis += 5
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis - 20, 320 + x_new-50-x_adjust, third_y - 65)
            mycanvas.line(660 + x_new-50-x_adjust-65, right_product_axis - 20, 660 + x_new-50-x_adjust-65, third_y - 65)
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis, 660 + x_new-50-x_adjust-65, right_product_axis)

            mycanvas.line(350 + x_new-55-x_adjust, right_product_axis, 350 + x_new-55-x_adjust, third_y - 65)
            mycanvas.line(440 + x_new-90-x_adjust, right_product_axis, 440 + x_new-90-x_adjust, third_y - 65)
            mycanvas.line(495 + x_new-100-x_adjust, right_product_axis, 495 + x_new-100-x_adjust, third_y - 65)
            mycanvas.line(545 + x_new-100-x_adjust, right_product_axis, 545 + x_new-100-x_adjust, third_y - 65)
            mycanvas.line(605 + x_new-100-x_adjust, right_product_axis, 605 + x_new-100-x_adjust, third_y - 65)

            # total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(325 + x_new-50-x_adjust, right_product_axis - 15, str('Milk(Cash Sales)'))
            mycanvas.drawString(510 + x_new-50-x_adjust, right_product_axis - 15, 'Rs. ' +  str(business_data['total_cost']))
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis - 20, 660 + x_new-50-x_adjust-65, right_product_axis - 20)

            mycanvas.drawString(400 + x_new-50, right_product_axis - 50, str('Receiver\'s Signature'))
            temp += 1

        elif temp == 3:
            third_y = 550
            # HEADER
            mycanvas.setFont('Helvetica', 12)
           
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(110 + x_new, third_y + 5, str('CDCMPU - Delivery Note'))
            mycanvas.drawString(x_new - 40, third_y - 15, str(business_data['route_name']) + ' '+ ' | ' + ' ' + str('No' + ' : ' + str(bill_number).zfill(6)) + ' '+ ' | ' + ' ' + str(route_date + '/' + business_data['session']))
            key_id = list(business_data['sales'].keys())
            # second line
            mycanvas.drawString(x_new - 40, third_y - 35, str('Booth: '))
            mycanvas.drawString(45, third_y - 35, str(' ' + business_data['business_code']) + ' '+ ' | ' + ' ' )
            # third line
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(90, third_y - 35, str(
                business_data['agent_first_name'][:25] + ' [' + business_data[
                    'agent_code'] + ']'))
            mycanvas.setFont('Helvetica', 12)
            third_y = third_y + 20
            # loop 1 table top line
            mycanvas.line(x_new - 40, third_y - 65, 300 + x_new-55, third_y - 65)
            # loop 1 line aftr table header
            mycanvas.line(x_new - 40, third_y - 85, 300 + x_new-55, third_y - 85)

            mycanvas.drawString(x_new - 35, third_y - 80, str('No'))

            # product
            mycanvas.drawString(5 + x_new-15, third_y - 80, str('Product'))

            # Cash
            mycanvas.drawString(90 + x_new-40, third_y - 80, str('Cash'))

            # Card
            mycanvas.drawString(145 + x_new-40, third_y - 80, str('Card'))

            # Trays
            mycanvas.drawString(192 + x_new-40, third_y - 80, str('Trays'))

            # pkts
            mycanvas.drawString(250 + x_new-40, third_y - 80, str('Pkts'))

            # order products
            mycanvas.setFont('Helvetica', 12)
            product_axis = third_y - 100
            for sale_index, sale in enumerate(business_data['sales'], start=1):
                mycanvas.drawString(x_new - 30, product_axis, str(sale_index))
                mycanvas.drawString(x_new -10, product_axis, str(business_data['sales'][sale]['product_short_name']))
                mycanvas.drawRightString(135 + x_new-50, product_axis, str(int(business_data['sales'][sale]['count'])))
                mycanvas.drawRightString(185 + x_new-45, product_axis,
                                         str(int(business_data['sales'][sale]['icustomer_count'])))
                mycanvas.drawRightString(240 + x_new-50, product_axis,
                                         str(int(business_data['sales'][sale]['calculated_tray_count'])))
                mycanvas.drawRightString(295 + x_new-55, product_axis,
                                         str(int(business_data['sales'][sale]['calculated_pocket_count'])))
                product_axis -= 15
            # border
            product_axis += 5
            mycanvas.line(x_new - 40, product_axis - 20, x_new - 40, third_y - 65)
            mycanvas.line(300 + x_new-55, product_axis - 20, 300 + x_new-55, third_y - 65)
            # inner lines
            mycanvas.line(x_new - 40, product_axis, 300 + x_new- 55, product_axis)

            mycanvas.line(x_new-15, product_axis, x_new-15, third_y - 65)
            mycanvas.line(85 + x_new-40, product_axis, 85 + x_new-40, third_y - 65)
            mycanvas.line(140 + x_new-40, product_axis, 140 + x_new-40, third_y - 65)
            mycanvas.line(190 + x_new-40, product_axis, 190 + x_new-40, third_y - 65)
            mycanvas.line(245 + x_new-40, product_axis, 245 + x_new-40, third_y - 65)

            # total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(x_new - 35, product_axis - 15, str('Milk(Cash Sales)'))
            mycanvas.drawString(150 + x_new, product_axis - 15, 'Rs. ' +  str(business_data['total_cost']))
            mycanvas.line(x_new - 40, product_axis - 20, 300 + x_new-55, product_axis - 20)

            mycanvas.drawString(100 + x_new, product_axis - 40, str('Receiver\'s Signature'))
            temp += 1


        elif temp == 4:
            # TOP RIGHT
            # HEADER
            x_adjust = 8
            third_y = 550
            third_right_y = third_y
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(480 + x_new-60-x_adjust, third_right_y + 5, str('CDCMPU - Delivery Note'))

            mycanvas.drawString(330 + x_new-60-x_adjust, third_right_y - 15, str(business_data['route_name']) + ' '+ ' | ' + ' ' + str('No' + ' : ' + str(bill_number).zfill(6)) + ' '+ ' | ' + ' ' + str(route_date + '/' + business_data['session']))
            key_id = list(business_data['sales'].keys())
            # second line
            mycanvas.drawString(310, third_right_y - 35, str('Booth:'))
            mycanvas.drawString(350, third_right_y - 35, str(business_data['business_code']) + ' '+ ' | ' + ' ')

            mycanvas.drawString(400, third_right_y - 35,  str(business_data['agent_first_name'][:25] + ' [' +
                business_data['agent_code'] + ']'))
            mycanvas.setFont('Helvetica', 12)
            third_y = third_y + 20
            third_right_y = third_y
            #         mycanvas.drawString(500,third_right_y-55, str(route_date +'/'+ business_data['session']))

            mycanvas.line(320 + x_new-50-x_adjust, third_right_y - 65, 660 + x_new-50-x_adjust-65, third_right_y - 65)
            mycanvas.line(320 + x_new-50-x_adjust, third_right_y - 85, 660 + x_new-50-x_adjust-65, third_right_y - 85)

            mycanvas.drawString(323 + x_new-50-x_adjust, third_y - 80, str('No'))

            # product
            mycanvas.drawString(360 + x_new-60-x_adjust, third_y - 80, str('Product'))

            # Cash
            mycanvas.drawString(448 + x_new-90-x_adjust, third_y - 80, str('Cash'))

            # Card
            mycanvas.drawString(500 + x_new-90-x_adjust, third_y - 80, str('Card'))

            # Trays
            mycanvas.drawString(550 + x_new-90-x_adjust, third_y - 80, str('Trays'))

            # pkts
            mycanvas.drawString(615 + x_new-100-x_adjust, third_y - 80, str('Pkts'))
            mycanvas.setFont('Helvetica', 12)
            right_product_axis = third_y - 100
            for sale_index, sale in enumerate(business_data['sales'], start=1):
                mycanvas.drawString(330 + x_new-50-x_adjust, right_product_axis, str(sale_index))
                mycanvas.drawString(352 + x_new-55-x_adjust, right_product_axis,
                                    str(business_data['sales'][sale]['product_short_name']))
                mycanvas.drawRightString(490 + x_new-100-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['count'])))
                mycanvas.drawRightString(535 + x_new-95-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['icustomer_count'])))
                mycanvas.drawRightString(600 + x_new-105-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['calculated_tray_count'])))
                mycanvas.drawRightString(655 + x_new-115-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['calculated_pocket_count'])))
                right_product_axis -= 15

            right_product_axis += 5
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis - 20, 320 + x_new-50-x_adjust, third_y - 65)
            mycanvas.line(660 + x_new-50-x_adjust-65, right_product_axis - 20, 660 + x_new-50-x_adjust-65, third_y - 65)
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis, 660 + x_new-50-x_adjust-65, right_product_axis)

            mycanvas.line(350 + x_new-55-x_adjust, right_product_axis, 350 + x_new-55-x_adjust, third_y - 65)
            mycanvas.line(440 + x_new-90-x_adjust, right_product_axis, 440 + x_new-90-x_adjust, third_y - 65)
            mycanvas.line(495 + x_new-100-x_adjust, right_product_axis, 495 + x_new-100-x_adjust, third_y - 65)
            mycanvas.line(545 + x_new-100-x_adjust, right_product_axis, 545 + x_new-100-x_adjust, third_y - 65)
            mycanvas.line(605 + x_new-100-x_adjust, right_product_axis, 605 + x_new-100-x_adjust, third_y - 65)

            # total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(325 + x_new-50-x_adjust, right_product_axis - 15, str('Milk(Cash Sales)'))
            mycanvas.drawString(510 + x_new-50-x_adjust, right_product_axis - 15, 'Rs. ' +  str(business_data['total_cost']))
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis - 20, 660 + x_new-50-x_adjust-65, right_product_axis - 20)

            mycanvas.drawString(400 + x_new-50, right_product_axis - 50, str('Receiver\'s Signature'))
            temp += 1

        elif temp == 5:
            third_y = 280
            # HEADER
            mycanvas.setFont('Helvetica', 12)
           
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(110 + x_new, third_y + 5, str('CDCMPU - Delivery Note'))
            mycanvas.drawString(x_new - 40, third_y - 15, str(business_data['route_name']) + ' '+ ' | ' + ' ' + str('No' + ' : ' + str(bill_number).zfill(6)) + ' '+ ' | ' + ' ' + str(route_date + '/' + business_data['session']))
            key_id = list(business_data['sales'].keys())
            # second line
            mycanvas.drawString(x_new - 40, third_y - 35, str('Booth: '))
            mycanvas.drawString(45, third_y - 35, str(' ' + business_data['business_code']) + ' '+ ' | ' + ' ' )
            # third line
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(90, third_y - 35, str(
                business_data['agent_first_name'][:25] + ' [' + business_data[
                    'agent_code'] + ']'))
            mycanvas.setFont('Helvetica', 12)
            third_y = third_y + 20

            #         mycanvas.drawString(200,third_y-55, str(route_date +'/'+ business_data['session']))
            # loop 1 table top line
            mycanvas.line(x_new - 40, third_y - 65, 300 + x_new-55, third_y - 65)
            # loop 1 line aftr table header
            mycanvas.line(x_new - 40, third_y - 85, 300 + x_new-55, third_y - 85)

            mycanvas.drawString(x_new - 35, third_y - 80, str('No'))

            # product
            mycanvas.drawString(5 + x_new-15, third_y - 80, str('Product'))

            # Cash
            mycanvas.drawString(90 + x_new-40, third_y - 80, str('Cash'))

            # Card
            mycanvas.drawString(145 + x_new-40, third_y - 80, str('Card'))

            # Trays
            mycanvas.drawString(192 + x_new-40, third_y - 80, str('Trays'))

            # pkts
            mycanvas.drawString(250 + x_new-40, third_y - 80, str('Pkts'))

            # order products
            mycanvas.setFont('Helvetica', 12)
            product_axis = third_y - 100
            for sale_index, sale in enumerate(business_data['sales'], start=1):
                mycanvas.drawString(x_new - 30, product_axis, str(sale_index))
                mycanvas.drawString(x_new -10, product_axis, str(business_data['sales'][sale]['product_short_name']))
                mycanvas.drawRightString(135 + x_new-50, product_axis, str(int(business_data['sales'][sale]['count'])))
                mycanvas.drawRightString(185 + x_new-45, product_axis,
                                         str(int(business_data['sales'][sale]['icustomer_count'])))
                mycanvas.drawRightString(240 + x_new-50, product_axis,
                                         str(int(business_data['sales'][sale]['calculated_tray_count'])))
                mycanvas.drawRightString(295 + x_new-55, product_axis,
                                         str(int(business_data['sales'][sale]['calculated_pocket_count'])))
                product_axis -= 15
            # border
            product_axis += 5
            mycanvas.line(x_new - 40, product_axis - 20, x_new - 40, third_y - 65)
            mycanvas.line(300 + x_new-55, product_axis - 20, 300 + x_new-55, third_y - 65)
            # inner lines
            mycanvas.line(x_new - 40, product_axis, 300 + x_new- 55, product_axis)

            mycanvas.line(x_new-15, product_axis, x_new-15, third_y - 65)
            mycanvas.line(85 + x_new-40, product_axis, 85 + x_new-40, third_y - 65)
            mycanvas.line(140 + x_new-40, product_axis, 140 + x_new-40, third_y - 65)
            mycanvas.line(190 + x_new-40, product_axis, 190 + x_new-40, third_y - 65)
            mycanvas.line(245 + x_new-40, product_axis, 245 + x_new-40, third_y - 65)

            # total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(x_new - 35, product_axis - 15, str('Milk(Cash Sales)'))
            mycanvas.drawString(150 + x_new, product_axis - 15, 'Rs. ' +  str(business_data['total_cost']))
            mycanvas.line(x_new - 40, product_axis - 20, 300 + x_new-55, product_axis - 20)

            mycanvas.drawString(100 + x_new, product_axis - 40, str('Receiver\'s Signature'))
            temp += 1


        elif temp == 6:
            # TOP RIGHT
           # HEADER
            x_adjust = 8
            third_y = 280
            third_right_y = third_y
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(480 + x_new-60-x_adjust, third_right_y + 5, str('CDCMPU - Delivery Note'))

            mycanvas.drawString(330 + x_new-60-x_adjust, third_right_y - 15, str(business_data['route_name']) + ' '+ ' | ' + ' ' + str('No' + ' : ' + str(bill_number).zfill(6)) + ' '+ ' | ' + ' ' + str(route_date + '/' + business_data['session']))
            key_id = list(business_data['sales'].keys())
            # second line
            mycanvas.drawString(310, third_right_y - 35, str('Booth:'))
            mycanvas.drawString(350, third_right_y - 35, str(business_data['business_code']) + ' '+ ' | ' + ' ')

            mycanvas.drawString(400, third_right_y - 35,  str(business_data['agent_first_name'][:25] + ' [' +
                business_data['agent_code'] + ']'))
            mycanvas.setFont('Helvetica', 12)
            third_y = third_y + 20
            third_right_y = third_y

            mycanvas.line(320 + x_new-50-x_adjust, third_right_y - 65, 660 + x_new-50-x_adjust-65, third_right_y - 65)
            mycanvas.line(320 + x_new-50-x_adjust, third_right_y - 85, 660 + x_new-50-x_adjust-65, third_right_y - 85)

            mycanvas.drawString(323 + x_new-50-x_adjust, third_y - 80, str('No'))

            # product
            mycanvas.drawString(360 + x_new-60-x_adjust, third_y - 80, str('Product'))

            # Cash
            mycanvas.drawString(448 + x_new-90-x_adjust, third_y - 80, str('Cash'))

            # Card
            mycanvas.drawString(500 + x_new-90-x_adjust, third_y - 80, str('Card'))

            # Trays
            mycanvas.drawString(550 + x_new-90-x_adjust, third_y - 80, str('Trays'))

            # pkts
            mycanvas.drawString(615 + x_new-100-x_adjust, third_y - 80, str('Pkts'))
            mycanvas.setFont('Helvetica', 12)
            right_product_axis = third_y - 100
            for sale_index, sale in enumerate(business_data['sales'], start=1):
                mycanvas.drawString(330 + x_new-50-x_adjust, right_product_axis, str(sale_index))
                mycanvas.drawString(352 + x_new-55-x_adjust, right_product_axis,
                                    str(business_data['sales'][sale]['product_short_name']))
                mycanvas.drawRightString(490 + x_new-100-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['count'])))
                mycanvas.drawRightString(535 + x_new-95-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['icustomer_count'])))
                mycanvas.drawRightString(600 + x_new-105-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['calculated_tray_count'])))
                mycanvas.drawRightString(655 + x_new-115-x_adjust, right_product_axis,
                                         str(int(business_data['sales'][sale]['calculated_pocket_count'])))
                right_product_axis -= 15

            right_product_axis += 5
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis - 20, 320 + x_new-50-x_adjust, third_y - 65)
            mycanvas.line(660 + x_new-50-x_adjust-65, right_product_axis - 20, 660 + x_new-50-x_adjust-65, third_y - 65)
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis, 660 + x_new-50-x_adjust-65, right_product_axis)

            mycanvas.line(350 + x_new-55-x_adjust, right_product_axis, 350 + x_new-55-x_adjust, third_y - 65)
            mycanvas.line(440 + x_new-90-x_adjust, right_product_axis, 440 + x_new-90-x_adjust, third_y - 65)
            mycanvas.line(495 + x_new-100-x_adjust, right_product_axis, 495 + x_new-100-x_adjust, third_y - 65)
            mycanvas.line(545 + x_new-100-x_adjust, right_product_axis, 545 + x_new-100-x_adjust, third_y - 65)
            mycanvas.line(605 + x_new-100-x_adjust, right_product_axis, 605 + x_new-100-x_adjust, third_y - 65)

            # total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(325 + x_new-50-x_adjust, right_product_axis - 15, str('Milk(Cash Sales)'))
            mycanvas.drawString(510 + x_new-50-x_adjust, right_product_axis - 15, 'Rs. ' +  str(business_data['total_cost']))
            mycanvas.line(320 + x_new-50-x_adjust, right_product_axis - 20, 660 + x_new-50-x_adjust-65, right_product_axis - 20)

            mycanvas.drawString(400 + x_new-50, right_product_axis - 50, str('Receiver\'s Signature'))
            mycanvas.showPage()
            mycanvas.setLineWidth(0)
            mycanvas.setStrokeColor(colors.lightgrey)

            temp = 1
    temp_route_id = RouteTempRouteMap.objects.get(main_route_id=route_id).temp_route_id
    if RouteTrace.objects.filter(route_id=temp_route_id, date=date).exists():
        generate_pdf_for_merging_temp_with_main(temp_route_id, session_id, date, mycanvas)
    mycanvas.save()
    document = {}
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
            document['path'] = image_path
    except Exception as err:
        print(err)
    return document


def route_wise_business_data(route_id, session_id, selected_date):
    route_id = route_id
    session_id = session_id
    selected_date = selected_date
    selected_month = selected_date.month
    selected_year = selected_date.year
    business_ids = RouteBusinessMap.objects.filter(route_id=route_id).values_list('business_id', flat=True)
    sales_values = Sale.objects.filter(sale_group__business_id__in=business_ids, sale_group__session_id=session_id,
                                       product__is_active=True,
                                       sale_group__date=selected_date).values_list('id', 'sale_group_id', 'count',
                                                                                   'cost', 'product_id',
                                                                                   'product__name',
                                                                                   'sale_group__session_id',
                                                                                   'sale_group__business_id',
                                                                                   'sale_group__business__business_type_id',
                                                                                   'sale_group__business__business_type__name',
                                                                                   'sale_group__business__business_type__display_ordinal')
    sales_column = ['id', 'sale_group_id', 'count', 'cost', 'product_id', 'product_name', 'session_id', 'business_id',
                    'business_type_id', 'business_type', 'business_type_display_ordinal']
    sales_df = pd.DataFrame(list(sales_values), columns=sales_column)

    # serve customer order based on the business ids
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=selected_month,
                                                      icustomer_sale_group__date__year=selected_year,
                                                      icustomer_sale_group__business_id__in=business_ids,
                                                      icustomer_sale_group__session_id=session_id)
    icustomer_sale_list = list(
        icustomer_sale_obj.values_list('id', 'icustomer_sale_group_id', 'count', 'cost', 'product_id', 'product__name',
                                       'icustomer_sale_group__session_id', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__business__business_type_id',
                                       'icustomer_sale_group__business__business_type__name',
                                       'icustomer_sale_group__business__business_type__display_ordinal'))
    icustomer_sale_column = ['id', 'sale_group_id', 'count', 'cost', 'product_id', 'product_name', 'session_id',
                             'business_id', 'business_type_id', 'business_type', 'business_type_display_ordinal']
    icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)

    # merge icustomer sale with business sale
    final_df = sales_df.merge(icustomer_sale_df, how="outer")
    vehicle_data = RouteVehicleMap.objects.get(route_id=route_id)

    agents_values = BusinessAgentMap.objects.filter(business_id__in=business_ids).values_list('business_id',
                                                                                              'business__code',
                                                                                              'agent__first_name',
                                                                                              'agent__last_name',
                                                                                              'agent__agent_profile__mobile',
                                                                                              'agent__agent_code')
    agent_columns = ['business_id', 'business_code', 'agent_first_name', 'agent_last_name', 'agent_mobile',
                     'agent_code']
    agent_df = pd.DataFrame(list(agents_values), columns=agent_columns)

    business_agent_df = pd.merge(final_df, agent_df, left_on='business_id', right_on='business_id', how='left')
    business_agent_df = business_agent_df.sort_values(by=['business_type_display_ordinal'])
    business_agent_df = business_agent_df.fillna(0)

    products = Product.objects.filter(is_active=True).order_by('id')
    route_wise_data = {
        'booth_types': {},
        'route_name': Route.objects.get(id=route_id).name,
        'vehicle_number': vehicle_data.vehicle.licence_number,
        'session_name': Session.objects.get(id=session_id).display_name,
        'total': {},
        'total_booth': 0
    }
    for product in products:
        route_wise_data['total'][product.id] = final_df[final_df['product_id'] == product.id].sum()['count']
    for index, row in business_agent_df.iterrows():
        if not row['business_type_id'] in route_wise_data['booth_types']:
            route_wise_data['booth_types'][row['business_type_id']] = {}
            route_wise_data['booth_types'][row['business_type_id']]['booth_ids'] = []
            route_wise_data['booth_types'][row['business_type_id']]['sub_total'] = {}
        if not row['business_id'] in route_wise_data['booth_types'][row['business_type_id']]:
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']] = {}
            route_wise_data['booth_types'][row['business_type_id']]['booth_ids'].append(row['business_id'])
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['agent_name'] = row[
                'agent_first_name']
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['business_code'] = row[
                'business_code']
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['product'] = {}

        if not row['product_id'] in route_wise_data['booth_types'][row['business_type_id']]['sub_total']:
            route_wise_data['booth_types'][row['business_type_id']]['sub_total'][row['product_id']] = 0
        route_wise_data['booth_types'][row['business_type_id']]['sub_total'][row['product_id']] += row['count']
        if not row['product_id'] in route_wise_data['booth_types'][row['business_type_id']][row['business_id']][
            'product']:
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['product'][
                row['product_id']] = 0
        route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['product'][row['product_id']] += \
            row['count']
    business_type_obj = BusinessType.objects.filter()
    for business_type in business_type_obj:
        if business_type.id in route_wise_data['booth_types'].keys():
            route_wise_data['total_booth'] += len(route_wise_data['booth_types'][business_type.id]['booth_ids'])
    return route_wise_data



def get_business_ids(route_id, session_id, date):
    # return ordered_business
    business_ids = RouteBusinessMap.objects.filter(route_id=route_id).values_list('business_id', flat=True)
    ordered_business = list(
        SaleGroup.objects.filter(business_id__in=business_ids, date=date, session_id=session_id).values_list(
            'business_id', flat=True))
    selected_month = date
    ordered_business_for_icustomer = list(
        ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=selected_month.month,
                                          date__year=selected_month.year, session_id=session_id).values_list(
            'business_id', flat=True))
    return list(set(ordered_business + ordered_business_for_icustomer))


def find_tray_count_for_indivioul_business(agent_count, icustomer_count, product_defalut_count, tray_count, product_id):
    count = agent_count + icustomer_count
    loose_milk_ids = [22, 23, 24]
    if not product_defalut_count == 0:
        remainder_of_tray_count = count % product_defalut_count
        coefieient_of_tray_count = count // product_defalut_count
        if not product_id in loose_milk_ids:
            tray_count = (count / product_defalut_count) * tray_count
            return tray_count
        else:
            if remainder_of_tray_count > 0:
                return coefieient_of_tray_count + 1
            else:
                return coefieient_of_tray_count
    else:
        return 0


def find_packet_count_for_indivioul_business(agent_count, icustomer_count, product_defalut_count,product_id):
    loose_milk_ids = [22, 23, 24]
    count = agent_count + icustomer_count
    if not product_id in loose_milk_ids:
        if not product_defalut_count == 0:
            packet_count = count % product_defalut_count
            return packet_count
        else:
            return 0
    else:
        return 0


def get_individual_business_data(business_id, session_id, date):
    product_values = Product.objects.filter(is_active=True).values_list('id', 'short_name', 'unit__name', 'quantity')
    product_columns = ['id', 'product_short_name', 'product_unit', 'quantity']
    product_df = pd.DataFrame(list(product_values), columns=product_columns)
    tray_config_values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id',
                                                                                               'tray_count',
                                                                                               'product_count')
    tray_config_columns = ['tray_product_id', 'p_c_tray_count', 'p_c_product_count']
    tray_config_df = pd.DataFrame(list(tray_config_values), columns=tray_config_columns)
    tray_config_df = tray_config_df.fillna(0)
    product_tray_merge_df = pd.merge(product_df, tray_config_df, how='left', left_on='id', right_on='tray_product_id')
    product_tray_merge_df = product_tray_merge_df.fillna(0)
    # business_code = request.data['business_code']
    business = Business.objects.get(id=business_id)
    session_id = session_id
    date = date
    month = date.month
    year = date.year
    # date = date.strftime("%Y-%m-%d")
    route = RouteBusinessMap.objects.get(business=business, route__session_id=session_id).route
    agent = BusinessAgentMap.objects.filter(business=business)[0].agent
    session = Session.objects.get(id=session_id)
    data = {
        'agent_first_name': agent.first_name,
        'agent_last_name': agent.last_name,
        'agent_code': agent.agent_code,
        'route_name': route.name,
        'date': date,
        'session': session.display_name,
        'business_code': business.code,
        'no': '232423',
        'total_cost': None,
        'sales': None
    }
    sale_group = SaleGroup.objects.filter(date=date, session_id=session_id, business_id=business_id)
    # business_sale_group = sale_group[0]
    sales_values = Sale.objects.filter(sale_group__in=sale_group, product__is_active=True).values_list('sale_group',
                                                                                                       'product_id',
                                                                                                       'count')
    sales_columns = ['sale_group_id', 'product_id', 'count']
    sale_df = pd.DataFrame(list(sales_values), columns=sales_columns)
    sale_df = sale_df.fillna(0)
    data['total_cost'] = sale_group.aggregate(Sum('total_cost'))['total_cost__sum']
    final_df = pd.merge(sale_df, product_tray_merge_df, how='left', left_on='product_id', right_on='id')
    final_df = final_df.fillna(0)

    business_df = final_df

    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=month,
                                                      icustomer_sale_group__date__year=year,
                                                      icustomer_sale_group__session_id=session_id,
                                                      product__is_active=True,
                                                      icustomer_sale_group__business_id=business_id)
    icustomer_sales_values = list(icustomer_sale_obj.values_list('icustomer_sale_group', 'product_id', 'count',
                                                                 'icustomer_sale_group__icustomer'))
    icustomer_sales_columns = ['icustomer_sale_group_id', 'product_id', 'indivioul_icustomer_count', 'icustomer_id']
    icustomer_sale_df = pd.DataFrame(icustomer_sales_values, columns=icustomer_sales_columns)
    icustomer_sale_df['icustomer_count'] = icustomer_sale_df.groupby(['product_id'])[
        'indivioul_icustomer_count'].transform('sum')
    icustomer_sale_df = icustomer_sale_df.drop_duplicates(subset=['product_id'], keep="first")
    icustomer_sale_df = icustomer_sale_df.fillna(0)
    icustomer_sale_df = pd.merge(icustomer_sale_df, product_tray_merge_df, how='left', left_on='product_id',
                                 right_on='id')

    # construct business sale df
    new_df = pd.merge(business_df, icustomer_sale_df, how='outer',
                      left_on=['id', 'product_short_name', 'p_c_product_count', 'p_c_tray_count', 'product_unit'],
                      right_on=['id', 'product_short_name', 'p_c_product_count', 'p_c_tray_count', 'product_unit'])
    new_df = new_df[
        ['id', 'count', 'icustomer_count', 'product_short_name', 'p_c_product_count', 'p_c_tray_count', 'product_unit']]
    new_df['count'] = new_df['count'].fillna(0)
    new_df['icustomer_count'] = new_df['icustomer_count'].fillna(0)
    new_df['count'].astype(int)
    new_df['icustomer_count'].astype(int)
    new_df['calculated_tray_count'] = new_df.apply(
        lambda x: find_tray_count_for_indivioul_business(x['count'], x['icustomer_count'], x['p_c_product_count'],
                                                         x['p_c_tray_count'], x['id']), axis=1)
    new_df['calculated_tray_count'] = new_df['calculated_tray_count'].fillna(0)
    new_df['calculated_tray_count'] = new_df['calculated_tray_count'].astype(int)
    new_df['calculated_pocket_count'] = new_df.apply(
        lambda x: find_packet_count_for_indivioul_business(x['count'], x['icustomer_count'], x['p_c_product_count'],
                                                           x['id']), axis=1)
    new_df['calculated_tray_count'] = new_df['calculated_tray_count'].fillna(0)
    new_df = new_df.fillna(0)
    data['sales'] = new_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    data['total_business_product_count'] = new_df['count'].sum()
    data['total_icustomer_product_count'] = new_df['icustomer_count'].sum()
    business_data = data
    return business_data


def serve_counter_order_details_for_agent(counter_id, date, user_name):
    
    if counter_id == 'online':
        ws_sale_group_obj = SaleGroup.objects.filter(time_created__date=date, ordered_via_id__in=[1, 3],
                                                        business__business_type_id=9).order_by('id')
        ns_sale_group_obj = SaleGroup.objects.filter(time_created__date=date, ordered_via_id__in=[1, 3]).exclude(
            business__business_type_id=9).order_by('id')       
        counter_name = 'Online'
    else:
        employee_trace_ids = list(
            CounterEmployeeTraceMap.objects.filter(counter_id=counter_id, time_created__date=date).values_list('id',
                                                                                                                flat=True))
        employee_trace_sale_group_obj = list(
            CounterEmployeeTraceSaleGroupMap.objects.filter(
                counter_employee_trace_id__in=employee_trace_ids).values_list(
                'sale_group', flat=True))
        ws_sale_group_obj = SaleGroup.objects.filter(id__in=employee_trace_sale_group_obj,
                                                        business__business_type_id=9).order_by('id')
        ns_sale_group_obj = SaleGroup.objects.filter(id__in=employee_trace_sale_group_obj).exclude(
            business__business_type_id=9).order_by('id')
        counter_name = Counter.objects.get(id=counter_id).name


    ws_sale_obj = Sale.objects.filter(sale_group_id__in=ws_sale_group_obj, product__is_active=True).order_by(
        'sale_group_id')
    ns_sale_obj = Sale.objects.filter(sale_group_id__in=ns_sale_group_obj, product__is_active=True).order_by(
        'sale_group_id')

    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
    
    zone_dict = {}
    for zone in Zone.objects.all().exclude(id__in=[11,12,13,15]):
        if zone.name not in zone_dict:
            zone_dict[zone.name] = {
                "amount":0,
                "order_count":[],
            }
    for sale_group in ws_sale_group_obj:
        if sale_group.zone.name in zone_dict:
            zone_dict[sale_group.zone.name]['order_count'].append(sale_group.business_id)
            zone_dict[sale_group.zone.name]['amount'] += sale_group.total_cost
    for sale_group in ns_sale_group_obj:
        if sale_group.zone.name in zone_dict:
            zone_dict[sale_group.zone.name]['order_count'].append(sale_group.business_id)
            zone_dict[sale_group.zone.name]['amount'] += sale_group.total_cost
    
    print(zone_dict)
    
    
    if counter_id == "online":
        data_dict ={
            "counter_details": {
                "counter_id": counter_id,
                "counter_name": counter_name,
                "employee_name": [],
                "date": date
            },
            "cash":{
                "grand_total": 0,
                "booth_sale": {},
                "product_total_count": {}
            },
            "cridet":{
                "grand_total": 0,
                "booth_sale": {},
                "product_total_count": {}
            }
        }
    else:
        data_dict = {
            "grand_total": 0,
            "counter_details": {
                "counter_id": counter_id,
                "counter_name": counter_name,
                "employee_name": [],
                "date": date
            },
            "booth_sale": {},
            "product_total_count": {}
        }
    if counter_id == 'online':
        data_dict["counter_details"]["employee_name"].append('-')
    else:
        for employee_trace_id in employee_trace_ids:
            employee_name = CounterEmployeeTraceMap.objects.get(
                id=employee_trace_id).employee.user_profile.user.first_name
            data_dict["counter_details"]["employee_name"].append(employee_name)
            
    if counter_id == 'online':
        for product in products:
            if not product.id in data_dict["cash"]["product_total_count"]:
                data_dict["cash"]["product_total_count"][product.id] = {
                    "count": 0,
                    "ns_litre": 0,
                    "ns_cost": 0,
                    "ns_count": 0,
                    "ws_litre": 0,
                    "ws_cost": 0,
                    "ws_count": 0,
                    "total_liter": 0
                }
            if not product.id in data_dict["cridet"]["product_total_count"]:
                data_dict["cridet"]["product_total_count"][product.id] = {
                    "count": 0,
                    "ns_litre": 0,
                    "ns_cost": 0,
                    "ns_count": 0,
                    "ws_litre": 0,
                    "ws_cost": 0,
                    "ws_count": 0,
                    "total_liter": 0
                }
    else:
        for product in products:
            if not product.id in data_dict["product_total_count"]:
                    data_dict["product_total_count"][product.id] = {
                        "count": 0,
                        "ns_litre": 0,
                        "ns_cost": 0,
                        "ns_count": 0,
                        "ws_litre": 0,
                        "ws_cost": 0,
                        "ws_count": 0,
                        "total_liter": 0
                    }
    online_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=1, order_category_id=1).values_list('business_type_id', flat=True))
    for ns in ns_sale_group_obj:
        if counter_id == "online":
            ns_sale = Sale.objects.filter(sale_group_id=ns.id, product__is_active=True)
            if ns.business.business_type_id in online_business_type_ids:
                time = ns.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ns.business.code in data_dict["cash"]["booth_sale"]:
                    data_dict["cash"]["booth_sale"][ns.business.code] = {
                        "date":ns.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ns.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(
                            business_id=ns.business.id).agent.first_name + " "+ BusinessAgentMap.objects.get(
                            business_id=ns.business.id).agent.last_name)[:5],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
            else:
                time = ns.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ns.business.code in data_dict["cridet"]["booth_sale"]:
                    data_dict["cridet"]["booth_sale"][ns.business.code] = {
                        "date":ns.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ns.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(business_id=ns.business.id).agent.first_name+" "+BusinessAgentMap.objects.get(business_id=ns.business.id).agent.last_name)[:6],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
                    
            for sale in ns_sale:
                if sale.sale_group.business.business_type_id in online_business_type_ids:
                    for product in products:
                        if not product.id in data_dict["cash"]["booth_sale"][ns.business.code]["ns"]:
                            data_dict["cash"]["booth_sale"][ns.business.code]["ns"][product.id] = {
                                "count": 0,
                                "cost": 0
                            }

                    data_dict["cash"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["cost"] += sale.cost
                    data_dict["cash"]["booth_sale"][ns.business.code]["product_total_cost"] += sale.cost

                    data_dict["cash"]["product_total_count"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ns_count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ns_litre"] += sale.count * float(
                        sale.product.quantity / 1000)
                    data_dict["cash"]["product_total_count"][sale.product_id]["ns_cost"] += sale.cost
                    data_dict["cash"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                        sale.product.quantity / 1000)

                    data_dict["cash"]["grand_total"] += sale.cost
                else:
                    for product in products:
                        if not product.id in data_dict["cridet"]["booth_sale"][ns.business.code]["ns"]:
                            data_dict["cridet"]["booth_sale"][ns.business.code]["ns"][product.id] = {
                                "count": 0,
                                "cost": 0
                            }

                    data_dict["cridet"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["count"] += sale.count
                    data_dict["cridet"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["cost"] += sale.cost
                    data_dict["cridet"]["booth_sale"][ns.business.code]["product_total_cost"] += sale.cost

                    data_dict["cridet"]["product_total_count"][sale.product_id]["count"] += sale.count
                    data_dict["cridet"]["product_total_count"][sale.product_id]["ns_count"] += sale.count
                    data_dict["cridet"]["product_total_count"][sale.product_id]["ns_litre"] += sale.count * float(
                        sale.product.quantity / 1000)
                    data_dict["cridet"]["product_total_count"][sale.product_id]["ns_cost"] += sale.cost
                    data_dict["cridet"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                        sale.product.quantity / 1000)

                    data_dict["cridet"]["grand_total"] += sale.cost
            
        else:
            ns_sale = Sale.objects.filter(sale_group_id=ns.id, product__is_active=True)
            time = ns.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")
            if not ns.business.code in data_dict["booth_sale"]:
                data_dict["booth_sale"][ns.business.code] = {
                    "date":ns.date.strftime("%d-%b"),
                    "time": time_created,
                    "zone": ns.business.zone.name,
                    "agent_name":str(BusinessAgentMap.objects.get(business_id=ns.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ns.business.id).agent.last_name)[:5],
                    "product_total_cost": 0,
                    "ns": {},
                    "ws": {}
                }
            
            for sale in ns_sale:
                for product in products:
                    if not product.id in data_dict["booth_sale"][ns.business.code]["ns"]:
                        data_dict["booth_sale"][ns.business.code]["ns"][product.id] = {
                            "count": 0,
                            "cost": 0
                        }

                data_dict["booth_sale"][ns.business.code]["ns"][sale.product_id]["count"] += sale.count
                data_dict["booth_sale"][ns.business.code]["ns"][sale.product_id]["cost"] += sale.cost
                data_dict["booth_sale"][ns.business.code]["product_total_cost"] += sale.cost

                data_dict["product_total_count"][sale.product_id]["count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ns_count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ns_litre"] += sale.count * float(
                    sale.product.quantity / 1000)
                data_dict["product_total_count"][sale.product_id]["ns_cost"] += sale.cost
                data_dict["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                    sale.product.quantity / 1000)

                data_dict["grand_total"] += sale.cost

    for ws in ws_sale_group_obj:
        if counter_id == "online":
            ws_sale = Sale.objects.filter(sale_group_id=ws.id, product__is_active=True)
            if ws.business.business_type_id in online_business_type_ids:
                time = ws.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ws.business.code in data_dict["cash"]["booth_sale"]:
                    data_dict["cash"]["booth_sale"][ws.business.code] = {
                        "date":ws.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ws.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(business_id=ws.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ws.business.id).agent.last_name)[:5],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
            else:
                time = ws.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ws.business.code in data_dict["cridet"]["booth_sale"]:
                    data_dict["cridet"]["booth_sale"][ws.business.code] = {
                        "date":ws.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ws.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(business_id=ws.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ws.business.id).agent.last_name)[:5],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
                    
            for sale in ws_sale:
                if sale.sale_group.business.business_type_id in online_business_type_ids:
                    for product in products:
                        if not product.id in data_dict["cash"]["booth_sale"][ws.business.code]["ws"]:
                            data_dict["cash"]["booth_sale"][ws.business.code]["ws"][product.id] = {
                                "count": 0,
                                "cost": 0
                            }

                    data_dict["cash"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["cost"] += sale.cost
                    data_dict["cash"]["booth_sale"][ws.business.code]["product_total_cost"] += sale.cost

                    data_dict["cash"]["product_total_count"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ws_count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ws_litre"] += sale.count * float(
                        sale.product.quantity / 1000)
                    data_dict["cash"]["product_total_count"][sale.product_id]["ws_cost"] += sale.cost
                    data_dict["cash"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                        sale.product.quantity / 1000)

                    data_dict["cash"]["grand_total"] += sale.cost
                else:
                    for product in products:
                        if not product.id in data_dict["cridet"]["booth_sale"][ws.business.code]["ws"]:
                            data_dict["cridet"]["booth_sale"][ws.business.code]["ws"][product.id] = {
                                "count": 0,
                                "cost": 0
                            }

                    data_dict["cridet"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["count"] += sale.count
                    data_dict["cridet"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["cost"] += sale.cost
                    data_dict["cridet"]["booth_sale"][ws.business.code]["product_total_cost"] += sale.cost

                    data_dict["cridet"]["product_total_count"][sale.product_id]["count"] += sale.count
                    data_dict["cridet"]["product_total_count"][sale.product_id]["ws_count"] += sale.count
                    data_dict["cridet"]["product_total_count"][sale.product_id]["ws_litre"] += sale.count * float(
                        sale.product.quantity / 1000)
                    data_dict["cridet"]["product_total_count"][sale.product_id]["ws_cost"] += sale.cost
                    data_dict["cridet"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                        sale.product.quantity / 1000)

                    data_dict["cridet"]["grand_total"] += sale.cost
            
            
        else:
            ws_sale = Sale.objects.filter(sale_group_id=ws.id, product__is_active=True)
            time = ws.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")
            if not ws.business.code in data_dict["booth_sale"]:
                data_dict["booth_sale"][ws.business.code] = {
                    "date":ws.date.strftime("%d-%b"),
                    "time": time_created,
                    "zone": ws.business.zone.name,
                    "agent_name": str(BusinessAgentMap.objects.get(business_id=ws.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ws.business.id).agent.last_name)[:5],
                    "product_total_cost": 0,
                    "ns": {},
                    "ws": {}
                } 
                
                
            for sale in ws_sale:
                for product in products:
                    if not product.id in data_dict["booth_sale"][ws.business.code]["ws"]:
                        data_dict["booth_sale"][ws.business.code]["ws"][product.id] = {
                            "count": 0,
                            "cost": 0
                        }

                data_dict["booth_sale"][ws.business.code]["ws"][sale.product_id]["count"] += sale.count
                data_dict["booth_sale"][ws.business.code]["ws"][sale.product_id]["cost"] += sale.cost
                data_dict["booth_sale"][ws.business.code]["product_total_cost"] += sale.cost

                data_dict["product_total_count"][sale.product_id]["count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ws_count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ws_litre"] += sale.count * float(
                    sale.product.quantity / 1000)
                data_dict["product_total_count"][sale.product_id]["ws_cost"] += sale.cost
                data_dict["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                    sale.product.quantity / 1000)

                data_dict["grand_total"] += sale.cost

    data_dict['user_name'] = user_name
    data = generate_sale_pdf_for_agent_order(data_dict, date,zone_dict)
    return data


def generate_sale_pdf_for_agent_order(data_dict, date,zone_dict):
    new_date = date
    # datetime.datetime.strftime(date, '%d-%b-%Y')
    file_name = str(new_date) + '_' + str(
        data_dict["counter_details"]["counter_name"]) + '_' + 'daily_counter_report_agent_sale' + '.pdf'
#     file_path = os.path.join('static/media/', file_name)
    file_path = os.path.join('static/media/counter_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    # ________Head_lines________#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
    
    #-----------------------------------------------------For_online_order--------------------------------------------------------------#
    if data_dict["counter_details"]["counter_name"] == "Online":
        counter = "Cash"
        for data in data_dict:
            print(data)
            if data == 'counter_details' or data == "user_name":
                pass
            else:
                #     mycanvas.setStrokeColor(colors.lightgrey)
                mycanvas.setFont('Helvetica', 12.5)
                mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Helvetica', 12)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
                mycanvas.setFont('Helvetica-Bold', 10)
                name_emp = ""
                for name in list(set(data_dict["counter_details"]["employee_name"])):
                    name_emp += name + ","
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)


                # _____________table header_____________#
                y_a4 = 90
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
                mycanvas.drawString(130, 675+y_a4, 'booth')
                mycanvas.drawString(130, 665+y_a4, 'code')
                mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
                mycanvas.drawString(126 - 35, 665+y_a4, 'name')
                mycanvas.drawString(50, 675+y_a4, 'zone')
                x_axis = 175
                y_axis = 675+y_a4
                line_x_axis = 50 - 40

                # _____________ Product heading _____________#

                products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
                x_adjust = 10
                for product in products:
                    product_name = list(product.short_name.split(" "))
                    mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
                    try:
                        mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
                    except:
                        pass
                    if product.short_name == products[-1].short_name:
                        x_axis += 50
                        mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

                    # table top line
                    mycanvas.setLineWidth(0)
                    mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
                    # table bottom line
                    mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
                    x_axis += 35 + 10
                    x_adjust += 10
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
                mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
                mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

                # _____________ Agent_name,Business_code,Product ___________#

                y_axix_agent_booth = 630+y_a4+10
                x_axis_agent_booth = 90 - 40
                y_axis_product = 675+y_a4+10

                for index, business in enumerate(data_dict[data]["booth_sale"], start=1):
                    mycanvas.setFont('Helvetica-Bold', 8)
                    mycanvas.drawRightString(line_x_axis + 20, y_axix_agent_booth, str(index))
                    mycanvas.drawString(x_axis_agent_booth-5, y_axix_agent_booth, str(data_dict[data]["booth_sale"][business]["zone"])[:5])
                    mycanvas.drawString(x_axis_agent_booth + 35, y_axix_agent_booth,
                                        str(data_dict[data]["booth_sale"][business]["agent_name"])[:5])
                    mycanvas.drawString(x_axis_agent_booth + 40 + 40, y_axix_agent_booth,
                                        str(business))

                    # _________lines_between_agent_name___________#

                    mycanvas.line(x_axis_agent_booth - 10, y_axix_agent_booth + 50, x_axis_agent_booth - 10,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 30, y_axix_agent_booth + 50, x_axis_agent_booth + 30,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 70, y_axix_agent_booth + 50, x_axis_agent_booth + 70,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 105, y_axix_agent_booth + 50, x_axis_agent_booth + 105,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 650-x_adjust, y_axix_agent_booth + 50, x_axis_agent_booth + 650-x_adjust,
                                  y_axix_agent_booth - 10)

                    # _________left_and_right_border___________#

                    mycanvas.line(line_x_axis, y_axix_agent_booth + 50, line_x_axis, y_axix_agent_booth - 10)
                    mycanvas.line(x_axis-x_adjust-10, y_axix_agent_booth + 50, x_axis-x_adjust-10, y_axix_agent_booth - 10)

                    y_axix_agent_booth -= 20
                    products_list = []
                    x_axis_product = 175
                    total_cost = 0

                    x_adjust = 10
                    for product in products:
                        print(product)
                        ns = 0
                        ws = 0
                        if len(data_dict[data]["booth_sale"][business]['ns']) != 0:
                            ns = data_dict[data]["booth_sale"][business]['ns'][product.id]["count"]
                        if len(data_dict[data]["booth_sale"][business]['ws']) != 0:
                            ws = data_dict[data]["booth_sale"][business]['ws'][product.id]["count"]

                        mycanvas.drawRightString(x_axis_product + 20-x_adjust, y_axis_product - 45, str(round(ns) + round(ws)))

                        x_axis_product += 35 + 10
                        mycanvas.setLineWidth(0)

                        mycanvas.line(x_axis_product - 20-x_adjust, y_axis_product + 5, x_axis_product - 20-x_adjust, y_axis_product - 55)

                        x_adjust += 10      
                    mycanvas.drawRightString(x_axis_product + 35-x_adjust, y_axis_product - 45,
                                             str(data_dict[data]["booth_sale"][business]["product_total_cost"]))
                    mycanvas.drawRightString(x_axis_product + 35 + 35-x_adjust, y_axis_product - 45,
                                             str(data_dict[data]["booth_sale"][business]["time"]))
                    y_axis_product -= 20

                    # _______________After /24____________#

                    if index % 34 == 0:

                        mycanvas.line(line_x_axis, y_axis_product - 35, x_axis-x_adjust+25, y_axis_product - 35)
                        mycanvas.showPage()

                        # ________Head_lines________#

                        light_color = 0x9b9999
                        dark_color = 0x000000
                        mycanvas.setFillColor(HexColor(light_color))
                        mycanvas.setFillColor(HexColor(dark_color))

                        mycanvas.setFont('Helvetica', 12.5)
                        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                        mycanvas.setFont('Helvetica', 12)
                        mycanvas.setFillColor(HexColor(dark_color))
                        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
                        mycanvas.setFont('Helvetica-Bold', 10)
                        name_emp = ""
                        for name in list(set(data_dict["counter_details"]["employee_name"])):
                            name_emp += name + ","
                        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

                        mycanvas.setFillColor(HexColor(dark_color))
                        mycanvas.setFont('Helvetica-Bold', 8)
                        mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
                        mycanvas.drawString(90 + 40, 675+y_a4, 'booth')
                        mycanvas.drawString(90 + 40, 665+y_a4, 'code')
                        mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
                        mycanvas.drawString(126 - 35, 665+y_a4, 'name')
                        mycanvas.drawString(50, 675+y_a4, 'zone')
                        x_axis = 175
                        y_axis = 675+y_a4
                        line_x_axis = 50 - 40

                        # _____________ Product heading _____________#

                        products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
                        x_adjust = 10
                        for product in products:
                            product_name = list(product.short_name.split(" "))
                            mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
                            try:
                                mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
                            except:
                                pass
                            if product.short_name == products[-1].short_name:
                                x_axis += 50
                                mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

                            # table top line
                            mycanvas.setLineWidth(0)
                            mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
                            # table bottom line
                            mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
                            x_axis += 35 + 10
                            x_adjust += 10
                        mycanvas.setFont('Helvetica-Bold', 8)
                        mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
                        mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
                        mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

                        # _____________ Agent_name,Business_code,Product ___________#

                        y_axix_agent_booth = 630+y_a4+10
                        x_axis_agent_booth = 90 - 40
                        y_axis_product = 675+y_a4+10

                        # _________Grand_total__________#

                x_axis_product = 175
                mycanvas.line(line_x_axis, y_axis_product - 35, x_axis + 25-x_adjust, y_axis_product - 35)
                x_adjust = 10
                for i in range(len(products) + 1):
                    mycanvas.line(x_axis_product - 10-x_adjust, y_axis_product, x_axis_product - 10-x_adjust, y_axis_product - 55)
                    x_axis_product += 35 + 10
                    x_adjust += 10

                mycanvas.line(line_x_axis, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 55)
                mycanvas.line(x_axis-x_adjust+35, y_axis_product - 35, x_axis-x_adjust+35, y_axis_product - 55)
                mycanvas.line(line_x_axis, y_axis_product - 35, line_x_axis, y_axis_product - 55)
                mycanvas.drawString(line_x_axis + 35, y_axis_product - 48, "Total Packets")
                mycanvas.drawRightString(x_axis_product-x_adjust+10, y_axis_product - 68, str(data_dict[data]["grand_total"]))

                mycanvas.line(x_axis-x_adjust+35, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 75)
                mycanvas.line(line_x_axis, y_axis_product - 55, line_x_axis, y_axis_product - 75)
                mycanvas.line(x_axis - 60-x_adjust+10, y_axis_product - 55, x_axis - 60-x_adjust+10, y_axis_product - 75)
                mycanvas.line(line_x_axis, y_axis_product - 75, x_axis-x_adjust+35, y_axis_product - 75)
                mycanvas.drawString(x_axis_product - 125-x_adjust+10, y_axis_product - 68, 'Grand Total Rs.')
                mycanvas.setFont('Helvetica-Bold', 12)
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')

                grand_total = data_dict[data]["grand_total"]
                grand_total = f"{grand_total:,.2f}"

                mycanvas.setFont('Helvetica-Bold', 11)
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                mycanvas.drawString(15, y_axis_product - 98, 'The total money collected by counter ' + str(
                    data_dict["counter_details"]["counter_name"])+"("+str(counter)+")" + ' on ')

                mycanvas.setFont('Helvetica-Bold', 13)
                mycanvas.drawString(360, y_axis_product - 98,
                                    str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

                x_axis_product += 35
                x_adjust = 10
                for product in products:
                    try:
                        mycanvas.setFont('Helvetica-Bold', 8)
                        mycanvas.drawRightString(line_x_axis + 145 + 40-x_adjust, y_axis_product - 48,
                                                 str(int(data_dict[data]["product_total_count"][product.id]["count"])))
                        line_x_axis += 35 + 10
                        x_adjust += 10
                    except:
                        pass

                mycanvas.showPage()
                counter = "Credit"
                
                
        # ________Head_lines_for_counter_wise_Total________#

        light_color = 0x9b9999
        dark_color = 0x000000
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.setFillColor(HexColor(dark_color))
        y_a4 = 80

        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 665 + 20+y_a4, "Milk Agents")
        mycanvas.line(300-50, 661 + 20+y_a4, 400-50, 661 + 20+y_a4)

        # table header

        x_adjust = 50
        y_axis_product_total = 645 - 20 + 20 +y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 668 - 20 + 20+y_a4
        y_head = 655 - 20 + 20+y_a4

        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        products_obj = list(Product.objects.filter(is_active=True, group_id__in=[1, 3]).order_by('display_ordinal'))

        index = 0
        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["cash"]["product_total_count"][product.id]["ns_count"] + data_dict["cridet"]["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["cash"]["product_total_count"][product.id]["ns_count"] + data_dict["cridet"]["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_agent
        y_a4 = 90
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 420 + 20+y_a4, "Curd Agents")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-x_adjust, 416 + 20+y_a4, 400-x_adjust, 416 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, group_id=2).order_by('display_ordinal'))

        y_axis_product_total = 405 - 25 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 428 - 25 + 20+y_a4
        y_head = 415 - 25 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["cash"]["product_total_count"][product.id]["ns_count"] + data_dict["cridet"]["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))
            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["cash"]["product_total_count"][product.id]["ns_count"]+data_dict["cridet"]["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"]+data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"]+data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_wholesale
        y_a4 = 100
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 195 + 20+y_a4, "Curd Wholesale")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-50, 191 + 20+y_a4, 400-50, 191 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, id__in=[25, 7, 10]).order_by('display_ordinal'))

        y_axis_product_total = 155 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 178 + 20+y_a4
        y_head = 165 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        wscost = 0
        wsliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["cash"]["product_total_count"][product.id]["ws_count"] + data_dict["cridet"]["product_total_count"][product.id]["ws_count"]
            wsliter += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ws_litre"]), 3)
            wscost += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ws_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["cash"]["product_total_count"][product.id]["ws_count"] + data_dict["cridet"]["product_total_count"][product.id]["ws_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ws_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ws_cost"]), 2)))

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 20, str(wsliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(wscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        grand_total = data_dict["cash"]["grand_total"] + data_dict["cridet"]["grand_total"]
        grand_total = f"{grand_total:,.2f}"

        mycanvas.setFont('Helvetica-Bold', 11)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(15, y_axis_product_total - 58, 'The total money collected by counter ' + str(
            data_dict["counter_details"]["counter_name"]) + ' on ')

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawString(360, y_axis_product_total - 58,
                            str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

        words = num2words(round(data_dict["cash"]["grand_total"] + data_dict["cridet"]["grand_total"]), lang='en_IN')
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawString(15, y_axis_product_total - 58 - 20 - 5,
                                   "Total Amount Collected " + "  Rupees.  " + str(words.upper()) + " " + "Only")

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))

        
        mycanvas.showPage()
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        zone_y = 690
        #for_zonewise_total
        grand_totals = 0
        order_count = 0
        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.line(375,zone_y+55,565,zone_y+55)
        mycanvas.drawCentredString(470,zone_y+37,"Zone Wise Sale Details")
        mycanvas.line(375,zone_y+25,565,zone_y+25)
        mycanvas.drawString(383,zone_y+10,"Sale For")
        mycanvas.drawString(448,zone_y+10,"Count")
        mycanvas.drawString(505,zone_y+10,"Amount")
        mycanvas.line(375,zone_y+5,565,zone_y+5)
        mycanvas.setFont('Helvetica', 10)

        for zone in zone_dict:
            print(zone)
            mycanvas.drawString(380,zone_y-10,str(zone))
            mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]["amount"]))
            mycanvas.drawRightString(485,zone_y-10,str(len(list(set(zone_dict[zone]["order_count"])))))
            mycanvas.line(375,zone_y-20,565,zone_y-20)
            mycanvas.line(440,zone_y+25,440,zone_y-40)
            mycanvas.line(490,zone_y+25,490,zone_y-40)
            mycanvas.line(375,zone_y+55,375,zone_y-40)
            mycanvas.line(565,zone_y+55,565,zone_y-40)
            grand_totals += zone_dict[zone]["amount"]
            order_count += len(list(set(zone_dict[zone]["order_count"])))
            zone_y -= 25
        mycanvas.drawString(380,zone_y-10,"Grand Total")
        mycanvas.drawRightString(560,zone_y-10,str(grand_totals))
        mycanvas.drawRightString(485,zone_y-10,str(order_count))
        mycanvas.line(375,zone_y-15,565,zone_y-15)

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
        
        
        
        mycanvas.save()
        document = {}
        document['file_name'] = file_name
            
    else:
        #     mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)


        # _____________table header_____________#
        y_a4 = 90
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 8)
        mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
        mycanvas.drawString(130, 675+y_a4, 'booth')
        mycanvas.drawString(130, 665+y_a4, 'code')
        mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
        mycanvas.drawString(126 - 35, 665+y_a4, 'name')
        mycanvas.drawString(50, 675+y_a4, 'zone')
        x_axis = 175
        y_axis = 675+y_a4
        line_x_axis = 50 - 40

        # _____________ Product heading _____________#

        products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
        x_adjust = 10
        for product in products:
            product_name = list(product.short_name.split(" "))
            mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
            try:
                mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
            except:
                pass
            if product.short_name == products[-1].short_name:
                x_axis += 50
                mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

            # table top line
            mycanvas.setLineWidth(0)
            mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
            # table bottom line
            mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
            x_axis += 35 + 10
            x_adjust += 10
        mycanvas.setFont('Helvetica-Bold', 8)
        mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
        mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
        mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

        # _____________ Agent_name,Business_code,Product ___________#

        y_axix_agent_booth = 630+y_a4+10
        x_axis_agent_booth = 90 - 40
        y_axis_product = 675+y_a4+10

        for index, business in enumerate(data_dict["booth_sale"], start=1):
            mycanvas.setFont('Helvetica-Bold', 8)
            mycanvas.drawRightString(line_x_axis + 20, y_axix_agent_booth, str(index))
            mycanvas.drawString(x_axis_agent_booth-5, y_axix_agent_booth, str(data_dict["booth_sale"][business]["zone"])[:5])
            mycanvas.drawString(x_axis_agent_booth + 35, y_axix_agent_booth,
                                str(data_dict["booth_sale"][business]["agent_name"]))
            mycanvas.drawString(x_axis_agent_booth + 40 + 40, y_axix_agent_booth,
                                str(business))

            # _________lines_between_agent_name___________#

            mycanvas.line(x_axis_agent_booth - 10, y_axix_agent_booth + 50, x_axis_agent_booth - 10,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 30, y_axix_agent_booth + 50, x_axis_agent_booth + 30,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 70, y_axix_agent_booth + 50, x_axis_agent_booth + 70,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 105, y_axix_agent_booth + 50, x_axis_agent_booth + 105,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 650-x_adjust, y_axix_agent_booth + 50, x_axis_agent_booth + 650-x_adjust,
                          y_axix_agent_booth - 10)

            # _________left_and_right_border___________#

            mycanvas.line(line_x_axis, y_axix_agent_booth + 50, line_x_axis, y_axix_agent_booth - 10)
            mycanvas.line(x_axis-x_adjust-10, y_axix_agent_booth + 50, x_axis-x_adjust-10, y_axix_agent_booth - 10)

            y_axix_agent_booth -= 20
            products_list = []
            x_axis_product = 175
            total_cost = 0

            x_adjust = 10
            for product in products:
                print(product)
                ns = 0
                ws = 0
                if len(data_dict["booth_sale"][business]['ns']) != 0:
                    ns = data_dict["booth_sale"][business]['ns'][product.id]["count"]
                if len(data_dict["booth_sale"][business]['ws']) != 0:
                    ws = data_dict["booth_sale"][business]['ws'][product.id]["count"]

                mycanvas.drawRightString(x_axis_product + 20-x_adjust, y_axis_product - 45, str(round(ns) + round(ws)))

                x_axis_product += 35 + 10
                mycanvas.setLineWidth(0)

                mycanvas.line(x_axis_product - 20-x_adjust, y_axis_product + 5, x_axis_product - 20-x_adjust, y_axis_product - 55)

                x_adjust += 10      
            mycanvas.drawRightString(x_axis_product + 35-x_adjust, y_axis_product - 45,
                                     str(data_dict["booth_sale"][business]["product_total_cost"]))
            mycanvas.drawRightString(x_axis_product + 35 + 35-x_adjust, y_axis_product - 45,
                                     str(data_dict["booth_sale"][business]["time"]))
            y_axis_product -= 20

            # _______________After /24____________#

            if index % 34 == 0:

                mycanvas.line(line_x_axis, y_axis_product - 35, x_axis-x_adjust+25, y_axis_product - 35)
                mycanvas.showPage()

                # ________Head_lines________#

                light_color = 0x9b9999
                dark_color = 0x000000
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.setFillColor(HexColor(dark_color))

                mycanvas.setFont('Helvetica', 12.5)
                mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Helvetica', 12)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
                mycanvas.setFont('Helvetica-Bold', 10)
                name_emp = ""
                for name in list(set(data_dict["counter_details"]["employee_name"])):
                    name_emp += name + ","
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
                mycanvas.drawString(90 + 40, 675+y_a4, 'booth')
                mycanvas.drawString(90 + 40, 665+y_a4, 'code')
                mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
                mycanvas.drawString(126 - 35, 665+y_a4, 'name')
                mycanvas.drawString(50, 675+y_a4, 'zone')
                x_axis = 175
                y_axis = 675+y_a4
                line_x_axis = 50 - 40

                # _____________ Product heading _____________#

                products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
                x_adjust = 10
                for product in products:
                    product_name = list(product.short_name.split(" "))
                    mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
                    try:
                        mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
                    except:
                        pass
                    if product.short_name == products[-1].short_name:
                        x_axis += 50
                        mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

                    # table top line
                    mycanvas.setLineWidth(0)
                    mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
                    # table bottom line
                    mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
                    x_axis += 35 + 10
                    x_adjust += 10
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
                mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
                mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

                # _____________ Agent_name,Business_code,Product ___________#

                y_axix_agent_booth = 630+y_a4+10
                x_axis_agent_booth = 90 - 40
                y_axis_product = 675+y_a4+10

                # _________Grand_total__________#

        x_axis_product = 175
        mycanvas.line(line_x_axis, y_axis_product - 35, x_axis + 25-x_adjust, y_axis_product - 35)
        x_adjust = 10
        for i in range(len(products) + 1):
            mycanvas.line(x_axis_product - 10-x_adjust, y_axis_product, x_axis_product - 10-x_adjust, y_axis_product - 55)
            x_axis_product += 35 + 10
            x_adjust += 10

        mycanvas.line(line_x_axis, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 55)
        mycanvas.line(x_axis-x_adjust+35, y_axis_product - 35, x_axis-x_adjust+35, y_axis_product - 55)
        mycanvas.line(line_x_axis, y_axis_product - 35, line_x_axis, y_axis_product - 55)
        mycanvas.drawString(line_x_axis + 35, y_axis_product - 48, "Total Packets")
        mycanvas.drawRightString(x_axis_product-x_adjust+10, y_axis_product - 68, str(data_dict["grand_total"]))

        mycanvas.line(x_axis-x_adjust+35, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 75)
        mycanvas.line(line_x_axis, y_axis_product - 55, line_x_axis, y_axis_product - 75)
        mycanvas.line(x_axis - 60-x_adjust+10, y_axis_product - 55, x_axis - 60-x_adjust+10, y_axis_product - 75)
        mycanvas.line(line_x_axis, y_axis_product - 75, x_axis-x_adjust+35, y_axis_product - 75)
        mycanvas.drawString(x_axis_product - 125-x_adjust+10, y_axis_product - 68, 'Grand Total Rs.')
        mycanvas.setFont('Helvetica-Bold', 12)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')

        grand_total = data_dict["grand_total"]
        grand_total = f"{grand_total:,.2f}"

        mycanvas.setFont('Helvetica-Bold', 11)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(15, y_axis_product - 98, 'The total money collected by counter ' + str(
            data_dict["counter_details"]["counter_name"]) + ' on ')

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawString(360, y_axis_product - 98,
                            str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

        x_axis_product += 35
        x_adjust = 10
        for product in products:
            try:
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawRightString(line_x_axis + 145 + 40-x_adjust, y_axis_product - 48,
                                         str(int(data_dict["product_total_count"][product.id]["count"])))
                line_x_axis += 35 + 10
                x_adjust += 10
            except:
                pass

        mycanvas.showPage()

        # ________Head_lines_for_counter_wise_Total________#

        light_color = 0x9b9999
        dark_color = 0x000000
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.setFillColor(HexColor(dark_color))
        y_a4 = 80

        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 665 + 20+y_a4, "Milk Agents")
        mycanvas.line(300-50, 661 + 20+y_a4, 400-50, 661 + 20+y_a4)

        # table header

        x_adjust = 50
        y_axis_product_total = 645 - 20 + 20 +y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 668 - 20 + 20+y_a4
        y_head = 655 - 20 + 20+y_a4

        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        products_obj = list(Product.objects.filter(is_active=True, group_id__in=[1, 3]).order_by('display_ordinal'))

        index = 0
        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_agent
        y_a4 = 90
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 420 + 20+y_a4, "Curd Agents")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-x_adjust, 416 + 20+y_a4, 400-x_adjust, 416 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, group_id=2).order_by('display_ordinal'))

        y_axis_product_total = 405 - 25 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 428 - 25 + 20+y_a4
        y_head = 415 - 25 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))
            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_wholesale
        y_a4 = 100
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 195 + 20+y_a4, "Curd Wholesale")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-50, 191 + 20+y_a4, 400-50, 191 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, id__in=[25, 7, 10]).order_by('display_ordinal'))

        y_axis_product_total = 155 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 178 + 20+y_a4
        y_head = 165 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        wscost = 0
        wsliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["product_total_count"][product.id]["ws_count"]
            wsliter += round(Decimal(data_dict["product_total_count"][product.id]["ws_litre"]), 3)
            wscost += round(Decimal(data_dict["product_total_count"][product.id]["ws_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["product_total_count"][product.id]["ws_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ws_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ws_cost"]), 2)))

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 20, str(wsliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(wscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        grand_total = data_dict["grand_total"]
        grand_total = f"{grand_total:,.2f}"

        mycanvas.setFont('Helvetica-Bold', 11)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(15, y_axis_product_total - 58, 'The total money collected by counter ' + str(
            data_dict["counter_details"]["counter_name"]) + ' on ')

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawString(360, y_axis_product_total - 58,
                            str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

        words = num2words(round(data_dict["grand_total"]), lang='en_IN')
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawString(15, y_axis_product_total - 58 - 20 - 5,
                                   "Total Amount Collected " + "  Rupees.  " + str(words.upper()) + " " + "Only")

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
        
        
        mycanvas.showPage()
        if data_dict["counter_details"]["counter_name"] != 'Online':
        #for Challa
            challan_y = 730
            x_ad = 120
            y_ad = 5
            mycanvas.setFont('Helvetica-Bold', 12)
            mycanvas.drawCentredString(300-x_ad,challan_y,str(str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))))
            mycanvas.drawCentredString(300-x_ad,challan_y-20,"COINWAR")

            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawRightString(190-x_ad,challan_y-60+y_ad,"2000")
            mycanvas.drawRightString(220-x_ad,challan_y-60+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-80+y_ad,"500")
            mycanvas.drawRightString(220-x_ad,challan_y-80+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-100+y_ad,"200")
            mycanvas.drawRightString(220-x_ad,challan_y-100+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-120+y_ad,"100")
            mycanvas.drawRightString(220-x_ad,challan_y-120+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-140+y_ad,"50")
            mycanvas.drawRightString(220-x_ad,challan_y-140+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-160+y_ad,"20")
            mycanvas.drawRightString(220-x_ad,challan_y-160+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-180+y_ad,"10")
            mycanvas.drawRightString(220-x_ad,challan_y-180+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-200+y_ad,"1")
            mycanvas.drawRightString(220-x_ad,challan_y-200+y_ad,"X")

            mycanvas.drawCentredString(215,challan_y-220+y_ad,"Total")

            mycanvas.drawString(150-x_ad,challan_y-240+y_ad,"Card Amount")
            mycanvas.drawString(150-x_ad,challan_y-260+y_ad,"MISC")
            mycanvas.drawString(150-x_ad,challan_y-280+y_ad,"Grand Total")
            mycanvas.drawString(150-x_ad,challan_y-300+y_ad,"Debit Card")
            mycanvas.drawString(150-x_ad,challan_y-320+y_ad,"Total")

            #line vertical
            mycanvas.line(300-x_ad,challan_y-24,300-x_ad,challan_y-325)
            mycanvas.line(140-x_ad,challan_y+14,140-x_ad,challan_y-325)
            mycanvas.line(460-x_ad,challan_y+14,460-x_ad,challan_y-325)

            mycanvas.line(200-x_ad,challan_y-24,200-x_ad,challan_y-205+y_ad)
            mycanvas.line(230-x_ad,challan_y-24,230-x_ad,challan_y-205+y_ad)

            #top & bottom line
            mycanvas.line(140-x_ad,challan_y+14,460-x_ad,challan_y+14)
            mycanvas.line(140-x_ad,challan_y-5,460-x_ad,challan_y-5)
            mycanvas.line(140-x_ad,challan_y-24,460-x_ad,challan_y-24)
            mycanvas.line(140-x_ad,challan_y-40,460-x_ad,challan_y-40)
            mycanvas.line(140-x_ad,challan_y-325,460-x_ad,challan_y-325)

            #lines between rows
            for i in range(13):
                mycanvas.line(140-x_ad,challan_y-65+y_ad,460-x_ad,challan_y-65+y_ad)
                challan_y -= 20

            #for_full_total
            zone_y = 730-300
            grand_totals = 0
            mycanvas.setFont('Helvetica-Bold', 12)
            mycanvas.line(375,zone_y+35,565,zone_y+35)
            mycanvas.drawCentredString(470,zone_y+17,"Total Amount Details")
            mycanvas.line(375,zone_y+5,565,zone_y+5)
            mycanvas.setFont('Helvetica', 12)
            data_list = ['Bank','Swiping Machine','R.S Puram','Total']
            for zone in data_list:
                mycanvas.drawString(380-3,zone_y-10,str(zone))
        #         mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]))
                mycanvas.line(375,zone_y-20,565,zone_y-20)
                mycanvas.line(470,zone_y+5,470,zone_y-20)
                mycanvas.line(375,zone_y+35,375,zone_y-20)
                mycanvas.line(565,zone_y+35,565,zone_y-20)
        #         grand_totals += zone_dict[zone]
                zone_y -= 25
        
    
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        zone_y = 690
        #for_zonewise_total
        grand_totals = 0
        order_count = 0
        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.line(375,zone_y+55,565,zone_y+55)
        mycanvas.drawCentredString(470,zone_y+37,"Zone Wise Sale Details")
        mycanvas.line(375,zone_y+25,565,zone_y+25)
        mycanvas.drawString(383,zone_y+10,"Sale For")
        mycanvas.drawString(448,zone_y+10,"Count")
        mycanvas.drawString(505,zone_y+10,"Amount")
        mycanvas.line(375,zone_y+5,565,zone_y+5)
        mycanvas.setFont('Helvetica', 10)

        for zone in zone_dict:
            print(zone)
            mycanvas.drawString(380,zone_y-10,str(zone))
            mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]["amount"]))
            mycanvas.drawRightString(485,zone_y-10,str(len(list(set(zone_dict[zone]["order_count"])))))
            mycanvas.line(375,zone_y-20,565,zone_y-20)
            mycanvas.line(440,zone_y+25,440,zone_y-40)
            mycanvas.line(490,zone_y+25,490,zone_y-40)
            mycanvas.line(375,zone_y+55,375,zone_y-40)
            mycanvas.line(565,zone_y+55,565,zone_y-40)
            grand_totals += zone_dict[zone]["amount"]
            order_count += len(list(set(zone_dict[zone]["order_count"])))
            zone_y -= 25
        mycanvas.drawString(380,zone_y-10,"Grand Total")
        mycanvas.drawRightString(560,zone_y-10,str(grand_totals))
        mycanvas.drawRightString(485,zone_y-10,str(order_count))
        mycanvas.line(375,zone_y-15,565,zone_y-15)

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
        
        

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
def serve_counter_order_details_for_agent_delivery(request):
    counter_id = request.data['selected_counter_id']
    date = request.data['selected_date']
    print(date)
    next_date = datetime.datetime.strptime(date,'%Y-%m-%d')
    next_date = next_date + timedelta(days=1)
    next_date = str(next_date)[:10]
    user_name = request.user.first_name
    if counter_id == 'online':
        ws_sale_group_obj = SaleGroup.objects.filter(date=next_date, ordered_via_id__in=[1, 3],
                                                     business__business_type_id=9).order_by('id')
        ns_sale_group_obj = SaleGroup.objects.filter(date=next_date, ordered_via_id__in=[1, 3]).exclude(
            business__business_type_id=9).order_by('id')       
        counter_name = 'Online'
    else:
        employee_trace_ids = list(
            CounterEmployeeTraceMap.objects.filter(counter_id=counter_id, collection_date=date, counteremployeetracesalegroupmap__sale_group__date=next_date).values_list('id',
                                                                                                               flat=True))
        employee_trace_sale_group_obj = list(
            CounterEmployeeTraceSaleGroupMap.objects.filter(
                counter_employee_trace_id__in=employee_trace_ids).values_list(
                'sale_group', flat=True))
        ws_sale_group_obj = SaleGroup.objects.filter(id__in=employee_trace_sale_group_obj,
                                                     business__business_type_id=9).order_by('id')
        ns_sale_group_obj = SaleGroup.objects.filter(id__in=employee_trace_sale_group_obj).exclude(
            business__business_type_id=9).order_by('id')
        counter_name = Counter.objects.get(id=counter_id).name


    ws_sale_obj = Sale.objects.filter(sale_group_id__in=ws_sale_group_obj, product__is_active=True).order_by(
        'sale_group_id')
    ns_sale_obj = Sale.objects.filter(sale_group_id__in=ns_sale_group_obj, product__is_active=True).order_by(
        'sale_group_id')

    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
    
    zone_dict = {}
    for zone in Zone.objects.all().exclude(id__in=[11,12,13,15]):
        if zone.name not in zone_dict:
            zone_dict[zone.name] = {
                "amount":0,
                "order_count":[],
            }
    online_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=1, order_category_id=1).values_list('business_type_id', flat=True))

    for sale_group in ws_sale_group_obj:
        if sale_group.business.business_type_id in online_business_type_ids:
            if sale_group.zone.name in zone_dict:
                zone_dict[sale_group.zone.name]['order_count'].append(sale_group.business_id)
                zone_dict[sale_group.zone.name]['amount'] += sale_group.total_cost

    # if counter_id != "online":
    for sale_group in ns_sale_group_obj:
        if sale_group.business.business_type_id in online_business_type_ids:
            if sale_group.zone.name in zone_dict:
                zone_dict[sale_group.zone.name]['order_count'].append(sale_group.business_id)
                zone_dict[sale_group.zone.name]['amount'] += sale_group.total_cost
    
    print(zone_dict)
    
    
    if counter_id == "online":
        data_dict ={
            "counter_details": {
                "counter_id": counter_id,
                "counter_name": counter_name,
                "employee_name": [],
                "date": date
            },
            "cash":{
                "grand_total": 0,
                "booth_sale": {},
                "product_total_count": {}
            },
            "cridet":{
                "grand_total": 0,
                "booth_sale": {},
                "product_total_count": {}
            }
        }
    else:
        data_dict = {
            "grand_total": 0,
            "counter_details": {
                "counter_id": counter_id,
                "counter_name": counter_name,
                "employee_name": [],
                "date": date
            },
            "booth_sale": {},
            "product_total_count": {}
        }
    if counter_id == 'online':
        data_dict["counter_details"]["employee_name"].append('-')
    else:
        for employee_trace_id in employee_trace_ids:
            employee_name = CounterEmployeeTraceMap.objects.get(
                id=employee_trace_id).employee.user_profile.user.first_name
            data_dict["counter_details"]["employee_name"].append(employee_name)
            
    if counter_id == 'online':
        for product in products:
            if not product.id in data_dict["cash"]["product_total_count"]:
                data_dict["cash"]["product_total_count"][product.id] = {
                    "count": 0,
                    "ns_litre": 0,
                    "ns_cost": 0,
                    "ns_count": 0,
                    "ws_litre": 0,
                    "ws_cost": 0,
                    "ws_count": 0,
                    "total_liter": 0
                }
            if not product.id in data_dict["cridet"]["product_total_count"]:
                data_dict["cridet"]["product_total_count"][product.id] = {
                    "count": 0,
                    "ns_litre": 0,
                    "ns_cost": 0,
                    "ns_count": 0,
                    "ws_litre": 0,
                    "ws_cost": 0,
                    "ws_count": 0,
                    "total_liter": 0
                }
    else:
        for product in products:
            if not product.id in data_dict["product_total_count"]:
                    data_dict["product_total_count"][product.id] = {
                        "count": 0,
                        "ns_litre": 0,
                        "ns_cost": 0,
                        "ns_count": 0,
                        "ws_litre": 0,
                        "ws_cost": 0,
                        "ws_count": 0,
                        "total_liter": 0
                    }

    for ns in ns_sale_group_obj:
        if counter_id == "online":
            ns_sale = Sale.objects.filter(sale_group_id=ns.id, product__is_active=True)
            if ns.business.business_type_id in online_business_type_ids:
                time = ns.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ns.business.code in data_dict["cash"]["booth_sale"]:
                    data_dict["cash"]["booth_sale"][ns.business.code] = {
                        "date":ns.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ns.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(
                            business_id=ns.business.id).agent.first_name + " "+ BusinessAgentMap.objects.get(
                            business_id=ns.business.id).agent.last_name)[:5],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
            else:
                time = ns.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ns.business.code in data_dict["cridet"]["booth_sale"]:
                    data_dict["cridet"]["booth_sale"][ns.business.code] = {
                        "date":ns.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ns.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(business_id=ns.business.id).agent.first_name+" "+BusinessAgentMap.objects.get(business_id=ns.business.id).agent.last_name)[:6],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
                    
            for sale in ns_sale:
                if sale.sale_group.business.business_type_id in online_business_type_ids:
                    for product in products:
                        if not product.id in data_dict["cash"]["booth_sale"][ns.business.code]["ns"]:
                            data_dict["cash"]["booth_sale"][ns.business.code]["ns"][product.id] = {
                                "count": 0,
                                "cost": 0
                            }

                    data_dict["cash"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["cost"] += sale.cost
                    data_dict["cash"]["booth_sale"][ns.business.code]["product_total_cost"] += sale.cost

                    data_dict["cash"]["product_total_count"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ns_count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ns_litre"] += sale.count * float(
                        sale.product.quantity / 1000)
                    data_dict["cash"]["product_total_count"][sale.product_id]["ns_cost"] += sale.cost
                    data_dict["cash"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                        sale.product.quantity / 1000)

                    data_dict["cash"]["grand_total"] += sale.cost
                # else:
                #     for product in products:
                #         if not product.id in data_dict["cridet"]["booth_sale"][ns.business.code]["ns"]:
                #             data_dict["cridet"]["booth_sale"][ns.business.code]["ns"][product.id] = {
                #                 "count": 0,
                #                 "cost": 0
                #             }

                #     data_dict["cridet"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["count"] += sale.count
                #     data_dict["cridet"]["booth_sale"][ns.business.code]["ns"][sale.product_id]["cost"] += sale.cost
                #     data_dict["cridet"]["booth_sale"][ns.business.code]["product_total_cost"] += sale.cost

                #     data_dict["cridet"]["product_total_count"][sale.product_id]["count"] += sale.count
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["ns_count"] += sale.count
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["ns_litre"] += sale.count * float(
                #         sale.product.quantity / 1000)
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["ns_cost"] += sale.cost
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                #         sale.product.quantity / 1000)

                #     data_dict["cridet"]["grand_total"] += sale.cost
            
        else:
            ns_sale = Sale.objects.filter(sale_group_id=ns.id, product__is_active=True)
            time = ns.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")
            if not ns.business.code in data_dict["booth_sale"]:
                data_dict["booth_sale"][ns.business.code] = {
                    "date":ns.date.strftime("%d-%b"),
                    "time": time_created,
                    "zone": ns.business.zone.name,
                    "agent_name":str(BusinessAgentMap.objects.get(business_id=ns.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ns.business.id).agent.last_name)[:5],
                    "product_total_cost": 0,
                    "ns": {},
                    "ws": {}
                }
            
            for sale in ns_sale:
                for product in products:
                    if not product.id in data_dict["booth_sale"][ns.business.code]["ns"]:
                        data_dict["booth_sale"][ns.business.code]["ns"][product.id] = {
                            "count": 0,
                            "cost": 0
                        }

                data_dict["booth_sale"][ns.business.code]["ns"][sale.product_id]["count"] += sale.count
                data_dict["booth_sale"][ns.business.code]["ns"][sale.product_id]["cost"] += sale.cost
                data_dict["booth_sale"][ns.business.code]["product_total_cost"] += sale.cost

                data_dict["product_total_count"][sale.product_id]["count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ns_count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ns_litre"] += sale.count * float(
                    sale.product.quantity / 1000)
                data_dict["product_total_count"][sale.product_id]["ns_cost"] += sale.cost
                data_dict["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                    sale.product.quantity / 1000)

                data_dict["grand_total"] += sale.cost

    for ws in ws_sale_group_obj:
        if counter_id == "online":
            ws_sale = Sale.objects.filter(sale_group_id=ws.id, product__is_active=True)
            if ws.business.business_type_id in online_business_type_ids:
                time = ws.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ws.business.code in data_dict["cash"]["booth_sale"]:
                    data_dict["cash"]["booth_sale"][ws.business.code] = {
                        "date":ws.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ws.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(business_id=ws.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ws.business.id).agent.last_name)[:5],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
            else:
                time = ws.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ws.business.code in data_dict["cridet"]["booth_sale"]:
                    data_dict["cridet"]["booth_sale"][ws.business.code] = {
                        "date":ws.date.strftime("%d-%b"),
                        "time": time_created,
                        "zone": ws.business.zone.name,
                        "agent_name": str(BusinessAgentMap.objects.get(business_id=ws.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ws.business.id).agent.last_name)[:5],
                        "product_total_cost": 0,
                        "ns": {},
                        "ws": {}
                    }
                    
            for sale in ws_sale:
                if sale.sale_group.business.business_type_id in online_business_type_ids:
                    for product in products:
                        if not product.id in data_dict["cash"]["booth_sale"][ws.business.code]["ws"]:
                            data_dict["cash"]["booth_sale"][ws.business.code]["ws"][product.id] = {
                                "count": 0,
                                "cost": 0
                            }

                    data_dict["cash"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["cost"] += sale.cost
                    data_dict["cash"]["booth_sale"][ws.business.code]["product_total_cost"] += sale.cost

                    data_dict["cash"]["product_total_count"][sale.product_id]["count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ws_count"] += sale.count
                    data_dict["cash"]["product_total_count"][sale.product_id]["ws_litre"] += sale.count * float(
                        sale.product.quantity / 1000)
                    data_dict["cash"]["product_total_count"][sale.product_id]["ws_cost"] += sale.cost
                    data_dict["cash"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                        sale.product.quantity / 1000)

                    data_dict["cash"]["grand_total"] += sale.cost
                # else:
                #     for product in products:
                #         if not product.id in data_dict["cridet"]["booth_sale"][ws.business.code]["ws"]:
                #             data_dict["cridet"]["booth_sale"][ws.business.code]["ws"][product.id] = {
                #                 "count": 0,
                #                 "cost": 0
                #             }

                #     data_dict["cridet"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["count"] += sale.count
                #     data_dict["cridet"]["booth_sale"][ws.business.code]["ws"][sale.product_id]["cost"] += sale.cost
                #     data_dict["cridet"]["booth_sale"][ws.business.code]["product_total_cost"] += sale.cost

                #     data_dict["cridet"]["product_total_count"][sale.product_id]["count"] += sale.count
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["ws_count"] += sale.count
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["ws_litre"] += sale.count * float(
                #         sale.product.quantity / 1000)
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["ws_cost"] += sale.cost
                #     data_dict["cridet"]["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                #         sale.product.quantity / 1000)

                #     data_dict["cridet"]["grand_total"] += sale.cost
            
            
        else:
            ws_sale = Sale.objects.filter(sale_group_id=ws.id, product__is_active=True)
            time = ws.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")
            if not ws.business.code in data_dict["booth_sale"]:
                data_dict["booth_sale"][ws.business.code] = {
                    "date":ws.date.strftime("%d-%b"),
                    "time": time_created,
                    "zone": ws.business.zone.name,
                    "agent_name": str(BusinessAgentMap.objects.get(business_id=ws.business.id).agent.first_name + " " + BusinessAgentMap.objects.get(business_id=ws.business.id).agent.last_name)[:5],
                    "product_total_cost": 0,
                    "ns": {},
                    "ws": {}
                } 
                
                
            for sale in ws_sale:
                for product in products:
                    if not product.id in data_dict["booth_sale"][ws.business.code]["ws"]:
                        data_dict["booth_sale"][ws.business.code]["ws"][product.id] = {
                            "count": 0,
                            "cost": 0
                        }

                data_dict["booth_sale"][ws.business.code]["ws"][sale.product_id]["count"] += sale.count
                data_dict["booth_sale"][ws.business.code]["ws"][sale.product_id]["cost"] += sale.cost
                data_dict["booth_sale"][ws.business.code]["product_total_cost"] += sale.cost

                data_dict["product_total_count"][sale.product_id]["count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ws_count"] += sale.count
                data_dict["product_total_count"][sale.product_id]["ws_litre"] += sale.count * float(
                    sale.product.quantity / 1000)
                data_dict["product_total_count"][sale.product_id]["ws_cost"] += sale.cost
                data_dict["product_total_count"][sale.product_id]["total_liter"] += sale.count * float(
                    sale.product.quantity / 1000)

                data_dict["grand_total"] += sale.cost

    data_dict['user_name'] = user_name
    data = generate_sale_pdf_for_agent_order_delivery(data_dict, date,zone_dict)
    return Response(data=data, status=status.HTTP_200_OK)


def generate_sale_pdf_for_agent_order_delivery(data_dict, date,zone_dict):
    new_date = date
    # datetime.datetime.strftime(date, '%d-%b-%Y')
    file_name = str(new_date) + '_' + str(
        data_dict["counter_details"]["counter_name"]) + '_' + 'daily_counter_report_agent_sale' + '.pdf'
#     file_path = os.path.join('static/media/', file_name)
    file_path = os.path.join('static/media/counter_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    # ________Head_lines________#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
    
    #-----------------------------------------------------For_online_order--------------------------------------------------------------#
    if data_dict["counter_details"]["counter_name"] == "Online":
        counter = "Cash"
        for data in data_dict:
            print(data)
            if data == 'counter_details' or data == "user_name":
                pass
            else:
                #     mycanvas.setStrokeColor(colors.lightgrey)
                mycanvas.setFont('Helvetica', 12.5)
                mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Helvetica', 12)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
                mycanvas.setFont('Helvetica-Bold', 10)
                name_emp = ""
                for name in list(set(data_dict["counter_details"]["employee_name"])):
                    name_emp += name + ","
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)


                # _____________table header_____________#
                y_a4 = 90
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
                mycanvas.drawString(130, 675+y_a4, 'booth')
                mycanvas.drawString(130, 665+y_a4, 'code')
                mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
                mycanvas.drawString(126 - 35, 665+y_a4, 'name')
                mycanvas.drawString(50, 675+y_a4, 'zone')
                x_axis = 175
                y_axis = 675+y_a4
                line_x_axis = 50 - 40

                # _____________ Product heading _____________#

                products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
                x_adjust = 10
                for product in products:
                    product_name = list(product.short_name.split(" "))
                    mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
                    try:
                        mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
                    except:
                        pass
                    if product.short_name == products[-1].short_name:
                        x_axis += 50
                        mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

                    # table top line
                    mycanvas.setLineWidth(0)
                    mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
                    # table bottom line
                    mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
                    x_axis += 35 + 10
                    x_adjust += 10
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
                mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
                mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

                # _____________ Agent_name,Business_code,Product ___________#

                y_axix_agent_booth = 630+y_a4+10
                x_axis_agent_booth = 90 - 40
                y_axis_product = 675+y_a4+10

                for index, business in enumerate(data_dict[data]["booth_sale"], start=1):
                    mycanvas.setFont('Helvetica-Bold', 8)
                    mycanvas.drawRightString(line_x_axis + 20, y_axix_agent_booth, str(index))
                    mycanvas.drawString(x_axis_agent_booth-5, y_axix_agent_booth, str(data_dict[data]["booth_sale"][business]["zone"])[:5])
                    mycanvas.drawString(x_axis_agent_booth + 35, y_axix_agent_booth,
                                        str(data_dict[data]["booth_sale"][business]["agent_name"])[:5])
                    mycanvas.drawString(x_axis_agent_booth + 40 + 40, y_axix_agent_booth,
                                        str(business))

                    # _________lines_between_agent_name___________#

                    mycanvas.line(x_axis_agent_booth - 10, y_axix_agent_booth + 50, x_axis_agent_booth - 10,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 30, y_axix_agent_booth + 50, x_axis_agent_booth + 30,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 70, y_axix_agent_booth + 50, x_axis_agent_booth + 70,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 105, y_axix_agent_booth + 50, x_axis_agent_booth + 105,
                                  y_axix_agent_booth - 10)
                    mycanvas.line(x_axis_agent_booth + 650-x_adjust, y_axix_agent_booth + 50, x_axis_agent_booth + 650-x_adjust,
                                  y_axix_agent_booth - 10)

                    # _________left_and_right_border___________#

                    mycanvas.line(line_x_axis, y_axix_agent_booth + 50, line_x_axis, y_axix_agent_booth - 10)
                    mycanvas.line(x_axis-x_adjust-10, y_axix_agent_booth + 50, x_axis-x_adjust-10, y_axix_agent_booth - 10)

                    y_axix_agent_booth -= 20
                    products_list = []
                    x_axis_product = 175
                    total_cost = 0

                    x_adjust = 10
                    for product in products:
                        print(product)
                        ns = 0
                        ws = 0
                        if len(data_dict[data]["booth_sale"][business]['ns']) != 0:
                            ns = data_dict[data]["booth_sale"][business]['ns'][product.id]["count"]
                        if len(data_dict[data]["booth_sale"][business]['ws']) != 0:
                            ws = data_dict[data]["booth_sale"][business]['ws'][product.id]["count"]

                        mycanvas.drawRightString(x_axis_product + 20-x_adjust, y_axis_product - 45, str(round(ns) + round(ws)))

                        x_axis_product += 35 + 10
                        mycanvas.setLineWidth(0)

                        mycanvas.line(x_axis_product - 20-x_adjust, y_axis_product + 5, x_axis_product - 20-x_adjust, y_axis_product - 55)

                        x_adjust += 10      
                    mycanvas.drawRightString(x_axis_product + 35-x_adjust, y_axis_product - 45,
                                             str(data_dict[data]["booth_sale"][business]["product_total_cost"]))
                    mycanvas.drawRightString(x_axis_product + 35 + 35-x_adjust, y_axis_product - 45,
                                             str(data_dict[data]["booth_sale"][business]["time"]))
                    y_axis_product -= 20

                    # _______________After /24____________#

                    if index % 34 == 0:

                        mycanvas.line(line_x_axis, y_axis_product - 35, x_axis-x_adjust+25, y_axis_product - 35)
                        mycanvas.showPage()

                        # ________Head_lines________#

                        light_color = 0x9b9999
                        dark_color = 0x000000
                        mycanvas.setFillColor(HexColor(light_color))
                        mycanvas.setFillColor(HexColor(dark_color))

                        mycanvas.setFont('Helvetica', 12.5)
                        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                        mycanvas.setFont('Helvetica', 12)
                        mycanvas.setFillColor(HexColor(dark_color))
                        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
                        mycanvas.setFont('Helvetica-Bold', 10)
                        name_emp = ""
                        for name in list(set(data_dict["counter_details"]["employee_name"])):
                            name_emp += name + ","
                        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

                        mycanvas.setFillColor(HexColor(dark_color))
                        mycanvas.setFont('Helvetica-Bold', 8)
                        mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
                        mycanvas.drawString(90 + 40, 675+y_a4, 'booth')
                        mycanvas.drawString(90 + 40, 665+y_a4, 'code')
                        mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
                        mycanvas.drawString(126 - 35, 665+y_a4, 'name')
                        mycanvas.drawString(50, 675+y_a4, 'zone')
                        x_axis = 175
                        y_axis = 675+y_a4
                        line_x_axis = 50 - 40

                        # _____________ Product heading _____________#

                        products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
                        x_adjust = 10
                        for product in products:
                            product_name = list(product.short_name.split(" "))
                            mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
                            try:
                                mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
                            except:
                                pass
                            if product.short_name == products[-1].short_name:
                                x_axis += 50
                                mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

                            # table top line
                            mycanvas.setLineWidth(0)
                            mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
                            # table bottom line
                            mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
                            x_axis += 35 + 10
                            x_adjust += 10
                        mycanvas.setFont('Helvetica-Bold', 8)
                        mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
                        mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
                        mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

                        # _____________ Agent_name,Business_code,Product ___________#

                        y_axix_agent_booth = 630+y_a4+10
                        x_axis_agent_booth = 90 - 40
                        y_axis_product = 675+y_a4+10

                        # _________Grand_total__________#

                x_axis_product = 175
                mycanvas.line(line_x_axis, y_axis_product - 35, x_axis + 25-x_adjust, y_axis_product - 35)
                x_adjust = 10
                for i in range(len(products) + 1):
                    mycanvas.line(x_axis_product - 10-x_adjust, y_axis_product, x_axis_product - 10-x_adjust, y_axis_product - 55)
                    x_axis_product += 35 + 10
                    x_adjust += 10

                mycanvas.line(line_x_axis, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 55)
                mycanvas.line(x_axis-x_adjust+35, y_axis_product - 35, x_axis-x_adjust+35, y_axis_product - 55)
                mycanvas.line(line_x_axis, y_axis_product - 35, line_x_axis, y_axis_product - 55)
                mycanvas.drawString(line_x_axis + 35, y_axis_product - 48, "Total Packets")
                mycanvas.drawRightString(x_axis_product-x_adjust+10, y_axis_product - 68, str(data_dict[data]["grand_total"]))

                mycanvas.line(x_axis-x_adjust+35, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 75)
                mycanvas.line(line_x_axis, y_axis_product - 55, line_x_axis, y_axis_product - 75)
                mycanvas.line(x_axis - 60-x_adjust+10, y_axis_product - 55, x_axis - 60-x_adjust+10, y_axis_product - 75)
                mycanvas.line(line_x_axis, y_axis_product - 75, x_axis-x_adjust+35, y_axis_product - 75)
                mycanvas.drawString(x_axis_product - 125-x_adjust+10, y_axis_product - 68, 'Grand Total Rs.')
                mycanvas.setFont('Helvetica-Bold', 12)
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')

                grand_total = data_dict[data]["grand_total"]
                grand_total = f"{grand_total:,.2f}"

                mycanvas.setFont('Helvetica-Bold', 11)
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                mycanvas.drawString(15, y_axis_product - 98, 'The total money collected by counter ' + str(
                    data_dict["counter_details"]["counter_name"])+"("+str(counter)+")" + ' on ')

                mycanvas.setFont('Helvetica-Bold', 13)
                mycanvas.drawString(360, y_axis_product - 98,
                                    str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

                x_axis_product += 35
                x_adjust = 10
                for product in products:
                    try:
                        mycanvas.setFont('Helvetica-Bold', 8)
                        mycanvas.drawRightString(line_x_axis + 145 + 40-x_adjust, y_axis_product - 48,
                                                 str(int(data_dict[data]["product_total_count"][product.id]["count"])))
                        line_x_axis += 35 + 10
                        x_adjust += 10
                    except:
                        pass

                mycanvas.showPage()
                counter = "Credit"
                break
                
        # ________Head_lines_for_counter_wise_Total________#

        light_color = 0x9b9999
        dark_color = 0x000000
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.setFillColor(HexColor(dark_color))
        y_a4 = 80

        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 665 + 20+y_a4, "Milk Agents")
        mycanvas.line(300-50, 661 + 20+y_a4, 400-50, 661 + 20+y_a4)

        # table header

        x_adjust = 50
        y_axis_product_total = 645 - 20 + 20 +y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 668 - 20 + 20+y_a4
        y_head = 655 - 20 + 20+y_a4

        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        products_obj = list(Product.objects.filter(is_active=True, group_id__in=[1, 3]).order_by('display_ordinal'))

        index = 0
        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["cash"]["product_total_count"][product.id]["ns_count"] + data_dict["cridet"]["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["cash"]["product_total_count"][product.id]["ns_count"] + data_dict["cridet"]["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_agent
        y_a4 = 90
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 420 + 20+y_a4, "Curd Agents")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-x_adjust, 416 + 20+y_a4, 400-x_adjust, 416 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, group_id=2).order_by('display_ordinal'))

        y_axis_product_total = 405 - 25 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 428 - 25 + 20+y_a4
        y_head = 415 - 25 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["cash"]["product_total_count"][product.id]["ns_count"] + data_dict["cridet"]["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))
            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["cash"]["product_total_count"][product.id]["ns_count"]+data_dict["cridet"]["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_litre"]+data_dict["cridet"]["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ns_cost"]+data_dict["cridet"]["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_wholesale
        y_a4 = 100
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 195 + 20+y_a4, "Curd Wholesale")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-50, 191 + 20+y_a4, 400-50, 191 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, id__in=[25, 7, 10]).order_by('display_ordinal'))

        y_axis_product_total = 155 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 178 + 20+y_a4
        y_head = 165 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        wscost = 0
        wsliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["cash"]["product_total_count"][product.id]["ws_count"] + data_dict["cridet"]["product_total_count"][product.id]["ws_count"]
            wsliter += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ws_litre"]), 3)
            wscost += round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ws_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["cash"]["product_total_count"][product.id]["ws_count"] + data_dict["cridet"]["product_total_count"][product.id]["ws_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_litre"] + data_dict["cridet"]["product_total_count"][product.id]["ws_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["cash"]["product_total_count"][product.id]["ws_cost"] + data_dict["cridet"]["product_total_count"][product.id]["ws_cost"]), 2)))

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 20, str(wsliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(wscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        grand_total = data_dict["cash"]["grand_total"] + data_dict["cridet"]["grand_total"]
        grand_total = f"{grand_total:,.2f}"

        mycanvas.setFont('Helvetica-Bold', 11)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(15, y_axis_product_total - 58, 'The total money collected by counter ' + str(
            data_dict["counter_details"]["counter_name"]) + ' on ')

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawString(360, y_axis_product_total - 58,
                            str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

        words = num2words(round(data_dict["cash"]["grand_total"] + data_dict["cridet"]["grand_total"]), lang='en_IN')
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawString(15, y_axis_product_total - 58 - 20 - 5,
                                   "Total Amount Collected " + "  Rupees.  " + str(words.upper()) + " " + "Only")

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))

        
        mycanvas.showPage()
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        zone_y = 690
        #for_zonewise_total
        grand_totals = 0
        order_count = 0
        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.line(375,zone_y+55,565,zone_y+55)
        mycanvas.drawCentredString(470,zone_y+37,"Zone Wise Sale Details")
        mycanvas.line(375,zone_y+25,565,zone_y+25)
        mycanvas.drawString(383,zone_y+10,"Sale For")
        mycanvas.drawString(448,zone_y+10,"Count")
        mycanvas.drawString(505,zone_y+10,"Amount")
        mycanvas.line(375,zone_y+5,565,zone_y+5)
        mycanvas.setFont('Helvetica', 10)

        for zone in zone_dict:
            print(zone)
            mycanvas.drawString(380,zone_y-10,str(zone))
            mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]["amount"]))
            mycanvas.drawRightString(485,zone_y-10,str(len(list(set(zone_dict[zone]["order_count"])))))
            mycanvas.line(375,zone_y-20,565,zone_y-20)
            mycanvas.line(440,zone_y+25,440,zone_y-40)
            mycanvas.line(490,zone_y+25,490,zone_y-40)
            mycanvas.line(375,zone_y+55,375,zone_y-40)
            mycanvas.line(565,zone_y+55,565,zone_y-40)
            grand_totals += zone_dict[zone]["amount"]
            order_count += len(list(set(zone_dict[zone]["order_count"])))
            zone_y -= 25
        mycanvas.drawString(380,zone_y-10,"Grand Total")
        mycanvas.drawRightString(560,zone_y-10,str(grand_totals))
        mycanvas.drawRightString(485,zone_y-10,str(order_count))
        mycanvas.line(375,zone_y-15,565,zone_y-15)

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
        
        
        
        mycanvas.save()
        document = {}
        document['file_name'] = file_name
            
    else:
        #     mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)


        # _____________table header_____________#
        y_a4 = 90
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 8)
        mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
        mycanvas.drawString(130, 675+y_a4, 'booth')
        mycanvas.drawString(130, 665+y_a4, 'code')
        mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
        mycanvas.drawString(126 - 35, 665+y_a4, 'name')
        mycanvas.drawString(50, 675+y_a4, 'zone')
        x_axis = 175
        y_axis = 675+y_a4
        line_x_axis = 50 - 40

        # _____________ Product heading _____________#

        products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
        x_adjust = 10
        for product in products:
            product_name = list(product.short_name.split(" "))
            mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
            try:
                mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
            except:
                pass
            if product.short_name == products[-1].short_name:
                x_axis += 50
                mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

            # table top line
            mycanvas.setLineWidth(0)
            mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
            # table bottom line
            mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
            x_axis += 35 + 10
            x_adjust += 10
        mycanvas.setFont('Helvetica-Bold', 8)
        mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
        mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
        mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

        # _____________ Agent_name,Business_code,Product ___________#

        y_axix_agent_booth = 630+y_a4+10
        x_axis_agent_booth = 90 - 40
        y_axis_product = 675+y_a4+10

        for index, business in enumerate(data_dict["booth_sale"], start=1):
            mycanvas.setFont('Helvetica-Bold', 8)
            mycanvas.drawRightString(line_x_axis + 20, y_axix_agent_booth, str(index))
            mycanvas.drawString(x_axis_agent_booth-5, y_axix_agent_booth, str(data_dict["booth_sale"][business]["zone"])[:5])
            mycanvas.drawString(x_axis_agent_booth + 35, y_axix_agent_booth,
                                str(data_dict["booth_sale"][business]["agent_name"]))
            mycanvas.drawString(x_axis_agent_booth + 40 + 40, y_axix_agent_booth,
                                str(business))

            # _________lines_between_agent_name___________#

            mycanvas.line(x_axis_agent_booth - 10, y_axix_agent_booth + 50, x_axis_agent_booth - 10,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 30, y_axix_agent_booth + 50, x_axis_agent_booth + 30,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 70, y_axix_agent_booth + 50, x_axis_agent_booth + 70,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 105, y_axix_agent_booth + 50, x_axis_agent_booth + 105,
                          y_axix_agent_booth - 10)
            mycanvas.line(x_axis_agent_booth + 650-x_adjust, y_axix_agent_booth + 50, x_axis_agent_booth + 650-x_adjust,
                          y_axix_agent_booth - 10)

            # _________left_and_right_border___________#

            mycanvas.line(line_x_axis, y_axix_agent_booth + 50, line_x_axis, y_axix_agent_booth - 10)
            mycanvas.line(x_axis-x_adjust-10, y_axix_agent_booth + 50, x_axis-x_adjust-10, y_axix_agent_booth - 10)

            y_axix_agent_booth -= 20
            products_list = []
            x_axis_product = 175
            total_cost = 0

            x_adjust = 10
            for product in products:
                print(product)
                ns = 0
                ws = 0
                if len(data_dict["booth_sale"][business]['ns']) != 0:
                    ns = data_dict["booth_sale"][business]['ns'][product.id]["count"]
                if len(data_dict["booth_sale"][business]['ws']) != 0:
                    ws = data_dict["booth_sale"][business]['ws'][product.id]["count"]

                mycanvas.drawRightString(x_axis_product + 20-x_adjust, y_axis_product - 45, str(round(ns) + round(ws)))

                x_axis_product += 35 + 10
                mycanvas.setLineWidth(0)

                mycanvas.line(x_axis_product - 20-x_adjust, y_axis_product + 5, x_axis_product - 20-x_adjust, y_axis_product - 55)

                x_adjust += 10      
            mycanvas.drawRightString(x_axis_product + 35-x_adjust, y_axis_product - 45,
                                     str(data_dict["booth_sale"][business]["product_total_cost"]))
            mycanvas.drawRightString(x_axis_product + 35 + 35-x_adjust, y_axis_product - 45,
                                     str(data_dict["booth_sale"][business]["time"]))
            y_axis_product -= 20

            # _______________After /24____________#

            if index % 34 == 0:

                mycanvas.line(line_x_axis, y_axis_product - 35, x_axis-x_adjust+25, y_axis_product - 35)
                mycanvas.showPage()

                # ________Head_lines________#

                light_color = 0x9b9999
                dark_color = 0x000000
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.setFillColor(HexColor(dark_color))

                mycanvas.setFont('Helvetica', 12.5)
                mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Helvetica', 12)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
                mycanvas.setFont('Helvetica-Bold', 10)
                name_emp = ""
                for name in list(set(data_dict["counter_details"]["employee_name"])):
                    name_emp += name + ","
                date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
                mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(55 - 40, 675+y_a4, 'S.No')
                mycanvas.drawString(90 + 40, 675+y_a4, 'booth')
                mycanvas.drawString(90 + 40, 665+y_a4, 'code')
                mycanvas.drawString(125 - 35, 675+y_a4, 'agent')
                mycanvas.drawString(126 - 35, 665+y_a4, 'name')
                mycanvas.drawString(50, 675+y_a4, 'zone')
                x_axis = 175
                y_axis = 675+y_a4
                line_x_axis = 50 - 40

                # _____________ Product heading _____________#

                products = list(Product.objects.filter(is_active=True).exclude(id__in=[21, 22, 23, 24]).order_by('display_ordinal'))
                x_adjust = 10
                for product in products:
                    product_name = list(product.short_name.split(" "))
                    mycanvas.drawString(x_axis-x_adjust, y_axis, str(product_name[0][:3]))
                    try:
                        mycanvas.drawString(x_axis-x_adjust, y_axis - 10, str(product_name[1]))
                    except:
                        pass
                    if product.short_name == products[-1].short_name:
                        x_axis += 50
                        mycanvas.drawString(x_axis-x_adjust-10, y_axis, 'Total')

                    # table top line
                    mycanvas.setLineWidth(0)
                    mycanvas.line(line_x_axis, y_axis + 15, x_axis-x_adjust + 45, y_axis + 15)
                    # table bottom line
                    mycanvas.line(line_x_axis, y_axis - 15, x_axis-x_adjust + 45, y_axis - 15)
                    x_axis += 35 + 10
                    x_adjust += 10
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawString(x_axis + 2-x_adjust-10, y_axis, 'Time@')
                mycanvas.line(x_axis-x_adjust-10, y_axis + 15, x_axis + 35-x_adjust-10, y_axis + 15)
                mycanvas.line(x_axis-x_adjust-10, y_axis - 15, x_axis + 35-x_adjust-10, y_axis - 15)

                # _____________ Agent_name,Business_code,Product ___________#

                y_axix_agent_booth = 630+y_a4+10
                x_axis_agent_booth = 90 - 40
                y_axis_product = 675+y_a4+10

                # _________Grand_total__________#

        x_axis_product = 175
        mycanvas.line(line_x_axis, y_axis_product - 35, x_axis + 25-x_adjust, y_axis_product - 35)
        x_adjust = 10
        for i in range(len(products) + 1):
            mycanvas.line(x_axis_product - 10-x_adjust, y_axis_product, x_axis_product - 10-x_adjust, y_axis_product - 55)
            x_axis_product += 35 + 10
            x_adjust += 10

        mycanvas.line(line_x_axis, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 55)
        mycanvas.line(x_axis-x_adjust+35, y_axis_product - 35, x_axis-x_adjust+35, y_axis_product - 55)
        mycanvas.line(line_x_axis, y_axis_product - 35, line_x_axis, y_axis_product - 55)
        mycanvas.drawString(line_x_axis + 35, y_axis_product - 48, "Total Packets")
        mycanvas.drawRightString(x_axis_product-x_adjust+10, y_axis_product - 68, str(data_dict["grand_total"]))

        mycanvas.line(x_axis-x_adjust+35, y_axis_product - 55, x_axis-x_adjust+35, y_axis_product - 75)
        mycanvas.line(line_x_axis, y_axis_product - 55, line_x_axis, y_axis_product - 75)
        mycanvas.line(x_axis - 60-x_adjust+10, y_axis_product - 55, x_axis - 60-x_adjust+10, y_axis_product - 75)
        mycanvas.line(line_x_axis, y_axis_product - 75, x_axis-x_adjust+35, y_axis_product - 75)
        mycanvas.drawString(x_axis_product - 125-x_adjust+10, y_axis_product - 68, 'Grand Total Rs.')
        mycanvas.setFont('Helvetica-Bold', 12)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')

        grand_total = data_dict["grand_total"]
        grand_total = f"{grand_total:,.2f}"

        mycanvas.setFont('Helvetica-Bold', 11)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(15, y_axis_product - 98, 'The total money collected by counter ' + str(
            data_dict["counter_details"]["counter_name"]) + ' on ')

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawString(360, y_axis_product - 98,
                            str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

        x_axis_product += 35
        x_adjust = 10
        for product in products:
            try:
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawRightString(line_x_axis + 145 + 40-x_adjust, y_axis_product - 48,
                                         str(int(data_dict["product_total_count"][product.id]["count"])))
                line_x_axis += 35 + 10
                x_adjust += 10
            except:
                pass

        mycanvas.showPage()

        # ________Head_lines_for_counter_wise_Total________#

        light_color = 0x9b9999
        dark_color = 0x000000
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.setFillColor(HexColor(dark_color))
        y_a4 = 80

        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 665 + 20+y_a4, "Milk Agents")
        mycanvas.line(300-50, 661 + 20+y_a4, 400-50, 661 + 20+y_a4)

        # table header

        x_adjust = 50
        y_axis_product_total = 645 - 20 + 20 +y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 668 - 20 + 20+y_a4
        y_head = 655 - 20 + 20+y_a4

        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        products_obj = list(Product.objects.filter(is_active=True, group_id__in=[1, 3]).order_by('display_ordinal'))

        index = 0
        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_agent
        y_a4 = 90
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 420 + 20+y_a4, "Curd Agents")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-x_adjust, 416 + 20+y_a4, 400-x_adjust, 416 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, group_id=2).order_by('display_ordinal'))

        y_axis_product_total = 405 - 25 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 428 - 25 + 20+y_a4
        y_head = 415 - 25 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        oscost = 0
        osliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["product_total_count"][product.id]["ns_count"]
            osliter += round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)
            oscost += round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))
            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["product_total_count"][product.id]["ns_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ns_cost"]), 2)))

            grand_total_litters += osliter

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 345, y_axis_product_total - 20, str(osliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(oscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        # curd_wholesale
        y_a4 = 100
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(300, 195 + 20+y_a4, "Curd Wholesale")
        mycanvas.setLineWidth(1.2)
        mycanvas.line(300-50, 191 + 20+y_a4, 400-50, 191 + 20+y_a4)
        mycanvas.setLineWidth(0)

        products_obj = list(Product.objects.filter(is_active=True, id__in=[25, 7, 10]).order_by('display_ordinal'))

        y_axis_product_total = 155 + 20+y_a4
        x_axis_line = 124-x_adjust
        y_axis_line = 178 + 20+y_a4
        y_head = 165 + 20+y_a4
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(70 + 60 + 10 + 5-x_adjust, y_head, 'S.No')
        mycanvas.drawCentredString(115 + 60 + 20-x_adjust, y_head, 'Products')
        mycanvas.drawCentredString(185 + 60 + 30-x_adjust, y_head, 'Total Packets')
        mycanvas.drawCentredString(425 - 70 + 5-x_adjust, y_head, 'Total Litters')
        mycanvas.drawCentredString(485 - 60 + 20-x_adjust, y_head, 'Price')
        mycanvas.drawCentredString(545 - 30 + 20-x_adjust, y_head, 'Sale Cost')

        mycanvas.setLineWidth(0)
        mycanvas.line(124-x_adjust, y_axis_line, 585-x_adjust, y_axis_line)
        mycanvas.line(124-x_adjust, y_axis_line - 20, 585-x_adjust, y_axis_line - 20)

        grand_total_litters = 0
        total_count = 0
        wscost = 0
        wsliter = 0
        index = 0

        for product in products_obj:
            index += 1
            x_axis_product_total = 52-x_adjust

            total_count += data_dict["product_total_count"][product.id]["ws_count"]
            wsliter += round(Decimal(data_dict["product_total_count"][product.id]["ws_litre"]), 3)
            wscost += round(Decimal(data_dict["product_total_count"][product.id]["ws_cost"]), 3)

            mycanvas.drawString(x_axis_product_total + 90, y_axis_product_total - 15, str(index))

            mycanvas.drawString(x_axis_product_total + 125, y_axis_product_total - 15, str(product.short_name))

            mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 15,
                                     str(int(data_dict["product_total_count"][product.id]["ws_count"])))
            mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ws_litre"]), 3)))
            mycanvas.drawRightString(x_axis_product_total + 427 + 10, y_axis_product_total - 15,
                                     str(round(Decimal(product.mrp), 2)))
            mycanvas.drawRightString(x_axis_product_total + 520 + 5, y_axis_product_total - 15,
                                     str(round(Decimal(data_dict["product_total_count"][product.id]["ws_cost"]), 2)))

            #         mycanvas.drawRightString(x_axis_product_total + 380, y_axis_product_total - 15, str(total_litters))

            # --line--#
            mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 40, y_axis_line, x_axis_line + 40, y_axis_product_total - 25)
            mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 195, y_axis_line, x_axis_line + 195, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 180 + 100, y_axis_line, x_axis_line + 180 + 100, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 452 - 80, y_axis_line, x_axis_line + 452 - 80, y_axis_product_total - 50)
            mycanvas.line(x_axis_line + 540 - 80, y_axis_line, x_axis_line + 540 - 80, y_axis_product_total - 50)

            y_axis_product_total -= 20

        mycanvas.drawRightString(x_axis_product_total + 260, y_axis_product_total - 20, str(int(total_count)))
        mycanvas.drawRightString(x_axis_product_total + 340 + 5, y_axis_product_total - 20, str(wsliter))
        mycanvas.drawRightString(x_axis_product_total + 525, y_axis_product_total - 20, str(round(Decimal(wscost), 2)))

        mycanvas.drawString(x_axis_product_total + 37 + 80, y_axis_product_total - 20, "Sub Total")

        mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 460, y_axis_product_total - 7)
        mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 460, y_axis_product_total - 30)

        grand_total = data_dict["grand_total"]
        grand_total = f"{grand_total:,.2f}"

        mycanvas.setFont('Helvetica-Bold', 11)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(15, y_axis_product_total - 58, 'The total money collected by counter ' + str(
            data_dict["counter_details"]["counter_name"]) + ' on ')

        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawString(360, y_axis_product_total - 58,
                            str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(grand_total) + '.')

        words = num2words(round(data_dict["grand_total"]), lang='en_IN')
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawString(15, y_axis_product_total - 58 - 20 - 5,
                                   "Total Amount Collected " + "  Rupees.  " + str(words.upper()) + " " + "Only")

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
        
        
        mycanvas.showPage()
        if data_dict["counter_details"]["counter_name"] != 'Online':
        #for Challa
            challan_y = 730
            x_ad = 120
            y_ad = 5
            mycanvas.setFont('Helvetica-Bold', 12)
            mycanvas.drawCentredString(300-x_ad,challan_y,str(str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))))
            mycanvas.drawCentredString(300-x_ad,challan_y-20,"COINWAR")

            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawRightString(190-x_ad,challan_y-60+y_ad,"2000")
            mycanvas.drawRightString(220-x_ad,challan_y-60+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-80+y_ad,"500")
            mycanvas.drawRightString(220-x_ad,challan_y-80+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-100+y_ad,"200")
            mycanvas.drawRightString(220-x_ad,challan_y-100+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-120+y_ad,"100")
            mycanvas.drawRightString(220-x_ad,challan_y-120+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-140+y_ad,"50")
            mycanvas.drawRightString(220-x_ad,challan_y-140+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-160+y_ad,"20")
            mycanvas.drawRightString(220-x_ad,challan_y-160+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-180+y_ad,"10")
            mycanvas.drawRightString(220-x_ad,challan_y-180+y_ad,"X")

            mycanvas.drawRightString(190-x_ad,challan_y-200+y_ad,"1")
            mycanvas.drawRightString(220-x_ad,challan_y-200+y_ad,"X")

            mycanvas.drawCentredString(215,challan_y-220+y_ad,"Total")

            mycanvas.drawString(150-x_ad,challan_y-240+y_ad,"Card Amount")
            mycanvas.drawString(150-x_ad,challan_y-260+y_ad,"MISC")
            mycanvas.drawString(150-x_ad,challan_y-280+y_ad,"Grand Total")
            mycanvas.drawString(150-x_ad,challan_y-300+y_ad,"Debit Card")
            mycanvas.drawString(150-x_ad,challan_y-320+y_ad,"Total")

            #line vertical
            mycanvas.line(300-x_ad,challan_y-24,300-x_ad,challan_y-325)
            mycanvas.line(140-x_ad,challan_y+14,140-x_ad,challan_y-325)
            mycanvas.line(460-x_ad,challan_y+14,460-x_ad,challan_y-325)

            mycanvas.line(200-x_ad,challan_y-24,200-x_ad,challan_y-205+y_ad)
            mycanvas.line(230-x_ad,challan_y-24,230-x_ad,challan_y-205+y_ad)

            #top & bottom line
            mycanvas.line(140-x_ad,challan_y+14,460-x_ad,challan_y+14)
            mycanvas.line(140-x_ad,challan_y-5,460-x_ad,challan_y-5)
            mycanvas.line(140-x_ad,challan_y-24,460-x_ad,challan_y-24)
            mycanvas.line(140-x_ad,challan_y-40,460-x_ad,challan_y-40)
            mycanvas.line(140-x_ad,challan_y-325,460-x_ad,challan_y-325)

            #lines between rows
            for i in range(13):
                mycanvas.line(140-x_ad,challan_y-65+y_ad,460-x_ad,challan_y-65+y_ad)
                challan_y -= 20

            #for_full_total
            zone_y = 730-300
            grand_totals = 0
            mycanvas.setFont('Helvetica-Bold', 12)
            mycanvas.line(375,zone_y+35,565,zone_y+35)
            mycanvas.drawCentredString(470,zone_y+17,"Total Amount Details")
            mycanvas.line(375,zone_y+5,565,zone_y+5)
            mycanvas.setFont('Helvetica', 12)
            data_list = ['Bank','Swiping Machine','R.S Puram','Total']
            for zone in data_list:
                mycanvas.drawString(380-3,zone_y-10,str(zone))
        #         mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]))
                mycanvas.line(375,zone_y-20,565,zone_y-20)
                mycanvas.line(470,zone_y+5,470,zone_y-20)
                mycanvas.line(375,zone_y+35,375,zone_y-20)
                mycanvas.line(565,zone_y+35,565,zone_y-20)
        #         grand_totals += zone_dict[zone]
                zone_y -= 25
        
    
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Agents Sales')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in list(set(data_dict["counter_details"]["employee_name"])):
            name_emp += name + ","
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

        zone_y = 690
        #for_zonewise_total
        grand_totals = 0
        order_count = 0
        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.line(375,zone_y+55,565,zone_y+55)
        mycanvas.drawCentredString(470,zone_y+37,"Zone Wise Sale Details")
        mycanvas.line(375,zone_y+25,565,zone_y+25)
        mycanvas.drawString(383,zone_y+10,"Sale For")
        mycanvas.drawString(448,zone_y+10,"Count")
        mycanvas.drawString(505,zone_y+10,"Amount")
        mycanvas.line(375,zone_y+5,565,zone_y+5)
        mycanvas.setFont('Helvetica', 10)

        for zone in zone_dict:
            print(zone)
            mycanvas.drawString(380,zone_y-10,str(zone))
            mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]["amount"]))
            mycanvas.drawRightString(485,zone_y-10,str(len(list(set(zone_dict[zone]["order_count"])))))
            mycanvas.line(375,zone_y-20,565,zone_y-20)
            mycanvas.line(440,zone_y+25,440,zone_y-40)
            mycanvas.line(490,zone_y+25,490,zone_y-40)
            mycanvas.line(375,zone_y+55,375,zone_y-40)
            mycanvas.line(565,zone_y+55,565,zone_y-40)
            grand_totals += zone_dict[zone]["amount"]
            order_count += len(list(set(zone_dict[zone]["order_count"])))
            zone_y -= 25
        mycanvas.drawString(380,zone_y-10,"Grand Total")
        mycanvas.drawRightString(560,zone_y-10,str(grand_totals))
        mycanvas.drawRightString(485,zone_y-10,str(order_count))
        mycanvas.line(375,zone_y-15,565,zone_y-15)

        indian = pytz.timezone('Asia/Kolkata')
        mycanvas.setFont('Times-Italic', 10)
        mycanvas.drawRightString(585, 10,
                            'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
        
        

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


def serve_counter_order_details_for_icustomer(counter_id, date, user_name):
    if counter_id == 'online':
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(time_created__date=date, ordered_via_id__in=[1, 3]).order_by('id')
        counter_name = 'Online'
    else:
        employee_trace_ids = list(
            CounterEmployeeTraceMap.objects.filter(counter_id=counter_id, collection_date=date).values_list('id',
                                                                                                            flat=True))
        employee_trace_sale_group_obj = list(
            CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace_id__in=employee_trace_ids).order_by('icustomer_sale_group').values_list(
                'icustomer_sale_group', flat=True))
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(id__in=employee_trace_sale_group_obj).order_by('id')
        counter_name = Counter.objects.get(id=counter_id).name
    icustomer_sale_group_ids = list(icustomer_sale_group_obj.values_list('id', flat=True))
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group_id__in=icustomer_sale_group_obj, product__is_active=True)
    products = Product.objects.filter(group_id=1, is_active=True).order_by('display_ordinal')
   
    zone_dict = {}
   
    for zone in Zone.objects.all().exclude(id__in=[11,12,13,15]):
        if zone.name not in zone_dict:
            zone_dict[zone.name] = {
                "amount":0,
                "order_count":[],
            }
           
    for sale_group in icustomer_sale_group_obj:
        if sale_group.zone.name in zone_dict:
            zone_dict[sale_group.zone.name]["order_count"].append(sale_group.business_id)
            zone_dict[sale_group.zone.name]["amount"] += sale_group.total_cost_for_month
    
    wallet_amount_for_order_obj = ICustomerWalletAmoutForOrder.objects.filter(icustomer_sale_group__in=icustomer_sale_group_ids)
    wallet_amount_for_order_list = list(wallet_amount_for_order_obj.values_list('id', 'month', 'year', 'icustomer', 'wallet_amount'))
    wallet_amount_for_order_column = ['id', 'month', 'year', 'icustomer', 'wallet_amount']
    waller_amount_for_order_df = pd.DataFrame(wallet_amount_for_order_list, columns=wallet_amount_for_order_column)
    waller_amount_for_order_df = waller_amount_for_order_df.groupby(['icustomer', 'month', 'year']).agg({'wallet_amount':'first'}).reset_index()
    waller_amount_for_order_df['wallet_amount'].sum()
    
   
    data_dict = {
        "total_amount_used_via_wallet": waller_amount_for_order_df['wallet_amount'].sum(),
        "counter_details": {
            "date": date,
            "counter_id": counter_id,
            "counter_name": counter_name,
            "employee_name": []
        },
        "agent_details": [],
        "icustomer_sale_details": {},
        "grand_total": None,
        "grand_total_month": None,
        "product_total_count": {},
        "product_total_cost":{},
        "product_total_cost_month":{}
    }
    if counter_id == 'online':
        data_dict["counter_details"]["employee_name"].append('-')
    else:
        for employee_trace_id in employee_trace_ids:
            employee_name = CounterEmployeeTraceMap.objects.get(id=employee_trace_id).employee.user_profile.user.first_name
            data_dict["counter_details"]["employee_name"].append(employee_name)

    for icustomer_sale_group in icustomer_sale_group_obj:
        #         print(icustomer_sale_group.id)
        order_for_date = str(icustomer_sale_group.date)
        my_date = datetime.datetime.strptime(order_for_date, "%Y-%m-%d")
        my_month = my_date.month
        my_month_name = month_name[my_date.month]
        my_days = monthrange(my_date.year, my_month)[1]
        count = 0
        for agent_details in data_dict["agent_details"]:
            if agent_details["for_date"] == order_for_date and agent_details[
                "icustomer_id"] == icustomer_sale_group.icustomer_id:
                agent_details["total_cost"] += icustomer_sale_group.total_cost
                count += 1
        if count == 0:
            tempicustomer_sale_group_dict = {
                "year": my_date.year,
                "for_date": order_for_date,
                "for_month": my_month_name,
                "for_day": my_days,
                "business_code": icustomer_sale_group.business.code,
                "icustomer_id": icustomer_sale_group.icustomer_id,
                "icustomer_code": icustomer_sale_group.icustomer.customer_code,
                "customer_name": icustomer_sale_group.icustomer.user_profile.user.first_name+ " "+icustomer_sale_group.icustomer.user_profile.user.last_name,
                "zone":icustomer_sale_group.zone.name,
                "card_no":ICustomerMonthlyOrderTransaction.objects.get(icustomer_id=icustomer_sale_group.icustomer_id, month=icustomer_sale_group.date.month, year=icustomer_sale_group.date.year).milk_card_number,
                "total_cost": icustomer_sale_group.total_cost,
                "icustomer_sale_group_id": icustomer_sale_group.id,
            }
            data_dict["agent_details"].append(tempicustomer_sale_group_dict)

    product_list = []
    for product in products:
        product_list.append(product.id)

    #     for product_id in product_list:
    for icustomer_sale in icustomer_sale_obj:
        #         print(icustomer_sale.icustomer_sale_group.icustomer_id)
        time = icustomer_sale.time_created
        time_now = time.astimezone(timezone('Asia/Kolkata'))
        time_created = time_now.strftime("%I:%M")
        try:
            if str(icustomer_sale.icustomer_sale_group.date) in data_dict["icustomer_sale_details"]:
                if icustomer_sale.icustomer_sale_group.icustomer_id in data_dict["icustomer_sale_details"][
                    str(icustomer_sale.icustomer_sale_group.date)]:
                    if not icustomer_sale.product.id in \
                           data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                               icustomer_sale.icustomer_sale_group.icustomer_id]:
                        pass
                    else:
                        data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                            icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id][
                            "product_name"] = icustomer_sale.product.name
                        data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                            icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id][
                            "icustomer_sale_count"] += icustomer_sale.count
                        data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                            icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id][
                            "icustomer_sale_cost"] += icustomer_sale.cost
            #                         data_dict["icustomer_sale_details"][icustomer_sale.icustomer_sale_group.date][icustomer_sale.icustomer_sale_group.business.id][icustomer_sale.product.id]["icustomer_sale_group"].append(icustomer_sale.icustomer_sale_group.id)

            if not str(icustomer_sale.icustomer_sale_group.date) in data_dict["icustomer_sale_details"]:
                data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)] = {}

            if not icustomer_sale.icustomer_sale_group.icustomer_id in data_dict["icustomer_sale_details"][
                str(icustomer_sale.icustomer_sale_group.date)]:
                data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                    icustomer_sale.icustomer_sale_group.icustomer_id] = {
                    "time":time_created,
                    "product_total_cost": None,
                    "product_cost_month": None,
                }
            if not icustomer_sale.product.id in \
                   data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                       icustomer_sale.icustomer_sale_group.icustomer_id]:
                data_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                    icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id] = {
                    "product_name": icustomer_sale.product.name,
                    "icustomer_sale_count": icustomer_sale.count,
                    "icustomer_sale_cost": icustomer_sale.cost,
                    #                     "icustomer_sale_group" : [icustomer_sale.icustomer_sale_group.id]
                }
        except:
            pass

    #   grand total
    grand_total = 0
    grand_total_month = 0
    for data in data_dict["agent_details"]:
        grand_total += data["total_cost"]
        grand_total_month += data["total_cost"] * data["for_day"]
    data_dict["grand_total"] = grand_total
    data_dict["grand_total_month"] = grand_total_month

    for sale_date in data_dict["icustomer_sale_details"]:
        for i_customer in data_dict["icustomer_sale_details"][sale_date]:
            if i_customer == "time":
                pass
            else:
                product_in_business = []
                for product in data_dict["icustomer_sale_details"][sale_date][i_customer]:
                    product_in_business.append(product)

                # checking a products present in under guven business_id
                total_cost = 0
                for product in product_list:
                    if product in product_in_business:
                        total_cost += data_dict["icustomer_sale_details"][sale_date][i_customer][product][
                            "icustomer_sale_cost"]
                data_dict["icustomer_sale_details"][sale_date][i_customer]["product_total_cost"] = total_cost

                current_id = 0
                for business in data_dict["agent_details"]:
                    if current_id == business["icustomer_id"]:
                        continue
                    if i_customer == business["icustomer_id"]:
                        #                 print(business["business_id"])
                        current_id = i_customer
                        data_dict["icustomer_sale_details"][sale_date][i_customer]["product_cost_month"] = total_cost * \
                                                                                                           business[
                                                                                                               "for_day"]

                #            adding products in data_dicts
                try:
                    for product in product_list:
                        if not product in data_dict["product_total_count"]:
                            data_dict["product_total_count"][product] = 0

                        if product in product_in_business:
                            product_sale_count = data_dict["icustomer_sale_details"][sale_date][i_customer][product][
                                "icustomer_sale_count"]
                            data_dict["product_total_count"][product] += product_sale_count
                        # product total
                        if not product in data_dict["product_total_cost"]:
                            data_dict["product_total_cost"][product] = 0

                        if product in product_in_business:
                            product_sale_cost = data_dict["icustomer_sale_details"][sale_date][i_customer][product][
                                "icustomer_sale_cost"]
                            data_dict["product_total_cost"][product] += product_sale_cost
                        #product_total_month
                        if not product in data_dict["product_total_cost_month"]:
                            data_dict["product_total_cost_month"][product] = 0

                        if product in product_in_business:
                            product_sale_cost = data_dict["icustomer_sale_details"][sale_date][i_customer][product][
                                "icustomer_sale_cost"]
                            data_dict["product_total_cost_month"][product] += product_sale_cost * my_days
                       
                except:
                    pass
    data_dict['user_name'] = user_name
    data = generate_sale_pdf_for_icustomer_order(data_dict, date,zone_dict)
    return data


def generate_sale_pdf_for_icustomer_order(data_dict, date, zone_dict):
    new_date = date
    # datetime.datetime.strftime(date, '%d-%b-%Y')
    file_name = str(new_date) + '_' + str(
        data_dict["counter_details"]["counter_name"]) + '_' + 'daily_coubter_report_family_card_sale' + '.pdf'
    # file_path = os.path.join('static/media/', file_name)
    file_path = os.path.join('static/media/counter_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

     # ___Head_lines___#
    light_color = 0x9b9999
    dark_color = 0x000000
    x_adjust = 66
    y_a4 = -80
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 12.5)
   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Family Card Sales')
    mycanvas.line(226-50, 802, 473-50, 802)
   
    date_in_format = datetime.datetime.strptime(str(data_dict["counter_details"]["date"]), '%Y-%m-%d')
                                               
    name_emp = ""
    for name in list(set(data_dict["counter_details"]["employee_name"])):
        name_emp += name + ","
                                               
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(60 + 20-x_adjust, 785, 'OrdersFor : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)


    # ____table header____#
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(55 + 30-x_adjust, 675-y_a4, 'S.No')
    mycanvas.drawString(100 + 15-x_adjust, 675-y_a4, 'Customer')
    mycanvas.drawString(100 + 25-x_adjust, 675-y_a4-10, 'Code')
#     mycanvas.drawString(100 + 100-x_adjust, 675-y_a4, 'Name')
    mycanvas.drawString(175 + 75-x_adjust, 675-y_a4, 'Zone')
    mycanvas.drawString(175 + 35-x_adjust, 675-y_a4, 'Booth')
    mycanvas.drawString(175 + 35-x_adjust, 675-y_a4-10, 'Code')
    mycanvas.drawString(190 - 20-x_adjust, 675-y_a4, 'Month')
    mycanvas.drawString(175 + 120-x_adjust, 675-y_a4, 'Card')
    mycanvas.drawString(175 + 125-x_adjust, 675-y_a4-10, 'No')
   
    x_axis = 370-x_adjust
    y_axis = 675-y_a4
    line_x_axis = 50-x_adjust

    # _____ Product heading _____#

    products = list(Product.objects.filter(is_active=True, group_id=1).order_by('display_ordinal'))

    for product in products:
        product_name = list(product.short_name.split(" "))
        mycanvas.drawString(x_axis - 30, y_axis, str(product_name[0][:3]))
        try:
            mycanvas.drawString(x_axis - 30, y_axis - 10, str(product_name[1]))
        except:
            pass
        if product.short_name == products[-1].short_name:
            x_axis += 45
            mycanvas.drawString(x_axis - 35, y_axis, 'Total /')
            mycanvas.drawString(x_axis - 35, y_axis - 10, ' Day')
            x_axis += 50
            mycanvas.drawString(x_axis - 30, y_axis, 'Total /')
            mycanvas.drawString(x_axis + 8 - 40, y_axis - 10, 'Month')
           
            mycanvas.drawString(x_axis + 20, y_axis, 'Time')
            mycanvas.drawString(x_axis + 8 +20, y_axis - 10, '@')
        # table top line
        mycanvas.setLineWidth(0)
        mycanvas.line(line_x_axis + 30, y_axis + 15, x_axis + 55 - 10, y_axis + 15)
        # table bottom line
        mycanvas.line(line_x_axis + 30, y_axis - 15, x_axis + 55 - 10, y_axis - 15)
        x_axis += 35

        # _____ Agent_name,Business_code,Product _____#

    y_axix_agent_booth = 640-y_a4
    x_axis_agent_booth = 90-x_adjust
    y_axis_product = 675-y_a4
    business_break = 0
    sale_date = ''
    index = 0
    for business in data_dict["agent_details"]:

        index += 1
        sale_date = business["for_date"]
        business_break = business["icustomer_id"]
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawRightString(line_x_axis + 20 + 30, y_axix_agent_booth, str(index))
        mycanvas.drawString(x_axis_agent_booth + 25, y_axix_agent_booth, str(business["icustomer_code"]))
#         mycanvas.drawString(x_axis_agent_booth + 89, y_axix_agent_booth, str(business["customer_name"])[:12])
        mycanvas.drawString(x_axis_agent_booth + 138 - 20, y_axix_agent_booth, str(business["business_code"]))
        mycanvas.drawString(x_axis_agent_booth + 140 + 63, y_axix_agent_booth, str(business["card_no"]))

        #             mycanvas.drawString(x_axis_agent_booth+160,y_axix_agent_booth,str(business["for_date"]))
        mycanvas.drawString(x_axis_agent_booth + 101 - 20, y_axix_agent_booth,
                            str(business["for_month"][:3]) + " " + str(str(business["year"])[2:]))
       
        mycanvas.drawString(x_axis_agent_booth + 140 + 18, y_axix_agent_booth,str(business["zone"][:6]))
       
        sale_group_id = business["icustomer_sale_group_id"]

        # ____lines_between_agent_name____#

        mycanvas.line(x_axis_agent_booth + 20, y_axix_agent_booth + 50, x_axis_agent_booth + 20,
                      y_axix_agent_booth - 10)
       
        mycanvas.line(x_axis_agent_booth + 75, y_axix_agent_booth + 50, x_axis_agent_booth + 75,
                      y_axix_agent_booth - 10)
       
        mycanvas.line(x_axis_agent_booth + 115, y_axix_agent_booth + 50, x_axis_agent_booth + 115,
                      y_axix_agent_booth - 10)
       
        mycanvas.line(x_axis_agent_booth + 75 + 80, y_axix_agent_booth + 50, x_axis_agent_booth + 75 + 80,
                      y_axix_agent_booth - 10)
        mycanvas.line(x_axis_agent_booth + 150 + 45, y_axix_agent_booth + 50, x_axis_agent_booth + 150 + 45,
                      y_axix_agent_booth - 10)
        mycanvas.line(x_axis_agent_booth + 270 - 30, y_axix_agent_booth + 50, x_axis_agent_booth + 270 - 30,
                      y_axix_agent_booth - 10)
        #             mycanvas.line(x_axis_agent_booth+215,y_axix_agent_booth+60,x_axis_agent_booth+215,y_axix_agent_booth-15)

        # ____left_and_right_border____#

        mycanvas.line(line_x_axis + 30, y_axix_agent_booth + 50, line_x_axis + 30, y_axix_agent_booth - 13)
        mycanvas.line(x_axis - 45 - 40, y_axix_agent_booth + 50, x_axis - 45 - 40, y_axix_agent_booth - 13)
        mycanvas.line(x_axis + 20 - 40, y_axix_agent_booth + 50, x_axis + 20 - 40, y_axix_agent_booth - 13)
        mycanvas.line(x_axis + 10, y_axix_agent_booth + 50, x_axis + 10, y_axix_agent_booth - 13)

        y_axix_agent_booth -= 13
        products_list = []
        mycanvas.drawString(x_axis_agent_booth + 500 + 34, y_axix_agent_booth+13,data_dict["icustomer_sale_details"][business["for_date"]][business["icustomer_id"]]["time"])
        for product_id in data_dict["icustomer_sale_details"][business["for_date"]][business["icustomer_id"]]:
            if product_id == "product_total_cost":
                continue
            products_list.append(product_id)
        x_axis_product = 370-x_adjust
        #             total_cost = 0
        for product in products:
            if not (product.id in products_list):
                mycanvas.drawRightString(x_axis_product + 20 - 30, y_axis_product - 35, "-")
                x_axis_product += 35
            if (product.id in products_list):
                mycanvas.drawRightString(x_axis_product + 20 - 30, y_axis_product - 35, str(int(
                    data_dict["icustomer_sale_details"][business["for_date"]][business["icustomer_id"]][product.id][
                        "icustomer_sale_count"])))
                x_axis_product += 35
            mycanvas.setLineWidth(0)
            mycanvas.line(x_axis_product - 10 - 30, y_axis_product + 15, x_axis_product - 10 - 30, y_axis_product - 43)
        total_cost = data_dict["icustomer_sale_details"][business["for_date"]][business["icustomer_id"]][
            "product_total_cost"]
        total_cost_month = data_dict["icustomer_sale_details"][business["for_date"]][business["icustomer_id"]][
            "product_cost_month"]
        mycanvas.drawRightString(x_axis_product + 35 - 30, y_axis_product - 35, str(total_cost))
        mycanvas.drawRightString(x_axis_product + 100 - 30, y_axis_product - 35, str(total_cost_month))
        y_axis_product -= 13

        # ______After /45_____#

        if index % 52 == 0:

            mycanvas.line(line_x_axis+30, y_axis_product - 30, x_axis+10, y_axis_product - 30)
            mycanvas.showPage()

            # ___Head_lines___#

            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 12.5)

            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawCentredString(300, 805, 'Daily Counter Report : Family Card Sales')
            mycanvas.line(226-50, 802, 473-50, 802)

            date_in_format = datetime.datetime.strptime(str(data_dict["counter_details"]["date"]), '%Y-%m-%d')

            name_emp = ""
            for name in list(set(data_dict["counter_details"]["employee_name"])):
                name_emp += name + ","

            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(60 + 20-x_adjust, 785, 'OrdersFor : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

            # ____table header____#
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(55 + 30-x_adjust, 675-y_a4, 'S.No')
            mycanvas.drawString(100 + 15-x_adjust, 675-y_a4, 'Customer')
            mycanvas.drawString(100 + 25-x_adjust, 675-y_a4-10, 'Code')
        #     mycanvas.drawString(100 + 100-x_adjust, 675-y_a4, 'Name')
            mycanvas.drawString(175 + 75-x_adjust, 675-y_a4, 'Zone')
            mycanvas.drawString(175 + 35-x_adjust, 675-y_a4, 'Booth')
            mycanvas.drawString(175 + 35-x_adjust, 675-y_a4-10, 'Code')
            mycanvas.drawString(190 - 20-x_adjust, 675-y_a4, 'Month')
            mycanvas.drawString(175 + 120-x_adjust, 675-y_a4, 'Card')
            mycanvas.drawString(175 + 125-x_adjust, 675-y_a4-10, 'No')
            x_axis = 370-x_adjust
            y_axis = 675-y_a4
            line_x_axis = 50-x_adjust

            # _____ Product heading _____#

            products = list(Product.objects.filter(is_active=True, group_id=1).order_by('display_ordinal'))

            for product in products:
                product_name = list(product.short_name.split(" "))
                mycanvas.drawString(x_axis - 30, y_axis, str(product_name[0][:3]))
                try:
                    mycanvas.drawString(x_axis - 30, y_axis - 10, str(product_name[1]))
                except:
                    pass
                if product.short_name == products[-1].short_name:
                    x_axis += 45
                    mycanvas.drawString(x_axis - 35, y_axis, 'Total /')
                    mycanvas.drawString(x_axis - 35, y_axis - 10, ' Day')
                    x_axis += 50
                    mycanvas.drawString(x_axis - 30, y_axis, 'Total /')
                    mycanvas.drawString(x_axis + 8 - 40, y_axis - 10, 'Month')
                    mycanvas.drawString(x_axis + 20, y_axis, 'Time')
                    mycanvas.drawString(x_axis + 8 +20, y_axis - 10, '@')
                # table top line
                mycanvas.setLineWidth(0)
                mycanvas.line(line_x_axis + 30, y_axis + 15, x_axis + 55 - 10, y_axis + 15)
                # table bottom line
                mycanvas.line(line_x_axis + 30, y_axis - 15, x_axis + 55 - 10, y_axis - 15)
                x_axis += 35

                # _____ Agent_name,Business_code,Product _____#

            y_axix_agent_booth = 640-y_a4
            x_axis_agent_booth = 90-x_adjust
            y_axis_product = 675-y_a4

            # ____Grand_total___#

    x_axis_product = 370-x_adjust
    mycanvas.line(line_x_axis + 30, y_axis_product - 35, x_axis + 20 - 10, y_axis_product - 35)
    for i in range(len(products) + 1):
        mycanvas.line(x_axis_product - 10 - 30, y_axis_product, x_axis_product - 10 - 30, y_axis_product - 55)
        x_axis_product += 35
    mycanvas.line(line_x_axis + 30, y_axis_product - 55, x_axis + 20 - 40, y_axis_product - 55)
    mycanvas.line(x_axis + 20 - 40, y_axis_product - 35, x_axis + 20 - 40, y_axis_product - 55)
    mycanvas.line(line_x_axis + 30, y_axis_product - 35, line_x_axis + 30, y_axis_product - 55)
    mycanvas.drawString(line_x_axis + 120, y_axis_product - 48, "Total Packets")

    mycanvas.line(line_x_axis + 30, y_axis_product - 75, x_axis + 20 - 40, y_axis_product - 75)
    mycanvas.line(x_axis + 20 - 40, y_axis_product - 55, x_axis + 20 - 40, y_axis_product - 75)
    mycanvas.line(x_axis + 20 - 95, y_axis_product - 55, x_axis + 20 - 95, y_axis_product - 75)
    mycanvas.line(line_x_axis + 30, y_axis_product - 55, line_x_axis + 30, y_axis_product - 75)
    mycanvas.drawRightString(x_axis_product - 30, y_axis_product - 68, 'Grand Total')
    mycanvas.drawRightString(x_axis_product + 65 - 30, y_axis_product - 68, str(data_dict["grand_total_month"]))

    x_axis_product += 35
    for priduct_total in data_dict["product_total_count"]:
        mycanvas.drawRightString(line_x_axis + 340 - 30, y_axis_product - 48,
                                 str(int(data_dict["product_total_count"][priduct_total])))
        line_x_axis += 35
   
    words = num2words(round(data_dict["grand_total_month"]), lang='en_IN')
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(15, y_axis_product - 93,
                               "Total Amount Collected " + "  Rupees.  " + str(words.upper()) + " " + "Only")
    # ------------------------------------------Final_Report---------------------------------------------------#

    mycanvas.showPage()
    x_adjust = 68
    y_a4 = -70
   
    light_color = 0x9b9999
    dark_color = 0x000000

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 795, 'Daily Counter Report : Family Card Sales')
    mycanvas.line(226-50, 792, 473-50, 792)
   
    date_in_format = datetime.datetime.strptime(str(data_dict["counter_details"]["date"]), '%Y-%m-%d')
                                               
    name_emp = ""
    for name in list(set(data_dict["counter_details"]["employee_name"])):
        name_emp += name + ","
                                               
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(60 + 10-50, 765, 'OrdersFor : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(data_dict["counter_details"]["counter_name"])+'  |  '+'Employees : '+name_emp)

    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(130-x_adjust, 655-y_a4, 'S.No')
    mycanvas.drawString(175-x_adjust, 655-y_a4, 'Products')
    mycanvas.drawString(235-x_adjust, 655-y_a4, 'Total Packets')
    mycanvas.drawString(310-x_adjust, 655-y_a4, 'Total Litters')
    mycanvas.drawString(385-x_adjust, 655-y_a4, 'Total Amount / Day')
    mycanvas.drawString(495-x_adjust, 655-y_a4, 'Total Amount / Month')

    mycanvas.setLineWidth(0)
    mycanvas.line(118-x_adjust, 668-y_a4, 610-x_adjust, 668-y_a4)
    mycanvas.line(118-x_adjust, 648-y_a4, 610-x_adjust, 648-y_a4)
    index = 0
    y_axis_product_total = 645-y_a4
    x_axis_line = 118-x_adjust
    y_axis_line = 668-y_a4
    grand_total_amount_day = 0
    grand_total_amount_month = 0
    grand_total_litters = 0
    total_count = 0
    for product in products:
        index += 1
        x_axis_product_total = 130-x_adjust
        mycanvas.line(x_axis_line, y_axis_line, x_axis_line, y_axis_product_total - 50)
        mycanvas.drawString(x_axis_product_total + 10, y_axis_product_total - 15, str(index))

        mycanvas.line(x_axis_line + 50, y_axis_line, x_axis_line + 50, y_axis_product_total - 25)
        mycanvas.drawString(x_axis_product_total + 45, y_axis_product_total - 15, str(product.short_name))

        mycanvas.line(x_axis_line + 110, y_axis_line, x_axis_line + 110, y_axis_product_total - 50)
        total_litters = 0
        total_amount_day = 0
        total_amount_month = 0
        if product.id in data_dict["product_total_count"].keys():
            mycanvas.drawRightString(x_axis_product_total + 163, y_axis_product_total - 15,
                                     str(int(data_dict["product_total_count"][product.id])))
            total_count += data_dict["product_total_count"][product.id]
           
            total_litters = round(Decimal((data_dict["product_total_count"][product.id] * float(product.quantity)) / 1000),
                                  3)
            total_amount_day = round(Decimal(data_dict["product_total_cost"][product.id]),2)
            total_amount_month = round(Decimal(data_dict["product_total_cost_month"][product.id]),2)
        grand_total_litters += total_litters
        grand_total_amount_day += total_amount_day
        grand_total_amount_month += total_amount_month
                                       
        mycanvas.line(x_axis_line + 185, y_axis_line, x_axis_line + 185, y_axis_product_total - 50)
        mycanvas.drawRightString(x_axis_product_total + 235, y_axis_product_total - 15, str(total_litters))
       
        mycanvas.drawRightString(x_axis_product_total + 340, y_axis_product_total - 15, str(total_amount_day))                            
        mycanvas.line(x_axis_line + 365, y_axis_line, x_axis_line + 365, y_axis_product_total - 50)
        mycanvas.drawRightString(x_axis_product_total + 465, y_axis_product_total - 15, str(total_amount_month))
       
        mycanvas.line(x_axis_line + 412-155, y_axis_line, x_axis_line + 412-155, y_axis_product_total - 50)
        mycanvas.line(x_axis_line + 492, y_axis_line, x_axis_line + 492, y_axis_product_total - 50)
        y_axis_product_total -= 20

    mycanvas.drawRightString(x_axis_product_total + 163, y_axis_product_total - 20, str(int(total_count)))
    mycanvas.drawRightString(x_axis_product_total + 235, y_axis_product_total - 20, str(grand_total_litters))
    mycanvas.drawRightString(x_axis_product_total + 465, y_axis_product_total - 20, str(grand_total_amount_month))
   
    mycanvas.drawString(x_axis_product_total + 37, y_axis_product_total - 20, "Grand Total")

    mycanvas.line(x_axis_line, y_axis_product_total - 7, x_axis_line + 492, y_axis_product_total - 7)
    mycanvas.line(x_axis_line, y_axis_product_total - 30, x_axis_line + 492, y_axis_product_total - 30)
   
    mycanvas.setFont('Helvetica-Bold', 11)
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
    mycanvas.drawString(15, y_axis_product_total - 58, 'The total money collected by counter ' + str(
        data_dict["counter_details"]["counter_name"]) + ' on ')

    mycanvas.setFont('Helvetica-Bold', 13)
    mycanvas.drawRightString(585, y_axis_product_total - 58,
                        str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(data_dict["grand_total_month"]) + '.')

    words = num2words(round(data_dict["grand_total_month"]), lang='en_IN')
    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(15, y_axis_product_total - 58 - 15,
                               "Total Amount Collected " + "  Rupees.  " + str(words.upper()) + " " + "Only")
    
    #code for showing used amunt from wallet
    mycanvas.drawString(15,  y_axis_product_total - 100,
                           "Total Amount Used By Wallet " + "  Rs.  " + str(data_dict['total_amount_used_via_wallet']) + ".")
    amount_in_hand = data_dict["grand_total_month"] - data_dict['total_amount_used_via_wallet']
    words_for_amount_in_hand = num2words(round(amount_in_hand), lang='en_IN')

    mycanvas.drawString(15, y_axis_product_total - 120, 'Total Amount Balance In Hand ' + ' on ')

    mycanvas.setFont('Helvetica-Bold', 13)
    mycanvas.drawRightString(585, y_axis_product_total - 120,
                        str(datetime.datetime.strftime(date_in_format, '%d %b %Y,')) + ' is ' + "Rs." + str(amount_in_hand) + '.')

    mycanvas.setFont('Helvetica-Bold', 10)

    mycanvas.drawString(15, y_axis_product_total - 140,
                            "Total Amount Balance In Hand" + "  Rupees.  " + str(words_for_amount_in_hand.upper()) + " " + "Only")
    gape_ad = 80
    if data_dict["counter_details"]["counter_name"] != "Online":
        challan_y = y_axis_product_total - 200 + gape_ad
        # #for Challan
        # x_ad = 120
        # y_ad = 5
        # mycanvas.setFont('Helvetica-Bold', 12)
        # mycanvas.drawCentredString(300-x_ad,challan_y,str(str(datetime.strftime(date_in_format, '%d-%m-%Y'))))
        # mycanvas.drawCentredString(300-x_ad,challan_y-20,"COINWAR")

        # mycanvas.setFont('Helvetica', 12)
        # mycanvas.drawRightString(190-x_ad,challan_y-60+y_ad,"2000")
        # mycanvas.drawRightString(220-x_ad,challan_y-60+y_ad,"X")

        # mycanvas.drawRightString(190-x_ad,challan_y-80+y_ad,"500")
        # mycanvas.drawRightString(220-x_ad,challan_y-80+y_ad,"X")

        # mycanvas.drawRightString(190-x_ad,challan_y-100+y_ad,"200")
        # mycanvas.drawRightString(220-x_ad,challan_y-100+y_ad,"X")

        # mycanvas.drawRightString(190-x_ad,challan_y-120+y_ad,"100")
        # mycanvas.drawRightString(220-x_ad,challan_y-120+y_ad,"X")

        # mycanvas.drawRightString(190-x_ad,challan_y-140+y_ad,"50")
        # mycanvas.drawRightString(220-x_ad,challan_y-140+y_ad,"X")

        # mycanvas.drawRightString(190-x_ad,challan_y-160+y_ad,"20")
        # mycanvas.drawRightString(220-x_ad,challan_y-160+y_ad,"X")

        # mycanvas.drawRightString(190-x_ad,challan_y-180+y_ad,"10")
        # mycanvas.drawRightString(220-x_ad,challan_y-180+y_ad,"X")

        # mycanvas.drawRightString(190-x_ad,challan_y-200+y_ad,"1")
        # mycanvas.drawRightString(220-x_ad,challan_y-200+y_ad,"X")

        # mycanvas.drawCentredString(215-x_ad,challan_y-220+y_ad,"Total")

        # mycanvas.drawString(150-x_ad,challan_y-240+y_ad,"Card Amount")
        # mycanvas.drawString(150-x_ad,challan_y-260+y_ad,"MISC")
        # mycanvas.drawString(150-x_ad,challan_y-280+y_ad,"Grand Total")
        # mycanvas.drawString(150-x_ad,challan_y-300+y_ad,"Debit Card")
        # mycanvas.drawString(150-x_ad,challan_y-320+y_ad,"Total")

        # #line vertical
        # mycanvas.line(300-x_ad,challan_y-24,300-x_ad,challan_y-325)
        # mycanvas.line(140-x_ad,challan_y+14,140-x_ad,challan_y-325)
        # mycanvas.line(460-x_ad,challan_y+14,460-x_ad,challan_y-325)

        # mycanvas.line(200-x_ad,challan_y-24,200-x_ad,challan_y-205+y_ad)
        # mycanvas.line(230-x_ad,challan_y-24,230-x_ad,challan_y-205+y_ad)

        # #top & bottom line
        # mycanvas.line(140-x_ad,challan_y+14,460-x_ad,challan_y+14)
        # mycanvas.line(140-x_ad,challan_y-5,460-x_ad,challan_y-5)
        # mycanvas.line(140-x_ad,challan_y-24,460-x_ad,challan_y-24)
        # mycanvas.line(140-x_ad,challan_y-40,460-x_ad,challan_y-40)
        # mycanvas.line(140-x_ad,challan_y-325,460-x_ad,challan_y-325)

        # #lines between rows
        # for i in range(13):
        #     mycanvas.line(140-x_ad,challan_y-65+y_ad,460-x_ad,challan_y-65+y_ad)
        #     challan_y -= 20
           
       
        zone_y = y_axis_product_total - 540 + gape_ad
        #for_full_total
        grand_totals = 0
        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.line(375,zone_y+35,565,zone_y+35)
        mycanvas.drawCentredString(470,zone_y+17,"Total Amount Details")
        mycanvas.line(375,zone_y+5,565,zone_y+5)
        mycanvas.setFont('Helvetica', 12)
        data_list = ['Bank','Swiping Machine','R.S Puram','Total']
        for zone in data_list:
            mycanvas.drawString(380-3,zone_y-10,str(zone))
    #         mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]))
            mycanvas.line(375,zone_y-20,565,zone_y-20)
            mycanvas.line(470,zone_y+5,470,zone_y-20)
            mycanvas.line(375,zone_y+35,375,zone_y-20)
            mycanvas.line(565,zone_y+35,565,zone_y-20)
    #         grand_totals += zone_dict[zone]
            zone_y -= 25
       
       
   
    zone_y = y_axis_product_total - 300+ gape_ad
    #for_zonewise_total
    grand_totals = 0
    order_count = 0
    mycanvas.setFont('Helvetica-Bold', 12)
    mycanvas.line(375,zone_y+55,565,zone_y+55)
    mycanvas.drawCentredString(470,zone_y+37,"Zone Wise Sale Details")
    mycanvas.line(375,zone_y+25,565,zone_y+25)
    mycanvas.drawString(383,zone_y+10,"Sale For")
    mycanvas.drawString(448,zone_y+10,"Count")
    mycanvas.drawString(505,zone_y+10,"Amount")
    mycanvas.line(375,zone_y+5,565,zone_y+5)
    mycanvas.setFont('Helvetica', 10)
    
    for zone in zone_dict:
        mycanvas.drawString(380,zone_y-10,str(zone))
        mycanvas.drawRightString(560,zone_y-10,str(zone_dict[zone]["amount"]))
        mycanvas.drawRightString(485,zone_y-10,str(len(list(set(zone_dict[zone]["order_count"])))))
        mycanvas.line(375,zone_y-20,565,zone_y-20)
        mycanvas.line(440,zone_y+25,440,zone_y-40)
        mycanvas.line(490,zone_y+25,490,zone_y-40)
        mycanvas.line(375,zone_y+55,375,zone_y-40)
        mycanvas.line(565,zone_y+55,565,zone_y-40)
        grand_totals += zone_dict[zone]["amount"]
        order_count += len(list(set(zone_dict[zone]["order_count"])))
        zone_y -= 25
    mycanvas.drawString(380,zone_y-10,"Grand Total")
    mycanvas.drawRightString(560,zone_y-10,str(grand_totals))
    mycanvas.drawRightString(485,zone_y-10,str(order_count))
    mycanvas.line(375,zone_y-15,565,zone_y-15)
   
   
    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawRightString(585, 10,
                        'Report Generated by: ' + str(data_dict['user_name'])+", " + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S")))
   
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


def serve_total_sale_counter_wise(date, user_name):
    print('data_', date, user_name)
    countt_total_file_list = []
    cash_employee_trace_objs = CounterEmployeeTraceMap.objects.filter(time_created__date=date,counter_id__in=[1,2,3,5,9,11,12, 26],counter__is_active=True)
    card_employee_trace_objs = CounterEmployeeTraceMap.objects.filter(time_created__date=date,counter_id__in=[4,6,7,21,25],counter__is_active=True)
    cridet_employee_trace_objs = CounterEmployeeTraceMap.objects.filter(time_created__date=date,counter_id__in=[8,13,14,15,16,17,22,29],counter__is_active=True)
    selected_date = date
    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d')
    date_in_format = selected_date + datetime.timedelta(days=1)

    data_dict = {
        "date": date,
        "cash": {},
        "card": {},
        "cridet" : {}
    }
    cash_counter_obj = Counter.objects.filter(id__in=[1,2,3,5,9,11,12,26],is_active=True).order_by('name')
    card_counter_obj = Counter.objects.filter(id__in=[4,6,7,21,25],is_active=True).order_by('name')
    cridet_counter_obj = Counter.objects.filter(id__in=[8,13,14,15,16,17,22,29],is_active=True).order_by('name')

    for counter in cash_counter_obj:
        if not counter.id in data_dict["cash"]:
            data_dict["cash"][counter.name] = {
                "sale_amount" : 0,
                "booth_count" : [],
                "closing_time" : [],
            }

    for counter in card_counter_obj:
        if not counter.id in data_dict["card"]:
            data_dict["card"][counter.name] = {
                "sale_amount" : 0,
                "booth_count" : [],
                "closing_time" : [],
            }

    for counter in cridet_counter_obj:
        if not counter.id in data_dict["cridet"]:
            data_dict["cridet"][counter.name] = {
                "sale_amount" : 0,
                "booth_count" : [],
                "closing_time" : [],
            }

    # data_dict["cash"]["P_Route"] = {
    #             "sale_amount" : 0,
    #             "booth_count" : [],
    #             "closing_time" : [],
    #         }
   
    data_dict["card"]["Online Counter"] = {
                "sale_amount" : 0,
                "booth_count" : [],
                "closing_time" : [],
            }
   
    data_dict["cash"]["Online Counter"] = {
                "sale_amount" : 0,
                "booth_count" : [],
                "closing_time" : [],
            }
   
    data_dict["cridet"]["Online Counter"] = {
                "sale_amount" : 0,
                "booth_count" : [],
                "closing_time" : [],
            }

   

    #---cash---#
    online_cash_salegrps = SaleGroup.objects.filter(date=date_in_format, ordered_via_id__in=[1,3])
    for online in online_cash_salegrps:
       
        if online.business.business_type_id in [1, 2, 9, 11, 12, 15]:
           
            data_dict["cash"]["Online Counter"]["sale_amount"] += online.total_cost

            time = online.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")

            data_dict["cash"]["Online Counter"]["booth_count"].append(online.business_id)
            data_dict["cash"]["Online Counter"]["closing_time"].append(time_created)
           
        else:
           
            data_dict["cridet"]["Online Counter"]["sale_amount"] += online.total_cost

            time = online.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")

            data_dict["cridet"]["Online Counter"]["booth_count"].append(online.business_id)
            data_dict["cridet"]["Online Counter"]["closing_time"].append(time_created)
   
    for employee_trace_obj in cash_employee_trace_objs:
       
        cash_obj = list(CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace_id=employee_trace_obj.id).order_by('sale_group').values_list('sale_group', flat=True))
        for cash_id in cash_obj:
            if SaleGroup.objects.filter(id=cash_id).exists():
                sale_group_obj = SaleGroup.objects.get(id=cash_id)
                # try:
                # except sale_group_obj.DoesNotExist:
                #     sale_group_obj = None
                
                if sale_group_obj is not None:
                    data_dict["cash"][employee_trace_obj.counter.name]["sale_amount"] += sale_group_obj.total_cost
                
                    time = sale_group_obj.time_created
                    time_now = time.astimezone(timezone('Asia/Kolkata'))
                    time_created = time_now.strftime("%I:%M")
                
                    data_dict["cash"][employee_trace_obj.counter.name]["booth_count"].append(sale_group_obj.business_id)
                    data_dict["cash"][employee_trace_obj.counter.name]["closing_time"].append(time_created)


    #---card---#
   
    online_card_salegrps = ICustomerSaleGroup.objects.filter(time_created__date=date,ordered_via_id__in=[1,3])
    for online in online_card_salegrps:
   
        data_dict["card"]["Online Counter"]["sale_amount"] += online.total_cost_for_month
       
        time = online.time_created
        time_now = time.astimezone(timezone('Asia/Kolkata'))
        time_created = time_now.strftime("%I:%M")
       
        data_dict["card"]["Online Counter"]["booth_count"].append(online.business_id)
        data_dict["card"]["Online Counter"]["closing_time"].append(time_created)
     

    for employee_trace_obj in card_employee_trace_objs:
       
        card_obj = list(CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace_id=employee_trace_obj.id).order_by('icustomer_sale_group').values_list('icustomer_sale_group', flat=True))
        for card_id in card_obj:
            sale_group_obj = ICustomerSaleGroup.objects.get(id=card_id)
           
            # try:
            # except sale_group_obj.DoesNotExist:
            #     sale_group_obj = None
           
            if sale_group_obj is not None:

                data_dict["card"][employee_trace_obj.counter.name]["sale_amount"] += sale_group_obj.total_cost_for_month

                time = sale_group_obj.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")

                data_dict["card"][employee_trace_obj.counter.name]["booth_count"].append(sale_group_obj.business_id)

                data_dict["card"][employee_trace_obj.counter.name]["closing_time"].append(time_created)

    #---cridet---#
    for employee_trace_obj in cridet_employee_trace_objs :

        cridet_obj = list(CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace_id=employee_trace_obj.id).order_by('sale_group').values_list('sale_group', flat=True))
        
        for credit_id in cridet_obj:
            try:
                sale_group_obj = SaleGroup.objects.get(id=credit_id)
            except SaleGroup.DoesNotExist:
                sale_group_obj = None
           
            if sale_group_obj is not None:
               
                if sale_group_obj.route_id == 119 or sale_group_obj.route_id == 118:
                    continue
                    # data_dict["cash"]["P_Route"]["sale_amount"] += sale_group_obj.total_cost

                    # time = sale_group_obj.time_created
                    # time_now = time.astimezone(timezone('Asia/Kolkata'))
                    # time_created = time_now.strftime("%I:%M")
                   
                    # data_dict["cash"]["P_Route"]["booth_count"].append(sale_group_obj.business_id)

                    # data_dict["cash"]["P_Route"]["closing_time"].append(time_created)
               
                else:
               
                    data_dict["cridet"][employee_trace_obj.counter.name]["sale_amount"] += sale_group_obj.total_cost

                    time = sale_group_obj.time_created
                    time_now = time.astimezone(timezone('Asia/Kolkata'))
                    time_created = time_now.strftime("%I:%M")

                    data_dict["cridet"][employee_trace_obj.counter.name]["booth_count"].append(sale_group_obj.business_id)
                    data_dict["cridet"][employee_trace_obj.counter.name]["closing_time"].append(time_created)
   
    data_dict["user_name"] = user_name
    date = str(date)[:10]
    print(date)
    data = generate_total_sale_pdf_counter_wise(data_dict, date)
    return data


def generate_total_sale_pdf_counter_wise(data_dict, date):
    new_date = date
    file_name = str(new_date) + '_all_counter_sale_summary' + '.pdf'
    file_path = os.path.join('static/media/counter_report/', file_name)
#     file_path = os.path.join('static/media', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

     # ________Head_lines________#
    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))

    x_adjust=60
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
#     mycanvas.setFont('Helvetica', 14)
#     mycanvas.drawCentredString(300, 785, 'Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(str(data_dict["date"])[:10], '%Y-%m-%d')

    mycanvas.drawCentredString(300, 795, 'Daily All Counter Sales summary Report ( '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+" )")
#     mycanvas.line(228-50, 752, 472-50, 752)

    # _____________table header_____________#

    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.setFillColor(HexColor(dark_color))

#     date_in_format = datetime.datetime.strptime(str(data_dict["date"])[:10], '%Y-%m-%d')

#     mycanvas.drawString(190 - 50-x_adjust, 725, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
#     #     mycanvas.setFillColor(HexColor(light_color))
#     mycanvas.drawString(160 - 50-x_adjust, 725, 'Date : ')

    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setLineWidth(0)

    x_axis = 195-x_adjust
    line_x_axis = 150-x_adjust
    card_sub = 0
    cash_sub = 0
    cridet_sub = 0

    for data in data_dict:
        if data == "date" or data == "user_name":
            continue
        else:
            if data == "cash":
                head = "Cash/Agent Counter Sales (code:929292)"
                y_axis = 650+60
                y_axis_agent = 665+60
                y_head = 685+60

                mycanvas.setLineWidth(0)
                mycanvas.line(line_x_axis - 50, y_axis_agent + 30, line_x_axis + 500 - 50 + 10, y_axis_agent + 30)
                mycanvas.line(line_x_axis - 50, y_axis_agent, line_x_axis + 500 - 50 + 10, y_axis_agent)
                mycanvas.setFont('Helvetica-Bold', 12)
                mycanvas.drawCentredString(300, y_head + 25, str(head))
                mycanvas.setLineWidth(1.2)
                mycanvas.line(228-50, y_head + 21, 472-50, y_head + 21)
                mycanvas.setLineWidth(0)

                mycanvas.setFont('Helvetica-Bold', 10)
                mycanvas.drawString(160 - 50-x_adjust, y_head, 'S.No')
                mycanvas.drawString(245 - 50-x_adjust, y_head, 'Counter Name')
                mycanvas.drawString(420 - 95-x_adjust, y_head, 'Total Number Of')
                mycanvas.drawString(421 - 95-x_adjust, y_head - 15, 'Booths Ordered')

                mycanvas.drawString(500 - 75-x_adjust, y_head, 'Time of Counter')
                mycanvas.drawString(530 - 75-x_adjust, y_head - 15, 'Close')

                mycanvas.drawString(595 - 50-x_adjust, y_head, 'Sale Amount')

            if data == "card":
                head = "Card Counter Sales (code:929293)"
                y_axis = 400 + 75
                y_axis_agent = 415 + 75
                y_head = 435 + 75

                mycanvas.line(line_x_axis - 50, y_axis_agent + 30, line_x_axis + 500 - 50 + 10, y_axis_agent + 30)
                mycanvas.line(line_x_axis - 50, y_axis_agent, line_x_axis + 500 - 50 + 10, y_axis_agent)
                mycanvas.setFont('Helvetica-Bold', 12)
                mycanvas.drawCentredString(300, y_head + 25, str(head))
                mycanvas.setLineWidth(1.2)
                mycanvas.line(228-50, y_head + 21, 472-50, y_head + 21)
                mycanvas.setLineWidth(0)

                mycanvas.setFont('Helvetica-Bold', 10)
                mycanvas.drawString(160 - 50-x_adjust, y_head, 'S.No')
                mycanvas.drawString(245 - 50-x_adjust, y_head, 'Counter Name')
                mycanvas.drawString(420 - 95-x_adjust, y_head, 'Total Number Of')
                mycanvas.drawString(421 - 95-x_adjust, y_head - 15, 'Booths Ordered')

                mycanvas.drawString(500 - 75-x_adjust, y_head, 'Time of Counter')
                mycanvas.drawString(530 - 75-x_adjust, y_head - 15, 'Close')

                mycanvas.drawString(595 - 50-x_adjust, y_head, 'Sale Amount')

            if data == "cridet":
                head = "Credit/Advance Virtual counter Sale (code:929294)"
                y_axis = 200 + 70 - 3 +20
                y_axis_agent = 215 + 60 - 3+30
                y_head = 235 + 70 - 3+20

                mycanvas.setLineWidth(0)
                mycanvas.line(line_x_axis - 50, y_axis_agent + 30, line_x_axis + 500 - 50 + 10, y_axis_agent + 30)
                mycanvas.line(line_x_axis - 50, y_axis_agent, line_x_axis + 500 - 50 + 10, y_axis_agent)
                mycanvas.setFont('Helvetica-Bold', 12)
                mycanvas.drawCentredString(350-x_adjust, y_head + 25, str(head))
                mycanvas.setLineWidth(1.2)
                mycanvas.line(228-x_adjust, y_head + 21, 472-x_adjust, y_head + 21)
                mycanvas.setLineWidth(0)

                mycanvas.setFont('Helvetica-Bold', 10)
                mycanvas.drawString(160 - 50-x_adjust, y_head, 'S.No')
                mycanvas.drawString(245 - 50-x_adjust, y_head, 'Counter Name')
                mycanvas.drawString(420 - 95-x_adjust, y_head, 'Total Number Of')
                mycanvas.drawString(421 - 95-x_adjust, y_head - 15, 'Booths Ordered')

                mycanvas.drawString(500 - 75-x_adjust, y_head, 'Time of Counter')
                mycanvas.drawString(530 - 75-x_adjust, y_head - 15, 'Close')

                mycanvas.drawString(595 - 50-x_adjust, y_head, 'Sale Amount')

            index = 1
            sub_total = 0
            total_booth = 0

            for counter in data_dict[data]:
                mycanvas.drawString(x_axis - 30 - 50, y_axis, str(index))
                mycanvas.line(x_axis - 50, y_axis_agent + 30, x_axis - 50, y_axis - 25)
                mycanvas.drawString(x_axis + 35 - 70, y_axis, str(counter))
                mycanvas.line(x_axis + 210 - 90, y_axis_agent + 30, x_axis + 210 - 90, y_axis - 25)
                mycanvas.drawRightString(x_axis + 280 - 70, y_axis, str(len(set(data_dict[data][counter]["booth_count"]))))
                mycanvas.line(x_axis + 290 - 70, y_axis_agent + 30, x_axis + 290 - 70, y_axis - 25)
                total_booth += len(set(data_dict[data][counter]["booth_count"]))
                if data_dict[data][counter]["closing_time"]:
                    mycanvas.drawRightString(x_axis + 360 - 50, y_axis, str(data_dict[data][counter]["closing_time"][-1]))
                else:
                    mycanvas.drawRightString(x_axis + 360 - 50, y_axis, '00:00')
                mycanvas.line(x_axis + 370 - 50, y_axis_agent + 30, x_axis + 370 - 50, y_axis - 25)

                mycanvas.drawRightString(x_axis + 455 - 50, y_axis,
                                         str(round(Decimal(data_dict[data][counter]["sale_amount"]), 2)))
                sub_total += round(Decimal(data_dict[data][counter]["sale_amount"]), 2)

                index += 1
                y_axis -= 16
            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.line(line_x_axis - 50, y_axis + 10, line_x_axis + 510 - 50, y_axis + 10)
            mycanvas.line(line_x_axis - 50, y_axis_agent + 30, line_x_axis - 50, y_axis + 10)
            mycanvas.line(x_axis + 455 - 40, y_axis_agent + 30, x_axis + 455 - 40, y_axis - 10)
            mycanvas.line(line_x_axis - 5, y_axis - 10, line_x_axis + 510 - 50, y_axis - 10)
            mycanvas.drawRightString(x_axis + 445 - 40, y_axis - 3, str(sub_total))

            mycanvas.drawRightString(x_axis + 280 - 70, y_axis - 3, str(total_booth))
            mycanvas.drawRightString(x_axis + 180 - 70, y_axis - 3, 'Sub Total')

            if data == "cash":
                cash_sub = sub_total
            if data == "card":
                card_sub = sub_total
            if data == "cridet":
                cridet_sub = sub_total

    mycanvas.setFont('Helvetica-Bold', 12)
   
    y_ads = 60
    mycanvas.drawCentredString(300, 120 - 5+70-y_ads, "Total Sale")
    mycanvas.setLineWidth(1.2)
    mycanvas.line(308-50, 120 - 9+70-y_ads, 392-50, 120 - 9+70-y_ads)
    mycanvas.setLineWidth(0)

    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(230-x_adjust, 100 - 20+80-y_ads, "Counter Type Sale")
    mycanvas.drawString(430 + 10-x_adjust, 100 - 20+80-y_ads, "Total Amount")
    mycanvas.drawString(230 - 50 - 20-x_adjust, 100 - 30 - 10+80-y_ads, "Cash/Agent Counter Sales (code:929292)")
    mycanvas.drawString(230 - 50 - 20-x_adjust, 100 - 45 - 10+80-y_ads, "Card Counter Sales (code:929293)")
    mycanvas.drawString(230 - 50 - 20-x_adjust, 100 - 60 - 10+80-y_ads, "Credit/Advance Virtual counter Sale (code:929294)")

    grand_total = cash_sub + card_sub + cridet_sub

    mycanvas.drawRightString(430 + 100-x_adjust, 100 - 30 - 10+80-y_ads, str(cash_sub))
    mycanvas.drawRightString(430 + 100-x_adjust, 100 - 45 - 10+80-y_ads, str(card_sub))
    mycanvas.drawRightString(430 + 100-x_adjust, 100 - 60 - 10+80-y_ads, str(cridet_sub))
    mycanvas.drawRightString(430 + 100-x_adjust, 100 - 75 - 10+80-y_ads, str(grand_total))
    mycanvas.drawString(320-x_adjust, 100 - 76 - 10+80-y_ads, "GRAND TOTAL")
    mycanvas.line(300-x_adjust, 45 - 15+80-y_ads, 300-x_adjust, 30 - 20+80-y_ads)

    mycanvas.line(155-x_adjust, 110 - 20+80-y_ads, 535-x_adjust, 110 - 20+80-y_ads)
    mycanvas.line(155-x_adjust, 110 - 25 - 10+80-y_ads, 535-x_adjust, 110 - 25 - 10+80-y_ads)
    mycanvas.line(155-x_adjust, 45 - 20+80-y_ads, 535-x_adjust, 45 - 20+80-y_ads)
    mycanvas.line(300-x_adjust, 30 - 20+80-y_ads, 535-x_adjust, 30 - 20+80-y_ads)

    mycanvas.line(155-x_adjust, 110 - 20+80-y_ads, 155-x_adjust, 45 - 20+80-y_ads)
    mycanvas.line(535-x_adjust, 110 - 20+80-y_ads, 535-x_adjust, 30 - 20+80-y_ads)
    mycanvas.line(415-x_adjust, 110 - 20+80-y_ads, 415-x_adjust, 30 - 20+80-y_ads)

    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawRightString(580, 5, 'Report Generated by: ' + str(
        data_dict['user_name'] + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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


def total_sale_per_date(date_for):
    date = date_for
    print(date)
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
    date_in_format = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
    print(str(date_in_format))
    employee_trace_objs = CounterEmployeeTraceMap.objects.filter(collection_date=date)

    data_dict = {
        "date": str(date_in_format),
        "icustomer_sale": {},
        "sale": {}
    }
    counter_obj = Counter.objects.all().order_by('name')

    #     for countes in counter_obj:
    #         print(countes.id)

    for counter in counter_obj:
        if not counter.id in data_dict["icustomer_sale"]:
            data_dict["icustomer_sale"][counter.id] = 0
        if not counter.id in data_dict["sale"]:
            data_dict["sale"][counter.id] = 0

    for employee_trace_obj in employee_trace_objs:
        #     print(employee_trace_id)
        icus_groups = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
            counter_employee_trace_id=employee_trace_obj.id).values_list('icustomer_sale_group', flat=True))
        for icus_group in icus_groups:
            try:
                #                 for icus_counter in data_dict["icustomer_sale"]:
                #                     if icus_counter == CounterEmployeeTraceMap.objects.get(id=employee_trace_id).counter_id:
                data_dict["icustomer_sale"][employee_trace_obj.counter_id] += ICustomerSaleGroup.objects.get(
                    id=icus_group).total_cost_for_month
            except:
                pass
        agent_order = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
            counter_employee_trace_id=employee_trace_obj.id).values_list('sale_group', flat=True))
        for sale_grp in agent_order:
            try:
                #                 for s_counter in data_dict["sale"]:
                #                     if s_counter == CounterEmployeeTraceMap.objects.get(id=employee_trace_id).counter_id:
                data_dict["sale"][employee_trace_obj.counter_id] += SaleGroup.objects.get(id=sale_grp).total_cost
            except:
                pass

    return data_dict


def serve_total_sale_per_month(month, year, username):
    counter_obj = Counter.objects.filter().order_by('name')
    total_days = monthrange(year, month)[1]
    month_dict = {
        "Current_month": month_name[month],
    }
    for day in range(1, (total_days + 1)):
        formated_date = str(day) + "-" + str(month) + "-" + str(year)
        date = str(year) + "-" + str(month) + "-" + str(day)
        data_dict = total_sale_per_date(date)
        month_dict[formated_date] = data_dict

        icus_toal_order = 0
        agent_total_order = 0
        for counter in counter_obj:
            # calculating total sale of i_customer for a day
            icus_toal_order += month_dict[formated_date]["icustomer_sale"][counter.id]
            # calculating total sale of agent for a day
            agent_total_order += month_dict[formated_date]["sale"][counter.id]
            # calculating total sale of agent & i_customer in particular counter for a day
            total = month_dict[formated_date]["icustomer_sale"][counter.id] + month_dict[formated_date]["sale"][counter.id]
            month_dict[formated_date]["total_sale_of_counter - " + str(counter.id)] = total

        month_dict[formated_date]["icus_toal_order"] = icus_toal_order
        month_dict[formated_date]["agent_total_order"] = agent_total_order

    month_dict['user_name'] = username
    data = generate_total_sale_pdf_per_month(month_dict, month, year)
    return data


def generate_total_sale_pdf_per_month(month_dict, month, year):
    print(month)
    file_name = str(month_name[month]) +'_'+ str(year) + 'counter_total_sale_agent_+_familycard' + '.pdf'
    print(file_name)
#     file_path = os.path.join('static/media/counter_report/', file_name)
    file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
   
    y_a4 = -80
    # ________Head_lines________#
    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
   
    x_a4 = 70
    #     mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.drawCentredString(300, 795, 'Monthly Counter Sales - Agents + Family Card Holders ( '+ str(month_dict["Current_month"])+" )")
#     mycanvas.drawCentredString(300, 777, '(Agents + Family Card Holders)')
#     mycanvas.line(278-50, 790, 420-50, 790)
#     mycanvas.line(260-50, 771, 440-50, 771)

    # _____________table header_____________#

    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.drawString(175-x_a4, 675-y_a4, 'S.No')
    mycanvas.drawString(230-x_a4, 675-y_a4, 'Date')
    mycanvas.drawString(300-x_a4, 675-y_a4, 'Agent Sale')
    mycanvas.drawString(382-x_a4, 675-y_a4, 'ICustomer Sale')
    mycanvas.drawString(500-x_a4, 675-y_a4, 'Total')

    date_time = datetime.datetime.now()
#     mycanvas.drawString(175-x_a4, 700, 'Month : ')
#     mycanvas.drawString(215-x_a4, 700, str(month_dict["Current_month"]))

    #     Report Generated by: Sunesh Rajan

    x_axis = 180-x_a4
    y_axis = 690-y_a4
    line_xaxis = 168-x_a4
    # lines for heading
    mycanvas.setLineWidth(0)
    mycanvas.line(line_xaxis, y_axis, line_xaxis + 390, y_axis)
    mycanvas.line(line_xaxis, y_axis - 25, line_xaxis + 390, y_axis - 25)

    # printing datas
    index = 0
    grand_total = 0
    icus_grand_total = 0
    agent_grand_total = 0
    for month in month_dict:
        print(month)
        if month == "Current_month" or month == "user_name":
            continue
        try:
            index += 1
            mycanvas.drawString(x_axis, y_axis - 50, str(index))
            mycanvas.line(line_xaxis + 40, y_axis, line_xaxis + 40, y_axis - 60)
            mycanvas.drawString(x_axis + 45, y_axis - 50, str(month))
            mycanvas.line(line_xaxis + 110, y_axis, line_xaxis + 110, y_axis - 60)

            mycanvas.drawRightString(x_axis + 180, y_axis - 50, str(month_dict[month]["agent_total_order"]))
            mycanvas.line(line_xaxis + 200, y_axis, line_xaxis + 200, y_axis - 60)

            mycanvas.drawRightString(x_axis + 280, y_axis - 50, str(month_dict[month]["icus_toal_order"]))
            mycanvas.line(line_xaxis + 300, y_axis, line_xaxis + 300, y_axis - 60)

            total = month_dict[month]["agent_total_order"] + month_dict[month]["icus_toal_order"]
            mycanvas.drawRightString(x_axis + 370, y_axis - 50, str(total))

            icus_grand_total += month_dict[month]["icus_toal_order"]
            agent_grand_total += month_dict[month]["agent_total_order"]
            grand_total += total
        except:
            pass
        # ______________border _ lines_______________

        mycanvas.line(line_xaxis, y_axis, line_xaxis, y_axis - 60)
        mycanvas.line(line_xaxis + 390, y_axis, line_xaxis + 390, y_axis - 60)

        y_axis -= 21

        #           ______After 24 ______

        if index % 32 == 0:
            mycanvas.line(line_xaxis, y_axis - 35, line_xaxis + 390, y_axis - 35)
            mycanvas.showPage()

            # ________Head_lines________#

            light_color = 0x9b9999
            dark_color = 0x000000
            mycanvas.setFillColor(HexColor(light_color))
            mycanvas.setFillColor(HexColor(dark_color))

            #     mycanvas.setStrokeColor(colors.lightgrey)
            mycanvas.setFont('Helvetica-Bold', 14)
            mycanvas.drawCentredString(300, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 785, 'Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica-Bold', 13)
            mycanvas.drawCentredString(300, 765, 'Monthly Counter Sales')
            mycanvas.drawCentredString(300, 747, 'Agents + Family Card Holders')
            mycanvas.line(278-50, 760, 420-50, 760)
            mycanvas.line(260-50, 741, 440-50, 741)

            # _____________table header_____________#

            mycanvas.setFont('Helvetica-Bold', 10)
            mycanvas.drawString(175-x_a4, 675, 'S.No')
            mycanvas.drawString(230-x_a4, 675, 'Date')
            mycanvas.drawString(300-x_a4, 675, 'Agent Sale')
            mycanvas.drawString(382-x_a4, 675, 'ICustomer Sale')
            mycanvas.drawString(500-x_a4, 675, 'Total')

            date_time = datetime.datetime.now()
            mycanvas.drawString(175-x_a4, 700, 'Month : ')
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawString(215-x_a4, 700, str(month_dict["Current_month"]))

            x_axis = 180-x_a4
            y_axis = 690
            line_xaxis = 168-x_a4
            mycanvas.setLineWidth(0)
            # lines for heading
            mycanvas.line(line_xaxis, y_axis, line_xaxis + 390, y_axis)
            mycanvas.line(line_xaxis, y_axis - 25, line_xaxis + 390, y_axis - 25)


    mycanvas.line(line_xaxis, y_axis - 35, line_xaxis + 390, y_axis - 35)
    mycanvas.line(line_xaxis, y_axis - 55, line_xaxis + 390, y_axis - 55)
    mycanvas.line(line_xaxis, y_axis, line_xaxis, y_axis - 55)
    mycanvas.line(line_xaxis + 390, y_axis, line_xaxis + 390, y_axis - 55)
    for line in range(3):
        line_xaxis += 100
        if line == 0:
            mycanvas.line(line_xaxis + 10, y_axis, line_xaxis + 10, y_axis - 55)
        else:
            mycanvas.line(line_xaxis, y_axis, line_xaxis, y_axis - 55)
    mycanvas.drawRightString(x_axis + 370, y_axis - 50, str(grand_total))
    mycanvas.drawRightString(x_axis + 280, y_axis - 50, str(icus_grand_total))
    mycanvas.drawRightString(x_axis + 180, y_axis - 50, str(agent_grand_total))
    mycanvas.drawRightString(x_axis + 80, y_axis - 50, 'Grand Total')
   
    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawString(340, 10,'Report Generated by: ' + str(month_dict['user_name'] + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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


def generate_pdf_for_all_zone_report_per_session(data_dict, user_name, date, session_id):
    session_name = ""
   
    for ses in reversed(session_id):
        session = Session.objects.get(id=ses).name
        session_name += session + ', '
   
    file_name = str(data_dict['date']) + '_' + str(session_name) + '_overall_zone_summary' + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
#     file_path = os.path.join('static/media', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))

    # _Head_lines_#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
    y_a4= 20

    #     mycanvas.setStrokeColor(colors.lightgrey)
#     mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
    date = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
    mycanvas.drawCentredString(300, 795, 'Daily Zone Report : Total Sales ( '+ str(date)+", "+str(session_name)+" )")

    x_a4 = 50
    y_a4 = 80
    # Table Header
    mycanvas.setLineWidth(0)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
    mycanvas.drawString(35-20, 655+y_a4, 'No')
    mycanvas.drawString(60-20, 655+y_a4, 'Zone')
    mycanvas.drawString(95-20, 665+y_a4, 'Items')

    mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
    mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

    mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
    mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')
   
    mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

    mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
    mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(470-20-x_a4, 650+y_a4, '120ml')
    mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
    mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

    mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
    mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

    mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
    mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
    mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
    mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

    products_list = ["TM", "SM", "FCM","TMATE",'CanMlk', "CURD", "BtrMlk", "BmJar", "BMJF", "Lassi"]
#     quantity_list = ["1000", "500", "250", "200", "150","100"]
    quantity_list = ["1000","500", "250", "200", "120","5000"]
    route_list = list(Route.objects.all().values_list("name",flat=True))

    index = 1
    y = 620+y_a4
    y_line = 690+y_a4
    x_line = 30
    grand_total = 0
    mycanvas.setFont('Helvetica', 8)
   
    current_route = ""

    for data in data_dict:
        print(data)
        if data == "date" or data == "session" or data == "final_results" or data_dict[data]["products_total"] == 0:
            continue
        mycanvas.drawString(13, y, str(index))
        #         mycanvas.drawString(75, y,str(data))

        # -----------------------------------------------------------------------------------------------------------------------------------------#

        # lines#
        mycanvas.line(x_line-20, y_line, x_line-20, y - 105)
        mycanvas.line(x_line, y_line, x_line, y - 105)
        mycanvas.line(x_line + 40, y_line, x_line + 40, y - 105)
        mycanvas.line(x_line + 80, y_line, x_line + 80, y - 105)
       
        mycanvas.line(x_line + 110+15, y_line - 26, x_line + 110+15, y - 105)
        mycanvas.line(x_line + 100+75, y_line - 26, x_line + 100+75, y - 105)
        mycanvas.line(x_line + 155+70, y_line - 26, x_line + 155+70, y - 105)
       
        mycanvas.line(x_line + 210+60, y_line - 26, x_line + 210+60, y - 105)
        mycanvas.line(x_line + 265+50, y_line - 26, x_line + 265+50, y - 105)
        mycanvas.line(x_line + 320+40, y_line - 26, x_line + 320+40, y - 105)
        mycanvas.line(x_line + 375+30, y_line - 26, x_line + 375+30, y - 105)
        mycanvas.line(x_line + 430+20, y_line, x_line + 430+20, y - 105)
        mycanvas.line(x_line + 430+70, y_line, x_line + 430+70, y - 105)
        mycanvas.line(x_line + 555, y_line, x_line + 555, y - 105)

        y_line -= 50
        current_route = data_dict[data]["route_name"]
        route_name = ''
        for letter in data_dict[data]["route_name"]:
            if letter == ' ':
                continue
            else:
                route_name += letter
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(30, y, str(route_name[:7]))
#         mycanvas.setFont('Helvetica', 12)
        for products in products_list:
            mycanvas.drawString(75, y, str(products))
            total_litter_line = 0
            x_1000 = 115+10
            x_500 = 105+60
            x_250 = 195+60
            x_200 = 275+60
            x_150 = 315+60
            x_5000 = 430+20
            x_total_litter_line = 520
            if not products in data_dict[data]:
                pass
            #                     if products == "TM" or products == "SM" or products == "FCM":
            #                         y -= 15
            #                         continue
            #                     continue
            if products in data_dict[data]:
                for quantity in quantity_list:
                    try:
                       
                        if quantity == "1000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_1000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_1000 += 50
                       
                        if quantity == "500":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_500 + 35, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_500 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_500 + 30, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_500 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_500 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))

                        if quantity == "250":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_250 + 40 - x_adjust, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_250 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_250 + 40, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_250 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_250 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))
                       
                        if quantity == "200":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_200 + 50, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_200 += 50

                        if quantity == "120":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_150 + 55, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_150 += 50
                       
                       
                        if quantity == "5000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_5000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_5000 += 30

                       
                    except:
                        pass
            mycanvas.drawRightString(x_total_litter_line + 5, y, str(total_litter_line))
            y -= 12
        grand_total += data_dict[data]["products_total"]
        mycanvas.drawRightString(x_total_litter_line + 60, y + 10, str(data_dict[data]["products_total"]))
        y -= 10
        mycanvas.line(10, y + 13, 585, y + 13)
        # -----------------------------------------------6------------------------------------------------------#
        if index % 6 == 0:
            mycanvas.showPage()

            #     mycanvas.setStrokeColor(colors.lightgrey)
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)
            mycanvas.setFillColor(HexColor(dark_color))
            date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
            date = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
            mycanvas.drawCentredString(300, 795, 'Daily Zone Report : Total Sales ( '+ str(date)+", "+str(session_name)+" )")
#             mycanvas.line(246-50, 792, 452-50, 792)
           
            x_a4 = 50
            y_a4 = 80
            # Table Header
            mycanvas.setLineWidth(0)
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica', 8)
            mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
            mycanvas.drawString(35-20, 655+y_a4, 'No')
            mycanvas.drawString(60-20, 655+y_a4, 'Zone')
            mycanvas.drawString(95-20, 665+y_a4, 'Items')

            mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
            mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

            mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
            mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
            mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(470-20-x_a4, 650+y_a4, '120ml')
            mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
            mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

            mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
            mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

            mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
            mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
            mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
            mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

            products_list = ["TM", "SM", "FCM", "TMATE",'CanMlk', "CURD", "BtrMlk", "BmJar",  "BMJF", "Lassi"]
            quantity_list = ["1000","500", "250", "200", "120","5000"]
            route_list = list(Route.objects.all().values_list("name",flat=True))

            y = 620+y_a4
            y_line = 690+y_a4
            x_line = 30
            mycanvas.setFont('Helvetica', 8)

        index += 1

    mycanvas.line(10, y + 13, 10, y - 23)
    mycanvas.line(585, y + 13, 585, y - 23)
    mycanvas.line(585, y + 13, 585, y - 23)
    mycanvas.line(10, y + 13, 585, y + 13)
    mycanvas.line(10, y - 23, 585, y - 23)
    mycanvas.drawRightString(x_total_litter_line + 60, y - 5, str(grand_total))
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(x_total_litter_line - 80, y - 5, 'Grand Total')

    # --------------------------------------------------------Final Report----------------------------------------------------#

    mycanvas.showPage()
    x_a4 = 90
    y_a4 = 120
   
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
    date = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
    mycanvas.drawCentredString(300, 795, 'Daily Zone Report : Total Sales ( '+ str(date)+", "+str(session_name)+" )")
   

    mycanvas.setFont('Helvetica', 10)
    #     mycanvas.drawString(70,655,'zone')
    mycanvas.drawString(110-x_a4, 600+y_a4, 'Items')

    mycanvas.drawString(192-x_a4, 590+y_a4, '1000ml')
    mycanvas.drawString(192+80-x_a4, 590+y_a4, '500ml')
    mycanvas.drawString(272+80-x_a4, 590+y_a4, '250ml')
    mycanvas.drawString(322+80-x_a4, 590+y_a4, '200ml')
    mycanvas.drawString(402+80-x_a4, 590+y_a4, '120ml')
    mycanvas.drawString(472+80-x_a4, 590+y_a4, '5000ml')
    mycanvas.drawString(545+80-x_a4, 600+y_a4, ' TOTAL')
    mycanvas.drawString(545+80-x_a4, 590+y_a4, 'LITTERS')
    #     mycanvas.drawString(602,620,'  NET')
    #     mycanvas.drawString(602,610,'LITTERS')

    # ------------------------------------------lines--------------------------------------------------#
    mycanvas.setLineWidth(0)
    mycanvas.line(90-x_a4+10, 615+y_a4, 615+80-x_a4-20, 615+y_a4)
    mycanvas.line(90-x_a4+10, 580+y_a4, 615+80-x_a4-20, 580+y_a4)

    #     mycanvas.drawString()

    y = 560+y_a4
    y_line = 615+y_a4
    x_line = 90-x_a4
    grand_total = 0

    for data in data_dict["final_results"]:
        mycanvas.line(x_line+10, y_line, x_line+10, y_line - 215)
        mycanvas.line(x_line + 70+10, y_line, x_line + 70+10, y_line - 215)
        mycanvas.line(x_line + 145+10, y_line, x_line + 145+10, y_line - 215)
        mycanvas.line(x_line + 145+80+10, y_line, x_line + 145+80+10, y_line - 215)

        mycanvas.line(x_line + 220+80, y_line, x_line + 220+80, y_line - 215)
        mycanvas.line(x_line + 295+80-10, y_line, x_line + 295+80-10, y_line - 215)
        mycanvas.line(x_line + 370+80-10, y_line, x_line + 370+80-10, y_line - 215)

        mycanvas.line(x_line + 445+80-20, y_line, x_line + 445+80-20, y_line - 215)
        mycanvas.line(x_line + 525+80-20, y_line, x_line + 525+80-20, y_line - 215)
        #         mycanvas.line(x_line+605,y_line,x_line+605,y_line-115)

        if data == "cash":
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 645+y_a4, 'Daily Zone Report : Total-Cash Sales')
            mycanvas.line(200, 640+y_a4, 400, 640+y_a4)

            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(350, 595, 'Daily Zone Report : Total-Cash Sales')
            else:
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                        print('passed')
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]
                                       
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 -10, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                           
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "card":
            y_a4 -= 25
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 420+y_a4-10, 'Daily Zone Report : Total-Card Sales')
            mycanvas.line(200, 415+y_a4-10, 400, 415+y_a4-10)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 350, '{----------There is no report to show----------}')

            else:
               
                mycanvas.setFont('Helvetica', 10)  

                mycanvas.drawString(110-x_a4, 375+y_a4, 'Items')

                mycanvas.drawString(192-x_a4, 365+y_a4, '1000ml')
                mycanvas.drawString(192+80-x_a4, 365+y_a4, '500ml')
                mycanvas.drawString(272+80-x_a4, 365+y_a4, '250ml')
                mycanvas.drawString(322+80-x_a4, 365+y_a4, '200ml')
                mycanvas.drawString(402+80-x_a4, 365+y_a4, '120ml')
                mycanvas.drawString(472+80-x_a4, 365+y_a4, '5000ml')
                mycanvas.drawString(545+80-x_a4, 375+y_a4, ' TOTAL')
                mycanvas.drawString(545+80-x_a4, 365+y_a4, 'LITTERS')
                mycanvas.setLineWidth(0)

                mycanvas.line(10, 390+y_a4, 585, 390+y_a4)
                mycanvas.line(10, 355+y_a4, 585, 355+y_a4)
                y = 335+y_a4
                y_line = 390+y_a4
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                        print('passed')
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]
                                       
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 -10, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]
                            
                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                       
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "total_sale":
            y_a4 -= 25
            x_a4 = 40
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 185+y_a4, 'Daily Zone Report : Total Sales')
            mycanvas.line(200, 180+y_a4, 400, 180+y_a4)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 130, '{----------There is no report to show----------}')
            else:
                # Table Header
                mycanvas.setLineWidth(0)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica', 10)

                mycanvas.drawString(15, 140+y_a4, 'Items')

                mycanvas.drawString(105-x_a4, 140+y_a4, '1000ml')
                mycanvas.drawString(100-x_a4, 130+y_a4, '  Cash')
               
                mycanvas.drawString(105+80-x_a4-10-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(100+80-x_a4-10-10-10, 130+y_a4, '  Cash')

                mycanvas.drawString(200+60-x_a4-20-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(195+60-x_a4-20-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(270+60-x_a4-30-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(265+60-x_a4-30-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(340+60-x_a4-40-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(335+60-x_a4-40-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(410+60-x_a4-50-10-10, 140+y_a4, '200ml')
                mycanvas.drawString(405+60-x_a4-50-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(480+60-x_a4-60-10-10, 140+y_a4, '120ml')
                mycanvas.drawString(475+60-x_a4-60-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(545+60-x_a4-70-10-10, 140+y_a4, '5000ml')
                mycanvas.drawString(540+60-x_a4-70-10-10, 130+y_a4, ' Cash')

                mycanvas.line(10, 155+y_a4, 585, 155+y_a4)
                mycanvas.line(10, 120+y_a4, 585, 120+y_a4)

                mycanvas.drawString(620+60-x_a4-80-10-10, 140+y_a4, ' TOTAL')
                mycanvas.drawString(620+60-x_a4-80-10-10, 130+y_a4, 'LITTERS')

                y = 100+y_a4
                y_line = 155+y_a4
                x_line = 30

                # -----------------------------------------------------------------------------------------------------------------------------------------#

                # lines#
                mycanvas.line(x_line + 5-25, y_line, x_line + 5-25, y_line - 205)
                mycanvas.line(x_line + 75-50, y_line, x_line + 75-50, y_line - 205)
               
                mycanvas.line(x_line + 145-70, y_line, x_line + 145-70, y_line - 205)
                mycanvas.line(x_line + 145+80-100, y_line, x_line + 145+80-100, y_line - 205)
                mycanvas.line(x_line + 215+80-110, y_line, x_line + 215+80-110, y_line - 205)
                mycanvas.line(x_line + 285+80-120, y_line, x_line + 285+80-120, y_line - 205)
                mycanvas.line(x_line + 355+80-130, y_line, x_line + 355+80-130, y_line - 205)
                mycanvas.line(x_line + 425+80-140, y_line, x_line + 425+80-140, y_line - 205)
                mycanvas.line(x_line + 495+80-150, y_line, x_line + 495+80-150, y_line - 205)
                mycanvas.line(x_line + 565+80-160, y_line, x_line + 565+80-160, y_line - 205)
                mycanvas.line(x_line + 650+80-175, y_line, x_line + 650+80-175, y_line - 205)
                #             mycanvas.line(x_line+660,y_line,x_line+660,y_line-107)

                y_line -= 50
                mycanvas.setFont('Helvetica', 8)
                total_1000 = 0
                total_500_cash = 0
                total_500_card = 0
                total_250_cash = 0
                total_250_card = 0
                total_200 = 0
                total_150 = 0
                total_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.drawString(15, y, str(products))
                    total_litter_line = 0
                    x_1000 = 180+20-70
                    x_500 = 180+80-97
                    x_250 = 280+80-117
                    x_200 = 380+80 - 137
                    x_150 = 430+80 - 147
                    x_5000 = 620+80 - 157
                    x_total_litter_line = 610 - 172

                    if not products in data_dict["final_results"][data]:
                        pass
                    #                     if products == "TM" or products == "SM" or products == "FCM":
                    #                         y -= 15
                    #                         continue
                    #                     continue

                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                           
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_1000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_1000 += data_dict["final_results"][data][products][quantity][
                                                    types]
                                               

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        if types == "card":
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        mycanvas.drawRightString(x_500 - 10 + x_adjust, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        x_500 += 50
                                                        x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            mycanvas.drawRightString(x_500, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        else:
                                                            x_500 += 50
                                                            mycanvas.drawRightString(x_500 + 40, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    if types == "card":
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    mycanvas.drawRightString(x_250 + 30 + x_adjust, y, str(
                                                        data_dict["final_results"][data][products][quantity][types]))
                                                    x_250 += 50
                                                    x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        x_250 += 50
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_200 + 70, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_200 += data_dict["final_results"][data][products][quantity][types]
                                                x_200 += 50

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:

                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_150 + 90, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_150 += data_dict["final_results"][data][products][quantity][types]
                                                x_150 += 50
                                               
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         for types in data_dict["final_results"][data][products][quantity]:
                            #             if data_dict["final_results"][data][products][quantity][types] != 0 and \
                            #                     data_dict["final_results"][data][products][quantity][types] != None:
                            #                 if types == "total":
                            #                     total_litter_line += \
                            #                     data_dict["final_results"][data][products][quantity][
                            #                         types]
                            #                 else:
                            #                     mycanvas.drawRightString(x_100 - 30, y, str(
                            #                         data_dict["final_results"][data][products][quantity][types]))
                            #                     total_100 += data_dict["final_results"][data][products][quantity][
                            #                         types]

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_5000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_5000 += data_dict["final_results"][data][products][quantity][
                                                    types]

                    mycanvas.drawRightString(x_total_litter_line + 65+80, y, str(total_litter_line))
                    grand_total += total_litter_line

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line + 65+80, y - 5, str(grand_total))
                mycanvas.drawRightString(x_total_litter_line - 90+105, y - 5, str(total_150))
                mycanvas.drawRightString(x_total_litter_line - 160+115, y - 5, str(total_200))
                mycanvas.drawRightString(x_total_litter_line - 230+125, y - 5, str(total_250_card))
                mycanvas.drawRightString(x_total_litter_line - 300+135, y - 5, str(total_250_cash))
                mycanvas.drawRightString(x_total_litter_line - 370+145, y - 5, str(total_500_card))
                mycanvas.drawRightString(x_total_litter_line - 440+155, y - 5, str(total_500_cash))
                mycanvas.drawRightString(x_total_litter_line - 20+95, y - 5, str(total_5000))
                mycanvas.drawRightString(x_total_litter_line - 335, y - 5, str(total_1000))
                mycanvas.drawRightString(x_total_litter_line - 385, y - 5, "Grand Total")
                #             grand_total += data_dict[data]["products_total"]
                #             mycanvas.drawRightString(x_total_litter_line+75,y+10,str(data_dict[data]["products_total"]))
                #             y -= 10
                mycanvas.line(10, y + 8, 585, y + 8)
                mycanvas.line(10, y - 15, 585, y - 15)
               
    mycanvas.setFont('Times-Italic', 12)      
    indian = pytz.timezone('Asia/Kolkata')          
    mycanvas.drawRightString(585, 5,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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


def serve_route_wise_sale_for_selected_session(date, session, user_name):
    date = date
    session_id = session
    final_dict = {
        'date': date,
        'session': session_id,
        'final_results': {'cash': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0,'500': 0, 'total': 0},
                                   'CURD': {'500': 0, '120': 0, '100': 0,'5000':0, 'total': 0},
                                   'BtrMlk':{'200': 0,'total':0},
                                   'Lassi': {'200': 0,'total':0},
                                   'CanMlk': {'1000': 0, 'total':0},
                                   'BmJar': {'200': 0, 'total': 0 }, 
                                   'BMJF': {'200': 0, 'total': 0 }
                                   },
                          
                          'card': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0,'500': 0, 'total': 0},
                                   'CURD': {'500': 0, '120': 0, '100': 0, '5000':0, 'total': 0},
                                   'BtrMlk': {'200': 0,'total':0},
                                   'Lassi': {'200': 0,'total':0},
                                   'CanMlk': {'1000': 0, 'total':0},
                                   'BmJar': {'200': 0, 'total': 0 },
                                   'BMJF': {'200': 0, 'total': 0 }
                                   },
                          
                          'total_sale': {'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                                                '250': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                 '500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                   '500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                                                  '120': {'cash': 0, 'card': 0, 'total': 0},
                                                  '500': {'cash': 0, 'card': 0, 'total': 0},
                                                  '5000': {'cash': 0, 'card': 0, 'total': 0}}, 
                                         'BtrMlk': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'Lassi': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'CanMlk': {'1000': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BmJar': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BMJF': {'200': {'cash': 0, 'card': 0, 'total': 0}}
                                        }
    }}
        
    for route in Route.objects.filter(is_temp_route=False, session_id=session_id).order_by('name'):
        final_dict[route.id] = {'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                                       '250': {'cash': 0, 'card': 0, 'total': 0}},
                                
                                'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},
                                
                                'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                        '500': {'cash': 0, 'card': 0, 'total': 0}},

                                'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                          '500': {'cash': 0, 'card': 0, 'total': 0}},        
                                
                                'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                                         '120': {'cash': 0, 'card': 0, 'total': 0},
                                         '500': {'cash': 0, 'card': 0, 'total': 0},
                                         '5000': {'cash': 0, 'card': 0, 'total': 0}},
                                
                                'BtrMlk': {'200':{'cash': 0, 'card': 0, 'total': 0}},
                                
                                'Lassi': {'200':{'cash': 0, 'card': 0, 'total': 0}},

                                'CanMlk': {'1000': {'cash': 0, 'card': 0, 'total': 0}},

                                'BmJar': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                
                                'BMJF': {'200': {'cash': 0, 'card': 0, 'total': 0}}
                               }
        final_dict[route.id]['products_total'] = 0
        final_dict[route.id]['route_name'] = route.name
    dsrs_obj = DailySessionllyRoutellySale.objects.filter(delivery_date=date, session_id=session_id)
    card_sale_obj = dsrs_obj.filter(sold_to='ICustomer')
    cash_sale_obj = dsrs_obj.filter(sold_to__in=['Agent',"Leakage"])
    # SM
    sm_500_cash_total = cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
    sm_500_card_total = card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']

    final_dict['final_results']['cash']['SM']['500'] = round(sm_500_cash_total, 3)
    final_dict['final_results']['card']['SM']['500'] = round(sm_500_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['500']['card'] = round(sm_500_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['500']['cash'] = round(sm_500_cash_total, 3)

    sm_250_cash_total = cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
    sm_250_card_total = card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
    final_dict['final_results']['cash']['SM']['250'] = round(sm_250_cash_total, 3)
    final_dict['final_results']['card']['SM']['250'] = round(sm_250_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['250']['card'] = round(sm_250_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['250']['cash'] = round(sm_250_cash_total, 3)

    # Total
    final_dict['final_results']['cash']['SM']['total'] = final_dict['final_results']['cash']['SM']['500'] + \
                                                         final_dict['final_results']['cash']['SM']['250']
    final_dict['final_results']['card']['SM']['total'] = final_dict['final_results']['card']['SM']['500'] + \
                                                         final_dict['final_results']['card']['SM']['250']
    final_dict['final_results']['total_sale']['SM']['500']['total'] = \
    final_dict['final_results']['total_sale']['SM']['500']['card'] + \
    final_dict['final_results']['total_sale']['SM']['500']['cash']
    final_dict['final_results']['total_sale']['SM']['250']['total'] = \
    final_dict['final_results']['total_sale']['SM']['250']['card'] + \
    final_dict['final_results']['total_sale']['SM']['250']['cash']

    # TM
    tm_500_cash_total = cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    tm_500_card_total = card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    final_dict['final_results']['cash']['TM']['500'] = round(tm_500_cash_total, 3)
    final_dict['final_results']['card']['TM']['500'] = round(tm_500_card_total, 3)
    final_dict['final_results']['total_sale']['TM']['500']['card'] = round(tm_500_card_total, 3)
    final_dict['final_results']['total_sale']['TM']['500']['cash'] = round(tm_500_cash_total, 3)

    final_dict['final_results']['cash']['TM']['total'] = final_dict['final_results']['cash']['TM']['500']
    final_dict['final_results']['card']['TM']['total'] = final_dict['final_results']['card']['TM']['500']
    final_dict['final_results']['total_sale']['TM']['500']['total'] = \
    final_dict['final_results']['total_sale']['TM']['500']['card'] + \
    final_dict['final_results']['total_sale']['TM']['500']['cash']

    #  FCM
    fcm_500_cash_total = cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
    fcm_500_card_total = card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
    final_dict['final_results']['cash']['FCM']['500'] = round(fcm_500_cash_total, 3)
    final_dict['final_results']['card']['FCM']['500'] = round(fcm_500_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['500']['card'] = round(fcm_500_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['500']['cash'] = round(fcm_500_cash_total, 3)
    
    fcm_1000_cash_total = cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
    fcm_1000_card_total = card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
    final_dict['final_results']['cash']['FCM']['1000'] = round(fcm_1000_cash_total, 3)
    final_dict['final_results']['card']['FCM']['1000'] = round(fcm_1000_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['1000']['card'] = round(fcm_1000_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['1000']['cash'] = round(fcm_1000_cash_total, 3)

    final_dict['final_results']['cash']['FCM']['total'] = final_dict['final_results']['cash']['FCM']['500'] + final_dict['final_results']['cash']['FCM']['1000']
    final_dict['final_results']['card']['FCM']['total'] = final_dict['final_results']['card']['FCM']['500'] + final_dict['final_results']['card']['FCM']['1000']
    final_dict['final_results']['total_sale']['FCM']['500']['total'] = \
    final_dict['final_results']['total_sale']['FCM']['500']['card'] + \
    final_dict['final_results']['total_sale']['FCM']['500']['cash']
    final_dict['final_results']['total_sale']['FCM']['1000']['total'] = \
    final_dict['final_results']['total_sale']['FCM']['1000']['card'] + \
    final_dict['final_results']['total_sale']['FCM']['1000']['cash']

     #  TMATE
    tea_500_cash_total = cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
    tea_500_card_total = card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
    final_dict['final_results']['cash']['TMATE']['500'] = round(tea_500_cash_total, 3)
    final_dict['final_results']['card']['TMATE']['500'] = round(tea_500_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['500']['card'] = round(tea_500_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['500']['cash'] = round(tea_500_cash_total, 3)

    tea_1000_cash_total = cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
    tea_1000_card_total = card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
    final_dict['final_results']['cash']['TMATE']['1000'] = round(tea_1000_cash_total, 3)
    final_dict['final_results']['card']['TMATE']['1000'] = round(tea_1000_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['1000']['card'] = round(tea_1000_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['1000']['cash'] = round(tea_1000_cash_total, 3)

    final_dict['final_results']['cash']['TMATE']['total'] = final_dict['final_results']['cash']['TMATE']['500'] + final_dict['final_results']['cash']['TMATE']['1000']
    final_dict['final_results']['card']['TMATE']['total'] = final_dict['final_results']['card']['TMATE']['500'] + final_dict['final_results']['card']['TMATE']['1000']
    final_dict['final_results']['total_sale']['TMATE']['500']['total'] = \
    final_dict['final_results']['total_sale']['TMATE']['500']['card'] + \
    final_dict['final_results']['total_sale']['TMATE']['500']['cash']
    final_dict['final_results']['total_sale']['TMATE']['1000']['total'] = \
    final_dict['final_results']['total_sale']['TMATE']['1000']['card'] + \
    final_dict['final_results']['total_sale']['TMATE']['1000']['cash']

    
    # CANMILK
    can_cash_total = cash_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum'] + cash_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum'] +cash_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
    can_card_total = card_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum'] + card_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum'] +card_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
    final_dict['final_results']['cash']['CanMlk']['1000'] = round(can_cash_total, 3)
    final_dict['final_results']['card']['CanMlk']['1000'] = round(can_card_total, 3)
    final_dict['final_results']['total_sale']['CanMlk']['1000']['cash'] = round(can_cash_total, 3)
    final_dict['final_results']['total_sale']['CanMlk']['1000']['card'] = round(can_card_total, 3)

    final_dict['final_results']['cash']['CanMlk']['total'] = final_dict['final_results']['cash']['CanMlk']['1000']
    final_dict['final_results']['card']['CanMlk']['total'] = final_dict['final_results']['card']['CanMlk']['1000']
    final_dict['final_results']['total_sale']['CanMlk']['1000']['total'] = \
    final_dict['final_results']['total_sale']['CanMlk']['1000']['card'] + \
    final_dict['final_results']['total_sale']['CanMlk']['1000']['cash']

    
    # Butter_milk
    buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
    buttermilk200_card_total = card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
    final_dict['final_results']['cash']['BtrMlk']['200'] = buttermilk200_cash_total
    final_dict['final_results']['card']['BtrMlk']['200'] = buttermilk200_card_total 
    final_dict['final_results']['total_sale']['BtrMlk']['200']['card'] = round(buttermilk200_card_total, 3)
    final_dict['final_results']['total_sale']['BtrMlk']['200']['cash'] = round(buttermilk200_cash_total, 3)

    final_dict['final_results']['cash']['BtrMlk']['total'] = final_dict['final_results']['cash']['BtrMlk']['200']
    final_dict['final_results']['card']['BtrMlk']['total'] = final_dict['final_results']['card']['BtrMlk']['200']
    final_dict['final_results']['total_sale']['BtrMlk']['200']['total'] = \
    final_dict['final_results']['total_sale']['BtrMlk']['200']['card'] + \
    final_dict['final_results']['total_sale']['BtrMlk']['200']['cash']

    # Butter_milk_jar
    buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
    buttermilk200_card_total = card_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
    final_dict['final_results']['cash']['BmJar']['200'] = buttermilk200_cash_total
    final_dict['final_results']['card']['BmJar']['200'] = buttermilk200_card_total 
    final_dict['final_results']['total_sale']['BmJar']['200']['card'] = round(buttermilk200_card_total, 3)
    final_dict['final_results']['total_sale']['BmJar']['200']['cash'] = round(buttermilk200_cash_total, 3)

    final_dict['final_results']['cash']['BmJar']['total'] = final_dict['final_results']['cash']['BmJar']['200']
    final_dict['final_results']['card']['BmJar']['total'] = final_dict['final_results']['card']['BmJar']['200']
    final_dict['final_results']['total_sale']['BmJar']['200']['total'] = \
    final_dict['final_results']['total_sale']['BmJar']['200']['card'] + \
    final_dict['final_results']['total_sale']['BmJar']['200']['cash']

    # Butter_milk_jar free
    buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
    buttermilk200_card_total = card_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
    final_dict['final_results']['cash']['BMJF']['200'] = buttermilk200_cash_total
    final_dict['final_results']['card']['BMJF']['200'] = buttermilk200_card_total 
    final_dict['final_results']['total_sale']['BMJF']['200']['card'] = round(buttermilk200_card_total, 3)
    final_dict['final_results']['total_sale']['BMJF']['200']['cash'] = round(buttermilk200_cash_total, 3)

    final_dict['final_results']['cash']['BMJF']['total'] = final_dict['final_results']['cash']['BMJF']['200']
    final_dict['final_results']['card']['BMJF']['total'] = final_dict['final_results']['card']['BMJF']['200']
    final_dict['final_results']['total_sale']['BMJF']['200']['total'] = \
    final_dict['final_results']['total_sale']['BMJF']['200']['card'] + \
    final_dict['final_results']['total_sale']['BMJF']['200']['cash']
        
    #lassi
    lassi200_cash_total = cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
    lassi200_card_total = card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
    final_dict['final_results']['cash']['Lassi']['200'] = lassi200_card_total
    final_dict['final_results']['card']['Lassi']['200'] = lassi200_card_total
    final_dict['final_results']['total_sale']['Lassi']['200']['cash'] = lassi200_cash_total
    final_dict['final_results']['total_sale']['Lassi']['200']['card'] = lassi200_card_total 

    final_dict['final_results']['cash']['Lassi']['total'] = final_dict['final_results']['cash']['Lassi']['200']
    final_dict['final_results']['card']['Lassi']['total'] = final_dict['final_results']['card']['Lassi']['200']
    final_dict['final_results']['total_sale']['Lassi']['200']['total'] = \
    final_dict['final_results']['total_sale']['Lassi']['200']['card'] + \
    final_dict['final_results']['total_sale']['Lassi']['200']['cash']

    # CURD
    curd_500_cash_total = cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd_500_card_total = card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    final_dict['final_results']['cash']['CURD']['500'] = round(curd_500_cash_total, 3)
    final_dict['final_results']['card']['CURD']['500'] = round(curd_500_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['500']['card'] = round(curd_500_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['500']['cash'] = round(curd_500_cash_total, 3)

    curd_150_cash_total = cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
    curd_150_card_total = card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
    final_dict['final_results']['cash']['CURD']['120'] = round(curd_150_cash_total, 3)
    final_dict['final_results']['card']['CURD']['120'] = round(curd_150_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['120']['card'] = round(curd_150_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['120']['cash'] = round(curd_150_cash_total, 3)
    
    curd_100_cash_total = cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
    curd_100_card_total = card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
    final_dict['final_results']['cash']['CURD']['100'] = round(curd_100_cash_total, 3)
    final_dict['final_results']['card']['CURD']['100'] = round(curd_100_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['100']['card'] = round(curd_100_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['100']['cash'] = round(curd_100_cash_total, 3)

    curd_5000_cash_total = cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    curd_5000_card_total = card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    final_dict['final_results']['cash']['CURD']['5000'] = round(curd_5000_cash_total, 3)
    final_dict['final_results']['card']['CURD']['5000'] = round(curd_5000_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['5000']['card'] = round(curd_5000_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['5000']['cash'] = round(curd_5000_cash_total, 3)

    # Total
    final_dict['final_results']['cash']['CURD']['total'] = final_dict['final_results']['cash']['CURD']['500'] + \
                                                           final_dict['final_results']['cash']['CURD']['5000'] + \
                                                           final_dict['final_results']['cash']['CURD']['120'] + final_dict['final_results']['cash']['CURD']['100']
    final_dict['final_results']['card']['CURD']['total'] = final_dict['final_results']['card']['CURD']['500'] + \
                                                           final_dict['final_results']['card']['CURD']['5000'] + \
                                                           final_dict['final_results']['card']['CURD']['120'] + final_dict['final_results']['card']['CURD']['100']
    final_dict['final_results']['total_sale']['CURD']['500']['total'] = \
    final_dict['final_results']['total_sale']['CURD']['500']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['500']['cash']
    final_dict['final_results']['total_sale']['CURD']['120']['total'] = \
    final_dict['final_results']['total_sale']['CURD']['120']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['120']['cash']
    final_dict['final_results']['total_sale']['CURD']['100']['total'] = \
    final_dict['final_results']['total_sale']['CURD']['100']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['100']['cash']
    final_dict['final_results']['total_sale']['CURD']['5000']['total'] = \
    final_dict['final_results']['total_sale']['CURD']['5000']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['5000']['cash']
        
        

    # route wise report
    for route in Route.objects.filter(is_temp_route=False, session_id=session_id):
        product_total = 0
        if dsrs_obj.filter(route=route).count() > 0:
            card_sale_obj = dsrs_obj.filter(sold_to='ICustomer', route=route)
            cash_sale_obj = dsrs_obj.filter(sold_to__in=['Agent','Leakage'], route=route)

            # SM
            if cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] is None:
                sm_500_cash_total = 0
            else:
                sm_500_cash_total = cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            if card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] is None:
                sm_500_card_total = 0
            else:
                sm_500_card_total = card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            sm_500_cash_total_count = cash_sale_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            sm_500_card_total_count = card_sale_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            final_dict[route.id]['SM']['500']['card'] = sm_500_card_total_count
            final_dict[route.id]['SM']['500']['cash'] = sm_500_cash_total_count

            if cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] is None:
                sm_250_cash_total = 0
            else:
                sm_250_cash_total = cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            if card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] is None:
                sm_250_card_total = 0
            else:
                sm_250_card_total = card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            sm_250_cash_total_count = cash_sale_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            sm_250_card_total_count = card_sale_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            final_dict[route.id]['SM']['250']['card'] = sm_250_card_total_count
            final_dict[route.id]['SM']['250']['cash'] = sm_250_cash_total_count

            # Total

            total_sm_500_litre = round(Decimal(sm_500_cash_total + sm_500_card_total), 3)
            total_sm_250_litre = round(Decimal(sm_250_cash_total + sm_250_card_total), 3)
            final_dict[route.id]['SM']['500']['total'] = total_sm_500_litre
            final_dict[route.id]['SM']['250']['total'] = total_sm_250_litre
            product_total += total_sm_500_litre + total_sm_250_litre

            #       TM
            if cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] is None:
                tm_500_cash_total = 0
            else:
                tm_500_cash_total = cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            if card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] is None:
                tm_500_card_total = 0
            else:
                tm_500_card_total = card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            tm_500_cash_total_count = cash_sale_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            tm_500_card_total_count = card_sale_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            final_dict[route.id]['TM']['500']['card'] = tm_500_card_total_count
            final_dict[route.id]['TM']['500']['cash'] = tm_500_cash_total_count

            # Total
            total_tm_500_litre = round(Decimal(tm_500_cash_total + tm_500_card_total), 3)
            final_dict[route.id]['TM']['500']['total'] = total_tm_500_litre
            product_total += total_tm_500_litre

            #       TMATE
            if cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] is None:
                tea_500_cash_total = 0
            else:
                tea_500_cash_total = cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            if card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] is None:
                tea_500_card_total = 0
            else:
                tea_500_card_total = card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            tea_500_cash_total_count = cash_sale_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            tea_500_card_total_count = card_sale_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            final_dict[route.id]['TMATE']['500']['card'] = tea_500_card_total_count
            final_dict[route.id]['TMATE']['500']['cash'] = tea_500_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum'] is None:
                tea_1000_cash_total = 0
            else:
                tea_1000_cash_total = cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            if card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum'] is None:
                tea_1000_card_total = 0
            else:
                tea_1000_card_total = card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            tea_1000_cash_total_count = cash_sale_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            tea_1000_card_total_count = card_sale_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            final_dict[route.id]['TMATE']['1000']['card'] = tea_1000_card_total_count
            final_dict[route.id]['TMATE']['1000']['cash'] = tea_1000_cash_total_count

            # Total
            total_tea_500_litre = round(Decimal(tea_500_cash_total + tea_500_card_total), 3)
            total_tea_1000_litre = round(Decimal(tea_1000_cash_total + tea_1000_card_total), 3)
            final_dict[route.id]['TMATE']['500']['total'] = total_tea_500_litre
            final_dict[route.id]['TMATE']['1000']['total'] = total_tea_1000_litre
            product_total += total_tea_500_litre + total_tea_1000_litre

            #       FCM
            if cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] is None:
                fcm_500_cash_total = 0
            else:
                fcm_500_cash_total = cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            if card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] is None:
                fcm_500_card_total = 0
            else:
                fcm_500_card_total = card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            fcm_500_cash_total_count = cash_sale_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            fcm_500_card_total_count = card_sale_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            final_dict[route.id]['FCM']['500']['card'] = fcm_500_card_total_count
            final_dict[route.id]['FCM']['500']['cash'] = fcm_500_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] is None:
                fcm_1000_cash_total = 0
            else:
                fcm_1000_cash_total = cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            if card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] is None:
                fcm_1000_card_total = 0
            else:
                fcm_1000_card_total = card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            fcm_1000_cash_total_count = cash_sale_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            fcm_1000_card_total_count = card_sale_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            final_dict[route.id]['FCM']['1000']['card'] = fcm_1000_card_total_count
            final_dict[route.id]['FCM']['1000']['cash'] = fcm_1000_cash_total_count

            # Total
            total_fcm_500_litre = round(Decimal(fcm_500_cash_total + fcm_500_card_total), 3)
            total_fcm_1000_litre = round(Decimal(fcm_1000_cash_total + fcm_1000_card_total), 3)
            final_dict[route.id]['FCM']['500']['total'] = total_fcm_500_litre
            final_dict[route.id]['FCM']['1000']['total'] = total_fcm_1000_litre
            product_total += total_fcm_500_litre + total_fcm_1000_litre


            #       CAN
            tm_can = cash_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
            sm_can = cash_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
            fcm_can = cash_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum'] 
            if tm_can is None:
                tm_can = 0
            if sm_can is None:
                sm_can = 0
            if fcm_can is None:
                fcm_can = 0
            can_cash_total = tm_can + sm_can + fcm_can

            tm_can = card_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
            sm_can = card_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
            fcm_can = card_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum'] 

            if tm_can is None:
                tm_can = 0
            if sm_can is None:
                sm_can = 0
            if fcm_can is None:
                fcm_can = 0
            can_card_total = tm_can + sm_can + fcm_can

            can_cash_total_count = round(can_cash_total)
            can_card_total_count = round(can_card_total)
            print(can_cash_total_count)
            final_dict[route.id]['CanMlk']['1000']['card'] = can_card_total_count
            final_dict[route.id]['CanMlk']['1000']['cash'] = can_cash_total_count

            # Total
            can_total_litre = round(Decimal(can_cash_total + can_card_total), 3)
            final_dict[route.id]['CanMlk']['1000']['total'] = can_total_litre
            product_total += can_total_litre
        
            #Lassi
            if cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum'] is None:
                lassi200_cash_total = 0
            else:
                lassi200_cash_total = cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            if card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum'] is None:
                lassi200_card_total = 0
            else:
                lassi200_card_total = card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            lassi200_cash_total_count = cash_sale_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            lassi200_card_total_count = card_sale_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            final_dict[route.id]['Lassi']['200']['card'] = lassi200_card_total_count
            final_dict[route.id]['Lassi']['200']['cash'] = lassi200_cash_total_count

            # Total
            total_lassi200_litre = round(Decimal(lassi200_card_total + lassi200_cash_total), 3)
            final_dict[route.id]['Lassi']['200']['total'] = total_lassi200_litre
            product_total += total_lassi200_litre
        
            
            #Butter_milk
            if cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum'] is None:
                buttermilk200_cash_total = 0
            else:
                buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            if card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum'] is None:
                buttermilk200_total = 0
            else:
                buttermilk200_card_total = card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            buttermilk200_cash_total_count = cash_sale_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            buttermilk200_card_total_count = card_sale_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            final_dict[route.id]['BtrMlk']['200']['card'] = buttermilk200_card_total_count
            final_dict[route.id]['BtrMlk']['200']['cash'] = buttermilk200_cash_total_count

            # Total
            total_buttermilk200_litre = round(Decimal(buttermilk200_card_total + buttermilk200_cash_total), 3)
            final_dict[route.id]['BtrMlk']['200']['total'] = total_buttermilk200_litre
            product_total += total_buttermilk200_litre


            #Butter_milk_jar
            if cash_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum'] is None:
                buttermilk200_cash_total = 0
            else:
                buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
            if card_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum'] is None:
                buttermilk200_total = 0
            else:
                buttermilk200_card_total = card_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
            buttermilk200_cash_total_count = cash_sale_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            buttermilk200_card_total_count = card_sale_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            final_dict[route.id]['BmJar']['200']['card'] = buttermilk200_card_total_count
            final_dict[route.id]['BmJar']['200']['cash'] = buttermilk200_cash_total_count

            # Total
            total_bm_jar200_litre = round(Decimal(buttermilk200_card_total + buttermilk200_cash_total), 3)
            final_dict[route.id]['BmJar']['200']['total'] = total_bm_jar200_litre
            product_total += total_bm_jar200_litre


            #Butter_milk_jar free
            if cash_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum'] is None:
                buttermilk200_cash_total = 0
            else:
                buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
            if card_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum'] is None:
                buttermilk200_total = 0
            else:
                buttermilk200_card_total = card_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
            buttermilk200_cash_total_count = cash_sale_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            buttermilk200_card_total_count = card_sale_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            final_dict[route.id]['BMJF']['200']['card'] = buttermilk200_card_total_count
            final_dict[route.id]['BMJF']['200']['cash'] = buttermilk200_cash_total_count

            # Total
            total_bmjf200_litre = round(Decimal(buttermilk200_card_total + buttermilk200_cash_total), 3)
            final_dict[route.id]['BMJF']['200']['total'] = total_bmjf200_litre
            product_total += total_bmjf200_litre
        
            
            #       CURD
            if cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] is None:
                curd_500_cash_total = 0
            else:
                curd_500_cash_total = cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] is None:
                curd_500_card_total = 0
            else:
                curd_500_card_total = card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            curd_500_cash_total_count = cash_sale_obj.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
            curd_500_card_total_count = card_sale_obj.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
            final_dict[route.id]['CURD']['500']['card'] = curd_500_card_total_count
            final_dict[route.id]['CURD']['500']['cash'] = curd_500_cash_total_count

            if cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] is None:
                curd_150_cash_total = 0
            else:
                curd_150_cash_total = cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] is None:
                curd_150_card_total = 0
            else:
                curd_150_card_total = card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            curd_150_cash_total_count = cash_sale_obj.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
            curd_150_card_total_count = card_sale_obj.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
            final_dict[route.id]['CURD']['120']['card'] = curd_150_card_total_count
            final_dict[route.id]['CURD']['120']['cash'] = curd_150_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] is None:
                curd_100_cash_total = 0
            else:
                curd_100_cash_total = cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            if card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] is None:
                curd_100_card_total = 0
            else:
                curd_100_card_total = card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            curd_100_cash_total_count = cash_sale_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            curd_100_card_total_count = card_sale_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            final_dict[route.id]['CURD']['100']['card'] = curd_100_card_total_count
            final_dict[route.id]['CURD']['100']['cash'] = curd_100_cash_total_count

# curd 5000
            if cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum'] is None:
                curd_5000_cash_total = 0
            else:
                curd_5000_cash_total = cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum'] is None:
                curd_5000_card_total = 0
            else:
                curd_5000_card_total = card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            curd_5000_cash_total_count = cash_sale_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            curd_5000_card_total_count = card_sale_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            final_dict[route.id]['CURD']['5000']['card'] = curd_5000_card_total_count
            final_dict[route.id]['CURD']['5000']['cash'] = curd_5000_cash_total_count


            # Total
            total_curd_500_litre = round(Decimal(curd_500_cash_total + curd_500_card_total), 3)
            total_curd_150_litre = round(Decimal(curd_150_cash_total + curd_150_card_total), 3)
            total_curd_100_litre = round(Decimal(curd_100_cash_total + curd_100_card_total), 3)
            total_curd_5000_litre = round(Decimal(curd_5000_cash_total + curd_5000_card_total), 3)
            final_dict[route.id]['CURD']['500']['total'] = total_curd_500_litre
            final_dict[route.id]['CURD']['120']['total'] = total_curd_150_litre
            final_dict[route.id]['CURD']['100']['total'] = total_curd_100_litre
            final_dict[route.id]['CURD']['5000']['total'] = total_curd_5000_litre
            product_total += total_curd_500_litre + total_curd_150_litre + total_curd_100_litre+ total_curd_5000_litre

            final_dict[route.id]['products_total'] = round(Decimal(product_total), 3)
    data = generate_pdf_for_route_wise_sale_details(final_dict, user_name)
    return data



def generate_pdf_for_route_wise_sale_details(data_dict, user_name):
    session_name = Session.objects.get(id=data_dict["session"]).name
    file_name = str(data_dict['date']) + '_' + str(session_name) + '_daily_all_route_details' + '.pdf'
    file_path = os.path.join('static/media/route_wise_report/', file_name)
#     file_path = os.path.join('static/media', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))

    # _Head_lines_#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
    y_a4= 20
   
    date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
    date = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
   
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
   
    mycanvas.drawCentredString(300, 795, 'Daily Route Report : Total Sales ( '+ str(date) + ", "+str(session_name)+" )")
#     mycanvas.line(246-50, 792, 452-50, 792)

    x_a4 = 50
    y_a4 = 80
    # Table Header
    mycanvas.setLineWidth(0)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
    mycanvas.drawString(35-20, 655+y_a4, 'No')
    mycanvas.drawString(60-20, 655+y_a4, 'Zone')
    mycanvas.drawString(95-20, 665+y_a4, 'Items')

    mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
    mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

    mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
    mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')
   
    mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

    mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
    mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(470-20-x_a4, 650+y_a4, '120ml')
    mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
    mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

    mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
    mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

    mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
    mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
    mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
    mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

    products_list = ["TM", "SM", "FCM", "TMATE" ,"CanMlk", "CURD", "BtrMlk", "BmJar", "BMJF", "Lassi"]
#     quantity_list = ["1000", "500", "250", "200", "150","100"]
    quantity_list = ["1000","500", "250", "200", "120","5000"]
    route_list = list(Route.objects.all().values_list("name",flat=True))

    index = 1
    y = 620+y_a4
    y_line = 690+y_a4
    x_line = 30
    grand_total = 0
    mycanvas.setFont('Helvetica', 8)
   
    current_route = ""

    for data in data_dict:
        if data == "date" or data == "session" or data == "final_results" or data_dict[data]["products_total"] == 0:
            continue
        mycanvas.drawString(13, y, str(index))
        #         mycanvas.drawString(75, y,str(data))

        # -----------------------------------------------------------------------------------------------------------------------------------------#
        # lines#
        mycanvas.line(x_line-20, y_line, x_line-20, y - 104)
        mycanvas.line(x_line, y_line, x_line, y - 104)
        mycanvas.line(x_line + 40, y_line, x_line + 40, y - 104)
        mycanvas.line(x_line + 80, y_line, x_line + 80, y - 104)
       
        mycanvas.line(x_line + 110+15, y_line - 26, x_line + 110+15, y - 104)
        mycanvas.line(x_line + 100+75, y_line - 26, x_line + 100+75, y - 104)
        mycanvas.line(x_line + 155+70, y_line - 26, x_line + 155+70, y - 104)
 
        mycanvas.line(x_line + 210+60, y_line - 26, x_line + 210+60, y - 104)
        mycanvas.line(x_line + 265+50, y_line - 26, x_line + 265+50, y - 104)
        mycanvas.line(x_line + 320+40, y_line - 26, x_line + 320+40, y - 104)
        mycanvas.line(x_line + 375+30, y_line - 26, x_line + 375+30, y - 104)
        mycanvas.line(x_line + 430+20, y_line, x_line + 430+20, y - 104)
        mycanvas.line(x_line + 430+70, y_line, x_line + 430+70, y - 104)
        mycanvas.line(x_line + 555, y_line, x_line + 555, y - 104)

        y_line -= 50
        current_route = data_dict[data]["route_name"]
        route_name = ''
        for letter in data_dict[data]["route_name"]:
            if letter == ' ':
                continue
            else:
                route_name += letter
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(30, y, str(route_name[:7]))
#         mycanvas.setFont('Helvetica', 12)
        for products in products_list:
            mycanvas.drawString(75, y, str(products))
            total_litter_line = 0
            x_1000 = 115+10
            x_500 = 105+60
            x_250 = 195+60
            x_200 = 275+60
            x_150 = 315+60
            x_5000 = 430+20
            x_total_litter_line = 520
            if not products in data_dict[data]:
                pass
            #                     if products == "TM" or products == "SM" or products == "FCM":
            #                         y -= 15
            #                         continue
            #                     continue
            if products in data_dict[data]:
                for quantity in quantity_list:
                    try:
                       
                        if quantity == "1000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_1000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_1000 += 50
                       
                        if quantity == "500":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_500 + 35, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_500 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_500 + 30, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_500 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_500 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))

                        if quantity == "250":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_250 + 40 - x_adjust, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_250 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_250 + 40, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_250 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_250 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))
                       
                        if quantity == "200":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_200 + 50, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_200 += 50

                        if quantity == "120":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_150 + 55, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_150 += 50
                       
                       
                        # if quantity == "100":
                        #     for types in data_dict[data][products][quantity]:
                        #         if types == "total":
                        #             total_litter_line += data_dict[data][products][quantity][types]
                        #         else:
                        #             if data_dict[data][products][quantity][types] != 0 and \
                        #                     data_dict[data][products][quantity][types] != None:
                        #                 mycanvas.drawRightString(x_100 + 25, y,
                        #                                          str(data_dict[data][products][quantity][types]))
                        #             x_100 += 30


                        if quantity == "5000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_5000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_5000 += 30

                       
                    except:
                        pass
            mycanvas.drawRightString(x_total_litter_line + 5, y, str(total_litter_line))
            y -= 12
        grand_total += data_dict[data]["products_total"]
        mycanvas.drawRightString(x_total_litter_line + 60, y + 10, str(data_dict[data]["products_total"]))
        y -= 10
        mycanvas.line(10, y + 13, 585, y + 13)
        # -----------------------------------------------6------------------------------------------------------#
        if index % 6 == 0:
            mycanvas.showPage()

            #     mycanvas.setStrokeColor(colors.lightgrey)
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)
            mycanvas.drawCentredString(300, 795, 'Daily Route Report : Total Sales ( '+ str(date) + ", "+str(session_name)+" )")
#             mycanvas.line(246-50, 792, 452-50, 792)

            x_a4 = 50
            y_a4 = 80
            # Table Header
            mycanvas.setLineWidth(0)
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica', 8)
            mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
            mycanvas.drawString(35-20, 655+y_a4, 'No')
            mycanvas.drawString(60-20, 655+y_a4, 'Zone')
            mycanvas.drawString(95-20, 665+y_a4, 'Items')

            mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
            mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

            mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
            mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
            mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(470-20-x_a4, 650+y_a4, '120ml')
            mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
            mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

            mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
            mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

            mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
            mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
            mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
            mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

            products_list = ["TM", "SM", "FCM", "TMATE" ,"CanMlk", "CURD", "BtrMlk", "BmJar",  "BMJF", "Lassi"]
            quantity_list = ["1000","500", "250", "200", "120","5000"]
            route_list = list(Route.objects.all().values_list("name",flat=True))

            y = 620+y_a4
            y_line = 690+y_a4
            x_line = 30
            mycanvas.setFont('Helvetica', 8)

        index += 1

    mycanvas.line(10, y + 13, 10, y - 13)
    mycanvas.line(585, y + 13, 585, y - 13)
    mycanvas.line(585, y + 13, 585, y - 13)
    mycanvas.line(10, y + 13, 585, y + 13)
    mycanvas.line(10, y - 13, 585, y - 13)
    mycanvas.drawRightString(x_total_litter_line + 60, y - 5, str(grand_total))
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(x_total_litter_line - 80, y - 5, 'Grand Total')

    # --------------------------------------------------------Final Report----------------------------------------------------#

    mycanvas.showPage()
    x_a4 = 90
    y_a4 = 120
   
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.drawCentredString(300, 795, 'Daily Route Report : Total Sales ( '+ str(date) + ", "+str(session_name)+" )")
   

    mycanvas.setFont('Helvetica', 10)
    #     mycanvas.drawString(70,655,'zone')
    mycanvas.drawString(110-x_a4, 600+y_a4, 'Items')

    mycanvas.drawString(192-x_a4, 590+y_a4, '1000ml')
    mycanvas.drawString(192+80-x_a4, 590+y_a4, '500ml')
    mycanvas.drawString(272+80-x_a4, 590+y_a4, '250ml')
    mycanvas.drawString(322+80-x_a4, 590+y_a4, '200ml')
    mycanvas.drawString(402+80-x_a4, 590+y_a4, '120ml')
    mycanvas.drawString(472+80-x_a4, 590+y_a4, '5000ml')
    mycanvas.drawString(545+80-x_a4, 600+y_a4, ' TOTAL')
    mycanvas.drawString(545+80-x_a4, 590+y_a4, 'LITTERS')
    #     mycanvas.drawString(602,620,'  NET')
    #     mycanvas.drawString(602,610,'LITTERS')

    # ------------------------------------------lines--------------------------------------------------#
    mycanvas.setLineWidth(0)
    mycanvas.line(90-x_a4+10, 615+y_a4, 615+80-x_a4-20, 615+y_a4)
    mycanvas.line(90-x_a4+10, 580+y_a4, 615+80-x_a4-20, 580+y_a4)

    #     mycanvas.drawString()

    y = 560+y_a4
    y_line = 615+y_a4
    x_line = 90-x_a4
    grand_total = 0

    for data in data_dict["final_results"]:
        mycanvas.line(x_line+10, y_line, x_line+10, y_line - 215)
        mycanvas.line(x_line + 70+10, y_line, x_line + 70+10, y_line - 215)
        mycanvas.line(x_line + 145+10, y_line, x_line + 145+10, y_line - 215)
        mycanvas.line(x_line + 145+80+10, y_line, x_line + 145+80+10, y_line - 215)

        mycanvas.line(x_line + 220+80, y_line, x_line + 220+80, y_line - 215)
        mycanvas.line(x_line + 295+80-10, y_line, x_line + 295+80-10, y_line - 215)
        mycanvas.line(x_line + 370+80-10, y_line, x_line + 370+80-10, y_line - 215)

        mycanvas.line(x_line + 445+80-20, y_line, x_line + 445+80-20, y_line - 215)
        mycanvas.line(x_line + 525+80-20, y_line, x_line + 525+80-20, y_line - 215)
        #         mycanvas.line(x_line+605,y_line,x_line+605,y_line-115)

        if data == "cash":
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 645+y_a4, 'Daily Route Report : Total-Cash Sales')
            mycanvas.line(200, 640+y_a4, 400, 640+y_a4)

            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(350, 595, 'Daily Route Report : Total-Cash Sales')
            else:
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]
                            
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 -10, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]           
                                       
                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                           
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "card":
            y_a4 -= 25
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 410+y_a4, 'Daily Route Report : Total-Card Sales')
            mycanvas.line(200, 405+y_a4, 400, 405+y_a4)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 350, '{----------There is no report to show----------}')

            else:
               
                mycanvas.setFont('Helvetica', 10)  

                mycanvas.drawString(110-x_a4, 375+y_a4, 'Items')

                mycanvas.drawString(192-x_a4, 365+y_a4, '1000ml')
                mycanvas.drawString(192+80-x_a4, 365+y_a4, '500ml')
                mycanvas.drawString(272+80-x_a4, 365+y_a4, '250ml')
                mycanvas.drawString(322+80-x_a4, 365+y_a4, '200ml')
                mycanvas.drawString(402+80-x_a4, 365+y_a4, '120ml')
                mycanvas.drawString(472+80-x_a4, 365+y_a4, '5000ml')
                mycanvas.drawString(545+80-x_a4, 375+y_a4, ' TOTAL')
                mycanvas.drawString(545+80-x_a4, 365+y_a4, 'LITTERS')
                mycanvas.setLineWidth(0)

                mycanvas.line(10, 390+y_a4, 585, 390+y_a4)
                mycanvas.line(10, 355+y_a4, 585, 355+y_a4)
                y = 335+y_a4
                y_line = 390+y_a4
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]
                                       
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 -10, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]
                           

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                           
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "total_sale":
            x_a4 = 40
            y_a4 -= 25
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 185+y_a4, 'Daily Route Report : Total Sales')
            mycanvas.line(200, 180+y_a4, 400, 180+y_a4)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 130, '{----------There is no report to show----------}')
            else:
                # Table Header
                mycanvas.setLineWidth(0)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica', 10)

                mycanvas.drawString(15, 140+y_a4, 'Items')

                mycanvas.drawString(105-x_a4, 140+y_a4, '1000ml')
                mycanvas.drawString(100-x_a4, 130+y_a4, '  Cash')
               
                mycanvas.drawString(105+80-x_a4-10-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(100+80-x_a4-10-10-10, 130+y_a4, '  Cash')

                mycanvas.drawString(200+60-x_a4-20-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(195+60-x_a4-20-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(270+60-x_a4-30-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(265+60-x_a4-30-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(340+60-x_a4-40-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(335+60-x_a4-40-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(410+60-x_a4-50-10-10, 140+y_a4, '200ml')
                mycanvas.drawString(405+60-x_a4-50-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(480+60-x_a4-60-10-10, 140+y_a4, '120ml')
                mycanvas.drawString(475+60-x_a4-60-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(545+60-x_a4-70-10-10, 140+y_a4, '5000ml')
                mycanvas.drawString(540+60-x_a4-70-10-10, 130+y_a4, ' Cash')

                mycanvas.line(10, 155+y_a4, 585, 155+y_a4)
                mycanvas.line(10, 120+y_a4, 585, 120+y_a4)

                mycanvas.drawString(620+60-x_a4-80-10-10, 140+y_a4, ' TOTAL')
                mycanvas.drawString(620+60-x_a4-80-10-10, 130+y_a4, 'LITTERS')

                y = 100+y_a4
                y_line = 155+y_a4
                x_line = 30

                # -----------------------------------------------------------------------------------------------------------------------------------------#

                # lines#
                mycanvas.line(x_line + 5-25, y_line, x_line + 5-25, y_line - 205)
                mycanvas.line(x_line + 75-50, y_line, x_line + 75-50, y_line - 205)
               
                mycanvas.line(x_line + 145-70, y_line, x_line + 145-70, y_line - 205)
                mycanvas.line(x_line + 145+80-100, y_line, x_line + 145+80-100, y_line - 205)
                mycanvas.line(x_line + 215+80-110, y_line, x_line + 215+80-110, y_line - 205)
                mycanvas.line(x_line + 285+80-120, y_line, x_line + 285+80-120, y_line - 205)
                mycanvas.line(x_line + 355+80-130, y_line, x_line + 355+80-130, y_line - 205)
                mycanvas.line(x_line + 425+80-140, y_line, x_line + 425+80-140, y_line - 205)
                mycanvas.line(x_line + 495+80-150, y_line, x_line + 495+80-150, y_line - 205)
                mycanvas.line(x_line + 565+80-160, y_line, x_line + 565+80-160, y_line - 205)
                mycanvas.line(x_line + 650+80-175, y_line, x_line + 650+80-175, y_line - 205)
                #             mycanvas.line(x_line+660,y_line,x_line+660,y_line-107)

                y_line -= 50
                mycanvas.setFont('Helvetica', 8)
                total_1000 = 0
                total_500_cash = 0
                total_500_card = 0
                total_250_cash = 0
                total_250_card = 0
                total_200 = 0
                total_150 = 0
                total_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.drawString(15, y, str(products))
                    total_litter_line = 0
                    x_1000 = 180+20-70
                    x_500 = 180+80-97
                    x_250 = 280+80-117
                    x_200 = 380+80 - 137
                    x_150 = 430+80 - 147
                    x_5000 = 620+80 - 157
                    x_total_litter_line = 610 - 172

                    if not products in data_dict["final_results"][data]:
                        pass
                    #                     if products == "TM" or products == "SM" or products == "FCM":
                    #                         y -= 15
                    #                         continue
                    #                     continue

                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                           
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_1000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_1000 += data_dict["final_results"][data][products][quantity][
                                                    types]
                                               

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        if types == "card":
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        mycanvas.drawRightString(x_500 - 10 + x_adjust, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        x_500 += 50
                                                        x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            mycanvas.drawRightString(x_500, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        else:
                                                            x_500 += 50
                                                            mycanvas.drawRightString(x_500 + 40, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    if types == "card":
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    mycanvas.drawRightString(x_250 + 30 + x_adjust, y, str(
                                                        data_dict["final_results"][data][products][quantity][types]))
                                                    x_250 += 50
                                                    x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        x_250 += 50
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_200 + 70, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_200 += data_dict["final_results"][data][products][quantity][types]
                                                x_200 += 50

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:

                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_150 + 90, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_150 += data_dict["final_results"][data][products][quantity][types]
                                                x_150 += 50
                                               
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         for types in data_dict["final_results"][data][products][quantity]:
                            #             if data_dict["final_results"][data][products][quantity][types] != 0 and \
                            #                     data_dict["final_results"][data][products][quantity][types] != None:
                            #                 if types == "total":
                            #                     total_litter_line += \
                            #                     data_dict["final_results"][data][products][quantity][
                            #                         types]
                            #                 else:
                            #                     mycanvas.drawRightString(x_100 - 30, y, str(
                            #                         data_dict["final_results"][data][products][quantity][types]))
                            #                     total_100 += data_dict["final_results"][data][products][quantity][
                            #                         types]


                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_5000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_5000 += data_dict["final_results"][data][products][quantity][
                                                    types]

                    mycanvas.drawRightString(x_total_litter_line + 65+80, y, str(total_litter_line))
                    grand_total += total_litter_line

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line + 65+80, y - 5, str(grand_total))
                mycanvas.drawRightString(x_total_litter_line - 90+105, y - 5, str(total_150))
                mycanvas.drawRightString(x_total_litter_line - 160+115, y - 5, str(total_200))
                mycanvas.drawRightString(x_total_litter_line - 230+125, y - 5, str(total_250_card))
                mycanvas.drawRightString(x_total_litter_line - 300+135, y - 5, str(total_250_cash))
                mycanvas.drawRightString(x_total_litter_line - 370+145, y - 5, str(total_500_card))
                mycanvas.drawRightString(x_total_litter_line - 440+155, y - 5, str(total_500_cash))
                mycanvas.drawRightString(x_total_litter_line - 20+95, y - 5, str(total_5000))
                mycanvas.drawRightString(x_total_litter_line - 335, y - 5, str(total_1000))
                mycanvas.drawRightString(x_total_litter_line - 385, y - 5, "Grand Total")
                #             grand_total += data_dict[data]["products_total"]
                #             mycanvas.drawRightString(x_total_litter_line+75,y+10,str(data_dict[data]["products_total"]))
                #             y -= 10
                mycanvas.line(10, y + 8, 585, y + 8)
                mycanvas.line(10, y - 15, 585, y - 15)
               
    mycanvas.setFont('Times-Italic', 12)      
    indian = pytz.timezone('Asia/Kolkata')          
    mycanvas.drawRightString(585, 5,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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




def serve_unique_route_wise_sale_for_selected_date(date, user_name):
    date = date
    route_with_quantity_dict= {
        "union":{},
        "route":{}
    }
    union_obj = Union.objects.all().order_by('id')
    for union in union_obj:
        if not union.name in route_with_quantity_dict["union"]:
            route_with_quantity_dict["union"][union.name] = {
                "mor":{
                            'milk_total': 0,
                            'curd_total': 0,
                            'butter_milk_total': 0,
                            'lassi_total': 0
                        },
                "eve":{
                            'milk_total': 0,
                            'curd_total': 0,
                            'butter_milk_total': 0,
                            'lassi_total': 0
                        }
            }
        route_obj = RouteGroupMap.objects.filter(union_id=union.id)
        if route_obj is None:
            pass
        else:
            for route in route_obj:
                route_with_quantity_dict["route"][route.name] = {}
                mor_sale_obj = DailySessionllyRoutellySale.objects.filter(delivery_date=date,
                                                                          route_id=route.mor_route_id)
                eve_sale_obj = DailySessionllyRoutellySale.objects.filter(delivery_date=date,
                                                                          route_id=route.eve_route_id)

                if not mor_sale_obj.exists():
                    if not "mor" in route_with_quantity_dict["route"][route.name]:
                        route_with_quantity_dict["route"][route.name]["mor"] = {
                            "union" :"na",
                            'milk_total': 0,
                            'curd_total': 0,
                            'butter_milk_total': 0,
                            'lassi_total': 0
                        }
                    route_with_quantity_dict["route"][route.name]["mor"]['union'] = union.name  
                    route_with_quantity_dict["route"][route.name]["mor"]['milk_total'] = 0
                    route_with_quantity_dict["route"][route.name]["mor"]['curd_total'] = 0
                    route_with_quantity_dict["route"][route.name]["mor"]['butter_milk_total'] = 0
                    route_with_quantity_dict["route"][route.name]["mor"]['lassi_total'] = 0
                else:
                    if mor_sale_obj:
                        if not "mor" in route_with_quantity_dict["route"][route.name]:
                            route_with_quantity_dict["route"][route.name]["mor"] = {
                                "union" : union.name,
                                'milk_total': 0,
                                'curd_total': 0,
                                'butter_milk_total': 0,
                                'lassi_total': 0
                            }
                        milk_total = mor_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] + \
                                     mor_sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"] + \
                                     mor_sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"] + \
                                     mor_sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + \
                                     mor_sale_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"] + \
                                     mor_sale_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"] + \
                                     mor_sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"] + \
                                     mor_sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + \
                                     mor_sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]
                        curd_total = mor_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] + \
                                     mor_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] + \
                                     mor_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] + \
                                     mor_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
                        butter_milk_total = mor_sale_obj.aggregate(Sum('buttermilk200_litre'))[
                            'buttermilk200_litre__sum'] + mor_sale_obj.aggregate(Sum('bm_jar200_litre'))[
                            'bm_jar200_litre__sum'] + mor_sale_obj.aggregate(Sum('bmjf200_litre'))[
                            'bmjf200_litre__sum']
                        lassi_total = mor_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
                        route_with_quantity_dict["route"][route.name]["mor"]['milk_total'] = milk_total
                        route_with_quantity_dict["route"][route.name]["mor"]['curd_total'] = curd_total
                        route_with_quantity_dict["route"][route.name]["mor"]['butter_milk_total'] = butter_milk_total
                        route_with_quantity_dict["route"][route.name]["mor"]['lassi_total'] = lassi_total
                       
                        route_with_quantity_dict["union"][union.name]["mor"]['milk_total'] += milk_total
                        route_with_quantity_dict["union"][union.name]["mor"]['curd_total'] += curd_total
                        route_with_quantity_dict["union"][union.name]["mor"]['butter_milk_total'] += butter_milk_total
                        route_with_quantity_dict["union"][union.name]["mor"]['lassi_total'] += lassi_total

                if not eve_sale_obj.exists():
                   
                    if not "eve" in route_with_quantity_dict["route"][route.name]:
                        route_with_quantity_dict["route"][route.name]["eve"] = {
                           
                            "union" : union.name,
                            'milk_total': 0,
                            'curd_total': 0,
                            'butter_milk_total': 0,
                            'lassi_total': 0
                        }
                    route_with_quantity_dict["route"][route.name]["eve"]['milk_total'] = 0
                    route_with_quantity_dict["route"][route.name]["eve"]['curd_total'] = 0
                    route_with_quantity_dict["route"][route.name]["eve"]['butter_milk_total'] = 0
                    route_with_quantity_dict["route"][route.name]["eve"]['lassi_total'] = 0
                else:
                    if eve_sale_obj:
                   
                        if not "eve" in route_with_quantity_dict["route"][route.name]:
                            route_with_quantity_dict["route"][route.name]["eve"] = {
                                "union" : union.name,
                                'milk_total': 0,
                                'curd_total': 0,
                                'butter_milk_total': 0,
                                'lassi_total': 0
                            }
                        milk_total = eve_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] + \
                                     eve_sale_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"] + \
                                     eve_sale_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"] + \
                                     eve_sale_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"] + \
                                     eve_sale_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"] + \
                                     eve_sale_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"] + \
                                     eve_sale_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"] + \
                                     eve_sale_obj.aggregate(Sum('tea500_litre'))["tea500_litre__sum"] + \
                                     eve_sale_obj.aggregate(Sum('tea1000_litre'))["tea1000_litre__sum"]
                        curd_total = eve_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] + \
                                     eve_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] + \
                                     eve_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] + \
                                     eve_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
                        butter_milk_total = eve_sale_obj.aggregate(Sum('buttermilk200_litre'))[
                            'buttermilk200_litre__sum'] + eve_sale_obj.aggregate(Sum('bm_jar200_litre'))[
                            'bm_jar200_litre__sum'] + eve_sale_obj.aggregate(Sum('bmjf200_litre'))[
                            'bmjf200_litre__sum']
                        lassi_total = eve_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
                        route_with_quantity_dict["route"][route.name]["eve"]['milk_total'] = milk_total
                        route_with_quantity_dict["route"][route.name]["eve"]['curd_total'] = curd_total
                        route_with_quantity_dict["route"][route.name]["eve"]['butter_milk_total'] = butter_milk_total
                        route_with_quantity_dict["route"][route.name]["eve"]['lassi_total'] = lassi_total
                       
                        route_with_quantity_dict["union"][union.name]["eve"]['milk_total'] += milk_total
                        route_with_quantity_dict["union"][union.name]["eve"]['curd_total'] += curd_total
                        route_with_quantity_dict["union"][union.name]["eve"]['butter_milk_total'] += butter_milk_total
                        route_with_quantity_dict["union"][union.name]["eve"]['lassi_total'] += lassi_total

    data = generate_pdf_for_unique_route_wise_sale_details(route_with_quantity_dict, user_name, date, union_obj)
    return data


def generate_pdf_for_unique_route_wise_sale_details(route_with_quantity_dict, user_name, date, union_obj):
    file_name = str(date) + '_route_wise_sale_absract'+ '.pdf'
    file_path = os.path.join('static/media/route_wise_report/', file_name)

    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    pdfmetrics.registerFont(TTFont('dot', 'dotmatrix.ttf'))

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
   
    mycanvas.setLineWidth(0)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 780, 'ROUTE WISE SALES ABSTRACT REPORT: MILK')
    mycanvas.line(150, 778, 450, 778)

    mycanvas.drawString(40, 758, 'Date : ')
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
    mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawCentredString(300, 743, 'UNION WISE SALE : MILK')
    mycanvas.line(200, 741, 400, 741)
    mycanvas.setFont('Helvetica', 12)
   
    #---------------------union_table-----------------------#
   
    mycanvas.line(20, 690+40, 575, 690+40)
    mycanvas.line(20, 660+40, 575, 660+40)
    mycanvas.line(20, 570+40, 575, 570+40)
    mycanvas.line(20, 545+40, 575, 545+40)
   
    #side line
    mycanvas.line(575, 690+40, 575, 545+40)
    mycanvas.line(20, 690+40, 20, 545+40)
   
    #Between line
   
    mycanvas.line(110, 690+40, 110, 545+40)
    mycanvas.line(260, 690+40, 260, 545+40)
    mycanvas.line(410, 690+40, 410, 545+40)
   
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(45, 672+40, 'Union')
    mycanvas.drawCentredString(260-80, 672+40, 'Morning')
    mycanvas.drawCentredString(420-85, 672+40, 'Evening')
    mycanvas.drawCentredString(580-90, 672+40, 'Milk Total (litre)')
    y_line = 640
    mycanvas.setFont('Helvetica', 12)
    mor_total = 0
    eve_total = 0
    grand_total = 0
    for union in route_with_quantity_dict["union"]:
        mycanvas.drawString(30, y_line+40, str(union))
        mycanvas.drawRightString(70+180, y_line+40, str(route_with_quantity_dict["union"][union]['mor']['milk_total']))
        mycanvas.drawRightString(70+180+150, y_line+40, str(route_with_quantity_dict["union"][union]['eve']['milk_total']))
        total = route_with_quantity_dict["union"][union]['mor']['milk_total']+route_with_quantity_dict["union"][union]['eve']['milk_total']
        mycanvas.drawRightString(70+155+340, y_line+40, str(total))
       
        mor_total += route_with_quantity_dict["union"][union]['mor']['milk_total']
        eve_total += route_with_quantity_dict["union"][union]['eve']['milk_total']
        grand_total += total
        y_line -= 20
    mycanvas.drawString(30, y_line-8+40," Grand Total" )
    mycanvas.drawRightString(70+180,y_line-8+40,str(mor_total))
    mycanvas.drawRightString(70+180+150, y_line-8+40,str(eve_total))
    mycanvas.drawRightString(70+155+340, y_line-8+40, str(grand_total))
   
    # table
    mycanvas.drawCentredString(300, 550, 'ROUTE WISE SALE : MILK')
    mycanvas.line(200, 548, 400, 548)
   
    mycanvas.line(20, 535, 575, 535)
    mycanvas.line(20, 495, 575, 495)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(100-40, 515, 'Route')
    mycanvas.drawString(230-60, 515, 'Union')
    mycanvas.drawCentredString(360-70, 520, 'Morning')
    mycanvas.drawCentredString(360-70, 505, 'Milk Total (litre)')
    mycanvas.drawCentredString(480-80, 520, 'Evening')
    mycanvas.drawCentredString(480-80, 505, 'Milk Total (litre)')
    mycanvas.drawCentredString(610-90, 520, 'Total')
    mycanvas.drawCentredString(610-90, 505, 'Milk (litre)')

    mycanvas.setFont('Helvetica', 12)

    initial_y_axis = 455
    mor_total = 0
    eve_total = 0
    overall_total = 0
    count=1
    for route in route_with_quantity_dict["route"]:
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(30, initial_y_axis+10, str(route)[:11])
        #         if not route_with_quantity_dict["route"][route['mor_route_id']]['milk_total'] == 0:
        mycanvas.drawString(180-30, initial_y_axis+10,str(route_with_quantity_dict["route"][route]['mor']['union']))
        mycanvas.drawRightString(410-80, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['mor']['milk_total']))
        mor_total += route_with_quantity_dict["route"][route]['mor']['milk_total']
        #         if not route_with_quantity_dict["route"][route['eve_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(530-90, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['eve']['milk_total']))
        eve_total += route_with_quantity_dict["route"][route]['eve']['milk_total']
        total = route_with_quantity_dict["route"][route]['mor']['milk_total'] + \
                route_with_quantity_dict["route"][route]['eve']['milk_total']

        #         if not total == 0:
        mycanvas.drawRightString(670-105, initial_y_axis+10, str(total))
        overall_total += total
       
        mycanvas.line(20, initial_y_axis - 10+10, 20, 535)
        mycanvas.line(130, initial_y_axis - 8+10, 130, 535)
        mycanvas.line(230, initial_y_axis - 10+10, 230, 535)
        mycanvas.line(340, initial_y_axis - 10+10, 340, 535)
        mycanvas.line(450, initial_y_axis - 10+10, 450, 535)
        mycanvas.line(575, initial_y_axis - 10+10, 575, 535)
       
        if initial_y_axis == 30:
            mycanvas.line(20, 30, 575,30)
            mycanvas.showPage()
            mycanvas.setLineWidth(0)
            initial_y_axis = 690
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawCentredString(300, 780, 'ROUTE WISE SALES ABSTRACT REPORT: MILK')
            mycanvas.line(150, 778, 450, 778)

#             mycanvas.setFillColor(HexColor(light_color))
            mycanvas.drawString(40, 758, 'Date : ')
            mycanvas.setFillColor(HexColor(dark_color))
            date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
            mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))

            # table
            mycanvas.line(20, 690+55, 575, 690+55)
            mycanvas.line(20, 660+45, 575, 660+45)
           
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(100-40, 675+50, 'Route')
            mycanvas.drawString(230-60, 675+50, 'Union')
            mycanvas.drawCentredString(360-70, 680+50, 'Morning')
            mycanvas.drawCentredString(360-70, 665+50, 'Milk Total (litre)')
            mycanvas.drawCentredString(480-80, 680+50, 'Evening')
            mycanvas.drawCentredString(480-80, 665+50, 'Milk Total (litre)')
            mycanvas.drawCentredString(610-90, 680+50, 'Total')
            mycanvas.drawCentredString(610-90, 665+50, 'Milk (litre)')

            mycanvas.setFont('Helvetica', 14)
        count +=1
        initial_y_axis -= 25

    mycanvas.drawRightString(410-80, initial_y_axis - 12, str(mor_total))
    mycanvas.drawRightString(530-90, initial_y_axis - 12, str(eve_total))
    mycanvas.drawRightString(670-105, initial_y_axis - 12, str(overall_total))

    mycanvas.line(20, initial_y_axis + 10, 575, initial_y_axis + 10)
    mycanvas.line(20, initial_y_axis - 20, 575, initial_y_axis - 20)
    mycanvas.setFont('Helvetica', 14)
    mycanvas.drawString(70, initial_y_axis -12, 'TOTAL LITRE')
   

#     # draw horizontal line
    mycanvas.line(20, initial_y_axis-20, 20, 745)
    mycanvas.line(130, initial_y_axis+10, 130, 745)
    mycanvas.line(230, initial_y_axis-20, 230, 745)
    mycanvas.line(340, initial_y_axis-20, 340, 745)
    mycanvas.line(450, initial_y_axis-20, 450, 745)
    mycanvas.line(575, initial_y_axis-20, 575, 745)
   
# --------------------------------------------CURD-------------------------------------------
   
    mycanvas.showPage()
    mycanvas.setLineWidth(0)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 780, 'ROUTE WISE SALES ABSTRACT REPORT: CURD')
    mycanvas.line(150, 778, 450, 778)

    mycanvas.drawString(40, 758, 'Date : ')
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
    mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawCentredString(300, 743, 'UNION WISE SALE : CURD')
    mycanvas.line(200, 741, 400, 741)
    mycanvas.setFont('Helvetica', 12)
   
    #---------------------union_table-----------------------#
   
    mycanvas.line(20, 690+40, 575, 690+40)
    mycanvas.line(20, 660+40, 575, 660+40)
    mycanvas.line(20, 570+40, 575, 570+40)
    mycanvas.line(20, 545+40, 575, 545+40)
   
    #side line
    mycanvas.line(575, 690+40, 575, 545+40)
    mycanvas.line(20, 690+40, 20, 545+40)
   
    #Between line
   
    mycanvas.line(110, 690+40, 110, 545+40)
    mycanvas.line(260, 690+40, 260, 545+40)
    mycanvas.line(410, 690+40, 410, 545+40)
   
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(45, 672+40, 'Union')
    mycanvas.drawCentredString(260-80, 672+40, 'Morning')
    mycanvas.drawCentredString(420-85, 672+40, 'Evening')
    mycanvas.drawCentredString(580-90, 672+40, 'Curd Total (Kgs)')
    y_line = 640
    mycanvas.setFont('Helvetica', 12)
    mor_total = 0
    eve_total = 0
    grand_total = 0
    for union in route_with_quantity_dict["union"]:
        mycanvas.drawString(30, y_line+40, str(union))
        mycanvas.drawRightString(70+180, y_line+40, str(route_with_quantity_dict["union"][union]['mor']['curd_total']))
        mycanvas.drawRightString(70+180+150, y_line+40, str(route_with_quantity_dict["union"][union]['eve']['curd_total']))
        total = route_with_quantity_dict["union"][union]['mor']['curd_total']+route_with_quantity_dict["union"][union]['eve']['curd_total']
        mycanvas.drawRightString(70+155+340, y_line+40, str(total))
       
        mor_total += route_with_quantity_dict["union"][union]['mor']['curd_total']
        eve_total += route_with_quantity_dict["union"][union]['eve']['curd_total']
        grand_total += total
        y_line -= 20
    mycanvas.drawString(30, y_line-8+40," Grand Total" )
    mycanvas.drawRightString(70+180,y_line-8+40,str(mor_total))
    mycanvas.drawRightString(70+180+150, y_line-8+40,str(eve_total))
    mycanvas.drawRightString(70+155+340, y_line-8+40, str(grand_total))
   
    # table
    mycanvas.drawCentredString(300, 550, 'ROUTE WISE SALE : CURD')
    mycanvas.line(200, 548, 400, 548)
   
    mycanvas.line(20, 535, 575, 535)
    mycanvas.line(20, 495, 575, 495)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(100-40, 515, 'Route')
    mycanvas.drawString(230-60, 515, 'Union')
    mycanvas.drawCentredString(360-70, 520, 'Morning')
    mycanvas.drawCentredString(360-70, 505, 'Curd Total (Kgs)')
    mycanvas.drawCentredString(480-80, 520, 'Evening')
    mycanvas.drawCentredString(480-80, 505, 'Curd Total (Kgs)')
    mycanvas.drawCentredString(610-90, 520, 'Total')
    mycanvas.drawCentredString(610-90, 505, 'Curd (Kgs)')

    mycanvas.setFont('Helvetica', 12)

    initial_y_axis = 455
    mor_total = 0
    eve_total = 0
    overall_total = 0
    count=1
    for route in route_with_quantity_dict["route"]:
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(30, initial_y_axis+10, str(route)[:11])
        #         if not route_with_quantity_dict["route"][route['mor_route_id']]['milk_total'] == 0:
        mycanvas.drawString(180-30, initial_y_axis+10,str(route_with_quantity_dict["route"][route]['mor']['union']))
        mycanvas.drawRightString(410-80, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['mor']['curd_total']))
        mor_total += route_with_quantity_dict["route"][route]['mor']['curd_total']
        #         if not route_with_quantity_dict["route"][route['eve_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(530-90, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['eve']['curd_total']))
        eve_total += route_with_quantity_dict["route"][route]['eve']['curd_total']
        total = route_with_quantity_dict["route"][route]['mor']['curd_total'] + \
                route_with_quantity_dict["route"][route]['eve']['curd_total']

        #         if not total == 0:
        mycanvas.drawRightString(670-105, initial_y_axis+10, str(total))
        overall_total += total
       
        mycanvas.line(20, initial_y_axis - 10+10, 20, 535)
        mycanvas.line(130, initial_y_axis - 8+10, 130, 535)
        mycanvas.line(230, initial_y_axis - 10+10, 230, 535)
        mycanvas.line(340, initial_y_axis - 10+10, 340, 535)
        mycanvas.line(450, initial_y_axis - 10+10, 450, 535)
        mycanvas.line(575, initial_y_axis - 10+10, 575, 535)
       
        if initial_y_axis == 30:
            mycanvas.line(20, 30, 575,30)
            mycanvas.showPage()
            mycanvas.setLineWidth(0)
            initial_y_axis = 690
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawCentredString(300, 780, 'ROUTE WISE SALES ABSTRACT REPORT: CURD')
            mycanvas.line(150, 778, 450, 778)

#             mycanvas.setFillColor(HexColor(light_color))
            mycanvas.drawString(40, 758, 'Date : ')
            mycanvas.setFillColor(HexColor(dark_color))
            date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
            mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))

            # table
            mycanvas.line(20, 690+55, 575, 690+55)
            mycanvas.line(20, 660+45, 575, 660+45)
           
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(100-40, 675+50, 'Route')
            mycanvas.drawString(230-60, 675+50, 'Union')
            mycanvas.drawCentredString(360-70, 680+50, 'Morning')
            mycanvas.drawCentredString(360-70, 665+50, 'Curd Total (Kgs)')
            mycanvas.drawCentredString(480-80, 680+50, 'Evening')
            mycanvas.drawCentredString(480-80, 665+50, 'Curd Total (Kgs)')
            mycanvas.drawCentredString(610-90, 680+50, 'Total')
            mycanvas.drawCentredString(610-90, 665+50, 'Curd (Kgs)')

            mycanvas.setFont('Helvetica', 14)
        count +=1
        initial_y_axis -= 25

    mycanvas.drawRightString(410-80, initial_y_axis - 12, str(mor_total))
    mycanvas.drawRightString(530-90, initial_y_axis - 12, str(eve_total))
    mycanvas.drawRightString(670-105, initial_y_axis - 12, str(overall_total))

    mycanvas.line(20, initial_y_axis + 10, 575, initial_y_axis + 10)
    mycanvas.line(20, initial_y_axis - 20, 575, initial_y_axis - 20)
    mycanvas.setFont('Helvetica', 14)
    mycanvas.drawString(70, initial_y_axis -12, 'TOTAL LITRE')
   

#     # draw horizontal line
    mycanvas.line(20, initial_y_axis-20, 20, 745)
    mycanvas.line(130, initial_y_axis+10, 130, 745)
    mycanvas.line(230, initial_y_axis-20, 230, 745)
    mycanvas.line(340, initial_y_axis-20, 340, 745)
    mycanvas.line(450, initial_y_axis-20, 450, 745)
    mycanvas.line(575, initial_y_axis-20, 575, 745)
   
#--------------------------------------------BUTTER MILK---------------------------------------
   
    mycanvas.showPage()

    mycanvas.setLineWidth(0)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 780, 'ROUTE WISE SALES ABSTRACT REPORT: BUTTER MILK')
    mycanvas.line(150, 778, 450, 778)

    mycanvas.drawString(40, 758, 'Date : ')
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
    mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawCentredString(300, 743, 'UNION WISE SALE : BUTTER MILK')
    mycanvas.line(200, 741, 400, 741)
    mycanvas.setFont('Helvetica', 12)
   
    #---------------------union_table-----------------------#
   
    mycanvas.line(20, 690+40, 575, 690+40)
    mycanvas.line(20, 660+40, 575, 660+40)
    mycanvas.line(20, 570+40, 575, 570+40)
    mycanvas.line(20, 545+40, 575, 545+40)
   
    #side line
    mycanvas.line(575, 690+40, 575, 545+40)
    mycanvas.line(20, 690+40, 20, 545+40)
   
    #Between line
   
    mycanvas.line(110, 690+40, 110, 545+40)
    mycanvas.line(260, 690+40, 260, 545+40)
    mycanvas.line(410, 690+40, 410, 545+40)
   
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(45, 672+40, 'Union')
    mycanvas.drawCentredString(260-80, 672+40, 'Morning')
    mycanvas.drawCentredString(420-85, 672+40, 'Evening')
    mycanvas.drawCentredString(580-90, 672+40, 'Butter Milk Total (litre)')
    y_line = 640
    mycanvas.setFont('Helvetica', 12)
    mor_total = 0
    eve_total = 0
    grand_total = 0
    for union in route_with_quantity_dict["union"]:
        mycanvas.drawString(30, y_line+40, str(union))
        mycanvas.drawRightString(70+180, y_line+40, str(route_with_quantity_dict["union"][union]['mor']['butter_milk_total']))
        mycanvas.drawRightString(70+180+150, y_line+40, str(route_with_quantity_dict["union"][union]['eve']['butter_milk_total']))
        total = route_with_quantity_dict["union"][union]['mor']['butter_milk_total']+route_with_quantity_dict["union"][union]['eve']['butter_milk_total']
        mycanvas.drawRightString(70+155+340, y_line+40, str(total))
       
        mor_total += route_with_quantity_dict["union"][union]['mor']['butter_milk_total']
        eve_total += route_with_quantity_dict["union"][union]['eve']['butter_milk_total']
        grand_total += total
        y_line -= 20
    mycanvas.drawString(30, y_line-8+40," Grand Total" )
    mycanvas.drawRightString(70+180,y_line-8+40,str(mor_total))
    mycanvas.drawRightString(70+180+150, y_line-8+40,str(eve_total))
    mycanvas.drawRightString(70+155+340, y_line-8+40, str(grand_total))
   
    # table
    mycanvas.drawCentredString(300, 550, 'ROUTE WISE SALE : BUTTER MILK')
    mycanvas.line(200, 548, 400, 548)
   
    mycanvas.line(20, 535, 575, 535)
    mycanvas.line(20, 495, 575, 495)
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(100-40, 515, 'Route')
    mycanvas.drawString(230-60, 515, 'Union')
    mycanvas.drawCentredString(360-70, 520, 'Morning')
    mycanvas.drawCentredString(360-75, 505, 'Butter Milk Total (litre)')
    mycanvas.drawCentredString(480-80, 520, 'Evening')
    mycanvas.drawCentredString(480-85, 505, 'Butter Milk Total (litre)')
    mycanvas.drawCentredString(610-90, 520, 'Total')
    mycanvas.drawCentredString(610-90, 505, 'Butter Milk (litre)')

    mycanvas.setFont('Helvetica', 12)

    initial_y_axis = 455
    mor_total = 0
    eve_total = 0
    overall_total = 0
    count=1
    for route in route_with_quantity_dict["route"]:
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(30, initial_y_axis+10, str(route)[:11])
        #         if not route_with_quantity_dict["route"][route['mor_route_id']]['milk_total'] == 0:
        mycanvas.drawString(180-30, initial_y_axis+10,str(route_with_quantity_dict["route"][route]['mor']['union']))
        mycanvas.drawRightString(410-80, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['mor']['butter_milk_total']))
        mor_total += route_with_quantity_dict["route"][route]['mor']['butter_milk_total']
        #         if not route_with_quantity_dict["route"][route['eve_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(530-90, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['eve']['butter_milk_total']))
        eve_total += route_with_quantity_dict["route"][route]['eve']['butter_milk_total']
        total = route_with_quantity_dict["route"][route]['mor']['butter_milk_total'] + \
                route_with_quantity_dict["route"][route]['eve']['butter_milk_total']

        #         if not total == 0:
        mycanvas.drawRightString(670-105, initial_y_axis+10, str(total))
        overall_total += total
       
        mycanvas.line(20, initial_y_axis - 10+10, 20, 535)
        mycanvas.line(130, initial_y_axis - 8+10, 130, 535)
        mycanvas.line(230, initial_y_axis - 10+10, 230, 535)
        mycanvas.line(340, initial_y_axis - 10+10, 340, 535)
        mycanvas.line(450, initial_y_axis - 10+10, 450, 535)
        mycanvas.line(575, initial_y_axis - 10+10, 575, 535)
       
        if initial_y_axis == 30:
            mycanvas.line(20, 30, 575,30)
            mycanvas.showPage()
            mycanvas.setLineWidth(0)
            initial_y_axis = 690
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawCentredString(300, 780, 'ROUTEWISE SALES ABSTRACT REPORT: BUTTER MILK')
            mycanvas.line(150, 778, 450, 778)

            mycanvas.drawString(40, 758, 'Date : ')
            mycanvas.setFillColor(HexColor(dark_color))
            date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
            mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))

            # table
            mycanvas.line(20, 690+55, 575, 690+55)
            mycanvas.line(20, 660+45, 575, 660+45)
           
            mycanvas.setFont('Helvetica', 10)
            mycanvas.drawString(100-40, 675+50, 'Route')
            mycanvas.drawString(230-60, 675+50, 'Union')
            mycanvas.drawCentredString(360-70, 680+50, 'Morning')
            mycanvas.drawCentredString(360-75, 665+50, 'butter Milk Total (litre)')
            mycanvas.drawCentredString(480-80, 680+50, 'Evening')
            mycanvas.drawCentredString(480-85, 665+50, 'butter Milk Total (litre)')
            mycanvas.drawCentredString(610-90, 680+50, 'Total')
            mycanvas.drawCentredString(610-90, 665+50, 'butter Milk (litre)')

            mycanvas.setFont('Helvetica', 14)
        count +=1
        initial_y_axis -= 25

    mycanvas.drawRightString(410-80, initial_y_axis - 12, str(mor_total))
    mycanvas.drawRightString(530-90, initial_y_axis - 12, str(eve_total))
    mycanvas.drawRightString(670-105, initial_y_axis - 12, str(overall_total))

    mycanvas.line(20, initial_y_axis + 10, 575, initial_y_axis + 10)
    mycanvas.line(20, initial_y_axis - 20, 575, initial_y_axis - 20)
    mycanvas.setFont('Helvetica', 14)
    mycanvas.drawString(70, initial_y_axis -12, 'TOTAL LITRE')
   

#     # draw horizontal line
    mycanvas.line(20, initial_y_axis-20, 20, 745)
    mycanvas.line(130, initial_y_axis+10, 130, 745)
    mycanvas.line(230, initial_y_axis-20, 230, 745)
    mycanvas.line(340, initial_y_axis-20, 340, 745)
    mycanvas.line(450, initial_y_axis-20, 450, 745)
    mycanvas.line(575, initial_y_axis-20, 575, 745)
   
   
#------------------------------------------Lassi MILK---------------------------------------#
   
    mycanvas.showPage()
    mycanvas.setLineWidth(0)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 780, 'ROUTEWISE SALES ABSTRACT REPORT: LASSI')
    mycanvas.line(150, 778, 450, 778)

    mycanvas.drawString(40, 758, 'Date : ')
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
    mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawCentredString(300, 743, 'UNION WISE SALE : LASSI')
    mycanvas.line(200, 741, 400, 741)
    mycanvas.setFont('Helvetica', 12)
   
    #---------------------union_table-----------------------#
   
    mycanvas.line(20, 690+40, 575, 690+40)
    mycanvas.line(20, 660+40, 575, 660+40)
    mycanvas.line(20, 570+40, 575, 570+40)
    mycanvas.line(20, 545+40, 575, 545+40)
   
    #side line
    mycanvas.line(575, 690+40, 575, 545+40)
    mycanvas.line(20, 690+40, 20, 545+40)
   
    #Between line
   
    mycanvas.line(110, 690+40, 110, 545+40)
    mycanvas.line(260, 690+40, 260, 545+40)
    mycanvas.line(410, 690+40, 410, 545+40)
   
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(45, 672+40, 'Union')
    mycanvas.drawCentredString(260-80, 672+40, 'Morning')
    mycanvas.drawCentredString(420-85, 672+40, 'Evening')
    mycanvas.drawCentredString(580-90, 672+40, 'Lassi Total (Kgs)')
    y_line = 640
    mycanvas.setFont('Helvetica', 12)
    mor_total = 0
    eve_total = 0
    grand_total = 0
    for union in route_with_quantity_dict["union"]:
        mycanvas.drawString(30, y_line+40, str(union))
        mycanvas.drawRightString(70+180, y_line+40, str(route_with_quantity_dict["union"][union]['mor']['lassi_total']))
        mycanvas.drawRightString(70+180+150, y_line+40, str(route_with_quantity_dict["union"][union]['eve']['lassi_total']))
        total = route_with_quantity_dict["union"][union]['mor']['lassi_total']+route_with_quantity_dict["union"][union]['eve']['lassi_total']
        mycanvas.drawRightString(70+155+340, y_line+40, str(total))
       
        mor_total += route_with_quantity_dict["union"][union]['mor']['lassi_total']
        eve_total += route_with_quantity_dict["union"][union]['eve']['lassi_total']
        grand_total += total
        y_line -= 20
    mycanvas.drawString(30, y_line-8+40," Grand Total" )
    mycanvas.drawRightString(70+180,y_line-8+40,str(mor_total))
    mycanvas.drawRightString(70+180+150, y_line-8+40,str(eve_total))
    mycanvas.drawRightString(70+155+340, y_line-8+40, str(grand_total))
   
    # table
    mycanvas.drawCentredString(300, 550, 'ROUTE WISE SALE : LASSI')
    mycanvas.line(200, 548, 400, 548)
   
    mycanvas.line(20, 535, 575, 535)
    mycanvas.line(20, 495, 575, 495)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(100-40, 515, 'Route')
    mycanvas.drawString(230-60, 515, 'Union')
    mycanvas.drawCentredString(360-70, 520, 'Morning')
    mycanvas.drawCentredString(360-70, 505, 'Lassi Total (Kgs)')
    mycanvas.drawCentredString(480-80, 520, 'Evening')
    mycanvas.drawCentredString(480-80, 505, 'Lassi Total (Kgs)')
    mycanvas.drawCentredString(610-90, 520, 'Total')
    mycanvas.drawCentredString(610-90, 505, 'Lassi (Kgs)')

    mycanvas.setFont('Helvetica', 12)

    initial_y_axis = 455
    mor_total = 0
    eve_total = 0
    overall_total = 0
    count=1
    for route in route_with_quantity_dict["route"]:
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(30, initial_y_axis+10, str(route)[:11])
        #         if not route_with_quantity_dict["route"][route['mor_route_id']]['milk_total'] == 0:
        mycanvas.drawString(180-30, initial_y_axis+10,str(route_with_quantity_dict["route"][route]['mor']['union']))
        mycanvas.drawRightString(410-80, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['mor']['lassi_total']))
        mor_total += route_with_quantity_dict["route"][route]['mor']['lassi_total']
        #         if not route_with_quantity_dict["route"][route['eve_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(530-90, initial_y_axis+10,
                                 str(route_with_quantity_dict["route"][route]['eve']['lassi_total']))
        eve_total += route_with_quantity_dict["route"][route]['eve']['lassi_total']
        total = route_with_quantity_dict["route"][route]['mor']['lassi_total'] + \
                route_with_quantity_dict["route"][route]['eve']['lassi_total']

        #         if not total == 0:
        mycanvas.drawRightString(670-105, initial_y_axis+10, str(total))
        overall_total += total
       
        mycanvas.line(20, initial_y_axis - 10+10, 20, 535)
        mycanvas.line(130, initial_y_axis - 8+10, 130, 535)
        mycanvas.line(230, initial_y_axis - 10+10, 230, 535)
        mycanvas.line(340, initial_y_axis - 10+10, 340, 535)
        mycanvas.line(450, initial_y_axis - 10+10, 450, 535)
        mycanvas.line(575, initial_y_axis - 10+10, 575, 535)
       
        if initial_y_axis == 30:
            mycanvas.line(20, 30, 575,30)
            mycanvas.showPage()
            mycanvas.setLineWidth(0)
            initial_y_axis = 690
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 800,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawCentredString(300, 780, 'ROUTEWISE SALES ABSTRACT REPORT: LASSI')
            mycanvas.line(150, 778, 450, 778)

#             mycanvas.setFillColor(HexColor(light_color))
            mycanvas.drawString(40, 758, 'Date : ')
            mycanvas.setFillColor(HexColor(dark_color))
            date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')    
            mycanvas.drawString(60 + 20, 758, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))

            # table
            mycanvas.line(20, 690+55, 575, 690+55)
            mycanvas.line(20, 660+45, 575, 660+45)
           
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(100-40, 675+50, 'Route')
            mycanvas.drawString(230-60, 675+50, 'Union')
            mycanvas.drawCentredString(360-70, 680+50, 'Morning')
            mycanvas.drawCentredString(360-70, 665+50, 'Lassi Total (Kgs)')
            mycanvas.drawCentredString(480-80, 680+50, 'Evening')
            mycanvas.drawCentredString(480-80, 665+50, 'Lassi Total (Kgs)')
            mycanvas.drawCentredString(610-90, 680+50, 'Total')
            mycanvas.drawCentredString(610-90, 665+50, 'Lassi (Kgs)')

            mycanvas.setFont('Helvetica', 14)
        count +=1
        initial_y_axis -= 25

    mycanvas.drawRightString(410-80, initial_y_axis - 12, str(mor_total))
    mycanvas.drawRightString(530-90, initial_y_axis - 12, str(eve_total))
    mycanvas.drawRightString(670-105, initial_y_axis - 12, str(overall_total))

    mycanvas.line(20, initial_y_axis + 10, 575, initial_y_axis + 10)
    mycanvas.line(20, initial_y_axis - 20, 575, initial_y_axis - 20)
    mycanvas.setFont('Helvetica', 14)
    mycanvas.drawString(70, initial_y_axis -12, 'TOTAL LITRE')
   

#     # draw horizontal line
    mycanvas.line(20, initial_y_axis-20, 20, 745)
    mycanvas.line(130, initial_y_axis+10, 130, 745)
    mycanvas.line(230, initial_y_axis-20, 230, 745)
    mycanvas.line(340, initial_y_axis-20, 340, 745)
    mycanvas.line(450, initial_y_axis-20, 450, 745)
    mycanvas.line(575, initial_y_axis-20, 575, 745)
   
   
    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawString(340, 10,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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


def serve_milk_acknowledgement_report_for_selected_session(date, session, user_name):
    if session == 'all':
        session = list(Session.objects.filter().values_list('id', flat=True))
    else:
        session = int(session)
        session = list(Session.objects.filter(id=session).values_list('id', flat=True))
    date_for = date

    milk_sale = DailySessionllyBusinessllySale.objects.filter(delivery_date=date,
                                                              session_id__in=session)
    products = Product.objects.filter().order_by('display_ordinal')
    data_dict = {
        "date": date_for,
        "shift": session,
        "milk_products": {
            "milk_total_count": 0,
            "milk_total_quantity": Decimal(0),
            "TM": {
                "total_quantity": Decimal(0),
            },
            "SM": {
                "total_quantity": Decimal(0),
            },
            "FCM": {
                "total_quantity": Decimal(0),
            },
            "Tea": {
                "total_quantity": Decimal(0),
            }
        },
        "non_milk_products": {
            
            "milk_total_count": 0,
            
            "milk_total_quantity": Decimal(0),
            "Curd": {
                "total_quantity": Decimal(0),
            },
            "Butte": {
                "total_quantity": Decimal(0),
            }
        },
        "grand_total": 0,
    }
    for product in products:
        if product.group_id == 1 or product.group_id == 3:
            for milk_type in data_dict["milk_products"]:
                # print('x',milk_type)
                if milk_type == product.code[:len(milk_type)]:
                    print('a', milk_type,'milk_type',product.code[:len(milk_type)])
                    if not product.code in data_dict["milk_products"][milk_type]:
                        data_dict["milk_products"][milk_type][product.code] = {
                            "count": 0,
                            "quantity": 0,
                        }
                        # print(product.code)
        if product.group_id == 2:
            if product.code == "BMILK" or product.code == "CURD500" or product.code == "CU150" or product.code == 'CURD5000' or product.code == 'BMJar' or product.code == "BMJF":
                if product.code == "BMILK" or product.code == "BMJar" or product.code == "BMJF":
                    milk_type = "Butte"
                else:
                    milk_type = "Curd"
                if not product.code in data_dict["non_milk_products"][milk_type]:
                    data_dict["non_milk_products"][milk_type][product.code] = {
                        "count": 0,
                        "quantity": 0,
                    }

    for milk in milk_sale:
        # -----MILK_PRODUCT----#
        
        # -----TM------#
        data_dict["milk_products"]["TM"]["TM500"]["count"] += milk.tm500_pkt
        data_dict["milk_products"]["TM"]["TM500"]["quantity"] += milk.tm500_litre
        data_dict["milk_products"]["TM"]["total_quantity"] += milk.tm500_litre

        # -----SM-----#
        data_dict["milk_products"]["SM"]["SM250"]["count"] += milk.std250_pkt
        data_dict["milk_products"]["SM"]["SM250"]["quantity"] += milk.std250_litre

        data_dict["milk_products"]["SM"]["SM500"]["count"] += milk.std500_pkt
        data_dict["milk_products"]["SM"]["SM500"]["quantity"] += milk.std500_litre

        data_dict["milk_products"]["SM"]["SMCAN"]["count"] += milk.smcan
        data_dict["milk_products"]["SM"]["SMCAN"]["quantity"] += milk.smcan_litre

        data_dict["milk_products"]["SM"]["total_quantity"] += milk.std250_litre + milk.std500_litre + milk.smcan_litre

        # ----FCM----#
        data_dict["milk_products"]["FCM"]["FCM500"]["count"] += milk.fcm500_pkt
        data_dict["milk_products"]["FCM"]["FCM500"]["quantity"] += milk.fcm500_litre

        data_dict["milk_products"]["FCM"]["FCM1000"]["count"] += milk.fcm1000_pkt
        data_dict["milk_products"]["FCM"]["FCM1000"]["quantity"] += milk.fcm1000_litre

        data_dict["milk_products"]["FCM"]["FCMCAN"]["count"] += milk.fcmcan
        data_dict["milk_products"]["FCM"]["FCMCAN"]["quantity"] += milk.fcmcan_litre

        data_dict["milk_products"]["FCM"]["total_quantity"] += milk.fcm500_litre + milk.fcmcan_litre + milk.fcm1000_litre

        # ----TMATE----#
        data_dict["milk_products"]["Tea"]["Tea500"]["count"] += milk.tea500_pkt
        data_dict["milk_products"]["Tea"]["Tea500"]["quantity"] += milk.tea500_litre

        data_dict["milk_products"]["Tea"]["Tea1000"]["count"] += milk.tea1000_pkt
        data_dict["milk_products"]["Tea"]["Tea1000"]["quantity"] += milk.tea1000_litre

        data_dict["milk_products"]["Tea"]["total_quantity"] += milk.tea500_litre +  milk.tea1000_litre

        data_dict["milk_products"]["milk_total_count"] += milk.std250_pkt + milk.std500_pkt + milk.smcan + milk.fcmcan + milk.fcm500_pkt + milk.fcm1000_pkt + milk.tea500_pkt + milk.tea1000_pkt + milk.tm500_pkt
        data_dict["milk_products"][
            "milk_total_quantity"] += milk.tm500_litre + milk.std250_litre + milk.std500_litre + milk.smcan_litre + milk.fcmcan_litre + milk.fcm500_litre + milk.fcm1000_litre +milk.tea500_litre + milk.tea1000_litre


        # -----NON_MILK_PRODUCT----#

        # ----Butter----#
        data_dict["non_milk_products"]["Butte"]["BMILK"]["count"] += milk.buttermilk200_pkt
        data_dict["non_milk_products"]["Butte"]["BMILK"]["quantity"] += milk.buttermilk200_litre
        data_dict["non_milk_products"]["Butte"]["total_quantity"] += milk.buttermilk200_litre

        # butter milk Jar
        data_dict["non_milk_products"]["Butte"]["BMJar"]["count"] += milk.bm_jar200_pkt
        data_dict["non_milk_products"]["Butte"]["BMJar"]["quantity"] += milk.bm_jar200_litre
        data_dict["non_milk_products"]["Butte"]["total_quantity"] += milk.bm_jar200_litre

        # butter milk Jar Free
        data_dict["non_milk_products"]["Butte"]["BMJF"]["count"] += milk.bmjf200_pkt
        data_dict["non_milk_products"]["Butte"]["BMJF"]["quantity"] += milk.bmjf200_litre
        data_dict["non_milk_products"]["Butte"]["total_quantity"] += milk.bmjf200_litre

        # ----Curd---#
        data_dict["non_milk_products"]["Curd"]["CURD500"]["count"] += milk.curd500_pkt
        data_dict["non_milk_products"]["Curd"]["CURD500"]["quantity"] += milk.curd500_kgs

        data_dict["non_milk_products"]["Curd"]["CU150"]["count"] += milk.curd150_pkt
        data_dict["non_milk_products"]["Curd"]["CU150"]["quantity"] += milk.curd150_kgs

        data_dict["non_milk_products"]["Curd"]["CURD5000"]["count"] += milk.curd5000_pkt
        data_dict["non_milk_products"]["Curd"]["CURD5000"]["quantity"] += milk.curd5000_kgs

        data_dict["non_milk_products"]["Curd"]["total_quantity"] += milk.curd500_kgs + milk.curd150_kgs + milk.curd5000_kgs

        data_dict["non_milk_products"][
            "milk_total_count"] += milk.buttermilk200_pkt + milk.curd500_pkt + milk.curd150_pkt + milk.curd5000_pkt + milk.bm_jar200_pkt + milk.bmjf200_pkt
        data_dict["non_milk_products"][
            "milk_total_quantity"] += milk.buttermilk200_litre + milk.curd500_kgs + milk.curd150_kgs + milk.curd5000_kgs + milk.bm_jar200_litre + milk.bmjf200_litre
        data_dict["grand_total"] = data_dict["milk_products"]["milk_total_quantity"] + data_dict["non_milk_products"][
            "milk_total_quantity"]
    data = generate_pdf_for_milk_acknowledgement_report(data_dict, user_name, date, session)
    return data


def generate_pdf_for_milk_acknowledgement_report(data_dict, user_name, date, session):
    session_name = ""
    indian = pytz.timezone('Asia/Kolkata')
   
    for ses in reversed(session):
        session = Session.objects.get(id=ses).name
        session_name += session + ', '
   
    file_name = str(date) + '_' + str(session_name) + '_milk_acknoledgement' + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
#     file_path = os.path.join('static/media', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize= A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'Helveticamatrix.ttf'))
    light_color = 0x9b9999
    dark_color = 0x000000
   
    mycanvas.setStrokeColor(colors.lightgrey)
#     mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 795, 'MILK ACKNOWLEDGEMENT')
    mycanvas.line(256-50, 792, 443-50, 792)

    mycanvas.setFont('Helvetica', 13)
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
    mycanvas.drawString(90 + 35-70, 770, 'Shift : ')
    mycanvas.setFillColor(HexColor(dark_color))
   
    shift_name = ""
    for shift in data_dict["shift"]:
        shift_name += Session.objects.get(id=shift).name +', '
       
    mycanvas.drawString(80+100-80, 770, str(shift_name)+"  |  "+'Date : ' + str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))

    # ---------------------------------------Headings------------------------------------------#
    x_a4 = 60
    mycanvas.setFillColor(HexColor(dark_color))

    mycanvas.drawString(120-x_a4, 635+90, 'Type Of Milk')
    mycanvas.drawString(270-x_a4, 635+90, 'Number Of')
    mycanvas.drawString(273-x_a4, 622+90, ' Pockets')
    mycanvas.drawString(400-x_a4, 635+90, 'Quantity')
    mycanvas.drawString(410-x_a4, 622+90, '(Ltr)')
    mycanvas.drawString(515-x_a4, 635+90, 'Total Qty')
    mycanvas.drawString(540-x_a4, 622+90, '(Ltr)')

    mycanvas.setLineWidth(0)
    x_line = 95-x_a4
    Y_line = 670+70
    y_start = 670+70
    x_adjust = 0
    mycanvas.line(x_line, Y_line, x_line + 525, Y_line)
    mycanvas.line(x_line, Y_line - 35, x_line + 525, Y_line - 35)

    for milk in data_dict:
        milk_types = "NON MILK"
        milk_total_count = "non_milk_total_count"
        if milk == "milk_products":
            milk_types = "MILK"
        if milk == "date" or milk == "shift" or milk == "grand_total":
            pass
        else:
            for milk_type in data_dict[milk]:
                if milk_type == "milk_total_count" or milk_type == "milk_total_quantity":
                    pass
                else:
                    mycanvas.drawString(x_line + 5, Y_line - 55, str(milk_type))
                    for product in data_dict[milk][milk_type]:
                        if product != "total_quantity":
                            mycanvas.drawString(x_line + 65, Y_line - 55, str(product))
                            mycanvas.drawRightString(x_line + 260, Y_line - 55,
                                                     str(data_dict[milk][milk_type][product]["count"]))
                            mycanvas.drawRightString(x_line + 390, Y_line - 55,
                                                     str(data_dict[milk][milk_type][product]["quantity"]))
                            Y_line -= 25
                    mycanvas.drawRightString(x_line + 515, Y_line - 30,
                                             str(data_dict[milk][milk_type]["total_quantity"]))

                    Y_line -= 25
                    mycanvas.line(x_line, Y_line - 25, x_line + 525, Y_line - 25)

            mycanvas.line(x_line, Y_line - 25, x_line + 525, Y_line - 25)
            mycanvas.drawString(x_line + 10, Y_line - 40, milk_types + " TOTAL")
            mycanvas.drawRightString(x_line + 260, Y_line - 40, str(int(data_dict[milk]["milk_total_count"])))
            mycanvas.drawRightString(x_line + 390, Y_line - 40, str(data_dict[milk]["milk_total_quantity"]))
            mycanvas.drawRightString(x_line + 515, Y_line - 40, str(data_dict[milk]["milk_total_quantity"]))
            mycanvas.line(x_line, Y_line - 50, x_line + 525, Y_line - 50)
            Y_line -= 25

            # -----------------------------------lines-----------------------------------------#
            mycanvas.line(x_line, y_start, x_line, Y_line - 50)
            mycanvas.line(x_line + 55, y_start - 35 + x_adjust, x_line + 55, Y_line)
            #             mycanvas.line(x_line+135,y_start,x_line+135,Y_line)
            #             mycanvas.line(x_line+190,y_start,x_line+190,Y_line)
            mycanvas.line(x_line + 155, y_start, x_line + 155, Y_line - 25)
            mycanvas.line(x_line + 270, y_start, x_line + 270, Y_line - 25)
            mycanvas.line(x_line + 400, y_start, x_line + 400, Y_line - 50)
            mycanvas.line(x_line + 525, y_start, x_line + 525, Y_line - 50)
            y_start = Y_line - 25
            x_adjust = 35

    mycanvas.drawString(x_line + 280, Y_line - 40, "GRAND TOTAL")
    mycanvas.drawRightString(x_line + 515, Y_line - 40, str(data_dict["grand_total"]))
    mycanvas.line(x_line, Y_line - 50, x_line + 525, Y_line - 50)

    mycanvas.drawString(x_line, Y_line - 120, "Exec(0)")
    mycanvas.drawCentredString(350, Y_line - 120, "DM(Mkg)")
    mycanvas.drawRightString(x_line + 525, Y_line - 120, "AGM(0)")
   
    # mycanvas.setFont('Times-Italic', 12)
    # mycanvas.drawRightString(585, 5,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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


def serve_all_zone_report_per_session(date, session, user_name):
    date_for = date

    session_id = session
   
    if session_id == 'all':
        session_id = list(Session.objects.filter().values_list('id', flat=True))
    else:
        session_id = int(session_id)
        session_id = list(Session.objects.filter(id=session_id).values_list('id', flat=True))
        
    data_dict = {
        "date": date_for,
        "session": session_id,
        'final_results': {'cash': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0, '500': 0, 'total': 0},
                                   'CanMlk' : {'1000': 0, 'total': 0},
                                   'CURD': {'500': 0, '120': 0, '100': 0, '5000': 0,'total': 0},
                                   'BtrMlk':{'200': 0,'total':0},
                                   'BmJar':{'200': 0,'total':0},
                                   'BMJF':{'200': 0,'total':0},
                                   'Lassi': {'200': 0,'total':0}},
                          
                          'card': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0, '500': 0, 'total': 0},
                                   'CanMlk' : {'1000': 0, 'total': 0},
                                   'CURD': {'500': 0, '120': 0, '100': 0, '5000': 0, 'total': 0},
                                   'BtrMlk': {'200': 0,'total':0},
                                   'BmJar':{'200': 0,'total':0},
                                   'BMJF':{'200': 0,'total':0},
                                   'Lassi': {'200': 0,'total':0}},
                          
                          'total_sale': {'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                                                '250': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                 '500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                 '500': {'cash': 0, 'card': 0, 'total': 0}},       
                                         'CanMlk': {'1000': {'cash': 0, 'card': 0, 'total': 0}},
                                         'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                                                  '120': {'cash': 0, 'card': 0, 'total': 0},
                                                  '500': {'cash': 0, 'card': 0, 'total': 0},
                                                  '5000': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BtrMlk': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BmJar': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BMJF': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'Lassi': {'200': {'cash': 0, 'card': 0, 'total': 0}}
                                        }
    }}

    zone_obj = list(Zone.objects.filter().values_list('id', flat=True))

    for zone in zone_obj:

        agent_zone_obj = DailySessionllyZonallySale.objects.filter(zone_id=zone, session_id__in=session_id, delivery_date=date,
                                                                   sold_to__in=["Agent","Leakage"])
        icustomer_zone_obj = DailySessionllyZonallySale.objects.filter(zone_id=zone, session_id__in=session_id,
                                                                       delivery_date=date, sold_to="ICustomer")

        data_dict[zone] = {
            "products_total": 0,
            "route_name": Zone.objects.get(id=zone).name,
            'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                   '250': {'cash': 0, 'card': 0, 'total': 0}},
                                
            'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},

            'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                    '500': {'cash': 0, 'card': 0, 'total': 0}},

            'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                    '500': {'cash': 0, 'card': 0, 'total': 0}},

            'CanMlk': {'1000': {'cash': 0, 'card': 0, 'total': 0}},

            'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                     '120': {'cash': 0, 'card': 0, 'total': 0},
                     '500': {'cash': 0, 'card': 0, 'total': 0},
                     '5000': {'cash': 0, 'card': 0, 'total': 0}},

            'BtrMlk': {'200':{'cash': 0, 'card': 0, 'total': 0}},

            'BmJar': {'200':{'cash': 0, 'card': 0, 'total': 0}},

            'BMJF': {'200': {'cash': 0, 'card': 0, 'total': 0}},

            'Lassi': {'200':{'cash': 0, 'card': 0, 'total': 0}}
        }

        if agent_zone_obj:
            
            #---BtrMlk---#
            data_dict[zone]["BtrMlk"]['200']['cash'] = agent_zone_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            data_dict[zone]["BtrMlk"]['200']['total'] += agent_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            data_dict['final_results']['cash']["BtrMlk"]['200'] += agent_zone_obj.aggregate(Sum('buttermilk200_litre'))[
                'buttermilk200_litre__sum']
            data_dict['final_results']['cash']["BtrMlk"]['total'] += agent_zone_obj.aggregate(Sum('buttermilk200_litre'))[
                'buttermilk200_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']

            data_dict['final_results']['total_sale']['BtrMlk']['200']['cash'] += \
            agent_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            data_dict['final_results']['total_sale']['BtrMlk']['200']['total'] += \
            agent_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']

            #---BtrMlk Jar---#
            data_dict[zone]["BmJar"]['200']['cash'] = agent_zone_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            data_dict[zone]["BmJar"]['200']['total'] += agent_zone_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
            data_dict['final_results']['cash']["BmJar"]['200'] += agent_zone_obj.aggregate(Sum('bm_jar200_litre'))[
                'bm_jar200_litre__sum']
            data_dict['final_results']['cash']["BmJar"]['total'] += agent_zone_obj.aggregate(Sum('bm_jar200_litre'))[
                'bm_jar200_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']

            data_dict['final_results']['total_sale']['BmJar']['200']['cash'] += \
            agent_zone_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
            data_dict['final_results']['total_sale']['BmJar']['200']['total'] += \
            agent_zone_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']

            #---BtrMlk Jar free---#
            data_dict[zone]["BMJF"]['200']['cash'] = agent_zone_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            data_dict[zone]["BMJF"]['200']['total'] += agent_zone_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
            data_dict['final_results']['cash']["BMJF"]['200'] += agent_zone_obj.aggregate(Sum('bmjf200_litre'))[
                'bmjf200_litre__sum']
            data_dict['final_results']['cash']["BMJF"]['total'] += agent_zone_obj.aggregate(Sum('bmjf200_litre'))[
                'bmjf200_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']

            data_dict['final_results']['total_sale']['BMJF']['200']['cash'] += \
            agent_zone_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
            data_dict['final_results']['total_sale']['BMJF']['200']['total'] += \
            agent_zone_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']

            #canmilk
            can_cash_total = agent_zone_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum'] + agent_zone_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum'] +agent_zone_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
            data_dict[zone]["CanMlk"]['1000']['cash'] = round(can_cash_total)
            data_dict[zone]["CanMlk"]['1000']['total'] += round(can_cash_total, 3)

            
            data_dict['final_results']['cash']['CanMlk']['1000'] += round(can_cash_total, 3)
            data_dict['final_results']['total_sale']['CanMlk']['1000']['cash'] += round(can_cash_total, 3)
            data_dict['final_results']['cash']['CanMlk']['total'] += round(can_cash_total, 3)
            data_dict['final_results']['total_sale']['CanMlk']['1000']['total'] += round(can_cash_total, 3)

            
            #---Lassi---#
            data_dict[zone]["Lassi"]['200']['cash'] = agent_zone_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            data_dict[zone]["Lassi"]['200']['total'] += agent_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            data_dict['final_results']['cash']["Lassi"]['200'] += agent_zone_obj.aggregate(Sum('lassi200_kgs'))[
                'lassi200_kgs__sum']
            data_dict['final_results']['cash']["Lassi"]['total'] += agent_zone_obj.aggregate(Sum('lassi200_kgs'))[
                'lassi200_kgs__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']

            data_dict['final_results']['total_sale']['Lassi']['200']['cash'] += \
            agent_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            data_dict['final_results']['total_sale']['Lassi']['200']['total'] += \
            agent_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            
            # --SM--#
            data_dict[zone]["SM"]['500']['cash'] = agent_zone_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            data_dict[zone]["SM"]['500']['total'] += agent_zone_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            data_dict['final_results']['cash']["SM"]['500'] += agent_zone_obj.aggregate(Sum('std500_litre'))[
                'std500_litre__sum']
            data_dict['final_results']['cash']["SM"]['total'] += agent_zone_obj.aggregate(Sum('std500_litre'))[
                'std500_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']

            data_dict['final_results']['total_sale']['SM']['500']['cash'] += \
            agent_zone_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            data_dict['final_results']['total_sale']['SM']['500']['total'] += \
            agent_zone_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']

            data_dict[zone]["SM"]['250']['cash'] = agent_zone_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            data_dict[zone]["SM"]['250']['total'] += agent_zone_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            data_dict['final_results']['cash']["SM"]['250'] += agent_zone_obj.aggregate(Sum('std250_litre'))[
                'std250_litre__sum']
            data_dict['final_results']['cash']["SM"]['total'] += agent_zone_obj.aggregate(Sum('std250_litre'))[
                'std250_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']

            data_dict['final_results']['total_sale']['SM']['250']['cash'] += \
            agent_zone_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            data_dict['final_results']['total_sale']['SM']['250']['total'] += \
            agent_zone_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']

            # --TM--#
            data_dict[zone]["TM"]['500']['cash'] = agent_zone_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            data_dict[zone]["TM"]['500']['total'] += agent_zone_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            data_dict['final_results']['cash']["TM"]['500'] += agent_zone_obj.aggregate(Sum('tm500_litre'))[
                'tm500_litre__sum']
            data_dict['final_results']['cash']["TM"]['total'] += agent_zone_obj.aggregate(Sum('tm500_litre'))[
                'tm500_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']

            data_dict['final_results']['total_sale']['TM']['500']['cash'] += \
            agent_zone_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            data_dict['final_results']['total_sale']['TM']['500']['total'] += \
            agent_zone_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']

            # --FCM--#
            data_dict[zone]["FCM"]['500']['cash'] = agent_zone_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            data_dict[zone]["FCM"]['500']['total'] += agent_zone_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            data_dict['final_results']['cash']["FCM"]['500'] += agent_zone_obj.aggregate(Sum('fcm500_litre'))[
                'fcm500_litre__sum']
            data_dict['final_results']['cash']["FCM"]['total'] += agent_zone_obj.aggregate(Sum('fcm500_litre'))[
                'fcm500_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']

            data_dict['final_results']['total_sale']['FCM']['500']['cash'] += \
            agent_zone_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            data_dict['final_results']['total_sale']['FCM']['500']['total'] += \
            agent_zone_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']

            
            data_dict[zone]["FCM"]['1000']['cash'] = agent_zone_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            data_dict[zone]["FCM"]['1000']['total'] += agent_zone_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            data_dict['final_results']['cash']["FCM"]['1000'] += agent_zone_obj.aggregate(Sum('fcm1000_litre'))[
                'fcm1000_litre__sum']
            data_dict['final_results']['cash']["FCM"]['total'] += agent_zone_obj.aggregate(Sum('fcm1000_litre'))[
                'fcm1000_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']

            data_dict['final_results']['total_sale']['FCM']['1000']['cash'] += \
            agent_zone_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            data_dict['final_results']['total_sale']['FCM']['1000']['total'] += \
            agent_zone_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
                

            # --TMATE--#
            data_dict[zone]["TMATE"]['500']['cash'] = agent_zone_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            data_dict[zone]["TMATE"]['500']['total'] += agent_zone_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            data_dict['final_results']['cash']["TMATE"]['500'] += agent_zone_obj.aggregate(Sum('tea500_litre'))[
                'tea500_litre__sum']
            data_dict['final_results']['cash']["TMATE"]['total'] += agent_zone_obj.aggregate(Sum('tea500_litre'))[
                'tea500_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']

            data_dict['final_results']['total_sale']['TMATE']['500']['cash'] += \
            agent_zone_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            data_dict['final_results']['total_sale']['TMATE']['500']['total'] += \
            agent_zone_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']

            
            data_dict[zone]["TMATE"]['1000']['cash'] = agent_zone_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            data_dict[zone]["TMATE"]['1000']['total'] += agent_zone_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            data_dict['final_results']['cash']["TMATE"]['1000'] += agent_zone_obj.aggregate(Sum('tea1000_litre'))[
                'tea1000_litre__sum']
            data_dict['final_results']['cash']["TMATE"]['total'] += agent_zone_obj.aggregate(Sum('tea1000_litre'))[
                'tea1000_litre__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']

            data_dict['final_results']['total_sale']['TMATE']['1000']['cash'] += \
            agent_zone_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            data_dict['final_results']['total_sale']['TMATE']['1000']['total'] += \
            agent_zone_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']

            # --CURD--#
            
            data_dict[zone]["CURD"]['100']['cash'] = agent_zone_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            data_dict[zone]["CURD"]['100']['total'] += agent_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['100'] += agent_zone_obj.aggregate(Sum('cupcurd_kgs'))[
                'cupcurd_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['total'] += agent_zone_obj.aggregate(Sum('cupcurd_kgs'))[
                'cupcurd_kgs__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['100']['cash'] += \
            agent_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['100']['total'] += \
            agent_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            
            data_dict[zone]["CURD"]['120']['cash'] = agent_zone_obj.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
            data_dict[zone]["CURD"]['120']['total'] += agent_zone_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['120'] += agent_zone_obj.aggregate(Sum('curd150_kgs'))[
                'curd150_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['total'] += agent_zone_obj.aggregate(Sum('curd150_kgs'))[
                'curd150_kgs__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['120']['cash'] += \
            agent_zone_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['120']['total'] += \
            agent_zone_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']

            data_dict[zone]["CURD"]['500']['cash'] = agent_zone_obj.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
            data_dict[zone]["CURD"]['500']['total'] += agent_zone_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['500'] += agent_zone_obj.aggregate(Sum('curd500_kgs'))[
                'curd500_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['total'] += agent_zone_obj.aggregate(Sum('curd500_kgs'))[
                'curd500_kgs__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['500']['cash'] += \
            agent_zone_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['500']['total'] += \
            agent_zone_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']

            data_dict[zone]["CURD"]['5000']['cash'] = agent_zone_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            data_dict[zone]["CURD"]['5000']['total'] += agent_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['5000'] += agent_zone_obj.aggregate(Sum('curd5000_kgs'))[
                'curd5000_kgs__sum']
            data_dict['final_results']['cash']["CURD"]['total'] += agent_zone_obj.aggregate(Sum('curd5000_kgs'))[
                'curd5000_kgs__sum']

            data_dict[zone]['products_total'] += agent_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['5000']['cash'] += \
            agent_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['5000']['total'] += \
            agent_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            
            
            

        # #       Card Sale
        if icustomer_zone_obj:
            
            #---BtrMlk---#
            data_dict[zone]["BtrMlk"]['200']['card'] = icustomer_zone_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            data_dict[zone]["BtrMlk"]['200']['total'] += icustomer_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            data_dict['final_results']['card']["BtrMlk"]['200'] += icustomer_zone_obj.aggregate(Sum('buttermilk200_litre'))[
                'buttermilk200_litre__sum']
            data_dict['final_results']['card']["BtrMlk"]['total'] += icustomer_zone_obj.aggregate(Sum('buttermilk200_litre'))[
                'buttermilk200_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']

            data_dict['final_results']['total_sale']['BtrMlk']['200']['card'] += \
            icustomer_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            data_dict['final_results']['total_sale']['BtrMlk']['200']['total'] += \
            icustomer_zone_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']

            #---BtrMlk Jar---#
            data_dict[zone]["BmJar"]['200']['card'] = icustomer_zone_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            data_dict[zone]["BmJar"]['200']['total'] += icustomer_zone_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            data_dict['final_results']['card']["BmJar"]['200'] += icustomer_zone_obj.aggregate(Sum('bm_jar200_pkt'))[
                'bm_jar200_pkt__sum']
            data_dict['final_results']['card']["BmJar"]['total'] += icustomer_zone_obj.aggregate(Sum('bm_jar200_pkt'))[
                'bm_jar200_pkt__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']

            data_dict['final_results']['total_sale']['BmJar']['200']['card'] += \
            icustomer_zone_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            data_dict['final_results']['total_sale']['BmJar']['200']['total'] += \
            icustomer_zone_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']


            #---BtrMlk Jar free---#
            data_dict[zone]["BMJF"]['200']['card'] = icustomer_zone_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            data_dict[zone]["BMJF"]['200']['total'] += icustomer_zone_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            data_dict['final_results']['card']["BMJF"]['200'] += icustomer_zone_obj.aggregate(Sum('bmjf200_pkt'))[
                'bmjf200_pkt__sum']
            data_dict['final_results']['card']["BMJF"]['total'] += icustomer_zone_obj.aggregate(Sum('bmjf200_pkt'))[
                'bmjf200_pkt__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']

            data_dict['final_results']['total_sale']['BMJF']['200']['card'] += \
            icustomer_zone_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            data_dict['final_results']['total_sale']['BMJF']['200']['total'] += \
            icustomer_zone_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']

            #canmilk
            can_card_total = icustomer_zone_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum'] + icustomer_zone_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum'] +icustomer_zone_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
            data_dict[zone]["CanMlk"]['1000']['card'] = round(can_card_total)
            data_dict[zone]["CanMlk"]['1000']['total'] += round(can_card_total, 3)

            data_dict['final_results']['card']['CanMlk']['1000'] = round(can_card_total, 3)
            data_dict['final_results']['total_sale']['CanMlk']['1000']['card'] = round(can_card_total, 3)
            data_dict['final_results']['card']['CanMlk']['total'] = round(can_card_total, 3)
            data_dict['final_results']['total_sale']['CanMlk']['1000']['total'] += round(can_card_total, 3)
            
            #---Lassi---#
            data_dict[zone]["Lassi"]['200']['card'] = icustomer_zone_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            data_dict[zone]["Lassi"]['200']['total'] += icustomer_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            data_dict['final_results']['card']["Lassi"]['200'] += icustomer_zone_obj.aggregate(Sum('lassi200_kgs'))[
                'lassi200_kgs__sum']
            data_dict['final_results']['card']["Lassi"]['total'] += icustomer_zone_obj.aggregate(Sum('lassi200_kgs'))[
                'lassi200_kgs__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']

            data_dict['final_results']['total_sale']['Lassi']['200']['card'] += \
            icustomer_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            data_dict['final_results']['total_sale']['Lassi']['200']['total'] += \
            icustomer_zone_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            
            # --SM--#
            data_dict[zone]["SM"]['500']['card'] = icustomer_zone_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            data_dict[zone]["SM"]['500']['total'] += icustomer_zone_obj.aggregate(Sum('std500_litre'))[
                'std500_litre__sum']
            data_dict['final_results']['card']["SM"]['500'] += icustomer_zone_obj.aggregate(Sum('std500_litre'))[
                'std500_litre__sum']
            data_dict['final_results']['card']["SM"]['total'] += icustomer_zone_obj.aggregate(Sum('std500_litre'))[
                'std500_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']

            data_dict['final_results']['total_sale']['SM']['500']['card'] += \
            icustomer_zone_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            data_dict['final_results']['total_sale']['SM']['500']['total'] += \
            icustomer_zone_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']

            data_dict[zone]["SM"]['250']['card'] = icustomer_zone_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            data_dict[zone]["SM"]['250']['total'] += icustomer_zone_obj.aggregate(Sum('std250_litre'))[
                'std250_litre__sum']
            data_dict['final_results']['card']["SM"]['250'] += icustomer_zone_obj.aggregate(Sum('std250_litre'))[
                'std250_litre__sum']
            data_dict['final_results']['card']["SM"]['total'] += icustomer_zone_obj.aggregate(Sum('std250_litre'))[
                'std250_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']

            data_dict['final_results']['total_sale']['SM']['250']['card'] += \
            icustomer_zone_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            data_dict['final_results']['total_sale']['SM']['250']['total'] += \
            icustomer_zone_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']

            # --TM--#
            data_dict[zone]["TM"]['500']['card'] = icustomer_zone_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            data_dict[zone]["TM"]['500']['total'] += icustomer_zone_obj.aggregate(Sum('tm500_litre'))[
                'tm500_litre__sum']
            data_dict['final_results']['card']["TM"]['500'] += icustomer_zone_obj.aggregate(Sum('tm500_litre'))[
                'tm500_litre__sum']
            data_dict['final_results']['card']["TM"]['total'] += icustomer_zone_obj.aggregate(Sum('tm500_litre'))[
                'tm500_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']

            data_dict['final_results']['total_sale']['TM']['500']['card'] += \
            icustomer_zone_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            data_dict['final_results']['total_sale']['TM']['500']['total'] += \
            icustomer_zone_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']

            # --FCM--#
            data_dict[zone]["FCM"]['500']['card'] = icustomer_zone_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            data_dict[zone]["FCM"]['500']['total'] += icustomer_zone_obj.aggregate(Sum('fcm500_litre'))[
                'fcm500_litre__sum']
            data_dict['final_results']['card']["FCM"]['500'] += icustomer_zone_obj.aggregate(Sum('fcm500_litre'))[
                'fcm500_litre__sum']
            data_dict['final_results']['card']["FCM"]['total'] += icustomer_zone_obj.aggregate(Sum('fcm500_litre'))[
                'fcm500_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']

            data_dict['final_results']['total_sale']['FCM']['500']['card'] += \
            icustomer_zone_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            data_dict['final_results']['total_sale']['FCM']['500']['total'] += \
            icustomer_zone_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']

            data_dict[zone]["FCM"]['1000']['card'] = icustomer_zone_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            data_dict[zone]["FCM"]['1000']['total'] += icustomer_zone_obj.aggregate(Sum('fcm1000_litre'))[
                'fcm1000_litre__sum']
            data_dict['final_results']['card']["FCM"]['1000'] += icustomer_zone_obj.aggregate(Sum('fcm1000_litre'))[
                'fcm1000_litre__sum']
            data_dict['final_results']['card']["FCM"]['total'] += icustomer_zone_obj.aggregate(Sum('fcm1000_litre'))[
                'fcm1000_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']

            data_dict['final_results']['total_sale']['FCM']['1000']['card'] += \
            icustomer_zone_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            data_dict['final_results']['total_sale']['FCM']['1000']['total'] += \
            icustomer_zone_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            
            # --TMATE--#
            data_dict[zone]["TMATE"]['500']['card'] = icustomer_zone_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            data_dict[zone]["TMATE"]['500']['total'] += icustomer_zone_obj.aggregate(Sum('tea500_litre'))[
                'tea500_litre__sum']
            data_dict['final_results']['card']["TMATE"]['500'] += icustomer_zone_obj.aggregate(Sum('tea500_litre'))[
                'tea500_litre__sum']
            data_dict['final_results']['card']["TMATE"]['total'] += icustomer_zone_obj.aggregate(Sum('tea500_litre'))[
                'tea500_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']

            data_dict['final_results']['total_sale']['TMATE']['500']['card'] += \
            icustomer_zone_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            data_dict['final_results']['total_sale']['TMATE']['500']['total'] += \
            icustomer_zone_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']

            data_dict[zone]["TMATE"]['1000']['card'] = icustomer_zone_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            data_dict[zone]["TMATE"]['1000']['total'] += icustomer_zone_obj.aggregate(Sum('tea1000_litre'))[
                'tea1000_litre__sum']
            data_dict['final_results']['card']["TMATE"]['1000'] += icustomer_zone_obj.aggregate(Sum('tea1000_litre'))[
                'tea1000_litre__sum']
            data_dict['final_results']['card']["TMATE"]['total'] += icustomer_zone_obj.aggregate(Sum('tea1000_litre'))[
                'tea1000_litre__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']

            data_dict['final_results']['total_sale']['TMATE']['1000']['card'] += \
            icustomer_zone_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            data_dict['final_results']['total_sale']['TMATE']['1000']['total'] += \
            icustomer_zone_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            

            # --CURD--#
            
            data_dict[zone]["CURD"]['100']['card'] = icustomer_zone_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            data_dict[zone]["CURD"]['100']['total'] += icustomer_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            data_dict['final_results']['card']["CURD"]['100'] += icustomer_zone_obj.aggregate(Sum('cupcurd_kgs'))[
                'cupcurd_kgs__sum']
            data_dict['final_results']['card']["CURD"]['total'] += icustomer_zone_obj.aggregate(Sum('cupcurd_kgs'))[
                'cupcurd_kgs__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['100']['card'] += \
            icustomer_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['100']['total'] += \
            icustomer_zone_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            
            
            data_dict[zone]["CURD"]['120']['card'] = icustomer_zone_obj.aggregate(Sum('curd150_pkt'))[
                'curd150_pkt__sum']
            data_dict[zone]["CURD"]['120']['total'] += icustomer_zone_obj.aggregate(Sum('curd150_kgs'))[
                'curd150_kgs__sum']
            data_dict['final_results']['card']["CURD"]['120'] += icustomer_zone_obj.aggregate(Sum('curd150_kgs'))[
                'curd150_kgs__sum']
            data_dict['final_results']['card']["CURD"]['total'] += icustomer_zone_obj.aggregate(Sum('curd150_kgs'))[
                'curd150_kgs__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['120']['card'] += \
            icustomer_zone_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['120']['total'] += \
            icustomer_zone_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']

            data_dict[zone]["CURD"]['500']['card'] = icustomer_zone_obj.aggregate(Sum('curd500_pkt'))[
                'curd500_pkt__sum']
            data_dict[zone]["CURD"]['500']['total'] += icustomer_zone_obj.aggregate(Sum('curd500_kgs'))[
                'curd500_kgs__sum']
            data_dict['final_results']['card']["CURD"]['500'] += icustomer_zone_obj.aggregate(Sum('curd500_kgs'))[
                'curd500_kgs__sum']
            data_dict['final_results']['card']["CURD"]['total'] += icustomer_zone_obj.aggregate(Sum('curd500_kgs'))[
                'curd500_kgs__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['500']['card'] += \
            icustomer_zone_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['500']['total'] += \
            icustomer_zone_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']

            data_dict[zone]["CURD"]['5000']['card'] = icustomer_zone_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            data_dict[zone]["CURD"]['5000']['total'] += icustomer_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            data_dict['final_results']['card']["CURD"]['5000'] += icustomer_zone_obj.aggregate(Sum('curd5000_kgs'))[
                'curd5000_kgs__sum']
            data_dict['final_results']['card']["CURD"]['total'] += icustomer_zone_obj.aggregate(Sum('curd5000_kgs'))[
                'curd5000_kgs__sum']

            data_dict[zone]['products_total'] += icustomer_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']

            data_dict['final_results']['total_sale']['CURD']['5000']['card'] += \
            icustomer_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            data_dict['final_results']['total_sale']['CURD']['5000']['total'] += \
            icustomer_zone_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    data = generate_pdf_for_all_zone_report_per_session(data_dict, user_name, date, session_id)
    return data



def serve_daily_sale_for_selected_zone(date, zone, user_name,session_id):
    
    session_id = session_id
   
    if session_id == 'all':
        session_id = list(Session.objects.filter().values_list('id', flat=True))
    else:
        session_id = int(session_id)
        session_id = list(Session.objects.filter(id=session_id).values_list('id', flat=True))
    
    zone_id = zone
    date = datetime.datetime.strptime(date, '%Y-%m-%d')

    business_ids = list(Business.objects.filter(zone_id=zone_id).values_list('id', flat=True))

    agent_salegroup_obj = list(
        SaleGroup.objects.filter(business_id__in=business_ids, date=date,session_id__in=session_id).values_list('id', flat=True))
    agent_salegroup = SaleGroup.objects.filter(business_id__in=business_ids, date=date,session_id__in=session_id)
    agent_sale = Sale.objects.filter(sale_group_id__in=agent_salegroup_obj)

    icus_salegroup_obj = list(ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date.month,
                                                                date__year=date.year,session_id__in=session_id).values_list('id', flat=True))
    icus_salegroup = ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date.month,
                                                       date__year=date.year,session_id__in=session_id)
    icus_sale = ICustomerSale.objects.filter(icustomer_sale_group_id__in=icus_salegroup_obj)

    products = Product.objects.filter().order_by('display_ordinal')
    icus_products = Product.objects.filter(group_id=1).order_by('display_ordinal')

    data_dict = {
        "agent_dict": None,
        "icus_dict": None
    }

    agent_dict = {
        "zone_details": {
            "zone_id": zone_id,
            "zone_name": Zone.objects.get(id=zone_id).name,
            "date": date
        },
        "agent_details": [],
        "sale_details": {},
        "grand_total": None,
        "product_count": {
        }
    }

    for sale_group in agent_salegroup:
        count = 0
        for sale_grp in agent_dict["agent_details"]:
            if sale_grp["sale_group_date"] == sale_group.date:
                if sale_grp["business_id"] == sale_group.business.id:
                    sale_grp["business_code"] = sale_group.business.code
                    sale_grp["business_id"] = sale_group.business.id
                    sale_grp["agent_name"] = BusinessAgentMap.objects.get(
                        business_id=sale_group.business.id).agent.first_name[:5]
                    sale_grp["total_cost"] += sale_group.total_cost
                    sale_grp["sale_group_date"] = sale_group.date
                    count += 1
        if count == 0:
            temp_sale_group_dict = {
                "business_code": sale_group.business.code,
                "business_id": sale_group.business.id,
                "agent_name": BusinessAgentMap.objects.get(
                    business_id=sale_group.business.id).agent.first_name[:5],
                "total_cost": sale_group.total_cost,
                "sale_group_id": sale_group.id,
                "sale_group_date": sale_group.date
            }
            agent_dict["agent_details"].append(temp_sale_group_dict)

    for sale in agent_sale:
        count = 0
        for sale_group in agent_dict["sale_details"]:
            for business in agent_dict["sale_details"][sale_group]:
                if business == sale.sale_group.business.id:
                    if agent_dict["sale_details"][sale_group][business]["sale_group_date"] == sale.sale_group.date:
                        if not sale.product.id in agent_dict["sale_details"][sale_group][business]:
                            agent_dict["sale_details"][sale_group][business][sale.product.id] = {
                                "product_name": sale.product.name,
                                "sale_count": sale.count,
                                "sale_cost": sale.cost,
                            }
                        else:
                            agent_dict["sale_details"][sale_group][business][sale.product.id][
                                "product_name"] = sale.product.name
                            agent_dict["sale_details"][sale_group][business][sale.product.id][
                                "sale_count"] += sale.count
                            agent_dict["sale_details"][sale_group][business][sale.product.id]["sale_cost"] += sale.cost
                        count += 1
        if count == 0:
            #             print(count)
            if not sale.sale_group.id in agent_dict["sale_details"]:
                agent_dict["sale_details"][sale.sale_group.id] = {}

            if not sale.sale_group.business.id in agent_dict["sale_details"][sale.sale_group.id]:
                agent_dict["sale_details"][sale.sale_group.id][sale.sale_group.business.id] = {
                    "product_total_cost": None,
                    "sale_group_date": sale.sale_group.date,
                }

            if not sale.product.id in agent_dict["sale_details"][sale.sale_group.id][sale.sale_group.business.id]:
                agent_dict["sale_details"][sale.sale_group.id][sale.sale_group.business.id][sale.product.id] = {
                    "product_name": sale.product.name,
                    "sale_count": sale.count,
                    "sale_cost": sale.cost,
                }

    grand_total = 0
    for data in agent_dict["agent_details"]:
        grand_total += data["total_cost"]
    agent_dict["grand_total"] = grand_total

    sale_group = []
    business = []
    for sale in agent_sale:
        sale_group.append(sale.sale_group.id)
        business.append(sale.sale_group.business.id)
    sale_group = set(sale_group)
    sale_group = list(sale_group)

    product_sale_count = 0
    for sale_group_id in sale_group:
        for business_id in business:
            business_id_single = business_id
            total_cost = 0
            products_list = []
            product_sale_count = 0
            try:
                for product_id in agent_dict["sale_details"][sale_group_id][business_id]:
                    products_list.append(product_id)

                for product in products:
                    #                     adding products in data_dicts
                    if not product.id in agent_dict["product_count"]:
                        agent_dict["product_count"][product.id] = 0
                    if not (product.id in products_list):
                        total_cost += 0
                    if product.id in products_list:
                        total_cost += agent_dict["sale_details"][sale_group_id][business_id][product.id]["sale_cost"]
                        product_sale_count = agent_dict["sale_details"][sale_group_id][business_id][product.id][
                            "sale_count"]
                        agent_dict["product_count"][product.id] += product_sale_count
                agent_dict["sale_details"][sale_group_id][business_id]["product_total_cost"] = total_cost
            except:
                continue
            if business_id_single == business_id:
                break
    data_dict["agent_dict"] = agent_dict

    # -------------------------------------------------ICustomer_Details---------------------------------------------------- #

    icus_dict = {
        "counter_details": {
            "date": date,
            "counter_id": zone_id,
            "counter_name": Zone.objects.get(id=zone_id).name,
            "employee_name": []
        },
        "agent_details": [],
        "icustomer_sale_details": {},
        "grand_total": None,
        "grand_total_month": None,
        "product_total_count": {}
    }

    for icustomer_sale_group in icus_salegroup:
        #         print(icustomer_sale_group.id)
        order_for_date = str(icustomer_sale_group.date)
        my_date = datetime.datetime.strptime(order_for_date, "%Y-%m-%d")
        my_month = my_date.month
        my_month_name = month_name[my_date.month]
        my_days = monthrange(my_date.year, my_month)[1]
        count = 0
        for agent_details in icus_dict["agent_details"]:
            if agent_details["for_date"] == order_for_date and agent_details[
                "icustomer_id"] == icustomer_sale_group.icustomer_id:
                agent_details["total_cost"] += icustomer_sale_group.total_cost
                count += 1
        if count == 0:
            tempicustomer_sale_group_dict = {
                "year": my_date.year,
                "for_date": order_for_date,
                "for_month": my_month_name,
                "for_day": my_days,
                "business_code": icustomer_sale_group.business.code,
                "icustomer_id": icustomer_sale_group.icustomer_id,
                "customer_name": icustomer_sale_group.icustomer.user_profile.user.first_name[:5],
                "total_cost": icustomer_sale_group.total_cost,
                "icustomer_sale_group_id": icustomer_sale_group.id,
            }
            icus_dict["agent_details"].append(tempicustomer_sale_group_dict)

    product_list = []
    for product in icus_products:
        product_list.append(product.id)

    #     for product_id in product_list:
    for icustomer_sale in icus_sale:
        #         print(icustomer_sale.icustomer_sale_group.icustomer_id)
        try:
            if str(icustomer_sale.icustomer_sale_group.date) in icus_dict["icustomer_sale_details"]:
                if icustomer_sale.icustomer_sale_group.icustomer_id in icus_dict["icustomer_sale_details"][
                    str(icustomer_sale.icustomer_sale_group.date)]:
                    if not icustomer_sale.product.id in \
                           icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                               icustomer_sale.icustomer_sale_group.icustomer_id]:
                        pass
                    else:
                        icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                            icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id][
                            "product_name"] = icustomer_sale.product.name
                        icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                            icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id][
                            "icustomer_sale_count"] += icustomer_sale.count
                        icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                            icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id][
                            "icustomer_sale_cost"] += icustomer_sale.cost
            #                         data_dict["icustomer_sale_details"][icustomer_sale.icustomer_sale_group.date][icustomer_sale.icustomer_sale_group.business.id][icustomer_sale.product.id]["icustomer_sale_group"].append(icustomer_sale.icustomer_sale_group.id)

            if not str(icustomer_sale.icustomer_sale_group.date) in icus_dict["icustomer_sale_details"]:
                icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)] = {}

            if not icustomer_sale.icustomer_sale_group.icustomer_id in icus_dict["icustomer_sale_details"][
                str(icustomer_sale.icustomer_sale_group.date)]:
                icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                    icustomer_sale.icustomer_sale_group.icustomer_id] = {
                    "product_total_cost": None,
                    "product_cost_month": None,
                }
            if not icustomer_sale.product.id in \
                   icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                       icustomer_sale.icustomer_sale_group.icustomer_id]:
                icus_dict["icustomer_sale_details"][str(icustomer_sale.icustomer_sale_group.date)][
                    icustomer_sale.icustomer_sale_group.icustomer_id][icustomer_sale.product.id] = {
                    "product_name": icustomer_sale.product.name,
                    "icustomer_sale_count": icustomer_sale.count,
                    "icustomer_sale_cost": icustomer_sale.cost,
                    #                     "icustomer_sale_group" : [icustomer_sale.icustomer_sale_group.id]
                }
        except:
            pass

    #   grand total
    grand_total = 0
    grand_total_month = 0
    for data in icus_dict["agent_details"]:
        grand_total += data["total_cost"]
        grand_total_month += data["total_cost"] * data["for_day"]
    icus_dict["grand_total"] = grand_total
    icus_dict["grand_total_month"] = grand_total_month

    for sale_date in icus_dict["icustomer_sale_details"]:
        for i_customer in icus_dict["icustomer_sale_details"][sale_date]:
            product_in_business = []

            for product in icus_dict["icustomer_sale_details"][sale_date][i_customer]:
                product_in_business.append(product)

            # checking a products present in under guven business_id
            total_cost = 0
            for product in product_list:
                if product in product_in_business:
                    total_cost += icus_dict["icustomer_sale_details"][sale_date][i_customer][product][
                        "icustomer_sale_cost"]
            icus_dict["icustomer_sale_details"][sale_date][i_customer]["product_total_cost"] = total_cost

            current_id = 0
            for business in icus_dict["agent_details"]:
                if current_id == business["icustomer_id"]:
                    continue
                if i_customer == business["icustomer_id"]:
                    #                 print(business["business_id"])
                    current_id = i_customer
                    icus_dict["icustomer_sale_details"][sale_date][i_customer]["product_cost_month"] = total_cost * \
                                                                                                       business[
                                                                                                           "for_day"]

            #            adding products in data_dicts
            try:
                for product in product_list:
                    if not product in icus_dict["product_total_count"]:
                        icus_dict["product_total_count"][product] = 0

                    if product in product_in_business:
                        product_sale_count = icus_dict["icustomer_sale_details"][sale_date][i_customer][product][
                            "icustomer_sale_count"]
                        icus_dict["product_total_count"][product] += product_sale_count
            except:
                pass
    data_dict["icus_dict"] = icus_dict

    data = generate_pdf_for_daily_sale_for_selected_zone(data_dict, user_name, date, zone,session_id)
    return data


def generate_pdf_for_daily_sale_for_selected_zone(data_dict, user_name, date, zone,session_id): 
    
    session_name = ""
    
    for ses in reversed(session_id):
        session = Session.objects.get(id=ses).name
        session_name += session + ', '
    
    zone_name = Zone.objects.get(id=zone).name
    
    file_name = str(date) + '_' + str(zone_name)+ '_' + str(session_name) + '_report.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    # print(file_path)
    mycanvas = canvas.Canvas(file_path, pagesize=(10.7 * inch, 12 * inch))

    # ________Head_lines________#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))

    #     mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Courier', 13)
    mycanvas.drawCentredString(350, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
    mycanvas.setFont('Courier', 13)
    mycanvas.drawCentredString(350, 785, 'Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Courier', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(350, 755, 'Daily Counter Report : Agents Sales')
    mycanvas.line(212, 752, 490, 752)

    mycanvas.setFont('Courier', 13)
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(60, 730, 'Zone : ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(120, 730, str(data_dict["agent_dict"]["zone_details"]["zone_name"]))

    #     mycanvas.setFillColor(HexColor(light_color))
    #     mycanvas.drawString(60, 700, 'Employees : ')
    #     mycanvas.setFillColor(HexColor(dark_color))

    #     name_emp = ""
    #     for name in list(set(data_dict["agent_dict"]["zone_details"]["employee_name"])):
    #         name_emp += name+","
    #     mycanvas.drawString(120, 700, str(name_emp))

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(60, 715, 'Date : ')
    mycanvas.drawString(60, 700, 'Business : ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(150, 700, str(session_name))
    date_in_format = datetime.datetime.strptime(str(data_dict["agent_dict"]["zone_details"]["date"]), '%Y-%m-%d %H:%M:%S')
    date = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
   
    mycanvas.drawString(120, 715, str(date))
    

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(360, 730, 'Report Generated @: ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(510, 730, str(datetime.datetime.strftime(datetime.datetime.now(timezone('Asia/Kolkata')), '%d-%m-%Y, %H:%M %p')))


    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(350, 715, 'Report Generated by: ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(510, 715, str(user_name))

    if data_dict["agent_dict"]["agent_details"] == []:
        mycanvas.drawCentredString(350, 680, '{------There is no report to show------}')

    else:

        # _____________table header_____________#

        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Courier', 13)
        mycanvas.drawString(28, 675, 'S.No')
        mycanvas.drawString(63, 675, 'booth')
        mycanvas.drawString(65, 663, 'code')
        mycanvas.drawString(109, 675, 'agent')
        mycanvas.drawString(110, 663, 'name')
        x_axis = 175
        y_axis = 675
        line_x_axis = 50

        # _____________ Product heading _____________#

        products = list(Product.objects.filter(is_active=True).order_by('display_ordinal'))

        for product in products:
            product_name = list(product.short_name.split(" "))
            mycanvas.drawString(x_axis-20, y_axis, str(product_name[0][:3]))
            try:
                mycanvas.drawString(x_axis-19, y_axis - 12, str(product_name[1]))
            except:
                pass
            if product.short_name == products[-1].short_name:
                x_axis += 40
                mycanvas.drawString(x_axis-25, y_axis, 'Total')
            # table top line
            mycanvas.setLineWidth(0)
            mycanvas.line(line_x_axis-25, y_axis + 15, x_axis + 40, y_axis + 15)
            # table bottom line
            mycanvas.line(line_x_axis-25, y_axis - 15, x_axis + 40, y_axis - 15)
            x_axis += 41
            # _____________ Agent_name,Business_code,Product ___________#

        y_axix_agent_booth = 630
        x_axis_agent_booth = 90
        y_axis_product = 675

        for index, business in enumerate(data_dict["agent_dict"]["agent_details"], start=1):
            mycanvas.setFont('Courier', 13)
            mycanvas.drawRightString(line_x_axis, y_axix_agent_booth, str(index))
            mycanvas.drawString(x_axis_agent_booth-25, y_axix_agent_booth, str(business["business_code"]))
            mycanvas.drawString(x_axis_agent_booth+18, y_axix_agent_booth, str(business["agent_name"]))
            sale_group_id = business["sale_group_id"]

    #         # _________lines_between_agent_name___________#

            mycanvas.line(x_axis_agent_booth - 30, y_axix_agent_booth + 60, x_axis_agent_booth-30,y_axix_agent_booth - 15)
            mycanvas.line(x_axis_agent_booth + 15, y_axix_agent_booth + 60, x_axis_agent_booth+15,y_axix_agent_booth - 15)
            mycanvas.line(x_axis_agent_booth + 60, y_axix_agent_booth + 60, x_axis_agent_booth + 60,y_axix_agent_booth - 15)

    #         # _________left_and_right_border___________#

            mycanvas.line(line_x_axis-25, y_axix_agent_booth + 60, line_x_axis-25, y_axix_agent_booth - 15)
            mycanvas.line(x_axis, y_axix_agent_booth + 60, x_axis, y_axix_agent_booth - 15)

            y_axix_agent_booth -= 26
            products_list = []

            try:
                for product_id in data_dict["agent_dict"]["sale_details"][business["sale_group_id"]][
                    business["business_id"]]:
                    if product_id == "product_total_cost" or product_id == "sale_group_date":
                        continue
                    products_list.append(product_id)
            except:
                pass
            x_axis_product = 175
            total_cost = 0

            for product in products:
                if not (product.id in products_list):
                    mycanvas.drawRightString(x_axis_product+18, y_axis_product - 45, "")
    #                 x_axis_product += 35
                if (product.id in products_list):
                    mycanvas.drawRightString(x_axis_product+18, y_axis_product - 45, str(int(
                        data_dict["agent_dict"]["sale_details"][business["sale_group_id"]][business["business_id"]][
                            product.id]["sale_count"])))
    #                 x_axis_product += 40
                    total_cost += \
                    data_dict["agent_dict"]["sale_details"][business["sale_group_id"]][business["business_id"]][
                        product.id]["sale_cost"]
                
                mycanvas.setLineWidth(0)
                mycanvas.line(x_axis_product+20, y_axis_product + 15, x_axis_product+20, y_axis_product - 60)
                x_axis_product += 40
            mycanvas.drawRightString(x_axis_product + 51, y_axis_product - 45, str(total_cost))
            y_axis_product -= 26

            # _______________After /24____________#

            if index % 24 == 0:

                mycanvas.line(line_x_axis-25, y_axis_product - 35, x_axis, y_axis_product - 35)
                mycanvas.showPage()

                # ________Head_lines________#

                light_color = 0x9b9999
                dark_color = 0x000000
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.setFillColor(HexColor(dark_color))

                #     mycanvas.setStrokeColor(colors.lightgrey)
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.setFont('Courier', 13)
                mycanvas.drawCentredString(350, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
                mycanvas.setFont('Courier', 13)
                mycanvas.drawCentredString(350, 785, 'Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Courier', 13)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawCentredString(350, 755, 'Daily Counter Report : Agents Sales')
                mycanvas.line(212, 752, 490, 752)

                mycanvas.setFont('Courier', 13)
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(60, 730, 'Zone : ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(120, 730, str(data_dict["agent_dict"]["zone_details"]["zone_name"]))

                #     mycanvas.setFillColor(HexColor(light_color))
                #     mycanvas.drawString(60, 700, 'Employees : ')
                #     mycanvas.setFillColor(HexColor(dark_color))

                #     name_emp = ""
                #     for name in list(set(data_dict["agent_dict"]["zone_details"]["employee_name"])):
                #         name_emp += name+","
                #     mycanvas.drawString(120, 700, str(name_emp))

                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(60, 715, 'Date : ')
                mycanvas.drawString(60, 700, 'Business : ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(150, 700, str(session_name))
                mycanvas.drawString(120, 715, str(data_dict["agent_dict"]["zone_details"]["date"]))

                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(360, 730, 'Report Generated @: ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(510, 730, str(datetime.datetime.strftime(datetime.datetime.now(timezone('Asia/Kolkata')), '%d-%m-%Y, %H:%M %p')))


                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(350, 715, 'Report Generated by: ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(510, 715, str(user_name))
                # _____________table header_____________#

                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Courier', 13)
                mycanvas.drawString(28, 675, 'S.No')
                mycanvas.drawString(63, 675, 'booth')
                mycanvas.drawString(65, 663, 'code')
                mycanvas.drawString(109, 675, 'agent')
                mycanvas.drawString(110, 663, 'name')
                x_axis = 175
                y_axis = 675
                line_x_axis = 50
                
                    # _____________ Product heading _____________#

                products = list(Product.objects.filter(is_active=True).order_by('display_ordinal'))

                for product in products:
                    product_name = list(product.short_name.split(" "))
                    mycanvas.drawString(x_axis-20, y_axis, str(product_name[0][:3]))
                    try:
                        mycanvas.drawString(x_axis-19, y_axis - 12, str(product_name[1]))
                    except:
                        pass
                    if product.short_name == products[-1].short_name:
                        x_axis += 40
                        mycanvas.drawString(x_axis-25, y_axis, 'Total')
                    # table top line
                    mycanvas.setLineWidth(0)
                    mycanvas.line(line_x_axis-25, y_axis + 15, x_axis + 40, y_axis + 15)
                    # table bottom line
                    mycanvas.line(line_x_axis-25, y_axis - 15, x_axis + 40, y_axis - 15)
                    x_axis += 41
                    # _____________ Agent_name,Business_code,Product ___________#

                y_axix_agent_booth = 630
                x_axis_agent_booth = 90
                y_axis_product = 675

                # _________Grand_total__________#

        x_axis_product = 175
        mycanvas.line(line_x_axis-25, y_axis_product - 35, x_axis, y_axis_product - 35)
        for i in range(len(products) + 1):
            if i != 0:
                mycanvas.line(x_axis_product-20, y_axis_product, x_axis_product-20, y_axis_product - 55)
            x_axis_product += 40
            
        mycanvas.line(line_x_axis-25, y_axis_product - 55, x_axis, y_axis_product - 55)
        mycanvas.line(x_axis, y_axis_product - 35, x_axis, y_axis_product - 55)
        mycanvas.line(line_x_axis-25, y_axis_product - 35, line_x_axis-25, y_axis_product - 55)
        mycanvas.drawString(line_x_axis -20, y_axis_product - 48, "Total Packets")
        mycanvas.drawRightString(x_axis_product + 10, y_axis_product - 68, str(data_dict["agent_dict"]["grand_total"]))

        mycanvas.line(x_axis, y_axis_product - 55, x_axis, y_axis_product - 75)
        mycanvas.line(line_x_axis-25, y_axis_product - 55, line_x_axis-25, y_axis_product - 75)
    #     mycanvas.line(x_axis - 60, y_axis_product - 55, x_axis - 60, y_axis_product - 75)
        mycanvas.line(line_x_axis-25, y_axis_product - 75, x_axis, y_axis_product - 75)
        mycanvas.drawString(x_axis_product - 205, y_axis_product - 68, 'Grand Total')

        x_axis_product += 35
        x_adjust = 0
        for product in products:
            mycanvas.setFont('Courier', 12)
            try:
                
                mycanvas.drawRightString(line_x_axis+145+x_adjust , y_axis_product - 48,
                                        str(int(data_dict["agent_dict"]["product_count"][product.id])))
                line_x_axis += 39
                x_adjust += 1
            except:
                pass
    mycanvas.setFont('Courier', 13)
    mycanvas.showPage()

    # ________Head_lines________#

    light_color = 0x9b9999
    dark_color = 0x000000

    #     mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Courier', 13)
    mycanvas.drawCentredString(350, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
    mycanvas.setFont('Courier', 13)
    mycanvas.drawCentredString(350, 785, 'Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Courier', 13)

    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(350, 755, 'Daily Counter Report : Family Card Sales')
    mycanvas.line(190, 752, 510, 752)

    mycanvas.setFont('Courier', 13)
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(60, 730, 'Zone : ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(120, 730, str(data_dict["icus_dict"]["counter_details"]["counter_name"]))

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(60, 715, 'Date : ')
    mycanvas.drawString(60, 700, 'Business : ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(150, 700, str(session_name))
    mycanvas.drawString(120, 715, str(data_dict["icus_dict"]["counter_details"]["date"]))

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(360, 730, 'Report Generated @: ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(510, 730, str(datetime.datetime.strftime(datetime.datetime.now(timezone('Asia/Kolkata')), '%d-%m-%Y, %H:%M %p')))


    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(350, 715, 'Report Generated by: ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(510, 715, str(user_name))
    if data_dict["icus_dict"]["agent_details"] == []:
        mycanvas.drawCentredString(350, 680, '{------There is no report to show------}')

    else:

        # _____________table header_____________#
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Courier', 13)
        mycanvas.drawString(25, 675, 'S.No')
        mycanvas.drawString(65, 675, 'Customer')
        #     mycanvas.drawString(100,665,'code')
        mycanvas.drawString(105 + 30, 675, 'Booth Code')
        #     mycanvas.drawString(175+40,665,'Name')
        #     mycanvas.drawString(145,665,'name')
        #     mycanvas.drawString(250,675,'OrderFor')
        #     mycanvas.drawString(258,665,'Date')
        mycanvas.drawString(260 - 30, 675, 'Month')
        x_axis = 370
        y_axis = 675
        line_x_axis = 50

        # _____________ Product heading _____________#

        icus_products = list(Product.objects.filter(is_active=True, group_id=1).order_by('display_ordinal'))

        for product in icus_products:
            product_name = list(product.short_name.split(" "))
            mycanvas.drawString(x_axis - 70, y_axis, str(product_name[0][:3]))
            try:
                mycanvas.drawString(x_axis - 70, y_axis - 10, str(product_name[1]))
            except:
                pass
            if product.short_name == icus_products[-1].short_name:
                x_axis += 45
                mycanvas.drawString(x_axis - 70, y_axis, 'Total / Day')
                mycanvas.drawString(x_axis - 35, y_axis - 10, ' ')
                x_axis += 50
                mycanvas.drawString(x_axis-25, y_axis, 'Total / Month')
    #             mycanvas.drawString(x_axis + 25 - 10, y_axis - 10, 'Month')
            # table top line
            mycanvas.setLineWidth(0)
            mycanvas.line(line_x_axis-30, y_axis + 15, x_axis + 80, y_axis + 15)
            # table bottom line
            mycanvas.line(line_x_axis -30, y_axis - 15, x_axis + 80, y_axis - 15)
            x_axis += 50

            # _____________ Agent_name,Business_code,Product ___________#

        y_axix_agent_booth = 630
        x_axis_agent_booth = 90
        y_axis_product = 675
        business_break = 0
        sale_date = ''
        index = 0
        
        for business in data_dict["icus_dict"]["agent_details"]:

            index += 1
            sale_date = business["for_date"]
            business_break = business["icustomer_id"]
            mycanvas.setFont('Courier', 13)
            mycanvas.drawRightString(line_x_axis - 50+ 20 + 30, y_axix_agent_booth, str(index))
            mycanvas.drawString(x_axis_agent_booth -20, y_axix_agent_booth, str(business["customer_name"]))
            mycanvas.drawString(x_axis_agent_booth + 30 + 30, y_axix_agent_booth, str(business["business_code"]))
            #             mycanvas.drawString(x_axis_agent_booth+160,y_axix_agent_booth,str(business["for_date"]))
            mycanvas.drawString(x_axis_agent_booth + 226 - 85, y_axix_agent_booth,
                                str(business["for_month"][:3]) + " " + str(str(business["year"])[2:]))
            sale_group_id = business["icustomer_sale_group_id"]

            # _________lines_between_agent_name___________#

            mycanvas.line(x_axis_agent_booth - 30, y_axix_agent_booth + 60, x_axis_agent_booth - 30,
                        y_axix_agent_booth - 15)
    #         mycanvas.line(x_axis_agent_booth + 75 + 30, y_axix_agent_booth + 60, x_axis_agent_booth + 75 + 30,
    #                       y_axix_agent_booth - 15)
            mycanvas.line(x_axis_agent_booth + 100 + 30, y_axix_agent_booth + 60, x_axis_agent_booth + 100 + 30,
                        y_axix_agent_booth - 15)
            mycanvas.line(x_axis_agent_booth + 270 - 70, y_axix_agent_booth + 60, x_axis_agent_booth + 270 - 70,
                        y_axix_agent_booth - 15)
            #             mycanvas.line(x_axis_agent_booth+215,y_axix_agent_booth+60,x_axis_agent_booth+215,y_axix_agent_booth-15)

            # _________left_and_right_border___________#

            mycanvas.line(line_x_axis -30, y_axix_agent_booth + 60, line_x_axis - 30, y_axix_agent_booth - 15)
            mycanvas.line(line_x_axis +80, y_axix_agent_booth + 60, line_x_axis + 80, y_axix_agent_booth - 15)
            mycanvas.line(x_axis - 80, y_axix_agent_booth + 60, x_axis - 80, y_axix_agent_booth - 15)
            mycanvas.line(x_axis + 30, y_axix_agent_booth + 60, x_axis + 30, y_axix_agent_booth - 15)

            y_axix_agent_booth -= 26
            products_list = []

            for product_id in data_dict["icus_dict"]["icustomer_sale_details"][business["for_date"]][
                business["icustomer_id"]]:
                if product_id == "product_total_cost":
                    continue
                products_list.append(product_id)
            x_axis_product = 370
            #             total_cost = 0
            for product in icus_products:
                if not (product.id in products_list):
                    mycanvas.drawRightString(x_axis_product + 20 - 70, y_axis_product - 45, " ")
    #                 x_axis_product += 35
                if (product.id in products_list):
                    mycanvas.drawRightString(x_axis_product + 20 - 70, y_axis_product - 45, str(int(
                        data_dict["icus_dict"]["icustomer_sale_details"][business["for_date"]][
                            business["icustomer_id"]][product.id]["icustomer_sale_count"])))
                x_axis_product += 50
                mycanvas.setLineWidth(0)
                mycanvas.line(x_axis_product - 80, y_axis_product + 15, x_axis_product - 80,
                            y_axis_product - 60)
            total_cost = \
            data_dict["icus_dict"]["icustomer_sale_details"][business["for_date"]][business["icustomer_id"]][
                "product_total_cost"]
            total_cost_month = \
            data_dict["icus_dict"]["icustomer_sale_details"][business["for_date"]][business["icustomer_id"]][
                "product_cost_month"]
            mycanvas.drawRightString(x_axis_product + 35 - 30, y_axis_product - 45, str(total_cost))
            mycanvas.drawRightString(x_axis_product + 120, y_axis_product - 45, str(total_cost_month))
            y_axis_product -= 26

            # _______________After /24____________#

            if index % 24 == 0:

                mycanvas.line(line_x_axis - 30, y_axis_product - 35, x_axis + 30, y_axis_product - 35)
                mycanvas.showPage()

                # ________Head_lines________#

                light_color = 0x9b9999
                dark_color = 0x000000

                #     mycanvas.setStrokeColor(colors.lightgrey)
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.setFont('Courier', 13)
                mycanvas.drawCentredString(350, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
                mycanvas.setFont('Courier', 13)
                mycanvas.drawCentredString(350, 785, 'Pachapalayam, Coimbatore - 641 010')
                mycanvas.setFont('Courier', 13)

                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawCentredString(350, 755, 'Daily Counter Report : Family Card Sales')
                mycanvas.line(190, 752, 510, 752)

                mycanvas.setFont('Courier', 13)
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(60, 730, 'Zone : ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(120, 730, str(data_dict["icus_dict"]["counter_details"]["counter_name"]))

                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(60, 715, 'Date : ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(120, 715, str(data_dict["icus_dict"]["counter_details"]["date"]))

                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(360, 730, 'Report Generated @: ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(510, 730, str(datetime.datetime.strftime(datetime.datetime.now(timezone('Asia/Kolkata')), '%d-%m-%Y, %H:%M %p')))


                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(350, 715, 'Report Generated by: ')
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.drawString(510, 715, 'Sunesh Rajan')

                # _____________table header_____________#
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Courier', 13)
                mycanvas.drawString(25, 675, 'S.No')
                mycanvas.drawString(65, 675, 'Customer')
                #     mycanvas.drawString(100,665,'code')
                mycanvas.drawString(105 + 30, 675, 'Booth Code')
                #     mycanvas.drawString(175+40,665,'Name')
                #     mycanvas.drawString(145,665,'name')
                #     mycanvas.drawString(250,675,'OrderFor')
                #     mycanvas.drawString(258,665,'Date')
                mycanvas.drawString(260 - 30, 675, 'Month')
                x_axis = 370
                y_axis = 675
                line_x_axis = 50

                # _____________ Product heading _____________#

                icus_products = list(Product.objects.filter(is_active=True, group_id=1).order_by('display_ordinal'))

                for product in icus_products:
                    product_name = list(product.short_name.split(" "))
                    mycanvas.drawString(x_axis - 70, y_axis, str(product_name[0][:3]))
                    try:
                        mycanvas.drawString(x_axis - 70, y_axis - 10, str(product_name[1]))
                    except:
                        pass
                    if product.short_name == icus_products[-1].short_name:
                        x_axis += 45
                        mycanvas.drawString(x_axis - 70, y_axis, 'Total / Day')
                        mycanvas.drawString(x_axis - 35, y_axis - 10, ' ')
                        x_axis += 50
                        mycanvas.drawString(x_axis-25, y_axis, 'Total / Month')
            #             mycanvas.drawString(x_axis + 25 - 10, y_axis - 10, 'Month')
                    # table top line
                    mycanvas.setLineWidth(0)
                    mycanvas.line(line_x_axis-30, y_axis + 15, x_axis + 80, y_axis + 15)
                    # table bottom line
                    mycanvas.line(line_x_axis -30, y_axis - 15, x_axis + 80, y_axis - 15)
                    x_axis += 50

                y_axix_agent_booth = 630
                x_axis_agent_booth = 90
                y_axis_product = 675

                # _________Grand_total__________#

        x_axis_product = 370
        mycanvas.line(line_x_axis -30, y_axis_product - 35, x_axis + 20 + 10, y_axis_product - 35)
        
        for i in range(len(icus_products) + 1):
            mycanvas.line(x_axis_product - 10 - 70, y_axis_product, x_axis_product - 10 - 70, y_axis_product - 55)
            x_axis_product += 50
        mycanvas.setFont('Courier', 13)
        mycanvas.line(line_x_axis - 30, y_axis_product - 55, x_axis + 20 + 10, y_axis_product - 55)
        mycanvas.line(x_axis + 20 - 30, y_axis_product - 55, x_axis + 20 - 30, y_axis_product - 55)
        mycanvas.line(line_x_axis - 30, y_axis_product - 35, line_x_axis - 30, y_axis_product - 55)
        mycanvas.drawString(line_x_axis + 120, y_axis_product - 48, "Total Packets")

        mycanvas.line(line_x_axis - 30, y_axis_product - 75, x_axis + 20+10, y_axis_product - 75)
        mycanvas.line(x_axis + 20 + 10, y_axis_product - 35, x_axis + 20 +10, y_axis_product - 75)
        mycanvas.line(x_axis + 20 - 100, y_axis_product - 35, x_axis + 20 - 100, y_axis_product - 55)
        mycanvas.line(line_x_axis - 30, y_axis_product - 55, line_x_axis - 30, y_axis_product - 75)
        mycanvas.drawRightString(x_axis_product - 60, y_axis_product - 68, 'Grand Total')
        mycanvas.drawRightString(x_axis_product + 65 - 30, y_axis_product - 68,
                                str(data_dict["icus_dict"]["grand_total_month"]))

        x_axis_product += 35
        for priduct_total in data_dict["icus_dict"]["product_total_count"]:
            mycanvas.drawRightString(line_x_axis + 340 - 60, y_axis_product - 48,
                                    str(int(data_dict["icus_dict"]["product_total_count"][priduct_total])))
            line_x_axis += 50
    mycanvas.setFont('Courier', 13)
    mycanvas.drawCentredString(350, 70, "Certified that the above particulars are checked and verfied found correct.")
    mycanvas.drawString(490, 25, "Zonal incharge")
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



def serve_business_type_wise_summay(date, session_id, user_name):
    
    session_id = session_id
   
    if session_id == 'all':
        session_id = list(Session.objects.filter().values_list('id', flat=True))
    else:
        session_id = int(session_id)
        session_id = list(Session.objects.filter(id=session_id).values_list('id', flat=True))
        
    final_dict = {
        'date': date,
        'session': session_id,
        'final_results': {'cash': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0, '500': 0, 'total': 0},
                                   'CURD': {'500': 0, '150': 0, '100': 0,'5000': 0,'total': 0},
                                   'BtrMlk':{'200': 0,'total':0},
                                   'Lassi': {'200': 0,'total':0}},
                          
                          'card': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0, '500': 0, 'total': 0},
                                   'CURD': {'500': 0, '150': 0, '100': 0,'5000': 0, 'total': 0},
                                   'BtrMlk': {'200': 0,'total':0},
                                   'Lassi': {'200': 0,'total':0}},
                          
                          'total_sale': {'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                                                '250': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                 '500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                 '500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                                                  '150': {'cash': 0, 'card': 0, 'total': 0},
                                                  '500': {'cash': 0, 'card': 0, 'total': 0},
                                                  '5000': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BtrMlk': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'Lassi': {'200': {'cash': 0, 'card': 0, 'total': 0}}
                                        }
    }}
    for business_type in BusinessType.objects.filter().order_by('display_ordinal'):
        final_dict[business_type.id] = {'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                                       '250': {'cash': 0, 'card': 0, 'total': 0}},
                                
                                'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},
                                
                                'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                        '500': {'cash': 0, 'card': 0, 'total': 0}},

                                'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                        '500': {'cash': 0, 'card': 0, 'total': 0}},        
                                
                                'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                                         '150': {'cash': 0, 'card': 0, 'total': 0},
                                         '500': {'cash': 0, 'card': 0, 'total': 0},
                                         '5000': {'cash': 0, 'card': 0, 'total': 0}},
                                
                                'BtrMlk': {'200':{'cash': 0, 'card': 0, 'total': 0}},
                                
                                'Lassi': {'200':{'cash': 0, 'card': 0, 'total': 0}}
                               }
        final_dict[business_type.id]['products_total'] = 0
        final_dict[business_type.id]['business_type_name'] = business_type.name
    dsbs_obj = DailySessionllyBusinessTypellySale.objects.filter(delivery_date=date, session_id__in=session_id)
    card_sale_obj = dsbs_obj.filter(sold_to='ICustomer')
    cash_sale_obj = dsbs_obj.filter(sold_to='Agent')
    # SM
    sm_500_cash_total = cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
    sm_500_card_total = card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
    final_dict['final_results']['cash']['SM']['500'] = round(sm_500_cash_total, 3)
    final_dict['final_results']['card']['SM']['500'] = round(sm_500_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['500']['card'] = round(sm_500_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['500']['cash'] = round(sm_500_cash_total, 3)

    sm_250_cash_total = cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
    sm_250_card_total = card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
    final_dict['final_results']['cash']['SM']['250'] = round(sm_250_cash_total, 3)
    final_dict['final_results']['card']['SM']['250'] = round(sm_250_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['250']['card'] = round(sm_250_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['250']['cash'] = round(sm_250_cash_total, 3)

    # Total
    final_dict['final_results']['cash']['SM']['total'] = final_dict['final_results']['cash']['SM']['500'] + \
                                                         final_dict['final_results']['cash']['SM']['250']
    final_dict['final_results']['card']['SM']['total'] = final_dict['final_results']['card']['SM']['500'] + \
                                                         final_dict['final_results']['card']['SM']['250']
    final_dict['final_results']['total_sale']['SM']['500']['total'] = \
    final_dict['final_results']['total_sale']['SM']['500']['card'] + \
    final_dict['final_results']['total_sale']['SM']['500']['cash']
    final_dict['final_results']['total_sale']['SM']['250']['total'] = \
    final_dict['final_results']['total_sale']['SM']['250']['card'] + \
    final_dict['final_results']['total_sale']['SM']['250']['cash']

    # TM
    tm_500_cash_total = cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    tm_500_card_total = card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    final_dict['final_results']['cash']['TM']['500'] = round(tm_500_cash_total, 3)
    final_dict['final_results']['card']['TM']['500'] = round(tm_500_card_total, 3)
    final_dict['final_results']['total_sale']['TM']['500']['card'] = round(tm_500_card_total, 3)
    final_dict['final_results']['total_sale']['TM']['500']['cash'] = round(tm_500_cash_total, 3)

    final_dict['final_results']['cash']['TM']['total'] = final_dict['final_results']['cash']['TM']['500']
    final_dict['final_results']['card']['TM']['total'] = final_dict['final_results']['card']['TM']['500']
    final_dict['final_results']['total_sale']['TM']['500']['total'] = \
    final_dict['final_results']['total_sale']['TM']['500']['card'] + \
    final_dict['final_results']['total_sale']['TM']['500']['cash']

    #  FCM
    fcm_500_cash_total = cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
    fcm_500_card_total = card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
    final_dict['final_results']['cash']['FCM']['500'] = round(fcm_500_cash_total, 3)
    final_dict['final_results']['card']['FCM']['500'] = round(fcm_500_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['500']['card'] = round(fcm_500_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['500']['cash'] = round(fcm_500_cash_total, 3)
    
    fcm_1000_cash_total = cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
    fcm_1000_card_total = card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
    final_dict['final_results']['cash']['FCM']['1000'] = round(fcm_1000_cash_total, 3)
    final_dict['final_results']['card']['FCM']['1000'] = round(fcm_1000_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['1000']['card'] = round(fcm_1000_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['1000']['cash'] = round(fcm_1000_cash_total, 3)

    final_dict['final_results']['cash']['FCM']['total'] = final_dict['final_results']['cash']['FCM']['500'] + final_dict['final_results']['cash']['FCM']['1000']
    final_dict['final_results']['card']['FCM']['total'] = final_dict['final_results']['card']['FCM']['500'] + final_dict['final_results']['card']['FCM']['1000']
    
    final_dict['final_results']['total_sale']['FCM']['500']['total'] = \
    final_dict['final_results']['total_sale']['FCM']['500']['card'] + \
    final_dict['final_results']['total_sale']['FCM']['500']['cash']
    
    final_dict['final_results']['total_sale']['FCM']['1000']['total'] = \
    final_dict['final_results']['total_sale']['FCM']['1000']['card'] + \
    final_dict['final_results']['total_sale']['FCM']['1000']['cash']


    #  TMATE
    tea_500_cash_total = cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
    tea_500_card_total = card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
    final_dict['final_results']['cash']['TMATE']['500'] = round(tea_500_cash_total, 3)
    final_dict['final_results']['card']['TMATE']['500'] = round(tea_500_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['500']['card'] = round(tea_500_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['500']['cash'] = round(tea_500_cash_total, 3)
    
    tea_1000_cash_total = cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
    tea_1000_card_total = card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
    final_dict['final_results']['cash']['TMATE']['1000'] = round(tea_1000_cash_total, 3)
    final_dict['final_results']['card']['TMATE']['1000'] = round(tea_1000_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['1000']['card'] = round(tea_1000_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['1000']['cash'] = round(tea_1000_cash_total, 3)

    final_dict['final_results']['cash']['TMATE']['total'] = final_dict['final_results']['cash']['TMATE']['500'] + final_dict['final_results']['cash']['TMATE']['1000']
    final_dict['final_results']['card']['TMATE']['total'] = final_dict['final_results']['card']['TMATE']['500'] + final_dict['final_results']['card']['TMATE']['1000']
    
    final_dict['final_results']['total_sale']['TMATE']['500']['total'] = \
    final_dict['final_results']['total_sale']['TMATE']['500']['card'] + \
    final_dict['final_results']['total_sale']['TMATE']['500']['cash']
    
    final_dict['final_results']['total_sale']['TMATE']['1000']['total'] = \
    final_dict['final_results']['total_sale']['TMATE']['1000']['card'] + \
    final_dict['final_results']['total_sale']['TMATE']['1000']['cash']
    
    # Butter_milk
    buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
    buttermilk200_card_total = card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
    final_dict['final_results']['cash']['BtrMlk']['200'] = buttermilk200_cash_total
    final_dict['final_results']['card']['BtrMlk']['200'] = buttermilk200_card_total 
    final_dict['final_results']['total_sale']['BtrMlk']['200']['card'] = round(buttermilk200_card_total, 3)
    final_dict['final_results']['total_sale']['BtrMlk']['200']['cash'] = round(buttermilk200_cash_total, 3)

    final_dict['final_results']['cash']['BtrMlk']['total'] = final_dict['final_results']['cash']['BtrMlk']['200']
    final_dict['final_results']['card']['BtrMlk']['total'] = final_dict['final_results']['card']['BtrMlk']['200']
    final_dict['final_results']['total_sale']['BtrMlk']['200']['total'] = \
    final_dict['final_results']['total_sale']['BtrMlk']['200']['card'] + \
    final_dict['final_results']['total_sale']['BtrMlk']['200']['cash']
        
    #lassi
    lassi200_cash_total = cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
    lassi200_card_total = card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
    final_dict['final_results']['cash']['Lassi']['200'] = lassi200_card_total
    final_dict['final_results']['card']['Lassi']['200'] = lassi200_card_total
    final_dict['final_results']['total_sale']['Lassi']['200']['cash'] = lassi200_cash_total
    final_dict['final_results']['total_sale']['Lassi']['200']['card'] = lassi200_card_total 

    final_dict['final_results']['cash']['Lassi']['total'] = final_dict['final_results']['cash']['Lassi']['200']
    final_dict['final_results']['card']['Lassi']['total'] = final_dict['final_results']['card']['Lassi']['200']
    final_dict['final_results']['total_sale']['Lassi']['200']['total'] = \
    final_dict['final_results']['total_sale']['Lassi']['200']['card'] + \
    final_dict['final_results']['total_sale']['Lassi']['200']['cash']

    # CURD
    curd_500_cash_total = cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd_500_card_total = card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    final_dict['final_results']['cash']['CURD']['500'] = round(curd_500_cash_total, 3)
    final_dict['final_results']['card']['CURD']['500'] = round(curd_500_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['500']['card'] = round(curd_500_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['500']['cash'] = round(curd_500_cash_total, 3)

    curd_150_cash_total = cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
    curd_150_card_total = card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
    final_dict['final_results']['cash']['CURD']['150'] = round(curd_150_cash_total, 3)
    final_dict['final_results']['card']['CURD']['150'] = round(curd_150_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['150']['card'] = round(curd_150_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['150']['cash'] = round(curd_150_cash_total, 3)
    
    curd_100_cash_total = cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
    curd_100_card_total = card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
    final_dict['final_results']['cash']['CURD']['100'] = round(curd_100_cash_total, 3)
    final_dict['final_results']['card']['CURD']['100'] = round(curd_100_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['100']['card'] = round(curd_100_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['100']['cash'] = round(curd_100_cash_total, 3)

    curd_5000_cash_total = cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    curd_5000_card_total = card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    final_dict['final_results']['cash']['CURD']['5000'] = round(curd_5000_cash_total, 3)
    final_dict['final_results']['card']['CURD']['5000'] = round(curd_5000_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['5000']['card'] = round(curd_5000_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['5000']['cash'] = round(curd_5000_cash_total, 3)

    # Total
    final_dict['final_results']['cash']['CURD']['total'] = final_dict['final_results']['cash']['CURD']['500'] + \
                                                           final_dict['final_results']['cash']['CURD']['150'] + final_dict['final_results']['cash']['CURD']['100'] + \
                                                           final_dict['final_results']['cash']['CURD']['5000']
    final_dict['final_results']['card']['CURD']['total'] = final_dict['final_results']['card']['CURD']['500'] + \
                                                           final_dict['final_results']['card']['CURD']['150'] + final_dict['final_results']['card']['CURD']['100'] + \
                                                           final_dict['final_results']['card']['CURD']['5000']
    final_dict['final_results']['total_sale']['CURD']['500']['total'] = \
    final_dict['final_results']['total_sale']['CURD']['500']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['500']['cash']
    final_dict['final_results']['total_sale']['CURD']['150']['total'] = \
    final_dict['final_results']['total_sale']['CURD']['150']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['150']['cash']
    final_dict['final_results']['total_sale']['CURD']['100']['total'] = \
    final_dict['final_results']['total_sale']['CURD']['100']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['100']['cash']
    final_dict['final_results']['total_sale']['CURD']['5000']['card'] + \
    final_dict['final_results']['total_sale']['CURD']['5000']['cash']


    # business type wise report
    for business_type in BusinessType.objects.filter():
        product_total = 0
        if dsbs_obj.filter(business_type_id=business_type.id).count() > 0:
            card_sale_obj = dsbs_obj.filter(sold_to='ICustomer', business_type_id=business_type.id)
            cash_sale_obj = dsbs_obj.filter(sold_to__in=['Agent','Leakage'], business_type_id=business_type.id)

            # SM
            if cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] is None:
                sm_500_cash_total = 0
            else:
                sm_500_cash_total = cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            if card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] is None:
                sm_500_card_total = 0
            else:
                sm_500_card_total = card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            sm_500_cash_total_count = cash_sale_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            sm_500_card_total_count = card_sale_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            final_dict[business_type.id]['SM']['500']['card'] = sm_500_card_total_count
            final_dict[business_type.id]['SM']['500']['cash'] = sm_500_cash_total_count

            if cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] is None:
                sm_250_cash_total = 0
            else:
                sm_250_cash_total = cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            if card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] is None:
                sm_250_card_total = 0
            else:
                sm_250_card_total = card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            sm_250_cash_total_count = cash_sale_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            sm_250_card_total_count = card_sale_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            final_dict[business_type.id]['SM']['250']['card'] = sm_250_card_total_count
            final_dict[business_type.id]['SM']['250']['cash'] = sm_250_cash_total_count

            # Total

            total_sm_500_litre = round(Decimal(sm_500_cash_total + sm_500_card_total), 3)
            total_sm_250_litre = round(Decimal(sm_250_cash_total + sm_250_card_total), 3)
            final_dict[business_type.id]['SM']['500']['total'] = total_sm_500_litre
            final_dict[business_type.id]['SM']['250']['total'] = total_sm_250_litre
            product_total += total_sm_500_litre + total_sm_250_litre

            #       TM
            if cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] is None:
                tm_500_cash_total = 0
            else:
                tm_500_cash_total = cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            if card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] is None:
                tm_500_card_total = 0
            else:
                tm_500_card_total = card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            tm_500_cash_total_count = cash_sale_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            tm_500_card_total_count = card_sale_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            final_dict[business_type.id]['TM']['500']['card'] = tm_500_card_total_count
            final_dict[business_type.id]['TM']['500']['cash'] = tm_500_cash_total_count

            # Total
            total_tm_500_litre = round(Decimal(tm_500_cash_total + tm_500_card_total), 3)
            final_dict[business_type.id]['TM']['500']['total'] = total_tm_500_litre
            product_total += total_tm_500_litre

            #       FCM
            if cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] is None:
                fcm_500_cash_total = 0
            else:
                fcm_500_cash_total = cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            if card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] is None:
                fcm_500_card_total = 0
            else:
                fcm_500_card_total = card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            fcm_500_cash_total_count = cash_sale_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            fcm_500_card_total_count = card_sale_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            final_dict[business_type.id]['FCM']['500']['card'] = fcm_500_card_total_count
            final_dict[business_type.id]['FCM']['500']['cash'] = fcm_500_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] is None:
                fcm_1000_cash_total = 0
            else:
                fcm_1000_cash_total = cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            if card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] is None:
                fcm_1000_card_total = 0
            else:
                fcm_1000_card_total = card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            fcm_1000_cash_total_count = cash_sale_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            fcm_1000_card_total_count = card_sale_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            final_dict[business_type.id]['FCM']['1000']['card'] = fcm_1000_card_total_count
            final_dict[business_type.id]['FCM']['1000']['cash'] = fcm_1000_cash_total_count

            # Total
            total_fcm_500_litre = round(Decimal(fcm_500_cash_total + fcm_500_card_total), 3)
            total_fcm_1000_litre = round(Decimal(fcm_1000_cash_total + fcm_1000_card_total), 3)
            final_dict[business_type.id]['FCM']['500']['total'] = total_fcm_500_litre
            final_dict[business_type.id]['FCM']['1000']['total'] = total_fcm_1000_litre
            product_total += total_fcm_500_litre + total_fcm_1000_litre

             #       TMATE
            if cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] is None:
                tea_500_cash_total = 0
            else:
                tea_500_cash_total = cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            if card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] is None:
                tea_500_card_total = 0
            else:
                tea_500_card_total = card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            tea_500_cash_total_count = cash_sale_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            tea_500_card_total_count = card_sale_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            final_dict[business_type.id]['TMATE']['500']['card'] = tea_500_card_total_count
            final_dict[business_type.id]['TMATE']['500']['cash'] = tea_500_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum'] is None:
                tea_1000_cash_total = 0
            else:
                tea_1000_cash_total = cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            if card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum'] is None:
                tea_1000_card_total = 0
            else:
                tea_1000_card_total = card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            tea_1000_cash_total_count = cash_sale_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            tea_1000_card_total_count = card_sale_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            final_dict[business_type.id]['TMATE']['1000']['card'] = tea_1000_card_total_count
            final_dict[business_type.id]['TMATE']['1000']['cash'] = tea_1000_cash_total_count

            # Total
            total_tea_500_litre = round(Decimal(tea_500_cash_total + tea_500_card_total), 3)
            total_tea_1000_litre = round(Decimal(tea_1000_cash_total + tea_1000_card_total), 3)
            final_dict[business_type.id]['TMATE']['500']['total'] = total_tea_500_litre
            final_dict[business_type.id]['TMATE']['1000']['total'] = total_tea_1000_litre
            product_total += total_tea_500_litre + total_tea_1000_litre
        
            #Lassi
            if cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum'] is None:
                lassi200_cash_total = 0
            else:
                lassi200_cash_total = cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            if card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum'] is None:
                lassi200_card_total = 0
            else:
                lassi200_card_total = card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            lassi200_cash_total_count = cash_sale_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            lassi200_card_total_count = card_sale_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            final_dict[business_type.id]['Lassi']['200']['card'] = lassi200_card_total_count
            final_dict[business_type.id]['Lassi']['200']['cash'] = lassi200_cash_total_count

            # Total
            total_lassi200_litre = round(Decimal(lassi200_card_total + lassi200_cash_total), 3)
            final_dict[business_type.id]['Lassi']['200']['total'] = total_lassi200_litre
            product_total += total_lassi200_litre
        
            
            #Butter_milk
            if cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum'] is None:
                buttermilk200_cash_total = 0
            else:
                buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            if card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum'] is None:
                buttermilk200_total = 0
            else:
                buttermilk200_card_total = card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
            buttermilk200_cash_total_count = cash_sale_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            buttermilk200_card_total_count = card_sale_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            final_dict[business_type.id]['BtrMlk']['200']['card'] = buttermilk200_card_total_count
            final_dict[business_type.id]['BtrMlk']['200']['cash'] = buttermilk200_cash_total_count

            # Total
            total_buttermilk200_litre = round(Decimal(buttermilk200_card_total + buttermilk200_cash_total), 3)
            final_dict[business_type.id]['BtrMlk']['200']['total'] = total_buttermilk200_litre
            product_total += total_buttermilk200_litre
        
            
            #       CURD
            if cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] is None:
                curd_500_cash_total = 0
            else:
                curd_500_cash_total = cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] is None:
                curd_500_card_total = 0
            else:
                curd_500_card_total = card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            curd_500_cash_total_count = cash_sale_obj.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
            curd_500_card_total_count = card_sale_obj.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
            final_dict[business_type.id]['CURD']['500']['card'] = curd_500_card_total_count
            final_dict[business_type.id]['CURD']['500']['cash'] = curd_500_cash_total_count

            if cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] is None:
                curd_150_cash_total = 0
            else:
                curd_150_cash_total = cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] is None:
                curd_150_card_total = 0
            else:
                curd_150_card_total = card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            curd_150_cash_total_count = cash_sale_obj.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
            curd_150_card_total_count = card_sale_obj.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
            final_dict[business_type.id]['CURD']['150']['card'] = curd_150_card_total_count
            final_dict[business_type.id]['CURD']['150']['cash'] = curd_150_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] is None:
                curd_100_cash_total = 0
            else:
                curd_100_cash_total = cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            if card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] is None:
                curd_100_card_total = 0
            else:
                curd_100_card_total = card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            curd_100_cash_total_count = cash_sale_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            curd_100_card_total_count = card_sale_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            final_dict[business_type.id]['CURD']['100']['card'] = curd_100_card_total_count
            final_dict[business_type.id]['CURD']['100']['cash'] = curd_100_cash_total_count
            if cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum'] is None:
                curd_5000_cash_total = 0
            else:
                curd_5000_cash_total = cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum'] is None:
                curd_5000_card_total = 0
            else:
                curd_5000_card_total = card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            curd_5000_cash_total_count = cash_sale_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            curd_5000_card_total_count = card_sale_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            final_dict[business_type.id]['CURD']['5000']['card'] = curd_5000_card_total_count
            final_dict[business_type.id]['CURD']['5000']['cash'] = curd_5000_cash_total_count


            # Total
            total_curd_500_litre = round(Decimal(curd_500_cash_total + curd_500_card_total), 3)
            total_curd_150_litre = round(Decimal(curd_150_cash_total + curd_150_card_total), 3)
            total_curd_100_litre = round(Decimal(curd_100_cash_total + curd_100_card_total), 3)
            total_curd_5000_litre = round(Decimal(curd_5000_cash_total + curd_5000_card_total), 3)
            final_dict[business_type.id]['CURD']['500']['total'] = total_curd_500_litre
            final_dict[business_type.id]['CURD']['150']['total'] = total_curd_150_litre
            final_dict[business_type.id]['CURD']['100']['total'] = total_curd_100_litre
            final_dict[business_type.id]['CURD']['5000']['total'] = total_curd_5000_litre
            product_total += total_curd_500_litre + total_curd_150_litre + total_curd_100_litre + total_curd_5000_litre

            final_dict[business_type.id]['products_total'] = round(Decimal(product_total), 3)
    data = generate_pdf_for_business_type_wise_summary(final_dict, user_name, date, session_id)
    return data


def generate_pdf_for_business_type_wise_summary(data_dict, user_name, date, session_id):
    
    session_name = ""
   
    if len(session_id) == 2:
        session_name = "Both Shift"
    else:
        for ses in reversed(session_id):
            session = Session.objects.get(id=ses).name
            session_name += session + 'Shift, '
   
    file_name = str(data_dict['date']) + '_' + str(session_name) + '_overall_businesstypewise_details' + '.pdf'
    file_path = os.path.join('static/media/route_wise_report/', file_name)
#     file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))

    # _Head_lines_#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
    y_a4= 20

    #     mycanvas.setStrokeColor(colors.lightgrey)
#     mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
    mycanvas.drawCentredString(300, 795, 'Daily Business Type Report : Total Sales, ('+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')+", "+str(session_name)+")"))
#     mycanvas.line(246-50, 792, 452-50, 792)

#     date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
#     mycanvas.setFont('Helvetica', 12)
#     mycanvas.drawString(20, 765, "Shift : " +str(session_name)+"  |  "+'Date : ' + str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))

    x_a4 = 50
    y_a4 = 70
    # Table Header
    mycanvas.setLineWidth(0)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
    mycanvas.drawString(35-20, 655+y_a4, 'No')
    mycanvas.drawString(60-20, 655+y_a4, 'Zone')
    mycanvas.drawString(95-20, 665+y_a4, 'Items')

    mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
    mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

    mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
    mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')
   
    mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

    mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
    mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(470-20-x_a4, 650+y_a4, '150ml')
    mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
    mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

    mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
    mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

    mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
    mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
    mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
    mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

    products_list = ["TM", "SM", "FCM","TMATE", "CURD", "BtrMlk", "Lassi"]
#     quantity_list = ["1000", "500", "250", "200", "150","100"]
    quantity_list = ["1000","500", "250", "200", "150","5000"]
    route_list = list(Route.objects.all().values_list("name",flat=True))

    index = 1
    y = 620+y_a4
    y_line = 690+y_a4
    x_line = 30
    grand_total = 0
    mycanvas.setFont('Helvetica', 8)
   
    current_route = ""

    for data in data_dict:
        if data == "date" or data == "session" or data == "final_results" or data_dict[data]["products_total"] == 0:
            continue
        mycanvas.drawString(13, y, str(index))
        #         mycanvas.drawString(75, y,str(data))

        # -----------------------------------------------------------------------------------------------------------------------------------------#

        # lines#
        mycanvas.line(x_line-20, y_line, x_line-20, y - 70)
        mycanvas.line(x_line, y_line, x_line, y - 70)
        mycanvas.line(x_line + 40, y_line, x_line + 40, y - 70)
        mycanvas.line(x_line + 80, y_line, x_line + 80, y - 70)
       
        mycanvas.line(x_line + 110+15, y_line - 26, x_line + 110+15, y - 70)
        mycanvas.line(x_line + 100+75, y_line - 26, x_line + 100+75, y - 70)
        mycanvas.line(x_line + 155+70, y_line - 26, x_line + 155+70, y - 70)
       
        mycanvas.line(x_line + 210+60, y_line - 26, x_line + 210+60, y - 70)
        mycanvas.line(x_line + 265+50, y_line - 26, x_line + 265+50, y - 70)
        mycanvas.line(x_line + 320+40, y_line - 26, x_line + 320+40, y - 70)
        mycanvas.line(x_line + 375+30, y_line - 26, x_line + 375+30, y - 70)
        mycanvas.line(x_line + 430+20, y_line, x_line + 430+20, y - 70)
        mycanvas.line(x_line + 430+70, y_line, x_line + 430+70, y - 70)
        mycanvas.line(x_line + 555, y_line, x_line + 555, y - 70)

        y_line -= 50
        current_route = data_dict[data]["business_type_name"]
        route_name = ''
        for letter in data_dict[data]["business_type_name"]:
            if letter == ' ':
                continue
            else:
                route_name += letter
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(30, y, str(route_name[:7]))
#         mycanvas.setFont('Helvetica', 12)
        for products in products_list:
            mycanvas.drawString(75, y, str(products))
            total_litter_line = 0
            x_1000 = 115+10
            x_500 = 105+60
            x_250 = 195+60
            x_200 = 275+60
            x_150 = 315+60
            x_5000 = 430+20
            x_total_litter_line = 520
            if not products in data_dict[data]:
                pass
            #                     if products == "TM" or products == "SM" or products == "FCM":
            #                         y -= 15
            #                         continue
            #                     continue
            if products in data_dict[data]:
                for quantity in quantity_list:
                    try:
                       
                        if quantity == "1000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_1000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_1000 += 50
                       
                        if quantity == "500":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_500 + 35, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_500 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_500 + 30, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_500 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_500 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))

                        if quantity == "250":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_250 + 40 - x_adjust, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_250 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_250 + 40, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_250 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_250 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))
                       
                        if quantity == "200":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_200 + 50, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_200 += 50

                        if quantity == "150":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_150 + 55, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_150 += 50
                       
                       
                        # if quantity == "100":
                        #     for types in data_dict[data][products][quantity]:
                        #         if types == "total":
                        #             total_litter_line += data_dict[data][products][quantity][types]
                        #         else:
                        #             if data_dict[data][products][quantity][types] != 0 and \
                        #                     data_dict[data][products][quantity][types] != None:
                        #                 mycanvas.drawRightString(x_100 + 25, y,
                        #                                          str(data_dict[data][products][quantity][types]))
                        #             x_100 += 30

                       
                        if quantity == "5000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_5000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_5000 += 30

                    except:
                        pass
            mycanvas.drawRightString(x_total_litter_line + 5, y, str(total_litter_line))
            y -= 12
        grand_total += data_dict[data]["products_total"]
        mycanvas.drawRightString(x_total_litter_line + 60, y + 10, str(data_dict[data]["products_total"]))
        y -= 10
        mycanvas.line(10, y + 13, 585, y + 13)
        # -----------------------------------------------12------------------------------------------------------#
        if index % 8 == 0:
            mycanvas.showPage()

            #     mycanvas.setStrokeColor(colors.lightgrey)
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawCentredString(300, 795, 'Daily Business Type Report : Total Sales')
            mycanvas.line(246-50, 792, 452-50, 792)

            date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(20, 765, "Shift : " +str(session_name)+"  |  "+'Date : ' + str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))

            x_a4 = 50
            y_a4 = 50
            # Table Header
            mycanvas.setLineWidth(0)
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica', 8)
            mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
            mycanvas.drawString(35-20, 655+y_a4, 'No')
            mycanvas.drawString(60-20, 655+y_a4, 'Zone')
            mycanvas.drawString(95-20, 665+y_a4, 'Items')

            mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
            mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

            mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
            mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
            mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(470-20-x_a4, 650+y_a4, '150ml')
            mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
            mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

            mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
            mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

            mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
            mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
            mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
            mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

            products_list = ["TM", "SM", "FCM","TMATE", "CURD", "BtrMlk", "Lassi"]
            quantity_list = ["1000","500", "250", "200", "150","5000"]
            route_list = list(Route.objects.all().values_list("name",flat=True))

            y = 620+y_a4
            y_line = 690+y_a4
            x_line = 30
            mycanvas.setFont('Helvetica', 8)

        index += 1

    mycanvas.line(10, y + 13, 10, y - 13)
    mycanvas.line(585, y + 13, 585, y - 13)
    mycanvas.line(585, y + 13, 585, y - 13)
    mycanvas.line(10, y + 13, 585, y + 13)
    mycanvas.line(10, y - 13, 585, y - 13)
    mycanvas.drawRightString(x_total_litter_line + 60, y - 5, str(grand_total))
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(x_total_litter_line - 80, y - 5, 'Grand Total')

    # --------------------------------------------------------Final Report----------------------------------------------------#

    mycanvas.showPage()
    x_a4 = 90
    y_a4 = 90
   
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
    mycanvas.drawCentredString(300, 795, 'Daily Business Type Report : Total Sales, ('+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')+", "+str(session_name)+")"))
#     mycanvas.line(200, 752, 400, 752)

   
#     mycanvas.drawString(60 + 20, 715, str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
   
#     mycanvas.setFillColor(HexColor(light_color))

#     mycanvas.drawString(20, 715, "Shift : " +str(session_name)+"  |  "+'Date : ' + str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
   

    mycanvas.setFont('Helvetica', 10)
    #     mycanvas.drawString(70,655,'zone')
    mycanvas.drawString(110-x_a4, 600+y_a4, 'Items')

    mycanvas.drawString(192-x_a4, 590+y_a4, '1000ml')
    mycanvas.drawString(192+80-x_a4, 590+y_a4, '500ml')
    mycanvas.drawString(272+80-x_a4, 590+y_a4, '250ml')
    mycanvas.drawString(322+80-x_a4, 590+y_a4, '200ml')
    mycanvas.drawString(402+80-x_a4, 590+y_a4, '150ml')
    mycanvas.drawString(472+80-x_a4, 590+y_a4, '5000ml')
    mycanvas.drawString(545+80-x_a4, 600+y_a4, ' TOTAL')
    mycanvas.drawString(545+80-x_a4, 590+y_a4, 'LITTERS')
    #     mycanvas.drawString(602,620,'  NET')
    #     mycanvas.drawString(602,610,'LITTERS')

    # ------------------------------------------lines--------------------------------------------------#
    mycanvas.setLineWidth(0)
    mycanvas.line(90-x_a4+10, 615+y_a4, 615+80-x_a4-20, 615+y_a4)
    mycanvas.line(90-x_a4+10, 580+y_a4, 615+80-x_a4-20, 580+y_a4)

    #     mycanvas.drawString()

    y = 560+y_a4
    y_line = 615+y_a4
    x_line = 90-x_a4
    grand_total = 0

    for data in data_dict["final_results"]:
        mycanvas.line(x_line+10, y_line, x_line+10, y_line - 145)
        mycanvas.line(x_line + 70+10, y_line, x_line + 70+10, y_line - 170)
        mycanvas.line(x_line + 145+10, y_line, x_line + 145+10, y_line - 170)
        mycanvas.line(x_line + 145+80+10, y_line, x_line + 145+80+10, y_line - 170)

        mycanvas.line(x_line + 220+80, y_line, x_line + 220+80, y_line - 170)
        mycanvas.line(x_line + 295+80-10, y_line, x_line + 295+80-10, y_line - 170)
        mycanvas.line(x_line + 370+80-10, y_line, x_line + 370+80-10, y_line - 170)

        mycanvas.line(x_line + 445+80-20, y_line, x_line + 445+80-20, y_line - 170)
        mycanvas.line(x_line + 525+80-20, y_line, x_line + 525+80-20, y_line - 145)
        #         mycanvas.line(x_line+605,y_line,x_line+605,y_line-115)

        if data == "cash":
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 645+y_a4, 'Daily Business Type Report : Total-Cash Sales')
            mycanvas.line(200, 640+y_a4, 400, 640+y_a4)

            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(350, 595, 'Daily Business Type Report : Total-Cash Sales')
            else:
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "150":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]
                                       
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 -10, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                           
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "card":
            y_a4 = 70
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 420+y_a4, 'Daily Business Type Report : Total-Card Sales')
            mycanvas.line(200, 415+y_a4, 400, 415+y_a4)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 350, '{----------There is no report to show----------}')

            else:
               
                mycanvas.setFont('Helvetica', 10)  

                mycanvas.drawString(110-x_a4, 375+y_a4, 'Items')

                mycanvas.drawString(192-x_a4, 365+y_a4, '1000ml')
                mycanvas.drawString(192+80-x_a4, 365+y_a4, '500ml')
                mycanvas.drawString(272+80-x_a4, 365+y_a4, '250ml')
                mycanvas.drawString(322+80-x_a4, 365+y_a4, '200ml')
                mycanvas.drawString(402+80-x_a4, 365+y_a4, '150ml')
                mycanvas.drawString(472+80-x_a4, 365+y_a4, '5000ml')
                mycanvas.drawString(545+80-x_a4, 375+y_a4, ' TOTAL')
                mycanvas.drawString(545+80-x_a4, 365+y_a4, 'LITTERS')
                mycanvas.setLineWidth(0)

                mycanvas.line(10, 390+y_a4, 585, 390+y_a4)
                mycanvas.line(10, 355+y_a4, 585, 355+y_a4)
                y = 335+y_a4
                y_line = 390+y_a4
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "150":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]
                                       
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 -10, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                           
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "total_sale":
            x_a4 = 40
            y_a4 = 50
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 185+y_a4, 'Daily Business Type Report : Total Sales')
            mycanvas.line(200, 180+y_a4, 400, 180+y_a4)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 130, '{----------There is no report to show----------}')
            else:
                # Table Header
                mycanvas.setLineWidth(0)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica', 10)

                mycanvas.drawString(15, 140+y_a4, 'Items')

                mycanvas.drawString(105-x_a4, 140+y_a4, '1000ml')
                mycanvas.drawString(100-x_a4, 130+y_a4, '  Cash')
               
                mycanvas.drawString(105+80-x_a4-10-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(100+80-x_a4-10-10-10, 130+y_a4, '  Cash')

                mycanvas.drawString(200+60-x_a4-20-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(195+60-x_a4-20-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(270+60-x_a4-30-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(265+60-x_a4-30-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(340+60-x_a4-40-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(335+60-x_a4-40-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(410+60-x_a4-50-10-10, 140+y_a4, '200ml')
                mycanvas.drawString(405+60-x_a4-50-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(480+60-x_a4-60-10-10, 140+y_a4, '150ml')
                mycanvas.drawString(475+60-x_a4-60-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(545+60-x_a4-70-10-10, 140+y_a4, '5000ml')
                mycanvas.drawString(540+60-x_a4-70-10-10, 130+y_a4, ' Cash')

                mycanvas.line(10, 155+y_a4, 585, 155+y_a4)
                mycanvas.line(10, 120+y_a4, 585, 120+y_a4)

                mycanvas.drawString(620+60-x_a4-80-10-10, 140+y_a4, ' TOTAL')
                mycanvas.drawString(620+60-x_a4-80-10-10, 130+y_a4, 'LITTERS')

                y = 100+y_a4
                y_line = 155+y_a4
                x_line = 30

                # -----------------------------------------------------------------------------------------------------------------------------------------#

                # lines#
                mycanvas.line(x_line + 5-25, y_line, x_line + 5-25, y_line - 160)
                mycanvas.line(x_line + 75-50, y_line, x_line + 75-50, y_line - 160)
               
                mycanvas.line(x_line + 145-70, y_line, x_line + 145-70, y_line - 160)
                mycanvas.line(x_line + 145+80-100, y_line, x_line + 145+80-100, y_line - 160)
                mycanvas.line(x_line + 215+80-110, y_line, x_line + 215+80-110, y_line - 160)
                mycanvas.line(x_line + 285+80-120, y_line, x_line + 285+80-120, y_line - 160)
                mycanvas.line(x_line + 355+80-130, y_line, x_line + 355+80-130, y_line - 160)
                mycanvas.line(x_line + 425+80-140, y_line, x_line + 425+80-140, y_line - 160)
                mycanvas.line(x_line + 495+80-150, y_line, x_line + 495+80-150, y_line - 160)
                mycanvas.line(x_line + 565+80-160, y_line, x_line + 565+80-160, y_line - 160)
                mycanvas.line(x_line + 650+80-175, y_line, x_line + 650+80-175, y_line - 160)
                #             mycanvas.line(x_line+660,y_line,x_line+660,y_line-107)

                y_line -= 50
                mycanvas.setFont('Helvetica', 8)
                total_1000 = 0
                total_500_cash = 0
                total_500_card = 0
                total_250_cash = 0
                total_250_card = 0
                total_200 = 0
                total_150 = 0
                total_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.drawString(15, y, str(products))
                    total_litter_line = 0
                    x_1000 = 180+20-70
                    x_500 = 180+80-97
                    x_250 = 280+80-117
                    x_200 = 380+80 - 137
                    x_150 = 430+80 - 147
                    x_5000 = 620+80 - 157
                    x_total_litter_line = 610 - 172

                    if not products in data_dict["final_results"][data]:
                        pass
                    #                     if products == "TM" or products == "SM" or products == "FCM":
                    #                         y -= 15
                    #                         continue
                    #                     continue

                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                           
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_1000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_1000 += data_dict["final_results"][data][products][quantity][
                                                    types]
                                               

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        if types == "card":
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        mycanvas.drawRightString(x_500 - 10 + x_adjust, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        x_500 += 50
                                                        x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            mycanvas.drawRightString(x_500, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        else:
                                                            x_500 += 50
                                                            mycanvas.drawRightString(x_500 + 40, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    if types == "card":
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    mycanvas.drawRightString(x_250 + 30 + x_adjust, y, str(
                                                        data_dict["final_results"][data][products][quantity][types]))
                                                    x_250 += 50
                                                    x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        x_250 += 50
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_200 + 70, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_200 += data_dict["final_results"][data][products][quantity][types]
                                                x_200 += 50

                            if quantity == "150":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:

                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_150 + 90, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_150 += data_dict["final_results"][data][products][quantity][types]
                                                x_150 += 50
                                               
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         for types in data_dict["final_results"][data][products][quantity]:
                            #             if data_dict["final_results"][data][products][quantity][types] != 0 and \
                            #                     data_dict["final_results"][data][products][quantity][types] != None:
                            #                 if types == "total":
                            #                     total_litter_line += \
                            #                     data_dict["final_results"][data][products][quantity][
                            #                         types]
                            #                 else:
                            #                     mycanvas.drawRightString(x_100 - 30, y, str(
                            #                         data_dict["final_results"][data][products][quantity][types]))
                            #                     total_100 += data_dict["final_results"][data][products][quantity][
                            #                         types]

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_5000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_5000 += data_dict["final_results"][data][products][quantity][
                                                    types]

                    mycanvas.drawRightString(x_total_litter_line + 65+80, y, str(total_litter_line))
                    grand_total += total_litter_line

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line + 65+80, y - 5, str(grand_total))
                mycanvas.drawRightString(x_total_litter_line - 90+105, y - 5, str(total_150))
                mycanvas.drawRightString(x_total_litter_line - 160+115, y - 5, str(total_200))
                mycanvas.drawRightString(x_total_litter_line - 230+125, y - 5, str(total_250_card))
                mycanvas.drawRightString(x_total_litter_line - 300+135, y - 5, str(total_250_cash))
                mycanvas.drawRightString(x_total_litter_line - 370+145, y - 5, str(total_500_card))
                mycanvas.drawRightString(x_total_litter_line - 440+155, y - 5, str(total_500_cash))
                mycanvas.drawRightString(x_total_litter_line - 20+95, y - 5, str(total_5000))
                mycanvas.drawRightString(x_total_litter_line - 335, y - 5, str(total_1000))
                mycanvas.drawRightString(x_total_litter_line - 385, y - 5, "Grand Total")
                #             grand_total += data_dict[data]["products_total"]
                #             mycanvas.drawRightString(x_total_litter_line+75,y+10,str(data_dict[data]["products_total"]))
                #             y -= 10
                mycanvas.line(10, y + 8, 585, y + 8)
                mycanvas.line(10, y - 15, 585, y - 15)
               
    mycanvas.setFont('Times-Italic', 12)      
    indian = pytz.timezone('Asia/Kolkata')          
    mycanvas.drawRightString(580, 10,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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




def serve_union_wise_summay(date, session_id, user_name):
    
    
    session_id = session_id
   
    if session_id == 'all':
        session_id = list(Session.objects.filter().values_list('id', flat=True))
    else:
        session_id = int(session_id)
        session_id = list(Session.objects.filter(id=session_id).values_list('id', flat=True))
    
    final_dict = {
        'date': date,
        'session': session_id,
        'final_results': {'cash': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0, '500': 0, 'total': 0},
                                   'CanMlk': {'1000': 0, 'total': 0},
                                   'CURD': {'500': 0, '120': 0, '100': 0, '5000': 0, 'total': 0},
                                   'BtrMlk': {'200': 0, 'total': 0},
                                   'BmJar': {'200': 0, 'total': 0},
                                   'BMJF': {'200': 0, 'total': 0},
                                   'Lassi': {'200': 0, 'total': 0}},

                          'card': {'SM': {'500': 0, '250': 0, 'total': 0},
                                   'TM': {'500': 0, 'total': 0},
                                   'FCM': {'1000': 0, '500': 0, 'total': 0},
                                   'TMATE': {'1000': 0, '500': 0, 'total': 0},
                                   'CanMlk': {'1000': 0, 'total': 0},
                                   'CURD': {'500': 0, '120': 0, '100': 0, '5000': 0, 'total': 0},
                                   'BtrMlk': {'200': 0, 'total': 0},
                                   'BmJar': {'200': 0, 'total': 0},
                                   'BMJF': {'200': 0, 'total': 0},
                                   'Lassi': {'200': 0, 'total': 0}},

                          'total_sale': {'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                                                '250': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                 '500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                                 '500': {'cash': 0, 'card': 0, 'total': 0}},
                                         'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                                                  '120': {'cash': 0, 'card': 0, 'total': 0},
                                                  '500': {'cash': 0, 'card': 0, 'total': 0},
                                                  '5000': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BtrMlk': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BmJar': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'BMJF': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'Lassi': {'200': {'cash': 0, 'card': 0, 'total': 0}},
                                         'CanMlk': {'1000': {'cash': 0, 'card': 0, 'total': 0}}
                                         }
                          }}
    union_list = list(set(DailySessionllyBusinessllySale.objects.all().values_list('union', flat=True)))
    for union in union_list:
        final_dict[union] = {'SM': {'500': {'cash': 0, 'card': 0, 'total': 0},
                                    '250': {'cash': 0, 'card': 0, 'total': 0}},

                             'TM': {'500': {'cash': 0, 'card': 0, 'total': 0}},

                             'FCM': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                     '500': {'cash': 0, 'card': 0, 'total': 0}},

                             'TMATE': {'1000': {'cash': 0, 'card': 0, 'total': 0},
                                     '500': {'cash': 0, 'card': 0, 'total': 0}},       

                             'CanMlk': {'1000': {'cash': 0, 'card': 0, 'total': 0}},

                             'CURD': {'100': {'cash': 0, 'card': 0, 'total': 0},
                                      '120': {'cash': 0, 'card': 0, 'total': 0},
                                      '500': {'cash': 0, 'card': 0, 'total': 0},
                                      '5000': {'cash': 0, 'card': 0, 'total': 0}},

                             'BtrMlk': {'200': {'cash': 0, 'card': 0, 'total': 0}},

                             'BmJar': {'200': {'cash': 0, 'card': 0, 'total': 0}},

                             'BMJF': {'200': {'cash': 0, 'card': 0, 'total': 0}},

                             'Lassi': {'200': {'cash': 0, 'card': 0, 'total': 0}}
                             }
        final_dict[union]['products_total'] = 0
        final_dict[union]['union'] = union
    dsus_obj = DailySessionllyUnionllySale.objects.filter(delivery_date=date, session_id__in=session_id)
    card_sale_obj = dsus_obj.filter(sold_to='ICustomer')
    cash_sale_obj = dsus_obj.filter(sold_to__in=["Agent", "Leakage"])
    # SM
    sm_500_cash_total = cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
    sm_500_card_total = card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
    final_dict['final_results']['cash']['SM']['500'] = round(sm_500_cash_total, 3)
    final_dict['final_results']['card']['SM']['500'] = round(sm_500_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['500']['card'] = round(sm_500_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['500']['cash'] = round(sm_500_cash_total, 3)

    sm_250_cash_total = cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
    sm_250_card_total = card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
    final_dict['final_results']['cash']['SM']['250'] = round(sm_250_cash_total, 3)
    final_dict['final_results']['card']['SM']['250'] = round(sm_250_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['250']['card'] = round(sm_250_card_total, 3)
    final_dict['final_results']['total_sale']['SM']['250']['cash'] = round(sm_250_cash_total, 3)

    # Total
    final_dict['final_results']['cash']['SM']['total'] = final_dict['final_results']['cash']['SM']['500'] + \
                                                         final_dict['final_results']['cash']['SM']['250']
    final_dict['final_results']['card']['SM']['total'] = final_dict['final_results']['card']['SM']['500'] + \
                                                         final_dict['final_results']['card']['SM']['250']
    final_dict['final_results']['total_sale']['SM']['500']['total'] = \
        final_dict['final_results']['total_sale']['SM']['500']['card'] + \
        final_dict['final_results']['total_sale']['SM']['500']['cash']
    final_dict['final_results']['total_sale']['SM']['250']['total'] = \
        final_dict['final_results']['total_sale']['SM']['250']['card'] + \
        final_dict['final_results']['total_sale']['SM']['250']['cash']

    # TM
    tm_500_cash_total = cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    tm_500_card_total = card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    final_dict['final_results']['cash']['TM']['500'] = round(tm_500_cash_total, 3)
    final_dict['final_results']['card']['TM']['500'] = round(tm_500_card_total, 3)
    final_dict['final_results']['total_sale']['TM']['500']['card'] = round(tm_500_card_total, 3)
    final_dict['final_results']['total_sale']['TM']['500']['cash'] = round(tm_500_cash_total, 3)

    final_dict['final_results']['cash']['TM']['total'] = final_dict['final_results']['cash']['TM']['500']
    final_dict['final_results']['card']['TM']['total'] = final_dict['final_results']['card']['TM']['500']
    final_dict['final_results']['total_sale']['TM']['500']['total'] = \
        final_dict['final_results']['total_sale']['TM']['500']['card'] + \
        final_dict['final_results']['total_sale']['TM']['500']['cash']

    # CANMILK
    can_cash_total = cash_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum'] + cash_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum'] +cash_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
    can_card_total = card_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum'] + card_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum'] +card_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
    final_dict['final_results']['cash']['CanMlk']['1000'] = round(can_cash_total, 3)
    final_dict['final_results']['card']['CanMlk']['1000'] = round(can_card_total, 3)
    final_dict['final_results']['total_sale']['CanMlk']['1000']['cash'] = round(can_cash_total, 3)
    final_dict['final_results']['total_sale']['CanMlk']['1000']['card'] = round(can_card_total, 3)

    final_dict['final_results']['cash']['CanMlk']['total'] = final_dict['final_results']['cash']['CanMlk']['1000']
    final_dict['final_results']['card']['CanMlk']['total'] = final_dict['final_results']['card']['CanMlk']['1000']
    final_dict['final_results']['total_sale']['CanMlk']['1000']['total'] = \
    final_dict['final_results']['total_sale']['CanMlk']['1000']['card'] + \
    final_dict['final_results']['total_sale']['CanMlk']['1000']['cash']

    #  FCM
    fcm_500_cash_total = cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
    fcm_500_card_total = card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
    final_dict['final_results']['cash']['FCM']['500'] = round(fcm_500_cash_total, 3)
    final_dict['final_results']['card']['FCM']['500'] = round(fcm_500_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['500']['card'] = round(fcm_500_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['500']['cash'] = round(fcm_500_cash_total, 3)
    
    fcm_1000_cash_total = cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
    fcm_1000_card_total = card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
    final_dict['final_results']['cash']['FCM']['1000'] = round(fcm_1000_cash_total, 3)
    final_dict['final_results']['card']['FCM']['1000'] = round(fcm_1000_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['1000']['card'] = round(fcm_1000_card_total, 3)
    final_dict['final_results']['total_sale']['FCM']['1000']['cash'] = round(fcm_1000_cash_total, 3)

    final_dict['final_results']['cash']['FCM']['total'] = final_dict['final_results']['cash']['FCM']['500'] + final_dict['final_results']['cash']['FCM']['1000']
    final_dict['final_results']['card']['FCM']['total'] = final_dict['final_results']['card']['FCM']['500'] + final_dict['final_results']['card']['FCM']['1000']
    final_dict['final_results']['total_sale']['FCM']['500']['total'] = \
        final_dict['final_results']['total_sale']['FCM']['500']['card'] + \
        final_dict['final_results']['total_sale']['FCM']['500']['cash']
    final_dict['final_results']['total_sale']['FCM']['1000']['total'] = \
        final_dict['final_results']['total_sale']['FCM']['1000']['card'] + \
        final_dict['final_results']['total_sale']['FCM']['1000']['cash']
    
     #  TMATE
    tea_500_cash_total = cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
    tea_500_card_total = card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
    final_dict['final_results']['cash']['TMATE']['500'] = round(tea_500_cash_total, 3)
    final_dict['final_results']['card']['TMATE']['500'] = round(tea_500_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['500']['card'] = round(tea_500_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['500']['cash'] = round(tea_500_cash_total, 3)
    
    tea_1000_cash_total = cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
    tea_1000_card_total = card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
    final_dict['final_results']['cash']['TMATE']['1000'] = round(tea_1000_cash_total, 3)
    final_dict['final_results']['card']['TMATE']['1000'] = round(tea_1000_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['1000']['card'] = round(tea_1000_card_total, 3)
    final_dict['final_results']['total_sale']['TMATE']['1000']['cash'] = round(tea_1000_cash_total, 3)

    final_dict['final_results']['cash']['TMATE']['total'] = final_dict['final_results']['cash']['TMATE']['500'] + final_dict['final_results']['cash']['TMATE']['1000']
    final_dict['final_results']['card']['TMATE']['total'] = final_dict['final_results']['card']['TMATE']['500'] + final_dict['final_results']['card']['TMATE']['1000']
    final_dict['final_results']['total_sale']['TMATE']['500']['total'] = \
        final_dict['final_results']['total_sale']['TMATE']['500']['card'] + \
        final_dict['final_results']['total_sale']['TMATE']['500']['cash']
    final_dict['final_results']['total_sale']['TMATE']['1000']['total'] = \
        final_dict['final_results']['total_sale']['TMATE']['1000']['card'] + \
        final_dict['final_results']['total_sale']['TMATE']['1000']['cash']


    # Butter_milk
    buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
    buttermilk200_card_total = card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
    final_dict['final_results']['cash']['BtrMlk']['200'] = buttermilk200_cash_total
    final_dict['final_results']['card']['BtrMlk']['200'] = buttermilk200_card_total
    final_dict['final_results']['total_sale']['BtrMlk']['200']['card'] = round(buttermilk200_card_total, 3)
    final_dict['final_results']['total_sale']['BtrMlk']['200']['cash'] = round(buttermilk200_cash_total, 3)

    final_dict['final_results']['cash']['BtrMlk']['total'] = final_dict['final_results']['cash']['BtrMlk']['200']
    final_dict['final_results']['card']['BtrMlk']['total'] = final_dict['final_results']['card']['BtrMlk']['200']
    final_dict['final_results']['total_sale']['BtrMlk']['200']['total'] = \
        final_dict['final_results']['total_sale']['BtrMlk']['200']['card'] + \
        final_dict['final_results']['total_sale']['BtrMlk']['200']['cash']

    
    # Butter_milk_jar
    buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
    buttermilk200_card_total = card_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum']
    final_dict['final_results']['cash']['BmJar']['200'] = buttermilk200_cash_total
    final_dict['final_results']['card']['BmJar']['200'] = buttermilk200_card_total
    final_dict['final_results']['total_sale']['BmJar']['200']['card'] = round(buttermilk200_card_total, 3)
    final_dict['final_results']['total_sale']['BmJar']['200']['cash'] = round(buttermilk200_cash_total, 3)

    final_dict['final_results']['cash']['BmJar']['total'] = final_dict['final_results']['cash']['BmJar']['200']
    final_dict['final_results']['card']['BmJar']['total'] = final_dict['final_results']['card']['BmJar']['200']
    final_dict['final_results']['total_sale']['BmJar']['200']['total'] = \
        final_dict['final_results']['total_sale']['BmJar']['200']['card'] + \
        final_dict['final_results']['total_sale']['BmJar']['200']['cash']

    
    # Butter_milk_jar free
    buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
    buttermilk200_card_total = card_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum']
    final_dict['final_results']['cash']['BMJF']['200'] = buttermilk200_cash_total
    final_dict['final_results']['card']['BMJF']['200'] = buttermilk200_card_total
    final_dict['final_results']['total_sale']['BMJF']['200']['card'] = round(buttermilk200_card_total, 3)
    final_dict['final_results']['total_sale']['BMJF']['200']['cash'] = round(buttermilk200_cash_total, 3)

    final_dict['final_results']['cash']['BMJF']['total'] = final_dict['final_results']['cash']['BMJF']['200']
    final_dict['final_results']['card']['BMJF']['total'] = final_dict['final_results']['card']['BMJF']['200']
    final_dict['final_results']['total_sale']['BMJF']['200']['total'] = \
        final_dict['final_results']['total_sale']['BMJF']['200']['card'] + \
        final_dict['final_results']['total_sale']['BMJF']['200']['cash']


    # lassi
    lassi200_cash_total = cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
    lassi200_card_total = card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
    final_dict['final_results']['cash']['Lassi']['200'] = lassi200_card_total
    final_dict['final_results']['card']['Lassi']['200'] = lassi200_card_total
    final_dict['final_results']['total_sale']['Lassi']['200']['cash'] = lassi200_cash_total
    final_dict['final_results']['total_sale']['Lassi']['200']['card'] = lassi200_card_total

    final_dict['final_results']['cash']['Lassi']['total'] = final_dict['final_results']['cash']['Lassi']['200']
    final_dict['final_results']['card']['Lassi']['total'] = final_dict['final_results']['card']['Lassi']['200']
    final_dict['final_results']['total_sale']['Lassi']['200']['total'] = \
        final_dict['final_results']['total_sale']['Lassi']['200']['card'] + \
        final_dict['final_results']['total_sale']['Lassi']['200']['cash']

    # CURD
    curd_500_cash_total = cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    curd_500_card_total = card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
    final_dict['final_results']['cash']['CURD']['500'] = round(curd_500_cash_total, 3)
    final_dict['final_results']['card']['CURD']['500'] = round(curd_500_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['500']['card'] = round(curd_500_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['500']['cash'] = round(curd_500_cash_total, 3)

    curd_150_cash_total = cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
    curd_150_card_total = card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
    final_dict['final_results']['cash']['CURD']['120'] = round(curd_150_cash_total, 3)
    final_dict['final_results']['card']['CURD']['120'] = round(curd_150_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['120']['card'] = round(curd_150_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['120']['cash'] = round(curd_150_cash_total, 3)

    curd_100_cash_total = cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
    curd_100_card_total = card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
    final_dict['final_results']['cash']['CURD']['100'] = round(curd_100_cash_total, 3)
    final_dict['final_results']['card']['CURD']['100'] = round(curd_100_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['100']['card'] = round(curd_100_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['100']['cash'] = round(curd_100_cash_total, 3)


    curd_5000_cash_total = cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    curd_5000_card_total = card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
    final_dict['final_results']['cash']['CURD']['5000'] = round(curd_5000_cash_total, 3)
    final_dict['final_results']['card']['CURD']['5000'] = round(curd_5000_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['5000']['card'] = round(curd_5000_card_total, 3)
    final_dict['final_results']['total_sale']['CURD']['5000']['cash'] = round(curd_5000_cash_total, 3)

    # Total
    final_dict['final_results']['cash']['CURD']['total'] = final_dict['final_results']['cash']['CURD']['500'] + \
                                                           final_dict['final_results']['cash']['CURD']['5000'] + \
                                                           final_dict['final_results']['cash']['CURD']['120'] + \
                                                           final_dict['final_results']['cash']['CURD']['100']
    final_dict['final_results']['card']['CURD']['total'] = final_dict['final_results']['card']['CURD']['500'] + \
                                                           final_dict['final_results']['card']['CURD']['5000'] + \
                                                           final_dict['final_results']['card']['CURD']['120'] + \
                                                           final_dict['final_results']['card']['CURD']['100']
    final_dict['final_results']['total_sale']['CURD']['500']['total'] = \
        final_dict['final_results']['total_sale']['CURD']['500']['card'] + \
        final_dict['final_results']['total_sale']['CURD']['500']['cash']
    final_dict['final_results']['total_sale']['CURD']['120']['total'] = \
        final_dict['final_results']['total_sale']['CURD']['120']['card'] + \
        final_dict['final_results']['total_sale']['CURD']['120']['cash']
    final_dict['final_results']['total_sale']['CURD']['100']['total'] = \
        final_dict['final_results']['total_sale']['CURD']['100']['card'] + \
        final_dict['final_results']['total_sale']['CURD']['100']['cash']
    final_dict['final_results']['total_sale']['CURD']['5000']['total'] = \
        final_dict['final_results']['total_sale']['CURD']['5000']['card'] + \
        final_dict['final_results']['total_sale']['CURD']['5000']['cash']

    # business type wise report
    for union in union_list:
        product_total = 0
        if dsus_obj.filter(union=union).count() > 0:
            card_sale_obj = dsus_obj.filter(sold_to='ICustomer', union=union)
            cash_sale_obj = dsus_obj.filter(sold_to__in=["Agent", "Leakage"], union=union)

            # SM
            if cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] is None:
                sm_500_cash_total = 0
            else:
                sm_500_cash_total = cash_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            if card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] is None:
                sm_500_card_total = 0
            else:
                sm_500_card_total = card_sale_obj.aggregate(Sum('std500_litre'))['std500_litre__sum']
            sm_500_cash_total_count = cash_sale_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            sm_500_card_total_count = card_sale_obj.aggregate(Sum('std500_pkt'))['std500_pkt__sum']
            final_dict[union]['SM']['500']['card'] = sm_500_card_total_count
            final_dict[union]['SM']['500']['cash'] = sm_500_cash_total_count

            if cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] is None:
                sm_250_cash_total = 0
            else:
                sm_250_cash_total = cash_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            if card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] is None:
                sm_250_card_total = 0
            else:
                sm_250_card_total = card_sale_obj.aggregate(Sum('std250_litre'))['std250_litre__sum']
            sm_250_cash_total_count = cash_sale_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            sm_250_card_total_count = card_sale_obj.aggregate(Sum('std250_pkt'))['std250_pkt__sum']
            final_dict[union]['SM']['250']['card'] = sm_250_card_total_count
            final_dict[union]['SM']['250']['cash'] = sm_250_cash_total_count

            # Total

            total_sm_500_litre = round(Decimal(sm_500_cash_total + sm_500_card_total), 3)
            total_sm_250_litre = round(Decimal(sm_250_cash_total + sm_250_card_total), 3)
            final_dict[union]['SM']['500']['total'] = total_sm_500_litre
            final_dict[union]['SM']['250']['total'] = total_sm_250_litre
            product_total += total_sm_500_litre + total_sm_250_litre

            #       TM
            if cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] is None:
                tm_500_cash_total = 0
            else:
                tm_500_cash_total = cash_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            if card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] is None:
                tm_500_card_total = 0
            else:
                tm_500_card_total = card_sale_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
            tm_500_cash_total_count = cash_sale_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            tm_500_card_total_count = card_sale_obj.aggregate(Sum('tm500_pkt'))['tm500_pkt__sum']
            final_dict[union]['TM']['500']['card'] = tm_500_card_total_count
            final_dict[union]['TM']['500']['cash'] = tm_500_cash_total_count

            # Total
            total_tm_500_litre = round(Decimal(tm_500_cash_total + tm_500_card_total), 3)
            final_dict[union]['TM']['500']['total'] = total_tm_500_litre
            product_total += total_tm_500_litre


            #       CAN
            tm_can = cash_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
            sm_can = cash_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
            fcm_can = cash_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum'] 
            if tm_can is None:
                tm_can = 0
            if sm_can is None:
                sm_can = 0
            if fcm_can is None:
                fcm_can = 0
            can_cash_total = tm_can + sm_can + fcm_can

            tm_can = card_sale_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum']
            sm_can = card_sale_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum']
            fcm_can = card_sale_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum'] 

            if tm_can is None:
                tm_can = 0
            if sm_can is None:
                sm_can = 0
            if fcm_can is None:
                fcm_can = 0
            can_card_total = tm_can + sm_can + fcm_can

            can_cash_total_count = round(can_cash_total)
            can_card_total_count = round(can_card_total)
            print(can_cash_total_count)
            final_dict[union]['CanMlk']['1000']['card'] = can_card_total_count
            final_dict[union]['CanMlk']['1000']['cash'] = can_cash_total_count

            # Total
            can_total_litre = round(Decimal(can_cash_total + can_card_total), 3)
            final_dict[union]['CanMlk']['1000']['total'] = can_total_litre
            product_total += can_total_litre


            #       FCM
            if cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] is None:
                fcm_500_cash_total = 0
            else:
                fcm_500_cash_total = cash_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            if card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] is None:
                fcm_500_card_total = 0
            else:
                fcm_500_card_total = card_sale_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum']
            fcm_500_cash_total_count = cash_sale_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            fcm_500_card_total_count = card_sale_obj.aggregate(Sum('fcm500_pkt'))['fcm500_pkt__sum']
            final_dict[union]['FCM']['500']['card'] = fcm_500_card_total_count
            final_dict[union]['FCM']['500']['cash'] = fcm_500_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] is None:
                fcm_1000_cash_total = 0
            else:
                fcm_1000_cash_total = cash_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            if card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] is None:
                fcm_1000_card_total = 0
            else:
                fcm_1000_card_total = card_sale_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum']
            fcm_1000_cash_total_count = cash_sale_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            fcm_1000_card_total_count = card_sale_obj.aggregate(Sum('fcm1000_pkt'))['fcm1000_pkt__sum']
            final_dict[union]['FCM']['1000']['card'] = fcm_1000_card_total_count
            final_dict[union]['FCM']['1000']['cash'] = fcm_1000_cash_total_count

            # Total
            total_fcm_500_litre = round(Decimal(fcm_500_cash_total + fcm_500_card_total), 3)
            total_fcm_1000_litre = round(Decimal(fcm_1000_cash_total + fcm_1000_card_total), 3)
            final_dict[union]['FCM']['500']['total'] = total_fcm_500_litre
            final_dict[union]['FCM']['1000']['total'] = total_fcm_1000_litre
            product_total += total_fcm_500_litre + total_fcm_1000_litre

            #       TMATE
            if cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] is None:
                tea_500_cash_total = 0
            else:
                tea_500_cash_total = cash_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            if card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] is None:
                tea_500_card_total = 0
            else:
                tea_500_card_total = card_sale_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum']
            tea_500_cash_total_count = cash_sale_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            tea_500_card_total_count = card_sale_obj.aggregate(Sum('tea500_pkt'))['tea500_pkt__sum']
            final_dict[union]['TMATE']['500']['card'] = tea_500_card_total_count
            final_dict[union]['TMATE']['500']['cash'] = tea_500_cash_total_count
            
            if cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum'] is None:
                tea_1000_cash_total = 0
            else:
                tea_1000_cash_total = cash_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            if card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum'] is None:
                tea_1000_card_total = 0
            else:
                tea_1000_card_total = card_sale_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum']
            tea_1000_cash_total_count = cash_sale_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            tea_1000_card_total_count = card_sale_obj.aggregate(Sum('tea1000_pkt'))['tea1000_pkt__sum']
            final_dict[union]['TMATE']['1000']['card'] = tea_1000_card_total_count
            final_dict[union]['TMATE']['1000']['cash'] = tea_1000_cash_total_count


            # Total
            total_tea_500_litre = round(Decimal(tea_500_cash_total + tea_500_card_total), 3)
            total_tea_1000_litre = round(Decimal(tea_1000_cash_total + tea_1000_card_total), 3)
            final_dict[union]['TMATE']['500']['total'] = total_tea_500_litre
            final_dict[union]['TMATE']['1000']['total'] = total_tea_1000_litre
            product_total += total_tea_500_litre + total_tea_1000_litre

            # Lassi
            if cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum'] is None:
                lassi200_cash_total = 0
            else:
                lassi200_cash_total = cash_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            if card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum'] is None:
                lassi200_card_total = 0
            else:
                lassi200_card_total = card_sale_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum']
            lassi200_cash_total_count = cash_sale_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            lassi200_card_total_count = card_sale_obj.aggregate(Sum('lassi200_pkt'))['lassi200_pkt__sum']
            final_dict[union]['Lassi']['200']['card'] = lassi200_card_total_count
            final_dict[union]['Lassi']['200']['cash'] = lassi200_cash_total_count

            # Total
            total_lassi200_litre = round(Decimal(lassi200_card_total + lassi200_cash_total), 3)
            final_dict[union]['Lassi']['200']['total'] = total_lassi200_litre
            product_total += total_lassi200_litre

            # Butter_milk
            if cash_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum'] is None:
                buttermilk200_cash_total = 0
            else:
                buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('buttermilk200_litre'))[
                    'buttermilk200_litre__sum']
            if card_sale_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum'] is None:
                buttermilk200_total = 0
            else:
                buttermilk200_card_total = card_sale_obj.aggregate(Sum('buttermilk200_litre'))[
                    'buttermilk200_litre__sum']
            buttermilk200_cash_total_count = cash_sale_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            buttermilk200_card_total_count = card_sale_obj.aggregate(Sum('buttermilk200_pkt'))['buttermilk200_pkt__sum']
            final_dict[union]['BtrMlk']['200']['card'] = buttermilk200_card_total_count
            final_dict[union]['BtrMlk']['200']['cash'] = buttermilk200_cash_total_count

             # Total
            total_buttermilk200_litre = round(Decimal(buttermilk200_card_total + buttermilk200_cash_total), 3)
            final_dict[union]['BtrMlk']['200']['total'] = total_buttermilk200_litre
            product_total += total_buttermilk200_litre

            # Butter_milk_jar
            if cash_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum'] is None:
                buttermilk200_cash_total = 0
            else:
                buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bm_jar200_litre'))[
                    'bm_jar200_litre__sum']
            if card_sale_obj.aggregate(Sum('bm_jar200_litre'))['bm_jar200_litre__sum'] is None:
                buttermilk200_total = 0
            else:
                buttermilk200_card_total = card_sale_obj.aggregate(Sum('bm_jar200_litre'))[
                    'bm_jar200_litre__sum']
            buttermilk200_cash_total_count = cash_sale_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            buttermilk200_card_total_count = card_sale_obj.aggregate(Sum('bm_jar200_pkt'))['bm_jar200_pkt__sum']
            final_dict[union]['BmJar']['200']['card'] = buttermilk200_card_total_count
            final_dict[union]['BmJar']['200']['cash'] = buttermilk200_cash_total_count

            # Total
            total_bm_jar200_litre = round(Decimal(buttermilk200_card_total + buttermilk200_cash_total), 3)
            final_dict[union]['BmJar']['200']['total'] = total_bm_jar200_litre
            product_total += total_bm_jar200_litre


            # Butter_milk_jar_free
            if cash_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum'] is None:
                buttermilk200_cash_total = 0
            else:
                buttermilk200_cash_total = cash_sale_obj.aggregate(Sum('bmjf200_litre'))[
                    'bmjf200_litre__sum']
            if card_sale_obj.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum'] is None:
                buttermilk200_total = 0
            else:
                buttermilk200_card_total = card_sale_obj.aggregate(Sum('bmjf200_litre'))[
                    'bmjf200_litre__sum']
            buttermilk200_cash_total_count = cash_sale_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            buttermilk200_card_total_count = card_sale_obj.aggregate(Sum('bmjf200_pkt'))['bmjf200_pkt__sum']
            final_dict[union]['BMJF']['200']['card'] = buttermilk200_card_total_count
            final_dict[union]['BMJF']['200']['cash'] = buttermilk200_cash_total_count

            # Total
            total_bmjf200_litre = round(Decimal(buttermilk200_card_total + buttermilk200_cash_total), 3)
            final_dict[union]['BMJF']['200']['total'] = total_bmjf200_litre
            product_total += total_bmjf200_litre


            #       CURD
            if cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] is None:
                curd_500_cash_total = 0
            else:
                curd_500_cash_total = cash_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] is None:
                curd_500_card_total = 0
            else:
                curd_500_card_total = card_sale_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum']
            curd_500_cash_total_count = cash_sale_obj.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
            curd_500_card_total_count = card_sale_obj.aggregate(Sum('curd500_pkt'))['curd500_pkt__sum']
            final_dict[union]['CURD']['500']['card'] = curd_500_card_total_count
            final_dict[union]['CURD']['500']['cash'] = curd_500_cash_total_count

            if cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] is None:
                curd_150_cash_total = 0
            else:
                curd_150_cash_total = cash_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] is None:
                curd_150_card_total = 0
            else:
                curd_150_card_total = card_sale_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum']
            curd_150_cash_total_count = cash_sale_obj.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
            curd_150_card_total_count = card_sale_obj.aggregate(Sum('curd150_pkt'))['curd150_pkt__sum']
            final_dict[union]['CURD']['120']['card'] = curd_150_card_total_count
            final_dict[union]['CURD']['120']['cash'] = curd_150_cash_total_count

            if cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] is None:
                curd_100_cash_total = 0
            else:
                curd_100_cash_total = cash_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            if card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] is None:
                curd_100_card_total = 0
            else:
                curd_100_card_total = card_sale_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum']
            curd_100_cash_total_count = cash_sale_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            curd_100_card_total_count = card_sale_obj.aggregate(Sum('cupcurd_count'))['cupcurd_count__sum']
            final_dict[union]['CURD']['100']['card'] = curd_100_card_total_count
            final_dict[union]['CURD']['100']['cash'] = curd_100_cash_total_count


            if cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum'] is None:
                curd_5000_cash_total = 0
            else:
                curd_5000_cash_total = cash_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            if card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum'] is None:
                curd_5000_card_total = 0
            else:
                curd_5000_card_total = card_sale_obj.aggregate(Sum('curd5000_kgs'))['curd5000_kgs__sum']
            curd_5000_cash_total_count = cash_sale_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            curd_5000_card_total_count = card_sale_obj.aggregate(Sum('curd5000_pkt'))['curd5000_pkt__sum']
            final_dict[union]['CURD']['5000']['card'] = curd_5000_card_total_count
            final_dict[union]['CURD']['5000']['cash'] = curd_5000_cash_total_count


            # Total
            total_curd_500_litre = round(Decimal(curd_500_cash_total + curd_500_card_total), 3)
            total_curd_150_litre = round(Decimal(curd_150_cash_total + curd_150_card_total), 3)
            total_curd_100_litre = round(Decimal(curd_100_cash_total + curd_100_card_total), 3)
            total_curd_5000_litre = round(Decimal(curd_5000_cash_total + curd_5000_card_total), 3)
            final_dict[union]['CURD']['500']['total'] = total_curd_500_litre
            final_dict[union]['CURD']['120']['total'] = total_curd_150_litre
            final_dict[union]['CURD']['100']['total'] = total_curd_100_litre
            final_dict[union]['CURD']['5000']['total'] = total_curd_5000_litre
            product_total += total_curd_500_litre + total_curd_150_litre + total_curd_100_litre + total_curd_5000_litre

            final_dict[union]['products_total'] = round(Decimal(product_total), 3)
        data = generate_pdf_for_union_wise_summary(final_dict, user_name, date, session_id)
    return data


def generate_pdf_for_union_wise_summary(data_dict, user_name, date, session_id):
    
    session_name = ""
   
    for ses in session_id:
        session = Session.objects.get(id=ses).name
        session_name += session + ', '
   
    file_name = str(data_dict['date']) + '_' + str(session_name) + '_overall_union_details' + '.pdf'
    file_path = os.path.join('static/media/route_wise_report/', file_name)
#     file_path = os.path.join('static/media', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))

    # _Head_lines_#

    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))
   
    date_in_format = datetime.datetime.strptime(data_dict["date"], '%Y-%m-%d')
    date = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
   
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 795, 'Daily Union Report : Total Sales ( '+str(date)+", "+str(session_name)+" )")

    x_a4 = 50
    y_a4 = 70
    # Table Header
    mycanvas.setLineWidth(0)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
    mycanvas.drawString(35-20, 655+y_a4, 'No')
    mycanvas.drawString(60-20, 655+y_a4, 'Zone')
    mycanvas.drawString(95-20, 665+y_a4, 'Items')

    mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
    mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

    mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
    mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')
   
    mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

    mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
    mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
    mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

    mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
    mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(470-20-x_a4, 650+y_a4, '120ml')
    mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

    mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
    mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

    mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
    mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

    mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
    mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
    mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
    mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

    products_list = ["TM", "SM", "FCM", "TMATE","CanMlk", "CURD", "BtrMlk", "BmJar", "BMJF", "Lassi"]
#     quantity_list = ["1000", "500", "250", "200", "150","100"]
    quantity_list = ["1000","500", "250", "200", "120","5000"]
    route_list = list(Route.objects.all().values_list("name",flat=True))

    index = 1
    y = 620+y_a4
    y_line = 690+y_a4
    x_line = 30
    grand_total = 0
    mycanvas.setFont('Helvetica', 8)
   
    current_route = ""

    for data in data_dict:
        print(data)
        if data == "date" or data == "session" or data == "final_results" or data_dict[data]["products_total"] == 0:
            continue
        mycanvas.drawString(13, y, str(index))
        #         mycanvas.drawString(75, y,str(data))

        # -----------------------------------------------------------------------------------------------------------------------------------------#

        # lines#
        mycanvas.line(x_line-20, y_line, x_line-20, y - 105)
        mycanvas.line(x_line, y_line, x_line, y - 105)
        mycanvas.line(x_line + 40, y_line, x_line + 40, y - 105)
        mycanvas.line(x_line + 80, y_line, x_line + 80, y - 105)
       
        mycanvas.line(x_line + 110+15, y_line - 26, x_line + 110+15, y - 105)
        mycanvas.line(x_line + 100+75, y_line - 26, x_line + 100+75, y - 105)
        mycanvas.line(x_line + 155+70, y_line - 26, x_line + 155+70, y - 105)
       
        mycanvas.line(x_line + 210+60, y_line - 26, x_line + 210+60, y - 105)
        mycanvas.line(x_line + 265+50, y_line - 26, x_line + 265+50, y - 105)
        mycanvas.line(x_line + 320+40, y_line - 26, x_line + 320+40, y - 105)
        mycanvas.line(x_line + 375+30, y_line - 26, x_line + 375+30, y - 105)
        mycanvas.line(x_line + 430+20, y_line, x_line + 430+20, y - 105)
        mycanvas.line(x_line + 430+70, y_line, x_line + 430+70, y - 105)
        mycanvas.line(x_line + 555, y_line, x_line + 555, y - 105)

        y_line -= 50
        current_route = data_dict[data]["union"]
        route_name = ''
        for letter in data_dict[data]["union"]:
            if letter == ' ':
                continue
            else:
                route_name += letter
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(30, y, str(route_name[:7]))
#         mycanvas.setFont('Helvetica', 12)
        for products in products_list:
            mycanvas.drawString(75, y, str(products))
            total_litter_line = 0
            x_1000 = 115+10
            x_500 = 105+60
            x_250 = 195+60
            x_200 = 275+60
            x_150 = 315+60
            x_5000 = 430+20
            x_total_litter_line = 520
            if not products in data_dict[data]:
                pass
            #                     if products == "TM" or products == "SM" or products == "FCM":
            #                         y -= 15
            #                         continue
            #                     continue
            if products in data_dict[data]:
                for quantity in quantity_list:
                    try:
                       
                        if quantity == "1000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_1000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_1000 += 50
                       
                        if quantity == "500":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_500 + 35, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_500 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_500 + 30, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_500 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_500 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))

                        if quantity == "250":
                            if len(data_dict[data][products][quantity]) == 3:
                                x_adjust = 0
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if data_dict[data][products][quantity][types] != 0 and \
                                                data_dict[data][products][quantity][types] != None:
                                            mycanvas.drawRightString(x_250 + 40 - x_adjust, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        x_250 += 50
                                        x_adjust = 5

                            if len(data_dict[data][products][quantity]) == 2:
                                for types in data_dict[data][products][quantity]:
                                    if types == "total":
                                        total_litter_line += data_dict[data][products][quantity][types]
                                    else:
                                        if types == "cash":
                                            mycanvas.drawRightString(x_250 + 40, y,
                                                                     str(data_dict[data][products][quantity][types]))
                                        else:
                                            x_250 += 50
                                            if data_dict[data][products][quantity][types] != 0 and \
                                                    data_dict[data][products][quantity][types] != None:
                                                mycanvas.drawRightString(x_250 + 40, y,
                                                                         str(data_dict[data][products][quantity][
                                                                                 types]))
                       
                        if quantity == "200":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_200 + 50, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_200 += 50

                        if quantity == "120":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_150 + 55, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_150 += 50


                        # if quantity == "100":
                        #     for types in data_dict[data][products][quantity]:
                        #         if types == "total":
                        #             total_litter_line += data_dict[data][products][quantity][types]
                        #         else:
                        #             if data_dict[data][products][quantity][types] != 0 and \
                        #                     data_dict[data][products][quantity][types] != None:
                        #                 mycanvas.drawRightString(x_100 + 25, y,
                        #                                          str(data_dict[data][products][quantity][types]))
                        #             x_100 += 30


                        if quantity == "5000":
                            for types in data_dict[data][products][quantity]:
                                if types == "total":
                                    total_litter_line += data_dict[data][products][quantity][types]
                                else:
                                    if data_dict[data][products][quantity][types] != 0 and \
                                            data_dict[data][products][quantity][types] != None:
                                        mycanvas.drawRightString(x_5000 + 25, y,
                                                                 str(data_dict[data][products][quantity][types]))
                                    x_5000 += 30

                       
                    except:
                        pass
            mycanvas.drawRightString(x_total_litter_line + 5, y, str(total_litter_line))
            y -= 12
        grand_total += data_dict[data]["products_total"]
        mycanvas.drawRightString(x_total_litter_line + 60, y + 10, str(data_dict[data]["products_total"]))
        y -= 10
        mycanvas.line(10, y + 13, 585, y + 13)
        # -----------------------------------------------6------------------------------------------------------#
        if index % 6 == 0:
            mycanvas.showPage()

            #     mycanvas.setStrokeColor(colors.lightgrey)
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.drawCentredString(300, 795, 'Daily Union Report : Total Sales ( '+str(date)+", "+str(session_name)+" )")

            x_a4 = 50
            y_a4 = 70
            # Table Header
            mycanvas.setLineWidth(0)
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica', 8)
            mycanvas.drawString(37-20, 665+y_a4, 'Sl.')
            mycanvas.drawString(35-20, 655+y_a4, 'No')
            mycanvas.drawString(60-20, 655+y_a4, 'Zone')
            mycanvas.drawString(95-20, 665+y_a4, 'Items')

            mycanvas.drawCentredString(300, 675+y_a4, 'MILK Supplied')
            mycanvas.line(160-x_a4, 665+y_a4, 430+90-x_a4+10, 665+y_a4)

            mycanvas.drawString(170-x_a4, 650+y_a4, '1000ml')
            mycanvas.drawString(170-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(155+65-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(155+65-x_a4, 640+y_a4, '  Cash')

            mycanvas.drawString(215+55-x_a4, 650+y_a4, '500ml')
            mycanvas.drawString(215+55-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(290+25-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(290+25-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(360-x_a4, 650+y_a4, '250ml')
            mycanvas.drawString(360-x_a4, 640+y_a4, ' Card')

            mycanvas.drawString(410-x_a4, 650+y_a4, '200ml')
            mycanvas.drawString(410-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(470-20-x_a4, 650+y_a4, '120ml')
            mycanvas.drawString(470-20-x_a4, 640+y_a4, ' Cash')

            mycanvas.drawString(525-30+5-x_a4, 650+y_a4, '5000ml')
            mycanvas.drawString(525-30+5-x_a4, 640+y_a4, ' Cash')

            mycanvas.line(10, 690+y_a4, 585, 690+y_a4)
            mycanvas.line(10, 632+y_a4, 585, 632+y_a4)

            mycanvas.drawString(575-40-x_a4, 675+y_a4, ' TOTAL')
            mycanvas.drawString(575-40-x_a4, 665+y_a4, 'LITTERS')
            mycanvas.drawString(635-40-x_a4, 665+y_a4, '   NET')
            mycanvas.drawString(635-40-x_a4, 655+y_a4, 'LITTERS')

            products_list = ["TM", "SM", "FCM", "TMATE","CanMlk", "CURD", "BtrMlk", "BmJar",  "BMJF", "Lassi"]
            quantity_list = ["1000","500", "250", "200", "120","5000"]
            route_list = list(Route.objects.all().values_list("name",flat=True))

            y = 620+y_a4
            y_line = 690+y_a4
            x_line = 30
            mycanvas.setFont('Helvetica', 8)

        index += 1
    x_total_litter_line = 520
    mycanvas.line(10, y + 13, 10, y - 13)
    mycanvas.line(585, y + 13, 585, y - 13)
    mycanvas.line(585, y + 13, 585, y - 13)
    mycanvas.line(10, y + 13, 585, y + 13)
    mycanvas.line(10, y - 13, 585, y - 13)
    mycanvas.drawRightString(x_total_litter_line + 60, y - 5, str(grand_total))
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(x_total_litter_line - 80, y - 5, 'Grand Total')

    # --------------------------------------------------------Final Report----------------------------------------------------#

    mycanvas.showPage()
    x_a4 = 90
    y_a4 = 120
    #     mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 795, 'Daily Union Report : Total Sales ( '+str(date)+", "+str(session_name)+" )")
   

    mycanvas.setFont('Helvetica', 10)
    #     mycanvas.drawString(70,655,'zone')
    mycanvas.drawString(110-x_a4, 600+y_a4, 'Items')

    mycanvas.drawString(192-x_a4, 590+y_a4, '1000ml')
    mycanvas.drawString(192+80-x_a4, 590+y_a4, '500ml')
    mycanvas.drawString(272+80-x_a4, 590+y_a4, '250ml')
    mycanvas.drawString(322+80-x_a4, 590+y_a4, '200ml')
    mycanvas.drawString(402+80-x_a4, 590+y_a4, '120ml')
    mycanvas.drawString(472+80-x_a4, 590+y_a4, '5000ml')
    mycanvas.drawString(545+80-x_a4, 600+y_a4, ' TOTAL')
    mycanvas.drawString(545+80-x_a4, 590+y_a4, 'LITTERS')
    #     mycanvas.drawString(602,620,'  NET')
    #     mycanvas.drawString(602,610,'LITTERS')

    # ------------------------------------------lines--------------------------------------------------#
    mycanvas.setLineWidth(0)
    mycanvas.line(90-x_a4+10, 615+y_a4, 615+80-x_a4-20, 615+y_a4)
    mycanvas.line(90-x_a4+10, 580+y_a4, 615+80-x_a4-20, 580+y_a4)

    #     mycanvas.drawString()

    y = 560+y_a4
    y_line = 615+y_a4
    x_line = 90-x_a4
    grand_total = 0

    for data in data_dict["final_results"]:
        mycanvas.line(x_line+10, y_line, x_line+10, y_line - 215)
        mycanvas.line(x_line + 70+10, y_line, x_line + 70+10, y_line - 215)
        mycanvas.line(x_line + 145+10, y_line, x_line + 145+10, y_line - 215)
        mycanvas.line(x_line + 145+80+10, y_line, x_line + 145+80+10, y_line - 215)

        mycanvas.line(x_line + 220+80, y_line, x_line + 220+80, y_line - 215)
        mycanvas.line(x_line + 295+80-10, y_line, x_line + 295+80-10, y_line - 215)
        mycanvas.line(x_line + 370+80-10, y_line, x_line + 370+80-10, y_line - 215)

        mycanvas.line(x_line + 445+80-20, y_line, x_line + 445+80-20, y_line - 215)
        mycanvas.line(x_line + 525+80-20, y_line, x_line + 525+80-20, y_line - 215)
        #         mycanvas.line(x_line+605,y_line,x_line+605,y_line-115)

        if data == "cash":
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 645+y_a4, 'Daily Union Report : Total-Cash Sales')
            mycanvas.line(200, 640+y_a4, 400, 640+y_a4)

            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(350, 595, 'Daily Union Report : Total-Cash Sales')
            else:
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]

                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 + 8 - 18, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]


                                       
                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 +8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                           
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "card":
            y_a4 -= 25
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 410+y_a4, 'Daily Union Report : Total-Card Sales')
            mycanvas.line(200, 405+y_a4, 400, 405+y_a4)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 350, '{----------There is no report to show----------}')

            else:
               
                mycanvas.setFont('Helvetica', 10)  

                mycanvas.drawString(110-x_a4, 375+y_a4, 'Items')

                mycanvas.drawString(192-x_a4, 365+y_a4, '1000ml')
                mycanvas.drawString(192+80-x_a4, 365+y_a4, '500ml')
                mycanvas.drawString(272+80-x_a4, 365+y_a4, '250ml')
                mycanvas.drawString(322+80-x_a4, 365+y_a4, '200ml')
                mycanvas.drawString(402+80-x_a4, 365+y_a4, '120ml')
                mycanvas.drawString(472+80-x_a4, 365+y_a4, '5000ml')
                mycanvas.drawString(545+80-x_a4, 375+y_a4, ' TOTAL')
                mycanvas.drawString(545+80-x_a4, 365+y_a4, 'LITTERS')
                mycanvas.setLineWidth(0)

                mycanvas.line(10, 390+y_a4, 585, 390+y_a4)
                mycanvas.line(10, 355+y_a4, 585, 355+y_a4)
                y = 335+y_a4
                y_line = 390+y_a4
                toal_1000 = 0
                toal_500 = 0
                toal_250 = 0
                toal_200 = 0
                toal_150 = 0
                toal_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.setFont('Helvetica', 10)
                   
                    x_1000 = 208+20+10-x_a4+10
                    x_500 = 208+80-x_a4+10
                    x_250 = 300+80-x_a4
                    x_200 = 413+80-x_a4-10
                    x_150 = 465+80-x_a4-10
                    x_5000 = 540+80-x_a4-10
                   
                    x_total_litter_line = 650+80-x_a4-20
                    mycanvas.drawString(105-x_a4, y, str(products))
                    if not products in data_dict["final_results"][data]:
                        pass
                        #                     if products == "TM" or products == "SM" or products == "FCM":
                        #                         y -= 15
                        #                         continue
                        #                     continue
                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                            mycanvas.setFont('Helvetica', 10)
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_1000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_1000 += data_dict["final_results"][data][products][quantity]

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_500 + 23, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_500 += data_dict["final_results"][data][products][quantity]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_250 + 8, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_250 += data_dict["final_results"][data][products][quantity]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_200 + 8 - 40, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_200 += data_dict["final_results"][data][products][quantity]

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_150 + 8 - 18, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_150 += data_dict["final_results"][data][products][quantity]
                                       
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         if data_dict["final_results"][data][products][quantity] != 0 and \
                            #                 data_dict["final_results"][data][products][quantity] != None:
                            #             mycanvas.drawRightString(x_100 -10, y,
                            #                                      str(data_dict["final_results"][data][products][
                            #                                              quantity]))
                            #             toal_100 += data_dict["final_results"][data][products][quantity]
                           

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if data_dict["final_results"][data][products][quantity] != 0 and \
                                            data_dict["final_results"][data][products][quantity] != None:
                                        mycanvas.drawRightString(x_5000 -10, y,
                                                                 str(data_dict["final_results"][data][products][
                                                                         quantity]))
                                        toal_5000 += data_dict["final_results"][data][products][quantity]
                           
                    mycanvas.drawRightString(x_total_litter_line + 8 - 48, y,
                                             str(data_dict["final_results"][data][products]["total"]))
                    grand_total += data_dict["final_results"][data][products]["total"]

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line - 40, y - 15, str(grand_total))
               
                mycanvas.drawRightString(220 + 23-x_a4, y - 15, str(toal_1000))
                mycanvas.drawRightString(220 + 23+80-x_a4, y - 15, str(toal_500))
                mycanvas.drawRightString(285 + 23+80-x_a4, y - 15, str(toal_250))

                mycanvas.drawRightString(365 + 8+80-x_a4, y - 15, str(toal_200))
                mycanvas.drawRightString(480 - 32+80-x_a4, y - 15, str(toal_150))
                mycanvas.drawRightString(530 - 10+70-x_a4, y - 15, str(toal_5000))
                mycanvas.drawString(x_line + 15, y - 15, 'Grand Total')
                mycanvas.line(x_line+10, y, x_line + 525+60, y)
                mycanvas.line(x_line+10, y - 25, x_line + 525+60, y - 25)
                mycanvas.line(x_line+10, y, x_line+10, y - 25)
                mycanvas.line(x_line + 525+60, y, x_line + 525+60, y - 25)

        if data == "total_sale":
            y_a4 -= 25
            x_a4 = 40
            mycanvas.setFont('Helvetica', 14)
            mycanvas.drawCentredString(300, 185+y_a4, 'Daily Union Report : Total Sales')
            mycanvas.line(200, 180+y_a4, 400, 180+y_a4)
            if data_dict["final_results"][data] == {}:
                mycanvas.drawCentredString(300, 130, '{----------There is no report to show----------}')
            else:
                # Table Header
                mycanvas.setLineWidth(0)
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica', 10)

                mycanvas.drawString(15, 140+y_a4, 'Items')

                mycanvas.drawString(105-x_a4, 140+y_a4, '1000ml')
                mycanvas.drawString(100-x_a4, 130+y_a4, '  Cash')
               
                mycanvas.drawString(105+80-x_a4-10-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(100+80-x_a4-10-10-10, 130+y_a4, '  Cash')

                mycanvas.drawString(200+60-x_a4-20-10-10, 140+y_a4, '500ml')
                mycanvas.drawString(195+60-x_a4-20-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(270+60-x_a4-30-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(265+60-x_a4-30-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(340+60-x_a4-40-10-10, 140+y_a4, '250ml')
                mycanvas.drawString(335+60-x_a4-40-10-10, 130+y_a4, ' Card')

                mycanvas.drawString(410+60-x_a4-50-10-10, 140+y_a4, '200ml')
                mycanvas.drawString(405+60-x_a4-50-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(480+60-x_a4-60-10-10, 140+y_a4, '120ml')
                mycanvas.drawString(475+60-x_a4-60-10-10, 130+y_a4, ' Cash')

                mycanvas.drawString(545+60-x_a4-70-10-10, 140+y_a4, '5000ml')
                mycanvas.drawString(540+60-x_a4-70-10-10, 130+y_a4, ' Cash')

                mycanvas.line(10, 155+y_a4, 585, 155+y_a4)
                mycanvas.line(10, 120+y_a4, 585, 120+y_a4)

                mycanvas.drawString(620+60-x_a4-80-10-10, 140+y_a4, ' TOTAL')
                mycanvas.drawString(620+60-x_a4-80-10-10, 130+y_a4, 'LITTERS')

                y = 100+y_a4
                y_line = 155+y_a4
                x_line = 30

                # -----------------------------------------------------------------------------------------------------------------------------------------#

                # lines#
                mycanvas.line(x_line + 5-25, y_line, x_line + 5-25, y_line - 205)
                mycanvas.line(x_line + 75-50, y_line, x_line + 75-50, y_line - 205)
               
                mycanvas.line(x_line + 145-70, y_line, x_line + 145-70, y_line - 205)
                mycanvas.line(x_line + 145+80-100, y_line, x_line + 145+80-100, y_line - 205)
                mycanvas.line(x_line + 215+80-110, y_line, x_line + 215+80-110, y_line - 205)
                mycanvas.line(x_line + 285+80-120, y_line, x_line + 285+80-120, y_line - 205)
                mycanvas.line(x_line + 355+80-130, y_line, x_line + 355+80-130, y_line - 205)
                mycanvas.line(x_line + 425+80-140, y_line, x_line + 425+80-140, y_line - 205)
                mycanvas.line(x_line + 495+80-150, y_line, x_line + 495+80-150, y_line - 205)
                mycanvas.line(x_line + 565+80-160, y_line, x_line + 565+80-160, y_line - 205)
                mycanvas.line(x_line + 650+80-175, y_line, x_line + 650+80-175, y_line - 205)
                #             mycanvas.line(x_line+660,y_line,x_line+660,y_line-107)

                y_line -= 50
                mycanvas.setFont('Helvetica', 8)
                total_1000 = 0
                total_500_cash = 0
                total_500_card = 0
                total_250_cash = 0
                total_250_card = 0
                total_200 = 0
                total_150 = 0
                total_5000 = 0
                grand_total = 0
                for products in products_list:
                    mycanvas.drawString(15, y, str(products))
                    total_litter_line = 0
                    x_1000 = 180+20-70
                    x_500 = 180+80-97
                    x_250 = 280+80-117
                    x_200 = 380+80 - 137
                    x_150 = 430+80 - 147
                    x_5000 = 620+80 - 157
                    x_total_litter_line = 610 - 172

                    if not products in data_dict["final_results"][data]:
                        pass
                    #                     if products == "TM" or products == "SM" or products == "FCM":
                    #                         y -= 15
                    #                         continue
                    #                     continue

                    if products in data_dict["final_results"][data]:
                        for quantity in quantity_list:
                           
                            if quantity == "1000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_1000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_1000 += data_dict["final_results"][data][products][quantity][
                                                    types]
                                               

                            if quantity == "500":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        if types == "card":
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        mycanvas.drawRightString(x_500 - 10 + x_adjust, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        x_500 += 50
                                                        x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        if quantity in data_dict["final_results"][data][products].keys():
                                            for types in data_dict["final_results"][data][products][quantity]:
                                                if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                        data_dict["final_results"][data][products][quantity][
                                                            types] != None:
                                                    if types == "total":
                                                        total_litter_line += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        if types == "cash":
                                                            mycanvas.drawRightString(x_500, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_cash += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]
                                                        else:
                                                            x_500 += 50
                                                            mycanvas.drawRightString(x_500 + 40, y, str(
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]))
                                                            total_500_card += \
                                                                data_dict["final_results"][data][products][quantity][
                                                                    types]

                            if quantity == "250":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    if len(data_dict["final_results"][data][products][quantity]) == 3:
                                        x_adjust = 0
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    if types == "card":
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    mycanvas.drawRightString(x_250 + 30 + x_adjust, y, str(
                                                        data_dict["final_results"][data][products][quantity][types]))
                                                    x_250 += 50
                                                    x_adjust = 10

                                    if len(data_dict["final_results"][data][products][quantity]) == 2:
                                        for types in data_dict["final_results"][data][products][quantity]:
                                            if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                    data_dict["final_results"][data][products][quantity][types] != None:
                                                if types == "total":
                                                    total_litter_line += \
                                                        data_dict["final_results"][data][products][quantity][types]
                                                else:
                                                    if types == "cash":
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_cash += \
                                                            data_dict["final_results"][data][products][quantity][types]
                                                    else:
                                                        x_250 += 50
                                                        mycanvas.drawRightString(x_250 + 30, y, str(
                                                            data_dict["final_results"][data][products][quantity][
                                                                types]))
                                                        total_250_card += \
                                                            data_dict["final_results"][data][products][quantity][types]

                            if quantity == "200":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_200 + 70, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_200 += data_dict["final_results"][data][products][quantity][types]
                                                x_200 += 50

                            if quantity == "120":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:

                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_150 + 90, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_150 += data_dict["final_results"][data][products][quantity][types]
                                                x_150 += 50
                                               
                            # if quantity == "100":
                            #     if quantity in data_dict["final_results"][data][products].keys():
                            #         for types in data_dict["final_results"][data][products][quantity]:
                            #             if data_dict["final_results"][data][products][quantity][types] != 0 and \
                            #                     data_dict["final_results"][data][products][quantity][types] != None:
                            #                 if types == "total":
                            #                     total_litter_line += \
                            #                     data_dict["final_results"][data][products][quantity][
                            #                         types]
                            #                 else:
                            #                     mycanvas.drawRightString(x_100 - 30, y, str(
                            #                         data_dict["final_results"][data][products][quantity][types]))
                            #                     total_100 += data_dict["final_results"][data][products][quantity][
                            #                         types]

                            if quantity == "5000":
                                if quantity in data_dict["final_results"][data][products].keys():
                                    for types in data_dict["final_results"][data][products][quantity]:
                                        if data_dict["final_results"][data][products][quantity][types] != 0 and \
                                                data_dict["final_results"][data][products][quantity][types] != None:
                                            if types == "total":
                                                total_litter_line += \
                                                data_dict["final_results"][data][products][quantity][
                                                    types]
                                            else:
                                                mycanvas.drawRightString(x_5000 - 30, y, str(
                                                    data_dict["final_results"][data][products][quantity][types]))
                                                total_5000 += data_dict["final_results"][data][products][quantity][
                                                    types]

                    mycanvas.drawRightString(x_total_litter_line + 65+80, y, str(total_litter_line))
                    grand_total += total_litter_line

                    y -= 15
                mycanvas.drawRightString(x_total_litter_line + 65+80, y - 5, str(grand_total))
                mycanvas.drawRightString(x_total_litter_line - 90+105, y - 5, str(total_150))
                mycanvas.drawRightString(x_total_litter_line - 160+115, y - 5, str(total_200))
                mycanvas.drawRightString(x_total_litter_line - 230+125, y - 5, str(total_250_card))
                mycanvas.drawRightString(x_total_litter_line - 300+135, y - 5, str(total_250_cash))
                mycanvas.drawRightString(x_total_litter_line - 370+145, y - 5, str(total_500_card))
                mycanvas.drawRightString(x_total_litter_line - 440+155, y - 5, str(total_500_cash))
                mycanvas.drawRightString(x_total_litter_line - 20+95, y - 5, str(total_5000))
                mycanvas.drawRightString(x_total_litter_line - 335, y - 5, str(total_1000))
                mycanvas.drawRightString(x_total_litter_line - 385, y - 5, "Grand Total")
                #             grand_total += data_dict[data]["products_total"]
                #             mycanvas.drawRightString(x_total_litter_line+75,y+10,str(data_dict[data]["products_total"]))
                #             y -= 10
                mycanvas.line(10, y + 8, 585, y + 8)
                mycanvas.line(10, y - 15, 585, y - 15)
               
    mycanvas.setFont('Times-Italic', 12)      
    indian = pytz.timezone('Asia/Kolkata')          
    mycanvas.drawRightString(585, 5,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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



def serve_zone_wise_abstract_pdf(date, user_name):
    zone_dict = {}
    zone_obj = list(Zone.objects.all().values_list('id', flat=True))
    for zone in zone_obj:
        if not zone in zone_dict:
            zone_dict[zone] = {
                'mor': {
                    'milk_total': 0,
                    'curd_total': 0,
                    'butter_milk_total': 0
                },
                'eve': {
                    'milk_total': 0,
                    'curd_total': 0,
                    'butter_milk_total': 0
                }
            }

        zone_wise_sale_morning = DailySessionllyZonallySale.objects.filter(zone_id=zone, delivery_date=date,
                                                                           session_id=1)
        zone_wise_sale_evening = DailySessionllyZonallySale.objects.filter(zone_id=zone, delivery_date=date,
                                                                           session_id=2)

        if zone_wise_sale_morning:
            zone_dict[zone]["mor"]['milk_total'] += zone_wise_sale_morning.aggregate(Sum('tm500_litre'))[
                                                        'tm500_litre__sum'] + \
                                                    zone_wise_sale_morning.aggregate(Sum("std250_litre"))[
                                                        "std250_litre__sum"] + \
                                                    zone_wise_sale_morning.aggregate(Sum("std500_litre"))[
                                                        "std500_litre__sum"] + \
                                                    zone_wise_sale_morning.aggregate(Sum("fcm500_litre"))[
                                                        "fcm500_litre__sum"] + \
                                                    zone_wise_sale_morning.aggregate(Sum("fcm1000_litre"))[
                                                        "fcm1000_litre__sum"] + \
                                                    zone_wise_sale_morning.aggregate(Sum("smcan_litre"))[
                                                        "smcan_litre__sum"] + \
                                                    zone_wise_sale_morning.aggregate(Sum("fcmcan_litre"))[
                                                        "fcmcan_litre__sum"] + \
                                                    zone_wise_sale_morning.aggregate(Sum("tea500_litre"))[
                                                        "tea500_litre__sum"] + \
                                                    zone_wise_sale_morning.aggregate(Sum("tea1000_litre"))[
                                                        "tea1000_litre__sum"]
            zone_dict[zone]["mor"]['curd_total'] += zone_wise_sale_morning.aggregate(Sum('curd500_kgs'))[
                                                        'curd500_kgs__sum'] + \
                                                    zone_wise_sale_morning.aggregate(Sum('curd150_kgs'))[
                                                        'curd150_kgs__sum'] + \
                                                    zone_wise_sale_morning.aggregate(Sum('curd5000_kgs'))[
                                                        'curd5000_kgs__sum'] + \
                                                    zone_wise_sale_morning.aggregate(Sum('cupcurd_kgs'))[
                                                        'cupcurd_kgs__sum']
            zone_dict[zone]["mor"]['butter_milk_total'] += zone_wise_sale_morning.aggregate(Sum('buttermilk200_litre'))[
                'buttermilk200_litre__sum'] + zone_wise_sale_morning.aggregate(Sum('bm_jar200_litre'))[
                'bm_jar200_litre__sum'] + zone_wise_sale_morning.aggregate(Sum('bmjf200_litre'))[
                'bmjf200_litre__sum']
            print(zone_wise_sale_morning.aggregate(Sum('bmjf200_litre'))['bmjf200_litre__sum'])
        if zone_wise_sale_evening:
            zone_dict[zone]['eve']['milk_total'] += zone_wise_sale_evening.aggregate(Sum('tm500_litre'))[
                                                        'tm500_litre__sum'] + \
                                                    zone_wise_sale_evening.aggregate(Sum("std250_litre"))[
                                                        "std250_litre__sum"] + \
                                                    zone_wise_sale_evening.aggregate(Sum("std500_litre"))[
                                                        "std500_litre__sum"] + \
                                                    zone_wise_sale_evening.aggregate(Sum("fcm500_litre"))[
                                                        "fcm500_litre__sum"] + \
                                                    zone_wise_sale_evening.aggregate(Sum("fcm1000_litre"))[
                                                        "fcm1000_litre__sum"] + \
                                                    zone_wise_sale_evening.aggregate(Sum("smcan_litre"))[
                                                        "smcan_litre__sum"] + \
                                                    zone_wise_sale_evening.aggregate(Sum("fcmcan_litre"))[
                                                        "fcmcan_litre__sum"] + \
                                                    zone_wise_sale_evening.aggregate(Sum("tea500_litre"))[
                                                        "tea500_litre__sum"] + \
                                                    zone_wise_sale_evening.aggregate(Sum("tea1000_litre"))[
                                                        "tea1000_litre__sum"]
            zone_dict[zone]['eve']['curd_total'] += zone_wise_sale_evening.aggregate(Sum('curd500_kgs'))[
                                                        'curd500_kgs__sum'] + \
                                                    zone_wise_sale_evening.aggregate(Sum('curd150_kgs'))[
                                                        'curd150_kgs__sum'] + \
                                                    zone_wise_sale_evening.aggregate(Sum('curd5000_kgs'))[
                                                        'curd5000_kgs__sum'] + \
                                                    zone_wise_sale_evening.aggregate(Sum('cupcurd_kgs'))[
                                                        'cupcurd_kgs__sum']
            zone_dict
            zone_dict[zone]['eve']['butter_milk_total'] += zone_wise_sale_evening.aggregate(Sum('buttermilk200_litre'))[
                'buttermilk200_litre__sum']+ zone_wise_sale_evening.aggregate(Sum('bm_jar200_litre'))[
                'bm_jar200_litre__sum'] + zone_wise_sale_evening.aggregate(Sum('bmjf200_litre'))[
                'bmjf200_litre__sum']


    data = generate_pdf_for_unique_zone_wise_sale_details(zone_dict, user_name, date)
    return data

    
def generate_pdf_for_unique_zone_wise_sale_details(zone_dict, user_name, date):
    file_name = str(date) + '_zone_sale_abstract' + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
#     file_path = os.path.join('static/media/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))

    light_color = 0x000000
    dark_color = 0x000000
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFillColor(HexColor(dark_color))

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 775,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 755, 'ZONE WISE SALES ABSTRACT REPORT: MILK')
    mycanvas.line(170, 752, 430, 752)

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(40, 715, 'Date : ')
    mycanvas.setFillColor(HexColor(dark_color))
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    date = datetime.datetime.strftime(date, '%d-%m-%Y')
    mycanvas.drawString(60 + 20, 715, str(date))

    # table
    mycanvas.line(40, 690, 560, 690)
    mycanvas.line(40, 660, 560, 660)
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(100, 675, 'Zone')
    mycanvas.drawCentredString(360-120, 680, 'Morning')
    mycanvas.drawCentredString(360-120, 665, 'Milk Total (litre)')
    mycanvas.drawCentredString(480-120, 680, 'Evening')
    mycanvas.drawCentredString(480-120, 665, 'Milk Total (litre)')
    mycanvas.drawCentredString(610-120, 680, 'Total')
    mycanvas.drawCentredString(610-120, 665, 'Milk (litre)')

    mycanvas.setFont('Helvetica', 14)

    initial_y_axis = 630
    mor_total = 0
    eve_total = 0
    overall_total = 0
    for zone in zone_dict:
        mycanvas.drawString(60, initial_y_axis, str(Zone.objects.get(id=zone).name))
        #         if not route_with_quantity_dict[route['mor_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(410-120, initial_y_axis,
                                 str(zone_dict[zone]['mor']['milk_total']))
        mor_total += zone_dict[zone]['mor']['milk_total']
        #         if not route_with_quantity_dict[route['eve_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(530-120, initial_y_axis,
                                 str(zone_dict[zone]['eve']['milk_total']))
        eve_total += zone_dict[zone]['eve']['milk_total']
        total = zone_dict[zone]['mor']['milk_total'] + \
                zone_dict[zone]['eve']['milk_total']

        #         if not total == 0:
        mycanvas.drawRightString(670-120, initial_y_axis, str(total))
        overall_total += total
        initial_y_axis -= 25

    mycanvas.drawRightString(410-120, initial_y_axis - 12, str(mor_total))
    mycanvas.drawRightString(530-120, initial_y_axis - 12, str(eve_total))
    mycanvas.drawRightString(670-120, initial_y_axis - 12, str(overall_total))

    mycanvas.line(40, initial_y_axis + 10, 680-120, initial_y_axis + 10)
    mycanvas.line(40, initial_y_axis - 20, 680-120, initial_y_axis - 20)
    mycanvas.setFont('Helvetica', 14)
    mycanvas.drawString(70, initial_y_axis - 40, 'TOTAL LITRE')
    mycanvas.drawRightString(410, initial_y_axis - 40, str(overall_total))

    # draw horizontal line
    mycanvas.line(40, initial_y_axis - 20, 40, 690)
    mycanvas.line(300-120, initial_y_axis - 20, 300-120, 690)
    mycanvas.line(420-120, initial_y_axis - 20, 420-120, 690)
    mycanvas.line(540-120, initial_y_axis - 20, 540-120, 690)
    mycanvas.line(680-120, initial_y_axis - 20, 680-120, 690)
    mycanvas.showPage()

    # Next page for curd products
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 775,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 755, 'ZONE WISE SALES ABSTRACT REPORT: CURD')
    mycanvas.line(170, 752, 430, 752)

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(40, 715, 'Date : ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(60 + 20, 715, str(date))

    # table
    mycanvas.line(40, 690, 680-120, 690)
    mycanvas.line(40, 660, 680-120, 660)
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(100, 675, 'Zone')
    mycanvas.drawCentredString(360-120, 680, 'Morning')
    mycanvas.drawCentredString(360-120, 665, 'Curd Total (Kgs)')
    mycanvas.drawCentredString(480-120, 680, 'Evening')
    mycanvas.drawCentredString(480-120, 665, 'Curd Total (Kgs)')
    mycanvas.drawCentredString(610-120, 680, 'Total')
    mycanvas.drawCentredString(610-120, 665, 'Curd (Kgs)')

    mycanvas.setFont('Helvetica', 14)

    initial_y_axis = 640
    mor_total = 0
    eve_total = 0
    overall_total = 0
    for zone in zone_dict:
        mycanvas.drawString(60, initial_y_axis, str(Zone.objects.get(id=zone).name))
        #         if not route_with_quantity_dict[route['mor_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(410-120, initial_y_axis,
                                 str(zone_dict[zone]['mor']['curd_total']))
        mor_total += zone_dict[zone]['mor']['curd_total']
        #         if not route_with_quantity_dict[route['eve_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(530-120, initial_y_axis,
                                 str(zone_dict[zone]['eve']['curd_total']))
        eve_total += zone_dict[zone]['eve']['curd_total']
        total = zone_dict[zone]['mor']['curd_total'] + \
                zone_dict[zone]['eve']['curd_total']

        #         if not total == 0:
        mycanvas.drawRightString(670-120, initial_y_axis, str(total))
        overall_total += total
        initial_y_axis -= 25

    mycanvas.drawRightString(410-120, initial_y_axis - 12, str(mor_total))
    mycanvas.drawRightString(530-120, initial_y_axis - 12, str(eve_total))
    mycanvas.drawRightString(670-120, initial_y_axis - 12, str(overall_total))

    mycanvas.line(40, initial_y_axis + 10, 680-120, initial_y_axis + 10)
    mycanvas.line(40, initial_y_axis - 20, 680-120, initial_y_axis - 20)
    mycanvas.setFont('Helvetica', 14)
    mycanvas.drawString(70, initial_y_axis - 40, 'TOTAL LITRE')
    mycanvas.drawRightString(410, initial_y_axis - 40, str(overall_total))

    mycanvas.line(40, initial_y_axis - 20, 40, 690)
    mycanvas.line(300-120, initial_y_axis - 20, 300-120, 690)
    mycanvas.line(420-120, initial_y_axis - 20, 420-120, 690)
    mycanvas.line(540-120, initial_y_axis - 20, 540-120, 690)
    mycanvas.line(680-120, initial_y_axis - 20, 680-120, 690)
    mycanvas.showPage()

    # Next page for Butter milk products
    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 775,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawCentredString(300, 755, 'ZONE WISE SALES ABSTRACT REPORT: BUTTER MILK')
    mycanvas.line(170, 752, 430, 752)

    mycanvas.setFillColor(HexColor(light_color))
    mycanvas.drawString(40, 715, 'Date : ')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.drawString(60 + 20, 715, str(date))

    # table
    mycanvas.line(40, 690, 680-120, 690)
    mycanvas.line(40, 660, 680-120, 660)
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(100, 675, 'Zone')
    mycanvas.drawCentredString(360-120, 680, 'Morning')
    mycanvas.drawCentredString(480-120, 680, 'Evening')
    mycanvas.drawCentredString(610-120, 680, 'Total')

    mycanvas.setFont('Helvetica', 9)
    mycanvas.drawCentredString(360-120, 665, 'Butter Milk Total (litre)')
    mycanvas.drawCentredString(480-120, 665, 'Butter Milk Total (litre)')
    mycanvas.drawCentredString(610-120, 665, 'Butter Milk (litre)')

    mycanvas.setFont('Helvetica', 14)

    initial_y_axis = 640
    mor_total = 0
    eve_total = 0
    overall_total = 0
    for zone in zone_dict:
        mycanvas.drawString(60, initial_y_axis, str(Zone.objects.get(id=zone).name))
        #         if not route_with_quantity_dict[route['mor_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(410-120, initial_y_axis,
                                 str(zone_dict[zone]['mor']['butter_milk_total']))
        mor_total += zone_dict[zone]['mor']['butter_milk_total']
        #         if not route_with_quantity_dict[route['eve_route_id']]['milk_total'] == 0:
        mycanvas.drawRightString(530-120, initial_y_axis,
                                 str(zone_dict[zone]['eve']['butter_milk_total']))
        eve_total += zone_dict[zone]['eve']['butter_milk_total']
        total = zone_dict[zone]['mor']['butter_milk_total'] + \
                zone_dict[zone]['eve']['butter_milk_total']

        #         if not total == 0:
        mycanvas.drawRightString(670-120, initial_y_axis, str(total))
        overall_total += total
        initial_y_axis -= 25

    mycanvas.drawRightString(410-120, initial_y_axis - 12, str(mor_total))
    mycanvas.drawRightString(530-120, initial_y_axis - 12, str(eve_total))
    mycanvas.drawRightString(670-120, initial_y_axis - 12, str(overall_total))

    mycanvas.line(40, initial_y_axis + 10, 680-120, initial_y_axis + 10)
    mycanvas.line(40, initial_y_axis - 20, 680-120, initial_y_axis - 20)
    mycanvas.setFont('Helvetica', 14)
    mycanvas.drawString(70, initial_y_axis - 40, 'TOTAL LITRE')
    mycanvas.drawRightString(410-120, initial_y_axis - 40, str(overall_total))

    mycanvas.line(40, initial_y_axis - 20, 40, 690)
    mycanvas.line(300-120, initial_y_axis - 20, 300-120, 690)
    mycanvas.line(420-120, initial_y_axis - 20, 420-120, 690)
    mycanvas.line(540-120, initial_y_axis - 20, 540-120, 690)
    mycanvas.line(680-120, initial_y_axis - 20, 680-120, 690)
   
    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawString(340, 10,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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


def serve_zone_wise_route_abstract_for_selected_date(date, user_name):
    data_dict = {}
    zone_dict = {}
    overall_total = 0
    for zone in Zone.objects.filter():
        zone_wise_total = 0
        if DailySessionllyBusinessllySale.objects.filter(delivery_date=date, zone=zone).exists():
            if not zone.id in zone_dict:
                zone_dict[zone.id] = {}
                zone_dict[zone.id]['route_wise'] = {}
                zone_dict[zone.id]['session_wise_total'] = {}
                zone_dict[zone.id]['total'] = {}

            for session in Session.objects.filter():
                session_wise_total = 0
                if not session.id in zone_dict[zone.id]['session_wise_total']:
                    zone_dict[zone.id]['session_wise_total'][session.id] = 0
                route_ids = list(set(list(DailySessionllyBusinessllySale.objects.filter(delivery_date=date, zone=zone,
                                                                                        session=session).values_list(
                    'route', flat=True))))
                for route in Route.objects.filter(id__in=route_ids):
                    if session.id == 1:
                        group_route_id = RouteGroupMap.objects.get(mor_route=route).id
                    if session.id == 2:
                        group_route_id = RouteGroupMap.objects.get(eve_route=route).id
                    if not group_route_id in zone_dict[zone.id]['route_wise']:
                        zone_dict[zone.id]['route_wise'][group_route_id] = {}
                    if not session.id in zone_dict[zone.id]['route_wise'][group_route_id]:
                        zone_dict[zone.id]['route_wise'][group_route_id][session.id] = {}
                    if not route.id in zone_dict[zone.id]['route_wise'][group_route_id][session.id]:
                        zone_dict[zone.id]['route_wise'][group_route_id][session.id][route.id] = 0
                    dsbs_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date=date, route=route, zone=zone,
                                                                             session=session)
                    #               + dsbs_obj.aggregate(Sum('curd500_kgs'))['curd500_kgs__sum'] + dsbs_obj.aggregate(Sum('curd150_kgs'))['curd150_kgs__sum'] + dsbs_obj.aggregate(Sum('cupcurd_kgs'))['cupcurd_kgs__sum'] + dsbs_obj.aggregate(Sum('curd_bucket_kgs'))['curd_bucket_kgs__sum'] + dsbs_obj.aggregate(Sum('lassi200_kgs'))['lassi200_kgs__sum'] + dsbs_obj.aggregate(Sum('buttermilk200_litre'))['buttermilk200_litre__sum']
                    total_sale_in_litre = dsbs_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('std250_litre'))['std250_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('std500_litre'))['std500_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('fcm500_litre'))['fcm500_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('fcm1000_litre'))['fcm1000_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('tea500_litre'))['tea500_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('tea1000_litre'))['tea1000_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('tmcan_litre'))['tmcan_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('smcan_litre'))['smcan_litre__sum'] + \
                                          dsbs_obj.aggregate(Sum('fcmcan_litre'))['fcmcan_litre__sum']
                    zone_dict[zone.id]['route_wise'][group_route_id][session.id][route.id] = total_sale_in_litre
                    session_wise_total += total_sale_in_litre
                zone_dict[zone.id]['session_wise_total'][session.id] = session_wise_total
                zone_wise_total += session_wise_total
            zone_dict[zone.id]['total'] = zone_wise_total
            overall_total += zone_wise_total
    #             total_litre =
    # print(overall_total)
    route_group_obj = RouteGroupMap.objects.filter()
    route_group_list = list(
        route_group_obj.values_list('id', 'full_name', 'name', 'mor_route_id', 'eve_route_id', 'mor_route__name',
                                    'eve_route__name'))
    route_group_column = ['id', 'full_name', 'name', 'mor_route_id', 'eve_route_id', 'mor_route_name', 'eve_route_name']
    route_group_df = pd.DataFrame(route_group_list, columns=route_group_column)
    data_dict = {
        'route_group_dict': route_group_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict(),
        'zone_dict': zone_dict,
        'grand_total': overall_total
    }
    data = generate_pdf_for_zone_wise_route_report(data_dict, user_name, date)
    return data


def generate_pdf_for_zone_wise_route_report(data_dict, user_name, date):
    file_name = str(date) + '_zone_wise_route_abstract_report' + '.pdf'
#     file_path = os.path.join('static/media', file_name)
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
#     pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))
    light_color = 0x9b9999
    dark_color = 0x000000
    x_adjust = 30
    y_a4 = 30
#     mycanvas.setDash(1, 6)
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawString(15, 775,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.setFillColor(HexColor(dark_color))
    date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
    date = datetime.datetime.strftime(date_in_format, '%d-%m-%Y')
    mycanvas.drawCentredString(300, 755, 'ZONE WISE SALES ABSTRACT REPORT: MILK ( '+str(date)+" )")
#     mycanvas.line(170, 752, 430, 752)

    #     table part
    mycanvas.line(40-x_adjust, 680+y_a4, 680-x_adjust-65, 680+y_a4)
    mycanvas.line(40-x_adjust, 650+y_a4, 680-x_adjust-65, 650+y_a4)
    mycanvas.drawString(50-x_adjust, 660+y_a4, 'Zone ')
    mycanvas.line(120-x_adjust, 650+y_a4, 120-x_adjust, 680+y_a4)
    mycanvas.drawCentredString(160-x_adjust, 660+y_a4, 'Route ')
    mycanvas.line(330-x_adjust, 650+y_a4, 330-x_adjust, 680+y_a4)
    mycanvas.drawString(370-x_adjust-10, 660+y_a4, 'Mor.Qty ')
    mycanvas.line(450-x_adjust-20, 650+y_a4, 450-x_adjust-20, 680+y_a4)
    mycanvas.drawString(480-x_adjust-25, 660+y_a4, 'Eve.Qty ')
    mycanvas.line(550-x_adjust-30, 650+y_a4, 550-x_adjust-30, 680+y_a4)
    mycanvas.drawString(600-x_adjust-45, 660+y_a4, 'Total')

    #     table content
    sessions = Session.objects.filter().order_by('id')
    y_start_for_zone_name = 630+y_a4
    for zone in Zone.objects.filter():
        mycanvas.setFont('Helvetica', 10)
        if zone.id in data_dict['zone_dict'].keys():
            if not data_dict['zone_dict'][zone.id]['total'] == 0:
                mycanvas.drawString(50-x_adjust, y_start_for_zone_name, str(zone.name[:8]))
                route_group_list = list(data_dict['zone_dict'][zone.id]['route_wise'].keys())
                for route_group in sorted(route_group_list):
                    mor_route_id = data_dict['route_group_dict'][route_group]['mor_route_id']
                    eve_route_id = data_dict['route_group_dict'][route_group]['eve_route_id']
                    mycanvas.drawString(130-x_adjust, y_start_for_zone_name,
                                        str(data_dict['route_group_dict'][route_group]['full_name']))
                    x_for_session_route_value = 445-x_adjust-30
                    total_for_route_group = 0
                    for session in sessions:
                        if session.id in data_dict['zone_dict'][zone.id]['route_wise'][route_group].keys():
                            if session.id == 1:
                                if mor_route_id in data_dict['zone_dict'][zone.id]['route_wise'][route_group][
                                    session.id].keys():
                                    mycanvas.drawRightString(x_for_session_route_value+10, y_start_for_zone_name, str(
                                        data_dict['zone_dict'][zone.id]['route_wise'][route_group][session.id][
                                            mor_route_id]))
                                    total_for_route_group += \
                                    data_dict['zone_dict'][zone.id]['route_wise'][route_group][session.id][mor_route_id]
                            if session.id == 2:
                                if eve_route_id in data_dict['zone_dict'][zone.id]['route_wise'][route_group][
                                    session.id].keys():
                                    mycanvas.drawRightString(x_for_session_route_value, y_start_for_zone_name, str(
                                        data_dict['zone_dict'][zone.id]['route_wise'][route_group][session.id][
                                            eve_route_id]))
                                    total_for_route_group += \
                                    data_dict['zone_dict'][zone.id]['route_wise'][route_group][session.id][eve_route_id]
                        x_for_session_route_value += 100
                    mycanvas.drawRightString(x_for_session_route_value-5, y_start_for_zone_name,
                                             str(total_for_route_group))

                    y_start_for_zone_name -= 18
                y_start_for_zone_name = y_start_for_zone_name + 10
                mycanvas.line(40-x_adjust, y_start_for_zone_name, 680-x_adjust-65, y_start_for_zone_name)
                mycanvas.drawString(150, y_start_for_zone_name - 15, str('Total Litre'))
                x_for_session_route_value = 445-x_adjust-30
                adjust = 0
                for session in sessions:
                    if session.id in data_dict['zone_dict'][zone.id]['session_wise_total'].keys():
                        mycanvas.drawRightString(x_for_session_route_value+10-adjust, y_start_for_zone_name - 15,
                                                 str(data_dict['zone_dict'][zone.id]['session_wise_total'][session.id]))
                    x_for_session_route_value += 100
                    adjust += 10
                mycanvas.drawRightString(x_for_session_route_value-5, y_start_for_zone_name - 15,
                                         str(data_dict['zone_dict'][zone.id]['total']))
                y_start_for_zone_name = y_start_for_zone_name - 25
                mycanvas.line(40-x_adjust, y_start_for_zone_name, 680-x_adjust-65, y_start_for_zone_name)
                y_start_for_zone_name -= 18
               
                if y_start_for_zone_name < 31:
                    mycanvas.line(40-x_adjust, y_start_for_zone_name + 18, 40-x_adjust, 680+y_a4)
                    mycanvas.line(120-x_adjust, y_start_for_zone_name + 18, 120-x_adjust, 650+y_a4)
                    mycanvas.line(330-x_adjust, y_start_for_zone_name + 18, 330-x_adjust, 650+y_a4)
                    mycanvas.line(450-x_adjust-20, y_start_for_zone_name + 18, 450-x_adjust-20, 650+y_a4)
                    mycanvas.line(550-x_adjust-30, y_start_for_zone_name + 18, 550-x_adjust-30, 650+y_a4)
                    mycanvas.line(680-x_adjust-65, y_start_for_zone_name + 18, 680-x_adjust-65, 680+y_a4)

                    mycanvas.showPage()
#                     mycanvas.setDash(1, 6)

                    mycanvas.setFont('Helvetica', 12.5)
                    mycanvas.drawString(15, 775,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                    mycanvas.setFont('Helvetica', 13)
                    mycanvas.setFillColor(HexColor(dark_color))
                   
                    mycanvas.drawCentredString(300, 755, 'ZONE WISE SALES ABSTRACT REPORT: MILK ( '+str(date)+" )")


                    #     table part
                    mycanvas.line(40-x_adjust, 680+y_a4, 680-x_adjust-65, 680+y_a4)
                    mycanvas.line(40-x_adjust, 650+y_a4, 680-x_adjust-65, 650+y_a4)
                    mycanvas.drawString(50-x_adjust, 660+y_a4, 'Zone ')
                    mycanvas.line(120-x_adjust, 650+y_a4, 120-x_adjust, 680+y_a4)
                    mycanvas.drawCentredString(160-x_adjust, 660+y_a4, 'Route ')
                    mycanvas.line(330-x_adjust, 650+y_a4, 330-x_adjust, 680+y_a4)
                    mycanvas.drawString(370-x_adjust-10, 660+y_a4, 'Mor.Qty ')
                    mycanvas.line(450-x_adjust-20, 650+y_a4, 450-x_adjust-20, 680+y_a4)
                    mycanvas.drawString(480-x_adjust-25, 660+y_a4, 'Eve.Qty ')
                    mycanvas.line(550-x_adjust-30, 650+y_a4, 550-x_adjust-30, 680+y_a4)
                    mycanvas.drawString(600-x_adjust-45, 660+y_a4, 'Total')

                    #     table content
                    y_start_for_zone_name = 630+y_a4
   
    mycanvas.line(40-x_adjust, y_start_for_zone_name + 18, 40-x_adjust, 680+y_a4)
    mycanvas.line(120-x_adjust, y_start_for_zone_name + 18, 120-x_adjust, 650+y_a4)
    mycanvas.line(330-x_adjust, y_start_for_zone_name + 18, 330-x_adjust, 650+y_a4)
    mycanvas.line(450-x_adjust-20, y_start_for_zone_name + 18, 450-x_adjust-20, 650+y_a4)
    mycanvas.line(550-x_adjust-30, y_start_for_zone_name + 18, 550-x_adjust-30, 650+y_a4)
    mycanvas.line(680-x_adjust-65, y_start_for_zone_name + 18, 680-x_adjust-65, 680+y_a4)
    mycanvas.setFont('Helvetica', 16)
    mycanvas.drawString(60-x_adjust, y_start_for_zone_name - 18, 'Net Litre')
    mycanvas.drawRightString(445-x_adjust-30, y_start_for_zone_name - 18, str(data_dict['grand_total']))
   
    indian = pytz.timezone('Asia/Kolkata')
    mycanvas.setFont('Times-Italic', 10)
    mycanvas.drawString(340, 10,'Report Generated by: ' + str(user_name + ", @" + str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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



def generate_customer_card_after_order(customer_code, month, year):
    data_dict = {}
    icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(date__year=year,date__month=month,icustomer__customer_code=customer_code)
    for sale_group in icustomer_sale_group_obj:
        if not sale_group.icustomer_id in data_dict:
            if ICustomerSerialNumberMap.objects.filter(month=month,year=year,icustomer_id=sale_group.icustomer_id).exists():
              serial_number = ICustomerSerialNumberMap.objects.get(month=month,year=year,icustomer_id=sale_group.icustomer_id).serial_number
            else:
              serial_number = 'Online'
            if sale_group.ordered_via_id == 2:
                serial_number_format = 'Z - '
            else:
                serial_number_format = 'O - '
            data_dict[sale_group.icustomer_id] = {
                "card_no" : ICustomerMonthlyOrderTransaction.objects.get(icustomer_id=sale_group.icustomer_id, month=month, year=year).milk_card_number,
                "booth": sale_group.business.code,
                "zone": sale_group.zone.name,
                "zoner_mobile": EmployeeZoneResponsibility.objects.get(zone_id=sale_group.zone_id).employee.user_profile.mobile,
                "customer_name": sale_group.icustomer.user_profile.user.first_name + ' ' +str(sale_group.icustomer.user_profile.user.last_name),
                "customer_id":sale_group.icustomer.customer_code,
                "month": month,
                "year": year,
                "sl_no": serial_number,
                "serial_number_format": serial_number_format,
                "amount": 0,
                "morning":{},
                "evening":{},
                'time_created': sale_group.time_created
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
    document_dict = {
      'without_layout': {},
      'with_layout': {}
    }
    document_dict['old_layout'] = generate_customer_card_with_layout(data_dict,year,month, customer_code)
    document_dict['new_layout'] = generate_customer_card_without_layout(data_dict,year,month, customer_code)
    
    return document_dict


def generate_customer_card_with_layout(data_dict,year,month, customer_code):
    file_name = 'customer_card_with_layout_' + str(customer_code) + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    month = month
    year = year
    days = monthrange(year, month)
    datetime_object = datetime.datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%b")

    y_ad = 10
    y2 = 5
    mycanvas = canvas.Canvas(file_path, pagesize = (6 * inch, 4 * inch))
    for data in data_dict:
        # drawMyRulerForCanvas(mycanvas)
        light_color = 0x9b9999
        dark_color = 0x000000
        mycanvas.setStrokeColor(HexColor(light_color))
        mycanvas.line(8, 270-y2, 422, 270-y2)
        mycanvas.line(59, 257-y2, 410, 257-y2)
        mycanvas.line(8, 240-y2, 422, 240-y2)

        mycanvas.setFont('Helvetica', 12)
        # first side
#         mycanvas.line(8, 270-y2, 8, 240-y2)
#         mycanvas.line(20, 270-y2, 20, 240-y2)
        mycanvas.line(59, 270-y2, 59, 240-y2)

        start_x_for_line = 59
        start_x_for_letter = 40
       
        for i in range(1,10):
            start_x_for_line += 39
            start_x_for_letter += 39
            mycanvas.setFont('Helvetica', 9)
            mycanvas.drawString(start_x_for_letter-15, 260-y2, "M")
            mycanvas.drawString(start_x_for_letter+5, 260-y2, "E")
            mycanvas.line(start_x_for_line-20, 270-y2, start_x_for_line-20, 257-y2)
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(start_x_for_letter, 244-y2, str(i))
            mycanvas.line(start_x_for_line, 270-y2, start_x_for_line, 240-y2)

        #  next side 2nd
        next_start_x_for_letter = start_x_for_letter - 5
        start_y_for_letter = 250-y2
        next_start_y_for_line = 240-y2
        for i in range(10,17):
            start_y_for_letter -=30
            next_start_y_for_line -=30
            if i == 16:
                mycanvas.setFont('Helvetica', 9)
                mycanvas.drawString(next_start_x_for_letter-9, start_y_for_letter-7, "M")
                mycanvas.drawString(next_start_x_for_letter+11, start_y_for_letter-7, "E")
                mycanvas.line(390, next_start_y_for_line+13, 390, next_start_y_for_line)
                mycanvas.setFont('Helvetica', 12)
               
                mycanvas.drawString(next_start_x_for_letter, start_y_for_letter+8, str(i))
            else:
                mycanvas.setFont('Helvetica', 9)
                mycanvas.drawString(next_start_x_for_letter+26, start_y_for_letter+9, "M")
                mycanvas.drawString(next_start_x_for_letter+26, start_y_for_letter-7, "E")
                mycanvas.line(410, next_start_y_for_line+15, 422, next_start_y_for_line+15)
                mycanvas.setFont('Helvetica', 12)
                mycanvas.drawString(next_start_x_for_letter, start_y_for_letter, str(i))
            mycanvas.line(371, next_start_y_for_line, 422, next_start_y_for_line)
            if i >= 12 and i <= 15:
                mycanvas.line(59, next_start_y_for_line, 371, next_start_y_for_line)
               
        mycanvas.line(422, 270-y2, 422, next_start_y_for_line)
        mycanvas.line(410, 240-y2, 410, next_start_y_for_line)
        mycanvas.line(371, 240-y2, 371, next_start_y_for_line)

        # next side 3rd
        next_start_x_for_line = 371
        for i in range(17,26):
            next_start_x_for_line -= 39
            next_start_x_for_letter -= 39
           
            mycanvas.setFont('Helvetica', 9)
            mycanvas.drawString(next_start_x_for_line+8, next_start_y_for_line+3, "M")
            mycanvas.drawString(next_start_x_for_line+27, next_start_y_for_line+3, "E")
            mycanvas.line(next_start_x_for_line+20, next_start_y_for_line+13, next_start_x_for_line+20, next_start_y_for_line)
            mycanvas.setFont('Helvetica', 12)
           
            mycanvas.drawString(next_start_x_for_letter, next_start_y_for_line + 18, str(i))
            mycanvas.line(next_start_x_for_line, next_start_y_for_line + 30, next_start_x_for_line, next_start_y_for_line)
        mycanvas.line(8, next_start_y_for_line, 371, next_start_y_for_line)
        mycanvas.line(20, next_start_y_for_line+13, 410, next_start_y_for_line+13)
       

        # final side
        next_start_y_for_letter = next_start_y_for_line + 8
        next_start_y_for_line = next_start_y_for_line + 30
        mycanvas.line(59, 240-y2, 59, next_start_y_for_line)
        mycanvas.line(20, 240-y2, 20, next_start_y_for_line)
        mycanvas.line(8, 270-y2, 8, next_start_y_for_line-30)
       
       
        for i in range(26,days[1]+1):
            mycanvas.line(8, next_start_y_for_line+15, 20, next_start_y_for_line+15)
            mycanvas.line(8, next_start_y_for_line, 59, next_start_y_for_line)
            next_start_y_for_line +=30

        product_list = []
       
        for products in data_dict[data]["morning"]:
            product_list.append(products)
        for products in data_dict[data]["evening"]:
            product_list.append(products)
           
        product_list = set(product_list)
        product_list = list(product_list)
       
        for i in range(26, days[1]+1):
            next_start_y_for_letter += 30
           
            mycanvas.setFont('Helvetica', 9)
            mycanvas.drawString(next_start_x_for_letter-25, next_start_y_for_letter+11, "M")
            mycanvas.drawString(next_start_x_for_letter-25, next_start_y_for_letter-5, "E")
           
            mycanvas.setFont('Helvetica', 12)
           
            mycanvas.drawString(35, next_start_y_for_letter, str(i))

            if i == 28:
                mycanvas.setFont('Helvetica', 8)
                mycanvas.setFillColor(HexColor(light_color))
                mycanvas.drawString(66, next_start_y_for_letter + 3, 'Milk Type')
                mycanvas.setFillColor(HexColor(dark_color))
                product_start_position = 66

                for product in product_list:
                    product_start_position +=51
                    mycanvas.drawString(product_start_position, next_start_y_for_letter + 3, str(product))
            if i == 27:
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawString(68, next_start_y_for_letter + 3, 'Morning')
                product_start_position = 66
                for product in product_list:
                    product_start_position += 55
                    if product in data_dict[data]["morning"]:
                        mycanvas.drawString(product_start_position, next_start_y_for_letter + 3, str(int(data_dict[data]["morning"][product])))
                    else:
                        mycanvas.setFillColor(HexColor(light_color))
                        mycanvas.drawString(product_start_position, next_start_y_for_letter + 3, '-')
                        mycanvas.setFillColor(HexColor(dark_color))

            if i == 26:
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawString(68, next_start_y_for_letter + 3, 'Evening')
                product_start_position = 66
                for product in product_list:
                    product_start_position += 55
                    if product in data_dict[data]["evening"]:
                        mycanvas.drawString(product_start_position, next_start_y_for_letter + 3, str(int(data_dict[data]["evening"][product])))
                    else:
                        mycanvas.setFillColor(HexColor(light_color))
                        mycanvas.drawString(product_start_position, next_start_y_for_letter + 3, '-')
                        mycanvas.setFillColor(HexColor(dark_color))

            mycanvas.setFont('Helvetica', 13)
        mycanvas.setFont('Helvetica', 7)
        start_x_for_product_verticle_line = 59
        for i in range(1,6):
            start_x_for_product_verticle_line += 52
            mycanvas.line(start_x_for_product_verticle_line, 150-y2, start_x_for_product_verticle_line, 60-y2)
       
       
        mycanvas.setFont('Helvetica', 7)
        mycanvas.drawCentredString(210, 232-y2, 'The Coimbatore District Co-Operative Milk Producers Union Ltd')
        mycanvas.drawCentredString(210, 224-y2,"Pachapalayam, Coimbatore - 641 010.")
       
        mycanvas.setFont('Helvetica-Bold', 6)
        mycanvas.drawCentredString(210, 216-y2, 'CUSTOMER MONTHLY MILK CARD')
       
        mycanvas.setFont('Helvetica', 8)
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(62, 225-y_ad-15-y2, 'Card No:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(105-10, 225-y_ad-15-y2, str(data_dict[data]['card_no']))

        mycanvas.setFont('Helvetica', 8)
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(180, 225-y_ad-15-y2, 'Booth:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(180+30, 225-y_ad-15-y2, str(data_dict[data]['booth']))

        mycanvas.setFont('Helvetica', 8)
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(250+30, 225-y_ad-15-y2, 'Sl No:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(280+30, 225-y_ad-15-y2, str(data_dict[data]["sl_no"]))

        mycanvas.setFont('Helvetica', 8)
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(180, 185-y_ad-5-y2, 'Customer Code:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(305-60, 185-y_ad-5-y2, str(data_dict[data]["customer_id"]))

        # second line of content
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(62, 205-y_ad-10-y2, 'Zone:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(100-10, 205-y_ad-10-y2, str(data_dict[data]['zone']))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(180, 205-y_ad-10-y2, 'Zone Officer Mobile:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(300-40, 205-y_ad-10-y2, str(data_dict[data]["zoner_mobile"]))

        # Third line of content
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(62, 185-y_ad-5-y2, 'Name:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(100-10, 185-y_ad-5-y2, str(data_dict[data]["customer_name"])[:17])
        mycanvas.setFont('Helvetica', 8)

        # Fourth line of content
        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(62, 165-y_ad-y2, 'Month:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(100-10, 165-y_ad-y2, str(month_name)[:3]+' - '+ str(year)+ " (" +str(days[1])+" Days"+") ")

        mycanvas.setFillColor(HexColor(light_color))
        mycanvas.drawString(180, 165-y_ad-y2, 'Amount:')
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(220-5, 165-y_ad-y2, str(data_dict[data]["amount"]))
       
        mycanvas.setFont('Helvetica', 6)
        mycanvas.drawString(330, 165-y_ad-y2-1, 'Signature')

    #     mycanvas.drawString(180, 165, '')
        mycanvas.setFont('Helvetica', 8)
        mycanvas.showPage()
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


def generate_customer_card_without_layout(data_dict,year,month, customer_code):
    file_name = 'customer_card_without_layout_' + str(customer_code) + '.pdf'
    file_path = os.path.join('static/media/zone_wise_report/', file_name)
    month = month
    year = year
    days = monthrange(year, month)
    datetime_object = datetime.datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%b")

    mycanvas = canvas.Canvas(file_path, pagesize = A4)#(20*inch,20*inch)
    mycanvas.setLineWidth(0)
   
    for data in data_dict:
        y=790

        list1 = ["Validity","Booth","Customer Code","Date"]
        list2 = ["Card No","Sl No","Name","Amount"]

        mycanvas.setFont("Times-Roman", 10)
        for i in range(4):
            #harizonal line
            mycanvas.line(260,y+12,396,y+12) #585
            mycanvas.line(400,y+12,545,y+12)
           
            mycanvas.line(260,y-4,396,y-4)
            mycanvas.line(400,y-4,545,y-4)
           
            mycanvas.line(260,y+12,260,y-4)
            mycanvas.line(332,y+12,332,y-4)
            mycanvas.line(396,y+12,396,y-4)
            mycanvas.line(400,y+12,400,y-4)
            mycanvas.line(442,y+12,442,y-4)
            mycanvas.line(545,y+12,545,y-4)
           
            mycanvas.drawString(265,y,str(list1[i]))
            mycanvas.drawString(405,y,str(list2[i]))
            y -= 20
#         mycanvas.line(300,y+12,585,y+12)

        y = 790
        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawString(335, y, str(month_name) + " - "+str(year))
        mycanvas.drawString(165, y-13, str(data_dict[data]['zone']))
        mycanvas.drawString(335, y-20, str(data_dict[data]['booth']))
        mycanvas.drawString(335, y-40, str(data_dict[data]["customer_id"]))
        # mycanvas.drawString(335, y-60, str(datetime.datetime.now().astimezone(indian).strftime("%d-%m-%Y")))
        mycanvas.drawString(335, y-60, str(data_dict[data]['time_created'].astimezone(timezone('Asia/Kolkata')).strftime("%d-%m-%Y")))




        mycanvas.drawString(445, y, str(data_dict[data]['card_no']))
        mycanvas.drawString(445, y-20, str(data_dict[data]["serial_number_format"]) + str(data_dict[data]["sl_no"]))
        mycanvas.drawString(445, y-40, str(data_dict[data]["customer_name"])[:17])
        mycanvas.drawString(445, y-60, str(data_dict[data]["amount"]))
       
        mycanvas.setFont('Helvetica', 10)
        mycanvas.drawString(390,y-80,"Zonal Officer Mobile : "+str(data_dict[data]["zoner_mobile"]))
       
        mycanvas.setFont("Times-Roman", 10)
        y2=690
        #for product table
        for i in range(3):
            if i == 0:
                mycanvas.drawString(338,y2-5,"Milk Type")
                mycanvas.drawString(338,y2-32,"Morning")
                mycanvas.drawString(338,y2-53,"Evening")
                mycanvas.line(330,y2+5,545,y2+5)
            else:
                mycanvas.line(330,y2,545,y2)
            mycanvas.line(330,y2+5,330,y2-20)
            mycanvas.line(390-5,y2+5,390-5,y2-20)
            mycanvas.line(430-5,y2+5,430-5,y2-20)
            mycanvas.line(470-5,y2+5,470-5,y2-20)
            mycanvas.line(510-5,y2+5,510-5,y2-20)
            mycanvas.line(545,y2+5,545,y2-20)
            y2 -=20
        mycanvas.line(330,y2,545,y2)
       
        x=402
        y2=690
    #---------------------------
        product_list = []

        for products in data_dict[data]["morning"]:
            product_list.append(products)
        for products in data_dict[data]["evening"]:
            product_list.append(products)

        product_list = set(product_list)
        product_list = list(product_list)

        for product in product_list:
            mycanvas.setFont("Times-Roman", 10)
            mycanvas.drawString(x-13, y2-5, str(product))
            mycanvas.drawString(x-3,y2-15,"ml")
           
            mycanvas.setFont('Helvetica-Bold', 10)
            if product in data_dict[data]["morning"]:
                mycanvas.drawRightString(x+2, y2-32, str(int(data_dict[data]["morning"][product])))
            else:
                mycanvas.drawRightString(x+2, y2-32, '-')

            if product in data_dict[data]["evening"]:
                mycanvas.drawRightString(x+2, y2-53, str(int(data_dict[data]["evening"][product])))
            else:
                mycanvas.drawRightString(x+2, y2-53, '-')
            x += 40
        mycanvas.drawString(280,y2-51,"Manager")
        mycanvas.drawString(270,y2-61,"(Marketing)")
       
        img_file = os.path.join('static/media/',"agm_sign4.png")
        mycanvas.drawInlineImage(img_file, 275, y2-41,(.5*inch), (.320*inch))
       
        mycanvas.showPage()
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
