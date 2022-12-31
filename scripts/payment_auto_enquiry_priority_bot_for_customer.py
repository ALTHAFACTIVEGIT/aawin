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


# send amount to icustomer wallert 
def send_amount_to_customer_wallet(customer_id, amount):
    customer_wallet_obj = ICustomerWallet.objects.get(customer_id=customer_id)
    current_balance = customer_wallet_obj.current_balance
    updated_balance = current_balance + amount
    customer_wallet_obj.current_balance = updated_balance
    customer_wallet_obj.save()
    

    
# create transaction log
def create_transaction_log(user_id, amount, rid, wallet_balance_before, wallet_balance_after, transaction_direction_id):
    transaction_obj = TransactionLog(
      date=datetime.datetime.now(),
      transacted_by_id=user_id,
      transacted_via_id=1,
      data_entered_by_id=user_id,
      amount=amount,
      transaction_direction_id=transaction_direction_id,
      transaction_mode_id=1,  # Upi
      transaction_status_id=2,  # completed
      transaction_id=rid,
      transaction_approval_status_id=1,  # Accepted
      transaction_approved_by_id=1,
      transaction_approved_time=datetime.datetime.now(),
      wallet_balance_before_this_transaction=wallet_balance_before,
      wallet_balance_after_transaction_approval=wallet_balance_after,
      description='Amount Send to customer wallet during auto bot',
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
        payment_request_obj = PaymentRequest.objects.filter(time_created__gte=half_hour_before_time, time_created__lte=ten_minute_before_time, payment_request_for_id__in=[3,4])
        run_type = 'Priority Run'
        end_time = ten_minute_before_time
    elif execute_option == 'regular_run':
        # today_date = date.today()
        today_date = datetime.datetime.now().date()
        half_hour_before_time = datetime.datetime.combine(today_date, datetime.datetime.min.time())
        five_minute_before_time = datetime.datetime.now() - timedelta(minutes=7)
        payment_request_obj = PaymentRequest.objects.filter(time_created__gte=half_hour_before_time, time_created__lte=five_minute_before_time, payment_request_for_id__in=[3,4])
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
                    customer_obj = ICustomer.objects.get(user_profile__user_id=user_id)
                    customer_wallet_obj = ICustomerWallet.objects.get(customer_id=customer_obj.id)
                    inital_wallet_balance = customer_wallet_obj.current_balance
            #         update icustomer wallet with requested amount
                    send_amount_to_customer_wallet(customer_obj.id, payment_request.amt)
            #         make transaction log for the requested amount
                    create_transaction_log(user_id, payment_request.amt, payment_request.rid, customer_wallet_obj.current_balance, customer_wallet_obj.current_balance + payment_request.amt, 6)
                    requested_time = payment_request.time_created.astimezone(indian).strftime("%d-%m-%Y %I:%M %p")
                    message = 'Dear ' + str(customer_obj.user_profile.user.first_name) + '(' + str(customer_obj.customer_code) + ') Payment initiated at ' + str(requested_time) + ' has been resolved. The money ' + str(payment_request.amt) +' has been deposited to your wallet. Sorry for the inconvenience.'
            #         send sms to agent abot amount deposite to wallet
                    send_message_via_netfision(customer_obj.user_profile.mobile, message)
                    payment_auto_enquiry_property_obj = PaymentAutoEnquiryProperty(payment_auto_enquiry_id=payment_auto_enquiry_obj.id,
                                                                                  payment_request_id=payment_request.id,
                                                                                  amount_sent_to_wallet=payment_request.amt,
                                                                                  )
                    payment_auto_enquiry_property_obj.save()
                    payment_auto_enquiry_obj.success_count = success_count
                    payment_auto_enquiry_obj.save()
            

def run(*args):
    if args[0]:
        execute_enquiry_script(args[0])

