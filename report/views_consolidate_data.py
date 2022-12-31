from django.shortcuts import render
import os
from PyPDF2 import PdfFileMerger
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
import numpy as np
from decimal import Decimal
from datetime import timedelta, date
# from datetime import datetime
import datetime
import dateutil.relativedelta
from base64 import b64encode, b64decode
#  Plivo credentials
# import plivo
import math
from random import randint
from django.core.files.base import ContentFile
from django.db.models import Sum, Max
from pytz import timezone
from django.db.models import Sum
from calendar import monthrange
from Google import Create_Service
from calendar import monthrange, month_name
API_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRET_FILE = 'google-client-data.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing',
          'https://www.googleapis.com/auth/photoslibrary.readonly']
# canvas
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from main.pdf_generate import *
from main.temp_pdf_generate import generate_pdf_for_temp_route
from django.db import transaction
import csv
import requests
months_in_english = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                     9: 'September', 10: 'October', 11: 'November', 12: 'December'}

def decode_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + '.xlsx')

# VIEWS TO CONSOLIDATE DATA


@api_view(['POST'])
def serve_all_type_of_report(request):
    date_list = pd.date_range(start=request.data['from_date'], end=request.data['to_date'])
    if request.data['session_id'] == 'all':
        session = list(Session.objects.filter().values_list('id', flat=True))
        session_name = 'Both Shift'
    else:
        session = int(request.data['session_id'])
        session_name = Session.objects.get(id=session).name
        session = list(Session.objects.filter(id=session).values_list('id', flat=True))
    report_option = request.data['report_option']
    sale_type_list = request.data['sale_type_list']
    product_list = request.data['product_list']
    data = generate_csv_for_all_type_of_report(date_list, session, session_name, report_option, sale_type_list, product_list)
    return Response(data=data, status=status.HTTP_200_OK)


def generate_csv_for_all_type_of_report(date_list, session, session_name, report_option, sale_type_list, product_list):
    level = report_option
    fields_list = product_list
    if level == "zone":
        zone_obj = Zone.objects.filter()
        final_list = []
        for zone in zone_obj:
            zone_list = []
            zone_list.append(zone.name)
            zone_list.append(session_name)
            for date in date_list:
                zone_report = DailySessionllyZonallySale.objects.filter(session_id__in=session, delivery_date=date,
                                                                        zone_id=zone.id, sold_to__in=sale_type_list)
                for field in fields_list:
                    zone_list.append(zone_report.aggregate(Sum(field))[field + "__sum"])
            final_list.append(zone_list)


        date_lists = ["", ""]
        product_lists = ["Zone", "Session"]
        for date in date_list:
            for fields in fields_list:
                date = str(date)
                date_lists.append(date[:10])
                fields = fields.upper()
                fields = fields.replace("_", "(") + ")"
                product_lists.append(fields)

    if level == "route":
        route_obj = Route.objects.filter(session_id__in=session, is_temp_route=False)
        final_list = []
        for route in route_obj:
            route_list = []
            route_list.append(route.name)
            route_list.append(session_name)
            for date in date_list:
                route_report = DailySessionllyRoutellySale.objects.filter(session_id__in=session, delivery_date=date,
                                                                          route_id=route.id, sold_to__in=sale_type_list)
                for field in fields_list:
                    route_list.append(route_report.aggregate(Sum(field))[field + "__sum"])
            final_list.append(route_list)


        date_lists = ["", ""]
        product_lists = ["Route", "Session"]
        for date in date_list:
            for fields in fields_list:
                date = str(date)
                date_lists.append(date[:10])
                fields = fields.upper()
                fields = fields.replace("_", "(") + ")"
                product_lists.append(fields)

    if level == "booth":
        business_ids = list(
            DailySessionllyBusinessllySale.objects.filter(session_id__in=session, delivery_date__in=date_list,
                                                          sold_to__in=sale_type_list).values_list('business_id',
                                                                                                  flat=True))
        business_obj = BusinessAgentMap.objects.filter(business_id__in=business_ids)
        final_list = []
        for business in business_obj:
            business_list = []
            business_list.append(business.business.code)
            business_list.append(session_name)
            business_list.append(business.business.business_type.name)
            business_list.append(business.agent.agent_code)
            business_list.append(business.agent.first_name)
            business_list.append(business.agent.agent_profile.mobile)
            business_list.append(business.business.zone.name)
            route_name = ''
            if len(session) > 1:
                for route in RouteBusinessMap.objects.filter(business_id=business.business_id,
                                                             route__session_id__in=session):
                    route_name = route_name + str(route.route.name) + ', '

            else:
                route_name = RouteBusinessMap.objects.get(business_id=business.business_id,
                                                          route__session_id__in=session).route.name
            business_list.append(route_name)
            for date in date_list:
                business_report = DailySessionllyBusinessllySale.objects.filter(session_id__in=session,
                                                                                delivery_date=date,
                                                                                business_id=business.business_id,
                                                                                sold_to__in=sale_type_list)

                for field in fields_list:
                    business_list.append(business_report.aggregate(Sum(field))[field + "__sum"])
            final_list.append(business_list)


        date_lists = ["", "", "", "", "", "", "", ""]
        product_lists = ["Business_code", "Session", "Business_type", "Agent_code", "Agent_name", "Agent_mobile",
                         "Zone", "Route"]
        for date in date_list:
            for fields in fields_list:
                date = str(date)
                date_lists.append(date[:10])
                fields = fields.upper()
                fields = fields.replace("_", "(") + ")"
                product_lists.append(fields)

    if level == "zone_wise_booth":
        business_ids = list(
            DailySessionllyBusinessllySale.objects.filter(session_id__in=session, delivery_date__in=date_list,
                                                          sold_to__in=sale_type_list).values_list('business_id',
                                                                                                  flat=True))
        business_obj = BusinessAgentMap.objects.filter(business_id__in=business_ids)
        final_list = []
        for business in business_obj:
            business_list = []
            business_list.append(business.business.code)
            business_list.append(session_name)
            business_list.append(business.business.business_type.name)
            business_list.append(business.agent.agent_code)
            business_list.append(business.agent.first_name)
            business_list.append(business.agent.agent_profile.mobile)
            business_list.append(business.business.zone.name)
            route_name = ''
            if len(session) > 1:
                for route in RouteBusinessMap.objects.filter(business_id=business.business_id,
                                                             route__session_id__in=session):
                    route_name = route_name + str(route.route.name) + ', '

            else:
                route_name = RouteBusinessMap.objects.get(business_id=business.business_id,
                                                          route__session_id__in=session).route.name
            business_list.append(route_name)
            for date in date_list:
                business_report = DailySessionllyBusinessllySale.objects.filter(session_id__in=session,
                                                                                delivery_date=date,
                                                                                business_id=business.business_id,
                                                                                sold_to__in=sale_type_list)

                for field in fields_list:
                    business_list.append(business_report.aggregate(Sum(field))[field + "__sum"])
            final_list.append(business_list)


        date_lists = ["", "", "", "", "", "", "", ""]
        product_lists = ["Business_code", "Session", "Business_type", "Agent_code", "Agent_name", "Agent_mobile",
                         "Zone", "Route"]
        for date in date_list:
            for fields in fields_list:
                date = str(date)
                date_lists.append(date[:10])
                fields = fields.upper()
                fields = fields.replace("_", "(") + ")"
                product_lists.append(fields)

    file_name = str(datetime.datetime.now().date()) + '_Report.csv'
    file_path = os.path.join('static/media/general_report/', file_name)
    with open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(date_lists)
        writer.writerow(product_lists)
        writer.writerows(final_list)
    excel_file_name = str(datetime.datetime.now().date()) + '_report.xlsx'
    excel_file_path = os.path.join('static/media/general_report/', excel_file_name)
    df = pd.read_csv(file_path, header=None)
    if level == 'zone_wise_booth':
      df = df.fillna('')
      with pd.ExcelWriter(excel_file_path) as writer:
        for zone in Zone.objects.all():
            filtered_df = df[(df[6]=="Zone")|(df[6]=='')|(df[6]==str(zone.name))]
            if filtered_df.shape[0] > 2:
                for columns in filtered_df.columns[8:]:
                    filtered_df[columns][2:] = pd.to_numeric(filtered_df[columns][2:])
                filtered_df.to_excel(writer, sheet_name=str(zone.name),header=None, index=False)
    elif level == "booth":
      for columns in df.columns[8:]:
        df[columns][2:] = pd.to_numeric(df[columns][2:])
      df.to_excel(excel_file_path, header=None, index=False)
    else:
      for columns in df.columns[2:]:
        df[columns][2:] = pd.to_numeric(df[columns][2:])
      df.to_excel(excel_file_path, header=None, index=False)
    document = {}
    document['file_name'] = excel_file_name
    try:
        image_path = excel_file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)
    return document


@api_view(['POST'])
def serve_simple_comparision_report(request):
  date_list = [request.data['from_date'], request.data['to_date']]
  session = list(Session.objects.filter().values_list('id', flat=True))
  session_name = 'Both Shift'
  report_option = 'zone_wise_booth'
  sale_type_list = ['Agent', 'ICustomer']
  product_list = ['milk_litre']
  data = generate_csv_for_all_type_of_report_for_simple_report(date_list, session, session_name, report_option, sale_type_list, product_list)
  return Response(data=data, status=status.HTTP_200_OK)


def generate_csv_for_all_type_of_report_for_simple_report(date_list, session, session_name, report_option, sale_type_list, product_list):
  level = report_option
  fields_list = product_list

  if level == "zone_wise_booth":
      business_ids = list(
          DailySessionllyBusinessllySale.objects.filter(session_id__in=session, delivery_date__in=date_list,
                                                        sold_to__in=sale_type_list).values_list('business_id',
                                                                                                flat=True))
      business_obj = BusinessAgentMap.objects.filter(business_id__in=business_ids)
      final_list = []
      for business in business_obj:
          business_list = []
          business_list.append(business.business.code)
          business_list.append(session_name)
          business_list.append(business.business.business_type.name)
          business_list.append(business.agent.agent_code)
          business_list.append(business.agent.first_name)
          business_list.append(business.agent.agent_profile.mobile)
          business_list.append(business.business.zone.name)
          route_name = ''
          if len(session) > 1:
              for route in RouteBusinessMap.objects.filter(business_id=business.business_id,
                                                            route__session_id__in=session):
                  route_name = route_name + str(route.route.name) + ', '

          else:
              route_name = RouteBusinessMap.objects.get(business_id=business.business_id,
                                                        route__session_id__in=session).route.name
          business_list.append(route_name)
          for date in date_list:
              business_report = DailySessionllyBusinessllySale.objects.filter(session_id__in=session,
                                                                              delivery_date=date,
                                                                              business_id=business.business_id,
                                                                              sold_to__in=sale_type_list)

              for field in fields_list:
                  business_list.append(business_report.aggregate(Sum(field))[field + "__sum"])
          if business_list[-1] == None:
            first_value = 0
          else:
            first_value = business_list[-1]
          if business_list[-2] == None:
            second_value = 0
          else:
            second_value = business_list[-2]
          business_list.append(first_value - second_value)
          final_list.append(business_list)


      date_lists = ["", "", "", "", "", "", "", ""]
      product_lists = ["Business_code", "Session", "Business_type", "Agent_code", "Agent_name", "Agent_mobile",
                        "Zone", "Route"]
      for date in date_list:
          for fields in fields_list:
              date = str(date)
              date_lists.append(date[:10])
              fields = fields.upper()
              fields = fields.replace("_", "(") + ")"
              product_lists.append(fields)
      date_lists.append('Diffrence')

  file_name = str(datetime.datetime.now().date()) + '_simple_Report.csv'
  file_path = os.path.join('static/media/general_report/', file_name)
  with open(file_path, 'w') as file:
      writer = csv.writer(file)
      writer.writerow(date_lists)
      writer.writerow(product_lists)
      writer.writerows(final_list)
  excel_file_name = str(datetime.datetime.now().date()) + '_simple_report.xlsx'
  excel_file_path = os.path.join('static/media/general_report/', excel_file_name)
  df = pd.read_csv(file_path, header=None)
  df = df.fillna('')
  with pd.ExcelWriter(excel_file_path) as writer:
    for zone in Zone.objects.all():
        filtered_df = df[(df[6]=="Zone")|(df[6]=='')|(df[6]==str(zone.name))]
        if filtered_df.shape[0] > 2:
            for columns in filtered_df.columns[8:]:
              filtered_df[columns][2:] = pd.to_numeric(filtered_df[columns][2:])
            filtered_df.to_excel(writer, sheet_name=str(zone.name),header=None, index=False)
  document = {}
  document['file_name'] = excel_file_name
  try:
      image_path = excel_file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
  except Exception as err:
      print(err)
  return document


