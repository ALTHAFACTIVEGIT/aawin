from datetime import datetime, timedelta, date
import pytz
from Crypto.Cipher import AES
import hashlib
import os
import random
from base64 import b64decode, b64encode
from report.models import *
from main.models import *
from decimal import Decimal
import pandas as pd

indian = pytz.timezone('Asia/Kolkata')
from dateutil import relativedelta
import math

pad_text_dict = {
    0: '\x00',
    1: '\x01',
    2: '\x02',
    3: '\x03',
    4: '\x04',
    5: '\x05',
    6: '\x06',
    7: '\x07',
    8: '\x08',
    9: '\x09',
    10: '\x0a',
    11: '\x0b',
    12: '\x0c',
    13: '\x0d',
    14: '\x0e',
    15: '\x0f',
    16: '\x10'

}
import requests

encryption_key = '0!EaW^9FwiZSlWF7'
checksum_key = '^aR^'


# enquriy to axis bank server
def get_enquiry_responce_from_server(rid):
    try:
      enquiry_limit = 30
      current_enquiry_count = 0
      payment_request_obj = PaymentRequest.objects.get(rid=rid)
      if EnquiryRequest.objects.filter(rid=payment_request_obj.rid).exists():
          current_enquiry_count = EnquiryRequest.objects.filter(rid=payment_request_obj.rid).count()
      if current_enquiry_count <= enquiry_limit:
          is_response_available = False
          brn = None
          if PaymentRequestResponse.objects.filter(payment_request_id=payment_request_obj.id).exists():
              payment_responce_obj = PaymentRequestResponse.objects.get(payment_request_id=payment_request_obj.id)
              brn = payment_responce_obj.brn
              is_response_available = True
          # dict for filling white space in ACII method
          pad_text_dict = {
            0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07', 8: '\x08', 9: '\x09', 10: '\x0a', 11: '\x0b', 12: '\x0c', 13: '\x0d', 14: '\x0e', 15: '\x0f', 16: '\x10'
          }
          ver = '1.0' #version
          cid = 5648 # cid for aavin given by axis bank
          typ = 'PRD' # test environment
          rid = payment_request_obj.rid # random reference number
          crn = payment_request_obj.crn # customer reference number
          key_before_sha_encrypt = '{}{}{}{}'.format(cid,rid,crn,checksum_key)
          cks = hashlib.sha256(key_before_sha_encrypt.encode()).hexdigest()
          if is_response_available:
              final_string = 'CID={}&RID={}&CRN={}&VER={}&TYP={}&BRN={}&CKS={}'.format(cid,rid,crn,ver,typ,brn,cks)
          else:
              final_string = 'CID={}&RID={}&CRN={}&VER={}&TYP={}&CKS={}'.format(cid,rid,crn,ver,typ,cks)
          obj = AES.new(encryption_key, AES.MODE_ECB, 'OPENSSL_RAW_DATA')
          pad_count = (16 - len(final_string) % 16)
          padded_text = final_string + (16 - len(final_string) % 16) * pad_text_dict[pad_count]
          cipertext = obj.encrypt(padded_text)
          cipertext = b64encode(cipertext).decode('utf-8')
          enquiry_request_obj = EnquiryRequest(rid=payment_request_obj.rid,
                                            status_id=1, # requested
                                            encrypted_string=cipertext,
                                            decrypted_string=final_string,
                                            ver=ver,
                                            cid=cid,
                                            typ=typ,
                                            crn=crn,
                                            cks=cks,
                                            enquiry_make_by_id=1)
          if is_response_available:
              enquiry_request_obj.brn=brn
          enquiry_request_obj.save()
          response_return = requests.post('https://easypay.axisbank.co.in/index.php/api/enquiry', {'i': cipertext})
          encrypted_key_from_enquiry = response_return.text
          print(encrypted_key_from_enquiry)

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
              transaction_date_time_in_format = datetime.datetime.strptime(decrypted_string_and_value['TET'], '%Y/%m/%d %H:%M:%S %p')
          if decrypted_string_and_value['AMT'] == '':
              decrypted_string_and_value['AMT'] = 0
          if decrypted_string_and_value['PMD'] == '':
              decrypted_string_and_value['PMD'] = ' '
          if decrypted_string_and_value['CNY'] == '':
              decrypted_string_and_value['CNY'] = ' '
          enquiry_responce_obj = EnquiryRequestResponse(enquiry_request_id=enquiry_request_obj.id,
                                                    rid=decrypted_string_and_value['RID'],
                                                    status_id=transaction_status_dict[decrypted_string_and_value['STC']]['id'],
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
          return decrypted_string_and_value['STC']
      else:
          return '111'
    except Exception as e:
      print(e)
      return '111'


# send amount to wallet
def send_amount_to_agent_wallet(agent_id, amount):
    agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
    current_balance = agent_wallet_obj.current_balance
    updated_balance = current_balance + amount
    agent_wallet_obj.current_balance = updated_balance
    agent_wallet_obj.save()


# create transaction log
def create_transaction_log(user_id, amount, rid, wallet_balance_before, wallet_balance_after, transaction_direction_id):
    transaction_obj = TransactionLog(
      date=datetime.datetime.now(),
      transacted_by_id=user_id,
      transacted_via_id=1,
      data_entered_by_id=user_id,
      amount=amount,
      transaction_direction_id=transaction_direction_id,  # from agent wallet to aavin
      transaction_mode_id=1,  # Upi
      transaction_status_id=2,  # completed
      transaction_id=rid,
      transaction_approval_status_id=1,  # Accepted
      transaction_approved_by_id=1,
      transaction_approved_time=datetime.datetime.now(),
      wallet_balance_before_this_transaction=wallet_balance_before,
      wallet_balance_after_transaction_approval=wallet_balance_after,
      description='Amount for ordering the product from agent wallet during auto bot',
      modified_by_id=user_id
    )
    transaction_obj.save()


# netfision sms
def send_message_via_netfision(mobile, message):
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
    try:
      payload = {'ClientId': 'c12015f4-2ae8-4c9f-bd74-51379169c9e5', 'ApiKey' : '622de6e4-91da-4e3b-9fb1-2262df7baff8', 'SenderID' : 'AAVINC', 'fl':'0', 'gwid':'2', 'sid':'AAVINC'}
      headers = {}
      url     = 'http://sms.tnvt.in/vendorsms/pushsms.aspx'
      payload['msg'] = message
      # payload['msisdn'] = 7010349412, 9003832999
      payload['msisdn'] = mobile, 9944774906
      res = requests.post(url, data=payload, headers=headers)
    except Exception as err:
      print(err)


# check order exipry or not
def check_order_expiry_available(sale_obj):
    indian = pytz.timezone('Asia/Kolkata')
    order_date = str(sale_obj.date)
    order_expiry_date = datetime.datetime.strptime(order_date, "%Y-%m-%d") - timedelta(days=sale_obj.route.session.expiry_day_before)
    order_expiry_time = sale_obj.route.order_expiry_time
    order_expiry_date_with_time = datetime.datetime.combine(order_expiry_date, order_expiry_time)
    indian_datetime = datetime.datetime.now().astimezone(indian).replace(tzinfo=None)
    if indian_datetime < order_expiry_date_with_time:
        return True
    else:
        return False


# main script
def execute_enquiry_script(execute_option):
    transaction_status_obj = PaymentTransactionStatus.objects.all()
    transaction_status_list = list(transaction_status_obj.values_list('id', 'name', 'code'))
    transaction_status_column = ['id', 'name', 'code']
    transaction_status_df = pd.DataFrame(transaction_status_list, columns=transaction_status_column)
    transaction_status_dict = transaction_status_df.groupby('code').apply(lambda x: x.to_dict('r')[0]).to_dict()
    if execute_option == 'priority_run':
        half_hour_before_time = datetime.datetime.now() - timedelta(hours=1)
        ten_minute_before_time = datetime.datetime.now() - timedelta(minutes=10)
        half_hour_before_time = half_hour_before_time.strftime('%Y-%m-%d %H:%M:%S')
        ten_minute_before_time = ten_minute_before_time.strftime('%Y-%m-%d %H:%M:%S')
        payment_request_obj = PaymentRequest.objects.filter(time_created__gte=half_hour_before_time, time_created__lte=ten_minute_before_time, payment_request_for_id__in=[1,2])
        run_type = 'Priority Run'
        end_time = ten_minute_before_time
    elif execute_option == 'regular_run':
        # today_date = date.today()
        today_date = datetime.datetime.now().date()
        half_hour_before_time = datetime.datetime.combine(today_date, datetime.datetime.min.time())
        five_minute_before_time = datetime.datetime.now() - timedelta(minutes=7)
        payment_request_obj = PaymentRequest.objects.filter(time_created__gte=half_hour_before_time, time_created__lte=five_minute_before_time, payment_request_for_id__in=[1,2])
        run_type = 'Regular Run'
        end_time = five_minute_before_time

    overall_canditate = payment_request_obj.count()
    success_count = 0
    payment_auto_enquiry_obj = PaymentAutoEnquiry(run_time=datetime.datetime.now(),
                                             run_interval_start=half_hour_before_time,
                                             run_interval_end=end_time,
                                             run_type=run_type,
                                             candidate_count=overall_canditate,
                                             success_count=0)

    payment_auto_enquiry_obj.save()
# loop through paymenrequest
    for payment_request in payment_request_obj:
        proceed_to_enquiry = True
        if PaymentRequestResponse.objects.filter(payment_request_id=payment_request.id).exists():
            payment_response_obj = PaymentRequestResponse.objects.get(payment_request_id=payment_request.id)
    #         get the un success requestsresponse
            if payment_response_obj.status.id == 1:
                proceed_to_enquiry = False
        if proceed_to_enquiry:
            if not payment_request.enquiry_response_status_latest_id == 1:
                enquiry_status = get_enquiry_responce_from_server(payment_request.rid)
                payment_request.enquiry_response_status_latest_id = transaction_status_dict[enquiry_status]['id']
                payment_request.save()
                if enquiry_status == '000':
                    try:
                        if EnquiryRequestResponse.objects.filter(rid=payment_request.rid, status_id=1).exists(): 
                            renquiry_responce_obj = EnquiryRequestResponse.objects.filter(rid=payment_request.rid, status_id=1).order_by('-id')[0]
                            if PaymentRequestResponse.objects.filter(rid=payment_request.rid).exists():
                                payment_request_response_obj = PaymentRequestResponse.objects.get(rid=payment_request.rid)
                                payment_request_response_obj.status = renquiry_responce_obj.status
                                payment_request_response_obj.is_enquired = True
                                payment_request_response_obj.encrypted_string = renquiry_responce_obj.encrypted_string
                                payment_request_response_obj.decrypted_string = renquiry_responce_obj.decrypted_string
                                payment_request_response_obj.brn = renquiry_responce_obj.brn
                                payment_request_response_obj.trn = renquiry_responce_obj.trn
                                payment_request_response_obj.tet = renquiry_responce_obj.tet
                                payment_request_response_obj.pmd = renquiry_responce_obj.pmd
                                payment_request_response_obj.stc = renquiry_responce_obj.stc
                                payment_request_response_obj.rmk = renquiry_responce_obj.rmk
                                payment_request_response_obj.ver = renquiry_responce_obj.ver
                                payment_request_response_obj.cid = renquiry_responce_obj.cid
                                payment_request_response_obj.typ = renquiry_responce_obj.typ
                                payment_request_response_obj.crn = renquiry_responce_obj.crn
                                payment_request_response_obj.cny = renquiry_responce_obj.cny
                                payment_request_response_obj.amt = renquiry_responce_obj.amt
                                payment_request_response_obj.cks = renquiry_responce_obj.cks
                                payment_request_response_obj.time_created = renquiry_responce_obj.time_created 
                                payment_request_response_obj.time_modified = renquiry_responce_obj.time_modified
                                payment_request_response_obj.save()
                            else:
                                payment_request_response_obj = PaymentRequestResponse(
                                                                                    payment_request=payment_request,
                                                                                    rid=renquiry_responce_obj.rid,
                                                                                    status=renquiry_responce_obj.status,
                                                                                    is_enquired=True,
                                                                                    encrypted_string=renquiry_responce_obj.encrypted_string,
                                                                                    decrypted_string=renquiry_responce_obj.decrypted_string,
                                                                                    brn=renquiry_responce_obj.brn,
                                                                                    trn=renquiry_responce_obj.trn,
                                                                                    tet=renquiry_responce_obj.tet,
                                                                                    pmd=renquiry_responce_obj.pmd,
                                                                                    stc=renquiry_responce_obj.stc,
                                                                                    rmk=renquiry_responce_obj.rmk,
                                                                                    ver=renquiry_responce_obj.ver,
                                                                                    cid=renquiry_responce_obj.cid,
                                                                                    typ=renquiry_responce_obj.typ,
                                                                                    crn=renquiry_responce_obj.crn,
                                                                                    cny=renquiry_responce_obj.cny,
                                                                                    amt=renquiry_responce_obj.amt,
                                                                                    cks=renquiry_responce_obj.cks,
                                                                                    time_created=renquiry_responce_obj.time_created,
                                                                                    time_modified=renquiry_responce_obj.time_modified,
                                                                                    )
                                payment_request_response_obj.save()
                    except Exception as err:
                        print(err)

                    success_count += 1
            #         GET User id for the agent
                    user_id = PaymentRequestUserMap.objects.get(payment_request_id=payment_request.id).payment_intitated_by.id
                    business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user_id=user_id)
                    agent_id = business_agent_obj.agent.id
                    agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_id)
                    inital_wallet_balance = agent_wallet_obj.current_balance
            #         update agent wallet with requested amount
                    send_amount_to_agent_wallet(agent_id, payment_request.amt)
            #         make transaction log for the requested amount
                    create_transaction_log(user_id, payment_request.amt, payment_request.rid, agent_wallet_obj.current_balance, agent_wallet_obj.current_balance + payment_request.amt, 3)
                    requested_time = payment_request.time_created.astimezone(indian).strftime("%d-%m-%Y %I:%M %p")
                    message = 'Dear ' + str(business_agent_obj.agent.first_name) + '(' + str(business_agent_obj.business.code) + ') Payment initiated at ' + str(requested_time) + ' has been resolved. The money ' + str(payment_request.amt) +' has been deposited to your wallet. Sorry for the inconvenience.'
            #         send sms to agent abot amount deposite to wallet
                    send_message_via_netfision(business_agent_obj.agent.agent_profile.mobile, message)
                    payment_auto_enquiry_property_obj = PaymentAutoEnquiryProperty(payment_auto_enquiry_id=payment_auto_enquiry_obj.id,
                                                                                  payment_request_id=payment_request.id,
                                                                                  amount_sent_to_wallet=payment_request.amt,
                                                                                  )
                    payment_auto_enquiry_property_obj.save()

                    # update wallet amount to deposit table
                    temp_sale_group_ids = list(SaleGroupPaymentRequestMap.objects.filter(payment_request_id=payment_request.id).values_list('temp_sale_group', flat=True))
                    delivery_date = TempSaleGroup.objects.get(id=temp_sale_group_ids[0]).date
                    auto_bot_money_deposit_obj = AutoBotMoneyDepositToWalletLog(business_id=business_agent_obj.business.id,
                                                                                delivery_date=delivery_date,
                                                                                amount=payment_request.amt,
                                                                                transaction_id=payment_request.rid,
                                                                                transacted_date=datetime.datetime.now()
                                                                                )
                    auto_bot_money_deposit_obj.save()
        #             if payment_request.payment_request_for_id == 1:
        #                 temp_sale_group_payment_request_map = SaleGroupPaymentRequestMap.objects.get(payment_request_id=payment_request.id)
        #                 temp_sale_group_ids = list(SaleGroupPaymentRequestMap.objects.filter(payment_request_id=payment_request.id).values_list('temp_sale_group', flat=True))
        #                 business_id = TempSaleGroup.objects.get(id=temp_sale_group_ids[0]).business_id
        #                 date = TempSaleGroup.objects.get(id=temp_sale_group_ids[0]).date
        #                 business_obj = BusinessAgentMap.objects.get(business_id=business_id).business
        #                 agent_obj = BusinessAgentMap.objects.get(business_id=business_id).agent
        #                 agent_wallet_obj = AgentWallet.objects.get(agent_id=agent_obj.id)
        #                 sale_group_ids = {
        #                     1: None,
        #                     2: None
        #                 }
        #                 if SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date).exists():
        #                     super_sale_group_obj = SuperSaleGroup.objects.filter(business_id=business_id, delivery_date=date)[0]
        #                 else:
        #                     super_sale_group_obj = SuperSaleGroup(business_id=business_id, delivery_date=date)
        #     #             loop thorough the tempsale groups
        #                 is_order_placed = False
        #                 for temp_sale_group_id in temp_sale_group_ids:
        #                     temp_sale_group_data_obj = TempSaleGroup.objects.get(id=temp_sale_group_id)
        #                     if RouteTrace.objects.filter(date=temp_sale_group_data_obj.date, session_id=temp_sale_group_data_obj.session_id, route_id=temp_sale_group_data_obj.route.id).exists():
        #                       route_trace_indent_status_id = RouteTrace.objects.get(date=temp_sale_group_data_obj.date, route_id=temp_sale_group_data_obj.route.id).indent_status.id
        #                     else:
        #                       route_trace_indent_status_id = 1
        #     #                 check indent closed or not
        #                     if route_trace_indent_status_id == 1:
        #     #                     check id order time closed or not
        #                         if check_order_expiry_available(temp_sale_group_data_obj):
        #                             temp_sale_group_obj = TempSaleGroup.objects.filter(id=temp_sale_group_id).values()[0]

        #                             if not SaleGroup.objects.filter(date=temp_sale_group_obj['date'], session_id=temp_sale_group_obj['session_id'], business_id=business_id).exists():
        #                                 temp_sale_group_obj['id'] = None
        #                                 main_sale_group_obj = SaleGroup.objects.create(**temp_sale_group_obj)
        #                                 sale_group_ids[main_sale_group_obj.session_id] = main_sale_group_obj.id
        #                                 vehicle_obj = RouteVehicleMap.objects.get(route_id=main_sale_group_obj.route.id).vehicle
        #                                 is_order_placed = True
        #                                 # sale
        #                                 temp_sale_ids = list(TempSale.objects.filter(temp_sale_group_id=temp_sale_group_id).values_list('id', flat=True))
        #                                 for temp_sale_id in temp_sale_ids:
        #                                     temp_sale_obj = TempSale.objects.filter(id=temp_sale_id).values()[0]
        #                                     temp_sale_obj['id'] = None
        #                                     temp_sale_obj['sale_group_id'] = main_sale_group_obj.id
        #                                     temp_sale_obj.pop('temp_sale_group_id', None)
        #                                     main_sale_obj = Sale.objects.create(**temp_sale_obj)
        #                                     if FreeProductProperty.objects.filter(main_product_id=main_sale_obj.product_id, is_active=True).exists():
        #                                         free_product_property_obj = FreeProductProperty.objects.get(main_product_id=main_sale_obj.product_id, is_active=True)
        #                                         eligible_product_count = free_product_property_obj.eligible_product_count
        #                                         defalut_free_product_count = free_product_property_obj.product_count
        #                                         if main_sale_obj.count >= eligible_product_count:
        #                                             box_count = math.floor(main_sale_obj.count/eligible_product_count)
        #                                             free_product_count = box_count*defalut_free_product_count
        #                                             sale_obj = Sale(
        #                                                 sale_group_id=main_sale_group_obj.id,
        #                                                 product_id=free_product_property_obj.free_product.id,
        #                                                 count=free_product_count,
        #                                                 cost=0,
        #                                                 ordered_by_id=1,
        #                                                 modified_by_id=1
        #                                             )
        #                                             sale_obj.save()

        #                                     # add sale to route trace
        #                                     if RouteTrace.objects.filter(date=main_sale_group_obj.date, session_id=main_sale_group_obj.session_id, route_id=main_sale_group_obj.route.id).exists():
        #                                         route_trace_obj = RouteTrace.objects.get(date=main_sale_group_obj.date, session_id=main_sale_group_obj.session_id, route_id=main_sale_group_obj.route.id)
        #                                         if RouteTraceWiseSaleSummary.objects.filter(route_trace_id=route_trace_obj.id, product_id=main_sale_obj.product.id).exists():
        #                                             route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.get(route_trace_id=route_trace_obj.id, product_id=main_sale_obj.product.id)
        #                                             route_trace_sale_summary_obj.quantity += Decimal(main_sale_obj.count)
        #                                             route_trace_sale_summary_obj.save()
        #                                         else:
        #                                             route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id, product_id=main_sale_obj.product.id, quantity= main_sale_obj.count)
        #                                             route_trace_sale_summary_obj.save()
        #                                     else:
        #                                         route_trace_obj = RouteTrace(indent_status_id=1, #initiated
        #                                                                       route_id=main_sale_group_obj.route.id,
        #                                                                       vehicle_id=vehicle_obj.id,
        #                                                                       date=main_sale_group_obj.date,
        #                                                                       session_id=main_sale_group_obj.session_id,
        #                                                                       driver_name=vehicle_obj.driver_name,
        #                                                                       driver_phone=vehicle_obj.driver_mobile)
        #                                         route_trace_obj.save()
        #                                         route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(route_trace_id=route_trace_obj.id,
        #                                                                                                   product_id=main_sale_obj.product.id,
        #                                                                                                   quantity=main_sale_obj.count)
        #                                         route_trace_sale_summary_obj.save()
        #                                 create_transaction_log(business_obj.user_profile.user.id, main_sale_group_obj.total_cost, payment_request.rid, agent_wallet_obj.current_balance, agent_wallet_obj.current_balance - main_sale_group_obj.total_cost, 2)
        #                                 agent_wallet_obj.current_balance -= main_sale_group_obj.total_cost
        #                                 agent_wallet_obj.save()
        #                                 auto_bot_money_deposit_obj.amount -= main_sale_group_obj.total_cost
        #                                 if auto_bot_money_deposit_obj.amount < 0:
        #                                   auto_bot_money_deposit_obj.amount = 0
        #                                 auto_bot_money_deposit_obj.save()

        #                                 message = 'Dear ' + str(business_agent_obj.agent.first_name) + '(' + str(business_agent_obj.business.code) + ') Your ' + str(main_sale_group_obj.session.name) + ' Order has been placed using wallet amout. Current wallet balance is ' + str(agent_wallet_obj.current_balance)
        #                         #         send sms to agent abot order placed
        #                                 send_message_via_netfision(business_agent_obj.agent.agent_profile.mobile, message)
        # #                                 update sale detais in auto enquiry log
        #                                 payment_auto_enquiry_property_obj.is_order_placed = True
        #                                 if main_sale_group_obj.session.id == 1:
        #                                     payment_auto_enquiry_property_obj.morning_sale_group_id = main_sale_group_obj.id
        #                                     payment_auto_enquiry_property_obj.morning_order_amount = main_sale_group_obj.total_cost
        #                                 else:
        #                                     payment_auto_enquiry_property_obj.evening_sale_group_id = main_sale_group_obj.id
        #                                     payment_auto_enquiry_property_obj.evening_order_amount = main_sale_group_obj.total_cost
        #                                 payment_auto_enquiry_property_obj.save()
        #                                 temp_sale_group_payment_request_map.sale_group.add(main_sale_group_obj.id)
        #                                 if super_sale_group_obj is not None:
        #                                   super_sale_group_obj.mor_sale_group_id = sale_group_ids[1]
        #                                   super_sale_group_obj.eve_sale_group_id = sale_group_ids[2]
        #                                   super_sale_group_obj.save()
        #                             #   add sale to online counter
        #                                 employee_id = 3
        #                                 if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
        #                                                                                               collection_date=datetime.datetime.now()).exists():
        #                                     counter_employee_trace_obj = CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
        #                                                                             collection_date=datetime.datetime.now())[0]
        #                                 else:
        #                                     counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=23, employee_id=employee_id,collection_date=datetime.datetime.now(),
        #                                                                                           start_date_time=datetime.datetime.now())
        #                                     counter_employee_trace_obj.save()
        #                                 if CounterEmployeeTraceSaleGroupMap.objects.filter(
        #                                         counter_employee_trace_id=counter_employee_trace_obj.id).exists():
        #                                     counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap.objects.get(
        #                                         counter_employee_trace_id=counter_employee_trace_obj.id)
        #                                     counter_sale_group_obj.sale_group.add(main_sale_group_obj.id)
        #                                     counter_sale_group_obj.save()
        #                                 else:
        #                                     counter_sale_group_obj = CounterEmployeeTraceSaleGroupMap(
        #                                         counter_employee_trace_id=counter_employee_trace_obj.id)
        #                                     counter_sale_group_obj.save()
        #                                     counter_sale_group_obj.sale_group.add(main_sale_group_obj.id)
        #                                     counter_sale_group_obj.save()

        #                                 temp_sale_group_payment_request_map.save()
                                      
        #                 if is_order_placed:
        #                   sale_df = None
        #                   if SaleGroup.objects.filter(business_id=business_id, date=date).exists():
        #                     sale_group_ids = list(SaleGroup.objects.filter(business_id=business_id, date=date).values_list('id', flat=True))
        #                     sale_obj = Sale.objects.filter(sale_group_id__in=sale_group_ids, product__is_active=True)
        #                     sale_list = list(sale_obj.values_list('id', 'sale_group', 'sale_group__business_id',
        #                                                           'sale_group__date', 'sale_group__session',
        #                                                           'sale_group__session__display_name', 'sale_group__ordered_via',
        #                                                           'sale_group__ordered_via__name', 'sale_group__payment_status__name',
        #                                                           'sale_group__sale_status__name', 'sale_group__total_cost', 'product',
        #                                                           'product__name', 'count', 'cost'))
        #                     sale_column = ['sale_id', 'sale_group_id', 'business_id', 'date', 'session_id', 'session_name',
        #                                   'ordered_via_id', 'ordered_via_name', 'payment_status',
        #                                   'sale_status',
        #                                   'session_wise_price', 'product_id', 'product_name', 'quantity', 'product_cost']
        #                     sale_df = pd.DataFrame(sale_list, columns=sale_column)
        #                   if not super_sale_group_obj is None:
        #                       sale_group_transaction_trace = SaleGroupTransactionTrace(delivery_date=date,
        #                                                                                 super_sale_group_id=super_sale_group_obj.id,
        #                                                                                 sale_group_order_type_id=1, #new Order
        #                                                                                 transacted_amount=payment_request.amt,
        #                                                                                 counter_id=23)
        #                       if not sale_df is None:
        #                           sale_group_transaction_trace.order_sale_group_json = sale_df.to_dict('r')                                        
        #                       sale_group_transaction_trace.save() 
        #                   if payment_request.is_wallet_selected:
        #                     # if payment_request.wallet_balance_after_this_transaction < agent_wallet_obj.current_balance:
        #                     transaction_obj = TransactionLog(
        #                         date=datetime.datetime.now(),
        #                         transacted_by_id=business_obj.user_profile.user.id,
        #                         transacted_via_id=1,
        #                         data_entered_by_id=business_obj.user_profile.user.id,
        #                         amount=inital_wallet_balance,
        #                         transaction_direction_id=2,  # from agent wallet to aavin
        #                         transaction_mode_id=1,  # Upi
        #                         transaction_status_id=2,  # completed
        #                         transaction_id=payment_request.rid,
        #                         transaction_approval_status_id=1,  # Accepted
        #                         transaction_approved_by_id=1,
        #                         transaction_approved_time=datetime.datetime.now(),
        #                         wallet_balance_before_this_transaction=inital_wallet_balance,
        #                         wallet_balance_after_transaction_approval=payment_request.wallet_balance_after_this_transaction,
        #                         description='Amount for ordering the product from agent wallet',
        #                         modified_by_id=business_obj.user_profile.user.id
        #                     )
        #                     transaction_obj.save()
        #                     agent_wallet_obj.current_balance = payment_request.wallet_balance_after_this_transaction
        #                     agent_wallet_obj.save()
        #                     sale_group_transaction_trace.is_wallet_used = True
        #                     sale_group_transaction_trace.wallet_amount = transaction_obj.amount
        #                     sale_group_transaction_trace.wallet_transaction_id = transaction_obj.id
        #                     sale_group_transaction_trace.save()
        #                 # update transaction log status
        #                   try:
        #                       transaction_log_obj = TransactionLog.objects.filter(transaction_id=payment_request.rid)[0]
        #                       transaction_log_obj.transaction_status_id = 2
        #                       transaction_log_obj.save()
        #                       sale_group_transaction_trace.bank_transaction_id = transaction_log_obj.id
        #                       sale_group_transaction_trace.save()
        #                   except Exception as e:
        #                       print(e)
            payment_auto_enquiry_obj.success_count = success_count
            payment_auto_enquiry_obj.save()


def run(*args):
    if args[0]:
        execute_enquiry_script(args[0])

