from django.shortcuts import render
import base64
from base64 import b64encode, b64decode
from decimal import Decimal
import datetime
from datetime import timedelta, date
from calendar import monthrange, month_name
import pandas as pd
import numpy as np
from transaction.models import *
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.core.files.base import ContentFile
import os
# Create your views here.
from django.db import transaction



def decode_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + '.xlsx')


def split_bank_date(bank_date):
    if len(str(bank_date).split("-")) == 2:
        date_split = str(bank_date).split("-")
    else:
        date_split = [bank_date]
    return date_split


@api_view(['GET'])
def serve_bank_transaction_uploaded_detalils(request):
    uploaded_data_list = list(BankTransactionMaster.objects.all().order_by('-id').values('file_name', 'uploaded_at', 'uploaded_by__first_name', 'uploaded_count', 'mismatch_count', 'updated_count'))
    return Response(data=uploaded_data_list, status=status.HTTP_200_OK)

@transaction.atomic
@api_view(['POST'])
def upload_bank_transaction_excel(request):
    sid = transaction.savepoint()
    try:
        print(request.user.id)

        mis_match_rid_list = []

        base64_file = request.data['base_64_excel']
        file_name = request.data['file_name'].split('\\')[-1]
        print(file_name)
        bank_transaction_master_obj = BankTransactionMaster(uploaded_by=request.user, uploaded_at=datetime.datetime.now(), uploaded_count=0, updated_count=0,mismatch_count=0, excel_file=decode_image(base64_file, file_name), file_name=file_name)
        bank_transaction_master_obj.save()

        #------------------data_upload_part--------------------------#
        df_from_excel = pd.read_excel(bank_transaction_master_obj.excel_file)

        # df_from_excel = df_from_excel.dropna(how='all', axis='columns')
        excel_columns = df_from_excel.columns

        # rename_columns
        for column_name in excel_columns:
            new_column_name = column_name.lower()
            if " " in new_column_name:
                new_column_name = new_column_name.replace(' ', '_')
                if new_column_name[-1] == "_":
                    new_column_name = new_column_name[:-1]

            df_from_excel = df_from_excel.rename(columns={column_name: new_column_name})

        df_from_excel = df_from_excel.fillna(0)

        df_from_excel = df_from_excel.rename(columns={'policy/crn_number':'crn', 'enquiry_id': 'rid'})

        # df_from_excel['bank_date_one'] = df_from_excel.apply(lambda x: split_bank_date(x['bank_date'])[0], axis=1)
        # df_from_excel['bank_date_two'] = df_from_excel.apply(lambda x: split_bank_date(x['bank_date'])[-1], axis=1)


        df_from_excel[['settlement_date', 'clearance_date', 'tran_date', 'cheque_date']] = df_from_excel[['settlement_date', 'clearance_date', 'tran_date', 'cheque_date']].apply(pd.to_datetime, format="%d-%m-%Y", errors='ignore')
        df_from_excel[['settlement_date', 'clearance_date', 'tran_date', 'cheque_date']] = df_from_excel[['settlement_date', 'clearance_date', 'tran_date', 'cheque_date']].astype(str)

        df_from_excel['settlement_date'] = df_from_excel['settlement_date'].str[:10]
        # df_from_excel['settlement_time'] = df_from_excel['settlement_time'].str[10:]

        df_from_excel['clearance_date'] = df_from_excel['clearance_date'].str[:10]
        # df_from_excel['clearance_date'] = df_from_excel['clearance_date'].str[10:]

        df_from_excel['tran_date'] = df_from_excel['tran_date'].str[:10]
        # df_from_excel['tran_date'] = df_from_excel['tran_date'].str[10:]

        df_from_excel['cheque_date'] = df_from_excel['cheque_date'].str[:10]
        # df_from_excel['cheque_date'] = df_from_excel['cheque_date'].str[10:]

        df_from_excel[['settlement_date', 'clearance_date', 'tran_date', 'cheque_date']] = df_from_excel[['settlement_date', 'clearance_date', 'tran_date', 'cheque_date']].apply(pd.to_datetime, format="%d-%m-%Y", errors='ignore')                                

        # , 'bank_date_one', 'bank_date_two'

        mismatch_count = 0
        uploaded_count = 0
        updated_count = 0

        for index, value in df_from_excel.iterrows():
            
            if BankTransactionCarryForward.objects.filter(rid=value.rid).exists():
                trn_cary_ovr_obj = BankTransactionCarryForward.objects.get(rid=value.rid)
                trn_cary_ovr_obj.is_carry_forward = True
                trn_cary_ovr_obj.crtd_date = value.settlement_date
                trn_cary_ovr_obj.updated_by = bank_transaction_master_obj.uploaded_by
                trn_cary_ovr_obj.bank_transaction_master = bank_transaction_master_obj
                trn_cary_ovr_obj.save()

            if value.clearance_date == 0 or value.clearance_date == '0':
                value.clearance_date = value.settlement_date
            if value.tran_date == 0 or value.tran_date == '0':
                value.tran_date = value.settlement_date
            if value.cheque_date == 0 or value.cheque_date == '0':
                value.cheque_date = value.settlement_date
                
            bank_transaction_obj = BankTransaction(bank_transaction_master=bank_transaction_master_obj, 
                                                    branch_code=value.branch_code, 
                                                    # cmpny_code=value.cmpny_code, 
                                                    trnsctn_nmbr=value.txn_no, 
                                                    tranaction_id=value.tranaction_id, 
                                                    transaction_pkey=value.transaction_pkey, 
                                                    salegroup_id=value.salegroup_id, 
                                                    booth_code=value.booth_code, 
                                                    customer_code=value.customer_code, 
                                                    product_list=value.product_list, 
                                                    user_code=value.user_code, 
                                                    device_type=value.device_type, 
                                                    amount=value.amount, 
                                                    total_amount=value.total_amount,
                                                    rid=value.rid, 
                                                    crn=value.crn, 
                                                    # comission_amnt=value.comission_amnt, 
                                                    # commission_amount=value.commission_amount, 
                                                    # gst_amount=value.gst_amount, 
                                                    cheque_number=value.cheque_number, 
                                                    cheque_date=value.cheque_date, 
                                                    bank_name=value.drawn_on_bank, 
                                                    branch_name=value.drawn_on_branch, 
                                                    transaction_mode=value.mode_description,
                                                    status=value.settlement_status, 
                                                    clrnce_date=value.clearance_date, 
                                                    settlement_date=value.settlement_date, 

                                                    # athrsd_date=value.athrsd_date, 
                                                    # aggregrator=value.aggregrator,
                                                    # settled = value.settled,
                                                    # bank_date=value.bank_date,
                                                    # bank_date_one = value.bank_date_one, 
                                                    # bank_date_two = value.bank_date_two
                                                )

            if BankTransaction.objects.filter(rid=bank_transaction_obj.rid).exists():
                updated_count += 1
                amount_matched = False
                rid_matched = False
                if not PaymentRequestResponse.objects.filter(rid=bank_transaction_obj.rid, status_id=1).exists():
                    mismatch_count += 1
                    mis_match_rid_list.append(value.rid) 
                else:
                    rid_matched = True
                    payment_request_respomce_obj = PaymentRequestResponse.objects.get(rid=bank_transaction_obj.rid)
                    if float(payment_request_respomce_obj.amt) == float(bank_transaction_obj.amount):
                        amount_matched = True
                BankTransaction.objects.filter(rid=bank_transaction_obj.rid).update(bank_transaction_master=bank_transaction_master_obj, 
                                                                                    branch_code=value.branch_code, 
                                                                                    # cmpny_code=value.cmpny_code, 
                                                                                    trnsctn_nmbr=value.txn_no, 
                                                                                    tranaction_id=value.tranaction_id, 
                                                                                    transaction_pkey=value.transaction_pkey, 
                                                                                    salegroup_id=value.salegroup_id, 
                                                                                    booth_code=value.booth_code, 
                                                                                    customer_code=value.customer_code, 
                                                                                    product_list=value.product_list, 
                                                                                    user_code=value.user_code, 
                                                                                    device_type=value.device_type, 
                                                                                    amount=value.amount, 
                                                                                    total_amount=value.total_amount,
                                                                                    rid=value.rid, 
                                                                                    crn=value.crn, 
                                                                                    # comission_amnt=value.comission_amnt, 
                                                                                    # commission_amount=value.commission_amount, 
                                                                                    # gst_amount=value.gst_amount, 
                                                                                    cheque_number=value.cheque_number, 
                                                                                    cheque_date=value.cheque_date, 
                                                                                    bank_name=value.drawn_on_bank, 
                                                                                    branch_name=value.drawn_on_branch, 
                                                                                    transaction_mode=value.mode_description,
                                                                                    status=value.settlement_status, 
                                                                                    clrnce_date=value.clearance_date, 
                                                                                    settlement_date=value.settlement_date, 
                                                                                    is_amount_matched = amount_matched,
                                                                                    is_rid_matched = rid_matched,
                                                                                    # athrsd_date=value.athrsd_date, 
                                                                                    # aggregrator=value.aggregrator,
                                                                                    # settled = value.settled,
                                                                                    # bank_date=value.bank_date,
                                                                                    # bank_date_one = value.bank_date_one, 
                                                                                    # bank_date_two = value.bank_date_two
                                                                                )       

            elif PaymentRequestResponse.objects.filter(rid=bank_transaction_obj.rid, status_id=1).exists():
                payment_request_respomce_obj = PaymentRequestResponse.objects.get(rid=bank_transaction_obj.rid)
                uploaded_count += 1
                bank_transaction_obj.is_rid_matched = True
                if float(payment_request_respomce_obj.amt) == float(bank_transaction_obj.amount):
                    bank_transaction_obj.is_amount_matched = True
                bank_transaction_obj.save()

                bank_transaction_payment_request_map_obj = BankTransactionPaymentResponseMap(bank_transaction_master=bank_transaction_master_obj, 
                                                                                            bank_transaction=bank_transaction_obj,
                                                                                            payment_response=payment_request_respomce_obj,
                                                                                            is_amount_matched=bank_transaction_obj.is_amount_matched)
                bank_transaction_payment_request_map_obj.save()

                if BankTransactionCarryForward.objects.filter(rid=bank_transaction_obj.rid).exists():
                    bnk_trn_cary_ovr_obj = BankTransactionCarryForward.objects.get(rid=bank_transaction_obj.rid)
                    bnk_trn_cary_ovr_obj.bank_transaction_payment_response_map = bank_transaction_payment_request_map_obj
                    bnk_trn_cary_ovr_obj.save()

            else:
                mismatch_count += 1
                uploaded_count += 1
                bank_transaction_obj.is_rid_matched = False
                bank_transaction_obj.is_amount_matched = False
                bank_transaction_obj.save()

            bank_transaction_master_obj.mismatch_count = mismatch_count
            bank_transaction_master_obj.uploaded_count = uploaded_count
            bank_transaction_master_obj.updated_count = updated_count

            bank_transaction_master_obj.save()


        data_dict = {
            'uploaded': True
        }
        print(mis_match_rid_list)
        transaction.savepoint_commit(sid)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    except Exception as e:
        data_dict = {
            'uploaded': False
        }
        print('inside error')
        print('Error - {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(data=data_dict, status=status.HTTP_400_BAD_REQUEST)


def find_out_booth_or_customer_code(string):
    string = str(string)
    index = string.index('b')
    return string[index + 1:]


@api_view(['POST'])
def serve_bank_transaction_report1(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    customer_type = request.data['customer_type']

    bank_transaction_payment_responce_obj = BankTransactionPaymentResponseMap.objects.filter(payment_response__payment_request__time_created__date__range=[from_date, to_date])
    payment_responce_obj = PaymentRequestResponse.objects.filter(payment_request__time_created__date__range=[from_date, to_date], status_id=1)

    if customer_type == 'Cash':
        payment_responce_obj = payment_responce_obj.filter(payment_request__payment_request_for_id__in=[1,2])
    elif customer_type == 'Card':
        payment_responce_obj = payment_responce_obj.filter(payment_request__payment_request_for_id__in=[3,4])
    else:
        customer_type = 'Cash + Card'
        payment_responce_obj = payment_responce_obj

    bank_transaction_rid_list = list(bank_transaction_payment_responce_obj.values_list('payment_response__rid', flat=True))                     
    not_included_payment_responce_rid_list = list(payment_responce_obj.exclude(rid__in=bank_transaction_rid_list).values_list('id', 'rid', 'amt', 'payment_request__payment_request_for__name', 'status__name', 'tet', 'trn', 'crn', 'payment_request__time_created', 'time_created'))
    not_included_payment_responce_rid_columns = ['ID', 'RID', 'Amount', 'Order For', 'Status', 'Transaction Time', 'Transaction Id', 'crn', 'Request Time', 'Responce Time']
    payment_response_df = pd.DataFrame(not_included_payment_responce_rid_list, columns=not_included_payment_responce_rid_columns)
    if payment_response_df.empty:
        document = {
            'is_report': True,
            'report' : "All Datas Are Matched !!!"
        }
        return Response(data=document, status=status.HTTP_200_OK)
    else:
        
        for index, value in payment_response_df.iterrows():
            if not BankTransactionCarryForward.objects.filter(rid=value['RID']).exists():
                print(value['ID'])
                bnk_trn_cry_ovr_obj = BankTransactionCarryForward(  
                                                                    payment_response_id=value['ID'],
                                                                    rid=value['RID'],
                                                                    updated_by=request.user
                                                                    )
                bnk_trn_cry_ovr_obj.save()

    payment_response_df['Booth/Customer Code'] = payment_response_df.apply(lambda x: find_out_booth_or_customer_code(x['crn']), axis=1)
    payment_response_df = payment_response_df.drop(columns=['crn'])
    payment_response_df.index += 1
    payment_response_df = payment_response_df.reindex(columns=['RID', 'Amount', 'Order For', 'Booth/Customer Code','Status', 'Transaction Time', 'Transaction Id', 'Request Time', 'Responce Time'])
    report_dict = payment_response_df.to_dict('r')
    payment_response_df[['Transaction Time', 'Request Time', 'Responce Time']] = payment_response_df[['Transaction Time', 'Request Time', 'Responce Time']].astype(str)
    payment_response_df['Amount'] = payment_response_df['Amount'].astype(float)
    print(list(payment_response_df['RID']))

    payment_response_df = payment_response_df.append({'RID': 'TOTAL AMOUNT', 'Amount':payment_response_df['Amount'].sum()}, ignore_index = True)
    # -------------------------------------Excel part----------------------------------------------------
    file_name = f'bank_transaction_report1_for_{from_date}_to_{to_date}.xlsx'
    file_path = os.path.join('static/media/banktransaction', file_name)
    # payment_response_df.to_excel(file_path)

    writer = pd.ExcelWriter(file_path , engine="xlsxwriter")

    spacing = 3

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = workbook.add_worksheet('r1_report')
    writer.sheets['r1_report'] = worksheet

    merge_dict = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        
    }

    merge_dict2 = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
       
    }


    merge_format = workbook.add_format(merge_dict)
    merge_format2 = workbook.add_format(merge_dict2)

    # Merge cells.
    product_len = len(list(payment_response_df.columns))
    ltr = chr(ord('@')+product_len+1)
    ltr = ltr+"2"
    worksheet.merge_range(f"A2:{ltr}", f"RI-MONEY IN TRANSIT({customer_type}) - {from_date} to {to_date}", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("C:H", 18, format1)
    worksheet.set_column(1, 7, 20)

    # df = payment_response_df.reset_index(drop=True)
    # df.index += 1
    df = payment_response_df
    df.insert(0,"S.NO", np.arange(1,len(df)+1))
    df = df.set_index("S.NO")
    df = df.fillna('')
    df.to_excel(writer,sheet_name='r1_report',startrow=spacing)
    writer.save()

    document = {}
    document['is_report'] = False
    document['file_name'] = file_name
    # document['alert'] = alert
    # document['show_alert'] = show_alert
    document['report_dict'] = report_dict
    try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
    except Exception as err:
      print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_bank_transaction_report2(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    customer_type = request.data['customer_type']
    bank_transaction_obj = BankTransaction.objects.filter(settlement_date__date__range=[from_date, to_date], is_rid_matched=False)

    bank_transaction_list = list(bank_transaction_obj.values_list('rid', 'customer_code', 'amount', 'transaction_mode', 'clrnce_date', 'settlement_date', 'athrsd_date', 'aggregrator'))                                                 
    bank_transaction_column = ['RID', 'Booth/Customr Code', 'Amount', 'Transaction Mode', 'CLRNCE DATE', 'CRTD DATE', 'ATHRSD DATE', 'Aggregrator']
    bank_transaction_df = pd.DataFrame(bank_transaction_list, columns=bank_transaction_column)

    if customer_type == 'Cash':
        bank_transaction_df = bank_transaction_df[bank_transaction_df['Booth/Customr Code'].str[:3]!='CBE']
    elif customer_type == 'Card':
        bank_transaction_df = bank_transaction_df[bank_transaction_df['Booth/Customr Code'].str[:3]=='CBE']
    else:
        customer_type = 'Cash + Card'
        bank_transaction_df = bank_transaction_df


    if bank_transaction_df.empty:
        document = {
            'is_report': True,
            'report' : "All Datas Are Matched !!!"
        }
        return Response(data=document, status=status.HTTP_200_OK)

    report_dict = bank_transaction_df.to_dict('r')

    bank_transaction_df[['CLRNCE DATE', 'CRTD DATE', 'ATHRSD DATE']] = bank_transaction_df[['CLRNCE DATE', 'CRTD DATE', 'ATHRSD DATE']].astype(str)
    bank_transaction_df['Amount'] = bank_transaction_df['Amount'].astype(float)
    bank_transaction_df.index += 1

    bank_transaction_df = bank_transaction_df.drop(columns=['CRTD DATE', 'ATHRSD DATE', 'Aggregrator'])

    bank_transaction_df = bank_transaction_df.append({'RID': '', 'Booth/Customr Code':'TOTAL AMOUNT', 'Amount':bank_transaction_df['Amount'].sum()}, ignore_index = True)
    
    file_name = f'bank_transaction_report2_for_{from_date}_to_{to_date}.xlsx'
    file_path = os.path.join('static/media/banktransaction', file_name)

    writer = pd.ExcelWriter(file_path , engine="xlsxwriter")

    spacing = 3

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = workbook.add_worksheet('r2_report')
    writer.sheets['r2_report'] = worksheet

    merge_dict = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        
    }

    merge_dict2 = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        
    }


    merge_format = workbook.add_format(merge_dict)
    merge_format2 = workbook.add_format(merge_dict2)

    # Merge cells.
    product_len = len(list(bank_transaction_df.columns))
    ltr = chr(ord('@')+product_len+1)
    ltr = ltr+"2"
    worksheet.merge_range(f"A2:{ltr}", f"R2-NOT IN DATABASE({customer_type}) - {from_date} to {to_date}", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("C:H", 18, format1)
    worksheet.set_column(1, 7, 20)

    # df = bank_transaction_df.reset_index(drop=True)
    # df.index += 1
    df = bank_transaction_df
    df.insert(0,"S.NO", np.arange(1,len(df)+1))
    df = df.set_index("S.NO")
    df = df.fillna('')
    df.to_excel(writer,sheet_name='r2_report',startrow=spacing)
    writer.save()

    document = {}
    document['is_report'] = False
    document['file_name'] = file_name
    # document['alert'] = alert
    # document['show_alert'] = show_alert
    document['report_dict'] = report_dict
    try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
    except Exception as err:
      print(err)
    print(list(bank_transaction_df['RID']))
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_bank_transaction_report3(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    customer_type = request.data['customer_type']
    bank_transaction_payment_response_obj = BankTransactionPaymentResponseMap.objects.filter(payment_response__payment_request__time_created__date__range=[from_date, to_date])

    if customer_type == 'Cash':
        bank_transaction_payment_response_obj = bank_transaction_payment_response_obj.filter(payment_response__payment_request__payment_request_for_id__in=[1,2])
    elif customer_type == 'Card':
        bank_transaction_payment_response_obj = bank_transaction_payment_response_obj.filter(payment_response__payment_request__payment_request_for_id__in=[3,4])
    else:
        bank_transaction_payment_response_obj = bank_transaction_payment_response_obj
    
    # Bank Response df
    bank_transaction_payment_map_values_list = list(bank_transaction_payment_response_obj.values_list('payment_response__crn', 'payment_response__trn', 'payment_response__rid', 'payment_response__amt', 'payment_response__payment_request__time_created', 'payment_response__time_created', 'bank_transaction__rid', 'bank_transaction__clrnce_date', 'bank_transaction__amount'))                                                                                            
    bank_transaction_payment_map_values_columns = ['Customer/Booth Code', 'Transaction Number', 'Request RID', 'Responce Amount', 'Request Time', 'Response Time', 'Bank RID', 'Clearance Date', 'Transacted Amount']
    payment_responce_df = pd.DataFrame(bank_transaction_payment_map_values_list, columns=bank_transaction_payment_map_values_columns)

    payment_responce_df['Difference Amount'] = payment_responce_df['Responce Amount']-payment_responce_df['Transacted Amount']

    payment_responce_df[['Request Time', 'Response Time', 'Clearance Date']] = payment_responce_df[['Request Time', 'Response Time', 'Clearance Date']].astype(str)
    payment_responce_df[['Responce Amount', 'Transacted Amount', 'Difference Amount']] = payment_responce_df[['Responce Amount', 'Transacted Amount', 'Difference Amount']].astype(float)

    payment_responce_df['Customer/Booth Code'] = payment_responce_df.apply(lambda x: find_out_booth_or_customer_code(x['Customer/Booth Code']), axis=1 )

    bank_data_list = payment_responce_df.to_dict('r')

    # mismatched amount df
    mismatch_df = payment_responce_df[payment_responce_df['Difference Amount'] != 0]
    mismatch_df = mismatch_df.reset_index(drop=True)
    mismatch_df.index += 1
    mismatch_df = mismatch_df.append({'Request RID':'TOTAL AMOUNT', 'Responce Amount':mismatch_df['Responce Amount'].sum() , 'Transacted Amount':mismatch_df['Transacted Amount'].sum(), 'Difference Amount':mismatch_df['Difference Amount'].sum()}, ignore_index = True)
    file_name1 = f'bank_transaction_report3_for_mismatched_amount_{from_date}_to_{to_date}.xlsx'
    file_path1 = os.path.join('static/media/banktransaction', file_name1)
    mismatch_df.to_excel(file_path1)

    # matched amount df
    matched_df = payment_responce_df[payment_responce_df['Difference Amount'] == 0]
    print(list(matched_df['Bank RID']))
    matched_df = matched_df.reset_index(drop=True)
    matched_df.index += 1
    matched_df = matched_df.append({'Request RID':'TOTAL AMOUNT', 'Responce Amount':matched_df['Responce Amount'].sum() , 'Transacted Amount':matched_df['Transacted Amount'].sum(), 'Difference Amount':mismatch_df['Difference Amount'].sum()}, ignore_index = True)
    file_name2 = f'bank_transaction_report3_for_matched_amount_{from_date}_to_{to_date}.xlsx'
    file_path2 = os.path.join('static/media/banktransaction', file_name2)

# ---------------------------------------------------Excel File Path 1----------------------------------#
    writer = pd.ExcelWriter(file_path1 , engine="xlsxwriter")

    spacing = 3

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = workbook.add_worksheet('r3_report')
    writer.sheets['r3_report'] = worksheet

    merge_dict = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
    }

    merge_dict2 = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
    }


    merge_format = workbook.add_format(merge_dict)
    merge_format2 = workbook.add_format(merge_dict2)

    # Merge cells.
    product_len = len(list(mismatch_df.columns))
    ltr = chr(ord('@')+product_len+1)
    ltr = ltr+"2"
    worksheet.merge_range(f"A2:{ltr}", f"R3-AMOUNT CREDITED FOR MONTH(AMOUNT NOT MATCHD) - {from_date} to {to_date} ", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("C:H", 18, format1)
    worksheet.set_column(1, 7, 20)

    # df = mismatch_df.reset_index(drop=True)
    # df.index += 1
    df = mismatch_df
    df.insert(0,"S.NO", np.arange(1,len(df)+1))
    df = df.set_index("S.NO")
    df = df.fillna('')
    df.to_excel(writer,sheet_name='r3_report',startrow=spacing)
    writer.save()

# ---------------------------------------------------Excel File Path 2----------------------------------#
    writer = pd.ExcelWriter(file_path2 , engine="xlsxwriter")

    spacing = 3

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = workbook.add_worksheet('r3_report')
    writer.sheets['r3_report'] = worksheet

    merge_dict = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter", 
    }

    merge_dict2 = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",   
    }


    merge_format = workbook.add_format(merge_dict)
    merge_format2 = workbook.add_format(merge_dict2)

    # Merge cells.
    product_len = len(list(matched_df.columns))
    ltr = chr(ord('@')+product_len+1)
    ltr = ltr+"2"
    worksheet.merge_range(f"A2:{ltr}", f"R3-AMOUNT CREDITED FOR MONTH(AMOUNT MATCHD)- {from_date} to {to_date}", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("C:H", 18, format1)
    worksheet.set_column(1, 7, 20)

    # df = matched_df.reset_index(drop=True)
    # df.index += 1
    df = matched_df
    df.insert(0,"S.NO", np.arange(1,len(df)+1))
    df = df.set_index("S.NO")
    df = df.fillna('')
    df.to_excel(writer,sheet_name='r3_report',startrow=spacing)
    writer.save()

    document = {}
    document['file_name1'] = file_name1
    document['file_name2'] = file_name2
    document['bank_data_list'] = bank_data_list
    try:
        image_path1 = file_path1
        image_path2 = file_path2
        with open(image_path1, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['excel1'] = encoded_image

        with open(image_path2, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel2'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_bank_transaction_report4(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    customer_type = request.data['customer_type']

    bank_transaction_carry_obj = BankTransactionCarryForward.objects.filter(payment_response__payment_request__time_created__date__range=[from_date, to_date])
    # customer_type = ''
    if customer_type == 'Cash':
        bank_transaction_carry_obj = bank_transaction_carry_obj.filter(payment_response__payment_request__payment_request_for_id__in=[1,2])
    elif customer_type == 'Card':
        bank_transaction_carry_obj = bank_transaction_carry_obj.filter(payment_response__payment_request__payment_request_for_id__in=[3,4])
    else:
        bank_transaction_carry_obj = bank_transaction_carry_obj

    bank_transaction_carry_list = list(bank_transaction_carry_obj.values_list('payment_response__crn', 'payment_response__trn', 'payment_response__rid', 'payment_response__amt', 'payment_response__payment_request__time_created', 'payment_response__time_created', 'crtd_date', 'is_carry_forward', 'updated_by__first_name'))               
    bank_transaction_carry_column = ['Customer/Booth Code', 'Transaction Number', 'RID', 'Responce Amount', 'Request Time', 'Response Time', 'Settled Date', 'is_carry', 'Uploaded By']
    bank_transaction_carry_df = pd.DataFrame(bank_transaction_carry_list, columns=bank_transaction_carry_column)

    print(bank_transaction_carry_df)

    bank_transaction_carry_df['Customer/Booth Code'] = bank_transaction_carry_df.apply(lambda x: find_out_booth_or_customer_code(x['Customer/Booth Code']), axis=1 )

    
    bank_transaction_carry_df[['Request Time', 'Response Time', 'Settled Date']] = bank_transaction_carry_df[['Request Time', 'Response Time', 'Settled Date']].astype(str)
    # bank_transaction_carry_df['Settled Date'] = bank_transaction_carry_df['Settled Date'].replace({pd.NaT: '0'}, inplace=True)
    # bank_transaction_carry_df = bank_transaction_carry_df.fillna('')

    #------------------------------------------------------------------------------Excel Part-------------------------------------------------------------------------------------

    file_name = f'bank_transaction_report_for_missed_transaction_details_from_{from_date}_to_{to_date}.xlsx'
    file_path = os.path.join('static/media/banktransaction', file_name)

    writer = pd.ExcelWriter(file_path , engine="xlsxwriter")

    spacing = 4

    # assigning that sheet to obj
    workbook = writer.book
    worksheet = workbook.add_worksheet('missed_miney')
    writer.sheets['missed_miney'] = worksheet

    merge_dict = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",       
    }

    merge_dict2 = {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter", 
    }


    merge_format = workbook.add_format(merge_dict)
    merge_format2 = workbook.add_format(merge_dict2)

    # Merge cells.
    product_len = len(list(bank_transaction_carry_df.columns))
    ltr = chr(ord('@')+product_len)
    ltr = ltr+"2"
    worksheet.merge_range(f"A2:{ltr}", f"PAYMENT DETAILS FOR MILK WENT OUT WITH OUT MONEY RECIVED - {from_date} to {to_date}", merge_format)

    format1 = workbook.add_format({"num_format": "#,##0.00"})

    # Set the column width and format.
    worksheet.set_column("C:H", 18, format1)
    worksheet.set_column(1, 7, 20)

    for value in [True, False]:
        if value == True:
            carry_over_name = "Payment Received"
        else:
            carry_over_name = "Payment Not Received Yet"

        ltr1 = 'A'+str(spacing)
        ltr2 = 'B'+str(spacing)

        worksheet.merge_range(f"{ltr1}:{ltr2}", f"{carry_over_name}", merge_format2)
        df = bank_transaction_carry_df[bank_transaction_carry_df['is_carry'] == value]
        df = df.drop(columns=['is_carry'])
        df['Responce Amount'] = df['Responce Amount'].astype(float)
        # df = df.reset_index(drop=True)
        # df.index += 1
        df.insert(0,"S.NO", np.arange(1,len(df)+1))
        df = df.set_index("S.NO")
        df = df.fillna('')
        df.to_excel(writer,sheet_name='missed_miney',startrow=spacing)
        spacing += df.shape[0] + 4
    writer.save()

    document = {}

    document['file_name'] = file_name
    # document['alert'] = alert
    # document['show_alert'] = show_alert
    document['bank_data_list'] = bank_transaction_carry_df.to_dict('r')
    try:
      image_path = file_path
      with open(image_path, 'rb') as image_file:
          encoded_image = b64encode(image_file.read())
          document['excel'] = encoded_image
    except Exception as err:
      print(err)
    return Response(data=document, status=status.HTTP_200_OK)

@api_view(['GET'])
def serve_customer_types(request):
    customer_type_list = ['Cash', 'Card', 'Both']
    data_dict = {
        'customer_type_list' : customer_type_list
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)