@api_view(['POST'])
def serve_advance_report_in_excel(request):
  # print(request.data)
  business_code_list = request.data['booth_code_list']
  exclude_business_list = request.data['exclude_booth_code_list']
  session_id = request.data['session_id']
  if session_id == 'all':
      session = list(Session.objects.filter().values_list('id', flat=True))
      session_name = 'Both Shift'
  else:
      session = int(session_id)
      session_name = Session.objects.get(id=session).name
      session = list(Session.objects.filter(id=session).values_list('id', flat=True))
  product_list = request.data['product_list']
  date_list = pd.date_range(start=request.data['from_date'], end=request.data['to_date'])
  product_wise_total_dict = {}
  for product in product_list:
      product_wise_total_dict[product] = 0
  output_data_list = []
  sale_obj = DailySessionllyBusinessllySale.objects.filter(business__code__in=business_code_list, sold_to__in=['Agent', 'ICustomer'], session_id__in=session).exclude(business__code__in=exclude_business_list)
  index = 0
  for date in date_list:
      temp_data_list = []
      index += 1
      temp_data_list.append(index)
      temp_data_list.append(date.date())
      sale_data = sale_obj.filter(delivery_date=date)
      for product in product_list:
          temp_data_list.append(sale_data.aggregate(Sum(product))[product + "__sum"])
          if not sale_data.aggregate(Sum(product))[product + "__sum"] is None:
              product_wise_total_dict[product] += sale_data.aggregate(Sum(product))[product + "__sum"]
      output_data_list.append(temp_data_list)
  total_list = ["", "Total"]
  for product in product_list:
      total_list.append(product_wise_total_dict[product])
  output_data_list.append(total_list)
  header_list = ["S.No", "Date"]
  for product in product_list:
      product = product.upper()
      product = product.replace("_", "(") + ")"
      header_list.append(product)
      
  file_name = str(datetime.datetime.now().date()) + '_advance_report.csv'
  file_path = os.path.join('static/media/general_report/', file_name)
  excel_file_name = str(datetime.datetime.now().date()) + '_advance_report_report.xlsx'
  excel_file_path = os.path.join('static/media/general_report/', excel_file_name)
  with open(file_path, 'w') as file:
      writer = csv.writer(file)
      writer.writerow(header_list)
      writer.writerows(output_data_list)
  df = pd.read_csv(file_path)
  df.to_excel(excel_file_path, index=False)
  document = {}
  document['file_name'] = excel_file_name
  try:
      image_path = excel_file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
  except Exception as err:
      print(err)
  return Response(data=document, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_advance_report_in_excel_for_route(request):
  route_list = request.data['route_list']
  exclude_business_list = request.data['exclude_booth_code_list']
  product_list = request.data['product_list']
  date_list = pd.date_range(start=request.data['from_date'], end=request.data['to_date'])
  product_wise_total_dict = {}
  if request.data['is_leakage_included']:
      sold_to_list = ['Agent', 'ICustomer', 'Leakage']
  else:
      sold_to_list = ['Agent', 'ICustomer']
  for product in product_list:
      product_wise_total_dict[product] = 0
  output_data_list = []
  index = 0
  for date in date_list:
      temp_data_list = []
      index += 1
      temp_data_list.append(index)
      temp_data_list.append(date.date())
      sale_data = DailySessionllyBusinessllySale.objects.filter(delivery_date=date, sold_to__in=sold_to_list, route_id__in=route_list).exclude(business__code__in=exclude_business_list)
      total_booth = len(list(set(sale_data.values_list('business_id', flat=True))))
      temp_data_list.append(total_booth)
      for product in product_list:
          temp_data_list.append(sale_data.aggregate(Sum(product))[product + "__sum"])
          if not sale_data.aggregate(Sum(product))[product + "__sum"] is None:
              product_wise_total_dict[product] += sale_data.aggregate(Sum(product))[product + "__sum"]
      output_data_list.append(temp_data_list)
  total_list = ["", "", "Total"]
  for product in product_list:
      total_list.append(product_wise_total_dict[product])
  output_data_list.append(total_list)
  header_list = ["S.No",  "Date", "Booth Count"]
  for product in product_list:
      product = product.upper()
      product = product.replace("_", "(") + ")"
      header_list.append(product)
      
  file_name = str(datetime.datetime.now().date()) + '_advance_report_route_wise.csv'
  file_path = os.path.join('static/media/general_report/', file_name)
  excel_file_name = str(datetime.datetime.now().date()) + '_advance_report_route_wise.xlsx'
  excel_file_path = os.path.join('static/media/general_report/', excel_file_name)
  with open(file_path, 'w') as file:
      writer = csv.writer(file)
      writer.writerow(header_list)
      writer.writerows(output_data_list)
  df = pd.read_csv(file_path)
  df.to_excel(excel_file_path, index=False)
  document = {}
  document['file_name'] = excel_file_name
  try:
      image_path = excel_file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
  except Exception as err:
      print(err)
  return Response(data=document, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_zone_booth_route_data_gor_general_report(request):
  data_dict = {'zone_data': [], 'business_type_data': [], 'mor_route_data': [], 'eve_route_data': [], 'session_data': [],
             'zone_wise_booth': {},
             'business_type_wise_booth': {},
             'route_wise_booth': {}}
  # zone
  zone_obj = Zone.objects.filter()
  zone_list = list(zone_obj.values_list('id', 'name'))
  zone_column = ['id', 'name']
  zone_df = pd.DataFrame(zone_list, columns=zone_column)
  data_dict['zone_data'] = zone_df.to_dict('r')
# session
  session_obj = Session.objects.filter().order_by('id')
  session_list = list(session_obj.values_list('id', 'name'))
  session_column = ['id', 'name']
  session_df = pd.DataFrame(session_list, columns=session_column)
  data_dict['session_data'] = session_df.to_dict('r')

  business_type_obj = BusinessType.objects.filter()
  business_type_list = list(business_type_obj.values_list('id', 'name'))
  business_type_column = ['id', 'name']
  business_type_df = pd.DataFrame(business_type_list, columns=business_type_column)
  data_dict['business_type_data'] = business_type_df.to_dict('r')

  mor_route_obj = Route.objects.filter(session_id=1, is_temp_route=False).order_by('name')
  mor_route_list = list(mor_route_obj.values_list('id', 'name'))
  mor_route_column = ['id', 'name']
  mor_route_df = pd.DataFrame(mor_route_list, columns=mor_route_column)
  data_dict['mor_route_data'] = mor_route_df.to_dict('r')

  eve_route_obj = Route.objects.filter(session_id=2, is_temp_route=False).order_by('name')
  eve_route_list = list(eve_route_obj.values_list('id', 'name'))
  eve_route_column = ['id', 'name']
  eve_route_df = pd.DataFrame(eve_route_list, columns=eve_route_column)
  data_dict['eve_route_data'] = eve_route_df.to_dict('r')
  main_business_obj = Business.objects.filter()
  main_business_list = list(main_business_obj.values_list('id', 'code', 'zone', 'business_type'))
  main_business_column = ['id', 'code', 'zone_id', 'business_type_id']
  main_business_df = pd.DataFrame(main_business_list, columns=main_business_column)
  data_dict['zone_wise_booth'] = main_business_df.groupby('zone_id')['code'].apply(list).to_dict()
  data_dict['business_type_wise_booth'] = main_business_df.groupby('business_type_id')['code'].apply(list).to_dict()
  values = RouteBusinessMap.objects.filter().values_list('business_id', 'business__code', 'route_id')
  columns = ['id', 'code', 'route_id']
  df = pd.DataFrame(list(values), columns=columns)
  data_dict['route_wise_booth'] = df.groupby('route_id')['code'].apply(list).to_dict()
  return Response(data=data_dict, status=status.HTTP_200_OK)


def calculate_percentage(total, percentage):
    return (percentage/100) * total

@transaction.atomic
@api_view(['POST'])
def run_booth_commission_for_seleted_date_range(request):
    sid = transaction.savepoint()
    try:
        start_time = datetime.datetime.now()
        indian = pytz.timezone('Asia/Kolkata')
        global_config_obj = GlobalConfig.objects.all()
        global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
        global_config_column = ['id', 'name', 'value', 'description']
        global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
        global_config_df['value'].astype('float')
        global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()
        from_date = request.data['from_date']
        to_date = request.data['to_date']
        format_date = datetime.datetime.strptime(from_date,'%Y-%m-%d')
        month = format_date.month
        year = format_date.year
        if MonthlyAgentCommissionRun.objects.filter(month=month, year=year).exists():
            split_count = MonthlyAgentCommissionRun.objects.filter(month=month, year=year).count()
            split_count += 1
        else:
            split_count = 1
        #   if MonthlyAgentCommissionRun.objects.filter(month=month, split=1, year=year).exists():
        #     MonthlyAgentCommissionRun.objects.filter(month=month, split=1, year=year).delete()
        #     print('deleted')
        
        monthly_agent_commission_run_obj = MonthlyAgentCommissionRun(
                                        year=year,
                                        month=month,
                                        split=split_count,
                                        run_from=from_date,
                                        run_to=to_date,
                                        card_milk_comm_percentage=global_config_dict['card_commission']['value'],
                                        cash_milk_comm_percentage=global_config_dict['cash_commission']['value'],
                                        tds_deduction_percentage=global_config_dict['tds']['value'],
                                        insurance_deduction_percentage=global_config_dict['agent_insurance_on_commission_deduction']['value'],
                                        slip_charge=global_config_dict['slip_charge']['value'],
                                        comm_run_started_at=datetime.datetime.now().astimezone(indian), 
                                        comm_calculated_by_id=request.user.id,
                                        comm_calculation_approved_by_id=request.user.id,
                                        comm_calculation_approved_at=datetime.datetime.now().astimezone(indian))
        monthly_agent_commission_run_obj.save()
        if request.data['is_sub_column_available']:
            for column in request.data['sub_column_list']:
                if column['label'] != None and column['file'] != None:
                    monthly_agent_commission_run_column_obj = MonthlyAgentCommissionRunColumnCv(run_id=monthly_agent_commission_run_obj.id,
                                                                                                column_name=column['label'])
                    try:
                        monthly_agent_commission_run_column_obj.document=decode_image(column['file'])
                    except Exception as err:
                        print(err)      
                    monthly_agent_commission_run_column_obj.save()                                                  
        document_data_dict = {}
        is_sub_column_avilable = False
        if MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=monthly_agent_commission_run_obj.id).exists():
            is_sub_column_avilable = True
            monthly_agent_commission_run_column_obj = MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=monthly_agent_commission_run_obj.id)
            for commission_run_column in monthly_agent_commission_run_column_obj:
                document_df = pd.read_excel('static/media/'+ str(commission_run_column.document))
                document_df = document_df.fillna(0)
                if not document_df['AgentCode'].dtypes == 'O':
                    document_df['AgentCode'] = document_df['AgentCode'].astype(int)
                    document_df['AgentCode'] = document_df['AgentCode'].astype(str)
                else:
                    document_df['AgentCode'] = document_df['AgentCode'].astype(str)
                document_df['Amount'] = document_df['Amount'].astype(int)
                document_data = document_df.groupby('AgentCode').apply(lambda x: x.to_dict('r')[0]).to_dict()
                document_data_dict[commission_run_column.column_name] = document_data
        for business in Business.objects.filter(business_type_id__in=[1, 2]):
            if BusinessAgentMap.objects.filter(business_id=business.id).exists():
            
                agent_id = BusinessAgentMap.objects.get(business_id=business.id).agent.id
                agent_obj = BusinessAgentMap.objects.get(business_id=business.id).agent
                monthly_agent_commission_obj = MonthlyAgentCommission(run_id=monthly_agent_commission_run_obj.id,
                                                                    agent_id=agent_id,
                                                                    business_codes=business.code,
                                                                    business_id=business.id,
                                                                    business_type_id=business.business_type_id)
                total_cash_objs = DailySessionllyBusinessllySale.objects.filter(delivery_date__range=[from_date,to_date], business_id=business.id,
                                                                                sold_to='Agent')
                total_card_objs = DailySessionllyBusinessllySale.objects.filter(delivery_date__range=[from_date,to_date], business_id=business.id,
                                                                                sold_to='ICustomer')
                total_tm_cash_amount = 0
                total_tm_card_amount = 0
                if not total_cash_objs.aggregate(Sum('tm500_cost'))['tm500_cost__sum'] is None:
                    total_tm_cash_amount = total_cash_objs.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
                if not total_card_objs.aggregate(Sum('tm500_cost'))['tm500_cost__sum'] is None:
                    total_tm_card_amount = total_card_objs.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
                
                if total_tm_cash_amount != 0:
                    monthly_agent_commission_obj.tm_cash_milk_sale = total_tm_cash_amount
                    monthly_agent_commission_obj.tm_cash_milk_comm = Decimal(format(
                        calculate_percentage(total_tm_cash_amount, Decimal(global_config_dict['cash_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.tm_cash_milk_sale = 0
                    monthly_agent_commission_obj.tm_cash_milk_comm = 0
                
                if total_tm_card_amount != 0:
                    monthly_agent_commission_obj.tm_card_milk_sale = total_tm_card_amount
                    monthly_agent_commission_obj.tm_card_milk_comm = Decimal(format(
                        calculate_percentage(total_tm_card_amount, Decimal(global_config_dict['card_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.tm_card_milk_sale = 0
                    monthly_agent_commission_obj.tm_card_milk_comm = 0
                
            #     sm
            #     cash
                total_sm_cash_amount = 0
                if not total_cash_objs.aggregate(Sum('std250_cost'))['std250_cost__sum'] is None:
                    total_sm_cash_amount += total_cash_objs.aggregate(Sum('std250_cost'))['std250_cost__sum']
                if not total_cash_objs.aggregate(Sum('std500_cost'))['std500_cost__sum'] is None:
                    total_sm_cash_amount += total_cash_objs.aggregate(Sum('std500_cost'))['std500_cost__sum']
            #   card
                total_sm_card_amount = 0
                if not total_card_objs.aggregate(Sum('std250_cost'))['std250_cost__sum'] is None:
                    total_sm_card_amount += total_card_objs.aggregate(Sum('std250_cost'))['std250_cost__sum']
                if not total_card_objs.aggregate(Sum('std500_cost'))['std500_cost__sum'] is None:
                    total_sm_card_amount += total_card_objs.aggregate(Sum('std500_cost'))['std500_cost__sum']
                    
                if total_sm_cash_amount != 0:
                    monthly_agent_commission_obj.sm_cash_milk_sale = total_sm_cash_amount
                    monthly_agent_commission_obj.sm_cash_milk_comm = Decimal(format(
                        calculate_percentage(total_sm_cash_amount, Decimal(global_config_dict['cash_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.sm_cash_milk_sale = 0
                    monthly_agent_commission_obj.sm_cash_milk_comm = 0
                
                if total_sm_card_amount != 0:
                    monthly_agent_commission_obj.sm_card_milk_sale = total_sm_card_amount
                    monthly_agent_commission_obj.sm_card_milk_comm = Decimal(format(
                        calculate_percentage(total_sm_card_amount, Decimal(global_config_dict['card_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.sm_card_milk_sale = 0
                    monthly_agent_commission_obj.sm_card_milk_comm = 0
                    
            #     fcm
            #     cash
                total_fcm_cash_amount = 0
                if not total_cash_objs.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum'] is None:
                    total_fcm_cash_amount += total_cash_objs.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum']
                if not total_cash_objs.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum'] is None:
                    total_fcm_cash_amount += total_cash_objs.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum']
                
                #   card
                total_fcm_card_amount = 0
                if not total_card_objs.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum'] is None:
                    total_fcm_card_amount += total_card_objs.aggregate(Sum('fcm500_cost'))['fcm500_cost__sum']
                if not total_card_objs.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum'] is None:
                    total_fcm_card_amount += total_card_objs.aggregate(Sum('fcm1000_cost'))['fcm1000_cost__sum']
                    
                
                if total_fcm_cash_amount != 0:
                    monthly_agent_commission_obj.fcm_cash_milk_sale = total_fcm_cash_amount
                    monthly_agent_commission_obj.fcm_cash_milk_comm = Decimal(format(
                        calculate_percentage(total_fcm_cash_amount, Decimal(global_config_dict['cash_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.fcm_cash_milk_sale = 0
                    monthly_agent_commission_obj.fcm_cash_milk_comm = 0
                
                if total_fcm_card_amount != 0:
                    monthly_agent_commission_obj.fcm_card_milk_sale = total_fcm_card_amount
                    monthly_agent_commission_obj.fcm_card_milk_comm = Decimal(format(
                        calculate_percentage(total_fcm_card_amount, Decimal(global_config_dict['card_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.fcm_card_milk_sale = 0
                    monthly_agent_commission_obj.fcm_card_milk_comm = 0

            #     tmate
            #     cash
                total_tea_cash_amount = 0
                if not total_cash_objs.aggregate(Sum('tea500_cost'))['tea500_cost__sum'] is None:
                    total_tea_cash_amount += total_cash_objs.aggregate(Sum('tea500_cost'))['tea500_cost__sum']
                if not total_cash_objs.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum'] is None:
                    total_tea_cash_amount += total_cash_objs.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum']
                
                #   card
                total_tea_card_amount = 0
                if not total_card_objs.aggregate(Sum('tea500_cost'))['tea500_cost__sum'] is None:
                    total_tea_card_amount += total_card_objs.aggregate(Sum('tea500_cost'))['tea500_cost__sum']
                if not total_card_objs.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum'] is None:
                    total_tea_card_amount += total_card_objs.aggregate(Sum('tea1000_cost'))['tea1000_cost__sum']
                    
                
                if total_tea_cash_amount != 0:
                    monthly_agent_commission_obj.tea_cash_milk_sale = total_tea_cash_amount
                    monthly_agent_commission_obj.tea_cash_milk_comm = Decimal(format(
                        calculate_percentage(total_tea_cash_amount, Decimal(global_config_dict['cash_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.tea_cash_milk_sale = 0
                    monthly_agent_commission_obj.tea_cash_milk_comm = 0
                
                if total_tea_card_amount != 0:
                    monthly_agent_commission_obj.tea_card_milk_sale = total_tea_card_amount
                    monthly_agent_commission_obj.tea_card_milk_comm = Decimal(format(
                        calculate_percentage(total_tea_card_amount, Decimal(global_config_dict['card_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.tea_card_milk_sale = 0
                    monthly_agent_commission_obj.tea_card_milk_comm = 0
                        
                    
            #     Can milk
            #     cash
                total_can_milk_cash_amount = 0
                if not total_cash_objs.aggregate(Sum('tmcan_cost'))['tmcan_cost__sum'] is None:
                    total_can_milk_cash_amount += total_cash_objs.aggregate(Sum('tmcan_cost'))['tmcan_cost__sum']
                if not total_cash_objs.aggregate(Sum('smcan_cost'))['smcan_cost__sum'] is None:
                    total_can_milk_cash_amount += total_cash_objs.aggregate(Sum('smcan_cost'))['smcan_cost__sum']
                if not total_cash_objs.aggregate(Sum('fcmcan_cost'))['fcmcan_cost__sum'] is None:
                    total_can_milk_cash_amount += total_cash_objs.aggregate(Sum('fcmcan_cost'))['fcmcan_cost__sum']
                    
                if total_can_milk_cash_amount != 0:
                    monthly_agent_commission_obj.can_milk_sale = total_can_milk_cash_amount
                    monthly_agent_commission_obj.can_milk_comm = Decimal(format(
                        calculate_percentage(total_can_milk_cash_amount, Decimal(global_config_dict['cash_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.can_milk_sale = 0
                    monthly_agent_commission_obj.can_milk_comm = 0
                
                
                #     total milk sale
                total_cash_sale = total_tm_cash_amount + total_sm_cash_amount + total_fcm_cash_amount + total_can_milk_cash_amount + total_tea_cash_amount
                if total_cash_sale != 0:
                    monthly_agent_commission_obj.total_cash_milk_sale = total_cash_sale
                    monthly_agent_commission_obj.total_cash_milk_comm = Decimal(format(
                        calculate_percentage(total_cash_sale, Decimal(global_config_dict['cash_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.total_cash_milk_sale = 0
                    monthly_agent_commission_obj.total_cash_milk_comm = 0
                total_card_sale = total_tm_card_amount + total_sm_card_amount + total_fcm_card_amount + total_tea_card_amount
                
                if total_card_sale != 0:
                    monthly_agent_commission_obj.total_card_milk_sale = total_card_sale
                    monthly_agent_commission_obj.total_card_milk_comm = Decimal(format(
                        calculate_percentage(total_card_sale, Decimal(global_config_dict['card_commission']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.total_card_milk_sale = 0
                    monthly_agent_commission_obj.total_card_milk_comm = 0
                                                                                
                monthly_agent_commission_obj.gross_sale = monthly_agent_commission_obj.total_cash_milk_sale + monthly_agent_commission_obj.total_card_milk_sale
                monthly_agent_commission_obj.gross_comm = round(monthly_agent_commission_obj.total_cash_milk_comm + monthly_agent_commission_obj.total_card_milk_comm)
            #     tds
                if agent_obj.pan_number == None or agent_obj.pan_number == '':
                    monthly_agent_commission_obj.tds_deduction = Decimal(
                                format(calculate_percentage(monthly_agent_commission_obj.gross_comm, Decimal(20))))
                elif monthly_agent_commission_obj.gross_comm >= int(global_config_dict['minimum_commission_amount_for_tds']['value']):
                    monthly_agent_commission_obj.tds_deduction = Decimal(
                            format(calculate_percentage(monthly_agent_commission_obj.gross_comm, Decimal(global_config_dict['tds']['value'])),'.2f'))
                else:
                    monthly_agent_commission_obj.tds_deduction = 0
                monthly_agent_commission_obj.tds_deduction = math.ceil(monthly_agent_commission_obj.tds_deduction)
            #     insurance
                if not monthly_agent_commission_obj.gross_comm == 0:
                    monthly_agent_commission_obj.insurance_deduction = Decimal(
                            format(calculate_percentage(monthly_agent_commission_obj.gross_comm, Decimal(global_config_dict['agent_insurance_on_commission_deduction']['value'])),'.2f'))
                    #     slip charge
                    monthly_agent_commission_obj.slip_charge = Decimal(global_config_dict['slip_charge']['value'])
                else:
                    monthly_agent_commission_obj.insurance_deduction = 0
                    monthly_agent_commission_obj.slip_charge = 0

            #     gross deduction
                gross_deduction = monthly_agent_commission_obj.tds_deduction + monthly_agent_commission_obj.insurance_deduction + monthly_agent_commission_obj.slip_charge 
                if is_sub_column_avilable:
                    for commission_run_column in monthly_agent_commission_run_column_obj:
                        if str(agent_obj.agent_code) in document_data_dict[commission_run_column.column_name].keys():
                            if not document_data_dict[commission_run_column.column_name][str(agent_obj.agent_code)]['Amount'] == 0:
                                gross_deduction += document_data_dict[commission_run_column.column_name][str(agent_obj.agent_code)]['Amount']
                        
                monthly_agent_commission_obj.gross_deduction = gross_deduction
                
            #     net total
                final_commission_amount = monthly_agent_commission_obj.gross_comm - monthly_agent_commission_obj.gross_deduction
                monthly_agent_commission_obj.net_comm = final_commission_amount
                
                monthly_agent_commission_obj.comm_calculated_at = datetime.datetime.now()
                monthly_agent_commission_obj.comm_calculated_by_id = request.user.id
                if monthly_agent_commission_obj.gross_comm > 0:
                    monthly_agent_commission_obj.save()
                    if is_sub_column_avilable:
                        for commission_run_column in monthly_agent_commission_run_column_obj:
                            if str(agent_obj.agent_code) in document_data_dict[commission_run_column.column_name].keys():
                                if not document_data_dict[commission_run_column.column_name][str(agent_obj.agent_code)]['Amount'] == 0:
                                    monthly_agent_commission_sub_column = MonthlyAgentCommissionSubColumn(agent_commission_id=monthly_agent_commission_obj.id,
                                                                                                        column_id=commission_run_column.id,
                                                                                                        value=document_data_dict[commission_run_column.column_name][str(agent_obj.agent_code)]['Amount'])
                                    monthly_agent_commission_sub_column.save()
            
        monthly_agent_commission_run_obj.comm_run_ended_at = datetime.datetime.now().astimezone(indian)
        monthly_agent_commission_run_obj.comm_calculated_at = datetime.datetime.now().astimezone(indian)
        monthly_agent_commission_run_obj.is_comm_run_completed = True
        monthly_agent_commission_run_obj.save()
        message = 'Commission run for {} month is started at {}. ended at {}. Now you can take your reports.  '.format(months_in_english[month], monthly_agent_commission_run_obj.comm_run_started_at, monthly_agent_commission_run_obj.comm_run_ended_at)
        purpose = 'Commission Run Alert'
        phone = UserProfile.objects.get(user_id=request.user.id).mobile
        send_message_via_netfision(purpose, phone, message)
        print(datetime.datetime.now() - start_time)
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        message = 'Commission run failed for  {} month'.format(months_in_english[month])
        purpose = 'Commission Run Alert'
        phone = UserProfile.objects.get(user_id=request.user.id).mobile
        send_message_via_netfision(purpose, phone, message)
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def send_message_via_netfision_using_kultivate(purpose, mobile, message):
    current_date = datetime.datetime.now().date()
    if DailySmsCount.objects.filter(date=current_date).exists():
        daily_sms_count_obj = DailySmsCount.objects.filter(date=current_date, sms_provider_id=2)[0]
    else:
        daily_sms_count_obj = DailySmsCount(date=current_date, count=0, sms_provider_id=2)
        daily_sms_count_obj.save()
    count = int(daily_sms_count_obj.count)
    count += 1
    daily_sms_count_obj.count = count
    daily_sms_count_obj.save() 
    payload = {'ClientId': 'c9dc2b72-a38c-4e29-9834-17fe1ef6df3f', 'ApiKey' :'0fa9908c-1e67-4ccb-86fc-2363f7f75839', 'SenderID' : 'KULTIV', 'fl':'0', 'gwid':'2', 'sid':'KULTIV'} 
    headers = {} 
    url     = 'http://sms.tnvt.in/vendorsms/pushsms.aspx' 
    payload['msg'] = message 
    payload['msisdn'] = mobile, 9363095091
    res = requests.post(url, data=payload, headers=headers) 


def send_message_via_netfision(purpose, mobile, message):
    current_date = datetime.datetime.now().date()
    if DailySmsCount.objects.filter(date=current_date).exists():
        daily_sms_count_obj = DailySmsCount.objects.filter(date=current_date, sms_provider_id=1)[0]
    else:
        daily_sms_count_obj = DailySmsCount(date=current_date, count=0, sms_provider_id=1)
        daily_sms_count_obj.save()
    count = int(daily_sms_count_obj.count)
    count += 1
    daily_sms_count_obj.count = count
    daily_sms_count_obj.save()

    payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey': '622de6e4-91da-4e3b-9fb1-2262df7baff8',
               'SenderID': 'AAVINC', 'fl': '0', 'gwid': '2', 'sid': 'AAVINC'}
    headers = {}
    url = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'
    payload['msg'] = message
    payload['msisdn'] = mobile
    res = requests.post(url, data=payload, headers=headers)


def find_out_tds_percentage(pan_number, tds_value):
    if pan_number == None or pan_number == '':
        return 20
    else:
        return tds_value


@api_view(['POST'])
def serve_agent_monthly_commission_report(request):
    print(request.data)
    data_dict = {
        'commission_report_c1' : {},
        'commission_report_c2': {},
        'commission_report_c3': {},
        'commission_report_c4': {},
        'commission_report_c5': {},
        'commission_report_c1b': {},
        'commission_report_slip_charge': {},
    }
    if request.data['report_option'] == 'commission_report_c1':
      data_dict['commission_report_c1'] = create_canvas_report_for_c1_commission_report(request.data)
    if request.data['report_option'] == 'commission_report_c1b':
      data_dict['commission_report_c1b'] = create_canvas_report_for_c1b_commission_report(request.data)
    if request.data['report_option'] == 'commission_report_c2':
      data_dict['commission_report_c2'] = create_canvas_report_for_c2_commission_report(request.data)
    if request.data['report_option'] == 'commission_report_c3':
      data_dict['commission_report_c3'] = create_canvas_report_for_c3_commission_report(request.data)
    if request.data['report_option'] == 'commission_report_c4':
      data_dict['commission_report_c4'] = create_canvas_report_for_c4_commission_report(request.data)
    if request.data['report_option'] == 'commission_report_c5':
      data_dict['commission_report_c5'] = create_canvas_report_for_c5_commission_report(request.data)
    if request.data['report_option'] == 'commission_report_slip_charge':
      data_dict['commission_report_slip_charge'] = create_canvas_report_for_commission_report_slip_charge(request.data)
    if request.data['report_option'] == 'commission_report_c2b':
      data_dict['commission_report_c2b'] = create_canvas_report_for_c2b_commission_report(request.data)

    return Response(data=data_dict, status=status.HTTP_200_OK)

def create_canvas_report_for_c2b_commission_report(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']

    monthly_agent_for_bank_obj = MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date).order_by('agent__agent_code')
    monthly_agent_for_bank_list =list(monthly_agent_for_bank_obj.values_list('agent__agentbankdetail__account_holder_name', 'agent__agentbankdetail__ifsc_code', 'agent__agentbankdetail__account_number', 'net_comm'))
    monthly_agent_for_bank_column = ['','', '', 'Total']
    monthly_agent_for_bank_df = pd.DataFrame(monthly_agent_for_bank_list,columns=monthly_agent_for_bank_column)
    monthly_agent_for_bank_df.insert(loc=0, column='AAVIN', value='')
    monthly_agent_for_bank_df.insert(loc=1, column='TB', value='')
    monthly_agent_for_bank_df.insert(loc=2, column=' ', value=len(str(len(monthly_agent_for_bank_df))))
    monthly_agent_for_bank_df.insert(loc=3, column='  ', value='')
    monthly_agent_for_bank_df.insert(loc=4, column='   ', value=len(monthly_agent_for_bank_df))
    monthly_agent_for_bank_df.insert(loc=5, column='    ', value='2020')
    monthly_agent_for_bank_df.insert(loc=6, column='     ', value='')
    monthly_agent_for_bank_df.insert(loc=7, column='       ', value='UTIB0000090')
    monthly_agent_for_bank_df.insert(loc=8, column='        ', value='910010044762468')
    monthly_agent_for_bank_df.insert(loc=9, column='         ', value='')
    monthly_agent_for_bank_df.insert(loc=10, column='          ', value='')
    monthly_agent_for_bank_df.insert(loc=11, column='           ', value='')
    monthly_agent_for_bank_df.insert(loc=12, column='            ', value='')
    monthly_agent_for_bank_df.insert(loc=13, column='             ', value='')
    monthly_agent_for_bank_df.insert(loc=14, column='              ', value='')
    monthly_agent_for_bank_df.insert(loc=17, column='               ', value='')
    monthly_agent_for_bank_df.insert(loc=19, column='                 ', value='')
    monthly_agent_for_bank_df['Total'] = monthly_agent_for_bank_df['Total'].astype(float)
    monthly_agent_for_bank_df.columns = monthly_agent_for_bank_df.columns.str.replace('Total', str(monthly_agent_for_bank_df['Total'].sum()))
    monthly_agent_for_bank_df.index = monthly_agent_for_bank_df.index + 1
    print(len(monthly_agent_for_bank_df))
    excel_file_name = 'commission_report_c2b_from_' + str(from_date) + '_to_' + str(to_date) + ".xlsx"
    excel_file_path = os.path.join('static/media/monthly_report/', excel_file_name)
    monthly_agent_for_bank_df.to_excel(excel_file_path)
    document = {}
    document['excel_file_name'] = excel_file_name

    try:
        image_path = excel_file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel'] = encoded_image
    except Exception as err:
        print(err)
    return document



def create_canvas_report_for_c1b_commission_report(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()
    
    # commission report
    monthly_agent_obj = MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date)
    monthly_agent_list = list(monthly_agent_obj.values_list('id','agent__agent_code','agent__first_name','agent__pan_number','gross_sale', 'gross_comm', 'tds_deduction', 'slip_charge', 'gross_deduction', 'net_comm'))
    monthly_agent_column = ['id','Agent Code', 'Agent Name','Pan No', 'Gross Value', 'GrossCommission', 'TDS deduction','Slip charges', 'Gross Deduction', 'Net Commission']
    monthly_agent_df = pd.DataFrame(monthly_agent_list, columns=monthly_agent_column)
    monthly_agent_df["sunesh"] = 0
    
    monthly_agent_df['TDS Percentage'] = monthly_agent_df.apply(lambda x: find_out_tds_percentage(x['Pan No'], global_config_dict['tds']['value']), axis=1)
    data_dict = monthly_agent_df.to_dict('r')
    agent_commission_columns = []
    if MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=run_id).exists():
      agent_commission_columns = list(MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=run_id).values_list('column_name', flat=True))
      for index, data in  enumerate(data_dict, start=0):
          if MonthlyAgentCommissionSubColumn.objects.filter(agent_commission_id=data['id']).exists():
              for sub_column in MonthlyAgentCommissionSubColumn.objects.filter(agent_commission_id=data['id']):
                  data_dict[index][sub_column.column.column_name] = sub_column.value
          else:
              for column in agent_commission_columns:
                  data_dict[index][column] = 0
    
    df = pd.DataFrame(data_dict)
    
    df.drop(['id','Pan No'],inplace = True,axis=1)
    column_titles = ['Agent Code', 'Agent Name', 'Gross Value', 'GrossCommission', 'TDS deduction', 'Slip charges']
    last_column = ['Gross Deduction', 'Net Commission','TDS Percentage']
    final_column = column_titles + agent_commission_columns + last_column
    df = df.reindex(columns=final_column)
   
    excel_file_name = 'commission_report_C1B_from_' + str(from_date) + '_to_' + str(to_date) + ".xlsx"
    excel_file_path = os.path.join('static/media/monthly_report/', excel_file_name)
    
    df.to_excel(excel_file_path)
    df_ex = pd.read_excel(excel_file_path)
    df_ex.drop("Unnamed: 0",inplace = True,axis=1)
    df_ex.index = df.index + 1
    df_ex.to_excel(excel_file_path)

   
    file_name = 'commission_report_C1B_from_' + str(from_date) + '_to_' + str(to_date) + ".pdf"
    file_path = os.path.join('static/media/monthly_report/', file_name)
   
    mycanvas = canvas.Canvas(file_path, pagesize=(15 * inch, 12 * inch))
    pdfmetrics.registerFont(TTFont('Helvetica', 'dotmatrix.ttf'))
    light_color =0x000000
    dark_color = 0x000000

    data_dict = df.to_dict('r')
    
    
    from_date = datetime.datetime.strptime(from_date[:10], '%Y-%m-%d')
    report_for_month = str(from_date.strftime('%B'))
    report_for_year = str(from_date.year)

    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica-Bold', 13)
    mycanvas.drawRightString(750, 795,"C1B")
    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(550, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 13)
    mycanvas.drawCentredString(550, 795, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)
   
    mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
   
    x_total_len = 1060
    x_axis = 20
    x_axis_line = 10
    y_axis = 670+90
    y_axis_line = 690+90
    sl_no = 1
    mycanvas.setFont('Helvetica', 10)
    len_adjust=len(data_dict[0])
       
    mycanvas.drawCentredString(x_axis,y_axis,str("Sl."))
    mycanvas.drawCentredString(x_axis,y_axis-15,str("No"))
   
    mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
    mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)

    for stock_name in data_dict[0]:
        data_name = ""
        data_2nd_name = ""
        data = stock_name.split(" ")

        if data[0] == "" :
            data.remove(data[0])

        if data[-1] == "":
            data.remove(data[-1])

        if len(data) == 1:
            if data[0] == "GrossCommission":
                data_name += "Gross"
                data_2nd_name += "Commission"

            elif data[0] == "BoothCodes":
                data_name += "Booth"
                data_2nd_name += "Codes"
            else:
                data_name += data[0]

        if len(data) == 2:
            data_name += data[0]
            data_2nd_name += data[1]

        if len(data) == 3:
            data_name += data[0] + " " + data[1]
            data_2nd_name += data[-1]

        if len(data) == 4:
            data_name += data[0] + " " + data[1]
            data_2nd_name += data[2]+ " " + data[3]
            
        if stock_name == list(data_dict[0].keys())[-1]:
            mycanvas.drawCentredString(x_axis+33,y_axis,str(data_name))
            mycanvas.drawCentredString(x_axis+33,y_axis-15,str(data_2nd_name))
        else:
            mycanvas.drawCentredString(x_axis+48,y_axis,str(data_name))
            mycanvas.drawCentredString(x_axis+48,y_axis-15,str(data_2nd_name))
        x_axis += ((x_total_len)/len_adjust)
           
    x_axis = 30
    mycanvas.setFont('Helvetica', 10)
    grs_val = 0
    grs_cmsn = 0
    tds_ded = 0
    grs_ded = 0
    net_com = 0
    
    grs_val_x = 0
    grs_cmsn_x = 0
    tds_ded_x = 0
    grs_ded_x = 0
    net_com_x = 0
    
    for values in data_dict:
        mycanvas.drawCentredString(x_axis-10,y_axis-40,str(sl_no))
        mycanvas.line(x_axis+5,y_axis+20,x_axis+5,y_axis-60)
        for stock_name in data_dict[0]:
            if stock_name == list(data_dict[0].keys())[0]:
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawString(x_axis+35,y_axis-40,str(values[stock_name]))
            elif stock_name == 'Agent Code':
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawString(x_axis+35,y_axis-40,str(values[stock_name]))
                mycanvas.line(x_axis-5,y_axis+20,x_axis-5,y_axis-90)
            elif stock_name =='Agent Name':
                mycanvas.setFont('Helvetica', 8)
                mycanvas.drawString(x_axis-3,y_axis-40,str(values[stock_name][:12]).upper())
                mycanvas.line(x_axis-5,y_axis+20,x_axis-5,y_axis-90)
            elif stock_name == list(data_dict[0].keys())[-1]:
                mycanvas.drawRightString(x_axis+50,y_axis-40,str(values[stock_name]))
                mycanvas.line(x_axis-5,y_axis+20,x_axis-5,y_axis-90)
            else:
                mycanvas.drawRightString(x_axis+65,y_axis-40,str(values[stock_name]))
                mycanvas.line(x_axis-5,y_axis+20,x_axis-5,y_axis-90)


            if stock_name =='Gross Value':
                grs_val += values[stock_name]
                grs_val_x = x_axis+65
            elif stock_name == 'GrossCommission':
                grs_cmsn += values[stock_name]
                grs_cmsn_x = x_axis+65
            elif stock_name == 'TDS deduction':
                tds_ded += values[stock_name]
                tds_ded_x = x_axis+65
            elif stock_name == 'Gross Deduction':
                grs_ded += values[stock_name]
                grs_ded_x = x_axis+65
            elif stock_name == 'Net Commission':
                net_com += values[stock_name]
                net_com_x = x_axis+65

            mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-90)
            mycanvas.line(x_total_len+10,y_axis+20,x_total_len+10,y_axis-90)
            x_axis += ((x_total_len)/len_adjust)

        y_axis-=18
        if sl_no % 40 == 0:
           
            mycanvas.line(x_axis_line,y_axis-30,x_total_len+10,y_axis-30)
            mycanvas.showPage()
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica-Bold', 13)
            mycanvas.drawRightString(750, 795,"C1B")
     
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(550, 820,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 13)
            mycanvas.drawCentredString(550, 795, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)

            mycanvas.setDash(6,3)
            mycanvas.setLineWidth(0)

            x_total_len = 1060
            x_axis = 20
            x_axis_line = 10
            y_axis = 670+90
            y_axis_line = 690+30
            mycanvas.setFont('Helvetica', 10)
            mycanvas.drawCentredString(x_axis+5,y_axis,str("Sl."))
            mycanvas.drawCentredString(x_axis+5,y_axis-15,str("No"))
           
            mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
            mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)
           
            for stock_name in data_dict[0]:
                data_name = ""
                data_2nd_name = ""
                data = stock_name.split(" ")

                if data[0] == "" :
                    data.remove(data[0])

                if data[-1] == "":
                    data.remove(data[0])

                if len(data) == 1:
                    if data[0] == "GrossCommission":
                        data_name += "Gross"
                        data_2nd_name += "Commission"

                    elif data[0] == "BoothCodes":
                        data_name += "Booth"
                        data_2nd_name += "Codes"
                    else:
                        data_name += data[0]

                if len(data) == 2:
                    data_name += data[0]
                    data_2nd_name += data[1]

                if len(data) == 3:
                    data_name += data[0] + " " + data[1]
                    data_2nd_name += data[-1]

                if len(data) == 4:
                    data_name += data[0] + " " + data[1]
                    data_2nd_name += data[2]+ " " + data[3]
                if stock_name == list(data_dict[0].keys())[-1]:
                    mycanvas.drawCentredString(x_axis+33,y_axis,str(data_name))
                    mycanvas.drawCentredString(x_axis+33,y_axis-15,str(data_2nd_name))
                else:
                    mycanvas.drawCentredString(x_axis+48,y_axis,str(data_name))
                    mycanvas.drawCentredString(x_axis+48,y_axis-15,str(data_2nd_name))
                x_axis += ((x_total_len)/len_adjust)
               
        sl_no += 1
        x_axis = 30
    mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
    mycanvas.line(x_axis_line,y_axis-70,x_total_len+10,y_axis-70)
   
    mycanvas.drawCentredString(x_axis+50,y_axis-60,"G  R  A  N    T  O  T  A  L")
    
    mycanvas.drawRightString(grs_val_x,y_axis-60,str(grs_val))
    mycanvas.drawRightString(grs_cmsn_x,y_axis-60,str(grs_cmsn))
    mycanvas.drawRightString(tds_ded_x,y_axis-60,str(tds_ded))
    mycanvas.drawRightString(grs_ded_x,y_axis-60,str(grs_ded))
    mycanvas.drawRightString(net_com_x,y_axis-60,str(net_com))

   
    mycanvas.save()
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
    return document


def create_canvas_report_for_commission_report_slip_charge(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()
    data_dict = {}
    data_list = []
    date_list = []
    date_timestamp_list = pd.date_range(start=from_date, end=to_date)
    for dates in date_timestamp_list:
        date_list.append(str(dates.date()))
    sale_quantity_obj = DailySessionllyBusinessllySale.objects.filter(delivery_date__range=[from_date[:10], to_date[:10]])
    for commission_obj in MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date).order_by('business__zone','agent__agent_code'):
        agent_dict = {
            "zone" : commission_obj.business.zone.name,
            "id":commission_obj.id,
            "agent_code": commission_obj.agent.agent_code,
            "agent_name": commission_obj.agent.first_name,
            "cash_sale":0,
            "card_sale":0,
            "total_commission": 0,
            "net_commission": 0,
            "incom_tax": 0,
            "slip_cost": 0,
            "sale_of_period": "",
            "others": 0,
        }
        cash_sale_obj = sale_quantity_obj.filter(business_id=commission_obj.business.id, sold_to='Agent')
        card_sale_obj = sale_quantity_obj.filter(business_id=commission_obj.business.id, sold_to='ICustomer')
        total_comm = commission_obj.gross_comm
        net_commission = commission_obj.net_comm
        cash_sale = cash_sale_obj.aggregate(Sum('milk_litre'))['milk_litre__sum']
        card_sale = card_sale_obj.aggregate(Sum('milk_litre'))['milk_litre__sum']
        incom_tax = commission_obj.tds_deduction
        slip_cost = commission_obj.slip_charge


        if total_comm == None:
            total_comm = 0

        if cash_sale == None:
            cash_sale = 0

        if card_sale == None:
            card_sale = 0

        if incom_tax == None:
            incom_tax = 0

        if slip_cost == None:
            slip_cost = 0
        if net_commission == None:
            net_commission = 0
        
        agent_dict["total_commission"] = total_comm
        agent_dict["net_commission"] = net_commission
        agent_dict["cash_sale"] = cash_sale
        agent_dict["card_sale"] = card_sale
        agent_dict["incom_tax"] = incom_tax
        agent_dict["slip_cost"] = round(Decimal(slip_cost),2)

        data_list.append(agent_dict)
    data_dict["agent_data_list"] = data_list
    
    agent_commission_columns = []
    if MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=run_id).exists():
        agent_commission_columns = list(MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=run_id).values_list('column_name', flat=True))
#         if len(agent_commission_columns) == 1:
        for index, data in  enumerate(data_dict["agent_data_list"], start=0):
            if MonthlyAgentCommissionSubColumn.objects.filter(agent_commission_id=data['id']).exists():
                total_val = 0
                for sub_column in MonthlyAgentCommissionSubColumn.objects.filter(agent_commission_id=data['id']):
                    total_val += sub_column.value
                data_dict["agent_data_list"][index]["others"] = total_val
            else:
                for column in agent_commission_columns:
                    data_dict["agent_data_list"][index]["others"] = 0

    # data_dict["user_name"] = request.user.first_name
    
    file_name = 'milk_sale_commmission_report( '+ str(date_list[0])+"to"+str(date_list[-1])+ ' ).pdf'
#     file_path = os.path.join('static/media/zone_wise_report/', file_name)
    file_path = os.path.join('static/media/monthly_report', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    light_color = 0x9b9999
    dark_color = 0x000000
    mycanvas.setFont('Helvetica', 10)
    mycanvas.setLineWidth(0)
    x = 30
    y = 800
    sl_no = 1
    for data in data_dict["agent_data_list"]:
        if data["total_commission"] != 0:
            # string to date_time formate 
            from_date = datetime.datetime.strptime(date_list[0], '%Y-%m-%d')
            to_date = datetime.datetime.strptime(date_list[-1], '%Y-%m-%d')

            # date time format change to '%d/%m/%Y'
            from_date = datetime.datetime.strftime(from_date, '%d/%m/%Y')
            to_date = datetime.datetime.strftime(to_date, '%d/%m/%Y')

            mycanvas.drawCentredString(300, y+20,'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.drawCentredString(300, y-15+20,'Milk Sale Commission for the Period of '+str(from_date+ " to " + to_date) +"   "+"( "+data["zone"]+" )")
            mycanvas.drawString(x+10,y-20,"Agent Code : "+str(data["agent_code"]))
            mycanvas.drawString(x+330,y-20,"Agent Name : "+str(data["agent_name"]))

            # head_line
            mycanvas.drawCentredString(x+10,y-40,"Milk")
            mycanvas.drawCentredString(x+80,y-40,"Quantity")
            mycanvas.drawCentredString(x+80,y-55,"(Ltr)")

            mycanvas.drawCentredString(x+170,y-40,"Tot.Commission")
            mycanvas.drawCentredString(x+170,y-55,"Rs.Ps.")

            mycanvas.drawCentredString(x+330,y-40,"Deduction Amount")
            mycanvas.drawCentredString(x+330,y-55,"Rs.Ps.")
            mycanvas.drawCentredString(x+490,y-40,"Amount")
            mycanvas.drawCentredString(x+490,y-55,"Rs.Ps.")

            #content
            mycanvas.drawCentredString(x+10,y-80,"Cash")
            mycanvas.drawCentredString(x+10,y-100,"Card")

            mycanvas.drawRightString(x+115,y-80,str(data["cash_sale"]))
            mycanvas.drawRightString(x+115,y-95,str(data["card_sale"]))

            mycanvas.drawRightString(x+225,y-80,str(data["total_commission"]))

            mycanvas.drawString(x+240,y-80,"Slip Cost      : ")
            mycanvas.drawRightString(x+415,y-80,str(data["slip_cost"]))

            mycanvas.drawString(x+240,y-95,"Incom Tax    : ")
            mycanvas.drawRightString(x+415,y-95,str(data["incom_tax"]))

            mycanvas.drawString(x+240,y-110,"Sale of Prod : ")
            mycanvas.drawString(x+240,y-125,"Others          : ")
            mycanvas.drawRightString(x+415,y-125,str(data["others"]))

            mycanvas.drawString(x+430,y-80,"ERN : ")
            mycanvas.drawRightString(x+550,y-80,str(data["total_commission"]))
            mycanvas.drawString(x+430,y-95,"DED : ")
            mycanvas.drawRightString(x+550,y-95,str(data["incom_tax"]+data["slip_cost"]+data["others"]))

            mycanvas.drawString(x+430,y-125,"NET : ")
            mycanvas.drawRightString(x+550,y-125,str(data["net_commission"]))

            mycanvas.line(10,y-30,585,y-30)
            mycanvas.line(10,y-60,585,y-60)
            mycanvas.line(10,y-130,585,y-130)

            #lines
            mycanvas.line(10,y-30,10,y-130)
            mycanvas.line(585,y-30,585,y-130)

            mycanvas.line(x+40,y-30,x+40,y-130)
            mycanvas.line(x+120,y-30,x+120,y-130)
            mycanvas.line(x+230,y-30,x+230,y-130)
            mycanvas.line(x+420,y-30,x+420,y-130)
           
            mycanvas.drawString(x,y-150,"NS :    The Net Amount is Subject to Confirmation ")

            y -= 210
            if sl_no % 4 == 0:
                mycanvas.showPage()
                mycanvas.setFont('Helvetica', 10)
                mycanvas.setLineWidth(0)
                x = 30
                y = 800
            sl_no += 1
    mycanvas.save()
    
#     print(pd.DataFrame(data_dict))
    document = {}
    document['pdf_file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document


def create_canvas_report_for_c1_commission_report(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()

    # commission report
    monthly_agent_obj = MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date)
    monthly_agent_list = list(monthly_agent_obj.values_list('agent__agent_code','agent__first_name', 'agent__pan_number',
    'business__code', 'tm_cash_milk_sale','tm_card_milk_sale', 'sm_cash_milk_sale', 'sm_card_milk_sale',
    'fcm_cash_milk_sale', 'fcm_card_milk_sale', 'can_milk_sale','total_cash_milk_sale',
    'total_cash_milk_comm','total_card_milk_sale','total_card_milk_comm','gross_sale', 'gross_comm', 'tds_deduction',
                                          'insurance_deduction','slip_charge', 'gross_deduction', 'net_comm'))
    monthly_agent_column = ['Agent Code', 'Agent Name', 'Pan No','BoothCodes', 'TM Cash Milk', 'TM Card Milk',
                            ' SM Cash Milk ', 'SM Card Milk', 'FCM CashMilk', 'FCM Card Milk',
                            'Can Milk Cash Milk', 'Total Cash Milk ','Cash Milk commission', 'Total Card Milk',
                            'Card Milk commission', 'Gross Value', 'GrossCommission', ' TDS deduction', 'Insurance Deduction',
                            'Slip charges', 'Gross Deduction', 'Net Commission']
    monthly_agent_df = pd.DataFrame(monthly_agent_list,columns=monthly_agent_column)
    monthly_agent_df['TDS Percentage'] = monthly_agent_df.apply(lambda x: find_out_tds_percentage(x['Pan No'], global_config_dict['tds']['value']), axis=1)
    data_dict = monthly_agent_df.to_dict('r')
    df = pd.DataFrame(data_dict)
    df.drop (['Pan No','BoothCodes',' TDS deduction','Slip charges','Gross Deduction','Insurance Deduction','Net Commission','TDS Percentage'],inplace = True,axis=1)
    
    excel_file_name = 'commission_report_from_' + str(from_date) + '_to_' + str(to_date) + ".xlsx"
    excel_file_path = os.path.join('static/media/monthly_report/', excel_file_name)
    df.to_excel(excel_file_path)
    df_ex = pd.read_excel(excel_file_path)
    df_ex.drop("Unnamed: 0",inplace = True,axis=1)
    df_ex.index = df.index + 1
    df_ex.to_excel(excel_file_path)
    
    print(df_ex.dtypes)

   
    file_name = 'commission_report_from_' + str(from_date) + '_to_' + str(to_date) + ".pdf"
    file_path = os.path.join('static/media/monthly_report/', file_name)
   
    mycanvas = canvas.Canvas(file_path, pagesize=(15 * inch, 12 * inch))
    pdfmetrics.registerFont(TTFont('dot', 'dotmatrix.ttf'))
    light_color =0x000000
    dark_color = 0x000000
    print(from_date)
    from_date = datetime.datetime.strptime(from_date[:10], '%Y-%m-%d')
    report_for_month = str(from_date.strftime('%B'))
    report_for_year = str(from_date.year)
   
   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica-Bold', 15)
    mycanvas.drawString(1000, 740+80,"C1")
    mycanvas.setFont('dot', 15)
    mycanvas.drawCentredString(560, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
    mycanvas.drawCentredString(560, 720+80, 'Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawCentredString(560, 700+80, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)
   
    mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
   
    x_total_len = 1060
    x_axis = 40
    x_axis_line = 10
    y_axis = 670+60
    y_axis_line = 690+60
    sl_no = 1
    mycanvas.setFont('dot', 12)
    len_adjust=len(data_dict[1])-8
       
       
    mycanvas.drawCentredString(x_axis-10,y_axis,str("Sl.no"))
   
    mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
    mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)
   
   
   
    for stock_name in data_dict[0]:
        if stock_name == "Insurance Deduction" or stock_name == 'Pan No' or stock_name == "BoothCodes" or stock_name == ' TDS deduction' or stock_name == 'Slip charges' or stock_name == 'Gross Deduction' or stock_name == 'Net Commission' or stock_name == 'TDS Percentage':
            pass
        else:
            data_name = ""
            data_2nd_name = ""
            data = stock_name.split(" ")

            if data[0] == "" :
                data.remove(data[0])

            if data[-1] == "":
                data.remove(data[-1])
           
            if len(data) == 1:
                if data[0] == "GrossCommission":
                    data_name += "Gross"
                    data_2nd_name += "Commission"
                   
                elif data[0] == "BoothCodes":
                    data_name += "Booth"
                    data_2nd_name += "Codes"
                else:
                    data_name += data[0]

            if len(data) == 2:
                data_name += data[0]
                data_2nd_name += data[1]

            if len(data) == 3:
                data_name += data[0] + " " + data[1]
                data_2nd_name += data[-1]

            if len(data) == 4:
                data_name += data[0] + " " + data[1]
                data_2nd_name += data[2]+ " " + data[3]

            mycanvas.drawCentredString(x_axis+40,y_axis,str(data_name))
            mycanvas.drawCentredString(x_axis+40,y_axis-15,str(data_2nd_name))
            x_axis += (x_total_len/len_adjust)-2
           
    x_axis = 40
    mycanvas.setFont('dot', 10)
    tm_csh_mlk = 0
    tm_crd_mlk = 0
    sm_csh_mlk = 0
    sm_crd_mlk = 0
    fcm_csh_mlk = 0
    fcm_crd_mlk = 0
    cn_csh_mlk = 0
    tot_csh_mlk = 0
    csh_mlk_cmsn = 0
    tot_crd_mlk = 0
    crd_mlk_cmsn = 0
    grs_val = 0
    grs_cmsn = 0
    for values in data_dict:
        for stock_name in data_dict[0]:
            if stock_name == "Insurance Deduction" or stock_name == 'Pan No' or stock_name == "BoothCodes" or stock_name == ' TDS deduction' or stock_name == 'Slip charges' or stock_name == 'Gross Deduction' or stock_name == 'Net Commission' or stock_name == 'TDS Percentage':
                pass
            else:
                if stock_name == 'Agent Code':
                    mycanvas.drawCentredString(x_axis-10,y_axis-40,str(sl_no))
                    mycanvas.drawCentredString(x_axis+40,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20,x_axis+10,y_axis-60)
                elif stock_name =='Agent Name':
                    mycanvas.setFont('dot', 10)
                    x_axis -= 8
                    mycanvas.drawString(x_axis+10,y_axis-40,str(values[stock_name][:15]).upper())
                    mycanvas.line(x_axis+10-2,y_axis+20,x_axis+10-2,y_axis-60)
                    x_axis += 8
                elif stock_name =='BoothCodes':
                    mycanvas.drawString(x_axis+40,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20,x_axis+10,y_axis-90)
                elif stock_name =='GrossCommission':
                    mycanvas.drawRightString(x_axis+65,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20,x_axis+10,y_axis-90)
                else:
                    mycanvas.drawRightString(x_axis+75,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20,x_axis+10,y_axis-90)
                   
                if stock_name == 'TM Cash Milk':
                    tm_csh_mlk += values[stock_name]
                elif stock_name =='TM Card Milk':
                    tm_crd_mlk += values[stock_name]
                elif stock_name ==' SM Cash Milk ':
                    sm_csh_mlk += values[stock_name]
                elif stock_name =='SM Card Milk':
                    sm_crd_mlk += values[stock_name]
                elif stock_name =='FCM CashMilk':
                    fcm_csh_mlk += values[stock_name]
                elif stock_name =='FCM Card Milk':
                    fcm_crd_mlk += values[stock_name]
                elif stock_name =='Can Milk Cash Milk':
                    cn_csh_mlk += values[stock_name]
                elif stock_name =='Total Cash Milk ':
                    tot_csh_mlk += values[stock_name]
                elif stock_name =='Cash Milk commission':
                    csh_mlk_cmsn += values[stock_name]
                elif stock_name =='Total Card Milk':
                    tot_crd_mlk += values[stock_name]
                elif stock_name =='Card Milk commission':
                    crd_mlk_cmsn += values[stock_name]
                elif stock_name =='Gross Value':
                    grs_val += values[stock_name]
                elif stock_name == 'GrossCommission':
                    grs_cmsn += values[stock_name]
                   
                mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-90)
                mycanvas.line(x_total_len+10,y_axis+20,x_total_len+10,y_axis-90)
                x_axis += (x_total_len/len_adjust)-2

        y_axis-=20
        if sl_no % 34 == 0:
           
            mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
            mycanvas.showPage()
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica-Bold', 15)
            mycanvas.drawString(1000, 740+80,"C1")
            mycanvas.setFont('dot', 15)
            mycanvas.drawCentredString(560, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
            mycanvas.drawCentredString(560, 720+80, 'Pachapalayam, Coimbatore - 641 010')
            mycanvas.drawCentredString(560, 700+80, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)

            mycanvas.setDash(6,3)
            mycanvas.setLineWidth(0)

            x_total_len = 1060
            x_axis = 40
            x_axis_line = 10
            y_axis = 670+60
            y_axis_line = 690
            mycanvas.setFont('dot', 12)
            mycanvas.drawCentredString(x_axis-10,y_axis,str("Sl.no"))
           
            mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
            mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)
           
            for stock_name in data_dict[0]:
                if stock_name == "Insurance Deduction" or stock_name == 'Pan No' or stock_name == "BoothCodes" or stock_name == ' TDS deduction' or stock_name == 'Slip charges' or stock_name == 'Gross Deduction' or stock_name == 'Net Commission' or stock_name == 'TDS Percentage':
                    pass
                else:
                    data_name = ""
                    data_2nd_name = ""
                    data = stock_name.split(" ")

                    if data[0] == "" :
                        data.remove(data[0])

                    if data[-1] == "":
                        data.remove(data[0])

                    if len(data) == 1:
                        if data[0] == "GrossCommission":
                            data_name += "Gross"
                            data_2nd_name += "Commission"

                        elif data[0] == "BoothCodes":
                            data_name += "Booth"
                            data_2nd_name += "Codes"
                        else:
                            data_name += data[0]

                    if len(data) == 2:
                        data_name += data[0]
                        data_2nd_name += data[1]

                    if len(data) == 3:
                        data_name += data[0] + " " + data[1]
                        data_2nd_name += data[-1]

                    if len(data) == 4:
                        data_name += data[0] + " " + data[1]
                        data_2nd_name += data[2]+ " " + data[3]

                    mycanvas.drawCentredString(x_axis+40,y_axis,str(data_name))
                    mycanvas.drawCentredString(x_axis+40,y_axis-15,str(data_2nd_name))
                    x_axis += (x_total_len/len_adjust)-2
               
        sl_no += 1
        x_axis = 40
    mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
    mycanvas.line(x_axis_line,y_axis-70,x_total_len+10,y_axis-70)
   
    mycanvas.drawCentredString(x_axis+50,y_axis-60,"G  R  A  N    T  O  T  A  L")
   
    mycanvas.drawRightString(x_axis+212,y_axis-60,str(tm_csh_mlk))
    mycanvas.drawRightString(x_axis+212+((x_total_len/len_adjust)-2),y_axis-60,str(tm_crd_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*2),y_axis-60,str(sm_csh_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*3),y_axis-60,str(sm_crd_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*4),y_axis-60,str(fcm_csh_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*5),y_axis-60,str(fcm_crd_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*6),y_axis-60,str(cn_csh_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*7),y_axis-60,str(tot_csh_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*8),y_axis-60,str(csh_mlk_cmsn))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*9),y_axis-60,str(tot_crd_mlk))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*10),y_axis-60,str(crd_mlk_cmsn))
    mycanvas.drawRightString(x_axis+212+(((x_total_len/len_adjust)-2)*11),y_axis-60,str(grs_val))
    mycanvas.drawRightString(x_axis+203+(((x_total_len/len_adjust)-2)*12),y_axis-60,str(grs_cmsn))
   
   
    mycanvas.save()
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
    return document
    

def create_canvas_report_for_c2_commission_report(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()

    # commission report
    monthly_agent_for_bank_obj = MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date).order_by('agent__agent_code')
    monthly_agent_for_bank_list =list(monthly_agent_for_bank_obj.values_list('agent_id','agent__agent_code','agent__first_name', 'gross_sale', 'gross_comm','gross_deduction', 'net_comm'))
    monthly_agent_for_bank_column = ['agent_id','Agent Code', 'AgentName', 'Gross Value', 'Gross Commission', 'Gross Deduction', 'NetCommission',]
    monthly_agent_for_bank_df = pd.DataFrame(monthly_agent_for_bank_list,columns=monthly_agent_for_bank_column)
    agent_bank_obj = AgentBankDetail.objects.filter()
    agent_bank_list = list(agent_bank_obj.values_list('agent_id','account_holder_name', 'account_number','bank', 'branch','ifsc_code'))
    agent_bank_column = ['agent_id', 'Bank Account Name', 'Bank Accountnumber', 'Bank Name', 'Bank Branch', 'IFSC code']
    agent_bank_df = pd.DataFrame(agent_bank_list, columns=agent_bank_column)
    final_df =  monthly_agent_for_bank_df.merge(agent_bank_df, how='left',left_on='agent_id', right_on='agent_id')
    final_df = final_df.fillna('')
    data_dict = final_df.to_dict('r')
    df = pd.DataFrame(data_dict)
    df.drop(['Gross Value','Gross Commission','Gross Deduction','agent_id', 'Bank Account Name'], inplace=True, axis=1)
    
    
    reindex_column = ['Agent Code', 'AgentName', 'Bank Accountnumber', 'Bank Name', 'Bank Branch', 'IFSC code', 'NetCommission']
    
    df = df.reindex(columns=reindex_column)
    
    data_dict = df.to_dict('r')
    
    print(df.columns)
    excel_file_name = 'commission_report_c2_from_' + str(from_date) + '_to_' + str(to_date) + ".xlsx"
    
    excel_file_path = os.path.join('static/media/monthly_report/', excel_file_name)
    df.to_excel(excel_file_path, index=False)
    
    df.to_excel(excel_file_path)
    df_ex = pd.read_excel(excel_file_path)
    df_ex.drop("Unnamed: 0",inplace = True,axis=1)
    df_ex.index = df.index + 1
    data_dict = df_ex.to_dict('r')
    df_ex.to_excel(excel_file_path)
    
    from_date = datetime.datetime.strptime(from_date[:10], '%Y-%m-%d')
    report_for_month = str(from_date.strftime('%B'))
    report_for_year = str(from_date.year)

   
    file_name = 'commission_report_c2_from_' + str(from_date) + '_to_' + str(to_date) + ".pdf"
    file_path = os.path.join('static/media/monthly_report/', file_name)
   
    mycanvas = canvas.Canvas(file_path, pagesize=(15 * inch, 12 * inch))
    pdfmetrics.registerFont(TTFont('dot', 'dotmatrix.ttf'))
    light_color = 0x000000
    dark_color = 0x000000

   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica-Bold', 15)
    mycanvas.drawString(1000, 740+80,"C2")
    mycanvas.setFont('dot', 15)
    mycanvas.drawCentredString(560, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
    mycanvas.drawCentredString(560, 720+80, 'Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawCentredString(560, 700+80, 'Bank Details Report for '+report_for_month +' - '+report_for_year)
   
    mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
   
    x_total_len = 1060
    x_axis = 40
    x_axis_line = 10
    y_axis = 670+60
    y_axis_line = 690+60
    sl_no = 1
    mycanvas.setFont('dot', 12)
    len_adjust=len(data_dict[1])
       
       
    mycanvas.drawCentredString(x_axis-10,y_axis,str("Sl.no"))
   
    mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
    mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)
   
   
   
    for stock_name in data_dict[0]:
        mycanvas.setFont('dot', 14)
        if stock_name == 'Agent Code':
            mycanvas.drawCentredString(x_axis+60, y_axis, str(stock_name))
        elif stock_name == "AgentName":
            mycanvas.drawCentredString(x_axis,y_axis,str(stock_name))
        elif stock_name == "NetCommission":
            mycanvas.drawCentredString(x_axis+60,y_axis,str(stock_name))
        elif stock_name == "Bank Account Name":
            mycanvas.drawCentredString(x_axis,y_axis,str(stock_name))
        elif stock_name == "Bank Accountnumber":
            mycanvas.drawCentredString(x_axis+5,y_axis,str(stock_name))
        elif stock_name == "Bank Name":
            mycanvas.drawCentredString(x_axis+10,y_axis,str(stock_name))
        elif stock_name == "Bank Branch":
            mycanvas.drawCentredString(x_axis+60,y_axis,str(stock_name))
        elif stock_name == "IFSC code":
            mycanvas.drawCentredString(x_axis+60,y_axis,str(stock_name))
        else:
            mycanvas.drawCentredString(x_axis+40,y_axis,str(stock_name))
        x_axis += (x_total_len/len_adjust) - 2
           
    x_axis = 40
    mycanvas.setFont('dot', 12)
   
    for values in data_dict:
        
        for stock_name in data_dict[0]:
            if stock_name == 'Gross Value' or stock_name == 'Gross Commission' or stock_name == 'Gross Deduction' :
                pass
            else:
                if stock_name == "Agent Code":
                    mycanvas.setFont('dot', 12)
                    mycanvas.drawCentredString(x_axis-10,y_axis-40,str(sl_no))
                    mycanvas.drawString(x_axis+20,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis+5,y_axis+20,x_axis+5,y_axis-60)
                    
                elif stock_name == "AgentName":
                    mycanvas.setFont('dot', 12)
                    mycanvas.drawString(x_axis-40,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis-50,y_axis+20,x_axis-50,y_axis-60)
                    
                elif stock_name == "Bank Accountnumber":
                    mycanvas.setFont('dot', 12)
                    mycanvas.drawString(x_axis-50,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis-60,y_axis+20,x_axis-60,y_axis-60)
                    
                elif stock_name == "Bank Name":
                    mycanvas.setFont('dot', 12)
                    mycanvas.drawString(x_axis-75,y_axis-40,str(values[stock_name]).lower())
                    mycanvas.line(x_axis-80,y_axis+20,x_axis-80,y_axis-60)
                    
                elif stock_name == "Bank Branch":
                    mycanvas.setFont('dot', 12)
                    mycanvas.drawString(x_axis-10,y_axis-40,str(values[stock_name]).lower())
                    mycanvas.line(x_axis-20,y_axis+20,x_axis-20,y_axis-60)
                   
                elif stock_name == "NetCommission":
                    mycanvas.setFont('dot', 12)
                    mycanvas.drawRightString(x_axis+100,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis,y_axis+20,x_axis,y_axis-60)
                   
                else:
                    mycanvas.setFont('dot', 12)
                    mycanvas.drawString(x_axis+40,y_axis-40,str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20,x_axis+10,y_axis-60)
               
                mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-60)
                mycanvas.line(x_total_len+10,y_axis+20,x_total_len+10,y_axis-60)
                x_axis += (x_total_len/len_adjust)-2
               
               
               
        y_axis-=20
        if sl_no % 34 == 0:
           
            mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
            mycanvas.showPage()
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica-Bold', 15)
            mycanvas.drawString(1000, 740+80,"C2")
            mycanvas.setFont('dot', 15)
            mycanvas.drawCentredString(560, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
            mycanvas.drawCentredString(560, 720+80, 'Pachapalayam, Coimbatore - 641 010')
            mycanvas.drawCentredString(560, 700+80, 'Bank Details Report for '+report_for_month +' - '+report_for_year)

            mycanvas.setDash(6,3)
            mycanvas.setLineWidth(0)

            x_total_len = 1060
            x_axis = 40
            x_axis_line = 10
            y_axis = 670+60
            y_axis_line = 690
            mycanvas.setFont('dot', 12)
            mycanvas.drawCentredString(x_axis-10,y_axis,str("Sl.no"))
           
            mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
            mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)
            
            for stock_name in data_dict[0]:
                mycanvas.setFont('dot', 14)
                if stock_name == 'Agent Code':
                    mycanvas.drawCentredString(x_axis+60, y_axis, str(stock_name))
                elif stock_name == "AgentName":
                    mycanvas.drawCentredString(x_axis,y_axis,str(stock_name))
                elif stock_name == "NetCommission":
                    mycanvas.drawCentredString(x_axis+60,y_axis,str(stock_name))
                elif stock_name == "Bank Account Name":
                    mycanvas.drawCentredString(x_axis,y_axis,str(stock_name))
                elif stock_name == "Bank Accountnumber":
                    mycanvas.drawCentredString(x_axis+5,y_axis,str(stock_name))
                elif stock_name == "Bank Name":
                    mycanvas.drawCentredString(x_axis+10,y_axis,str(stock_name))
                elif stock_name == "Bank Branch":
                    mycanvas.drawCentredString(x_axis+60,y_axis,str(stock_name))
                elif stock_name == "IFSC code":
                    mycanvas.drawCentredString(x_axis+60,y_axis,str(stock_name))
                else:
                    mycanvas.drawCentredString(x_axis+40,y_axis,str(stock_name))
                x_axis += (x_total_len/len_adjust) - 2
       
        sl_no += 1
        x_axis = 40
    mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
    mycanvas.save()
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
    return document


def create_canvas_report_for_c3_commission_report(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()

    # commission report
    monthly_agent_obj = MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date)
    monthly_agent_list = list(monthly_agent_obj.values_list('id','agent__agent_code','agent__first_name', 'agent__pan_number',
    'business__code', 'tm_cash_milk_sale','tm_card_milk_sale', 'sm_cash_milk_sale', 'sm_card_milk_sale',
    'fcm_cash_milk_sale', 'fcm_card_milk_sale', 'can_milk_sale','total_cash_milk_sale',
    'total_cash_milk_comm','total_card_milk_sale','total_card_milk_comm','gross_sale', 'gross_comm', 'tds_deduction',
                                          'insurance_deduction','slip_charge', 'gross_deduction', 'net_comm'))
    monthly_agent_column = ['id','Agent Code', 'Agent Name', 'Pan No','BoothCodes', 'TM Cash Milk', 'TM Card Milk',
                            ' SM Cash Milk ', 'SM Card Milk', 'FCM CashMilk', 'FCM Card Milk',
                            'Can Milk Cash Milk', 'Total Cash Milk ','Cash Milk commission', 'Total Card Milk',
                            'Card Milk commission', 'Gross Value', 'GrossCommission', ' TDS deduction', 'Insurance Deduction',
                            'Slip charges', 'Gross Deduction', 'Net Commission']
    monthly_agent_df = pd.DataFrame(monthly_agent_list,columns=monthly_agent_column)
    monthly_agent_df['TDS Percentage'] = monthly_agent_df.apply(lambda x: find_out_tds_percentage(x['Pan No'], global_config_dict['tds']['value']), axis=1)
    data_dict = monthly_agent_df.to_dict('r')
    agent_commission_columns = []
    if MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=run_id).exists():
      agent_commission_columns = list(MonthlyAgentCommissionRunColumnCv.objects.filter(run_id=run_id).values_list('column_name', flat=True))
      for index, data in  enumerate(data_dict, start=0):
          if MonthlyAgentCommissionSubColumn.objects.filter(agent_commission_id=data['id']).exists():
              for sub_column in MonthlyAgentCommissionSubColumn.objects.filter(agent_commission_id=data['id']):
                  data_dict[index][sub_column.column.column_name] = sub_column.value
          else:
              for column in agent_commission_columns:
                  data_dict[index][column] = 0
    df = pd.DataFrame(data_dict)
    df.drop (['id', 'Pan No','BoothCodes','TM Cash Milk','TM Card Milk',' SM Cash Milk ','SM Card Milk','FCM CashMilk','FCM Card Milk',
          'Can Milk Cash Milk','Total Cash Milk ','Cash Milk commission','Total Card Milk','Card Milk commission',
          'Gross Value','GrossCommission','Insurance Deduction','Net Commission','TDS Percentage'],inplace = True,axis=1)
    column_titles = ['Agent Code','Agent Name',' TDS deduction','Slip charges']
    last_column = ['Gross Deduction']
    final_column = column_titles + agent_commission_columns + last_column
    df = df.reindex(columns=final_column)
    excel_file_name = 'commission_report_c3_from_' + str(from_date) + '_to_' + str(to_date) + ".xlsx"
    excel_file_path = os.path.join('static/media/monthly_report/', excel_file_name)
    df.to_excel(excel_file_path)

    data_dict = df.to_dict('r')
    file_name = 'commission_report_c3_from_' + str(from_date) + '_to_' + str(to_date) + ".pdf"
    file_path = os.path.join('static/media/monthly_report/', file_name)
    
    df.to_excel(excel_file_path)
    df_ex = pd.read_excel(excel_file_path)
    df_ex.drop("Unnamed: 0",inplace = True,axis=1)
    df_ex.index = df.index + 1
    df_ex.to_excel(excel_file_path)
    
   
    mycanvas = canvas.Canvas(file_path, pagesize=(10 * inch, 12 * inch))
    pdfmetrics.registerFont(TTFont('dot', 'dotmatrix.ttf'))
    light_color = 0x9b9999
    dark_color = 0x000000

    from_date = datetime.datetime.strptime(from_date[:10], '%Y-%m-%d')
    report_for_month = str(from_date.strftime('%B'))
    report_for_year = str(from_date.year)
   
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('Helvetica-Bold', 15)
    mycanvas.drawString(650, 740+80,"C3")
    mycanvas.setFont('dot', 15)
    mycanvas.drawCentredString(350, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
    mycanvas.drawCentredString(350, 720+80, 'Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawCentredString(350, 700+80, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)
   
    mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
   
    x_total_len = 700
    x_axis = 40
    x_axis_line = 10
    y_axis = 670+60
    y_axis_line = 690+60
    sl_no = 1
    mycanvas.setFont('dot', 12)
    len_adjust=len(data_dict[1])
       
       
    mycanvas.drawCentredString(x_axis-20,y_axis,str("Sl"))
    mycanvas.drawCentredString(x_axis-20,y_axis-15,str(".no"))
   
    mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
    mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)
   
   
   
    for stock_name in data_dict[0]:
        
        data_name = ""
        data_2nd_name = ""
        data = stock_name.split(" ")

        if data[0] == "" :
            data.remove(data[0])

        if data[-1] == "":
            data.remove(data[-1])

        if len(data) == 1:
            if data[0] == "GrossCommission":
                data_name += "Total"
                data_2nd_name += "Earnings"
            else:
                data_name += data[0]

        if len(data) == 2:
            data_name += data[0]
            data_2nd_name += data[1]

        if len(data) == 3:
            data_name += data[0] + " " + data[1]
            data_2nd_name += data[-1]

        if len(data) == 4:
            data_name += data[0] + " " + data[1]
            data_2nd_name += data[2]+ " " + data[3]

        mycanvas.drawCentredString(x_axis+20,y_axis,str(data_name))
        mycanvas.drawCentredString(x_axis+20,y_axis-15,str(data_2nd_name))
        x_axis += (x_total_len/len_adjust)
           
           
    x_axis = 30
    mycanvas.setFont('dot', 10)
    
    tds_ded = 0
    slp_crg = 0
    grs_ded = 0
    
    tds_ded_x = 0
    slp_crg_x = 0
    grs_ded_x = 0
   
    for values in data_dict:
        mycanvas.drawCentredString(x_axis-10,y_axis-40,str(sl_no))
        mycanvas.line(x_axis,y_axis+20,x_axis,y_axis-60)
        for stock_name in data_dict[0]:
            
            if stock_name == list(data_dict[0].keys())[0]:
                mycanvas.drawString(x_axis+20,y_axis-40,str(values[stock_name]))
            elif stock_name == 'Agent Code':
                mycanvas.drawCentredString(x_axis+20,y_axis-40,str(values[stock_name]))
                mycanvas.line(x_axis-20,y_axis+20,x_axis-20,y_axis-60)
            elif stock_name =='Agent Name':
                mycanvas.setFont('dot', 10)
                mycanvas.drawString(x_axis-15,y_axis-40,str(values[stock_name][:15]).upper())
                mycanvas.line(x_axis-20,y_axis+20,x_axis-20,y_axis-60)
            else:
                mycanvas.drawRightString(x_axis+45,y_axis-40,str(values[stock_name]))
                mycanvas.line(x_axis-20,y_axis+20,x_axis-20,y_axis-90)
                

            if stock_name == 'Slip charges':
                slp_crg += values[stock_name]
                slp_crg_x = x_axis+45
            if stock_name ==' TDS deduction':
                tds_ded += values[stock_name]
                tds_ded_x = x_axis+45
            if stock_name =='Gross Deduction':
                grs_ded += values[stock_name]
                grs_ded_x = x_axis+45
                
            mycanvas.line(x_axis_line,y_axis+20,x_axis_line,y_axis-90)
            mycanvas.line(x_total_len+10,y_axis+20,x_total_len+10,y_axis-90)
            x_axis += (x_total_len/len_adjust)
               
               
               
        y_axis-=20
        if sl_no % 34 == 0:
           
            mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
            mycanvas.showPage()
            mycanvas.setFillColor(HexColor(dark_color))
            mycanvas.setFont('Helvetica-Bold', 15)
            mycanvas.drawString(650, 740+80,"C3")
            mycanvas.setFont('dot', 15)
            mycanvas.drawCentredString(350, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
            mycanvas.drawCentredString(350, 720+80, 'Pachapalayam, Coimbatore - 641 010')
            mycanvas.drawCentredString(350, 700+80, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)

            mycanvas.setDash(6,3)
            mycanvas.setLineWidth(0)

            x_total_len = 700
            x_axis = 40
            x_axis_line = 10
            y_axis = 670+60
            y_axis_line = 690
            mycanvas.setFont('dot', 12)
            mycanvas.drawCentredString(x_axis-20,y_axis,str("Sl"))
            mycanvas.drawCentredString(x_axis-20,y_axis-15,str(".no"))
           
            mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
            mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)
           
            for stock_name in data_dict[0]:
                
                data_name = ""
                data_2nd_name = ""
                data = stock_name.split(" ")

                if data[0] == "" :
                    data.remove(data[0])

                if data[-1] == "":
                    data.remove(data[-1])

                if len(data) == 1:
                    if data[0] == "GrossCommission":
                        data_name += "Total"
                        data_2nd_name += "Earnings"
                    else:
                        data_name += data[0]

                if len(data) == 2:
                    data_name += data[0]
                    data_2nd_name += data[1]

                if len(data) == 3:
                    data_name += data[0] + " " + data[1]
                    data_2nd_name += data[-1]

                if len(data) == 4:
                    data_name += data[0] + " " + data[1]
                    data_2nd_name += data[2]+ " " + data[3]

                mycanvas.drawCentredString(x_axis+20,y_axis,str(data_name))
                mycanvas.drawCentredString(x_axis+20,y_axis-15,str(data_2nd_name))
                x_axis += (x_total_len/len_adjust)
               
        sl_no += 1
        x_axis = 30
    mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
    mycanvas.line(x_axis_line,y_axis-70,x_total_len+10,y_axis-70)
   
    mycanvas.drawCentredString(x_axis+100,y_axis-60,"G  R  A  N    T  O  T  A  L")
   
#     mycanvas.drawRightString(x_axis+212,y_axis-60,str(tm_csh_mlk))

    mycanvas.drawRightString(tds_ded_x,y_axis-60,str(tds_ded))
    mycanvas.drawRightString(slp_crg_x,y_axis-60,str(slp_crg))
    mycanvas.drawRightString(grs_ded_x,y_axis-60,str(grs_ded))
   
   
    mycanvas.save()
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
    return document


def create_canvas_report_for_c4_commission_report(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']
    
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()

    # commission report
    monthly_agent_obj = MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date)
    monthly_agent_list = list(monthly_agent_obj.values_list('agent__agent_code','agent__first_name', 'agent__pan_number',
    'business__code', 'tm_cash_milk_sale','tm_card_milk_sale', 'sm_cash_milk_sale', 'sm_card_milk_sale',
    'fcm_cash_milk_sale', 'fcm_card_milk_sale', 'can_milk_sale','total_cash_milk_sale',
    'total_cash_milk_comm','total_card_milk_sale','total_card_milk_comm','gross_sale', 'gross_comm', 'tds_deduction',
                                          'insurance_deduction','slip_charge', 'gross_deduction', 'net_comm'))
    monthly_agent_column = ['Agent Code', 'Agent Name', 'Pan No','BoothCodes', 'TM Cash Milk', 'TM Card Milk',
                            ' SM Cash Milk ', 'SM Card Milk', 'FCM CashMilk', 'FCM Card Milk',
                            'Can Milk Cash Milk', 'Total Cash Milk ','Cash Milk commission', 'Total Card Milk',
                            'Card Milk commission', 'Gross Value', 'GrossCommission', ' TDS deduction', 'Insurance Deduction',
                            'Slip charges', 'Gross Deduction', 'Net Commission']
    monthly_agent_df = pd.DataFrame(monthly_agent_list,columns=monthly_agent_column)
    monthly_agent_df['TDS Percentage'] = monthly_agent_df.apply(lambda x: find_out_tds_percentage(x['Pan No'], global_config_dict['tds']['value']), axis=1)
    data_dict = monthly_agent_df.to_dict('r')
    df = pd.DataFrame(data_dict)

    df.drop (['BoothCodes','TM Cash Milk','TM Card Milk',' SM Cash Milk ','SM Card Milk','FCM CashMilk','FCM Card Milk',
          'Can Milk Cash Milk','Total Cash Milk ','Cash Milk commission','Total Card Milk','Card Milk commission',
          'Gross Value','Insurance Deduction','Net Commission','Gross Deduction','Slip charges'],inplace = True,axis=1)
   

    columns_titles = ['Agent Code','Agent Name','Pan No','GrossCommission','TDS Percentage',' TDS deduction']
    df = df.reindex(columns=columns_titles)
    df['Total TDS Paid'] = df[' TDS deduction']
    df.rename(columns = {'GrossCommission':'Total Earnings'}, inplace = True)
    excel_file_name = 'commission_report_c4_from_' + str(from_date) + '_to_' + str(to_date) + ".xlsx"
    excel_file_path = os.path.join('static/media/monthly_report/', excel_file_name)
    df.to_excel(excel_file_path)
    
    df_ex = pd.read_excel(excel_file_path)
    df_ex.drop("Unnamed: 0",inplace = True,axis=1)
    df_ex.index = df.index + 1
    
    df_ex = df_ex.sort_values('TDS Percentage',ascending=False)
    df_ex['TDS Percentage'] = df_ex['TDS Percentage'].astype(str)
    df1 = df_ex[(df_ex['TDS Percentage'] == '20') | (df_ex['Pan No'] == '0') | (df_ex['Pan No'] == 0)]
    df1 = df1.fillna('')
    df1['Pan No'] = ''
    df1['TDS Percentage'] = 20
    df1.reset_index(inplace=True)
    df1.drop("index",inplace = True,axis=1)
    df1.index = df1.index + 1
    data_dict1 = df1.to_dict('r')
    
    df2 = df_ex[(df_ex['TDS Percentage'] == global_config_dict['tds']['value']) & (df_ex['Pan No'] != '0') & (df_ex['Pan No'] != 0)]
    df2.reset_index(inplace=True)
    df2.drop("index",inplace = True,axis=1)
    df2.index = df2.index + 1
    df2.fillna('-')
    print("----------------", df2.shape[0])
    data_dict2 = df2.to_dict('r')
    print(data_dict1)
    print()
    print('--------------------------------------------------------------------------------')
    print()
    print(data_dict2)

    
    with pd.ExcelWriter(excel_file_path) as writer:  
        df1.to_excel(writer, sheet_name='Members Without Pancard', index=True)
        df2.to_excel(writer, sheet_name='Members With Pancard', index=True)
         
    file_name = 'commission_report_c4_from_' + str(from_date) + '_to_' + str(to_date) + ".pdf"
    file_path = os.path.join('static/media/monthly_report/', file_name)
   
    mycanvas = canvas.Canvas(file_path, pagesize=(10 * inch, 12 * inch))
    pdfmetrics.registerFont(TTFont('dot', 'dotmatrix.ttf'))
    light_color = 0x9b9999
    dark_color = 0x000000

    
    from_date = datetime.datetime.strptime(from_date[:10], '%Y-%m-%d')
    report_for_month = str(from_date.strftime('%B'))
    report_for_year = str(from_date.year)
   
    data_dict_list = [data_dict1,data_dict2]
    
    for data_dict in data_dict_list:
        if data_dict == data_dict_list[0]:
            title = "Customer Without PanCard"
        else:
            title = "Customer With PanCard"
        mycanvas.setFillColor(HexColor(dark_color))
        mycanvas.setFont('Helvetica-Bold', 15)
        mycanvas.drawString(650, 740+80,"C4")
        mycanvas.setFont('dot', 15)
        mycanvas.drawCentredString(350, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
        mycanvas.drawCentredString(350, 720+80, 'Pachapalayam, Coimbatore - 641 010')
        mycanvas.drawCentredString(350, 700+80, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)
        mycanvas.drawCentredString(350, 680+80, title)

        mycanvas.setDash(6,3)
        mycanvas.setLineWidth(0)

        x_total_len = 700
        x_axis = 40
        x_axis_line = 10
        y_axis = 670+60
        y_axis_line = 690+60
        sl_no = 1
        mycanvas.setFont('dot', 12)
        len_adjust=len(data_dict[0])
        print(len_adjust)


        mycanvas.drawCentredString(x_axis-10, y_axis, str("Sl.no"))

        mycanvas.line(x_axis_line,y_axis+20, x_total_len+10, y_axis+20)
        mycanvas.line(x_axis_line,y_axis-20, x_total_len+10, y_axis-20)



        for stock_name in data_dict[0]:
            data_name = ""
            data_2nd_name = ""
            data = stock_name.split(" ")

            if data[0] == "" :
                data.remove(data[0])

            if data[-1] == "":
                data.remove(data[-1])

            if len(data) == 1:
                if data[0] == "GrossCommission":
                    data_name += "Total"
                    data_2nd_name += "Earnings"

            if len(data) == 2:

                data_name += data[0]
                data_2nd_name += data[1]

            if len(data) == 3:
                if stock_name == 'Total TDS Paid':
                    x_axis -= 20
                data_name += data[0] + " " + data[1]
                data_2nd_name += data[-1]

            if len(data) == 4:
                data_name += data[0] + " " + data[1]
                data_2nd_name += data[2]+ " " + data[3]

            if stock_name == 'Pan No' or stock_name == 'GrossCommission':
                mycanvas.drawCentredString(x_axis+60, y_axis, str(data_name))
                mycanvas.drawCentredString(x_axis+60, y_axis-15, str(data_2nd_name))
            elif stock_name == 'Agent Code' or stock_name == 'Agent Name':
                mycanvas.drawCentredString(x_axis+50, y_axis, str(data_name))
                mycanvas.drawCentredString(x_axis+50, y_axis-15, str(data_2nd_name))
            else:
                mycanvas.drawCentredString(x_axis+60, y_axis, str(data_name))
                mycanvas.drawCentredString(x_axis+60, y_axis-15, str(data_2nd_name))
            x_axis += (x_total_len/len_adjust)-2

        x_axis = 40
        mycanvas.setFont('dot', 10)
        tds_ded = 0
        tds_prs = 0
        grs_cmsn = 0

        for values in data_dict:
            for stock_name in data_dict[0]:
                if stock_name == 'Agent Code':
                    mycanvas.drawCentredString(x_axis-10, y_axis-40, str(sl_no))
                    mycanvas.drawCentredString(x_axis+40, y_axis-40, str(values[stock_name]))
                    mycanvas.line(x_axis+10, y_axis+20, x_axis+10, y_axis-60)
                elif stock_name =='Agent Name':
                    mycanvas.setFont('dot', 10)
                    x_axis -= 8
                    mycanvas.drawString(x_axis+10, y_axis-40, str(values[stock_name][:15]).upper())
                    mycanvas.line(x_axis, y_axis+20, x_axis, y_axis-60)
                    x_axis += 8
                elif stock_name =='Pan No':
                    if values[stock_name] == None or values[stock_name] == '':
                        mycanvas.drawString(x_axis+40, y_axis-40, str("-"))
                    else :
                        mycanvas.drawString(x_axis+40, y_axis-40, str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20, x_axis+10, y_axis-60)
                elif stock_name == 'Total Earnings':
                    grs_cmsn += values[stock_name]
                    mycanvas.drawRightString(x_axis+100, y_axis-40, str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20, x_axis+10, y_axis-90)
                elif stock_name == ' TDS deduction':
                    tds_ded += values[stock_name]
                    mycanvas.drawRightString(x_axis+(x_total_len/len_adjust)-2, y_axis-40, str(values[stock_name]))
                    mycanvas.drawRightString(x_axis+172+(x_total_len/len_adjust)-2, y_axis-40, str(values[stock_name]))
                    mycanvas.line(x_axis+10, y_axis+20, x_axis+10, y_axis-90)
                    mycanvas.line(x_axis+180, y_axis+20, x_axis+180, y_axis-90)
                elif stock_name == 'TDS Percentage':
                    mycanvas.drawRightString(x_axis+75-2, y_axis-40, str(values[stock_name]))
                    mycanvas.line(x_axis+10, y_axis+20, x_axis+10, y_axis-90)
                else:
                    mycanvas.drawRightString(x_axis+75, y_axis-40, str(values[stock_name]))
                    mycanvas.line(x_axis+10,y_axis+20, x_axis+10, y_axis-90)


                mycanvas.line(x_axis_line, y_axis+20, x_axis_line, y_axis-90)
                mycanvas.line(x_total_len+10, y_axis+20, x_total_len+10, y_axis-90)
                x_axis += (x_total_len/len_adjust) - 2



            y_axis-=20
            if sl_no % 33 == 0:

                mycanvas.line(x_axis_line, y_axis-40, x_total_len+10, y_axis-40)
                mycanvas.showPage()
                mycanvas.setFillColor(HexColor(dark_color))
                mycanvas.setFont('Helvetica-Bold', 15)
                mycanvas.drawString(650, 740+80, "C4")
                mycanvas.setFont('dot', 15)
                mycanvas.drawCentredString(350, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
                mycanvas.drawCentredString(350, 720+80, 'Pachapalayam, Coimbatore - 641 010')
                mycanvas.drawCentredString(350, 700+80, 'Booth Commission Report for '+report_for_month +' - '+report_for_year)
                mycanvas.drawCentredString(350, 680+80, title)

                mycanvas.setDash(6,3)
                mycanvas.setLineWidth(0)

                x_total_len = 700
                x_axis = 40
                x_axis_line = 10
                y_axis = 670+60
                y_axis_line = 690
                mycanvas.setFont('dot', 12)
                mycanvas.drawCentredString(x_axis-10,y_axis,str("Sl.no"))

                mycanvas.line(x_axis_line,y_axis+20,x_total_len+10,y_axis+20)
                mycanvas.line(x_axis_line,y_axis-20,x_total_len+10,y_axis-20)

                for stock_name in data_dict[0]:
                    data_name = ""
                    data_2nd_name = ""
                    data = stock_name.split(" ")

                    if data[0] == "" :
                        data.remove(data[0])

                    if data[-1] == "":
                        data.remove(data[-1])

                    if len(data) == 1:
                        if data[0] == "GrossCommission":
                            data_name += "Total"
                            data_2nd_name += "Earnings"

                    if len(data) == 2:

                        data_name += data[0]
                        data_2nd_name += data[1]

                    if len(data) == 3:
                        if stock_name == 'Total TDS Paid':
                            x_axis -= 20
                        data_name += data[0] + " " + data[1]
                        data_2nd_name += data[-1]

                    if len(data) == 4:
                        data_name += data[0] + " " + data[1]
                        data_2nd_name += data[2]+ " " + data[3]

                    if stock_name == 'Pan No' or stock_name == 'GrossCommission':
                        mycanvas.drawCentredString(x_axis+60,y_axis,str(data_name))
                        mycanvas.drawCentredString(x_axis+60,y_axis-15,str(data_2nd_name))
                    elif stock_name == 'Agent Code' or stock_name == 'Agent Name':
                        mycanvas.drawCentredString(x_axis+50,y_axis,str(data_name))
                        mycanvas.drawCentredString(x_axis+50,y_axis-15,str(data_2nd_name))
                    else:
                        mycanvas.drawCentredString(x_axis+60,y_axis,str(data_name))
                        mycanvas.drawCentredString(x_axis+60,y_axis-15,str(data_2nd_name))
                    x_axis += (x_total_len/len_adjust)-2

                mycanvas.drawCentredString(x_axis+40+(x_total_len/len_adjust)-2,y_axis,"Total TDS")
                mycanvas.drawCentredString(x_axis+40+(x_total_len/len_adjust)-2,y_axis-15,"Paid")

            sl_no += 1
            x_axis = 40
        mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
        mycanvas.line(x_axis_line,y_axis-70,x_total_len+10,y_axis-70)

        mycanvas.drawCentredString(x_axis+100,y_axis-60,"G  R  A  N    T  O  T  A  L")

    #     mycanvas.drawRightString(x_axis+212,y_axis-60,str(tm_csh_mlk))
        mycanvas.drawRightString(x_axis+295+((x_total_len/len_adjust)-2),y_axis-60,str(grs_cmsn))
        mycanvas.drawRightString(x_axis+(((x_total_len/len_adjust)-2)*6),y_axis-60,str(tds_ded))
        mycanvas.drawRightString(x_axis+(((x_total_len/len_adjust)-2)*7 -22),y_axis-60,str(tds_ded))
        
        mycanvas.showPage()
   
    mycanvas.save()
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
    return document



def create_canvas_report_for_c5_commission_report(monthly_run_obj):
    from_date = monthly_run_obj['run_from']
    to_date = monthly_run_obj['run_to']
    split = monthly_run_obj['split']
    run_id = monthly_run_obj['id']
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()
    data_dict = {
        "commission" : {
            "PLACE":"COIMBATORE",
            "COMM RATE": 4.1,
            "COMM QTY": 0,
            "COMM VALUE": 0,
            "TOAL DEDECTUON": 0,
            "TOTAL PAYMENT": 0
        },
        "center_content" : {
            "tm_litre":0,
            "tm_cost":0,
            "sm_liter":0,
            "sm_cost":0,
            "fcm_liter":0,
            "fcm_cost":0
        },
        "down_content" : {
            "sundry_debtor":0,
            "slip_cost":0,
            "incomtax" :0,
            "others" : 0,
        }
    }
    #for other value
    other_val_obj = MonthlyAgentCommissionSubColumn.objects.filter(column__run_id=run_id)
    other_value = other_val_obj.aggregate(Sum("value"))["value__sum"]
    data_dict["down_content"]["others"] = other_value
   
    agent_commission_obj = MonthlyAgentCommission.objects.filter(run_id=run_id, run__split=split, run__run_from=from_date, run__run_to=to_date)
   
    data_dict["commission"]["COMM VALUE"] = agent_commission_obj.aggregate(Sum("gross_comm"))["gross_comm__sum"]
    data_dict["commission"]["TOAL DEDECTUON"] = agent_commission_obj.aggregate(Sum("gross_deduction"))["gross_deduction__sum"]
    data_dict["commission"]["TOTAL PAYMENT"] = agent_commission_obj.aggregate(Sum("net_comm"))["net_comm__sum"]
   
   
    business_obj = DailySessionllyBusinessllySale.objects.filter(business_type_id__in=[1,2], delivery_date__range=[from_date[:10], to_date[:10]])
   
    tm500_sale = business_obj.aggregate(Sum('tm500_litre'))['tm500_litre__sum']
    std250_sale = business_obj.aggregate(Sum('std250_litre'))["std250_litre__sum"]
    std500_sale = business_obj.aggregate(Sum('std500_litre'))["std500_litre__sum"]
    fcm500_sale = business_obj.aggregate(Sum('fcm500_litre'))["fcm500_litre__sum"]
    fcm1000_sale = business_obj.aggregate(Sum('fcm1000_litre'))["fcm1000_litre__sum"]
   
    tmcan_sale = business_obj.aggregate(Sum('tmcan_litre'))["tmcan_litre__sum"]
    smcan_sale = business_obj.aggregate(Sum('smcan_litre'))["smcan_litre__sum"]
    fcmcan_sale = business_obj.aggregate(Sum('fcmcan_litre'))["fcmcan_litre__sum"]

    tm500_sale_cost = business_obj.aggregate(Sum('tm500_cost'))['tm500_cost__sum']
    std250_sale_cost = business_obj.aggregate(Sum('std250_cost'))["std250_cost__sum"]
    std500_sale_cost = business_obj.aggregate(Sum('std500_cost'))["std500_cost__sum"]
    fcm500_sale_cost = business_obj.aggregate(Sum('fcm500_cost'))["fcm500_cost__sum"]
    fcm1000_sale_cost = business_obj.aggregate(Sum('fcm1000_cost'))["fcm1000_cost__sum"]
   
    tmcan_sale_cost = business_obj.aggregate(Sum('tmcan_cost'))["tmcan_cost__sum"]
    smcan_sale_cost = business_obj.aggregate(Sum('smcan_cost'))["smcan_cost__sum"]
    fcmcan_sale_cost = business_obj.aggregate(Sum('fcmcan_cost'))["fcmcan_cost__sum"]
   
   
    data_dict["commission"]["COMM QTY"] = tm500_sale + tmcan_sale + std250_sale + std500_sale + smcan_sale + fcm500_sale + fcm1000_sale + fcmcan_sale
   
    data_dict["center_content"]["tm_litre"] = tm500_sale + tmcan_sale
    data_dict["center_content"]["tm_cost"] = tm500_sale_cost + tmcan_sale_cost
    data_dict["center_content"]["sm_liter"] = std250_sale + std500_sale + smcan_sale
    data_dict["center_content"]["sm_cost"] = std250_sale_cost + std500_sale_cost + smcan_sale_cost
    data_dict["center_content"]["fcm_liter"] = fcm500_sale + fcm1000_sale + fcmcan_sale
    data_dict["center_content"]["fcm_cost"] = fcm500_sale_cost + fcm1000_sale_cost + fcmcan_sale_cost
   
   
    data_dict["down_content"]["slip_cost"] = agent_commission_obj.aggregate(Sum("slip_charge"))["slip_charge__sum"]
    data_dict["down_content"]["incomtax"] = agent_commission_obj.aggregate(Sum("tds_deduction"))["tds_deduction__sum"]
  
    file_name = 'commission_report_c5_from_' + str(from_date) + '_to_' + str(to_date) + ".pdf"
    file_path = os.path.join('static/media/monthly_report', file_name)
   
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    pdfmetrics.registerFont(TTFont('dot', 'dotmatrix.ttf'))
    light_color = 0x9b9999
    dark_color = 0x000000

   
    from_date = datetime.datetime.strptime(from_date[:10],'%Y-%m-%d')
    to_date = datetime.datetime.strptime(to_date[:10],'%Y-%m-%d')
    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setFont('dot', 15)
    mycanvas.drawCentredString(300, 740+80, 'The Coimbatore District Co-Operative Milk Producers Union Ltd.')
    mycanvas.drawCentredString(300, 720+80, 'Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawCentredString(300, 700+80, 'ABSTRACT OF COMMISSION PAYMENT STATEMENT FOR THE PERIOD OF (  '+str(from_date.strftime("%d-%m-%Y")+"  to  "+str(to_date.strftime("%d-%m-%Y") +"  )")))
   
    mycanvas.setDash(6,3)
    mycanvas.setLineWidth(0)
   
    x_total_len = 575
    x_axis = 40
    x_axis_line = 10
    y_axis = 670+40
    y_axis_line = 690+50
    sl_no = 1
    mycanvas.setFont('dot', 12)
    len_adjust=6
   
    mycanvas.line(x_axis_line,y_axis+30,x_total_len+10,y_axis+30)
    mycanvas.line(x_axis_line,y_axis,x_total_len+10,y_axis)
   
    for data in data_dict["commission"]:
        mycanvas.drawCentredString(x_axis+22,y_axis+10,str(data))
        mycanvas.drawCentredString(x_axis+22,y_axis-20,str(data_dict["commission"][data]))
       
        mycanvas.line(x_axis-30,y_axis+30,x_axis-30,y_axis-40)
        x_axis += (x_total_len/len_adjust)-2
    mycanvas.line(x_axis_line,y_axis+30,x_axis_line,y_axis-40)
    mycanvas.line(x_total_len+10,y_axis+30,x_total_len+10,y_axis-40)
    mycanvas.line(x_axis_line,y_axis-40,x_total_len+10,y_axis-40)
   
    #-------------------------centred content --------------------------------#
   
    mycanvas.setFont('dot', 15)
    mycanvas.drawCentredString(300, y_axis-70, 'CERTIFICATE')
    mycanvas.drawCentredString(300, y_axis-90, 'Percentage  Of  Commission  Details:  TM, SM, FCM (Card & Cash 4.10%)')
   
    x_axis = 40
    mycanvas.setFont('dot', 12.5)
    mycanvas.drawString(x_axis-20, y_axis-140, '1. Certified that   '+ str(data_dict["center_content"]["tm_litre"]) +'   litres of  TONNED MILK was sold during this month and corresponding sale proceeds of')
    mycanvas.drawString(x_axis-20, y_axis-160, '   Rs. '+str(data_dict["center_content"]["tm_cost"])+'   was collected and no dues is pending as on date.')
   
    mycanvas.drawString(x_axis-20, y_axis-190, '2. Certified that   '+ str(data_dict["center_content"]["sm_liter"]) +'   litres of  STD MILK was sold during this month and corresponding sale proceeds of ')
    mycanvas.drawString(x_axis-20, y_axis-210, '   Rs. '+ str(data_dict["center_content"]["sm_cost"]) +'   was collected and no dues is pending as on date.')
   
    mycanvas.drawString(x_axis-20, y_axis-240, '3. Certified that   '+ str(data_dict["center_content"]["fcm_liter"]) +'   litres of  FCM MILK was sold during this month and corresponding sale proceeds of ')
    mycanvas.drawString(x_axis-20, y_axis-260, '   Rs. '+ str(data_dict["center_content"]["fcm_cost"]) +'   was collected and no dues is pending as on date.')
   
    mycanvas.drawString(x_axis-20, y_axis-290, '4. Certified that this bill was prepared as per commission rate approved by competent authority.')
    
    mycanvas.setFont('dot', 15)

    mycanvas.drawCentredString(300,y_axis-350,'EXECUTIVE(O)                  DEPUTY MANAGER(O)                      Manager(Mkg)                      AGM(MKG)')
   
    mycanvas.line(x_axis_line,y_axis-370,x_total_len+10,y_axis-370)
    mycanvas.line(x_axis_line,y_axis-380,x_total_len+10,y_axis-380)
   
    words = num2words(round(data_dict["commission"]["COMM VALUE"]), lang='en_IN')
    mycanvas.setFont('dot', 13)
    mycanvas.drawCentredString(300,y_axis-410,"PASSED FOR Rs. "+str(round(data_dict["commission"]["COMM VALUE"]))+" ( "+str(words.upper())+" "+"Only )")
   
    mycanvas.setFont('dot', 13)
    mycanvas.drawString(x_axis-20, y_axis-460,'BY CASH/CHEQUE/RTGS ----------------------------------------------------------->     '+str(data_dict["commission"]["TOTAL PAYMENT"]))
    mycanvas.drawString(x_axis-20, y_axis-500,'BY ADJ')
   
   
    mycanvas.drawString(x_axis, y_axis-520,'1. SUNDRY DEBTOR')
    mycanvas.drawRightString(x_axis+400, y_axis-520,str(data_dict["down_content"]["sundry_debtor"]))
   
    mycanvas.drawString(x_axis, y_axis-540,'2. SLIP COST')
    mycanvas.drawRightString(x_axis+400, y_axis-540,str(data_dict["down_content"]["slip_cost"]))
   
    mycanvas.drawString(x_axis, y_axis-560,'3. INCOMETAX')
    mycanvas.drawRightString(x_axis+400, y_axis-560,str(data_dict["down_content"]["incomtax"]))
    
    
    if data_dict["down_content"]["others"] == 0 or data_dict["down_content"]["others"] == None:
        mycanvas.drawRightString(x_axis+500, y_axis-560,str(data_dict["commission"]["TOAL DEDECTUON"]))
        mycanvas.line(x_axis+430,y_axis-580,x_axis+510,y_axis-580)
        mycanvas.drawString(x_axis-20, y_axis-600,'T O T A L')
        mycanvas.drawRightString(x_axis+500, y_axis-600,str(data_dict["commission"]["COMM VALUE"]))
    else:
        mycanvas.drawString(x_axis, y_axis-580,'4. OTHERS')
        mycanvas.drawRightString(x_axis+400, y_axis-580,str(data_dict["down_content"]["others"]))
        mycanvas.drawRightString(x_axis+500, y_axis-580,str(data_dict["commission"]["TOAL DEDECTUON"]))
        
        mycanvas.line(x_axis+430,y_axis-600,x_axis+510,y_axis-600)
        mycanvas.drawString(x_axis-20, y_axis-620,'T O T A L')
        mycanvas.drawRightString(x_axis+500, y_axis-620,str(data_dict["commission"]["COMM VALUE"]))
   
    mycanvas.setFont('dot', 15)
    mycanvas.drawCentredString(300, y_axis-680, 'DM(Accts)                                      AGM(Finance)                            General Manager')
   
    mycanvas.save()
    document = {}
    document['pdf_file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return document


@api_view(['POST'])
def serve_run_list_for_commission(request):
  print(request.data)  
  data_dict = {'is_data_available': None}
  selected_month = request.data['month_in_integer'] + 1
  selected_year = request.data['year']
  if MonthlyAgentCommissionRun.objects.filter(month=selected_month, year=selected_year, is_comm_run_completed=True).exists():
    data_dict['is_data_available'] = True
    monthly_agent_commision_obj = MonthlyAgentCommissionRun.objects.filter(month=selected_month, year=selected_year)
    monthly_agent_commision_list = list(monthly_agent_commision_obj.values_list('id', 'split', 'run_from', 'run_to'))
    monthly_agent_commision_column = ['id', 'split', 'run_from', 'run_to']
    monthly_agent_commision_df = pd.DataFrame(monthly_agent_commision_list, columns=monthly_agent_commision_column)
    monthly_agent_commision = monthly_agent_commision_df.to_dict('r')
    data_dict['data'] = monthly_agent_commision
    return Response(data=data_dict, status=status.HTTP_200_OK)
  else:
    data_dict['is_data_available'] = False
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_online_payment_transation_report(request):

    from_date = request.data['from_date']
    to_date = request.data['to_date']
    input_type = request.data['option_type']

    #payment_response_time_amount_df
    payment_response_obj = PaymentRequestResponse.objects.filter(time_created__date__gte=from_date, time_created__date__lte=to_date, status_id=1).order_by('time_created')
    payment_response_df = pd.DataFrame(list(payment_response_obj.values_list('trn', 'amt', 'time_created','payment_request_id')), columns=['Transaction Id', 'Amount', 'Transaction Time','payment_request_id'])
    payment_response_df['Transaction Time'] = pd.to_datetime(payment_response_df['Transaction Time'], errors='coerce')
    payment_response_df['Transaction Time'] = payment_response_df['Transaction Time'].dt.strftime('%d-%m-%Y/%H:%M %p')

    #payment_request_map_df
    payment_requset_df = pd.DataFrame(list(PaymentRequestUserMap.objects.filter(payment_request_id__in=payment_response_df['payment_request_id']).values_list('payment_intitated_by_id','payment_request_id')), columns=['user_id', 'payment_request_id'])

    # payment_response_time_amount_df + payment_request_map_df
    payment_request_response_df = pd.merge(payment_response_df, payment_requset_df, left_on='payment_request_id', right_on='payment_request_id', how='left')

    #user_booth_df
    if input_type == 'agent':
        business_df = pd.DataFrame(list(Business.objects.filter(user_profile__user_id__in=payment_requset_df['user_id']).values_list('user_profile__user_id', 'code', 'user_profile__user__first_name', 'user_profile__user__last_name')), columns=['user_id', 'Booth Code', 'user_first_name', 'user_last_name'])
        business_df['Agent Name'] = business_df['user_first_name'] + ' ' + business_df['user_last_name']
        business_df = business_df.reindex(columns=['user_id', 'Agent Name', 'Booth Code'])
        
        merged_df = pd.merge(payment_request_response_df, business_df, left_on='user_id', right_on='user_id', how='left')
        merged_df = merged_df.fillna('')
        final_df = merged_df[(merged_df['Booth Code'] != '')]
        
        final_df = final_df.reindex(columns=['Agent Name', 'Booth Code', 'Transaction Id', 'Amount', 'Transaction Time'])
        
    else:
        business_df = pd.DataFrame(list(ICustomer.objects.filter(user_profile__user_id__in=payment_requset_df['user_id']).values_list('user_profile__user_id', 'customer_code', 'user_profile__user__first_name', 'user_profile__user__last_name')), columns=['user_id', 'Customer Code', 'user_first_name', 'user_last_name'])
        business_df['Customer Name'] = business_df['user_first_name'] + ' ' + business_df['user_last_name']
        business_df = business_df.reindex(columns=['user_id', 'Customer Name', 'Customer Code'])
        
        merged_df = pd.merge(payment_request_response_df, business_df, left_on='user_id', right_on='user_id', how='left')
        merged_df = merged_df.fillna('')
        final_df = merged_df[(merged_df['Customer Code'] != '')]
                            
        final_df = final_df.reindex(columns=['Customer Name', 'Customer Code', 'Transaction Id', 'Amount', 'Transaction Time'])
        
    data_dict = final_df.to_dict('r')


    #--------------------------------

    file_name = f'online_payment_transaction_for-{input_type}-{from_date}_to_{to_date}.pdf'
    file_path = os.path.join('static/media/general_report/', file_name)

    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    mycanvas.setLineWidth(0)

    from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')

    from_date = datetime.datetime.strftime(from_date, '%d/%m/%Y')
    to_date = datetime.datetime.strftime(to_date, '%d/%m/%Y')


    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 805, 'Online Payment Transaction Report - ( '+from_date+" to "+to_date+' )')
    mycanvas.setFont('Helvetica', 9)

    x = 40
    y = 790
    x_total_len = 590
    len_adjust = len(data_dict[0])

    mycanvas.line(x - 20, y, x_total_len, y)
    mycanvas.line(x - 20 , y - 20, x_total_len, y - 20)
    mycanvas.drawCentredString(x - 10 ,y - 9, str('Sl'))
    mycanvas.drawCentredString(x - 10 ,y - 19, str('No'))
    amount_total = 0
    for data in data_dict[0]:
        if data == list(data_dict[0])[-1]:
            mycanvas.drawCentredString(x + 42, y - 15, data)
        elif data == 'Customer Code':
            mycanvas.drawCentredString(x + 34, y - 15, data)
        elif data == 'Booth Code':
            mycanvas.drawCentredString(x + 34, y - 15, data)
        elif data == 'Transaction Id':
            mycanvas.drawCentredString(x + 25, y - 15, data)
        else:
            mycanvas.drawCentredString(x + 62, y - 15, data)
        x += (x_total_len/len_adjust) 

    x = 40 
    mlk_ltr = 0
    mlk_cst = 0
    tot_icen = 0
    for sl_no,datas in enumerate(data_dict,1):
        mycanvas.line(x - 20, y, x - 20, y - 40)
        mycanvas.setFont('Helvetica', 7)
        mycanvas.drawRightString(x-5, y - 35, str(sl_no))
        mycanvas.setLineWidth(0)
        for data in data_dict[0]:
            if data == 'Customer Name':
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawString(x+5, y - 35, str(datas[data][:25]).capitalize())
                mycanvas.line(x, y, x, y - 40)
            elif data == 'Agent Name':
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawString(x + 5, y - 35, str(datas[data][:25]).capitalize())
                mycanvas.line(x, y, x, y - 40)
            elif data == 'Customer Code':
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawString(x+5, y - 35, str(datas[data]))
                mycanvas.line(x, y, x, y - 40)
            elif data == 'Booth Code':
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawString(x+5, y - 35, str(datas[data]))
                mycanvas.line(x, y, x, y - 40)
            elif data == 'Transaction Id':
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawString(x-45, y - 35, str(datas[data]))
                mycanvas.line(x-50,y,x-50,y-40)
            elif data == list(data_dict[0])[-1]:
                date_in_format = datetime.datetime.strptime(datas[data], '%d-%m-%Y/%H:%M %p').astimezone(indian)
                date_in_format = datetime.datetime.strftime(date_in_format,'%d-%m-%Y/%I:%M %p')
                mycanvas.setFont('Helvetica', 7)
                mycanvas.drawRightString(x + (x_total_len/len_adjust) - 45, y - 35, str(date_in_format))
                mycanvas.line(x, y, x, y - 40)
            else:
                amount_total += datas[data]
                mycanvas.drawRightString(x + (x_total_len/len_adjust) - 5, y - 35, str(datas[data]))
                mycanvas.line(x, y, x, y-40)

            x += (x_total_len/len_adjust)

        x = 40
        mycanvas.line(x, y, x, y - 40)
        mycanvas.line(x_total_len, y, x_total_len, y-40)
        y -= 15

        if sl_no % 49 == 0:
            mycanvas.setLineWidth(0)
            x = 40
            mycanvas.line(x-20, y-25, x_total_len, y-25)
            mycanvas.showPage()
            y = 790
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 805, 'Online Payment Transaction Report - ( '+from_date+" to "+to_date+' )')
            mycanvas.setFont('Helvetica', 9)
            mycanvas.setLineWidth(0)
            mycanvas.line(x-20, y, x_total_len, y)
            mycanvas.line(x-20, y-20, x_total_len, y-20)
            mycanvas.drawCentredString(x - 10 ,y - 9, str('Sl'))
            mycanvas.drawCentredString(x - 10 ,y - 19, str('No'))

            for data in data_dict[0]:
                if data == list(data_dict[0])[-1]:
                    mycanvas.drawCentredString(x+42, y-15, data)
                elif data == 'Customer Code':
                    mycanvas.drawCentredString(x+34, y-15, data)
                elif data == 'Booth Code':
                    mycanvas.drawCentredString(x+34, y-15, data)
                elif data == 'Transaction Id':
                    mycanvas.drawCentredString(x+25, y-15, data)
                else:
                    mycanvas.drawCentredString(x+62, y-15, data)
                x += (x_total_len/len_adjust) 
            x = 40

    mycanvas.line(x-20, y-25, x_total_len, y-25)
    mycanvas.line(x_total_len, y-25, x_total_len, y-25)

    mycanvas.drawRightString(x + (x_total_len/len_adjust)*3 - 5, y - 35, 'Grand Total')
    mycanvas.drawRightString(x + (x_total_len/len_adjust)*4 - 5, y - 35, str(amount_total))
    mycanvas.line((x_total_len/len_adjust)*3+40, y, (x_total_len/len_adjust)*3+40, y-40)
    mycanvas.line((x_total_len/len_adjust)*4+40, y, (x_total_len/len_adjust)*4+40, y-40)
    mycanvas.line((x_total_len/len_adjust)*3+40, y-40, (x_total_len/len_adjust)*4+40, y-40)

    mycanvas.save()

    document = {}
    document['pdf_file_name'] = file_name
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_super_sale_group_report(request):
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  business_type_ids = request.data['selected_business_type_ids']
  file_name = 'total_transaction_'+str(from_date)+'_to_'+str(to_date)+'.xlsx'
  file_path = os.path.join('static/media/general_report/', file_name)
  

  super_sale_group_obj = SuperSaleGroup.objects.filter(delivery_date__range=[from_date, to_date], business__business_type_id__in=business_type_ids)
  # super_sale_group_values = list(super_sale_group_obj.values_list('business__code', 'business__user_profile__user__first_name', 'salegrouptransactiontrace__counter_amount', 'salegrouptransactiontrace__transacted_amount', 'salegrouptransactiontrace__wallet_amount'))                     
  super_sale_group_values = list(super_sale_group_obj.values_list('business__code', 'business__user_profile__user__first_name', 'salegrouptransactiontrace__counter_amount', 'salegrouptransactiontrace__transacted_amount'))                     
  super_sale_group_olumn = ['business_code', 'agent_name', 'counter_amount', 'online_amount',]
  super_sale_group_df = pd.DataFrame(super_sale_group_values, columns=super_sale_group_olumn)
  # super_sale_group_df['online_amount'] = super_sale_group_df['trasacted_amount'] + super_sale_group_df['wallet_amount']
  super_sale_group_df = super_sale_group_df.groupby(['business_code', 'agent_name']).agg({'counter_amount': 'sum', 'online_amount': 'sum'}).reset_index()


  # wallet details

  wallet_balance_obj = SaleGroupTransactionTrace.objects.filter(delivery_date__range=[from_date, to_date], super_sale_group__business__business_type_id__in=business_type_ids).order_by('-id')

  counter_list = list(wallet_balance_obj.values_list('super_sale_group__business__code', 'counter_transaction__id', 'counter_transaction__wallet_balance_before_this_transaction', 'counter_transaction__wallet_balance_after_transaction_approval'))
  counter_column = ['business_code', 'transaction_id', 'wallet_before_amount', 'wallet_after_amount']
  counter_df = pd.DataFrame(counter_list, columns=counter_column).fillna(0)

  bank_list = list(wallet_balance_obj.values_list('super_sale_group__business__code', 'bank_transaction__id', 'bank_transaction__wallet_balance_before_this_transaction', 'bank_transaction__wallet_balance_after_transaction_approval'))
  bank_column = ['business_code', 'transaction_id', 'wallet_before_amount', 'wallet_after_amount']
  bank_df = pd.DataFrame(bank_list, columns=bank_column).fillna(0)

  wallet_list = list(wallet_balance_obj.values_list('super_sale_group__business__code', 'wallet_transaction__id', 'wallet_transaction__wallet_balance_before_this_transaction', 'wallet_transaction__wallet_balance_after_transaction_approval'))
  wallet_column = ['business_code', 'transaction_id', 'wallet_before_amount', 'wallet_after_amount']
  wallet_df = pd.DataFrame(wallet_list, columns=wallet_column).fillna(0)

  wallet_df = pd.concat([counter_df, bank_df, wallet_df], ignore_index=True)

  wallet_df = wallet_df[wallet_df['transaction_id'] != 0]

  wallet_df = wallet_df.sort_values(by=['transaction_id'], ascending=True)
  wallet_df = wallet_df.groupby('business_code').agg({'wallet_before_amount': 'first', 'wallet_after_amount': 'last'}).reset_index()

  # merging supersale_df, wallet_df 
  wallet_super_sale_group_df = pd.merge(super_sale_group_df, wallet_df, left_on='business_code', right_on='business_code', how='left')


  # product_wise_sale_df
  agent_sale_list = list(Sale.objects.filter(sale_group__business__business_type_id__in=business_type_ids, sale_group__date__range=[from_date, to_date]).order_by('product_id').values_list('sale_group__business__code', 'product__short_name', 'count', 'cost'))
  agent_sale_column = ['business_code', 'product_name', 'product_count', 'product_cost']
  agent_sale_df = pd.DataFrame(agent_sale_list, columns=agent_sale_column)
  agent_sale_df = agent_sale_df.groupby(['business_code', 'product_name']).agg({'product_cost': 'sum'})

  #convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
  agent_product_cost_df = pd.pivot_table(agent_sale_df, index='business_code', columns='product_name', aggfunc=min, fill_value=0)

  #convert_pivot_table_to_normal_df
  agent_product_cost_df.columns = agent_product_cost_df.columns.droplevel(0) #remove amount
  agent_product_cost_df.columns.name = None  #remove categories
  agent_product_cost_df = agent_product_cost_df.reset_index() #index to columns

  # merging wallet_super_sale_group_df and agent_product_cost_df

  final_df = pd.merge(wallet_super_sale_group_df, agent_product_cost_df, left_on='business_code', right_on='business_code', how='left')

  #auto bot money deposit wallet log
  auto_bot_deposit_list = list(AutoBotMoneyDepositToWalletLog.objects.filter(delivery_date__range=[from_date, to_date], business__business_type_id__in=business_type_ids).values_list('business__code', 'amount'))
  auto_bot_deposit_column = ['business_code', 'deposited_amount']
  auto_bot_deposit_df = pd.DataFrame(auto_bot_deposit_list, columns=auto_bot_deposit_column)
  auto_bot_deposit_df = auto_bot_deposit_df.groupby('business_code').agg({'deposited_amount': sum}).reset_index()
  final_df = pd.merge(final_df, auto_bot_deposit_df, left_on='business_code', right_on='business_code', how='left').fillna(0)
  
  final_df = final_df.reindex(columns=['business_code', 'agent_name', 'wallet_before_amount', 'counter_amount', 'online_amount', 'deposited_amount', 'wallet_after_amount', 'Total Amount Paid To Aavin For This Month', 'BM 200', 'Curd 100', 'Curd 150', 'Curd 500', 'FCM 1000', 'FCM 500', 'STD 250', 'STD 500', 'TM 500', 'Total Cost Of The Products Orderd For This Month', 'Difference'])
  final_df = final_df.fillna(0)

  final_df['Total Amount Paid To Aavin For This Month'] = final_df['wallet_before_amount'].astype('float') + final_df['counter_amount'].astype('float') + final_df['online_amount'].astype('float') + final_df['deposited_amount'].astype('float') - final_df['wallet_after_amount'].astype('float')
  final_df['Total Cost Of The Products Orderd For This Month'] = final_df['BM 200'].astype('float') + final_df['Curd 100'].astype('float') + final_df['Curd 150'].astype('float') + final_df['Curd 500'].astype('float') + final_df['FCM 1000'].astype('float') + final_df['FCM 500'].astype('float') + final_df['STD 250'].astype('float') + final_df['STD 500'].astype('float') + final_df['TM 500'].astype('float')

  final_df['Difference'] = final_df['Total Cost Of The Products Orderd For This Month'].astype('float') - final_df['Total Amount Paid To Aavin For This Month'].astype('float')
  final_df = final_df.rename(columns={'business_code': 'Booth Code', 'agent_name': 'Agent Name', 'wallet_before_amount': 'Wallet At The Start Of Month', 'counter_amount': 'Paid At Counter For This Month', 'online_amount': 'Paid Via Online For This Month', 'wallet_after_amount': 'Wallet At The End Of This Month', 'deposited_amount': 'Deposited Amount'})
  final_df_for_json = final_df
  final_df_for_json = final_df_for_json.rename(columns={'Booth Code': 'business_code', 'Agent Name': 'agent_name', 'Wallet At The Start Of Month': 'wallet_before_amount', 'Paid At Counter For This Month': 'counter_amount', 'Paid Via Online For This Month': 'online_amount', 'Wallet At The End Of This Month': 'wallet_after_amount', 'Total Amount Paid To Aavin For This Month': 'total_amount_paid', 'Total Cost Of The Products Orderd For This Month': 'product_total_amount', 'Difference': 'difference', 'Deposited Amount': 'deposited_amount'})
  final_df_for_json['from_date'] = from_date
  final_df_for_json['to_date'] = to_date
  final_df.to_excel(file_path, index=False)
  df = pd.read_excel(file_path)
  df.to_excel(file_path, index=False)
  product_list = list(Product.objects.filter(group_id__in=[1,2]).order_by('display_ordinal').values_list('short_name', flat=True))
  document = {}
  document['sale_group_data'] = final_df_for_json.to_dict('r')
  document['excel_file_name'] = file_name
  document['product_list'] = product_list
  try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
  except Exception as err:
      print('Error', err)
  return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_counter_amount_in_super_sale_group(request):
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  business_code = request.data['selected_business_code']
  super_sale_group_counter_values = list(SuperSaleGroup.objects.filter(delivery_date__range=[from_date, to_date], business__code=business_code).values_list('delivery_date', 'salegrouptransactiontrace__counter_amount', 'time_created'))                     
  super_sale_group_counter_olumn = ['delivery_date', 'counter_amount', 'order_time']
  super_sale_group_counter_df = pd.DataFrame(super_sale_group_counter_values, columns=super_sale_group_counter_olumn)
  super_sale_group_counter_df = super_sale_group_counter_df.groupby('delivery_date').agg({'counter_amount': 'sum','order_time': 'first'}).reset_index()
  return Response(data=super_sale_group_counter_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_online_amount_in_super_sale_group(request):
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  business_code = request.data['selected_business_code']
  super_sale_group_online_values = list(SuperSaleGroup.objects.filter(delivery_date__range=[from_date, to_date], business__code=business_code).values_list('delivery_date', 'salegrouptransactiontrace__transacted_amount', 'time_created'))                     
  super_sale_group_online_olumn = ['delivery_date', 'online_amount', 'order_time']
  super_sale_group_online_df = pd.DataFrame(super_sale_group_online_values, columns=super_sale_group_online_olumn)
  super_sale_group_online_df = super_sale_group_online_df.groupby('delivery_date').agg({'online_amount': 'sum','order_time': 'first'}).reset_index()
  return Response(data=super_sale_group_online_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_wallet_amount_in_super_sale_group(request):
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  business_code = request.data['selected_business_code']
  data_dict = {
      'opening_wallet_balance': None,
      'wallet_transaction': None,
      'closing_wallet_balance': None,
  }

  super_sale_group_wallet_values = list(SuperSaleGroup.objects.filter(delivery_date__range=[from_date, to_date], business__code=business_code, salegrouptransactiontrace__wallet_amount__gt=0).values_list('delivery_date', 'salegrouptransactiontrace__wallet_amount', 'time_created', 'salegrouptransactiontrace__wallet_transaction__wallet_balance_after_transaction_approval'))                     
  super_sale_group_wallet_olumn = ['delivery_date', 'wallet_amount', 'order_time', 'wallet_balance']
  super_sale_group_wallet_df = pd.DataFrame(super_sale_group_wallet_values, columns=super_sale_group_wallet_olumn)
  data_dict['wallet_transaction'] = super_sale_group_wallet_df.to_dict('r')

  # opening_balance_closing_balace
  #opening_balance
  if SaleGroupTransactionTrace.objects.filter(delivery_date=from_date, super_sale_group__business__code=business_code).exists():
      wallet_balance_before_obj = SaleGroupTransactionTrace.objects.filter(delivery_date=from_date, super_sale_group__business__code=business_code).order_by('-id')[0]

      if wallet_balance_before_obj.counter_transaction is not None:
          data_dict['opening_wallet_balance'] = wallet_balance_before_obj.counter_transaction.wallet_balance_before_this_transaction
      elif wallet_balance_before_obj.bank_transaction is not None:
          data_dict['opening_wallet_balance'] = wallet_balance_before_obj.bank_transaction.wallet_balance_before_this_transaction
      elif wallet_balance_before_obj.wallet_transaction is not None:
          data_dict['opening_wallet_balance'] = wallet_balance_before_obj.wallet_transaction.wallet_balance_before_this_transaction
      else:
          data_dict['opening_wallet_balance'] = 0
  
  #closing_balance
  if SaleGroupTransactionTrace.objects.filter(delivery_date=to_date, super_sale_group__business__code=business_code).exists():
      wallet_balance_after_obj = SaleGroupTransactionTrace.objects.filter(delivery_date=to_date, super_sale_group__business__code=business_code).order_by('-id')[0]

      if wallet_balance_after_obj.counter_transaction is not None:
          data_dict['closing_wallet_balance'] = wallet_balance_after_obj.counter_transaction.wallet_balance_after_transaction_approval
      elif wallet_balance_after_obj.bank_transaction is not None:
          data_dict['closing_wallet_balance'] = wallet_balance_after_obj.bank_transaction.wallet_balance_after_transaction_approval
      elif wallet_balance_after_obj.wallet_transaction is not None:
          data_dict['closing_wallet_balance'] = wallet_balance_after_obj.wallet_transaction.wallet_balance_after_transaction_approval
      else:
          data_dict['closing_wallet_balance'] = 0
  return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_product_wise_super_sale_group(request):
  from_date = request.data['from_date']
  to_date = request.data['to_date']
  business_code = request.data['selected_business_code']

  super_sale_group_obj = SaleGroupTransactionTrace.objects.filter(delivery_date__range=[from_date, to_date], super_sale_group__business__code=business_code)
  super_sale_group_values = list(super_sale_group_obj.values_list('super_sale_group__business__code', 'delivery_date', 'super_sale_group__time_created', 'super_sale_group__time_modified', 'super_sale_group__mor_sale_group__total_cost', 'super_sale_group__eve_sale_group__total_cost', 'counter_amount', 'transacted_amount', 'wallet_amount'))                              
  super_sale_group_columns = ['business_code', 'delivery_date', 'time_created', 'time_modified', 'morning_sale_group', 'evening_sale_group', 'counter_amount', 'online_amount', 'wallet_amount']

  agent_super_sale_group_df = pd.DataFrame(super_sale_group_values, columns=super_sale_group_columns)
  agent_super_sale_group_df = agent_super_sale_group_df.groupby('delivery_date').agg({'time_created': 'last',  'time_modified': 'last', 'morning_sale_group': 'last', 'evening_sale_group': 'last', 'counter_amount': 'sum', 'online_amount': 'sum', 'wallet_amount': 'sum'})               
  agent_super_sale_group_df = agent_super_sale_group_df.reset_index().fillna(0)
  agent_super_sale_group_df['final_order_value'] = agent_super_sale_group_df['morning_sale_group'] + agent_super_sale_group_df['evening_sale_group']
  agent_super_sale_group_df['total_amount_paid'] = agent_super_sale_group_df['counter_amount'] + agent_super_sale_group_df['online_amount'] + agent_super_sale_group_df['wallet_amount']
  agent_super_sale_group_df['difference'] = agent_super_sale_group_df['final_order_value'] - agent_super_sale_group_df['total_amount_paid']
  agent_super_sale_group_df = agent_super_sale_group_df.drop(columns=['morning_sale_group', 'evening_sale_group', 'counter_amount', 'online_amount', 'wallet_amount'])

  data_dict = {}
# trase_value = super_sale_group_obj.values_list('delivery_date', 'salegrouptransactiontrace__counter_amount', 'salegrouptransactiontrace__transacted_amount',     
  super_sale_group_obj = super_sale_group_obj.order_by('time_created')
  for trace in super_sale_group_obj:
      if not trace.delivery_date in data_dict:
          data_dict[trace.delivery_date] = {'transaction_details':[], 'total': 0}                     
      
      if trace.counter_transaction is not None:
          data_dict[trace.delivery_date]['transaction_details'].append({'scope': 'Counter', 'amount': trace.counter_amount, 'time_created': trace.counter_transaction.time_created})    
          data_dict[trace.delivery_date]['total'] += trace.counter_amount

      if trace.bank_transaction is not None:
          data_dict[trace.delivery_date]['transaction_details'].append({'scope': 'Online', 'amount': trace.transacted_amount, 'time_created': trace.bank_transaction.time_created, 'rid':trace.bank_transaction.transaction_id})
          data_dict[trace.delivery_date]['total'] += trace.transacted_amount

      if trace.wallet_transaction is not None:
          data_dict[trace.delivery_date]['transaction_details'].append({'scope': 'Wallet', 'amount': trace.wallet_amount, 'time_created': trace.wallet_transaction.time_created})
          data_dict[trace.delivery_date]['total'] += trace.wallet_amount

  transaction_df = pd.DataFrame(data_dict)
  transaction_df = transaction_df.T
  super_sale_group_df = pd.merge(agent_super_sale_group_df, transaction_df, left_on='delivery_date', right_index=True, how='left')
  sale_group_ids = list(SaleGroup.objects.filter(business__code=business_code, date__range=[from_date, to_date]).values_list('id', flat=True))
  sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids, product__is_active=True)
  sale_list = list(sale_obj.values_list('id', 'sale_group', 'sale_group__business_id',
                                        'sale_group__date', 'sale_group__session',
                                        'sale_group__session__display_name', 'sale_group__ordered_via',
                                        'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                                        'sale_group__sale_status__name', 'sale_group__total_cost', 'product',
                                        'product__name', 'count', 'cost'))
  sale_column = ['sale_id', 'sale_group_id', 'business_id', 'date', 'session_id', 'session_name',
                'ordered_via_id', 'ordered_via_name', 'payment_status',
                'sale_status',
                'session_wise_price', 'product_id', 'product_name', 'quantity', 'product_cost']
  sale_df = pd.DataFrame(sale_list, columns=sale_column)
  sale_value_list = []
  for date in super_sale_group_df['delivery_date']:
      date_wise_df = sale_df[sale_df['date']==date]
      data_dict = {
          'delivery_date': date,
          'total_sale_details': date_wise_df.to_dict('r')
      }
      sale_value_list.append(data_dict)
  day_wise_sale_df = pd.DataFrame(sale_value_list)
  final_df = pd.merge(super_sale_group_df, day_wise_sale_df, left_on='delivery_date', right_on='delivery_date')
  final_df = final_df.reindex(columns=['delivery_date', 'time_created', 'time_modified', 'total_sale_details', 'final_order_value', 'total_amount_paid', 'difference', 'transaction_details', 'total'])
  return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)



@api_view(['POST'])
def generate_pdf_code_for_cash_finace_report_on_delivery_date(request):
    print(request.data)
    selected_date = request.data['selected_date']
    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d')
    date_in_format = selected_date + datetime.timedelta(days=1)

    business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(order_category_id=1, payment_option_id=1).order_by('business_type_id').values_list('business_type_id', flat=True))

    data_dict = {
      'counter_wise': {},
      'counter_wise_product':{},
      'product_wise': {}
    }
    counter_obj = Counter.objects.filter(is_included_in_cash_collection_report=True).exclude(collection_center_id=9).order_by('id')
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
        counter_employee_trace_ids = list(CounterEmployeeTraceMap.objects.filter(counter_id=row['id'], collection_date__gte=selected_date).values_list(
            'id', flat=True))
        counter_sale_group_ids = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
            counter_employee_trace_id__in=counter_employee_trace_ids, sale_group__date=date_in_format).values_list('sale_group', flat=True))
        if not row['id'] == 23:
            sale_obj = Sale.objects.filter(sale_group_id__in=counter_sale_group_ids)
        else:
            sale_group_ids = list(SaleGroup.objects.filter(date=date_in_format, ordered_via_id__in=[1,3], business_type_id__in=business_type_ids).values_list('id', flat=True))
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
        defalut_product_obj = Product.objects.get(id=product_id)
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
        total_sale_in_litre_wise['milk'][product_id]['litre'] = Decimal(total_quantity) * defalut_product_obj.quantity / 1000
        total_sale_in_litre_wise['milk'][product_id]['amount'] = total_amount
        total_sale_in_litre_wise['milk']['total']['litre'] += total_sale_in_litre_wise['milk'][product_id]['litre']
        total_sale_in_litre_wise['milk']['total']['amount'] += total_sale_in_litre_wise['milk'][product_id]['amount']

    # CURD
    for curd_product_id in product_finance_map_sub_list[2]:
        defalut_product_obj = Product.objects.get(id=curd_product_id)
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
        total_sale_in_litre_wise['curd']['wsd'][curd_product_id]['litre'] = Decimal(total_quantity) * defalut_product_obj.quantity / 1000
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
        total_sale_in_litre_wise['curd']['rtd'][curd_product_id]['litre'] = Decimal(total_quantity) * defalut_product_obj.quantity / 1000
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
        defalut_product_obj = Product.objects.get(id=butter_milk_product_id)
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
        total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['litre'] = Decimal(total_quantity) * defalut_product_obj.quantity / 1000
        total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['amount'] = total_amount
        total_sale_in_litre_wise['butter_milk']['total']['litre'] += total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['litre']
        total_sale_in_litre_wise['butter_milk']['total']['amount'] += total_sale_in_litre_wise['butter_milk'][butter_milk_product_id]['amount']
    data_dict['product_wise'] = total_sale_in_litre_wise
    data = create_canvas_for_finace_report_on_delivery_date(selected_date, date_in_format ,data_dict, counter_list, product_finance_map_main_list, product_finance_map_dict, request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


def create_canvas_for_finace_report_on_delivery_date(selected_date, date_in_format, data_dict, counter_list, product_finance_map_main_list, product_finance_map_dict, user_name):
    file_name = str(date_in_format)+ ' counter_sale_summary_cash' + '.pdf'
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
    # date_in_format = datetime.datetime.strptime(str(date_in_format), '%Y-%m-%d')
    mycanvas.drawCentredString(310-x_a4,770, "Sale Date : " + str(datetime.datetime.strftime(selected_date, '%d-%m-%Y')))
    mycanvas.drawCentredString(510-x_a4,770, "Delivery Date : " + str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y')))
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
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawRightString(start_x_for_milk_product-x_a4-10-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk'][product['product']]['litre']))
        start_x_for_milk_product += 49
        x_adjust += 0
    mycanvas.drawRightString(start_x_for_milk_product-32-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk']['total']['litre']))
    #     retaill amount
    y_for_counter_name -= 20
    mycanvas.drawString(15, y_for_counter_name, 'Retail(Amount)')
    start_x_for_milk_product = 220
    x_adjust = 15
    for product in product_finance_map_dict[1]:
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawRightString(start_x_for_milk_product-x_a4-40-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk'][product['product']]['amount']))
        start_x_for_milk_product += 55
        x_adjust += 5
    mycanvas.drawRightString(start_x_for_milk_product-70-x_adjust, y_for_counter_name, str(data_dict['product_wise']['milk']['total']['amount']))
    y_for_counter_name -= 15
   
   
    mycanvas.line(40-x_a4, y_for_counter_name, 585, y_for_counter_name)
    mycanvas.line(40-x_a4, y_for_counter_name, 40-x_a4, start_of_milk_heading_line)
    mycanvas.line(105-x_a4, y_for_counter_name, 105-x_a4, start_of_milk_heading_line)
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
   
   
    mycanvas.drawRightString(585, 10, 'Report Generated by: '+str(user_name+", @"+str(datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%S"))))

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
def serve_combain_online_report(request):

    from_date = request.data['from_date']
    to_date = request.data['to_date']

    final_dict = {}
    business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(order_category_id=1, payment_option_id=1).order_by('business_type_id').values_list('business_type_id', flat=True))

    date_wise_sale_list = list(SaleGroup.objects.filter(business__business_type_id__in=business_type_ids, date__range=[from_date, to_date], ordered_via_id__in=[1,3]).order_by('date').values_list('date', 'sale__product__short_name', 'sale__count', 'sale__cost', 'sale__product__productfinancecodemap__group_name', 'sale__product__quantity'))                                                          
    date_wise_sale_columns = ['date', 'product', 'sale_count', 'sale_cost', 'product_type', 'product_quantity']
    date_wise_sale_df = pd.DataFrame(date_wise_sale_list, columns=date_wise_sale_columns)

    date_wise_sale_df = date_wise_sale_df.groupby(['date', 'product_type', 'product', 'product_quantity']).agg({'sale_count':sum, 'sale_cost': sum}).reset_index()
    date_wise_sale_df['date'] = pd.to_datetime(date_wise_sale_df['date'], format='%Y-%m-%d').dt.strftime('%d-%m-%Y')


    for index,data in date_wise_sale_df.iterrows():
        if not data['date'] in final_dict:
            data_dict = {}
            for product_finance_code in ProductFinanceCodeMap.objects.filter():
                if not product_finance_code.group_name in data_dict:
                    data_dict[product_finance_code.group_name] = {}
                for product in list(ProductFinanceCodeMap.objects.filter(id=product_finance_code.id).values('product__short_name', 'product__quantity')):
                    if not product['product__short_name'] in data_dict[product_finance_code.group_name]:
                        data_dict[product_finance_code.group_name][product['product__short_name']] = {
                            'sale_count': 0,
                            'sale_cost': 0,
                            'product_quantity': product['product__quantity'],
                            'sale_liter': 0
                        }
            final_dict[data['date']] = data_dict
            final_dict[data['date']]['total_liter'] = 0
            final_dict[data['date']]['total_cost'] = 0


        final_dict[data['date']][data['product_type']][data['product']]["sale_count"] = data['sale_count']
        final_dict[data['date']][data['product_type']][data['product']]["sale_cost"] = data.sale_cost
        final_dict[data['date']][data['product_type']][data['product']]["sale_liter"] = (Decimal(data.product_quantity) * Decimal(data.sale_count))/ 1000
        final_dict[data['date']]["total_liter"] += final_dict[data['date']][data['product_type']][data['product']]["sale_liter"]
        final_dict[data['date']]["total_cost"] += data.sale_cost

    # ____________________________pdf_______________________________________________

    file_name = str(from_date) + '_' + str(to_date) + 'daily_total_product_saale_report.pdf'
    file_path = os.path.join('static/media/monthly_report/', file_name)

    mycanvas = canvas.Canvas(file_path, pagesize=(11.694 * inch, 8.264 * inch))
    # ________Head_lines________#
    mycanvas.drawCentredString(405, 575, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')

    x = 45
    y = 500

    mycanvas.setFont('Helvetica-Bold', 11)
    mycanvas.line(x+75,y+35, x+700, y+35)
    mycanvas.line(x+75,y+35, x+75, y)
    mycanvas.line(x+345,y+35, x+345, y)
    mycanvas.line(x+525,y+35, x+525, y)
    mycanvas.line(x+700,y+35, x+700, y)

    mycanvas.drawCentredString(x+205,y+20,"MILK")
    mycanvas.drawCentredString(x+435,y+20,"CURD")
    mycanvas.drawCentredString(x+610,y+20,"BUTTER MILK")

    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawCentredString(x-10,y,"S.NO")
    mycanvas.drawCentredString(x+40,y,"Date")
    mycanvas.drawCentredString(x+105-5,y,"TM500")
    mycanvas.drawCentredString(x+160-10,y,"STD250")
    mycanvas.drawCentredString(x+220-15,y,"STD500")
    mycanvas.drawCentredString(x+280-20,y,"FCM500")
    mycanvas.drawCentredString(x+345-30,y,"FCM1000")
    mycanvas.drawCentredString(x+410-34,y,"CURD100")
    mycanvas.drawCentredString(x+480-44,y,"CURD150")

    mycanvas.drawCentredString(x+550-55,y,"CURD500")
    mycanvas.drawCentredString(x+615-62,y,"BM200")
    mycanvas.drawCentredString(x+675-65,y,"BMJ200")
    mycanvas.drawCentredString(x+675,y,"BMJF")
    mycanvas.drawCentredString(x+745,y,"Total")

    mycanvas.line(x-25,y+15, x+775, y+15)
    mycanvas.line(x-25,y-10, x+775, y-10)

    total_litter = 0
    total_cost = 0

    tm_500_ltr = 0 
    sm_250_ltr = 0 
    sm_500_ltr = 0 
    fcm_500_ltr = 0 
    fcm_1000_ltr = 0 
    crd_100_ltr = 0 
    crd_150_ltr = 0 
    crd_500_ltr = 0 
    bm_200_ltr = 0  
    bmj_200_ltr = 0  
    bmjf_ltr = 0  

    tm_500_cst = 0
    sm_250_cst = 0
    sm_500_cst = 0
    fcm_500_cst = 0
    fcm_1000_cst = 0
    crd_100_cst = 0
    crd_150_cst = 0
    crd_500_cst = 0
    bm_200_cst =  0
    bmj_200_cst =  0
    bmjf_cst = 0


    mycanvas.setFont('Helvetica', 9)
    for index,data in enumerate(final_dict):
        print(data)
        mycanvas.drawString(x-15,y-25,str(index+1))
        mycanvas.drawString(x+20,y-25,str(data))
        mycanvas.drawRightString(x+120,y-25,str(final_dict[data]['Milk']['TM 500']['sale_liter']))
        tm_500_ltr += final_dict[data]['Milk']['TM 500']['sale_liter']

        mycanvas.drawRightString(x+170,y-25,str(final_dict[data]['Milk']['STD 250']['sale_liter']))
        sm_250_ltr += final_dict[data]['Milk']['STD 250']['sale_liter']

        mycanvas.drawRightString(x+225,y-25,str(final_dict[data]['Milk']['STD 500']['sale_liter']))
        sm_500_ltr += final_dict[data]['Milk']['STD 500']['sale_liter']

        mycanvas.drawRightString(x+280,y-25,str(final_dict[data]['Milk']['FCM 500']['sale_liter']))
        fcm_500_ltr += final_dict[data]['Milk']['FCM 500']['sale_liter']

        mycanvas.drawRightString(x+340,y-25,str(final_dict[data]['Milk']['FCM 1000']['sale_liter']))
        fcm_1000_ltr += final_dict[data]['Milk']['FCM 1000']['sale_liter']

        mycanvas.drawRightString(x+400,y-25,str(final_dict[data]['Curd']['Curd 100']['sale_liter']))
        crd_100_ltr += final_dict[data]['Curd']['Curd 100']['sale_liter']

        mycanvas.drawRightString(x+460,y-25,str(final_dict[data]['Curd']['Curd 150']['sale_liter']))
        crd_150_ltr += final_dict[data]['Curd']['Curd 150']['sale_liter']

        mycanvas.drawRightString(x+520,y-25,str(final_dict[data]['Curd']['Curd 500']['sale_liter']))
        crd_500_ltr += final_dict[data]['Curd']['Curd 500']['sale_liter']

        mycanvas.drawRightString(x+575,y-25,str(final_dict[data]['Butter Milk']['BM 200']['sale_liter']))
        bm_200_ltr += final_dict[data]['Butter Milk']['BM 200']['sale_liter']

        mycanvas.drawRightString(x+635,y-25,str(final_dict[data]['Butter Milk']['BMJar']['sale_liter']))
        bmj_200_ltr += final_dict[data]['Butter Milk']['BMJar']['sale_liter']

        mycanvas.drawRightString(x+695,y-25,str(final_dict[data]['Butter Milk']['BMJF']['sale_liter']))
        bmjf_ltr += final_dict[data]['Butter Milk']['BMJF']['sale_liter']

        mycanvas.drawRightString(x+770,y-25,str(final_dict[data]['total_liter']))   
        total_litter += final_dict[data]['total_liter']

        #lines 
        mycanvas.line(x-25,y+15, x-25, y-35)
        mycanvas.line(x+10,y+15, x+10, y-35)
        mycanvas.line(x+75,y+15, x+75, y-35)
        mycanvas.line(x+122,y+15, x+122, y-35)
        mycanvas.line(x+175,y+15, x+175, y-35)
        mycanvas.line(x+230,y+15, x+230, y-35)
        mycanvas.line(x+285,y+15, x+285, y-35)
        mycanvas.line(x+345,y+15, x+345, y-35)
        mycanvas.line(x+405,y+15, x+405, y-35)
        mycanvas.line(x+465,y+15, x+465, y-35)
        mycanvas.line(x+525,y+15, x+525, y-35)
        mycanvas.line(x+580,y+15, x+580, y-35)
        mycanvas.line(x+640,y+15, x+640, y-35)
        mycanvas.line(x+700,y+15, x+700, y-35)
        mycanvas.line(x+775,y+15, x+775, y-35)

        if (index + 1) % 22 == 0:
            mycanvas.line(x-25,y-35, x+775, y-35)
            mycanvas.showPage()
            mycanvas.drawCentredString(405, 575, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            x = 45
            y = 500

            mycanvas.setFont('Helvetica-Bold', 11)
            mycanvas.line(x+75,y+35, x+700, y+35)
            mycanvas.line(x+75,y+35, x+75, y)
            mycanvas.line(x+345,y+35, x+345, y)
            mycanvas.line(x+525,y+35, x+525, y)
            mycanvas.line(x+700,y+35, x+700, y)

            mycanvas.drawCentredString(x+205,y+20,"MILK")
            mycanvas.drawCentredString(x+435,y+20,"CURD")
            mycanvas.drawCentredString(x+610,y+20,"BUTTER MILK")

            mycanvas.setFont('Helvetica', 11)
            mycanvas.drawCentredString(x-10,y,"S.NO")
            mycanvas.drawCentredString(x+40,y,"Date")
            mycanvas.drawCentredString(x+105-5,y,"TM500")
            mycanvas.drawCentredString(x+160-10,y,"STD250")
            mycanvas.drawCentredString(x+220-15,y,"STD500")
            mycanvas.drawCentredString(x+280-20,y,"FCM500")
            mycanvas.drawCentredString(x+345-30,y,"FCM1000")
            mycanvas.drawCentredString(x+410-34,y,"CURD100")
            mycanvas.drawCentredString(x+480-44,y,"CURD150")

            mycanvas.drawCentredString(x+550-55,y,"CURD500")
            mycanvas.drawCentredString(x+615-62,y,"BM200")
            mycanvas.drawCentredString(x+675-65,y,"BMJ200")
            mycanvas.drawCentredString(x+675,y,"BMJF")
            mycanvas.drawCentredString(x+745,y,"Total")

            mycanvas.line(x-25,y+15, x+775, y+15)
            mycanvas.line(x-25,y-10, x+775, y-10)
            y += 20
            mycanvas.setFont('Helvetica', 9)

        y -= 20

    mycanvas.line(x-25,y-15, x+775, y-15)
    mycanvas.line(x+10,y-35, x+775, y-35)

    mycanvas.line(x+10,y-15, x+10, y-35)
    mycanvas.line(x+75,y-15, x+75, y-35)
    mycanvas.line(x+122,y-15, x+122, y-35)
    mycanvas.line(x+175,y-15, x+175, y-35)
    mycanvas.line(x+230,y-15, x+230, y-35)
    mycanvas.line(x+285,y-15, x+285, y-35)
    mycanvas.line(x+345,y-15, x+345, y-35)
    mycanvas.line(x+405,y-15, x+405, y-35)
    mycanvas.line(x+465,y-15, x+465, y-35)
    mycanvas.line(x+525,y-15, x+525, y-35)
    mycanvas.line(x+580,y-15, x+580, y-35)
    mycanvas.line(x+640,y-15, x+640, y-35)
    mycanvas.line(x+700,y-15, x+700, y-35)
    mycanvas.line(x+775,y-15, x+775, y-35)

    mycanvas.line(x+700,y-15, x+700, y-35)
    mycanvas.line(x+775,y-15, x+775, y-35)


    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawRightString(x+70,y-30,"Total Litre")
    mycanvas.drawRightString(x+120,y-30,str(tm_500_ltr))
    mycanvas.drawRightString(x+170,y-30,str(sm_250_ltr))
    mycanvas.drawRightString(x+227,y-30,str(sm_500_ltr))
    mycanvas.drawRightString(x+282,y-30,str(fcm_500_ltr))
    mycanvas.drawRightString(x+340,y-30,str(fcm_1000_ltr))
    mycanvas.drawRightString(x+400,y-30,str(crd_100_ltr))
    mycanvas.drawRightString(x+460,y-30,str(crd_150_ltr))
    mycanvas.drawRightString(x+520,y-30,str(crd_500_ltr))
    mycanvas.drawRightString(x+575,y-30,str(bm_200_ltr))
    mycanvas.drawRightString(x+635,y-30,str(bmj_200_ltr))
    mycanvas.drawRightString(x+695,y-30,str(bmjf_ltr))
    mycanvas.drawRightString(x+770,y-30,str(total_litter))

    mycanvas.showPage()


    # --------------------------------------------------for cost-------------------------------------------
    mycanvas.drawCentredString(405, 575, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')

    x = 45
    y = 500

    mycanvas.setFont('Helvetica-Bold', 11)
    mycanvas.line(x+75,y+35, x+700, y+35)
    mycanvas.line(x+75,y+35, x+75, y)
    mycanvas.line(x+345,y+35, x+345, y)
    mycanvas.line(x+525,y+35, x+525, y)
    mycanvas.line(x+700,y+35, x+700, y)

    mycanvas.drawCentredString(x+205,y+20,"MILK")
    mycanvas.drawCentredString(x+435,y+20,"CURD")
    mycanvas.drawCentredString(x+610,y+20,"BUTTER MILK")

    mycanvas.setFont('Helvetica', 11)
    mycanvas.drawCentredString(x-10,y,"S.NO")
    mycanvas.drawCentredString(x+40,y,"Date")
    mycanvas.drawCentredString(x+105-5,y,"TM500")
    mycanvas.drawCentredString(x+160-10,y,"STD250")
    mycanvas.drawCentredString(x+220-15,y,"STD500")
    mycanvas.drawCentredString(x+280-20,y,"FCM500")
    mycanvas.drawCentredString(x+345-30,y,"FCM1000")
    mycanvas.drawCentredString(x+410-34,y,"CURD100")
    mycanvas.drawCentredString(x+480-44,y,"CURD150")

    mycanvas.drawCentredString(x+550-55,y,"CURD500")
    mycanvas.drawCentredString(x+615-62,y,"BM200")
    mycanvas.drawCentredString(x+675-65,y,"BMJ200")
    mycanvas.drawCentredString(x+675,y,"BMJF")
    mycanvas.drawCentredString(x+745,y,"Total")

    mycanvas.line(x-25,y+15, x+775, y+15)
    mycanvas.line(x-25,y-10, x+775, y-10)

    mycanvas.setFont('Helvetica', 9)
    for index,data in enumerate(final_dict):
        mycanvas.drawString(x-15,y-25,str(index+1))
        mycanvas.drawString(x+20,y-25,str(data))
        mycanvas.drawRightString(x+120,y-25,str(final_dict[data]['Milk']['TM 500']['sale_cost']))
        tm_500_cst += final_dict[data]['Milk']['TM 500']['sale_cost']

        mycanvas.drawRightString(x+170,y-25,str(final_dict[data]['Milk']['STD 250']['sale_cost']))
        sm_250_cst += final_dict[data]['Milk']['STD 250']['sale_cost'] 

        mycanvas.drawRightString(x+225,y-25,str(final_dict[data]['Milk']['STD 500']['sale_cost']))
        sm_500_cst += final_dict[data]['Milk']['STD 500']['sale_cost']    

        mycanvas.drawRightString(x+280,y-25,str(final_dict[data]['Milk']['FCM 500']['sale_cost']))
        fcm_500_cst += final_dict[data]['Milk']['FCM 500']['sale_cost']    

        mycanvas.drawRightString(x+340,y-25,str(final_dict[data]['Milk']['FCM 1000']['sale_cost']))
        fcm_1000_cst += final_dict[data]['Milk']['FCM 1000']['sale_cost']   

        mycanvas.drawRightString(x+400,y-25,str(final_dict[data]['Curd']['Curd 100']['sale_cost']))
        crd_100_cst += final_dict[data]['Curd']['Curd 100']['sale_cost']   

        mycanvas.drawRightString(x+460,y-25,str(final_dict[data]['Curd']['Curd 150']['sale_cost']))
        crd_150_cst += final_dict[data]['Curd']['Curd 150']['sale_cost']   

        mycanvas.drawRightString(x+520,y-25,str(final_dict[data]['Curd']['Curd 500']['sale_cost']))
        crd_500_cst += final_dict[data]['Curd']['Curd 500']['sale_cost']   

        mycanvas.drawRightString(x+575,y-25,str(final_dict[data]['Butter Milk']['BM 200']['sale_cost']))
        bm_200_cst += final_dict[data]['Butter Milk']['BM 200']['sale_cost']    

        mycanvas.drawRightString(x+635,y-25,str(final_dict[data]['Butter Milk']['BMJar']['sale_cost']))
        bmj_200_cst += final_dict[data]['Butter Milk']['BMJar']['sale_cost']   

        mycanvas.drawRightString(x+695,y-25,str(final_dict[data]['Butter Milk']['BMJF']['sale_cost']))
        bmjf_cst += final_dict[data]['Butter Milk']['BMJF']['sale_cost']     

        mycanvas.drawRightString(x+770,y-25,str(final_dict[data]['total_cost']))
        total_cost += final_dict[data]['total_cost']

        #lines 
        mycanvas.line(x-25,y+15, x-25, y-35)
        mycanvas.line(x+10,y+15, x+10, y-35)
        mycanvas.line(x+75,y+15, x+75, y-35)
        mycanvas.line(x+122,y+15, x+122, y-35)
        mycanvas.line(x+175,y+15, x+175, y-35)
        mycanvas.line(x+230,y+15, x+230, y-35)
        mycanvas.line(x+285,y+15, x+285, y-35)
        mycanvas.line(x+345,y+15, x+345, y-35)
        mycanvas.line(x+405,y+15, x+405, y-35)
        mycanvas.line(x+465,y+15, x+465, y-35)
        mycanvas.line(x+525,y+15, x+525, y-35)
        mycanvas.line(x+580,y+15, x+580, y-35)
        mycanvas.line(x+640,y+15, x+640, y-35)
        mycanvas.line(x+700,y+15, x+700, y-35)
        mycanvas.line(x+775,y+15, x+775, y-35)

        if (index + 1) % 22 == 0:
            mycanvas.line(x-25,y-35, x+775, y-35)
            mycanvas.showPage()
            mycanvas.drawCentredString(405, 575, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            x = 45
            y = 500

            mycanvas.setFont('Helvetica-Bold', 11)
            mycanvas.line(x+75,y+35, x+700, y+35)
            mycanvas.line(x+75,y+35, x+75, y)
            mycanvas.line(x+345,y+35, x+345, y)
            mycanvas.line(x+525,y+35, x+525, y)
            mycanvas.line(x+700,y+35, x+700, y)

            mycanvas.drawCentredString(x+205,y+20,"MILK")
            mycanvas.drawCentredString(x+435,y+20,"CURD")
            mycanvas.drawCentredString(x+610,y+20,"BUTTER MILK")

            mycanvas.setFont('Helvetica', 11)
            mycanvas.drawCentredString(x-10,y,"S.NO")
            mycanvas.drawCentredString(x+40,y,"Date")
            mycanvas.drawCentredString(x+105-5,y,"TM500")
            mycanvas.drawCentredString(x+160-10,y,"STD250")
            mycanvas.drawCentredString(x+220-15,y,"STD500")
            mycanvas.drawCentredString(x+280-20,y,"FCM500")
            mycanvas.drawCentredString(x+345-30,y,"FCM1000")
            mycanvas.drawCentredString(x+410-34,y,"CURD100")
            mycanvas.drawCentredString(x+480-44,y,"CURD150")

            mycanvas.drawCentredString(x+550-55,y,"CURD500")
            mycanvas.drawCentredString(x+615-62,y,"BM200")
            mycanvas.drawCentredString(x+675-65,y,"BMJ200")
            mycanvas.drawCentredString(x+675,y,"BMJF")
            mycanvas.drawCentredString(x+745,y,"Total")

            mycanvas.line(x-25,y+15, x+775, y+15)
            mycanvas.line(x-25,y-10, x+775, y-10)
            y += 20
            mycanvas.setFont('Helvetica', 9)

        y -= 20

    mycanvas.line(x-25,y-15, x+775, y-15)
    mycanvas.line(x+10,y-35, x+775, y-35)

    mycanvas.line(x+10,y-15, x+10, y-35)
    mycanvas.line(x+75,y-15, x+75, y-35)
    mycanvas.line(x+122,y-15, x+122, y-35)
    mycanvas.line(x+175,y-15, x+175, y-35)
    mycanvas.line(x+230,y-15, x+230, y-35)
    mycanvas.line(x+285,y-15, x+285, y-35)
    mycanvas.line(x+345,y-15, x+345, y-35)
    mycanvas.line(x+405,y-15, x+405, y-35)
    mycanvas.line(x+465,y-15, x+465, y-35)
    mycanvas.line(x+525,y-15, x+525, y-35)
    mycanvas.line(x+580,y-15, x+580, y-35)
    mycanvas.line(x+640,y-15, x+640, y-35)
    mycanvas.line(x+700,y-15, x+700, y-35)
    mycanvas.line(x+775,y-15, x+775, y-35)

    mycanvas.line(x+700,y-15, x+700, y-35)
    mycanvas.line(x+775,y-15, x+775, y-35)


    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawRightString(x+70,y-30,"Total Cost")
    mycanvas.drawRightString(x+120,y-30,str(tm_500_cst))
    mycanvas.drawRightString(x+170,y-30,str(sm_250_cst))
    mycanvas.drawRightString(x+227,y-30,str(sm_500_cst))
    mycanvas.drawRightString(x+282,y-30,str(fcm_500_cst))
    mycanvas.drawRightString(x+340,y-30,str(fcm_1000_cst))
    mycanvas.drawRightString(x+400,y-30,str(crd_100_cst))
    mycanvas.drawRightString(x+460,y-30,str(crd_150_cst))
    mycanvas.drawRightString(x+520,y-30,str(crd_500_cst))
    mycanvas.drawRightString(x+575,y-30,str(bm_200_cst))
    mycanvas.drawRightString(x+635,y-30,str(bmj_200_cst))
    mycanvas.drawRightString(x+695,y-30,str(bmjf_cst))
    mycanvas.drawRightString(x+770,y-30,str(total_cost))


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
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_excel_for_city_wise_sale_report(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    product_type_id = request.data['product_type_id']

    mor_sale_obj = RouteGroupMap.objects.filter(mor_route__dailysessionllybusinessllysale__delivery_date__range=[from_date, to_date])
    eve_sale_obj = RouteGroupMap.objects.filter(eve_route__dailysessionllybusinessllysale__delivery_date__range=[from_date, to_date])

    if product_type_id == 1:
        product_list = ['tm500_litre', 'tmcan_litre', 'smcan_litre', 'fcm1000_litre', 'fcm500_litre', 'tea1000_litre', 'tea500_litre','std500_litre', 'std250_litre']
        mor_route_group_vlaues = mor_sale_obj.values_list('mor_route__dailysessionllybusinessllysale__tm500_litre', 'mor_route__dailysessionllybusinessllysale__fcm1000_litre', 'mor_route__dailysessionllybusinessllysale__fcm500_litre', 'mor_route__dailysessionllybusinessllysale__tea1000_litre', 'mor_route__dailysessionllybusinessllysale__tea500_litre','mor_route__dailysessionllybusinessllysale__std500_litre', 'mor_route__dailysessionllybusinessllysale__std250_litre', 'mor_route__dailysessionllybusinessllysale__tmcan_litre', 'mor_route__dailysessionllybusinessllysale__smcan_litre', 'mor_route__name', 'route_city__name')                                                                                    
        eve_route_group_vlaues = eve_sale_obj.values_list('eve_route__dailysessionllybusinessllysale__tm500_litre', 'eve_route__dailysessionllybusinessllysale__fcm1000_litre', 'eve_route__dailysessionllybusinessllysale__fcm500_litre', 'eve_route__dailysessionllybusinessllysale__tea1000_litre', 'eve_route__dailysessionllybusinessllysale__tea500_litre', 'eve_route__dailysessionllybusinessllysale__std500_litre', 'eve_route__dailysessionllybusinessllysale__std250_litre', 'eve_route__dailysessionllybusinessllysale__tmcan_litre', 'eve_route__dailysessionllybusinessllysale__smcan_litre', 'eve_route__name', 'route_city__name')
        route_group_columns = ['TM 500', 'FCM 1000', 'FCM 500','TMT 1000', 'TMT 500', 'SM 500', 'SM 250', 'TM Can', 'SM Can', 'Route Name', 'route_city_name']
        mor_sale_df = pd.DataFrame(mor_route_group_vlaues, columns = route_group_columns)
        eve_sale_df = pd.DataFrame(eve_route_group_vlaues, columns = route_group_columns)

        if mor_route_group_vlaues:
            mor_sale_df = mor_sale_df.groupby(['Route Name', 'route_city_name']).agg({'TM 500':sum, 'FCM 1000':sum, 'FCM 500':sum, 'TMT 1000':sum, 'TMT 500':sum, 'SM 500':sum, 'SM 250':sum, 'TM Can':sum, 'SM Can':sum}).reset_index()
            mor_sale_df['Route Name'] = mor_sale_df['Route Name'].str[:-4]

        if eve_route_group_vlaues:
            eve_sale_df = eve_sale_df.groupby(['Route Name', 'route_city_name']).agg({'TM 500':sum, 'FCM 1000':sum, 'FCM 500':sum,'TMT 1000':sum, 'TMT 500':sum, 'SM 500':sum, 'SM 250':sum, 'TM Can':sum, 'SM Can':sum}).reset_index()
            eve_sale_df['Route Name'] = eve_sale_df['Route Name'].str[:-4]

        if eve_route_group_vlaues or mor_route_group_vlaues:
            final_df = pd.concat([mor_sale_df, eve_sale_df])
            final_df = final_df.groupby(['Route Name', 'route_city_name']).agg({'TM 500':sum, 'FCM 1000':sum, 'FCM 500':sum, 'TMT 1000':sum, 'TMT 500':sum, 'SM 500':sum, 'SM 250':sum, 'TM Can':sum, 'SM Can':sum}).reset_index()
        else:
            print('No Data Avaliable')

    if product_type_id == 2:
        product_list = ['curd5000_kgs', 'curd150_kgs', 'curd500_kgs']
        mor_route_group_vlaues = mor_sale_obj.values_list('mor_route__dailysessionllybusinessllysale__curd5000_kgs', 'mor_route__dailysessionllybusinessllysale__curd150_kgs', 'mor_route__dailysessionllybusinessllysale__curd500_kgs', 'mor_route__name', 'route_city__name')                                                                                    
        eve_route_group_vlaues = eve_sale_obj.values_list('eve_route__dailysessionllybusinessllysale__curd5000_kgs', 'eve_route__dailysessionllybusinessllysale__curd150_kgs', 'eve_route__dailysessionllybusinessllysale__curd500_kgs', 'eve_route__name', 'route_city__name')
        route_group_columns = ['CURD 5000', 'CURD 150', 'CURD 500', 'Route Name', 'route_city_name']
        mor_sale_df = pd.DataFrame(mor_route_group_vlaues, columns = route_group_columns)
        eve_sale_df = pd.DataFrame(eve_route_group_vlaues, columns = route_group_columns)

        if mor_route_group_vlaues:
            mor_sale_df = mor_sale_df.groupby(['Route Name', 'route_city_name']).agg({'CURD 5000':sum, 'CURD 150':sum, 'CURD 500':sum}).reset_index()
            mor_sale_df['Route Name'] = mor_sale_df['Route Name'].str[:-4]

        if eve_route_group_vlaues:
            eve_sale_df = eve_sale_df.groupby(['Route Name', 'route_city_name']).agg({'CURD 5000':sum, 'CURD 150':sum, 'CURD 500':sum}).reset_index()
            eve_sale_df['Route Name'] = eve_sale_df['Route Name'].str[:-4]

        if eve_route_group_vlaues or mor_route_group_vlaues:
            final_df = pd.concat([mor_sale_df, eve_sale_df])
            final_df = final_df.groupby(['Route Name', 'route_city_name']).agg({'CURD 5000':sum, 'CURD 150':sum, 'CURD 500':sum}).reset_index()
        else:
            print('No Data Avaliable')

    if product_type_id == 3:
        product_list = ['buttermilk200_litre', 'bm_jar200_litre', 'bmjf200_litre']
        mor_route_group_vlaues = mor_sale_obj.values_list('mor_route__dailysessionllybusinessllysale__buttermilk200_litre', 'mor_route__dailysessionllybusinessllysale__bm_jar200_litre', 'mor_route__dailysessionllybusinessllysale__bmjf200_litre', 'mor_route__name', 'route_city__name')                                                                                    
        eve_route_group_vlaues = eve_sale_obj.values_list('eve_route__dailysessionllybusinessllysale__buttermilk200_litre', 'eve_route__dailysessionllybusinessllysale__bm_jar200_litre', 'eve_route__dailysessionllybusinessllysale__bmjf200_litre', 'eve_route__name', 'route_city__name')
        route_group_columns = ['BM 200', 'BM Jar', 'BMJF', 'Route Name', 'route_city_name']
        mor_sale_df = pd.DataFrame(mor_route_group_vlaues, columns = route_group_columns)
        eve_sale_df = pd.DataFrame(eve_route_group_vlaues, columns = route_group_columns)

        if mor_route_group_vlaues:
            mor_sale_df = mor_sale_df.groupby(['Route Name', 'route_city_name']).agg({'BM 200':sum, 'BM Jar':sum, 'BMJF':sum}).reset_index()
            mor_sale_df['Route Name'] = mor_sale_df['Route Name'].str[:-4]

        if eve_route_group_vlaues:
            eve_sale_df = eve_sale_df.groupby(['Route Name', 'route_city_name']).agg({'BM 200':sum, 'BM Jar':sum, 'BMJF':sum}).reset_index()
            eve_sale_df['Route Name'] = eve_sale_df['Route Name'].str[:-4]

        if eve_route_group_vlaues or mor_route_group_vlaues:
            final_df = pd.concat([mor_sale_df, eve_sale_df])
            final_df = final_df.groupby(['Route Name', 'route_city_name']).agg({'BM 200':sum, 'BM Jar':sum, 'BMJF':sum}).reset_index()
        else:
            print('No Data Avaliable')

    final_df.index += 1

    final_df = final_df.iloc[:, :].astype('float64', errors='ignore')

    # row wise total
    final_df['TOTAL'] = final_df.sum(numeric_only=True,axis=1)

    # column wise total
    final_df.loc['',2:]= final_df.iloc[:, 2:].sum(numeric_only=True, axis=0)
    final_df.iloc[-1, final_df.columns.get_loc('Route Name')] = 'Grand Total'

    #grand_total df
    grand_df = final_df[final_df['Route Name'] == 'Grand Total']

    # -----------------------------------------------------------------------Excel part----------------------------------------------------------------------

    file_name = f'route_wise_sale_details_for_{from_date}_to_{to_date}.xlsx'
    file_path = os.path.join('static/media/monthly_report/', file_name)

    writer = pd.ExcelWriter(file_path , engine="xlsxwriter")

    spacing = 4

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = workbook.add_worksheet('CITY ROUTE WISE SALE')
    writer.sheets['CITY ROUTE WISE SALE'] = worksheet

    merge_dict = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "yellow",
    }

    merge_dict2 = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "cyan",
    }


    merge_format = workbook.add_format(merge_dict)
    merge_format2 = workbook.add_format(merge_dict2)

    # Merge cells.
    product_len = len(product_list)
    ltr = chr(ord('@')+product_len+3)
    ltr = ltr+"2"
    worksheet.merge_range(f"A2:{ltr}", f"City Wise Sale Report For {from_date} to {to_date}", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.000"})

    # Set the column width and format.
    worksheet.set_column("C:H", 18, format1)
    worksheet.set_column(1, 7, 20)

    for route_city in list(RouteCity.objects.filter().order_by('display_ordinal').values_list('name', flat=True)):
        merge_dict['fg_color'] = 'blue'

        ltr1 = 'A'+str(spacing)
        ltr2 = 'B'+str(spacing)

        worksheet.merge_range(f"{ltr1}:{ltr2}", f"{route_city}", merge_format2)
        df = final_df[final_df['route_city_name'] == route_city]
        df = df.drop(columns=['route_city_name'])
        df = df.reset_index(drop=True)
        df.index += 1
        df.loc['',0:]= df.iloc[:, 1:].sum(numeric_only=True, axis=0)
        df.iloc[-1, df.columns.get_loc('Route Name')] = 'Sub Total'
        df.to_excel(writer,sheet_name='CITY ROUTE WISE SALE',startrow=spacing)
        spacing += df.shape[0] + 4

    grand_df = grand_df.drop(columns=['route_city_name']).rename(columns={'Route Name': ''})
    grand_df.to_excel(writer,sheet_name='CITY ROUTE WISE SALE',startrow=spacing)
    writer.save()

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

@api_view(['GET'])
def serve_product_type_list_from_product_finance_code_map(request):
    product_finance_code_dict = list(ProductFinanceCodeMap.objects.filter().values('id', 'group_name'))
    return Response(data=product_finance_code_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_wise_business_for_bill(request):
    data_dict = {}
    main_business_obj = Business.objects.filter()
    main_business_list = list(main_business_obj.values_list('id', 'code', 'zone', 'business_type', 'businessownparlourtypemap__own_parlour_type_id'))
    main_business_column = ['id', 'code', 'zone_id', 'business_type_id', 'own_parlour_type_id']
    main_business_df = pd.DataFrame(main_business_list, columns=main_business_column)
    main_business_df = main_business_df.fillna(0)

    data_dict['union_parlour'] = main_business_df[main_business_df['own_parlour_type_id'] == 1]['code'].to_list()
    data_dict['union_booth'] = main_business_df[main_business_df['own_parlour_type_id'] == 2]['code'].to_list()
    data_dict['private_institute'] = main_business_df[main_business_df['business_type_id'] == 4]['code'].to_list()
    data_dict['govt_institute'] = main_business_df[main_business_df['business_type_id'] == 5]['code'].to_list()
    data_dict['society'] = main_business_df[main_business_df['business_type_id'] == 10]['code'].to_list()
    data_dict['nilgris'] = main_business_df[main_business_df['zone_id'] == 11]['code'].to_list()
    data_dict['tirupur'] = main_business_df[main_business_df['zone_id'] == 13]['code'].to_list()
    return Response(data=data_dict, status=status.HTTP_200_OK)