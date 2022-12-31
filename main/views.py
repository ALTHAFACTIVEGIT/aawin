from by_products.views import generate_by_product_order_code, serve_by_product_price_dict
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
from by_products.models import *
import pandas as pd
from pandas import Timestamp
from decimal import Decimal
from datetime import timedelta, date
# from datetime import datetime
import datetime
import dateutil.relativedelta
from base64 import b64encode, b64decode
#  Plivo credentials
# import plivo
from random import randint
from django.core.files.base import ContentFile
from django.db.models import Sum, Max
from pytz import timezone
from django.db.models import Sum
from calendar import monthrange
from Crypto.Cipher import AES
import hashlib
from Google import Create_Service
from calendar import monthrange, month_name
import calendar
import math

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
import requests
from django.db import transaction
from main.tasks import send_message_from_bsnl

indian = pytz.timezone('Asia/Kolkata')
months_in_english = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                     9: 'September', 10: 'October', 11: 'November', 12: 'December'}
months_in_tamil = {1: 'ஜனவரி', 2: 'பிப்ரவரி', 3: 'மார்ச்', 4: 'ஏப்ரல்', 5: 'மே', 6: 'ஜூன்', 7: 'ஜூலை', 8: 'ஆகஸ்ட்',
                   9: 'செப்டம்பர்', 10: 'அக்டோபர்', 11: 'நவம்பர்', 12: 'டிசம்பர்'}
auth_id = "MAZJZINTYZZTQ4MTG0MT"
auth_token = "NWJkN2Q5MGM2OGI2Njc1MGM3NzMzMmMyZjQyYWIw"

# Axis bank encryption key
test_encryption_key = 'axisbank12345678'
test_checksum_key = 'axis'

# production
encryption_key = '0!EaW^9FwiZSlWF7'
checksum_key = '^aR^'
import pytz
indian = pytz.timezone('Asia/Kolkata')
end_date_for_trace_filter = '2051-05-01'


def send_message_via_netfision(purpose, mobile, message):
    print('camee')
    current_date = datetime.datetime.now().date()
    if DailySmsCount.objects.filter(date=current_date, sms_provider_id=1).exists():
        daily_sms_count_obj = DailySmsCount.objects.filter(date=current_date, sms_provider_id=1)[0]
    else:
        daily_sms_count_obj = DailySmsCount(date=current_date, count=0, sms_provider_id=1)
        daily_sms_count_obj.save()
    print(daily_sms_count_obj.id)
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
    # return True


def decode_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + '.jpeg')


def encode_image(image_path):
    print('encode image function')
    image_path = '{}{}'.format('static/media/', image_path)
    # print(image_path)
    with open(image_path, 'rb') as image_file:
        print('with in with')
        encoded_image = b64encode(image_file.read())
        image = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
        # print(image)
        return image


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_for_token(request):
    print('LOGIN FUNCTION')
    print(request.data)
    if User.objects.filter(username=request.data['user_name'], is_active=True).exists():
        user = authenticate(username=request.data['user_name'], password=request.data['password'])
        print('---------user-----------')
        # print('user id = ', user.id)
        print('user = ', user)
        print('-------------------------')
        if user is not None:
            user_profile_obj = UserProfile.objects.get(user=user)
            if Token.objects.filter(user_id=user.id).exists():
                print('user already logged')
                Token.objects.filter(user_id=user.id).delete()
                print('previous token deleted')
            token = Token.objects.create(user=user)
            print('token created for user')
            user_dict = defaultdict(dict)
            user_dict['token'] = str(token)
            user_dict['user_type_id'] = user_profile_obj.user_type.id
            user_dict['user_id'] = user.id
            user_dict['user_type_name'] = user_profile_obj.user_type.name
            user_dict['first_name'] = user.first_name
            user_dict['server_time'] = datetime.datetime.now().astimezone(indian)
            user_dict['app_version'] = '0.0.11'

            if user_dict['user_type_id'] == 3:
                customer_obj = ICustomer.objects.get(user_profile__user=user)
                user_dict['mobile'] = UserProfile.objects.get(user=user).mobile
                user_dict['is_mobile_verfied'] = customer_obj.is_mobile_number_verified_by_customer
            elif user_dict['user_type_id'] == 2:
                business_obj = Business.objects.get(user_profile__user=user)
                agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=user).agent
                user_dict['mobile'] = agent_obj.agent_profile.mobile
                user_dict['is_mobile_verfied'] = agent_obj.is_mobile_number_verified_by_agent
                user_dict['business_type_id'] = business_obj.business_type.id
                
                business_type_id = business_obj.business_type.id
                business_type_category_obj = BusinessTypeOrderCategoryeMap.objects.filter(business_type_id=business_type_id)
                business_type_category_list = list(business_type_category_obj.values_list('id', 'business_type_id', 'order_category', 'order_category__name', 'payment_option', 'payment_option__name'))
                business_type_category_column = ['id', 'business_type_id', 'order_category_id', 'order_category_name', 'payment_option_id', 'payment_option_name']
                business_type_category_df = pd.DataFrame(business_type_category_list, columns=business_type_category_column)
                user_dict['business_type_wise_order_category_list'] = business_type_category_df.to_dict('r')
            return Response(user_dict)
        else:
            content = {'detail': 'Incorrect User Name/Password!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print('USER DOES NOT EXISTS')
        content = {'detail': 'Incorrect User Name/Password!'}
        return Response(data=content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def portal_login_for_token(request):
    print('LOGIN FUNCTION')
    print(request.data)
    if User.objects.filter(username=request.data['user_name'], is_active=True).exists():
        user = authenticate(username=request.data['user_name'], password=request.data['password'])
        print('---------user-----------')
        # print('user id = ', user.id)
        print('user = ', user)
        print('-------------------------')
        if user is not None:
            if Token.objects.filter(user_id=user.id).exists():
                print('user already logged')
                Token.objects.filter(user_id=user.id).delete()
                print('previous token deleted')
            token = Token.objects.create(user=user)
            print('token created for user')
            user_dict = defaultdict(dict)
            user_dict['token'] = str(token)
            user_dict['user_position_name'] = None
            user_dict['first_name'] = user.first_name
            user_profile_obj = UserProfile.objects.get(user=user)
            profile_image = user_profile_obj.image
            if profile_image != '':
                print('profile_image')
                try:
                    image_path = 'static/media/' + str(profile_image)
                    with open(image_path, 'rb') as image_file:
                        encoded_image = b64encode(image_file.read())
                        user_dict['user_image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
                except Exception as err:
                    print(err)
                    pass
            else:
                user_dict['user_image'] = 'no-image'
            user_dict['user_type_name'] = user_profile_obj.user_type.name
            user_dict['server_time'] = datetime.datetime.now().astimezone(indian)
            if Employee.objects.filter(user_profile__user=user).exists():
                user_dict['employee_id'] = Employee.objects.get(user_profile__user=user).id
                user_dict['user_position_name'] = Employee.objects.filter(user_profile__user=user)[0].role.name
            return Response(user_dict)
        else:
            content = {'detail': 'Incorrect User Name/Password!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print('USER DOES NOT EXISTS')
        content = {'detail': 'Incorrect User Name/Password!'}
        return Response(data=content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def website_login_for_token(request):
    print('LOGIN FUNCTION')
    print(request.data)
    if User.objects.filter(username=request.data['user_name'], is_active=True).exists():
        user = authenticate(username=request.data['user_name'], password=request.data['password'])
        print('---------user-----------')
        # print('user id = ', user.id)
        print('user = ', user)
        print('-------------------------')
        if user is not None:
            if Token.objects.filter(user_id=user.id).exists():
                print('user already logged')
                Token.objects.filter(user_id=user.id).delete()
                print('previous token deleted')
            token = Token.objects.create(user=user)
            print('token created for user')
            user_dict = defaultdict(dict)
            user_dict['token'] = str(token)
            # user_dict['user_id'] = user.id
            # user_dict['user_profile'] = user_profile
            user_dict['first_name'] = user.first_name
            user_dict['user_id'] = user.id
            # user_dict['email'] = user.email
            # user_type_map = TradeUserMap.objects.get(user=user).trade_user_type.name
            user_dict['user_type'] = UserProfile.objects.get(user=user).user_type_id
            user_dict['server_time'] = datetime.datetime.now().astimezone(indian)
            if user_dict['user_type'] == 3:
                customer_obj = ICustomer.objects.get(user_profile__user=user)
                user_dict['mobile'] = UserProfile.objects.get(user=user).mobile
                user_dict['is_mobile_verfied'] = customer_obj.is_mobile_number_verified_by_customer
            else:
                business_obj = Business.objects.get(user_profile__user=user)
                agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=user).agent
                user_dict['mobile'] = agent_obj.agent_profile.mobile
                user_dict['is_mobile_verfied'] = agent_obj.is_mobile_number_verified_by_agent
                user_dict['business_type_id'] = business_obj.business_type.id
                business_type_id = business_obj.business_type.id

                business_type_category_obj = BusinessTypeOrderCategoryeMap.objects.filter(business_type_id=business_type_id)
                business_type_category_list = list(business_type_category_obj.values_list('id', 'business_type_id', 'order_category', 'order_category__name', 'payment_option', 'payment_option__name'))
                business_type_category_column = ['id', 'business_type_id', 'order_category_id', 'order_category_name', 'payment_option_id', 'payment_option_name']
                business_type_category_df = pd.DataFrame(business_type_category_list, columns=business_type_category_column)
                user_dict['business_type_wise_order_category_list'] = business_type_category_df.to_dict('r')
                
            return Response(user_dict)
        else:
            content = {'detail': 'Incorrect User Name/Password!'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        print('USER DOES NOT EXISTS')
        content = {'detail': 'Incorrect User Name/Password!'}
        return Response(data=content, status=status.HTTP_404_NOT_FOUND)


def clean_phone_number(number):
    cleaned_number = ""
    length = len(str(number))
    if length == 12 and number[:2] == "91":
        cleaned_number = number[2:]
    elif length == 10:
        cleaned_number = number

    # if length == 12 and number[:2] == "91":
    #     cleaned_number = number
    # elif length == 10:
    #     cleaned_number = "91" + str(number)
    # else:
    #     cleaned_number = "91" + str(number)
    return int(cleaned_number)


def add_to_phone_number(number):
    cleaned_number = number
    length = len(str(number))

    if length == 12 and str(number)[:2] == "91":
        user = User()
        cleaned_number = number
    elif length == 10:
        cleaned_number = "91" + str(number)
    else:
        cleaned_number = "91" + str(number)
    print("cleaned number: %s" % cleaned_number)
    return int(cleaned_number)


def generate_otp():
    return str(random.randint(1000, 9999))


def generate_password():
    return str(random.randint(1000, 9999))


def generate_booth_password():
    return str(random.randint(10000, 99999))


# def send_message(to, message, purpose, user_id=None):
#     """
#        Send message to a single phone number via plivo service 0.0037 USD/sms; only outgoing
#        :return:
#        """
#     try:
#         print("original to:%s" % to)
#         to_good = add_to_phone_number(to)
#         print("91 added to:%s" % to_good)
#         client = plivo.RestClient(auth_id=auth_id, auth_token=auth_token)
#         message_created = client.messages.create(
#             src='919500989012',
#             dst=to_good,
#             text=message
#         )
#         # obj = SMSTrace(union_id=1, message=message, receiver_user_id=user_id, purpose='Password reset')
#         # obj.save()
#         if user_id is not None:
#             sms_trace_obj = SMSTrace(
#                 union_id=1,
#                 receiver_user_id=user_id,
#                 purpose=purpose,
#                 message=message
#             )
#             sms_trace_obj.save()
#             print('SMS Trace is saved')
#         else:
#             sms_trace_obj = SMSTrace(
#                 union_id=1,
#                 purpose=purpose,
#                 message=message
#             )
#             sms_trace_obj.save()
#             print('SMS Trace is saved')
#         # params = {'src': '919500989012', 'method': 'POST', 'dst': '918940341505', 'text': 'messgae'}
#         # params = {'src': '919500989012', 'method': 'POST', 'dst': to_good, 'text': message}

#         # response = p.send_message(params)
#         print('response = {}'.format(message_created))
#     except Exception as e:
#         print('=====ERROR====')
#         print(e)


@api_view(['POST'])
@permission_classes((AllowAny,))
def username_validation(request):
    print(request.data)
    if User.objects.filter(username=request.data['user_name']).exists():
        user = User.objects.get(username=request.data['user_name'])
        user_obj = UserProfile.objects.get(user=user)
        print(user_obj.mobile)
        if user_obj.mobile == None:
            data = {'message': 'Phone number does not Exists!'}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
        otp = generate_otp()
        now = datetime.datetime.now()
        expiry_time = now + datetime.timedelta(minutes=30)
        
        password_reset_obj = PasswordResetRequest(
            user=user,
            otp=otp,
            expiry_time=expiry_time,
        )
        password_reset_obj.save()
        print(otp)
        user_details = {
            'user_id': user.id,
            'user_name': user.username,
            'mobile': user_obj.mobile,
        }
        template_id = BsnlSmsTemplate.objects.filter(message_name='password_otp').first().template_id
        template_list = [
            {'Key': 'otp', 'Value': str(otp)}
        ]
        send_message_from_bsnl(template_id, template_list, user_obj.mobile)
        return Response(data=user_details, status=status.HTTP_200_OK)
    else:
        data = {'message': 'User does not Exists!'}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['POST'])
@permission_classes((AllowAny,))
def otp_validation(request):
    if PasswordResetRequest.objects.filter(user=request.data['user_id'],
                                           expiry_time__gte=datetime.datetime.now()).exists():
        password_reset_obj = PasswordResetRequest.objects.filter(user=request.data['user_id'],
                                                                 expiry_time__gte=datetime.datetime.now()).order_by(
            '-id')[0]
        print(password_reset_obj.otp)
        if request.data['otp'] == password_reset_obj.otp:
            return Response(data='Correct otp', status=status.HTTP_200_OK)
        else:
            data = {'message': 'OTP does Not Match'}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        data = {'message': 'Please Try After Some Time'}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['POST'])
@permission_classes((AllowAny,))
def reset_password(request):
    print(request.data)
    if User.objects.filter(id=request.data['user_id']).exists():
        user_obj = User.objects.get(id=request.data['user_id'])
        user_obj.password = make_password(request.data['raw_password'])
        user_obj.save()
        print('password is updated')
        return Response(status=status.HTTP_200_OK)


def serve_product_and_session_list(user_profile_id):
    business_id = BusinessAgentMap.objects.get(business__user_profile_id=user_profile_id, is_active=True).business_id
    business_type_id = Business.objects.get(id=business_id).business_type_id
    commission_product_ids = list(
        BusinessProductConcessionMap.objects.filter(business_type_id=business_type_id, product__is_active=True,
                                                    concession_type_id=1).values_list(
            'product_id', flat=True))
    discount_product_ids = list(
        BusinessProductConcessionMap.objects.filter(business_type_id=business_type_id, product__is_active=True,
                                                    concession_type_id=2).values_list(
            'product_id', flat=True))
    product_obj = Product.objects.filter(is_active=True, id__in=commission_product_ids).order_by(
        'display_ordinal').exclude(group_id=3)
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'color', 'minimum_quantity'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'color', 'minimum_quantity']
    product_df = pd.DataFrame(product_list, columns=product_column)
    if business_type_id == 1 or business_type_id == 2 or business_type_id == 3 or business_type_id == 9 or business_type_id == 11 or business_type_id == 16:
        discounted_product_obj = BusinessTypeWiseProductDiscount.objects.filter(business_type_id=business_type_id,
                                                                                product__is_active=True,
                                                                                product_id__in=discount_product_ids).order_by(
            'product__display_ordinal').exclude(product__group_id=3)
        discounted_product_list = list(
            discounted_product_obj.values_list('product_id', 'product__group', 'product__group__name',
                                               'product__name', 'product__short_name', 'product__code',
                                               'product__unit',
                                               'product__unit__display_name', 'product__description',
                                               'product__quantity', 'discounted_price', 'product__gst_percent',
                                               'product__color', 'product__minimum_quantity'))
        discounted_product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name',
                                     'product_short_name',
                                     'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity',
                                     'product_mrp',
                                     'gst_percent', 'color', 'minimum_quantity']
        discounted_product_df = pd.DataFrame(discounted_product_list, columns=discounted_product_column)
    else:
        discounted_product_obj = BusinessWiseProductDiscount.objects.filter(business_id=business_id,
                                                                            product__is_active=True,
                                                                            product_id__in=discount_product_ids).order_by(
            'product__display_ordinal').exclude(product__group_id=3)
        discounted_product_list = list(
            discounted_product_obj.values_list('product_id', 'product__group', 'product__group__name',
                                               'product__name', 'product__short_name', 'product__code',
                                               'product__unit',
                                               'product__unit__display_name', 'product__description',
                                               'product__quantity', 'discounted_price', 'product__gst_percent',
                                               'product__color', 'product__minimum_quantity'))
        discounted_product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name',
                                     'product_short_name',
                                     'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity',
                                     'product_mrp',
                                     'gst_percent', 'color', 'minimum_quantity']
        discounted_product_df = pd.DataFrame(discounted_product_list, columns=discounted_product_column)
    final_product_df = product_df.merge(discounted_product_df, how="outer")
    loose_milk_obj = ProductQuantityVariationPrice.objects.filter(min_quantity=1, product__is_active=True).order_by(
        'product__display_ordinal')
    loose_milk_list = list(
        loose_milk_obj.values_list('product_id', 'product__group', 'product__group__name', 'product__name',
                                   'product__short_name', 'product__code', 'product__unit',
                                   'product__unit__display_name', 'product__description', 'product__quantity', 'mrp',
                                   'product__gst_percent', 'product__color', 'product__minimum_quantity'))
    loose_milk_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                         'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                         'gst_percent', 'color', 'minimum_quantity']
    loose_milk_df = pd.DataFrame(loose_milk_list, columns=loose_milk_column)
    final_product_df = final_product_df.merge(loose_milk_df, how="outer")
    final_product_df = final_product_df.fillna(0)
    route_session_obj = RouteBusinessMap.objects.filter(business_id=business_id).order_by('route__session')
    route_session_list = list(
        route_session_obj.values_list('route__session', 'route__session__name', 'route__session__display_name',
                                      'route__session__expiry_day_before', 'route__order_expiry_time'))
    route_session_column = ['id', 'name', 'display_name', 'expiry_day_before', 'expiry_time']
    route_session_df = pd.DataFrame(route_session_list, columns=route_session_column)
    product_quantity_variation_obj = ProductQuantityVariationPrice.objects.filter(product__is_active=True)
    product_quantity_variation_list = list(
        product_quantity_variation_obj.values_list('id', 'product', 'min_quantity', 'max_quantity', 'mrp'))
    product_quantity_variation_column = ['id', 'product_id', 'min_quantity', 'max_quantity', 'mrp']
    product_quantity_variation_df = pd.DataFrame(product_quantity_variation_list,
                                                 columns=product_quantity_variation_column)
    business_type_wise_product_minimum_obj = BusinessTypeWiseProductMinimumQuantityInLitre.objects.all()
    # product wise minimum quantity
    product_wise_minimum_obj = ProductWiseMinimumQuantity.objects.all()
    product_wise_minimum_list = list(product_wise_minimum_obj.values_list('id', 'product_id', 'value_in_quantity'))
    product_wise_minimum_column = ['id', 'product_id', 'value_in_quantity']
    product_wise_minimum_df = pd.DataFrame(product_wise_minimum_list, columns=product_wise_minimum_column)
    obj_dict = {}
    for obj in business_type_wise_product_minimum_obj:
        if not obj.business_type_id in obj_dict:
            obj_dict[obj.business_type_id] = {}
        if not obj.product_id in obj_dict[obj.business_type_id]:
            obj_dict[obj.business_type_id][obj.product.id] = obj.value_in_litre

    overall_litre_obj = {}
    for obj in BusinessTypeWiseOverallLitreLimit.objects.all():
        if not obj.business_type_id in overall_litre_obj:
            overall_litre_obj[obj.business_type_id] = obj.litre_limit

    business_wise_future_order = BusinessTypeWiseFutureOrderConfig.objects.all()
    business_wise_future_order_list = list(business_wise_future_order.values_list('business_type', 'is_future_order_accept'))
    business_wise_future_order_column = ['business_type', 'is_future_order_accept']
    business_wise_future_order_df = pd.DataFrame(business_wise_future_order_list, columns=business_wise_future_order_column)
    business_wise_future_order_dict = business_wise_future_order_df.groupby('business_type').apply(lambda x:x.to_dict('r')[0]).to_dict()

    if BusinessWiseMilkLitreLimit.objects.filter(business_id=business_id).exists():
        milk_litre_limit = BusinessWiseMilkLitreLimit.objects.get(business_id=business_id).limit_in_litre
    else:
        milk_litre_limit = 0
    milk_product_list = list(Product.objects.filter(group_id=1).values('id', 'quantity'))
    future_order_alert_content = 'நாளைக்கான ஆர்டர் முன்பே பதியப்பட்டு விட்டது. வேறு ஒரு நாளைக்காக புதிய ஆர்டர்'
    data_dict = {
        'product_list': final_product_df.to_dict('r'),
        'session_list': route_session_df.to_dict('r'),
        'product_groupby_list': final_product_df.groupby('product_group_id')['product_id'].apply(list).to_dict(),
        'product_quantity_variation_list': product_quantity_variation_df.groupby('product_id').apply(
            lambda x: x.to_dict('r')).to_dict(),
        'minimum_quantity_for_product': obj_dict,
        'overall_litre_limit': overall_litre_obj,
        'product_wise_minimum_quantity': product_wise_minimum_df.groupby('product_id').apply(
            lambda x: x.to_dict('r')[0]).to_dict(),
        'business_wise_future_order_dict': business_wise_future_order_dict,
        'future_order_alert_content': future_order_alert_content,
        'milk_litre_limit': milk_litre_limit,
        'milk_product_list': milk_product_list
    }
    return data_dict


@api_view(['POST'])
def serve_product_list(request):
    if request.data['from'] == 'portal':
        business_code = request.data['business_code']
        business = Business.objects.get(code=business_code)
        print(business.user_profile_id)
        data_dict = serve_product_and_session_list(business.user_profile_id)
        data_dict['product_availability'] = serve_product_availability()
        return Response(data=data_dict, status=status.HTTP_200_OK)
    elif request.data['from'] == 'mobile' or request.data['from'] == 'website':
        data_dict = serve_product_and_session_list(request.user.userprofile.id)
        data_dict['product_availability'] = serve_product_availability()
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_user_types(request):
    user_types = UserType.objects.filter()
    user_type_values = user_types.values_list('id', 'name')
    user_types_columns = ['id', 'name']
    data = pd.DataFrame(list(user_type_values), columns=user_types_columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_location_cv(request):
    location_dict = {'state': [], 'district': {}, 'taluk': {}}
    state_values = State.objects.all().values_list('id', 'name')
    state_columns = ['id', 'name']
    state_df = pd.DataFrame(list(state_values), columns=state_columns)
    location_dict['state'] = state_df.groupby('name').apply(lambda x: x.to_dict('r')).to_dict()

    district_values = District.objects.all().values_list('id', 'name')
    district_columns = ['id', 'name']
    district_df = pd.DataFrame(list(district_values), columns=district_columns)
    location_dict['district'] = district_df.groupby('name').apply(lambda x: x.to_dict('r')).to_dict()

    taluk_values = Taluk.objects.all().values_list('id', 'name')
    taluk_columns = ['id', 'name']
    taluk_df = pd.DataFrame(list(taluk_values), columns=taluk_columns)
    location_dict['taluk'] = taluk_df.groupby('name').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=location_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_or_update_zone(request):
    print(request.data)
    union = Union.objects.filter()[0]
    data = {'message': ''}
    if request.data['id'] == None:
        if Zone.objects.filter(union=union, name__iexact=request.data['name']).exists():
            data['message'] = "zone already registered"
        else:
            zone = Zone.objects.create(union=union, name=request.data['name'])
            data['message'] = '{} registered successfully!'.format(zone.name)
    else:
        old_zone_name = Zone.objects.get(id=request.data['id']).name
        Zone.objects.filter(id=request.data['id']).update(name=request.data['name'])
        data['message'] = '"{old_zone}" is updated to "{new_zone}"'.format(old_zone=old_zone_name,
                                                                           new_zone=request.data['name'])

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_booth_type(request):
    print(request.data)
    data = {'message': ''}
    if request.data['id'] == None:
        if BusinessType.objects.filter(name__iexact=request.data['name'], code=request.data['code']).exists():
            data['message'] = 'Business Type Already Registered!'
        else:
            BusinessType.objects.create(name=request.data['name'], code=request.data['code'])
            data['message'] = 'Business Type Registered Successfully!'
    else:
        BusinessType.objects.filter(id=request.data['id']).update(name=request.data['name'], code=request.data['code'])
        data['message'] = 'Business Type Updated Successfully'
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_district(request):
    print(request.data)
    district_values = District.objects.filter().values_list('id', 'name', 'state_id', 'state__name', 'code', 'capital')
    district_columns = ['id', 'name', 'state_id', 'state_name', 'code', 'capital']
    district_df = pd.DataFrame((list(district_values)), columns=district_columns)
    data = district_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_constituency(request):
    print(request.data)
    data = {'message': ''}
    if request.data['id'] == None:
        district = District.objects.all()[0]
        if Constituency.objects.filter(district=district, name_iexact=request.data['name']).exists():
            data['message'] = 'Constituency already registered'
        else:
            constituency = Constituency.objects.create(district=district, name=request.data['name'])
            data['message'] = '{} registered successfully!'.format(constituency.name)
    else:
        old_constituency_name = Constituency.objects.get(id=request.data['id']).name
        Constituency.objects.filter(id=request.data['id']).update(name=request.data['name'])
        data['message'] = '"{old_constituency}" is updated to "{new_consituency}"'.format(
            old_constituency=old_constituency_name, new_consituency=request.data['name'])
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_ward(request):
    print(request.data)
    data = {'message': ''}
    if request.data['ward_id'] is None:
        # save new ward
        if Ward.objects.filter(constituency_id=request.data['constituency_id'], name__iexact=request.data['name'],
                               number=request.data['ward_number'],
                               corporation_zone_id=request.data['corporataion_zone']).exists():
            data['message'] = 'Ward is Already registered'
        else:
            ward = Ward.objects.create(constituency_id=request.data['constituency_id'], name=request.data['name'],
                                       number=request.data['ward_number'],
                                       corporation_zone_id=request.data['corporataion_zone'])
            data['message'] = '{ward_name} is registered successfully!'.format(ward_name=ward.name)
    else:
        print('edit')
        # update ward
        old_constituency_name = Constituency.objects.get(id=request.data['constituency_id']).name
        old_ward_name = Ward.objects.get(id=request.data['ward_id']).name
        ward = Ward.objects.get(id=request.data['ward_id'])
        ward.constituency_id = request.data['constituency_id']
        ward.name = request.data['name']
        ward.number = request.data['ward_number']
        ward.corporation_zone_id = request.data['corporataion_zone']
        ward.save()
        print('ward saved')
        data['message'] = 'Update {old_ward} under {old_constituency} to {new_ward} under {new_constituency}'.format(
            old_ward=old_ward_name,
            old_constituency=old_constituency_name,
            new_ward=ward.name,
            new_constituency=ward.constituency.name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_constituency(request):
    print(request.data)
    constituency_values = Constituency.objects.filter().values_list('id', 'name', 'district__name')
    constituency_columns = ['id', 'name', 'district_name']
    constituency_df = pd.DataFrame((list(constituency_values)), columns=constituency_columns)
    data = constituency_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_zones(request):
    values = Zone.objects.filter().order_by('id').values_list('id', 'name', 'union__name')
    columns = ['id', 'name', 'union_name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_mor_routes(request):
    values = Route.objects.filter(is_temp_route=False, session_id=1).order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_booth_types(request):
    values = BusinessType.objects.filter().order_by('id').values_list('id', 'name', 'code')
    columns = ['id', 'name', 'code']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_wards(request):
    values = Ward.objects.filter().order_by('name').values_list('id', 'name', 'constituency', 'constituency__name',
                                                                'number', 'corporation_zone_id',
                                                                'corporation_zone__name')
    columns = ['id', 'name', 'constituency_id', 'constituency_name', 'ward_number', 'corporation_zone',
               'corporation_zone_name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_agents(request):
    values = BusinessAgentMap.objects.filter().values_list('business__zone__name', 'agent__agent_code',
                                                           'agent__first_name', 'agent__last_name', 'business__code',
                                                           'business__business_type__name',
                                                           'agent__agent_profile__mobile',
                                                           'agent__agent_profile__gender__name', 'business_id',
                                                           'agent_id')

    columns = ['zone_name', 'agent_code', 'first_name', 'last_name', 'business_code', 'business_type', 'mobile',
               'gender', 'business_id', 'agent_id']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def serve_agents(request):
#     values = Agent.objects.filter().order_by('id').values_list(
#         'id', 'user_profile', 'user_profile__user_id', 'user_profile__user__first_name', 'user_profile__user__last_name', 'user_profile__user__username', 'user_profile__union_id', 'user_profile__user_type_id', 'user_profile__street', 'user_profile__gender__name', 'user_profile__gender__id', 'user_profile__taluk_id', 'user_profile__taluk__name', 'user_profile__district_id', 'user_profile__district__name', 'user_profile__state_id', 'user_profile__pincode', 'user_profile__mobile', 'user_profile__alternate_mobile',
#         'agent_code', 'relation_type_id', 'relation_name', 'aadhar_number', 'pan_number', 'ration_card_number','communication_address')
#     columns = ['agent_id', 'user_profile_id', 'user_id', 'first_name', 'last_name', 'username', 'union_id', 'user_type_id', 'street', 'gender','gender_id', 'taluk_id', 'taluk', 'district_id', 'district', 'state_id', 'pincode', 'mobile', 'alternate_mobile', 'agent_code', 'relation_type_id',
#     'relation_name', 'aadhar_number', 'pan_number', 'ration_card_number',  'communication_address']
#     df = pd.DataFrame(list(values), columns=columns)
#
#     business_agent_map = BusinessAgentMap.objects.all()
#     business_agent_values = business_agent_map.values_list('id', 'agent_id','business__code', 'business__business_type__name')
#     business_agent_columns = ['id', 'agent_id', 'booth_code','booth_type']
#     business_agent_df = pd.DataFrame(list(business_agent_values), columns=business_agent_columns)
#     merged_df = pd.merge(df, business_agent_df, left_on='agent_id', right_on='agent_id', how='left')
#     merged_df = merged_df.fillna(0)
#     data = merged_df.to_dict('r')
#     print('dataframe')
#     return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_product_group(request):
    values = ProductGroup.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_product_group(request):
    print(request.data)
    data = {'message': ''}
    if request.data['id'] is None:
        # save new ward
        if ProductGroup.objects.filter(name__iexact=request.data['name']).exists():
            data['message'] = 'product group already registered!'
        else:
            product_group = ProductGroup.objects.create(name=request.data['name'])
            data['message'] = '{product_group_name} is registered successfully!'.format(
                product_group_name=product_group.name)
    else:
        print('edit')
        # update ward
        product_group = ProductGroup.objects.get(id=request.data['id'])
        product_group.name = request.data['name']
        product_group.save()
        print('ward saved')
        data['message'] = 'Product Group updated successfully'
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_product(request):
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    # Current time in UTC
    now_utc = datetime.datetime.now(timezone('UTC'))
    print(now_utc.strftime(format))
    # Convert to Asia/Kolkata time zone
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata')) 
    print(now_asia.strftime(format))
    # This will give the output:
    formatted_date = now_asia
    print(request.data)
    data = {'message': ''}
    if request.data['id'] is None:  # save product
        product = Product.objects.create(
            name=request.data['name'],
            group_id=request.data['group_id'],
            short_name=request.data['short_name'],
            base_price=request.data['base_price'],
            code=request.data['code'],
            unit_id=request.data['unit_id'],
            description=request.data['description'],
            quantity=request.data['quantity'],
            mrp=request.data['mrp'],
            gst_percent=request.data['gst_percent'],
            snf=request.data['snf'],
            fat=request.data['snf'],
            is_homogenised=request.data['is_homogenised'],
            display_ordinal=0,
            private_institute_price=request.data['pvt_discount_price'],
            govt_institute_price=request.data['gvt_discount_price'],
            society_price=request.data['society_price']
        )

        ProductTrace.objects.create(
            product=product,
            start_date=formatted_date,
            end_date=end_date_for_trace_filter,
            product_price_started_by=request.user,
            name=request.data['name'],
            short_name=request.data['short_name'],
            base_price=request.data['base_price'],
            code=request.data['code'],
            unit_id=request.data['unit_id'],
            quantity=request.data['quantity'],
            mrp=request.data['mrp'],
            gst_percent=request.data['gst_percent'],
            snf=request.data['snf'],
            fat=request.data['fat'],
            is_homogenised=request.data['is_homogenised'],
        )
        sessions = Session.objects.all().values_list('id', flat=True)
        for session in sessions:
            ProductAvailabilityMap.objects.create(product=product, session_id=session)
        data['message'] = '{product_name} is registered successfully!'.format(product_name=product.name)

    else:  # update product
        print('edit')
        formatted_date = now_asia + timedelta(days=1)
        product = Product.objects.get(id=request.data['id'])
        # product trace
        if ProductTrace.objects.filter(product=product).order_by('-time_created').exists():
            if product.mrp != request.data['mrp']:
                ProductTrace.objects.filter(product=product, end_date=end_date_for_trace_filter).update(
                    end_date=datetime.datetime.now(),
                    product_price_ended_by=request.user,
                )
                ProductTrace.objects.create(
                    product=product,
                    start_date=formatted_date,
                    end_date=end_date_for_trace_filter,
                    name=request.data['name'],
                    short_name=request.data['short_name'],
                    code=request.data['code'],
                    unit_id=request.data['unit_id'],
                    base_price=request.data['base_price'],
                    quantity=request.data['quantity'],
                    mrp=request.data['mrp'],
                    gst_percent=request.data['gst_percent'],
                    snf=request.data['snf'],
                    fat=request.data['fat'],
                    is_homogenised=request.data['is_homogenised'],
                    product_price_started_by=request.user
                )
        else:
            ProductTrace.objects.create(
                product=product,
                start_date=formatted_date,
                end_date=end_date_for_trace_filter,
                name=request.data['name'],
                short_name=request.data['short_name'],
                code=request.data['code'],
                unit_id=request.data['unit_id'],
                base_price=request.data['base_price'],
                quantity=request.data['quantity'],
                mrp=request.data['mrp'],
                gst_percent=request.data['gst_percent'],
                snf=request.data['snf'],
                fat=request.data['fat'],
                is_homogenised=request.data['is_homogenised'],
                product_price_started_by=request.user
            )
            print('old trace log expired')
        # product update
        old_product_name = Product.objects.get(id=request.data['id']).name
        product.name = request.data['name']
        product.base_price = request.data['base_price']
        product.group_id = request.data['group_id']
        product.short_name = request.data['short_name']
        base_price = request.data['base_price']
        product.code = request.data['code']
        product.unit_id = request.data['unit_id']
        product.description = request.data['description']
        product.quantity = request.data['quantity']
        product.mrp = request.data['mrp']
        product.gst_percent = request.data['gst_percent']
        product.snf = request.data['snf']
        product.fat = request.data['fat']
        product.is_homogenised = request.data['is_homogenised']
        product.private_institute_price = request.data['pvt_discount_price']
        product.govt_institute_price = request.data['gvt_discount_price']
        product.society_price = request.data['society_price']
        product.save()
        print('product saved')
        # return statement
        data['message'] = 'Update {old_product_name} to {new_product_name} Successfully!'.format(
            old_product_name=old_product_name,
            new_product_name=product.name)

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_product(request):
    values = Product.objects.filter(is_active=True).order_by('display_ordinal').values_list('id', 'name', 'base_price',
                                                                                            'group_id', 'group__name',
                                                                                            'short_name', 'code',
                                                                                            'unit_id', 'unit__name',
                                                                                            'description', 'quantity',
                                                                                            'mrp', 'gst_percent', 'snf',
                                                                                            'fat', 'is_homogenised',
                                                                                            'private_institute_price',
                                                                                            'govt_institute_price',
                                                                                            'society_price')
    columns = ['id', 'name', 'base_price', 'group_id', 'group_name', 'short_name', 'code', 'unit_id', 'unit_name',
               'description', 'quantity', 'mrp', 'gst_percent', 'snf', 'fat', 'is_homogenised',
               'private_institute_price', 'govt_institute_price', 'society_price']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_product_unit(request):
    values = ProductUnit.objects.filter().order_by('name').values_list('id', 'name', 'display_name')
    columns = ['id', 'name', 'display_name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_product_unit(request):
    print(request.data)
    data = {'message': ''}
    if request.data['id'] is None:  # save product
        if ProductUnit.objects.filter(name__iexact=request.data['name'],
                                      display_name__iexact=request.data['display_name']).exists():
            data['message'] = 'product unit is already registered'
        else:
            product_unit = ProductUnit.objects.create(name=request.data['name'],
                                                      display_name=request.data['display_name'])
            data['message'] = '{product_unit_name} is registered successfully!'.format(
                product_unit_name=product_unit.name)
    else:  # update product
        print('edit')
        product_unit = ProductUnit.objects.get(id=request.data['id'])
        product_unit.name = request.data['name']
        product_unit.display_name = request.data['display_name']
        product_unit.save()
        data['message'] = 'Product updated successfully'
    return Response(data=data, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
def register_order_for_agent(request):
    # print(request.data)
    sid = transaction.savepoint()
    try:
        if request.data['from'] == 'portal':
            business_id = Business.objects.get(code=request.data['business_code']).id
            business_type_id = Business.objects.get(code=request.data['business_code']).business_type.id
            user_profile_id = Business.objects.get(code=request.data['business_code']).user_profile_id
            agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
            agent_user_id = Business.objects.get(id=business_id).user_profile.user.id
            via_id = 2
        elif request.data['from'] == 'mobile':
            user_profile_id = request.user.userprofile.id
            business_id = Business.objects.get(user_profile_id=user_profile_id).id
            agent_user_id = Business.objects.get(id=business_id).user_profile.user.id
            agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
            business_type_id = Business.objects.get(id=business_id).business_type.id
            via_id = 1
        elif request.data['from'] == 'website':
            user_profile_id = request.user.userprofile.id
            business_id = Business.objects.get(user_profile_id=user_profile_id).id
            agent_user_id = Business.objects.get(id=business_id).user_profile.user.id
            agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
            business_type_id = Business.objects.get(id=business_id).business_type.id
            via_id = 3

        business_obj = Business.objects.get(id=business_id)
        data_dict = serve_product_and_session_list(user_profile_id)
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        product_quantity_variation_list = data_dict['product_quantity_variation_list']
        product_form_details = request.data['product_form_details']
        agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
        temp_wallet_amount = agent_wallet_obj.current_balance
        counter_id = None
        is_order_placed = False
        for date in request.data['order_date']:
            sale_group_ids = {
                1: None,
                2: None
            }
            if SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date).exists():
                super_sale_group_obj = SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date)[0]
            else:
                super_sale_group_obj = SuperSaleGroup(business_id=business_id, delivery_date=date)
                super_sale_group_obj.save()
            for session in session_list:
                if not SaleGroup.objects.filter(date=date, session_id=session['id'], business_id=business_id).exists():
                    total_cost_per_session = 0
                    route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                            route__session_id=session['id']).route_id
                    vehicle_obj = RouteVehicleMap.objects.get(route_id=route_id).vehicle
                    if product_form_details[date]['total_price_per_session'][str(session['id'])] != 0:
                        sale_group_obj = SaleGroup(
                            business_id=business_id,
                            business_type_id=business_type_id,
                            date=date,
                            session_id=session['id'],
                            ordered_via_id=via_id,
                            payment_status_id=1,  # paid m
                            sale_status_id=1,  # ordered
                            total_cost=0,
                            ordered_by=request.user,
                            modified_by=request.user,
                            product_amount=0,
                            route_id=route_id,
                            zone_id=business_obj.zone.id
                        )
                        sale_group_obj.save()
                        is_order_placed = True
                        # print('sale group saved')
                        for product in product_list:
                            product_quantity = \
                            product_form_details[date]['product'][str(session['id'])][str(product['product_id'])][
                                'quantity']
                            if product_quantity != 0 and product_quantity != None:
                                if product['product_group_id'] == 3:
                                    for variation_price in product_quantity_variation_list[product['product_id']]:
                                        if product_quantity >= variation_price['min_quantity'] and product_quantity <= \
                                                variation_price['max_quantity']:
                                            product_cost = product_quantity * variation_price['mrp']
                                else:
                                    product_cost = product_quantity * product['product_mrp']
                                sale_obj = Sale(
                                    sale_group_id=sale_group_obj.id,
                                    product_id=product['product_id'],
                                    count=product_quantity,
                                    cost=product_cost,
                                    ordered_by=request.user,
                                    modified_by=request.user
                                )
                                sale_obj.save()
                                if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                    if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                        free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                        eligible_product_count = free_product_property_obj.eligible_product_count
                                        defalut_free_product_count = free_product_property_obj.product_count
                                        if product_quantity >= eligible_product_count:
                                            box_count = math.floor(product_quantity/eligible_product_count)
                                            free_product_count = box_count*defalut_free_product_count
                                            sale_obj = Sale(
                                                sale_group_id=sale_group_obj.id,
                                                product_id=free_product_property_obj.free_product.id,
                                                count=free_product_count,
                                                cost=0,
                                                ordered_by_id=1,
                                                modified_by_id=1
                                            )
                                            sale_obj.save()


                                total_cost_per_session += product_cost
                                # For agent check route exiist for selected date, session, and routeid, if exists check routesalesummary exists and update the product quantity, if not
                                # create routettrase wise sale summary and add product quantity
                                if RouteTrace.objects.filter(date=date, session_id=session['id'],
                                                            route_id=route_id).exists():
                                    route_trace_obj = RouteTrace.objects.get(date=date, session_id=session['id'],
                                                                            route_id=route_id)
                                    if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id,
                                                                                product_id=product['product_id']).exists():
                                        route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.filter(
                                            route_trace_id=route_trace_obj.id, product_id=product['product_id'])[0]
                                        route_trace_sale_summary_obj.quantity += product_quantity
                                        route_trace_sale_summary_obj.save()
                                    else:
                                        route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(
                                            route_trace_id=route_trace_obj.id, product_id=product['product_id'],
                                            quantity=product_quantity)
                                        route_trace_sale_summary_obj.save()
                                else:
                                    route_trace_obj = RouteTrace(indent_status_id=1,  # initiated
                                                                route_id=route_id,
                                                                vehicle_id=vehicle_obj.id,
                                                                date=date,
                                                                session_id=session['id'],
                                                                driver_name=vehicle_obj.driver_name,
                                                                driver_phone=vehicle_obj.driver_mobile)
                                    route_trace_obj.save()
                                    route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(
                                        route_trace_id=route_trace_obj.id,
                                        product_id=product['product_id'],
                                        quantity=product_quantity)
                                    route_trace_sale_summary_obj.save()
                                if OverallIndentPerSession.objects.filter(date=date, session_id=session['id']).exists():
                                    overall_route_trace_obj = OverallIndentPerSession.objects.get(date=date,
                                                                                                session_id=session['id'])
                                    overall_route_trace_obj.route_trace.add(route_trace_obj)
                                    overall_route_trace_obj.save()
                                else:
                                    overall_route_trace_obj = OverallIndentPerSession(date=date,
                                                                                    session_id=session['id'],
                                                                                    overall_indent_status_id=1,
                                                                                    created_by_id=1)  # aavin
                                    overall_route_trace_obj.save()
                                    overall_route_trace_obj.route_trace.add(route_trace_obj)
                                    overall_route_trace_obj.save()
                        saved_sale_group_obj = SaleGroup.objects.get(id=sale_group_obj.id)
                        saved_sale_group_obj.total_cost = total_cost_per_session
                        saved_sale_group_obj.product_amount = total_cost_per_session
                        credit_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=2, order_category_id=1).values_list('business_type_id', flat=True))

                        if business_type_id in credit_business_type_ids:
                            if temp_wallet_amount >= 0:
                                temp_wallet_amount = temp_wallet_amount - total_cost_per_session
                                if temp_wallet_amount >= 0:
                                    saved_sale_group_obj.payment_status_id = 1  # Paid
                                else:
                                    saved_sale_group_obj.payment_status_id = 2  # partically paid
                            else:
                                saved_sale_group_obj.payment_status_id = 3  # Not paid
                        saved_sale_group_obj.save()
                        sale_group_ids[session['id']] = saved_sale_group_obj.id
                        if request.data['from'] == 'portal':
                            # Adding the saved salegroup to the counter based on the employee who login to that counter
                            employee_id = Employee.objects.get(user_profile__user=request.user).id
                            if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                    collection_date=datetime.datetime.now()).exists():
                                counter_employee_trace_obj = \
                                CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                    collection_date=datetime.datetime.now())[0]
                                counter_id = counter_employee_trace_obj.counter.id
                                if CounterEmployeeTraceSaleGroupMap.objects.filter(
                                        counter_employee_trace_id=counter_employee_trace_obj.id).exists():
                                    counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                                        counter_employee_trace_id=counter_employee_trace_obj.id)
                                    counter_sale_group_obj.sale_group.add(saved_sale_group_obj.id)
                                    counter_sale_group_obj.save()
                                    print('counter sale updated')
                                else:
                                    counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap(
                                        counter_employee_trace_id=counter_employee_trace_obj.id)
                                    counter_sale_group_obj.save()
                                    counter_sale_group_obj.sale_group.add(saved_sale_group_obj.id)
                                    counter_sale_group_obj.save()
                                    print('counter sale created')
                        else:
                            employee_id = 3
                            counter_id = 23
                            online_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=1, order_category_id=1).values_list('business_type_id', flat=True))
                            if business_type_id in online_business_type_ids:
                                if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                        collection_date=datetime.datetime.now()).exists():
                                    counter_employee_trace_obj = \
                                        CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                            collection_date=datetime.datetime.now())[0]
                                else:
                                    counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=23,
                                                                                        employee_id=employee_id,
                                                                                        collection_date=datetime.datetime.now(),
                                                                                        start_date_time=datetime.datetime.now())
                                    counter_employee_trace_obj.save()
                                if CounterEmployeeTraceSaleGroupMap.objects.filter(
                                        counter_employee_trace_id=counter_employee_trace_obj.id).exists():
                                    counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                                        counter_employee_trace_id=counter_employee_trace_obj.id)
                                    counter_sale_group_obj.sale_group.add(saved_sale_group_obj.id)
                                    counter_sale_group_obj.save()
                                    print('counter sale updated')
                                else:
                                    counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap(
                                        counter_employee_trace_id=counter_employee_trace_obj.id)
                                    counter_sale_group_obj.save()
                                    counter_sale_group_obj.sale_group.add(saved_sale_group_obj.id)
                                    counter_sale_group_obj.save()
                                    print('counter sale created')
                        if product_form_details[date]['total_price_per_session'][
                            str(session['id'])] == total_cost_per_session:
                            print('session price is equal')
                        else:
                            print('session price not equal')
                    if super_sale_group_obj is not None:
                        super_sale_group_obj.mor_sale_group_id = sale_group_ids[1]
                        super_sale_group_obj.eve_sale_group_id = sale_group_ids[2]
                        super_sale_group_obj.save()
            sale_df = None
            sale_group_transaction_trace = None
            if is_order_placed:
                if SaleGroup.objects.filter(business_id=business_id, date=date).exists():
                    sale_group_ids = list(
                        SaleGroup.objects.filter(business_id=business_id, date=date).values_list('id', flat=True))
                    sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids, product__is_active=True)
                    sale_list = list(sale_obj.values_list('id', 'sale_group', 'sale_group__business_id',
                                                        'sale_group__date', 'sale_group__session',
                                                        'sale_group__session__display_name', 'sale_group__ordered_via',
                                                        'sale_group__ordered_via__name',
                                                        'sale_group__payment_status__name',
                                                        'sale_group__sale_status__name', 'sale_group__total_cost',
                                                        'product',
                                                        'product__name', 'count', 'cost'))
                    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'date', 'session_id', 'session_name',
                                'ordered_via_id', 'ordered_via_name', 'payment_status',
                                'sale_status',
                                'session_wise_price', 'product_id', 'product_name', 'quantity', 'product_cost']
                    sale_df = pd.DataFrame(sale_list, columns=sale_column)
                if not super_sale_group_obj is None:
                    sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=date,
                                                                            super_sale_group_id=super_sale_group_obj.id,
                                                                            sale_group_order_type_id=1,  # new Order
                                                                            counter_amount=request.data['final_price'],
                                                                            counter_id=counter_id)
                    if not sale_df is None:
                        sale_group_transaction_trace.order_sale_group_json = sale_df.to_dict('r')
                    sale_group_transaction_trace.save()
        if request.data['final_customer_wallet'] is not None:
            if request.data['final_customer_wallet'] < agent_wallet_obj.current_balance:
                transaction_obj = TransactionLog(
                    date=datetime.datetime.now(),
                    transacted_by_id=agent_user_id,
                    transacted_via_id=via_id,
                    data_entered_by=request.user,
                    amount=agent_wallet_obj.current_balance - Decimal(request.data['final_customer_wallet']),
                    transaction_direction_id=2,  # from agent wallet to aavin
                    transaction_mode_id=1,  # Upi
                    transaction_status_id=2,  # completed
                    transaction_id='1234',
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=datetime.datetime.now(),
                    wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=request.data['final_customer_wallet'],
                    description='Amount for ordering the product from agent wallet',
                    modified_by=request.user
                )
                transaction_obj.save()
                agent_wallet_obj.current_balance = request.data['final_customer_wallet']
                agent_wallet_obj.save()
                if not sale_group_transaction_trace is None:
                    sale_group_transaction_trace.is_wallet_used = True
                    sale_group_transaction_trace.wallet_amount = transaction_obj.amount
                    sale_group_transaction_trace.wallet_transaction_id = transaction_obj.id
                    sale_group_transaction_trace.save()
        online_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=1, order_category_id=1).values_list('business_type_id', flat=True))

        if business_type_id in online_business_type_ids:
            if request.data['final_price'] != 0:
                transaction_obj = TransactionLog(
                    date=datetime.datetime.now(),
                    transacted_by_id=agent_user_id,
                    transacted_via_id=via_id,
                    data_entered_by=request.user,
                    amount=request.data['final_price'],
                    transaction_direction_id=1,  # from agent to aavin
                    transaction_mode_id=1,  # Upi
                    transaction_id='1234',
                    transaction_status_id=2,  # completed
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=datetime.datetime.now(),
                    wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                    description='Amount for ordering the product',
                    modified_by=request.user
                )
                transaction_obj.save()
                if not sale_group_transaction_trace is None:
                    sale_group_transaction_trace.counter_transaction_id = transaction_obj.id
                    sale_group_transaction_trace.save()
        if is_order_placed:
            try:
                sale_group_obj = SaleGroup.objects.filter(business_id=business_id, date=date)
                sale_group_ids = list(sale_group_obj.values_list('id', flat=True))
                sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids, product__is_active=True)
                sale_list = list(sale_obj.values_list('id', 'sale_group__session',
                                                    'product__short_name', 'count', ))
                sale_column = ['sale_id', 'session_name', 'product_name', 'quantity', ]
                sale_df = pd.DataFrame(sale_list, columns=sale_column)
                product_message = ''
                product_list = sale_df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
                for product in product_list:
                    temp_dict = product_list[product]
                    morning_order = 0
                    eve_order = 0
                    for order in temp_dict:
                        if order['session_name'] == 1:
                            morning_order = order['quantity']
                        elif order['session_name'] == 2:
                            eve_order = order['quantity']
                    product_message = product_message + product + ':' + str(int(morning_order)) + '+' + str(
                        int(eve_order)) + '; '
                booth_number = Business.objects.get(id=business_id).code
                date_in_format = datetime.datetime.strptime(str(date), '%Y-%m-%d')
                date = datetime.datetime.strftime(date_in_format, '%d-%m-%y')
                if request.data['from'] == 'portal':
                    counter_name = CounterEmployeeTraceSaleGroupMap.objects.get(
                        sale_group=sale_group_ids[0]).counter_employee_trace.counter.name
                else:
                    counter_name = 'Online'

                amount = sale_group_obj.aggregate(Sum('total_cost'))['total_cost__sum']
                template_id = BsnlSmsTemplate.objects.filter(message_name='register_order').first().template_id
                template_list = [
                    {'Key': 'amount', 'Value': str(amount)},
                    {'Key': 'booth_number', 'Value': str(booth_number)},
                    # {'Key': 'counter_name', 'Value': str('-')},
                    {'Key': 'date', 'Value': str(date)},
                    # {'Key': 'product_message', 'Value': str('-')}
                    ]
                phone = Agent.objects.get(id=agent_id).agent_profile.mobile
                send_message_from_bsnl(template_id, template_list, phone)
                # message = 'Booth#{}. for {}. @{}. Rs. {}. {}'.format(booth_number, date, counter_name, amount, product_message)
                # purpose = 'New Order Confirmation Message'
                # phone = Agent.objects.get(id=agent_id).agent_profile.mobile
                # send_message_via_netfision(purpose, phone, message)
                print('message sent')
            except Exception as e:
                print(e)
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def serve_sale_details_for_future_week(request):
    if request.data['from'] == 'portal':
        from_date = datetime.datetime.now()
        after_one_week_date = from_date + datetime.timedelta(days=6)
        from_date = from_date - datetime.timedelta(days=7)
        business_id = Business.objects.get(code=request.data['booth_code']).id
    elif request.data['from'] == 'website':
        from_date = datetime.datetime.now()
        after_one_week_date = from_date + datetime.timedelta(days=6)
        from_date = from_date - datetime.timedelta(days=7)
        business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).agent_id
    elif request.data['from'] == 'mobile':
        business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
        eve_route_expiry_time = RouteBusinessMap.objects.filter(business_id=business_id, route__session_id=2)[0].route.order_expiry_time
        if datetime.datetime.now().astimezone(indian).time() > eve_route_expiry_time:
            from_date = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            from_date = datetime.datetime.now()
        after_one_week_date = from_date + datetime.timedelta(days=6)
        agent_id = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).agent_id
    sale_obj = Sale.objects.filter(sale_group__date__lte=after_one_week_date, sale_group__date__gte=from_date,
                                   sale_group__business_id=business_id, product__is_active=True).order_by(
        '-sale_group__date')
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost', 'product', 'product__quantity',
                             'product__name', 'count', 'cost', 'sale_group__time_created', 'sale_group__time_modified',
                             'sale_group__ordered_by__first_name', 'sale_group__modified_by__first_name'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'date', 'session_id', 'session_name', 'ordered_via_id',
                   'ordered_via_name', 'payment_status', 'sale_status',
                   'session_wise_price', 'product_id', 'product_quantity', 'product_name', 'quantity', 'product_cost',
                   'time_created', 'time_modified', 'ordered_by', 'modified_by']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['date'] = sale_df['date'].astype(str)
    master_dict = defaultdict(dict)
    today = date.today()
    tomorrow = today + datetime.timedelta(days=1)
    for row_index, row in sale_df.iterrows():
        if not row['date'] in master_dict:
            master_dict[row['date']]['session'] = {}
            master_dict[row['date']]['per_date'] = 0
            master_dict[row['date']]['per_product'] = {}
            master_dict[row['date']]['total_quantity_per_date'] = 0
            master_dict[row['date']]['counter_name'] = None
            if CounterEmployeeTraceSaleGroupMap.objects.filter(
                    counter_employee_trace__collection_date=row['time_created'],
                    sale_group=row['sale_group_id']).exists():
                counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                    counter_employee_trace__collection_date=row['time_created'],
                    sale_group=row['sale_group_id'])
                master_dict[row['date']]['counter_name'] = counter_sale_group_obj.counter_employee_trace.counter.name
        if not row['session_id'] in master_dict[row['date']]['session']:
            master_dict[row['date']]['session'][row['session_id']] = {}
            master_dict[row['date']]['session'][row['session_id']]['product'] = {}
            master_dict[row['date']]['session'][row['session_id']]['order_date_and_time'] = {}
            master_dict[row['date']]['session'][row['session_id']]['order_date_and_time']['time_created'] = row[
                'time_created']
            if not row['time_created'] == row['time_modified']:
                master_dict[row['date']]['session'][row['session_id']]['order_date_and_time']['time_modified'] = row[
                    'time_modified']
            else:
                master_dict[row['date']]['session'][row['session_id']]['order_date_and_time']['time_modified'] = None
            master_dict[row['date']]['session'][row['session_id']]['order_date_and_time']['ordered_by'] = row[
                'ordered_by']
            master_dict[row['date']]['session'][row['session_id']]['order_date_and_time']['modified_by'] = row[
                'modified_by']
            if row['date'] == str(today) or row['date'] == str(tomorrow):
                master_dict[row['date']]['session'][row['session_id']]['timer_info'] = 0
        if not row['product_id'] in master_dict[row['date']]['session'][row['session_id']]['product']:
            master_dict[row['date']]['session'][row['session_id']]['product'][row['product_id']] = {}
        master_dict[row['date']]['session'][row['session_id']]['product'][row['product_id']] = row[
            'quantity']
        if not row['product_id'] in master_dict[row['date']]['per_product']:
            master_dict[row['date']]['per_product'][row['product_id']] = 0
        master_dict[row['date']]['per_product'][row['product_id']] += row['product_cost']
        master_dict[row['date']]['total_quantity_per_date'] += Decimal(row['quantity']) * row['product_quantity'] / 1000
        master_dict[row['date']]['per_date'] += row['product_cost']
    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_last_date_for_agent_order(request):
    print(request.data)
    business_id = None
    agent_waller_obj = None
    if request.data['from'] == 'portal':
        employee_obj = Employee.objects.get(user_profile__user=request.user)
        # we are checking if user has a access for the order
        business_ids = []
        if employee_obj.business_group is not None:
            business_ids = list(Business.objects.filter(business_group_id=employee_obj.business_group.id).values_list('id', flat=True))
            if not Business.objects.filter(code=request.data['business_code'], is_working_now=True, id__in=business_ids).exists():
                print('not exists')
                data = {'error_message': str(request.data['business_code']) + ' is not a valid booth code. Please Check'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        if not Business.objects.filter(code=request.data['business_code'], is_working_now=True).exists():
            print('not exists')
            data = {'error_message': str(request.data['business_code']) + ' is not a valid booth code. Please Check'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        business_id = Business.objects.get(code=request.data['business_code']).id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
        business_obj = Business.objects.get(id=business_id)
        business_type_id = Business.objects.get(code=request.data['business_code']).business_type.id
        agent_waller_obj = AgentWallet.objects.get(agent_id=agent_id)

    elif request.data['from'] == 'mobile' or request.data['from'] == 'website':
        business_id = Business.objects.get(user_profile__user=request.user).id
        business_obj = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).business
        business_type_id = business_obj.business_type_id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).agent.id
        agent_waller_obj = AgentWallet.objects.get(agent_id=agent_id)

    if SaleGroup.objects.filter(business_id=business_id).exists():
        last_date = SaleGroup.objects.filter(business_id=business_id).order_by('-date')[0].date
        print(last_date)
        next_date_from_last_date = last_date + datetime.timedelta(days=1)
        sale_group_ids = list(
            SaleGroup.objects.filter(business_id=business_id, date=last_date).values_list('id', flat=True))
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
        sale_df['date'] = sale_df['date'].astype(str)
        master_dict = defaultdict(dict)
        master_dict['product'] = {}
        master_dict['total_price_per_product'] = {}
        master_dict['total_price_per_session'] = {}
        master_dict['total_price_per_date'] = 0
        for row_index, row in sale_df.iterrows():
            if row['session_id'] not in master_dict['product']:
                master_dict['product'][row['session_id']] = {}
            if row['product_id'] not in master_dict['product'][row['session_id']]:
                master_dict['product'][row['session_id']][row['product_id']] = {
                    'quantity': row['quantity'],
                    'price': row['product_cost']
                }
            if row['product_id'] not in master_dict['total_price_per_product']:
                master_dict['total_price_per_product'][row['product_id']] = 0

            master_dict['total_price_per_product'][row['product_id']] += row['product_cost']
            if row['session_id'] not in master_dict['total_price_per_session']:
                master_dict['total_price_per_session'][row['session_id']] = 0
            master_dict['total_price_per_session'][row['session_id']] += row['product_cost']
            master_dict['total_price_per_date'] += row['product_cost']
        data_dict = {
            'is_exists': True,
            'next_date_from_last_date': next_date_from_last_date,
            'last_date_product_data': master_dict,
            'wallet_balance': agent_waller_obj.current_balance,
            'business_type_id': business_type_id
        }
        agent_details = Agent.objects.get(id=agent_id)
        online_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=1, order_category_id=1).values_list('business_type_id', flat=True))
        if business_type_id in online_business_type_ids:
            mobile_verification = agent_details.is_mobile_number_verified_by_agent
        else:
            mobile_verification = True
        data_dict['agent_name'] = agent_details.first_name
        data_dict['agent_code'] = agent_details.agent_code
        data_dict['agent_mobile'] = agent_details.agent_profile.mobile
        data_dict['booth_address'] = business_obj.address
        data_dict['booth_zone'] = business_obj.zone.name
        data_dict['booth_code'] = business_obj.code
        data_dict['user_id'] = business_obj.user_profile.user.id
        data_dict['is_mobile_verified'] = mobile_verification
        data_dict['wallet_amount'] = AgentWallet.objects.get(agent_id=agent_id).current_balance
        if RouteBusinessMap.objects.filter(business=business_obj, route__session_id=1).exists():
            data_dict['mor_route_name'] = RouteBusinessMap.objects.get(business=business_obj,
                                                                       route__session_id=1).route.name
        else:
            data_dict['mor_route_name'] = None
        if RouteBusinessMap.objects.filter(business=business_obj, route__session_id=2).exists():
            data_dict['eve_route_name'] = RouteBusinessMap.objects.get(business=business_obj,
                                                                       route__session_id=2).route.name
        else:
            data_dict['eve_route_name'] = None
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict = {
            'is_exists': False,
            'wallet_balance': agent_waller_obj.current_balance,
            'business_type_id': business_type_id

        }
        agent_details = Agent.objects.get(id=agent_id)
        online_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=1, order_category_id=1).values_list('business_type_id', flat=True))

        if business_type_id in online_business_type_ids:
            mobile_verification = agent_details.is_mobile_number_verified_by_agent
        else:
            mobile_verification = True
        data_dict['agent_name'] = agent_details.first_name
        data_dict['agent_code'] = agent_details.agent_code
        data_dict['agent_mobile'] = agent_details.agent_profile.mobile
        data_dict['booth_address'] = business_obj.address
        data_dict['booth_zone'] = business_obj.zone.name
        data_dict['booth_code'] = business_obj.code
        data_dict['user_id'] = business_obj.user_profile.user.id
        data_dict['wallet_amount'] = AgentWallet.objects.get(agent_id=agent_id).current_balance
        data_dict['is_mobile_verified'] = mobile_verification

        if RouteBusinessMap.objects.filter(business=business_obj, route__session_id=1).exists():
            data_dict['mor_route_name'] = RouteBusinessMap.objects.get(business=business_obj,
                                                                       route__session_id=1).route.name
        else:
            data_dict['mor_route_name'] = None
        if RouteBusinessMap.objects.filter(business=business_obj, route__session_id=2).exists():
            data_dict['eve_route_name'] = RouteBusinessMap.objects.get(business=business_obj,
                                                                       route__session_id=2).route.name
        else:
            data_dict['eve_route_name'] = None
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_order_exits(request):
    print(request.data)
    date = request.data['date']
    if request.data['from'] == 'portal':
        business_id = Business.objects.get(code=request.data['business_code']).id
        # date = datetime.datetime.strptime(request.data['date'], '%m/%d/%Y')
    elif request.data['from'] == 'mobile' or request.data['from'] == 'website':
        business_id = BusinessAgentMap.objects.get(business__user_profile_id=request.user.userprofile.id,
                                                   is_active=True).business_id
    if SaleGroup.objects.filter(business_id=business_id, date=date).exists():
        last_date = SaleGroup.objects.filter(business_id=business_id).order_by('-date')[0].date
        next_date_from_last_date = last_date + datetime.timedelta(days=1)
        data_dict = {
            'is_exists': True,
            'last_date': next_date_from_last_date
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict = {
            'is_exists': False,
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_sale_details_for_last_week(request):
    today_datetime = datetime.datetime.now()
    before_one_week_date = today_datetime - datetime.timedelta(days=6)
    if request.data['from'] == 'portal':
        business_id = Business.objects.get(code=request.data['booth_code']).id
    elif request.data['from'] == 'mobile':
        business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
    sale_obj = Sale.objects.filter(sale_group__date__gte=before_one_week_date, sale_group__date__lte=today_datetime,
                                   sale_group__business_id=business_id, product__is_active=True).order_by(
        '-sale_group__date')
    sale_list = list(sale_obj.values_list('id', 'sale_group', 'sale_group__business_id',
                                          'sale_group__date', 'sale_group__session',
                                          'sale_group__session__display_name', 'sale_group__ordered_via',
                                          'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                                          'sale_group__sale_status__name', 'sale_group__total_cost', 'product',
                                          'product__quantity',
                                          'product__name', 'count', 'cost'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'date', 'session_id', 'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_id', 'product_quantity', 'product_name', 'quantity', 'product_cost']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['date'] = sale_df['date'].astype(str)
    master_dict = defaultdict(dict)
    for row_index, row in sale_df.iterrows():
        if not row['date'] in master_dict:
            master_dict[row['date']]['session'] = {}
            master_dict[row['date']]['per_date'] = 0
            master_dict[row['date']]['per_product'] = {}
            master_dict[row['date']]['total_quantity_per_date'] = 0
        if not row['session_id'] in master_dict[row['date']]['session']:
            master_dict[row['date']]['session'][row['session_id']] = {}
        if not row['product_id'] in master_dict[row['date']]['session'][row['session_id']]:
            master_dict[row['date']]['session'][row['session_id']][row['product_id']] = {}
        master_dict[row['date']]['session'][row['session_id']][row['product_id']] = row[
            'quantity']
        if not row['product_id'] in master_dict[row['date']]['per_product']:
            master_dict[row['date']]['per_product'][row['product_id']] = 0
        master_dict[row['date']]['per_product'][row['product_id']] += row['product_cost']
        master_dict[row['date']]['per_date'] += row['product_cost']
        master_dict[row['date']]['total_quantity_per_date'] += Decimal(row['quantity']) * row['product_quantity'] / 1000
    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_unions(request):
    values = Union.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


def find_route_name_for_booth(business_id, session_id):
    if RouteBusinessMap.objects.filter(route__session_id=session_id, business_id=business_id).exists():
        route_name = RouteBusinessMap.objects.get(route__session_id=session_id, business_id=business_id).route.name
    else:
        route_name = 'N/A'
    return route_name


@api_view(['GET'])
def serve_booths(request):
    values = Business.objects.filter().order_by('name').values_list('id', 'name', 'address', 'code', 'zone_id',
                                                                    'zone__name', 'business_type_id',
                                                                    'business_type__name', 'name', 'constituency_id',
                                                                    'ward_id', 'address', 'is_rural', 'is_urban',
                                                                    'location_category_id', 'location_category_value',
                                                                    'landmark', 'latitude', 'longitude',
                                                                    'working_hours_from', 'working_hours_to', 'pincode')
    columns = ['id', 'name', 'address', 'code', 'zone_id', 'zone', 'business_type_id', 'business_type', 'name',
               'constituency_id', 'ward_id', 'address', 'is_rural', 'is_urban', 'location_category_id',
               'location_category_value', 'landmark', 'latitude', 'longitude', 'working_hours_from', 'working_hours_to',
               'pincode']
    df = pd.DataFrame(list(values), columns=columns)
    df['mor_route'] = df.apply(lambda x: find_route_name_for_booth(x['id'], 1), axis=1)
    df['eve_route'] = df.apply(lambda x: find_route_name_for_booth(x['id'], 2), axis=1)
    data = df.to_dict('r')
    print('booth data loaded')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_location_categories(request):
    values = LocationCategory.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_booth(request):
    print(request.data)
    if request.data['id'] is None:
        business_obj = Business(
            code=request.data['code'],
            zone_id=request.data['zone_id'],
            business_type_id=request.data['business_type_id'],
            constituency_id=request.data['constituency_id'],
            ward_id=request.data['ward_id'],
            address=request.data['address'],
            location_category_id=request.data['location_category_id'],
            location_category_value=request.data['location_category_value'],

            pincode=request.data['pincode'],
            working_hours_from=request.data['working_hours_from'],
            working_hours_to=request.data['working_hours_to']
        )

        if request.data['landmark'] == None:
            business_obj.landmark = ' '
        else:
            business_obj.landmark = request.data['landmark']
        if request.data['is_rural']:
            business_obj.is_rural = True
            business_obj.is_urban = False
        else:
            business_obj.is_rural = False
            business_obj.is_urban = True

        if request.data['name'] != None:
            business_obj.name = request.data['name']
        business_obj.save()
        # updating the last count in business code bank
        BusinessCodeBank.objects.filter(business_type_id=request.data['business_type_id']).update(
            last_code=request.data['code'])
        # for trace table and product business wise discount table
        if 'product_price' in request.data:
            product_ids = request.data['product_price'].keys()
            if len(product_ids) > 0:
                for product_id in product_ids:
                    # save_business_wise_product_discount(business_obj.id, product_id,
                    #                                     request.data['product_price'][product_id], request.user.id)
                    print('saved product discounts')
        data = {'message': 'Booth registered successfully'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        business_obj = Business.objects.get(id=request.data['id'])
        Business.objects.filter(id=request.data['id']).update(
            code=request.data['code'],
            zone_id=request.data['zone_id'],
            business_type_id=request.data['business_type_id'],
            constituency_id=request.data['constituency_id'],
            ward_id=request.data['ward_id'],
            address=request.data['address'],
            location_category_id=request.data['location_category_id'],
            location_category_value=request.data['location_category_value'],
            landmark=request.data['landmark'],
            working_hours_from=request.data['working_hours_from'],
            working_hours_to=request.data['working_hours_to']
        )
        # business_obj = Business.objects.filter(id=request.data['id'])
        if request.data['is_rural']:
            business_obj.is_rural = True
            business_obj.is_urban = False
        else:
            business_obj.is_rural = False
            business_obj.is_urban = True
        business_obj.save()
        if request.data['name'] != None:
            Business.objects.filter(id=request.data['id']).update(
                name=request.data['name']
            )
        if 'product_price' in request.data:
            product_ids = request.data['product_price'].keys()
            if len(product_ids) > 0:
                for product_id in product_ids:
                    # save_business_wise_product_discount(business_obj.id, product_id,
                    #                                     request.data['product_price'][product_id], request.user.id)
                    print('saved product discounts')
        data = {'message': 'Booth updated successfully'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_genders(request):
    values = Gender.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_taluks(request):
    values = Taluk.objects.filter().order_by('name').values_list('id', 'name', 'district', 'district__name')
    columns = ['id', 'name', 'district_id', 'district_name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_states(request):
    values = State.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_relation_types(request):
    values = RelationType.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_vehicle_transports(request):
    values = VehicleTransport.objects.filter().order_by('name').values_list('id', 'name', 'contact_person', 'mobile',
                                                                            'alternate_mobile', 'address', 'latitude',
                                                                            'longitude')
    columns = ['id', 'name', 'contact_person', 'mobile', 'alternate_mobile', 'address', 'latitude', 'longitude']
    df = pd.DataFrame(list(values), columns=columns)
    if not df.empty:
        data = df.to_dict('r')
    else:
        data = []
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_vehicle_transport(request):
    print(request.data)
    if request.data['id'] is None:
        if VehicleTransport.objects.filter(name__iexact=request.data['name'],
                                           contact_person__iexact=request.data['contact_person'],
                                           mobile=request.data['mobile']).exists():
            data = {'message': 'Vehicle transport already registered!'}
        else:
            vehicle_obj = VehicleTransport(
                name=request.data['name'],
                contact_person=request.data['contact_person'],
                mobile=request.data['mobile'],
                alternate_mobile=request.data['alternate_mobile'],
                address=request.data['address'],
                latitude=request.data['latitude'],
                longitude=request.data['longitude']
            )
            if request.data['alternate_mobile'] != None:
                vehicle_obj.alternate_mobile = request.data['alternate_mobile']
            vehicle_obj.save()
            data = {'message': 'Vehicle transport registered successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        VehicleTransport.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
            contact_person=request.data['contact_person'],
            mobile=request.data['mobile'],
            alternate_mobile=request.data['alternate_mobile'],
            address=request.data['address'],
            latitude=request.data['latitude'],
            longitude=request.data['longitude']
        )
        if request.data['alternate_mobile'] != None:
            VehicleTransport.objects.filter(id=request.data['id']).update(
                alternate_mobile=request.data['alternate_mobile']
            )
        data = {'message': 'Vehicle transport updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_vehicle_type(request):
    if request.data['id'] is None:
        if VehicleType.objects.filter(name__iexact=request.data['name']).exists():
            data = {'message': 'Vehicle type alrady exists'}
        else:
            VehicleType.objects.create(
                name=request.data['name']
            )
            data = {'message': 'Vehicle type registered successfully'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        VehicleType.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
        )
        data = {'message': 'Vehicle type updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_commission_product_display_columns(request):
    product_names = list(Product.objects.filter(is_active=True).values_list('name', flat=True))
    return Response(data=product_names, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_commission_business_product_percentage(request):
    product_names = list(Product.objects.filter(is_active=True).values_list('name', flat=True))
    return Response(data=product_names, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_sale_for_selected_date(request):
    if request.data['from'] == 'portal':
        business_id = Business.objects.get(code=request.data['business_code']).id
        business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
        agent_id = business_agent_obj.agent_id
    elif request.data['from'] == 'mobile' or request.data['from'] == 'website':
        business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
        business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
    sale_obj = Sale.objects.filter(sale_group__date=request.data['selected_date'], sale_group__business_id=business_id,
                                   product__is_active=True)
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
    master_dict = defaultdict(dict)
    master_dict['session'] = {}
    master_dict['total_price_per_date'] = 0
    master_dict['total_price_per_product'] = {}
    master_dict['total_price_per_session'] = {}
    for row_index, row in sale_df.iterrows():
        if not row['session_id'] in master_dict['session']:
            master_dict['session'][row['session_id']] = {}
            master_dict['session'][row['session_id']]['product'] = {}
            master_dict['session'][row['session_id']]['sale_group_id'] = row['sale_group_id']
        if not row['product_id'] in master_dict['session'][row['session_id']]['product']:
            master_dict['session'][row['session_id']]['product'][row['product_id']] = {
                'quantity': row['quantity'],
                'price': row['product_cost'],
                'sale_id': row['sale_id'],
            }
        if not row['product_id'] in master_dict['total_price_per_product']:
            master_dict['total_price_per_product'][row['product_id']] = 0
        if not row['session_id'] in master_dict['total_price_per_session']:
            master_dict['total_price_per_session'][row['session_id']] = 0
        master_dict['total_price_per_session'][row['session_id']] += row['product_cost']
        master_dict['total_price_per_product'][row['product_id']] += row['product_cost']
        master_dict['total_price_per_date'] += row['product_cost']
    agent_waller_obj = AgentWallet.objects.get(agent_id=business_agent_obj.agent.id)
    data_dict = {
        'order_details': master_dict,
        'current_wallet_amount': agent_waller_obj.current_balance,
    }
    data_dict['business_details'] = {
        'business_code': business_agent_obj.business.code,
        'agent_first_name': business_agent_obj.agent.first_name,
        'agent_last_name': business_agent_obj.agent.last_name
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
def update_selected_sale_group(request):
    sid = transaction.savepoint()
    try:
        if request.data['from'] == 'portal':
            business_id = Business.objects.get(code=request.data['business_code']).id
            business_type_id = Business.objects.get(code=request.data['business_code']).business_type.id
            user_profile_id = Business.objects.get(code=request.data['business_code']).user_profile_id
            agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
            agent_user_id = Business.objects.get(code=request.data['business_code']).user_profile.user.id
            via_id = 2
        elif request.data['from'] == 'mobile':
            user_profile_id = request.user.userprofile.id
            business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
            agent_user_id = request.user.id
            agent_id = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).agent.id
            business_type_id = Business.objects.get(user_profile_id=request.user.userprofile.id).business_type.id
            via_id = 1
        elif request.data['from'] == 'website':
            user_profile_id = request.user.userprofile.id
            business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
            agent_user_id = request.user.id
            agent_id = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).agent.id
            business_type_id = Business.objects.get(user_profile_id=request.user.userprofile.id).business_type.id
            via_id = 3
        business_obj = Business.objects.get(id=business_id)
        data_dict = serve_product_and_session_list(user_profile_id)
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        product_quantity_variation_list = data_dict['product_quantity_variation_list']
        product_form_details = request.data['product_form_details']
        selected_date = request.data['selected_date']
        counter_id = None
        agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
        sale_group_ids = {
            1: None,
            2: None
        }
        if SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=selected_date).exists():
            super_sale_group_obj = SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=selected_date)[0]
        else:
            super_sale_group_obj = None
        for session in session_list:
            total_cost_per_session = 0
            route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                    route__session_id=session['id']).route_id
            vehicle_obj = RouteVehicleMap.objects.get(route_id=route_id).vehicle
            if product_form_details['total_price_per_session'][str(session['id'])] != 0:
                if product_form_details['session'][str(session['id'])]['sale_group_id'] is not None:
                    sale_group_obj = SaleGroup.objects.get(
                        id=product_form_details['session'][str(session['id'])]['sale_group_id'])
                else:
                    sale_group_obj = SaleGroup(
                        business_id=business_id,
                        business_type_id=business_type_id,
                        date=selected_date,
                        session_id=session['id'],
                        ordered_via_id=via_id,  # via mobile
                        payment_status_id=1,  # paid
                        sale_status_id=1,  # ordered
                        total_cost=0,
                        ordered_by=request.user,
                        modified_by=request.user,
                        product_amount=0,
                        route_id=route_id,
                        zone_id=business_obj.zone_id
                    )
                    sale_group_obj.save()
                sale_group_ids[session['id']] = sale_group_obj.id
                for product in product_list:
                    product_quantity = \
                    product_form_details['session'][str(session['id'])]['product'][str(product['product_id'])][
                        'quantity']
                    if product_quantity != 0 and product_quantity is not None:
                        if product['product_group_id'] == 3:
                            for variation_price in product_quantity_variation_list[product['product_id']]:
                                if product_quantity >= variation_price['min_quantity'] and product_quantity <= \
                                        variation_price['max_quantity']:
                                    product_cost = product_quantity * variation_price['mrp']
                        else:
                            product_cost = product_quantity * product['product_mrp']
                        if product_form_details['session'][str(session['id'])]['product'][str(product['product_id'])][
                            'sale_id'] is not None:
                            sale_id = \
                            product_form_details['session'][str(session['id'])]['product'][str(product['product_id'])][
                                'sale_id']
                            if Sale.objects.filter(id=sale_id).exists():
                                sale_obj = Sale.objects.get(id=sale_id)
                                # Check route trace exists and update the quatitu that agent changed
                                if RouteTrace.objects.filter(date=selected_date, session_id=session['id'],
                                                            route_id=route_id).exists():
                                    route_trace_obj = RouteTrace.objects.get(date=selected_date, session_id=session['id'],
                                                                            route_id=route_id)
                                    if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id,
                                                                                product_id=product['product_id']).exists():
                                        route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(
                                            route_trace_id=route_trace_obj.id, product_id=product['product_id'])
                                        route_trace_sale_summary_obj.quantity -= Decimal(sale_obj.count)
                                        route_trace_sale_summary_obj.save()
                                        route_trace_sale_summary_obj.quantity += product_quantity
                                        route_trace_sale_summary_obj.save()
                                sale_obj.count = product_quantity
                                sale_obj.cost = product_cost
                                sale_obj.modified_by = request.user
                                sale_obj.save()

                                # update free product and remove 
                                if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                    if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                        free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                        eligible_product_count = free_product_property_obj.eligible_product_count
                                        defalut_free_product_count = free_product_property_obj.product_count
                                        if product_quantity >= eligible_product_count:
                                            box_count = math.floor(product_quantity/eligible_product_count)
                                            free_product_count = box_count*defalut_free_product_count
                                            if Sale.objects.filter(sale_group_id=sale_group_obj.id, product_id=free_product_property_obj.free_product.id).exists():
                                                free_product_sale_obj = Sale.objects.get(sale_group_id=sale_group_obj.id, product_id=free_product_property_obj.free_product.id)
                                                free_product_sale_obj.count = free_product_count
                                                free_product_sale_obj.modified_by = request.user
                                                free_product_sale_obj.save()
                                            else:
                                                sale_obj = Sale(
                                                    sale_group_id=sale_group_obj.id,
                                                    product_id=free_product_property_obj.free_product.id,
                                                    count=free_product_count,
                                                    cost=0,
                                                    ordered_by_id=1,
                                                    modified_by_id=1
                                                )
                                                sale_obj.save()
                                        else:
                                            if Sale.objects.filter(sale_group_id=sale_group_obj.id, product_id=free_product_property_obj.free_product.id).exists():
                                                Sale.objects.filter(sale_group_id=sale_group_obj.id, product_id=free_product_property_obj.free_product.id).delete()
                            # print('old sale edited')
                        else:
                            sale_obj = Sale(
                                sale_group_id=sale_group_obj.id,
                                product_id=product['product_id'],
                                count=product_quantity,
                                cost=product_cost,
                                ordered_by=request.user,
                                modified_by=request.user
                            )
                            sale_obj.save()
                            if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                    free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                    eligible_product_count = free_product_property_obj.eligible_product_count
                                    defalut_free_product_count = free_product_property_obj.product_count
                                    if product_quantity >= eligible_product_count:
                                        box_count = math.floor(product_quantity/eligible_product_count)
                                        free_product_count = box_count*defalut_free_product_count
                                        sale_obj = Sale(
                                            sale_group_id=sale_group_obj.id,
                                            product_id=free_product_property_obj.free_product.id,
                                            count=free_product_count,
                                            cost=0,
                                            ordered_by_id=1,
                                            modified_by_id=1
                                        )
                                        sale_obj.save()
                            # check route trace and update quatitu if route trace not exists create new route trace ana update the quantity
                            if RouteTrace.objects.filter(date=selected_date, session_id=session['id'],
                                                        route_id=route_id).exists():
                                route_trace_obj = RouteTrace.objects.get(date=selected_date, session_id=session['id'],
                                                                        route_id=route_id)
                                if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id,
                                                                            product_id=product['product_id']).exists():
                                    route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(
                                        route_trace_id=route_trace_obj.id, product_id=product['product_id'])
                                    route_trace_sale_summary_obj.quantity += product_quantity
                                    route_trace_sale_summary_obj.save()
                                else:
                                    route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(
                                        route_trace_id=route_trace_obj.id, product_id=product['product_id'],
                                        quantity=product_quantity)
                                    route_trace_sale_summary_obj.save()
                            else:
                                route_trace_obj = RouteTrace(indent_status_id=1,  # initiated
                                                            route_id=route_id,
                                                            vehicle_id=vehicle_obj.id,
                                                            date=selected_date,
                                                            session_id=session['id'],
                                                            driver_name=vehicle_obj.driver_name,
                                                            driver_phone=vehicle_obj.driver_mobile)
                                route_trace_obj.save()
                                route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id,
                                                                                        product_id=product['product_id'],
                                                                                        quantity=product_quantity)
                                route_trace_sale_summary_obj.save()
                            # need to discuss with sir about If agent edit and create en route need to check the customers orders.
                        total_cost_per_session += product_cost
                    else:
                        if product_form_details['session'][str(session['id'])]['product'][str(product['product_id'])][
                            'sale_id'] is not None:
                            sale_id = \
                            product_form_details['session'][str(session['id'])]['product'][str(product['product_id'])][
                                'sale_id']
                            sale_obj = Sale.objects.get(id=sale_id)
                            # product removed during agent edit then we need to reduce the quatity in route trace
                            if RouteTrace.objects.filter(date=selected_date, session_id=session['id'],
                                                        route_id=route_id).exists():
                                route_trace_obj = RouteTrace.objects.get(date=selected_date, session_id=session['id'],
                                                                        route_id=route_id)
                                if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id, product_id=product['product_id']).exists():
                                    route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(
                                        route_trace_id=route_trace_obj.id, product_id=product['product_id'])
                                    route_trace_sale_summary_obj.quantity -= Decimal(sale_obj.count)
                                    route_trace_sale_summary_obj.save()
                            if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                    free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                    if Sale.objects.filter(sale_group_id=sale_group_obj.id, product_id=free_product_property_obj.free_product.id).exists():
                                        Sale.objects.filter(sale_group_id=sale_group_obj.id, product_id=free_product_property_obj.free_product.id).delete()


                            # sale_obj.cost = 0
                            # sale_obj.count = 0
                            # sale_obj.modified_by = request.user
                            # sale_obj.save()
                            sale_obj.delete()
                            # print('Sale price is 0')
                if request.data['from'] == 'portal':
                    # Adding the saved salegroup to the counter based on the employee who login to that counter
                    employee_id = Employee.objects.get(user_profile__user=request.user).id
                    if session['id'] == 1:
                        oppsite_session_id = 2
                    else:
                        oppsite_session_id = 1
                    if SaleGroup.objects.filter(date=selected_date, session_id=oppsite_session_id,
                                                business_id=business_id).exists():
                        opposite_sale_group_obj = SaleGroup.objects.get(date=selected_date, session_id=oppsite_session_id,
                                                                        business_id=business_id)
                        if CounterEmployeeTraceSaleGroupMap.objects.filter(
                                counter_employee_trace__collection_date=opposite_sale_group_obj.time_created,
                                sale_group=opposite_sale_group_obj).exists():
                            counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                                counter_employee_trace__collection_date=opposite_sale_group_obj.time_created,
                                sale_group=opposite_sale_group_obj)
                            counter_id = counter_sale_group_obj.counter_employee_trace.counter_id
                            counter_sale_group_obj.sale_group.add(sale_group_obj)
                            counter_sale_group_obj.save()
                else:
                    counter_id = 23
                sale_group_obj.total_cost = total_cost_per_session
                sale_group_obj.product_amount = total_cost_per_session
                sale_group_obj.modified_by = request.user
                sale_group_obj.save()
                if product_form_details['total_price_per_session'][str(session['id'])] == total_cost_per_session:
                    print('session price is equal')
                else:
                    print('session price not equal')
            else:
                if product_form_details['session'][str(session['id'])]['sale_group_id'] is not None:
                    if product_form_details['total_price_per_session'][str(session['id'])] == 0:
                        SaleGroup.objects.get(
                            id=product_form_details['session'][str(session['id'])]['sale_group_id']).delete()

        if super_sale_group_obj is not None:
            super_sale_group_obj.mor_sale_group_id = sale_group_ids[1]
            super_sale_group_obj.eve_sale_group_id = sale_group_ids[2]
            super_sale_group_obj.save()
            sale_df = None
            # if SaleGroup.objects.filter(business_id=business_id, date=selected_date).exists():
            sale_group_ids = list(
                SaleGroup.objects.filter(business_id=business_id, date=selected_date).values_list('id', flat=True))
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
            sale_group_transaction_trace = None
            if request.data['final_price'] != 0 or request.data[
                'final_customer_wallet'] < agent_wallet_obj.current_balance:
                sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=selected_date,
                                                                        super_sale_group_id=super_sale_group_obj.id,
                                                                        sale_group_order_type_id=2,  # order increase
                                                                        counter_amount=request.data['final_price'],
                                                                        counter_id=counter_id)
                if not sale_df is None:
                    sale_group_transaction_trace.order_sale_group_json = sale_df.to_dict('r')
                sale_group_transaction_trace.save()
            elif request.data['final_customer_wallet'] > agent_wallet_obj.current_balance:
                sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=selected_date,
                                                                        super_sale_group_id=super_sale_group_obj.id,
                                                                        sale_group_order_type_id=3,  # Order decrease
                                                                        counter_id=counter_id,
                                                                        )
                if via_id == 2:
                    sale_group_transaction_trace.counter_amount = -(
                                Decimal(request.data['final_customer_wallet']) - agent_wallet_obj.current_balance)

                if not sale_df is None:
                    sale_group_transaction_trace.order_sale_group_json = sale_df.to_dict('r')
                sale_group_transaction_trace.save()

        if request.data['final_price'] != 0:
            transaction_obj = TransactionLog(
                date=datetime.datetime.now(),
                transacted_by_id=agent_user_id,
                transacted_via_id=via_id,
                data_entered_by=request.user,
                amount=request.data['final_price'],
                transaction_direction_id=1,  # from agent to aavin
                transaction_mode_id=1,  # Upi
                transaction_id='1234',
                transaction_status_id=2,  # completed
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                description='Amount for ordering the product',
                modified_by=request.user
            )
            transaction_obj.save()
            sale_group_transaction_trace.counter_transaction_id = transaction_obj.id
            sale_group_transaction_trace.save()
        if not request.data['from'] == 'portal':
            online_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=1, order_category_id=1).values_list('business_type_id', flat=True))
            if business_type_id  in online_business_type_ids:
                # balance amount lesser than the available amount
                if request.data['final_customer_wallet'] < agent_wallet_obj.current_balance:
                    transaction_obj = TransactionLog(
                        date=datetime.datetime.now(),
                        transacted_by_id=agent_user_id,
                        transacted_via_id=via_id,
                        data_entered_by=request.user,
                        amount=agent_wallet_obj.current_balance - Decimal(request.data['final_customer_wallet']),
                        transaction_direction_id=2,  # from agent wallet to aavin
                        transaction_mode_id=1,  # Upi
                        transaction_status_id=2,  # completed
                        transaction_id='1234',
                        transaction_approval_status_id=1,  # Accepted
                        transaction_approved_by_id=1,
                        transaction_approved_time=datetime.datetime.now(),
                        wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                        wallet_balance_after_transaction_approval=request.data['final_customer_wallet'],
                        description='Amount for ordering the product from agent wallet',
                        modified_by=request.user
                    )
                    transaction_obj.save()
                    agent_wallet_obj.current_balance = request.data['final_customer_wallet']
                    agent_wallet_obj.save()
                    if sale_group_transaction_trace is not None:
                        sale_group_transaction_trace.is_wallet_used = True
                        sale_group_transaction_trace.wallet_amount = transaction_obj.amount
                        sale_group_transaction_trace.wallet_transaction_id = transaction_obj.id
                        sale_group_transaction_trace.save()
                # balance amout greated than the available amount that means refund to wallet
                elif request.data['final_customer_wallet'] > agent_wallet_obj.current_balance:
                    transaction_obj = TransactionLog(
                        date=datetime.datetime.now(),
                        transacted_by_id=agent_user_id,
                        transacted_via_id=via_id,
                        data_entered_by=request.user,
                        amount=Decimal(request.data['final_customer_wallet']) - agent_wallet_obj.current_balance,
                        transaction_direction_id=3,  # from  aavin to agent wallet
                        transaction_mode_id=1,  # Upi
                        transaction_status_id=2,  # completed
                        transaction_id='1234',
                        transaction_approval_status_id=1,  # Accepted
                        transaction_approved_by_id=1,
                        transaction_approved_time=datetime.datetime.now(),
                        wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                        wallet_balance_after_transaction_approval=request.data['final_customer_wallet'],
                        description='Amount for refunding amount from aavin to agent wallet',
                        modified_by=request.user
                    )
                    transaction_obj.save()
                    agent_wallet_obj.current_balance = request.data['final_customer_wallet']
                    agent_wallet_obj.save()
                    if sale_group_transaction_trace is not None:
                        sale_group_transaction_trace.is_wallet_used = True
                        sale_group_transaction_trace.wallet_amount = -transaction_obj.amount
                        sale_group_transaction_trace.wallet_transaction_id = transaction_obj.id
                        sale_group_transaction_trace.save()
        try:
            sale_group_obj = SaleGroup.objects.filter(business_id=business_id, date=selected_date)
            sale_group_ids = list(sale_group_obj.values_list('id', flat=True))
            sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids, product__is_active=True)
            sale_list = list(sale_obj.values_list('id', 'sale_group__session',
                                                'product__short_name', 'count', ))
            sale_column = ['sale_id', 'session_name', 'product_name', 'quantity', ]
            sale_df = pd.DataFrame(sale_list, columns=sale_column)
            product_message = ''
            product_list = sale_df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
            for product in product_list:
                temp_dict = product_list[product]
                morning_order = 0
                eve_order = 0
                for order in temp_dict:
                    if order['session_name'] == 1:
                        morning_order = order['quantity']
                    elif order['session_name'] == 2:
                        eve_order = order['quantity']
                product_message = product_message + product + ':' + str(int(morning_order)) + '+' + str(
                    int(eve_order)) + '; '
            booth_number = Business.objects.get(id=business_id).code
            date_in_format = datetime.datetime.strptime(str(selected_date), '%Y-%m-%d')
            date = datetime.datetime.strftime(date_in_format, '%d-%m-%y')
            if request.data['from'] == 'portal':
                counter_name = CounterEmployeeTraceSaleGroupMap.objects.get(
                    sale_group=sale_group_ids[0]).counter_employee_trace.counter.name
            else:
                counter_name = 'Online'
            amount = sale_group_obj.aggregate(Sum('total_cost'))['total_cost__sum']
            message = 'Booth#{}. for {}. @{}. Rs. {}. {} Edited'.format(booth_number, date, counter_name, amount, product_message)
            purpose = 'Edit Order Confirmation Message'
            phone = Agent.objects.get(id=agent_id).agent_profile.mobile
            send_message_via_netfision(purpose, phone, message)
        except Exception as e:
            print(e)
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def serve_agent_wallet(request):
    business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=request.user)
    agent_wallet_obj = AgentWallet.objects.get(agent_id=business_agent_obj.agent.id)
    data_dict = {
        'wallet_balance': agent_wallet_obj.current_balance
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_last_week_transaction_log_and_wallet_balance(request):
    print('transaction log')
    print(request.data)
    if request.data['from'] == 'portal':
        user_id = BusinessAgentMap.objects.get(agent_id=request.data['agent_id']).business.user_profile.user.id
    if request.data['from'] == 'mobile':
        user_id = request.user.id
    today_datetime = datetime.datetime.now()
    before_one_month_date = today_datetime - datetime.timedelta(days=30)
    transaction_log_obj = TransactionLog.objects.filter(transacted_by=user_id, date__gte=before_one_month_date,
                                                        date__lte=today_datetime).order_by('-id')
    transaction_log_list = list(
        transaction_log_obj.values_list('id', 'date', 'transacted_by', 'transaction_status', 'transaction_status__name',
                                        'amount', 'transaction_direction', 'transaction_direction__description',
                                        'transaction_mode', 'transaction_mode__name', 'transaction_id',
                                        'wallet_balance_before_this_transaction',
                                        'wallet_balance_after_transaction_approval', 'description', 'time_created',
                                        'transaction_status', 'transaction_status__name', 'transaction_approval_status',
                                        'transaction_approval_status__name', 'transaction_approved_by',
                                        'transaction_approved_time'))
    transaction_log_column = ['id', 'date', 'transacted_by', 'transaction_status_id', 'transaction_status_name',
                              'amount', 'transaction_direction_id', 'transaction_direction_description',
                              'transaction_mode', 'transaction_mode_name', 'transaction_id', 'wallet_balance_before',
                              'wallet_balance_after', 'description', 'time_created', 'transaction_status_id',
                              'transaction_status_name', 'transaction_approval_status_id',
                              'transaction_approval_status_name', 'transaction_approved_by',
                              'transaction_approved_time']
    transaction_log_df = pd.DataFrame(transaction_log_list, columns=transaction_log_column)
    # transaction_log_df['date'] = transaction_log_df['date'].astype(str)
    transaction_log_list = transaction_log_df.to_dict('r')
    business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user_id=user_id)
    agent_wallet_obj = AgentWallet.objects.get(agent_id=business_agent_obj.agent.id)
    data_dict = {
        'wallet_balance': agent_wallet_obj.current_balance,
        'transaction_log': transaction_log_list
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_last_week_transaction_log_and_wallet_balance_for_customer(request):
    print('transaction log')
    user_id = request.user.id
    today_datetime = datetime.datetime.now()
    before_one_month_date = today_datetime - datetime.timedelta(days=30)
    transaction_log_obj = TransactionLog.objects.filter(transacted_by=user_id, date__gte=before_one_month_date,
                                                        date__lte=today_datetime).order_by('-id')
    transaction_log_list = list(
        transaction_log_obj.values_list('id', 'date', 'transacted_by', 'transaction_status', 'transaction_status__name',
                                        'amount', 'transaction_direction', 'transaction_direction__description',
                                        'transaction_mode', 'transaction_mode__name', 'transaction_id',
                                        'wallet_balance_before_this_transaction',
                                        'wallet_balance_after_transaction_approval', 'description', 'time_created',
                                        'transaction_status', 'transaction_status__name', 'transaction_approval_status',
                                        'transaction_approval_status__name', 'transaction_approved_by',
                                        'transaction_approved_time'))
    transaction_log_column = ['id', 'date', 'transacted_by', 'transaction_status_id', 'transaction_status_name',
                              'amount', 'transaction_direction_id', 'transaction_direction_description',
                              'transaction_mode', 'transaction_mode_name', 'transaction_id', 'wallet_balance_before',
                              'wallet_balance_after', 'description', 'time_created', 'transaction_status_id',
                              'transaction_status_name', 'transaction_approval_status_id',
                              'transaction_approval_status_name', 'transaction_approved_by',
                              'transaction_approved_time']
    transaction_log_df = pd.DataFrame(transaction_log_list, columns=transaction_log_column)
    # transaction_log_df['date'] = transaction_log_df['date'].astype(str)
    transaction_log_list = transaction_log_df.to_dict('r')
    customer_wallet_obj = ICustomerWallet.objects.get(customer__user_profile__user_id=request.user.id)
    data_dict = {
        'wallet_balance': customer_wallet_obj.current_balance,
        'transaction_log': transaction_log_list
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_advertisement(request):
    advertisement_obj = Advertisement.objects.filter(expires_on__gte=datetime.datetime.now())

    advertisement_list = list(advertisement_obj.values_list(
        'id', 'advertisement_image', 'link', 'publish_from', 'expires_on', 'is_active', 'time_created'))

    advertisement_column = ['id', 'advertisement_image', 'link', 'publish_from', 'expires_on', 'is_active',
                            'time_created']

    advertisement_df = pd.DataFrame(advertisement_list, columns=advertisement_column)

    for index, row in advertisement_df.iterrows():
        try:
            image_path = 'static/media/' + row['advertisement_image']
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                advertisement_df.at[index, 'advertisement_image'] = encoded_image
        except Exception as err:
            print(err)

    return Response(advertisement_df.to_dict('r'))


@api_view(['GET'])
def serve_business_types_for_commission(request):
    business_type_wise_ids = [1, 2, 3]
    values = BusinessType.objects.filter(id__in=business_type_wise_ids).order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    data = pd.DataFrame(list(values), columns=columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_wise_product_commission(request):
    business_type_wise_ids = [1, 2, 3]
    product_data = {}
    product_ids = BusinessProductConcessionMap.objects.filter(business_type_id__in=business_type_wise_ids,
                                                              product__is_active=True,
                                                              concession_type_id=1).values_list('product_id', flat=True)

    commissions = BusinessTypeWiseProductCommission.objects.filter(business_type_id__in=business_type_wise_ids,
                                                                   product__is_active=True,
                                                                   product_id__in=product_ids).order_by('product_id')
    for commission in commissions:
        print(commission.business_type_id)
        if str(commission.business_type_id) not in product_data:
            product_data[str(commission.business_type_id)] = {}
        #     if str(commission.product_id) not in data[str(commission.product_id)]:
        #         data[str(commission.business_type_id)][str(commission.product_id)] = {}
        product_data[str(commission.business_type_id)][str(commission.product_id)] = commission.commission_percentage
    return Response(data=product_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_or_update_business_type_wise_product_commission(request):
    print(request.data)
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    now_utc = datetime.datetime.now(timezone('UTC'))
    print(now_utc.strftime(format))
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    print(now_asia.strftime(format))
    formatted_date = now_asia

    obj = BusinessTypeWiseProductCommission.objects.filter(
        product_id=request.data['product_id'], business_type_id=request.data['business_type_id']
    )

    if obj.exists():
        # trace update
        business_type_wise_commission_obj = BusinessTypeWiseProductCommission.objects.get(
            product_id=request.data['product_id'], business_type_id=request.data['business_type_id'])
        if BusinessTypeWiseProductCommissionTrace.objects.filter(
                business_type_wise_commission=business_type_wise_commission_obj, end_date__isnull=True).exists():
            business_type_commission_obj = BusinessTypeWiseProductCommissionTrace.objects.filter(
                business_type_wise_commission=business_type_wise_commission_obj).order_by('-time_created')[0]
            if Decimal(business_type_commission_obj.commission_percentage) != Decimal(request.data['commission']):
                BusinessTypeWiseProductCommissionTrace.objects.filter(
                    business_type_wise_commission=business_type_wise_commission_obj, end_date__isnull=True).update(
                    end_date=formatted_date,
                    product_commission_ended_by=request.user,
                )
        # update
        obj.update(commission_percentage=request.data['commission'], modified_by=request.user)

        # trace creation
        if BusinessTypeWiseProductCommissionTrace.objects.filter(
                business_type_wise_commission=business_type_wise_commission_obj).exists():
            business_type_commission_obj = BusinessTypeWiseProductCommissionTrace.objects.filter(
                business_type_wise_commission=business_type_wise_commission_obj).order_by('-time_created')[0]
            if Decimal(business_type_commission_obj.commission_percentage) != Decimal(request.data['commission']):
                BusinessTypeWiseProductCommissionTrace.objects.create(
                    business_type_wise_commission=business_type_wise_commission_obj,
                    start_date=formatted_date,
                    mrp=Product.objects.get(id=request.data['product_id']).mrp,
                    commission_percentage=request.data['commission'],
                    product_commission_started_by=request.user
                )
        else:
            BusinessTypeWiseProductCommissionTrace.objects.create(
                business_type_wise_commission=business_type_wise_commission_obj,
                start_date=formatted_date,
                mrp=Product.objects.get(id=request.data['product_id']).mrp,
                commission_percentage=request.data['commission'],
                product_commission_started_by=request.user
            )

    else:
        business_type_wise_commission_obj = BusinessTypeWiseProductCommission.objects.create(
            product_id=request.data['product_id'],
            business_type_id=request.data['business_type_id'],
            commission_percentage=request.data['commission'],
            created_by=request.user,
            modified_by=request.user
        )

        BusinessTypeWiseProductCommissionTrace.objects.create(
            business_type_wise_commission=business_type_wise_commission_obj,
            start_date=formatted_date,
            mrp=Product.objects.get(id=request.data['product_id']).mrp,
            commission_percentage=request.data['commission'],
            product_commission_started_by=request.user
        )
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_commission_products(request):
    print(request.data)
    data = {'ordered_product_ids': [], 'products': []}
    business_type_wise_ids = [1, 2, 3]
    values = BusinessProductConcessionMap.objects.filter(business_type_id__in=business_type_wise_ids,
                                                         product__is_active=True,
                                                         concession_type_id=1).order_by('id').values_list('product',
                                                                                                          'product__name',
                                                                                                          'product__mrp',
                                                                                                          'product__short_name',
                                                                                                          'product__unit__name',
                                                                                                          'product__quantity',
                                                                                                          'business_type_id',
                                                                                                          'concession_type__name',
                                                                                                          'product__gst_percent')
    columns = ['product_id', 'product_name', 'product_mrp', 'short_name', 'product_unit', 'quantity',
               'business_type_id', 'consession', 'gst']
    concession_df = pd.DataFrame(list(values), columns=columns)
    concession_df = concession_df.drop_duplicates(subset='product_id', keep='first')
    concession_df['quantity'] = concession_df['quantity'].astype('int').astype('str')
    concession_df['product_name'] = concession_df['product_name'] + ' ' + concession_df['quantity'] + concession_df[
        'product_unit']
    data['products'] = concession_df.to_dict('r')
    data['ordered_product_ids'] = concession_df.sort_values(by=['product_id'])['product_id'].to_list()
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_products_name_dict_type(request):
    values = Product.objects.filter(is_active=True).order_by('id').values_list('id', 'name', 'quantity', 'unit__name')
    columns = ['id', 'name', 'quantity', 'unit']
    df = pd.DataFrame(list(values), columns=columns)
    df['quantity'] = df['quantity'].astype('int').astype('str')
    df['name'] = df['name'] + ' ' + df['quantity'] + df['unit']
    data = dict(zip(df['id'], df['name']))
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_name_dict_type(request):
    values = BusinessType.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = dict(zip(df['id'], df['name']))
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_discount_products(request):
    data = {'product_ids': [], 'products': []}
    values = Product.objects.filter(is_active=True).exclude(id=28).order_by('id').values_list('id', 'name', 'quantity', 'short_name',
                                                                               'unit__name', 'mrp', 'gst_percent')
    columns = ['id', 'name', 'quantity', 'short_name', 'unit', 'mrp', 'gst']
    df = pd.DataFrame(list(values), columns=columns)
    data['products'] = df.to_dict('r')
    data['product_ids'] = df['id'].to_list()
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_discount_business(request):
    data = []
    business_type_ids = [4, 5, 6, 7, 10, 12, 15]
    values = Business.objects.filter(business_type_id__in=business_type_ids).order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    if not df.empty:
        data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_wise_discount_price_dict(request):
    data = {}
    business_type_ids = [4, 5, 6, 7, 10, 12, 15]
    values = BusinessWiseProductDiscount.objects.filter(business__business_type_id__in=business_type_ids).values_list(
        'business', 'product', 'discounted_price')
    columns = ['business_id', 'product_id', 'price']
    df = pd.DataFrame(list(values), columns=columns)
    if not df.empty:
        business_ids = df['business_id'].unique()
        for business_id in business_ids:
            filtered_df = df[df['business_id'] == business_id]
            data[str(business_id)] = {}
            data[str(business_id)] = dict(zip(filtered_df['product_id'], filtered_df['price']))
    return Response(data=data, status=status.HTTP_200_OK)


def make_business_wise_product_discount_trace(data):
    pass


@api_view(['POST'])
def remove_business_wise_product(request):
    if BusinessWiseProductDiscount.objects.filter(business_id=request.data['business_id'],
                                                  product_id=request.data['product_id']).exists():
        BusinessWiseProductDiscount.objects.filter(business_id=request.data['business_id'],
                                                   product_id=request.data['product_id']).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def save_or_update_business_wise_product_discount_price(request):
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    formatted_date = now_asia

    if BusinessWiseProductDiscount.objects.filter(business_id=request.data['business_id'],
                                                  product_id=request.data['product_id']).exists():
        formatted_date = now_asia + timedelta(days=1)
        obj = BusinessWiseProductDiscount.objects.get(business_id=request.data['business_id'],
                                                      product_id=request.data['product_id'])
        if BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount=obj, end_date=end_date_for_trace_filter).exists():
            business_discount_obj = \
            BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount=obj, end_date=end_date_for_trace_filter).order_by('-time_created')[0]
            if Decimal(business_discount_obj.discounted_price) != Decimal(request.data['discount_price']):
                BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount=obj,
                                                                end_date=end_date_for_trace_filter).update(
                    end_date=datetime.datetime.now(),
                    product_discount_ended_by=request.user
                )
                BusinessWiseProductDiscountTrace.objects.create(
                business_wise_discount=obj,
                end_date=end_date_for_trace_filter,
                start_date=formatted_date,
                mrp=Product.objects.get(id=request.data['product_id']).mrp,
                discounted_price=request.data['discount_price'],
                product_discount_started_by_id=request.user.id
                )
        else:
            BusinessWiseProductDiscountTrace.objects.create(
                business_wise_discount=obj,
                start_date=formatted_date,
                end_date=end_date_for_trace_filter,
                mrp=Product.objects.get(id=request.data['product_id']).mrp,
                discounted_price=request.data['discount_price'],
                product_discount_started_by_id=request.user.id
            )

        data = {
            'old_discount_price': obj.discounted_price
        }

        obj.discounted_price = request.data['discount_price']
        obj.save()
        data['new_discount_price'] = obj.discounted_price
        data['product_id'] = obj.product_id
        data['business_id'] = obj.business_id

        return Response(status=status.HTTP_200_OK)
    else:
        obj = BusinessWiseProductDiscount.objects.create(
            business_id=request.data['business_id'],
            product_id=request.data['product_id'],
            discounted_price=request.data['discount_price'],
            created_by=request.user,
            modified_by=request.user
        )

        BusinessWiseProductDiscountTrace.objects.create(
            business_wise_discount=obj,
            end_date=end_date_for_trace_filter,
            start_date=formatted_date,
            mrp=Product.objects.get(id=request.data['product_id']).mrp,
            discounted_price=request.data['discount_price'],
            product_discount_started_by=request.user
        )

        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_wise_discount_product(request):
    values = Product.objects.filter(group_id__in=[2, 3], is_active=True).exclude(id=28).order_by('id').values_list('id', 'name',
                                                                                                    'quantity',
                                                                                                    'short_name',
                                                                                                    'unit__name', 'mrp',
                                                                                                    'gst_percent')
    columns = ['id', 'name', 'quantity', 'short_name', 'unit', 'mrp', 'gst']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_icustomer_wise_discount_product(request):
    values = Product.objects.filter(group_id=1, is_active=True).order_by('id').values_list('id', 'name', 'quantity',
                                                                                           'unit__name', 'mrp')
    columns = ['id', 'name', 'quantity', 'unit', 'mrp']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_wise_discount_business_types(request):
    data = []
    business_type_ids = [1, 2, 3, 9, 16]
    values = BusinessType.objects.filter(id__in=business_type_ids).order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    if not df.empty:
        data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_wise_discount_price_dict(request):
    print('SOMETHING')
    data = {}
    business_type_ids = [1, 2, 3, 9, 16]
    values = BusinessTypeWiseProductDiscount.objects.filter(business_type_id__in=business_type_ids,
                                                            product__is_active=True).values_list('business_type',
                                                                                                 'business_type__name',
                                                                                                 'product',
                                                                                                 'product__name',
                                                                                                 'discounted_price')
    columns = ['business_type_id', 'business_type_name', 'product_id', 'product_name', 'discounted_price']
    df = pd.DataFrame(list(values), columns=columns)
    print(df)
    if not df.empty:
        business_ids = df['business_type_id'].unique()
        for business_id in business_ids:
            filtered_df = df[df['business_type_id'] == business_id]
            data[str(business_id)] = {}
            data[str(business_id)] = dict(zip(filtered_df['product_id'], filtered_df['discounted_price']))
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_or_update_business_type_wise_discount_price(request):
    print(request.data)
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    formatted_date = now_asia
    if BusinessTypeWiseProductDiscount.objects.filter(business_type_id=request.data['business_type_id'],
                                                      product_id=request.data['product_id']).exists():
        formatted_date = now_asia + timedelta(days=1)
        obj = BusinessTypeWiseProductDiscount.objects.get(business_type_id=request.data['business_type_id'],
                                                          product_id=request.data['product_id'])
        if BusinessTypeWiseProductDiscountTrace.objects.filter(business_type_wise_discount=obj,
                                                               end_date=end_date_for_trace_filter).exists():
            business_type_discount_obj = \
            BusinessTypeWiseProductDiscountTrace.objects.filter(business_type_wise_discount=obj).order_by(
                '-time_created')[0]
            if Decimal(business_type_discount_obj.discounted_price) != Decimal(request.data['discount_price']):
                BusinessTypeWiseProductDiscountTrace.objects.filter(business_type_wise_discount=obj,
                                                                    end_date=end_date_for_trace_filter).update(
                    end_date=datetime.datetime.now(),
                    product_discount_ended_by_id=request.user.id
                )

                BusinessTypeWiseProductDiscountTrace.objects.create(
                    business_type_wise_discount=obj,
                    start_date=formatted_date,
                    end_date=end_date_for_trace_filter,
                    mrp=Product.objects.get(id=request.data['product_id']).mrp,
                    discounted_price=request.data['discount_price'],
                    product_discount_started_by_id=request.user.id
                )
        else:
            BusinessTypeWiseProductDiscountTrace.objects.create(
                business_type_wise_discount=obj,
                start_date=formatted_date,
                end_date=end_date_for_trace_filter,
                mrp=Product.objects.get(id=request.data['product_id']).mrp,
                discounted_price=request.data['discount_price'],
                product_discount_started_by_id=request.user.id
            )

        data = {
            'old_discount_price': obj.discounted_price
        }
        obj.discounted_price = request.data['discount_price']
        obj.save()
        data['new_discount_price'] = obj.discounted_price
        data['product_id'] = obj.product_id
        data['business_type_id'] = obj.business_type_id
        return Response(status=status.HTTP_200_OK)
    else:
        obj = BusinessTypeWiseProductDiscount.objects.create(
            business_type_id=request.data['business_type_id'],
            product_id=request.data['product_id'],
            discounted_price=request.data['discount_price'],
            created_by=request.user,
            modified_by=request.user
        )

        BusinessTypeWiseProductDiscountTrace.objects.create(
            business_type_wise_discount=obj,
            start_date=formatted_date,
            end_date=end_date_for_trace_filter,
            mrp=Product.objects.get(id=request.data['product_id']).mrp,
            discounted_price=request.data['discount_price'],
            product_discount_started_by_id=request.user.id
        )
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_business_type_wise_product(request):
    print(request.data)
    if BusinessTypeWiseProductDiscount.objects.filter(business_type_id=request.data['business_type_id'],
                                                      product_id=request.data['product_id']).exists():
        print('exists deleted')
        BusinessTypeWiseProductDiscount.objects.filter(business_type_id=request.data['business_type_id'],
                                                       product_id=request.data['product_id']).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_all_business(request):
    values = Business.objects.all().values_list('id', 'name', 'code')
    columns = ['id', 'name', 'code']
    data = pd.DataFrame(list(values), columns=columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)

    
@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_all_business_for_booth_change(request):
    values = BusinessAgentMap.objects.filter(business__business_type__in=[1, 2, 3]).values_list('business_id',
                                                                                                'agent__first_name',
                                                                                                'business__code').order_by(
        'business__code')
    columns = ['id', 'name', 'code']
    data = pd.DataFrame(list(values), columns=columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_unmapped_business_with_route_session(request):
    print(request.data)
    route_id = request.data['route_id']
    route_session = Route.objects.get(id=route_id).session
    exclude_business_ids = RouteBusinessMap.objects.filter(route__session=route_session).values_list('business_id',
                                                                                                     flat=True)
    business = Business.objects.filter().exclude(id__in=exclude_business_ids)
    values = business.order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    data = pd.DataFrame(list(values), columns=columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
def check_wheather_customer_exists(request):
    print(request.data)
    data_dict = {}
    if UserProfile.objects.filter(mobile=request.data['phone']).exists():
        # user_obj = UserProfile.objects.get(mobile=request.data['phone'])
        data_dict['status'] = True
        # otp = generate_otp()
        # message = 'Your OTP is' + str(otp)
        # purpose = 'To valid the user phone number'
        # send_message_via_netfision(purpose, request.data['phone'], message)
        # if TemporaryRegistration.objects.filter(username=request.data['phone']).exists():
        #     temporary_register_obj = TemporaryRegistration.objects.get(username=request.data['phone'])
        #     temporary_register_obj.otp = otp
        #     temporary_register_obj.save()
        #     print('Temporary registation is replaced')
        # else:
        #     temporary_register_obj = TemporaryRegistration(
        #         union_id=1,
        #         first_name=user_obj.user.first_name,
        #         last_name=user_obj.user.last_name,
        #         username=request.data['phone'],
        #         mobile=request.data['phone'],
        #         otp=otp
        #     )
        #     temporary_register_obj.save()
        #     print('New temp reg data uploaded')
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        print('user Not Exists')
        otp = generate_otp()
        print(otp)
        message = 'Your OTP is ' + str(otp)
        purpose = 'To valid the user phone number'


        send_message_via_netfision(purpose, request.data['phone'], message)
        if TemporaryRegistration.objects.filter(username=request.data['phone']).exists():
            temporary_register_obj = TemporaryRegistration.objects.get(username=request.data['phone'])
            temporary_register_obj.otp = otp
            temporary_register_obj.save()
            print('Temporary registation is replaced')
        else:
            temporary_register_obj = TemporaryRegistration(
                union_id=1,
                first_name='customer',
                last_name='customer',
                username=request.data['phone'],
                mobile=request.data['phone'],
                otp=otp
            )
            temporary_register_obj.save()
            print('New temp reg data uploaded')
        data_dict['status'] = False
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_taluk(request):
    print(request.data)
    data = {'message': ''}
    if request.data['id'] is None:  # save product
        if Taluk.objects.filter(name__iexact=request.data['name'], district_id=request.data['district_id']).exists():
            data['message'] = 'taluk is already registered'
        else:
            taluk = Taluk.objects.create(name=request.data['name'], district_id=request.data['district_id'])
            data['message'] = '{taluk_name} is registered successfully!'.format(taluk_name=taluk.name)
        return Response(data, status=status.HTTP_200_OK)
    else:  # update product
        print('edit')
        taluk = Taluk.objects.get(id=request.data['id'])
        taluk.name = request.data['name']
        taluk.district_id = request.data['district_id']
        taluk.save()
        data['message'] = 'taluk updated successfully'
        return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_employee(request):
    values = Employee.objects.filter().order_by('user_profile__user__first_name').values_list('id',
                                                                                              'user_profile__user__first_name',
                                                                                              'user_profile__user__last_name',
                                                                                              'user_profile__mobile',
                                                                                              'user_profile',
                                                                                              'office__name',
                                                                                              'role__name',
                                                                                              'joining_date',
                                                                                              'user_profile__image',
                                                                                              'user_profile__union__name',
                                                                                              'user_profile__gender__name',
                                                                                              'user_profile__street',
                                                                                              'user_profile__taluk__name',
                                                                                              'user_profile__district__name',
                                                                                              'user_profile__state__name')
    columns = ['id', 'first_name', 'last_name', 'mobile', 'user_profile_id', 'office_name', 'role_name', 'joining_date',
               'image', 'union_name',
               'gender_name', 'street', 'taluk_name', 'district_name', 'state_name']
    df = pd.DataFrame(list(values), columns=columns)

    for index, row in df.iterrows():
        try:
            image_path = 'static/media/' + row['image']
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                df.at[index, 'image'] = encoded_image
        except Exception as err:
            print(err)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_office(request):
    values = Office.objects.filter().order_by('name').values_list('id', 'union_id', 'union__name', 'name', 'street',
                                                                  'taluk', 'taluk__name', 'district', 'district__name',
                                                                  'state', 'mobile', 'alternate_mobile', 'phone',
                                                                  'address')
    columns = ['id', 'union_id', 'union', 'name', 'street', 'taluk_id', 'taluk', 'district_id', 'district', 'state_id',
               'mobile', 'alternate_mobile', 'phone', 'address']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_employee_role(request):
    values = EmployeeRole.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_employee(request):
    data = {'message': ''}
    print(request.data)
    if request.data['id'] is None:  # save product
        if User.objects.filter(username=request.data['mobile']).exists():
            data['message'] = 'Employee already Exists'
        else:
            user_obj = User(
                username=request.data['mobile'],
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                password=make_password(1234)
            )
            user_obj.save()
            user_profile_obj = UserProfile(
                union_id=request.data['union_id'],
                user=user_obj,
                user_type_id=1,
                gender_id=request.data['gender_id'],
                taluk_id=request.data['taluk_id'],
                district_id=request.data['district_id'],
                state_id=request.data['state_id'],
                mobile=request.data['mobile']
            )
            if request.data['street'] != None:
                user_profile_obj.street = request.data['street']

            if request.data['alternate_mobile'] != None:
                user_profile_obj.alternate_mobile = request.data['alternate_mobile']

            if request.data['pincode'] != None:
                user_profile_obj.pincode = request.data['pincode']

            if request.data['employee_image'] != None:
                user_profile_obj.image = decode_image(request.data['employee_image'])

            user_profile_obj.save()
            employee_obj = Employee(user_profile=user_profile_obj,
                                    office_id=request.data['office'],
                                    role_id=request.data['role'],
                                    joining_date=request.data['joining_date'],
                                    )
            if not request.data['release_date'] is None:
                employee_obj.release_date = request.data['release_date']

            employee_obj.save()
            data['message'] = 'Employee registered successfully'
            print('employee saved')
        return Response(data, status=status.HTTP_200_OK)
    else:
        user_id = Employee.objects.get(id=request.data['id']).user_profile.user.id
        User.objects.filter(id=user_id).update(
            first_name=request.data['first_name'],
            last_name=request.data['last_name']
        )
        UserProfile.objects.filter(user_id=user_id).update(
            union_id=request.data['union_id'],
            street=request.data['street'],
            gender_id=request.data['gender_id'],
            taluk_id=request.data['taluk_id'],
            district_id=request.data['district_id'],
            state_id=request.data['state_id'],
            mobile=request.data['mobile'],
            alternate_mobile=request.data['alternate_mobile'],
            pincode=request.data['pincode']
        )
        user_profile_obj = UserProfile.objects.get(user_id=user_id)
        if request.data['street'] != None:
            user_profile_obj.street = request.data['street']

        if request.data['alternate_mobile'] != None:
            user_profile_obj.alternate_mobile = request.data['alternate_mobile']

        if request.data['pincode'] != None:
            user_profile_obj.pincode = request.data['pincode']

        if request.data['employee_image'] != None:
            if 'changingThisBreaksApplicationSecurity' in request.data['employee_image']:
                user_profile_obj.image = decode_image(
                    request.data['employee_image']['changingThisBreaksApplicationSecurity'])
            else:
                user_profile_obj.image = decode_image(request.data['employee_image'])

        Employee.objects.filter(id=request.data['id']).update(
            office_id=request.data['office'],
            role_id=request.data['role'],
            joining_date=request.data['joining_date'],
        )
        if 'release date' in request.data:
            Employee.objects.filter(id=request.data['id']).update(release_date=request.data['release_date'])
        user_profile_obj.save()
        data['message'] = 'Employee updated successfully'
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def otp_validation_for_temporary_registration(request):
    print(request.data)
    data_dict = {}
    if request.data['customer_exists']:
        if TemporaryRegistration.objects.filter(username=request.data['phone']).exists():
            temporary_register_obj = TemporaryRegistration.objects.get(username=request.data['phone'])
            if temporary_register_obj.otp == str(request.data['otp']):
                print('Otp Matched')
                if User.objects.filter(username=request.data['phone']).exists():
                    print('username exists')
                    data_dict['user_exists'] = True
                else:
                    data_dict['user_exists'] = False
                return Response(data=data_dict, status=status.HTTP_200_OK)
            else:
                return Response(data='OTP does Not Match', status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            print('Temp Not available')
            return Response(data='Not Avl', status=status.HTTP_409_CONFLICT)

    else:
        if TemporaryRegistration.objects.filter(username=request.data['phone']).exists():
            print('Temp Reg. Avl!')
            temporary_register_obj = TemporaryRegistration.objects.get(username=request.data['phone'])
            if temporary_register_obj.otp == str(request.data['otp']):
                print('Otp Matched')
                return Response(data='Correct otp', status=status.HTTP_200_OK)
            else:
                return Response(data='OTP does Not Match', status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            print('Temp Not available')
            return Response(data='Not Avl', status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def save_relation_type(request):
    print(request.data)
    if request.data['id'] is None:
        if RelationType.objects.filter(name=request.data['relation_type_name']).exists():
            data = {'message': 'Relation type already registered'}
        else:
            RelationType.objects.create(
                name=request.data['relation_type_name']
            )
            data = {'message': 'Relation type registered successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        RelationType.objects.filter(id=request.data['id']).update(
            name=request.data['relation_type_name'],
        )
        data = {'message': 'relation type updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_routes(request):
    values = Route.objects.filter(is_temp_route=False).order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    data = pd.DataFrame(list(values), columns=columns).to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def route_business_map(request):
    print(request.data)
    data = {}
    if not SaleGroup.objects.filter(date__gt=datetime.datetime.now(), business_id=request.data['business_id']).exists():
        data['is_time_available'] = True
        route_id = request.data['route_id']
        route_name = Route.objects.get(id=route_id).name
        route_session_id = Route.objects.get(id=route_id).session.id
        busines_name = Business.objects.get(id=request.data['business_id']).name
        busines_code = Business.objects.get(id=request.data['business_id']).code
        print(route_session_id)
        print(request.data['business_id'])
        if RouteBusinessMap.objects.filter(route_id=route_id, business_id=request.data['business_id']).exists():
            data['status'] = 'alert'
            data['message'] = busines_name + 'is already exists in this route'
            return Response(data, status=status.HTTP_200_OK)
        if RouteBusinessMap.objects.filter(business_id=request.data['business_id'],
                                           route__session_id=route_session_id).exists():
            maped_route_name = RouteBusinessMap.objects.get(business_id=request.data['business_id'],
                                                            route__session_id=route_session_id).route.name
            data['status'] = 'confirm'
            data['message'] = busines_name + ' is already mapped to ' + maped_route_name
            data['route_map_id'] = RouteBusinessMap.objects.get(business_id=request.data['business_id'],
                                                                route__session_id=route_session_id).id
            print(data)
            return Response(data, status=status.HTTP_200_OK)

        business_route_change_log = BusinessRouteChangeLog(business_id=request.data['business_id'],
                                                           new_route_id=route_id,
                                                           changed_by_id=request.user.id,
                                                           description=str(busines_code) + ' Booth Attached To ' + str(
                                                               route_name),
                                                           changed_at=datetime.datetime.now())
        business_route_change_log.save()

        RouteBusinessMap.objects.get_or_create(
            route_id=route_id,
            business_id=request.data['business_id']
        )
        route_objects = RouteBusinessMap.objects.filter(route_id=route_id,
                                                        ordinal__gte=request.data['current_index'] + 1)
        for route_object in route_objects:
            route_object.ordinal = route_object.ordinal + 1
            route_object.save()
            print('saved')
        RouteBusinessMap.objects.filter(route_id=route_id, business_id=request.data['business_id']).update(
            ordinal=request.data['current_index'] + 1)
        data['status'] = 'toast'
        return Response(data, status=status.HTTP_200_OK)
    else:
        data['is_time_available'] = False
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_business_from_route(request):
    print(request.data)
    data = {}
    if not SaleGroup.objects.filter(date__gt=datetime.datetime.now(), business_id=request.data['business_id']).exists():
        route_id = request.data['route_id']
        route_name = Route.objects.get(id=route_id).name
        busines_code = Business.objects.get(id=request.data['business_id']).code
        RouteBusinessMap.objects.filter(
            route_id=route_id,
            business_id=request.data['business_id']
        ).delete()
        business_route_change_log = BusinessRouteChangeLog(business_id=request.data['business_id'],
                                                           old_route_id=route_id,
                                                           changed_by_id=request.user.id,
                                                           description=str(busines_code) + ' Booth Removed From ' + str(
                                                               route_name),
                                                           changed_at=datetime.datetime.now())
        business_route_change_log.save()
        data = {'message': 'Business removed from route', 'is_time_available': True}

        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data['is_time_available'] = False
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_business_by_route(request):
    print(request.data)
    route_name = Route.objects.get(id=request.data['route_id']).name
    values = RouteBusinessMap.objects.filter(route_id=request.data['route_id']).order_by('ordinal').values_list(
        'business_id', 'business__name', 'business__is_active', 'ordinal')
    columns = ['id', 'name', 'business_is_active', 'ordinal']
    route_df = pd.DataFrame(list(values), columns=columns)
    temp_data = route_df.to_dict('r')
    data = {}
    data['route_name'] = route_name
    data['businesses'] = temp_data
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_products_for_agent_order(request):
    values = Product.objects.filter(is_active=True).values_list('id', 'name', 'short_name')
    columns = ['id', 'name', 'short_name']
    route_df = pd.DataFrame(list(values), columns=columns)
    data = route_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


def serve_state_district_taluk():
    temp_dict = {'states': [], 'districts': {}, 'taluks': {}}
    states = State.objects.all().order_by('id')
    districts = District.objects.all().order_by('name')
    taluks = Taluk.objects.all().order_by('name')

    state_values = list(states.values_list('id', 'name'))
    state_columns = ['id', 'name']
    state_df = pd.DataFrame(state_values, columns=state_columns)

    district_values = list(districts.values_list('id', 'name', 'state'))
    district_columns = ['id', 'name', 'state_id']
    district_df = pd.DataFrame(district_values, columns=district_columns)

    taluk_values = list(taluks.values_list('id', 'name', 'district'))
    taluk_columns = ['id', 'name', 'district_id']
    taluk_df = pd.DataFrame(taluk_values, columns=taluk_columns)

    temp_dict['states'] = state_df.to_dict('r')
    temp_dict['districts'] = district_df.groupby('state_id').apply(
        lambda x: x.set_index('state_id').to_dict('r')).to_dict()
    temp_dict['taluks'] = taluk_df.groupby('district_id').apply(
        lambda x: x.set_index('district_id').to_dict('r')).to_dict()

    return temp_dict


def serve_gender():
    gender = Gender.objects.all()
    gender_values = list(gender.values_list('id', 'name'))
    gender_columns = ['id', 'name']
    gender_df = pd.DataFrame(gender_values, columns=gender_columns)
    return gender_df.to_dict('r')


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_general_data_for_registration(request):
    data_dict = {'location_details': {}, 'genders': []}
    data_dict['location_details'] = serve_state_district_taluk()
    data_dict['genders'] = serve_gender()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_employee_details(request):
    employee_obj = Employee.objects.get(id=request.data['id'])
    user_profile = UserProfile.objects.get(id=employee_obj.user_profile.id)
    user_obj = User.objects.get(id=user_profile.user.id)

    data_dict = {
        'id': employee_obj.id,
        'office_id': employee_obj.office.id,
        'role_id': employee_obj.role.id,
        'joining_date': str(employee_obj.joining_date).split(' ')[0],
        'union_id': user_profile.union.id,
        'user_type_id': user_profile.user_type.id,
        'street': user_profile.street,
        'gender_id': user_profile.gender.id,
        'taluk_id': user_profile.taluk.id,
        'district_id': user_profile.district.id,
        'state_id': user_profile.state.id,
        'mobile': user_profile.mobile,
        'alternate_mobile': user_profile.alternate_mobile,
        'pincode': user_profile.pincode,
        'username': user_obj.username,
        'first_name': user_obj.first_name,
        'last_name': user_obj.last_name,
    }
    try:
        image_path = 'static/media/' + str(user_profile.image)
        # print(image_path)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_union_office(request):
    print(request.data)
    if request.data['id'] is None:  # save product
        if Office.objects.filter(union_id=request.data['union_id'], name__iexact=request.data['name'],
                                 taluk_id=request.data['taluk_id'], district_id=request.data['district_id'],
                                 state_id=request.data['state_id'], mobile=request.data['mobile']).exists():
            data = {'message': "Union office already exists"}
        else:
            office_obj = Office(
                union_id=request.data['union_id'],
                name=request.data['name'],
                taluk_id=request.data['taluk_id'],
                district_id=request.data['district_id'],
                state_id=request.data['state_id'],
                mobile=request.data['mobile']
            )

            if request.data['street'] != None:
                office_obj.street = request.data['street']

            if request.data['address'] != None:
                office_obj.address = request.data['address']

            if request.data['phone'] != None:
                office_obj.phone = request.data['phone']

            if request.data['alternate_mobile'] != None:
                office_obj.alternate_mobile = request.data['alternate_mobile']

            office_obj.save()
            data = {'message': "union office added successfully"}
        return Response(data, status=status.HTTP_200_OK)
    else:
        Office.objects.filter(id=request.data['id']).update(
            union_id=request.data['union_id'],
            name=request.data['name'],
            taluk_id=request.data['taluk_id'],
            district_id=request.data['district_id'],
            state_id=request.data['state_id'],
            mobile=request.data['mobile']
        )
        office_obj = Office.objects.get(id=request.data['id'])

        if request.data['street'] != None:
            office_obj.street = request.data['street']

        if request.data['address'] != None:
            office_obj.address = request.data['address']

        if request.data['phone'] != None:
            office_obj.phone = request.data['phone']

        if request.data['alternate_mobile'] != None:
            office_obj.alternate_mobile = request.data['alternate_mobile']

        office_obj.save()
        data = {'message': 'union office updated successfully'}
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def register_customer(request):
    print(request.data)
    if request.data['from'] == 'mobile':
        via_id = 1
    else:
        via_id = 3
    last_count = IcustomerIdBank.objects.get(id=1).last_count
    prefix = int(last_count)
    updated_code = 'CBE' + str(prefix)
    not_exists = True
    while (not_exists):
        print(updated_code)
        if ICustomer.objects.filter(customer_code=updated_code).exists():
            prefix = prefix + 1
            updated_code = 'CBE' + str(prefix)
        else:
            not_exists = False
    user_obj = User(username=updated_code,
                    first_name=request.data['form_values']['first_name'],
                    last_name=request.data['form_values']['last_name'],
                    password=make_password(request.data['form_values']['password']))
    if request.data['form_values']['email'] is not None:
        user_obj.email = request.data['form_values']['email']
    user_obj.save()
    user_profile_obj = UserProfile(union_id=1,
                                   user=user_obj,
                                   user_type_id=3,  # icustomer
                                   gender_id=request.data['form_values']['gender'],
                                   taluk_id=request.data['form_values']['taluk'],
                                   district_id=request.data['form_values']['district'],
                                   state_id=request.data['form_values']['state'],
                                   mobile=request.data['form_values']['phone'],
                                   pincode=request.data['form_values']['pincode'],
                                   )
    if request.data['form_values']['alternate_mobile'] is not None:
        user_profile_obj.alternate_mobile = request.data['form_values']['alternate_mobile']
    if request.data['form_values']['street'] is not None:
        user_profile_obj.street = request.data['form_values']['street']
    if request.data['form_values']['latitude'] is not None:
        user_profile_obj.latitude = request.data['form_values']['latitude']
        user_profile_obj.longitude = request.data['form_values']['longitude']
    user_profile_obj.save()
    customer_obj = ICustomer(user_profile_id=user_profile_obj.id,
                             customer_code=str(updated_code),
                             customer_type_id=1,
                             aadhar_number=request.data['form_values']['aadhar_card_number'],
                             is_mobile_number_verified_by_customer=True,
                             is_aadhar_number_verified_by_customer=True,
                             created_via_id=via_id
                             )
    if request.data['form_values']['aadhar_image'] is not None:
        customer_obj.aadhar_document = decode_image(request.data['form_values']['aadhar_image'],
                                                    customer_obj.user_profile.user.first_name)
    customer_obj.save()
    print('Icustomer created')
    purpose = 'Confimation message'
    message = 'Dear ' + str(
        customer_obj.user_profile.user.first_name) + ' you have successfully registered yourself as Aavin card Milk subscribe. Your customer code is ' + str(
        customer_obj.customer_code) + ' Thank You. Please complete the process by selecting point of delivery.'

    template_id = BsnlSmsTemplate.objects.filter(message_name='register_customer').first().template_id
    template_list = [
                {'Key': 'name', 'Value': str(customer_obj.user_profile.user.first_name)},
                {'Key': 'customer_code', 'Value': str(customer_obj.customer_code)}
                    ]
    send_message_from_bsnl(template_id, template_list, user_obj.mobile)

    # send_message_via_netfision(purpose, request.data['form_values']['phone'], message)
    IcustomerIdBank.objects.filter(id=1).update(last_count=str(prefix))

    icustomer_wallet = ICustomerWallet(customer_id=customer_obj.id,
                                       current_balance=0,
                                       credit_limit=0)
    icustomer_wallet.save()
    data_dict = {
        'user_profile_id': user_profile_obj.id
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def serve_routes(request):
#     values = Route.objects.filter(is_temp_route=False).order_by('id').values_list('id', 'name')
#     columns = ['id', 'name']
#     data = pd.DataFrame(list(values), columns=columns).to_dict('r')
#     return Response(data=data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def route_business_map(request):
#     print(request.data)
#     route_id = request.data['route_id']
#     RouteBusinessMap.objects.get_or_create(
#         route_id=route_id,
#         business_id=request.data['business_id']
#     )
#     return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_booth_under_pincode(request):
    print(request.data)
    business_obj = BusinessAgentMap.objects.filter(business__pincode=request.data['pincode'],
                                                   business__business_type_id=1)
    business_list = list(
        business_obj.values_list('business_id', 'business__code', 'business__zone', 'business__zone__name',
                                 'business__name', 'business__constituency', 'business__constituency__name',
                                 'business__ward', 'business__ward__name', 'business__address',
                                 'business__location_category', 'business__location_category__name',
                                 'business__location_category_value', 'business__pincode', 'business__landmark',
                                 'business__working_hours_from', 'business__working_hours_to', 'business__latitude',
                                 'business__longitude', 'agent__first_name',
                                 'agent__last_name', 'agent__agent_profile__mobile'))
    business_column = ['business_id', 'code', 'zone_id', 'zone_name', 'name', 'constituency_id', 'constituency_name',
                       'ward_id', 'ward_name', 'address', 'location_category_id', 'location_category_name',
                       'location_category_value', 'pincode', 'landmark', 'working_hours_from', 'working_hours_to',
                       'latitude', 'longitude', 'agent_first_name', 'agent_last_name', 'agent_mobile_number']
    business_df = pd.DataFrame(business_list, columns=business_column)
    business_df['working_hours_from'] = business_df['working_hours_from'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    business_df['working_hours_to'] = business_df['working_hours_to'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    return Response(data=business_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_booth_lat_lng(request):
    business_obj = BusinessAgentMap.objects.filter(business__business_type_id=1)
    business_list = list(
        business_obj.values_list('business_id', 'business__code', 'business__latitude', 'business__longitude'))
    business_column = ['business_id', 'business_code', 'lat', 'lng']
    business_df = pd.DataFrame(business_list, columns=business_column)
    return Response(data=business_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_selected_booth_details(request):
    business_obj = BusinessAgentMap.objects.filter(business_id=request.data['business_id'])
    business_list = list(
        business_obj.values_list('business_id', 'business__code', 'business__latitude', 'business__longitude',
                                 'business__address', 'business__name', 'business__location_category__name',
                                 'business__location_category_value', 'business__landmark', 'agent__first_name',
                                 'agent__last_name', 'agent__agent_profile__mobile', 'business__working_hours_from',
                                 'business__working_hours_to'))
    business_column = ['business_id', 'business_code', 'lat', 'lng', 'address', 'name', 'location_category_name',
                       'location_category_value', 'landmark', 'agent_first_name', 'agent_last_name',
                       'agent_mobile_number', 'working_hours_from', 'working_hours_to']
    business_df = pd.DataFrame(business_list, columns=business_column)
    business_df['working_hours_from'] = business_df['working_hours_from'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    business_df['working_hours_to'] = business_df['working_hours_to'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    return Response(data=business_df.to_dict('r')[0], status=status.HTTP_200_OK)


def update_customer_booth_change_log(old_business_id, new_business_id, icustomer_id, user_id):
    print(old_business_id, new_business_id)
    icustomer_booth_change_log = ICustomerBusinessLog(icustomer_id=icustomer_id,
                                                      old_business_id=old_business_id,
                                                      new_business_id=new_business_id,
                                                      changed_by_id=user_id,
                                                      changed_at=datetime.datetime.now())
    icustomer_booth_change_log.save()


@api_view(['POST'])
@permission_classes((AllowAny,))
def link_booth_with_customer(request):
    print(request.data)
    if request.data['page_action'] == 'register':
        user_profile_id = request.data['user_profile_id']
        icustomer_obj = ICustomer.objects.get(user_profile_id=user_profile_id)
        icustomer_obj.business_id = request.data['business_id']
        icustomer_obj.save()
        data_dict = {
            'customer_code': icustomer_obj.customer_code
        }
        purpose = 'Confimation message'
        message = 'Dear ' + str(icustomer_obj.user_profile.user.first_name) + '(' + str(
            icustomer_obj.customer_code) + ')' + ', You have selected booth number ' + str(
            icustomer_obj.business.code) + ' to recieve your milk packets. Your orders will be delivered to a this booth.'
        if not str(icustomer_obj.user_profile.mobile)[0:5] == '99999':
            try:
                template_id = BsnlSmsTemplate.objects.filter(message_name='link_booth_with_customer').first().template_id
                template_list = [
                    {'Key': 'booth', 'Value': str(icustomer_obj.business.code)},
                    {'Key': 'customer_code', 'Value': str(icustomer_obj.customer_code)},
                    {'Key': 'name', 'Value': str(icustomer_obj.user_profile.user.first_name)},
                ]
                send_message_from_bsnl(template_id, template_list, icustomer_obj.user_profile.mobile)
            except Exception as e:
                print(e)
            # send_message_via_netfision(purpose, icustomer_obj.user_profile.mobile, message)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    elif request.data['page_action'] == 'edit':
        if request.data['from'] == 'portal' or request.data['from'] == 'website':
            user_profile_id = request.data['user_profile_id']
        elif request.data['from'] == 'mobile':
            user_profile_id = request.user.userprofile.id
        customer_obj = ICustomer.objects.get(user_profile_id=user_profile_id)
        update_customer_booth_change_log(customer_obj.business_id, request.data['business_id'], customer_obj.id,
                                         request.user.id)
        old_booth_code = customer_obj.business.code
        customer_obj.business_id = request.data['business_id']
        customer_obj.save()
        new_buiness_code = Business.objects.get(id=request.data['business_id']).code
        purpose = 'Confimation message'
        message = 'Dear ' + str(customer_obj.user_profile.user.first_name) + '(' + str(
            customer_obj.customer_code) + ')' + ', You have successfully changed your booth from ' + str(
            old_booth_code) + ' to ' + str(
            new_buiness_code) + ' Your orders will be delivered to a this booth. Thank you very much'
        if not str(customer_obj.user_profile.mobile)[0:5] == '99999':
            try:
                template_id = BsnlSmsTemplate.objects.filter(message_name='link_booth_customer_before').first().template_id
                template_list = [
                    {'Key': 'name', 'Value': str(customer_obj.user_profile.user.first_name)},
                    {'Key': 'customer_code', 'Value': str(customer_obj.customer_code)},
                    {'Key': 'old_code', 'Value': str(old_booth_code)},
                    {'Key': 'new_code', 'Value': str(new_buiness_code)},
                ]
                send_message_from_bsnl(template_id, template_list, icustomer_obj.user_profile.mobile)
            except Exception as e:
                print(e)
            # send_message_via_netfision(purpose, customer_obj.user_profile.mobile, message)
        return Response(status=status.HTTP_200_OK)
    elif request.data['page_action'] == 'after_order':
        if request.data['from'] == 'portal' or request.data['from'] == 'website':
            user_profile_id = request.data['user_profile_id']
        elif request.data['from'] == 'mobile':
            user_profile_id = request.user.userprofile.id
        customer_obj = ICustomer.objects.get(user_profile_id=user_profile_id)
        update_customer_booth_change_log(customer_obj.business_id, request.data['business_id'], customer_obj.id,
                                         request.user.id)
        old_booth_code = customer_obj.business.code
        customer_obj.business_id = request.data['business_id']
        new_buiness_code = Business.objects.get(id=request.data['business_id']).code
        customer_obj.save()
        sale_group_obj = ICustomerSaleGroup.objects.filter(date__month=request.data['selected_date']['month'],
                                                           date__year=request.data['selected_date']['year'],
                                                           icustomer_id=customer_obj.id)
        for sale_group in sale_group_obj:
            sale_group.business_id = request.data['business_id']
            sale_group.save()
            print(sale_group.date)
        purpose = 'Confimation message'
        message = 'Dear ' + str(customer_obj.user_profile.user.first_name) + '(' + str(
            customer_obj.customer_code) + ')' + ', You have successfully changed your booth from ' + str(
            old_booth_code) + ' to ' + str(
            new_buiness_code) + ' Your orders will be delivered to a this booth. Thank you very much'
        if not str(customer_obj.user_profile.mobile)[0:5] == '99999':
            # try:
            #     template_id = BsnlSmsTemplate.objects.filter(message_name='link_booth_customer_after').first().template_id
            #     template_list = [
            #         {'Key': 'name', 'Value': str(customer_obj.user_profile.user.first_name)},
            #         {'Key': 'customer_code', 'Value': str(customer_obj.customer_code)},
            #         {'Key': 'old_code', 'Value': str(old_booth_code)},
            #         {'Key': 'new_code', 'Value': str(new_buiness_code)},
            #     ]
            #     send_message_from_bsnl(template_id, template_list, icustomer_obj.user_profile.mobile)
            # except Exception as e:
            #     print(e)
            send_message_via_netfision(purpose, customer_obj.user_profile.mobile, message)
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_location_category(request):
    if request.data['id'] is None:
        if LocationCategory.objects.filter(name__iexact=request.data['location_category_name']).exists():
            data = {'message': 'location cateogry already Exists!'}
        else:
            LocationCategory.objects.create(
                name=request.data['location_category_name']
            )
            data = {'message': 'location cateogry registered successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)

    else:
        LocationCategory.objects.filter(id=request.data['id']).update(
            name=request.data['location_category_name'],
        )
        data = {'message': 'location cateogry updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_icustomer_list(request):
    values = ICustomer.objects.filter(is_active=True).order_by('user_profile__user__first_name').values_list('id',
                                                                                                             'user_profile__user__first_name',
                                                                                                             'user_profile__mobile',
                                                                                                             'user_profile__gender__name',
                                                                                                             'user_profile',
                                                                                                             'user_profile__taluk__name',
                                                                                                             'user_profile__district__name',
                                                                                                             'customer_code',
                                                                                                             'customer_type',
                                                                                                             'business',
                                                                                                             'aadhar_number',
                                                                                                             'customer_type__name',
                                                                                                             'user_profile__pincode',
                                                                                                             'business__code',
                                                                                                             'business__business_type__name',
                                                                                                             'business__zone__name')
    columns = ['id', 'name', 'mobile', 'gender', 'user_profile', 'taluk', 'district', 'customer_code_id',
               'customer_type_id', 'business_id', 'aadhar_number', 'customer_type', 'pincode', 'booth_code',
               'booth_type', 'booth_zone']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna(0)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_session(request):
    values = Session.objects.filter().values_list('id', 'name')
    columns = ['id', 'name']
    route_df = pd.DataFrame(list(values), columns=columns)
    data = route_df.to_dict('r')


@api_view(['GET'])
def serve_ex_employee_union_dict(request):
    data_dict = {}
    ex_employee_values = UnionForIcustomer.objects.filter().exclude(id__in=[2, 6]).values_list('id', 'name')
    ex_employee_columns = ['id', 'name']
    ex_employee_df = pd.DataFrame(list(ex_employee_values), columns=ex_employee_columns)
    ex_employee_data = ex_employee_df.to_dict('r')
    print(ex_employee_df)

    employee_values = UnionForIcustomer.objects.filter(id__in=[2, 6]).values_list('id', 'name')
    employee_columns = ['id', 'name']
    employee_df = pd.DataFrame(list(employee_values), columns=employee_columns)
    employee_data = employee_df.to_dict('r')

    data_dict["3"] = employee_data
    data_dict["2"] = ex_employee_data
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_customer_type(request):
    values = ICustomerType.objects.all().order_by('name').values_list('id', 'name')
    columns = ['id', 'name', ]
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_business_last_sale(request):
    print('serve last sale')
    print(request.data)
    data = {'business_details': {}, 'last_order': {}}
    business_code = request.data['business_code']
    business = Business.objects.get(code=business_code)
    if not Business.objects.filter(code=business_code).exists():
        data = {'error_message': 'Booth not available'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data['business_details']['business_id'] = business.id
        data['business_details']['business_name'] = business.name
        agent = BusinessAgentMap.objects.get(business=business, is_active=True).agent
        data['business_details']['agent_id'] = agent.id
        data['business_details']['agent_wallet'] = AgentWallet.objects.get(agent_id=agent.id).current_balance
        data['business_details']['agent_first_name'] = agent.first_name
        data['business_details']['agent_last_name'] = agent.last_name
        data['business_details']['agent_phone'] = agent.agent_profile.mobile

    # check last sale
    if SaleGroup.objects.filter(business=business).exists():
        print('SALE ALREADY EXISTS')
        # make dict for last sale
        products = Product.objects.filter(is_active=True)
        sessions = Session.objects.filter()
        last_order_date = SaleGroup.objects.filter().order_by('-id')[0].date
        for session in sessions:
            data['last_order'][session.id] = {}
            for product in products:
                if Sale.objects.filter(product=product, sale_group__session=session, sale_group__date=last_order_date,
                                       sale_group__business=business).exists():
                    print('product available')
                    quantity = Sale.objects.get(product=product, sale_group__session=session,
                                                sale_group__date=last_order_date, sale_group__business=business).count
                    price = Decimal(quantity) * serve_business_type_wise_product_price_local(business.id, product.id)
                    data['last_order'][session.id][product.id] = {
                        'price': price,
                        'quantity': quantity
                    }
                else:
                    print('product not available')
                    data['last_order'][session.id][product.id] = {'price': 0, 'quantity': 0}
    else:
        print('sale not exits')
        # make fresh dict for last order
        products = Product.objects.filter(is_active=True)
        sessions = Session.objects.filter()
        for session in sessions:
            data['last_order'][session.id] = {}
            for product in products:
                data['last_order'][session.id][product.id] = {'price': 0, 'quantity': 0}
    return Response(data=data, status=status.HTTP_200_OK)


# @permission_classes((AllowAny, ))
# def remove_business_from_route(request):
#     print(request.data)
#     route_id = request.data['route_id']
#     RouteBusinessMap.objects.filter(
#         route_id=route_id,
#         business_id=request.data['business_id']
#     ).delete()
#     data = {'message': 'Business removed from route'}
#     return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_icustomer(request):
    print('saving icustomer')
    print(request.data)
    if request.data['id'] is None:  # save customer
        if UserProfile.objects.filter(mobile=request.data['mobile']).exists():
            print('exists')
            data = {'message': 'Mobile number already registed'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            last_count = IcustomerIdBank.objects.get(id=1).last_count
            prefix = int(last_count)
            print(prefix)
            last_customer_code = ICustomer.objects.filter().order_by('-id')[0].customer_code
            updated_code = 'CBE' + str(prefix)
            if last_customer_code[:3] != 'CBE':
                updated_code = 'EXEMP' + str(prefix)
            print('hi..........................', updated_code)
            not_exists = True
            while (not_exists):
                print(updated_code)
                if ICustomer.objects.filter(customer_code=updated_code).exists():
                    prefix = prefix + 1
                    print(prefix)
                    if request.data['customer_type_id'] == '2':
                        updated_code = 'EXEMP' + str(prefix)
                    else:
                        updated_code = 'CBE' + str(prefix)
                    print('if')
                else:
                    not_exists = False
                    print('else')

            random_password = randint(100000, 999999)
            user_obj = User(
                username=updated_code,
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                password=make_password(1234)
            )
            user_obj.save()
            user_profile_obj = UserProfile(
                union_id=request.data['union_id'],
                user=user_obj,
                user_type_id=3,
                gender_id=request.data['gender_id'],
                taluk_id=request.data['taluk_id'],
                district_id=request.data['district_id'],
                state_id=request.data['state_id'],
                mobile=request.data['mobile'],
            )

            if request.data['street'] != None:
                user_profile_obj.street = request.data['street']

            if request.data['alternate_mobile'] != None:
                user_profile_obj.alternate_mobile = request.data['alternate_mobile']

            if request.data['pincode'] != None:
                user_profile_obj.pincode = request.data['pincode']

            if request.data['icustomer_image'] != None:
                if 'changingThisBreaksApplicationSecurity' in request.data['icustomer_image']:
                    user_profile_obj.image = decode_image(
                        request.data['icustomer_image']['changingThisBreaksApplicationSecurity'])
                else:
                    user_profile_obj.image = decode_image(request.data['icustomer_image'])

            user_profile_obj.save()

            icustomer_obj = ICustomer(user_profile=user_profile_obj,
                                      customer_code=updated_code,
                                      customer_type_id=request.data['customer_type_id'],
                                      business_id=request.data['business_id'],
                                      aadhar_number=request.data['aadhar_number'],
                                      union_for_icustomer_id=request.data['union_for_icustomer_id']
                                      )

            icustomer_obj.save()
            if request.data['customer_type_id'] == '2':
                IcustomerProductMap.objects.create(
                    icustomer=icustomer_obj,
                    product_id=request.data['product_id']
                )
            icustomer_wallet_obj = ICustomerWallet(
                customer=icustomer_obj
            )
            icustomer_wallet_obj.save()
            IcustomerIdBank.objects.filter(id=1).update(last_count=str(prefix))
            data = {'message': 'Icustomer registed successfully'}
        return Response(data, status=status.HTTP_200_OK)
    else:
        print('----------------Updating Part-------------------')
        user_id = ICustomer.objects.get(id=request.data['id']).user_profile.user.id
        icustomer_obj = ICustomer.objects.get(id=request.data['id'])
        User.objects.filter(id=user_id).update(
            first_name=request.data['first_name'],
            last_name=request.data['last_name']
        )
        UserProfile.objects.filter(user_id=user_id).update(
            union_id=request.data['union_id'],
            user_id=user_id,
            gender_id=request.data['gender_id'],
            taluk_id=request.data['taluk_id'],
            district_id=request.data['district_id'],
            state_id=request.data['state_id'],
            mobile=request.data['mobile'],
        )
        if request.data['customer_type_id'] == '2':
            if IcustomerProductMap.objects.filter(icustomer_id=request.data['id']).exists():
                IcustomerProductMap.objects.filter(icustomer_id=request.data['id']).update(
                    product_id=request.data['product_id']
                )
            else:
                IcustomerProductMap.objects.create(icustomer=icustomer_obj, product_id=request.data['product_id'])
            # IcustomerProductMap.objects.create(
            #         icustomer=icustomer_obj,
            #         product_id = request.data['product_id']
            #     )

        user_profile_obj = UserProfile.objects.get(user_id=user_id)
        if request.data['street'] != None:
            user_profile_obj.street = request.data['street']

        if request.data['alternate_mobile'] != None:
            user_profile_obj.alternate_mobile = request.data['alternate_mobile']

        if request.data['pincode'] != None:
            user_profile_obj.pincode = request.data['pincode']

        if request.data['icustomer_image'] != None:
            if 'changingThisBreaksApplicationSecurity' in request.data['icustomer_image']:
                user_profile_obj.image = decode_image(
                    request.data['icustomer_image']['changingThisBreaksApplicationSecurity'])
            else:
                user_profile_obj.image = decode_image(request.data['icustomer_image'])

        user_profile_obj.save()

        ICustomer.objects.filter(id=request.data['id']).update(
            customer_type_id=request.data['customer_type_id'],
            business_id=request.data['business_id'],
            user_profile=UserProfile.objects.get(user_id=user_id),
            aadhar_number=request.data['aadhar_number']
        )

        if request.data['customer_type_id'] == '2':
            print('employee to ex-employee change area')
            if ICustomer.objects.filter(id=request.data['id']).exists():
                customer_code = ICustomer.objects.get(id=request.data['id']).customer_code
                print('coimming inside if --------------> ', customer_code)
                if customer_code[:3] == 'CBE':
                    customer_code = 'EXEMP' + customer_code[3:]
                ICustomer.objects.filter(id=request.data['id']).update(customer_code=customer_code)

        icustomer_obj = ICustomer.objects.get(id=request.data['id'])
        if request.data['aadhar_number'] != None:
            icustomer_obj.image = request.data['aadhar_number']
        icustomer_obj.save()
        data = {'message': 'Icustomer updated successfully'}
        return Response(data, status=status.HTTP_200_OK)


def serve_product__and_session_list_for_customer(user_profile_id):
    icustomer_obj = ICustomer.objects.get(user_profile_id=user_profile_id)
    icustomer_type_id = icustomer_obj.customer_type.id
    icustomer_id = icustomer_obj.id
    old_employee_product_list = list(
        IcustomerProductMap.objects.filter(icustomer_id=icustomer_id, product__is_active=True,product_id__in=[1,2,3]).values_list('product_id',
                                                                                                           flat=True))
    product_obj = ICustomerTypeWiseProductDiscount.objects.filter(customer_type_id=icustomer_type_id,
                                                                  product__is_active=True,product_id__in=[1,2,3,33,34]).order_by(
        'product__display_ordinal')
    product_obj_list = list(
        product_obj.values_list('product_id', 'product__group', 'product__group__name',
                                'product__name', 'product__short_name', 'product__code',
                                'product__unit',
                                'product__unit__display_name', 'product__description',
                                'product__quantity', 'discounted_price', 'product__gst_percent', 'product__color'))
    product_obj_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name',
                          'product_short_name',
                          'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity',
                          'product_mrp',
                          'gst_percent', 'color']
    product_df = pd.DataFrame(product_obj_list, columns=product_obj_column)
    session_obj = Session.objects.filter().order_by('id')
    session_list = list(session_obj.values_list('id', 'name', 'display_name', 'expiry_day_before', 'expiry_time'))
    session_column = ['id', 'name', 'display_name', 'expiry_day_before', 'expiry_time']
    session_df = pd.DataFrame(session_list, columns=session_column)
    milk_limit = ICustomerType.objects.get(id=icustomer_type_id).milk_limit
    order_expiry_date_obj = ICustomerOrderEndDateMonthWise.objects.all()
    order_expiry_date_list = list(order_expiry_date_obj.values_list('id', 'month', 'date'))
    order_expiry_date_column = ['id', 'month', 'date']
    order_expiry_date_df = pd.DataFrame(order_expiry_date_list, columns=order_expiry_date_column)
    pincode = UserProfile.objects.get(id=user_profile_id).pincode
    data_dict = {
        'product_list': product_df.to_dict('r'),
        'session_list': session_df.to_dict('r'),
        'milk_limit': milk_limit,
        'old_employee_product_list': old_employee_product_list,
        'icustomer_type_id': icustomer_type_id,
        'order_expiry_date': order_expiry_date_df.groupby('month').apply(lambda x: x.to_dict('r')[0]).to_dict(),
        'pincode': pincode
    }
    return data_dict


@api_view(['POST'])
def serve_product_list_for_customer(request):
    print(request.data)
    if request.data['from'] == 'portal':
        user_profile_id = ICustomer.objects.get(id=request.data['icustomer_id']).user_profile.id
        data_dict = serve_product__and_session_list_for_customer(user_profile_id)
        data_dict['product_availability'] = serve_product_availability()
        data_dict['wallet_balance'] = ICustomerWallet.objects.get(
            customer_id=request.data['icustomer_id']).current_balance
    elif request.data['from'] == 'mobile' or request.data['from'] == 'website':
        data_dict = serve_product__and_session_list_for_customer(request.user.userprofile.id)
        data_dict['product_availability'] = serve_product_availability()
        data_dict['wallet_balance'] = ICustomerWallet.objects.get(
            customer__user_profile__user_id=request.user.id).current_balance
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_last_month_order_for_icustomer(request):
    data_dict = {}
    if request.data['from'] == 'portal':
        icustomer_id = request.data['icustomer_id']
        icustomer_obj = ICustomer.objects.get(id=icustomer_id)
    elif request.data['from'] == 'mobile' or request.data['from'] == 'website':
        icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
        icustomer_obj = ICustomer.objects.get(user_profile_id=request.user.userprofile.id)

    user_pincode = icustomer_obj.user_profile.pincode
    user_profile_id = icustomer_obj.user_profile_id
    business_id = icustomer_obj.business_id
    if icustomer_obj.is_business_approved is False:
        data_dict['is_business_approved'] = False
    else:
        data_dict['is_business_approved'] = True
    if ICustomerSaleGroup.objects.filter(icustomer_id=icustomer_id).exists():
        last_date = ICustomerSaleGroup.objects.filter(icustomer_id=icustomer_id).order_by('-date')[0].date
        print(last_date)
        # last_date = last_date + datetime.timedelta(days=1)
        # sale_group_ids = list(
        #     SaleGroup.objects.filter(date=last_date, icustomer_id=icustomer_id).values_list('id', flat=True))
        # sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids)
        # sale_list = list(sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__icustomer_id',
        #                                       'sale_group__date', 'sale_group__session',
        #                                       'sale_group__session__display_name', 'sale_group__ordered_via',
        #                                       'sale_group__ordered_via__name', 'sale_group__sale_type',
        #                                       'sale_group__sale_type__name', 'sale_group__payment_status__name',
        #                                       'sale_group__sale_status__name', 'sale_group__total_cost', 'product',
        #                                       'product__name', 'count', 'cost'))
        # sale_column = ['sale_id', 'sale_group_id', 'business_id', 'icustomer_id', 'date', 'session_id', 'session_name',
        #                'ordered_via_id', 'ordered_via_name', 'sale_type_id', 'sale_type_name', 'payment_status',
        #                'sale_status',
        #                'session_wise_price', 'product_id', 'product_name', 'quantity', 'product_cost']
        # sale_df = pd.DataFrame(sale_list, columns=sale_column)
        # sale_df['date'] = sale_df['date'].astype(str)
        # master_dict = defaultdict(dict)
        # master_dict['product'] = {}
        # master_dict['total_price_per_product'] = {}
        # master_dict['total_price_per_session'] = {}
        # master_dict['total_price_per_date'] = 0
        # product_availability = serve_product_availability()
        # for row_index, row in sale_df.iterrows():
        #     if row['session_id'] not in master_dict['product']:
        #         master_dict['product'][row['session_id']] = {}
        #     if row['product_id'] not in master_dict['product'][row['session_id']]:
        #         if product_availability[row['session_id']][row['product_id']]:
        #             master_dict['product'][row['session_id']][row['product_id']] = {
        #                 'quantity': row['quantity'],
        #                 'price': row['product_cost']
        #             }
        #     if row['product_id'] not in master_dict['total_price_per_product']:
        #         master_dict['total_price_per_product'][row['product_id']] = 0
        #     if row['session_id'] not in master_dict['total_price_per_session']:
        #         master_dict['total_price_per_session'][row['session_id']] = 0
        #     if product_availability[row['session_id']][row['product_id']]:
        #         master_dict['total_price_per_product'][row['product_id']] += row['product_cost']
        #         master_dict['total_price_per_session'][row['session_id']] += row['product_cost']
        #         master_dict['total_quantity_per_session'][row['session_id']] += row['quantity']
        #     master_dict['total_price_per_date'] += row['product_cost']
        data_dict['is_exists'] = True
        data_dict['next_date_from_last_date'] = last_date
        # data_dict['last_date_product_data'] = master_dict
        data_dict['pincode'] = user_pincode
        data_dict['user_profile_id'] = user_profile_id
        data_dict['aadhar_number'] = icustomer_obj.aadhar_number
        data_dict['address'] = icustomer_obj.user_profile.street
        data_dict['is_aadhar_verified'] = icustomer_obj.is_aadhar_number_verified_by_customer
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict['is_exists'] = False
        data_dict['pincode'] = user_pincode
        data_dict['user_profile_id'] = user_profile_id
        data_dict['aadhar_number'] = icustomer_obj.aadhar_number
        data_dict['address'] = icustomer_obj.user_profile.street
        data_dict['is_aadhar_verified'] = icustomer_obj.is_aadhar_number_verified_by_customer
        return Response(data=data_dict, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
def register_order_for_icustomer(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        if request.data['from'] == 'portal':
            icustomer_id = request.data['icustomer_id']
            business_id = ICustomer.objects.get(id=icustomer_id).business_id
            user_profile_id = ICustomer.objects.get(id=icustomer_id).user_profile.id
            user_id = ICustomer.objects.get(id=icustomer_id).user_profile.user.id
            via_id = 2
        elif request.data['from'] == 'mobile':
            icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
            business_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).business_id
            user_profile_id = request.user.userprofile.id
            user_id = request.user.id
            via_id = 1
        elif request.data['from'] == 'website':
            icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
            business_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).business_id
            user_profile_id = request.user.userprofile.id
            user_id = request.user.id
            via_id = 3
        business_obj = Business.objects.get(id=business_id)
        data_dict = serve_product__and_session_list_for_customer(user_profile_id)
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        date = str(request.data['month_start_date'])
        # date = '2020-03-01'
        month = datetime.datetime.strptime(date, '%Y-%m-%d').month
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        if month == datetime.datetime.now().month:
            return Response(status=status.HTTP_409_CONFLICT)
        product_dict = {}
        product_dict[1] = {}
        product_dict[2] = {}
        product_in_string = ''
        product_form_details = request.data['product_form_data']
        total_amount = 0
        customer_wallet_obj = ICustomerWallet.objects.get(customer_id=icustomer_id)
        is_wallet_used_for_order = False
        expected_current_balance_after_order = customer_wallet_obj.current_balance - Decimal(request.data['final_customer_wallet'])
        print(expected_current_balance_after_order)
        if expected_current_balance_after_order > 0:
            is_wallet_used_for_order = True
        for session in session_list:
            if not ICustomerSaleGroup.objects.filter(date=date, session_id=session['id'],
                                                    icustomer_id=icustomer_id).exists():
                route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                        route__session_id=session['id']).route_id
                vehicle_obj = RouteVehicleMap.objects.get(route_id=route_id).vehicle
                total_cost_per_session = 0
                total_cost_per_session_for_month = 0
                if product_form_details['total_quantity_per_session'][str(session['id'])] != 0:
                    sale_group_obj = ICustomerSaleGroup(
                        business_id=business_id,
                        icustomer_id=icustomer_id,
                        date=date,
                        session_id=session['id'],
                        ordered_via_id=via_id,
                        payment_status_id=1,  # paid
                        sale_status_id=1,  # ordered
                        total_cost=0,
                        total_cost_for_month=0,
                        ordered_by=request.user,
                        modified_by=request.user,
                        product_amount=0,
                        route_id=route_id,
                        zone_id=business_obj.zone.id
                    )
                    sale_group_obj.save()
                    # print('sale group saved')
                    for product in product_list:
                        product_quantity = \
                            product_form_details['product'][str(session['id'])][str(product['product_id'])][
                                'quantity']
                        if product_quantity != 0 and product_quantity != None:
                            sale_obj = ICustomerSale(
                                icustomer_sale_group_id=sale_group_obj.id,
                                product_id=product['product_id'],
                                count=product_quantity,
                                cost=product_quantity * product['product_mrp'],
                                cost_for_month=product_quantity * product['product_mrp'] * request.data[
                                    'total_days_in_month'],
                                ordered_by=request.user,
                                modified_by=request.user
                            )
                            sale_obj.save()
                            product_in_string += str(product['product_short_name']) + '-' + str(
                                product_quantity) + 'pkt' + '-' + str(session['display_name']) + ','
                            product_dict[session['id']][product['product_id']] = product_quantity
                            # print('new sale created')
                            total_cost_per_session += product_quantity * product['product_mrp']
                            total_cost_per_session_for_month += product_quantity * product['product_mrp'] * request.data[
                                'total_days_in_month']
                    # saved_sale_group_obj = SaleGroup.objects.get(id=sale_group_obj.id)
                    sale_group_obj.total_cost = total_cost_per_session
                    sale_group_obj.total_cost_for_month = total_cost_per_session_for_month
                    sale_group_obj.product_amount = total_cost_per_session
                    sale_group_obj.save()
                    total_amount += total_cost_per_session_for_month
                    # print('sale group price updated')
                    if request.data['from'] == 'portal':
                        # Adding the saved salegroup to the counter based on the employee who login to that counter
                        employee_id = Employee.objects.get(user_profile__user=request.user).id
                        if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                collection_date=datetime.datetime.now()).exists():
                            counter_employee_trace_obj = \
                            CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                collection_date=datetime.datetime.now())[0]
                            if CounterEmployeeTraceSaleGroupMap.objects.filter(
                                    counter_employee_trace_id=counter_employee_trace_obj.id).exists():
                                counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                                    counter_employee_trace_id=counter_employee_trace_obj.id)
                                counter_sale_group_obj.icustomer_sale_group.add(sale_group_obj.id)
                                counter_sale_group_obj.save()
                            else:
                                counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap(
                                    counter_employee_trace_id=counter_employee_trace_obj.id)
                                counter_sale_group_obj.save()
                                counter_sale_group_obj.icustomer_sale_group.add(sale_group_obj.id)
                                counter_sale_group_obj.save()
                    if product_form_details['total_price_per_session'][
                        str(session['id'])] == total_cost_per_session:
                        print('session price is equal')
                    else:
                        print('session price not equal')
                        transaction.savepoint_rollback(sid)
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                    # map with monthly agent transaction
                    if ICustomerMonthlyOrderTransaction.objects.filter(icustomer_id=icustomer_id,
                                                                    month=date_in_format.month,
                                                                    year=date_in_format.year).exists():
                        icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction.objects.get(
                            icustomer_id=icustomer_id, month=date_in_format.month, year=date_in_format.year)
                        is_date_available = True
                    else:
                        icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction(icustomer_id=icustomer_id,
                                                                                    month=date_in_format.month,
                                                                                    year=date_in_format.year,
                                                                                    transacted_date_time=datetime.datetime.now(),
                                                                                    total_cost=0,
                                                                                    created_by_id=request.user.id,
                                                                                    milk_card_number=0)
                        icustomer_monthly_order_obj.save()
                        is_date_available = False

                    icustomer_monthly_order_obj.total_cost += sale_group_obj.total_cost_for_month
                    icustomer_monthly_order_obj.icustomer_sale_group.add(sale_group_obj.id)
                    icustomer_milk_card_id_bank_obj = ICustomerMilkCarkNumberIdBank.objects.get(id=1)
                    if is_date_available:
                        last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number
                    else:
                        last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number + 1
                    icustomer_monthly_order_obj.milk_card_number = str(last_count).zfill(6)
                    icustomer_monthly_order_obj.save()
                    # update_last_count_in_id_bank
                    icustomer_milk_card_id_bank_obj.last_milk_card_number = last_count
                    icustomer_milk_card_id_bank_obj.save()

                    # check wheather wallet used for order and add the used amount in ICustomerWalletAmoutForOrder table
                    if is_wallet_used_for_order:
                        if ICustomerWalletAmoutForOrder.objects.filter(icustomer_id=icustomer_id,month=date_in_format.month,year=date_in_format.year).exists():
                            icustomer_waller_amount_for_order_obj = ICustomerWalletAmoutForOrder.objects.get(icustomer_id=icustomer_id,month=date_in_format.month,year=date_in_format.year)
                        else:
                            icustomer_waller_amount_for_order_obj = ICustomerWalletAmoutForOrder(icustomer_id=icustomer_id,month=date_in_format.month,year=date_in_format.year, wallet_amount=0)
                            icustomer_waller_amount_for_order_obj.save()

                        icustomer_waller_amount_for_order_obj.icustomer_sale_group.add(sale_group_obj.id)
                        icustomer_waller_amount_for_order_obj.save()
        if is_wallet_used_for_order:
            icustomer_waller_amount_for_order_obj.wallet_amount = expected_current_balance_after_order
            icustomer_waller_amount_for_order_obj.save()
        else:
            if ICustomerWalletAmoutForOrder.objects.filter(icustomer_id=icustomer_id,month=date_in_format.month,year=date_in_format.year).exists(): 
                ICustomerWalletAmoutForOrder.objects.get(icustomer_id=icustomer_id,month=date_in_format.month,year=date_in_format.year).delete()
        # sending confirmation message to customer
        icustomer_obj = ICustomer.objects.get(id=icustomer_id)
        customer_first_name = icustomer_obj.user_profile.user.first_name
        current_date_time = datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%p")
        # counter_name = counter_employee_trace_obj.counter.name
        amount = total_amount
        milk_card_number = icustomer_monthly_order_obj.milk_card_number
        customer_code = icustomer_obj.customer_code
        business_code = Business.objects.get(id=business_id).code
        # message = 'Dear ' + str(customer_first_name) + '(' + str(customer_code)+ ')' + ', you have successfully subscribed milk for the month of  ' +str(months_in_english[date_in_format.month]) + ' Milk Card No : ' + str(milk_card_number) + ' Booked on ' + str(current_date_time) + ' @ ' + str(counter_name) + ' counter totalling ' + str(amount) + ' Rs. Items:' + str(product_in_string)
        message = str(customer_first_name) + '(' + str(customer_code) + ')' + ' subscribed milk for ' + str(
            months_in_english[date_in_format.month]) + '.Booth- ' + str(business_code) + ' Card No :' + str(
            milk_card_number) + ' Rs. ' + str(amount) + str(product_in_string)
        purpose = 'Confirmation message to customer'
        payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey': '622de6e4-91da-4e3b-9fb1-2262df7baff8',
                'SenderID': 'AAVINC', 'fl': '0', 'gwid': '2', 'sid': 'AAVINC'}
        headers = {}
        url = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'

        payload['msg'] = message
        payload['msisdn'] = icustomer_obj.user_profile.mobile
        if not str(icustomer_obj.user_profile.mobile)[0:5] == '99999':
            try:
                res = requests.post(url, data=payload, headers=headers)
            except Exception as e:
                print(e)
                pass
            try:
                template_id = BsnlSmsTemplate.objects.filter(message_name='register_order_for_icustomer').first().template_id
                template_list = [
                                {'Key': 'name', 'Value': str(customer_first_name)},
                                {'Key': 'customer_code', 'Value': str(customer_code)},
                                {'Key': 'month', 'Value': str(months_in_english[date_in_format.month])},
                                {'Key': 'booth', 'Value': str(business_code)},
                                {'Key': 'card_no', 'Value': str(milk_card_number)},
                                {'Key': 'amount', 'Value': str(amount)},
                                {'Key': 'product_in_string', 'Value': str(product_in_string)}
                                ]
                send_message_from_bsnl(template_id, template_list, icustomer_obj.user_profile.mobile)
            except Exception as e:
                print(e)
        # send_message(icustomer_obj.user_profile.mobile, message, purpose, request.user.id)

        for date_count in range(1, int(request.data['total_days_in_month']) + 1):
            date = date[:7] + '-' + str(date_count)
            for session in session_list:
                route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                        route__session_id=session['id']).route_id
                vehicle_obj = RouteVehicleMap.objects.get(route_id=route_id).vehicle
                for product in product_list:
                    if product['product_id'] in product_dict[session['id']].keys():
                        if RouteTrace.objects.filter(date=date, session_id=session['id'], route_id=route_id).exists():
                            route_trace_obj = RouteTrace.objects.get(date=date, session_id=session['id'], route_id=route_id)
                            if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id,
                                                                        product_id=product['product_id']).exists():
                                route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(
                                    route_trace_id=route_trace_obj.id, product_id=product['product_id'])
                                route_trace_sale_summary_obj.quantity += product_dict[session['id']][product['product_id']]
                                route_trace_sale_summary_obj.save()
                            else:
                                route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id,
                                                                                        product_id=product['product_id'],
                                                                                        quantity=
                                                                                        product_dict[session['id']][
                                                                                            product['product_id']])
                                route_trace_sale_summary_obj.save()
                        else:
                            route_trace_obj = RouteTrace(indent_status_id=1,  # initiated
                                                        route_id=route_id,
                                                        vehicle_id=vehicle_obj.id,
                                                        date=date,
                                                        session_id=session['id'],
                                                        driver_name=vehicle_obj.driver_name,
                                                        driver_phone=vehicle_obj.driver_mobile)
                            route_trace_obj.save()
                            route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id,
                                                                                    product_id=product['product_id'],
                                                                                    quantity=product_dict[session['id']][
                                                                                        product['product_id']])
                            route_trace_sale_summary_obj.save()
                            if OverallIndentPerSession.objects.filter(date=date, session_id=session['id']).exists():
                                overall_route_trace_obj = OverallIndentPerSession.objects.get(date=date,
                                                                                            session_id=session['id'])
                                overall_route_trace_obj.route_trace.add(route_trace_obj)
                                overall_route_trace_obj.save()
                            else:
                                overall_route_trace_obj = OverallIndentPerSession(date=date,
                                                                                session_id=session['id'],
                                                                                overall_indent_status_id=1,
                                                                                created_by_id=1)  # aavin
                                overall_route_trace_obj.save()
                                overall_route_trace_obj.route_trace.add(route_trace_obj)
                                overall_route_trace_obj.save()
        if ICustomerCardSerialNumberIdBank.objects.filter(business_id=business_id, month=date_in_format.month,
                                                        year=date_in_format.year).exists():
            icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank.objects.get(business_id=business_id,
                                                                                    month=date_in_format.month,
                                                                                    year=date_in_format.year)
        else:
            icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank(business_id=business_id,
                                                                        month=date_in_format.month,
                                                                        year=date_in_format.year, counter_last_count=0,
                                                                        online_last_count=0)
            icustomer_serial_bank_id_obj.save()

        icustomer_serial_number_map = ICustomerSerialNumberMap(icustomer_id=icustomer_id, business_id=business_id,
                                                            month=date_in_format.month, year=date_in_format.year)
        serial_number = icustomer_serial_bank_id_obj.counter_last_count + 1
        icustomer_serial_number_map.serial_number = serial_number
        icustomer_serial_number_map.save()
        # update serail number in ID bank
        icustomer_serial_bank_id_obj.counter_last_count = serial_number
        icustomer_serial_bank_id_obj.online_last_count = serial_number
        icustomer_serial_bank_id_obj.save()
        if request.data['from'] == 'portal':
            data_dict = generate_customer_card_after_order(icustomer_obj.customer_code, date_in_format.month,
                                                        date_in_format.year)
        if request.data['from'] == 'mobile':
            amount_that_customer_pay = product_form_details['total_price_per_order']
        else:
            amount_that_customer_pay = request.data['final_price']
        if amount_that_customer_pay != 0:
            transaction_obj = TransactionLog(
                date=datetime.datetime.now(),
                transacted_by_id=user_id,
                transacted_via_id=via_id,
                data_entered_by=request.user,
                amount=amount_that_customer_pay,
                transaction_direction_id=4,  # from icustomer to aavin
                transaction_mode_id=1,  # Upi
                transaction_id='1234',
                transaction_status_id=2,  # completed
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=customer_wallet_obj.current_balance,
                wallet_balance_after_transaction_approval=customer_wallet_obj.current_balance,
                description='Amount for ordering the product from Icustomer',
                modified_by=request.user
            )
            transaction_obj.save()
        if request.data['from'] == 'portal':
            transaction_mode = 2
        else:
            transaction_mode = 1
        if 'final_customer_wallet' in request.data:
            if request.data['final_customer_wallet'] < customer_wallet_obj.current_balance:
                transaction_obj = TransactionLog(
                    date=datetime.datetime.now(),
                    transacted_by_id=user_id,
                    transacted_via_id=1,
                    data_entered_by_id=user_id,
                    amount=customer_wallet_obj.current_balance - Decimal(request.data['final_customer_wallet']),
                    transaction_direction_id=5,  # from customer wallet to aavin
                    transaction_mode_id=transaction_mode,
                    transaction_status_id=2,  # completed
                    transaction_id='1234',
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=datetime.datetime.now(),
                    wallet_balance_before_this_transaction=customer_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=request.data['final_customer_wallet'],
                    description='Amount for ordering the product from customer wallet',
                    modified_by_id=user_id
                )
                transaction_obj.save()
                customer_wallet_obj.current_balance = request.data['final_customer_wallet']
                customer_wallet_obj.save()
        transaction.savepoint_commit(sid)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def serve_customer_business_details(request):
    if request.data['from'] == 'portal':
        business_id = ICustomer.objects.get(id=request.data['icustomer_id']).business_id
    else:
        business_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).business_id
    business_obj = BusinessAgentMap.objects.filter(business_id=business_id)
    business_list = list(
        business_obj.values_list('business_id', 'business__code', 'business__zone', 'business__zone__name',
                                 'business__name', 'business__constituency', 'business__constituency__name',
                                 'business__ward', 'business__ward__name', 'business__address',
                                 'business__location_category', 'business__location_category__name',
                                 'business__location_category_value', 'business__pincode', 'business__landmark',
                                 'business__working_hours_from', 'business__working_hours_to', 'business__latitude',
                                 'business__longitude', 'agent__first_name',
                                 'agent__last_name', 'agent__agent_profile__mobile'))
    business_column = ['business_id', 'code', 'zone_id', 'zone_name', 'name', 'constituency_id', 'constituency_name',
                       'ward_id', 'ward_name', 'address', 'location_category_id', 'location_category_name',
                       'location_category_value', 'pincode', 'landmark', 'working_hours_from', 'working_hours_to',
                       'latitude', 'longitude', 'agent_first_name', 'agent_last_name', 'agent_mobile_number']
    business_df = pd.DataFrame(business_list, columns=business_column)
    business_df['working_hours_from'] = business_df['working_hours_from'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    business_df['working_hours_to'] = business_df['working_hours_to'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    return Response(data=business_df.to_dict('r')[0], status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_icustomer_history_data_for_last_four_month(request):
    print(request.data)
    if request.data['from'] == "portal":
        icustomer_id = request.data['icustomer_id']
    elif request.data['from'] == "mobile":
        icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
    today = datetime.datetime.now()
    date_list = []
    if request.data['data_for'] == 'past':
        for count in range(0, 13):
            date = today - dateutil.relativedelta.relativedelta(months=count)
            if ICustomerSaleGroup.objects.filter(date__year=date.year, date__month=date.month,
                                                 icustomer_id=icustomer_id).exists():
                sale_group_count = ICustomerSaleGroup.objects.filter(date__year=date.year, date__month=date.month,
                                                                     icustomer_id=icustomer_id).aggregate(
                    Sum('total_cost_for_month'))
                order_date = ICustomerSaleGroup.objects.filter(date__year=date.year, date__month=date.month,
                                                               icustomer_id=icustomer_id)[0].time_created
                date_list.append({'month': date.month, 'year': date.year, 'sale_group_count': sale_group_count,
                                  'order_date': order_date})
    elif request.data['data_for'] == 'future':
        for count in range(0, 13):
            next_month_date = today.replace(day=1) + timedelta(days=32)
            date = next_month_date + dateutil.relativedelta.relativedelta(months=count)
            if ICustomerSaleGroup.objects.filter(date__year=date.year, date__month=date.month,
                                                 icustomer_id=icustomer_id).exists():
                sale_group_count = ICustomerSaleGroup.objects.filter(date__year=date.year, date__month=date.month,
                                                                     icustomer_id=icustomer_id).aggregate(
                    Sum('total_cost_for_month'))
                order_date = ICustomerSaleGroup.objects.filter(date__year=date.year, date__month=date.month,
                                                               icustomer_id=icustomer_id)[0].time_created
                date_list.append({'month': date.month, 'year': date.year, 'sale_group_count': sale_group_count,
                                  'order_date': order_date})

    return Response(data=date_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_icustomer_selected_month_sale_group(request):
    print(request.data)
    if request.data['from'] == 'portal':
        icustomer_id = request.data['icustomer_id']
    elif request.data['from'] == 'mobile' or request.data['from'] == 'website':
        icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
    icustomer_sale_group_ids = list(
        ICustomerSaleGroup.objects.filter(date=request.data['selected_date'], icustomer_id=icustomer_id).values_list(
            'id', flat=True))
    business_id = ICustomerSaleGroup.objects.get(id=icustomer_sale_group_ids[0]).business_id
    business_obj = BusinessAgentMap.objects.filter(business_id=business_id)
    business_list = list(
        business_obj.values_list('business_id', 'business__code', 'business__zone', 'business__zone__name',
                                 'business__name', 'business__constituency', 'business__constituency__name',
                                 'business__ward', 'business__ward__name', 'business__address',
                                 'business__location_category', 'business__location_category__name',
                                 'business__location_category_value', 'business__pincode', 'business__landmark',
                                 'business__working_hours_from', 'business__working_hours_to', 'business__latitude',
                                 'business__longitude', 'agent__first_name',
                                 'agent__last_name', 'agent__agent_profile__mobile'))
    business_column = ['business_id', 'code', 'zone_id', 'zone_name', 'name', 'constituency_id', 'constituency_name',
                       'ward_id', 'ward_name', 'address', 'location_category_id', 'location_category_name',
                       'location_category_value', 'pincode', 'landmark', 'working_hours_from', 'working_hours_to',
                       'latitude', 'longitude', 'agent_first_name', 'agent_last_name', 'agent_mobile_number']
    business_df = pd.DataFrame(business_list, columns=business_column)
    business_df['working_hours_from'] = business_df['working_hours_from'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    business_df['working_hours_to'] = business_df['working_hours_to'].apply(lambda x: x.strftime("%I:%M:%S %p"))
    icuctomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group_id__in=icustomer_sale_group_ids,
                                                      product__is_active=True)
    icuctomer_sale_list = list(
        icuctomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__icustomer_id',
                                       'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                       'icustomer_sale_group__session__display_name',
                                       'icustomer_sale_group__ordered_via',
                                       'icustomer_sale_group__ordered_via__name',
                                       'icustomer_sale_group__payment_status__name',
                                       'icustomer_sale_group__sale_status__name', 'icustomer_sale_group__total_cost',
                                       'product',
                                       'product__name', 'count', 'cost'))
    icuctomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'icustomer_id', 'date', 'session_id',
                             'session_name',
                             'ordered_via_id', 'ordered_via_name', 'payment_status',
                             'sale_status',
                             'session_wise_price', 'product_id', 'product_name', 'quantity', 'product_cost']
    icuctomer_sale_df = pd.DataFrame(icuctomer_sale_list, columns=icuctomer_sale_column)
    icuctomer_sale_df['date'] = icuctomer_sale_df['date'].astype(str)
    master_dict = defaultdict(dict)
    master_dict['product'] = {}
    master_dict['business_details'] = business_df.to_dict('r')[0]
    master_dict['total_price_per_product'] = {}
    master_dict['total_price_per_session'] = {}
    master_dict['total_price_per_date'] = 0
    for row_index, row in icuctomer_sale_df.iterrows():
        if row['session_id'] not in master_dict['product']:
            master_dict['product'][row['session_id']] = {}
        if row['product_id'] not in master_dict['product'][row['session_id']]:
            master_dict['product'][row['session_id']][row['product_id']] = {
                'quantity': row['quantity'],
                'price': row['product_cost']
            }
        if row['product_id'] not in master_dict['total_price_per_product']:
            master_dict['total_price_per_product'][row['product_id']] = 0
        master_dict['total_price_per_product'][row['product_id']] += row['product_cost']
        if row['session_id'] not in master_dict['total_price_per_session']:
            master_dict['total_price_per_session'][row['session_id']] = 0
        master_dict['total_price_per_session'][row['session_id']] += row['product_cost']
        master_dict['total_price_per_date'] += row['product_cost']
    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_last_date_for_the_icustomer_order(request):
    icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
    business_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).business_id
    if ICustomerSaleGroup.objects.filter(icustomer_id=icustomer_id).exists():
        last_date = ICustomerSaleGroup.objects.filter(icustomer_id=icustomer_id).order_by('-date')[0].date
        data_dict = {
            'is_exists': True,
            'last_date': last_date,
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict = {
            'is_exists': False,
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_icustomer_details_for_update(request):
    icustomer_obj = ICustomer.objects.get(id=request.data['id'])
    user_profile = UserProfile.objects.get(id=icustomer_obj.user_profile.id)
    user_obj = User.objects.get(id=user_profile.user.id)
    icustomer_obj = ICustomer.objects.get(id=request.data['id'])

    data_dict = {
        'id': icustomer_obj.id,
        'customer_type_id': icustomer_obj.customer_type.id,
        'aadhar_number': icustomer_obj.aadhar_number,
        'union_id': user_profile.union.id,
        'user_type_id': user_profile.user_type.id,
        'street': user_profile.street,
        'gender_id': user_profile.gender.id,
        'taluk_id': user_profile.taluk.id,
        'district_id': user_profile.district.id,
        'state_id': user_profile.state.id,
        'mobile': user_profile.mobile,
        'alternate_mobile': user_profile.alternate_mobile,
        'pincode': user_profile.pincode,
        'username': user_obj.username,
        'first_name': user_obj.first_name,
        'last_name': user_obj.last_name,
        'union_for_icustomer': icustomer_obj.union_for_icustomer_id
    }
    if ICustomer.objects.get(id=request.data['id']).business != None:
        print('---is not none-----')
        data_dict['business_id'] = icustomer_obj.business.id

    if IcustomerProductMap.objects.filter(icustomer_id=request.data['id']).exists():
        data_dict['product_id'] = IcustomerProductMap.objects.get(icustomer_id=request.data['id']).product.id

    try:
        image_path = 'static/media/' + str(user_profile.image)
        # print(image_path)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data_dict['image'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_vehicle_type(request):
    values = VehicleType.objects.all().order_by('name').values_list('id', 'name')
    columns = ['id', 'name', ]
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_vehicle(request):
    values = Vehicle.objects.all().order_by('vehicle_transport__name').values_list('id', 'vehicle_transport__name',
                                                                                   'code', 'licence_number',
                                                                                   'driver_name', 'driver_mobile',
                                                                                   'vehicle_type__name',
                                                                                   'fc_expiry_date',
                                                                                   'insurance_expiry_date',
                                                                                   'fc_document', 'insurance_document',
                                                                                   'contract_start_from',
                                                                                   'contract_ends_on')
    columns = ['id', 'name', 'code', 'licence_number', 'driver_name', 'driver_mobile', 'vehicle_type_name',
               'fc_expiry_date', 'insurance_expiry_date', 'fc_document', 'insurance_document', 'contract_starts_from',
               'contract_ends_on']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna(0)
    for index, row in df.iterrows():
        try:
            image_path = 'static/media/' + str(row['fc_document'])
            # print(image_path)
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                df.at[index, 'fc_document'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
        except Exception as err:
            print(err)
        try:
            insurance_image_path = 'static/media/' + str(row['insurance_document'])
            # print(image_path)
            with open(insurance_image_path, 'rb') as image_file:
                insurance_encoded_image = b64encode(image_file.read())
                df.at[index, 'insurance_document'] = 'data:image/jpeg;base64,' + insurance_encoded_image.decode("utf-8")
        except Exception as err:
            print(err)
    data = df.to_dict('r')

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_vehicle(request):
    if request.data['id'] is None:
        random_code = randint(100000, 999999)
        if Vehicle.objects.filter(licence_number=request.data['licence_number']).exists():
            data = {'message': 'vehicle alrady registered'}
        else:
            vehicle_obj = Vehicle.objects.create(
                vehicle_transport_id=request.data['vehicle_transport_id'],
                code=random_code,
                licence_number=request.data['licence_number'],
                driver_name=request.data['driver_name'],
                driver_mobile=request.data['mobile'],
                capacity_in_kg=request.data['capacity_in_kg'],
                tray_capacity=request.data['tray_capacity'],
                vehicle_type_id=request.data['vehicle_type_id'],
                fc_expiry_date=request.data['fc_expiry_date'],
                insurance_expiry_date=request.data['insurance_expiry_date'],
                contract_start_from=request.data['contract_starts_from'],
                contract_ends_on=request.data['contract_ends_on']
            )

            if request.data['insurance_document'] != None:
                vehicle_obj.insurance_document = decode_image(request.data['insurance_document'])

            if request.data['fc_document'] != None:
                vehicle_obj.fc_document = decode_image(request.data['fc_document'])
            vehicle_obj.save()
            print('saved')
            data = {'message': 'vehicle registered successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)

    else:
        Vehicle.objects.filter(id=request.data['id']).update(
            vehicle_transport_id=request.data['vehicle_transport_id'],
            licence_number=request.data['licence_number'],
            driver_name=request.data['driver_name'],
            driver_mobile=request.data['mobile'],
            capacity_in_kg=request.data['capacity_in_kg'],
            tray_capacity=request.data['tray_capacity'],
            vehicle_type_id=request.data['vehicle_type_id'],
            contract_start_from=request.data['contract_starts_from'],
            contract_ends_on=request.data['contract_ends_on']
        )
        vehicle_obj = Vehicle.objects.get(id=request.data['id'])
        print(request.data['insurance_document'])

        if request.data['insurance_document'] != None:
            vehicle_obj.insurance_document = decode_image(request.data['insurance_document'])

        if request.data['fc_document'] != None:
            vehicle_obj.fc_document = decode_image(request.data['fc_document'])

        vehicle_obj.save()

        data = {'message': 'vehicle registered updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_vehicle_details_for_update(request):
    print(request.data)
    vehicle_obj = Vehicle.objects.get(id=request.data['id'])
    data_dict = {
        'id': vehicle_obj.id,
        'vehicle_transport_id': vehicle_obj.vehicle_transport.id,
        'code': vehicle_obj.code,
        'licence_number': vehicle_obj.licence_number,
        'vehicle_type_id': vehicle_obj.vehicle_type.id,
        'driver_name': vehicle_obj.driver_name,
        'driver_mobile': vehicle_obj.driver_mobile,
        'capacity_in_kg': vehicle_obj.capacity_in_kg,
        'tray_capacity': vehicle_obj.tray_capacity,
        'fc_expiry_date': vehicle_obj.fc_expiry_date,
        'insurance_expiry_date': vehicle_obj.insurance_expiry_date,
        'contract_starts_from': vehicle_obj.contract_start_from,
        'contract_ends_on': vehicle_obj.contract_ends_on,
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_route(request):
    values = Route.objects.filter(is_temp_route=False).order_by('name').values_list('id', 'name', 'union',
                                                                                    'union__name', 'session',
                                                                                    'session__name',
                                                                                    'order_expiry_time',
                                                                                    'departure_time')
    columns = ['id', 'name', 'union_id', 'union', 'session_id', 'session_name', 'order_expiry_time', 'departure_time']
    df = pd.DataFrame(list(values), columns=columns)

    route_vehicle_map = RouteVehicleMap.objects.all()
    route_vehicle_values = list(route_vehicle_map.values_list('id', 'route__id', 'vehicle__id'))
    route_vehicle_columns = ['route_vehicle_id', 'id', 'vehicle_id']
    route_vehicle_df = pd.DataFrame(route_vehicle_values, columns=route_vehicle_columns)
    final_df = pd.merge(df, route_vehicle_df, left_on="id", right_on='id', how='left')
    final_df = final_df.fillna(0)
    data = final_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_session(request):
    values = Session.objects.all().order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_route(request):
    if request.data['id'] is None:
        if not Route.objects.filter(name__iexact=request.data['name'], union_id=request.data['union_id'],
                                    session_id=request.data['session_id']).exists():
            route_obj = Route.objects.create(
                name=request.data['name'],
                union_id=request.data['union_id'],
                session_id=request.data['session_id'],
                order_expiry_time=request.data['order_expiry_time'],
                reference_order_expiry_time=request.data['order_expiry_time'],
                departure_time=request.data['departure_time']
            )
            temp_route_obj = Route.objects.create(
                name=request.data['name'] + '_temp',
                union_id=request.data['union_id'],
                session_id=request.data['session_id'],
                is_temp_route=True,
                order_expiry_time=request.data['order_expiry_time'],
                reference_order_expiry_time=request.data['order_expiry_time'],
                departure_time=request.data['departure_time']
            )

            RouteTempRouteMap.objects.create(main_route=route_obj, temp_route=temp_route_obj)
            if RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                              route__session_id=request.data['session_id']).exists():
                RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                               route__session_id=request.data['session_id']).delete()

            RouteVehicleMap.objects.create(
                route=route_obj,
                vehicle_id=request.data['vehicle_id']
            )

            RouteVehicleMap.objects.create(
                route=temp_route_obj,
                vehicle_id=53
            )

            data = {'message': 'route registered successfully!'}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {'message': 'route name already exists!'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    else:
        if not Route.objects.filter(name=request.data['name']).exclude(id=request.data['id']).exists():
            Route.objects.filter(id=request.data['id']).update(
                name=request.data['name'],
                union_id=request.data['union_id'],
                session_id=request.data['session_id'],
                order_expiry_time=request.data['order_expiry_time'],
                departure_time=request.data['departure_time']
            )
            if RouteTempRouteMap.objects.filter(main_route_id=request.data['id']).exists():
                temp_route_id = RouteTempRouteMap.objects.get(main_route_id=request.data['id']).temp_route.id
                Route.objects.filter(id=temp_route_id).update(
                    union_id=request.data['union_id'],
                    session_id=request.data['session_id'],
                    order_expiry_time=request.data['order_expiry_time'],
                    departure_time=request.data['departure_time']
                )
            route_obj = Route.objects.get(id=request.data['id'])
            if not RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                                  route_id=request.data['id']).exists():
                if RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                                  route__session_id=request.data['session_id']).exists():
                    RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                                   route__session_id=request.data['session_id']).delete()

                RouteVehicleMap.objects.create(
                    route=route_obj,
                    vehicle_id=request.data['vehicle_id']
                )

            data = {'message': 'route updated successfully!'}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {'message': 'route name already exists!'}
            return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_business_type_wise_product_price(request):
    print(request.data)
    business_code = request.data['business_code']
    business = Business.objects.get(code=business_code)
    values = BusinessTypeWiseProductDiscount.objects.filter(business_type=business.business_type,
                                                            product__is_active=True).values_list('product',
                                                                                                 'discounted_price')
    columns = ['product_id', 'price']
    df = pd.DataFrame(list(values), columns=columns)
    print(df)
    data = dict(zip(df['product_id'], df['price']))

    p_values = Product.objects.filter(is_active=True).exclude(id__in=df['product_id']).values_list('id', 'mrp')
    p_columns = ['product_id', 'mrp']
    p_df = pd.DataFrame(list(p_values), columns=p_columns)
    p_data = dict(zip(p_df['product_id'], p_df['mrp']))
    data = {**data, **p_data}
    return Response(data=data, status=status.HTTP_200_OK)


def serve_business_type_wise_product_price_local(business_id, product_id):
    business_type = Business.objects.get(id=business_id).business_type
    print('business_type.id = {}'.format(business_type.id))
    print('product_id = {}'.format(product_id))
    concession = BusinessProductConcessionMap.objects.get(business_type=business_type,
                                                          product_id=product_id).concession_type.name
    print('concession = {}'.format(concession))
    if concession == 'Commission':
        print('Product.objects.get(id=product_id).mrp = {}'.format(Product.objects.get(id=product_id).mrp))
        return Product.objects.get(id=product_id).mrp
    elif concession == 'Discount':
        print('business type id = {}'.format(business_type.id))
        if business_type.id in [1, 3, 5]:
            # print('discount price = {}'.format(BusinessTypeWiseProductDiscount.objects.get(product_id=product_id, business_type=business_type).discounted_price))
            return BusinessTypeWiseProductDiscount.objects.get(product_id=product_id,
                                                               business_type=business_type).discounted_price
        else:
            return BusinessWiseProductDiscount.objects.get(product_id=product_id,
                                                           business_id=business_id).discounted_price


@api_view(['POST'])
def place_agent_order(request):
    print(request.data)
    todate = datetime.datetime.now().date()
    business_id = request.data['business_id']
    order = request.data['order']
    order_date = datetime.datetime.strptime(request.data['order_date'], '%Y-%m-%d').date()
    print(order_date)
    for session_id, product in order.items():
        print('session id = {}'.format(session_id))
        print('business id = {}'.format(business_id))
        print('order date = {}'.format(order_date))
        print('date type = {}'.format(type(order_date)))
        if SaleGroup.objects.filter(date=order_date, session_id=session_id, business_id=business_id).exists():
            print('sale group already registered')
            data = {'error_message': 'Order registered already this date!'}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)

        print('sale group not existed')
        sale_group = SaleGroup.objects.create(
            date=order_date,
            session_id=session_id,
            business_id=business_id,
            ordered_via_id=2,  # via portal
            sale_type_id=2,  # to business
            total_cost=0,
            sale_status_id=1,
            ordered_by=request.user,
            modified_by=request.user,
            payment_status_id=1,
            product_amount=0
        )
        for product_id, order in product.items():
            if order['quantity'] != 0:
                # create sale group
                product_price = serve_business_type_wise_product_price_local(business_id, product_id)
                print('quantity = {}'.format(order['quantity']))
                print('quantity type = {}'.format(type(order['quantity'])))

                cost = product_price * int(order['quantity'])
                print('price = {}'.format(product_price))
                Sale.objects.create(
                    sale_group=sale_group,
                    product_id=product_id,
                    count=order['quantity'],
                    cost=cost,
                    ordered_by=request.user,
                    modified_by=request.user,
                )
                sale_group.total_cost += cost
                sale_group.product_amount += cost
                sale_group.save()
                print('sale group created')
        data = {'success_message': 'Order successfully registered'}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_order_expiry_time_by_business(request):
    data = defaultdict(dict)
    business_id = request.data['business_id']
    route_ids = RouteBusinessMap.objects.filter(business_id=business_id).values_list('id', flat=True)
    routes = Route.objects.filter(id__in=route_ids)
    for route in routes:
        data[route.session.id] = route.order_expiry_time
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_business_order_future_date(request):
    print(request.data)
    business_id = request.data['business_id']
    today = datetime.datetime.now().date()
    tomorrow = today + datetime.timedelta(days=1)
    if not SaleGroup.objects.filter(business_id=business_id).exists():
        data = {'future_date': tomorrow}
        return Response(data=data, status=status.HTTP_200_OK)

    last_sale_date = SaleGroup.objects.filter(business_id=business_id).order_by('-date')[0].date
    future_date = None
    if last_sale_date >= tomorrow:
        future_date = last_sale_date + datetime.timedelta(days=1)
        data = {'future_date': future_date}
    else:
        data = {'future_date': tomorrow.strftime('%m/%d/%Y')}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_products_for_agent_order(request):
    values = Product.objects.filter(is_active=True).order_by('display_ordinal').values_list('id', 'name', 'short_name')
    columns = ['id', 'name', 'short_name']
    route_df = pd.DataFrame(list(values), columns=columns)
    data = route_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_session(request):
    values = Session.objects.filter().order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    route_df = pd.DataFrame(list(values), columns=columns)
    data = route_df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_icustomer_wise_discount_price_dict(request):
    print('SOMETHING')
    data = {}
    icustomer_type_ids = [1, 2, 3, 5]
    values = ICustomerTypeWiseProductDiscount.objects.filter(customer_type_id__in=icustomer_type_ids,
                                                             product__is_active=True).values_list('customer_type_id',
                                                                                                  'customer_type__name',
                                                                                                  'product',
                                                                                                  'product__name',
                                                                                                  'discounted_price')
    columns = ['icustomer_type_id', 'icustomer_type_name', 'product_id', 'product_name', 'discounted_price']
    df = pd.DataFrame(list(values), columns=columns)
    print(df)
    if not df.empty:
        icustomer_ids = df['icustomer_type_id'].unique()
        for icustomer_id in icustomer_ids:
            filtered_df = df[df['icustomer_type_id'] == icustomer_id]
            data[str(icustomer_id)] = {}
            data[str(icustomer_id)] = dict(zip(filtered_df['product_id'], filtered_df['discounted_price']))
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_or_update_icustomer_type_wise_discount_price(request):
    print(request.data)
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    formatted_date = now_asia
    if ICustomerTypeWiseProductDiscount.objects.filter(customer_type_id=request.data['customer_type_id'],
                                                       product_id=request.data['product_id']).exists():
        obj = ICustomerTypeWiseProductDiscount.objects.get(customer_type_id=request.data['customer_type_id'],
                                                           product_id=request.data['product_id'])
        if ICustomerTypeWiseProductDiscountTrace.objects.filter(icustomer_type_wiser_product_discount_id=obj,
                                                                end_date__isnull=True).exists():
            customer_type_discount_obj = \
            ICustomerTypeWiseProductDiscountTrace.objects.filter(icustomer_type_wiser_product_discount=obj).order_by(
                '-time_created')[0]
            if Decimal(customer_type_discount_obj.discounted_price) != Decimal(request.data['discount_price']):
                ICustomerTypeWiseProductDiscountTrace.objects.filter(icustomer_type_wiser_product_discount=obj,
                                                                     end_date__isnull=True).update(
                    end_date=formatted_date,
                    product_discount_ended_by=request.user
                )

        data = {
            'old_discount_price': obj.discounted_price
        }
        obj.discounted_price = request.data['discount_price']
        obj.save()

        data['new_discount_price'] = obj.discounted_price
        data['product_id'] = obj.product_id
        data['customer_type_id'] = obj.customer_type_id
        if ICustomerTypeWiseProductDiscountTrace.objects.filter(icustomer_type_wiser_product_discount=obj,
                                                                end_date__isnull=True).exists():
            customer_type_discount_obj = \
            ICustomerTypeWiseProductDiscountTrace.objects.filter(icustomer_type_wiser_product_discount=obj).order_by(
                '-time_created')[0]
            if Decimal(customer_type_discount_obj.discounted_price) != Decimal(request.data['discount_price']):
                ICustomerTypeWiseProductDiscountTrace.objects.create(
                    icustomer_type_wiser_product_discount=obj,
                    start_date=formatted_date,
                    mrp=Product.objects.get(id=request.data['product_id']).mrp,
                    discounted_price=request.data['discount_price'],
                    product_discount_started_by=request.user)
        else:
            ICustomerTypeWiseProductDiscountTrace.objects.create(
                icustomer_type_wiser_product_discount=obj,
                start_date=formatted_date,
                mrp=Product.objects.get(id=request.data['product_id']).mrp,
                discounted_price=request.data['discount_price'],
                product_discount_started_by=request.user)

        return Response(status=status.HTTP_200_OK)
    else:
        obj = ICustomerTypeWiseProductDiscount.objects.create(
            customer_type_id=request.data['customer_type_id'],
            product_id=request.data['product_id'],
            discounted_price=request.data['discount_price'],
            created_by=request.user,
            modified_by=request.user
        )
        ICustomerTypeWiseProductDiscountTrace.objects.create(
            icustomer_type_wiser_product_discount=obj,
            start_date=formatted_date,
            mrp=Product.objects.get(id=request.data['product_id']).mrp,
            discounted_price=request.data['discount_price'],
            product_discount_started_by=request.user
        )
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_product_trace_log(request):
    master_list = []

    product_trace_obj = ProductTrace.objects.filter(product__is_active=True).order_by('-id')
    values = product_trace_obj.filter().values_list('id', 'product', 'start_date',
                                                    'product_price_started_by__first_name', 'name', 'short_name',
                                                    'code', 'unit__name', 'quantity', 'mrp', 'gst_percent', 'snf',
                                                    'fat', 'is_homogenised', 'end_date', 'time_created',
                                                    'product_price_ended_by__first_name')
    columns = ['id', 'product_id', 'start_date', 'product_price_started_by', 'name', 'short_name', 'code', 'unit',
               'quantity', 'mrp', 'gst_percent', 'snf', 'fat', 'is_homogenised', 'end_date', 'time_created',
               'product_price_ended_by']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna('-')
    for index, row in df.iterrows():
        master_dict = {}
        master_dict['product_id'] = row['product_id']
        master_dict['product_name'] = row['name']
        master_dict['start_date'] = row['start_date']
        master_dict['start_by'] = row['product_price_started_by']
        master_dict['new_code'] = row['code']
        master_dict['new_unit'] = row['unit']
        master_dict['new_quantity'] = row['quantity']
        master_dict['new_mrp'] = row['mrp']
        master_dict['new_gst_percent'] = row['gst_percent']
        master_dict['new_snf'] = row['snf']
        master_dict['new_fat'] = row['fat']
        master_dict['new_is_homogenised'] = row['is_homogenised']
        master_dict['end_date'] = row['end_date']
        master_dict['ended_by'] = row['product_price_ended_by']
        if product_trace_obj.filter(product_id=row['product_id'], time_created__lte=row['time_created']).exclude(
                id=row['id']).order_by('time_created').exists():
            old_price = \
            product_trace_obj.filter(product_id=row['product_id'], time_created__lte=row['time_created']).exclude(
                id=row['id']).order_by('-time_created')[0]
            master_dict['old_code'] = old_price.code
            master_dict['old_unit'] = old_price.unit.name
            master_dict['old_quantity'] = old_price.quantity
            master_dict['old_mrp'] = old_price.mrp
            master_dict['old_gst_percent'] = old_price.gst_percent
            master_dict['old_snf'] = old_price.snf
            master_dict['old_fat'] = old_price.fat
            master_dict['old_is_homogenised'] = old_price.is_homogenised
        else:
            master_dict['old_code'] = '-'
            master_dict['old_unit'] = '-'
            master_dict['old_quantity'] = '-'
            master_dict['old_mrp'] = '-'
            master_dict['old_gst_percent'] = '-'
            master_dict['old_snf'] = '-'
            master_dict['old_fat'] = '-'
            master_dict['old_is_homogenised'] = '-'
        master_list.append(master_dict)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_all_product_list_for_display(request):
    product_obj = Product.objects.filter(is_active=True, group_id=1).order_by('display_ordinal')
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'snf', 'fat', 'is_homogenised', 'color'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'snf', 'fat', 'is_homogenised', 'color']
    product_df = pd.DataFrame(product_list, columns=product_column)
    return Response(data=product_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_icustomer_list_linked_with_agent(request):
    data_dict = {}
    business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
    agent_id = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).agent_id
    icustomer_obj = ICustomer.objects.filter(business_id=business_id)
    icustomer_list = list(
        icustomer_obj.values_list('id', 'user_profile__user__first_name', 'user_profile__user__last_name',
                                  'user_profile__street', 'user_profile__taluk__name', 'user_profile__mobile'))
    icustomer_column = ['id', 'first_name', 'last_name', 'address', 'taluk', 'mobile']
    icustomer_df = pd.DataFrame(icustomer_list, columns=icustomer_column)
    data_dict['icustomer_list'] = icustomer_df.to_dict('r')
    # sale_obj = Sale.objects.filter(sale_group__date=datetime.datetime.now(), sale_group__business_id=business_id)
    # sale_list = list(
    #     sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
    #                          'sale_group__date', 'sale_group__session',
    #                          'sale_group__session__display_name', 'sale_group__ordered_via',
    #                          'sale_group__ordered_via__name', 'sale_group__payment_status__name',
    #                          'sale_group__sale_status__name', 'sale_group__total_cost',
    #                          'product__group_id', 'product__quantity', 'product',
    #                          'product__name', 'count', 'cost'))
    # sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
    #                'session_name',
    #                'ordered_via_id', 'ordered_via_name','payment_status',
    #                'sale_status',
    #                'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id', 'product_name',
    #                'count', 'product_cost']
    # sale_df = pd.DataFrame(sale_list, columns=sale_column)
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year

    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=current_month,
                                                      icustomer_sale_group__date__year=current_year,
                                                      icustomer_sale_group__business_id=business_id,
                                                      product__is_active=True)
    icustomer_sale_list = list(
        icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__business__business_type_id',
                                       'icustomer_sale_group__icustomer_id',
                                       'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                       'icustomer_sale_group__session__display_name',
                                       'icustomer_sale_group__ordered_via',
                                       'icustomer_sale_group__ordered_via__name',
                                       'icustomer_sale_group__payment_status__name',
                                       'icustomer_sale_group__sale_status__name', 'icustomer_sale_group__total_cost',
                                       'product__group_id', 'product__quantity', 'product',
                                       'product__name', 'count', 'cost'))
    icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'icustomer_id', 'date',
                             'session_id',
                             'session_name',
                             'ordered_via_id', 'ordered_via_name', 'payment_status',
                             'sale_status',
                             'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id',
                             'product_name',
                             'count', 'product_cost']
    icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)
    # icustomer_sale_df = sale_df[sale_df['icustomer_id'].notna()]
    # icustomer_sale_df['icustomer_id'] = icustomer_sale_df['icustomer_id'].astype('int')
    master_dict = {}
    for index, row in icustomer_sale_df.iterrows():
        if not row['icustomer_id'] in master_dict:
            master_dict[row['icustomer_id']] = {}
        if not row['session_id'] in master_dict[row['icustomer_id']]:
            master_dict[row['icustomer_id']][row['session_id']] = {}
        if not row['product_id'] in master_dict[row['icustomer_id']][row['session_id']]:
            master_dict[row['icustomer_id']][row['session_id']][row['product_id']] = row['count']
    data_dict['individual_customer_order_details'] = master_dict
    product_obj = Product.objects.filter(group_id=1, is_active=True).order_by('display_ordinal')
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'snf', 'fat', 'is_homogenised'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'snf', 'fat', 'is_homogenised']
    product_df = pd.DataFrame(product_list, columns=product_column)
    session_obj = Session.objects.filter().order_by('id')
    session_list = list(session_obj.values_list('id', 'name', 'display_name', 'expiry_day_before', 'expiry_time'))
    session_column = ['id', 'name', 'display_name', 'expiry_day_before', 'expiry_time']
    session_df = pd.DataFrame(session_list, columns=session_column)
    milk_product_df = product_df.to_dict('r')
    data_dict['milk_product_list'] = milk_product_df
    data_dict['session_list'] = session_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_icustomer_orders_for_agent(request):
    data_dict = {}
    business_id = Business.objects.get(user_profile_id=request.user.userprofile.id).id
    agent_id = BusinessAgentMap.objects.get(business_id=business_id, is_active=True).agent_id
    sale_obj = Sale.objects.filter(sale_group__date=datetime.datetime.now(), sale_group__business_id=business_id,
                                   product__is_active=True)
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost',
                             'product__group_id', 'product__quantity', 'product',
                             'product__name', 'count', 'cost'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                   'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id', 'product_name',
                   'count', 'product_cost']
    business_sale_df = pd.DataFrame(sale_list, columns=sale_column)
    total_milk_quantity = 0
    master_dict = {}
    for index, row in business_sale_df.iterrows():
        if not row['session_id'] in master_dict:
            master_dict[row['session_id']] = {}
        if not row['product_id'] in master_dict[row['session_id']]:
            master_dict[row['session_id']][row['product_id']] = row['count']
        total_milk_quantity += Decimal(row['count']) * row['product_default_quantity'] / 1000
    data_dict['agent_order_details'] = master_dict

    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=current_month,
                                                      icustomer_sale_group__date__year=current_year,
                                                      product__is_active=True,
                                                      icustomer_sale_group__business_id=business_id)
    icustomer_sale_list = list(
        icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__business__business_type_id',
                                       'icustomer_sale_group__icustomer_id',
                                       'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                       'icustomer_sale_group__session__display_name',
                                       'icustomer_sale_group__ordered_via',
                                       'icustomer_sale_group__ordered_via__name',
                                       'icustomer_sale_group__payment_status__name',
                                       'icustomer_sale_group__sale_status__name', 'icustomer_sale_group__total_cost',
                                       'product__group_id', 'product__quantity', 'product',
                                       'product__name', 'count', 'cost'))
    icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'icustomer_id', 'date',
                             'session_id',
                             'session_name',
                             'ordered_via_id', 'ordered_via_name', 'payment_status',
                             'sale_status',
                             'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id',
                             'product_name',
                             'count', 'product_cost']
    icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)

    master_dict = {}
    for index, row in icustomer_sale_df.iterrows():
        if not row['session_id'] in master_dict:
            master_dict[row['session_id']] = {}
        if not row['product_id'] in master_dict[row['session_id']]:
            master_dict[row['session_id']][row['product_id']] = 0
        master_dict[row['session_id']][row['product_id']] += row['count']
        total_milk_quantity += Decimal(row['count']) * row['product_default_quantity'] / 1000
    data_dict['icustomer_overall_order_details'] = master_dict

    product_obj = Product.objects.filter(group__in=[1, 2], is_active=True).order_by('id')
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'snf', 'fat', 'is_homogenised', 'color'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'snf', 'fat', 'is_homogenised', 'color']
    product_df = pd.DataFrame(product_list, columns=product_column)
    session_obj = Session.objects.filter().order_by('id')
    session_list = list(session_obj.values_list('id', 'name', 'display_name', 'expiry_day_before', 'expiry_time'))
    session_column = ['id', 'name', 'display_name', 'expiry_day_before', 'expiry_time']
    session_df = pd.DataFrame(session_list, columns=session_column)
    milk_product_df = product_df[product_df['product_group_id'] == 1]
    data_dict['product_list'] = product_df.to_dict('r')
    data_dict['session_list'] = session_df.to_dict('r')
    data_dict['total_milk_quantity'] = total_milk_quantity
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_sale_details_based_on_date_range(request):
    print(request.data)
    data_dict = {}
    sale_obj = Sale.objects.filter(sale_group__date=request.data['selected_date'], product__is_active=True)
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost',
                             'product__group_id', 'product__quantity', 'product',
                             'product__name', 'count', 'cost'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id', 'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id', 'product_name',
                   'count', 'product_cost']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['count'] = sale_df['count'].astype('float')
    sale_df['product_default_quantity'] = sale_df['product_default_quantity'].astype('float')
    sale_df['count_multiply_by_quantity'] = sale_df['product_default_quantity'] * sale_df['count'] / 1000

    # Icustomer sale group dataframe
    requested_month = datetime.datetime.strptime(request.data['selected_date'], '%Y-%m-%d').month
    requested_year = datetime.datetime.strptime(request.data['selected_date'], '%Y-%m-%d').year
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                      icustomer_sale_group__date__year=requested_year,
                                                      product__is_active=True)
    icustomer_sale_list = list(
        icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__business__business_type_id',
                                       'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                       'icustomer_sale_group__session__display_name',
                                       'icustomer_sale_group__ordered_via',
                                       'icustomer_sale_group__ordered_via__name',
                                       'icustomer_sale_group__payment_status__name',
                                       'icustomer_sale_group__sale_status__name', 'icustomer_sale_group__total_cost',
                                       'product__group_id', 'product__quantity', 'product',
                                       'product__name', 'count', 'cost'))
    icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                             'session_name',
                             'ordered_via_id', 'ordered_via_name', 'payment_status',
                             'sale_status',
                             'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id',
                             'product_name',
                             'count', 'product_cost']
    icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)
    icustomer_sale_df['count'] = icustomer_sale_df['count'].astype('float')
    icustomer_sale_df['product_default_quantity'] = icustomer_sale_df['product_default_quantity'].astype('float')
    icustomer_sale_df['count_multiply_by_quantity'] = icustomer_sale_df['product_default_quantity'] * icustomer_sale_df[
        'count'] / 1000
    final_df = sale_df.merge(icustomer_sale_df, how="outer")
    data_dict['total_quantity'] = final_df['count_multiply_by_quantity'].sum()
    data_dict['total_price'] = final_df['product_cost'].sum()
    # cbe union sale
    cbe_union_agent_sale_df = sale_df[(sale_df['business_type_id'] != 6) & (sale_df['business_type_id'] != 7)]
    cbe_union_customer_sale_df = icustomer_sale_df[
        (icustomer_sale_df['business_type_id'] != 6) & (icustomer_sale_df['business_type_id'] != 7)]
    cbe_union_final_df = cbe_union_agent_sale_df.merge(cbe_union_customer_sale_df, how="outer")
    data_dict['cbe_union_total_quantity'] = cbe_union_final_df['count_multiply_by_quantity'].sum()
    data_dict['cbe_union_total_price'] = cbe_union_final_df['product_cost'].sum()
    data_dict['cbe_union_total_quantity_per_product_group_for_icustomer'] = \
    cbe_union_customer_sale_df.groupby('product_group_id')['count_multiply_by_quantity'].agg('sum').to_dict()
    data_dict['cbe_union_total_quantity_per_product_group_for_business'] = \
    cbe_union_agent_sale_df.groupby('product_group_id')['count_multiply_by_quantity'].agg('sum').to_dict()
    data_dict['cbe_union_total_quantity_per_product_group'] = cbe_union_final_df.groupby('product_group_id')[
        'count_multiply_by_quantity'].agg('sum').to_dict()

    data_dict['total_quantity_per_product_group_for_icustomer'] = icustomer_sale_df.groupby('product_group_id')[
        'count_multiply_by_quantity'].agg('sum').to_dict()
    data_dict['total_quantity_per_product_group_for_business'] = sale_df.groupby('product_group_id')[
        'count_multiply_by_quantity'].agg('sum').to_dict()
    data_dict['total_quantity_per_product_group'] = final_df.groupby('product_group_id')[
        'count_multiply_by_quantity'].agg('sum').to_dict()
    sale_df_with_other_union = sale_df[sale_df['business_type_id'] == 6]
    sale_df_with_other_state = sale_df[sale_df['business_type_id'] == 7]
    sale_df_without_other_union_and_state = final_df[
        (final_df['business_type_id'] != 6) & (final_df['business_type_id'] != 7)]
    master_dict_overall = {}
    for index, row in sale_df_without_other_union_and_state.iterrows():
        if not row['product_group_id'] in master_dict_overall:
            master_dict_overall[row['product_group_id']] = {}
        if not row['session_id'] in master_dict_overall[row['product_group_id']]:
            master_dict_overall[row['product_group_id']][row['session_id']] = {}
        if not row['product_id'] in master_dict_overall[row['product_group_id']][row['session_id']]:
            master_dict_overall[row['product_group_id']][row['session_id']][row['product_id']] = 0
        master_dict_overall[row['product_group_id']][row['session_id']][row['product_id']] += row[
            'count_multiply_by_quantity']
    data_dict['total_quantity_per_product'] = master_dict_overall
    master_dict_other_union = {}
    for index, row in sale_df_with_other_union.iterrows():
        if not row['product_group_id'] in master_dict_other_union:
            master_dict_other_union[row['product_group_id']] = {}
        if not row['product_id'] in master_dict_other_union[row['product_group_id']]:
            master_dict_other_union[row['product_group_id']][row['product_id']] = 0
        master_dict_other_union[row['product_group_id']][row['product_id']] += row[
            'count_multiply_by_quantity']
    data_dict['total_quantity_per_product_for_other_union'] = master_dict_other_union
    master_dict_other_state = {}
    for index, row in sale_df_with_other_state.iterrows():
        if not row['product_group_id'] in master_dict_other_state:
            master_dict_other_state[row['product_group_id']] = {}
        if not row['product_id'] in master_dict_other_state[row['product_group_id']]:
            master_dict_other_state[row['product_group_id']][row['product_id']] = 0
        master_dict_other_state[row['product_group_id']][row['product_id']] += row[
            'count_multiply_by_quantity']
    data_dict['total_quantity_per_product_for_other_state'] = master_dict_other_state
    product_group_obj = ProductGroup.objects.filter(id__in=[1, 2])
    product_group_list = list(product_group_obj.values_list('id', 'name'))
    product_group_column = ['id', 'name']
    product_group_df = pd.DataFrame(product_group_list, columns=product_group_column)
    product_obj = Product.objects.filter(is_active=True).order_by('display_ordinal')
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'snf', 'fat', 'is_homogenised'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'snf', 'fat', 'is_homogenised']
    product_df = pd.DataFrame(product_list, columns=product_column)
    data_dict['product_dict'] = product_df.groupby('product_group_id').apply(lambda x: x.to_dict('r')).to_dict()
    data_dict['product_group_dict'] = product_group_df.to_dict('r')
    session_obj = Session.objects.filter().order_by('id')
    session_list = list(session_obj.values_list('id', 'name', 'display_name', 'expiry_day_before', 'expiry_time'))
    session_column = ['id', 'name', 'display_name', 'expiry_day_before', 'expiry_time']
    session_df = pd.DataFrame(session_list, columns=session_column)
    data_dict['session_list'] = session_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_zone_wise_split_aavin_today_data(request):
    product_group_obj = ProductGroup.objects.filter(id__in=[1, 2])
    product_group_list = list(product_group_obj.values_list('id', 'name'))
    product_group_column = ['id', 'name']
    product_group_df = pd.DataFrame(product_group_list, columns=product_group_column)
    sale_obj = Sale.objects.filter(sale_group__date=request.data['selected_date'], product__is_active=True).exclude(
        sale_group__business__zone_id__in=[11, 13, 15])
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost',
                             'product__group_id', 'product__quantity', 'product',
                             'product__name', 'count', 'cost', 'sale_group__business__zone_id'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id', 'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id', 'product_name',
                   'count', 'product_cost', 'zone_id']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['count'] = sale_df['count'].astype('float')
    sale_df['product_default_quantity'] = sale_df['product_default_quantity'].astype('float')
    sale_df['count_multiply_by_quantity'] = sale_df['product_default_quantity'] * sale_df['count'] / 1000
    # icustomer
    requested_month = datetime.datetime.strptime(request.data['selected_date'], '%Y-%m-%d').month
    requested_year = datetime.datetime.strptime(request.data['selected_date'], '%Y-%m-%d').year
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                      icustomer_sale_group__date__year=requested_year,
                                                      product__is_active=True).exclude(
        icustomer_sale_group__business__zone_id__in=[11, 13, 15])
    icustomer_sale_list = list(
        icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__business__business_type_id',
                                       'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                       'icustomer_sale_group__session__display_name',
                                       'icustomer_sale_group__ordered_via',
                                       'icustomer_sale_group__ordered_via__name',
                                       'icustomer_sale_group__payment_status__name',
                                       'icustomer_sale_group__sale_status__name', 'icustomer_sale_group__total_cost',
                                       'product__group_id', 'product__quantity', 'product',
                                       'product__name', 'count', 'cost', 'icustomer_sale_group__business__zone_id'))
    icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                             'session_name',
                             'ordered_via_id', 'ordered_via_name', 'payment_status',
                             'sale_status',
                             'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id',
                             'product_name',
                             'count', 'product_cost', 'zone_id']
    icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)
    icustomer_sale_df['count'] = icustomer_sale_df['count'].astype('float')
    icustomer_sale_df['product_default_quantity'] = icustomer_sale_df['product_default_quantity'].astype('float')
    icustomer_sale_df['count_multiply_by_quantity'] = icustomer_sale_df['product_default_quantity'] * icustomer_sale_df[
        'count'] / 1000
    final_df = sale_df.merge(icustomer_sale_df, how="outer")

    zone_data_list = []
    for zone in Zone.objects.filter().exclude(id__in=[11, 13, 15]).order_by('id'):
        filtered_sale_df = sale_df[sale_df['zone_id'] == zone.id]
        filtered_icustomer_sale_df = icustomer_sale_df[icustomer_sale_df['zone_id'] == zone.id]
        filtered_final_df = final_df[final_df['zone_id'] == zone.id]
        data_dict = {}
        data_dict['zone_name'] = zone.name
        data_dict['total_quantity'] = filtered_final_df['count_multiply_by_quantity'].sum()
        data_dict['total_price'] = filtered_final_df['product_cost'].sum()

        data_dict['total_quantity_per_product_group_for_icustomer'] = \
        filtered_icustomer_sale_df.groupby('product_group_id')['count_multiply_by_quantity'].agg('sum').to_dict()
        data_dict['total_quantity_per_product_group_for_business'] = filtered_sale_df.groupby('product_group_id')[
            'count_multiply_by_quantity'].agg('sum').to_dict()
        data_dict['total_quantity_per_product_group'] = filtered_final_df.groupby('product_group_id')[
            'count_multiply_by_quantity'].agg('sum').to_dict()

        zone_data_list.append(data_dict)
    final_data_dict = {
        'zone_data': zone_data_list,
        'product_group_list': product_group_df.to_dict('r')
    }
    return Response(data=final_data_dict, status=status.HTTP_200_OK)


def selected_date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


@api_view(['POST'])
def serve_sale_details_based_on_week_range(request):
    print(request.data)
    data_dict = {}
    label = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    color_pallets = ['#F5B7B1', '#EC7063', '#AED6F1', '#5DADE2', '#FAD7A0', '#F5B041', '#DC7633', '#5D6D7E', '#EB984E',
                     '#F4D03F', '#7B241C', '#7B7D7D', '#9B59B6', '#5499C7', '#F4D03F']
    product_group_name = ProductGroup.objects.get(id=request.data['product_group_id']).name
    if request.data['week_option'] == 'this_week':
        date_str = datetime.datetime.now()
        start_date = date_str - timedelta(days=date_str.weekday() + 1)  # Sunday
        end_date = start_date + timedelta(days=7)  # next Sunday
        sale_obj = Sale.objects.filter(sale_group__date__gte=start_date, sale_group__date__lt=end_date,
                                       product__group_id=request.data['product_group_id'], product__is_active=True)
    elif request.data['week_option'] == 'last_week':
        date_str = datetime.datetime.now()
        end_date = date_str - timedelta(days=date_str.weekday() + 1)
        last_week_last_date = end_date - timedelta(days=1)
        start_date = last_week_last_date - timedelta(days=last_week_last_date.weekday() + 1)
        sale_obj = Sale.objects.filter(sale_group__date__gte=start_date, sale_group__date__lt=end_date,
                                       product__group_id=request.data['product_group_id'], product__is_active=True)
    elif request.data['week_option'] == 'custom':
        date_str = datetime.datetime.strptime(request.data['selected_week_date'], "%Y-%m-%d")
        start_date = date_str - timedelta(days=date_str.weekday() + 1)  # Sunday
        end_date = start_date + timedelta(days=7)  # next Sunday
        sale_obj = Sale.objects.filter(sale_group__date__gte=start_date, sale_group__date__lt=end_date,
                                       product__group_id=request.data['product_group_id'], product__is_active=True)
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost', 'product__group_id',
                             'product__group__name', 'product__quantity', 'product',
                             'product__name', 'count', 'cost'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                   'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_group_name', 'product_default_quantity',
                   'product_id', 'product_name', 'count', 'product_cost']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    final_icustomer_df = pd.DataFrame(
        columns=['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id', 'session_name',
                 'ordered_via_id', 'ordered_via_name', 'payment_status',
                 'sale_status',
                 'session_wise_price', 'product_group_id', 'product_group_name', 'product_default_quantity',
                 'product_id', 'product_name',
                 'count', 'product_cost'])
    for single_date in selected_date_range(start_date, end_date):
        date = single_date.strftime("%Y-%m-%d")
        requested_month = datetime.datetime.strptime(date, '%Y-%m-%d').month
        requested_year = datetime.datetime.strptime(date, '%Y-%m-%d').year

        icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                          icustomer_sale_group__date__year=requested_year,
                                                          product__group_id=request.data['product_group_id'],
                                                          product__is_active=True)
        icustomer_sale_list = list(
            icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                           'icustomer_sale_group__business__business_type_id',
                                           'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                           'icustomer_sale_group__session__display_name',
                                           'icustomer_sale_group__ordered_via',
                                           'icustomer_sale_group__ordered_via__name',
                                           'icustomer_sale_group__payment_status__name',
                                           'icustomer_sale_group__sale_status__name',
                                           'icustomer_sale_group__total_cost',
                                           'product__group_id', 'product__group__name', 'product__quantity', 'product',
                                           'product__name', 'count', 'cost'))
        icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                                 'session_name',
                                 'ordered_via_id', 'ordered_via_name', 'payment_status',
                                 'sale_status',
                                 'session_wise_price', 'product_group_id', 'product_group_name',
                                 'product_default_quantity', 'product_id',
                                 'product_name',
                                 'count', 'product_cost']

        icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)
        icustomer_sale_df['date'] = date
        final_icustomer_df = final_icustomer_df.append(icustomer_sale_df)
    final_df = sale_df.merge(final_icustomer_df, how="outer")
    final_df['count'] = final_df['count'].astype('float')
    final_df['date'] = final_df['date'].astype('str')
    final_df['product_default_quantity'] = final_df['product_default_quantity'].astype('float')
    final_df['count_multiply_by_quantity'] = final_df['product_default_quantity'] * final_df['count'] / 1000
    product_obj = Product.objects.filter(group_id=request.data['product_group_id'], is_active=True).order_by(
        'display_ordinal')
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'snf', 'fat', 'is_homogenised'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'snf', 'fat', 'is_homogenised']
    product_df = pd.DataFrame(product_list, columns=product_column)
    master_dict_product_group = defaultdict(dict)
    master_dict_product_group['label'] = product_group_name
    master_dict_product_group['data'] = []
    master_dict_product_group['backgroundColor'] = color_pallets[1]
    master_dict_product_group['borderColor'] = color_pallets[1]
    master_dict_product_group['pointBorderColor'] = color_pallets[1]
    master_dict_product_group['pointHoverBackgroundColor'] = color_pallets[1]
    master_dict_product_group['pointHoverBorderColor'] = color_pallets[1]
    master_dict_product_group['fill'] = False
    master_dict_product_group['lineTension'] = 0.1
    master_dict_product_group['borderCapStyle'] = 'butt'
    master_dict_product_group['borderDash'] = []
    master_dict_product_group['borderDashOffset'] = 0.0
    master_dict_product_group['borderJoinStyle'] = 'miter'
    master_dict_product_group['pointBorderWidth'] = 1
    master_dict_product_group['pointHoverRadius'] = 5
    master_dict_product_group['pointHoverBorderWidth'] = 2
    master_dict_product_group['pointRadius'] = 1
    master_dict_product_group['pointHitRadius'] = 10
    master_dict_product_group['spanGaps'] = False
    for single_date in selected_date_range(start_date, end_date):
        date = single_date.strftime("%Y-%m-%d")
        filtered_df = final_df[final_df['date'] == date]
        if not filtered_df.empty:
            master_dict_product_group['data'].append(filtered_df['count_multiply_by_quantity'].sum())
        else:
            master_dict_product_group['data'].append(0)
    master_dict_product = defaultdict(dict)
    master_list_product = []
    for index, row in product_df.iterrows():
        master_dict_product = defaultdict(dict)
        master_dict_product['label'] = row['product_name']
        master_dict_product['data'] = []
        master_dict_product['backgroundColor'] = color_pallets[index]
        master_dict_product['borderColor'] = color_pallets[index]
        master_dict_product['pointBorderColor'] = color_pallets[index]
        master_dict_product['pointHoverBackgroundColor'] = color_pallets[index]
        master_dict_product['pointHoverBorderColor'] = color_pallets[index]
        master_dict_product['fill'] = False
        master_dict_product['lineTension'] = 0.1
        master_dict_product['borderCapStyle'] = 'butt'
        master_dict_product['borderDash'] = []
        master_dict_product['borderDashOffset'] = 0.0
        master_dict_product['borderJoinStyle'] = 'miter'
        master_dict_product['pointBorderWidth'] = 1
        master_dict_product['pointHoverRadius'] = 5
        master_dict_product['pointHoverBorderWidth'] = 2
        master_dict_product['pointRadius'] = 1
        master_dict_product['pointHitRadius'] = 10
        master_dict_product['spanGaps'] = False
        for single_date in selected_date_range(start_date, end_date):
            date = single_date.strftime("%Y-%m-%d")
            filtered_df = final_df[(final_df['date'] == date) & (final_df['product_id'] == row['product_id'])]
            if not filtered_df.empty:
                master_dict_product['data'].append(filtered_df['count_multiply_by_quantity'].sum())
            else:
                master_dict_product['data'].append(0)
        master_list_product.append(master_dict_product)
    data_dict['product_group_wise_data'] = {}
    data_dict['product_group_wise_data']['datasets'] = [master_dict_product_group]
    data_dict['product_group_wise_data']['labels'] = label
    data_dict['product_wise_data'] = {}
    data_dict['product_wise_data']['datasets'] = master_list_product
    data_dict['product_wise_data']['labels'] = label
    end_date = end_date - timedelta(days=1)
    data_dict['week_start_date'] = start_date
    data_dict['week_end_date'] = end_date
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_sale_details_based_on_month_range(request):
    print(request.data)
    data_dict = {}
    label = []
    color_pallets = ['#F5B7B1', '#EC7063', '#AED6F1', '#5DADE2', '#FAD7A0', '#F5B041', '#DC7633', '#5D6D7E', '#EB984E',
                     '#F4D03F', '#7B241C', '#7B7D7D', '#9B59B6', '#5499C7', '#F4D03F']
    product_group_name = ProductGroup.objects.get(id=request.data['product_group_id']).name
    if request.data['month_option'] == 'this_month':
        current_month_in_string = datetime.datetime.now().strftime("%m")
        current_month_in_integer = int(datetime.datetime.now().strftime("%m"))
        current_year = datetime.datetime.now().year
        total_days_in_month = monthrange(current_year, current_month_in_integer)[1]
        sale_obj = Sale.objects.filter(sale_group__date__month=current_month_in_integer,
                                       sale_group__date__year=current_year,
                                       product__group_id=request.data['product_group_id'], product__is_active=True)
        icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=current_month_in_integer,
                                                          icustomer_sale_group__date__year=current_year,
                                                          product__group_id=request.data['product_group_id'],
                                                          product__is_active=True)
    elif request.data['month_option'] == 'last_month':
        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonth = first - timedelta(days=1)
        current_month_in_string = lastMonth.strftime("%m")
        current_month_in_integer = int(lastMonth.strftime("%m"))
        current_year = lastMonth.year
        total_days_in_month = monthrange(current_year, current_month_in_integer)[1]
        sale_obj = Sale.objects.filter(sale_group__date__month=current_month_in_integer,
                                       sale_group__date__year=current_year,
                                       product__group_id=request.data['product_group_id'], product__is_active=True)
        icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=current_month_in_integer,
                                                          icustomer_sale_group__date__year=current_year,
                                                          product__group_id=request.data['product_group_id'],
                                                          product__is_active=True)

    elif request.data['month_option'] == 'custom':
        current_month_in_integer = int(request.data['selected_month']['month_in_integer'] + 1)
        current_month_in_string = str(current_month_in_integer)
        current_year = request.data['selected_month']['year']
        total_days_in_month = monthrange(current_year, current_month_in_integer)[1]
        sale_obj = Sale.objects.filter(sale_group__date__month=current_month_in_integer,
                                       sale_group__date__year=current_year, product__is_active=True,
                                       product__group_id=request.data['product_group_id'])
        icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=current_month_in_integer,
                                                          icustomer_sale_group__date__year=current_year,
                                                          product__group_id=request.data['product_group_id'])

    for count in range(1, total_days_in_month + 1):
        label.append(count)
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost', 'product__group_id',
                             'product__group__name', 'product__quantity', 'product',
                             'product__name', 'count', 'cost'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                   'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_group_name', 'product_default_quantity',
                   'product_id', 'product_name', 'count', 'product_cost']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)

    # construct Icustomer dataframe for one month
    final_icustomer_df = pd.DataFrame(
        columns=['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id', 'session_name',
                 'ordered_via_id', 'ordered_via_name', 'payment_status',
                 'sale_status',
                 'session_wise_price', 'product_group_id', 'product_group_name', 'product_default_quantity',
                 'product_id', 'product_name',
                 'count', 'product_cost'])

    for date_count in range(1, total_days_in_month + 1):
        date = str(current_year) + '-' + current_month_in_string + '-' + str(date_count)
        icustomer_sale_list = list(
            icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                           'icustomer_sale_group__business__business_type_id',
                                           'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                           'icustomer_sale_group__session__display_name',
                                           'icustomer_sale_group__ordered_via',
                                           'icustomer_sale_group__ordered_via__name',
                                           'icustomer_sale_group__payment_status__name',
                                           'icustomer_sale_group__sale_status__name',
                                           'icustomer_sale_group__total_cost',
                                           'product__group_id', 'product__group__name', 'product__quantity', 'product',
                                           'product__name', 'count', 'cost'))
        icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                                 'session_name',
                                 'ordered_via_id', 'ordered_via_name', 'payment_status',
                                 'sale_status',
                                 'session_wise_price', 'product_group_id', 'product_group_name',
                                 'product_default_quantity', 'product_id',
                                 'product_name',
                                 'count', 'product_cost']

        icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)
        icustomer_sale_df['date'] = date
        final_icustomer_df = final_icustomer_df.append(icustomer_sale_df)
    final_df = sale_df.merge(final_icustomer_df, how="outer")

    final_df['count'] = final_df['count'].astype('float')
    final_df['date'] = final_df['date'].astype('str')
    final_df['product_default_quantity'] = final_df['product_default_quantity'].astype('float')
    final_df['count_multiply_by_quantity'] = final_df['product_default_quantity'] * final_df['count'] / 1000
    product_obj = Product.objects.filter(group_id=request.data['product_group_id'], is_active=True).order_by(
        'display_ordinal')
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'snf', 'fat', 'is_homogenised'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'snf', 'fat', 'is_homogenised']
    product_df = pd.DataFrame(product_list, columns=product_column)
    master_dict_product_group = defaultdict(dict)
    master_dict_product_group['label'] = product_group_name
    master_dict_product_group['data'] = []
    master_dict_product_group['backgroundColor'] = color_pallets[1]
    master_dict_product_group['borderColor'] = color_pallets[1]
    master_dict_product_group['pointBorderColor'] = color_pallets[1]
    master_dict_product_group['pointHoverBackgroundColor'] = color_pallets[1]
    master_dict_product_group['pointHoverBorderColor'] = color_pallets[1]
    master_dict_product_group['fill'] = False
    master_dict_product_group['lineTension'] = 0.1
    master_dict_product_group['borderCapStyle'] = 'butt'
    master_dict_product_group['borderDash'] = []
    master_dict_product_group['borderDashOffset'] = 0.0
    master_dict_product_group['borderJoinStyle'] = 'miter'
    master_dict_product_group['pointBorderWidth'] = 1
    master_dict_product_group['pointHoverRadius'] = 5
    master_dict_product_group['pointHoverBorderWidth'] = 2
    master_dict_product_group['pointRadius'] = 1
    master_dict_product_group['pointHitRadius'] = 10
    master_dict_product_group['spanGaps'] = False
    for date_count in range(1, total_days_in_month + 1):
        date = str(current_year) + '-' + current_month_in_string + '-' + str(date_count)
        filtered_df = final_df[final_df['date'] == date]
        if not filtered_df.empty:
            master_dict_product_group['data'].append(filtered_df['count_multiply_by_quantity'].sum())
        else:
            master_dict_product_group['data'].append(0)
    master_dict_product = defaultdict(dict)
    master_list_product = []
    for index, row in product_df.iterrows():
        master_dict_product = defaultdict(dict)
        master_dict_product['label'] = row['product_name']
        master_dict_product['data'] = []
        master_dict_product['backgroundColor'] = color_pallets[index]
        master_dict_product['borderColor'] = color_pallets[index]
        master_dict_product['pointBorderColor'] = color_pallets[index]
        master_dict_product['pointHoverBackgroundColor'] = color_pallets[index]
        master_dict_product['pointHoverBorderColor'] = color_pallets[index]
        master_dict_product['fill'] = False
        master_dict_product['lineTension'] = 0.1
        master_dict_product['borderCapStyle'] = 'butt'
        master_dict_product['borderDash'] = []
        master_dict_product['borderDashOffset'] = 0.0
        master_dict_product['borderJoinStyle'] = 'miter'
        master_dict_product['pointBorderWidth'] = 1
        master_dict_product['pointHoverRadius'] = 5
        master_dict_product['pointHoverBorderWidth'] = 2
        master_dict_product['pointRadius'] = 1
        master_dict_product['pointHitRadius'] = 10
        master_dict_product['spanGaps'] = False
        for date_count in range(1, total_days_in_month + 1):
            date = str(current_year) + '-' + current_month_in_string + '-' + str(date_count)
            filtered_df = final_df[(final_df['date'] == date) & (final_df['product_id'] == row['product_id'])]
            if not filtered_df.empty:
                master_dict_product['data'].append(filtered_df['count_multiply_by_quantity'].sum())
            else:
                master_dict_product['data'].append(0)
        master_list_product.append(master_dict_product)
    data_dict['product_group_wise_data'] = {}
    data_dict['product_group_wise_data']['datasets'] = [master_dict_product_group]
    data_dict['product_group_wise_data']['labels'] = label
    data_dict['product_wise_data'] = {}
    data_dict['product_wise_data']['datasets'] = master_list_product
    data_dict['product_wise_data']['labels'] = label
    data_dict['month_in_integer'] = current_month_in_integer
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_product_group_for_aavin_today(request):
    product_group_obj = ProductGroup.objects.all()
    product_group_list = list(product_group_obj.values_list('id', 'name'))
    product_group_column = ['id', 'name']
    product_group_df = pd.DataFrame(product_group_list, columns=product_group_column)
    return Response(data=product_group_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_wise_product_commission_trace_log(request):
    business_type_wise_product_commission_trace_obj = BusinessTypeWiseProductCommissionTrace.objects.filter(
        business_type_wise_commission__product__is_active=True).order_by("-time_created")
    values = business_type_wise_product_commission_trace_obj.filter().values_list('id',
                                                                                  'business_type_wise_commission_id',
                                                                                  'business_type_wise_commission__business_type__name',
                                                                                  'start_date', 'end_date', 'mrp',
                                                                                  'commission_percentage',
                                                                                  'time_created', 'time_modified',
                                                                                  'product_commission_started_by__first_name',
                                                                                  'product_commission_ended_by__first_name')
    columns = ['id', 'business_type_wise_commission_id', 'business_type_name', 'start_date', 'end_date', 'mrp',
               'commission_percentage', 'time_created', 'time_modified', 'product_commission_started_by_first_name',
               'product_commission_ended_by_first_name']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna('-')
    master_list = []
    for index, row in df.iterrows():
        master_dict = {}
        master_dict['business_type_wise_commission_id'] = row['business_type_wise_commission_id']
        master_dict['business_type_name'] = row['business_type_name']
        master_dict['start_date'] = row['start_date']
        master_dict['new_mrp'] = row['mrp']
        master_dict['new_commission_percentage'] = row['commission_percentage']
        master_dict['start_by'] = row['product_commission_started_by_first_name']
        master_dict['ended_by'] = row['product_commission_ended_by_first_name']
        master_dict['end_date'] = row['end_date']
        if business_type_wise_product_commission_trace_obj.filter(
                business_type_wise_commission_id=row['business_type_wise_commission_id'],
                time_created__lte=row['time_created']).exclude(id=row['id']).exists():
            old_price = business_type_wise_product_commission_trace_obj.filter(
                business_type_wise_commission_id=row['business_type_wise_commission_id'],
                time_created__lte=row['time_created']).exclude(id=row['id']).order_by('-time_created')[0]
            master_dict['old_mrp'] = old_price.mrp
            master_dict['old_commission_percentage'] = old_price.commission_percentage
        else:
            continue
            master_dict['old_mrp'] = '-'
            master_dict['old_commission_percentage'] = '-'
        master_list.append(master_dict)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_wise_product_discount_trace_log(request):
    business_type_wise_product_discount_trace_obj = BusinessTypeWiseProductDiscountTrace.objects.filter().order_by("-time_created")
    values = business_type_wise_product_discount_trace_obj.filter().values_list('id', 'business_type_wise_discount_id',
                                                                                'business_type_wise_discount__business_type__name',
                                                                                'start_date', 'end_date', 'mrp',
                                                                                'discounted_price', 'time_created',
                                                                                'product_discount_started_by__first_name',
                                                                                'product_discount_ended_by__first_name', 'business_type_wise_discount__product__short_name')
    columns = ['id', 'business_type_wise_discount_id', 'business_type_name', 'start_date', 'end_date', 'mrp',
               'discounted_price', 'time_created', 'product_discount_started_by_first_name',
               'product_discount_ended_by_first_name', 'product_short_name']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna('-')
    print(df)
    master_list = []
    for index, row in df.iterrows():
        master_dict = {}
        master_dict['business_type_wise_discount_id'] = row['business_type_wise_discount_id']
        master_dict['business_type_name'] = row['business_type_name']
        master_dict['start_date'] = row['start_date']
        master_dict['product_short_name'] = row['product_short_name']
        master_dict['new_mrp'] = row['mrp']
        master_dict['new_discounted_price'] = row['discounted_price']
        master_dict['start_by'] = row['product_discount_started_by_first_name']
        master_dict['ended_by'] = row['product_discount_ended_by_first_name']
        master_dict['end_date'] = row['end_date']
        if business_type_wise_product_discount_trace_obj.filter(
                business_type_wise_discount_id=row['business_type_wise_discount_id'],
                time_created__lte=row['time_created']).exclude(id=row['id']).exists():
            old_price = business_type_wise_product_discount_trace_obj.filter(
                business_type_wise_discount_id=row['business_type_wise_discount_id'],
                time_created__lte=row['time_created']).exclude(id=row['id']).order_by('-time_created')[0]
            master_dict['old_mrp'] = old_price.mrp
            master_dict['old_discounted_price'] = old_price.discounted_price
        else:
            master_dict['old_mrp'] = '-'
            master_dict['old_discounted_price'] = '-'
        master_list.append(master_dict)
    print(master_list)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_wise_product_discount_trace_log(request):
    business_wise_product_discount_trace_obj = BusinessWiseProductDiscountTrace.objects.filter(
        business_wise_discount__product__is_active=True).order_by('-time_created')
    values = business_wise_product_discount_trace_obj.filter().values_list('id', 'business_wise_discount_id',
                                                                           'business_wise_discount__business__name',
                                                                           'start_date', 'end_date', 'mrp',
                                                                           'discounted_price', 'time_created',
                                                                           'product_discount_started_by__first_name',
                                                                           'product_discount_ended_by__first_name', 'business_wise_discount__product__short_name')
    columns = ['id', 'business_wise_discount_id', 'business_name', 'start_date', 'end_date', 'mrp', 'discounted_price',
               'time_created', 'product_discount_started_by_first_name', 'product_discount_ended_by_first_name', 'product_short_name']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna('-')
    master_list = []
    for index, row in df.iterrows():
        master_dict = {}
        master_dict['business_wise_discount_id'] = row['business_wise_discount_id']
        master_dict['business_name'] = row['business_name']
        master_dict['start_date'] = row['start_date']
        master_dict['product_short_name'] = row['product_short_name']
        master_dict['new_mrp'] = row['mrp']
        master_dict['new_discounted_price'] = row['discounted_price']
        master_dict['start_by'] = row['product_discount_started_by_first_name']
        master_dict['ended_by'] = row['product_discount_ended_by_first_name']
        master_dict['end_date'] = row['end_date']
        if business_wise_product_discount_trace_obj.filter(business_wise_discount_id=row['business_wise_discount_id'],
                                                           time_created__lte=row['time_created']).exclude(
                id=row['id']).exists():
            old_price = \
            business_wise_product_discount_trace_obj.filter(business_wise_discount_id=row['business_wise_discount_id'],
                                                            time_created__lte=row['time_created']).exclude(
                id=row['id']).order_by('-time_created')[0]
            master_dict['old_mrp'] = old_price.mrp
            master_dict['old_discounted_price'] = old_price.discounted_price
        else:
            master_dict['old_mrp'] = '-'
            master_dict['old_discounted_price'] = '-'
        master_list.append(master_dict)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_icustomer_type_wise_product_discount_trace_log(request):
    business_wise_product_discount_trace_obj = ICustomerTypeWiseProductDiscountTrace.objects.filter(
        icustomer_type_wiser_product_discount__product__is_active=True).order_by('-time_created')
    values = business_wise_product_discount_trace_obj.filter().values_list('id',
                                                                           'icustomer_type_wiser_product_discount',
                                                                           'icustomer_type_wiser_product_discount__customer_type__name',
                                                                           'start_date', 'end_date', 'mrp',
                                                                           'discounted_price', 'time_created',
                                                                           'product_discount_started_by__first_name',
                                                                           'product_discount_ended_by__first_name')
    columns = ['id', 'icustomer_type_wiser_product_discount_id', 'customer_type_name', 'start_date', 'end_date', 'mrp',
               'discounted_price', 'time_created', 'product_discount_started_by_first_name',
               'product_discount_ended_by_first_name']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna('-')
    master_list = []
    for index, row in df.iterrows():
        master_dict = {}
        master_dict['icustomer_type_wiser_product_discount_id'] = row['icustomer_type_wiser_product_discount_id']
        master_dict['customer_type_name'] = row['customer_type_name']
        master_dict['start_date'] = row['start_date']
        master_dict['new_mrp'] = row['mrp']
        master_dict['new_discounted_price'] = row['discounted_price']
        master_dict['start_by'] = row['product_discount_started_by_first_name']
        master_dict['ended_by'] = row['product_discount_ended_by_first_name']
        master_dict['end_date'] = row['end_date']
        if business_wise_product_discount_trace_obj.filter(
                icustomer_type_wiser_product_discount_id=row['icustomer_type_wiser_product_discount_id'],
                time_created__lte=row['time_created']).exclude(id=row['id']).exists():
            old_price = business_wise_product_discount_trace_obj.filter(
                icustomer_type_wiser_product_discount_id=row['icustomer_type_wiser_product_discount_id'],
                time_created__lte=row['time_created']).exclude(id=row['id']).order_by('-time_created')[0]
            master_dict['old_mrp'] = old_price.mrp
            master_dict['old_discounted_price'] = old_price.discounted_price
        else:
            continue
            master_dict['old_mrp'] = '-'
            master_dict['old_discounted_price'] = '-'
        master_list.append(master_dict)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_live_indent_for_selected_date(request):
    data_dict = {}

    sale_obj = Sale.objects.filter(sale_group__date=request.data['requested_date'], product__is_active=True).exclude(
        sale_group__business__zone_id__in=[11, 13, 15])
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost',
                             'product__group_id', 'product__quantity', 'product',
                             'product__name', 'count', 'cost', 'sale_group__business__zone_id'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id', 'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id', 'product_name',
                   'count', 'product_cost', 'zone_id']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['count'] = sale_df['count'].astype('float')
    sale_df['product_default_quantity'] = sale_df['product_default_quantity'].astype('float')
    sale_df['count_multiply_by_quantity'] = sale_df['product_default_quantity'] * sale_df['count'] / 1000
    # icustomer
    requested_month = datetime.datetime.strptime(request.data['requested_date'], '%Y-%m-%d').month
    requested_year = datetime.datetime.strptime(request.data['requested_date'], '%Y-%m-%d').year
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                      icustomer_sale_group__date__year=requested_year,
                                                      product__is_active=True).exclude(
        icustomer_sale_group__business__zone_id__in=[11, 13, 15])
    icustomer_sale_list = list(
        icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__business__business_type_id',
                                       'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                       'icustomer_sale_group__session__display_name',
                                       'icustomer_sale_group__ordered_via',
                                       'icustomer_sale_group__ordered_via__name',
                                       'icustomer_sale_group__payment_status__name',
                                       'icustomer_sale_group__sale_status__name', 'icustomer_sale_group__total_cost',
                                       'product__group_id', 'product__quantity', 'product',
                                       'product__name', 'count', 'cost', 'icustomer_sale_group__business__zone_id'))
    icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                             'session_name',
                             'ordered_via_id', 'ordered_via_name', 'payment_status',
                             'sale_status',
                             'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id',
                             'product_name',
                             'count', 'product_cost', 'zone_id']
    icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)
    icustomer_sale_df['count'] = icustomer_sale_df['count'].astype('float')
    icustomer_sale_df['product_default_quantity'] = icustomer_sale_df['product_default_quantity'].astype('float')
    icustomer_sale_df['count_multiply_by_quantity'] = icustomer_sale_df['product_default_quantity'] * icustomer_sale_df[
        'count'] / 1000
    final_df = sale_df.merge(icustomer_sale_df, how="outer")

    product_group_obj = ProductGroup.objects.filter(id__in=[1, 2])
    product_group_list = list(product_group_obj.values_list('id', 'name'))
    product_group_column = ['id', 'name']
    product_group_df = pd.DataFrame(product_group_list, columns=product_group_column)
    product_obj = Product.objects.filter(is_active=True).order_by('display_ordinal')
    product_list = list(product_obj.values_list('id', 'group', 'group__name', 'name', 'short_name', 'code', 'unit',
                                                'unit__display_name', 'description', 'quantity', 'mrp',
                                                'gst_percent', 'snf', 'fat', 'is_homogenised'))
    product_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name', 'product_short_name',
                      'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity', 'product_mrp',
                      'gst_percent', 'snf', 'fat', 'is_homogenised']
    product_df = pd.DataFrame(product_list, columns=product_column)
    session_obj = Session.objects.filter().order_by('id')
    session_list = list(session_obj.values_list('id', 'name', 'display_name', 'expiry_day_before', 'expiry_time'))
    session_column = ['id', 'name', 'display_name', 'expiry_day_before', 'expiry_time']
    session_df = pd.DataFrame(session_list, columns=session_column)
    data_dict['product_dict'] = product_df.groupby('product_group_id').apply(lambda x: x.to_dict('r')).to_dict()
    data_dict['product_group_list'] = product_group_df.to_dict('r')
    data_dict['session_list'] = session_df.to_dict('r')
    master_dict = defaultdict(dict)
    for index, row in final_df.iterrows():
        if not row['session_id'] in master_dict:
            master_dict[row['session_id']] = {}
        if not row['product_group_id'] in master_dict[row['session_id']]:
            master_dict[row['session_id']][row['product_group_id']] = {}
        if not row['product_id'] in master_dict[row['session_id']][row['product_group_id']]:
            master_dict[row['session_id']][row['product_group_id']][row['product_id']] = {
                'count_in_litre': 0,
                'count_in_quantity': 0
            }
        master_dict[row['session_id']][row['product_group_id']][row['product_id']]['count_in_litre'] += row[
            'count_multiply_by_quantity']
        master_dict[row['session_id']][row['product_group_id']][row['product_id']]['count_in_quantity'] += row['count']
    data_dict['live_intent_details'] = master_dict
    route_obj = Route.objects.filter(is_temp_route=False)
    route_list = list(route_obj.values_list('id', 'session', 'name'))
    route_column = ['id', 'session_id', 'route_name']
    route_df = pd.DataFrame(route_list, columns=route_column)
    data_dict['total_route'] = route_df.groupby('session_id')['id'].count().to_dict()
    route_trace_obj = RouteTrace.objects.filter(date=request.data['requested_date'], indent_status_id=3)
    route_trace_list = list(route_trace_obj.values_list('id', 'route__session', 'route__name'))
    route_trace_column = ['route_trace_id', 'session_id', 'route_name']
    route_trace_df = pd.DataFrame(route_trace_list, columns=route_trace_column)
    data_dict['closed_route'] = route_trace_df.groupby('session_id')['route_trace_id'].count().to_dict()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_products_with_mrp(request):
    products = Product.objects.filter(is_active=True)
    product_values = products.values_list('id', 'name', 'mrp', 'private_institute_price', 'govt_institute_price',
                                          'society_price')
    product_columns = ['id', 'name', 'mrp', 'private_institute_price', 'govt_institute_price', 'society_price']
    data = pd.DataFrame(list(product_values), columns=product_columns).to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def generate_booth_code(request):
    print(request.data)
    business_code_obj = BusinessCodeBank.objects.get(business_type_id=request.data['business_type_id'])
    last_code = business_code_obj.last_code
    min_range = business_code_obj.from_code
    max_range = business_code_obj.to_code
    print(min_range)
    print(max_range)
    print(last_code)
    if int(last_code) > int(max_range):
        error = "reached limit"
        return Response(error, status=status.HTTP_200_OK)
    else:
        generated_code = int(last_code) + 1
        return Response(generated_code, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_booth_name_availability(request):
    print(request.data)
    if Business.objects.filter(name=request.data['booth_name']).exists():
        data = False
    else:
        data = True
    return Response(data, status=status.HTTP_200_OK)


def save_business_wise_product_discount(business_id, product_id, discounted_price, user_id):
    print(business_id)
    print(product_id)
    print(discounted_price)
    print(user_id)
    if BusinessWiseProductDiscount.objects.filter(business_id=business_id, product_id=product_id).exists():
        obj = BusinessWiseProductDiscount.objects.get(business_id=business_id, product_id=product_id)
        if BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount=obj, end_date=end_date_for_trace_filter).exists():
            BusinessWiseProductDiscountTrace.objects.filter(business_wise_discount=obj, end_date=end_date_for_trace_filter).update(
                end_date=datetime.datetime.now(),
                product_discount_ended_by_id=user_id
            )

        data = {
            'old_discount_price': obj.discounted_price
        }
        obj.discounted_price = discounted_price
        obj.save()
        data['new_discount_price'] = obj.discounted_price
        data['product_id'] = obj.product_id
        data['business_id'] = obj.business_id

        BusinessWiseProductDiscountTrace.objects.create(
            business_wise_discount=obj,
            end_date=end_date_for_trace_filter,
            start_date=datetime.datetime.now() + timedelta(days=1),
            mrp=Product.objects.get(id=product_id).mrp,
            discounted_price=discounted_price,
            product_discount_started_by_id=user_id
        )
        return Response(status=status.HTTP_200_OK)
    else:
        obj = BusinessWiseProductDiscount.objects.create(
            business_id=business_id,
            product_id=product_id,
            discounted_price=discounted_price,
            created_by_id=user_id,
            modified_by_id=user_id
        )

        BusinessWiseProductDiscountTrace.objects.create(
            business_wise_discount=obj,
            end_date=end_date_for_trace_filter,
            start_date=datetime.datetime.now(),
            mrp=Product.objects.get(id=product_id).mrp,
            discounted_price=discounted_price,
            product_discount_started_by_id=user_id
        )


@api_view(['POST'])
def check_booth_code(request):
    print(request.data)
    data = {}
    if Business.objects.filter(code=request.data['booth_name']).exists():
        print('exists')
        if BusinessAgentMap.objects.filter(business__code=request.data['booth_name']).exists():
            print('already exists')
            data['exists'] = False
            data['mapped'] = True
            data['agent'] = BusinessAgentMap.objects.get(
                business__code=request.data['booth_name']).agent.user_profile.user.first_name
        else:
            data['exists'] = True
    else:
        print('not exists')
        data['mapped'] = False
        data['exists'] = False
    print(data)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def generate_agent_code(request):
    agent_last_id = Agent.objects.all().order_by('-id')[0].id
    print(agent_last_id)
    updated_agent_last = agent_last_id + 1
    return Response(updated_agent_last, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_indent_overall_data(request):
    """
    serve route_count, business/orderbusiness
    :param request:
    :return:
    """
    print(request.data)
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    print(tomorrow_date)
    session_id = request.data['session_id']
    data = {'date': tomorrow_date,
            'session': Session.objects.get(id=session_id).name,
            'overall_data': {'route_count': None,
                             'business_count': None,
                             'ordered_business_count': None,
                             'products': []
                             },
            'icustomer_data': {'icustomer_count': None,
                               'products': []
                               },
            'booth_data': {'booth_count': None,
                           'products': []
                           },
            'booth_types': {},
            'product_group_wise': {},
            'product_ids': []
            }

    route = Route.objects.filter(session_id=session_id, is_temp_route=False)
    route_count = route.count()
    data['overall_data']['route_count'] = route_count
    if RouteTrace.objects.filter(session_id=session_id, date=tomorrow_date).exists():
        data['overall_data']['ordered_route_count'] = RouteTrace.objects.filter(session_id=session_id,
                                                                                date=tomorrow_date).count()
        data['overall_data']['closed_route_count'] = RouteTrace.objects.filter(session_id=session_id,
                                                                               date=tomorrow_date,
                                                                               indent_status_id__in=[2, 3]).count()
    else:
        data['overall_data']['ordered_route_count'] = 0
        data['overall_data']['closed_route_count'] = 0
    business_ids = RouteBusinessMap.objects.filter(route__in=route).values_list('business_id', flat=True)
    business = Business.objects.filter(id__in=business_ids, is_active=True)
    # business_count = business.count()
    data['overall_data']['business_count'] = business.count()
    requested_month = tomorrow_date.month
    requested_year = tomorrow_date.year
    data['icustomer_data']['icustomer_count'] = ICustomerSaleGroup.objects.filter(business__in=business,
                                                                                  date__month=requested_month,
                                                                                  date__year=requested_year,
                                                                                  session_id=session_id).count()
    data['booth_data']['booth_count'] = SaleGroup.objects.filter(business__in=business, date=tomorrow_date,
                                                                 session_id=session_id).count()

    sale_group_business_ids = list(
        SaleGroup.objects.filter(date=tomorrow_date, business__in=business, session_id=session_id).values_list(
            'business_id', flat=True))
    icustomer_sale_group_business_ids = list(
        ICustomerSaleGroup.objects.filter(date__month=tomorrow_date.month, date__year=tomorrow_date.year,
                                          business__in=business, session_id=session_id).values_list(
            'business_id', flat=True))
    data['overall_data']['ordered_business_count'] = len(
        list(set(sale_group_business_ids + icustomer_sale_group_business_ids)))

    # data['overall_data']['ordered_business_count'] = data['icustomer_data']['icustomer_count'] + data['booth_data']['booth_count']

    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
    milk_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(order_category_id=1).values_list('business_type_id', flat=True))

    booth_types = BusinessType.objects.filter(id__in=milk_business_type_ids).order_by('id')
    milk_product_ids = [1, 2, 3, 4, 6, 22, 23, 24]
    curd_product_ids = [7, 10, 21, 25]
    butter_milk_ids = [8, 26, 28]
    lassi_ids = [9]
    data['product_group_wise']['Milk'] = {'unit': 'L', 'count': 0}
    data['product_group_wise']['Curd'] = {'unit': 'Kg', 'count': 0}
    data['product_group_wise']['Butter Milk'] = {'unit': 'L', 'count': 0}
    data['product_group_wise']['Lassi'] = {'unit': 'L', 'count': 0}
    temp = 0
    for product in products:
        # overall
        overall_sum = \
            Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                                product=product).aggregate(
                Sum('count'))['count__sum']
        icustomer_sum = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                     icustomer_sale_group__date__year=requested_year,
                                                     product__is_active=True,
                                                     icustomer_sale_group__session_id=session_id,
                                                     product=product).aggregate(
            Sum('count'))['count__sum']
        if overall_sum is None:
            overall_sum = 0
        if icustomer_sum is None:
            icustomer_sum = 0
        overall_temp_dict = {
            'name': product.short_name,
            'sum': overall_sum + icustomer_sum,
        }
        data['overall_data']['products'].append(overall_temp_dict)

        # icustomer
        only_icustomer_sum = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                          icustomer_sale_group__date__year=requested_year,
                                                          icustomer_sale_group__session_id=session_id, product=product,
                                                          product__is_active=True).aggregate(Sum('count'))['count__sum']
        # icustomer_price_sum = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product=product,  sale_group__icustomer__isnull=False).aggregate(Sum('cost'))['cost__sum']
        icustomer_temp_dict = {
            'name': product.name,
            'sum': only_icustomer_sum,
        }
        # 'price':icustomer_price_sum
        data['icustomer_data']['products'].append(icustomer_temp_dict)

        # booth
        for booth_type in booth_types:
            booth_sum = \
            Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product=product,
                                sale_group__business__business_type__id=booth_type.id).aggregate(Sum('count'))[
                'count__sum']
            # # booth_price_sum = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product=product,  sale_group__icustomer__isnull=True).aggregate(Sum('cost'))['cost__sum']
            booth_temp_dict = {
                'name': product.name,
                'sum': booth_sum,
            }
            # 'price':booth_price_sum
            if not booth_type.name in data['booth_types']:
                data['booth_types'][booth_type.name] = {}
                data['booth_types'][booth_type.name]['product'] = []
            data['booth_types'][booth_type.name]['product'].append(booth_temp_dict)
        if Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                               product_id=product.id).exists():
            sale_obj = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                                           product_id=product.id)
        else:
            sale_obj = None

        if ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                        icustomer_sale_group__date__year=requested_year,
                                        icustomer_sale_group__session_id=session_id, product__is_active=True).exists():
            icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                              icustomer_sale_group__date__year=requested_year,
                                                              icustomer_sale_group__session_id=session_id,
                                                              product__is_active=True)
        else:
            icustomer_sale_obj = None
        if product.id in milk_product_ids:
            if sale_obj is not None:
                calculated_count_for_business = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                                     'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Milk']['count'] += calculated_count_for_business
            if icustomer_sale_obj is not None:
                if icustomer_sale_obj.filter(product_id=product.id).count() != 0:
                    calculated_count_for_icustomer = (icustomer_sale_obj.filter(product_id=product.id).aggregate(
                        Sum('count'))['count__sum'] * int(product.quantity)) / 1000
                    data['product_group_wise']['Milk']['count'] += calculated_count_for_icustomer
            # print(calculated_count_for_business)
            # print(calculated_count_for_icustomer)
            # data['product_group_wise']['Milk']['count'] += calculated_count_for_business + calculated_count_for_icustomer
        elif product.id in curd_product_ids:
            if sale_obj is not None:
                calculated_count = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                        'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Curd']['count'] = data['product_group_wise']['Curd'][
                                                                  'count'] + calculated_count
        elif product.id in butter_milk_ids:
            if sale_obj is not None:
                calculated_count = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                        'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Butter Milk']['count'] = data['product_group_wise']['Butter Milk'][
                                                                         'count'] + calculated_count
        elif product.id in lassi_ids:
            if sale_obj is not None:
                calculated_count = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                        'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Lassi']['count'] = data['product_group_wise']['Lassi'][
                                                                   'count'] + calculated_count

        data['product_ids'] = list(Product.objects.filter(is_active=True).values_list('id', flat=True))
    # data['product_group_wise']['Loose milk'] = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product_id__in=[22,23,24]).aggregate(Sum('count'))['count__sum']
    return Response(data=data, status=status.HTTP_200_OK) 


@api_view(['POST'])
def serve_indent_overall_data_for_old_indent(request):
    """
    serve route_count, business/orderbusiness
    :param request:
    :return:
    """
    print(request.data)
    tomorrow_date = datetime.datetime.strptime(request.data['date'], '%Y-%m-%d')
    session_id = request.data['session_id']
    data = {'date': tomorrow_date,
            'session': Session.objects.get(id=session_id).name,
            'overall_data': {'route_count': None,
                             'business_count': None,
                             'ordered_business_count': None,
                             'products': []
                             },
            'icustomer_data': {'icustomer_count': None,
                               'products': []
                               },
            'booth_data': {'booth_count': None,
                           'products': []
                           },
            'booth_types': {},
            'product_group_wise': {},
            'product_ids': []
            }

    route = Route.objects.filter(session_id=session_id, is_temp_route=False)
    route_count = route.count()
    data['overall_data']['route_count'] = route_count
    if RouteTrace.objects.filter(session_id=session_id, date=tomorrow_date).exists():
        data['overall_data']['ordered_route_count'] = RouteTrace.objects.filter(session_id=session_id,
                                                                                date=tomorrow_date).count()
        data['overall_data']['closed_route_count'] = RouteTrace.objects.filter(session_id=session_id,
                                                                               date=tomorrow_date,
                                                                               indent_status_id__in=[2, 3]).count()
    else:
        data['overall_data']['ordered_route_count'] = 0
        data['overall_data']['closed_route_count'] = 0
    business_ids = RouteBusinessMap.objects.filter(route__in=route).values_list('business_id', flat=True)
    business = Business.objects.filter(id__in=business_ids, is_active=True)
    # business_count = business.count()
    data['overall_data']['business_count'] = business.count()
    requested_month = tomorrow_date.month
    requested_year = tomorrow_date.year
    data['icustomer_data']['icustomer_count'] = ICustomerSaleGroup.objects.filter(business__in=business,
                                                                                  date__month=requested_month,
                                                                                  date__year=requested_year,
                                                                                  session_id=session_id).count()
    data['booth_data']['booth_count'] = SaleGroup.objects.filter(business__in=business, date=tomorrow_date,
                                                                 session_id=session_id).count()

    sale_group_business_ids = list(
        SaleGroup.objects.filter(date=tomorrow_date, business__in=business, session_id=session_id).values_list(
            'business_id', flat=True))
    icustomer_sale_group_business_ids = list(
        ICustomerSaleGroup.objects.filter(date__month=tomorrow_date.month, date__year=tomorrow_date.year,
                                          business__in=business, session_id=session_id).values_list(
            'business_id', flat=True))
    data['overall_data']['ordered_business_count'] = len(
        list(set(sale_group_business_ids + icustomer_sale_group_business_ids)))

    # data['overall_data']['ordered_business_count'] = data['icustomer_data']['icustomer_count'] + data['booth_data']['booth_count']

    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
    booth_types = BusinessType.objects.all().order_by('id')
    milk_product_ids = [1, 2, 3, 4, 6, 22, 23, 24]
    curd_product_ids = [7, 10, 21, 25]
    butter_milk_ids = [8]
    lassi_ids = [9]
    data['product_group_wise']['Milk'] = {'unit': 'L', 'count': 0}
    data['product_group_wise']['Curd'] = {'unit': 'Kg', 'count': 0}
    data['product_group_wise']['Butter Milk'] = {'unit': 'L', 'count': 0}
    data['product_group_wise']['Lassi'] = {'unit': 'L', 'count': 0}
    temp = 0
    for product in products:
        # overall
        overall_sum = \
            Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                                product=product).aggregate(
                Sum('count'))['count__sum']
        icustomer_sum = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                     icustomer_sale_group__date__year=requested_year,
                                                     product__is_active=True,
                                                     icustomer_sale_group__session_id=session_id,
                                                     product=product).aggregate(
            Sum('count'))['count__sum']
        if overall_sum is None:
            overall_sum = 0
        if icustomer_sum is None:
            icustomer_sum = 0
        overall_temp_dict = {
            'name': product.short_name,
            'sum': overall_sum + icustomer_sum,
        }
        data['overall_data']['products'].append(overall_temp_dict)

        # icustomer
        only_icustomer_sum = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                          icustomer_sale_group__date__year=requested_year,
                                                          icustomer_sale_group__session_id=session_id, product=product,
                                                          product__is_active=True).aggregate(Sum('count'))['count__sum']
        # icustomer_price_sum = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product=product,  sale_group__icustomer__isnull=False).aggregate(Sum('cost'))['cost__sum']
        icustomer_temp_dict = {
            'name': product.name,
            'sum': only_icustomer_sum,
        }
        # 'price':icustomer_price_sum
        data['icustomer_data']['products'].append(icustomer_temp_dict)

        # booth
        for booth_type in booth_types:
            booth_sum = \
            Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product=product,
                                sale_group__business__business_type__id=booth_type.id).aggregate(Sum('count'))[
                'count__sum']
            # # booth_price_sum = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product=product,  sale_group__icustomer__isnull=True).aggregate(Sum('cost'))['cost__sum']
            booth_temp_dict = {
                'name': product.name,
                'sum': booth_sum,
            }
            # 'price':booth_price_sum
            if not booth_type.name in data['booth_types']:
                data['booth_types'][booth_type.name] = {}
                data['booth_types'][booth_type.name]['product'] = []
            data['booth_types'][booth_type.name]['product'].append(booth_temp_dict)
        if Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                               product_id=product.id).exists():
            sale_obj = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                                           product_id=product.id)
        else:
            sale_obj = None

        if ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                        icustomer_sale_group__date__year=requested_year,
                                        icustomer_sale_group__session_id=session_id, product__is_active=True).exists():
            icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                              icustomer_sale_group__date__year=requested_year,
                                                              icustomer_sale_group__session_id=session_id,
                                                              product__is_active=True)
        else:
            icustomer_sale_obj = None
        if product.id in milk_product_ids:
            if sale_obj is not None:
                calculated_count_for_business = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                                     'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Milk']['count'] += calculated_count_for_business
            if icustomer_sale_obj is not None:
                if icustomer_sale_obj.filter(product_id=product.id).count() != 0:
                    calculated_count_for_icustomer = (icustomer_sale_obj.filter(product_id=product.id).aggregate(
                        Sum('count'))['count__sum'] * int(product.quantity)) / 1000
                    data['product_group_wise']['Milk']['count'] += calculated_count_for_icustomer
            # print(calculated_count_for_business)
            # print(calculated_count_for_icustomer)
            # data['product_group_wise']['Milk']['count'] += calculated_count_for_business + calculated_count_for_icustomer
        elif product.id in curd_product_ids:
            if sale_obj is not None:
                calculated_count = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                        'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Curd']['count'] = data['product_group_wise']['Curd'][
                                                                  'count'] + calculated_count
        elif product.id in butter_milk_ids:
            if sale_obj is not None:
                calculated_count = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                        'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Butter Milk']['count'] = data['product_group_wise']['Butter Milk'][
                                                                         'count'] + calculated_count
        elif product.id in lassi_ids:
            if sale_obj is not None:
                calculated_count = (sale_obj.filter(product_id=product.id).aggregate(Sum('count'))[
                                        'count__sum'] * int(product.quantity)) / 1000
                data['product_group_wise']['Lassi']['count'] = data['product_group_wise']['Lassi'][
                                                                   'count'] + calculated_count

        data['product_ids'] = list(Product.objects.filter(is_active=True).values_list('id', flat=True))
    # data['product_group_wise']['Loose milk'] = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id, product_id__in=[22,23,24]).aggregate(Sum('count'))['count__sum']
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_indent_route_wise_data(request):
    """
    serve route_count, business/orderbusiness
    :param request:
    :return:
    """
    print(request.data)
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    print(tomorrow_date)
    data = []
    # get
    session_id = request.data['session_id']
    # route
    routes = Route.objects.filter(session_id=session_id, is_temp_route=False)
    route_values = routes.values_list('id', 'name', 'session__expiry_day_before', 'order_expiry_time')
    route_columns = ['id', 'name', 'session_expiry_day_before', 'order_expiry_time']
    route_df = pd.DataFrame(list(route_values), columns=route_columns)

    products = Product.objects.filter(is_active=True).order_by('id')
    product_values = products.values_list('id', 'name', 'short_name')
    product_columns = ['id', 'name', 'short_name']
    product_df = pd.DataFrame(list(product_values), columns=product_columns)

    businesses = Business.objects.filter()
    route_business_map = RouteBusinessMap.objects.filter()

    business_values = RouteBusinessMap.objects.filter().values_list('business', 'route', 'ordinal')
    business_columns = ['business_id', 'route_id', 'ordinal']
    business_df = pd.DataFrame(list(business_values), columns=business_columns)

    # agent_map
    agent_map_values = BusinessAgentMap.objects.filter(is_active=True).values_list('agent', 'business',
                                                                                   'business__code',
                                                                                   'agent__first_name',
                                                                                   'agent__last_name',
                                                                                   'agent__agent_profile__mobile',
                                                                                   'business__zone__name')
    agent_map_columns = ['agent', 'business_id', 'business_code', 'first_name', 'last_name', 'mobile', 'zone_name']
    agent_map_df = pd.DataFrame(list(agent_map_values), columns=agent_map_columns)

    merged_df = pd.merge(business_df, agent_map_df, left_on='business_id', right_on='business_id', how='inner')

    # sale_values
    sale_values = Sale.objects.filter(sale_group__date=tomorrow_date,
                                      sale_group__business_id__in=business_df['business_id'],
                                      sale_group__session_id=session_id, product__is_active=True).values_list(
        'sale_group', 'product_id', 'product__name', 'count', 'sale_group__business', 'sale_group__icustomer')
    sale_columns = ['sale_group', 'product_id', 'product_name', 'count', 'business_id', 'icustomer_id']
    sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)
    sale_df['count'] = sale_df['count'].astype('int')
    for index, route_row in route_df.iterrows():
        business_ids = route_business_map.filter(route=route_row['id']).order_by('ordinal').values_list('business_id',
                                                                                                        flat=True)
        temp_dict = defaultdict(dict)
        temp_dict['route_name'] = route_row['name']
        temp_dict['route_id'] = route_row['id']
        # temp_dict['order_expiry_time'] = route.order_expiry_time
        route_expiry_date = tomorrow_date - datetime.timedelta(days=route_row['session_expiry_day_before'])
        temp_dict['order_expiry_time'] = datetime.datetime.combine(route_expiry_date, route_row['order_expiry_time'])
        # temp_dict['order_expiry_time'] = datetime.datetime.combine(route_expiry_date, route.order_expiry_time).strftime('%m-%d-%Y %H:%M:%S')
        temp_dict['business_count'] = len(list(set(business_ids)))
        temp_dict['order_business_count'] = SaleGroup.objects.filter(date=tomorrow_date, business_id__in=business_ids,
                                                                     session_id=session_id,
                                                                     icustomer__isnull=True).count()
        temp_dict['business'] = []
        temp_dict['products'] = []
        for index, product in product_df.iterrows():
            product_sum = \
            sale_df[(sale_df['business_id'].isin(business_ids)) & (sale_df['product_name'] == product.name)].sum()[
                'count']
            product_temp_dict = {
                'name': product.name,
                'sum': int(product_sum)
            }
            temp_dict['products'].append(product_temp_dict)
        # temp_dict['business']
        # manipulate business data
        filtered_df = merged_df[merged_df['route_id'] == route_row['id']]
        for index, row in filtered_df.iterrows():
            business_sale_df = sale_df[sale_df['business_id'] == row['business_id']]
            business_sale_df = business_sale_df.fillna(0)
            icustomer_business_df = sale_df[
                (sale_df['business_id'] == row['business_id']) & (sale_df['icustomer_id'] != 0)]
            icustomer_business_df = icustomer_business_df.fillna(0)
            only_business_df = sale_df[(sale_df['business_id'] == row['business_id']) & (sale_df['icustomer_id'] == 0)]
            only_business_df = only_business_df.fillna(0)
            business_dict = {
                'id': row['business_id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'business_code': row['business_code'],
                'mobile': row['mobile'],
                'zone_name': row['zone_name'],
                # 'count': row['count'],
                'products': business_sale_df.to_dict('r'),
                'icustomer_products': icustomer_business_df.to_dict('r'),
                'business_products': only_business_df.to_dict('r'),
            }
            #
            temp_dict['business'].append(business_dict)
        # temp_dict['business'] = filtered_df.to_dict('r')
        data.append(temp_dict)

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def prepare_route_indent(request):
    route_id = request.data['route_id']
    session_id = request.data['session_id']
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    for sale in SaleGroup.objects.filter(date=tomorrow_date, route_id=route_id):
        if not Sale.objects.filter(sale_group_id=sale.id).exists():
            SaleGroup.objects.get(id=sale.id).delete()
    if not RouteTrace.objects.filter(route_id=route_id, date=tomorrow_date, session_id=session_id).exists():
        data = {'error_message': 'There is no order for this route'}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        if RouteTrace.objects.get(route_id=route_id, date=tomorrow_date, session_id=session_id).indent_status_id == 2:
            data = {'error_message': 'Closed already'}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)

    route_trace = RouteTrace.objects.get(route_id=route_id, date=tomorrow_date, session_id=session_id)

    route_trace_map = RouteBusinessMap.objects.filter(route_id=route_id).order_by('ordinal')

    calculated_tray_count = check_tray_count(route_id, tomorrow_date, session_id)
    print(calculated_tray_count)
    vehicle_tray_capacity = RouteVehicleMap.objects.get(route_id=route_id).vehicle.tray_capacity
    is_tray_capacity_greater = False
    if calculated_tray_count > vehicle_tray_capacity:
        is_tray_capacity_greater = True
        data_dict = {
            'tray_capasity_status': is_tray_capacity_greater
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        for map in route_trace_map:
            if SaleGroup.objects.filter(date=tomorrow_date, session_id=session_id, business=map.business).exists():
                RouteBusinessTrace.objects.create(route_trace=route_trace, business=map.business, ordinal=map.ordinal)
        route_trace.indent_status_id = 2  # closed
        route_trace.indent_prepare_date_time = datetime.datetime.now()

        if RouteTrace.objects.filter().aggregate(Max('indent_number'))['indent_number__max'] is None:
            route_trace.indent_number = 1
        else:
            max_indent = RouteTrace.objects.filter().aggregate(Max('indent_number'))['indent_number__max']
            new_indent_number = int(max_indent) + 1
            route_trace.indent_number = new_indent_number

        route_trace.save()

        data = {'success_message': 'Indent Closed successfully!',
                'tray_capasity_status': is_tray_capacity_greater}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def close_temp_and_main_route(request):
    route_id = request.data['route_id']
    session_id = request.data['session_id']

    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)

    if not RouteTrace.objects.filter(route_id=route_id, date=tomorrow_date, session_id=session_id).exists():
        data = {'error_message': 'There is no order for this route'}
        return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        if RouteTrace.objects.get(route_id=route_id, date=tomorrow_date, session_id=session_id).indent_status_id == 2:
            data = {'error_message': 'Closed already'}
            return Response(data=data, status=status.HTTP_406_NOT_ACCEPTABLE)

    route_trace = RouteTrace.objects.get(route_id=route_id, date=tomorrow_date, session_id=session_id)

    route_business_map = RouteBusinessMap.objects.filter(route_id=route_id).order_by('ordinal')
    for map in route_business_map:
        if SaleGroup.objects.filter(date=tomorrow_date, session_id=session_id, business=map.business).exists():
            RouteBusinessTrace.objects.create(route_trace=route_trace, business=map.business, ordinal=map.ordinal)
    route_trace.indent_status_id = 2  # closed
    route_trace.indent_prepare_date_time = datetime.datetime.now()

    if RouteTrace.objects.filter().aggregate(Max('indent_number'))['indent_number__max'] is None:
        route_trace.indent_number = 1
    else:
        max_indent = RouteTrace.objects.filter().aggregate(Max('indent_number'))['indent_number__max']
        new_indent_number = int(max_indent) + 1
        route_trace.indent_number = new_indent_number

    route_trace.save()
    temp_route_id = RouteTempRouteMap.objects.get(main_route_id=route_id).temp_route_id
    if RouteBusinessMap.objects.filter(route_id=temp_route_id).count() > 0:
        route_trace = RouteTrace.objects.get(route_id=temp_route_id, date=tomorrow_date, session_id=session_id)

        route_business_map = RouteBusinessMap.objects.filter(route_id=temp_route_id).order_by('ordinal')
        for map in route_business_map:
            if SaleGroup.objects.filter(date=tomorrow_date, session_id=session_id, business=map.business).exists():
                RouteBusinessTrace.objects.create(route_trace=route_trace, business=map.business, ordinal=map.ordinal)
        route_trace.indent_status_id = 2  # closed
        route_trace.indent_prepare_date_time = datetime.datetime.now()
    data = {'success_message': 'Indent Closed successfully!'}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_prepared_indent_route_ids(request):
    print(request.data)
    session_id = request.data['session_id']
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    print('route_ids date = {}'.format(date))
    indent_prepared_route_ids = list(
        RouteTrace.objects.filter(date=date, indent_status_id=2, session_id=session_id).values_list('route_id',
                                                                                                    flat=True))  # closed
    data = {'indent_prepared_route_ids': indent_prepared_route_ids}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_route_indent_details(request):
    print(request.data)
    session_id = request.data['session_id']
    route_id = request.data['route_id']
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)

    products = Product.objects.filter(is_active=True)
    data = {
        'product_details': [],
        'route_details': {}
    }
    route = Route.objects.get(id=route_id)
    data['route_details']['name'] = route.name
    data['route_details']['session'] = route.session.name
    data['route_details']['order_expiry_time'] = route.order_expiry_time

    route_trace = RouteTrace.objects.get(route_id=route_id, date=date)
    data['route_details']['driver_name'] = route_trace.driver_name
    data['route_details']['driver_phone'] = route_trace.driver_phone
    data['route_details']['indent_number'] = route_trace.indent_number
    data['route_details']['vehicle_licence_number'] = route_trace.vehicle.licence_number
    data['route_details']['date'] = date
    for product in products:
        quantity = \
        Sale.objects.filter(sale_group__date=date, sale_group__session_id=session_id, product=product).aggregate(
            Sum('count'))['count__sum']
        if quantity is not None:
            temp_dict = {
                'product_name': product.name + str(product.quantity),
                'quantity': quantity,
            }
            data['product_details'].append(temp_dict)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_vehicle_assigned_to_another_route(request):
    print(request.data)
    data = 'success'
    # new route
    if request.data['route_id'] == None:
        if RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                          route__session_id=request.data['session_id']).exists():
            route_name = RouteVehicleMap.objects.get(vehicle_id=request.data['vehicle_id'],
                                                     route__session_id=request.data['session_id']).route.name
            data = 'already the vehicle has been assigned to ' + route_name
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = 'please confirm this vehicle to assign to this route'
    # update route
    else:
        if RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                          route__session_id=request.data['session_id']).exclude(
                route_id=request.data['route_id']).exists():
            route_name = RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'],
                                                     route__session_id=request.data['session_id']).exclude(
                route_id=request.data['route_id']).first().route.name
            data = 'already the vehicle has been assigned to ' + route_name
        else:
            data = 'Please confirm with OK to update'

    return Response(data=data, status=status.HTTP_200_OK)


def serve_product_availability():
    product_availabiliy_map = ProductAvailabilityMap.objects.filter(product__is_active=True)
    product_availablly_list = list(
        product_availabiliy_map.values_list('id', 'product_id', 'session_id', 'is_available'))
    product_availabiliy_column = ['id', 'product_id', 'session_id', 'is_available']
    product_availabiliy_df = pd.DataFrame(product_availablly_list, columns=product_availabiliy_column)
    master_dict = {}
    for index, row in product_availabiliy_df.iterrows():
        if not row['session_id'] in master_dict:
            master_dict[row['session_id']] = {}
        if not row['product_id'] in master_dict[row['session_id']]:
            master_dict[row['session_id']][row['product_id']] = row['is_available']
    return master_dict


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_business_type(request):
    data_dict = {}
    business_type_obj = BusinessType.objects.filter().exclude(id=6).exclude(id=7).exclude(id=3).order_by('id')
    business_type_list = list(business_type_obj.values_list('id', 'name', 'description'))
    business_type_column = ['id', 'name', 'description']
    business_type_df = pd.DataFrame(business_type_list, columns=business_type_column)
    data_dict['business_type'] = business_type_df.to_dict('r')
    document_type_obj = DocumentTypeCv.objects.filter(is_active=True)
    document_type_list = list(document_type_obj.values_list('id', 'name'))
    document_type_column = ['id', 'name']
    document_type_df = pd.DataFrame(document_type_list, columns=document_type_column)
    document_type_df['document_value'] = None
    data_dict['document_type'] = document_type_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def check_phone_number_exists_on_agent_request_form(request):
    if AgentRequest.objects.filter(phone=request.data['phone_number']).exists():
        data_dict = {
            'is_exists': True
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict = {
            'is_exists': False
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def save_agent_request_form(request):
    form_values = request.data['form_values']
    agent_request_obj = AgentRequest(first_name=form_values['first_name'],
                                     last_name=form_values['last_name'],
                                     address=form_values['address'],
                                     pincode=form_values['pincode'],
                                     phone=form_values['phone_number'],
                                     business_type_id=form_values['booth_type'],
                                     date=datetime.datetime.now(),
                                     )
    agent_request_obj.save()
    for document_type in request.data['document_value']:
        if document_type['document_value'] is not None:
            agent_request_document_map_obj = AgentRequestDocumentMap(
                document_type_id=document_type['id'],
                agent_request_id=agent_request_obj.id
            )
            agent_request_document_map_obj.request_document_value = decode_image(document_type['document_value'],
                                                                                 agent_request_obj.first_name)
            agent_request_document_map_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_product_availability_for_portal(request):
    master_dict = serve_product_availability()
    return Response(master_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_product_availability(request):
    print(request.data)
    ProductAvailabilityMap.objects.filter(product_id=request.data['product_id'],
                                          session_id=request.data['session_id']).update(
        is_available=request.data['availability']
    )
    data = "product availability is updated"
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def check_icustomer_details(request):
    print(request.data)
    data = {}
    if ICustomer.objects.filter(user_profile__mobile=request.data['icustomer_number']).exists():
        customer_found = True
        icustomer = ICustomer.objects.get(user_profile__mobile=request.data['icustomer_number'])

    elif ICustomer.objects.filter(customer_code__iexact=request.data['icustomer_code']).exists():
        icustomer = ICustomer.objects.filter(customer_code__iexact=request.data['icustomer_code'])[0]
        customer_found = True

    else:
        customer_found = False
        data['found'] = False

    if customer_found:
        data['found'] = True
        data['icustomer_id'] = icustomer.id
        data['icustomer_code'] = icustomer.customer_code
        data['first_name'] = icustomer.user_profile.user.first_name
        data['last_name'] = icustomer.user_profile.user.last_name
        data['mobile'] = icustomer.user_profile.mobile
        data['customer_type_name'] = icustomer.customer_type.name
        data['address'] = icustomer.user_profile.street
        data['taluk'] = icustomer.user_profile.taluk.name
        data['district'] = icustomer.user_profile.district.name
        data['pincode'] = icustomer.user_profile.pincode
        data['user_profile_id'] = icustomer.user_profile.id
        data['user_id'] = icustomer.user_profile.user.id
        data['wallet_amount'] = ICustomerWallet.objects.get(customer_id=icustomer.id).current_balance
        try:
            insurance_image_path = 'static/media/' + str(icustomer.user_profile.image)
            # print(image_path)
            with open(insurance_image_path, 'rb') as image_file:
                insurance_encoded_image = b64encode(image_file.read())
                data['image'] = 'data:image/jpeg;base64,' + insurance_encoded_image.decode("utf-8")
        except Exception as err:
            print(err)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_unordered_and_ordered_booth_for_zone(request):
    print(request.data)
    business_ids = list(Business.objects.filter(zone_id=request.data['zone_id']).values_list('id', flat=True))
    ordered_business_ids = list(
        SaleGroup.objects.filter(business_id__in=business_ids, date=request.data['requested_date']).values_list(
            'business_id', flat=True))
    ordered_sale_group_ids = list(
        SaleGroup.objects.filter(business_id__in=business_ids, date=request.data['requested_date']).values_list(
            'id', flat=True))

    sale_obj = Sale.objects.filter(sale_group_id__in=ordered_sale_group_ids)
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost',
                             'product__group_id', 'product__quantity', 'product',
                             'product__name', 'count', 'cost', 'sale_group__business__zone_id'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id', 'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_default_quantity', 'product_id', 'product_name',
                   'count', 'product_cost', 'zone_id']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['count'] = sale_df['count'].astype('float')
    sale_df['product_default_quantity'] = sale_df['product_default_quantity'].astype('float')
    sale_df['count_multiply_by_quantity'] = sale_df['product_default_quantity'] * sale_df['count'] / 1000

    ordered_business_ids = list(dict.fromkeys(ordered_business_ids))
    ordered_business_obj = BusinessAgentMap.objects.filter(business__id__in=ordered_business_ids)
    ordered_business_list = list(
        ordered_business_obj.values_list('business_id', 'business__code', 'business__zone', 'business__zone__name',
                                         'business__name', 'business__constituency', 'business__constituency__name',
                                         'business__ward', 'business__ward__name', 'business__address',
                                         'business__location_category', 'business__location_category__name',
                                         'business__location_category_value', 'business__pincode', 'business__landmark',
                                         'business__working_hours_from', 'business__working_hours_to',
                                         'business__latitude',
                                         'business__longitude', 'agent__first_name',
                                         'agent__last_name', 'agent__agent_profile__mobile'))
    ordered_business_column = ['business_id', 'code', 'zone_id', 'zone_name', 'name', 'constituency_id',
                               'constituency_name',
                               'ward_id', 'ward_name', 'address', 'location_category_id', 'location_category_name',
                               'location_category_value', 'pincode', 'landmark', 'working_hours_from',
                               'working_hours_to',
                               'latitude', 'longitude', 'agent_first_name', 'agent_last_name', 'agent_mobile_number']
    ordered_business_df = pd.DataFrame(ordered_business_list, columns=ordered_business_column)
    ordered_business_df['working_hours_from'] = ordered_business_df['working_hours_from'].apply(
        lambda x: x.strftime("%I:%M:%S %p"))
    ordered_business_df['working_hours_to'] = ordered_business_df['working_hours_to'].apply(
        lambda x: x.strftime("%I:%M:%S %p"))
    ordered_business_df['order_status'] = True
    unordered_business_obj = BusinessAgentMap.objects.filter(business__id__in=business_ids).exclude(
        business__id__in=ordered_business_ids)
    unordered_business_list = list(
        unordered_business_obj.values_list('business_id', 'business__code', 'business__zone', 'business__zone__name',
                                           'business__name', 'business__constituency', 'business__constituency__name',
                                           'business__ward', 'business__ward__name', 'business__address',
                                           'business__location_category', 'business__location_category__name',
                                           'business__location_category_value', 'business__pincode',
                                           'business__landmark',
                                           'business__working_hours_from', 'business__working_hours_to',
                                           'business__latitude',
                                           'business__longitude', 'agent__first_name',
                                           'agent__last_name', 'agent__agent_profile__mobile'))
    unordered_business_column = ['business_id', 'code', 'zone_id', 'zone_name', 'name', 'constituency_id',
                                 'constituency_name',
                                 'ward_id', 'ward_name', 'address', 'location_category_id', 'location_category_name',
                                 'location_category_value', 'pincode', 'landmark', 'working_hours_from',
                                 'working_hours_to',
                                 'latitude', 'longitude', 'agent_first_name', 'agent_last_name', 'agent_mobile_number']
    unordered_business_df = pd.DataFrame(unordered_business_list, columns=unordered_business_column)
    unordered_business_df['working_hours_from'] = unordered_business_df['working_hours_from'].apply(
        lambda x: x.strftime("%I:%M:%S %p"))
    unordered_business_df['working_hours_to'] = unordered_business_df['working_hours_to'].apply(
        lambda x: x.strftime("%I:%M:%S %p"))
    unordered_business_df['order_status'] = False
    # combined_df = pd.concat([ordered_business_df, unordered_business_df]).sort_values(by=['order_status'],
    #                                                                                   ascending=False)
    data_dict = {
        'ordered_business_list': ordered_business_df.to_dict('r'),
        'unordered_business_list': unordered_business_df.to_dict('r'),
        'ordered_quantity_in_litre': None
    }
    if not sale_df.empty:
        data_dict['ordered_quantity_in_litre'] = sale_df['count_multiply_by_quantity'].sum()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_zone_under_employee(request):
    zone_obj = Zone.objects.filter().order_by('id')
    zone_list = list(zone_obj.values_list('id', 'name'))
    zone_column = ['id', 'zone_name']
    zone_df = pd.DataFrame(zone_list, columns=zone_column)
    return Response(data=zone_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_route_vehicle_map(request):
    routes = Route.objects.filter(is_temp_route=False)
    route_values = list(routes.values_list('id', 'name', 'session_id', 'session__name'))
    route_columns = ['route_id', 'name', 'session_id', 'session_name']
    route_df = pd.DataFrame(route_values, columns=route_columns)

    route_vehicle_map = RouteVehicleMap.objects.filter()
    route_vehicle_values = list(route_vehicle_map.values_list('id', 'route__id', 'vehicle__code'))
    route_vehicle_columns = ['route_vehicle_id', 'route_id', 'vehicle_code']
    route_vehicle_df = pd.DataFrame(route_vehicle_values, columns=route_vehicle_columns)

    final_df = route_df.merge(route_vehicle_df, on="route_id", how='outer')
    final_df = final_df.fillna('N/A')
    master_list = []
    for index, row in final_df.iterrows():
        route_dict = {}
        route_dict['name'] = row['name']
        route_dict[row['session_name']] = row['vehicle_code']
        master_list.append(route_dict)
    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_business_ordinal_in_route_map(request):
    print(request.data)
    if request.data['operation'] == 'ordinal_update':
        print('old_ordinal_place', request.data['selected_business']['ordinal'])
        print('new_ordinal', request.data['current_index'] + 1)
        present_ordinal = request.data['selected_business']['ordinal']
        updated_ordinal = request.data['current_index'] + 1
        if present_ordinal > updated_ordinal:
            route_ordinals_update_objs = RouteBusinessMap.objects.filter(route_id=request.data['selected_route_id'],
                                                                         ordinal__gte=updated_ordinal,
                                                                         ordinal__lt=present_ordinal).order_by(
                'ordinal')
            for route_map_obj in route_ordinals_update_objs:
                print(route_map_obj.ordinal)
                route_map_obj.ordinal = route_map_obj.ordinal + 1
                route_map_obj.save()
            RouteBusinessMap.objects.filter(business_id=request.data['selected_business']['id']).update(
                ordinal=request.data['current_index'] + 1)
        if present_ordinal < updated_ordinal:
            route_ordinals_update_objs = RouteBusinessMap.objects.filter(route_id=request.data['selected_route_id'],
                                                                         ordinal__gt=present_ordinal,
                                                                         ordinal__lte=updated_ordinal).order_by(
                'ordinal')
            for route_map_obj in route_ordinals_update_objs:
                print(route_map_obj.ordinal)
                route_map_obj.ordinal = route_map_obj.ordinal - 1
                route_map_obj.save()
            RouteBusinessMap.objects.filter(business_id=request.data['selected_business']['id']).update(
                ordinal=request.data['current_index'] + 1)
    elif request.data['operation'] == 'remove_business':
        ordinal_value = RouteBusinessMap.objects.get(route_id=request.data['route_id'],
                                                     business_id=request.data['business_id']).ordinal
        print(ordinal_value)
        route_map_objs = RouteBusinessMap.objects.filter(route_id=request.data['route_id'], ordinal__gt=ordinal_value)
        for route_map_obj in route_map_objs:
            route_map_obj.ordinal = route_map_obj.ordinal - 1
            route_map_obj.save()
            print(route_map_obj.ordinal)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_last_seven_days_data_for_aavin_today(request):
    data_dict = {}
    color_pallets = ['#ffffff', '#e07d04']
    today = datetime.datetime.now()
    end_date = today + timedelta(days=1)
    start_date = today - timedelta(days=6)
    sale_obj = Sale.objects.filter(sale_group__date__gte=start_date, sale_group__date__lte=end_date,
                                   product__group_id=1, product__is_active=True)
    sale_list = list(
        sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__business_type_id',
                             'sale_group__date', 'sale_group__session',
                             'sale_group__session__display_name', 'sale_group__ordered_via',
                             'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                             'sale_group__sale_status__name', 'sale_group__total_cost', 'product__group_id',
                             'product__group__name', 'product__quantity', 'product',
                             'product__name', 'count', 'cost'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                   'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'product_group_id', 'product_group_name', 'product_default_quantity',
                   'product_id', 'product_name', 'count', 'product_cost']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)

    final_icustomer_df = pd.DataFrame(
        columns=['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id', 'session_name',
                 'ordered_via_id', 'ordered_via_name', 'payment_status',
                 'sale_status',
                 'session_wise_price', 'product_group_id', 'product_group_name', 'product_default_quantity',
                 'product_id', 'product_name',
                 'count', 'product_cost'])
    for single_date in selected_date_range(start_date + timedelta(days=1), end_date + timedelta(days=1)):
        date = single_date.strftime("%Y-%m-%d")
        requested_month = datetime.datetime.strptime(date, '%Y-%m-%d').month
        requested_year = datetime.datetime.strptime(date, '%Y-%m-%d').year
        icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=requested_month,
                                                          icustomer_sale_group__date__year=requested_year,
                                                          product__is_active=True)
        icustomer_sale_list = list(
            icustomer_sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                           'icustomer_sale_group__business__business_type_id',
                                           'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                           'icustomer_sale_group__session__display_name',
                                           'icustomer_sale_group__ordered_via',
                                           'icustomer_sale_group__ordered_via__name',
                                           'icustomer_sale_group__payment_status__name',
                                           'icustomer_sale_group__sale_status__name',
                                           'icustomer_sale_group__total_cost',
                                           'product__group_id', 'product__group__name', 'product__quantity', 'product',
                                           'product__name', 'count', 'cost'))
        icustomer_sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                                 'session_name',
                                 'ordered_via_id', 'ordered_via_name', 'payment_status',
                                 'sale_status',
                                 'session_wise_price', 'product_group_id', 'product_group_name',
                                 'product_default_quantity', 'product_id',
                                 'product_name',
                                 'count', 'product_cost']

        icustomer_sale_df = pd.DataFrame(icustomer_sale_list, columns=icustomer_sale_column)
        icustomer_sale_df['date'] = date
        final_icustomer_df = final_icustomer_df.append(icustomer_sale_df)
    final_df = sale_df.merge(final_icustomer_df, how="outer")

    final_df['count'] = final_df['count'].astype('float')
    final_df['date'] = final_df['date'].astype('str')
    final_df['product_default_quantity'] = final_df['product_default_quantity'].astype('float')
    final_df['count_multiply_by_quantity'] = final_df['product_default_quantity'] * final_df['count'] / 1000

    master_dict_product_group = defaultdict(dict)
    master_dict_product_group['label'] = 'Milk'
    master_dict_product_group['data'] = []
    master_dict_product_group['backgroundColor'] = color_pallets[1]
    master_dict_product_group['borderColor'] = color_pallets[1]
    master_dict_product_group['pointBorderColor'] = color_pallets[1]
    master_dict_product_group['pointHoverBackgroundColor'] = color_pallets[1]
    master_dict_product_group['pointHoverBorderColor'] = color_pallets[1]
    master_dict_product_group['fill'] = False
    master_dict_product_group['lineTension'] = 0.1
    master_dict_product_group['borderCapStyle'] = 'butt'
    master_dict_product_group['borderDash'] = []
    master_dict_product_group['borderDashOffset'] = 0.0
    master_dict_product_group['borderJoinStyle'] = 'miter'
    master_dict_product_group['pointBorderWidth'] = 1
    master_dict_product_group['pointHoverRadius'] = 5
    master_dict_product_group['pointHoverBorderWidth'] = 2
    master_dict_product_group['pointRadius'] = 1
    master_dict_product_group['pointHitRadius'] = 10
    master_dict_product_group['spanGaps'] = False
    for single_date in selected_date_range(start_date + timedelta(days=1), end_date + timedelta(days=1)):
        date = single_date.strftime("%Y-%m-%d")
        filtered_df = final_df[final_df['date'] == date]
        if not filtered_df.empty:
            master_dict_product_group['data'].append(filtered_df['count_multiply_by_quantity'].sum())
        else:
            master_dict_product_group['data'].append(0)
    date_range_df = pd.date_range(start_date + timedelta(days=1), freq='D', periods=7)
    date_range_df = date_range_df.day_name()
    days_list = [days[:3] for days in date_range_df.to_list()]
    data_dict['milk_product_data'] = {}
    data_dict['milk_product_data']['datasets'] = [master_dict_product_group]
    data_dict['milk_product_data']['labels'] = days_list
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_all_route_wise_data(request):
    print(request.data)
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    print(tomorrow_date)
    data = []
    # get
    session_id = request.data['session_id']
    routes = Route.objects.filter(session_id=session_id, is_temp_route=False).order_by('name')
    route_values = routes.values_list('id', 'name', 'session__expiry_day_before', 'order_expiry_time')
    route_columns = ['id', 'name', 'session_expiry_day_before', 'order_expiry_time']
    route_df = pd.DataFrame(list(route_values), columns=route_columns)
    products = Product.objects.filter(is_active=True).order_by('display_ordinal')

    # business_values = RouteBusinessMap.objects.filter().values_list('business', 'route', 'ordinal')
    # business_columns = ['business_id', 'route_id', 'ordinal']
    # business_df = pd.DataFrame(list(business_values), columns=business_columns)

    route_trace = RouteTrace.objects.filter(session_id=session_id, date=tomorrow_date, route__is_temp_route=False)
    route_trace_values = route_trace.values_list('indent_status', 'route_id')
    route_trace_columns = ['indent_status', 'id']
    route_trace_df = pd.DataFrame(list(route_trace_values), columns=route_trace_columns)

    route_business_df = route_df.merge(route_trace_df, on="id", how='outer')
    # route_business_df = route_business_df.sort_values(by='indent_status', ascending=True)
    route_business_df = route_business_df.fillna(0)
    # route_business_df = pd.merge(route_df, route_trace_df, left_on='id', right_on='route_id', how='inner')
    # sale_values = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__business_id__in=business_df['business_id'],
    #                                 sale_group__session_id=session_id).values_list('sale_group', 'product__name',
    #                                                                                 'count', 'sale_group__business')
    # sale_columns = ['sale_group', 'product_name', 'count', 'business_id']
    # sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)
    sales = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                                product__is_active=True)
    icustomer_sales = ICustomerSale.objects.filter(icustomer_sale_group__date__month=tomorrow_date.month,
                                                   icustomer_sale_group__date__year=tomorrow_date.year,
                                                   icustomer_sale_group__session_id=session_id, product__is_active=True)
    for index, row in route_business_df.iterrows():
        business_ids = list(RouteBusinessMap.objects.filter(route_id=row['id']).order_by('ordinal').values_list(
            'business_id', flat=True))
        sale_group_business_ids = list(SaleGroup.objects.filter(route_id=row['id'], date=tomorrow_date).values_list('business_id', flat=True))
        merged_business_ids = list(set(business_ids + sale_group_business_ids))
        temp_dict = defaultdict(dict)
        temp_dict['route_name'] = row['name']
        temp_dict['indent_status'] = row['indent_status']
        temp_dict['route_id'] = row['id']
        temp_dict['temp_route_id'] = RouteTempRouteMap.objects.get(main_route_id=row['id']).temp_route.id
        route_expiry_date = tomorrow_date - datetime.timedelta(days=row['session_expiry_day_before'])
        temp_dict['order_expiry_time'] = datetime.datetime.combine(route_expiry_date, row['order_expiry_time'])
        temp_dict['business_count'] = len(list(set(merged_business_ids)))
        sale_group_business_ids = list(SaleGroup.objects.filter(date=tomorrow_date, business_id__in=merged_business_ids,
                                                                session_id=session_id).values_list('business_id',
                                                                                                   flat=True))
        icustomer_sale_group_business_ids = list(
            ICustomerSaleGroup.objects.filter(date__month=tomorrow_date.month, date__year=tomorrow_date.year,
                                              business_id__in=merged_business_ids, session_id=session_id).values_list(
                'business_id', flat=True))
        temp_dict['order_business_count'] = len(list(set(sale_group_business_ids + icustomer_sale_group_business_ids)))
        temp_dict['products'] = []
        temp_dict['icustomer_products'] = []
        temp_dict['business_products'] = []
        for product in products:
            product_sum = \
            sales.filter(sale_group__business_id__in=merged_business_ids, product=product).aggregate(Sum('count'))[
                'count__sum']
            icustomer_product_sum = \
            icustomer_sales.filter(icustomer_sale_group__business_id__in=merged_business_ids, product=product).aggregate(
                Sum('count'))['count__sum']
            if product_sum is None:
                product_sum = 0
            if icustomer_product_sum is None:
                icustomer_product_sum = 0
            product_temp_dict = {
                'name': product.short_name,
                'sum': product_sum + icustomer_product_sum
                # 'cost':product_cost
            }
            temp_dict['products'].append(product_temp_dict)

            icustomer_product_sum = \
            icustomer_sales.filter(icustomer_sale_group__business_id__in=merged_business_ids, product=product).aggregate(
                Sum('count'))['count__sum']
            icustomer_product_temp_dict = {
                'name': product.short_name,
                'sum': icustomer_product_sum
                # 'cost':icustomer_product_cost
            }
            temp_dict['icustomer_products'].append(icustomer_product_temp_dict)

            business_product_sum = \
            sales.filter(sale_group__business_id__in=merged_business_ids, product=product).aggregate(Sum('count'))[
                'count__sum']
            business_product_temp_dict = {
                'name': product.short_name,
                'sum': business_product_sum
                # 'cost':business_product_cost
            }
            temp_dict['business_products'].append(business_product_temp_dict)
        data.append(temp_dict)
    return Response(data, status=status.HTTP_200_OK)
 

@api_view(['POST'])
def serve_all_route_wise_data_for_old_indent(request):
    print(request.data)
    tomorrow_date = datetime.datetime.strptime(request.data['date'], '%Y-%m-%d')
    data = []
    # get
    session_id = request.data['session_id']
    routes = Route.objects.filter(session_id=session_id, is_temp_route=False).order_by('name')
    route_values = routes.values_list('id', 'name', 'session__expiry_day_before', 'order_expiry_time')
    route_columns = ['id', 'name', 'session_expiry_day_before', 'order_expiry_time']
    route_df = pd.DataFrame(list(route_values), columns=route_columns)
    products = Product.objects.filter(is_active=True).order_by('display_ordinal')

    # business_values = RouteBusinessMap.objects.filter().values_list('business', 'route', 'ordinal')
    # business_columns = ['business_id', 'route_id', 'ordinal']
    # business_df = pd.DataFrame(list(business_values), columns=business_columns)

    route_trace = RouteTrace.objects.filter(session_id=session_id, date=tomorrow_date, route__is_temp_route=False)
    route_trace_values = route_trace.values_list('indent_status', 'route_id')
    route_trace_columns = ['indent_status', 'id']
    route_trace_df = pd.DataFrame(list(route_trace_values), columns=route_trace_columns)

    route_business_df = route_df.merge(route_trace_df, on="id", how='outer')
    route_business_df = route_business_df.sort_values(by='indent_status', ascending=True)
    route_business_df = route_business_df.fillna(0)
    # route_business_df = pd.merge(route_df, route_trace_df, left_on='id', right_on='route_id', how='inner')
    # sale_values = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__business_id__in=business_df['business_id'],
    #                                 sale_group__session_id=session_id).values_list('sale_group', 'product__name',
    #                                                                                 'count', 'sale_group__business')
    # sale_columns = ['sale_group', 'product_name', 'count', 'business_id']
    # sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)
    sales = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                                product__is_active=True)
    icustomer_sales = ICustomerSale.objects.filter(icustomer_sale_group__date__month=tomorrow_date.month,
                                                   icustomer_sale_group__date__year=tomorrow_date.year,
                                                   icustomer_sale_group__session_id=session_id, product__is_active=True)
    route_business_df = route_business_df.sort_values(by=['name'])
    for index, row in route_business_df.iterrows():
        business_ids = []
        # business_ids = list(RouteBusinessMap.objects.filter(route_id=row['id']).order_by('ordinal').values_list(
        #     'business_id', flat=True))
        sale_group_business_ids = list(SaleGroup.objects.filter(route_id=row['id'], date=tomorrow_date).values_list('business_id', flat=True))
        merged_business_ids = list(set(business_ids + sale_group_business_ids))
        temp_dict = defaultdict(dict)
        temp_dict['route_name'] = row['name']
        temp_dict['indent_status'] = row['indent_status']
        temp_dict['route_id'] = row['id']
        temp_dict['temp_route_id'] = RouteTempRouteMap.objects.get(main_route_id=row['id']).temp_route.id
        route_expiry_date = tomorrow_date - datetime.timedelta(days=row['session_expiry_day_before'])
        temp_dict['order_expiry_time'] = datetime.datetime.combine(route_expiry_date, row['order_expiry_time'])
        temp_dict['business_count'] = len(list(set(merged_business_ids)))
        sale_group_business_ids = list(SaleGroup.objects.filter(date=tomorrow_date, business_id__in=merged_business_ids,
                                                                session_id=session_id).values_list('business_id',
                                                                                                   flat=True))
        icustomer_sale_group_business_ids = list(
            ICustomerSaleGroup.objects.filter(date__month=tomorrow_date.month, date__year=tomorrow_date.year,
                                              business_id__in=merged_business_ids, session_id=session_id).values_list(
                'business_id', flat=True))
        temp_dict['order_business_count'] = len(list(set(sale_group_business_ids + icustomer_sale_group_business_ids)))
        temp_dict['products'] = []
        temp_dict['icustomer_products'] = []
        temp_dict['business_products'] = []
        for product in products:
            product_sum = \
            sales.filter(sale_group__business_id__in=merged_business_ids, product=product).aggregate(Sum('count'))[
                'count__sum']
            icustomer_product_sum = \
            icustomer_sales.filter(icustomer_sale_group__business_id__in=merged_business_ids, product=product).aggregate(
                Sum('count'))['count__sum']
            if product_sum is None:
                product_sum = 0
            if icustomer_product_sum is None:
                icustomer_product_sum = 0
            product_temp_dict = {
                'name': product.short_name,
                'sum': product_sum + icustomer_product_sum
                # 'cost':product_cost
            }
            temp_dict['products'].append(product_temp_dict)

            icustomer_product_sum = \
            icustomer_sales.filter(icustomer_sale_group__business_id__in=merged_business_ids, product=product).aggregate(
                Sum('count'))['count__sum']
            icustomer_product_temp_dict = {
                'name': product.short_name,
                'sum': icustomer_product_sum
                # 'cost':icustomer_product_cost
            }
            temp_dict['icustomer_products'].append(icustomer_product_temp_dict)

            business_product_sum = \
            sales.filter(sale_group__business_id__in=merged_business_ids, product=product).aggregate(Sum('count'))[
                'count__sum']
            business_product_temp_dict = {
                'name': product.short_name,
                'sum': business_product_sum
                # 'cost':business_product_cost
            }
            temp_dict['business_products'].append(business_product_temp_dict)
        data.append(temp_dict)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_intent_for_business_wise(request):
    print(request.data)
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    print(tomorrow_date)
    route_id = request.data['route_id']
    session_id = request.data['session_id']
    # business_ids = RouteBusinessMap.objects.filter(route_id=route_id).order_by('ordinal').values_list('business_id', flat=True)
    #
    business_values = RouteBusinessMap.objects.filter(route_id=route_id).values_list('business', 'route', 'ordinal')
    business_columns = ['business_id', 'route_id', 'ordinal']
    business_df = pd.DataFrame(list(business_values), columns=business_columns)

    # print(business_df.count())

    agent_map_values = BusinessAgentMap.objects.filter(is_active=True).values_list('agent', 'business',
                                                                                   'business__business_type__name',
                                                                                   'business__code',
                                                                                   'agent__first_name',
                                                                                   'agent__last_name',
                                                                                   'agent__agent_profile__mobile',
                                                                                   'business__zone__name')
    agent_map_columns = ['agent', 'business_id', 'business_type_name', 'business_code', 'first_name', 'last_name',
                         'mobile', 'zone_name']
    agent_map_df = pd.DataFrame(list(agent_map_values), columns=agent_map_columns)

    merged_df = pd.merge(business_df, agent_map_df, left_on='business_id', right_on='business_id', how='inner')

    # sale_values = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__business_id__in=business_df['business_id'],
    #                                     sale_group__session_id=session_id).values_list('sale_group', 'product__name',
    #                                                                                     'count', 'sale_group__business')
    # sale_columns = ['sale_group', 'product_name', 'count', 'business_id']
    # sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)

    route_session_expiry_day_before = Route.objects.get(id=route_id).session.expiry_day_before
    route_expiry_date = tomorrow_date - datetime.timedelta(days=route_session_expiry_day_before)
    route_expiry_date
    temp_dict = []

    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
    sales = Sale.objects.filter(sale_group__date=tomorrow_date, sale_group__session_id=session_id,
                                product__is_active=True)
    icustomer_sales = ICustomerSale.objects.filter(icustomer_sale_group__date__month=tomorrow_date.month,
                                                   icustomer_sale_group__date__year=tomorrow_date.year,
                                                   product__is_active=True,
                                                   icustomer_sale_group__session_id=session_id)
    for index, row in merged_df.iterrows():
        business_dict = {
            'first_name': row['first_name'],
            'business_code': row['business_code'],
            'business_type_name': row['business_type_name'],
            'business_id': row['business_id'],
            'last_name': row['last_name'],
            'mobile': row['mobile'],
            'zone_name': row['zone_name'],
            'product': [],
            'icustomer_product': [],
            'business_product': []

        }
        for product in products:
            product_sum = \
                sales.filter(sale_group__business_id=row['business_id'], product=product).aggregate(Sum('count'))[
                    'count__sum']
            icustomer_product_sum = \
                icustomer_sales.filter(icustomer_sale_group__business_id=row['business_id'], product=product).aggregate(
                    Sum('count'))['count__sum']
            if product_sum is None:
                product_sum = 0
            if icustomer_product_sum is None:
                icustomer_product_sum = 0
            product_temp_dict = {
                'name': product.name,
                'sum': product_sum + icustomer_product_sum,
                # 'cost': product_cost
            }
            business_dict['product'].append(product_temp_dict)
            icustomer_product_sum = \
            icustomer_sales.filter(icustomer_sale_group__business_id=row['business_id'], product=product).aggregate(
                Sum('count'))['count__sum']
            icustomers_product_temp_dict = {
                'name': product.name,
                'sum': icustomer_product_sum,
                # 'cost': icustomers_product_cost
            }
            business_dict['icustomer_product'].append(icustomers_product_temp_dict)

            business_product_sum = \
            Sale.objects.filter(sale_group__business_id=row['business_id'], product=product).aggregate(Sum('count'))[
                'count__sum']
            # business_product_cost = Sale.objects.filter(sale_group__icustomer__isnull=True, sale_group__date=tomorrow_date, sale_group__business_id=row['business_id'], sale_group__session_id=session_id, product=product).aggregate(Sum('cost'))['cost__sum']
            business_product_temp_dict = {
                'name': product.name,
                'sum': business_product_sum,
                # 'cost': business_product_cost
            }
            business_dict['business_product'].append(business_product_temp_dict)
        temp_dict.append(business_dict)

    return Response(temp_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def route_wise_business_sale_reports(request):
    print(request.data)
    route_id = request.data['route_id']
    session_id = request.data['session_id']
    print(route_id)
    selected_date = datetime.datetime.strptime(request.data['selected_date'], '%m/%d/%Y')
    selected_month = datetime.datetime.strptime(request.data['selected_date'], '%m/%d/%Y').month
    selected_year = datetime.datetime.strptime(request.data['selected_date'], '%m/%d/%Y').year
    print(selected_date)
    business_ids = RouteBusinessMap.objects.filter(route_id=route_id).values_list('business_id', flat=True)
    sales_values = Sale.objects.filter(sale_group__business_id__in=business_ids, product__is_active=True,
                                       sale_group__session_id=session_id, sale_group__date=selected_date).values_list(
        'id', 'sale_group_id', 'count', 'cost', 'product_id',
        'product__name', 'sale_group__session_id', 'sale_group__business_id',
        'sale_group__business__business_type_id', 'sale_group__business__business_type__name')
    sales_column = ['id', 'sale_group_id', 'count', 'cost', 'product_id', 'product_name', 'session_id', 'business_id',
                    'business_type_id', 'business_type']
    sales_df = pd.DataFrame(list(sales_values), columns=sales_column)

    # serve customer order based on the business ids
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=selected_month,
                                                      icustomer_sale_group__date__year=selected_year,
                                                      icustomer_sale_group__business_id__in=business_ids,
                                                      icustomer_sale_group__session_id=session_id,
                                                      product__is_active=True)
    icustomer_sale_list = list(
        icustomer_sale_obj.values_list('id', 'icustomer_sale_group_id', 'count', 'cost', 'product_id', 'product__name',
                                       'icustomer_sale_group__session_id', 'icustomer_sale_group__business_id',
                                       'icustomer_sale_group__business__business_type_id',
                                       'icustomer_sale_group__business__business_type__name'))
    icustomer_sale_column = ['id', 'sale_group_id', 'count', 'cost', 'product_id', 'product_name', 'session_id',
                             'business_id', 'business_type_id', 'business_type']
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
    business_agent_df = business_agent_df.fillna(0)

    products = Product.objects.filter(is_active=True).order_by('id')
    route_wise_data = {
        'booth_types': {},
        'route_name': Route.objects.get(id=route_id).name,
        'vehicle_number': vehicle_data.vehicle.licence_number,
        'session_name': Session.objects.get(id=session_id).display_name,
        'total': {}
    }
    for index, row in business_agent_df.iterrows():
        if not row['business_type_id'] in route_wise_data['booth_types']:
            route_wise_data['booth_types'][row['business_type_id']] = {}
            route_wise_data['booth_types'][row['business_type_id']]['booth_ids'] = []
        if not row['business_id'] in route_wise_data['booth_types'][row['business_type_id']]:
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']] = {}
            route_wise_data['booth_types'][row['business_type_id']]['booth_ids'].append(row['business_id'])
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['agent_name'] = row[
                'agent_first_name']
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['business_code'] = row[
                'business_code']
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['product'] = {}

        if not row['product_id'] in route_wise_data['booth_types'][row['business_type_id']][row['business_id']][
            'product']:
            route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['product'][
                row['product_id']] = 0
        route_wise_data['booth_types'][row['business_type_id']][row['business_id']]['product'][row['product_id']] += \
        row['count']
    return Response(route_wise_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def close_overall_route_indent(request):
    print(request.data)
    session_id = request.data['session_id']
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    # routes = Route.objects.filter(session_id=session_id)
    route_trace_ids = list(
        OverallIndentPerSession.objects.filter(date=tomorrow_date, session_id=session_id).values_list('route_trace',
                                                                                                      flat=True))
    not_closed_route_list = []
    print(route_trace_ids)
    for route_trace_id in route_trace_ids:
        if RouteTrace.objects.get(id=route_trace_id).indent_status_id == 1:
            route_trace = RouteTrace.objects.get(id=route_trace_id)
            print(route_trace.route.id)
            calculated_tray_count = check_tray_count(route_trace.route.id, tomorrow_date, session_id)
            vehicle_tray_capacity = RouteVehicleMap.objects.get(route_id=route_trace.route.id).vehicle.tray_capacity
            if calculated_tray_count < vehicle_tray_capacity:
                route_trace_map = RouteBusinessMap.objects.filter(route_id=route_trace.route.id).order_by('ordinal')
                for map in route_trace_map:
                    if SaleGroup.objects.filter(date=tomorrow_date, session_id=session_id,
                                                business=map.business).exists():
                        RouteBusinessTrace.objects.create(route_trace=route_trace, business=map.business,
                                                          ordinal=map.ordinal)
                route_trace.indent_status_id = 2
                route_trace.indent_prepare_date_time = datetime.datetime.now()
                if RouteTrace.objects.filter().aggregate(Max('indent_number'))['indent_number__max'] is None:
                    route_trace.indent_number = 1
                else:
                    max_indent = RouteTrace.objects.filter().aggregate(Max('indent_number'))['indent_number__max']
                    new_indent_number = int(max_indent) + 1
                    route_trace.indent_number = new_indent_number
                print('save success')
                route_trace.save()
            else:
                route_dict = {
                    'name': route_trace.route.name
                }
                not_closed_route_list.append(route_dict)
    print('req', request.data['date'])
    if len(not_closed_route_list) == 0:
        OverallIndentPerSession.objects.filter(date=tomorrow_date, session_id=session_id).update(
            overall_indent_status_id=2, created_by=request.user)
    # prepare_overall_indent_pdf(route_trace_ids,request.data['date'], session_id, request.user)
    data = True
    return Response(data=not_closed_route_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def prepare_indent_for_all_closed_routes(request):
    session_id = request.data['session_id']
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    # routes = Route.objects.filter(session_id=session_id)
    print('tomorrow_date', tomorrow_date)
    print('session_id', session_id)
    if RouteTrace.objects.filter(date=tomorrow_date, session_id=session_id, indent_status_id=1).exists():
        data = False
        return Response(data=data, status=status.HTTP_200_OK)
    route_trace_ids = list(OverallIndentPerSession.objects.filter(date=tomorrow_date, session_id=session_id).order_by(
        'route_trace__route__name').values_list('route_trace', flat=True))
    data = prepare_overall_indent_pdf(route_trace_ids, request.data['date'], session_id, request.user)
    # data = True
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_agent_monthly_report(request):
    print(request.data)
    data_dict = {}
    if request.data['from'] == 'portal':
        business_code = request.data['business_code']
        business_id = Business.objects.get(code=request.data['business_code']).id
        user_profile_id = Business.objects.get(code=request.data['business_code']).user_profile_id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
    else:
        business_obj = Business.objects.get(user_profile__user_id=request.user.id)
        business_id = business_obj.id
        user_profile_id = business_obj.user_profile_id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
        business_code = business_obj.code
    if Business.objects.filter(code=business_code).exists():
        data_dict['status'] = True
        product_and_session_list = serve_product_and_session_list(user_profile_id)
        data_dict['session_list'] = product_and_session_list['session_list']
        data_dict['product_list'] = product_and_session_list['product_list']
        data_dict['milk_product_list'] = list(
            filter(lambda d: d['product_group_id'] in [1], product_and_session_list['product_list']))
        data_dict['fermented_product_list'] = list(
            filter(lambda d: d['product_group_id'] in [2], product_and_session_list['product_list']))
        sale_obj = Sale.objects.filter(sale_group__date__month=request.data['selected_month']['month_in_integer'] + 1,
                                       sale_group__date__year=request.data['selected_month']['year'],
                                       sale_group__business_id=business_id, product__is_active=True)
        sale_list = list(
            sale_obj.values_list('id', 'sale_group', 'sale_group__business_id',
                                 'sale_group__business__business_type_id',
                                 'sale_group__date', 'sale_group__session',
                                 'sale_group__session__display_name', 'sale_group__ordered_via',
                                 'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                                 'sale_group__sale_status__name', 'sale_group__total_cost', 'product__group_id',
                                 'product__group__name', 'product__quantity', 'product',
                                 'product__name', 'count', 'cost'))
        sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_type_id', 'date', 'session_id',
                       'session_name',
                       'ordered_via_id', 'ordered_via_name', 'payment_status',
                       'sale_status',
                       'session_wise_price', 'product_group_id', 'product_group_name', 'product_default_quantity',
                       'product_id', 'product_name', 'count', 'product_cost']
        sale_df = pd.DataFrame(sale_list, columns=sale_column)
        sale_df['date'] = sale_df['date'].astype(str)
        milk_product_df = sale_df[sale_df['product_group_id'] == 1]
        master_dict = {}
        master_dict['product_details'] = {}
        master_dict['total_price'] = 0
        for index, row in milk_product_df.iterrows():
            if not row['date'] in master_dict['product_details']:
                master_dict['product_details'][row['date']] = {}
                master_dict['product_details'][row['date']]['product_wise'] = {}
                master_dict['product_details'][row['date']]['date_wise_total_price'] = 0
            if not row['product_id'] in master_dict['product_details'][row['date']]['product_wise']:
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']] = {}
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_quantity_per_product'] = 0
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_quantity_product_per_session'] = {}
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_price_per_product'] = 0
            if not row['session_id'] in master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                'total_quantity_product_per_session']:
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_quantity_product_per_session'][
                    row['session_id']] = {}
            master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                'total_quantity_product_per_session'][
                row['session_id']] = row['count']
            master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                'total_quantity_per_product'] += \
                row['count']
            master_dict['product_details'][row['date']]['product_wise'][row['product_id']]['total_price_per_product'] += \
                row['product_cost']
            master_dict['product_details'][row['date']]['date_wise_total_price'] += row['product_cost']
            master_dict['total_price'] += row['product_cost']
        data_dict['milk_product_report'] = master_dict
        fermented_product_df = sale_df[sale_df['product_group_id'] == 2]
        master_dict = {}
        master_dict['product_details'] = {}
        master_dict['total_price'] = 0
        for index, row in fermented_product_df.iterrows():
            if not row['date'] in master_dict['product_details']:
                master_dict['product_details'][row['date']] = {}
                master_dict['product_details'][row['date']]['product_wise'] = {}
                master_dict['product_details'][row['date']]['date_wise_total_price'] = 0
            if not row['product_id'] in master_dict['product_details'][row['date']]['product_wise']:
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']] = {}
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_quantity_per_product'] = 0
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_quantity_product_per_session'] = {}
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_price_per_product'] = 0
            if not row['session_id'] in master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                'total_quantity_product_per_session']:
                master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                    'total_quantity_product_per_session'][
                    row['session_id']] = {}
            master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                'total_quantity_product_per_session'][
                row['session_id']] = row['count']
            master_dict['product_details'][row['date']]['product_wise'][row['product_id']][
                'total_quantity_per_product'] += \
                row['count']
            master_dict['product_details'][row['date']]['product_wise'][row['product_id']]['total_price_per_product'] += \
                row['product_cost']
            master_dict['product_details'][row['date']]['date_wise_total_price'] += row['product_cost']
            master_dict['total_price'] += row['product_cost']
        data_dict['fermented_product_report'] = master_dict
        master_dict = {}
        master_dict['total_price'] = 0
        master_dict['product_details'] = {}
        for index, row in sale_df.iterrows():
            if not row['product_id'] in master_dict['product_details']:
                master_dict['product_details'][row['product_id']] = {}
                master_dict['product_details'][row['product_id']]['quantity'] = 0
                master_dict['product_details'][row['product_id']]['price'] = 0
            master_dict['product_details'][row['product_id']]['quantity'] += row['count']
            master_dict['product_details'][row['product_id']]['price'] += row['product_cost']
            master_dict['total_price'] += row['product_cost']
        data_dict['overall_month_report'] = master_dict
        global_config_obj = GlobalConfig.objects.all()
        global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
        global_config_column = ['id', 'name', 'value', 'description']
        global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
        global_config_df['value'].astype('float')
        global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()
        master_dict = {}
        total_cash_amount = DailySessionllyBusinessllySale.objects.filter(
            delivery_date__month=request.data['selected_month']['month_in_integer'] + 1,
            delivery_date__year=request.data['selected_month']['year'], business_id=business_id,
            sold_to='Agent').aggregate(Sum('milk_cost'))
        total_card_amount = DailySessionllyBusinessllySale.objects.filter(
            delivery_date__month=request.data['selected_month']['month_in_integer'] + 1,
            delivery_date__year=request.data['selected_month']['year'], business_id=business_id,
            sold_to='ICustomer').aggregate(Sum('milk_cost'))
        if total_cash_amount['milk_cost__sum'] is not None:
            master_dict['total_cash_amount'] = total_cash_amount['milk_cost__sum']
        else:
            master_dict['total_cash_amount'] = 0
        if total_card_amount['milk_cost__sum'] is not None:
            master_dict['total_card_amount'] = total_card_amount['milk_cost__sum']
        else:
            master_dict['total_card_amount'] = 0
        master_dict['cash_commission'] = Decimal(format(
            calculate_percentage(master_dict['total_cash_amount'],
                                 Decimal(global_config_dict['cash_commission']['value'])),
            '.2f'))
        master_dict['card_commission'] = Decimal(format(
            calculate_percentage(master_dict['total_card_amount'],
                                 Decimal(global_config_dict['card_commission']['value'])),
            '.2f'))
        master_dict['total_commission'] = round(master_dict['cash_commission'] + master_dict['card_commission'])
        master_dict['tds_amount'] = math.ceil(Decimal(
            format(calculate_percentage(master_dict['total_commission'], Decimal(global_config_dict['tds']['value'])),
                   '.2f')))
        total_after_detect_tds = master_dict['total_commission'] - master_dict['tds_amount']
        master_dict['slip_charge'] = Decimal(global_config_dict['slip_charge']['value'])
        total_after_detect_slip_charge = total_after_detect_tds - master_dict['slip_charge']
        master_dict['insurance_amount'] = Decimal(
            global_config_dict['agent_insurance_on_commission_deduction']['value'])
        master_dict['final_amount'] = total_after_detect_slip_charge - master_dict['insurance_amount']
        data_dict['global_config_dict'] = global_config_dict
        data_dict['commission_details'] = master_dict
    else:
        data_dict['status'] = False
    return Response(data=data_dict, status=status.HTTP_200_OK)


def calculate_percentage(total, percentage):
    return (percentage / 100) * total


@api_view(['POST'])
def serve_business_bill(request):
    print(request.data)
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
    business_code = request.data['business_code']
    session_id = request.data['session_id']
    date = request.data['date']
    month = datetime.datetime.strptime(date, '%m/%d/%Y').month
    year = datetime.datetime.strptime(date, '%m/%d/%Y').year
    date = datetime.datetime.strptime(date, '%m/%d/%Y').strftime("%Y-%m-%d")
    business = Business.objects.get(code=business_code)
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
    sale_group = SaleGroup.objects.filter(date=date, session_id=session_id, business__code=business_code)
    business_sale_group = sale_group[0]
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
                                                      icustomer_sale_group__business__code=business_code)
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
    new_df['calculated_tray_count'] = ((new_df['count'] + new_df['icustomer_count']) / new_df['p_c_product_count']) * \
                                      new_df['p_c_tray_count']
    new_df['calculated_tray_count'] = new_df['calculated_tray_count'].fillna(0)
    new_df['calculated_tray_count'] = new_df['calculated_tray_count'].astype(int)
    new_df['calculated_pocket_count'] = (new_df['count'] + new_df['icustomer_count']) % new_df['p_c_product_count']
    new_df = new_df.fillna(0)
    data['sales'] = new_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    data['total_business_product_count'] = new_df['count'].sum()
    data['total_icustomer_product_count'] = new_df['icustomer_count'].sum()
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_tray_config(request):
    values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id', 'tray_count',
                                                                                   'product_count')
    columns = ['product_id', 'tray_count', 'product_count']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.groupby('product_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=data, status=status.HTTP_200_OK)



def findout_packet_count(count, product_defalut_count):
    if not product_defalut_count == 0:
        remainder_of_tray_count = count % product_defalut_count
        # coefieient_of_tray_count = count // product_defalut_count
    else:
        remainder_of_tray_count = 0
        # coefieient_of_tray_count = 0
    if not remainder_of_tray_count == 0:
        if remainder_of_tray_count < (product_defalut_count / 2):
            return remainder_of_tray_count
        else:
            return 0
    else:
        return remainder_of_tray_count


def findout_packet_count_in_negative(count, product_defalut_count, tray_count, packet_count):
    if not tray_count == 0:
        if not product_defalut_count == 0:
            remainder_of_tray_count = count % product_defalut_count
            # coefieient_of_tray_count = count // product_defalut_count
        else:
            remainder_of_tray_count = 0
            # coefieient_of_tray_count = 0
        if remainder_of_tray_count >= (product_defalut_count / 2):
            return product_defalut_count - remainder_of_tray_count
        else:
            return 0
    else:
        return 0


@api_view(['POST'])
def serve_route_gate_pass(request):
    print(request.data)
    route_id = request.data['route_id']
    # date = datetime.datetime.strptime(request.data['date'], '%m/%d/%Y')
    date = request.data['date']
    session_id = request.data['session_id']
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
        tray_config_values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id',
                                                                                                   'tray_count',
                                                                                                   'product_count')
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
            BusinessWiseLeakageAllowanceAsPacket.objects.filter(session_id=route.session_id,
                                                                product__is_active=True).values_list('business_id',
                                                                                                     flat=True))
        print(allowance_business_ids)
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
        data['total_milk_tray_count'] = milk_df['calculated_tray_count'].sum()
        data['total_milk_packet_count'] = milk_df['calculated_pocket_count'].sum()
        data['total_milk_packet_count_in_negative'] = milk_df['calculated_pocket_count_in_negative'].sum()
        data['total_milk_leak_packet_count'] = milk_df['leak_packet'].sum()
        data['total_milk_litre_count'] = milk_df['litre'].sum()

        # curd product details
        curd_df = tray_config_merge_df[tray_config_merge_df['id'].isin(curd_product_ids)]
        data['curd'] = curd_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
        data['total_curd_product_count'] = curd_df['count'].sum()
        df_without_cup_curd = curd_df[curd_df['id'] != 10]
        data['total_curd_tray_count'] = df_without_cup_curd['calculated_tray_count'].sum()
        data['total_curd_packet_count'] = curd_df['calculated_pocket_count'].sum()
        data['total_curd_packet_count_in_negative'] = curd_df['calculated_pocket_count_in_negative'].sum()
        data['total_curd_leak_packet_count'] = curd_df['leak_packet'].sum()
        data['total_curd_litre_count'] = curd_df['litre'].sum()

        other_df = tray_config_merge_df[~tray_config_merge_df['id'].isin(milk_product_ids)]
        other_df = other_df.fillna(0)
        data['other'] = other_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_route_session_wise(request):
    route_values = Route.objects.filter(is_temp_route=False).values_list('id', 'name', 'session').order_by('name')
    route_columns = ['id', 'name', 'session_id']
    route_df = pd.DataFrame(list(route_values), columns=route_columns)
    data = route_df.groupby('session_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=data, status=status.HTTP_200_OK)


def check_tray_count(route_id, date, session_id):
    route = Route.objects.get(id=route_id)
    business_ids = RouteBusinessMap.objects.filter(route=route).values_list('business', flat=True)
    sale_group = SaleGroup.objects.filter(business_id__in=business_ids, date=date, session_id=session_id)
    sale_values = Sale.objects.filter(sale_group__in=sale_group, product__is_active=True).values_list('product_id',
                                                                                                      'count')
    sale_columns = ['product_id', 'count']
    sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)
    icustomer_sale_group = ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date.month,
                                                             date__year=date.year, session_id=session_id)
    icustomer_sale_values = ICustomerSale.objects.filter(icustomer_sale_group__in=icustomer_sale_group,
                                                         product__is_active=True).values_list(
        'product_id', 'count')
    icustomer_sale_columns = ['product_id', 'count']
    icustomer_sale_df = pd.DataFrame(list(icustomer_sale_values), columns=icustomer_sale_columns)

    combined_df = sale_df.append(icustomer_sale_df)
    product_values = Product.objects.filter(is_active=True).order_by('display_ordinal').values_list('id', 'short_name',
                                                                                                    'unit', 'quantity')
    product_columns = ['id', 'product_short_name', 'unit', 'quantity']
    product_df = pd.DataFrame(list(product_values), columns=product_columns)
    total_sale_df = combined_df.groupby(['product_id'])['count'].sum().reset_index()
    merged_df = pd.merge(total_sale_df, product_df, how='left', left_on='product_id', right_on='id')
    tray_config_values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id',
                                                                                               'tray_count',
                                                                                               'product_count')
    tray_config_columns = ['product_id', 'p_c_tray_count', 'p_c_product_count']
    tray_config_df = pd.DataFrame(list(tray_config_values), columns=tray_config_columns)
    tray_config_merge_df = pd.merge(merged_df, tray_config_df, how='left', left_on='id', right_on='product_id')
    # print(tray_config_merge_df)
    # finding the tray count based on the defalut product tray count
    tray_config_merge_df['calculated_tray_count'] = tray_config_merge_df.apply(
        lambda x: findout_tray_count(x['count'], x['p_c_product_count'], x['id']), axis=1)
    tray_config_merge_df = tray_config_merge_df[(tray_config_merge_df['id'] != 10) & (tray_config_merge_df['id'] != 26) & (tray_config_merge_df['id'] != 28)]

    tray_config_merge_df = tray_config_merge_df.fillna(0)
    # print(tray_config_merge_df['calculated_tray_count'])
    return tray_config_merge_df['calculated_tray_count'].sum()


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


@api_view(['POST'])
def create_canvas_report(request):
    print(request.data)
    route_id = request.data['route_id']
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    session_id = request.data['session_id']
    if request.data['which_route'] == 'temp':
        data = generate_pdf_for_temp_route(route_id, session_id, date)
    else:
        data = gatepass_data(route_id, date, session_id)

    RouteTrace.objects.filter(route_id=route_id, session_id=session_id, date=date).update(
        indent_document=data['pdf_data']['path'],
        indent_status_id=3,
    )
    if request.data['which_route'] == 'main':
        route_trace_obj = RouteTrace.objects.get(route_id=route_id, session_id=session_id, date=date)
        route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.filter(route_trace=route_trace_obj)
        for product in Product.objects.filter(is_active=True):
            if product.id in data['data']['sales'].keys():
                if route_trace_sale_summary_obj.filter(product=product).exists():
                    route_trace_sale_summary_product = route_trace_sale_summary_obj.get(product=product)
                    route_trace_sale_summary_product.tray_count = data['data']['sales'][product.id][
                        'calculated_tray_count']
                    route_trace_sale_summary_product.loose_packet_count = data['data']['sales'][product.id][
                        'calculated_pocket_count']
                    route_trace_sale_summary_product.leak_packet_count = data['data']['sales'][product.id][
                        'leak_packet']
                    route_trace_sale_summary_product.quantity = data['data']['sales'][product.id]['quantity']
                    route_trace_sale_summary_product.save()
                else:
                    temp_route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(
                        quantity=data['data']['sales'][product.id]['quantity'],
                        product_id=product.id,
                        route_trace_id=route_trace_obj.id,
                        tray_count=data['data']['sales'][product.id]['calculated_tray_count'],
                        loose_packet_count=data['data']['sales'][product.id]['calculated_pocket_count'],
                        leak_packet_count=data['data']['sales'][product.id]['leak_packet'])
                    temp_route_trace_sale_summary_obj.save()

    if request.data['which_route'] == 'temp':
        route_business_map = RouteBusinessMap.objects.filter(route_id=route_id).order_by('ordinal')
        main_route_id = RouteTempRouteMap.objects.get(temp_route_id=route_id).main_route.id
        for map in route_business_map:
            map.route_id = main_route_id
            map.save()
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_corporation_zone(request):
    values = CorporationZone.objects.filter().order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_corporation_zone(request):
    print(request.data)
    if request.data['id'] is None:
        if CorporationZone.objects.filter(name__iexact=request.data['corporation_zone_name']).exists():
            data = {'message': 'Corporation zone already registered'}
        else:
            CorporationZone.objects.create(
                name=request.data['corporation_zone_name']
            )
            data = {'message': 'Corporation zone registered successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        CorporationZone.objects.filter(id=request.data['id']).update(
            name=request.data['corporation_zone_name'],
        )
        data = {'message': 'Corporation zone updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_agent_image(request):
    image_path = 'static/media/'
    if request.data['image_type'] == 'agent_image':
        image_path = 'static/media/' + str(Agent.objects.get(id=request.data['agent_id']).agent_profile.image)
    elif request.data['image_type'] == 'adhaar_image':
        image_path = 'static/media/' + str(Agent.objects.get(id=request.data['agent_id']).aadhar_document)

    data = {}
    print(image_path)
    try:
        # print(image_path)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data['image'] = 'data:image/jpeg;base64,' + encoded_image.decode("utf-8")
    except Exception as err:
        print(err)
        data['image'] = 'no-image'
    print(data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_milk_products(request):
    values = Product.objects.filter(group_id=1, is_active=True).order_by('name').values_list('id', 'name', 'base_price',
                                                                                             'group_id', 'group__name',
                                                                                             'short_name', 'code',
                                                                                             'unit_id', 'unit__name',
                                                                                             'description', 'quantity',
                                                                                             'mrp', 'gst_percent',
                                                                                             'snf', 'fat',
                                                                                             'is_homogenised')
    columns = ['id', 'name', 'base_price', 'group_id', 'group_name', 'short_name', 'code', 'unit_id', 'unit_name',
               'description', 'quantity', 'mrp', 'gst_percent', 'snf', 'fat', 'is_homogenised']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_district(request):
    print(request.data)
    if request.data['id'] is None:
        if District.objects.filter(name__iexact=request.data['name']).exists():
            data = {'message': 'District already registered'}
        else:
            District.objects.create(
                name=request.data['name'],
                state_id=request.data['state_id'],
                code=request.data['code'],
                capital=request.data['capital']
            )
            data = {'message': 'District registered successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        District.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
            state_id=request.data['state_id'],
            code=request.data['code'],
            capital=request.data['capital']
        )
        data = {'message': 'Block updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_block(request):
    if request.data['id'] is None:
        if Block.objects.filter(name__iexact=request.data['name']).exists():
            data = {'message': 'Block already registered'}
        else:
            Block.objects.create(
                name=request.data['name'],
                district_id=request.data['district_id'],
            )
            data = {'message': 'Block registered successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        Block.objects.filter(id=request.data['id']).update(
            name=request.data['name'],
            district_id=request.data['district_id']
        )
        data = {'message': 'Block updated successfully!'}
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_block(request):
    values = Block.objects.filter().order_by('name').values_list('id', 'name', 'district_id', 'district__name')
    columns = ['id', 'name', 'district_id', 'district_name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


# intent prepare
@api_view(['POST'])
def serve_indent_pdf(request):
    document = {}
    route_id = request.data['route_id']
    session_id = request.data['session_id']
    # date = request.data['date']
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    new_date = datetime.datetime.strftime(date, '%d-%b-%Y')
    session = 'Morning'
    if session_id == 2:
        session = 'Evening'
    route_name = Route.objects.get(id=route_id).name
    if RouteTrace.objects.filter(route_id=route_id, date=date, session_id=session_id, indent_status=3):
        file_path = RouteTrace.objects.get(route_id=route_id, date=date, session_id=session_id,
                                           indent_status=3).indent_document
        try:
            image_path = str(file_path)
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)
    else:
        print('there is no pdf')
        data = gatepass_data(route_id, date, session_id)
        RouteTrace.objects.filter(route_id=route_id, date=date, session_id=session_id).update(
            indent_document=data['pdf_data']['path'],
            indent_status_id=3
        )
        route_trace_obj = RouteTrace.objects.filter(route_id=route_id, session_id=session_id, date=date)
        route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.filter(route_trace=route_trace_obj)
        for product in Product.objects.filter(is_active=True):
            if product.id in data['data']['sales'].keys():
                if route_trace_sale_summary_obj.filter(product=product).exists():
                    route_trace_sale_summary_product = route_trace_sale_summary_obj.get(product=product)
                    route_trace_sale_summary_product.tray_count = data['data']['sales'][product.id][
                        'calculated_tray_count']
                    route_trace_sale_summary_product.loose_packet_count = data['data']['sales'][product.id][
                        'calculated_pocket_count']
                    route_trace_sale_summary_product.leak_packet_count = data['data']['sales'][product.id][
                        'leak_packet']
                    route_trace_sale_summary_product.save()
        print('individual pdf saved to route trace database')
        document['pdf'] = data
    # print(document['pdf'])
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_indent_pdf_for_old_indent(request):
    document = {}
    route_id = request.data['route_id']
    session_id = request.data['session_id']
    date = request.data['date']
    document['status'] = True
    if RouteTrace.objects.filter(route_id=route_id, date=date, session_id=session_id, indent_status=3):
        document['status'] = True
        file_path = RouteTrace.objects.get(route_id=route_id, date=date, session_id=session_id,
                                           indent_status=3).indent_document
        try:
            image_path = str(file_path)
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data=document, status=status.HTTP_200_OK)

    else:
        document['status'] = False
        return Response(data=document, status=status.HTTP_200_OK)


def prepare_overall_indent_pdf(route_trace_ids, date, session_id, user):
    route_trace_indent_paths = []
    merger = PdfFileMerger()
    for route_trace_id in route_trace_ids:
        route_id = RouteTrace.objects.get(id=route_trace_id).route.id
        # date = request.data['date']
        rec_date = date
        new_date = datetime.datetime.now().date()
        if rec_date == 'tomorrow':
            new_date += datetime.timedelta(days=1)
        session_id = session_id
        session = 'Morning'
        if session_id == 2:
            session = 'Evening'
        if RouteTrace.objects.filter(route_id=route_id, date=new_date, session_id=session_id,
                                     indent_status_id=3).exists():
            route_trace = RouteTrace.objects.get(route_id=route_id, date=new_date, session_id=session_id,
                                                 indent_status_id=3)
            print('------------------------')
            print('already present in database')
            route_trace_indent_paths.append(route_trace.indent_document)
        else:
            data = gatepass_data(route_id, new_date, session_id)
            RouteTrace.objects.filter(route_id=route_id, date=new_date, session_id=session_id).update(
                indent_document=data['pdf_data']['path'],
                indent_status_id=3
            )
            route_trace_obj = RouteTrace.objects.filter(route_id=route_id, session_id=session_id, date=new_date)
            route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.filter(route_trace=route_trace_obj)
            for product in Product.objects.filter(is_active=True):
                if route_trace_sale_summary_obj.filter(product=product).exists():
                    if product.id in data['data']['sales'].keys():
                        route_trace_sale_summary_product = route_trace_sale_summary_obj.get(product=product)
                        route_trace_sale_summary_product.tray_count = data['data']['sales'][product.id][
                            'calculated_tray_count']
                        route_trace_sale_summary_product.loose_packet_count = data['data']['sales'][product.id][
                            'calculated_pocket_count']
                        route_trace_sale_summary_product.leak_packet_count = data['data']['sales'][product.id][
                            'leak_packet']
                        route_trace_sale_summary_product.save()
            print('************************')
            print('creating pdf for route')
            route_trace_indent_paths.append(data['pdf_data']['path'])
            pdfPathSelectedRoutes(route_id, new_date, session_id, data['pdf_data']['path'])
    # unique_path = list(set(route_trace_indent_paths))
    unique_path = route_trace_indent_paths

    for file_path in unique_path:
        pdf_file_path = os.path.join(str(file_path))
        merger.append(pdf_file_path)
    overall_indent_file_path = os.path.join('static/media/indent_document/', str(new_date), session, 'overall')
    os.makedirs(overall_indent_file_path)
    merger.write("static/media/indent_document/" + str(new_date) + "/" + session + "/" + "overall" + "/overall.pdf")
    merger.close()
    document = {}
    try:
        image_path = "static/media/indent_document/" + str(new_date) + "/" + session + "/" + "overall" + "/overall.pdf"
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    image_path = "indent_document/" + str(new_date) + "/" + session + "/" + "overall" + "/overall.pdf"
    OverallIndentPerSession.objects.filter(date=new_date, session_id=session_id).update(
        overall_indent_status_id=3,
        created_by=user,
        overall_indent_document=image_path
    )
    return document['pdf']


def pdfPathSelectedRoutes(route_id, new_date, session_id, pdf_path):
    route_trace = RouteTrace.objects.get(route_id=route_id, date=new_date, session_id=session_id)
    route_trace.indent_document = pdf_path
    route_trace.indent_status_id = 3
    route_trace.save()


@api_view(['POST'])
def check_for_overal_route_is_closed(request):
    data = {}
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    session_id = request.data['session_id']
    data['status'] = OverallIndentPerSession.objects.get(session_id=session_id, date=date).overall_indent_status.id
    data['route_trace'] = {}
    if RouteTrace.objects.filter(session_id=session_id, date=date).exists():
        route_traces = RouteTrace.objects.filter(session_id=session_id, date=date)
        for route_trace in route_traces:
            data['route_trace'][route_trace.route.id] = route_trace.indent_status_id
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_for_overal_route_is_closed_for_old_indent(request):
    data = {}
    date = request.data['date']
    session_id = request.data['session_id']
    data['status'] = OverallIndentPerSession.objects.get(session_id=session_id, date=date).overall_indent_status.id
    data['route_trace'] = {}
    if RouteTrace.objects.filter(session_id=session_id, date=date).exists():
        route_traces = RouteTrace.objects.filter(session_id=session_id, date=date)
        for route_trace in route_traces:
            data['route_trace'][route_trace.route.id] = route_trace.indent_status_id
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_for_booth_agent_exists(request):
    print(request.data)
    data = {'found': False}
    if request.data['booth_code'] != None:
        if BusinessAgentMap.objects.filter(business__code__iexact=request.data['booth_code']).exists():
            agent_id = BusinessAgentMap.objects.get(business__code__iexact=request.data['booth_code']).agent_id
            data['found'] = True
    if not data['found']:
        if request.data['agent_code'] != None:
            if Agent.objects.filter(agent_code__iexact=request.data['agent_code']).exists():
                agent_id = Agent.objects.get(agent_code__iexact=request.data['agent_code']).id
                data['found'] = True
    if data['found']:
        print('agent_id', agent_id)
        agent_details = BusinessAgentMap.objects.get(agent_id=agent_id)
        agent_bank_details = AgentBankDetail.objects.get(agent_id=agent_id, is_active=True)
        data['agent_name'] = agent_details.agent.first_name
        data['agent_id'] = agent_id
        data['agent_mobile'] = agent_details.agent.agent_profile.mobile
        data['agent_wallet_balance'] = AgentWallet.objects.get(agent_id=agent_id).current_balance
        data['booth_address'] = agent_details.business.address
        data['booth_zone'] = agent_details.business.zone.name
        data['booth_code'] = agent_details.business.code
        data['booth_type'] = agent_details.business.business_type.name
        data['agent_code'] = agent_details.agent.agent_code
        data['bank_name'] = agent_bank_details.bank
        data['branch_name'] = agent_bank_details.branch
        data['ifsc_code'] = agent_bank_details.ifsc_code
        data['micr_code'] = agent_bank_details.micr_code
        data['account_holder_name'] = agent_bank_details.account_holder_name
        data['account_number'] = agent_bank_details.account_number

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_payment_modes(request):
    values = TransactionMode.objects.filter(id__in=[2, 3]).order_by('name').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_money_to_wallet(request):
    print('add_money', request.data)
    # check for wallet exists
    if AgentWallet.objects.filter(agent_id=request.data['agent_id']).exists():
        old_wallet_value = AgentWallet.objects.get(agent_id=request.data['agent_id']).current_balance
        # update if not check mode is selected, since check should be updated approved
        if request.data['mode'] != 3:
            AgentWallet.objects.filter(agent_id=request.data['agent_id']).update(
                current_balance=old_wallet_value + Decimal(request.data['money'])
            )
        new_value = old_wallet_value + Decimal(request.data['money'])
    else:
        old_wallet_value = 0
        AgentWallet.objects.create(agent_id=request.data['agent_id'], current_balance=0)
        new_value = old_wallet_value + Decimal(request.data['money'])
    # transaction logs
    user_id = BusinessAgentMap.objects.get(agent_id=request.data['agent_id']).business.user_profile.user.id
    print(user_id)
    transaction_log_obj = TransactionLog(
        date=datetime.datetime.now().date(),
        transacted_by_id=user_id,
        transacted_via_id=2,
        data_entered_by=request.user,
        amount=request.data['money'],
        transaction_direction_id=1,
        transaction_mode_id=request.data['mode'],
        transaction_status_id=1,
        wallet_balance_before_this_transaction=old_wallet_value,
        description='money added to wallet from agent',
        modified_by=request.user,
        transaction_approved_by=request.user,
        transaction_approved_time=datetime.datetime.now(),
        wallet_balance_after_transaction_approval=new_value,
        transaction_approval_status_id=1
    )
    if request.data['mode'] == 3:
        transaction_log_obj.transaction_approval_status_id = 2
    transaction_log_obj.save()
    print('saved log')
    # if cheque is selected
    if request.data['mode'] == 3:
        transaction_cheque_details = TransactionChequeDetails(
            bank_name=request.data['cheque_details']['bank_name'],
            branch_name=request.data['cheque_details']['branch_name'],
            ifsc_code=request.data['cheque_details']['ifsc_code'].upper(),
            account_holder_name=request.data['cheque_details']['account_holder_name'],
            account_number=request.data['cheque_details']['account_number'],
            date_of_issue=request.data['cheque_details']['cheque_issue_date'],
            cheque_number=request.data['cheque_details']['cheque_number'],
            micr_code=request.data['cheque_details']['micr_code']
        )
        transaction_cheque_details.save()
        transaction_log_obj.cheque_detail = transaction_cheque_details
        transaction_log_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_cheque_status_logs(request):
    transactions = TransactionLog.objects.filter(transaction_mode_id=3)
    transacted_users = transactions.values_list('transacted_by', flat=True)
    values = transactions.order_by('cheque_detail__is_cleared').values_list('id', 'cheque_detail__bank_name',
                                                                            'cheque_detail__branch_name',
                                                                            'cheque_detail__ifsc_code',
                                                                            'cheque_detail__micr_code',
                                                                            'cheque_detail__account_holder_name',
                                                                            'cheque_detail__account_number',
                                                                            'cheque_detail__date_of_issue',
                                                                            'cheque_detail__cheque_number',
                                                                            'cheque_detail__is_cleared',
                                                                            'cheque_detail__cheque_cleared_date',
                                                                            'transacted_by')
    columns = ['id', 'bank_name', 'branch_name', 'ifsc_code', 'micr_code', 'account_holder_name', 'account_number',
               'date_of_issue', 'cheque_number', 'is_cleared', 'cheque_cleared_date', 'transacted_by']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna(0)
    agent_ids = list(
        BusinessAgentMap.objects.filter(business__user_profile__user_id__in=transacted_users).values_list('agent_id',
                                                                                                          flat=True))
    agents = BusinessAgentMap.objects.filter(agent_id__in=agent_ids)
    agent_values = agents.values_list('business__user_profile__user_id', 'agent_id', 'agent__first_name')
    agent_columns = ['agent_id', 'agent_profile_id', 'agent_name']
    agent_df = pd.DataFrame(list(agent_values), columns=agent_columns)

    new_df = pd.merge(df, agent_df, left_on='transacted_by', right_on='agent_id', how='left')

    business_agent_map = BusinessAgentMap.objects.filter(business__user_profile__user_id__in=transacted_users)
    business_values = business_agent_map.values_list('business__code', 'business__name',
                                                     'business__user_profile__user__id')
    business_columns = ['business_code', 'business_name', 'agent_id']
    business_df = pd.DataFrame(list(business_values), columns=business_columns)

    final_df = pd.merge(new_df, business_df, left_on='agent_id', right_on='agent_id', how='left')
    data = final_df.to_dict('r')
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_cheque_approval(request):
    print('save cheque approval')
    print(request.data)
    transaction_log_obj = TransactionLog.objects.get(id=request.data['transaction_log_id'])
    old_wallet_value = AgentWallet.objects.get(agent_id=request.data['agent_id']).current_balance
    print(old_wallet_value)

    AgentWallet.objects.filter(agent_id=request.data['agent_id']).update(
        current_balance=old_wallet_value + transaction_log_obj.amount
    )

    new_value = old_wallet_value + transaction_log_obj.amount
    print(new_value)

    TransactionLog.objects.filter(id=request.data['transaction_log_id']).update(
        transaction_id=request.data['transaction_id'],
        transaction_status_id=2,
        transaction_approval_status_id=1,
        transaction_approved_by=request.user,
        transaction_approved_time=datetime.datetime.now(),
        wallet_balance_after_transaction_approval=new_value,
        modified_by=request.user
    )

    TransactionChequeDetails.objects.filter(id=transaction_log_obj.cheque_detail.id).update(
        is_cleared=True,
        cheque_cleared_date=request.data['approved_on']
    )
    print('saved the log')
    data = True
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_cheque_status_logs_for_individual_transaction(request):
    values = TransactionLog.objects.filter(id=request.data['transaction_log_id']).order_by(
        'cheque_detail__date_of_issue').values_list('id', 'cheque_detail__bank_name', 'cheque_detail__branch_name',
                                                    'cheque_detail__ifsc_code', 'cheque_detail__micr_code',
                                                    'cheque_detail__account_holder_name',
                                                    'cheque_detail__account_number', 'cheque_detail__date_of_issue',
                                                    'cheque_detail__cheque_number', 'cheque_detail__is_cleared',
                                                    'cheque_detail__cheque_cleared_date', 'transacted_by')
    columns = ['id', 'bank_name', 'branch_name', 'ifsc_code', 'micr_code', 'account_holder_name', 'account_number',
               'date_of_issue', 'cheque_number', 'is_cleared', 'cheque_cleared_date', 'transacted_by']
    df = pd.DataFrame(list(values), columns=columns)
    df = df.fillna(0)
    data = df.to_dict('r')[0]
    user_id = TransactionLog.objects.get(id=request.data['transaction_log_id']).transacted_by_id
    data['agent_name'] = BusinessAgentMap.objects.get(business__user_profile__user_id=user_id).agent.first_name
    data['agent_id'] = BusinessAgentMap.objects.get(business__user_profile__user_id=user_id).agent.id
    data['business_code'] = BusinessAgentMap.objects.get(business__user_profile__user__id=user_id).business.code
    data['business_name'] = BusinessAgentMap.objects.get(business__user_profile__user__id=user_id).business.name

    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_last_week_transaction_log_for_icustomers(request):
    print('transaction log')
    print(request.data)
    if request.data['from'] == 'portal':
        user_id = ICustomer.objects.get(id=request.data['icustomer_id']).user_profile.user.id
    if request.data['from'] == 'mobile':
        user_id = request.user.id
    today_datetime = datetime.datetime.now()
    print(user_id)
    before_one_year_date = today_datetime - datetime.timedelta(days=365)
    transaction_log_obj = TransactionLog.objects.filter(transacted_by=user_id, date__gte=before_one_year_date,
                                                        date__lte=today_datetime).order_by('-id')
    transaction_log_list = list(
        transaction_log_obj.values_list('id', 'date', 'transacted_by', 'transaction_status', 'transaction_status__name',
                                        'amount', 'transaction_direction', 'transaction_direction__description',
                                        'transaction_mode', 'transaction_mode__name', 'transaction_id',
                                        'wallet_balance_before_this_transaction',
                                        'wallet_balance_after_transaction_approval', 'description', 'time_created',
                                        'transaction_status', 'transaction_status__name', 'transaction_approval_status',
                                        'transaction_approval_status__name', 'transaction_approved_by',
                                        'transaction_approved_time'))
    transaction_log_column = ['id', 'date', 'transacted_by', 'transaction_status_id', 'transaction_status_name',
                              'amount', 'transaction_direction_id', 'transaction_direction_description',
                              'transaction_mode', 'transaction_mode_name', 'transaction_id', 'wallet_balance_before',
                              'wallet_balance_after', 'description', 'time_created', 'transaction_status_id',
                              'transaction_status_name', 'transaction_approval_status_id',
                              'transaction_approval_status_name', 'transaction_approved_by',
                              'transaction_approved_time']
    transaction_log_df = pd.DataFrame(transaction_log_list, columns=transaction_log_column)
    print(transaction_log_df)
    transaction_log_list = transaction_log_df.to_dict('r')
    data_dict = {
        'transaction_log': transaction_log_list
    }

    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_un_active_counter(request):
    counter_ids = []
    employee_obj = Employee.objects.get(user_profile__user=request.user)
    employee_id = employee_obj.id
    employee_role_id = employee_obj.role.id
    authorized_role_ids = [2, 5, 6, 4]
    if CounterEmployeeTraceMap.objects.filter(is_active=True, employee_id=employee_id,
                                              collection_date=datetime.datetime.now()).exists():
        return Response(data='counter already selected', status=status.HTTP_200_OK)
    else:
        if employee_role_id in authorized_role_ids:
            if employee_role_id == 2:
                counter_obj = Counter.objects.filter(is_active=True).order_by('id')
            else:
                counter_obj = Counter.objects.filter(is_active=True, collection_center_id=5).order_by('id').exclude(
                    collection_center_id__in=[6])
        else:
            if employee_role_id in [12, 9]:
                counter_obj = Counter.objects.filter(is_active=True, collection_center_id=9).order_by('id')
            else:
                if employee_role_id == 13:
                    if employee_obj.business_group is not None:
                        counter_obj = Counter.objects.filter(is_active=True, collection_center__business_group_id=employee_obj.business_group.id).order_by('id')
                else:
                    counter_obj = Counter.objects.filter(is_active=True).order_by('id').exclude(collection_center_id__in=[5, 6, 10])
        counter_list = list(
            counter_obj.values_list('id', 'name', 'collection_center', 'collection_center__building_name'))
        counter_column = ['counter_id', 'counter_name', 'collection_center', 'collection_center_name']
        counter_df = pd.DataFrame(counter_list, columns=counter_column)
        counter_dict = counter_df.groupby('collection_center_name').apply(lambda x: x.to_dict('r')).to_dict()
        counter_emoloyee_trace_obj = CounterEmployeeTraceMap.objects.filter(collection_date=datetime.datetime.now(),
                                                                            is_active=True)
        counter_employee_trace_list = list(
            counter_emoloyee_trace_obj.values_list('id', 'employee', 'employee__user_profile__user__first_name',
                                                   'counter', 'start_date_time'))
        counter_employee_trace_column = ['id', 'employee_id', 'employee_name', 'counter_id', 'start_date_time']
        counter_emoloyee_trace_df = pd.DataFrame(counter_employee_trace_list, columns=counter_employee_trace_column)
        logged_users = counter_emoloyee_trace_df.groupby('counter_id').apply(lambda x: x.to_dict('r')[0]).to_dict()
        data_dict = {
            'counter_data': counter_dict,
            'logged_users': logged_users
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def assign_counter_to_employee(request):
    print(request.data)
    employee_id = Employee.objects.get(user_profile__user=request.user).id
    if CounterEmployeeTraceMap.objects.filter(is_active=True, collection_date=datetime.datetime.now(),
                                              counter_id=request.data['counter_id']).exists():
        counter_employee_trace_obj = CounterEmployeeTraceMap.objects.get(is_active=True,
                                                                         collection_date=datetime.datetime.now(),
                                                                         counter_id=request.data['counter_id'])
        data_dict = {
            'is_taken': True,
            'taken_by': counter_employee_trace_obj.employee.user_profile.user.first_name
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=request.data['counter_id'],
                                                             employee_id=employee_id,
                                                             is_active=True,
                                                             collection_date=datetime.datetime.now(),
                                                             start_date_time=datetime.datetime.now())
        counter_employee_trace_obj.save()
        data_dict = {
            'is_taken': False,
        }
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def logout_employee_from_counter(request):
    print(request.data)
    employee_id = request.data['employee_id']
    if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True, collection_date=datetime.datetime.now()).exists():
        latest_active_trace = CounterEmployeeTraceMap.objects.get(employee_id=employee_id, is_active=True, collection_date=datetime.datetime.now())
        if not CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace=latest_active_trace).exists():
            if not CounterEmployeeTraceBySaleGroupMap.objects.filter(counter_employee_trace=latest_active_trace).exists():
                latest_active_trace.delete()
                print('delete')
        CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True, collection_date=datetime.datetime.now()).update(is_active=False, end_date_time=datetime.datetime.now())
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def serve_counter_orders(request):
    employee_id = Employee.objects.get(user_profile__user=request.user).id
    counter_obj = CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True, collection_date=datetime.datetime.now())[0]
    counter_employee_trace_ids = list(CounterEmployeeTraceMap.objects.filter(counter_id=counter_obj.counter.id,
                                                                             collection_date=datetime.datetime.now()).values_list(
        'id', flat=True))
    counter_sale_group_ids = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
        counter_employee_trace_id__in=counter_employee_trace_ids).values_list('sale_group', flat=True))
    counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.filter(
        counter_employee_trace_id__in=counter_employee_trace_ids)
    counter_sale_group_list = list(counter_sale_group_obj.values_list('counter_employee_trace', 'sale_group'))
    counter_sale_group_column = ['login_id', 'sale_group']
    counter_sale_group_df = pd.DataFrame(counter_sale_group_list, columns=counter_sale_group_column)
    login_user_obj = CounterEmployeeTraceMap.objects.filter(counter_id=counter_obj.counter.id,
                                                            collection_date=datetime.datetime.now()).order_by('-id')
    login_user_list = list(
        login_user_obj.values_list('id', 'employee__user_profile__user__first_name', 'start_date_time',
                                   'end_date_time', 'counter__name'))
    login_user_column = ['login_id', 'employee_name', 'login_time', 'logout_time', 'counter_name']
    login_user_df = pd.DataFrame(login_user_list, columns=login_user_column)
    login_user_df = login_user_df.fillna(0)
    sale_obj = Sale.objects.filter(sale_group_id__in=counter_sale_group_ids, product__is_active=True).order_by(
        '-sale_group_id')
    sale_list = list(sale_obj.values_list('id', 'sale_group', 'sale_group__business_id', 'sale_group__business__code',
                                          'sale_group__business__business_type_id',
                                          'sale_group__date', 'sale_group__session',
                                          'sale_group__session__display_name', 'sale_group__ordered_via',
                                          'sale_group__ordered_via__name', 'sale_group__payment_status__name',
                                          'sale_group__sale_status__name', 'sale_group__total_cost',
                                          'sale_group__time_created',
                                          'product__group_id', 'product__group__name', 'product__quantity', 'product',
                                          'product__name', 'count', 'cost', ))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_code', 'business_type_id',
                   'date', 'session_id', 'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'order_created_time', 'product_group_id', 'product_group_name',
                   'product_default_quantity',
                   'product_id', 'product_name', 'count', 'product_cost']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['date'] = sale_df['date'].astype('str')
    sale_df = sale_df.merge(counter_sale_group_df, how="inner", left_on='sale_group_id', right_on="sale_group")
    if not sale_df.empty:
        sale_df['total_price_per_date'] = sale_df.groupby(['business_code', 'date'])[
            'product_cost'].transform('sum')
        sale_df = sale_df.drop_duplicates(subset=['business_code', 'date'],
                                          keep="first")
        business_ids = list(sale_df['business_id'])
        business_agent_map = BusinessAgentMap.objects.filter(business_id__in=business_ids)
        business_agent_values = business_agent_map.values_list('id', 'agent__first_name',
                                                               'business_id')
        business_agent_columns = ['id', 'agent_first_name', 'business_id']
        business_agent_df = pd.DataFrame(list(business_agent_values), columns=business_agent_columns)
        sale_df = sale_df.merge(business_agent_df, how="left", left_on="business_id", right_on="business_id")
        sale_list = sale_df.groupby('login_id').apply(lambda x: x.to_dict('r')).to_dict()
    else:
        sale_list = []
    data_dict = {
        'login_users': login_user_df.to_dict('r'),
        'sale_data': sale_list,
        # 'total_booth_count': sale_df.shape[0]
        'total_booth_count': len(sale_df['business_id'].unique())
    }
    if not sale_df.empty:
        data_dict['total_quantity'] = sale_df['total_price_per_date'].sum()
    else:
        data_dict['total_quantity'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_icustomer_counter_orders(request):
    data_dict = {}
    employee_id = Employee.objects.get(user_profile__user=request.user).id
    counter_obj = CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True, collection_date=datetime.datetime.now())[0]
    counter_employee_trace_ids = list(CounterEmployeeTraceMap.objects.filter(counter_id=counter_obj.counter.id,
                                                                             collection_date=datetime.datetime.now()).values_list(
        'id', flat=True))
    counter_sale_group_ids = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
        counter_employee_trace_id__in=counter_employee_trace_ids).values_list('icustomer_sale_group', flat=True))

    # to find how much wallet amount used in selected counter
    wallet_amount_for_order_obj = ICustomerWalletAmoutForOrder.objects.filter(icustomer_sale_group__in=counter_sale_group_ids)
    wallet_amount_for_order_list = list(wallet_amount_for_order_obj.values_list('id', 'month', 'year', 'icustomer', 'wallet_amount'))
    wallet_amount_for_order_column = ['id', 'month', 'year', 'icustomer', 'wallet_amount']
    waller_amount_for_order_df = pd.DataFrame(wallet_amount_for_order_list, columns=wallet_amount_for_order_column)
    waller_amount_for_order_df = waller_amount_for_order_df.groupby(['icustomer', 'month', 'year']).agg({'wallet_amount':'first'}).reset_index()
    

    counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.filter(
        counter_employee_trace_id__in=counter_employee_trace_ids)
    counter_sale_group_list = list(counter_sale_group_obj.values_list('counter_employee_trace', 'icustomer_sale_group'))
    counter_sale_group_column = ['login_id', 'sale_group']
    counter_sale_group_df = pd.DataFrame(counter_sale_group_list, columns=counter_sale_group_column)
    login_user_obj = CounterEmployeeTraceMap.objects.filter(counter_id=counter_obj.counter.id,
                                                            collection_date=datetime.datetime.now()).order_by('-id')
    login_user_list = list(
        login_user_obj.values_list('id', 'employee__user_profile__user__first_name', 'start_date_time',
                                   'end_date_time', 'counter__name'))
    login_user_column = ['login_id', 'employee_name', 'login_time', 'logout_time', 'counter_name']
    login_user_df = pd.DataFrame(login_user_list, columns=login_user_column)
    login_user_df = login_user_df.fillna(0)
    sale_obj = ICustomerSale.objects.filter(icustomer_sale_group_id__in=counter_sale_group_ids,
                                            product__is_active=True).order_by('-icustomer_sale_group_id')
    sale_list = list(sale_obj.values_list('id', 'icustomer_sale_group', 'icustomer_sale_group__business_id',
                                          'icustomer_sale_group__business__code',
                                          'icustomer_sale_group__business__business_type_id',
                                          'icustomer_sale_group__icustomer_id',
                                          'icustomer_sale_group__icustomer__customer_code',
                                          'icustomer_sale_group__icustomer__user_profile__user__first_name',
                                          'icustomer_sale_group__date', 'icustomer_sale_group__session',
                                          'icustomer_sale_group__session__display_name',
                                          'icustomer_sale_group__ordered_via',
                                          'icustomer_sale_group__ordered_via__name',
                                          'icustomer_sale_group__payment_status__name',
                                          'icustomer_sale_group__sale_status__name', 'icustomer_sale_group__total_cost',
                                          'icustomer_sale_group__time_created',
                                          'product__group_id', 'product__group__name', 'product__quantity', 'product',
                                          'product__name', 'count', 'cost', 'cost_for_month'))
    sale_column = ['sale_id', 'sale_group_id', 'business_id', 'business_code', 'business_type_id', 'icustomer_id',
                   'icustomer_code', 'customer_first_name',
                   'date', 'session_id', 'session_name',
                   'ordered_via_id', 'ordered_via_name', 'payment_status',
                   'sale_status',
                   'session_wise_price', 'order_created_time', 'product_group_id', 'product_group_name',
                   'product_default_quantity',
                   'product_id', 'product_name', 'count', 'product_cost', 'product_cost_for_month']
    sale_df = pd.DataFrame(sale_list, columns=sale_column)
    sale_df['date'] = sale_df['date'].astype('str')
    sale_df = sale_df.merge(counter_sale_group_df, how="inner", left_on='sale_group_id', right_on="sale_group")
    sale_df['month'] = pd.DatetimeIndex(sale_df['date']).month
    if not sale_df.empty:
        sale_df['total_price_per_date'] = sale_df.groupby(['icustomer_code', 'month'])[
            'product_cost_for_month'].transform('sum')
        sale_df = sale_df.drop_duplicates(subset=['icustomer_code', 'month'],
                                          keep="first")
        sale_list = sale_df.groupby('login_id').apply(lambda x: x.to_dict('r')).to_dict()
    data_dict = {
        'login_users': login_user_df.to_dict('r'),
        'sale_data': sale_list,
        'total_booth_count': len(sale_df['icustomer_id'].unique())
    }
    if not sale_df.empty:
        data_dict['total_quantity'] = sale_df['total_price_per_date'].sum()
    else:
        data_dict['total_quantity'] = 0
    data_dict['total_amount_used_via_wallet'] =  waller_amount_for_order_df['wallet_amount'].sum()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_icustomer_latest_twelve_orders(request):
    if request.data['from'] == 'portal':
        icustomer_id = request.data['icustomer_id']
    elif request.data['from'] == 'website':
        icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
    sale_group_obj = ICustomerSaleGroup.objects.filter(icustomer_id=icustomer_id).order_by('-id')
    sale_group_list = list(sale_group_obj.values_list('id', 'business_id', 'business__code',
                                                      'business__business_type_id', 'icustomer_id',
                                                      'icustomer__customer_code',
                                                      'date', 'session',
                                                      'session__display_name', 'ordered_via',
                                                      'ordered_via__name', 'payment_status__name',
                                                      'sale_status__name', 'total_cost', 'total_cost_for_month',
                                                      'time_created', 'ordered_by__first_name', 'ordered_by_id'))
    sale_group_column = ['sale_group_id', 'business_id', 'business_code', 'business_type_id', 'icustomer_id',
                         'icustomer_code', 'date', 'session_id', 'session_name',
                         'ordered_via_id', 'ordered_via_name', 'payment_status',
                         'sale_status',
                         'session_wise_price', 'total_cost_for_month', 'order_date', 'ordered_by_name', 'ordered_by_id']
    sale_group_df = pd.DataFrame(sale_group_list, columns=sale_group_column)
    sale_group_df['month'] = pd.DatetimeIndex(sale_group_df['date']).month
    sale_group_df['year'] = pd.DatetimeIndex(sale_group_df['date']).year
    sale_group_df['current_date'] = str(datetime.datetime.now())[:10]
    # sale_group_df['order_date'] = sale_group_df.to_datetime(sale_group_df['order_date'], unit='s')
    sale_group_df['order_date'] = sale_group_df['order_date'].astype(str)
    sale_group_df['order_date'] = sale_group_df['order_date'].str[:10]
    sale_group_df['total_price_per_month'] = sale_group_df.groupby(['month', 'year'])[
        'total_cost_for_month'].transform('sum')
    sale_group_df = sale_group_df.drop_duplicates(subset=['month', 'year'], keep="first")
    sale_group_df = sale_group_df.head(12)
    print(sale_group_df.to_dict('r'))
    return Response(data=sale_group_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_indent_pdf_all_closed_routes(request):
    session = 'Morning'
    if request.data['session_id'] == 2:
        session = 'Evening'
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    print(tomorrow_date)
    try:
        image_path = "static/media/indent_document/" + str(
            tomorrow_date) + "/" + session + "/" + "overall" + "/overall.pdf"
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            data = encoded_image
    except Exception as err:
        print(err)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_indent_pdf_all_closed_routes_for_old_indent(request):
    data_dict = {}
    session = 'Morning'
    if request.data['session_id'] == 2:
        session = 'Evening'
    tomorrow_date = request.data['date']
    print(tomorrow_date)
    data_dict['status'] = True
    if OverallIndentPerSession.objects.filter(date=request.data['date'], session_id=request.data['session_id'],
                                              overall_indent_status_id=3).exists():
        data_dict['status'] = True
        try:
            image_path = "static/media/indent_document/" + str(
                tomorrow_date) + "/" + session + "/" + "overall" + "/overall.pdf"
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                data_dict['pdf_document'] = encoded_image
        except Exception as err:
            print(err)
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        data_dict['status'] = False
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_wards_based_on_constituency(request):
    values = Ward.objects.filter().order_by('name').values_list('id', 'name', 'constituency', 'constituency__name',
                                                                'number', 'corporation_zone_id',
                                                                'corporation_zone__name')
    columns = ['id', 'name', 'constituency_id', 'constituency_name', 'ward_number', 'corporation_zone',
               'corporation_zone_name']
    df = pd.DataFrame(list(values), columns=columns)
    data = df.groupby('constituency_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data, status=status.HTTP_200_OK)


# serve route_tray count
def check_tray_count_for_route_rearrange(route_id, date, session_id):
    route = Route.objects.get(id=route_id)
    business_ids = RouteBusinessMap.objects.filter(route=route).values_list('business', flat=True)
    sale_group = SaleGroup.objects.filter(business_id__in=business_ids, date=date, session_id=session_id)
    sale_values = Sale.objects.filter(sale_group__in=sale_group, product__is_active=True).values_list('product_id',
                                                                                                      'count')
    sale_columns = ['product_id', 'count']
    sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)

    icustomer_sale_group = ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date.month,
                                                             date__year=date.year, session_id=session_id)
    icustomer_sale_values = ICustomerSale.objects.filter(icustomer_sale_group__in=icustomer_sale_group,
                                                         product__is_active=True).values_list(
        'product_id', 'count')
    icustomer_sale_columns = ['product_id', 'count']
    icustomer_sale_df = pd.DataFrame(list(icustomer_sale_values), columns=icustomer_sale_columns)

    combined_df = sale_df.append(icustomer_sale_df)

    product_values = Product.objects.filter(is_active=True).order_by('display_ordinal').values_list('id', 'short_name',
                                                                                                    'unit', 'quantity')
    product_columns = ['id', 'product_short_name', 'unit', 'quantity']
    product_df = pd.DataFrame(list(product_values), columns=product_columns)
    total_sale_df = combined_df.groupby(['product_id'])['count'].sum().reset_index()
    merged_df = pd.merge(total_sale_df, product_df, how='left', left_on='product_id', right_on='id')
    tray_config_values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id',
                                                                                               'tray_count',
                                                                                               'product_count')
    tray_config_columns = ['product_id', 'p_c_tray_count', 'p_c_product_count']
    tray_config_df = pd.DataFrame(list(tray_config_values), columns=tray_config_columns)
    tray_config_merge_df = pd.merge(merged_df, tray_config_df, how='left', left_on='id', right_on='product_id')

    # finding the tray count based on the defalut product tray count
    tray_config_merge_df['calculated_tray_count'] = tray_config_merge_df.apply(
        lambda x: findout_tray_count(x['count'], x['p_c_product_count'], x['id']), axis=1)
    tray_config_merge_df = tray_config_merge_df[(tray_config_merge_df['id'] != 10) & (tray_config_merge_df['id'] != 26) & (tray_config_merge_df['id'] != 28)]

    tray_config_merge_df = tray_config_merge_df.fillna(0)
    data_dict = {
        'route_name': route.name,
        'route_id': route.id,
        'selected_date': date,
        'tray_count': tray_config_merge_df['calculated_tray_count'].sum()
    }
    return data_dict


def get_individual_business_data(business_id, date, session_id):
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
        'business_code': business.code,
        'business_id': business.id,
        'tray_count': 0
    }
    sale_group = SaleGroup.objects.filter(date=date, session_id=session_id, business_id=business_id)
    # business_sale_group = sale_group[0]
    sales_values = Sale.objects.filter(sale_group__in=sale_group, product__is_active=True).values_list('sale_group',
                                                                                                       'product_id',
                                                                                                       'count')
    sales_columns = ['sale_group_id', 'product_id', 'count']
    sale_df = pd.DataFrame(list(sales_values), columns=sales_columns)
    sale_df = sale_df.fillna(0)
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
    new_df['calculated_tray_count'] = ((new_df['count'] + new_df['icustomer_count']) / new_df['p_c_product_count']) * \
                                      new_df['p_c_tray_count']
    new_df['calculated_tray_count'] = new_df['calculated_tray_count'].fillna(0)
    new_df['calculated_tray_count'] = new_df['calculated_tray_count'].astype(int)
    data['tray_count'] = new_df['calculated_tray_count'].sum()
    return data


def get_business_ids(route_id, date, session_id):
    # return ordered_business
    business_ids = RouteBusinessMap.objects.filter(route_id=route_id).values_list('business_id', flat=True).order_by(
        'ordinal')
    ordered_business = list(
        SaleGroup.objects.filter(business_id__in=business_ids, date=date, session_id=session_id).values_list(
            'business_id', flat=True))
    selected_month = date
    ordered_business_for_icustomer = list(
        ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=selected_month.month,
                                          date__year=selected_month.year, session_id=session_id).values_list(
            'business_id', flat=True))
    return list(set(ordered_business + ordered_business_for_icustomer))


@api_view(['POST'])
def serve_business_list_for_route_rearrange(request):
    data_dict = {'main_route_details': {}, 'temp_route_details': {}}
    route_id = request.data['route_id']
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    session_id = request.data['session_id']
    # get the main route tray count
    data_dict['main_route_details'] = check_tray_count_for_route_rearrange(route_id, date, session_id)
    data_dict['main_route_details']['business_details'] = []
    # get the business ids under mainroute

    business_ids = get_business_ids(route_id, date, session_id)
    # get the business sale details under mainroute
    for business_id in business_ids:
        data_dict['main_route_details']['business_details'].append(
            get_individual_business_data(business_id, date, session_id))
    temp_route_details = RouteTempRouteMap.objects.filter(main_route_id=route_id)[0]
    data_dict['temp_route_details']['route_name'] = temp_route_details.temp_route.name
    data_dict['temp_route_details']['route_id'] = temp_route_details.temp_route_id
    temp_route_business_ids = get_business_ids(temp_route_details.temp_route_id, date, session_id)
    data_dict['temp_route_details']['business_details'] = []
    if not len(temp_route_business_ids) == 0:
        temp_route_tray_count = check_tray_count_for_route_rearrange(temp_route_details.temp_route_id, date, session_id)
        data_dict['temp_route_details']['tray_count'] = temp_route_tray_count['tray_count']
        for business_id in temp_route_business_ids:
            data_dict['temp_route_details']['business_details'].append(
                get_individual_business_data(business_id, date, session_id))
    else:
        data_dict['temp_route_details']['business_details'] = []
        data_dict['temp_route_details']['tray_count'] = 0
    data_dict['defalut_tray_capacity'] = RouteVehicleMap.objects.get(route_id=route_id).vehicle.tray_capacity
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def move_business_to_temp_route(request):
    print(request.data)
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    session_id = request.data['session_id']
    route_business_map = RouteBusinessMap.objects.get(route_id=request.data['main_route_id'],
                                                      business_id=request.data['selected_business_id'])
    route_business_map.route_id = request.data['temp_route_id']
    route_business_map.save()
    route_temp_route_map = RouteTempRouteMap.objects.get(main_route_id=request.data['main_route_id'],
                                                         temp_route_id=request.data['temp_route_id'])
    route_temp_route_map.is_active = True
    route_temp_route_map.save()
    vehicle_obj = RouteVehicleMap.objects.get(route_id=request.data['temp_route_id']).vehicle
    if not RouteTrace.objects.filter(route_id=request.data['temp_route_id'], date=date, session_id=session_id).exists():
        route_trace_obj = RouteTrace(indent_status_id=1,  # initiated
                                     route_id=request.data['temp_route_id'],
                                     vehicle_id=vehicle_obj.id,
                                     date=date,
                                     session_id=session_id,
                                     driver_name=vehicle_obj.driver_name,
                                     driver_phone=vehicle_obj.driver_mobile)
        route_trace_obj.save()
        if OverallIndentPerSession.objects.filter(date=date, session_id=session_id).exists():
            overall_route_trace_obj = OverallIndentPerSession.objects.get(date=date, session_id=session_id)
            overall_route_trace_obj.route_trace.add(route_trace_obj)
            overall_route_trace_obj.save()
    data_dict = {}

    data_dict['main_route_tray_count'] = check_tray_count_for_route_rearrange(request.data['main_route_id'], date,
                                                                              session_id)
    data_dict['temp_route_tray_count'] = check_tray_count_for_route_rearrange(request.data['temp_route_id'], date,
                                                                              session_id)
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def move_business_to_main_route(request):
    print(request.data)
    route_business_map = RouteBusinessMap.objects.get(route_id=request.data['temp_route_id'],
                                                      business_id=request.data['selected_business_id'])
    route_business_map.route_id = request.data['main_route_id']
    route_business_map.save()
    data_dict = {'temp_route_tray_count': {}, 'main_route_tray_count': {}}
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    session_id = request.data['session_id']

    temp_route_business_ids = get_business_ids(request.data['temp_route_id'], date, session_id)
    if not len(temp_route_business_ids) == 0:
        data_dict['temp_route_tray_count'] = check_tray_count_for_route_rearrange(request.data['temp_route_id'], date,
                                                                                  session_id)
    else:
        route_temp_route_map = RouteTempRouteMap.objects.get(main_route_id=request.data['main_route_id'],
                                                             temp_route_id=request.data['temp_route_id'])
        route_temp_route_map.is_active = False
        route_temp_route_map.save()
        data_dict['temp_route_tray_count']['tray_count'] = 0
        route_trace_obj = RouteTrace.objects.get(date=date, session_id=session_id,
                                                 route_id=request.data['temp_route_id'])
        if OverallIndentPerSession.objects.filter(date=date, session_id=session_id).exists():
            overall_route_trace_obj = OverallIndentPerSession.objects.get(date=date, session_id=session_id)
            overall_route_trace_obj.route_trace.remove(route_trace_obj)
            overall_route_trace_obj.save()
        RouteTrace.objects.get(date=date, session_id=session_id, route_id=request.data['temp_route_id']).delete()
    data_dict['main_route_tray_count'] = check_tray_count_for_route_rearrange(request.data['main_route_id'], date,
                                                                              session_id)
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_temp_route_details(request):
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    session_id = request.data['session_id']
    route_ids = list(Route.objects.filter(session_id=session_id, is_temp_route=False).values_list('id', flat=True))
    route_dict = {}
    for route_id in route_ids:
        temp_route_id = RouteTempRouteMap.objects.get(main_route_id=route_id).temp_route.id
        if not route_id in route_dict:
            route_dict[route_id] = {}
        if not temp_route_id in route_dict[route_id]:
            if RouteTrace.objects.filter(route_id=temp_route_id, session_id=session_id, date=date).exists():
                route_trace = RouteTrace.objects.get(route_id=temp_route_id, session_id=session_id, date=date)
                route_dict[route_id][temp_route_id] = route_trace.indent_status.id
            else:
                route_dict[route_id][temp_route_id] = 1
    return Response(data=route_dict, status=status.HTTP_200_OK) 


@api_view(['POST'])
def serve_temp_route_details_for_old_indent(request):
    date = request.data['date']
    session_id = request.data['session_id']
    route_ids = list(Route.objects.filter(session_id=session_id, is_temp_route=False).values_list('id', flat=True))
    route_dict = {}
    for route_id in route_ids:
        temp_route_id = RouteTempRouteMap.objects.get(main_route_id=route_id).temp_route.id
        if not route_id in route_dict:
            route_dict[route_id] = {}
        if not temp_route_id in route_dict[route_id]:
            if RouteTrace.objects.filter(route_id=temp_route_id, session_id=session_id, date=date).exists():
                route_trace = RouteTrace.objects.get(route_id=temp_route_id, session_id=session_id, date=date)
                route_dict[route_id][temp_route_id] = route_trace.indent_status.id
            else:
                route_dict[route_id][temp_route_id] = 1
    return Response(data=route_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def rerrange_to_original_route(request):
    route_id = request.data['temp_route_id']
    session_id = request.data['session_id']
    date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        date += datetime.timedelta(days=1)
    route_business_map = RouteBusinessMap.objects.filter(route_id=route_id).order_by('ordinal')
    main_route_id = RouteTempRouteMap.objects.get(temp_route_id=route_id).main_route.id
    for map in route_business_map:
        map.route_id = main_route_id
        map.save()
    route_trace_obj = RouteTrace.objects.get(date=date, session_id=session_id, route_id=request.data['temp_route_id'])
    if OverallIndentPerSession.objects.filter(date=date, session_id=session_id).exists():
        overall_route_trace_obj = OverallIndentPerSession.objects.get(date=date, session_id=session_id)
        overall_route_trace_obj.route_trace.remove(route_trace_obj)
        overall_route_trace_obj.save()
    RouteTrace.objects.get(date=date, session_id=session_id, route_id=request.data['temp_route_id']).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_album(request):
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    data_dict = service.albums().list().execute()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_photos_inside_album(request):
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    photos_inside_album = service.mediaItems().search(body=request.data).execute()
    return Response(data=photos_inside_album, status=status.HTTP_200_OK)


def convert_to_encode(image):
    try:
        image_path = 'static/media/' + image
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            return encoded_image
    except Exception as e:
        return None


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_active_carrier(request):
    data_dict = {
        'carrier_list': [],
        'carrier_image_dict': {}
    }
    today = datetime.datetime.now()
    carrier_obj = Carrier.objects.filter(expires_on__gte=today, is_active=True)
    carrier_list = list(
        carrier_obj.values_list('id', 'title', 'description', 'publish_from', 'expires_on', 'created_by', 'is_active',
                                'last_date_for_apply',
                                'time_created', 'time_modified'))
    carrier_column = ['id', 'title', 'description', 'publish_from', 'expires_on', 'created_by', 'is_active',
                      'last_date_for_apply',
                      'time_created', 'time_modified']
    carrier_df = pd.DataFrame(carrier_list, columns=carrier_column)
    if not carrier_df.empty:
        data_dict['carrier_list'] = carrier_df.to_dict('r')
    carrier_file_map_obj = CarrierFileMap.objects.filter(carrier__expires_on__gte=today, carrier__is_active=True)
    carrier_file_map_list = list(carrier_file_map_obj.values_list('id', 'carrier_id', 'document_name', 'file'))
    carrier_file_map_column = ['id', 'carrier_id', 'document_name', 'file']
    carrier_file_map_df = pd.DataFrame(carrier_file_map_list, columns=carrier_file_map_column)
    if not carrier_file_map_df.empty:
        carrier_file_map_df['file'] = carrier_file_map_df.apply(lambda x: convert_to_encode(x['file']), axis=1)
        carrier_file_map_dict = carrier_file_map_df.groupby('carrier_id').apply(lambda x: x.to_dict('r')).to_dict()
        data_dict['carrier_image_dict'] = carrier_file_map_dict

    return Response(data=data_dict, status=status.HTTP_200_OK) 


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_active_tender(request):
    data_dict = {
        'tender_list': [],
        'tender_image_dict': {}
    }
    today = datetime.datetime.now()
    tender_obj = Tender.objects.filter(expires_on__gte=today, is_active=True)
    tender_list = list(
        tender_obj.values_list('id', 'title', 'description', 'publish_from', 'expires_on', 'created_by', 'is_active',
                               'ends_on',
                               'time_created', 'time_modified'))
    tender_column = ['id', 'title', 'description', 'publish_from', 'expires_on', 'created_by', 'is_active',
                     'tender_ends_on',
                     'time_created', 'time_modified']
    tender_df = pd.DataFrame(tender_list, columns=tender_column)
    if not tender_df.empty:
        data_dict['tender_list'] = tender_df.to_dict('r')
    tender_file_map_obj = TenderFileMap.objects.filter(tender__expires_on__gte=today, tender__is_active=True)
    tender_file_map_list = list(tender_file_map_obj.values_list('id', 'tender_id', 'document_name', 'file'))
    tender_file_map_column = ['id', 'tender_id', 'document_name', 'file']
    tender_file_map_df = pd.DataFrame(tender_file_map_list, columns=tender_file_map_column)
    if not tender_file_map_df.empty:
        tender_file_map_df['file'] = tender_file_map_df.apply(lambda x: convert_to_encode(x['file']), axis=1)
        tender_file_map_dict = tender_file_map_df.groupby('tender_id').apply(lambda x: x.to_dict('r')).to_dict()
        data_dict['tender_image_dict'] = tender_file_map_dict
    return Response(data=data_dict, status=status.HTTP_200_OK)


def get_business_details(zone_id, exclude_business_ids):
    businss_obj = BusinessAgentMap.objects.filter(business__zone_id=zone_id, business__is_active=True).exclude(
        business_id__in=exclude_business_ids)
    business_list = list(
        businss_obj.values_list('business_id', 'business__business_type', 'business__code', 'agent__first_name',
                                'agent__last_name'))
    business_column = ['business_id', 'business_type_id', 'business_code', 'agent_first_name', 'agent_last_name']
    business_df = pd.DataFrame(business_list, columns=business_column)
    business_df = business_df.groupby('business_type_id').apply(lambda x: x.to_dict('r')).to_dict()
    return business_df


@api_view(['GET'])
def serve_zone_wise_ordered_business_data(request):
    tomorrow_date = datetime.datetime.now() + datetime.timedelta(days=1)
    zone_obj = Zone.objects.all()
    data_dict = {
        'zone_with_count_dict': {},
        'zone_list': []
    }
    zone_list = list(zone_obj.values_list('id', 'name'))
    zone_column = ['id', 'name']
    zone_df = pd.DataFrame(zone_list, columns=zone_column)
    data_dict['zone_list'] = zone_df.to_dict('r')
    for zone in zone_obj:
        if not zone.id in data_dict['zone_with_count_dict']:
            data_dict['zone_with_count_dict'][zone.id] = {}
        data_dict['zone_with_count_dict'][zone.id]['ovellall_business_count'] = Business.objects.filter(
            zone=zone, is_active=True).count()
        data_dict['zone_with_count_dict'][zone.id]['orderered_business_via_portal'] = len(list(set(
            SaleGroup.objects.filter(business__zone=zone, date=tomorrow_date, ordered_via_id=2).values_list(
                'business_id', flat=True))))
        data_dict['zone_with_count_dict'][zone.id]['orderered_business_via_mobile'] = len(list(set(
            SaleGroup.objects.filter(business__zone=zone, date=tomorrow_date, ordered_via_id=1).values_list(
                'business_id', flat=True))))
        data_dict['zone_with_count_dict'][zone.id]['unordered_business_count'] = \
            data_dict['zone_with_count_dict'][zone.id]['ovellall_business_count'] - (
                    data_dict['zone_with_count_dict'][zone.id]['orderered_business_via_mobile'] +
                    data_dict['zone_with_count_dict'][zone.id]['orderered_business_via_portal'])
        ordered_business_ids = list(
            SaleGroup.objects.filter(business__zone=zone, date=tomorrow_date).values_list('business_id', flat=True))
        data_dict['zone_with_count_dict'][zone.id]['un_ordered_list'] = get_business_details(zone.id,
                                                                                             ordered_business_ids)
    business_type_obj = BusinessType.objects.all()
    business_type_list = list(business_type_obj.values_list('id', 'name'))
    business_type_column = ['id', 'name']
    business_type_df = pd.DataFrame(business_type_list, columns=business_type_column)
    data_dict['business_type_list'] = business_type_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_counter_list(request):
    employee_obj = Employee.objects.get(user_profile__user=request.user)
    if employee_obj.business_group is not None:
        counter_obj = Counter.objects.filter(is_active=True, collection_center__business_group_id=employee_obj.business_group.id).order_by('id')
        booth_or_customer_json = [{'name': 'booth', 'display_name': 'Booth'}]
    else:
        counter_obj = Counter.objects.filter(is_active=True).order_by('id')
        booth_or_customer_json = [{'name': 'booth', 'display_name': 'Booth'}, {'name': 'customer', 'display_name': 'Customer'}]

    counter_list = list(
        counter_obj.values_list('id', 'name', 'collection_center', 'collection_center__building_name'))
    counter_column = ['id', 'name', 'collection_center', 'collection_center_name']
    counter_df = pd.DataFrame(counter_list, columns=counter_column)
    final_list = counter_df.to_dict('r')
    if employee_obj.business_group is None:
        online_json = {
            'id': 'online',
            'name': 'Online',
            'collection_center': 'Online',
            'collection_center_name': 'Online',
            }
        final_list.append(online_json)
    data_dict = {
        'final_list': final_list,
        'booth_or_customer_json': booth_or_customer_json
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
def delete_selected_order(request):
    sid = transaction.savepoint()
    session_list = [1, 2]
    indent_status = True
    order_date = request.data['selected_date']
    business_code = request.data['business_code']
    for session_id in session_list:
        if RouteTrace.objects.filter(date=order_date, route__routebusinessmap__business__code=business_code,
                                     session_id=session_id).exists():
            route_trace_obj = RouteTrace.objects.get(date=order_date,
                                                     route__routebusinessmap__business__code=business_code,
                                                     session_id=session_id)
            if session_id == 1:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
                    break
            else:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
    if indent_status:
        try:
            if SuperSaleGroup.objects.filter(delivery_date=request.data['selected_date'],
                                            business__code=request.data['business_code']).exists():
                super_sale_group_obj = SuperSaleGroup.objects.filter(delivery_date=request.data['selected_date'],
                                                                    business__code=request.data['business_code'])[0]
                super_sale_group_obj.mor_sale_group = None
                super_sale_group_obj.eve_sale_group = None
                super_sale_group_obj.save()
            sale_group_obj = SaleGroup.objects.filter(date=request.data['selected_date'],
                                                    business__code=request.data['business_code'])
            total_amount = 0
            for sale in sale_group_obj:
                delete_sale_group_obj = SaleGroupDeleteLog(business_id=sale.business.id,
                                                        delivery_date=sale.date,
                                                        total_cost=sale.total_cost,
                                                        session_id=sale.session.id,
                                                        ordered_by_id=sale.ordered_by.id,
                                                        ordered_date_time=sale.time_created,
                                                        deleted_by_id=request.user.id,
                                                        delete_date_time=datetime.datetime.now())
                delete_sale_group_obj.save()
                total_amount += sale.total_cost
            sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=request.data['selected_date'],
                                                                    super_sale_group_id=super_sale_group_obj.id,
                                                                    sale_group_order_type_id=3,  # order decrease
                                                                    counter_amount=-total_amount)
            sale_group_transaction_trace.save()
            SaleGroup.objects.filter(date=request.data['selected_date'],
                                    business__code=request.data['business_code']).delete()
            date_in_format = datetime.datetime.strptime(request.data['selected_date'], '%Y-%m-%d')
            # Get mor route business ids
            mor_route_id = RouteBusinessMap.objects.get(business__code=request.data['business_code'],
                                                        route__session_id=1).route.id
            business_ids = list(
                RouteBusinessMap.objects.filter(route_id=mor_route_id).values_list('business_id', flat=True))
            if not SaleGroup.objects.filter(business_id__in=business_ids, date=request.data['selected_date']).exists():
                if not ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date_in_format.month,
                                                        date__year=date_in_format.year).exists():
                    RouteTrace.objects.filter(date=request.data['selected_date'], route_id=mor_route_id).delete()
            # Get eve route business ids
            eve_route_id = RouteBusinessMap.objects.get(business__code=request.data['business_code'],
                                                        route__session_id=2).route.id
            business_ids = list(
                RouteBusinessMap.objects.filter(route_id=eve_route_id).values_list('business_id', flat=True))
            if not SaleGroup.objects.filter(business_id__in=business_ids, date=request.data['selected_date']).exists():
                if not ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date_in_format.month,
                                                        date__year=date_in_format.year).exists():
                    RouteTrace.objects.filter(date=request.data['selected_date'], route_id=eve_route_id).delete()
            transaction.savepoint_commit(sid)
        except Exception as e:
            print('Error - {}'.format(e))
            transaction.savepoint_rollback(sid)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@transaction.atomic
def delete_selected_order_from_website(request):
    print(request.data)
    sid = transaction.savepoint()
    business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=request.user)

    session_list = [1, 2]
    indent_status = True
    order_date = request.data['selected_date']
    for session_id in session_list:
        if RouteTrace.objects.filter(date=order_date, route__routebusinessmap__business_id=business_agent_obj.business.id,
                                     session_id=session_id).exists():
            route_trace_obj = RouteTrace.objects.get(date=order_date,
                                                     route__routebusinessmap__business_id=business_agent_obj.business.id,
                                                     session_id=session_id)
            if session_id == 1:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
                    break
            else:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
    if indent_status:
        try:
            order_category_dict = {}
            for map_obj in BusinessTypeOrderCategoryeMap.objects.filter(business_type_id=business_agent_obj.business.business_type_id):
                if not map_obj.order_category.id in order_category_dict:
                    order_category_dict[map_obj.order_category.id] = map_obj.payment_option.id
            business_id = business_agent_obj.business.id
            business_type_id = business_agent_obj.business.business_type.id
            agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent.id
            agent_wallet = AgentWallet.objects.get(agent_id=agent_id)
            before_wallet_balance = agent_wallet.current_balance
            total_amount = 0
            if SuperSaleGroup.objects.filter(delivery_date=request.data['selected_date'], business_id=business_id).exists():
                super_sale_group_obj = \
                SuperSaleGroup.objects.filter(delivery_date=request.data['selected_date'], business_id=business_id)[0]
                super_sale_group_obj.mor_sale_group = None
                super_sale_group_obj.eve_sale_group = None
                super_sale_group_obj.save()

            sale_group_obj = SaleGroup.objects.filter(date=request.data['selected_date'], business_id=business_id)
            for sale in sale_group_obj:
                delete_sale_group_obj = SaleGroupDeleteLog(business_id=sale.business.id,
                                                        delivery_date=sale.date,
                                                        total_cost=sale.total_cost,
                                                        session_id=sale.session.id,
                                                        ordered_by_id=sale.ordered_by.id,
                                                        ordered_date_time=sale.time_created,
                                                        deleted_by_id=request.user.id,
                                                        delete_date_time=datetime.datetime.now())
                delete_sale_group_obj.save()
            date = None
            for sale in SaleGroup.objects.filter(date=request.data['selected_date'], business_id=business_id):
                date = sale.date
                if sale.ordered_via.id != 2:
                    if order_category_dict[1] == 1 :
                        total_amount += sale.total_cost
            agent_wallet.current_balance += total_amount
            agent_wallet.save()
            if order_category_dict[1] == 1:
                message = 'Order deleted and the money ' + str(total_amount) +' has been deposited to your wallet. For the Delivery date : ' + str(date)
                purpose = ''
                try:
                    template_id = BsnlSmsTemplate.objects.filter(message_name='delete_order_from_website').first().template_id
                    template_list = [
                        {'Key': 'amount', 'Value': str(total_amount)},
                        {'Key': 'date', 'Value': str(date)}
                    ]
                    send_message_from_bsnl(template_id, template_list, business_agent_obj.agent.agent_profile.mobile)
                except Exception as e:
                    print(e)
                # send_message_via_netfision(purpose, business_agent_obj.agent.agent_profile.mobile, message)
            transaction_obj = TransactionLog(
                date=datetime.datetime.now(),
                transacted_by=request.user,
                transacted_via_id=3,
                data_entered_by=request.user,
                amount=total_amount,
                transaction_direction_id=3,  # from  aavin to agent wallet
                transaction_mode_id=1,  # Upi
                transaction_status_id=2,  # completed
                transaction_id='1234',
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=before_wallet_balance,
                wallet_balance_after_transaction_approval=agent_wallet.current_balance,
                description='Amount for refunding amount from aavin to agent wallet',
                modified_by=request.user
            )
            transaction_obj.save()

            sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=request.data['selected_date'],
                                                                    super_sale_group_id=super_sale_group_obj.id,
                                                                    sale_group_order_type_id=3,  # order decrease
                                                                    wallet_amount=-total_amount,
                                                                    wallet_transaction_id=transaction_obj.id,
                                                                    counter_id=23)
            sale_group_transaction_trace.save()
            SaleGroup.objects.filter(date=request.data['selected_date'], business_id=business_id).delete()
            date_in_format = datetime.datetime.strptime(request.data['selected_date'], '%Y-%m-%d')
            # Get mor route business ids
            mor_route_id = RouteBusinessMap.objects.get(business_id=business_id, route__session_id=1).route.id
            business_ids = list(
                RouteBusinessMap.objects.filter(route_id=mor_route_id).values_list('business_id', flat=True))
            if not SaleGroup.objects.filter(business_id__in=business_ids, date=request.data['selected_date']).exists():
                if not ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date_in_format.month,
                                                        date__year=date_in_format.year).exists():
                    RouteTrace.objects.filter(date=request.data['selected_date'], route_id=mor_route_id).delete()
            # Get eve route business ids
            eve_route_id = RouteBusinessMap.objects.get(business_id=business_id, route__session_id=2).route.id
            business_ids = list(
                RouteBusinessMap.objects.filter(route_id=eve_route_id).values_list('business_id', flat=True))
            if not SaleGroup.objects.filter(business_id__in=business_ids, date=request.data['selected_date']).exists():
                if not ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date_in_format.month,
                                                        date__year=date_in_format.year).exists():
                    RouteTrace.objects.filter(date=request.data['selected_date'], route_id=eve_route_id).delete()
            transaction.savepoint_commit(sid)
        except Exception as e:
            print('Error - {}'.format(e))
            transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_counter_report_for_agent(request):
    if request.data['selected_report_option'] == 'booth':
        data = serve_counter_order_details_for_agent(request.data['selected_counter_id'], request.data['selected_date'],
                                                     request.user.first_name)
        return Response(data=data, status=status.HTTP_200_OK)
    elif request.data['selected_report_option'] == 'customer':
        data = serve_counter_order_details_for_icustomer(request.data['selected_counter_id'],
                                                         request.data['selected_date'], request.user.first_name)
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_counter_report_json_for_agent(request):
    counter_id = request.data['selected_counter_id']
    date = request.data['selected_date']
    user_name = request.user.first_name

    if counter_id == 'online':
        ws_sale_group_obj = SaleGroup.objects.filter(time_created__date=date, ordered_via_id__in=[1, 3],
                                                     business__business_type_id=9).order_by('id')
        ns_sale_group_obj = SaleGroup.objects.filter(time_created__date=date, ordered_via_id__in=[1, 3], business__business_type_id__in=[1, 2, 11, 12]).order_by('id')
        counter_name = 'Online'
    else:
        counter_employee_trace_obj = CounterEmployeeTraceMap.objects.filter(counter_id=counter_id, time_created__date=date).order_by('-id')
        employee_trace_ids = list(counter_employee_trace_obj.values_list('id', flat=True))
        
        if not counter_id == 29:
            # check wheathe all order maps with employess counter start
            ordered_employee_user_ids = list(counter_employee_trace_obj.values_list('employee__user_profile__user_id', flat=True))
            ordered_sale_group_ids = list(SaleGroup.objects.filter(ordered_by_id__in=ordered_employee_user_ids, time_created__date=date).values_list('id', flat=True))
            employee_trace_sale_group_obj = list(
                CounterEmployeeTraceSaleGroupMap.objects.filter(
                    counter_employee_trace_id__in=employee_trace_ids).values_list(
                    'sale_group', flat=True))
            if not len(ordered_sale_group_ids) == len(employee_trace_sale_group_obj):
                for ordered_sale_group_id in ordered_sale_group_ids:
                    if not ordered_sale_group_id in employee_trace_sale_group_obj:
                        counter_sale_obj = CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace__in=counter_employee_trace_obj)[0]
                        counter_sale_obj.sale_group.add(ordered_sale_group_id)
                        counter_sale_obj.save()

            # check wheathe all order maps with employess counter end

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

    for ns in ns_sale_group_obj.order_by('time_created'):
        ns_sale = Sale.objects.filter(sale_group_id=ns.id, product__is_active=True)
        time = ns.time_created
        time_now = time.astimezone(timezone('Asia/Kolkata'))
        time_created = time_now.strftime("%I:%M")
        if not ns.business.code in data_dict["booth_sale"]:
            data_dict["booth_sale"][ns.business.code] = {
                "time": time_created,
                "zone": ns.business.zone.name,
                "agent_name": BusinessAgentMap.objects.get(
                    business_id=ns.business.id).agent.first_name[:5],
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

    for ws in ws_sale_group_obj.order_by('time_created'):
        ws_sale = Sale.objects.filter(sale_group_id=ws.id, product__is_active=True)
        time = ws.time_created
        time_now = time.astimezone(timezone('Asia/Kolkata'))
        time_created = time_now.strftime("%I:%M")
        if not ws.business.code in data_dict["booth_sale"]:
            data_dict["booth_sale"][ws.business.code] = {
                "time": time_created,
                "zone": ws.business.zone.name,
                "agent_name": BusinessAgentMap.objects.get(
                    business_id=ws.business.id).agent.first_name[:5],
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
    product_list = list(products.values_list('id', 'name', 'short_name', 'quantity'))
    product_column = ['id', 'name', 'short_name', 'quantity']
    product_df = pd.DataFrame(product_list, columns=product_column)
    data_dict['product_list'] = product_df.to_dict('r')
    data_dict['booth_list'] = data_dict['booth_sale'].keys()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_counter_report_json_for_agent_delivery(request):
    counter_id = request.data['selected_counter_id']
    date = request.data['selected_date']
    next_date = datetime.datetime.strptime(date, '%Y-%m-%d')
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
            CounterEmployeeTraceMap.objects.filter(counter_id=counter_id, collection_date=date,
                                                   counteremployeetracesalegroupmap__sale_group__date=next_date).values_list(
                'id',
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
    for ns in ns_sale_group_obj.order_by('time_created'):
        if counter_id == 'online':
            if ns.business.business_type_id in online_business_type_ids:
                ns_sale = Sale.objects.filter(sale_group_id=ns.id, product__is_active=True)
                time = ns.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ns.business.code in data_dict["booth_sale"]:
                    data_dict["booth_sale"][ns.business.code] = {
                        "time": time_created,
                        "zone": ns.business.zone.name,
                        "agent_name": BusinessAgentMap.objects.get(
                            business_id=ns.business.id).agent.first_name[:5],
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
        else:
            ns_sale = Sale.objects.filter(sale_group_id=ns.id, product__is_active=True)
            time = ns.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")
            if not ns.business.code in data_dict["booth_sale"]:
                data_dict["booth_sale"][ns.business.code] = {
                    "time": time_created,
                    "zone": ns.business.zone.name,
                    "agent_name": BusinessAgentMap.objects.get(
                        business_id=ns.business.id).agent.first_name[:5],
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

    for ws in ws_sale_group_obj.order_by('time_created'):
        if counter_id == 'online':
            if ws.business.business_type_id in online_business_type_ids:
                ws_sale = Sale.objects.filter(sale_group_id=ws.id, product__is_active=True)
                time = ws.time_created
                time_now = time.astimezone(timezone('Asia/Kolkata'))
                time_created = time_now.strftime("%I:%M")
                if not ws.business.code in data_dict["booth_sale"]:
                    data_dict["booth_sale"][ws.business.code] = {
                        "time": time_created,
                        "zone": ws.business.zone.name,
                        "agent_name": BusinessAgentMap.objects.get(
                            business_id=ws.business.id).agent.first_name[:5],
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
        else:
            ws_sale = Sale.objects.filter(sale_group_id=ws.id, product__is_active=True)
            time = ws.time_created
            time_now = time.astimezone(timezone('Asia/Kolkata'))
            time_created = time_now.strftime("%I:%M")
            if not ws.business.code in data_dict["booth_sale"]:
                data_dict["booth_sale"][ws.business.code] = {
                    "time": time_created,
                    "zone": ws.business.zone.name,
                    "agent_name": BusinessAgentMap.objects.get(
                        business_id=ws.business.id).agent.first_name[:5],
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
    product_list = list(products.values_list('id', 'name', 'short_name', 'quantity'))
    product_column = ['id', 'name', 'short_name', 'quantity']
    product_df = pd.DataFrame(product_list, columns=product_column)
    data_dict['product_list'] = product_df.to_dict('r')
    data_dict['booth_list'] = data_dict['booth_sale'].keys()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_user_is_anonymous(request):
    if request.user.is_anonymous:
        data_dict = {
            'status': True,
            'message': 'Your session is expired please relogin'
        }
    else:
        data_dict = {
            'status': False
        }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_counter_report_json_for_customer(request):
    counter_id = request.data['selected_counter_id']
    date = request.data['selected_date']
    if counter_id == 'online':
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(time_created__date=date,
                                                                     ordered_via_id__in=[1, 3]).order_by('id')
        counter_name = 'Online'
    else:
        counter_employee_trace_obj = CounterEmployeeTraceMap.objects.filter(counter_id=counter_id, time_created__date=date).order_by('-id')
        employee_trace_ids = list(counter_employee_trace_obj.values_list('id', flat=True))
        
        # check wheather all order maps with employess counter start
        ordered_employee_user_ids = list(counter_employee_trace_obj.values_list('employee__user_profile__user_id', flat=True))
        ordered_icustomer_sale_group_ids = list(ICustomerSaleGroup.objects.filter(ordered_by_id__in=ordered_employee_user_ids, time_created__date=date).values_list('id', flat=True))
        employee_trace_sale_group_obj = list(
            CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace_id__in=employee_trace_ids).order_by(
                'icustomer_sale_group').values_list(
                'icustomer_sale_group', flat=True))
        if not len(ordered_icustomer_sale_group_ids) == len(employee_trace_sale_group_obj):
            for ordered_icustomer_sale_group_id in ordered_icustomer_sale_group_ids:
                if not ordered_icustomer_sale_group_id in employee_trace_sale_group_obj:
                    counter_sale_obj = CounterEmployeeTraceSaleGroupMap.objects.get(counter_employee_trace_id=counter_employee_trace_obj[0].id)
                    counter_sale_obj.icustomer_sale_group.add(ordered_icustomer_sale_group_id)
                    counter_sale_obj.save()

        # check wheather all order maps with employess counter end

        employee_trace_sale_group_obj = list(
            CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace_id__in=employee_trace_ids).order_by(
                'icustomer_sale_group').values_list(
                'icustomer_sale_group', flat=True))
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(id__in=employee_trace_sale_group_obj).order_by(
            'id')
        counter_name = Counter.objects.get(id=counter_id).name
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group_id__in=icustomer_sale_group_obj,
                                                      product__is_active=True)
    products = Product.objects.filter(group_id=1, is_active=True).order_by('display_ordinal')

    data_dict = {
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
        "product_total_count": {}
    }
    if counter_id == 'online':
        data_dict["counter_details"]["employee_name"].append('-')
    else:
        for employee_trace_id in employee_trace_ids:
            employee_name = CounterEmployeeTraceMap.objects.get(
                id=employee_trace_id).employee.user_profile.user.first_name
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
                "customer_name": icustomer_sale_group.icustomer.user_profile.user.first_name[:5],
                "total_cost": icustomer_sale_group.total_cost,
                "icustomer_sale_group_id": icustomer_sale_group.id,
                "customer_code": icustomer_sale_group.icustomer.customer_code
            }
            data_dict["agent_details"].append(tempicustomer_sale_group_dict)

    product_list = []
    for product in products:
        product_list.append(product.id)

    #     for product_id in product_list:
    for icustomer_sale in icustomer_sale_obj:
        #         print(icustomer_sale.icustomer_sale_group.icustomer_id)
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
            except:
                pass

    product_list = list(products.values_list('id', 'name', 'short_name', 'quantity'))
    product_column = ['id', 'name', 'short_name', 'quantity']
    product_df = pd.DataFrame(product_list, columns=product_column)
    data_dict['product_list'] = product_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_product_discount_price_for_update(request):
    if BusinessWiseProductDiscount.objects.filter(business_id=request.data['booth_id']).exists:
        product_prices = BusinessWiseProductDiscount.objects.filter(business_id=request.data['booth_id'])
        data_dict = {}
        for product_price in product_prices:
            data_dict[product_price.product.id] = product_price.discounted_price
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_total_sale_for_selected_date_counter_wise(request):
    data = serve_total_sale_counter_wise(request.data['selected_date'], request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_total_sale_for_selected_date_counter_wise_as_json(request):
    # date = request.data['selected_date']
    # employee_trace_objs = CounterEmployeeTraceMap.objects.filter(collection_date=date)

    # data_dict = {
    #     "date": date,
    #     "icustomer_sale": {},
    #     "sale": {}
    # }
    # counter_obj = Counter.objects.all().order_by('name')
    # for counter in counter_obj:
    #     if not counter.id in data_dict["icustomer_sale"]:
    #         data_dict["icustomer_sale"][counter.id] = 0
    #     if not counter.id in data_dict["sale"]:
    #         data_dict["sale"][counter.id] = 0
    # icustomer_total_sale = 0
    # agent_total_sale = 0
    # for employee_trace_obj in employee_trace_objs:
    #     #     print(employee_trace_id)
    #     icus_groups = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
    #         counter_employee_trace_id=employee_trace_obj.id).values_list('icustomer_sale_group', flat=True))
    #     for icus_group in icus_groups:
    #         try:
    #             total_sale = ICustomerSaleGroup.objects.get(
    #                 id=icus_group).total_cost_for_month
    #             data_dict["icustomer_sale"][employee_trace_obj.counter_id] += total_sale
    #             icustomer_total_sale += total_sale
    #         except:
    #             pass
    #     agent_order = list(CounterEmployeeTraceSaleGroupMap.objects.filter(
    #         counter_employee_trace_id=employee_trace_obj.id).values_list('sale_group', flat=True))
    #     for sale_grp in agent_order:
    #         try:
    #             total_sale = SaleGroup.objects.get(id=sale_grp).total_cost
    #             data_dict["sale"][employee_trace_obj.counter_id] += total_sale
    #             agent_total_sale +=  total_sale
    #         except:
    #             pass
    # data_dict['agent_total_sale'] = agent_total_sale
    # data_dict['icustomer_total_sale'] = icustomer_total_sale
    # data_dict['grand_total'] = icustomer_total_sale + agent_total_sale
    # counter_list = list(counter_obj.values_list('id', 'name'))
    # counter_column = ['id', 'name']
    # counter_df = pd.DataFrame(counter_list, columns=counter_column)
    # data_dict['counter_list'] = counter_df.to_dict('r')
    return Response(data=[], status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_total_sale_per_month_in_counter(request):
    print(request.data)
    month = request.data['selected_month']
    year = request.data['selected_year']
    data = serve_total_sale_per_month(month, year, request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_total_sale_per_month_in_counter_as_json(request):
    print(request.data)
    year = request.data['selected_year']
    month = request.data['selected_month']
    counter_obj = Counter.objects.filter().order_by('name')
    total_days = monthrange(year, month)[1]
    month_dict = {
        "Current_month": month_name[month],
    }
    grand_total = 0
    temp_icustomer_total = 0
    temp_agent_total = 0
    date_list = []
    for day in range(1, (total_days + 1)):
        date = str(year) + "-" + str(month) + "-" + str(day)
        data_dict = total_sale_per_date(date)
        month_dict[date] = data_dict

        icus_total_order = 0
        agent_total_order = 0
        total = 0
        for counter in counter_obj:
            # calculating total sale of i_customer for a day
            icus_total_order += month_dict[date]["icustomer_sale"][counter.id]
            # calculating total sale of agent for a day
            agent_total_order += month_dict[date]["sale"][counter.id]
            # calculating total sale of agent & i_customer in particular counter for a day
            total += month_dict[date]["icustomer_sale"][counter.id] + month_dict[date]["sale"][counter.id]
            # month_dict[date]["total_sale_of_counter - " + str(counter.id)] = total

        grand_total += total
        temp_icustomer_total += icus_total_order
        temp_agent_total += agent_total_order
        month_dict[date]["icus_total_order"] = icus_total_order
        month_dict[date]["agent_total_order"] = agent_total_order
        date_list.append(date)
    month_dict['grand_total'] = grand_total
    month_dict['total_icustomer_total'] = temp_icustomer_total
    month_dict['total_agent_total'] = temp_agent_total
    month_dict['date_list'] = date_list
    return Response(data=month_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_route_wise_sale_abstract(request):
    print(request.data)
    data = serve_route_wise_sale_for_selected_session(request.data['selected_date'],
                                                      request.data['selected_session_id'], request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_business_type_wise_summary(request):
    print(request.data)
    data = serve_business_type_wise_summay(request.data['selected_date'], request.data['selected_session_id'],
                                           request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK) 


@api_view(['POST'])
def serve_union_wise_summary(request):
    print(request.data)
    data = serve_union_wise_summay(request.data['selected_date'], request.data['selected_session_id'],
                                   request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_zone_wise_route_abstract(request):
    print(request.data)
    data = serve_zone_wise_route_abstract_for_selected_date(request.data['selected_date'], request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_milk_acknowledgement_report(request):
    print(request.data)
    data = serve_milk_acknowledgement_report_for_selected_session(request.data['selected_date'],
                                                                  request.data['selected_session_id'],
                                                                  request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_all_zone_report(request):
    print(request.data)
    data = serve_all_zone_report_per_session(request.data['selected_date'], request.data['selected_session_id'],
                                             request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_daily_zone_wise_sale(request):
    print(request.data)
    data = serve_daily_sale_for_selected_zone(request.data['selected_date'], request.data['selected_zone_id'],
                                              request.user.first_name, request.data['selected_session_id'])
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_unique_route_wise_sale_abstract(request):
    print(request.data)
    data = serve_unique_route_wise_sale_for_selected_date(request.data['selected_date'], request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_route_wise_sale_statement(request):
    print(request.data)
    data = get_route_wise_statement_pdf(request.data['selected_route_id'], request.data['selected_session_id'],
                                        request.data['selected_date'], request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_zone_wise_abstract(request):
    print(request.data)
    data = serve_zone_wise_abstract_pdf(request.data['selected_date'], request.user.first_name)
    return Response(data=data, status=status.HTTP_200_OK)


# state based district
@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_state_based_district(request):
    state_list = {}
    for state in State.objects.all():
        state_list[state.id] = []
        for dist in District.objects.filter(state=state.id):
            district_dict = {
                "name": dist.name,
                "id": dist.id
            }
            state_list[state.id].append(district_dict)
    return Response(data=state_list, status=status.HTTP_200_OK)


# district based taluk
@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_district_based_taluk(request):
    district_dict = {}
    for district in District.objects.all():
        district_dict[district.id] = []
        for taluk in Taluk.objects.filter(district=district.id):
            taluk_dict = {
                "name": taluk.name,
                "id": taluk.id
            }
            district_dict[district.id].append(taluk_dict)
    return Response(data=district_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_selected_icustomer_sale(request):
    print("request_data.........................", request.data)
    date_in_format = datetime.datetime.strptime(request.data['date'], '%Y-%m-%d')
    if ICustomerSaleGroup.objects.filter(date__month=date_in_format.month, date__year=date_in_format.year,
                                         icustomer_id=request.data['icustomer_id']).exists():
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(date__month=date_in_format.month,
                                                                     date__year=date_in_format.year,
                                                                     icustomer_id=request.data['icustomer_id'])

        icustomer_sale_group_list = list(icustomer_sale_group_obj.values_list('id', 'business_id', 'business__code',
                                                                              'business__business_type_id',
                                                                              'icustomer_id',
                                                                              'icustomer__customer_code',
                                                                              'date', 'session',
                                                                              'session__display_name', 'ordered_via',
                                                                              'ordered_via__name',
                                                                              'payment_status__name',
                                                                              'sale_status__name', 'total_cost',
                                                                              'total_cost_for_month',
                                                                              'time_created', 'ordered_by__first_name',
                                                                              'ordered_by_id'))
        icustomer_sale_group_column = ['icustomer_sale_group_id', 'business_id', 'business_code', 'business_type_id',
                                       'icustomer_id',
                                       'icustomer_code', 'date', 'session_id', 'session_name',
                                       'ordered_via_id', 'ordered_via_name', 'payment_status',
                                       'sale_status',
                                       'session_wise_price', 'total_cost_for_month', 'order_date', 'ordered_by_name',
                                       'ordered_by_id']
        icustomer_sale_group_df = pd.DataFrame(icustomer_sale_group_list, columns=icustomer_sale_group_column)
        icustomer_sale_group_df['month'] = pd.DatetimeIndex(icustomer_sale_group_df['date']).month
        icustomer_sale_group_df['year'] = pd.DatetimeIndex(icustomer_sale_group_df['date']).year

        sale_json = icustomer_sale_group_df.to_dict('r')

        icustomer_sale_group_obj.delete()

        coutomer_order_delete_obj = CustomerOrderDeleteLog(customer_id=sale_json[0]['icustomer_id'],
                                                           ordered_on=sale_json[0]['order_date'],
                                                           ordered_by_id=sale_json[0]['ordered_by_id'],
                                                           deleted_on=datetime.datetime.now(),
                                                           deleted_by_id=request.user.id,
                                                           date_of_delivery=sale_json[0]['date'],
                                                           deleted_value_json=sale_json)
        coutomer_order_delete_obj.save()
        print(coutomer_order_delete_obj.deleted_value_json)

    total_days_in_month = monthrange(date_in_format.year, date_in_format.month)[1]
    for date_count in range(1, int(total_days_in_month + 1)):
        date = request.data['date'][:7] + '-' + str(date_count)
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        mor_route_id = RouteBusinessMap.objects.get(business_id=request.data['business_id'],
                                                    route__session_id=1).route.id
        business_ids = list(
            RouteBusinessMap.objects.filter(route_id=mor_route_id).values_list('business_id', flat=True))
        if not SaleGroup.objects.filter(business_id__in=business_ids, date=date).exists():
            if not ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date_in_format.month,
                                                     date__year=date_in_format.year).exists():
                RouteTrace.objects.filter(date=date, route_id=mor_route_id).delete()
        # Get eve route business ids
        eve_route_id = RouteBusinessMap.objects.get(business_id=request.data['business_id'],
                                                    route__session_id=2).route.id
        business_ids = list(
            RouteBusinessMap.objects.filter(route_id=eve_route_id).values_list('business_id', flat=True))
        if not SaleGroup.objects.filter(business_id__in=business_ids, date=date).exists():
            if not ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date_in_format.month,
                                                     date__year=date_in_format.year).exists():
                RouteTrace.objects.filter(date=date, route_id=eve_route_id).delete()
    ICustomerSerialNumberMap.objects.filter(month=date_in_format.month, year=date_in_format.year,
                                            icustomer_id=request.data['icustomer_id']).delete()

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_selected_icustomer_sale_for_current_month(request):
    print("request_data.........................", request.data)
    date_in_format = datetime.datetime.strptime(request.data['date'], '%Y-%m-%d')
    if ICustomerSaleGroup.objects.filter(date__month=date_in_format.month, date__year=date_in_format.year,
                                         icustomer_id=request.data['icustomer_id']).exists():
        icustomer_sale_group_obj = ICustomerSaleGroup.objects.filter(date__month=date_in_format.month,
                                                                     date__year=date_in_format.year,
                                                                     icustomer_id=request.data['icustomer_id'])

        icustomer_sale_group_list = list(icustomer_sale_group_obj.values_list('id', 'business_id', 'business__code',
                                                                              'business__business_type_id',
                                                                              'icustomer_id',
                                                                              'icustomer__customer_code',
                                                                              'date', 'session',
                                                                              'session__display_name', 'ordered_via',
                                                                              'ordered_via__name',
                                                                              'payment_status__name',
                                                                              'sale_status__name', 'total_cost',
                                                                              'total_cost_for_month',
                                                                              'time_created', 'ordered_by__first_name',
                                                                              'ordered_by_id', 'icustomersale__product_id',
                                                                              'icustomersale__count', 'icustomersale__cost'))
        icustomer_sale_group_column = ['icustomer_sale_group_id', 'business_id', 'business_code', 'business_type_id',
                                       'icustomer_id',
                                       'icustomer_code', 'date', 'session_id', 'session_name',
                                       'ordered_via_id', 'ordered_via_name', 'payment_status',
                                       'sale_status',
                                       'session_wise_price', 'total_cost_for_month', 'order_date', 'ordered_by_name',
                                       'ordered_by_id', 'product_id', 'product_count', 'cost_per_quantity']
        icustomer_sale_group_df = pd.DataFrame(icustomer_sale_group_list, columns=icustomer_sale_group_column)
        icustomer_sale_group_df['month'] = pd.DatetimeIndex(icustomer_sale_group_df['date']).month
        icustomer_sale_group_df['year'] = pd.DatetimeIndex(icustomer_sale_group_df['date']).year

        sale_json = icustomer_sale_group_df.to_dict('r')

        icustomer_sale_group_obj.delete()

        coutomer_order_delete_obj = CustomerOrderDeleteLog(customer_id=sale_json[0]['icustomer_id'],
                                                           ordered_on=sale_json[0]['order_date'],
                                                           ordered_by_id=sale_json[0]['ordered_by_id'],
                                                           deleted_on=datetime.datetime.now(),
                                                           deleted_by_id=request.user.id,
                                                           date_of_delivery=sale_json[0]['date'],
                                                           deleted_value_json=sale_json)
        coutomer_order_delete_obj.save()
        print(coutomer_order_delete_obj.deleted_value_json)

    ICustomerSerialNumberMap.objects.filter(month=date_in_format.month, year=date_in_format.year,
                                            icustomer_id=request.data['icustomer_id']).delete()


    today = datetime.datetime.now()
    from_date = today.replace(day=1)
    to_date = today.date()
    order_day_count = today.day
    cost_per_quantity = sale_json[0]['cost_per_quantity']
    total_cost = cost_per_quantity * order_day_count
    employee_order_change_obj = EmployeeOrderChangeLog(icustomer_id=sale_json[0]['icustomer_id'],
                                                        date_of_delivery=sale_json[0]['date'],
                                                        employee_order_change_mode_id=1,
                                                        total_days=order_day_count,
                                                        from_date=from_date.date(),
                                                        to_date=to_date,
                                                        modified_by=request.user,
                                                        product_id = sale_json[0]['product_id'],
                                                        count = sale_json[0]['product_count'],
                                                        cost_per_quantity = cost_per_quantity,
                                                        session_id = sale_json[0]['session_id'],
                                                        total_cost = total_cost,
                                                        modified_at=from_date,
                                                        )
    employee_order_change_obj.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def update_business_route_map(request):
    print(request.data)
    data = {}
    ordinal = RouteBusinessMap.objects.get(id=request.data['route_map_id']).ordinal
    route = RouteBusinessMap.objects.get(id=request.data['route_map_id']).route.id
    route_maps_ids = list(
        RouteBusinessMap.objects.filter(route_id=route, ordinal__gt=ordinal).values_list('id', flat=True))
    print('old_ordinal_', ordinal)
    for route_map_id in route_maps_ids:
        route_map_obj = RouteBusinessMap.objects.get(id=route_map_id)
        route_map_obj.ordinal = route_map_obj.ordinal - 1
        route_map_obj.save()
    RouteBusinessMap.objects.filter(id=request.data['route_map_id']).delete()

    route_objects = RouteBusinessMap.objects.filter(route_id=request.data['route_id'],
                                                    ordinal__gte=request.data['current_index'] + 1)
    for route_object in route_objects:
        route_object.ordinal = route_object.ordinal + 1
        route_object.save()
    old_route_name = Route.objects.get(id=route).name
    new_route_name = Route.objects.get(id=request.data['route_id'])
    busines_code = Business.objects.get(id=request.data['business_id']).code
    RouteBusinessMap.objects.create(route_id=request.data['route_id'], business_id=request.data['business_id'],
                                    ordinal=request.data['current_index'] + 1)
    business_route_change_log = BusinessRouteChangeLog(business_id=request.data['business_id'],
                                                       old_route_id=route,
                                                       new_route_id=request.data['route_id'],
                                                       description=str(busines_code) + ' Booth Moved From ' + str(
                                                           old_route_name) + ' To ' + str(new_route_name),
                                                       changed_by_id=request.user.id,
                                                       changed_at=datetime.datetime.now())
    business_route_change_log.save()
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_route_vehicle_map_log(request):
    route_vehicle_map = RouteVehicleMap.objects.all()
    route_groups = RouteGroupMap.objects.all()
    master_dict = {}
    for route_group in route_groups:
        master_dict[route_group.full_name] = {}
        master_dict[route_group.full_name]['mor_route_id'] = route_group.mor_route_id
        master_dict[route_group.full_name]['eve_route_id'] = route_group.eve_route_id
        #     morg vehicle
        if route_vehicle_map.filter(route_id=route_group.mor_route_id).exists():
            master_dict[route_group.full_name]['mor_vehicle_name'] = route_vehicle_map.get(
                route_id=route_group.mor_route_id).vehicle.licence_number
            master_dict[route_group.full_name]['mor_vehicle_id'] = route_vehicle_map.get(
                route_id=route_group.mor_route_id).vehicle.id
            master_dict[route_group.full_name]['mor_vehicle_tray_capacity'] = route_vehicle_map.get(
                route_id=route_group.mor_route_id).vehicle.tray_capacity
        else:
            master_dict[route_group.full_name]['mor_vehicle_name'] = 'N/A'
            master_dict[route_group.full_name]['mor_vehicle_id'] = 'N/A'
            master_dict[route_group.full_name]['mor_vehicle_tray_capacity'] = '-'
        #     eveg vehicle
        if route_vehicle_map.filter(route_id=route_group.eve_route_id).exists():
            master_dict[route_group.full_name]['eve_vehicle_name'] = route_vehicle_map.get(
                route_id=route_group.eve_route_id).vehicle.licence_number
            master_dict[route_group.full_name]['eve_vehicle_id'] = route_vehicle_map.get(
                route_id=route_group.eve_route_id).vehicle.id
            master_dict[route_group.full_name]['eve_vehicle_tray_capacity'] = route_vehicle_map.get(
                route_id=route_group.eve_route_id).vehicle.tray_capacity
        else:
            master_dict[route_group.full_name]['eve_vehicle_name'] = 'N/A'
            master_dict[route_group.full_name]['eve_vehicle_id'] = 'N/A'
            master_dict[route_group.full_name]['eve_vehicle_tray_capacity'] = '-'

    return Response(data=master_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_route_vehicle_change(request):
    print(request.data)
    session_id = Route.objects.get(id=request.data['route_id']).session_id
    route_name = Route.objects.get(id=request.data['route_id']).name
    data = {}
    if RouteVehicleMap.objects.filter(route_id=request.data['route_id'],
                                      vehicle_id=request.data['vehicle_id']).exists():
        data['message'] = 'route is already maped to this vehicle'
        data['status'] = 'success'

    elif RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'], route__session_id=session_id).exists():
        assigned_route_name = RouteVehicleMap.objects.get(vehicle_id=request.data['vehicle_id'],
                                                          route__session_id=session_id).route.name
        data[
            'message'] = 'Vehicle is already assigned to ' + assigned_route_name + ' route , do you want to re-assign it to ' + route_name
        data['status'] = 'confirm'
    else:
        if RouteVehicleMap.objects.filter(route_id=request.data['route_id']).exists():
            RouteVehicleMap.objects.filter(route_id=request.data['route_id']).update(
                vehicle_id=request.data['vehicle_id'])
        else:
            RouteVehicleMap.objects.create(route_id=request.data['route_id'], vehicle_id=request.data['vehicle_id'])
        data['status'] = 'success'
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_route_vehicle(request):
    session_id = Route.objects.get(id=request.data['route_id']).session_id
    route_name = Route.objects.get(id=request.data['route_id']).name
    RouteVehicleMap.objects.filter(vehicle_id=request.data['vehicle_id'], route__session_id=session_id).delete()
    if RouteVehicleMap.objects.filter(route_id=request.data['route_id']).exists():
        RouteVehicleMap.objects.filter(route_id=request.data['route_id']).update(vehicle_id=request.data['vehicle_id'])
    else:
        RouteVehicleMap.objects.create(route_id=request.data['route_id'], vehicle_id=request.data['vehicle_id'])
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def change_business_active_status(request):
    print(request.data)
    Business.objects.filter(id=request.data['business_id']).update(is_active=request.data['action'])
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_transaction_history_agent(request):
    agent_id = request.data['agent_id']
    user_id = BusinessAgentMap.objects.get(agent_id=agent_id).business.user_profile.user.id
    master_list = []
    if TransactionLog.objects.filter(transacted_by_id=user_id, transaction_direction_id=1,
                                     transaction_approval_status_id=1).exists():
        transactions = TransactionLog.objects.filter(transacted_by_id=user_id, transaction_direction_id=1,
                                                     transaction_approval_status_id=1).order_by('-time_modified')
        for transaction in transactions:
            master_dict = {}
            master_dict['old_balance'] = transaction.wallet_balance_before_this_transaction
            master_dict['amount'] = transaction.amount
            master_dict['new_balance'] = transaction.wallet_balance_after_transaction_approval
            master_dict['date'] = transaction.time_modified
            master_dict['data_entered_by'] = transaction.data_entered_by.first_name
            master_list.append(master_dict)

    return Response(master_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_route_indent_status_per_sesion(request):
    data_dict = {1: False, 2: False}
    if RouteBusinessMap.objects.filter(business__code=request.data['selected_business_code'],
                                       route__session_id=1).exists():
        mor_route_id = RouteBusinessMap.objects.get(business__code=request.data['selected_business_code'],
                                                    route__session_id=1).route_id
        if RouteTrace.objects.filter(date=request.data['selected_date'], route_id=mor_route_id).exists():
            route_indent_status_id = RouteTrace.objects.get(date=request.data['selected_date'],
                                                            route_id=mor_route_id).indent_status.id
            if route_indent_status_id == 3:
                data_dict['1'] = True
    if RouteBusinessMap.objects.filter(business__code=request.data['selected_business_code'],
                                       route__session_id=2).exists():
        eve_route_id = RouteBusinessMap.objects.get(business__code=request.data['selected_business_code'],
                                                    route__session_id=2).route_id
        if RouteTrace.objects.filter(date=request.data['selected_date'], route_id=eve_route_id).exists():
            route_indent_status_id = RouteTrace.objects.get(date=request.data['selected_date'],
                                                            route_id=eve_route_id).indent_status.id
            if route_indent_status_id == 3:
                data_dict['2'] = True
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_route_indent_status_per_sesion_for_website(request):
    data_dict = {1: False, 2: False}
    business_id = BusinessAgentMap.objects.get(business__user_profile__user=request.user).business.id
    if RouteBusinessMap.objects.filter(business_id=business_id, route__session_id=1).exists():
        mor_route_id = RouteBusinessMap.objects.get(business_id=business_id, route__session_id=1).route_id
        if RouteTrace.objects.filter(date=request.data['selected_date'], route_id=mor_route_id).exists():
            route_indent_status_id = RouteTrace.objects.get(date=request.data['selected_date'],
                                                            route_id=mor_route_id).indent_status.id
            if route_indent_status_id == 3:
                data_dict['1'] = True
    if RouteBusinessMap.objects.filter(business_id=business_id,
                                       route__session_id=2).exists():
        eve_route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                    route__session_id=2).route_id
        if RouteTrace.objects.filter(date=request.data['selected_date'], route_id=eve_route_id).exists():
            route_indent_status_id = RouteTrace.objects.get(date=request.data['selected_date'],
                                                            route_id=eve_route_id).indent_status.id
            if route_indent_status_id == 3:
                data_dict['2'] = True
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_employee_user_type(request):
    employee_type_id = Employee.objects.filter(user_profile__user=request.user)[0].role.id
    return Response(data=employee_type_id, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_booth_code_exists(request):
    print('check booth code')
    if User.objects.filter(username=request.data['business_code']).exists():
        print('exists')
        return Response(data=True, status=status.HTTP_200_OK)
    else:
        return Response(data=False, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_agent_code(request):
    print('check booth code')
    data = {}
    if Agent.objects.filter(agent_code=request.data['agent_code']).exists():
        print('exists')
        agent_id = Agent.objects.get(agent_code=request.data['agent_code']).id
        data['agent_id'] = agent_id
        data['status'] = True
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data['status'] = False
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def reprepare_indent(request):
    tomorrow_date = datetime.datetime.now().date()
    if request.data['date'] == 'tomorrow':
        tomorrow_date += datetime.timedelta(days=1)
    route_trace_obj = RouteTrace.objects.get(date=tomorrow_date, route_id=request.data['selected_route_id'])
    route_trace_obj.indent_status_id = 1
    route_trace_obj.save()
    temp_route_id = RouteTempRouteMap.objects.get(main_route_id=request.data['selected_route_id']).temp_route_id
    if RouteTrace.objects.filter(route_id=temp_route_id, date=tomorrow_date).exists():
        RouteTrace.objects.filter(route_id=temp_route_id, date=tomorrow_date).delete()
    data_dict = {}
    data_dict['temp_route_id'] = temp_route_id
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_global_config_data(request):
    global_config_obj = GlobalConfig.objects.all()
    global_config_list = list(global_config_obj.values_list('id', 'name', 'value', 'description'))
    global_config_column = ['id', 'name', 'value', 'description']
    global_config_df = pd.DataFrame(global_config_list, columns=global_config_column)
    global_config_df['value'].astype('float')
    global_config_dict = global_config_df.groupby('name').apply(lambda x: x.to_dict('r')[0]).to_dict()
    global_config_dict['mobile_number'] = UserProfile.objects.get(user_id=request.user.id).mobile
    return Response(data=global_config_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_last_month_order_count_for_counter(request):
    employee_id = Employee.objects.get(user_profile__user=request.user).id
    counter_obj = CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True)[0]
    print(counter_obj.id)
    to_date = datetime.datetime.now()
    from_date = to_date - timedelta(days=30)
    employee_trace_ids = list(
        CounterEmployeeTraceMap.objects.filter(counter_id=counter_obj.counter.id, collection_date__lte=to_date,
                                               collection_date__gte=from_date).values_list('id', flat=True))
    employee_trace_sale_group_obj = list(
        CounterEmployeeTraceSaleGroupMap.objects.filter(counter_employee_trace_id__in=employee_trace_ids).order_by(
            'sale_group').values_list(
            'sale_group', flat=True))
    sale_group_obj = SaleGroup.objects.filter(id__in=employee_trace_sale_group_obj, session_id=1).order_by('id')
    sale_group_list = list(sale_group_obj.values_list('id', 'business__code'))
    sale_group_column = ['id', 'business_code']
    sale_group_df = pd.DataFrame(sale_group_list, columns=sale_group_column)
    final_data = sale_group_df.groupby(['business_code']).agg('count').to_dict()
    return Response(data=final_data['id'], status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_employee_role_menu(request):
    data_dict = {'header': [], 'page': {}}
    print('get menu function')
    print(request.user)
    # request.user.user_profile
    employee_role = request.user.userprofile.employee.role
    print(employee_role)
    if employee_role.id == 2:
        menu_header_ids = MenuHeader.objects.filter().values_list('id', flat=True)
        menu_header_page_ids = MenuHeaderPage.objects.filter().values_list('id', flat=True)
    else:
        menu_header_ids = MenuHeaderPermission.objects.filter(employee_role=employee_role).values_list('menu_header',
                                                                                                       flat=True)
        menu_header_page_ids = MenuHeaderPagePermission.objects.filter(employee_role=employee_role).values_list(
            'menu_header_page', flat=True)
    print('one')
    header_values = MenuHeader.objects.filter(id__in=menu_header_ids).values_list('id', 'display_name', 'icon',
                                                                                  'link').order_by('ordinal')
    header_columns = ['id', 'display_name', 'icon', 'link']
    header_df = pd.DataFrame(list(header_values), columns=header_columns)
    data_dict['header'] = header_df.to_dict('r')

    page_values = MenuHeaderPage.objects.filter(id__in=menu_header_page_ids).values_list('id', 'display_name', 'icon',
                                                                                         'link', 'menu_header')
    page_columns = ['id', 'display_name', 'icon', 'link', 'header_id']
    page_df = pd.DataFrame(list(page_values), columns=page_columns)
    data_dict['page'] = page_df.groupby('header_id').apply(lambda x: x.to_dict('r')).to_dict()
    return Response(data=data_dict, status=status.HTTP_200_OK)


def create_main_icustomer_sale_from_temp_sale_icustomer_sale(payment_request_obj, decrypted_string_and_value):
    temp_sale_group_payment_request_map = ICustomerSaleGroupPaymentRequestMap.objects.get(
        payment_request_id=payment_request_obj.id)
    temp_sale_group_ids = list(
        ICustomerSaleGroupPaymentRequestMap.objects.filter(payment_request_id=payment_request_obj.id).values_list(
            'temp_sale_group', flat=True))
    if decrypted_string_and_value['STC'] == '000':
        product_dict = {}
        product_dict[1] = {}
        product_dict[2] = {}
        temp_sale_group_obj = TempICustomerSaleGroup.objects.filter(id=temp_sale_group_ids[0])[0]
        month = temp_sale_group_obj.date.month
        year = temp_sale_group_obj.date.year
        icustomer_id = temp_sale_group_obj.icustomer_id
        user_id = temp_sale_group_obj.icustomer.user_profile.user.id
        customer_wallet_obj = ICustomerWallet.objects.get(customer_id=icustomer_id)
        # check wallet used
        is_wallet_used_for_order = False
        expected_current_balance_after_order = customer_wallet_obj.current_balance - Decimal(payment_request_obj.wallet_balance_after_this_transaction)
        print(expected_current_balance_after_order)
        if expected_current_balance_after_order > 0:
            is_wallet_used_for_order = True

        date = str(temp_sale_group_obj.date)
        total_days_in_month = monthrange(year, month)[1]
        user_profile_id = ICustomer.objects.get(id=temp_sale_group_obj.icustomer.id).user_profile.id
        data_dict = serve_product__and_session_list_for_customer(user_profile_id)
        business_id = ICustomer.objects.get(id=temp_sale_group_obj.icustomer.id).business.id
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        product_in_string = ''
        for temp_sale_group_id in temp_sale_group_ids:
            # sale_group
            temp_sale_group_obj = TempICustomerSaleGroup.objects.filter(id=temp_sale_group_id).values()[0]
            temp_sale_group_obj['id'] = None
            main_sale_group_obj = ICustomerSaleGroup.objects.create(**temp_sale_group_obj)
            # sale
            temp_sale_ids = list(
                TempICustomerSale.objects.filter(temp_icustomer_sale_group_id=temp_sale_group_id).values_list('id',
                                                                                                              flat=True))
            for temp_sale_id in temp_sale_ids:
                temp_sale_obj = TempICustomerSale.objects.filter(id=temp_sale_id).values()[0]
                temp_sale_obj['id'] = None
                temp_sale_obj['icustomer_sale_group_id'] = main_sale_group_obj.id
                temp_sale_obj.pop('temp_icustomer_sale_group_id', None)
                main_sale_obj = ICustomerSale.objects.create(**temp_sale_obj)
                product_dict[main_sale_group_obj.session_id][main_sale_obj.product.id] = main_sale_obj.count
                product_in_string += str(main_sale_obj.product.short_name) + '-' + str(
                    main_sale_obj.count) + 'pkt' + '-' + str(main_sale_group_obj.session.display_name) + ','

            # adding sale to online counter
            employee_id = 3
            if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                      collection_date=datetime.datetime.now()).exists():
                counter_employee_trace_obj = \
                CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                       collection_date=datetime.datetime.now())[0]
            else:
                counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=24, employee_id=employee_id,
                                                                     collection_date=datetime.datetime.now(),
                                                                     start_date_time=datetime.datetime.now())
                counter_employee_trace_obj.save()
            if CounterEmployeeTraceSaleGroupMap.objects.filter(
                    counter_employee_trace_id=counter_employee_trace_obj.id).exists():
                counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                    counter_employee_trace_id=counter_employee_trace_obj.id)
                counter_sale_group_obj.icustomer_sale_group.add(main_sale_group_obj.id)
                counter_sale_group_obj.save()
            else:
                counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap(
                    counter_employee_trace_id=counter_employee_trace_obj.id)
                counter_sale_group_obj.save()
                counter_sale_group_obj.icustomer_sale_group.add(main_sale_group_obj.id)
                counter_sale_group_obj.save()
            # generate milkcard number
            if ICustomerMonthlyOrderTransaction.objects.filter(icustomer_id=main_sale_group_obj.icustomer_id,
                                                               month=main_sale_group_obj.date.month,
                                                               year=main_sale_group_obj.date.year).exists():
                icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction.objects.get(
                    icustomer_id=main_sale_group_obj.icustomer_id, month=main_sale_group_obj.date.month,
                    year=main_sale_group_obj.date.year)
                is_date_available = True
            else:
                icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction(
                    icustomer_id=main_sale_group_obj.icustomer_id, month=main_sale_group_obj.date.month,
                    year=main_sale_group_obj.date.year, transacted_date_time=datetime.datetime.now(), total_cost=0,
                    created_by_id=main_sale_group_obj.ordered_by.id, milk_card_number=0)
                icustomer_monthly_order_obj.save()
                is_date_available = False

            icustomer_monthly_order_obj.total_cost += main_sale_group_obj.total_cost_for_month
            icustomer_monthly_order_obj.icustomer_sale_group.add(main_sale_group_obj.id)
            icustomer_milk_card_id_bank_obj = ICustomerMilkCarkNumberIdBank.objects.get(id=1)
            if is_date_available:
                last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number
            else:
                last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number + 1
            icustomer_monthly_order_obj.milk_card_number = str(last_count).zfill(6)
            icustomer_monthly_order_obj.save()
            # update_last_count_in_id_bank
            icustomer_milk_card_id_bank_obj.last_milk_card_number = last_count
            icustomer_milk_card_id_bank_obj.save()
            temp_sale_group_payment_request_map.sale_group.add(main_sale_group_obj.id)

            if is_wallet_used_for_order:
                if ICustomerWalletAmoutForOrder.objects.filter(icustomer_id=icustomer_id, month=main_sale_group_obj.date.month, year=main_sale_group_obj.date.year).exists():
                    icustomer_waller_amount_for_order_obj = ICustomerWalletAmoutForOrder.objects.get(icustomer_id=icustomer_id, month=main_sale_group_obj.date.month, year=main_sale_group_obj.date.year)
                else:
                    icustomer_waller_amount_for_order_obj = ICustomerWalletAmoutForOrder(icustomer_id=icustomer_id, month=main_sale_group_obj.date.month, year=main_sale_group_obj.date.year, wallet_amount=0)
                    icustomer_waller_amount_for_order_obj.save()

                icustomer_waller_amount_for_order_obj.icustomer_sale_group.add(main_sale_group_obj.id)
                icustomer_waller_amount_for_order_obj.save()
        if is_wallet_used_for_order:
            icustomer_waller_amount_for_order_obj.wallet_amount = expected_current_balance_after_order
            icustomer_waller_amount_for_order_obj.save()
        else:
            if ICustomerWalletAmoutForOrder.objects.filter(icustomer_id=icustomer_id,month=main_sale_group_obj.date.month,year=main_sale_group_obj.date.year).exists(): 
                ICustomerWalletAmoutForOrder.objects.get(icustomer_id=icustomer_id,month=main_sale_group_obj.date.month,year=main_sale_group_obj.date.year).delete()

        for date_count in range(1, int(total_days_in_month) + 1):
            date = date[:7] + '-' + str(date_count)
            for session in session_list:
                route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                        route__session_id=session['id']).route_id
                vehicle_obj = RouteVehicleMap.objects.get(route_id=route_id).vehicle
                for product in product_list:
                    if product['product_id'] in product_dict[session['id']].keys():
                        if RouteTrace.objects.filter(date=date, session_id=session['id'], route_id=route_id).exists():
                            print(date)
                            route_trace_obj = RouteTrace.objects.get(date=date, session_id=session['id'],
                                                                     route_id=route_id)
                            if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id,
                                                                        product_id=product['product_id']).exists():
                                route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(
                                    route_trace_id=route_trace_obj.id, product_id=product['product_id'])
                                route_trace_sale_summary_obj.quantity += Decimal(
                                    product_dict[session['id']][product['product_id']])
                                route_trace_sale_summary_obj.save()
                            else:
                                route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(
                                    route_trace_id=route_trace_obj.id,
                                    product_id=product['product_id'],
                                    quantity=product_dict[session['id']][product['product_id']])
                                route_trace_sale_summary_obj.save()
                        else:
                            route_trace_obj = RouteTrace(indent_status_id=1,  # initiated
                                                         route_id=route_id,
                                                         vehicle_id=vehicle_obj.id,
                                                         date=date,
                                                         session_id=session['id'],
                                                         driver_name=vehicle_obj.driver_name,
                                                         driver_phone=vehicle_obj.driver_mobile)
                            route_trace_obj.save()
                            route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id,
                                                                                     product_id=product['product_id'],
                                                                                     quantity=
                                                                                     product_dict[session['id']][
                                                                                         product['product_id']])
                            route_trace_sale_summary_obj.save()
        temp_sale_group_payment_request_map.save()
        icustomer_obj = ICustomer.objects.get(id=main_sale_group_obj.icustomer_id)
        customer_first_name = icustomer_obj.user_profile.user.first_name
        current_date_time = datetime.datetime.now().astimezone(indian).strftime("%Y-%m-%d %I:%M:%p")
        counter_name = 'Online'
        amount = Decimal(decrypted_string_and_value['AMT']) + (
                    customer_wallet_obj.current_balance - payment_request_obj.wallet_balance_after_this_transaction)
        milk_card_number = icustomer_monthly_order_obj.milk_card_number
        customer_code = icustomer_obj.customer_code
        business_code = Business.objects.get(id=business_id).code
        message = str(customer_first_name) + '(' + str(customer_code) + ')' + ' subscribed milk for ' + str(
            months_in_english[month]) + '.Booth- ' + str(business_code) + ' Card No :' + str(
            milk_card_number) + ' Rs. ' + str(amount) + ' ' + str(product_in_string)

        # message = 'Dear ' + str(customer_first_name) + '(' + str(customer_code)+ ')' + ', you have successfully subscribed milk for the month of  ' +str(months_in_english[main_sale_group_obj.date.month]) + ' Milk Card No : ' + str(milk_card_number) + ' Booked on ' + str(current_date_time) + ' @ ' + str(counter_name) + ' counter totalling ' + str(amount) + ' Rs. Items:' + str(product_in_string)
        purpose = 'Confirmation message to customer'
        payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey': '622de6e4-91da-4e3b-9fb1-2262df7baff8',
                   'SenderID': 'AAVINC', 'fl': '0', 'gwid': '2', 'sid': 'AAVINC'}
        headers = {}
        url = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'
        payload['msg'] = message
        payload['msisdn'] = icustomer_obj.user_profile.mobile
        if not str(icustomer_obj.user_profile.mobile)[0:5] == '99999':
            res = requests.post(url, data=payload, headers=headers)
        if ICustomerCardSerialNumberIdBank.objects.filter(business_id=business_id, month=month, year=year).exists():
            icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank.objects.get(business_id=business_id,
                                                                                       month=month, year=year)
        else:
            icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank(business_id=business_id, month=month,
                                                                           year=year, counter_last_count=0,
                                                                           online_last_count=0)
            icustomer_serial_bank_id_obj.save()

        icustomer_serial_number_map = ICustomerSerialNumberMap(icustomer_id=icustomer_id, business_id=business_id,
                                                               month=month, year=year)
        serial_number = icustomer_serial_bank_id_obj.counter_last_count + 1
        icustomer_serial_number_map.serial_number = serial_number
        icustomer_serial_number_map.save()
        # update serail number in ID bank
        icustomer_serial_bank_id_obj.counter_last_count = serial_number
        icustomer_serial_bank_id_obj.online_last_count = serial_number
        icustomer_serial_bank_id_obj.save()
        # update transactino log status
        if payment_request_obj.is_wallet_selected:
            if payment_request_obj.wallet_balance_after_this_transaction < customer_wallet_obj.current_balance:
                transaction_obj = TransactionLog(
                    date=datetime.datetime.now(),
                    transacted_by_id=user_id,
                    transacted_via_id=1,
                    data_entered_by_id=user_id,
                    amount=customer_wallet_obj.current_balance - Decimal(
                        payment_request_obj.wallet_balance_after_this_transaction),
                    transaction_direction_id=5,  # from customer wallet to aavin
                    transaction_mode_id=1,  # Upi
                    transaction_status_id=2,  # completed
                    transaction_id=decrypted_string_and_value['RID'],
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=datetime.datetime.now(),
                    wallet_balance_before_this_transaction=customer_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=payment_request_obj.wallet_balance_after_this_transaction,
                    description='Amount for ordering the product from customer wallet',
                    modified_by_id=user_id
                )
                transaction_obj.save()
                customer_wallet_obj.current_balance = payment_request_obj.wallet_balance_after_this_transaction
                customer_wallet_obj.save()
        try:
            transaction_log_obj = TransactionLog.objects.get(transaction_id=decrypted_string_and_value['RID'])
            transaction_log_obj.transaction_status_id = 2
            transaction_log_obj.save()
        except Exception as e:
            print(e)


def create_main_by_sale_from_temp_by_sale(payment_request_obj, decrypted_string_and_value):
    temp_by_sale_group_payment_request_map = BySaleGroupPaymentRequestMap.objects.get(
        payment_request_id=payment_request_obj.id)
    temp_by_sale_group_ids = list(
        BySaleGroupPaymentRequestMap.objects.filter(payment_request_id=payment_request_obj.id).values_list(
            'temp_sale_group', flat=True))
    temp_sale_obj = TempBySale.objects.filter(temp_by_sale_group_id__in=temp_by_sale_group_ids)
    temp_sale_list = list(temp_sale_obj.values_list('id', 'by_product_id', 'count'))
    temp_sale_column = ['id', 'product_id', 'count']
    temp_sale_df = pd.DataFrame(temp_sale_list, columns=temp_sale_column)
    request_product_list = temp_sale_df.to_dict('r')
    print(decrypted_string_and_value['STC'])
    if decrypted_string_and_value['STC'] == '000':
        first_temp_sale_obj = TempBySaleGroup.objects.get(id=temp_by_sale_group_ids[0])
        business_id = first_temp_sale_obj.business.id
        business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
        business_type_id = business_agent_obj.business.business_type.id
        user_profile_id = business_agent_obj.business.user_profile_id
        agent_id = business_agent_obj.agent_id
        agent_user_id = business_agent_obj.business.user_profile.user.id
        data_dict = serve_by_product_price_dict(user_profile_id)
        product_price_dict = data_dict['product_price_dict']
        order_category_dict = data_dict['order_category']
        agent_wallet_obj = ByProductAgentWallet.objects.get(agent_id=agent_id)
        order_code = generate_by_product_order_code()
        payment_request_obj = PaymentRequest.objects.get(id=payment_request_obj.id)
        is_order_placed = False
        total_cost = 0
        un_ordered_product_cost = 0
        by_sale_group_obj = BySaleGroup(
                business_id=business_id,
                order_code=order_code,
                zone_id=business_agent_obj.business.zone.id,
                ordered_date=datetime.datetime.now(),
                ordered_via_id=first_temp_sale_obj.ordered_via_id,
                total_cost=0,
                sale_status_id=1, #ordered
                ordered_by_id=agent_user_id,
                modified_by_id=agent_user_id,
                payment_status_id=1
            )
        by_sale_group_obj.save()
        super_by_sale_group_obj = BySaleGroupTransactionTrace(
            by_sale_group_id=by_sale_group_obj.id,
            sale_group_order_type_id=1,
        )
        super_by_sale_group_obj.save()

        for product in request_product_list:
            current_product_availablity = ByProductCurrentAvailablity.objects.get(by_product_id=product['product_id'])
            product_price = Decimal(product['count']) * (product_price_dict[product['product_id']]['price'])
            if product['count'] <= current_product_availablity.quantity_now:
                by_sale_obj = BySale(
                    by_sale_group_id=by_sale_group_obj.id,
                    by_product_id=product['product_id'],
                    count=product['count'],
                    cost=product_price,
                    ordered_by_id=agent_user_id,
                    modified_by_id=agent_user_id,
                )
                by_sale_obj.save()
                current_product_availablity.quantity_now = current_product_availablity.quantity_now - Decimal(product['count'])
                current_product_availablity.quantity_now_time = datetime.datetime.now()
                current_product_availablity.save()
                total_cost += product_price
                is_order_placed = True
            else:
                un_ordered_product_cost += product_price
        saved_by_sale_group_obj = BySaleGroup.objects.get(id=by_sale_group_obj.id)
        saved_by_sale_group_obj.total_cost = total_cost
        saved_by_sale_group_obj.save()
        if is_order_placed:
            by_sale_obj = BySale.objects.filter(by_sale_group_id=by_sale_group_obj.id)
            by_sale_list = list(by_sale_obj.values_list('id', 'by_product_id', 'count'))
            by_sale_column = ['id', 'product_id', 'count']
            by_sale_df = pd.DataFrame(by_sale_list, columns=by_sale_column)
            if not by_sale_df is None:
                if not super_by_sale_group_obj is None:
                    super_by_sale_group_obj.order_sale_group_json = by_sale_df.to_dict('r')
                    super_by_sale_group_obj.counter_id = 1
                    super_by_sale_group_obj.save()

        temp_by_sale_group_payment_request_map.by_sale_group.add(saved_by_sale_group_obj.id)
        employee_id = 3
        counter_id = 23
        if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                    collection_date=datetime.datetime.now()).exists():
            counter_employee_trace_obj = CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                        collection_date=datetime.datetime.now())[0]
        else:
            counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=23,
                                                                    employee_id=employee_id,
                                                                    collection_date=datetime.datetime.now(),
                                                                    start_date_time=datetime.datetime.now())
            counter_employee_trace_obj.save()
        if CounterEmployeeTraceBySaleGroupMap.objects.filter(
                counter_employee_trace_id=counter_employee_trace_obj.id).exists():
            counter_sale_group_obj = CounterEmployeeTraceBySaleGroupMap.objects.get(
                counter_employee_trace_id=counter_employee_trace_obj.id)
            counter_sale_group_obj.by_sale_group.add(saved_by_sale_group_obj.id)
            counter_sale_group_obj.save()
            print('counter sale updated')
        else:
            counter_sale_group_obj = CounterEmployeeTraceBySaleGroupMap(
                counter_employee_trace_id=counter_employee_trace_obj.id)
            counter_sale_group_obj.save()
            counter_sale_group_obj.by_sale_group.add(saved_by_sale_group_obj.id)
            counter_sale_group_obj.save()
            print('counter sale created')
        
        if payment_request_obj.is_wallet_selected:
            if payment_request_obj.wallet_balance_after_this_transaction < agent_wallet_obj.current_balance:
                transaction_obj = ByProductTransactionLog(
                    date=datetime.datetime.now(),
                    transacted_by_id=agent_user_id,
                    transacted_via_id=first_temp_sale_obj.ordered_via_id,
                    data_entered_by_id=agent_user_id,
                    amount=agent_wallet_obj.current_balance - Decimal(
                        payment_request_obj.wallet_balance_after_this_transaction),
                    transaction_direction_id=2,  # from agent wallet to aavin
                    transaction_mode_id=1,  # Upi
                    transaction_status_id=2,  # completed
                    transaction_id=decrypted_string_and_value['RID'],
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=datetime.datetime.now(),
                    wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=payment_request_obj.wallet_balance_after_this_transaction,
                    description='Amount for ordering the product from agent wallet',
                    modified_by_id=agent_user_id
                )
                transaction_obj.save()
                agent_wallet_obj.current_balance = payment_request_obj.wallet_balance_after_this_transaction
                agent_wallet_obj.save()
                if not super_by_sale_group_obj is None:
                    super_by_sale_group_obj.is_wallet_used = True
                    super_by_sale_group_obj.wallet_amount = transaction_obj.amount
                    super_by_sale_group_obj.wallet_transaction_id = transaction_obj.id
                    super_by_sale_group_obj.save()
        temp_by_sale_group_payment_request_map.save()
        if un_ordered_product_cost != 0:
            agent_wallet_obj.current_balance = agent_wallet_obj.current_balance + un_ordered_product_cost
            agent_wallet_obj.save()
            transaction_obj = ByProductTransactionLog(
                date=datetime.datetime.now(),
                transacted_by_id=agent_user_id,
                transacted_via_id=first_temp_sale_obj.ordered_via_id,
                data_entered_by_id=agent_user_id,
                amount=un_ordered_product_cost,
                transaction_direction_id=3,  # from aavin to  agent wallet
                transaction_mode_id=1,  # Upi
                transaction_status_id=2,  # completed
                transaction_id=decrypted_string_and_value['RID'],
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                description='Amount for ordering the product from agent wallet',
                modified_by_id=agent_user_id
            )
            transaction_obj.save()
            if not super_by_sale_group_obj is None:
                super_by_sale_group_obj.is_wallet_used = True
                super_by_sale_group_obj.wallet_return_amount = -transaction_obj.amount
                super_by_sale_group_obj.wallet_return_transaction_id = transaction_obj.id
                super_by_sale_group_obj.save()
            message = 'The money ' + str(un_ordered_product_cost) +' has been deposited to your wallet. Sorry for the inconvenience.'
            purpose = 'Inform About un ordered Data'
            phone = Agent.objects.get(id=agent_id).agent_profile.mobile


            send_message_via_netfision(purpose, phone, message)
        # update transactino log status
        try:
            transaction_log_obj = ByProductTransactionLog.objects.filter(transaction_id=decrypted_string_and_value['RID'], transaction_direction_id=1)[0]
            transaction_log_obj.transaction_status_id = 2
            transaction_log_obj.save()
            if not super_by_sale_group_obj is None:
                super_by_sale_group_obj.transacted_amount = transaction_log_obj.amount
                super_by_sale_group_obj.bank_transaction_id = transaction_obj.id
                super_by_sale_group_obj.save()
        except Exception as e:
            print(e)
        

def create_main_sale_from_temp_sale(payment_request_obj, decrypted_string_and_value):
    temp_sale_group_payment_request_map = SaleGroupPaymentRequestMap.objects.get(
        payment_request_id=payment_request_obj.id)
    temp_sale_group_ids = list(
        SaleGroupPaymentRequestMap.objects.filter(payment_request_id=payment_request_obj.id).values_list(
            'temp_sale_group', flat=True))
    if decrypted_string_and_value['STC'] == '000':
        business_id = TempSaleGroup.objects.get(id=temp_sale_group_ids[0]).business_id
        date = TempSaleGroup.objects.get(id=temp_sale_group_ids[0]).date
        business_obj = BusinessAgentMap.objects.get(business_id=business_id).business
        agent_obj = BusinessAgentMap.objects.get(business_id=business_id).agent
        agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_obj.id)
        sale_group_ids = {
            1: None,
            2: None
        }
        if SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date).exists():
            super_sale_group_obj = SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date)[0]
        else:
            super_sale_group_obj = SuperSaleGroup(business_id=business_id, delivery_date=date)
        for temp_sale_group_id in temp_sale_group_ids:
            # sale_group
            temp_sale_group_obj = TempSaleGroup.objects.filter(id=temp_sale_group_id).values()[0]
            temp_sale_group_obj['id'] = None
            main_sale_group_obj = SaleGroup.objects.create(**temp_sale_group_obj)
            sale_group_ids[main_sale_group_obj.session_id] = main_sale_group_obj.id
            vehicle_obj = RouteVehicleMap.objects.get(route_id=main_sale_group_obj.route.id).vehicle
            # sale
            temp_sale_ids = list(
                TempSale.objects.filter(temp_sale_group_id=temp_sale_group_id).values_list('id', flat=True))
            for temp_sale_id in temp_sale_ids:
                temp_sale_obj = TempSale.objects.filter(id=temp_sale_id).values()[0]
                temp_sale_obj['id'] = None
                temp_sale_obj['sale_group_id'] = main_sale_group_obj.id
                temp_sale_obj.pop('temp_sale_group_id', None)
                main_sale_obj = Sale.objects.create(**temp_sale_obj)
                try:
                    if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=main_sale_group_obj.businesss.business_type_id, main_product_id=main_sale_obj.product_id, is_free=True).exists():
                        if FreeProductProperty.objects.filter(main_product_id=main_sale_obj.product_id, is_active=True).exists():
                            free_product_property_obj = FreeProductProperty.objects.get(main_product_id=main_sale_obj.product_id, is_active=True)
                            eligible_product_count = free_product_property_obj.eligible_product_count
                            defalut_free_product_count = free_product_property_obj.product_count
                            if main_sale_obj.count >= eligible_product_count:
                                box_count = math.floor(main_sale_obj.count/eligible_product_count)
                                free_product_count = box_count*defalut_free_product_count
                                sale_obj = Sale(
                                    sale_group_id=main_sale_group_obj.id,
                                    product_id=free_product_property_obj.free_product.id,
                                    count=free_product_count,
                                    cost=0,
                                    ordered_by_id=1,
                                    modified_by_id=1
                                )
                                sale_obj.save()
                except Exception as e:
                    print(e)


                # add sale to route trace
                if RouteTrace.objects.filter(date=main_sale_group_obj.date, session_id=main_sale_group_obj.session_id,
                                             route_id=main_sale_group_obj.route.id).exists():
                    route_trace_obj = RouteTrace.objects.get(date=main_sale_group_obj.date,
                                                             session_id=main_sale_group_obj.session_id,
                                                             route_id=main_sale_group_obj.route.id)
                    if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id,
                                                                product_id=main_sale_obj.product.id).exists():
                        route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(
                            route_trace_id=route_trace_obj.id, product_id=main_sale_obj.product.id)
                        route_trace_sale_summary_obj.quantity += Decimal(main_sale_obj.count)
                        route_trace_sale_summary_obj.save()
                    else:
                        route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id,
                                                                                 product_id=main_sale_obj.product.id,
                                                                                 quantity=main_sale_obj.count)
                        route_trace_sale_summary_obj.save()
                else:
                    route_trace_obj = RouteTrace(indent_status_id=1,  # initiated
                                                 route_id=main_sale_group_obj.route.id,
                                                 vehicle_id=vehicle_obj.id,
                                                 date=main_sale_group_obj.date,
                                                 session_id=main_sale_group_obj.session_id,
                                                 driver_name=vehicle_obj.driver_name,
                                                 driver_phone=vehicle_obj.driver_mobile)
                    route_trace_obj.save()
                    route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id,
                                                                             product_id=main_sale_obj.product.id,
                                                                             quantity=main_sale_obj.count)
                    route_trace_sale_summary_obj.save()

            temp_sale_group_payment_request_map.sale_group.add(main_sale_group_obj.id)
            if super_sale_group_obj is not None:
                super_sale_group_obj.mor_sale_group_id = sale_group_ids[1]
                super_sale_group_obj.eve_sale_group_id = sale_group_ids[2]
                super_sale_group_obj.save()
            #   add sale to online counter
            employee_id = 3
            if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                      collection_date=datetime.datetime.now()).exists():
                counter_employee_trace_obj = \
                CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                       collection_date=datetime.datetime.now())[0]
            else:
                counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=23, employee_id=employee_id,
                                                                     collection_date=datetime.datetime.now(),
                                                                     start_date_time=datetime.datetime.now())
                counter_employee_trace_obj.save()
            if CounterEmployeeTraceSaleGroupMap.objects.filter(
                    counter_employee_trace_id=counter_employee_trace_obj.id).exists():
                counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                    counter_employee_trace_id=counter_employee_trace_obj.id)
                counter_sale_group_obj.sale_group.add(main_sale_group_obj.id)
                counter_sale_group_obj.save()
            else:
                counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap(
                    counter_employee_trace_id=counter_employee_trace_obj.id)
                counter_sale_group_obj.save()
                counter_sale_group_obj.sale_group.add(main_sale_group_obj.id)
                counter_sale_group_obj.save()
        sale_df = None
        if SaleGroup.objects.filter(business_id=business_id, date=date).exists():
            sale_group_ids = list(
                SaleGroup.objects.filter(business_id=business_id, date=date).values_list('id', flat=True))
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
        if not super_sale_group_obj is None:
            sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=date,
                                                                     super_sale_group_id=super_sale_group_obj.id,
                                                                     sale_group_order_type_id=1,  # new Order
                                                                     transacted_amount=decrypted_string_and_value[
                                                                         'AMT'],
                                                                     counter_id=23)
            if not sale_df is None:
                sale_group_transaction_trace.order_sale_group_json = sale_df.to_dict('r')
            sale_group_transaction_trace.save()
        payment_request_obj = PaymentRequest.objects.get(id=payment_request_obj.id)
        if payment_request_obj.is_wallet_selected:
            if payment_request_obj.wallet_balance_after_this_transaction < agent_wallet_obj.current_balance:
                transaction_obj = TransactionLog(
                    date=datetime.datetime.now(),
                    transacted_by_id=business_obj.user_profile.user.id,
                    transacted_via_id=1,
                    data_entered_by_id=business_obj.user_profile.user.id,
                    amount=agent_wallet_obj.current_balance - Decimal(
                        payment_request_obj.wallet_balance_after_this_transaction),
                    transaction_direction_id=2,  # from agent wallet to aavin
                    transaction_mode_id=1,  # Upi
                    transaction_status_id=2,  # completed
                    transaction_id=decrypted_string_and_value['RID'],
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=datetime.datetime.now(),
                    wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=payment_request_obj.wallet_balance_after_this_transaction,
                    description='Amount for ordering the product from agent wallet',
                    modified_by_id=business_obj.user_profile.user.id
                )
                transaction_obj.save()
                agent_wallet_obj.current_balance = payment_request_obj.wallet_balance_after_this_transaction
                agent_wallet_obj.save()
                sale_group_transaction_trace.is_wallet_used = True
                sale_group_transaction_trace.wallet_amount = transaction_obj.amount
                sale_group_transaction_trace.wallet_transaction_id = transaction_obj.id
                sale_group_transaction_trace.save()
        temp_sale_group_payment_request_map.save()
        try:
            sale_group_obj = SaleGroup.objects.filter(business_id=business_id, date=date)
            sale_group_ids = list(sale_group_obj.values_list('id', flat=True))
            sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids, product__is_active=True)
            sale_list = list(sale_obj.values_list('id', 'sale_group__session',
                                                  'product__short_name', 'count', ))
            sale_column = ['sale_id', 'session_name', 'product_name', 'quantity', ]
            sale_df = pd.DataFrame(sale_list, columns=sale_column)
            product_message = ''
            product_list = sale_df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
            for product in product_list:
                temp_dict = product_list[product]
                morning_order = 0
                eve_order = 0
                for order in temp_dict:
                    if order['session_name'] == 1:
                        morning_order = order['quantity']
                    elif order['session_name'] == 2:
                        eve_order = order['quantity']
                product_message = product_message + product + ':' + str(int(morning_order)) + '+' + str(
                    int(eve_order)) + '; '
            booth_number = Business.objects.get(id=business_id).code
            date_in_format = datetime.datetime.strptime(str(date), '%Y-%m-%d')
            date = datetime.datetime.strftime(date_in_format, '%d-%m-%y')
            counter_name = 'Online'
            amount = sale_group_obj.aggregate(Sum('total_cost'))['total_cost__sum']
            message = 'Booth#{}. for {}. @{}. Rs. {}. {}'.format(booth_number, date, counter_name, amount,
                                                              product_message)
            purpose = 'New Order Confirmation Message'
            phone = agent_obj.agent_profile.mobile
            send_message_via_netfision(purpose, phone, message)
            print('message sent')
        except Exception as e:
            print(e)
        # update transactino log status
        try:
            transaction_log_obj = TransactionLog.objects.filter(transaction_id=decrypted_string_and_value['RID'])[0]
            transaction_log_obj.transaction_status_id = 2
            transaction_log_obj.save()
            sale_group_transaction_trace.bank_transaction_id = transaction_log_obj.id
            sale_group_transaction_trace.save()
        except Exception as e:
            print(e)


def update_main_sale_from_temp_sale_edit(payment_request_obj, decrypted_string_and_value):
    temp_sale_group_payment_request_map = SaleGroupEditPaymentRequestMap.objects.get(
        payment_request_id=payment_request_obj.id)
    temp_sale_group_ids = list(
        SaleGroupEditPaymentRequestMap.objects.filter(payment_request_id=payment_request_obj.id).values_list(
            'temp_sale_group_for_edit', flat=True))
    if decrypted_string_and_value['STC'] == '000':
        business_id = TempSaleGroupForEdit.objects.get(id=temp_sale_group_ids[0]).business_id
        date = TempSaleGroupForEdit.objects.get(id=temp_sale_group_ids[0]).date
        sale_group_ids = {
            1: None,
            2: None
        }
        if SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date).exists():
            super_sale_group_obj = SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date)[0]
        else:
            super_sale_group_obj = None
        business_obj = BusinessAgentMap.objects.get(business_id=business_id).business
        agent_obj = BusinessAgentMap.objects.get(business_id=business_id).agent
        agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_obj.id)
        sale_obj = TempSaleForEdit.objects.filter(temp_sale_group_for_edit_id__in=temp_sale_group_ids)
        sale_list = list(sale_obj.values_list('main_sale', 'id', 'temp_sale_group_for_edit__main_sale_group_id',
                                              'temp_sale_group_for_edit', 'temp_sale_group_for_edit__business_id',
                                              'temp_sale_group_for_edit__date', 'temp_sale_group_for_edit__session',
                                              'temp_sale_group_for_edit__session__display_name',
                                              'temp_sale_group_for_edit__ordered_via',
                                              'temp_sale_group_for_edit__ordered_via__name',
                                              'temp_sale_group_for_edit__payment_status__name',
                                              'temp_sale_group_for_edit__sale_status__name',
                                              'temp_sale_group_for_edit__total_cost', 'product', 'product__quantity',
                                              'product__name', 'count', 'cost',
                                              'temp_sale_group_for_edit__time_created',
                                              'temp_sale_group_for_edit__time_modified',
                                              'temp_sale_group_for_edit__ordered_by__first_name',
                                              'temp_sale_group_for_edit__modified_by__first_name'))
        sale_column = ['sale_id', 'temp_sale_id', 'sale_group_id', 'temp_sale_group_id', 'business_id', 'date',
                       'session_id', 'session_name', 'ordered_via_id', 'ordered_via_name', 'payment_status',
                       'sale_status',
                       'session_wise_price', 'product_id', 'product_quantity', 'product_name', 'quantity',
                       'product_cost', 'time_created', 'time_modified', 'ordered_by', 'modified_by']
        sale_df = pd.DataFrame(sale_list, columns=sale_column)
        sale_df['date'] = sale_df['date'].astype(str)
        sale_df = sale_df.fillna(0)
        master_dict = {}
        master_dict['session'] = {}
        master_dict['total_price_per_date'] = 0
        master_dict['total_price_per_product'] = {}
        master_dict['total_price_per_session'] = {}
        for row_index, row in sale_df.iterrows():
            if not row['session_id'] in master_dict['session']:
                master_dict['session'][row['session_id']] = {}
                master_dict['session'][row['session_id']]['product'] = {}
                master_dict['session'][row['session_id']]['sale_group_id'] = row['sale_group_id']
                master_dict['session'][row['session_id']]['temp_sale_group_id'] = row['temp_sale_group_id']
            if not row['product_id'] in master_dict['session'][row['session_id']]['product']:
                master_dict['session'][row['session_id']]['product'][row['product_id']] = {
                    'quantity': row['quantity'],
                    'price': row['product_cost'],
                    'sale_id': row['sale_id'],
                    'temp_sale_id': row['temp_sale_id']
                }
            if not row['product_id'] in master_dict['total_price_per_product']:
                master_dict['total_price_per_product'][row['product_id']] = 0
            if not row['session_id'] in master_dict['total_price_per_session']:
                master_dict['total_price_per_session'][row['session_id']] = 0
            master_dict['total_price_per_session'][row['session_id']] += row['product_cost']
            master_dict['total_price_per_product'][row['product_id']] += row['product_cost']
            master_dict['total_price_per_date'] += row['product_cost']
        business_id = TempSaleGroupForEdit.objects.get(id=temp_sale_group_ids[0]).business.id
        user_profile_id = BusinessAgentMap.objects.get(business_id=business_id).business.user_profile.id
        data_dict = serve_product_and_session_list(user_profile_id)
        data = master_dict
        for session in Session.objects.filter():
            if session.id in data['session'].keys():
                if not data['session'][session.id]['sale_group_id'] == 0:
                    if SaleGroup.objects.filter(id=data['session'][session.id]['sale_group_id']).exists():
                        main_sale_group_obj = SaleGroup.objects.get(id=data['session'][session.id]['sale_group_id'])
                        temp_sale_group_obj = TempSaleGroupForEdit.objects.get(
                            id=data['session'][session.id]['temp_sale_group_id'])
                        if temp_sale_group_obj.total_cost == 0:
                            main_sale_group_obj.delete()
                        else:
                            main_sale_group_obj.total_cost = temp_sale_group_obj.total_cost
                            main_sale_group_obj.product_amount = temp_sale_group_obj.product_amount
                            main_sale_group_obj.save()
                        sale_group_ids[session.id] = main_sale_group_obj.id
                else:
                    temp_sale_group_obj = \
                    TempSaleGroupForEdit.objects.filter(id=data['session'][session.id]['temp_sale_group_id']).values()[
                        0]
                    temp_sale_group_obj['id'] = None
                    temp_sale_group_obj.pop('main_sale_group_id', None)
                    if not temp_sale_group_obj['total_cost'] == 0:
                        main_sale_group_obj = SaleGroup.objects.create(**temp_sale_group_obj)
                        sale_group_ids[session.id] = main_sale_group_obj.id

                for product in data_dict['product_list']:
                    if product['product_id'] in data['session'][session.id]['product']:
                        if not data['session'][session.id]['product'][product['product_id']]['sale_id'] == 0:
                            if Sale.objects.filter(id=data['session'][session.id]['product'][product['product_id']][
                                'sale_id']).exists():
                                main_sale_obj = Sale.objects.get(
                                    id=data['session'][session.id]['product'][product['product_id']]['sale_id'])
                                temp_sale_obj = TempSaleForEdit.objects.get(
                                    id=data['session'][session.id]['product'][product['product_id']]['temp_sale_id'])
                                main_sale_obj.count = temp_sale_obj.count
                                main_sale_obj.cost = temp_sale_obj.cost
                                main_sale_obj.save()
                                if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_obj.business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                    if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                        free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                        eligible_product_count = free_product_property_obj.eligible_product_count
                                        defalut_free_product_count = free_product_property_obj.product_count
                                        if temp_sale_obj.count >= eligible_product_count:
                                            box_count = math.floor(temp_sale_obj.count/eligible_product_count)
                                            free_product_count = box_count*defalut_free_product_count
                                            if Sale.objects.filter(sale_group_id=main_sale_group_obj.id, product_id=free_product_property_obj.free_product.id).exists():
                                                free_product_sale_obj = Sale.objects.get(sale_group_id=main_sale_group_obj.id, product_id=free_product_property_obj.free_product.id)
                                                free_product_sale_obj.count = free_product_count
                                                free_product_sale_obj.save()
                                            else:
                                                sale_obj = Sale(
                                                    sale_group_id=main_sale_group_obj.id,
                                                    product_id=free_product_property_obj.free_product.id,
                                                    count=free_product_count,
                                                    cost=0,
                                                    ordered_by_id=1,
                                                    modified_by_id=1
                                                )
                                                sale_obj.save()
                                        else:
                                            if Sale.objects.filter(sale_group_id=main_sale_group_obj.id, product_id=free_product_property_obj.free_product.id).exists():
                                                Sale.objects.filter(sale_group_id=main_sale_group_obj.id, product_id=free_product_property_obj.free_product.id).delete()

                        else:
                            temp_sale_obj = TempSaleForEdit.objects.filter(
                                id=data['session'][session.id]['product'][product['product_id']][
                                    'temp_sale_id']).values()[0]
                            temp_sale_obj['id'] = None
                            temp_sale_obj['sale_group_id'] = main_sale_group_obj.id
                            temp_sale_obj.pop('main_sale_id', None)
                            temp_sale_obj.pop('temp_sale_group_for_edit_id', None)
                            main_sale_obj = Sale.objects.create(**temp_sale_obj)
                            if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_obj.business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                    free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                    eligible_product_count = free_product_property_obj.eligible_product_count
                                    defalut_free_product_count = free_product_property_obj.product_count
                                    if main_sale_obj.count >= eligible_product_count:
                                        box_count = math.floor(main_sale_obj.count/eligible_product_count)
                                        free_product_count = box_count*defalut_free_product_count
                                        sale_obj = Sale(
                                            sale_group_id=main_sale_group_obj.id,
                                            product_id=free_product_property_obj.free_product.id,
                                            count=free_product_count,
                                            cost=0,
                                            ordered_by_id=1,
                                            modified_by_id=1
                                        )
                                        sale_obj.save()
                    else:
                        if Sale.objects.filter(sale_group_id=main_sale_group_obj.id,
                                               product_id=product['product_id']).exists():
                            Sale.objects.filter(sale_group_id=main_sale_group_obj.id,
                                                product_id=product['product_id']).delete()
                            if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_obj.business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                    free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                    if Sale.objects.filter(sale_group_id=main_sale_group_obj.id, product_id=free_product_property_obj.free_product.id).exists():
                                        Sale.objects.filter(sale_group_id=main_sale_group_obj.id, product_id=free_product_property_obj.free_product.id).delete()
                            print('deleted')
                employee_id = 3
                if session.id == 1:
                    oppsite_session_id = 2
                else:
                    oppsite_session_id = 1
                if SaleGroup.objects.filter(date=main_sale_group_obj.date, session_id=oppsite_session_id,
                                            business_id=business_id).exists():
                    opposite_sale_group_obj = SaleGroup.objects.get(date=main_sale_group_obj.date,
                                                                    session_id=oppsite_session_id,
                                                                    business_id=business_id)
                    if CounterEmployeeTraceSaleGroupMap.objects.filter(
                            counter_employee_trace__collection_date=opposite_sale_group_obj.time_created,
                            sale_group=opposite_sale_group_obj).exists():
                        counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
                            counter_employee_trace__collection_date=opposite_sale_group_obj.time_created,
                            sale_group=opposite_sale_group_obj)
                        counter_sale_group_obj.sale_group.add(main_sale_group_obj)
                        counter_sale_group_obj.save()
                temp_sale_group_payment_request_map.sale_group.add(main_sale_group_obj.id)
        temp_sale_group_payment_request_map.save()
        if super_sale_group_obj is not None:
            super_sale_group_obj.mor_sale_group_id = sale_group_ids[1]
            super_sale_group_obj.eve_sale_group_id = sale_group_ids[2]
            super_sale_group_obj.save()
            sale_df = None
            sale_group_ids = list(SaleGroup.objects.filter(business_id=business_id, date=date).values_list('id', flat=True))
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
            sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=date,
                                                                     super_sale_group_id=super_sale_group_obj.id,
                                                                     sale_group_order_type_id=2,  # order increase
                                                                     transacted_amount=decrypted_string_and_value['AMT'],
                                                                     counter_id=23)
            if not sale_df is None:
                sale_group_transaction_trace.order_sale_group_json = sale_df.to_dict('r')
            sale_group_transaction_trace.save()
        if payment_request_obj.is_wallet_selected:
            if payment_request_obj.wallet_balance_after_this_transaction < agent_wallet_obj.current_balance:
                print('came first')
                transaction_obj = TransactionLog(
                    date=datetime.datetime.now(),
                    transacted_by_id=business_obj.user_profile.user.id,
                    transacted_via_id=1,
                    data_entered_by_id=business_obj.user_profile.user.id,
                    amount=agent_wallet_obj.current_balance - Decimal(
                        payment_request_obj.wallet_balance_after_this_transaction),
                    transaction_direction_id=2,  # from agent wallet to aavin
                    transaction_mode_id=1,  # Upi
                    transaction_status_id=2,  # completed
                    transaction_id=decrypted_string_and_value['RID'],
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=datetime.datetime.now(),
                    wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=payment_request_obj.wallet_balance_after_this_transaction,
                    description='Amount for ordering the product from agent wallet',
                    modified_by_id=business_obj.user_profile.user.id
                )
                transaction_obj.save()
                agent_wallet_obj.current_balance = payment_request_obj.wallet_balance_after_this_transaction
                agent_wallet_obj.save()
                if super_sale_group_obj is not None:
                    sale_group_transaction_trace.is_wallet_used = True
                    sale_group_transaction_trace.wallet_amount = transaction_obj.amount
                    sale_group_transaction_trace.wallet_transaction_id = transaction_obj.id
                    sale_group_transaction_trace.save()
        try:
            sale_group_obj = SaleGroup.objects.filter(business_id=business_id, date=date)
            sale_group_ids = list(sale_group_obj.values_list('id', flat=True))
            sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids, product__is_active=True)
            sale_list = list(sale_obj.values_list('id', 'sale_group__session',
                                                  'product__short_name', 'count', ))
            sale_column = ['sale_id', 'session_name', 'product_name', 'quantity', ]
            sale_df = pd.DataFrame(sale_list, columns=sale_column)
            product_message = ''
            product_list = sale_df.groupby('product_name').apply(lambda x: x.to_dict('r')).to_dict()
            for product in product_list:
                temp_dict = product_list[product]
                morning_order = 0
                eve_order = 0
                for order in temp_dict:
                    if order['session_name'] == 1:
                        morning_order = order['quantity']
                    elif order['session_name'] == 2:
                        eve_order = order['quantity']
                product_message = product_message + product + ':' + str(int(morning_order)) + '+' + str(
                    int(eve_order)) + '; '
            booth_number = Business.objects.get(id=business_id).code
            date_in_format = datetime.datetime.strptime(str(date), '%Y-%m-%d')
            date = datetime.datetime.strftime(date_in_format, '%d-%m-%y')
            counter_name = 'Online'
            amount = sale_group_obj.aggregate(Sum('total_cost'))['total_cost__sum']
            message = 'Booth#{}. for {}. @{}. Rs. {}. {} Edited'.format(booth_number, date, counter_name, amount,
                                                              product_message)
            purpose = 'New Order Confirmation Message'
            phone = agent_obj.agent_profile.mobile
            send_message_via_netfision(purpose, phone, message)
            print('message sent')
        except Exception as e:
            print(e)
        try:
            transaction_log_obj = TransactionLog.objects.filter(transaction_id=decrypted_string_and_value['RID'])[0]
            transaction_log_obj.transaction_status_id = 2
            transaction_log_obj.save()
            sale_group_transaction_trace.bank_transaction_id = transaction_log_obj.id
            sale_group_transaction_trace.save()
        except Exception as e:
            print(e)


@transaction.atomic
@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def payment_response(request):
    sid = transaction.savepoint()
    try:

        encrypted_key_from_payment = request.query_params.get('i')
        # encrypted_key_from_payment = '2rYmGMyoQhictpWmGE6D4vhePd+HmEf87QizvjiB8MT9NkQhBB4VFT8v9Kqff1nHjP3mQINg/P+E/4GTozLedKx9p9zg4CLjnBz99cfi12OAmq+genM9QRE7+I4x59A2h4bFO3WBw13c+u8/+Zrnxq46ial2TPpnhTb9DUUlqXT1qHX8pnIUbQWzalsDCNmd+xoOpy7j7G98TFewtYWWusdsEZ940xYFlxyWTC561S4e1NUvsuh3NazecZ90P6OLP+AFPLcBxxHzf5DT7sZ7dwvz2a/tHuJNc1sOofNG28Q='

        encrypted_key_from_payment = b64decode(encrypted_key_from_payment)
        decipher = AES.new(encryption_key, AES.MODE_ECB)
        decrypted_text = decipher.decrypt(encrypted_key_from_payment).decode("utf-8")
        print(decrypted_text)
        # split plain text by &
        splited_string = decrypted_text.split('&')

        # status code with ids
        transaction_status_obj = PaymentTransactionStatus.objects.all()
        transaction_status_list = list(transaction_status_obj.values_list('id', 'name', 'code'))
        transaction_status_column = ['id', 'name', 'code']
        transaction_status_df = pd.DataFrame(transaction_status_list, columns=transaction_status_column)
        transaction_status_dict = transaction_status_df.groupby('code').apply(lambda x: x.to_dict('r')[0]).to_dict()

        # create dict for key and respected value
        decrypted_string_and_value = {
            'BRN': None,
            'STC': None,
            'RMK': None,
            'TRN': None,
            'TET': None,
            'PMD': None,
            'RID': None,
            'VER': None,
            'CID': None,
            'TYP': None,
            'CRN': None,
            'CNY': None,
            'AMT': None,
            'CKS': None,
        }

        # store the parameters in dict for update payemnt responce table
        for string in splited_string:
            temp_split = string.split('=')
            decrypted_string_and_value[temp_split[0]] = temp_split[1]
        payment_request_obj = PaymentRequest.objects.get(rid=decrypted_string_and_value['RID'])
        try:
            if str(decrypted_string_and_value['PMD']) == 'C' and str(decrypted_string_and_value['STC']) == '101':
                purpose = 'Sending URN number to cash mode payment customers'
                user_id = PaymentRequestUserMap.objects.get(
                    payment_request_id=payment_request_obj.id).payment_intitated_by.id
                user_type_id = UserProfile.objects.get(user_id=user_id).user_type_id
                if user_type_id == 2:
                    business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user_id=user_id)
                    mobile_number = business_agent_obj.agent.agent_profile.mobile
                    booth_code = business_agent_obj.business.code
                    name = business_agent_obj.agent.first_name
                    amount = round(Decimal(decrypted_string_and_value['AMT']), 2)
                    if payment_request_obj.payment_request_for_id == 1:
                        temp_sale_group_ids = list(SaleGroupPaymentRequestMap.objects.filter(
                            payment_request_id=payment_request_obj.id).values_list('temp_sale_group', flat=True))
                        date = TempSaleGroup.objects.get(id=temp_sale_group_ids[0]).date
                        date = date.strftime("%d-%b")
                    elif payment_request_obj.payment_request_for_id == 2:
                        temp_sale_group_ids = list(SaleGroupEditPaymentRequestMap.objects.filter(
                            payment_request_id=payment_request_obj.id).values_list('temp_sale_group_for_edit', flat=True))
                        date = TempSaleGroup.objects.get(id=temp_sale_group_ids[0]).date
                        date = date.strftime("%d-%b")
                    message = 'Dear, {} (#{}), URN for delivery date {} is {}. Total amont to be paid is {} Rs. Please Pay before 3pm today at any Axis Bank Branch'.format(
                        name, booth_code, date, str(decrypted_string_and_value['BRN']), amount)
                elif user_type_id == 3:
                    mobile_number = UserProfile.objects.get(user_id=user_id).mobile
                    message = 'Your URN Number is ' + str(decrypted_string_and_value['BRN'])
                send_message_via_netfision(purpose, mobile_number, message)
        except Exception as e:
            print(e)
        # get patment request obj
        if payment_request_obj.payment_request_for_id == 1:
            create_main_sale_from_temp_sale(payment_request_obj, decrypted_string_and_value)
        elif payment_request_obj.payment_request_for_id == 2:
            update_main_sale_from_temp_sale_edit(payment_request_obj, decrypted_string_and_value)
        elif payment_request_obj.payment_request_for_id == 3:
            create_main_icustomer_sale_from_temp_sale_icustomer_sale(payment_request_obj, decrypted_string_and_value)
        elif payment_request_obj.payment_request_for_id == 5:
            create_main_by_sale_from_temp_by_sale(payment_request_obj, decrypted_string_and_value)
        decrypted_string_and_value['request_from_id'] = payment_request_obj.payment_request_for_id
        decrypted_string_and_value['ordered_via_id'] = payment_request_obj.ordered_via.id

        # # create payment responce obj
        if decrypted_string_and_value['TET'] == '':
            transaction_date_time_in_format = datetime.datetime.now()
        else:
            transaction_date_time_in_format = datetime.datetime.strptime(decrypted_string_and_value['TET'],
                                                                        '%Y/%m/%d %H:%M:%S %p')
        # transaction_date_time_in_format = datetime.datetime.strptime(decrypted_string_and_value['TET'], '%Y/%m/%d %H:%M:%S %p')
        if decrypted_string_and_value['TRN'] == '':
            decrypted_string_and_value['TRN'] = decrypted_string_and_value['RID'] + '_cancelled'
        payment_responce_obj = PaymentRequestResponse(payment_request_id=payment_request_obj.id,
                                                    rid=decrypted_string_and_value['RID'],
                                                    status_id=transaction_status_dict[decrypted_string_and_value['STC']][
                                                        'id'],
                                                    encrypted_string=str(encrypted_key_from_payment),
                                                    decrypted_string=decrypted_text,
                                                    brn=decrypted_string_and_value['BRN'],
                                                    trn=decrypted_string_and_value['TRN'],
                                                    tet=transaction_date_time_in_format,
                                                    pmd=decrypted_string_and_value['PMD'],
                                                    stc=decrypted_string_and_value['STC'],
                                                    rmk=decrypted_string_and_value['RMK'],
                                                    ver=decrypted_string_and_value['VER'],
                                                    cid=decrypted_string_and_value['CID'],
                                                    typ=decrypted_string_and_value['TYP'],
                                                    crn=decrypted_string_and_value['CRN'],
                                                    cny=decrypted_string_and_value['CNY'],
                                                    amt=decrypted_string_and_value['AMT'],
                                                    cks=decrypted_string_and_value['CKS'])

        payment_responce_obj.save()
        print('saved')
        transaction.savepoint_commit(sid)
        return render(request, 'success.html', decrypted_string_and_value)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_route_expiry_time(request):
    print(request.data)
    route_obj = Route.objects.get(id=request.data['id'])
    route_time_change_log_obj = RouteTimeChangeLog(route=route_obj.name[:-4],
                                                   session_id=route_obj.session.id,
                                                   old_time=route_obj.order_expiry_time,
                                                   new_time=request.data['order_expiry_time'],
                                                   changed_by=request.user,
                                                   changed_at=datetime.datetime.now())
    route_time_change_log_obj.save()
    route_obj.order_expiry_time = request.data['order_expiry_time']
    route_obj.save()
    return Response(status=status.HTTP_200_OK)


def generate_rid_code():
    current_date = datetime.datetime.now().date()
    rid_value = str((current_date.year))[2:] + str(current_date.month) + str(current_date.day).zfill(2)
    if PaymentRequestIdBank.objects.filter(date=current_date).exists():
        id_bank_obj = PaymentRequestIdBank.objects.filter(date=current_date)[0]
    else:
        id_bank_obj = PaymentRequestIdBank(date=current_date, last_count=0)
        id_bank_obj.save()
    last_count = int(id_bank_obj.last_count)
    last_count += 1
    id_bank_obj.last_count = last_count
    id_bank_obj.save()
    last_count = str(last_count).zfill(5)
    return rid_value + str(last_count)

@transaction.atomic
@api_view(['POST'])
def create_encryption_text_and_make_request(request):
    # save order in temp salegroup
    sid = transaction.savepoint()
    try:
        user_profile_id = request.user.userprofile.id
        business_id = Business.objects.get(user_profile_id=user_profile_id).id
        agent_user_id = Business.objects.get(id=business_id).user_profile.user.id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
        business_type_id = Business.objects.get(id=business_id).business_type.id
        if request.data['from'] == 'mobile':
            via_id = 1
        else:
            via_id = 3
        if PaymentGatewayConfiguration.objects.filter(ordered_via_id=via_id).exists():
            online_payment_configuration_obj = PaymentGatewayConfiguration.objects.get(ordered_via_id=via_id)
            if online_payment_configuration_obj.is_enable == False:
                data_dict = {
                    'is_online_enable': False,
                    'alert_text': online_payment_configuration_obj.alert_message
                }
                return Response(data=data_dict, status=status.HTTP_200_OK)
        business_obj = Business.objects.get(id=business_id)
        data_dict = serve_product_and_session_list(user_profile_id)
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        product_quantity_variation_list = data_dict['product_quantity_variation_list']
        product_form_details = request.data['product_form_details']
        agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
        temp_wallet_amount = agent_wallet_obj.current_balance
        product_shot_name_for_transaction = ''
        temp_sale_group_list = []
        overall_total_cost = 0
        for date in request.data['order_date']:
            for session in session_list:
                total_cost_per_session = 0
                route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                        route__session_id=session['id']).route_id
                print(route_id)
                if product_form_details[date]['total_price_per_session'][str(session['id'])] != 0:
                    temp_sale_group_obj = TempSaleGroup(
                        business_id=business_id,
                        business_type_id=business_type_id,
                        date=date,
                        session_id=session['id'],
                        ordered_via_id=via_id,
                        payment_status_id=1,  # paid m
                        sale_status_id=1,  # ordered
                        total_cost=0,
                        ordered_by=request.user,
                        modified_by=request.user,
                        product_amount=0,
                        route_id=route_id,
                        zone_id=business_obj.zone.id
                    )
                    temp_sale_group_obj.save()
                    # print('sale group saved')
                    for product in product_list:
                        product_quantity = \
                        product_form_details[date]['product'][str(session['id'])][str(product['product_id'])]['quantity']
                        if product_quantity != 0 and product_quantity != None:
                            if product['product_group_id'] == 3:
                                for variation_price in product_quantity_variation_list[product['product_id']]:
                                    if product_quantity >= variation_price['min_quantity'] and product_quantity <= \
                                            variation_price['max_quantity']:
                                        product_cost = product_quantity * variation_price['mrp']
                            else:
                                product_cost = product_quantity * product['product_mrp']
                            sale_obj = TempSale(
                                temp_sale_group_id=temp_sale_group_obj.id,
                                product_id=product['product_id'],
                                count=product_quantity,
                                cost=product_cost,
                                ordered_by=request.user,
                                modified_by=request.user
                            )
                            sale_obj.save()
                            if BusinessTypeWiseFreeProductConfig.objects.filter(business_type_id=business_type_id, main_product_id=product['product_id'], is_free=True).exists():
                                if FreeProductProperty.objects.filter(main_product_id=product['product_id'], is_active=True).exists():
                                    free_product_property_obj = FreeProductProperty.objects.get(main_product_id=product['product_id'], is_active=True)
                                    eligible_product_count = free_product_property_obj.eligible_product_count
                                    defalut_free_product_count = free_product_property_obj.product_count
                                    if product_quantity >= eligible_product_count:
                                        box_count = math.floor(product_quantity/eligible_product_count)
                                        free_product_count = box_count*defalut_free_product_count
                                        sale_obj = TempSale(
                                            temp_sale_group_id=temp_sale_group_obj.id,
                                            product_id=free_product_property_obj.free_product.id,
                                            count=free_product_count,
                                            cost=0,
                                            ordered_by_id=1,
                                            modified_by_id=1
                                        )
                                        sale_obj.save()
                            product_shot_name_for_transaction = product_shot_name_for_transaction + product[
                                'product_short_name'] + ','
                            # print('new sale created')
                            total_cost_per_session += product_cost
                    saved_temp_sale_group_obj = TempSaleGroup.objects.get(id=temp_sale_group_obj.id)
                    saved_temp_sale_group_obj.total_cost = total_cost_per_session
                    saved_temp_sale_group_obj.product_amount = total_cost_per_session
                    overall_total_cost += total_cost_per_session
                    credit_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=2, order_category_id=1).values_list('business_type_id', flat=True))
                    if business_type_id in credit_business_type_ids:
                        if temp_wallet_amount >= 0:
                            temp_wallet_amount = temp_wallet_amount - total_cost_per_session
                            if temp_wallet_amount >= 0:
                                saved_temp_sale_group_obj.payment_status_id = 1  # Paid
                            else:
                                saved_temp_sale_group_obj.payment_status_id = 2  # partically paid
                        else:
                            saved_temp_sale_group_obj.payment_status_id = 3  # Not paid
                    saved_temp_sale_group_obj.save()
                    temp_sale_group_list.append(saved_temp_sale_group_obj.id)
                    if product_form_details[date]['total_price_per_session'][str(session['id'])] == total_cost_per_session:
                        print('session price is equal')
                    else:
                        print('session price not equal')
        rid = generate_rid_code()
        if request.data['final_price'] != 0:
            transaction_obj = TransactionLog(
                date=datetime.datetime.now(),
                transacted_by_id=agent_user_id,
                transacted_via_id=via_id,
                data_entered_by=request.user,
                amount=request.data['final_price'],
                transaction_direction_id=1,  # from agent to aavin
                transaction_mode_id=1,  # Upi
                transaction_id=rid,
                transaction_status_id=1,  # completed
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                description='Amount for ordering the product',
                modified_by=request.user
            )
            transaction_obj.save()

        # dict for filling white space in ACII method
        pad_text_dict = {
            0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07', 8: '\x08', 9: '\x09',
            10: '\x0a', 11: '\x0b', 12: '\x0c', 13: '\x0d', 14: '\x0e', 15: '\x0f', 16: '\x10'
        }

        ppi_parameter_list = ['transaction_id', 'transaction_pkey', 'salegroup_id', 'booth_code', 'customer_code',
                            'product_list', 'user_code', 'device_type', 'amount']
        ppi_parameter_dict = {'transaction_id': '', 'transaction_pkey': '', 'salegroup_id': '', 'booth_code': '',
                            'customer_code': '', 'product_list': '', 'user_code': '', 'device_type': '', 'amount': ''}

        # PPI parameters
        ppi_parameter_dict['transaction_id'] = rid
        ppi_parameter_dict['transaction_pkey'] = transaction_obj.id
        ppi_parameter_dict['salegroup_id'] = temp_sale_group_list[0]
        ppi_parameter_dict['product_list'] = product_shot_name_for_transaction[:50]
        ppi_parameter_dict['user_code'] = request.user.id
        ppi_parameter_dict['device_type'] = request.data['from']
        ppi_parameter_dict['amount'] = round(request.data['final_price'], 2)

        # parameters for encryption
        booth_or_customer_code = business_obj.code
        ppi_parameter_dict['booth_code'] = booth_or_customer_code
        ppi_parameter_dict['customer_code'] = booth_or_customer_code
        ver = '1.0'  # version
        # cid = 5494 # cid for aavin given by axis bank
        # typ = 'TEST' # test environment
        cid = 5648  # cid for aavin given by axis bank
        typ = 'PRD'  # Production environment
        rid = rid  # generated reference number
        crn = rid + 'b' + booth_or_customer_code  # customer reference number
        cny = 'INR'
        amount = ppi_parameter_dict['amount']
        rtu = 'http://pay.aavincoimbatore.com/main/payment/response/'  # reponse will returned to this uRL
        ppi = '{}|{}|{}|{}|{}|{}|{}|{}|{}|'.format(ppi_parameter_dict['transaction_id'],
                                                ppi_parameter_dict['transaction_pkey'],
                                                ppi_parameter_dict['salegroup_id'], ppi_parameter_dict['booth_code'],
                                                ppi_parameter_dict['customer_code'], ppi_parameter_dict['product_list'],
                                                ppi_parameter_dict['user_code'], ppi_parameter_dict['device_type'],
                                                ppi_parameter_dict['amount'])  # ppi parameters for display on interface
        re1 = 'MN'

        # need to encrypt cid, rid, crn, amt and checksum in Sha256
        key_before_sha_encrypt = '{}{}{}{}{}'.format(cid, rid, crn, amount, checksum_key)
        cks = hashlib.sha256(key_before_sha_encrypt.encode()).hexdigest()
        plain_string = 'CID={}&RID={}&CRN={}&AMT={}&VER={}&TYP={}&CNY={}&RTU={}&PPI={}&RE1=&RE2=&RE3=&RE4=&RE5=&CKS={}'.format(
            cid, rid, crn, amount, ver, typ, cny, rtu, ppi, cks)

        # AES encryption
        obj = AES.new(encryption_key, AES.MODE_ECB, 'OPENSSL_RAW_DATA')
        pad_count = (16 - len(plain_string) % 16)
        padded_text = plain_string + (16 - len(plain_string) % 16) * pad_text_dict[pad_count]
        cipertext = obj.encrypt(padded_text)
        encrypted_string = b64encode(cipertext).decode('utf-8')
        payment_request_obj = PaymentRequest(rid=rid,
                                            status_id=1,
                                            payment_request_for_id=1,
                                            encrypted_string=encrypted_string,
                                            decrypted_string=plain_string,
                                            ordered_via_id=via_id,
                                            ver=ver,
                                            cid=cid,
                                            typ=typ,
                                            crn=crn,
                                            cny=cny,
                                            amt=amount,
                                            rtu=rtu,
                                            ppi=ppi,
                                            re1=re1,
                                            cks=cks)
        if request.data['final_customer_wallet'] < agent_wallet_obj.current_balance:
            payment_request_obj.is_wallet_selected = True
            payment_request_obj.wallet_balance_after_this_transaction = request.data['final_customer_wallet']
        payment_request_obj.save()

        # payement request PPI
        for parameter in ppi_parameter_list:
            payment_request_ppi = PaymentRequestPPI(payment_request=payment_request_obj,
                                                    key=parameter,
                                                    value=ppi_parameter_dict[parameter]
                                                    )
            payment_request_ppi.save()

        # link temp_salegroup with payment request
        temp_sale_group_payment_request_map = SaleGroupPaymentRequestMap(payment_request_id=payment_request_obj.id)
        temp_sale_group_payment_request_map.save()
        for sale_group_id in temp_sale_group_list:
            temp_sale_group_payment_request_map.temp_sale_group.add(sale_group_id)
        temp_sale_group_payment_request_map.save()

        # payment_request_inditated
        payment_request_user_map = PaymentRequestUserMap(payment_request_id=payment_request_obj.id,
                                                        payment_intitated_by_id=request.user.id)
        payment_request_user_map.save()

        data_dict = {
            'encrypted_string': encrypted_string,
            'is_online_enable': True,
        }
        transaction.savepoint_commit(sid)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_overall_route_expiry_time(request):
    print(request.data)
    if request.data['session_id'] == 1:
        exclude_route_ids = [149, 233, 151, 234, 153, 235, 256, 250, 147, 262, 270]
    else:
        exclude_route_ids = [150, 194, 152, 195, 154, 196, 258, 252, 148, 264, 272]
    for route in Route.objects.filter(session_id=request.data['session_id']).exclude(id__in=exclude_route_ids):
        last_time = route.order_expiry_time
        route.order_expiry_time = request.data['route_time']
        route.save()
    route_time_change_log_obj = RouteTimeChangeLog(route='All Route',
                                                   session_id=route.session.id,
                                                   old_time=last_time,
                                                   new_time=request.data['route_time'],
                                                   changed_by=request.user,
                                                   changed_at=datetime.datetime.now())
    route_time_change_log_obj.save()
    return Response(status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['POST'])
def save_agent(request):
    sid = transaction.savepoint()
    try:
        if request.data['agent_id'] is None:
            if Agent.objects.filter(agent_code=request.data['agent_code']).exists():
                data = {'message': 'Agent already created :' + str(request.data['agent_code'])}
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                print('agent register : user saved')
                # user saved
                agent_profile = AgentProfile(
                    union_id=request.data['union_id'],
                    street=request.data['street'],
                    gender_id=request.data['gender_id'],
                    taluk_id=request.data['taluk_id'],
                    district_id=request.data['district_id'],
                    state_id=request.data['state_id'],
                    mobile=request.data['mobile'],
                    alternate_mobile=request.data['alternate_mobile'],
                    pincode=request.data['pincode'],
                    created_by=request.user,
                    modified_by=request.user
                )

                try:
                    agent_profile.image = decode_image(request.data['image'])
                except Exception as err:
                    print(err)
                agent_profile.save()

                print('agent profile saved')

                agent = Agent(
                    agent_profile=agent_profile,
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name'],
                    agent_code=request.data['agent_code'],
                    aadhar_number=request.data['aadhar_number'],
                    pan_number=request.data['pan_number'],
                    ration_card_number=request.data['ration_card_number'],
                    communication_address=request.data['communication_address'],
                    created_by=request.user,
                    modified_by=request.user
                )

                try:
                    if request.data['aadhar_document'] != None:
                        agent.aadhar_document = decode_image(request.data['aadhar_document'])
                except Exception as err:
                    print(err)
                agent.save()

                print('agent saved')

                AgentWallet.objects.create(agent=agent)
                ByProductAgentWallet.objects.create(agent=agent)
                print('agent wallet saved')

                # bank
                agent_bank = AgentBankDetail(
                    agent=agent,
                    bank=request.data['bank_name'],
                    account_number=request.data['account_number'],
                    branch=request.data['branch_name'],
                    ifsc_code=request.data['ifsc_code'],
                    is_active=True
                )

                if request.data['micr_code'] != None:
                    agent_bank.micr_code = request.data['micr_code']

                if request.data['account_holder_name'] != None:
                    agent_bank.account_holder_name = request.data['account_holder_name']

                if request.data['account_number'] != None:
                    agent_bank.account_number = request.data['account_number']

                agent_bank.save()

                print('agent register : agent bank saved')
                data = {'message': 'Agent created completed succssfully'}
                data['agent_id'] = agent.id
                transaction.savepoint_commit(sid)
                return Response(data=data, status=status.HTTP_200_OK)
        else:
            print(request.data)
            print('else')
            agent_id = request.data['agent_id']
            agent = Agent.objects.get(id=agent_id)
            agent_profile_id = Agent.objects.get(id=agent.id).agent_profile.id

            agent_profile_obj = AgentProfile.objects.filter(id=agent_profile_id).update(
                union_id=request.data['union_id'],
                street=request.data['street'],
                gender_id=request.data['gender_id'],
                taluk_id=request.data['taluk_id'],
                district_id=request.data['district_id'],
                state_id=request.data['state_id'],
                mobile=request.data['mobile'],
                alternate_mobile=request.data['alternate_mobile'],
                pincode=request.data['pincode'],
                created_by=request.user,
                modified_by=request.user
            )
            agent_profile_obj = AgentProfile.objects.get(id=agent_profile_id)
            if request.data['image'] != None:
                try:
                    if 'changingThisBreaksApplicationSecurity' in request.data['image']:
                        agent_profile_obj.image = decode_image(
                            request.data['image']['changingThisBreaksApplicationSecurity'])
                    else:
                        agent_profile_obj.image = decode_image(request.data['image'])
                except Exception as err:
                    print(err)

                agent_profile_obj.save()

            Agent.objects.filter(id=agent_id).update(
                agent_profile=agent_profile_obj,
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                agent_code=request.data['agent_code'],
                aadhar_number=request.data['aadhar_number'],
                pan_number=request.data['pan_number'],
                ration_card_number=request.data['ration_card_number'],
                communication_address=request.data['communication_address'],
                created_by=request.user,
                modified_by=request.user
            )

            if request.data['aadhar_document'] != None:
                agent_obj = Agent.objects.get(id=agent_id)
                try:
                    if 'changingThisBreaksApplicationSecurity' in request.data['aadhar_document']:
                        agent_obj.aadhar_document = decode_image(
                            request.data['aadhar_document']['changingThisBreaksApplicationSecurity'])
                    else:
                        agent_obj.aadhar_document = decode_image(request.data['aadhar_document'])
                except Exception as err:
                    print(err)
                agent_obj.save()

            AgentBankDetail.objects.filter(agent_id=request.data['agent_id']).update(
                agent=agent,
                bank=request.data['bank_name'],
                branch=request.data['branch_name'],
                ifsc_code=request.data['ifsc_code'],
                account_number=request.data['account_number'],
                is_active=True,
                micr_code=None
            )

            agent_bank = AgentBankDetail.objects.get(agent_id=request.data['agent_id'])

            if request.data['micr_code'] != None:
                agent_bank.micr_code = request.data['micr_code']

            if request.data['account_holder_name'] != None:
                agent_bank.account_holder_name = request.data['account_holder_name']

            agent_bank.save()

            data = {'message': 'Agent Updated successfully'}
            transaction.savepoint_commit(sid)
            return Response(data=data, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)

@transaction.atomic
@api_view(['POST'])
def save_booth_with_nominee(request):
    data = {}
    # create if not
    if request.data['id'] is None:
        if User.objects.filter(username=request.data['code']).exists():
            print('already booth exists')
            data['message'] = "already booth exists"
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            sid = transaction.savepoint()
            try:
                pass_code = generate_booth_password()
                user = User(
                    username=request.data['code'],
                    first_name=request.data['code'],
                    password=make_password(pass_code),
                )
                user.save()
                print('booth user created')

                print(request.data['agent_id'])
                agent = Agent.objects.get(id=request.data['agent_id'])
                agent_mobile = agent.agent_profile.mobile
                # user profile
                user_profile = UserProfile(
                    union=agent.agent_profile.union,
                    user=user,
                    user_type_id=2,
                    gender=agent.agent_profile.gender,
                    taluk=agent.agent_profile.taluk,
                    district=agent.agent_profile.district,
                    state=agent.agent_profile.state,
                    mobile=agent.agent_profile.mobile,
                )
                user_profile.save()
                print('user_profile saved')

                business_obj = Business(
                    code=request.data['code'],
                    zone_id=request.data['zone_id'],
                    user_profile=user_profile,
                    business_type_id=request.data['business_type_id'],
                    constituency_id=request.data['constituency_id'],
                    ward_id=request.data['ward_id'],
                    address=request.data['address'],
                    location_category_id=request.data['location_category_id'],
                    location_category_value=request.data['location_category_value'],

                    pincode=request.data['pincode'],
                    working_hours_from=request.data['working_hours_from'],
                    working_hours_to=request.data['working_hours_to'],
                    created_by=request.user,
                    modified_by=request.user
                )

                if request.data['landmark'] == None:
                    business_obj.landmark = ' '
                else:
                    business_obj.landmark = request.data['landmark']
                if request.data['is_rural']:
                    business_obj.is_rural = True
                    business_obj.is_urban = False
                else:
                    business_obj.is_rural = False
                    business_obj.is_urban = True

                if request.data['name'] != None:
                    business_obj.name = request.data['name']
                business_obj.save()

                # updating the last count in business code bank
                BusinessCodeBank.objects.filter(business_type_id=request.data['business_type_id']).update(
                    last_code=request.data['code'])

                # for trace table and product business wise discount table
                if not request.data['business_type_id'] == 10:
                    if 'product_price' in request.data:
                        product_ids = request.data['product_price'].keys()
                        if len(product_ids) > 0:
                            for product_id in product_ids:
                                # save_business_wise_product_discount(business_obj.id, product_id,
                                #                                     request.data['product_price'][product_id],
                                #                                     request.user.id)
                                print('saved product discounts')
                data = {'message': 'Booth registered successfully'}

                # nominee
                nominee_obj = Nominee(
                    first_name=request.data['nominee_first_name'],
                    last_name=request.data['nominee_last_name'],
                    relation_type_id=request.data['nominee_relation_type_id'],
                )
                if 'nominee_aadhar_number' in request.data:
                    nominee_obj.aadhar_number = request.data['nominee_aadhar_number']

                if request.data['nominee_aadhar_number'] != None:
                    nominee_obj.aadhar_number = request.data['nominee_aadhar_number']
                if request.data['nominee_phone'] != None:
                    nominee_obj.phone = request.data['nominee_phone']

                nominee_obj.save()
                print('nominee saved')

                # business map
                business_agent_map = BusinessAgentMap(
                    agent=agent,
                    business=business_obj,
                    is_active=True,
                    active_from=datetime.datetime.now(),
                    nominee=nominee_obj,
                    deposit_date=request.data['deposit_date'].split('T')[0],
                    deposit_amount=request.data['deposit_amount'],
                    deposit_status_id=1,
                    deposit_status_description='deposited',
                )
                try:
                    if request.data['deposit_receipt_image'] is not None:
                        business_agent_map.deposit_receipt_image = decode_image(request.data['deposit_receipt_image'])
                except Exception as err:
                    print(err)
                business_agent_map.save()
                print('Business agent map saved')
                # business_agent_map saved

                # route map
                morg_last_ordinal = 1
                eve_last_ordinal = 1
                if RouteBusinessMap.objects.filter(route_id=request.data['morg_route_id']).exists():
                    morg_last_ordinal = RouteBusinessMap.objects.filter(route_id=request.data['morg_route_id']).order_by('-ordinal')[0].ordinal
                if RouteBusinessMap.objects.filter(route_id=request.data['eve_route_id']).exists():
                    eve_last_ordinal = RouteBusinessMap.objects.filter(route_id=request.data['eve_route_id']).order_by('-ordinal')[0].ordinal

                morg_route_map = RouteBusinessMap(
                    route_id=request.data['morg_route_id'],
                    business=business_obj,
                    ordinal=morg_last_ordinal)
                morg_route_map.save()
    
                eveg_route_map = RouteBusinessMap(
                    route_id=request.data['eve_route_id'],
                    business=business_obj,
                    ordinal=eve_last_ordinal)
                eveg_route_map.save()
                message = ''
                purpose = 'sending_otp_for_booth_agent'
                message = 'Dear ' + str(
                    agent.first_name) + ' you have successfully set up an online account.Your username is: ' + str(
                    request.data['code']) + 'and  Your temporary password is  ' + str(
                    pass_code) + '. You can change it anytime on the order page.'
                send_message_via_netfision(purpose, agent_mobile, message)
                transaction.savepoint_commit(sid)
                return Response(data=data, status=status.HTTP_200_OK)
            except Exception as err:
                print('roll back start')
                # with transaction.atomic():
                transaction.savepoint_rollback(sid)
                print('roll back done')
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

@transaction.atomic
@api_view(['POST'])
def update_and_pay_selected_sale_group(request):
    sid = transaction.savepoint()
    try:
        if request.data['from'] == 'mobile':
            via_id = 1
        else:
            via_id = 3
        if PaymentGatewayConfiguration.objects.filter(ordered_via_id=via_id).exists():
            online_payment_configuration_obj = PaymentGatewayConfiguration.objects.get(ordered_via_id=via_id)
            if online_payment_configuration_obj.is_enable == False:
                data_dict = {
                    'is_online_enable': False,
                    'alert_text': online_payment_configuration_obj.alert_message
                }
                return Response(data=data_dict, status=status.HTTP_200_OK)
        # save order in temp salegroup
        user_profile_id = request.user.userprofile.id
        business_id = Business.objects.get(user_profile_id=user_profile_id).id
        agent_user_id = Business.objects.get(id=business_id).user_profile.user.id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
        business_type_id = Business.objects.get(id=business_id).business_type.id
        business_obj = Business.objects.get(id=business_id)
        data_dict = serve_product_and_session_list(user_profile_id)
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        product_quantity_variation_list = data_dict['product_quantity_variation_list']
        product_form_details = request.data['product_form_details']
        agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
        temp_wallet_amount = agent_wallet_obj.current_balance
        product_shot_name_for_transaction = ''
        temp_sale_group_list = []
        for session in session_list:
            total_cost_per_session = 0
            route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                    route__session_id=session['id']).route_id
            if product_form_details['total_price_per_session'][str(session['id'])] != 0:
                temp_sale_group_obj = TempSaleGroupForEdit(
                    main_sale_group_id=product_form_details['session'][str(session['id'])]['sale_group_id'],
                    business_type_id=business_type_id,
                    business_id=business_id,
                    date=request.data['selected_date'],
                    session_id=session['id'],
                    ordered_via_id=via_id,
                    payment_status_id=1,  # paid m
                    sale_status_id=1,  # ordered
                    total_cost=0,
                    ordered_by=request.user,
                    modified_by=request.user,
                    product_amount=0,
                    route_id=route_id,
                    zone_id=business_obj.zone.id
                )
                temp_sale_group_obj.save()
                # print('sale group saved')
                for product in product_list:
                    product_quantity = \
                    product_form_details['session'][str(session['id'])]['product'][str(product['product_id'])]['quantity']
                    if product_quantity != 0 and product_quantity != None:
                        if product['product_group_id'] == 3:
                            for variation_price in product_quantity_variation_list[product['product_id']]:
                                if product_quantity >= variation_price['min_quantity'] and product_quantity <= \
                                        variation_price['max_quantity']:
                                    product_cost = product_quantity * variation_price['mrp']
                        else:
                            product_cost = product_quantity * product['product_mrp']
                        sale_obj = TempSaleForEdit(
                            main_sale_id=
                            product_form_details['session'][str(session['id'])]['product'][str(product['product_id'])][
                                'sale_id'],
                            temp_sale_group_for_edit_id=temp_sale_group_obj.id,
                            product_id=product['product_id'],
                            count=product_quantity,
                            cost=product_cost,
                            ordered_by=request.user,
                            modified_by=request.user
                        )
                        sale_obj.save()
                        product_shot_name_for_transaction = product_shot_name_for_transaction + product[
                            'product_short_name'] + ','
                        # print('new sale created')
                        total_cost_per_session += product_cost
                saved_temp_sale_group_obj = TempSaleGroupForEdit.objects.get(id=temp_sale_group_obj.id)
                saved_temp_sale_group_obj.total_cost = total_cost_per_session
                saved_temp_sale_group_obj.product_amount = total_cost_per_session
                saved_temp_sale_group_obj.save()
                temp_sale_group_list.append(saved_temp_sale_group_obj.id)
                if product_form_details['total_price_per_session'][str(session['id'])] == total_cost_per_session:
                    print('session price is equal')
                else:
                    print('session price is not equal')
                    # transaction.savepoint_rollback(sid)
                    # return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                if product_form_details['session'][str(session['id'])]['sale_group_id'] is not None:
                    if product_form_details['total_price_per_session'][str(session['id'])] == 0:
                        SaleGroup.objects.get(
                            id=product_form_details['session'][str(session['id'])]['sale_group_id']).delete()
                    else:
                        sale_group_obj = SaleGroup.objects.get(
                            id=product_form_details['session'][str(session['id'])]['sale_group_id'])
                        sale_group_obj.total_cost = total_cost_per_session
                        sale_group_obj.modified_by = request.user
                        sale_group_obj.save()
                        # print('sale group price is 0')
                        sale_obj = Sale.objects.filter(sale_group_id=sale_group_obj.id, product__is_active=True)
                        for sale in sale_obj:
                            # user remove entire session and we need remove quantity from route trace
                            if RouteTrace.objects.filter(date=request.data['selected_date'], session_id=session['id'],
                                                        route_id=route_id).exists():
                                route_trace_obj = RouteTrace.objects.get(date=request.data['selected_date'],
                                                                        session_id=session['id'],
                                                                        route_id=route_id)
                                route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(
                                    route_trace_id=route_trace_obj.id, product_id=sale.product_id)
                                route_trace_sale_summary_obj.quantity -= Decimal(sale.count)
                                route_trace_sale_summary_obj.save()
                            sale.cost = 0
                            sale.count = 0
                            sale.modified_by = request.user
                            sale.save()
        rid = generate_rid_code()
        if request.data['final_price'] != 0:
            transaction_obj = TransactionLog(
                date=datetime.datetime.now(),
                transacted_by_id=agent_user_id,
                transacted_via_id=via_id,
                data_entered_by=request.user,
                amount=request.data['final_price'],
                transaction_direction_id=1,  # from agent to aavin
                transaction_mode_id=1,  # Upi
                transaction_id=rid,
                transaction_status_id=1,  # completed
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                description='Amount for ordering the product',
                modified_by=request.user
            )
            transaction_obj.save()
        # dict for filling white space in ACII method
        pad_text_dict = {
            0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07', 8: '\x08', 9: '\x09',
            10: '\x0a', 11: '\x0b', 12: '\x0c', 13: '\x0d', 14: '\x0e', 15: '\x0f', 16: '\x10'
        }

        ppi_parameter_list = ['transaction_id', 'transaction_pkey', 'salegroup_id', 'booth_code', 'customer_code',
                            'product_list', 'user_code', 'device_type', 'amount']
        ppi_parameter_dict = {'transaction_id': '', 'transaction_pkey': '', 'salegroup_id': '', 'booth_code': '',
                            'customer_code': '', 'product_list': '', 'user_code': '', 'device_type': '', 'amount': ''}

        # PPI parameters
        ppi_parameter_dict['transaction_id'] = rid
        ppi_parameter_dict['transaction_pkey'] = transaction_obj.id
        ppi_parameter_dict['salegroup_id'] = temp_sale_group_list[0]
        ppi_parameter_dict['product_list'] = product_shot_name_for_transaction[:50]
        ppi_parameter_dict['user_code'] = request.user.id
        ppi_parameter_dict['device_type'] = request.data['from']
        ppi_parameter_dict['amount'] = round(request.data['final_price'], 2)

        # parameters for encryption
        booth_or_customer_code = business_obj.code
        ppi_parameter_dict['booth_code'] = booth_or_customer_code
        ppi_parameter_dict['customer_code'] = booth_or_customer_code
        ver = '1.0'  # version
        # cid = 5494 # cid for aavin given by axis bank
        # typ = 'TEST' # test environment
        cid = 5648  # cid for aavin given by axis bank
        typ = 'PRD'  # Production environment
        rid = rid  # generated reference number
        crn = rid + 'b' + booth_or_customer_code  # customer reference number
        cny = 'INR'
        amount = ppi_parameter_dict['amount']
        rtu = 'http://pay.aavincoimbatore.com/main/payment/response/'  # reponse will returned to this uRL
        ppi = '{}|{}|{}|{}|{}|{}|{}|{}|{}|'.format(ppi_parameter_dict['transaction_id'],
                                                ppi_parameter_dict['transaction_pkey'],
                                                ppi_parameter_dict['salegroup_id'], ppi_parameter_dict['booth_code'],
                                                ppi_parameter_dict['customer_code'], ppi_parameter_dict['product_list'],
                                                ppi_parameter_dict['user_code'], ppi_parameter_dict['device_type'],
                                                ppi_parameter_dict['amount'])  # ppi parameters for display on interface
        re1 = 'MN'

        # need to encrypt cid, rid, crn, amt and checksum in Sha256
        key_before_sha_encrypt = '{}{}{}{}{}'.format(cid, rid, crn, amount, checksum_key)
        cks = hashlib.sha256(key_before_sha_encrypt.encode()).hexdigest()
        plain_string = 'CID={}&RID={}&CRN={}&AMT={}&VER={}&TYP={}&CNY={}&RTU={}&PPI={}&RE1=&RE2=&RE3=&RE4=&RE5=&CKS={}'.format(
            cid, rid, crn, amount, ver, typ, cny, rtu, ppi, cks)

        # AES encryption
        obj = AES.new(encryption_key, AES.MODE_ECB, 'OPENSSL_RAW_DATA')
        pad_count = (16 - len(plain_string) % 16)
        padded_text = plain_string + (16 - len(plain_string) % 16) * pad_text_dict[pad_count]
        cipertext = obj.encrypt(padded_text)
        encrypted_string = b64encode(cipertext).decode('utf-8')
        payment_request_obj = PaymentRequest(rid=rid,
                                            status_id=1,
                                            payment_request_for_id=2,
                                            encrypted_string=encrypted_string,
                                            decrypted_string=plain_string,
                                            ordered_via_id=via_id,
                                            ver=ver,
                                            cid=cid,
                                            typ=typ,
                                            crn=crn,
                                            cny=cny,
                                            amt=amount,
                                            rtu=rtu,
                                            ppi=ppi,
                                            re1=re1,
                                            cks=cks)
        if request.data['final_customer_wallet'] < agent_wallet_obj.current_balance:
            payment_request_obj.is_wallet_selected = True
            payment_request_obj.wallet_balance_after_this_transaction = request.data['final_customer_wallet']
        payment_request_obj.save()

        # payement request PPI
        for parameter in ppi_parameter_list:
            payment_request_ppi = PaymentRequestPPI(payment_request=payment_request_obj,
                                                    key=parameter,
                                                    value=ppi_parameter_dict[parameter]
                                                    )
            payment_request_ppi.save()

        # link temp_salegroup with payment request
        temp_sale_group_payment_request_map = SaleGroupEditPaymentRequestMap(payment_request_id=payment_request_obj.id)
        temp_sale_group_payment_request_map.save()
        for sale_group_id in temp_sale_group_list:
            temp_sale_group_payment_request_map.temp_sale_group_for_edit.add(sale_group_id)
        temp_sale_group_payment_request_map.save()

        # payment_request_inditated
        payment_request_user_map = PaymentRequestUserMap(payment_request_id=payment_request_obj.id,
                                                        payment_intitated_by_id=request.user.id)
        payment_request_user_map.save()

        data_dict = {
            'encrypted_string': encrypted_string
        }
        if request.data['from'] == 'mobile':
            identificaiton_token_responce = requests.get('https://easypay.axisbank.co.in/api/generateToken')
            token_from_pg = identificaiton_token_responce.json()['token']
            data_dict['token'] = token_from_pg
        data_dict['is_online_enable'] = True
        transaction.savepoint_commit(sid)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['POST'])
def generate_payment_link_for_icustomer_order(request):
    print(request.data['from'])
    sid = transaction.savepoint()
    try:
        icustomer_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).id
        business_id = ICustomer.objects.get(user_profile_id=request.user.userprofile.id).business_id
        user_profile_id = request.user.userprofile.id
        user_id = request.user.id
        if request.data['from'] == 'mobile':
            via_id = 1
        else:
            via_id = 3
        print(via_id)
        if PaymentGatewayConfiguration.objects.filter(ordered_via_id=via_id).exists():
            online_payment_configuration_obj = PaymentGatewayConfiguration.objects.get(ordered_via_id=via_id)
            if online_payment_configuration_obj.is_enable == False:
                data_dict = {
                    'is_online_enable': False,
                    'alert_text': online_payment_configuration_obj.alert_message
                }
                return Response(data=data_dict, status=status.HTTP_200_OK)
        business_obj = Business.objects.get(id=business_id)
        data_dict = serve_product__and_session_list_for_customer(user_profile_id)
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        date = str(request.data['month_start_date'])
        # date = '2020-03-01'
        month = datetime.datetime.strptime(date, '%Y-%m-%d').month
        date_in_format = datetime.datetime.strptime(date, '%Y-%m-%d')
        if month == datetime.datetime.now().month:
            return Response(status=status.HTTP_409_CONFLICT)
        product_dict = {}
        product_dict[1] = {}
        product_dict[2] = {}
        product_shot_name_for_transaction = ''
        temp_sale_group_list = []
        product_form_details = request.data['product_form_data']
        overall_total_cost = 0
        for session in session_list:
            route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                    route__session_id=session['id']).route_id
            vehicle_obj = RouteVehicleMap.objects.get(route_id=route_id).vehicle
            total_cost_per_session = 0
            total_cost_per_session_for_month = 0
            if product_form_details['total_quantity_per_session'][str(session['id'])] != 0:
                sale_group_obj = TempICustomerSaleGroup(
                    business_id=business_id,
                    icustomer_id=icustomer_id,
                    date=date,
                    session_id=session['id'],
                    ordered_via_id=via_id,
                    payment_status_id=1,  # paid
                    sale_status_id=1,  # ordered
                    total_cost=0,
                    total_cost_for_month=0,
                    ordered_by=request.user,
                    modified_by=request.user,
                    product_amount=0,
                    route_id=route_id,
                    zone_id=business_obj.zone.id
                )
                sale_group_obj.save()
                # print('sale group saved')
                for product in product_list:
                    product_quantity = \
                        product_form_details['product'][str(session['id'])][str(product['product_id'])][
                            'quantity']
                    if product_quantity != 0 and product_quantity != None:
                        sale_obj = TempICustomerSale(
                            temp_icustomer_sale_group_id=sale_group_obj.id,
                            product_id=product['product_id'],
                            count=product_quantity,
                            cost=product_quantity * product['product_mrp'],
                            cost_for_month=product_quantity * product['product_mrp'] * request.data['total_days_in_month'],
                            ordered_by=request.user,
                            modified_by=request.user
                        )
                        sale_obj.save()
                        product_dict[session['id']][product['product_id']] = product_quantity
                        # print('new sale created')
                        total_cost_per_session += product_quantity * product['product_mrp']
                        total_cost_per_session_for_month += product_quantity * product['product_mrp'] * request.data[
                            'total_days_in_month']
                # saved_sale_group_obj = SaleGroup.objects.get(id=sale_group_obj.id)
                sale_group_obj.total_cost = total_cost_per_session
                sale_group_obj.total_cost_for_month = total_cost_per_session_for_month
                sale_group_obj.product_amount = total_cost_per_session
                sale_group_obj.save()
                overall_total_cost += total_cost_per_session_for_month
                product_shot_name_for_transaction = product_shot_name_for_transaction + product['product_short_name'] + ','

                # print('sale group price updated')
                temp_sale_group_list.append(sale_group_obj.id)
                if product_form_details['total_price_per_session'][
                    str(session['id'])] == total_cost_per_session:
                    print('session price is equal')
                else:
                    print('session price not equal')
        icustomer_obj = ICustomer.objects.get(id=icustomer_id)
        customer_wallet_obj = ICustomerWallet.objects.get(customer_id=icustomer_id)
        rid = generate_rid_code()
        if request.data['from'] == 'mobile':
            amount_that_customer_pay = product_form_details['total_price_per_order']
        else:
            amount_that_customer_pay = request.data['final_price']
        
        if amount_that_customer_pay != 0:
            transaction_obj = TransactionLog(
                date=datetime.datetime.now(),
                transacted_by_id=user_id,
                transacted_via_id=via_id,
                data_entered_by=request.user,
                amount=amount_that_customer_pay,
                transaction_direction_id=4,  # from icustomer to aavin
                transaction_mode_id=1,  # Upi
                transaction_id=rid,
                transaction_status_id=2,  # completed
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=customer_wallet_obj.current_balance,
                wallet_balance_after_transaction_approval=customer_wallet_obj.current_balance,
                description='Amount for ordering the product from Icustomer',
                modified_by=request.user
            )
            transaction_obj.save()
        # dict for filling white space in ACII method
        pad_text_dict = {
            0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07', 8: '\x08', 9: '\x09',
            10: '\x0a', 11: '\x0b', 12: '\x0c', 13: '\x0d', 14: '\x0e', 15: '\x0f', 16: '\x10'
        }

        ppi_parameter_list = ['transaction_id', 'transaction_pkey', 'salegroup_id', 'booth_code', 'customer_code',
                            'product_list', 'user_code', 'device_type', 'amount']
        ppi_parameter_dict = {'transaction_id': '', 'transaction_pkey': '', 'salegroup_id': '', 'booth_code': '',
                            'customer_code': '', 'product_list': '', 'user_code': '', 'device_type': '', 'amount': ''}

        # PPI parameters
        ppi_parameter_dict['transaction_id'] = rid
        ppi_parameter_dict['transaction_pkey'] = transaction_obj.id
        ppi_parameter_dict['salegroup_id'] = temp_sale_group_list[0]
        ppi_parameter_dict['product_list'] = product_shot_name_for_transaction[:50]
        ppi_parameter_dict['user_code'] = request.user.id
        ppi_parameter_dict['device_type'] = request.data['from']
        ppi_parameter_dict['amount'] = amount_that_customer_pay

        # parameters for encryption
        business_obj = Business.objects.get(id=business_id)
        booth_or_customer_code = icustomer_obj.customer_code
        ppi_parameter_dict['booth_code'] = business_obj.code
        ppi_parameter_dict['customer_code'] = booth_or_customer_code
        ver = '1.0'  # version
        # cid = 5494 # cid for aavin given by axis bank
        # typ = 'TEST' # test environment
        cid = 5648  # cid for aavin given by axis bank
        typ = 'PRD'  # Production environment
        rid = rid  # generated reference number
        crn = rid + 'b' + booth_or_customer_code  # customer reference number
        crn = crn[:20]
        cny = 'INR'
        amount = ppi_parameter_dict['amount']
        rtu = 'http://pay.aavincoimbatore.com/main/payment/response/'  # reponse will returned to this uRL
        ppi = '{}|{}|{}|{}|{}|{}|{}|{}|{}|'.format(ppi_parameter_dict['transaction_id'],
                                                ppi_parameter_dict['transaction_pkey'],
                                                ppi_parameter_dict['salegroup_id'], ppi_parameter_dict['booth_code'],
                                                ppi_parameter_dict['customer_code'], ppi_parameter_dict['product_list'],
                                                ppi_parameter_dict['user_code'], ppi_parameter_dict['device_type'],
                                                ppi_parameter_dict['amount'])  # ppi parameters for display on interface
        re1 = 'MN'

        # need to encrypt cid, rid, crn, amt and checksum in Sha256
        key_before_sha_encrypt = '{}{}{}{}{}'.format(cid, rid, crn, amount, checksum_key)
        cks = hashlib.sha256(key_before_sha_encrypt.encode()).hexdigest()
        plain_string = 'CID={}&RID={}&CRN={}&AMT={}&VER={}&TYP={}&CNY={}&RTU={}&PPI={}&RE1=&RE2=&RE3=&RE4=&RE5=&CKS={}'.format(
            cid, rid, crn, amount, ver, typ, cny, rtu, ppi, cks)

        # AES encryption
        obj = AES.new(encryption_key, AES.MODE_ECB, 'OPENSSL_RAW_DATA')
        pad_count = (16 - len(plain_string) % 16)
        padded_text = plain_string + (16 - len(plain_string) % 16) * pad_text_dict[pad_count]
        cipertext = obj.encrypt(padded_text)
        encrypted_string = b64encode(cipertext).decode('utf-8')
        payment_request_obj = PaymentRequest(rid=rid,
                                            status_id=1,
                                            payment_request_for_id=3,
                                            encrypted_string=encrypted_string,
                                            decrypted_string=plain_string,
                                            ordered_via_id=via_id,
                                            ver=ver,
                                            cid=cid,
                                            typ=typ,
                                            crn=crn,
                                            cny=cny,
                                            amt=amount,
                                            rtu=rtu,
                                            ppi=ppi,
                                            re1=re1,
                                            cks=cks)
        if 'final_customer_wallet' in request.data:
            if request.data['final_customer_wallet'] < customer_wallet_obj.current_balance:
                payment_request_obj.is_wallet_selected = True
                payment_request_obj.wallet_balance_after_this_transaction = request.data['final_customer_wallet']
        payment_request_obj.save()

        # payement request PPI
        for parameter in ppi_parameter_list:
            payment_request_ppi = PaymentRequestPPI(payment_request=payment_request_obj,
                                                    key=parameter,
                                                    value=ppi_parameter_dict[parameter]
                                                    )
            payment_request_ppi.save()

        # link temp_salegroup with payment request
        temp_sale_group_payment_request_map = ICustomerSaleGroupPaymentRequestMap(payment_request_id=payment_request_obj.id)
        temp_sale_group_payment_request_map.save()
        for sale_group_id in temp_sale_group_list:
            temp_sale_group_payment_request_map.temp_sale_group.add(sale_group_id)
        temp_sale_group_payment_request_map.save()

        # payment_request_inditated
        payment_request_user_map = PaymentRequestUserMap(payment_request_id=payment_request_obj.id,
                                                        payment_intitated_by_id=request.user.id)
        payment_request_user_map.save()

        data_dict = {
            'encrypted_string': encrypted_string
        }
        if request.data['from'] == 'mobile':
            identificaiton_token_responce = requests.get('https://easypay.axisbank.co.in/api/generateToken')
            token_from_pg = identificaiton_token_responce.json()['token']
            data_dict['token'] = token_from_pg
        data_dict['is_online_enable'] = True
        transaction.savepoint_commit(sid)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def serve_booth_change_time_range(request):
    data_dict = {
        'from_time': None,
        'to_time': None
    }
    time_range_obj = CustomerOrderEditTimeRange.objects.filter()[0]
    data_dict['from_time'] = time_range_obj.from_time
    data_dict['to_time'] = time_range_obj.to_time
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def customer_card_preview(request):
    data_dict = generate_customer_card_after_order(request.data['customer_code'], request.data['month'],
                                                   request.data['year'])
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def confirm_mobile_verification(request):
    print(request.data)
    if 'mobile_number' in request.data:
        agent_obj = BusinessAgentMap.objects.get(business__user_profile__user_id=request.data['user_id']).agent
        agent_obj.is_mobile_number_verified_by_agent = True
        agent_obj.save()
        agent_profile_obj = AgentProfile.objects.get(id=agent_obj.agent_profile.id)
        agent_profile_obj.mobile = request.data['mobile_number']
        agent_profile_obj.save()
    else:
        if request.data['user_type_id'] == 3:
            icustomer_obj = ICustomer.objects.get(user_profile__user_id=request.data['user_id'])
            icustomer_obj.is_mobile_number_verified_by_customer = True
            icustomer_obj.save()
        else:
            agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=request.user).agent
            agent_obj.is_mobile_number_verified_by_agent = True
            agent_obj.save()
            print('agent_ works')
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def serve_nominee_and_bank_info_for_agent_update(request):
    print('recieved_data : ', request.data)
    agent = Agent.objects.get(agent_code=request.data['agent_code'])
    agent_bank = AgentBankDetail.objects.get(agent=agent)
    data_dict = {
        'agent_id': agent.id,
        'agent_profile_id': agent.agent_profile.id,
        'agent_first_name': agent.first_name,
        'agent_last_name': agent.last_name,
        'agent_gender_id': agent.agent_profile.gender_id,
        'agent_union_id': agent.agent_profile.union_id,
        'agent_street': agent.agent_profile.street,
        'agent_pincode': agent.agent_profile.pincode,
        'agent_state_id': agent.agent_profile.state_id,
        'agent_distict_id': agent.agent_profile.district_id,
        'agent_taluk_id': agent.agent_profile.taluk_id,
        'agent_communication_address': agent.communication_address,
        'agent_mobile': agent.agent_profile.mobile,
        'agent_alternate_mobile': agent.agent_profile.alternate_mobile,
        'agent_pan': agent.pan_number,
        'agent_ration_card_number': agent.ration_card_number,
        'agent_aadhar_number': agent.aadhar_number,
        'agent_bank': agent_bank.bank,
        'agent_branch': agent_bank.branch,
        'agent_ifsc_code': agent_bank.ifsc_code,
        'agent_micr_code': agent_bank.micr_code,
        'agent_account_holder_name': agent_bank.account_holder_name,
        'agent_account_number': agent_bank.account_number,
        'agent_gst_number':agent.agent_profile.gst_number,
    }
    # agent image

    try:
        user_profile_image_path = 'static/media/' + str(agent.agent_profile.image)
        with open(user_profile_image_path, 'rb') as image_file:
            user_profile_image_encoded_image = b64encode(image_file.read())
            data_dict['agent_image'] = user_profile_image_encoded_image
    except Exception as err:
        print(err)

    try:
        aadhar_document_image_path = 'static/media/' + str(agent.aadhar_document)
        with open(aadhar_document_image_path, 'rb') as image_file:
            aadhar_document_image_encoded_image = b64encode(image_file.read())
            data_dict['aadhar_document'] = aadhar_document_image_encoded_image
    except Exception as err:
        print(err)
    if BusinessAgentMap.objects.filter(agent=agent).exists():
        data_dict['business_codes'] = BusinessAgentMap.objects.filter(agent=agent).order_by(
            'business__code').values_list('business__code', flat=True)
        data_dict['business_linked'] = True
        business = Business.objects.get(code=data_dict['business_codes'][0])
        business_agent_map = BusinessAgentMap.objects.get(business=business)
        business_dict = {
            'business_id': business.id,
            'code': business.code,
            'name': business.name,
            'business_type_id': business.business_type_id,
            'zone_id': business.zone_id,
            'constituency_id': business.constituency_id,
            'ward_id': business.ward_id,
            'address': business.address,
            'landmark': business.landmark,
            'location_category_id': business.location_category_id,
            'location_category_value': business.location_category_value,
            'pincode': business.pincode,
            'urban': business.is_urban,
            'rural': business.is_rural,
            'nominee_first_name': business_agent_map.nominee.first_name,
            'nominee_last_name': business_agent_map.nominee.last_name,
            'nominee_relation_type_id': business_agent_map.nominee.relation_type_id,
            'nominee_aadhar_number': business_agent_map.nominee.aadhar_number,
            'nominee_phone': business_agent_map.nominee.phone,
            'deposit_date': business_agent_map.deposit_date,
            'deposit_amount': business_agent_map.deposit_amount,
        }

        try:
            deposit_receipt_image_path = 'static/media/' + str(business_agent_map.deposit_receipt_image)
            with open(deposit_receipt_image_path, 'rb') as image_file:
                deposit_receipt_image_encoded_image = b64encode(image_file.read())
                business_dict['deposit_receipt_image'] = deposit_receipt_image_encoded_image
        except Exception as err:
            print(err)

        try:
            nominee_image_path = 'static/media/' + str(business_agent_map.nominee.image)
            with open(nominee_image_path, 'rb') as image_file:
                nominee_image_encoded_image = b64encode(image_file.read())
                business_dict['nominee_image'] = nominee_image_encoded_image
        except Exception as err:
            print(err)
            business_dict['nominee_image'] = 'no_image'
        if RouteBusinessMap.objects.filter(business=business, route__session_id=1).exists():
            business_dict['morg_route_id'] = RouteBusinessMap.objects.get(business=business,
                                                                          route__session_id=1).route_id
        if RouteBusinessMap.objects.filter(business=business, route__session_id=2).exists():
            business_dict['eve_route_id'] = RouteBusinessMap.objects.get(business=business,
                                                                         route__session_id=2).route_id
    else:
        business_dict = {}
        data_dict['business_linked'] = False
    data_dict['business_data'] = business_dict
    return Response(data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_booth_details_for_update(request):
    print(request.data['booth_code'])
    business = Business.objects.get(code=request.data['booth_code'])
    business_agent_map = BusinessAgentMap.objects.get(business=business)
    business_dict = {
        'business_id': business.id,
        'code': business.code,
        'name': business.name,
        'business_type_id': business.business_type_id,
        'zone_id': business.zone_id,
        'constituency_id': business.constituency_id,
        'ward_id': business.ward_id,
        'address': business.address,
        'landmark': business.landmark,
        'location_category_id': business.location_category_id,
        'location_category_value': business.location_category_value,
        'pincode': business.pincode,
        'urban': business.is_urban,
        'rural': business.is_rural,
        'nominee_first_name': business_agent_map.nominee.first_name,
        'nominee_last_name': business_agent_map.nominee.last_name,
        'nominee_relation_type_id': business_agent_map.nominee.relation_type_id,
        'aadhar_number': business_agent_map.nominee.aadhar_number,
        'phone': business_agent_map.nominee.phone,
        'deposit_date': business_agent_map.deposit_date,
        'deposit_amount': business_agent_map.deposit_amount,
    }

    try:
        deposit_receipt_image_path = 'static/media/' + str(business_agent_map.deposit_receipt_image)
        with open(deposit_receipt_image_path, 'rb') as image_file:
            deposit_receipt_image_encoded_image = b64encode(image_file.read())
            business_dict['deposit_receipt_image'] = deposit_receipt_image_encoded_image
    except Exception as err:
        print(err)

    try:
        nominee_image_path = 'static/media/' + str(business_agent_map.nominee.image)
        with open(nominee_image_path, 'rb') as image_file:
            nominee_image_encoded_image = b64encode(image_file.read())
            business_dict['nominee_image'] = nominee_image_encoded_image
    except Exception as err:
        print(err)
        business_dict['nominee_image'] = 'no_image'
    if RouteBusinessMap.objects.filter(business=business, route__session_id=1).exists():
        business_dict['morg_route_id'] = RouteBusinessMap.objects.get(business=business, route__session_id=1).route_id
    if RouteBusinessMap.objects.filter(business=business, route__session_id=2).exists():
        business_dict['eve_route_id'] = RouteBusinessMap.objects.get(business=business, route__session_id=2).route_id

    return Response(business_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_individual_field_in_agent_booth(request):
    print('-----------------------')
    print(request.data)

    # first name
    if request.data['field'] == 'first_name':
        Agent.objects.filter(id=request.data['agent_id']).update(
            first_name=request.data['value']
        )

        print('success')
    # last name
    if request.data['field'] == 'last_name':
        Agent.objects.filter(id=request.data['agent_id']).update(
            last_name=request.data['value']
        )

        print('success')

    # agent_code
    elif request.data['field'] == 'agent_code':
        Agent.objects.filter(id=request.data['agent_id']).update(
            agent_code=request.data['value']
        )
        print('success')


    # communication_address
    elif request.data['field'] == 'communication_address':
        Agent.objects.filter(id=request.data['agent_id']).update(
            communication_address=request.data['value']
        )
        print('success')

    # gender
    elif request.data['field'] == 'gender_id':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            gender_id=request.data['value']
        )
        print('success')


    # union_id
    elif request.data['field'] == 'union_id':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            union_id=request.data['value']
        )
        print('success')

    # street
    elif request.data['field'] == 'street':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            street=request.data['value']
        )
        print('success')

    # pincode
    elif request.data['field'] == 'pincode':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            pincode=request.data['value']
        )
        print('success')

    # state_id
    elif request.data['field'] == 'state_id':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            state_id=request.data['value']
        )
        print('success')

    # district_id
    elif request.data['field'] == 'district_id':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            district_id=request.data['value']
        )
        print('success')

    # taluk_id
    elif request.data['field'] == 'taluk_id':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            taluk_id=request.data['value']
        )
        print('success')


    # mobile
    elif request.data['field'] == 'mobile':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            mobile=request.data['value']
        )
        print('success')

    # alternate_mobile
    elif request.data['field'] == 'alternate_mobile':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        AgentProfile.objects.filter(id=agent_profile_id).update(
            alternate_mobile=request.data['value']
        )
        print('success')


    # image
    elif request.data['field'] == 'agent_image':
        agent_profile_id = Agent.objects.get(id=request.data['agent_id']).agent_profile.id
        agent_profile_obj = AgentProfile.objects.get(id=agent_profile_id)
        try:
            if 'changingThisBreaksApplicationSecurity' in request.data['value']:
                agent_profile_obj.image = decode_image(request.data['value']['changingThisBreaksApplicationSecurity'])
            else:
                agent_profile_obj.image = decode_image(request.data['value'])
        except Exception as err:
            print(err)

        agent_profile_obj.save()
        print('success')

    # pan_number
    elif request.data['field'] == 'pan_number':
        Agent.objects.filter(id=request.data['agent_id']).update(
            pan_number=request.data['value']
        )
        print('success')

    # ration_card_number
    elif request.data['field'] == 'ration_card_number':
        Agent.objects.filter(id=request.data['agent_id']).update(
            ration_card_number=request.data['value']
        )
        print('success')


    # aadhar_number
    elif request.data['field'] == 'aadhar_number':
        Agent.objects.filter(id=request.data['agent_id']).update(
            aadhar_number=request.data['value']
        )
        print('success')

    # image
    elif request.data['field'] == 'aadhar_document':
        agent = Agent.objects.get(id=request.data['agent_id'])
        try:
            if 'changingThisBreaksApplicationSecurity' in request.data['value']:
                agent.aadhar_document = decode_image(request.data['value']['changingThisBreaksApplicationSecurity'])
            else:
                agent.aadhar_document = decode_image(request.data['value'])
        except Exception as err:
            print(err)
        agent.save()
        print('success')

    elif request.data['field'] == 'account_holder_name':
        AgentBankDetail.objects.filter(agent_id=request.data['agent_id']).update(
            account_holder_name=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'account_number':
        AgentBankDetail.objects.filter(agent_id=request.data['agent_id']).update(
            account_number=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'bank_name':
        AgentBankDetail.objects.filter(agent_id=request.data['agent_id']).update(
            bank=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'branch_name':
        AgentBankDetail.objects.filter(agent_id=request.data['agent_id']).update(
            branch=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'ifsc_code':
        AgentBankDetail.objects.filter(agent_id=request.data['agent_id']).update(
            ifsc_code=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'micr_code':
        AgentBankDetail.objects.filter(agent_id=request.data['agent_id']).update(
            micr_code=request.data['value']
        )
        print('success')
    if 'agent_id' in request.data:
        agent_obj = Agent.objects.get(id=request.data['agent_id'])
        agent_obj.modified_by_id = request.user.id
        agent_obj.save()

    if 'business_id' in request.data:
        business_obj = Business.objects.get(id=request.data['business_id'])
        business_obj.modified_by_id = request.user.id
        business_obj.save()

    # business
    if request.data['field'] == 'code':
        Business.objects.filter(id=request.data['business_id']).update(
            code=request.data['value']
        )
        print('success')

    # business name
    elif request.data['field'] == 'name':
        print('business name changing')
        Business.objects.filter(id=request.data['business_id']).update(
            name=request.data['value']
        )
        print('success')

    # business type
    elif request.data['field'] == 'business_type_id':
        Business.objects.filter(id=request.data['business_id']).update(
            business_type_id=request.data['value']
        )
        print('success')

    # business
    elif request.data['field'] == 'zone_id':
        Business.objects.filter(id=request.data['business_id']).update(
            zone_id=request.data['value']
        )
        print('success')

    # business name
    elif request.data['field'] == 'constituency_id':
        Business.objects.filter(id=request.data['business_id']).update(
            constituency_id=request.data['value']
        )
        print('success')

    # business type
    elif request.data['field'] == 'ward_id':
        Business.objects.filter(id=request.data['business_id']).update(
            ward_id=request.data['value']
        )
        print('success')

    # business name
    elif request.data['field'] == 'address':
        Business.objects.filter(id=request.data['business_id']).update(
            address=request.data['value']
        )
        print('success')

    # business type
    elif request.data['field'] == 'landmark':
        Business.objects.filter(id=request.data['business_id']).update(
            landmark=request.data['value']
        )
        print('success')

    # business type
    elif request.data['field'] == 'location_category_id':
        Business.objects.filter(id=request.data['business_id']).update(
            location_category_id=request.data['value']
        )
        print('success')

    # business name
    elif request.data['field'] == 'location_category_value':
        Business.objects.filter(id=request.data['business_id']).update(
            location_category_value=request.data['value']
        )
        print('success')


    # business name
    elif request.data['field'] == 'location_category_value':
        Business.objects.filter(id=request.data['business_id']).update(
            location_category_value=request.data['value']
        )
        print('success')

    # business type
    elif request.data['field'] == 'business_pincode':
        Business.objects.filter(id=request.data['business_id']).update(
            pincode=request.data['value']
        )
        print('success')


    # business type
    elif request.data['field'] == 'is_rural':
        business = Business.objects.get(id=request.data['business_id'])
        print('success')
        if request.data['value']:
            business.is_rural = True
            business.is_urban = False
        else:
            business.is_rural = False
            business.is_urban = True
        business.save()

    elif request.data['field'] == 'nominee_first_name':
        Nominee.objects.filter(
            id=BusinessAgentMap.objects.get(business_id=request.data['business_id']).nominee.id).update(
            first_name=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'nominee_last_name':
        Nominee.objects.filter(
            id=BusinessAgentMap.objects.get(business_id=request.data['business_id']).nominee.id).update(
            last_name=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'nominee_relation_type_id':
        Nominee.objects.filter(
            id=BusinessAgentMap.objects.get(business_id=request.data['business_id']).nominee.id).update(
            relation_type_id=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'nominee_aadhar_number':
        Nominee.objects.filter(
            id=BusinessAgentMap.objects.get(business_id=request.data['business_id']).nominee.id).update(
            aadhar_number=request.data['value']
        )
        print('success aadhar')
        print(Nominee.objects.get(
            id=BusinessAgentMap.objects.get(business_id=request.data['business_id']).nominee.id).aadhar_number)

    elif request.data['field'] == 'nominee_phone':
        Nominee.objects.filter(
            id=BusinessAgentMap.objects.get(business_id=request.data['business_id']).nominee.id).update(
            phone=request.data['value']
        )
        print('success')


    elif request.data['field'] == 'nominee_image':
        nominee_obj = Nominee.objects.get(
            id=BusinessAgentMap.objects.get(business_id=request.data['business_id']).nominee.id)
        try:
            if 'changingThisBreaksApplicationSecurity' in request.data['value']:
                nominee_obj.image = decode_image(request.data['value']['changingThisBreaksApplicationSecurity'])
            else:
                nominee_obj.image = decode_image(request.data['value'])
        except Exception as err:
            print(err)
        nominee_obj.save()
        print('success')

    elif request.data['field'] == 'deposit_date':
        BusinessAgentMap.objects.filter(business_id=request.data['business_id']).update(
            deposit_date=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'deposit_amount':
        BusinessAgentMap.objects.filter(business_id=request.data['business_id']).update(
            deposit_amount=request.data['value']
        )
        print('success')

    elif request.data['field'] == 'morg_route_id':
        if not RouteBusinessMap.objects.filter(route_id=request.data['value'],
                                               business_id=request.data['business_id']).exists():
            if RouteBusinessMap.objects.filter(business_id=request.data['business_id'], route__session_id=1).exists():
                morg_route_map_id = RouteBusinessMap.objects.get(business_id=request.data['business_id'],
                                                                 route__session_id=1).id
                morg_ordinal = RouteBusinessMap.objects.get(id=morg_route_map_id).ordinal
                morg_route = RouteBusinessMap.objects.get(id=morg_route_map_id).route.id
                morg_route_maps_ids = list(
                    RouteBusinessMap.objects.filter(route_id=morg_route, ordinal__gt=morg_ordinal).values_list('id',
                                                                                                               flat=True))

                for route_map_id in morg_route_maps_ids:
                    route_map_obj = RouteBusinessMap.objects.get(id=morg_route_map_id)
                    route_map_obj.ordinal = route_map_obj.mog_ordinal - 1
                    route_map_obj.save()
                RouteBusinessMap.objects.filter(id=morg_route_map_id).delete()
                morg_last_ordinal = \
                RouteBusinessMap.objects.filter(route_id=request.data['value']).order_by('-ordinal')[0].ordinal
                morg_route_map = RouteBusinessMap(
                    route_id=request.data['value'],
                    business_id=request.data['business_id'],
                    ordinal=morg_last_ordinal)
                morg_route_map.save()
            else:
                if request.data['value'] != None:
                    morg_last_ordinal = \
                    RouteBusinessMap.objects.filter(route_id=request.data['value']).order_by('-ordinal')[0].ordinal
                    morg_route_map = RouteBusinessMap(
                        route_id=request.data['value'],
                        business_id=request.data['business_id'],
                        ordinal=morg_last_ordinal)
                    morg_route_map.save()

    elif request.data['field'] == 'eve_route_id':
        # morg route business map
        if not RouteBusinessMap.objects.filter(route_id=request.data['value'],
                                               business_id=request.data['business_id']).exists():
            if RouteBusinessMap.objects.filter(business_id=request.data['business_id'], route__session_id=2).exists():
                eve_route_map_id = RouteBusinessMap.objects.get(business_id=request.data['business_id'],
                                                                route__session_id=2).id
                eve_ordinal = RouteBusinessMap.objects.get(id=eve_route_map_id).ordinal
                eve_route = RouteBusinessMap.objects.get(id=eve_route_map_id).route.id
                eve_route_maps_ids = list(
                    RouteBusinessMap.objects.filter(route_id=eve_route, ordinal__gt=eve_ordinal).values_list('id',
                                                                                                             flat=True))

                for route_map_id in eve_route_maps_ids:
                    route_map_obj = RouteBusinessMap.objects.get(id=eve_route_map_id)
                    route_map_obj.ordinal = route_map_obj.mog_ordinal - 1
                    route_map_obj.save()
                RouteBusinessMap.objects.filter(id=eve_route_map_id).delete()
                eve_last_ordinal = RouteBusinessMap.objects.filter(route_id=request.data['value']).order_by('-ordinal')[
                    0].ordinal
                eve_route_map = RouteBusinessMap(
                    route_id=request.data['value'],
                    business_id=request.data['business_id'],
                    ordinal=eve_last_ordinal)
                eve_route_map.save()
            else:
                if request.data['value'] != None:
                    eve_last_ordinal = \
                    RouteBusinessMap.objects.filter(route_id=request.data['value']).order_by('-ordinal')[0].ordinal
                    eve_route_map = RouteBusinessMap(
                        route_id=request.data['value'],
                        business_id=request.data['business_id'],
                        ordinal=eve_last_ordinal)
                    eve_route_map.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_sale_group_delele_log(request):
    sale_group_delete_obj = SaleGroupDeleteLog.objects.all().order_by('-id')
    sale_group_delete_list = list(
        sale_group_delete_obj.values_list('id', 'business__code', 'delivery_date', 'total_cost', 'session__name',
                                          'ordered_by__first_name', 'ordered_date_time', 'deleted_by__first_name',
                                          'delete_date_time'))
    sale_group_delete_column = ['id', 'business_code', 'delivery_date', 'total_cost', 'session_name', 'order_by',
                                'ordered_time', 'deleted_by', 'deleted_time']
    sale_group_delete_df = pd.DataFrame(sale_group_delete_list, columns=sale_group_delete_column)
    return Response(data=sale_group_delete_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_route_time_change_log(request):
    route_time_change_log_obj = RouteTimeChangeLog.objects.all().order_by('-id')
    route_time_change_log_list = list(
        route_time_change_log_obj.values_list('id', 'route', 'session__name', 'old_time', 'new_time',
                                              'changed_by__first_name', 'changed_at'))
    route_time_change_log_column = ['id', 'route_name', 'session_name', 'old_time', 'new_time', 'changed_by',
                                    'changed_at']
    route_time_change_log_df = pd.DataFrame(route_time_change_log_list, columns=route_time_change_log_column)
    return Response(data=route_time_change_log_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_route_business_change_log(request):
    route_business_change_log_obj = BusinessRouteChangeLog.objects.all().order_by('-id')
    route_business_change_log_list = list(
        route_business_change_log_obj.values_list('id', 'business__code', 'old_route__name', 'new_route__name',
                                                  'changed_by__first_name', 'changed_at', 'description'))
    route_business_change_log_column = ['id', 'business_code', 'old_route', 'new_route', 'changed_by', 'changed_at',
                                        'description']
    route_business_change_log_df = pd.DataFrame(route_business_change_log_list,
                                                columns=route_business_change_log_column)
    return Response(data=route_business_change_log_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_icustomer_business_change_log(request):
    icustomer_business_change_log_obj = ICustomerBusinessLog.objects.all().order_by('-id')
    icustomer_business_change_log_list = list(
        icustomer_business_change_log_obj.values_list('id', 'icustomer__customer_code',
                                                      'icustomer__user_profile__user__first_name', 'old_business__code',
                                                      'new_business__code', 'changed_by__first_name', 'changed_at'))
    icustomer_business_change_log_column = ['id', 'icustomer_code', 'icustomer_name', 'old_business_code',
                                            'new_business_code', 'changed_by', 'changed_at']
    icustomer_business_change_log_df = pd.DataFrame(icustomer_business_change_log_list,
                                                    columns=icustomer_business_change_log_column)
    return Response(data=icustomer_business_change_log_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def send_otp_to_mobile_number(request):
    print(request.data)
    user_obj = User.objects.get(id=request.data['user_id'])
    otp = generate_otp()
    print(otp)
    message = 'Your OTP for ' + str(request.data['for']) + ' ' + str(otp)
    purpose = 'To valid the user phone number'
    send_message_via_netfision(purpose, request.data['mobile_number'], message)
    TemporaryRegistration.objects.filter(mobile=request.data['mobile_number']).delete()
    temporary_register_obj = TemporaryRegistration(union_id=1,
                                                   first_name=user_obj.first_name,
                                                   last_name='customer',
                                                   mobile=request.data['mobile_number'],
                                                   otp=otp)
    temporary_register_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def confirm_otp_for_mobile_verification(request):
    print(request.data)
    otp = TemporaryRegistration.objects.filter(mobile=request.data['mobile_number'])[0].otp
    otp = int(otp)
    if request.data['otp'] == otp:
        if request.data['user_type_id'] == 3:
            icustomer_obj = ICustomer.objects.get(user_profile__user_id=request.data['user_id'])
            icustomer_obj.is_mobile_number_verified_by_customer = True
            icustomer_obj.save()
        else:
            agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=request.user).agent
            agent_obj.is_mobile_number_verified_by_agent = True
            agent_obj.save()
            agent_profile_obj = AgentProfile.objects.get(id=agent_obj.agent_profile.id)
            agent_profile_obj.mobile = request.data['mobile_number']
            agent_profile_obj.save()
        user_profile_obj = UserProfile.objects.get(user_id=request.data['user_id'])
        user_profile_obj.mobile = request.data['mobile_number']
        user_profile_obj.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def confirm_otp_for_password_change(request):
    print(request.data)
    otp = TemporaryRegistration.objects.filter(mobile=request.data['mobile_number'])[0].otp
    otp = int(otp)
    if request.data['otp'] == otp:
        print('Matched')
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def update_password_for_user(request):
    user_obj = User.objects.get(id=request.data['user_id'])
    user_obj.password = make_password(request.data['password'])
    user_obj.save()
    message = 'Dear ' + str(user_obj.first_name) + ' Your password has been changed to ' + str(request.data['password'])
    purpose = 'Confirmation Message'
    send_message_via_netfision(purpose, request.data['mobile'], message)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def confirm_otp_for_customer_verification(request):
    otp = TemporaryRegistration.objects.filter(mobile=request.data['mobile_number'])[0].otp
    otp = int(otp)
    if request.data['otp'] == otp:
        user_profile_obj = UserProfile.objects.get(user_id=request.data['user_id'])
        user_profile_obj.mobile = request.data['mobile_number']
        user_profile_obj.save()
        user_obj = User.objects.get(id=request.data['user_id'])
        password = generate_password()
        user_obj.password = make_password(password)
        user_obj.save()
        icustomer_obj = ICustomer.objects.get(user_profile__user_id=request.data['user_id'])
        icustomer_obj.is_mobile_number_verified_by_customer = True
        icustomer_obj.save()
        message = 'Dear ' + str(user_obj.first_name) + '(' + str(
            icustomer_obj.customer_code) + ')' + ' you have successfully set up an online account. ' + str(
            request.data['mobile_number']) + ' will be used for all communication. Your temporary password is  ' + str(
            password) + '. You can change it anytime on the order page.'
        purpose = 'Confirmation Message'
        send_message_via_netfision(purpose, request.data['mobile_number'], message)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
def update_kyc_for_icustomer(request):
    print(request.data)
    icustomer_obj = ICustomer.objects.get(user_profile__user_id=request.user.id)
    icustomer_obj.aadhar_number = request.data['aadhar_number']
    icustomer_obj.is_aadhar_number_verified_by_customer = True
    icustomer_obj.save()
    user_profile_obj = UserProfile.objects.get(id=icustomer_obj.user_profile.id)
    user_profile_obj.street = request.data['address']
    user_profile_obj.save()
    return Response(status=status.HTTP_200_OK)


def find_out_booth_or_customer_code(string):
    string = str(string)
    index = string.index('b')
    return string[index + 1:]


@api_view(['POST'])
def serve_payment_request_and_responce_details(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    payment_request_obj = PaymentRequest.objects.filter(time_created__date__gte=from_date,time_created__date__lte=to_date).order_by('-time_created')
    payment_request_list = list(
        payment_request_obj.values_list('id', 'rid', 'status__description', 'enquiry_response_status_latest__name',
                                        'time_modified', 'encrypted_string', 'decrypted_string',
                                        'payment_request_for__name', 'crn', 'ppi', 'cks', 'is_wallet_selected',
                                        'is_amount_returened_to_wallet', 'wallet_balance_after_this_transaction',
                                        'time_created', 'amt'))
    payment_request_column = ['id', 'rid', 'request_status_name', 'enquiry_response_status_latest',
                              'latest_enquiryed_time', 'request_encrypted_string', 'request_decrypted_string',
                              'payment_request_for', 'crn', 'ppi', 'cks', 'is_wallet_selected',
                              'is_amount_returened_to_wallet', 'wallet_balance_after_this_transaction',
                              'request_time_created', 'amt']
    payment_request_df = pd.DataFrame(payment_request_list, columns=payment_request_column)
    # responce
    payement_request_ids = list(
        PaymentRequest.objects.filter(time_created__date__gte=from_date, time_created__date__lte=to_date).values_list(
            'id', flat=True))
    payment_responce_obj = PaymentRequestResponse.objects.filter(payment_request_id__in=payement_request_ids)
    print(payment_responce_obj)
    payment_responce_list = list(
        payment_responce_obj.values_list('payment_request', 'status__name', 'is_enquired', 'encrypted_string',
                                         'decrypted_string', 'brn', 'trn', 'tet', 'pmd', 'stc', 'rmk', 'time_created'))
    payment_responce_column = ['payment_request', 'responce_status_name', 'is_enquired', 'responce_encrypted_string',
                               'responce_decrypted_string', 'brn', 'trn', 'tet', 'pmd', 'stc', 'rmk',
                               'responce_time_created']
    payment_responce_df = pd.DataFrame(payment_responce_list, columns=payment_responce_column)
    # requested user
    payment_request_user = PaymentRequestUserMap.objects.filter(payment_request_id__in=payement_request_ids)
    payment_request_user_list = list(
        payment_request_user.values_list('payment_request', 'payment_intitated_by', 'payment_intitated_by__first_name',
                                         'payment_intitated_by__last_name'))
    payment_request_user_column = ['request_map_request_id', 'user_id', 'first_name', 'last_name']
    payment_request_user_df = pd.DataFrame(payment_request_user_list, columns=payment_request_user_column)
    # merge user with request table
    payment_request_df = pd.merge(payment_request_df, payment_request_user_df, how='left', left_on='id',
                                  right_on='request_map_request_id')

    # merge request with responce
    final_df = pd.merge(payment_request_df, payment_responce_df, left_on='id', right_on='payment_request', how='left')
    if not final_df.empty:
        final_df['booth_or_customer_code'] = final_df.apply(lambda x: find_out_booth_or_customer_code(x['crn']), axis=1)

    final_df = final_df.fillna(0)
    return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def create_encryption_text_and_make_enquiry(request):
    payment_request_obj = PaymentRequest.objects.get(rid=request.data['rid'])
    is_response_available = False
    brn = None
    if PaymentRequestResponse.objects.filter(payment_request_id=payment_request_obj.id).exists():
        payment_responce_obj = PaymentRequestResponse.objects.get(payment_request_id=payment_request_obj.id)
        brn = payment_responce_obj.brn
        is_response_available = True
    # dict for filling white space in ACII method
    pad_text_dict = {
        0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07', 8: '\x08', 9: '\x09',
        10: '\x0a', 11: '\x0b', 12: '\x0c', 13: '\x0d', 14: '\x0e', 15: '\x0f', 16: '\x10'
    }
    ver = '1.0'  # version
    cid = 5648  # cid for aavin given by axis bank
    typ = 'PRD'  # test environment
    rid = payment_request_obj.rid  # random reference number
    crn = payment_request_obj.crn  # customer reference number
    key_before_sha_encrypt = '{}{}{}{}'.format(cid, rid, crn, checksum_key)
    cks = hashlib.sha256(key_before_sha_encrypt.encode()).hexdigest()
    if is_response_available:
        final_string = 'CID={}&RID={}&CRN={}&VER={}&TYP={}&BRN={}&CKS={}'.format(cid, rid, crn, ver, typ, brn, cks)
    else:
        final_string = 'CID={}&RID={}&CRN={}&VER={}&TYP={}&CKS={}'.format(cid, rid, crn, ver, typ, cks)
    print(final_string)
    obj = AES.new(encryption_key, AES.MODE_ECB, 'OPENSSL_RAW_DATA')
    pad_count = (16 - len(final_string) % 16)
    padded_text = final_string + (16 - len(final_string) % 16) * pad_text_dict[pad_count]
    cipertext = obj.encrypt(padded_text)
    cipertext = b64encode(cipertext).decode('utf-8')
    enquiry_request_obj = EnquiryRequest(rid=payment_request_obj.rid,
                                         status_id=1,  # requested
                                         encrypted_string=cipertext,
                                         decrypted_string=final_string,
                                         ver=ver,
                                         cid=cid,
                                         typ=typ,
                                         crn=crn,
                                         cks=cks,
                                         enquiry_make_by_id=request.user.id)
    if is_response_available:
        enquiry_request_obj.brn = brn
    enquiry_request_obj.save()
    response_return = requests.post('https://easypay.axisbank.co.in/index.php/api/enquiry', {'i': cipertext})
    encrypted_key_from_enquiry = response_return.text

    encrypted_key_from_enquiry = b64decode(encrypted_key_from_enquiry)
    decipher = AES.new(encryption_key, AES.MODE_ECB)
    decrypted_text = decipher.decrypt(encrypted_key_from_enquiry).decode("utf-8")
    print(decrypted_text)
    # split plain text by &
    splited_string = decrypted_text.split('&')

    # status code with ids
    transaction_status_obj = PaymentTransactionStatus.objects.all()
    transaction_status_list = list(transaction_status_obj.values_list('id', 'name', 'code'))
    transaction_status_column = ['id', 'name', 'code']
    transaction_status_df = pd.DataFrame(transaction_status_list, columns=transaction_status_column)
    transaction_status_dict = transaction_status_df.groupby('code').apply(lambda x: x.to_dict('r')[0]).to_dict()

    # create dict for key and respected value
    decrypted_string_and_value = {
        'BRN': None,
        'STC': None,
        'RMK': None,
        'TRN': None,
        'TET': None,
        'PMD': None,
        'RID': None,
        'VER': None,
        'CID': None,
        'TYP': None,
        'CRN': None,
        'CNY': None,
        'AMT': None,
        'CKS': None,
    }

    # store the parameters in dict for update payemnt responce table
    for string in splited_string:
        temp_split = string.split('=')
        decrypted_string_and_value[temp_split[0]] = temp_split[1]

    # # create enquiry responce obj
    # transaction_date_time_in_format = transaction_date_time_in_format.astimezone(indian)
    if decrypted_string_and_value['TRN'] == '':
        decrypted_string_and_value['TRN'] = decrypted_string_and_value['RID'] + '_cancelled'
    if decrypted_string_and_value['TET'] == '':
        transaction_date_time_in_format = datetime.datetime.now()
    else:
        transaction_date_time_in_format = datetime.datetime.strptime(decrypted_string_and_value['TET'],
                                                                     '%Y/%m/%d %H:%M:%S %p')
    if decrypted_string_and_value['AMT'] == '':
        decrypted_string_and_value['AMT'] = 0
    if decrypted_string_and_value['PMD'] == '':
        decrypted_string_and_value['PMD'] = ' '
    if decrypted_string_and_value['CNY'] == '':
        decrypted_string_and_value['CNY'] = ' '
    enquiry_responce_obj = EnquiryRequestResponse(enquiry_request_id=enquiry_request_obj.id,
                                                  rid=decrypted_string_and_value['RID'],
                                                  status_id=transaction_status_dict[decrypted_string_and_value['STC']][
                                                      'id'],
                                                  encrypted_string=str(encrypted_key_from_enquiry),
                                                  decrypted_string=decrypted_text,
                                                  brn=decrypted_string_and_value['BRN'],
                                                  trn=decrypted_string_and_value['TRN'],
                                                  tet=transaction_date_time_in_format,
                                                  pmd=decrypted_string_and_value['PMD'],
                                                  stc=decrypted_string_and_value['STC'],
                                                  rmk=decrypted_string_and_value['RMK'],
                                                  ver=decrypted_string_and_value['VER'],
                                                  cid=decrypted_string_and_value['CID'],
                                                  typ=decrypted_string_and_value['TYP'],
                                                  crn=decrypted_string_and_value['CRN'],
                                                  cny=decrypted_string_and_value['CNY'],
                                                  amt=decrypted_string_and_value['AMT'],
                                                  cks=decrypted_string_and_value['CKS'])

    enquiry_responce_obj.save()
    payment_request_obj.enquiry_response_status_latest_id = transaction_status_dict[decrypted_string_and_value['STC']][
        'id']
    payment_request_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_enquiry_request_log(request):
    rid = request.data['rid']
    enquiry_request_obj = EnquiryRequest.objects.filter(rid=rid)
    enquiry_request_list = list(
        enquiry_request_obj.values_list('id', 'rid', 'status__description', 'encrypted_string', 'decrypted_string',
                                        'crn', 'brn', 'cks', 'enquiry_make_by__first_name',
                                        'enquiry_make_by__last_name', 'time_created'))
    enquiry_request_column = ['id', 'rid', 'request_status_name', 'request_encrypted_string',
                              'request_decrypted_string', 'request_crn', 'request_brn', 'cks', 'first_name',
                              'last_name', 'request_time_created']
    enquiry_request_df = pd.DataFrame(enquiry_request_list, columns=enquiry_request_column)

    enquiry_request_ids = list(EnquiryRequest.objects.filter(rid=rid).values_list('id', flat=True))
    enquiry_response_obj = EnquiryRequestResponse.objects.filter(enquiry_request_id__in=enquiry_request_ids)
    enquiry_response_list = list(
        enquiry_response_obj.values_list('enquiry_request', 'status__name', 'encrypted_string', 'decrypted_string',
                                         'brn', 'trn', 'tet', 'pmd', 'crn', 'amt', 'time_created'))
    enquiry_response_column = ['enquiry_request_id', 'responce_status_name', 'responce_encrypted_string',
                               'responce_decrypted_string', 'responce_brn', 'trn', 'tet', 'pmd', 'responce_crn', 'amt',
                               'responce_time_created']
    enquiry_response_df = pd.DataFrame(enquiry_response_list, columns=enquiry_response_column)
    final_df = pd.merge(enquiry_request_df, enquiry_response_df, left_on='id', right_on='enquiry_request_id',
                        how='left')
    if not final_df.empty:
        final_df['booth_or_customer_code'] = final_df.apply(lambda x: find_out_booth_or_customer_code(x['request_crn']),
                                                            axis=1)
    final_df = final_df.fillna(0)

    return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_user_manual(request):
    data_dict = {}
    data_dict['is_data_available'] = False
    data_dict['pdf_data'] = None
    if request.data['selected_manual'] == 'existing_customer':
        try:
            image_path = 'static/media/manual/existing_card_customer.pdf'
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                data_dict['pdf_data'] = encoded_image
                data_dict['is_data_available'] = True
        except Exception as err:
            print(err)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    elif request.data['selected_manual'] == 'new_customer':
        try:
            image_path = 'static/media/manual/new_card_customer.pdf'
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                data_dict['pdf_data'] = encoded_image
                data_dict['is_data_available'] = True
        except Exception as err:
            print(err)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    elif request.data['selected_manual'] == 'agent':
        try:
            image_path = 'static/media/manual/agent.pdf'
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                data_dict['pdf_data'] = encoded_image
                data_dict['is_data_available'] = True
        except Exception as err:
            print(err)
        return Response(data=data_dict, status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['POST'])
def create_encryption_text_and_make_request_for_mobile(request):
    # save order in temp salegroup
    sid = transaction.savepoint()
    try:
        if request.data['from'] == 'mobile':
            via_id = 1
        else:
            via_id = 3
        if PaymentGatewayConfiguration.objects.filter(ordered_via_id=via_id).exists():
            online_payment_configuration_obj = PaymentGatewayConfiguration.objects.get(ordered_via_id=via_id)
            if online_payment_configuration_obj.is_enable == False:
                data_dict = {
                    'is_online_enable': False,
                    'alert_text': online_payment_configuration_obj.alert_message
                }
                return Response(data=data_dict, status=status.HTTP_200_OK)
        user_profile_id = request.user.userprofile.id
        business_id = Business.objects.get(user_profile_id=user_profile_id).id
        agent_user_id = Business.objects.get(id=business_id).user_profile.user.id
        agent_id = BusinessAgentMap.objects.get(business_id=business_id).agent_id
        business_type_id = Business.objects.get(id=business_id).business_type.id

        business_obj = Business.objects.get(id=business_id)
        data_dict = serve_product_and_session_list(user_profile_id)
        session_list = data_dict['session_list']
        product_list = data_dict['product_list']
        product_quantity_variation_list = data_dict['product_quantity_variation_list']
        product_form_details = request.data['product_form_details']
        agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
        temp_wallet_amount = agent_wallet_obj.current_balance
        product_shot_name_for_transaction = ''
        temp_sale_group_list = []
        overall_total_cost = 0
        for date in request.data['order_date']:
            for session in session_list:
                total_cost_per_session = 0
                route_id = RouteBusinessMap.objects.get(business_id=business_id,
                                                        route__session_id=session['id']).route_id
                print(route_id)
                if product_form_details[date]['total_price_per_session'][str(session['id'])] != 0:
                    temp_sale_group_obj = TempSaleGroup(
                        business_id=business_id,
                        business_type_id=business_type_id,
                        date=date,
                        session_id=session['id'],
                        ordered_via_id=via_id,
                        payment_status_id=1,  # paid m
                        sale_status_id=1,  # ordered
                        total_cost=0,
                        ordered_by=request.user,
                        modified_by=request.user,
                        product_amount=0,
                        route_id=route_id,
                        zone_id=business_obj.zone.id
                    )
                    temp_sale_group_obj.save()
                    # print('sale group saved')
                    for product in product_list:
                        product_quantity = \
                        product_form_details[date]['product'][str(session['id'])][str(product['product_id'])]['quantity']
                        if product_quantity != 0 and product_quantity != None:
                            if product['product_group_id'] == 3:
                                for variation_price in product_quantity_variation_list[product['product_id']]:
                                    if product_quantity >= variation_price['min_quantity'] and product_quantity <= \
                                            variation_price['max_quantity']:
                                        product_cost = product_quantity * variation_price['mrp']
                            else:
                                product_cost = product_quantity * product['product_mrp']
                            sale_obj = TempSale(
                                temp_sale_group_id=temp_sale_group_obj.id,
                                product_id=product['product_id'],
                                count=product_quantity,
                                cost=product_cost,
                                ordered_by=request.user,
                                modified_by=request.user
                            )
                            sale_obj.save()
                            product_shot_name_for_transaction = product_shot_name_for_transaction + product[
                                'product_short_name'] + ','
                            # print('new sale created')
                            total_cost_per_session += product_cost
                    saved_temp_sale_group_obj = TempSaleGroup.objects.get(id=temp_sale_group_obj.id)
                    saved_temp_sale_group_obj.total_cost = total_cost_per_session
                    saved_temp_sale_group_obj.product_amount = total_cost_per_session
                    overall_total_cost += total_cost_per_session
                    credit_business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(payment_option_id=2, order_category_id=1).values_list('business_type_id', flat=True))

                    if business_type_id in credit_business_type_ids:
                        if temp_wallet_amount >= 0:
                            temp_wallet_amount = temp_wallet_amount - total_cost_per_session
                            if temp_wallet_amount >= 0:
                                saved_temp_sale_group_obj.payment_status_id = 1  # Paid
                            else:
                                saved_temp_sale_group_obj.payment_status_id = 2  # partically paid
                        else:
                            saved_temp_sale_group_obj.payment_status_id = 3  # Not paid
                    saved_temp_sale_group_obj.save()
                    temp_sale_group_list.append(saved_temp_sale_group_obj.id)
                    if product_form_details[date]['total_price_per_session'][str(session['id'])] == total_cost_per_session:
                        print('session price is equal')
                    else:
                        print('session price not equal')
        rid = generate_rid_code()
        if request.data['final_price'] != 0:
            transaction_obj = TransactionLog(
                date=datetime.datetime.now(),
                transacted_by_id=agent_user_id,
                transacted_via_id=via_id,
                data_entered_by=request.user,
                amount=request.data['final_price'],
                transaction_direction_id=1,  # from agent to aavin
                transaction_mode_id=1,  # Upi
                transaction_id=rid,
                transaction_status_id=1,  # completed
                transaction_approval_status_id=1,  # Accepted
                transaction_approved_by_id=1,
                transaction_approved_time=datetime.datetime.now(),
                wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                description='Amount for ordering the product',
                modified_by=request.user
            )
            transaction_obj.save()

        # dict for filling white space in ACII method
        pad_text_dict = {
            0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07', 8: '\x08', 9: '\x09',
            10: '\x0a', 11: '\x0b', 12: '\x0c', 13: '\x0d', 14: '\x0e', 15: '\x0f', 16: '\x10'
        }

        ppi_parameter_list = ['transaction_id', 'transaction_pkey', 'salegroup_id', 'booth_code', 'customer_code',
                            'product_list', 'user_code', 'device_type', 'amount']
        ppi_parameter_dict = {'transaction_id': '', 'transaction_pkey': '', 'salegroup_id': '', 'booth_code': '',
                            'customer_code': '', 'product_list': '', 'user_code': '', 'device_type': '', 'amount': ''}

        # PPI parameters
        ppi_parameter_dict['transaction_id'] = rid
        ppi_parameter_dict['transaction_pkey'] = transaction_obj.id
        ppi_parameter_dict['salegroup_id'] = temp_sale_group_list[0]
        ppi_parameter_dict['product_list'] = product_shot_name_for_transaction[:50]
        ppi_parameter_dict['user_code'] = request.user.id
        ppi_parameter_dict['device_type'] = request.data['from']
        ppi_parameter_dict['amount'] = round(request.data['final_price'], 2)
        print(ppi_parameter_dict['amount'])

        # parameters for encryption
        booth_or_customer_code = business_obj.code
        ppi_parameter_dict['booth_code'] = booth_or_customer_code
        ppi_parameter_dict['customer_code'] = booth_or_customer_code
        ver = '1.0'  # version
        # cid = 5494 # cid for aavin given by axis bank
        typ = 'PRD'  # test environment
        cid = 5648  # cid for aavin given by axis bank
        rid = rid  # generated reference number
        crn = rid + 'b' + booth_or_customer_code  # customer reference number
        cny = 'INR'
        amount = ppi_parameter_dict['amount']
        rtu = 'http://pay.aavincoimbatore.com/main/payment/response/'  # reponse will returned to this uRL
        ppi = '{}|{}|{}|{}|{}|{}|{}|{}|{}|'.format(ppi_parameter_dict['transaction_id'],
                                                ppi_parameter_dict['transaction_pkey'],
                                                ppi_parameter_dict['salegroup_id'], ppi_parameter_dict['booth_code'],
                                                ppi_parameter_dict['customer_code'], ppi_parameter_dict['product_list'],
                                                ppi_parameter_dict['user_code'], ppi_parameter_dict['device_type'],
                                                ppi_parameter_dict['amount'])  # ppi parameters for display on interface
        re1 = 'MN'

        # need to encrypt cid, rid, crn, amt and checksum in Sha256
        key_before_sha_encrypt = '{}{}{}{}{}'.format(cid, rid, crn, amount, checksum_key)
        cks = hashlib.sha256(key_before_sha_encrypt.encode()).hexdigest()
        plain_string = 'CID={}&RID={}&CRN={}&AMT={}&VER={}&TYP={}&CNY={}&RTU={}&PPI={}&RE1=&RE2=&RE3=&RE4=&RE5=&CKS={}'.format(
            cid, rid, crn, amount, ver, typ, cny, rtu, ppi, cks)

        # AES encryption
        obj = AES.new(encryption_key, AES.MODE_ECB, 'OPENSSL_RAW_DATA')
        pad_count = (16 - len(plain_string) % 16)
        padded_text = plain_string + (16 - len(plain_string) % 16) * pad_text_dict[pad_count]
        cipertext = obj.encrypt(padded_text)
        encrypted_string = b64encode(cipertext).decode('utf-8')
        payment_request_obj = PaymentRequest(rid=rid,
                                            status_id=1,
                                            payment_request_for_id=1,
                                            encrypted_string=encrypted_string,
                                            decrypted_string=plain_string,
                                            ordered_via_id=via_id,
                                            ver=ver,
                                            cid=cid,
                                            typ=typ,
                                            crn=crn,
                                            cny=cny,
                                            amt=amount,
                                            rtu=rtu,
                                            ppi=ppi,
                                            re1=re1,
                                            cks=cks)
        if request.data['final_customer_wallet'] < agent_wallet_obj.current_balance:
            payment_request_obj.is_wallet_selected = True
            payment_request_obj.wallet_balance_after_this_transaction = request.data['final_customer_wallet']
        payment_request_obj.save()

        # payement request PPI
        for parameter in ppi_parameter_list:
            payment_request_ppi = PaymentRequestPPI(payment_request=payment_request_obj,
                                                    key=parameter,
                                                    value=ppi_parameter_dict[parameter]
                                                    )
            payment_request_ppi.save()

        # link temp_salegroup with payment request
        temp_sale_group_payment_request_map = SaleGroupPaymentRequestMap(payment_request_id=payment_request_obj.id)
        temp_sale_group_payment_request_map.save()
        for sale_group_id in temp_sale_group_list:
            temp_sale_group_payment_request_map.temp_sale_group.add(sale_group_id)
        temp_sale_group_payment_request_map.save()

        # payment_request_inditated
        payment_request_user_map = PaymentRequestUserMap(payment_request_id=payment_request_obj.id,
                                                        payment_intitated_by_id=request.user.id)
        payment_request_user_map.save()
        identificaiton_token_responce = requests.get('https://easypay.axisbank.co.in/api/generateToken')
        token_from_pg = identificaiton_token_responce.json()['token']
        data_dict = {
            'encrypted_string': encrypted_string,
            'token': token_from_pg,
            'is_online_enable': True
        }
        transaction.savepoint_commit(sid)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_edit_order_permission(request):
    print(request.data)
    data_dict = {}
    if request.data['from'] == 'portal':
        business_code = request.data['business_code']
    elif request.data['from'] == 'website' or request.data['from'] == 'mobile':
        business_code = Business.objects.get(user_profile__user_id=request.user.id).code
    sale_group_obj = SaleGroup.objects.filter(date=request.data['selected_date'], business__code=business_code)[0]
    if request.user.id == sale_group_obj.ordered_by.id:
        data_dict['permission_available'] = True
    else:
        data_dict['permission_available'] = False
    if Employee.objects.filter(user_profile__user_id=request.user.id).exists():
        employee_obj = Employee.objects.get(user_profile__user_id=request.user.id)
        if employee_obj.role_id == 2:
            data_dict['permission_available'] = True
    data_dict['ordered_person_firstname'] = sale_group_obj.ordered_by.first_name
    data_dict['business_type_id'] = Business.objects.get(code=business_code).business_type.id
    return Response(data=data_dict, status=status.HTTP_200_OK)


def get_payment_request_user_first_name(payment_request_id):
    payment_request_obj = PaymentRequest.objects.get(id=payment_request_id)
    user_id = PaymentRequestUserMap.objects.get(payment_request_id=payment_request_id).payment_intitated_by.id
    return str(User.objects.get(id=user_id).first_name)




def get_payment_request_user_booth_or_customer_code(payment_request_id):
    payment_request_obj = PaymentRequest.objects.get(id=payment_request_id)
    user_id = PaymentRequestUserMap.objects.get(payment_request_id=payment_request_id).payment_intitated_by.id
    if payment_request_obj.payment_request_for.id in [1,2]:
        business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user_id=user_id)
        return str(business_agent_obj.business.code)
    else:
        icustomer_obj = ICustomer.objects.get(user_profile__user_id=user_id)
        return str(icustomer_obj.customer_code)


def check_order_placed(sale_group_id):
    if sale_group_id == 0:
        return 'No'
    else:
        return 'Yes'


@api_view(['POST'])
def serve_auto_enquiry_log(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    payment_auto_enquiry_obj = PaymentAutoEnquiry.objects.filter(run_time__date__gte=from_date,
                                                                 run_time__date__lte=to_date,
                                                                 candidate_count__gt=0).order_by('-time_created')
    payment_auto_enquiry_list = list(
        payment_auto_enquiry_obj.values_list('id', 'run_time', 'run_interval_start', 'run_interval_end', 'run_type',
                                             'candidate_count', 'success_count'))
    payment_auto_enquiry_column = ['id', 'run_time', 'start_time', 'end_time', 'run_type', 'candidate_count',
                                   'success_count']
    payment_auto_enquiry_df = pd.DataFrame(payment_auto_enquiry_list, columns=payment_auto_enquiry_column)
    payment_auto_enquiry_data = payment_auto_enquiry_df.to_dict('r')

    #     payment auto enquiry property log
    payment_auto_enquiry_ids = list(
        PaymentAutoEnquiry.objects.filter(run_time__date__gte=from_date, run_time__date__lte=to_date,
                                          candidate_count__gt=0).values_list('id',
                                                                             flat=True))

    payment_auto_enquiry_property_obj = PaymentAutoEnquiryProperty.objects.filter(
        payment_auto_enquiry_id__in=payment_auto_enquiry_ids)
    payment_auto_enquiry_property_list = list(
        payment_auto_enquiry_property_obj.values_list('id', 'payment_auto_enquiry', 'payment_request',
                                                      'payment_request__time_created',
                                                      'amount_sent_to_wallet', 'is_order_placed', 'morning_sale_group',
                                                      'morning_order_amount', 'evening_sale_group',
                                                      'evening_order_amount'))
    payment_auto_enquiry_property_column = ['id', 'payment_auto_enquiry', 'payment_request', 'payment_requested_time',
                                            'amount_sent_to_wallet',
                                            'is_order_placed', 'morning_sale_group', 'morning_order_amount',
                                            'evening_sale_group', 'evening_order_amount']
    payment_auto_enquiry_property_df = pd.DataFrame(payment_auto_enquiry_property_list,
                                                    columns=payment_auto_enquiry_property_column)
    payment_auto_enquiry_property_df = payment_auto_enquiry_property_df.fillna(0)

    if not payment_auto_enquiry_property_df.empty:
        payment_auto_enquiry_property_df['first_name'] = payment_auto_enquiry_property_df.apply(
            lambda x: get_payment_request_user_first_name(x['payment_request']), axis=1)
        payment_auto_enquiry_property_df['booth_code'] = payment_auto_enquiry_property_df.apply(
            lambda x: get_payment_request_user_booth_or_customer_code(x['payment_request']), axis=1)
        payment_auto_enquiry_property_df['is_mor_order_placed'] = payment_auto_enquiry_property_df.apply(
            lambda x: check_order_placed(x['morning_sale_group']), axis=1)
        payment_auto_enquiry_property_df['is_eve_order_placed'] = payment_auto_enquiry_property_df.apply(
            lambda x: check_order_placed(x['evening_sale_group']), axis=1)
    payment_auto_enquiry_property_data = payment_auto_enquiry_property_df.groupby('payment_auto_enquiry').apply(
        lambda x: x.to_dict('r')).to_dict()
    data_dict = {
        'enquiry_log': payment_auto_enquiry_data,
        'enquiry_property': payment_auto_enquiry_property_data
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_icustomer_details_for_edit(request):
    icustomer_obj = ICustomer.objects.get(id=request.data['icustomer_id'])
    data_dict = {
        'first_name': icustomer_obj.user_profile.user.first_name,
        'last_name': icustomer_obj.user_profile.user.last_name,
        'mobile': icustomer_obj.user_profile.mobile
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_icustomer_details(request):
    print(request.data)
    form_data = request.data['form_data']
    icustomer_obj = ICustomer.objects.get(id=request.data['icustomer_id'])
    icustomer_obj.user_profile.user.first_name = form_data['first_name']
    icustomer_obj.user_profile.user.last_name = form_data['last_name']
    icustomer_obj.user_profile.user.save()
    icustomer_obj.user_profile.mobile = form_data['mobile']
    icustomer_obj.user_profile.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_years_list_for_comparision_five(request):
    year = datetime.datetime.today().year
    data = [year - i for i in range(6)]
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_from_time_for_booth_change(request):
    data_dict = {
        'from_time': 10
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_current_date(request):
    indian = pytz.timezone('Asia/Kolkata')
    current_date = datetime.datetime.now().astimezone(indian)
    return Response(data=current_date, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
def app_version_check(request):
    """
    app version check
    """
    version = '0.0.11'
    relogin = True
    data = {'version': version, 'relogin': relogin}
    return Response(data)


@api_view(['GET'])
@permission_classes((AllowAny,))
def serve_customer_support_mobile_number(request):
    data_dict = {
        'mobile_number': 9489043716
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_indent_staus(request):
    print(request.data)
    business_code = request.data['business_code']
    order_date = request.data['order_date']
    session_list = request.data['session_list']
    indent_status = True
    for session_id in session_list:
        if RouteTrace.objects.filter(date=order_date, route__routebusinessmap__business__code=business_code,
                                     session_id=session_id).exists():
            route_trace_obj = RouteTrace.objects.get(date=order_date,
                                                     route__routebusinessmap__business__code=business_code,
                                                     session_id=session_id)
            if session_id == 1:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
                    break
            else:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
    return Response(data=indent_status, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_indent_status_for_online(request):
    print(request.data)
    business_code = Business.objects.get(user_profile__user=request.user).code
    order_date = request.data['order_date']
    session_list = request.data['session_list']
    indent_status = True
    for session_id in session_list:
        if RouteTrace.objects.filter(date=order_date, route__routebusinessmap__business__code=business_code,
                                     session_id=session_id).exists():
            route_trace_obj = RouteTrace.objects.get(date=order_date,
                                                     route__routebusinessmap__business__code=business_code,
                                                     session_id=session_id)
            if session_id == 1:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
                    break
            else:
                if route_trace_obj.indent_status_id == 3:
                    indent_status = False
    return Response(data=indent_status, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_next_month_order_is_available_for_customer(request):
    next_month_date = date.today().replace(day=1) + timedelta(days=32)
    next_month = next_month_date.month
    next_year = next_month_date.year
    is_order_availble = False
    if ICustomerSaleGroup.objects.filter(date__month=next_month, date__year=next_year,
                                         icustomer__user_profile__user_id=request.user.id).exists():
        is_order_availble = True
        icustomer_sale_obj = ICustomerSaleGroup.objects.filter(date__month=next_month, date__year=next_year,
                                                               icustomer__user_profile__user_id=request.user.id)[0]
    data_dict = {
        'is_order_placed': is_order_availble,
    }
    if is_order_availble:
        data_dict['order_placed_on'] = icustomer_sale_obj.time_created
        data_dict['next_month_in_string'] = month_name[next_month]
        if next_month == 12:
            next_month = 1
        else:
            next_month += 1
        data_dict['order_month_in_string'] = month_name[next_month]
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_next_month_order_is_available_for_customer_portal(request):
    next_month_date = date.today().replace(day=1) + timedelta(days=32)
    next_month = next_month_date.month
    next_year = next_month_date.year
    is_order_availble = False
    if ICustomerSaleGroup.objects.filter(date__month=next_month, date__year=next_year,
                                         icustomer__customer_code__iexact=request.data['customer_code']).exists():
        is_order_availble = True
        icustomer_sale_obj = ICustomerSaleGroup.objects.filter(date__month=next_month, date__year=next_year,
                                                               icustomer__customer_code__iexact=request.data['customer_code'])[
            0]
    data_dict = {
        'is_order_placed': is_order_availble,
    }
    if is_order_availble:
        data_dict['order_placed_on'] = icustomer_sale_obj.time_created
        data_dict['next_month_in_string'] = month_name[next_month]
        if next_month == 12:
            next_month = 1
        else:
            next_month += 1
        data_dict['order_month_in_string'] = month_name[next_month]
        print(data_dict)
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(["GET"])
def serve_product_list_for_employee(request):
    product_values = list(Product.objects.filter(id__in=[1, 2]).values('short_name', 'id'))
    print(product_values)
    return Response(data=product_values, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_employee_last_order_details(request):
    print(request.data)
    customer_type = request.data['employee_id']
    today = date.today()
    next_month_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    month = request.data['month']
    year = request.data['year']
    customer_next_month_order_placed_list = list(set(list(
        ICustomerSaleGroup.objects.filter(icustomer__customer_type_id=customer_type, date__month=next_month_date.month,
                                          date__year=next_month_date.year).values_list('icustomer_id', flat=True))))
    customer_order_not_placed_list = list(set(list(
        ICustomerSaleGroup.objects.filter(icustomer__customer_type_id=customer_type, date__month=month,
                                          date__year=year).exclude(
            icustomer_id__in=customer_next_month_order_placed_list).values_list('icustomer_id', flat=True))))
    if customer_order_not_placed_list:
        employee_order_obj = ICustomerSaleGroup.objects.filter(icustomer_id__in=customer_order_not_placed_list,
                                                               date__month=month, date__year=year)
        employee_order_list = employee_order_obj.values_list('icustomer__customer_code',
                                                             'icustomer__user_profile__user__first_name',
                                                             'icustomer__union_for_icustomer__name',
                                                             'icustomer__business__code',
                                                             'icustomersale__product__short_name',
                                                             'icustomersale__count')
        employee_order_column = ['employee_code', 'name', 'union', 'booth_code', 'product', 'quantity']
        employee_order_df = pd.DataFrame(employee_order_list, columns=employee_order_column)
        employee_order_dict = employee_order_df.to_dict('r')
        data_dict = {
            'employee_order_dict': employee_order_dict,
            'order_status': False
        }
    else:
        data_dict = {
            'order_status': True,
            'month': next_month_date.month,
            'year': next_month_date.year,
            'content': f'Order for month {calendar.month_name[next_month_date.month]}, {next_month_date.year} is alresdy placed .'
        }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def place_employee_order(request):
    print(request.data)
    order_list = request.data['employee_order_list']
    customer_type_id = request.data['customer_type_id']
    today = date.today()
    next_month_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

    # ----------------EmployeeMonthlyOrderLog-------------------#
    icustomer_type_obj = ICustomerType.objects.get(id=customer_type_id)
    employee_order_log_obj = EmployeeMonthlyOrderLog(order_for=icustomer_type_obj, order_for_date=next_month_date,
                                                     time_statrted=datetime.datetime.now(), ordered_by=request.user)
    employee_order_log_obj.save()
    # -----------------------------------------------------------#

    missing_list = []
    missind_customer_list = []
    start_date = next_month_date
    month = start_date.month
    year = start_date.year
    day_count = monthrange(year, month)[1]
    session_id = 1

    employee_order_df = pd.DataFrame(order_list)

    employee_order_df = employee_order_df.reindex(
        columns=['booth_code', 'employee_code', 'name', 'product', 'quantity'])

    employee_booth_df = employee_order_df.groupby(['employee_code', 'name']).agg({'booth_code': 'sum'}).reset_index()

    employee_order_df = employee_order_df.groupby(['booth_code', 'employee_code', 'product']).agg({'quantity': 'sum'})

    # convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
    employee_order_df = pd.pivot_table(employee_order_df, index='employee_code', columns='product', aggfunc=min,
                                       fill_value=0)

    # convert_pivot_table_to_normal_df
    employee_order_df.columns = employee_order_df.columns.droplevel(0)  # remove amount
    employee_order_df.columns.name = None  # remove categories
    employee_order_df = employee_order_df.reset_index()  # index to columns
    employee_order_df

    df = pd.merge(employee_booth_df, employee_order_df, left_on='employee_code', right_on='employee_code', how='left')
    df = df.rename(columns={'employee_code': 'CODE', 'name': 'NAME', 'booth_code': 'POINT'})
    df['Total'] = df.iloc[:, 3:].sum(axis=1)

    product_obj = ICustomerTypeWiseProductDiscount.objects.filter(customer_type_id=customer_type_id,
                                                                  product__is_active=True).order_by(
        'product__display_ordinal')
    product_obj_list = list(
        product_obj.values_list('product_id', 'product__group', 'product__group__name',
                                'product__name', 'product__short_name', 'product__code',
                                'product__unit',
                                'product__unit__display_name', 'product__description',
                                'product__quantity', 'discounted_price', 'product__gst_percent', 'product__color'))
    product_obj_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name',
                          'product_short_name',
                          'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity',
                          'product_mrp',
                          'gst_percent', 'color']
    product_df = pd.DataFrame(product_obj_list, columns=product_obj_column)
    product_list = product_df.to_dict('r')
    product_dict = {}
    for index, row in df.iterrows():
        print('crossed - {} - booth code -{}'.format(index, row['POINT']))
        if not Business.objects.filter(code=row['POINT']).exists():
            missing_list.append(row['POINT'])
            print('{} code is not available'.format(row['POINT']))
            continue;
        if not row['Total'] == 0:
            print('Value greated than zero')
            if ICustomer.objects.filter(customer_code=row['CODE']).exists():
                #         if ICustomer.objects.filter(customer_code=str(row['CODE'])).exists():
                business_obj = Business.objects.get(code=row['POINT'])
                icustomer_obj = ICustomer.objects.get(customer_code=row['CODE'])
                #             icustomer_obj = ICustomer.objects.get(customer_code=row['CODE'])
                icustomer_obj.business_id = business_obj.id
                icustomer_obj.save()
                icustomer_id = icustomer_obj.id
                route_id = RouteBusinessMap.objects.get(business_id=business_obj.id,
                                                        route__session_id=session_id).route_id
                total_cost_per_session = 0
                total_cost_per_session_for_month = 0
                sale_group_obj = ICustomerSaleGroup(
                    business_id=business_obj.id,
                    icustomer_id=icustomer_id,
                    date=start_date,
                    session_id=session_id,
                    route_id=route_id,
                    zone_id=business_obj.zone.id,
                    ordered_via_id=2,
                    payment_status_id=1,  # paid
                    sale_status_id=1,  # ordered
                    total_cost=0,
                    total_cost_for_month=0,
                    ordered_by_id=1,
                    modified_by_id=1,
                    product_amount=0,
                )
                sale_group_obj.save()
                for product in product_list:
                    if product['product_short_name'] in row.keys():
                        product_quantity = row[product['product_short_name']]
                        #                         product_quantity = Decimal(product_quantity)
                        if product_quantity != 0 and product_quantity != None:
                            sale_obj = ICustomerSale(
                                icustomer_sale_group_id=sale_group_obj.id,
                                product_id=product['product_id'],
                                count=product_quantity,
                                cost=product_quantity * product['product_mrp'],
                                cost_for_month=product_quantity * product['product_mrp'] * day_count,
                                ordered_by_id=1,
                                modified_by_id=1
                            )

                            sale_obj.save()
                            product_dict[product['product_id']] = product_quantity
                            total_cost_per_session += product_quantity * product['product_mrp']
                            total_cost_per_session_for_month += product_quantity * product['product_mrp'] * day_count

                sale_group_obj.total_cost = total_cost_per_session
                sale_group_obj.total_cost_for_month = total_cost_per_session_for_month
                sale_group_obj.product_amount = total_cost_per_session
                sale_group_obj.save()
                print('Customer order saved {}'.format(row['CODE']))
                if ICustomerMonthlyOrderTransaction.objects.filter(icustomer_id=icustomer_id, month=month,
                                                                   year=year).exists():
                    icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction.objects.get(
                        icustomer_id=icustomer_id, month=month, year=year)
                    is_date_available = True
                else:
                    icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction(icustomer_id=icustomer_id,
                                                                                   month=month, year=year,
                                                                                   transacted_date_time=datetime.datetime.now(),
                                                                                   total_cost=0, created_by_id=1,
                                                                                   milk_card_number=0)
                    icustomer_monthly_order_obj.save()
                    is_date_available = False

                icustomer_monthly_order_obj.total_cost += sale_group_obj.total_cost_for_month
                icustomer_monthly_order_obj.icustomer_sale_group.add(sale_group_obj.id)
                icustomer_milk_card_id_bank_obj = ICustomerMilkCarkNumberIdBank.objects.get(id=1)
                if is_date_available:
                    last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number
                else:
                    last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number + 1
                icustomer_monthly_order_obj.milk_card_number = str(last_count).zfill(6)
                icustomer_monthly_order_obj.save()
                # update_last_count_in_id_bank
                icustomer_milk_card_id_bank_obj.last_milk_card_number = last_count
                icustomer_milk_card_id_bank_obj.save()

                #             serial number code
                if ICustomerCardSerialNumberIdBank.objects.filter(business_id=business_obj.id, month=month,
                                                                  year=year).exists():
                    icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank.objects.get(
                        business_id=business_obj.id, month=month, year=year)
                else:
                    icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank(business_id=business_obj.id,
                                                                                   month=month, year=year,
                                                                                   counter_last_count=0,
                                                                                   online_last_count=0)
                    icustomer_serial_bank_id_obj.save()

                icustomer_serial_number_map = ICustomerSerialNumberMap(icustomer_id=icustomer_id,
                                                                       business_id=business_obj.id, month=month,
                                                                       year=year)
                serial_number = icustomer_serial_bank_id_obj.counter_last_count + 1
                icustomer_serial_number_map.serial_number = serial_number
                icustomer_serial_number_map.save()
                # update serail number in ID bank
                icustomer_serial_bank_id_obj.counter_last_count = serial_number
                icustomer_serial_bank_id_obj.online_last_count = serial_number
                icustomer_serial_bank_id_obj.save()
            else:
                print('Customer not exists {}'.format(row['CODE']))
                missind_customer_list.append(row['CODE'])

    employee_order_log_obj.time_ended = datetime.datetime.now()
    employee_order_log_obj.save()
    return Response(data=True, status=status.HTTP_200_OK)



@api_view(['POST'])
def place_employee_order_current_month(request):
    print(request.data)
    order_list = request.data['employee_order_list']
    customer_type_id = request.data['customer_type_id']
    today = date.today()

    start_date = today.replace(day=1)
    month = start_date.month
    year = start_date.year
    day_count = monthrange(year, month)[1]

    product_obj = ICustomerTypeWiseProductDiscount.objects.filter(customer_type_id=customer_type_id,
                                                                    product__is_active=True).order_by(
        'product__display_ordinal')
    product_obj_list = list(
        product_obj.values_list('product_id', 'product__group', 'product__group__name',
                                'product__name', 'product__short_name', 'product__code',
                                'product__unit',
                                'product__unit__display_name', 'product__description',
                                'product__quantity', 'discounted_price', 'product__gst_percent', 'product__color'))
    product_obj_column = ['product_id', 'product_group_id', 'product_group_name', 'product_name',
                        'product_short_name',
                        'product_code', 'unit_id', 'unit_name', 'description', 'product_quantity',
                        'product_mrp',
                        'gst_percent', 'color']
    product_df = pd.DataFrame(product_obj_list, columns=product_obj_column)
    product_list = product_df.to_dict('r')
    products_dict = product_df.groupby('product_short_name').apply(lambda x: x.to_dict('r')[0]).to_dict()
    order_list[0]['product']

    if order_list[0]['is_new'] == True:

        # ----------------EmployeeMonthlyOrderLog-------------------#
        icustomer_type_obj = ICustomerType.objects.get(id=customer_type_id)
        employee_order_log_obj = EmployeeMonthlyOrderLog(order_for=icustomer_type_obj, order_for_date=start_date,
                                                        time_statrted=datetime.datetime.now(), ordered_by=request.user)
        employee_order_log_obj.save()
        # -----------------------------------------------------------#

        missing_list = []
        missind_customer_list = []
        session_id = 1

        employee_order_df = pd.DataFrame(order_list)

        employee_order_df = employee_order_df.reindex(
            columns=['booth_code', 'employee_code', 'name', 'product', 'quantity'])

        employee_booth_df = employee_order_df.groupby(['employee_code', 'name']).agg({'booth_code': 'sum'}).reset_index()

        employee_order_df = employee_order_df.groupby(['booth_code', 'employee_code', 'product']).agg({'quantity': 'sum'})

        # convert_groupby_table_product_cost_row_wise_value_into_column(using_pandas_pivot_table)
        employee_order_df = pd.pivot_table(employee_order_df, index='employee_code', columns='product', aggfunc=min,
                                        fill_value=0)

        # convert_pivot_table_to_normal_df
        employee_order_df.columns = employee_order_df.columns.droplevel(0)  # remove amount
        employee_order_df.columns.name = None  # remove categories
        employee_order_df = employee_order_df.reset_index()  # index to columns
        employee_order_df

        df = pd.merge(employee_booth_df, employee_order_df, left_on='employee_code', right_on='employee_code', how='left')
        df = df.rename(columns={'employee_code': 'CODE', 'name': 'NAME', 'booth_code': 'POINT'})
        df['Total'] = df.iloc[:, 3:].sum(axis=1)

        product_dict = {}
        for index, row in df.iterrows():
            print('crossed - {} - booth code -{}'.format(index, row['POINT']))
            if not Business.objects.filter(code=row['POINT']).exists():
                missing_list.append(row['POINT'])
                print('{} code is not available'.format(row['POINT']))
                continue;
            if not row['Total'] == 0:
                print('Value greated than zero')
                if ICustomer.objects.filter(customer_code=row['CODE']).exists():
                    #         if ICustomer.objects.filter(customer_code=str(row['CODE'])).exists():
                    business_obj = Business.objects.get(code=row['POINT'])
                    icustomer_obj = ICustomer.objects.get(customer_code=row['CODE'])
                    #             icustomer_obj = ICustomer.objects.get(customer_code=row['CODE'])
                    icustomer_obj.business_id = business_obj.id
                    icustomer_obj.save()
                    icustomer_id = icustomer_obj.id
                    route_id = RouteBusinessMap.objects.get(business_id=business_obj.id,
                                                            route__session_id=session_id).route_id
                    total_cost_per_session = 0
                    total_cost_per_session_for_month = 0
                    sale_group_obj = ICustomerSaleGroup(
                        business_id=business_obj.id,
                        icustomer_id=icustomer_id,
                        date=start_date,
                        session_id=session_id,
                        route_id=route_id,
                        zone_id=business_obj.zone.id,
                        ordered_via_id=2,
                        payment_status_id=1,  # paid
                        sale_status_id=1,  # ordered
                        total_cost=0,
                        total_cost_for_month=0,
                        ordered_by_id=1,
                        modified_by_id=1,
                        product_amount=0,
                    )
                    sale_group_obj.save()
                    for product in product_list:
                        if product['product_short_name'] in row.keys():
                            product_quantity = row[product['product_short_name']]
                            #                         product_quantity = Decimal(product_quantity)
                            if product_quantity != 0 and product_quantity != None:
                                sale_obj = ICustomerSale(
                                    icustomer_sale_group_id=sale_group_obj.id,
                                    product_id=product['product_id'],
                                    count=product_quantity,
                                    cost=product_quantity * product['product_mrp'],
                                    cost_for_month=product_quantity * product['product_mrp'] * day_count,
                                    ordered_by_id=1,
                                    modified_by_id=1
                                )

                                sale_obj.save()
                                product_dict[product['product_id']] = product_quantity
                                total_cost_per_session += product_quantity * product['product_mrp']
                                total_cost_per_session_for_month += product_quantity * product['product_mrp'] * day_count

                    sale_group_obj.total_cost = total_cost_per_session
                    sale_group_obj.total_cost_for_month = total_cost_per_session_for_month
                    sale_group_obj.product_amount = total_cost_per_session
                    sale_group_obj.save()
                    print('Customer order saved {}'.format(row['CODE']))
                    if ICustomerMonthlyOrderTransaction.objects.filter(icustomer_id=icustomer_id, month=month,
                                                                    year=year).exists():
                        icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction.objects.get(
                            icustomer_id=icustomer_id, month=month, year=year)
                        is_date_available = True
                    else:
                        icustomer_monthly_order_obj = ICustomerMonthlyOrderTransaction(icustomer_id=icustomer_id,
                                                                                    month=month, year=year,
                                                                                    transacted_date_time=datetime.datetime.now(),
                                                                                    total_cost=0, created_by_id=1,
                                                                                    milk_card_number=0)
                        icustomer_monthly_order_obj.save()
                        is_date_available = False

                    icustomer_monthly_order_obj.total_cost += sale_group_obj.total_cost_for_month
                    icustomer_monthly_order_obj.icustomer_sale_group.add(sale_group_obj.id)
                    icustomer_milk_card_id_bank_obj = ICustomerMilkCarkNumberIdBank.objects.get(id=1)
                    if is_date_available:
                        last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number
                    else:
                        last_count = icustomer_milk_card_id_bank_obj.last_milk_card_number + 1
                    icustomer_monthly_order_obj.milk_card_number = str(last_count).zfill(6)
                    icustomer_monthly_order_obj.save()
                    # update_last_count_in_id_bank
                    icustomer_milk_card_id_bank_obj.last_milk_card_number = last_count
                    icustomer_milk_card_id_bank_obj.save()

                    #             serial number code
                    if ICustomerCardSerialNumberIdBank.objects.filter(business_id=business_obj.id, month=month,
                                                                    year=year).exists():
                        icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank.objects.get(
                            business_id=business_obj.id, month=month, year=year)
                    else:
                        icustomer_serial_bank_id_obj = ICustomerCardSerialNumberIdBank(business_id=business_obj.id,
                                                                                    month=month, year=year,
                                                                                    counter_last_count=0,
                                                                                    online_last_count=0)
                        icustomer_serial_bank_id_obj.save()

                    icustomer_serial_number_map = ICustomerSerialNumberMap(icustomer_id=icustomer_id,
                                                                        business_id=business_obj.id, month=month,
                                                                        year=year)
                    serial_number = icustomer_serial_bank_id_obj.counter_last_count + 1
                    icustomer_serial_number_map.serial_number = serial_number
                    icustomer_serial_number_map.save()
                    # update serail number in ID bank
                    icustomer_serial_bank_id_obj.counter_last_count = serial_number
                    icustomer_serial_bank_id_obj.online_last_count = serial_number
                    icustomer_serial_bank_id_obj.save()

                    today = datetime.datetime.now()
                    from_date = today.date() + datetime.timedelta(days=1)
                    to_date = today.replace(day = monthrange(today.year, today.month)[1]).date()
                    order_day_count = day_count - today.date().day
                    cost_per_quantity = sale_obj.cost
                    total_cost = cost_per_quantity * order_day_count
                    employee_order_change_obj = EmployeeOrderChangeLog(icustomer_id=sale_group_obj.icustomer_id,
                                                                        date_of_delivery=sale_group_obj.date,
                                                                        employee_order_change_mode_id=2,
                                                                        total_days=order_day_count,
                                                                        from_date=from_date,
                                                                        to_date=to_date,
                                                                        icustomer_sale=sale_obj,
                                                                        product_id = products_dict[order_list[0]['product']]['product_id'],
                                                                        count = sale_obj.count,
                                                                        cost_per_quantity = cost_per_quantity,
                                                                        total_cost = total_cost,
                                                                        session_id = sale_group_obj.session_id,
                                                                        modified_by=request.user,
                                                                        modified_at=from_date,
                                                                        )
                    employee_order_change_obj.save()
                else:
                    print('Customer not exists {}'.format(row['CODE']))
                    missind_customer_list.append(row['CODE'])

        employee_order_log_obj.time_ended = datetime.datetime.now()
        employee_order_log_obj.save()
        
        return Response(data=True, status=status.HTTP_200_OK)
    else:
        order_dict = order_list[0] 
        sale_obj = ICustomerSale.objects.get(icustomer_sale_group_id=order_dict['icustomer_sale_group_id'])
        sale_group_obj = ICustomerSaleGroup.objects.get(id=order_dict['icustomer_sale_group_id'])
        #FOR ORDER DELETE 
        today = datetime.datetime.now()
        from_date = today.replace(day=1)
        to_date = today.date()
        order_day_count = today.day
        cost_per_quantity = sale_obj.cost
        total_cost = cost_per_quantity * order_day_count
        employee_order_change_obj_delete = EmployeeOrderChangeLog(icustomer_id=order_dict['icustomer_id'],
                                                            date_of_delivery=start_date,
                                                            employee_order_change_mode_id=1,
                                                            total_days=order_day_count,
                                                            from_date=from_date.date(),
                                                            to_date=to_date,
                                                            product_id=sale_obj.product_id,
                                                            count = sale_obj.count,
                                                            cost_per_quantity = cost_per_quantity,
                                                            total_cost = total_cost,
                                                            session_id = sale_group_obj.session_id,
                                                            modified_by=request.user,
                                                            modified_at=from_date.date(),
                                                            )
        employee_order_change_obj_delete.save()

        # CUSTOMER SALE EDIT
        sale_cost = products_dict[order_dict['product']]['product_mrp'] * order_dict['quantity']
        sale_obj.count = order_dict['quantity']
        sale_obj.cost = sale_cost
        sale_obj.cost_for_month = sale_cost * day_count
        sale_obj.product_id = products_dict[order_dict['product']]['product_id']
        sale_obj.save()

        print("----------------------crossed customer sale----------------------------" , start_date)

        # CUSTOMER SALEGROUP EDIT
        sale_group_obj = ICustomerSaleGroup.objects.get(id=order_dict['icustomer_sale_group_id'])
        sale_group_obj.total_cost_for_month = sale_obj.cost_for_month
        sale_group_obj.total_cost = sale_obj.cost
        sale_group_obj.poduct_amount = sale_obj.cost
        sale_group_obj.save()

        print("---------------------sale group Crossed--------------------------")

        #FOR EDITED ORDER 
        today = datetime.datetime.now()
        from_date = today.date() + datetime.timedelta(days=1)
        to_date = today.replace(day = monthrange(today.year, today.month)[1]).date()
        order_day_count = day_count - today.date().day
        cost_per_quantity = sale_obj.cost
        total_cost = cost_per_quantity * order_day_count

        employee_order_change_obj_add = EmployeeOrderChangeLog(icustomer_id=sale_group_obj.icustomer_id,
                                                            date_of_delivery=sale_group_obj.date,
                                                            employee_order_change_mode_id=2,
                                                            total_days=order_day_count,
                                                            from_date=from_date,
                                                            to_date=to_date,
                                                            icustomer_sale=sale_obj,
                                                            product_id=products_dict[order_dict['product']]['product_id'],
                                                            count = sale_obj.count,
                                                            cost_per_quantity = cost_per_quantity,
                                                            total_cost = total_cost,
                                                            session_id = sale_group_obj.session_id,
                                                            modified_by=request.user,
                                                            modified_at=from_date,
                                                            )
        employee_order_change_obj_add.save()
        
        print("---------------------Edit Order Crossed--------------------------")

        return Response(data=True, status=status.HTTP_200_OK)



@api_view(["GET"])
def serve_employee_exemployee_list(request):
    employee_list = list(ICustomer.objects.filter(customer_type_id__in=[2, 3]).values_list('customer_code',
                                                                                           'user_profile__user__first_name'))
    employee_df = pd.DataFrame(employee_list, columns=['employee_code', 'employee_name'])
    new_employee_list = employee_df.to_dict('r')
    return Response(data=new_employee_list, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_employee_for_new_order(request):
    employee_code = request.data['employee_code']
    month = request.data['month']
    year = request.data['year']
    today = date.today()
    next_month_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

    next_month = next_month_date.month
    next_month_year = next_month_date.year

    if ICustomerSaleGroup.objects.filter(icustomer__customer_code=employee_code, date__month=next_month,
                                         date__year=next_month_year).exists():
        data_dict = {
            'order_status': True,
            'data': 'Your Trying Already Placed Order',
        }
        print(data_dict)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    elif ICustomerSaleGroup.objects.filter(icustomer__customer_code=employee_code, date__month=month,
                                           date__year=year).exists():
        data_dict = {
            'order_status': True,
            'data': 'This is not new customer. please go to EMPLOYEE ORDER page to place an order.',
        }
        print(data_dict)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        employee_order_obj = ICustomer.objects.filter(customer_code=employee_code)
        employee_order_list = employee_order_obj.values_list('customer_code', 'customer_type_id',
                                                             'user_profile__user__first_name',
                                                             'union_for_icustomer__name', 'business__code',
                                                             'icustomerproductmap__product__short_name')
        employee_order_column = ['employee_code', 'customer_type', 'name', 'union', 'booth_code', 'product']
        employee_order_df = pd.DataFrame(employee_order_list, columns=employee_order_column)
        employee_order_df['quantity'] = 1
        employee_order_dict = employee_order_df.to_dict('r')
        data_dict = {
            'data': employee_order_dict,
            'order_status': False
        }
        print(data_dict)
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_employee_for_new_order_for_currrent_month(request):
    employee_code = request.data['employee_code']
    month = request.data['month']
    year = request.data['year']

    if ICustomerSaleGroup.objects.filter(icustomer__customer_code=employee_code, date__month=month, date__year=year).exists():
        print("------------Exists---------------------")
        employee_order_obj = ICustomerSaleGroup.objects.filter(icustomer__customer_code=employee_code, date__month=month, date__year=year)
        employee_order_list = employee_order_obj.values_list('id', 'icustomer__customer_code',
                                                            'icustomer__user_profile__user__first_name',
                                                            'icustomer__union_for_icustomer__name',
                                                            'icustomer__business__code',
                                                            'icustomersale__product__short_name',
                                                            'icustomersale__count', 'icustomer_id', 'session_id', 'route_id', 
                                                            'business_id', 'zone_id', 'date', 'icustomer__customer_type_id')
        employee_order_column = ['icustomer_sale_group_id', 'employee_code', 'name', 'union', 'booth_code', 'product', 'quantity', 'icustomer_id', 'session_id', 'route_id', 'business_id', 'zone_id', 'date', 'customer_type']
        employee_order_df = pd.DataFrame(employee_order_list, columns=employee_order_column)
        employee_order_df['is_new'] = False
        employee_order_dict = employee_order_df.to_dict('r')
        data_dict = {
            'data': employee_order_dict,
        }
    else:
        employee_order_obj = ICustomer.objects.filter(customer_code=employee_code)
        employee_order_list = employee_order_obj.values_list('customer_code', 'customer_type_id',
                                                                'user_profile__user__first_name',
                                                                'union_for_icustomer__name', 'business__code',
                                                                'icustomerproductmap__product__short_name')
        employee_order_column = ['employee_code', 'customer_type', 'name', 'union', 'booth_code', 'product']
        employee_order_df = pd.DataFrame(employee_order_list, columns=employee_order_column)
        employee_order_df['quantity'] = 1
        employee_order_df['is_new'] = True
        employee_order_dict = employee_order_df.to_dict('r')
        data_dict = {
            'data': employee_order_dict,
        }
    print(data_dict)
    return Response(data=data_dict, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_payment_request_and_responce_details_in_excel(request):
    print(request.data)
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    rid = request.data['rid']
    order_status = request.data['status']
    customer_type_list = request.data['customer_type']
    
    payment_request_obj = PaymentRequest.objects.filter(time_created__date__range=[from_date,to_date]).order_by('-time_created')
    payment_request_list = list(
        payment_request_obj.values_list('id', 'rid', 'status__description', 'enquiry_response_status_latest__name',
                                        'time_modified', 'encrypted_string', 'decrypted_string',
                                        'payment_request_for__name', 'crn', 'ppi', 'cks', 'is_wallet_selected',
                                        'is_amount_returened_to_wallet', 'wallet_balance_after_this_transaction',
                                        'time_created'))
    payment_request_column = ['id', 'rid', 'request_status_name', 'enquiry_response_status_latest',
                              'latest_enquiryed_time', 'request_encrypted_string', 'request_decrypted_string',
                              'payment_request_for', 'crn', 'ppi', 'cks', 'is_wallet_selected',
                              'is_amount_returened_to_wallet', 'wallet_balance_after_this_transaction',
                              'request_time_created']
    payment_request_df = pd.DataFrame(payment_request_list, columns=payment_request_column)
    # responce
    payment_responce_obj = PaymentRequestResponse.objects.filter(payment_request__time_created__date__range=[from_date,to_date])
    payment_responce_list = list(
        payment_responce_obj.values_list('payment_request', 'status__name', 'is_enquired', 'encrypted_string',
                                         'decrypted_string', 'brn', 'trn', 'tet', 'pmd', 'stc', 'rmk', 'time_created', 'amt'))
    payment_responce_column = ['payment_request', 'responce_status_name', 'is_enquired', 'responce_encrypted_string',
                               'responce_decrypted_string', 'brn', 'trn', 'tet', 'pmd', 'stc', 'rmk',
                               'responce_time_created', 'amt']
    payment_responce_df = pd.DataFrame(payment_responce_list, columns=payment_responce_column)
    # requested user
    payment_request_user = PaymentRequestUserMap.objects.filter(payment_request_id__in=list(payment_request_df['id']))
    payment_request_user_list = list(
        payment_request_user.values_list('payment_request', 'payment_intitated_by', 'payment_intitated_by__first_name',
                                         'payment_intitated_by__last_name'))
    payment_request_user_column = ['request_map_request_id', 'user_id', 'first_name', 'last_name']
    payment_request_user_df = pd.DataFrame(payment_request_user_list, columns=payment_request_user_column)
    # merge user with request table
    payment_request_df = pd.merge(payment_request_df, payment_request_user_df, how='outer', left_on='id',
                                  right_on='request_map_request_id')

    # merge request with responce
    final_df = pd.merge(payment_request_df, payment_responce_df, left_on='id', right_on='payment_request', how='outer')
    if not final_df.empty:
        final_df['booth_or_customer_code'] = final_df.apply(lambda x: find_out_booth_or_customer_code(x['crn']), axis=1)

    final_df = final_df.fillna(0)

    # excel part
    final_df = final_df.reindex(columns=[
        'first_name', 'last_name', 'booth_or_customer_code', 'amt', 'request_time_created', 
        'payment_request_for', 'responce_status_name', 'responce_time_created', 'enquiry_response_status_latest', 
        'latest_enquiryed_time', 'is_wallet_selected', 'rid', 'crn', 'trn', 'tet', 'brn', 'pmd'
    ])


    final_df=final_df.rename(columns={
        'first_name':'First Name', 'last_name':'Last Name', 'booth_or_customer_code': 'Booth/Customer Code', 'amt': 'Amount', 'request_time_created': 'Requested Time', 
        'payment_request_for': 'Requested For', 'responce_status_name': 'Responce Status', 'responce_time_created': 'Responce Time', 'enquiry_response_status_latest': 'Enquiry Status', 
        'latest_enquiryed_time': 'Enquiry Time', 'is_wallet_selected': 'Is Wallet Used', 'rid': 'RID', 'crn': 'CRN', 'trn': 'Transaction Number', 'tet': 'Transaction Time', 'brn': 'BRN', 'pmd': 'Payment Mode'
    })

    file_name = ''
    file_path = ''
    if rid == None:
        if order_status == 'Success':
            final_df = final_df[(final_df['Responce Status'] == 'Success') | (final_df['Enquiry Status'] == 'Success')]
        elif order_status == 'Failed':
            final_df = final_df[(final_df['Enquiry Status'] == 'Failed') & (final_df['Responce Status'] != 'Success')]
        elif order_status == 'Pending':
            final_df = final_df[(final_df['Enquiry Status'] == 'Pending') & (final_df['Responce Status'] != 'Success')]
        else:
            final_df = final_df[(final_df['Responce Status'] == 0) & (final_df['Enquiry Status'] == 0)]

        final_df['Requested Time'] = final_df['Requested Time'].astype(str)
        final_df['Enquiry Time'] = final_df['Enquiry Time'].astype(str)

        final_df.index = pd.RangeIndex(start=1, stop=final_df.shape[0]+1, step=1)

        final_df['Responce Time'] = final_df['Responce Time'].astype(str)
        final_df['Transaction Time'] = final_df['Transaction Time'].astype(str)

        file_name = from_date + '_to_' + to_date + '_'+order_status+"_status.xlsx"
        file_path = os.path.join('static/media/zone_wise_report', file_name)
        final_df['Amount'] = final_df['Amount'].astype(float)
        print(list(final_df['RID']))
        final_df.to_excel(file_path)
        alert = "Data Not Avaliable"
        show_alert = False
        if final_df.empty:
            show_alert = True
    else:
        final_df = final_df[(final_df['RID'] == str(rid))]

        final_df['Requested Time'] = final_df['Requested Time'].astype(str)
        final_df['Enquiry Time'] = final_df['Enquiry Time'].astype(str)

        final_df.index = pd.RangeIndex(start=1, stop=final_df.shape[0]+1, step=1)

        final_df['Responce Time'] = final_df['Responce Time'].astype(str)
        final_df['Transaction Time'] = final_df['Transaction Time'].astype(str)

        file_name = from_date + '_to_' + to_date + '_'+str(rid)+"_status.xlsx"
        file_path = os.path.join('static/media/zone_wise_report', file_name)
        final_df.to_excel(file_path)
        alert = "Please Check Rid"
        show_alert = False
        if final_df.empty:
            show_alert = True


    print(file_path)
    document = {}
    document['file_name'] = file_name
    document['alert'] = alert
    document['show_alert'] = show_alert
    try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
    except Exception as err:
      print(err)
            

    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_customer_order_delete_log(request):
    customer_order_delete_list = list(CustomerOrderDeleteLog.objects.filter().order_by('-deleted_on').values('customer__customer_code', 'ordered_on', 'ordered_by__first_name', 'deleted_on', 'deleted_by__first_name', 'date_of_delivery', 'deleted_value_json'))
    df = pd.DataFrame(customer_order_delete_list)
    df['deleted_value_json'] = df.apply(lambda x: eval(x['deleted_value_json'])[0], axis=1)
    df_to_dic_list = df.to_dict('r')
    return Response(data=df_to_dic_list, status=status.HTTP_200_OK)

#--------------------------fermented_product_gst---------------------------

@api_view(['POST'])
def serve_fermented_products_gst_bill(request):
    print(request.data)
    selected_business_type_ids = request.data['selected_business_type_id']
    start_date = request.data['start_date']
    end_date = request.data['end_date']
    if SaleGroup.objects.filter(date__range=[start_date, end_date], business__business_type_id__in=selected_business_type_ids, sale__product__group_id=2).exists():
        sale_obj = SaleGroup.objects.filter(date__range=[start_date, end_date], business__business_type_id__in=selected_business_type_ids, sale__product__group_id=2)
        sale_values = list(sale_obj.values_list('business__businessagentmap__agent__first_name', 'business__businessagentmap__agent__agent_profile__gst_number', 'date', 'total_cost', 'sale__product__gst_percent', 'sale__cost','id'))
        sale_column = ['agent_name', 'gst_number', 'bill_date', 'total_cost', 'gst_percent', 'cost', 'bill_id']
        
        sale_df = pd.DataFrame(sale_values, columns=sale_column)
        sale_df['bill_date'] = pd.to_datetime(sale_df['bill_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%Y-%m-%d")
        
        default_value=1
        sale_df['gst']=default_value+(sale_df['gst_percent'].astype('float')/100)
        sale_df['cost']=sale_df['total_cost'].astype('float')/sale_df['gst'].astype('float')
        sale_df['total_gst']=sale_df['cost'].astype('float')*(sale_df['gst_percent'].astype('float')/100)
        sale_df['cgst']=(sale_df['total_gst'].astype('float'))/2
        sale_df['sgst']=(sale_df['total_gst'].astype('float'))/2
        
        sale_df = sale_df.fillna('')
        sale_df = sale_df.groupby(['bill_id', 'gst']).agg({'agent_name': 'first','gst_number': 'first','bill_date': 'first', 'total_cost': 'first','gst_percent':sum,'cost': sum ,'cgst':sum,'sgst':sum}).reset_index()
        final_df = sale_df.rename(columns = {'gst_number': 'GSTIN_UINOFRECIPIENT', 'agent_name': 'NAME','bill_date' : 'INVOICEDATE', 'total_cost': 'INVOICEVALUE', 'gst_percent': 'RATE', 'cost': 'TAXABLEVALUE','cgst':'CGST','sgst':'SGST'})
        final_df['PLACEOFSUPPLY'] = ''
        final_df['REVERSECHARGE'] = ''
        final_df['INVOICETYPE'] = ''
        final_df['IGST'] = 0
        final_df['INVOICENO'] = ""
        final_df = final_df.drop(columns=['bill_id'])
        final_df = final_df[['GSTIN_UINOFRECIPIENT', 'NAME', 'INVOICENO', 'INVOICEDATE', 'INVOICEVALUE', 'PLACEOFSUPPLY', 'REVERSECHARGE', 'INVOICETYPE', 'RATE', 'TAXABLEVALUE','CGST','SGST','IGST']]
        final_df.round(2)
        sale_group_gatepass_obj = SaleGroup.objects.filter(date__range=[start_date, end_date], business__business_type_id__in=selected_business_type_ids, sale__product__group_id=2).values_list('business__businessagentmap__agent__first_name', 'business__businessagentmap__agent__agent_profile__gst_number', 'sale__product__short_name','date', 'sale__product__gst_percent','sale__cost', 'sale__count', 'sale__product__hsn_code')
        sale_group_gatepass_columns = ["agent_name","gst_number","short_name", "bill_date","gst_percent","net_amount",'count', 'hsn_code']
        df = pd.DataFrame(list(sale_group_gatepass_obj), columns=sale_group_gatepass_columns)
        
        default_value=1
        df['gst']=default_value+(df['gst_percent'].astype('float')/100)
        df['cost']=df['net_amount'].astype('float')/df['gst'].astype('float')
        df['total_gst']=df['cost'].astype('float')*(df['gst_percent'].astype('float')/100)
        df['cgst']=(df['total_gst'].astype('float'))/2
        df['sgst']=(df['total_gst'].astype('float'))/2
        
        df['RATE'] = (df['net_amount'].astype('float')/df['count'].astype('float'))
        df['bill_date'] = pd.to_datetime(df['bill_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%Y-%m-%d")
        df['IGST'] = 0
        df['(No column name)'] = 0
        df['INVNO'] = ""
        df = df.rename(columns={'agent_name':'AGENT', 'gst_number':'BTAXNO', 'short_name':'PRODUCT', 'bill_date':'INVDATE','RATE':'RATE','gst_percent':'GST','net_amount':'NETAMOUNT','cgst':'CGST','sgst':'SGST','igst':'IGST', 'hsn_code': 'HSNCODE'})
        
        final_df_2 = df[['AGENT', 'BTAXNO', 'PRODUCT', 'INVNO','INVDATE','RATE','GST','(No column name)','SGST','CGST','IGST','NETAMOUNT','HSNCODE']]
        final_df_2.round(2)
        final_df_2 = final_df_2.fillna(' ')
        
        file_name = f"static/media/by_product/monthly_report/{start_date} - {end_date} - GVT MILK GST Bill.xlsx"
        writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
        sheet_name1 = "sheet1"
        sheet_name2 = "sheet2"
        final_df.to_excel(writer, sheet_name=sheet_name1, index=False)
        final_df_2.to_excel(writer, sheet_name=sheet_name2, index=False)
        writer.save()
        document = {}
        document['is_data_available'] = True
        document['file_name'] = f"{start_date} - {end_date} - GVT GST MILK Bill.xlsx"
        try:
            image_path = file_name
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['excel'] = encoded_image
        except Exception as err:
            print(err)
        return Response(data=document, status=status.HTTP_200_OK)
    else:
        document = {}
        document['is_data_available'] = False
        return Response(data=document, status=status.HTTP_200_OK)

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

