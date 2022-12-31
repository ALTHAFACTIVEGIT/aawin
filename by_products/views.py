from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, logout, login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
import pandas as pd
from by_products.models import *
import datetime
from datetime import timedelta
from django.db import transaction
from decimal import Decimal
from pytz import timezone
from Crypto.Cipher import AES
import hashlib
import requests
from base64 import b64encode, b64decode
from django.db.models import Q
import math
from django.db.models import Sum, Max

import numpy as np
from django.core.files.base import ContentFile

# canvas
import os
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

from reportlab.pdfbase.ttfonts import TTFont
from num2words import num2words
from PyPDF2 import PdfFileMerger
import pytz
indian = pytz.timezone('Asia/Kolkata')

# production
encryption_key = '0!EaW^9FwiZSlWF7'
checksum_key = '^aR^'

@api_view(['GET'])
@permission_classes((AllowAny, ))
def serve_by_product_stock_record(request):
    data_dict = {}
    by_product_obj = ByProduct.objects.filter(is_active=True).order_by('by_product_group', 'display_ordinal',)
    by_product_list = list(by_product_obj.values_list('id', 'by_product_group', 'name', 'short_name', 'unit__name', 'quantity', 'igst_percent', 'cgst_percent', 'sgst_percent'))
    by_product_column = ['id', 'product_group', 'name', 'short_name', 'unit_name', 'quantity', 'igst_percent', 'cgst_percent', 'sgst_percent']
    by_product_df = pd.DataFrame(by_product_list, columns=by_product_column)


    # product group list
    by_product_group_obj = ByProductGroup.objects.all()
    by_product_group_list = list(by_product_group_obj.values_list('id', 'name'))
    by_product_group_column = ['id', 'name']
    by_product_group_df = pd.DataFrame(by_product_group_list, columns=by_product_group_column)
    data_dict['by_product_group_list'] = by_product_group_df.to_dict('r')

    goods_receipt_record_obj = GoodsReceiptRecord.objects.filter().exclude(quantity_now=0)
    goods_receipt_record_list = list(goods_receipt_record_obj.values_list('id', 'quantity_now', 'by_product'))
    goods_receipt_record_column = ['goods_receipt_id', 'quantity_now', 'by_product_id']
    goods_receipt_record_df = pd.DataFrame(goods_receipt_record_list, columns=goods_receipt_record_column)
    goods_receipt_record_df = goods_receipt_record_df.groupby('by_product_id').agg({'quantity_now': 'sum'}).reset_index()
    by_product_df = by_product_df.merge(goods_receipt_record_df, how='left', left_on='id', right_on='by_product_id').fillna(0)

    availablity_product_obj = ByProductCurrentAvailablity.objects.filter().exclude(quantity_now=0)
    availablity_product_list = list(availablity_product_obj.values_list('id', 'quantity_now', 'by_product'))
    availablity_product_column = ['availablity_id', 'avilable_quantity_after_order', 'available_by_product_id']
    availablity_product_df = pd.DataFrame(availablity_product_list, columns=availablity_product_column)

    by_product_df = by_product_df.merge(availablity_product_df, how='left', left_on='id', right_on='available_by_product_id').fillna(0)
    by_product_df['new_quantity'] = None
    by_product_df['expiry_date'] = None
    by_product_df['is_checked'] = False
    by_product_df['is_valid'] = False
    by_product_df['price_per_unit'] = None
    by_product_df['price'] = None
    by_product_df['total_price'] = None
    by_product_df['igst_value'] = None
    by_product_df['sgst_value'] = None
    by_product_df['cgst_value'] = None
    by_product_df['default_sgst_value'] = None
    by_product_df['default_cgst_value'] = None
    data_dict['by_product_dict'] = by_product_df.groupby('product_group').apply(lambda x:x.to_dict('r')).to_dict()
    return Response(data=data_dict, status=status.HTTP_200_OK)


def generate_batch_code():
    code_bank_obj = GoodsReceiptRecordCodeBank.objects.filter()[0]
    current_date = datetime.datetime.now().date()
    prefix_value = str(code_bank_obj.code_prefix) +  str((current_date.year))[2:] + str(current_date.month).zfill(2) + str(current_date.day)
    last_digit = int(code_bank_obj.last_digit)
    new_digit = last_digit + 1
    code_bank_obj.last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(4)
    return prefix_value + str(last_count)


@transaction.atomic
@api_view(['POST'])
def create_input_stock_record(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        # if not GoodsReceiptMaster.objects.filter(grn_number=request.data['grn_number']).exists():
        goods_receipt_mater = GoodsReceiptMaster(grn_number=request.data['grn_number'],
                                        grn_date=datetime.datetime.now(),
                                        bill_number=request.data['bill_number'],
                                        bill_date=request.data['bill_date'],
                                        purchase_company_id=request.data['source']['id'],
                                        po_number=request.data['po_number'],
                                        po_date=request.data['po_date'],
                                        dc_number=request.data['dc_number'],
                                        dc_date=request.data['dc_date'],
                                        created_by_id=request.user.id,
                                        modified_by_id=request.user.id,
                                        )
        goods_receipt_mater.save()

        for product in request.data['selected_product_list']:
            goods_receipt_record_obj = GoodsReceiptRecord(goods_receipt_master_id=goods_receipt_mater.id,
                                                        by_product_id=product['id'],
                                                        quantity_at_receipt=product['new_quantity'],
                                                        quantity_now=product['new_quantity'],
                                                        quantity_now_time=datetime.datetime.now(),
                                                        price_per_unit=product['price_per_unit'],
                                                        price=product['price'],
                                                        total_price=product['total_price'],
                                                        goods_receipt_code=generate_batch_code(),
                                                        created_by_id=request.user.id,
                                                        modified_by_id=request.user.id,
                                                        )
            if not product['igst_value'] is None:
                goods_receipt_record_obj.igst_value = product['igst_value']
            if not product['cgst_value'] is None:
                goods_receipt_record_obj.cgst_value = product['cgst_value']
            if not product['sgst_value'] is None:
                goods_receipt_record_obj.sgst_value = product['sgst_value']
            if not product['expiry_date'] is None:
                goods_receipt_record_obj.expiry_date = product['expiry_date']
            goods_receipt_record_obj.save()
            daily_goods_receipt_record_obj = GoodsReceiptRecordForDaily(sale_date=datetime.datetime.now(),
                                                        by_product_id=product['id'],
                                                        quantity_at_receipt=product['new_quantity'],
                                                        quantity_now=product['new_quantity'],
                                                        quantity_now_time=datetime.datetime.now(),
                                                        price_per_unit=product['price_per_unit'],
                                                        total_price=product['total_price'],
                                                        grn_number=request.data['grn_number'],
                                                        )
            daily_goods_receipt_record_obj.save()

            # add data to Main Stock
            if ByProductCurrentAvailablity.objects.filter(by_product_id=product['id']).exists():
                main_input_stock_obj = ByProductCurrentAvailablity.objects.get(by_product_id=product['id'])
                main_input_stock_obj.quantity_now = main_input_stock_obj.quantity_now + product['new_quantity']
                main_input_stock_obj.quantity_now_time = datetime.datetime.now()
                main_input_stock_obj.modified_by_id = request.user.id
                main_input_stock_obj.save()
            else:
                main_input_stock_obj = ByProductCurrentAvailablity(by_product_id=product['id'],
                                                    quantity_now=product['new_quantity'],
                                                    quantity_now_time=datetime.datetime.now(),
                                                    created_by_id=request.user.id,
                                                    modified_by_id=request.user.id)
                main_input_stock_obj.save()
        code_bank_obj = GoodsReceiptMasterCodeBank.objects.filter()[0]
        code_bank_obj.last_digit = code_bank_obj.temp_last_digit
        code_bank_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def serve_new_grn_number(request):
    code_bank_obj = GoodsReceiptMasterCodeBank.objects.filter()[0]
    current_date = datetime.datetime.now().date()
    prefix_value = str(code_bank_obj.code_prefix) +  str((current_date.year))[2:]
    temp_last_digit = int(code_bank_obj.temp_last_digit)
    new_digit = temp_last_digit + 1
    code_bank_obj.temp_last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(5)
    new_grn_code = prefix_value + str(last_count)
    return Response(data=new_grn_code, status=status.HTTP_200_OK)


@api_view(['GET'])
def update_grn_back_to_original_digit(request):
    code_bank_obj = GoodsReceiptMasterCodeBank.objects.filter()[0]
    if code_bank_obj.last_digit != code_bank_obj.temp_last_digit:
        code_bank_obj.temp_last_digit = code_bank_obj.last_digit
        code_bank_obj.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_goods_record_for_selected_product(request):
    goods_receipt_record_obj = GoodsReceiptRecord.objects.filter(by_product_id=request.data['product_id'])
    goods_receipt_record_list = list(goods_receipt_record_obj.values_list('id', 'by_product', 'quantity_at_receipt', 'quantity_now', 'quantity_now_time', 'expiry_date', 'created_by__first_name', 'goods_receipt_master__grn_number', 'goods_receipt_master__grn_date', 'goods_receipt_master__po_number', 'goods_receipt_master__po_date', 'goods_receipt_master__dc_number', 'goods_receipt_master__dc_date', 'price_per_unit', 'price', 'igst_value', 'cgst_value', 'sgst_value', 'total_price', 'goods_receipt_master__purchase_company__company_name'))
    goods_receipt_record_column = ['id', 'by_product_id','quantity_at_receipt', 'quantity_now', 'quantity_now_time', 'expiry_date', 'created_by', 'grn_number', 'grn_date', 'po_number', 'po_date', 'dc_number', 'dc_date', 'price_per_unit', 'price', 'igst_value', 'cgst_value', 'sgst_value', 'total_price', 'purchase_company']
    goods_receipt_record_df = pd.DataFrame(goods_receipt_record_list, columns=goods_receipt_record_column)
    goods_receipt_record_df = goods_receipt_record_df.fillna(0)
    return Response(data=goods_receipt_record_df.to_dict('r'), status=status.HTTP_200_OK)



@api_view(['GET'])
def serve_by_product_list(request):
    data_dict = {}
    by_product_obj = ByProduct.objects.filter(is_active=True).order_by('by_product_group', 'display_ordinal',)
    by_product_list = list(by_product_obj.values_list('id', 'by_product_group', 'name', 'short_name', 'unit__name', 'quantity', 'code', 'base_price', 'mrp', 'igst_percent', 'cgst_percent', 'sgst_percent', 'unit_id', 'description', 'igst_amount', 'cgst_amount', 'sgst_amount', 'display_ordinal'))
    by_product_column = ['id', 'product_group', 'name', 'short_name', 'unit_name', 'quantity', 'product_code', 'base_price', 'mrp', 'igst_percent', 'cgst_percent', 'sgst_percent', 'unit_id', 'description', 'igst_amount', 'cgst_amount', 'sgst_amount', 'display_ordinal']
    by_product_df = pd.DataFrame(by_product_list, columns=by_product_column)
    by_product_group_obj = ByProductGroup.objects.all()
    by_product_group_list = list(by_product_group_obj.values_list('id', 'name'))
    by_product_group_column = ['id', 'name']
    by_product_group_df = pd.DataFrame(by_product_group_list, columns=by_product_group_column)
    data_dict['by_product_group_list'] = by_product_group_df.to_dict('r')
    data_dict['by_product_dict'] = by_product_df.groupby('product_group').apply(lambda x:x.to_dict('r')).to_dict()
    unit_obj = ByProductUnit.objects.all()
    unit_list = list(unit_obj.values_list('id', 'name'))
    unit_column = ['id', 'name']
    unit_df = pd.DataFrame(unit_list, columns=unit_column)
    data_dict['unit_list'] = unit_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_or_update_by_product(request):
    if request.data['id'] == None:
        by_product_obj = ByProduct(by_product_group_id=request.data['group_id'],
                                name=request.data['name'],
                                short_name=request.data['name'],
                                display_ordinal=request.data['display_ordinal'],
                                code=request.data['product_code'],
                                unit_id=request.data['unit_id'],
                                description=request.data['description'],
                                quantity=request.data['quantity'],
                                base_price=request.data['base_price'],
                                mrp=request.data['mrp'],
                                igst_amount=request.data['igst_amount'],
                                cgst_amount=request.data['cgst_amount'],
                                sgst_amount=request.data['sgst_amount'],
                                    )
        
        if not request.data['sgst_percent'] is None:
            by_product_obj.sgst_percent = request.data['sgst_percent']
        
        if not request.data['igst_percent'] is None:
            by_product_obj.igst_percent = request.data['igst_percent']
        
        if not request.data['cgst_percent'] is None:
            by_product_obj.cgst_percent = request.data['cgst_percent']

        by_product_obj.save()
    else:
        by_product_obj = ByProduct.objects.get(id=request.data['id'])
        by_product_obj.by_product_group_id = request.data['group_id']
        by_product_obj.name = request.data['name']
        by_product_obj.short_name = request.data['name']
        by_product_obj.code = request.data['product_code']
        by_product_obj.display_ordinal = request.data['display_ordinal']
        by_product_obj.unit_id = request.data['unit_id']
        by_product_obj.description = request.data['description']
        by_product_obj.quantity = request.data['quantity']
        by_product_obj.base_price = request.data['base_price']
        by_product_obj.mrp = request.data['mrp']
        by_product_obj.igst_amount = request.data['igst_amount']
        by_product_obj.sgst_amount = request.data['sgst_amount']
        by_product_obj.cgst_amount = request.data['cgst_amount']

        if not request.data['sgst_percent'] is None:
            by_product_obj.sgst_percent = request.data['sgst_percent']
        else:
            by_product_obj.sgst_percent = 0
        
        if not request.data['igst_percent'] is None:
            by_product_obj.igst_percent = request.data['igst_percent']
        else:
            by_product_obj.igst_percent = 0
        
        if not request.data['cgst_percent'] is None:
            by_product_obj.cgst_percent = request.data['cgst_percent']
        else:
            by_product_obj.cgst_percent = 0

        by_product_obj.save()

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_business_type_list_for_by_product_price(request):
    data = []
    business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(order_category_id=2).values_list('business_type', flat=True))

    # business_type_ids = [1, 2, 3, 9, 10, 12, 4]
    values = BusinessType.objects.filter(id__in=business_type_ids).order_by('id').values_list('id', 'name')
    columns = ['id', 'name']
    df = pd.DataFrame(list(values), columns=columns)
    if not df.empty:
        data = df.to_dict('r')
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_business_type_wise_discount_price_dict_for_by_product(request):
    data = {}
    business_type_id = request.data['business_type_id']
    # business_type_ids = list(BusinessTypeOrderCategoryeMap.objects.filter(order_category_id=2).values_list('business_type', flat=True))
    business_type_wise_obj = BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=business_type_id, by_product__is_active=True)
    business_type_wise_list = list(business_type_wise_obj.values_list('by_product', 'by_product__name', 'base_price', 'mrp', 'igst_amount', 'cgst_amount', 'sgst_amount'))
    business_type_wise_columns = ['product_id', 'product_name', 'base_price', 'mrp', 'igst_amount', 'cgst_amount', 'sgst_amount']
    df = pd.DataFrame(business_type_wise_list, columns=business_type_wise_columns)
    grouped_df = df.groupby('product_id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    return Response(data=grouped_df, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
def save_or_update_business_type_wise_discount_price_for_by_product(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        print(request.data)
        format = "%Y-%m-%d %H:%M:%S %Z%z"
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        formatted_date = now_asia
        if BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=request.data['business_type_id'],
                                                        by_product_id=request.data['product_id']).exists():
            obj = BusinessTypeWiseByProductDiscount.objects.get(business_type_id=request.data['business_type_id'],
                                                            by_product_id=request.data['product_id'])
            if request.data['value_for'] == 'Base Price':
                obj.base_price = request.data['price']
            elif request.data['value_for'] == 'CGST Amount':
                obj.cgst_amount = request.data['price']
            elif request.data['value_for'] == 'SGST Amount':
                obj.sgst_amount = request.data['price']
            else:
                obj.mrp = request.data['price']
            obj.igst_amount = Decimal(obj.cgst_amount) + Decimal(obj.sgst_amount)
            obj.modified_by_id = request.user.id
            obj.save()
            if BusinessTypeWiseByProductDiscountTrace.objects.filter(business_type_wise_discount_id=obj.id).exists():
                latest_trace_obj = BusinessTypeWiseByProductDiscountTrace.objects.filter(business_type_wise_discount_id=obj.id).order_by('-id')[0]
                latest_trace_obj.end_date = datetime.datetime.now()
                latest_trace_obj.product_discount_ended_by_id = request.user.id
                latest_trace_obj.save()
            trace_obj = BusinessTypeWiseByProductDiscountTrace(business_type_wise_discount_id=obj.id,
                                                               start_date=datetime.datetime.now(),
                                                               base_price=obj.base_price,
                                                               igst_amount=obj.igst_amount,
                                                               cgst_amount=obj.cgst_amount,
                                                               sgst_amount=obj.sgst_amount,
                                                               mrp=obj.mrp,
                                                               product_discount_started_by_id=request.user.id
                                                               )
            trace_obj.save()
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_200_OK)
        else:
            print('came in else')
            obj = BusinessTypeWiseByProductDiscount.objects.create(
                business_type_id=request.data['business_type_id'],
                by_product_id=request.data['product_id'],
                created_by=request.user,
                modified_by=request.user
            )

            if request.data['value_for'] == 'Base Price':
                obj.base_price = request.data['price']
            elif request.data['value_for'] == 'CGST Amount':
                obj.cgst_amount = request.data['price']
            elif request.data['value_for'] == 'SGST Amount':
                obj.sgst_amount = request.data['price']
            else:
                obj.mrp = request.data['price']
            obj.igst_amount = Decimal(obj.cgst_amount) + Decimal(obj.sgst_amount)
            obj.save()
            trace_obj = BusinessTypeWiseByProductDiscountTrace(business_type_wise_discount_id=obj.id,
                                                               start_date=datetime.datetime.now(),
                                                               base_price=obj.base_price,
                                                               igst_amount=obj.igst_amount,
                                                               cgst_amount=obj.cgst_amount,
                                                               sgst_amount=obj.sgst_amount,
                                                               mrp=obj.mrp,
                                                               product_discount_started_by_id=request.user.id
                                                               )
            trace_obj.save()
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def remove_business_type_wise_product_for_by_product(request):
    print(request.data)
    if BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=request.data['business_type_id'],
                                                      by_product_id=request.data['product_id']).exists():
        print('exists deleted')
        BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=request.data['business_type_id'],
                                                       by_product_id=request.data['product_id']).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_by_product_list_for_order(request):
    if request.data['from'] == 'portal':
        business_obj = Business.objects.get(code=request.data['business_code'])
        # if not Agent.objects.filter(agent_code=request.data['business_code']).exists():
        #     if not Business.objects.filter(code=request.data['business_code']).exists():
        #         print('not exists')
        #         data = {'error_message': str(request.data['business_code']) + ' is not a valid booth code. Please Check'}
        #         return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        #     else:
        # else:
        #     agent_obj = Agent.objects.get(agent_code=request.data['business_code'])

        #     business_agent_obj = BusinessAgentMap.objects.get(agent_id=agent_obj.id)
        #     business_obj = Business.objects.get(code=business_agent_obj.business.code)
        # business_obj = Business.objects.get(code=request.data['business_code'])
    else:
        business_obj = Business.objects.get(user_profile__user_id=request.user.id)
    business_type_wise_product_ids = list(BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=business_obj.business_type_id).values_list('by_product', flat=True))

    data_dict = {}
    to_date = datetime.datetime.now()
    from_date = to_date - timedelta(days=30)
    # agent_ordered_product_ids = list(set(list(BySale.objects.filter(by_sale_group__business_id=business_obj.id, by_sale_group__ordered_date__gte=from_date, by_sale_group__ordered_date__lte=to_date, by_product_id__in=business_type_wise_product_ids).values_list('by_product_id', flat=True))))
    agent_ordered_product_ids = []
    by_product_obj = ByProduct.objects.filter(is_active=True).order_by('by_product_group', 'display_ordinal')
    by_product_list = list(by_product_obj.values_list('id', 'by_product_group', 'name', 'short_name', 'unit__name', 'quantity', 'code'))
    by_product_column = ['product_id', 'product_group', 'name', 'short_name', 'unit_name', 'quantity', 'product_code']
    by_product_df = pd.DataFrame(by_product_list, columns=by_product_column)
    goods_receipt_record_obj = ByProductCurrentAvailablity.objects.filter(by_product_id__in=business_type_wise_product_ids)
    goods_receipt_record_list = list(goods_receipt_record_obj.values_list('id', 'quantity_now', 'by_product'))
    goods_receipt_record_column = ['availablity_product_id', 'quantity_now', 'by_product_id']
    goods_receipt_record_df = pd.DataFrame(goods_receipt_record_list, columns=goods_receipt_record_column)
    by_product_df = by_product_df.merge(goods_receipt_record_df, how='left', left_on='product_id', right_on='by_product_id').fillna(0)
    # by_product_df = by_product_df[by_product_df['quantity_now'] > 0]
    by_product_df['entered_qty'] = 0
    by_product_df['cgst_value'] = 0
    by_product_df['sgst_value'] = 0
    by_product_df['is_checked'] = False
    by_product_df['value'] = 0
    by_product_df['total_price'] = 0
    # daily sale update checks
    daily_sale_update_obj = BusinessWiseDailySaleUpdate.objects.filter(by_product_id__in=business_type_wise_product_ids, business_id=business_obj.id, sale_date=to_date, closing_quantity__isnull=False)
    sale_closed_product_list = list(daily_sale_update_obj.values_list('by_product', flat=True))
    by_product_df.loc[(by_product_df['product_id'].isin(agent_ordered_product_ids)) & (by_product_df['quantity_now'] > 0) & (~by_product_df['product_id'].isin(sale_closed_product_list)) , 'is_checked'] = True
    data_dict['by_product_group_dict'] = by_product_df.groupby('product_group').apply(lambda x:x.to_dict('r')).to_dict()


    by_product_group_obj = ByProductGroup.objects.all()
    by_product_group_list = list(by_product_group_obj.values_list('id', 'name'))
    by_product_group_column = ['id', 'name']
    by_product_group_df = pd.DataFrame(by_product_group_list, columns=by_product_group_column)
    data_dict['by_product_group_list'] = by_product_group_df.to_dict('r')
    selected_product_list = by_product_df[by_product_df['is_checked'] == True]
    data_dict['selected_product_list'] = selected_product_list.to_dict('r')
    data_dict['all_product_list'] = by_product_df.to_dict('r')
    data_dict['sale_closed_product_list'] = sale_closed_product_list
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_by_product_availablity_and_price_list(request):
    data_dict = {}
    if request.data['from'] == 'portal':
        business_obj = Business.objects.get(code=request.data['business_code'])
    else:
        business_obj = Business.objects.get(user_profile__user_id=request.user.id)
    goods_receipt_record_obj = ByProductCurrentAvailablity.objects.filter()
    goods_receipt_record_list = list(goods_receipt_record_obj.values_list('id', 'quantity_now', 'by_product'))
    goods_receipt_record_column = ['availablity_product_id', 'quantity_now', 'by_product_id']
    goods_receipt_record_df = pd.DataFrame(goods_receipt_record_list, columns=goods_receipt_record_column)
    data_dict['product_availablity_dict'] = goods_receipt_record_df.groupby('by_product_id').apply(lambda x:x.to_dict('r')[0]).to_dict()

    business_type_wise_price_obj = BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=business_obj.business_type_id)
    business_type_wise_price_list = list(business_type_wise_price_obj.values_list('id', 'business_type', 'by_product', 'base_price', 'mrp', 'cgst_amount', 'sgst_amount'))
    business_type_wise_price_column = ['id', 'business_type', 'by_product_id', 'base_price', 'mrp', 'cgst_amount', 'sgst_amount']
    business_type_wise_price_df = pd.DataFrame(business_type_wise_price_list, columns=business_type_wise_price_column)
    data_dict['product_price_dict']  = business_type_wise_price_df.groupby('by_product_id').apply(lambda x:x.to_dict('r')[0]).to_dict()
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_wallet_balance_and_order_category(request):
    data_dict = {}
    print(request.data)
    if request.data['from'] == 'portal':
        business_agent_obj = BusinessAgentMap.objects.get(business__code=request.data['business_code'])
    else:
        business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=request.user)
    wallet_obj = ByProductAgentWallet.objects.get(agent_id=business_agent_obj.agent.id)
    data_dict['wallet_balance'] = wallet_obj.current_balance
    order_category_dict = {}
    for map_obj in BusinessTypeOrderCategoryeMap.objects.filter(business_type_id=business_agent_obj.business.business_type_id):
        if not map_obj.order_category.id in order_category_dict:
            order_category_dict[map_obj.order_category.id] = map_obj.payment_option.id
    data_dict['order_category'] = order_category_dict
    data_dict['business_type_id'] = business_agent_obj.business.business_type_id
    return Response(data=data_dict, status=status.HTTP_200_OK)


def generate_by_product_order_code():
    code_bank_obj = BySaleGroupOrderCodeBank.objects.filter()[0]
    current_date = datetime.datetime.now().date()
    prefix_value = str(code_bank_obj.code_prefix) +  str((current_date.year))[2:] + str(current_date.month).zfill(2) + str(current_date.day)
    last_digit = int(code_bank_obj.last_digit)
    new_digit = last_digit + 1
    code_bank_obj.last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(4)
    return prefix_value + str(last_count)


def generate_temp_by_product_order_code():
    code_bank_obj = TempBySaleGroupOrderCodeBank.objects.filter()[0]
    current_date = datetime.datetime.now().date()
    prefix_value = str(code_bank_obj.code_prefix) +  str((current_date.year))[2:] + str(current_date.month).zfill(2) + str(current_date.day)
    last_digit = int(code_bank_obj.last_digit)
    new_digit = last_digit + 1
    code_bank_obj.last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(4)
    return prefix_value + str(last_count)


def calculate_gst_value(base_price, mrp, qty):
    total_gst = mrp - base_price
    product_cgst_value = total_gst / 2
    product_sgst_value = total_gst / 2
    data_dict = {
        'product_cgst_value': product_cgst_value,
        'product_sgst_value': product_sgst_value
    }
    return data_dict


@transaction.atomic
@api_view(['POST'])
def register_order_for_by_product_employee(request):
    sid = transaction.savepoint()
    try:
        if request.data['from'] == 'portal':
            business_agent_obj = BusinessAgentMap.objects.get(business__code=request.data['business_code'])
            business_type_id = business_agent_obj.business.business_type.id
            user_profile_id = business_agent_obj.business.user_profile_id
            agent_id = business_agent_obj.agent_id
            agent_user_id = business_agent_obj.business.user_profile.user.id
            business_id = business_agent_obj.business.id
            via_id = 2
        elif request.data['from'] == 'mobile':
            business_id = Business.objects.get(user_profile__user_id=request.user.id).id
            business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
            business_type_id = business_agent_obj.business.business_type.id
            user_profile_id = business_agent_obj.business.user_profile_id
            agent_id = business_agent_obj.agent_id
            agent_user_id = business_agent_obj.business.user_profile.user.id
            via_id = 1
        elif request.data['from'] == 'website':
            business_id = Business.objects.get(user_profile__user_id=request.user.id).id
            business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
            business_type_id = business_agent_obj.business.business_type.id
            user_profile_id = business_agent_obj.business.user_profile_id
            agent_id = business_agent_obj.agent_id
            agent_user_id = business_agent_obj.business.user_profile.user.id
            via_id = 3

        data_dict = serve_by_product_price_dict(user_profile_id)
        product_price_dict = data_dict['product_price_dict']
        order_category_dict = data_dict['order_category']
        order_category_id = 2
        agent_wallet_obj = ByProductAgentWallet.objects.get(agent_id=agent_id)
        counter_id = None
        is_order_placed = False
        order_code = generate_by_product_order_code()
        total_cost = 0
        if not request.data['final_price_before_wallet'] == 0:
            by_sale_group_obj = EmployeeOrderBySaleGroup(
                business_id=business_id,
                order_code=order_code,
                zone_id=business_agent_obj.business.zone.id,
                ordered_date=datetime.datetime.now(),
                ordered_via_id=via_id,
                total_cost=0,
                sale_status_id=1, #ordered
                ordered_by_id=request.user.id,
                modified_by_id=request.user.id,
                payment_status_id=1
            )
            by_sale_group_obj.save()
            
            for product in request.data['selected_product_list']:
                product_qty = product['entered_qty']
                current_product_availablity = ByProductCurrentAvailablity.objects.get(by_product_id=product['product_id'])
                if product_qty != 0 and product_qty != None:
                    if product_qty <= current_product_availablity.quantity_now:
                        product_base_price = product_qty * product_price_dict[product['product_id']]['base_price']
                        product_mrp = product_qty * product_price_dict[product['product_id']]['mrp']
                        product_gst_dict = calculate_gst_value(product_base_price, product_mrp, product_qty)
                        by_sale_obj = EmployeeOrderBySale(
                            employeee_order_by_sale_group_id=by_sale_group_obj.id,
                            by_product_id=product['product_id'],
                            count=product_qty,
                            cost=product_base_price,
                            cgst_value=product_gst_dict['product_cgst_value'],
                            sgst_value=product_gst_dict['product_sgst_value'],
                            total_cost=product_mrp,
                            ordered_by_id=request.user.id,
                            modified_by_id=request.user.id,
                        )
                        by_sale_obj.save()
                        current_product_availablity.quantity_now = current_product_availablity.quantity_now - product_qty
                        current_product_availablity.quantity_now_time = datetime.datetime.now()
                        current_product_availablity.save()
                        total_cost += product_base_price
                    else:
                        error_dict = {}
                        error_dict['product_name'] = current_product_availablity.by_product.short_name
                        error_dict['required_qty'] = product_qty
                        error_dict['available_qty'] = current_product_availablity.quantity_now
                        transaction.savepoint_rollback(sid)
                        return Response(data=error_dict, status=status.HTTP_400_BAD_REQUEST)
            saved_by_sale_group_obj = EmployeeOrderBySaleGroup.objects.get(id=by_sale_group_obj.id)
            saved_by_sale_group_obj.total_cost = total_cost
            saved_by_sale_group_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@transaction.atomic
@api_view(['POST'])
def return_grn_and_order_to_main_employee_order(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        business_agent_obj = BusinessAgentMap.objects.get(business__code=request.data['business_code'])
        business_type_id = business_agent_obj.business.business_type.id
        user_profile_id = business_agent_obj.business.user_profile_id
        agent_id = business_agent_obj.agent_id
        agent_user_id = business_agent_obj.business.user_profile.user.id
        business_id = business_agent_obj.business.id
        data_dict = serve_by_product_price_dict(user_profile_id)
        product_price_dict = data_dict['product_price_dict']
        order_category_dict = data_dict['order_category']
        order_category_id = 2
        counter_id = None
        is_order_placed = False
        order_code = generate_by_product_order_code()
        total_cost = 0
        if not request.data['total_price'] == 0:
            by_sale_group_obj = BySaleGroup(
                business_id=business_id,
                order_code=order_code,
                zone_id=business_agent_obj.business.zone.id,
                ordered_date=datetime.datetime.now(),
                ordered_via_id=2,
                total_cost=0,
                sale_status_id=2, #ordered
                ordered_by_id=request.user.id,
                modified_by_id=request.user.id,
                payment_status_id=1
            )
            by_sale_group_obj.save()
            super_by_sale_group_obj = BySaleGroupTransactionTrace(
                by_sale_group_id=by_sale_group_obj.id,
                sale_group_order_type_id=1,
            )
            super_by_sale_group_obj.save()
            
            for product in request.data['product_list']:
                product_qty = product['billing_qty']
                if product_qty != 0 and product_qty != None:
                    product_price = product_qty * product_price_dict[product['by_product_id']]['price']
                    product_gst_dict = calculate_gst_percentage(product['by_product_id'], product_price)
                    total_cost_for_product = product_gst_dict['product_cgst_value'] + product_gst_dict['product_sgst_value'] + product_price
                    by_sale_obj = BySale(
                        by_sale_group_id=by_sale_group_obj.id,
                        by_product_id=product['by_product_id'],
                        count=product_qty,
                        cost=product_price,
                        cgst_value=product_gst_dict['product_cgst_value'],
                        sgst_value=product_gst_dict['product_sgst_value'],
                        total_cost=total_cost_for_product,
                        ordered_by_id=request.user.id,
                        modified_by_id=request.user.id,
                    )
                    by_sale_obj.save()
                    total_cost += total_cost_for_product
                    is_order_placed = True
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
                    super_by_sale_group_obj.counter_amount = request.data['total_price']
                    super_by_sale_group_obj.counter_id = counter_id
                    super_by_sale_group_obj.order_sale_group_json = by_sale_df.to_dict('r')
                    super_by_sale_group_obj.save()
        
        print('crossed')
        by_sale_employee_order_obj = EmployeeOrderBySaleGroup.objects.get(id=request.data['order_sale_group_id'])
        by_sale_employee_order_obj.sale_status_id = 3
        by_sale_employee_order_obj.save()
        by_sale_employee_order_goods = EmployeeOrderBySaleGroupGatepass.objects.get(employeee_order_by_sale_group_id=by_sale_employee_order_obj.id)
        goods_receipt_mater = GoodsReceiptMaster(grn_number=generate_grn_code(),
                                        grn_date=datetime.datetime.now(),
                                        bill_number=by_sale_employee_order_goods.bill_number,
                                        bill_date=by_sale_employee_order_goods.bill_date,
                                        purchase_company_id=4, #employee
                                        po_number=by_sale_employee_order_obj.order_code,
                                        po_date=by_sale_employee_order_obj.ordered_date,
                                        dc_number=by_sale_employee_order_goods.dc_number,
                                        dc_date=by_sale_employee_order_goods.dc_date,
                                        created_by_id=request.user.id,
                                        modified_by_id=request.user.id,
                                        )
        goods_receipt_mater.save()
        print('crossed1')

        for product in request.data['return_product_list']:
            if not product['return_qty'] == 0 or product['return_qty'] == None:
                goods_receipt_record_obj = GoodsReceiptRecord(goods_receipt_master_id=goods_receipt_mater.id,
                                                            by_product_id=product['goods_product_id'],
                                                            quantity_at_receipt=product['return_qty'],
                                                            quantity_now=product['return_qty'],
                                                            quantity_now_time=datetime.datetime.now(),
                                                            price_per_unit=0,
                                                            price=0,
                                                            igst_value=0,
                                                            cgst_value=0,
                                                            sgst_value=0,
                                                            total_price=0,
                                                            expiry_date=product['expiry_date'],
                                                            goods_receipt_code=generate_batch_code(),
                                                            created_by_id=request.user.id,
                                                            modified_by_id=request.user.id,
                                                            )
                goods_receipt_record_obj.save()


                # add data to Main Stock
                if ByProductCurrentAvailablity.objects.filter(by_product_id=product['goods_product_id']).exists():
                    main_input_stock_obj = ByProductCurrentAvailablity.objects.get(by_product_id=product['goods_product_id'])
                    main_input_stock_obj.quantity_now = main_input_stock_obj.quantity_now + product['return_qty']
                    main_input_stock_obj.quantity_now_time = datetime.datetime.now()
                    main_input_stock_obj.modified_by_id = request.user.id
                    main_input_stock_obj.save()
                else:
                    main_input_stock_obj = ByProductCurrentAvailablity(by_product_id=product['goods_product_id'],
                                                        quantity_now=product['return_qty'],
                                                        quantity_now_time=datetime.datetime.now(),
                                                        created_by_id=request.user.id,
                                                        modified_by_id=request.user.id)
                    main_input_stock_obj.save()
        gst_number = '33AAAAT7787L2ZU'
        if not request.data['total_price'] == 0:
            dc_number = by_sale_employee_order_goods.dc_number
            bill_number = generate_bill_code()
            dc_date = by_sale_employee_order_goods.dc_date
            bill_date = datetime.datetime.now()
            by_sale_group_id = by_sale_group_obj.id
            sale_group_gatepass_obj = BySaleGroupGatepass(
                by_sale_group_id=by_sale_group_id,
                dc_number=dc_number,
                dc_date=dc_date,
                bill_number=bill_number,
                bill_date=bill_date,
                prepared_by=request.user,
                prepated_at=datetime.datetime.now()
            )
            bill_file_path = create_gate_pass_bill_for_employee_order(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number)
            sale_group_gatepass_obj.bill_file = bill_file_path
            sale_group_gatepass_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def create_gate_pass_bill_for_employee_order(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number):
    dc_date = datetime.datetime.strftime(dc_date, '%d-%m-%Y')
    bill_date = datetime.datetime.strftime(bill_date, '%d-%m-%Y')

    by_sale_group_obj = BySaleGroup.objects.get(id=by_sale_group_id)
    order_code = by_sale_group_obj.order_code
    order_date = by_sale_group_obj.ordered_date
    order_date = datetime.datetime.strftime(order_date, '%d-%m-%Y')
    business_obj = Business.objects.get(id=by_sale_group_obj.business.id)
    business_code = business_obj.code
    business_id = business_obj.id
    agent_first_name = BusinessAgentMap.objects.get(business_id=business_id).agent.first_name
    payment_option = 'Credit'

    by_sale_goods_obj = BySale.objects.filter(by_sale_group_id=by_sale_group_id)
    by_sale_goods_list = list(by_sale_goods_obj.values_list('id', 'by_product__display_ordinal', 'by_product__short_name', 'count', 'cost', 'cgst_value', 'sgst_value', 'total_cost'))
    by_sale_goods_column = ['id', 'display_ordinal', 'product_name', 'qty', 'cost', 'cgst_value', 'sgst_value', 'total_cost']
    by_sale_goods_df = pd.DataFrame(by_sale_goods_list, columns=by_sale_goods_column)
    by_sale_goods_df = by_sale_goods_df.sort_values(by=['display_ordinal'], ascending=True)
    by_sale_goods_df['s_no'] = range(1, 1+len(by_sale_goods_df))
    final_price = by_sale_goods_df['total_cost'].sum()

    file_name = str(business_code) + '_' + str(order_code) + '_bill.pdf'
    try:
        path = os.path.join('static/media/by_product/gate_pass/', str(business_code), str(order_code), 'bill')
        os.makedirs(path)
    except FileExistsError:
        print('already created')
    file_path = os.path.join(path, file_name)
    print(file_path)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(500, 830, str(payment_option) + ' Sale')
    mycanvas.drawCentredString(300, 810,
                            'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawString(40, 790, 'GST Number : ' + str(gst_number))
    mycanvas.drawCentredString(300, 790, 'Bill')
    mycanvas.line(250, 785, 350, 785)

    # Order Data
    mycanvas.drawString(40, 760, 'DC Number: ')
    mycanvas.drawString(130, 760, str(dc_number))
    mycanvas.drawString(40, 740, 'Bill Number: ')
    mycanvas.drawString(130, 740, str(bill_number))
    mycanvas.drawString(40, 720, 'Order Number: ')
    mycanvas.drawString(130, 720, str(order_code))
    mycanvas.drawString(40, 700, 'Booth Code: ')
    mycanvas.drawString(130, 700, str(business_code))

    mycanvas.drawString(340, 760, 'DC Date: ')
    mycanvas.drawString(430, 760, str(dc_date))
    mycanvas.drawString(340, 740, 'Bill Date: ')
    mycanvas.drawString(430, 740, str(bill_date))
    mycanvas.drawString(340, 720, 'Order Date: ')
    mycanvas.drawString(430, 720, str(order_date))
    mycanvas.drawString(340, 700, 'Agent Name: ')
    mycanvas.drawString(430, 700, str(agent_first_name))

    mycanvas.setStrokeColor(colors.black)

    # product list
    mycanvas.drawCentredString(300, 680, 'Product List')
    mycanvas.line(40, 670, 550, 670)
    mycanvas.drawString(48, 655, 'S. No')
    mycanvas.drawString(100, 655, 'Product')
    mycanvas.drawString(260, 655, 'Quantity')
    mycanvas.drawString(330, 655, 'Cost')
    mycanvas.drawString(390, 655, 'CGST')
    mycanvas.drawString(440, 655, 'SGST')
    mycanvas.drawString(490, 655, 'Total Cost')

    mycanvas.line(40, 650, 550, 650)
    y_point = 630
    mycanvas.setFont('Helvetica', 11)

    for index, product in by_sale_goods_df.iterrows():
        mycanvas.drawString(55, y_point, str(product['s_no']))
        mycanvas.drawString(90, y_point, str(product['product_name']))
        mycanvas.drawRightString(300, y_point, str(int(product['qty'])))
        mycanvas.drawRightString(360, y_point, str(product['cost']))
        mycanvas.drawRightString(420, y_point, str(product['cgst_value']))
        mycanvas.drawRightString(475, y_point, str(product['sgst_value']))
        mycanvas.drawRightString(545, y_point, str(product['total_cost']))

        y_point -=15
    mycanvas.line(40, y_point, 550, y_point)
    y_point -= 15
    mycanvas.drawRightString(460, y_point, 'Total')
    mycanvas.drawRightString(545, y_point, str(final_price))

    y_point += 15

    mycanvas.line(40, y_point, 40, 670)
    mycanvas.line(82, y_point, 82, 670)
    mycanvas.line(250, y_point, 250, 670)
    mycanvas.line(310, y_point, 310, 670)
    mycanvas.line(370, y_point, 370, 670)
    y_point -= 25
    mycanvas.line(430, y_point, 430, 670)
    mycanvas.line(480, y_point, 480, 670)
    mycanvas.line(550, y_point, 550, 670)
    mycanvas.line(430, y_point, 550, y_point)


    mycanvas.setFont('Helvetica', 12)

    y_point -= 70
    mycanvas.drawString(50, y_point, 'Signature of Recipient')
    mycanvas.drawString(445, y_point, 'Issuer Signature')

    mycanvas.save()
    return file_path



def serve_by_product_price_dict(user_profile_id):
    data_dict = {}
    business_obj = Business.objects.get(user_profile_id=user_profile_id)
    business_type_wise_price_obj = BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=business_obj.business_type_id)
    business_type_wise_price_list = list(business_type_wise_price_obj.values_list('id', 'business_type', 'by_product', 'base_price', 'mrp'))
    business_type_wise_price_column = ['id', 'business_type', 'by_product_id', 'base_price', 'mrp']
    business_type_wise_price_df = pd.DataFrame(business_type_wise_price_list, columns=business_type_wise_price_column)
    data_dict['product_price_dict'] = business_type_wise_price_df.groupby('by_product_id').apply(lambda x:x.to_dict('r')[0]).to_dict()
    order_category_dict = {}
    for map_obj in BusinessTypeOrderCategoryeMap.objects.filter(business_type_id=business_obj.business_type_id):
        if not map_obj.order_category.id in order_category_dict:
            order_category_dict[map_obj.order_category.id] = map_obj.payment_option.id
    data_dict['order_category'] = order_category_dict
    return data_dict

def generate_cash_receipt_code():
    code_bank_obj = CashReceiptCodeBank.objects.filter()[0]
    prefix_value = str(code_bank_obj.code_prefix)
    last_digit = int(code_bank_obj.last_digit)
    new_digit = last_digit + 1
    code_bank_obj.last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(6)
    return prefix_value + str(last_count)

def create_and_register_cash_receipt_after_order(by_sale_group_cash_receipt_id):
    by_sale_group_cash_receipt_obj = BySaleGroupCashReceipt.objects.get(id=by_sale_group_cash_receipt_id)
    by_sale_group_obj = BySaleGroup.objects.get(id=by_sale_group_cash_receipt_obj.by_sale_group_id)
    business_obj = by_sale_group_obj.business
    order_code = by_sale_group_obj.order_code
    agent_obj = Agent.objects.get(businessagentmap__business_id=business_obj.id)

    cash_receipt_account_obj = CashReceiptAccountPaymentMethodMap.objects.get(payment_method_id=by_sale_group_obj.payment_method_id)
    file_name = f"{order_code}-cash_receipt.pdf"
    file_path = os.path.join('static/media/by_product/gate_pass/', business_obj.code)
    try:
        path = file_path
        os.makedirs(path)
    except FileExistsError:
        print('already created')
        
    file_path = os.path.join(file_path, file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    img_file = os.path.join('static/media/',"logo.png")
    mycanvas.drawInlineImage(img_file, 30, 800,(.8*inch), (.320*inch))
    mycanvas.drawString(90, 800, str('(Coimbatore)'))
    mycanvas.drawCentredString(300, 800, str(by_sale_group_obj.payment_method.name))
    mycanvas.line(250, 795, 350, 795)
    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawString(380, 810, str('Phone : 2607951, 21982901, 2607971, 2208006'))
    mycanvas.drawString(380, 800, str('Marketing Office : 2545529, 2544777'))

    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 780,
                            'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')

    mycanvas.drawCentredString(300, 750, str('Head of Account: ') + str(cash_receipt_account_obj.cash_receipt_account_master.account_name))

    mycanvas.line(430, 760, 580, 760)
    mycanvas.line(430, 720, 580, 720)
    mycanvas.line(430, 760, 430, 720)
    mycanvas.line(580, 760, 580, 720)
    mycanvas.line(580, 760, 580, 720)

    mycanvas.drawString(435, 740, str('Code'))
    mycanvas.drawString(440, 728, str('No.'))

    mycanvas.line(470, 760, 470, 720)

    mycanvas.drawString(475, 745, str('Main'))
    mycanvas.line(470, 738, 580, 738)
    mycanvas.drawString(475, 726, str('Sub'))
    mycanvas.line(505, 760, 505, 720)
    mycanvas.drawString(515, 745, str(cash_receipt_account_obj.cash_receipt_account_master.account_code))
    mycanvas.drawString(515, 726, str(business_obj.code))

    mycanvas.drawString(30, 700, str('No : ') + str(by_sale_group_cash_receipt_obj.receipt_number))
    date_in_format = datetime.datetime.strftime(by_sale_group_obj.ordered_date, '%d-%m-%Y')
    mycanvas.drawString(480, 700, str('Date : ') + date_in_format)
    mycanvas.drawString(100, 670, str('Received from'))
    mycanvas.setFont('Helvetica-Bold', 12)
    mycanvas.drawString(180, 670, str(agent_obj.first_name))
    mycanvas.setFont('Helvetica', 12)
    amount = by_sale_group_obj.total_cost
    words = num2words(amount, lang='en_IN')
    mycanvas.drawString(30, 640, 'the sum of ')
    mycanvas.setFont('Helvetica-Bold', 12)
    string_for_second_line = f"Rs. {amount} ({words.capitalize()} only)"
    mycanvas.drawString(90, 640, str(string_for_second_line))
    mycanvas.setFont('Helvetica', 12)

    mycanvas.drawString(30, 610, str('towards supply of byproduct.'))

    mycanvas.drawCentredString(300, 500, 'Session Asst                                       Cashier                                       General Manager')

    mycanvas.save()
    by_sale_group_cash_receipt_obj.receipt_file = file_path
    by_sale_group_cash_receipt_obj.save()
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



@transaction.atomic
@api_view(['POST'])
def register_order_for_by_product_agent(request):
    sid = transaction.savepoint()
    try:
        if request.data['from'] == 'portal':
            business_agent_obj = BusinessAgentMap.objects.get(business__code=request.data['business_code'])
            business_type_id = business_agent_obj.business.business_type.id
            user_profile_id = business_agent_obj.business.user_profile_id
            agent_id = business_agent_obj.agent_id
            agent_user_id = business_agent_obj.business.user_profile.user.id
            business_id = business_agent_obj.business.id
            via_id = 2
        elif request.data['from'] == 'mobile':
            business_id = Business.objects.get(user_profile__user_id=request.user.id).id
            business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
            business_type_id = business_agent_obj.business.business_type.id
            user_profile_id = business_agent_obj.business.user_profile_id
            agent_id = business_agent_obj.agent_id
            agent_user_id = business_agent_obj.business.user_profile.user.id
            via_id = 1
        elif request.data['from'] == 'website':
            business_id = Business.objects.get(user_profile__user_id=request.user.id).id
            business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
            business_type_id = business_agent_obj.business.business_type.id
            user_profile_id = business_agent_obj.business.user_profile_id
            agent_id = business_agent_obj.agent_id
            agent_user_id = business_agent_obj.business.user_profile.user.id
            via_id = 3
        today = datetime.datetime.now()
        data_dict = serve_by_product_price_dict(user_profile_id)
        product_price_dict = data_dict['product_price_dict']
        order_category_dict = data_dict['order_category']
        order_category_id = 2
        agent_wallet_obj = ByProductAgentWallet.objects.get(agent_id=agent_id)
        counter_id = None
        is_order_placed = False
        order_code = generate_by_product_order_code()
        total_cost = 0
        if not request.data['final_price_before_wallet'] == 0:
            by_sale_group_obj = BySaleGroup(
                business_id=business_id,
                order_code=order_code,
                zone_id=business_agent_obj.business.zone.id,
                ordered_date=today,
                ordered_via_id=via_id,
                value_before_round_off=0,
                round_off_value=0,
                total_cost=0,
                sale_status_id=1, #ordered
                ordered_by_id=request.user.id,
                modified_by_id=request.user.id,
                payment_method_id=request.data['payment_method_id'],
                payment_status_id=1
            )
            by_sale_group_obj.save()
            super_by_sale_group_obj = BySaleGroupTransactionTrace(
                by_sale_group_id=by_sale_group_obj.id,
                sale_group_order_type_id=1,
            )
            super_by_sale_group_obj.save()
            
            for product in request.data['selected_product_list']:
                product_qty = product['entered_qty']
                current_product_availablity = ByProductCurrentAvailablity.objects.get(by_product_id=product['product_id'])
                if product_qty != 0 and product_qty != None:
                    if product_qty <= current_product_availablity.quantity_now:
                        product_base_price = product_qty * product_price_dict[product['product_id']]['base_price']
                        product_mrp = product_qty * product_price_dict[product['product_id']]['mrp']
                        product_gst_dict = calculate_gst_value(product_base_price, product_mrp, product_qty)
                        by_sale_obj = BySale(
                            by_sale_group_id=by_sale_group_obj.id,
                            by_product_id=product['product_id'],
                            count=product_qty,
                            cost=product_base_price,
                            cgst_value=product_gst_dict['product_cgst_value'],
                            sgst_value=product_gst_dict['product_sgst_value'],
                            total_cost=product_mrp,
                            ordered_by_id=request.user.id,
                            modified_by_id=request.user.id,
                        )
                        by_sale_obj.save()
                        daily_goods_receipt_record_obj = GoodsReceiptRecordForDaily.objects.filter(by_product_id=by_sale_obj.by_product.id, sale_date=today).exclude(quantity_now=0).order_by('id')
                        required_qty = product_qty
                        for goods in daily_goods_receipt_record_obj:
                            if goods.quantity_now >= required_qty:
                                balance_in_goods = goods.quantity_now - Decimal(required_qty)
                                goods.quantity_now = balance_in_goods
                                goods.quantity_now_time = datetime.datetime.now()
                                goods.save()

                                goods_receipt_record_sale_map_obj = DailyGoodsReceiptRecordBySaleMap(
                                    daily_goods_receipt_record_id=goods.id,
                                    by_sale_id=by_sale_obj.id,
                                    quantity_dispatched=required_qty
                                )
                                goods_receipt_record_sale_map_obj.save()
                                break
                            else:
                                required_qty = Decimal(required_qty) - goods.quantity_now
                                goods_receipt_record_sale_map_obj = DailyGoodsReceiptRecordBySaleMap(
                                    daily_goods_receipt_record_id=goods.id,
                                    by_sale_id=by_sale_obj.id,
                                    quantity_dispatched=required_qty
                                )
                                goods_receipt_record_sale_map_obj.save()

                                goods.quantity_now = 0
                                goods.quantity_now_time = datetime.datetime.now()
                                goods.save()


                        if BusinessWiseDailySaleUpdate.objects.filter(sale_date=today, business_id=business_id, by_product_id=product['product_id']).exists():
                            business_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=today, business_id=business_id, by_product_id=product['product_id'])
                            business_sale_obj.received_quantity = business_sale_obj.received_quantity + product_qty
                            business_sale_obj.save()
                        else:
                            is_yesterday_sale_closed = False
                            if BusinessWiseDailySaleUpdate.objects.filter(sale_date__lt=today, business_id=business_id, by_product_id=product['product_id']).exists():
                                business_sale_obj = BusinessWiseDailySaleUpdate.objects.filter(sale_date__lt=today, business_id=business_id, by_product_id=product['product_id']).order_by('sale_date')[0]
                                if business_sale_obj.closing_quantity is not None:
                                    is_yesterday_sale_closed = True
                            else:
                                is_yesterday_sale_closed = True
                            business_sale_obj = BusinessWiseDailySaleUpdate(business_id=business_id,
                                                                           sale_date=today,
                                                                           by_product_id=product['product_id'],
                                                                           received_quantity=product_qty,
                                                                           created_by_id=request.user.id,
                                                                           is_yesterday_sale_closed=is_yesterday_sale_closed,
                                                                           updated_by_id=request.user.id)
                            business_sale_obj.save()
                        current_product_availablity.quantity_now = current_product_availablity.quantity_now - product_qty
                        current_product_availablity.quantity_now_time = today
                        current_product_availablity.save()
                        total_cost += product_mrp
                        is_order_placed = True
                    else:
                        error_dict = {}
                        error_dict['product_name'] = current_product_availablity.by_product.short_name
                        error_dict['required_qty'] = product_qty
                        error_dict['available_qty'] = current_product_availablity.quantity_now
                        transaction.savepoint_rollback(sid)
                        return Response(data=error_dict, status=status.HTTP_400_BAD_REQUEST)
            value_before_round_off = total_cost
            value_after_round_off = math.ceil(value_before_round_off)
            round_off_value = value_after_round_off - value_before_round_off
            saved_by_sale_group_obj = BySaleGroup.objects.get(id=by_sale_group_obj.id)
            saved_by_sale_group_obj.value_before_round_off = value_before_round_off
            saved_by_sale_group_obj.round_off_value = round_off_value
            saved_by_sale_group_obj.total_cost = value_after_round_off
            saved_by_sale_group_obj.save()
            by_sale_group_cash_receipt_obj = BySaleGroupCashReceipt(by_sale_group_id=saved_by_sale_group_obj.id,
                                                                    receipt_date=today,
                                                                    receipt_number=generate_cash_receipt_code(),
                                                                    prepared_by_id=request.user.id,
                                                                    prepated_at=today)
            by_sale_group_cash_receipt_obj.save()
            if request.data['from'] == 'portal':
                employee_id = Employee.objects.get(user_profile__user=request.user).id
                if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                            collection_date=today).exists():
                    counter_employee_trace_obj = \
                    CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                            collection_date=today)[0]
                    counter_id = counter_employee_trace_obj.counter.id
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
            else:
                employee_id = 3
                counter_id = 23
                if order_category_dict[order_category_id] == 1: 
                    if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                collection_date=today).exists():
                        counter_employee_trace_obj = \
                            CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                                    collection_date=today)[0]
                    else:
                        counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=23,
                                                                                employee_id=employee_id,
                                                                                collection_date=today,
                                                                                start_date_time=today)
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
        if is_order_placed:
            by_sale_obj = BySale.objects.filter(by_sale_group_id=by_sale_group_obj.id)
            by_sale_list = list(by_sale_obj.values_list('id', 'by_product_id', 'count'))
            by_sale_column = ['id', 'product_id', 'count']
            by_sale_df = pd.DataFrame(by_sale_list, columns=by_sale_column)
            if not by_sale_df is None:
                if not super_by_sale_group_obj is None:
                    super_by_sale_group_obj.counter_amount = request.data['final_price']
                    super_by_sale_group_obj.counter_id = counter_id
                    super_by_sale_group_obj.order_sale_group_json = by_sale_df.to_dict('r')
                    super_by_sale_group_obj.save()
        if request.data['final_wallet'] is not None:
            if request.data['final_wallet'] < agent_wallet_obj.current_balance:
                transaction_obj = ByProductTransactionLog(
                    date=today,
                    transacted_by_id=agent_user_id,
                    transacted_via_id=via_id,
                    data_entered_by=request.user,
                    amount=agent_wallet_obj.current_balance - Decimal(request.data['final_wallet']),
                    transaction_direction_id=2,  # from agent wallet to aavin
                    transaction_mode_id=1,  # Upi
                    transaction_status_id=2,  # completed
                    transaction_id='1234',
                    transaction_approval_status_id=1,  # Accepted
                    transaction_approved_by_id=1,
                    transaction_approved_time=today,
                    wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=request.data['final_wallet'],
                    description='Amount for ordering the By product from agent wallet',
                    modified_by=request.user
                )
                transaction_obj.save()
                agent_wallet_obj.current_balance = request.data['final_wallet']
                agent_wallet_obj.save()
                if not super_by_sale_group_obj is None:
                    super_by_sale_group_obj.is_wallet_used = True
                    super_by_sale_group_obj.wallet_amount = transaction_obj.amount
                    super_by_sale_group_obj.wallet_transaction_id = transaction_obj.id
                    super_by_sale_group_obj.save()
        if order_category_dict[order_category_id] == 1:
            if request.data['final_price'] != 0:
                transaction_obj = ByProductTransactionLog(
                    date=today,
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
                    transaction_approved_time=today,
                    wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                    wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                    description='Amount for ordering the by product',
                    modified_by=request.user
                )
                transaction_obj.save()
                if not super_by_sale_group_obj is None:
                    super_by_sale_group_obj.counter_transaction_id = transaction_obj.id
                    super_by_sale_group_obj.save()
        document = create_and_register_cash_receipt_after_order(by_sale_group_cash_receipt_obj.id)
        transaction.savepoint_commit(sid)
        return Response(data=document, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
def create_encrypeted_string_and_make_request_for_by_product(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        business_id = Business.objects.get(user_profile__user_id=request.user.id).id
        business_agent_obj = BusinessAgentMap.objects.get(business_id=business_id)
        business_type_id = business_agent_obj.business.business_type.id
        user_profile_id = business_agent_obj.business.user_profile_id
        agent_id = business_agent_obj.agent_id
        agent_user_id = business_agent_obj.business.user_profile.user.id
        business_obj = business_agent_obj.business
        if request.data['from'] == 'mobile':
            via_id = 1
        else:
            via_id = 3
        data_dict = serve_by_product_price_dict(user_profile_id)
        product_price_dict = data_dict['product_price_dict']
        order_category_dict = data_dict['order_category']
        order_category_id = 2
        agent_wallet_obj = ByProductAgentWallet.objects.get(agent_id=agent_id)
        order_code = generate_temp_by_product_order_code()
        product_shot_name_for_transaction = ''
        temp_by_sale_group_list = []
        if not request.data['final_price_before_wallet'] == 0:
            total_cost = 0
            temp_by_sale_group_obj = TempBySaleGroup(
                business_id=business_id,
                order_code=order_code,
                zone_id=business_agent_obj.business.zone.id,
                ordered_date=datetime.datetime.now(),
                ordered_via_id=via_id,
                total_cost=0,
                sale_status_id=1, #ordered
                ordered_by_id=request.user.id,
                modified_by_id=request.user.id,
                payment_status_id=1
            )
            temp_by_sale_group_obj.save()
            for product in request.data['selected_product_list']:
                product_qty = product['entered_qty']
                if product_qty != 0 and product_qty != None :
                    product_price = product_qty * product_price_dict[product['product_id']]['price']
                    by_sale_obj = TempBySale(
                        temp_by_sale_group_id=temp_by_sale_group_obj.id,
                        by_product_id=product['product_id'],
                        count=product_qty,
                        cost=product_price,
                        ordered_by_id=request.user.id,
                        modified_by_id=request.user.id,
                    )
                    by_sale_obj.save()
                    product_shot_name_for_transaction = product_shot_name_for_transaction + product['short_name'] + ','
                    total_cost += product_price
            saved_temp_by_sale_group_obj = TempBySaleGroup.objects.get(id=temp_by_sale_group_obj.id)
            saved_temp_by_sale_group_obj.total_cost = total_cost
            saved_temp_by_sale_group_obj.save()
            temp_by_sale_group_list.append(saved_temp_by_sale_group_obj.id)
        
        # payment gateway work started
        rid = generate_rid_code()
        if request.data['final_price'] != 0:
            transaction_obj = ByProductTransactionLog(
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
                description='Amount for ordering the by product',
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
        ppi_parameter_dict['salegroup_id'] = temp_by_sale_group_list[0]
        ppi_parameter_dict['product_list'] = product_shot_name_for_transaction[:50]
        ppi_parameter_dict['user_code'] = request.user.id
        ppi_parameter_dict['device_type'] = request.data['from']
        ppi_parameter_dict['amount'] = request.data['final_price']

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
                                            payment_request_for_id=5,
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
        if request.data['final_wallet'] < agent_wallet_obj.current_balance:
            payment_request_obj.is_wallet_selected = True
            payment_request_obj.wallet_balance_after_this_transaction = request.data['final_wallet']
        payment_request_obj.save()

        # payement request PPI
        for parameter in ppi_parameter_list:
            payment_request_ppi = PaymentRequestPPI(payment_request=payment_request_obj,
                                                    key=parameter,
                                                    value=ppi_parameter_dict[parameter]
                                                    )
            payment_request_ppi.save()

        # link temp_salegroup with payment request
        temp_sale_group_payment_request_map = BySaleGroupPaymentRequestMap(payment_request_id=payment_request_obj.id)
        temp_sale_group_payment_request_map.save()
        for sale_group_id in temp_by_sale_group_list:
            temp_sale_group_payment_request_map.temp_sale_group.add(sale_group_id)
        temp_sale_group_payment_request_map.save()

        # payment_request_inditated
        payment_request_user_map = PaymentRequestUserMap(payment_request_id=payment_request_obj.id,
                                                        payment_intitated_by_id=request.user.id)
        payment_request_user_map.save()
        # identificaiton_token_responce = requests.get('https://easypay.axisbank.co.in/api/generateToken')
        # token_from_pg = identificaiton_token_responce.json()['token']
        # print(token_from_pg)
        token_from_pg = 'SKTcRfXx4YCmpIkEgn2F4pipCKtqqGQCsGXiira6oaEA2s6qh4nZuZy5mxtn81AH'
        data_dict = {
            'encrypted_string': encrypted_string,
            'token': token_from_pg
        }
        print(encrypted_string)
        transaction.savepoint_commit(sid)
        return Response(data=data_dict, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def serve_by_product_order_history_for_selected_date_range(request):
    to_date = request.data['to_date']
    from_date = request.data['from_date']
    agent_sale_obj = BySale.objects.filter(by_sale_group__ordered_date__gte=from_date, by_sale_group__ordered_date__lte=to_date, by_sale_group__business__user_profile__user_id=request.user.id)
    agent_sale_list = list(agent_sale_obj.values_list('id', 'by_product_id', 'by_product__short_name', 'count', 'cost', 'by_sale_group__total_cost', 'by_sale_group__ordered_date', 'by_sale_group'))
    agent_sale_column = ['id', 'by_product_id', 'product_short_name', 'count', 'price', 'total_cost', 'ordered_date', 'by_sale_group_id']
    agent_sale_df = pd.DataFrame(agent_sale_list, columns=agent_sale_column)
    grouped_based_on_sale_group_id_frame = agent_sale_df.groupby('by_sale_group_id').apply(lambda x:x.to_dict('r')).to_frame().reset_index()

    agent_sale_df = agent_sale_df.groupby('by_sale_group_id').agg({'ordered_date':'first', 'total_cost': 'first'}).reset_index()

    final_df = agent_sale_df.merge(grouped_based_on_sale_group_id_frame, how='left', left_on='by_sale_group_id', right_on='by_sale_group_id')
    final_df = final_df.rename(columns={0: 'product_list'})
    final_df = final_df.sort_values(by=['by_sale_group_id'], ascending=False)
    return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_transaction_log_data_for_by_product_order(request):
    today_datetime = datetime.datetime.now()
    before_one_month_date = today_datetime - datetime.timedelta(days=1)
    transaction_log_obj = ByProductTransactionLog.objects.filter(transacted_by=request.user.id, date__gte=before_one_month_date,
                                                        date__lte=today_datetime).order_by('-id')
    transaction_log_list = list(
        transaction_log_obj.values_list('id', 'transacted_by', 'transaction_status', 'transaction_status__name',
                                        'amount', 'transaction_direction', 'transaction_direction__description', 'transaction_id',
                                        'wallet_balance_before_this_transaction',
                                        'wallet_balance_after_transaction_approval', 'time_created'))
    transaction_log_column = ['id', 'transacted_by', 'transaction_status_id', 'transaction_status_name',
                            'amount', 'transaction_direction_id', 'transaction_direction_description',
                            'transaction_id', 'wallet_balance_before',
                            'wallet_balance_after', 'time_created']
    transaction_log_df = pd.DataFrame(transaction_log_list, columns=transaction_log_column)
    transaction_log_dict = transaction_log_df.groupby('id').apply(lambda x:x.to_dict('r')[0]).to_dict()
    super_sale_group_transaction_obj = BySaleGroupTransactionTrace.objects.filter(by_sale_group__business__user_profile__user_id=request.user.id)
    super_sale_group_transaction_list = list(super_sale_group_transaction_obj.values_list('id', 'by_sale_group', 'bank_transaction', 'wallet_transaction', 'counter_transaction', 'wallet_return_transaction', 'by_sale_group__ordered_date', 'by_sale_group__total_cost'))
    super_sale_group_transaction_column = ['id', 'by_sale_group_id',  'bank_transaction_id', 'wallet_transaction_id', 'counter_transaction_id', 'wallet_return_transaction_id', 'ordered_date', 'total_cost']
    super_sale_group_transaction_df = pd.DataFrame(super_sale_group_transaction_list, columns=super_sale_group_transaction_column)
    super_sale_group_transaction_df = super_sale_group_transaction_df.fillna(0)
    super_sale_group_transaction_df = super_sale_group_transaction_df.sort_values(by=['by_sale_group_id'], ascending=False)
    transaction_list = []
    for index, row in super_sale_group_transaction_df.iterrows():
        data_dict = {
            'sale_date': row['ordered_date'],
            'total_cost': row['total_cost'],
            'transaction_list': []
        }
        if not row['bank_transaction_id'] == 0:
            data_dict['transaction_list'].append(row['bank_transaction_id'])
        if not row['wallet_transaction_id'] == 0:
            data_dict['transaction_list'].append(row['wallet_transaction_id'])
        if not row['counter_transaction_id'] == 0:
            data_dict['transaction_list'].append(row['counter_transaction_id'])
        if not row['wallet_return_transaction_id'] == 0:
            data_dict['transaction_list'].append(row['wallet_return_transaction_id'])
        transaction_list.append(data_dict)

    business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user_id=request.user.id)
    agent_wallet_obj = ByProductAgentWallet.objects.get(agent_id=business_agent_obj.agent.id)
    data_dict = {
        'wallet_balance': agent_wallet_obj.current_balance,
        'transaction_dict': transaction_log_dict,
        'transaction_list': transaction_list
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_order_category_for_order(request):
    if request.data['from'] == 'portal':
        business_agent_obj = BusinessAgentMap.objects.get(business__code=request.data['business_code'])
    else:
        business_agent_obj = BusinessAgentMap.objects.get(business__user_profile__user=request.user)
    order_category_dict = {}
    for map_obj in BusinessTypeOrderCategoryeMap.objects.filter(business_type_id=business_agent_obj.business.business_type_id):
        if not map_obj.order_category.id in order_category_dict:
            order_category_dict[map_obj.order_category.id] = map_obj.payment_option.id
    return Response(data=order_category_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_by_product_order_list_for_gatepass(request):
    print(datetime.datetime.now().date())
    if BySale.objects.filter(Q(by_sale_group__sale_status_id=1) | Q(by_sale_group__sale_status_id=2) & Q(by_sale_group__ordered_date=datetime.datetime.now().date())).exists():
        by_product_order_obj = BySale.objects.filter(Q(by_sale_group__sale_status_id=1) | Q(by_sale_group__sale_status_id=2) & Q(by_sale_group__ordered_date=datetime.datetime.now().date()))
        by_product_order_list = list(by_product_order_obj.values_list('by_sale_group', 'by_sale_group__ordered_date', 'by_sale_group__total_cost', 'by_sale_group__business__code', 'by_sale_group__business__business_type_id', 'by_sale_group__business__businessagentmap__agent__first_name', 'by_product', 'by_product__short_name', 'count', 'total_cost', 'by_sale_group__ordered_via__name', 'by_sale_group__sale_status', 'by_sale_group__time_created'))
        by_product_order_column = ['by_sale_group_id', 'ordered_date', 'total_cost', 'business_code', 'business_type_id', 'agent_name', 'by_product_id', 'by_product_name', 'count', 'cost', 'ordered_via', 'sale_status_id', 'time_created']
        by_product_order_df = pd.DataFrame(by_product_order_list, columns=by_product_order_column)
        grouped_by_sale_group_df = by_product_order_df.groupby('by_sale_group_id').agg({'total_cost': 'first', 'business_code': 'first', 'agent_name': 'first', 'ordered_via': 'first', 'ordered_date': 'first', 'sale_status_id': 'first', 'business_type_id': 'first', 'time_created': 'first'}).reset_index()
        grouped_by_product_df = by_product_order_df.groupby('by_sale_group_id').apply(lambda x: x.to_dict('r')).to_frame().reset_index()
        by_product_sale_df = grouped_by_sale_group_df.merge(grouped_by_product_df, how="left", left_on="by_sale_group_id", right_on="by_sale_group_id")
        by_product_sale_df = by_product_sale_df.rename(columns={0: 'product_list'})
        by_product_sale_df['is_for'] = 'Agent'
    else:
        by_product_sale_df = pd.DataFrame()

    if EmployeeOrderBySale.objects.filter(Q(employeee_order_by_sale_group__sale_status_id=1) | Q(employeee_order_by_sale_group__sale_status_id=2) & Q(employeee_order_by_sale_group__ordered_date=datetime.datetime.now().date())).exists():
        employee_order_by_product_order_obj = EmployeeOrderBySale.objects.filter(Q(employeee_order_by_sale_group__sale_status_id=1) | Q(employeee_order_by_sale_group__sale_status_id=2) & Q(employeee_order_by_sale_group__ordered_date=datetime.datetime.now().date()))
        employee_order_by_product_order_list = list(employee_order_by_product_order_obj.values_list('employeee_order_by_sale_group', 'employeee_order_by_sale_group__ordered_date', 'employeee_order_by_sale_group__total_cost', 'employeee_order_by_sale_group__business__code', 'employeee_order_by_sale_group__business__business_type_id', 'employeee_order_by_sale_group__business__businessagentmap__agent__first_name', 'by_product', 'by_product__short_name', 'count', 'total_cost', 'employeee_order_by_sale_group__ordered_via__name', 'employeee_order_by_sale_group__sale_status', 'employeee_order_by_sale_group__time_created'))
        employee_order_by_product_order_column = ['by_sale_group_id', 'ordered_date', 'total_cost', 'business_code', 'business_type_id',  'agent_name', 'by_product_id', 'by_product_name', 'count', 'cost', 'ordered_via', 'sale_status_id', 'time_created']
        employee_order_by_product_order_df = pd.DataFrame(employee_order_by_product_order_list, columns=employee_order_by_product_order_column)
        employee_order_grouped_by_sale_group_df = employee_order_by_product_order_df.groupby('by_sale_group_id').agg({'total_cost': 'first', 'business_code': 'first', 'agent_name': 'first', 'ordered_via': 'first', 'ordered_date': 'first', 'sale_status_id': 'first', 'business_type_id': 'first', 'time_created': 'first'}).reset_index()
        employee_order_grouped_by_product_df = employee_order_by_product_order_df.groupby('by_sale_group_id').apply(lambda x: x.to_dict('r')).to_frame().reset_index()
        employee_order_final_df = employee_order_grouped_by_sale_group_df.merge(employee_order_grouped_by_product_df, how="left", left_on="by_sale_group_id", right_on="by_sale_group_id")
        employee_order_final_df = employee_order_final_df.rename(columns={0: 'product_list'})
        employee_order_final_df['is_for'] = 'Employee'
    else:
        employee_order_final_df = pd.DataFrame()
    final_df = pd.concat([by_product_sale_df, employee_order_final_df])
    
    if not final_df.empty:
        final_df = final_df.sort_values(by=['time_created'], ascending=False)
        data = final_df.to_dict('r')
    else:
        data = []
    return Response(data=data, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_by_product_order_list_for_employee(request):
    by_product_order_obj = EmployeeOrderBySale.objects.filter(employeee_order_by_sale_group__sale_status_id=2, employeee_order_by_sale_group__business__code=request.data['business_code']).order_by('employeee_order_by_sale_group__ordered_date')
    by_product_order_list = list(by_product_order_obj.values_list('employeee_order_by_sale_group', 'employeee_order_by_sale_group__ordered_date', 'employeee_order_by_sale_group__total_cost', 'employeee_order_by_sale_group__business__code', 'employeee_order_by_sale_group__business__businessagentmap__agent__first_name', 'by_product', 'by_product__short_name', 'count', 'total_cost', 'employeee_order_by_sale_group__ordered_via__name', 'employeee_order_by_sale_group__sale_status'))
    by_product_order_column = ['by_sale_group_id', 'ordered_date', 'total_cost', 'business_code', 'agent_name', 'by_product_id', 'by_product_name', 'count', 'cost', 'ordered_via', 'sale_status_id']
    by_product_order_df = pd.DataFrame(by_product_order_list, columns=by_product_order_column)
    if not by_product_order_df.empty:
        grouped_by_sale_group_df = by_product_order_df.groupby('by_sale_group_id').agg({'total_cost': 'first', 'business_code': 'first', 'agent_name': 'first', 'ordered_via': 'first', 'ordered_date': 'first', 'sale_status_id': 'first'}).reset_index()
        grouped_by_product_df = by_product_order_df.groupby('by_sale_group_id').apply(lambda x: x.to_dict('r')).to_frame().reset_index()
        final_df = grouped_by_sale_group_df.merge(grouped_by_product_df, how="left", left_on="by_sale_group_id", right_on="by_sale_group_id")
        final_df = final_df.rename(columns={0: 'product_list'})
    else:
        final_df = by_product_order_df
    return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_by_product_order_list_for_selected_business(request):
    by_product_order_obj = BySale.objects.filter(by_sale_group__sale_status_id=2, by_sale_group__business__code=request.data['business_code'])
    by_product_order_list = list(by_product_order_obj.values_list('by_sale_group', 'by_sale_group__ordered_date', 'by_sale_group__total_cost', 'by_sale_group__business__code', 'by_sale_group__business__business_type_id','by_sale_group__business__businessagentmap__agent__first_name', 'by_product', 'by_product__short_name', 'count', 'total_cost', 'by_sale_group__ordered_via__name', 'by_sale_group__sale_status'))
    by_product_order_column = ['by_sale_group_id', 'ordered_date', 'total_cost', 'business_code', 'business_type_id', 'agent_name', 'by_product_id', 'by_product_name', 'count', 'cost', 'ordered_via', 'sale_status_id']
    by_product_order_df = pd.DataFrame(by_product_order_list, columns=by_product_order_column)
    if not by_product_order_df.empty:
        grouped_by_sale_group_df = by_product_order_df.groupby('by_sale_group_id').agg({'total_cost': 'first', 'business_code': 'first', 'agent_name': 'first', 'ordered_via': 'first', 'ordered_date': 'first', 'sale_status_id': 'first', 'business_type_id': 'first'}).reset_index()
        grouped_by_product_df = by_product_order_df.groupby('by_sale_group_id').apply(lambda x: x.to_dict('r')).to_frame().reset_index()
        final_df = grouped_by_sale_group_df.merge(grouped_by_product_df, how="left", left_on="by_sale_group_id", right_on="by_sale_group_id")
        final_df = final_df.rename(columns={0: 'product_list'})
    else:
        final_df = by_product_order_df
    return Response(data=final_df.to_dict('r'), status=status.HTTP_200_OK)


def generate_bill_code():
    code_bank_obj = GatepassBillCodeBank.objects.filter()[0]
    current_date = datetime.datetime.now().date()
    prefix_value = str(code_bank_obj.code_prefix) + '_' +  str((current_date.year))[2:]
    last_digit = int(code_bank_obj.last_digit)
    new_digit = last_digit + 1
    code_bank_obj.last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(4)
    return prefix_value + str(last_count)


def generate_dc_code():
    code_bank_obj = GatepassDCCodeBank.objects.filter()[0]
    current_date = datetime.datetime.now().date()
    prefix_value = str(code_bank_obj.code_prefix) + '_' +  str((current_date.year))[2:] 
    last_digit = int(code_bank_obj.last_digit)
    new_digit = last_digit + 1
    code_bank_obj.last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(4)
    return prefix_value + str(last_count)


def create_gate_pass_temp_dc_for_employee_order(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number):
    dc_date = datetime.datetime.strftime(dc_date, '%d-%m-%Y')
    bill_date = datetime.datetime.strftime(bill_date, '%d-%m-%Y')

    by_sale_group_obj = EmployeeOrderBySaleGroup.objects.get(id=by_sale_group_id)
    order_code = by_sale_group_obj.order_code
    order_date = by_sale_group_obj.ordered_date
    order_date = datetime.datetime.strftime(order_date, '%d-%m-%Y')
    business_obj = Business.objects.get(id=by_sale_group_obj.business.id)
    business_code = business_obj.code
    business_id = business_obj.id
    agent_first_name = BusinessAgentMap.objects.get(business_id=business_id).agent.first_name
    # payment_option = BusinessTypeOrderCategoryeMap.objects.get(order_category_id=2, business_type_id=business_obj.business_type_id).payment_option.name
    payment_option = by_sale_group_obj.payment_method.name
    
    by_sale_goods_obj = GoodsReceiptRecordEmployeeOrderBySaleMap.objects.filter(employee_order_by_sale__employeee_order_by_sale_group_id=by_sale_group_id)
    by_sale_goods_list = list(by_sale_goods_obj.values_list('id', 'employee_order_by_sale__by_product__display_ordinal', 'employee_order_by_sale__by_product__short_name', 'goods_receipt_record__expiry_date', 'quantity_dispatched', 'cost', 'cgst_value', 'sgst_value', 'total_cost'))
    by_sale_goods_column = ['id', 'display_ordinal', 'product_name', 'expiry_date', 'qty', 'cost', 'cgst_value', 'sgst_value', 'total_cost']
    by_sale_goods_df = pd.DataFrame(by_sale_goods_list, columns=by_sale_goods_column)
    by_sale_goods_df = by_sale_goods_df.sort_values(by=['display_ordinal', 'expiry_date'], ascending=True)
    by_sale_goods_df['s_no'] = range(1, 1+len(by_sale_goods_df))
    by_sale_goods_df['expiry_date'] = pd.to_datetime(by_sale_goods_df['expiry_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%d-%m-%Y')
    final_price = by_sale_goods_df['total_cost'].sum()
        
    # file creation
    file_name = str(business_code) + '_' + str(order_code) + '_temp_dc.pdf'
    try:
        path = os.path.join('static/media/by_product/gate_pass/', str(business_code), str(order_code), 'temp_dc')
        os.makedirs(path)
    except FileExistsError:
        print('already created')
    file_path = os.path.join(path, file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(500, 830, str(payment_option) + ' Sale')
    mycanvas.drawCentredString(300, 810,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawString(40, 790, 'GST Number : ' + str(gst_number))
    mycanvas.drawCentredString(300, 790, 'Temp DC')
    mycanvas.line(250, 785, 350, 785)
    
    # Order Data
    mycanvas.drawString(40, 760, 'DC Number: ')
    mycanvas.drawString(130, 760, str(dc_number))
    mycanvas.drawString(40, 740, 'Bill Number: ')
    mycanvas.drawString(130, 740, str(bill_number))
    mycanvas.drawString(40, 720, 'Order Number: ')
    mycanvas.drawString(130, 720, str(order_code))
    mycanvas.drawString(40, 700, 'Booth Code: ')
    mycanvas.drawString(130, 700, str(business_code))
    
    mycanvas.drawString(340, 760, 'DC Date: ')
    mycanvas.drawString(430, 760, str(dc_date))
    mycanvas.drawString(340, 740, 'Bill Date: ')
    mycanvas.drawString(430, 740, str(bill_date))
    mycanvas.drawString(340, 720, 'Order Date: ')
    mycanvas.drawString(430, 720, str(order_date))
    mycanvas.drawString(340, 700, 'Agent Name: ')
    mycanvas.drawString(430, 700, str(agent_first_name))
    
    mycanvas.setStrokeColor(colors.black)

    # product list
    mycanvas.drawCentredString(300, 680, 'Product List')
    mycanvas.line(40, 670, 550, 670)
    mycanvas.drawString(48, 655, 'S. No')
    mycanvas.drawString(100, 655, 'Product')
    mycanvas.drawString(200, 655, 'Expiry')
    mycanvas.drawString(260, 655, 'Quantity')
    mycanvas.drawString(330, 655, 'Cost')
    mycanvas.drawString(390, 655, 'CGST')
    mycanvas.drawString(440, 655, 'SGST')
    mycanvas.drawString(490, 655, 'Total Cost')

    mycanvas.line(40, 650, 550, 650)
    y_point = 630
    mycanvas.setFont('Helvetica', 11)

    for index, product in by_sale_goods_df.iterrows():
        mycanvas.drawString(55, y_point, str(product['s_no']))
        if not len(product['product_name']) > 13:
            mycanvas.drawString(90, y_point, str(product['product_name']))
        else:
            mycanvas.drawString(90, y_point, str(product['product_name'])[0:13])
            y_point -=10
            mycanvas.drawString(90, y_point, str(product['product_name'])[13:])
            y_point += 10
        mycanvas.drawString(190, y_point, str(product['expiry_date']))
        mycanvas.drawRightString(300, y_point, str(int(product['qty'])))
        mycanvas.drawRightString(360, y_point, str(product['cost']))
        mycanvas.drawRightString(420, y_point, str(product['cgst_value']))
        mycanvas.drawRightString(475, y_point, str(product['sgst_value']))
        mycanvas.drawRightString(545, y_point, str(product['total_cost']))
        if not len(product['product_name']) > 13:
            y_point -=15
        else:
            y_point -=25
    mycanvas.line(40, y_point, 550, y_point)
    y_point -= 15
    mycanvas.drawRightString(460, y_point, 'Total')
    mycanvas.drawRightString(545, y_point, str(final_price))
    
    y_point += 15
    
    mycanvas.line(40, y_point, 40, 670)
    mycanvas.line(82, y_point, 82, 670)
    mycanvas.line(186, y_point, 186, 670)
    mycanvas.line(259, y_point, 259, 670)
    mycanvas.line(310, y_point, 310, 670)
    mycanvas.line(370, y_point, 370, 670)
    y_point -= 25
    mycanvas.line(430, y_point, 430, 670)
    mycanvas.line(480, y_point, 480, 670)
    mycanvas.line(550, y_point, 550, 670)
    mycanvas.line(430, y_point, 550, y_point)
    
    
    mycanvas.setFont('Helvetica', 12)

    y_point -= 70
    mycanvas.drawString(50, y_point, 'Signature of Recipient')
    mycanvas.drawString(445, y_point, 'Issuer Signature')

    mycanvas.save()
    return file_path


@transaction.atomic
@api_view(['POST'])
def prepare_gate_pass_for_by_product_employee(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        user_profile_id = EmployeeOrderBySaleGroup.objects.get(id=request.data['by_sale_group_id']).business.user_profile.id
        by_sale_obj = EmployeeOrderBySale.objects.filter(employeee_order_by_sale_group_id=request.data['by_sale_group_id'])
        data_dict = serve_by_product_price_dict(user_profile_id)
        product_price_dict = data_dict['product_price_dict']
        for sale in by_sale_obj:
            required_qty = sale.count
            if not required_qty == 0:
                goods_receipt_record_obj = GoodsReceiptRecord.objects.filter(by_product_id=sale.by_product.id).exclude(quantity_now=0).order_by('id')
                for goods in goods_receipt_record_obj:
                    if goods.quantity_now > required_qty:
                        balance_in_goods = goods.quantity_now - Decimal(required_qty)
                        goods.quantity_now = balance_in_goods
                        goods.quantity_now_time = datetime.datetime.now()
                        goods.save()
                        product_price = Decimal(required_qty) * product_price_dict[sale.by_product.id]['price']
                        product_gst_dict = calculate_gst_percentage(sale.by_product.id, product_price)
                        total_cost_for_product = product_gst_dict['product_cgst_value'] + product_gst_dict['product_sgst_value'] + product_price
                        goods_receipt_record_sale_map_obj = GoodsReceiptRecordEmployeeOrderBySaleMap(
                            goods_receipt_record_id=goods.id,
                            employee_order_by_sale_id=sale.id,
                            quantity_dispatched=required_qty,
                            cost=product_price,
                            cgst_value=product_gst_dict['product_cgst_value'],
                            sgst_value=product_gst_dict['product_sgst_value'],
                            total_cost=total_cost_for_product,
                        )
                        goods_receipt_record_sale_map_obj.save()
                        break
                    else:
                        required_qty = Decimal(required_qty) - goods.quantity_now
                        product_price = goods.quantity_now * product_price_dict[sale.by_product.id]['price']
                        product_gst_dict = calculate_gst_percentage(sale.by_product.id, product_price)
                        total_cost_for_product = product_gst_dict['product_cgst_value'] + product_gst_dict['product_sgst_value'] + product_price
                        goods_receipt_record_sale_map_obj = GoodsReceiptRecordEmployeeOrderBySaleMap(
                            goods_receipt_record_id=goods.id,
                            employee_order_by_sale_id=sale.id,
                            quantity_dispatched=goods.quantity_now,
                            cost=product_price,
                            cgst_value=product_gst_dict['product_cgst_value'],
                            sgst_value=product_gst_dict['product_sgst_value'],
                            total_cost=total_cost_for_product,
                        )
                        goods.quantity_now = 0
                        goods.quantity_now_time = datetime.datetime.now()
                        goods.save()
                        goods_receipt_record_sale_map_obj.save()
        by_sale_group_obj = EmployeeOrderBySaleGroup.objects.get(id=request.data['by_sale_group_id'])
        by_sale_group_obj.sale_status_id = 2 # gatepass prepared
        by_sale_group_obj.save()
        by_sale_group_id = by_sale_group_obj.id

        dc_number = generate_dc_code()
        dc_number = 'Temp_' + str(dc_number)
        bill_number = generate_bill_code()
        dc_date = datetime.datetime.now()
        bill_date = datetime.datetime.now()
        sale_group_gatepass_obj = EmployeeOrderBySaleGroupGatepass(
            employeee_order_by_sale_group_id=by_sale_group_obj.id,
            dc_number=dc_number,
            dc_date=dc_date,
            bill_number=bill_number,
            bill_date=bill_date,
            prepared_by=request.user,
            prepated_at=datetime.datetime.now()
        )
        gst_number = '33AAAAT7787L2ZU'

        dc_file_path = create_gate_pass_temp_dc_for_employee_order(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number)
        sale_group_gatepass_obj.dc_file = dc_file_path
        sale_group_gatepass_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('Error - {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)

@transaction.atomic
@api_view(['POST'])
def prepare_gate_pass_for_by_product(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        if not BySaleGroupGatepass.objects.filter(by_sale_group_id=request.data['by_sale_group_id']).exists():
            user_profile_id = BySaleGroup.objects.get(id=request.data['by_sale_group_id']).business.user_profile.id
            by_sale_obj = BySale.objects.filter(by_sale_group_id=request.data['by_sale_group_id'])
            data_dict = serve_by_product_price_dict(user_profile_id)
            product_price_dict = data_dict['product_price_dict']
            for sale in by_sale_obj:
                required_qty = sale.count
                print('required_qty:', required_qty)
                if not required_qty == 0:
                    goods_receipt_record_obj = GoodsReceiptRecord.objects.filter(by_product_id=sale.by_product.id).exclude(quantity_now=0).order_by('id')
                    for goods in goods_receipt_record_obj:
                        if goods.quantity_now >= required_qty:
                            balance_in_goods = goods.quantity_now - Decimal(required_qty)
                            goods.quantity_now = balance_in_goods
                            goods.quantity_now_time = datetime.datetime.now()
                            goods.save()
                            product_base_price = Decimal(required_qty) * product_price_dict[sale.by_product.id]['base_price']
                            product_mrp = Decimal(required_qty) * product_price_dict[sale.by_product.id]['mrp']
                            product_gst_dict = calculate_gst_value(product_base_price, product_mrp, Decimal(required_qty))

                            print('product_gst_dict:', product_gst_dict)
                            total_cost_for_product = product_mrp
                            goods_receipt_record_sale_map_obj = GoodsReceiptRecordBySaleMap(
                                goods_receipt_record_id=goods.id,
                                by_sale_id=sale.id,
                                quantity_dispatched=required_qty,
                                cost=product_base_price,
                                cgst_value=product_gst_dict['product_cgst_value'],
                                sgst_value=product_gst_dict['product_sgst_value'],
                                total_cost=total_cost_for_product,
                            )
                            goods_receipt_record_sale_map_obj.save()
                            break
                        else:
                            print('else')
                            required_qty = Decimal(required_qty) - goods.quantity_now
                            product_base_price = Decimal(goods.quantity_now) * product_price_dict[sale.by_product.id]['base_price']
                            product_mrp = Decimal(goods.quantity_now) * product_price_dict[sale.by_product.id]['mrp']
                            product_gst_dict = calculate_gst_value(product_base_price, product_mrp, Decimal(goods.quantity_now))
                            print('product_gst_dict_else:', product_gst_dict)
                            
                            total_cost_for_product = product_mrp
                            goods_receipt_record_sale_map_obj = GoodsReceiptRecordBySaleMap(
                                goods_receipt_record_id=goods.id,
                                by_sale_id=sale.id,
                                quantity_dispatched=goods.quantity_now,
                                cost=product_base_price,
                                cgst_value=product_gst_dict['product_cgst_value'],
                                sgst_value=product_gst_dict['product_sgst_value'],
                                total_cost=total_cost_for_product,
                            )
                            goods.quantity_now = 0
                            goods.quantity_now_time = datetime.datetime.now()
                            goods.save()
                            goods_receipt_record_sale_map_obj.save()
            by_sale_group_obj = BySaleGroup.objects.get(id=request.data['by_sale_group_id'])
            by_sale_group_obj.sale_status_id = 2 # gatepass prepared
            by_sale_group_obj.save()
            by_sale_group_id = by_sale_group_obj.id

            dc_number = generate_dc_code()
            bill_number = generate_bill_code()
            dc_date = datetime.datetime.now()
            bill_date = datetime.datetime.now()
            sale_group_gatepass_obj = BySaleGroupGatepass(
                by_sale_group_id=by_sale_group_obj.id,
                dc_number=dc_number,
                dc_date=dc_date,
                bill_number=bill_number,
                bill_date=bill_date,
                prepared_by=request.user,
                prepated_at=datetime.datetime.now()
            )
            gst_number = '33AAAAT7787L2ZU'

            dc_file_path = create_gate_pass_dc(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number)
            bill_file_path = create_gate_pass_bill(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number)
            sale_group_gatepass_obj.dc_file = dc_file_path
            sale_group_gatepass_obj.bill_file = bill_file_path
            sale_group_gatepass_obj.save()
            transaction.savepoint_commit(sid)
            return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('Error - {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def create_gate_pass_bill(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number):
    dc_date = datetime.datetime.strftime(dc_date, '%d-%m-%Y')
    bill_date = datetime.datetime.strftime(bill_date, '%d-%m-%Y')

    by_sale_group_obj = BySaleGroup.objects.get(id=by_sale_group_id)
    order_code = by_sale_group_obj.order_code
    order_date = by_sale_group_obj.ordered_date
    order_date = datetime.datetime.strftime(order_date, '%d-%m-%Y')
    business_obj = Business.objects.get(id=by_sale_group_obj.business.id)
    business_code = business_obj.code
    business_type_name = business_obj.business_type.name
    business_id = business_obj.id
    agent = BusinessAgentMap.objects.get(business_id=business_id).agent
    agent_gst_number = agent.agent_profile.gst_number
    agent_first_name = agent.first_name
    street = ''
    if agent.agent_profile.street is not None:
        street = agent.agent_profile.street
    pincode = ''
    if agent.agent_profile.pincode is not None:
        pincode = agent.agent_profile.pincode
    agent_address = str(street) + ' ' + str(pincode)
    payment_option = by_sale_group_obj.payment_method.name
    
    business_type_wise_price_obj = BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=business_obj.business_type_id)
    business_type_wise_price_list = list(business_type_wise_price_obj.values_list('id', 'business_type', 'by_product', 'base_price', 'mrp', 'cgst_amount', 'sgst_amount', 'by_product__cgst_percent', 'by_product__sgst_percent'))
    business_type_wise_price_column = ['id', 'business_type', 'by_product_id', 'base_price', 'mrp', 'cgst_amount', 'sgst_amount', 'cgst_percent', 'sgst_percent']
    business_type_wise_price_df = pd.DataFrame(business_type_wise_price_list, columns=business_type_wise_price_column)
    product_price_dict = business_type_wise_price_df.groupby('by_product_id').apply(lambda x:x.to_dict('r')[0]).to_dict()
    
    
    by_sale_goods_obj = GoodsReceiptRecordBySaleMap.objects.filter(by_sale__by_sale_group_id=by_sale_group_id)
    by_sale_goods_list = list(by_sale_goods_obj.values_list('id', 'by_sale__by_product', 'by_sale__by_product__by_product_group__hsn_code',  'by_sale__by_product__display_ordinal', 'by_sale__by_product__short_name', 'goods_receipt_record__expiry_date', 'quantity_dispatched', 'cost', 'cgst_value', 'sgst_value', 'total_cost'))
    by_sale_goods_column = ['id', 'by_product_id', 'hsn_code', 'display_ordinal', 'product_name', 'expiry_date', 'qty', 'cost', 'cgst_value', 'sgst_value', 'total_cost']
    by_sale_goods_df = pd.DataFrame(by_sale_goods_list, columns=by_sale_goods_column)
    by_sale_goods_df = by_sale_goods_df.sort_values(by=['display_ordinal', 'expiry_date'], ascending=True)
    by_sale_goods_df['s_no'] = range(1, 1+len(by_sale_goods_df))
    by_sale_goods_df['expiry_date'] = pd.to_datetime(by_sale_goods_df['expiry_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%d-%m-%Y')
    by_sale_goods_df = by_sale_goods_df.fillna('-')
    final_price_before_round = by_sale_group_obj.value_before_round_off
    round_off_value = by_sale_group_obj.round_off_value
    total_cost = by_sale_group_obj.total_cost
    total_cost_in_words = num2words(round(total_cost), lang='en_IN')
        
    # file creation
    file_name = str(business_code) + '_' + str(order_code) + '_bill.pdf'
    try:
        path = os.path.join('static/media/by_product/gate_pass/', str(business_code), str(order_code), 'bill')
        os.makedirs(path)
    except FileExistsError:
        print('already created')
    file_path = os.path.join(path, file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(500, 830, str(payment_option) + ' Sale')
    mycanvas.drawCentredString(300, 810,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawString(40, 790, 'GST Number : ' + str(gst_number))
    mycanvas.drawCentredString(300, 790, 'Tax Invoice')
    mycanvas.line(250, 785, 350, 785)
    
    # Order Data
    mycanvas.drawString(40, 760, 'DC Number: ')
    mycanvas.drawString(130, 760, str(dc_number))
    mycanvas.drawString(40, 740, 'Bill Number: ')
    mycanvas.drawString(130, 740, str(bill_number))
    mycanvas.drawString(40, 720, 'Order Number: ')
    mycanvas.drawString(130, 720, str(order_code))
    mycanvas.drawString(40, 700, 'Booth Code: ')
    if business_type_name == 'Booth':
        mycanvas.drawString(130, 700, str(business_code) + str(' Retail'))
    else:
        mycanvas.drawString(130, 700, str(business_code) + ' ' + str(business_type_name))
    mycanvas.drawString(40, 680, 'GST Number: ')
    if agent_gst_number is not None:
        mycanvas.drawString(130, 680, str(agent_gst_number))
    else:
        mycanvas.drawString(130, 680, str('-'))
    
    mycanvas.drawString(340, 760, 'DC Date: ')
    mycanvas.drawString(430, 760, str(dc_date))
    mycanvas.drawString(340, 740, 'Bill Date: ')
    mycanvas.drawString(430, 740, str(bill_date))
    mycanvas.drawString(340, 720, 'Order Date: ')
    mycanvas.drawString(430, 720, str(order_date))
    mycanvas.drawString(340, 700, 'Agent Name: ')
    mycanvas.drawString(430, 700, str(agent_first_name)[0:18])
    mycanvas.drawString(340, 680, 'Address: ')
    mycanvas.setFont('Helvetica', 8)
    mycanvas.drawString(430, 680, str(agent_address))
    mycanvas.setFont('Helvetica', 10)
    
    mycanvas.setStrokeColor(colors.black)

    # product list
    mycanvas.drawCentredString(300, 650, 'Product List')
    mycanvas.line(20, 640, 570, 640)
    mycanvas.drawString(22, 625, 'Sl')
    mycanvas.drawString(50, 625, 'HSN')
    mycanvas.drawString(87, 625, 'Product')
    mycanvas.drawString(180, 625, 'Expiry')
    mycanvas.drawString(220, 625, 'Qty')
    mycanvas.drawString(265, 625, 'Rate')
    mycanvas.drawString(310, 625, 'Cost')
    mycanvas.setFont('Helvetica', 9)
    mycanvas.drawString(350, 630, 'CGST')
    mycanvas.drawString(360, 620, '%')
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(390, 625, 'CGST')
    mycanvas.setFont('Helvetica', 9)
    mycanvas.drawString(430, 630, 'SGST')
    mycanvas.drawString(440, 620, '%')
    mycanvas.setFont('Helvetica', 10)
    mycanvas.drawString(470, 625, 'SGST')
    mycanvas.drawString(520, 625, 'Total Cost')

    mycanvas.line(20, 615, 570, 615)
    y_point = 600
    mycanvas.setFont('Helvetica', 8)

    for index, product in by_sale_goods_df.iterrows():
        mycanvas.drawString(25, y_point, str(product['s_no']))
        mycanvas.drawString(45, y_point, str(product['hsn_code']))
        if not len(product['product_name']) > 19:
            mycanvas.drawString(87, y_point, str(product['product_name']))
        else:
            mycanvas.drawString(87, y_point, str(product['product_name'])[0:23])
            y_point -=10
            mycanvas.drawString(87, y_point, str(product['product_name'])[23:])
            y_point += 10
        mycanvas.setFont('Helvetica', 6)    
        mycanvas.drawString(180, y_point, str(product['expiry_date']))
        mycanvas.setFont('Helvetica', 8)
        mycanvas.drawString(220, y_point, str(int(product['qty'])))
        mycanvas.drawRightString(288, y_point, str(product_price_dict[product['by_product_id']]['mrp']))
        mycanvas.drawRightString(338, y_point, str(product['cost']))
        mycanvas.drawRightString(373, y_point, str(product_price_dict[product['by_product_id']]['cgst_percent']))
        mycanvas.drawRightString(417, y_point, str(product['cgst_value']))
        mycanvas.drawRightString(453, y_point, str(product_price_dict[product['by_product_id']]['sgst_percent']))
        mycanvas.drawRightString(498, y_point, str(product['sgst_value']))
        mycanvas.drawRightString(565, y_point, str(product['total_cost']))
        if not len(product['product_name']) > 19:
            y_point -=15
        else:
            y_point -=25
    mycanvas.line(20, y_point, 570, y_point)
    y_point -= 15
    mycanvas.drawString(20, y_point, str(total_cost_in_words).title()  + ' Only')
    mycanvas.drawRightString(490, y_point, 'Total')
    mycanvas.drawRightString(565, y_point, str(final_price_before_round))
    mycanvas.drawString(20, y_point-15, "Goods once sold can't be taken back")
    mycanvas.drawRightString(490, y_point - 15, 'Rounded Value')
    mycanvas.drawRightString(565, y_point - 15, str(round_off_value))
    mycanvas.drawRightString(490, y_point - 30, 'Final Price')
    mycanvas.drawRightString(565, y_point - 30, str(total_cost))
    
    y_point += 15
    
    mycanvas.line(20, y_point, 20, 640)
    mycanvas.line(40, y_point, 40, 640)
    mycanvas.line(85, y_point, 85, 640)
    mycanvas.line(179, y_point, 179, 640)
    mycanvas.line(218, y_point, 218, 640)
    mycanvas.line(245, y_point, 245, 640)
    mycanvas.line(290, y_point, 290, 640)
    mycanvas.line(339, y_point, 339, 640)
    mycanvas.line(375, y_point, 375, 640)
    mycanvas.line(419, y_point, 419, 640)
    mycanvas.line(458, y_point, 458, 640)
    y_point -= 55
    mycanvas.line(500, y_point, 500, 640)
    mycanvas.line(570, y_point, 570, 640)
    mycanvas.line(500, y_point, 570, y_point)
    
    
    mycanvas.setFont('Helvetica', 12)

    y_point -= 70
    mycanvas.drawString(50, y_point, 'Signature of Recipient')
    mycanvas.drawString(445, y_point, 'Issuer Signature')

    mycanvas.save()
    return file_path


def create_gate_pass_dc(dc_number, bill_number, dc_date, bill_date, by_sale_group_id, gst_number):
    dc_date = datetime.datetime.strftime(dc_date, '%d-%m-%Y')
    bill_date = datetime.datetime.strftime(bill_date, '%d-%m-%Y')

    by_sale_group_obj = BySaleGroup.objects.get(id=by_sale_group_id)
    order_code = by_sale_group_obj.order_code
    order_date = by_sale_group_obj.ordered_date
    order_date = datetime.datetime.strftime(order_date, '%d-%m-%Y')
    business_obj = Business.objects.get(id=by_sale_group_obj.business.id)
    business_code = business_obj.code
    business_id = business_obj.id
    agent_first_name = BusinessAgentMap.objects.get(business_id=business_id).agent.first_name
    # payment_option = BusinessTypeOrderCategoryeMap.objects.get(order_category_id=2, business_type_id=business_obj.business_type_id).payment_option.name
    payment_option = by_sale_group_obj.payment_method.name
    by_sale_goods_obj = GoodsReceiptRecordBySaleMap.objects.filter(by_sale__by_sale_group_id=by_sale_group_id)
    by_sale_goods_list = list(by_sale_goods_obj.values_list('id', 'by_sale__by_product__by_product_group__hsn_code',  'by_sale__by_product__display_ordinal', 'by_sale__by_product__short_name', 'goods_receipt_record__expiry_date', 'quantity_dispatched', 'cost', 'cgst_value', 'sgst_value', 'total_cost'))
    by_sale_goods_column = ['id', 'hsn_code', 'display_ordinal', 'product_name', 'expiry_date', 'qty', 'cost', 'cgst_value', 'sgst_value', 'total_cost']
    by_sale_goods_df = pd.DataFrame(by_sale_goods_list, columns=by_sale_goods_column)
    by_sale_goods_df = by_sale_goods_df.sort_values(by=['display_ordinal', 'expiry_date'], ascending=True)
    by_sale_goods_df['s_no'] = range(1, 1+len(by_sale_goods_df))
    by_sale_goods_df['expiry_date'] = pd.to_datetime(by_sale_goods_df['expiry_date'] ,errors = 'coerce',format = '%Y-%m-%d').dt.strftime('%d-%m-%Y')
    by_sale_goods_df = by_sale_goods_df.fillna('-')
    final_price_before_round = by_sale_group_obj.value_before_round_off
    round_off_value = by_sale_group_obj.round_off_value
    total_cost = by_sale_group_obj.total_cost
        
    # file creation
    file_name = str(business_code) + '_' + str(order_code) +  '_dc.pdf'
    try:
        path = os.path.join('static/media/by_product/gate_pass/', str(business_code), str(order_code), 'dc')
        os.makedirs(path)
    except FileExistsError:
        print('already created')

    file_path = os.path.join(path, file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawString(500, 830, str(payment_option) + ' Sale')

    mycanvas.drawCentredString(300, 810,
                               'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawString(40, 790, 'GST Number : ' + str(gst_number))

    mycanvas.drawCentredString(300, 790, 'Delivery Challan')
    mycanvas.line(250, 785, 350, 785)
    
    # Order Data
    mycanvas.drawString(40, 745, 'DC Number: ')
    mycanvas.drawString(130, 745, str(dc_number))
    # mycanvas.drawString(40, 740, 'Bill Number: ')
    # mycanvas.drawString(130, 740, str(bill_number))
    mycanvas.drawString(40, 720, 'Order Number: ')
    mycanvas.drawString(130, 720, str(order_code))
    mycanvas.drawString(40, 700, 'Booth Code: ')
    mycanvas.drawString(130, 700, str(business_code))
    
    mycanvas.drawString(340, 745, 'DC Date: ')
    mycanvas.drawString(430, 745, str(dc_date))
    # mycanvas.drawString(340, 740, 'Bill Date: ')
    # mycanvas.drawString(430, 740, str(bill_date))
    mycanvas.drawString(340, 720, 'Order Date: ')
    mycanvas.drawString(430, 720, str(order_date))
    mycanvas.drawString(340, 700, 'Agent Name: ')
    mycanvas.drawString(430, 700, str(agent_first_name)[0:18])
    
    mycanvas.setStrokeColor(colors.black)

    # product list
    mycanvas.drawCentredString(300, 680, 'Product List')
    mycanvas.setFont('Helvetica', 10)
    mycanvas.line(20, 670, 570, 670)
    mycanvas.drawString(25, 655, 'Sl')
    mycanvas.drawString(43, 655, 'HSN')
    mycanvas.drawString(110, 655, 'Product')
    mycanvas.drawString(202, 655, 'Expiry')
    mycanvas.drawString(270, 655, 'Qty')
    mycanvas.drawString(330, 655, 'Cost')
    mycanvas.drawString(390, 655, 'CGST')
    mycanvas.drawString(440, 655, 'SGST')
    mycanvas.drawString(510, 655, 'Total Cost')

    mycanvas.line(20, 650, 570, 650)
    y_point = 630
    mycanvas.setFont('Helvetica', 8)

    for index, product in by_sale_goods_df.iterrows():
        mycanvas.drawString(25, y_point, str(product['s_no']))
        mycanvas.drawString(43, y_point, str(product['hsn_code']))
        if not len(product['product_name']) > 23:
            mycanvas.drawString(100, y_point, str(product['product_name']))
        else:
            mycanvas.drawString(100, y_point, str(product['product_name'])[0:23])
            y_point -=10
            mycanvas.drawString(100, y_point, str(product['product_name'])[23:])
            y_point += 10
        mycanvas.drawString(202, y_point, str(product['expiry_date']))
        mycanvas.drawRightString(272, y_point, str(int(product['qty'])))
        mycanvas.drawRightString(360, y_point, str(product['cost']))
        mycanvas.drawRightString(420, y_point, str(product['cgst_value']))
        mycanvas.drawRightString(475, y_point, str(product['sgst_value']))
        mycanvas.drawRightString(565, y_point, str(product['total_cost']))
        if not len(product['product_name']) > 13:
            y_point -=15
        else:
            y_point -=25
    mycanvas.line(20, y_point, 570, y_point)
    y_point -= 15
    mycanvas.drawRightString(490, y_point, 'Total')
    mycanvas.drawRightString(565, y_point, str(final_price_before_round))
    mycanvas.drawRightString(490, y_point - 15, 'Rounded Value')
    mycanvas.drawRightString(565, y_point - 15, str(round_off_value))
    mycanvas.drawRightString(490, y_point - 30, 'Final Price')
    mycanvas.drawRightString(565, y_point - 30, str(total_cost))
    
    y_point += 15
    
    mycanvas.line(20, y_point, 20, 670)
    mycanvas.line(40, y_point, 40, 670)
    mycanvas.line(98, y_point, 98, 670)
    mycanvas.line(200, y_point, 200, 670)
    mycanvas.line(265, y_point, 265, 670)
    mycanvas.line(310, y_point, 310, 670)
    mycanvas.line(370, y_point, 370, 670)
    mycanvas.line(430, y_point, 430, 670)
    y_point -= 55
    mycanvas.line(500, y_point, 500, 670)
    mycanvas.line(570, y_point, 570, 670)
    mycanvas.line(500, y_point, 570, y_point)
    
    
    mycanvas.setFont('Helvetica', 12)

    y_point -= 70
    mycanvas.drawString(50, y_point, 'Signature of Recipient')
    mycanvas.drawString(445, y_point, 'Issuer Signature')

    mycanvas.save()
    return file_path


@api_view(['GET'])
def serve_counter_orders_for_by_product(request):
    employee_id = Employee.objects.get(user_profile__user=request.user).id
    print(employee_id)
    counter_obj = CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True, collection_date=datetime.datetime.now())[0]
    counter_employee_trace_ids = list(CounterEmployeeTraceMap.objects.filter(counter_id=counter_obj.counter.id,
                                                                            collection_date=datetime.datetime.now()).values_list(
        'id', flat=True))
    counter_sale_group_ids = list(CounterEmployeeTraceBySaleGroupMap.objects.filter(
        counter_employee_trace_id__in=counter_employee_trace_ids).values_list('by_sale_group', flat=True))
    counter_sale_group_obj = CounterEmployeeTraceBySaleGroupMap.objects.filter(
        counter_employee_trace_id__in=counter_employee_trace_ids)
    counter_sale_group_list = list(counter_sale_group_obj.values_list('counter_employee_trace', 'by_sale_group'))
    counter_sale_group_column = ['login_id', 'by_sale_group']
    counter_sale_group_df = pd.DataFrame(counter_sale_group_list, columns=counter_sale_group_column)
    login_user_obj = CounterEmployeeTraceMap.objects.filter(counter_id=counter_obj.counter.id,
                                                            collection_date=datetime.datetime.now()).order_by('-id')
    login_user_list = list(
        login_user_obj.values_list('id', 'employee__user_profile__user__first_name', 'start_date_time',
                                'end_date_time', 'counter__name'))
    login_user_column = ['login_id', 'employee_name', 'login_time', 'logout_time', 'counter_name']
    login_user_df = pd.DataFrame(login_user_list, columns=login_user_column)
    login_user_df = login_user_df.fillna(0)
    by_sale_group_obj = BySaleGroup.objects.filter(id__in=counter_sale_group_ids).order_by('-id')
    by_sale_group_list = list(by_sale_group_obj.values_list('id', 'total_cost', 'ordered_date', 'business_id', 'order_code', 'business__code'))
    by_sale_group_column = ['id', 'total_cost', 'ordered_date', 'business_id', 'order_code', 'business_code']
    by_sale_group_df = pd.DataFrame(by_sale_group_list, columns=by_sale_group_column)
    sale_df = by_sale_group_df.merge(counter_sale_group_df, how="inner", left_on='id', right_on="by_sale_group")
    if not sale_df.empty:
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
        'total_booth_count': len(sale_df['business_id'])
    }
    if not sale_df.empty:
        data_dict['total_quantity'] = sale_df['total_cost'].sum()
    else:
        data_dict['total_quantity'] = 0
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_business_details_for_by_product_order(request):
    data_dict = {}
    if not Business.objects.filter(code=request.data['business_code']).exists():
        print('not exists')
        data = {'error_message': str(request.data['business_code']) + ' is not a valid booth code. Please Check'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    # if not Agent.objects.filter(agent_code=request.data['business_code']).exists():
        
    #     else:
    business_obj = Business.objects.get(code=request.data['business_code'])
    # else:
    #     agent_obj = Agent.objects.get(agent_code=request.data['business_code'])

    #     business_agent_obj = BusinessAgentMap.objects.get(agent_id=agent_obj.id)
        # business_obj = Business.objects.get(code=business_agent_obj.business.code)
    if not BusinessTypeOrderCategoryeMap.objects.filter(business_type_id=business_obj.business_type_id, order_category_id=2).exists():
        data = {'error_message': str(request.data['business_code']) + ' is not a valid booth code. Please Check'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    
    business_id = business_obj.id
    agent_details = BusinessAgentMap.objects.get(business_id=business_id).agent
    business_obj = Business.objects.get(id=business_id)
    agent_wallet_obj = ByProductAgentWallet.objects.get(agent_id=agent_details.id)
    # if business_type_id == 1 or business_type_id == 2 or business_type_id == 9 or business_type_id == 11 or business_type_id == 12:
    #     mobile_verification = agent_details.is_mobile_number_verified_by_agent
    # else:
    mobile_verification = True
    data_dict['agent_name'] = agent_details.first_name
    data_dict['agent_code'] = agent_details.agent_code
    data_dict['agent_mobile'] = agent_details.agent_profile.mobile
    data_dict['booth_address'] = business_obj.address
    data_dict['booth_zone'] = business_obj.zone.name
    data_dict['booth_code'] = business_obj.code
    data_dict['user_id'] = business_obj.user_profile.user.id
    data_dict['is_mobile_verified'] = mobile_verification
    data_dict['wallet_amount'] =agent_wallet_obj.current_balance
    return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_counter_wise_sale_summary_for_byproducts(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']

    data_dict = {}

    by_business_type_list = list(BusinessTypeOrderCategoryeMap.objects.filter(order_category=2).values_list('business_type_id', 'business_type__name'))
    by_business_type_column = ['business_type_id', 'business_type_name']
    by_business_type_df = pd.DataFrame(by_business_type_list, columns=by_business_type_column)
    by_business_type_df

    for index,ordered_via in enumerate([[2], [1,3]]):

        #by_product_common_salegroup_df
        by_salegroup_list = list(BySaleGroup.objects.filter(ordered_date__range=[from_date, to_date], ordered_via_id__in=ordered_via, business__business_type__businesstypeordercategoryemap__order_category=2).values_list('business__business_type_id', 'business__business_type__name', 'total_cost', 'business__business_type__businesstypeordercategoryemap__payment_option'))                        
        by_salegroup_column = ['business_type_id', 'business_type_name', 'total_cost', 'payment_option']
        by_salegroup_df = pd.DataFrame(by_salegroup_list, columns=by_salegroup_column)
        by_salegroup_df

        # groub_by_df
        by_salegroup_df = by_salegroup_df.groupby('business_type_name').agg({'business_type_id': 'first', 'total_cost': 'sum', 'payment_option': 'first'}).reset_index()
        by_salegroup_df

        # seprating cash and credit
        credit_df = pd.merge(by_business_type_df, by_salegroup_df[by_salegroup_df['payment_option']==2], left_on=['business_type_id', 'business_type_name'], right_on=['business_type_id', 'business_type_name'], how='left').fillna(0).rename(columns={'total_cost': 'credit_cost'}).drop(columns=['payment_option'])                                                                                
        cash_df = pd.merge(by_business_type_df, by_salegroup_df[by_salegroup_df['payment_option']==1], left_on=['business_type_id', 'business_type_name'], right_on=['business_type_id', 'business_type_name'], how='left').fillna(0).rename(columns={'total_cost': 'cash_cost'}).drop(columns=['payment_option'])

        #final_df
        final_df = pd.merge(cash_df, credit_df, left_on=['business_type_id', 'business_type_name'], right_on=['business_type_id', 'business_type_name'], how='left')
        final_df['total'] = final_df.iloc[:, 2:].sum(axis=1)

        final_cost_dict = final_df.groupby('business_type_name').apply(lambda x:x.to_dict('r')[0]).to_dict()
        
        if index == 0:
            data_dict['portal'] = final_cost_dict
        else:
            data_dict['online'] = final_cost_dict 

            
    # -------------------pdf Code -----------------------
    file_name = str(from_date) +'_to_'+ str(to_date) + '_all_counter_sale_summary_by_products' + '.pdf'
    file_path = os.path.join('static/media/by_product/sale_summary', file_name)
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
    date_in_format_from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    date_in_format_to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')

    from_date = datetime.datetime.strftime(date_in_format_from_date, '%d-%m-%Y')
    to_date = datetime.datetime.strftime(date_in_format_to_date, '%d-%m-%Y')

    mycanvas.drawCentredString(300, 795, 'Daily All Counter ByProducts Sales summary Report ( '+str(from_date)+' to '+str(to_date)+" )")
    #     mycanvas.line(228-50, 752, 472-50, 752)

    #_____________table header_____________#

    mycanvas.setFont('Helvetica-Bold', 10)
    mycanvas.setFillColor(HexColor(dark_color))


    mycanvas.setFillColor(HexColor(dark_color))
    mycanvas.setLineWidth(0)

    x_axis = 195-x_adjust
    line_x_axis = 150-x_adjust

    y_axis = 710
    y_axis_agent = 725
    y_head = 745
        
    for data in data_dict:
        print(data)
        if data == "portal":
            head = "Portal Sale"
        else:
            head = "Online Sale"
            

        mycanvas.setLineWidth(0)
        mycanvas.line(line_x_axis - 50, y_axis_agent + 30, line_x_axis + 460 , y_axis_agent + 30)
        mycanvas.line(line_x_axis - 50, y_axis_agent, line_x_axis + 460, y_axis_agent)
        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.drawCentredString(300, y_head + 25, str(head))
        mycanvas.setLineWidth(1.2)
        mycanvas.line(188, y_head + 21, 422, y_head + 21)
        mycanvas.setLineWidth(0)

        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.drawCentredString(120 - x_adjust, y_head-5, 'S.No')
        mycanvas.drawCentredString(220 - x_adjust, y_head-5, 'Counter Name')
        mycanvas.drawCentredString(375 - x_adjust, y_head-5, 'Cash')
        mycanvas.drawString(500 - 50-x_adjust, y_head-5, 'Credit')
        mycanvas.drawString(595 - 63-x_adjust, y_head-5, 'Sale Amount')


        index = 1
        total = 0
        cash_total = 0
        credit_total = 0

        for counter in data_dict[data]:
            print(counter)
            mycanvas.drawString(x_axis - 80, y_axis, str(index))
            mycanvas.line(x_axis - 50, y_axis_agent + 30, x_axis - 50, y_axis - 25)
            mycanvas.drawString(x_axis -35 , y_axis, str(counter))
            mycanvas.line(x_axis + 120 , y_axis_agent + 30, x_axis + 120, y_axis - 25)
            
            mycanvas.drawRightString(x_axis + 280 - 70, y_axis, str(data_dict[data][counter]["cash_cost"]))
            mycanvas.line(x_axis + 220, y_axis_agent + 30, x_axis + 220, y_axis - 25)
            cash_total += data_dict[data][counter]["cash_cost"]
            
            mycanvas.drawRightString(x_axis + 310, y_axis, str(data_dict[data][counter]["credit_cost"]))
            mycanvas.line(x_axis + 320, y_axis_agent + 30, x_axis + 320, y_axis - 25)
            credit_total += data_dict[data][counter]["credit_cost"]

            mycanvas.drawRightString(x_axis + 405, y_axis,
                                    str(round(Decimal(data_dict[data][counter]["total"]), 2)))
            total += round(Decimal(data_dict[data][counter]["total"]), 2)

            index += 1
            y_axis -= 16

        mycanvas.setFont('Helvetica-Bold', 10)
        mycanvas.line(line_x_axis - 50, y_axis + 10, line_x_axis + 460, y_axis + 10)
        mycanvas.line(line_x_axis - 50, y_axis_agent + 30, line_x_axis - 50, y_axis + 10)
        mycanvas.line(x_axis + 455 - 40, y_axis_agent + 30, x_axis + 415 , y_axis - 10)
        mycanvas.line(line_x_axis - 5, y_axis - 10, line_x_axis + 460, y_axis - 10)
        
        mycanvas.drawRightString(x_axis + 210, y_axis - 3, str(cash_total))
        mycanvas.drawRightString(x_axis + 310, y_axis - 3, str(credit_total))
        mycanvas.drawRightString(x_axis + 405, y_axis - 3, str(total))
        
        mycanvas.drawRightString(x_axis + 110, y_axis - 3, 'Total')
        y_axis -= 118
        y_axis_agent -= 200
        y_head -= 200
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
def download_gate_pass_for_by_product(request):
    print(request.data)
    merger = PdfFileMerger()
    by_sale_gate_pass_obj = BySaleGroupGatepass.objects.get(by_sale_group_id=request.data['by_sale_group_id'])
    business_code = by_sale_gate_pass_obj.by_sale_group.business.code
    order_code = by_sale_gate_pass_obj.by_sale_group.order_code
    file_name = str(order_code) + '_' + str(request.data['for']) + '.pdf'
    if request.data['for'] == 'bill':
        file_path = by_sale_gate_pass_obj.bill_file
    else:
        file_path = by_sale_gate_pass_obj.dc_file
    for i in range(1, request.data['count'] + 1):
        pdf_file_path = os.path.join(str(file_path))
        merger.append(pdf_file_path)
    try:
        combined_pdf = os.path.join('static/media/by_product/gate_pass/', str(business_code), str(order_code), 'overall')
        os.makedirs(combined_pdf)
    except FileExistsError:
        print('already created')
    merger.write(combined_pdf + file_name)
    merger.close()
    document = {}
    document['file_name'] = file_name   
    combined_pdf_file_path = combined_pdf + file_name
    try:
        image_path = str(combined_pdf_file_path)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def download_gate_pass_for_by_product_employee(request):
    print(request.data)
    merger = PdfFileMerger()
    by_sale_gate_pass_obj = EmployeeOrderBySaleGroupGatepass.objects.get(employeee_order_by_sale_group_id=request.data['by_sale_group_id'])
    business_code = by_sale_gate_pass_obj.employeee_order_by_sale_group.business.code
    order_code = by_sale_gate_pass_obj.employeee_order_by_sale_group.order_code
    file_name = str(order_code) + '_' + str(request.data['for']) + '.pdf'
    if request.data['for'] == 'bill':
        file_path = by_sale_gate_pass_obj.bill_file
    else:
        file_path = by_sale_gate_pass_obj.dc_file
    for i in range(1, request.data['count'] + 1):
        pdf_file_path = os.path.join(str(file_path))
        merger.append(pdf_file_path)
    try:
        combined_pdf = os.path.join('static/media/by_product/gate_pass/', str(business_code), str(order_code), 'temp_overall')
        os.makedirs(combined_pdf)
    except FileExistsError:
        print('already created')
    merger.write(combined_pdf + file_name)
    merger.close()
    document = {}
    document['file_name'] = file_name   
    combined_pdf_file_path = combined_pdf + file_name
    try:
        image_path = str(combined_pdf_file_path)
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_by_product_counters(request):
    counter_list = list(Counter.objects.filter(collection_center_id=9).values('id', 'name'))
    return Response(data=counter_list, status=status.HTTP_200_OK)


@api_view(['POSt'])
def serve_counter_sale_by_products_report(request):
    print(request.data)
    ordered_date = request.data['order_date']
    counter_id = request.data['counter_id']

    alert = ''
    alert_status = False
    counter_employee_trace_obj = CounterEmployeeTraceMap.objects.filter(counter_id=counter_id, collection_date=ordered_date)

    # if counter_id == 'online':
    #     counter_sale_list = list(BySaleGroup.objects.filter(ordered_via__in=[1,3], business__business_type_id__in=business_type_ids, ordered_date=ordered_date).values_list('business__code', 'business__user_profile__user__first_name', 'order_code', 'ordered_date', 'bysalegroupgatepass__dc_number', 'bysalegroupgatepass__bill_number', 'total_cost'))
    # else: 
    #     counter_sale_list = list(CounterEmployeeTraceBySaleGroupMap.objects.filter(counter_employee_trace__counter_id=counter_id, by_sale_group__business__business_type_id__in=business_type_ids, by_sale_group__ordered_date=ordered_date).values_list('by_sale_group__business__code', 'by_sale_group__business__user_profile__user__first_name', 'by_sale_group__order_code', 'by_sale_group__ordered_date', 'by_sale_group__bysalegroupgatepass__dc_number', 'by_sale_group__bysalegroupgatepass__bill_number', 'by_sale_group__total_cost'))                                                                 

    counter_sale_list = list(CounterEmployeeTraceBySaleGroupMap.objects.filter(counter_employee_trace__counter_id=counter_id, by_sale_group__payment_method_id=1, by_sale_group__ordered_date=ordered_date).values_list('by_sale_group__business__code', 'by_sale_group__business__user_profile__user__first_name', 'by_sale_group__order_code', 'by_sale_group__ordered_date', 'by_sale_group__bysalegroupgatepass__dc_number', 'by_sale_group__bysalegroupgatepass__bill_number', 'by_sale_group__total_cost'))                                                                 
    counter_sale_colum = ['Booth Code', 'Agent Name', 'Order Code', 'Order Date', 'DC No', 'Bill No', 'Total Cost']
    counter_sale_df = pd.DataFrame(counter_sale_list, columns=counter_sale_colum)
    counter_sale_df = counter_sale_df.fillna(' ')
    counter_sale_df['Order Date'] = pd.to_datetime(counter_sale_df['Order Date'], errors='coerce')
    counter_sale_df['Order Date']  = counter_sale_df['Order Date'].dt.strftime('%d-%m-%Y')


    file_name = str(ordered_date) + '_counter_sale_by_products' + '.pdf'
    file_path = os.path.join('static/media/by_product', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    total = 0

    # ________Head_lines________#

    mycanvas.setFont('Helvetica', 12.5)
    mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 805, 'Daily Counter Report : By Product Cash Sale')
    mycanvas.setFont('Helvetica-Bold', 10)
    name_emp = ""
    employee_id_list = []
    for name in counter_employee_trace_obj:
        if not name.employee.id in employee_id_list:
            name_emp += name.employee.user_profile.user.first_name + ","
            employee_id_list.append(name.employee.id)
    date_in_format = datetime.datetime.strptime(ordered_date, '%Y-%m-%d')
    print(date_in_format)
    mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(counter_employee_trace_obj[0].counter.name)+'  |  '+'Employees : '+name_emp)



    #_____________table header_____________#
    mycanvas.setFont('Helvetica', 10)
    x_axis = 35
    y_axis = 750

    #__________top_table_lines______________#

    mycanvas.line(x_axis-20, y_axis+15, x_axis+545, y_axis+15)
    mycanvas.line(x_axis-20, y_axis-10, x_axis+545, y_axis-10)

    mycanvas.drawCentredString(x_axis, y_axis, 'S.NO')
    mycanvas.drawCentredString(x_axis+50, y_axis, 'Booth Code')
    mycanvas.drawCentredString(x_axis+127, y_axis, 'Agent Name')
    mycanvas.drawCentredString(x_axis+230, y_axis, 'Order Code')
    mycanvas.drawCentredString(x_axis+300, y_axis, 'Order Date')
    mycanvas.drawCentredString(x_axis+370, y_axis, 'DC No')
    mycanvas.drawCentredString(x_axis+440, y_axis, 'Bill No')
    mycanvas.drawCentredString(x_axis+510, y_axis, 'Amount')

    for index, value in counter_sale_df.iterrows():
        mycanvas.drawString(x_axis,y_axis-25, str(index+1))
        mycanvas.drawString(x_axis+30, y_axis-25, str(value['Booth Code']))
        mycanvas.drawString(x_axis+84, y_axis-25, str(value['Agent Name']).title()[:21])
        mycanvas.drawCentredString(x_axis+230, y_axis-25, str(value['Order Code']))
        mycanvas.drawCentredString(x_axis+300, y_axis-25, str(value['Order Date']))
        mycanvas.drawCentredString(x_axis+370, y_axis-25, str(value['DC No']))
        mycanvas.drawCentredString(x_axis+440, y_axis-25, str(value['Bill No']))
        mycanvas.drawRightString(x_axis+540, y_axis-25, str(value['Total Cost']))
        total += value['Total Cost']

        mycanvas.line(x_axis-20, y_axis+15, x_axis-20, y_axis-34)
        mycanvas.line(x_axis+20, y_axis+15, x_axis+20, y_axis-34)
        mycanvas.line(x_axis+80, y_axis+15, x_axis+80, y_axis-34)
        mycanvas.line(x_axis+200, y_axis+15, x_axis+200, y_axis-34)
        mycanvas.line(x_axis+265, y_axis+15, x_axis+265, y_axis-34)
        mycanvas.line(x_axis+335, y_axis+15, x_axis+335, y_axis-34)
        mycanvas.line(x_axis+405, y_axis+15, x_axis+405, y_axis-34)
        mycanvas.line(x_axis+475, y_axis+15, x_axis+475, y_axis-34)
        mycanvas.line(x_axis+545, y_axis+15, x_axis+545, y_axis-34)

        if (index+1) % 50 == 0:
            mycanvas.line(x_axis-20, y_axis-34, x_axis+545, y_axis-34)
            mycanvas.showPage()
            mycanvas.setFont('Helvetica', 12.5)
            mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawCentredString(300, 805, 'Daily Counter Report : By Product Cash Sale')
            mycanvas.setFont('Helvetica-Bold', 10)
            name_emp = ""
            for name in counter_employee_trace_obj:
                name_emp += name.employee.user_profile.user.first_name + ","
            date_in_format = datetime.datetime.strptime(ordered_date, '%Y-%m-%d')
            mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(counter_employee_trace_obj[0].counter.name)+'  |  '+'Employees : '+name_emp)



            #_____________table header_____________#
            mycanvas.setFont('Helvetica', 10)
            x_axis = 35
            y_axis = 750

            #__________top_table_lines______________#

            mycanvas.line(x_axis-20, y_axis+15, x_axis+545, y_axis+15)
            mycanvas.line(x_axis-20, y_axis-10, x_axis+545, y_axis-10)

            mycanvas.drawCentredString(x_axis, y_axis, 'S.NO')
            mycanvas.drawCentredString(x_axis+50, y_axis, 'Booth Code')
            mycanvas.drawCentredString(x_axis+140, y_axis, 'Agent Name')
            mycanvas.drawCentredString(x_axis+220, y_axis, 'Order Code')
            mycanvas.drawCentredString(x_axis+300, y_axis, 'Order Date')
            mycanvas.drawCentredString(x_axis+370, y_axis, 'DC No')
            mycanvas.drawCentredString(x_axis+440, y_axis, 'Bill No')
            mycanvas.drawCentredString(x_axis+510, y_axis, 'Amount')
            y_axis += 14

        y_axis -= 14

    # total
    mycanvas.line(x_axis-20, y_axis-20, x_axis+545, y_axis-20)
    mycanvas.line(x_axis+475, y_axis-40, x_axis+545, y_axis-40)

    mycanvas.line(x_axis+475, y_axis+15, x_axis+475, y_axis-40)
    mycanvas.line(x_axis+545, y_axis+15, x_axis+545, y_axis-40)

    mycanvas.drawRightString(x_axis+470, y_axis-35, 'Total')
    mycanvas.drawRightString(x_axis+540, y_axis-35, str(total))

    words = num2words(round(total), lang='en_IN')
    mycanvas.drawRightString(300, y_axis-35, str(words).title())


    if counter_sale_df.shape[0] > 30 :
        mycanvas.showPage()
        mycanvas.setFont('Helvetica', 12.5)
        mycanvas.drawCentredString(300, 820, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 805, 'Daily Counter Report : By Product Cash Sale')
        mycanvas.setFont('Helvetica-Bold', 10)
        name_emp = ""
        for name in counter_employee_trace_obj:
            name_emp += name.employee.user_profile.user.first_name + ","
        date_in_format = datetime.datetime.strptime(ordered_date, '%Y-%m-%d')
        mycanvas.drawString(60-30, 790, 'Date : '+str(datetime.datetime.strftime(date_in_format, '%d-%m-%Y'))+ '  |  ' +'Counter : '+str(counter_employee_trace_obj[0].counter.name)+'  |  '+'Employees : '+name_emp)
        
        challan_y = 720
        show_total_in_word = True
    else:
        challan_y = x_axis+220
        show_total_in_word = False
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

    mycanvas.drawCentredString(125,challan_y-220+y_ad,"Total")

    #line vertical
    mycanvas.line(300-x_ad,challan_y-24,300-x_ad,challan_y-225)
    mycanvas.line(140-x_ad,challan_y+14,140-x_ad,challan_y-225)
    mycanvas.line(460-x_ad,challan_y+14,460-x_ad,challan_y-225)

    mycanvas.line(200-x_ad,challan_y-24,200-x_ad,challan_y-205+y_ad)
    mycanvas.line(230-x_ad,challan_y-24,230-x_ad,challan_y-205+y_ad)

    # #top & bottom line
    mycanvas.line(140-x_ad,challan_y+14,460-x_ad,challan_y+14)
    mycanvas.line(140-x_ad,challan_y-5,460-x_ad,challan_y-5)
    mycanvas.line(140-x_ad,challan_y-24,460-x_ad,challan_y-24)
    mycanvas.line(140-x_ad,challan_y-40,460-x_ad,challan_y-40)
    mycanvas.line(140-x_ad,challan_y-225,460-x_ad,challan_y-225)
    mycanvas.setFont('Helvetica', 10)
    for i in range(8):
        mycanvas.line(140-x_ad,challan_y-65+y_ad,460-x_ad,challan_y-65+y_ad)
        challan_y -= 20

    # if show_total_in_word:
    words = num2words(round(total), lang='en_IN')
    mycanvas.drawRightString(300, challan_y-80, str(words).title())
        
    mycanvas.save()

    document = {}
    document['file_name'] = file_name
    document['alert'] = alert
    document['alert_status'] = alert_status
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf'] = encoded_image
    except Exception as err:
        print(err)
    return Response(data=document, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_goods_product_record_for_employee_order(request):
    print(request.data)
    by_order_sale_goods_obj = GoodsReceiptRecordEmployeeOrderBySaleMap.objects.filter(employee_order_by_sale__employeee_order_by_sale_group_id=request.data['sale_group_id'])
    by_order_sale_goods_list = list(by_order_sale_goods_obj.values_list('employee_order_by_sale__by_product', 'quantity_dispatched', 'employee_order_by_sale__employeee_order_by_sale_group', 'employee_order_by_sale__by_product__short_name', 'goods_receipt_record__expiry_date'))
    by_order_sale_goods_column = ['goods_product_id', 'count', 'goods_sale_group_id', 'by_product_name', 'expiry_date']
    by_order_sale_goods_df = pd.DataFrame(by_order_sale_goods_list, columns=by_order_sale_goods_column)
    by_order_sale_goods_df['return_qty'] = 0
    by_order_sale_goods_df['billing_qty'] = by_order_sale_goods_df['count']
    return Response(data=by_order_sale_goods_df.to_dict('r'), status=status.HTTP_200_OK)


def generate_grn_code():
    code_bank_obj = GoodsReceiptMasterCodeBank.objects.filter()[0]
    current_date = datetime.datetime.now().date()
    prefix_value = str(code_bank_obj.code_prefix) +  str((current_date.year))[2:]
    temp_last_digit = int(code_bank_obj.temp_last_digit)
    new_digit = temp_last_digit + 1
    code_bank_obj.temp_last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(5)
    new_grn_code = prefix_value + str(last_count)
    return new_grn_code


@api_view(['POST'])
def serve_billing_preview_for_employee_order(request):
    #construction of billing qty
    business_obj = Business.objects.get(code=request.data['business_code'])
    updated_product_data = request.data['product_list']
    by_product_order_obj = EmployeeOrderBySale.objects.filter(employeee_order_by_sale_group_id=request.data['by_sale_group_id'])
    by_product_order_list = list(by_product_order_obj.values_list('employeee_order_by_sale_group', 'employeee_order_by_sale_group__business__code', 'by_product', 'by_product__short_name', 'count', 'cost', 'by_product__cgst_percent', 'by_product__sgst_percent'))
    by_product_order_column = ['by_sale_group_id', 'business_code', 'by_product_id', 'product_name', 'count', 'cost', 'cgst_percent', 'sgst_percent']
    by_product_order_df = pd.DataFrame(by_product_order_list, columns=by_product_order_column)
    return_df = pd.DataFrame(updated_product_data)
    return_df['billing_qty'] = return_df['billing_qty'].astype(int)
    by_product_order_df = by_product_order_df.merge(return_df, how='left', left_on='by_product_id', right_on='goods_product_id')

    business_type_wise_price_obj = BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=business_obj.business_type_id)
    business_type_wise_price_list = list(business_type_wise_price_obj.values_list('by_product', 'discounted_price'))
    business_type_wise_price_column = ['price_by_product_id', 'price']
    business_type_wise_price_df = pd.DataFrame(business_type_wise_price_list, columns=business_type_wise_price_column)
    by_product_order_df = by_product_order_df.merge(business_type_wise_price_df, how='left', left_on='by_product_id', right_on='price_by_product_id')
    by_product_order_df['product_price'] = by_product_order_df['billing_qty'] * by_product_order_df['price']
    by_product_order_df['cgst_value'] = (by_product_order_df['cgst_percent']/100) * by_product_order_df['product_price']
    by_product_order_df['sgst_value'] = (by_product_order_df['sgst_percent']/100) * by_product_order_df['product_price']
    by_product_order_df['total_price'] = by_product_order_df['cgst_value'] + by_product_order_df['sgst_value'] + by_product_order_df['product_price']
    by_product_order_df = by_product_order_df.groupby('by_product_id').agg({'billing_qty': 'sum', 'by_product_name': 'first', 'product_price': 'sum', 'cgst_value': 'sum', 'sgst_value': 'sum', 'total_price': 'sum'}).reset_index()
    data_dict = {
        'product_list': by_product_order_df.to_dict('r'),
        'total_price': by_product_order_df['total_price'].sum()
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def serve_purchase_company(request):
    purchase_obj = PurchaseCompany.objects.filter(is_active=True)
    purchase_list = list(purchase_obj.values_list('id', 'company_name', 'gst_number', 'pan_number'))
    purchase_column = ['id', 'company_name', 'gst_number', 'pan_number']
    purchase_df = pd.DataFrame(purchase_list, columns=purchase_column)
    return Response(data=purchase_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def register_purchase_company(request):
    if not PurchaseCompany.objects.filter(company_name=request.data['company_name']).exists():
        purchase_obj = PurchaseCompany(company_name=request.data['company_name'],
                                    gst_number=request.data['gst_number'],
                                    created_by_id=request.user.id,
                                    pan_number=request.data['pan_number'])
        purchase_obj.save()
        data = {
            'is_available': False
        }
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data = {
            'is_available': True
        }
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def serve_sale_group_payment_method(request):
    sale_group_payment_method_obj = BySaleGroupPaymentMethod.objects.filter(is_active=True)
    sale_group_payment_method_list = list(sale_group_payment_method_obj.values_list('id', 'name'))
    sale_group_payment_method_column = ['id', 'name']
    sale_group_payment_method_df = pd.DataFrame(sale_group_payment_method_list, columns=sale_group_payment_method_column)
    return Response(data=sale_group_payment_method_df.to_dict('r'), status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_daily_sale_quantity_business_wise(request):
    business_code = request.data['booth_code']
    data_dict = {}
    if not BusinessAgentMap.objects.filter(business__code=business_code).exists():
        data_dict['available'] = False
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict['available'] = True
        from_date = request.data['from_date']
        to_date = request.data['to_date']
        date_list = pd.date_range(start=from_date, end=to_date)
        business_agent_map_obj = BusinessAgentMap.objects.get(business__code=business_code)

        business_wise_sale_obj = BusinessWiseDailySaleUpdate.objects.filter(Q(sale_date__range=[from_date, to_date], business__code=business_code) & Q(received_quantity__gt=0) | Q(opening_quantity__gt=0))
        business_wise_sale_list = list(business_wise_sale_obj.values_list('id', 'by_product__name', 'opening_quantity', 'received_quantity', 'sales_quantity', 'closing_quantity', 'sale_date', 'is_yesterday_sale_closed', 'by_product_id', 'is_edit_expired', 'edit_expiry_time'))
        business_wise_sale_column = ['id', 'product_name', 'opening_quantity', 'received_quantity', 'sales_quantity', 'closing_quantity', 'sale_date', 'is_yesterday_sale_closed', 'by_product_id', 'is_edit_expired', 'edit_expiry_time']
        business_wise_sale_df = pd.DataFrame(business_wise_sale_list, columns=business_wise_sale_column)
        business_wise_sale_df = business_wise_sale_df[(business_wise_sale_df['opening_quantity'] != 0) | business_wise_sale_df['received_quantity'] != 0]
        business_wise_sale_df['total_quantity'] = business_wise_sale_df['opening_quantity'] + business_wise_sale_df['received_quantity']
        business_wise_sale_df['sale_date'] = business_wise_sale_df['sale_date'].apply(str)
        business_wise_sale_df['is_edit_clicked'] = False
        business_wise_sale_df['edit_expiry_time'] = pd.to_datetime(business_wise_sale_df.edit_expiry_time).dt.tz_localize(None)

        business_wise_sale_df['current_date_and_time'] = pd.to_datetime("now", utc=True).tz_convert('Asia/Kolkata').to_pydatetime()
        business_wise_sale_df['current_date_and_time'] = business_wise_sale_df.current_date_and_time.dt.tz_localize(None)
        business_wise_sale_df.loc[business_wise_sale_df['edit_expiry_time'] < business_wise_sale_df['current_date_and_time'], 'is_edit_expired'] = True
        
        date_df = pd.DataFrame(date_list, columns=['date'])
        date_df['date'] = date_df['date'].dt.date
        date_df['date'] = date_df['date'].apply(str)
        date_df = date_df.reindex(index=date_df.index[::-1])

        # serve mrp rate business wise
        product_ids = list(business_wise_sale_obj.values_list('by_product', flat=True))
        business_wise_sale_df = business_wise_sale_df.fillna('N/A')
        business_wise_sale_df['is_sale_qty_entered'] = False
        business_wise_sale_df.loc[business_wise_sale_df['closing_quantity'] != 'N/A' , 'is_sale_qty_entered'] = True
        business_obj = Business.objects.get(code=business_code)
        business_type_wise_price_obj = BusinessTypeWiseByProductDiscount.objects.filter(business_type_id=business_obj.business_type_id, by_product_id__in=product_ids)
        business_type_wise_price_list = list(business_type_wise_price_obj.values_list('by_product', 'mrp'))
        business_type_wise_price_column = ['product_id', 'mrp']
        business_type_wise_price_df = pd.DataFrame(business_type_wise_price_list, columns=business_type_wise_price_column)

        business_wise_sale_df = business_wise_sale_df.merge(business_type_wise_price_df, how="left", left_on='by_product_id', right_on='product_id')
        final_df = business_wise_sale_df.groupby('sale_date').apply(lambda x: x.to_dict('r')).to_dict()
        data_dict['sale_dict'] = final_df
        data_dict['date_list'] = date_df.to_dict('r')

        file_name = f"{from_date}-{to_date}.daily_sale_bill.pdf"
        try:
            path = os.path.join('static/media/by_product/daily_sale/', str(business_code))
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join(path, file_name)
        mycanvas = canvas.Canvas(file_path, pagesize=A4)
        mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 810,
                                'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
        mycanvas.drawCentredString(300, 790, 'Daily Sale')
        mycanvas.line(250, 785, 350, 785)
        mycanvas.drawString(27, 790, 'Booth : ' + str(business_agent_map_obj.agent.first_name) + ' (' + str(business_agent_map_obj.business.code) + ')')

        main_y = 750
        table_content_y = 705

        for index, date in enumerate(data_dict['date_list']):
            if date['date'] not in data_dict['sale_dict']:
                continue
            sale_in_date_type = datetime.datetime.strptime(date['date'], '%Y-%m-%d')
            sale_in_display_format = sale_in_date_type.strftime('%d %b %Y')
            mycanvas.drawString(27, main_y, 'Date : ' + str(sale_in_display_format))
            mycanvas.setStrokeColor(colors.black)

            #table header
            mycanvas.line(25, main_y - 10, 575, main_y - 10)
            mycanvas.drawString(30, main_y - 25, 'S No.' )
            mycanvas.drawString(80, main_y - 25, 'Product' )
            mycanvas.drawString(270, main_y - 25, 'Mrp' )
            mycanvas.drawString(315, main_y - 25, 'O/B' )
            mycanvas.drawString(350, main_y - 25, 'Received' )
            mycanvas.drawString(425, main_y - 25, 'Total' )
            mycanvas.drawString(485, main_y - 25, 'Sale' )
            mycanvas.drawString(540, main_y - 25, 'C/B' )
            mycanvas.line(25, main_y - 30, 575, main_y - 30)
            for sale_index, sale in enumerate(data_dict['sale_dict'][date['date']]):
                #table content
                mycanvas.drawRightString(50, table_content_y, str(sale_index + 1) )
                mycanvas.drawString(80, table_content_y, str(sale['product_name']) )
                mycanvas.drawRightString(305, table_content_y, str(sale['mrp']) )
                mycanvas.drawRightString(330, table_content_y, str(sale['opening_quantity']) )
                mycanvas.drawRightString(380, table_content_y, str(sale['received_quantity']) )
                mycanvas.drawRightString(440, table_content_y, str(sale['total_quantity']) )
                mycanvas.drawRightString(500, table_content_y, str(sale['sales_quantity']) )
                if sale['closing_quantity'] != 'N/A':
                    mycanvas.drawRightString(560, table_content_y, str(int(sale['closing_quantity'])) )
                else:
                    mycanvas.drawRightString(560, table_content_y, str(sale['closing_quantity']) )
                table_content_y -= 15
                if table_content_y <= 50:
                    # product table lines
            
                    mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)

                    # vertical lines
                    mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
                    mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
                    mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
                    mycanvas.line(310, table_content_y + 10, 310, main_y - 10)
                    mycanvas.line(345, table_content_y + 10, 345, main_y - 10)
                    mycanvas.line(410, table_content_y + 10, 410, main_y - 10)
                    mycanvas.line(470, table_content_y + 10, 470, main_y - 10)
                    mycanvas.line(530, table_content_y + 10, 530, main_y - 10)
                    mycanvas.line(575, table_content_y + 10, 575, main_y - 10)
                    
                    mycanvas.showPage()
                    mycanvas.setStrokeColor(colors.lightgrey)
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(300, 810,
                                            'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
                    mycanvas.drawCentredString(300, 790, 'Daily Sale')
                    mycanvas.line(250, 785, 350, 785)
                    mycanvas.drawString(27, 790, 'Booth : ' + str(business_agent_map_obj.agent.first_name) + ' (' + str(business_agent_map_obj.business.code) + ')')
                    mycanvas.setStrokeColor(colors.black)
                    main_y = 750
                    table_content_y = 725
                    mycanvas.line(25, table_content_y + 15, 575, table_content_y + 15)
            
            # vertical lines
            mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
            mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
            mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
            mycanvas.line(310, table_content_y + 10, 310, main_y - 10)
            mycanvas.line(345, table_content_y + 10, 345, main_y - 10)
            mycanvas.line(410, table_content_y + 10, 410, main_y - 10)
            mycanvas.line(470, table_content_y + 10, 470, main_y - 10)
            mycanvas.line(530, table_content_y + 10, 530, main_y - 10)
            mycanvas.line(575, table_content_y + 10, 575, main_y - 10)
                
            # product table lines
            
            mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)
            if table_content_y + 10 <= 85:
                # product table lines
            
                mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)

                # vertical lines
                mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
                mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
                mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
                mycanvas.line(310, table_content_y + 10, 310, main_y - 10)
                mycanvas.line(345, table_content_y + 10, 345, main_y - 10)
                mycanvas.line(410, table_content_y + 10, 410, main_y - 10)
                mycanvas.line(470, table_content_y + 10, 470, main_y - 10)
                mycanvas.line(530, table_content_y + 10, 530, main_y - 10)
                mycanvas.line(575, table_content_y + 10, 575, main_y - 10)

                mycanvas.showPage()
                mycanvas.setStrokeColor(colors.lightgrey)
                mycanvas.setFont('Helvetica', 12)
                mycanvas.drawCentredString(300, 810,
                                        'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
                mycanvas.drawCentredString(300, 790, 'Daily Sale')
                mycanvas.line(250, 785, 350, 785)
                mycanvas.drawString(27, 790, 'Booth : ' + str(business_agent_map_obj.agent.first_name) + ' (' + str(business_agent_map_obj.business.code) + ')')
                mycanvas.setStrokeColor(colors.black)
                main_y = 750
                table_content_y = 760
            main_y = table_content_y - 20
            table_content_y = main_y - 45


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
        data_dict['document'] = document
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_daily_sale_quantity_product_wise(request):
    data_dict = {}
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    if not BusinessWiseDailySaleUpdate.objects.filter(sale_date__range=[from_date, to_date], closing_quantity__isnull=False).exists():
        data_dict['available'] = False
        return Response(data=data_dict, status=status.HTTP_200_OK)
    else:
        data_dict['available'] = True
        date_list = pd.date_range(start=from_date, end=to_date)
        business_wise_sale_obj = BusinessWiseDailySaleUpdate.objects.filter(sale_date__range=[from_date, to_date], closing_quantity__isnull=False)
        business_wise_sale_list = list(business_wise_sale_obj.values_list('id', 'by_product', 'by_product__name', 'opening_quantity', 'received_quantity', 'sales_quantity', 'closing_quantity', 'sale_date', 'is_yesterday_sale_closed', 'by_product_id'))
        business_wise_sale_column = ['id', 'product_id', 'product_name', 'opening_quantity', 'received_quantity', 'sales_quantity', 'closing_quantity', 'sale_date', 'is_yesterday_sale_closed', 'by_product_id']
        business_wise_sale_df = pd.DataFrame(business_wise_sale_list, columns=business_wise_sale_column)
        business_wise_sale_df = business_wise_sale_df[(business_wise_sale_df['opening_quantity'] != 0) | business_wise_sale_df['received_quantity'] != 0]
        business_wise_sale_df['sale_date'] = business_wise_sale_df['sale_date'].apply(str)
        date_df = pd.DataFrame(date_list, columns=['date'])
        date_df['date'] = date_df['date'].dt.date
        date_df['date'] = date_df['date'].apply(str)
        date_df = date_df.reindex(index=date_df.index[::-1])
        business_wise_sale_df = business_wise_sale_df.groupby(['sale_date', 'product_id']).agg({'product_name': 'first', 'opening_quantity': 'sum', 'received_quantity': 'sum', 'sales_quantity': 'sum', 'closing_quantity': 'sum'}).reset_index()
        business_wise_sale_df['total_quantity'] = business_wise_sale_df['opening_quantity'] + business_wise_sale_df['received_quantity']


        final_df = business_wise_sale_df.groupby('sale_date').apply(lambda x: x.to_dict('r')).to_dict()
        data_dict['sale_dict'] = final_df
        data_dict['date_list'] = date_df.to_dict('r')

        file_name = f"{from_date}-{to_date}.daily_sale_bill.pdf"
        file_path = os.path.join('static/media/by_product/daily_sale_product_wise/')
        try:
            path = file_path
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join('static/media/by_product/daily_sale_product_wise/', file_name)
        print(file_path)
        mycanvas = canvas.Canvas(file_path, pagesize=A4)
        mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 810,
                                'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
        mycanvas.drawCentredString(300, 790, 'Daily Sale Product Wise')
        mycanvas.line(250, 785, 350, 785)

        main_y = 750
        table_content_y = 705

        for index, date in enumerate(data_dict['date_list']):
            if date['date'] not in data_dict['sale_dict']:
                continue
            sale_in_date_type = datetime.datetime.strptime(date['date'], '%Y-%m-%d')
            sale_in_display_format = sale_in_date_type.strftime('%d %b %Y')
            mycanvas.drawString(27, main_y, 'Date : ' + str(sale_in_display_format))
            mycanvas.setStrokeColor(colors.black)

            #table header
            mycanvas.line(25, main_y - 10, 575, main_y - 10)
            mycanvas.drawString(30, main_y - 25, 'S No.' )
            mycanvas.drawString(80, main_y - 25, 'Product' )
            mycanvas.drawString(315, main_y - 25, 'O/B' )
            mycanvas.drawString(350, main_y - 25, 'Received' )
            mycanvas.drawString(425, main_y - 25, 'Total' )
            mycanvas.drawString(485, main_y - 25, 'Sale' )
            mycanvas.drawString(540, main_y - 25, 'C/B' )
            mycanvas.line(25, main_y - 30, 575, main_y - 30)
            for sale_index, sale in enumerate(data_dict['sale_dict'][date['date']]):
                #table content
                mycanvas.drawRightString(50, table_content_y, str(sale_index + 1) )
                mycanvas.drawString(80, table_content_y, str(sale['product_name']) )
                mycanvas.drawRightString(330, table_content_y, str(sale['opening_quantity']) )
                mycanvas.drawRightString(380, table_content_y, str(sale['received_quantity']) )
                mycanvas.drawRightString(440, table_content_y, str(sale['total_quantity']) )
                mycanvas.drawRightString(500, table_content_y, str(sale['sales_quantity']) )
                if sale['closing_quantity'] != 'N/A':
                    mycanvas.drawRightString(560, table_content_y, str(int(sale['closing_quantity'])) )
                else:
                    mycanvas.drawRightString(560, table_content_y, str(sale['closing_quantity']) )
                table_content_y -= 15
                if table_content_y <= 50:
                    print(table_content_y)
                    # product table lines
            
                    mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)

                    # vertical lines
                    mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
                    mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
                    mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
                    mycanvas.line(345, table_content_y + 10, 345, main_y - 10)
                    mycanvas.line(410, table_content_y + 10, 410, main_y - 10)
                    mycanvas.line(470, table_content_y + 10, 470, main_y - 10)
                    mycanvas.line(530, table_content_y + 10, 530, main_y - 10)
                    mycanvas.line(575, table_content_y + 10, 575, main_y - 10)
                    
                    mycanvas.showPage()
                    mycanvas.setStrokeColor(colors.lightgrey)
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(300, 810,
                                            'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
                    mycanvas.drawCentredString(300, 790, 'Daily Sale')
                    mycanvas.line(250, 785, 350, 785)
                    mycanvas.drawString(27, 790, 'Booth : ' + str(business_agent_map_obj.agent.first_name) + ' (' + str(business_agent_map_obj.business.code) + ')')
                    mycanvas.setStrokeColor(colors.black)
                    main_y = 750
                    table_content_y = 725
                    mycanvas.line(25, table_content_y + 15, 575, table_content_y + 15)
                
                

            
            # vertical lines
            mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
            mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
            mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
            mycanvas.line(345, table_content_y + 10, 345, main_y - 10)
            mycanvas.line(410, table_content_y + 10, 410, main_y - 10)
            mycanvas.line(470, table_content_y + 10, 470, main_y - 10)
            mycanvas.line(530, table_content_y + 10, 530, main_y - 10)
            mycanvas.line(575, table_content_y + 10, 575, main_y - 10)
                
            # product table lines
            
            mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)
            if table_content_y + 10 <= 85:
                # product table lines
            
                mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)

                # vertical lines
                mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
                mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
                mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
                mycanvas.line(310, table_content_y + 10, 310, main_y - 10)
                mycanvas.line(345, table_content_y + 10, 345, main_y - 10)
                mycanvas.line(410, table_content_y + 10, 410, main_y - 10)
                mycanvas.line(470, table_content_y + 10, 470, main_y - 10)
                mycanvas.line(530, table_content_y + 10, 530, main_y - 10)
                mycanvas.line(575, table_content_y + 10, 575, main_y - 10)

                mycanvas.showPage()
                mycanvas.setStrokeColor(colors.lightgrey)
                mycanvas.setFont('Helvetica', 12)
                mycanvas.drawCentredString(300, 810,
                                        'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
                mycanvas.drawCentredString(300, 790, 'Daily Sale Product Wise')
                mycanvas.line(250, 785, 350, 785)
                mycanvas.setStrokeColor(colors.black)
                main_y = 750
                table_content_y = 760
            main_y = table_content_y - 20
            table_content_y = main_y - 45

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
        data_dict['document'] = document
        return Response(data=data_dict, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_edit_daily_sale_quantity_business_wise(request):
    sale = request.data
    previous_business_wise_sale_obj = BusinessWiseDailySaleUpdate.objects.get(id=sale['id'])
    business_wise_sale_obj = BusinessWiseDailySaleUpdate.objects.get(id=sale['id'])
    business_wise_sale_obj.sales_quantity = sale['sales_quantity']
    opening_quantity = business_wise_sale_obj.opening_quantity
    received_quantity = business_wise_sale_obj.received_quantity
    business_wise_sale_obj.closing_quantity = (opening_quantity + received_quantity) - sale['sales_quantity']
    # set expiry time to today 11:53 pm
    business_wise_sale_obj.edit_expiry_time = datetime.datetime.now().replace(hour=23, minute=59)
    business_wise_sale_obj.save()

    business_wise_daily_sale_edit_obj = BusinessWiseDailySaleEditTrace(business_id=previous_business_wise_sale_obj.business.id,
                                                                       sale_date=previous_business_wise_sale_obj.sale_date,
                                                                       by_product=previous_business_wise_sale_obj.by_product,
                                                                       old_opening_quantity=previous_business_wise_sale_obj.opening_quantity,
                                                                       old_received_quantity=previous_business_wise_sale_obj.received_quantity,
                                                                       old_sales_quantity=previous_business_wise_sale_obj.sales_quantity,
                                                                       old_closing_quantity=previous_business_wise_sale_obj.closing_quantity,
                                                                       opening_quantity=business_wise_sale_obj.opening_quantity,
                                                                       received_quantity=business_wise_sale_obj.received_quantity,
                                                                       sales_quantity=business_wise_sale_obj.sales_quantity,
                                                                       closing_quantity=business_wise_sale_obj.closing_quantity,
                                                                       edited_by_id=request.user.id,
                                                                       edited_at=datetime.datetime.now()
                                                                       )
    business_wise_daily_sale_edit_obj.save()

    product_id = business_wise_sale_obj.by_product.id
    business_id = business_wise_sale_obj.business.id
    sale_date = business_wise_sale_obj.sale_date
    previous_date =  sale_date - datetime.timedelta(days=1) 

    # check previous sale is exists and change is_edit_expired to true so they cannot edit the sale if next day sale is closed
    if BusinessWiseDailySaleUpdate.objects.filter(sale_date=previous_date, business_id=business_id, by_product_id=product_id).exists():
        previous_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=previous_date, business_id=business_id, by_product_id=product_id)
        previous_sale_obj.is_edit_expired = True
        previous_sale_obj.save()
    
    next_date = sale_date + datetime.timedelta(days=1) 
    if business_wise_sale_obj.closing_quantity == 0:
        if BusinessWiseDailySaleUpdate.objects.filter(sale_date__gt=sale_date, business_id=business_id, by_product_id=product_id).exists():
            last_sale_obj = BusinessWiseDailySaleUpdate.objects.filter(sale_date__gt=sale_date, business_id=business_id, by_product_id=product_id).order_by('sale_date')[0]
            last_sale_obj.is_yesterday_sale_closed = True
            last_sale_obj.save()
        if BusinessWiseDailySaleUpdate.objects.filter(sale_date=next_date, business_id=business_id, by_product_id=product_id).exists():
            next_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=next_date, business_id=business_id, by_product_id=product_id)
            next_sale_obj.opening_quantity = business_wise_sale_obj.closing_quantity
            next_sale_obj.is_yesterday_sale_closed = True
            next_sale_obj.save()
    else:
        if BusinessWiseDailySaleUpdate.objects.filter(sale_date=next_date, business_id=business_id, by_product_id=product_id).exists():
            next_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=next_date, business_id=business_id, by_product_id=product_id)
            next_sale_obj.opening_quantity = business_wise_sale_obj.closing_quantity
            next_sale_obj.is_yesterday_sale_closed = True
            next_sale_obj.save()
        else:
            business_sale_obj = BusinessWiseDailySaleUpdate(business_id=business_id,
                                                            sale_date=next_date,
                                                            by_product_id=product_id,
                                                            created_by_id=request.user.id,
                                                            is_yesterday_sale_closed=True,
                                                            opening_quantity=business_wise_sale_obj.closing_quantity,
                                                            updated_by_id=request.user.id)
            business_sale_obj.save()
    
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def update_daily_sale_quantity_business_wise(request):
    sale = request.data
    business_wise_sale_obj = BusinessWiseDailySaleUpdate.objects.get(id=sale['id'])
    business_wise_sale_obj.sales_quantity = sale['sales_quantity']
    opening_quantity = business_wise_sale_obj.opening_quantity
    received_quantity = business_wise_sale_obj.received_quantity
    business_wise_sale_obj.closing_quantity = (opening_quantity + received_quantity) - sale['sales_quantity']
    # set expiry time to today 11:53 pm
    business_wise_sale_obj.edit_expiry_time = datetime.datetime.now().replace(hour=23, minute=59)
    business_wise_sale_obj.save()

    product_id = business_wise_sale_obj.by_product.id
    business_id = business_wise_sale_obj.business.id
    sale_date = business_wise_sale_obj.sale_date
    previous_date =  sale_date - datetime.timedelta(days=1) 

    # check previous sale is exists and change is_edit_expired to true so they cannot edit the sale if next day sale is closed
    if BusinessWiseDailySaleUpdate.objects.filter(sale_date=previous_date, business_id=business_id, by_product_id=product_id).exists():
        previous_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=previous_date, business_id=business_id, by_product_id=product_id)
        previous_sale_obj.is_edit_expired = True
        previous_sale_obj.save()
    
    next_date = sale_date + datetime.timedelta(days=1) 
    if business_wise_sale_obj.closing_quantity == 0:
        if BusinessWiseDailySaleUpdate.objects.filter(sale_date__gt=sale_date, business_id=business_id, by_product_id=product_id).exists():
            last_sale_obj = BusinessWiseDailySaleUpdate.objects.filter(sale_date__gt=sale_date, business_id=business_id, by_product_id=product_id).order_by('sale_date')[0]
            last_sale_obj.is_yesterday_sale_closed = True
            last_sale_obj.save()
    else:
        if BusinessWiseDailySaleUpdate.objects.filter(sale_date=next_date, business_id=business_id, by_product_id=product_id).exists():
            next_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=next_date, business_id=business_id, by_product_id=product_id)
            next_sale_obj.opening_quantity = business_wise_sale_obj.closing_quantity
            next_sale_obj.is_yesterday_sale_closed = True
            next_sale_obj.save()
        else:
            business_sale_obj = BusinessWiseDailySaleUpdate(business_id=business_id,
                                                            sale_date=next_date,
                                                            by_product_id=product_id,
                                                            created_by_id=request.user.id,
                                                            is_yesterday_sale_closed=True,
                                                            opening_quantity=business_wise_sale_obj.closing_quantity,
                                                            updated_by_id=request.user.id)
            business_sale_obj.save()
    
    return Response(status=status.HTTP_200_OK)


    
@api_view(['POST'])
def monthly_sale_regisred_dealers(request):
    print(request.data)
    month_in_string = request.data['month']['month_in_string']
    month = request.data['month']['month_in_integer']+1
    print(month)
    year = request.data['month']['year']
    register_result = request.data['register_status']

    if BySaleGroup.objects.filter(ordered_date__year=year, ordered_date__month=month, business__businessagentmap__agent__agent_profile__gst_number__isnull=False).exists():
        print('Yes')
        by_sale_group_obj = BySaleGroup.objects.filter(ordered_date__year=year,ordered_date__month=month,  business__businessagentmap__agent__agent_profile__gst_number__isnull=False)
        by_sale_group_values_list = list(by_sale_group_obj.values_list('order_code', 'ordered_date', 'total_cost', 'bysale__by_product__igst_percent', 'bysale__cost', 'bysale__cgst_value', 'bysale__sgst_value', 'business__businessagentmap__agent__first_name', 'business__businessagentmap__agent__agent_profile__gst_number'))
        by_sale_group_col = ["INVOICENO", "INVOICEDATE", "INVOICEVALUE","RATE", "TAXABLEVALUE", "CGST", "SGST", "NAME", "GSTIN_UNIFORMRECIEPT"]
        by_sale_group_df = pd.DataFrame(by_sale_group_values_list, columns=by_sale_group_col)
        by_sale_group_df['IGST'] = 0.00
        by_sale_group_df = by_sale_group_df.groupby(['INVOICENO','RATE']).agg({'INVOICEDATE':'first', 'INVOICEVALUE': 'first', 'TAXABLEVALUE': 'sum', 'CGST':'sum', 'SGST':'sum', 'NAME':'first', 'GSTIN_UNIFORMRECIEPT':'first', 'IGST':'sum'}).reset_index()
        by_sale_group_df = by_sale_group_df[['GSTIN_UNIFORMRECIEPT', 'NAME', 'INVOICENO', 'INVOICEDATE', 'INVOICEVALUE', 'RATE', 'TAXABLEVALUE', 'CGST', 'SGST', 'IGST']]
        by_sale_group_df = by_sale_group_df.fillna('-') 
        final_df = by_sale_group_df
        final_dict = final_df.to_dict('r')

        # ____________________________pdf_______________________________________________
        file_name =  'BYPRODUCT SALE REPORT.pdf'
        file_path = os.path.join('static/media/by_product/monthly_report/', file_name)
        mycanvas = canvas.Canvas(file_path, pagesize=(11.694 * inch, 8.264 * inch))

        # ________Head_lines________#
        mycanvas.setFont('Helvetica-Bold', 11)
        mycanvas.drawCentredString(405, 575, 'AAVIN-COIMBATORE')
        mycanvas.drawCentredString(405, 556, 'BYPRODUCT SALE REPORT - '+str(month_in_string[:3])+"-"+str(year)[-2:]+' REGISTRED DEALEARS')

        x = 50
        y = 530
        mycanvas.setFont('Helvetica-Bold', 8.4)
        mycanvas.drawCentredString(x+10-20,y,"GSTIN")
        mycanvas.drawCentredString(x+130-20,y,"NAME")
        mycanvas.drawCentredString(x+260-10,y,"INVOICENO")
        mycanvas.drawCentredString(x+365-20,y,"INVOICEDATE")
        mycanvas.drawCentredString(x+435-20,y,"INVOICEVALUE")
        mycanvas.drawCentredString(x+490-20,y,"RATE")
        mycanvas.drawCentredString(x+570-20,y,"TAXABLEVALUE")
        mycanvas.drawCentredString(x+660-20,y,"CGST")
        mycanvas.drawCentredString(x+720-20,y,"SGST")
        mycanvas.drawCentredString(x+820-55,y,"IGST")

        # Heading lines
        mycanvas.line(x-30,y+15, x+780, y+15)
        mycanvas.line(x-30,y-5, x+780, y-5)

        header_line_y = y+15
        y_point = 505
        x1_line = 20
        x2_line = 830
        mycanvas.setFont('Helvetica', 8.3)

        for index, product in final_df.iterrows():
        #     print(index, product['TAXABLEVALUE'])
            date_in_format = datetime.datetime.strftime(product['INVOICEDATE'],'%d-%b-%Y')
            mycanvas.setFont('Helvetica', 8.3)
            mycanvas.drawString(30, y_point, str(product['GSTIN_UNIFORMRECIEPT']))
            mycanvas.drawString(150, y_point, str(product['NAME'])[:15])
            mycanvas.drawString(275, y_point, str(product['INVOICENO']))
            mycanvas.drawString(370, y_point, str(date_in_format))
            mycanvas.drawRightString(498, y_point, str(product['INVOICEVALUE']))
            mycanvas.drawRightString(555, y_point, str(int(product['RATE'])))
            mycanvas.drawRightString(647, y_point, str(product['TAXABLEVALUE']))
            mycanvas.drawRightString(713, y_point, str(product['CGST']))
            mycanvas.drawRightString(784, y_point, str(product['SGST']))
            mycanvas.drawRightString(825, y_point, str(product['IGST']))
            mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)
            y_point -=20

            #for next page once completed 24 lines in previous page
            if (index+1) % 25 == 0:
                #vertical line for previous page 
                mycanvas.line(x-30,header_line_y, x-30, y_point+15)
                mycanvas.line(x+95,header_line_y, x+95, y_point+15)
                mycanvas.line(x+225,header_line_y, x+225, y_point+15)
                mycanvas.line(x+315,header_line_y, x+315, y_point+15)
                mycanvas.line(x+380,header_line_y, x+380, y_point+15)
                mycanvas.line(x+455,header_line_y, x+455, y_point+15)
                mycanvas.line(x+510,header_line_y, x+510, y_point+15)
                mycanvas.line(x+600,header_line_y, x+600, y_point+15)
                mycanvas.line(x+670,header_line_y, x+670, y_point+15)
                mycanvas.line(x+740,header_line_y, x+740, y_point+15)
                mycanvas.line(x+780,header_line_y, x+780, y_point+15)
                mycanvas.showPage()
                y_point = 505
                x1_line = 20
                x2_line = 830

                #for new next page hearders
                mycanvas.setFont('Helvetica-Bold', 8.4)
                mycanvas.drawCentredString(x+10-20,y,"GSTIN")
                mycanvas.drawCentredString(x+130-20,y,"NAME")
                mycanvas.drawCentredString(x+260-10,y,"INVOICENO")
                mycanvas.drawCentredString(x+365-20,y,"INVOICEDATE")
                mycanvas.drawCentredString(x+435-20,y,"INVOICEVALUE")
                mycanvas.drawCentredString(x+490-20,y,"RATE")
                mycanvas.drawCentredString(x+570-20,y,"TAXABLEVALUE")
                mycanvas.drawCentredString(x+660-20,y,"CGST")
                mycanvas.drawCentredString(x+720-20,y,"SGST")
                mycanvas.drawCentredString(x+820-55,y,"IGST")

                # Heading lines
                mycanvas.line(x-30,y+15, x+780, y+15)
                mycanvas.line(x-30,y-5, x+780, y-5)
        #end lines for remining columns
        mycanvas.line(x-30,header_line_y, x-30, y_point-5)
        mycanvas.line(x+95,header_line_y, x+95, y_point-5)
        mycanvas.line(x+225,header_line_y, x+225, y_point-5)
        mycanvas.line(x+315,header_line_y, x+315, y_point-5)
        mycanvas.line(x+380,header_line_y, x+380, y_point-5)
        mycanvas.line(x+455,header_line_y, x+455, y_point-5)
        mycanvas.line(x+510,header_line_y, x+510, y_point-5)
        mycanvas.line(x+600,header_line_y, x+600, y_point-5)
        mycanvas.line(x+670,header_line_y, x+670, y_point-5)
        mycanvas.line(x+740,header_line_y, x+740, y_point-5)
        mycanvas.line(x+780,header_line_y, x+780, y_point-5)

        #lastline (for Total)
        mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)
        mycanvas.setFont('Helvetica-Bold' ,9)
        mycanvas.drawString(150, y_point, str("TOTAL"))
        mycanvas.drawRightString(647, y_point, str(final_df['TAXABLEVALUE'].sum()))
        mycanvas.drawRightString(717, y_point, str(final_df['CGST'].sum()))
        mycanvas.drawRightString(785, y_point, str(final_df['SGST'].sum()))
        mycanvas.drawRightString(825, y_point, str(final_df['IGST'].sum()))

        mycanvas.save()
    else:
        print('no data')
        document = False
        return Response(data=document, status=status.HTTP_200_OK)

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
def monthly_sale_non_regisred_dealers(request):
    print(request.data)
    month_in_string = request.data['month']['month_in_string']
    month = request.data['month']['month_in_integer']+1
    print(month)
    year = request.data['month']['year']
    register_result = request.data['register_status']

    if BySaleGroup.objects.filter(ordered_date__year=year,ordered_date__month=month,  business__businessagentmap__agent__agent_profile__gst_number__isnull=True).exists():
        print('Yes')
        by_sale_group_obj = BySaleGroup.objects.filter(ordered_date__year=year,ordered_date__month=month,  business__businessagentmap__agent__agent_profile__gst_number__isnull=True)
        by_sale_group_values_list = list(by_sale_group_obj.values_list('order_code', 'ordered_date', 'total_cost', 'bysale__by_product__igst_percent', 'bysale__cost', 'bysale__cgst_value', 'bysale__sgst_value', 'business__businessagentmap__agent__first_name'))
        by_sale_group_col = ["INVOICENO", "INVOICEDATE", "INVOICEVALUE","RATE", "TAXABLEVALUE", "CGST", "SGST", "NAME"]
        by_sale_group_df = pd.DataFrame(by_sale_group_values_list, columns=by_sale_group_col)
        by_sale_group_df['IGST'] = 0.00
        by_sale_group_df = by_sale_group_df.groupby(['INVOICENO','RATE']).agg({'INVOICEDATE':'first', 'INVOICEVALUE': 'first', 'TAXABLEVALUE': 'sum', 'CGST':'sum', 'SGST':'sum', 'NAME':'first', 'IGST':'sum'}).reset_index()
        by_sale_group_df = by_sale_group_df[['NAME', 'INVOICENO', 'INVOICEDATE', 'INVOICEVALUE', 'RATE', 'TAXABLEVALUE', 'CGST', 'SGST', 'IGST']]
        by_sale_group_df = by_sale_group_df.fillna('-') 
        final_df = by_sale_group_df
        final_dict = final_df.to_dict('r')


        # ____________________________pdf_______________________________________________
        file_name =  'BYPRODUCT SALE REPORT.pdf'
        file_path = os.path.join('static/media/by_product/monthly_report/', file_name)
        mycanvas = canvas.Canvas(file_path, pagesize=(11.694 * inch, 8.264 * inch))

        # ________Head_lines________#
        mycanvas.setFont('Helvetica-Bold', 11)
        mycanvas.drawCentredString(405, 575, 'AAVIN-COIMBATORE')
        mycanvas.drawCentredString(405, 556, 'BYPRODUCT SALE REPORT - '+str(month_in_string[:3])+"-"+str(year)[-2:]+' UNREGISTRED DEALEARS')

        x = 50
        y = 530
        # To Write headers
        mycanvas.setFont('Helvetica-Bold', 8.4)
        mycanvas.drawCentredString(x+20,y,"NAME")
        mycanvas.drawCentredString(x+150,y,"INVOICENO")
        mycanvas.drawCentredString(x+260-10,y,"INVOICEDATE")
        mycanvas.drawCentredString(x+365-30,y,"INVOICEVALUE")
        mycanvas.drawCentredString(x+435-20,y,"RATE")
        mycanvas.drawCentredString(x+489,y,"TAXABLEVALUE")
        mycanvas.drawCentredString(x+570,y,"CGST")
        mycanvas.drawCentredString(x+635,y,"SGST")
        mycanvas.drawCentredString(x+725,y,"IGST")

        # Heading lines
        mycanvas.line(x-30,y+15, x+770, y+15)
        mycanvas.line(x-30,y-5, x+770, y-5)

        header_line_y = y+15
        y_point = 505
        x1_line = 20
        x2_line = 820

        for index, product in final_df.iterrows():
            #print(index, product['TAXABLEVALUE'])
            date_in_format = datetime.datetime.strftime(product['INVOICEDATE'],'%d-%b-%Y')
            mycanvas.setFont('Helvetica', 8.3)
            mycanvas.drawString(30, y_point, str(product['NAME'])[:15])
            mycanvas.drawString(160, y_point, str(product['INVOICENO']))
            mycanvas.drawString(275, y_point, str(date_in_format))
            mycanvas.drawRightString(430, y_point, str(product['INVOICEVALUE']))
            mycanvas.drawRightString(480, y_point, str(int(product['RATE'])))
            mycanvas.drawRightString(578, y_point, str(product['TAXABLEVALUE']))
            mycanvas.drawRightString(655, y_point, str(product['CGST']))
            mycanvas.drawRightString(730, y_point, str(product['SGST']))
            mycanvas.drawRightString(805, y_point, str(product['IGST']))
            #end horizontal Line
            mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)
            y_point -=20

            #for next page once completed 24 lines in previous page
            if (index+1) % 24 == 0:
                #vertical line for previous page 
                mycanvas.line(x-30,header_line_y, x-30, y_point+15)
                mycanvas.line(x+100,header_line_y, x+100, y_point+15)
                mycanvas.line(x+215,header_line_y, x+215, y_point+15)
                mycanvas.line(x+290,header_line_y, x+290, y_point+15)
                mycanvas.line(x+390,header_line_y, x+390, y_point+15)
                mycanvas.line(x+445,header_line_y, x+445, y_point+15)
                mycanvas.line(x+535,header_line_y, x+535, y_point+15)
                mycanvas.line(x+610,header_line_y, x+610, y_point+15)
                mycanvas.line(x+685,header_line_y, x+685, y_point+15)
                mycanvas.line(x+770,header_line_y, x+770, y_point+15)
                mycanvas.showPage()
                y_point = 505
                x1_line = 20
                x2_line = 820

                #for new next page hearders
                mycanvas.setFont('Helvetica-Bold', 8.4)
                mycanvas.drawCentredString(x+20,y,"NAME")
                mycanvas.drawCentredString(x+150,y,"INVOICENO")
                mycanvas.drawCentredString(x+260-10,y,"INVOICEDATE")
                mycanvas.drawCentredString(x+365-30,y,"INVOICEVALUE")
                mycanvas.drawCentredString(x+435-20,y,"RATE")
                mycanvas.drawCentredString(x+489,y,"TAXABLEVALUE")
                mycanvas.drawCentredString(x+570,y,"CGST")
                mycanvas.drawCentredString(x+635,y,"SGST")
                mycanvas.drawCentredString(x+725,y,"IGST")


                # Heading lines
                mycanvas.line(x-30,y+15, x+770, y+15)
                mycanvas.line(x-30,y-5, x+770, y-5)

        #end verticle lines for remining columns
        mycanvas.line(x-30,header_line_y, x-30, y_point-5)
        mycanvas.line(x+100,header_line_y, x+100, y_point-5)
        mycanvas.line(x+215,header_line_y, x+215, y_point-5)
        mycanvas.line(x+290,header_line_y, x+290, y_point-5)
        mycanvas.line(x+390,header_line_y, x+390, y_point-5)
        mycanvas.line(x+445,header_line_y, x+445, y_point-5)
        mycanvas.line(x+535,header_line_y, x+535, y_point-5)
        mycanvas.line(x+610,header_line_y, x+610, y_point-5)
        mycanvas.line(x+685,header_line_y, x+685, y_point-5)
        mycanvas.line(x+770,header_line_y, x+770, y_point-5)
        
        mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)
        
        #lastline (for Total)
        mycanvas.setFont('Helvetica-Bold' ,9)
        mycanvas.drawString(155, y_point, str("TOTAL"))
        mycanvas.drawRightString(575, y_point, str(final_df['TAXABLEVALUE'].sum()))
        mycanvas.drawRightString(655, y_point, str(final_df['CGST'].sum()))
        mycanvas.drawRightString(730, y_point, str(final_df['SGST'].sum()))
        mycanvas.drawRightString(805, y_point, str(final_df['IGST'].sum()))


        mycanvas.save()
    else:
        print('no data')
        document = False
        return Response(data=document, status=status.HTTP_200_OK)
    
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
def monthly_sale_register_and_unregisred_dealers(request):
    print(request.data)
    month_in_string = request.data['month']['month_in_string']
    month = request.data['month']['month_in_integer']+1
    print(month)
    year = request.data['month']['year']
    
    #register
    by_sale_group_obj = BySaleGroup.objects.filter(ordered_date__year=year,ordered_date__month=month, business__businessagentmap__agent__agent_profile__gst_number__isnull=False)
    by_sale_group_values_list = list(by_sale_group_obj.values_list('bysale__by_product__igst_percent', 'bysale__cost', 'bysale__cgst_value', 'bysale__sgst_value'))
    by_sale_group_col = ["RATE OF TAX", "TAXABLE VALUE", "CGST", "SGST"]
    by_sale_group_df = pd.DataFrame(by_sale_group_values_list, columns=by_sale_group_col)
    by_sale_group_df['IGST'] = 0.00
    by_sale_group_df['TYPE'] = 'REG SALES-LOCAL'
    by_sale_group_df = by_sale_group_df.groupby(['RATE OF TAX']).agg({'TYPE':'first' ,'TAXABLE VALUE': 'sum', 'CGST':'sum', 'SGST':'sum', 'IGST':'sum'}).reset_index()
    by_sale_group_df = by_sale_group_df[['TYPE', 'RATE OF TAX', 'TAXABLE VALUE', 'IGST', 'CGST', 'SGST']]
    by_sale_group_df['TAXABLE VALUE'] = by_sale_group_df['TAXABLE VALUE'].astype(float)
    by_sale_group_df['CGST'] = by_sale_group_df['CGST'].astype(float)
    by_sale_group_df['SGST'] = by_sale_group_df['SGST'].astype(float)
    by_sale_group_df.loc[:,'TOTAL'] = by_sale_group_df.sum(axis=1)
    by_sale_register_df = by_sale_group_df

    by_sale_group_df[['TAXABLE VALUE', 'IGST', 'CGST', 'SGST', 'TOTAL']].sum()
    by_sale_group_df.append(by_sale_group_df[['TAXABLE VALUE', 'IGST', 'CGST', 'SGST', 'TOTAL']].sum().rename('TOTAL'))
    by_sale_group_df.loc['TOTAL'] = by_sale_group_df[['TAXABLE VALUE', 'IGST', 'CGST', 'SGST', 'TOTAL']].sum()

    by_sale_group_df.loc[by_sale_group_df.index[-1], "TYPE"] = 'TOTAL'
    by_sale_group_df

    #unregister
    by_sale_unregister_group_obj = BySaleGroup.objects.filter(ordered_date__year=year,ordered_date__month=month, business__businessagentmap__agent__agent_profile__gst_number__isnull=True)
    by_sale_unregister_group_obj_values_list = list(by_sale_unregister_group_obj.values_list('bysale__by_product__igst_percent', 'bysale__cost', 'bysale__cgst_value', 'bysale__sgst_value'))
    by_sale_group_col = ["RATE OF TAX", "TAXABLE VALUE", "CGST", "SGST"]
    by_sale_unregister_group_df = pd.DataFrame(by_sale_unregister_group_obj_values_list, columns=by_sale_group_col)
    by_sale_unregister_group_df['IGST'] = 0.00
    by_sale_unregister_group_df['TYPE'] = 'UN-REG SALES-LOCAL'
    by_sale_unregister_group_df = by_sale_unregister_group_df.groupby(['RATE OF TAX']).agg({'TYPE':'first' ,'TAXABLE VALUE': 'sum', 'CGST':'sum', 'SGST':'sum', 'IGST':'sum'}).reset_index()
    by_sale_unregister_group_df = by_sale_unregister_group_df[['TYPE', 'RATE OF TAX', 'TAXABLE VALUE', 'IGST', 'CGST', 'SGST']]
    by_sale_unregister_group_df['TAXABLE VALUE'] = by_sale_unregister_group_df['TAXABLE VALUE'].astype(float)
    by_sale_unregister_group_df['CGST'] = by_sale_unregister_group_df['CGST'].astype(float)
    by_sale_unregister_group_df['SGST'] = by_sale_unregister_group_df['SGST'].astype(float)
    by_sale_unregister_group_df.loc[:,'TOTAL'] = by_sale_unregister_group_df.sum(axis=1)
    by_sale_unregister_df = by_sale_unregister_group_df

    #total for columns
    by_sale_unregister_df[['TAXABLE VALUE', 'IGST', 'CGST', 'SGST', 'TOTAL']].sum()
    by_sale_unregister_df.append(by_sale_unregister_df[['TAXABLE VALUE', 'IGST', 'CGST', 'SGST', 'TOTAL']].sum().rename('TOTAL'))
    by_sale_unregister_df.loc['TOTAL'] = by_sale_unregister_df[['TAXABLE VALUE', 'IGST', 'CGST', 'SGST', 'TOTAL']].sum()

    #add TOTAL in first column
    by_sale_unregister_df.loc[by_sale_unregister_df.index[-1], "TYPE"] = 'TOTAL'

    file_name = f'Sale Details.xlsx'
    file_path = os.path.join('static/media/by_product/', file_name)


    writer = pd.ExcelWriter(file_path,engine='xlsxwriter')   
    workbook=writer.book
    worksheet=workbook.add_worksheet('sale_details')

    format = workbook.add_format({'bold': True})
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'yellow'})
    writer.sheets['sale_details'] = worksheet
    worksheet.merge_range('A1:G1', 'Sale Details'+" "+str(month_in_string[:3])+"-"+str(year)[-2:], merge_format)
    by_sale_group_df.to_excel(writer,sheet_name='sale_details',startrow=2 , startcol=0, index=False)
    # worksheet.write('A6', 'TOTAL',format)
    by_sale_unregister_df.to_excel(writer,sheet_name='sale_details',startrow=11, startcol=0, index=False) 
    writer.save()
    print('ok')

    print(file_path)
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




def to_find_values(by_product_unit_name, group_unit, total_qty):
#     print('ok')
    value = 0
    if by_product_unit_name == 'Nos.' or by_product_unit_name == 'L' or by_product_unit_name == 'Kg':
        value = total_qty
    else:
        value = total_qty / 1000
    return value


@api_view(['POST'])
def monthly_product_sales_abstract_report(request):
    month_in_string = request.data['month']['month_in_string']
    month = request.data['month']['month_in_integer']+1
    year = request.data['month']['year']

    # df_one / by_sale_df_all
    by_sale_obj = BySale.objects.filter(by_sale_group__ordered_date__year=year,by_sale_group__ordered_date__month=month)
    by_sale_values = list(by_sale_obj.values_list( 'by_product_id','by_product__unit__name','by_product__by_product_group_id','by_product__by_product_group__unit__name', 'by_product__quantity' ,'count',))
    by_sale_columns = ["by_product_id", "by_product_unit_name","group_id","group_unit","by_product_quantity", "count"]
    by_sale_df = pd.DataFrame(by_sale_values, columns=by_sale_columns)
    by_sale_df_all = by_sale_df
    by_sale_df_all['total_qty'] = by_sale_df_all['by_product_quantity'].astype(float)*by_sale_df_all['count']
    by_sale_df_all['new_total'] = by_sale_df_all.apply(lambda x: to_find_values(x['by_product_unit_name'], x['group_unit'], x['total_qty']), axis=1)
    by_sale_df_all['new_total'] = by_sale_df_all['new_total'].astype(float)

    by_sale_df_all = by_sale_df_all.groupby(['group_id']).agg({'new_total':'sum'}).reset_index()

    # df_two / by_sale_df
    by_sale_values = list(by_sale_obj.values_list('by_sale_group_id', 'by_product_id','by_product__by_product_group_id','by_product__by_product_group__name', 'by_product__by_product_group__unit__display_name','by_product__name' ,'count','cost' ,'cgst_value', 'sgst_value', 'total_cost'))
    by_sale_columns = ["by_sale_group_id", "by_product_id", "group_id","group_name",'display_name',"by_product_name", "count","cost", "cgst", "sgst", "total_cost"]
    by_sale_df = pd.DataFrame(by_sale_values, columns=by_sale_columns)
    by_sale_df = by_sale_df.groupby(['group_id', 'group_name']).agg({'by_sale_group_id':'first','count':'first', 'cost':'sum', 'cgst': 'sum', 'sgst': 'sum', 'total_cost':'sum','display_name':'first'}).reset_index() 

    # merging two df
    merge_df = pd.merge(by_sale_df_all, by_sale_df, left_on='group_id', right_on='group_id', how='left')
    merge_df = merge_df.rename(columns={'group_name': 'PARTICULARS', 'new_total': 'QTY', 'cost': 'BASIC', 'cgst':'CGST', 'sgst':'SGST', 'total_cost':'TOTAL'})
    merge_df = merge_df[['PARTICULARS', 'display_name','QTY', 'BASIC', 'CGST', 'SGST', 'TOTAL']]
    merge_df.insert(0,"S.NO", np.arange(1,len(merge_df)+1))

    #-----------------------Excel--------------------------------------------------
    merge_df['PARTICULARS'] = merge_df['PARTICULARS']+merge_df['display_name']
    merge_df.drop('display_name', inplace=True, axis=1)
    
    # ____________________________pdf_______________________________________________
    file_name =  'PRODUCT SALES ABSTRACT.pdf'
    file_path = os.path.join('static/media/monthly_report/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=(11.694 * inch, 8.264 * inch))

    # ________Head_lines________#
    mycanvas.setFont('Helvetica-Bold', 11)
    mycanvas.drawCentredString(405, 575, 'AAVIN CBE')
    mycanvas.drawCentredString(405, 556, 'PRODUCT SALES ABSTRACT '+str(month_in_string).upper()+"- "+str(year))

    x = 50
    y = 530
    # To Write headers
    mycanvas.setFont('Helvetica-Bold', 8.4)
    mycanvas.drawCentredString(x+7,y,"S.NO")
    mycanvas.drawCentredString(x+70,y,"PARTICULARS")
    mycanvas.drawCentredString(x+310,y,"QTY")
    mycanvas.drawCentredString(x+390,y,"BASIC")
    mycanvas.drawCentredString(x+465,y,"CGST")
    mycanvas.drawCentredString(x+540,y,"SGST")
    mycanvas.drawCentredString(x+620,y,"TOTAL")

    # Heading lines
    mycanvas.line(x-10,y+15, x+650, y+15)
    mycanvas.line(x-10,y-3, x+650, y-3)

    header_line_y = y+15
    y_point = 514
    x1_line = 40
    x2_line = 700

    for index, product in merge_df.iterrows():
        # print(index, product['BASIC'])
        mycanvas.setFont('Helvetica', 8.3)
        mycanvas.drawString(50, y_point, str(int(product['S.NO'])))
        mycanvas.drawString(95, y_point, str(product['PARTICULARS']))
        print(product['QTY']) 
        mycanvas.drawRightString(370, y_point, str("{:.2f}".format(product['QTY'])))
        mycanvas.drawRightString(460, y_point, str(product['BASIC']))
        mycanvas.drawRightString(530, y_point, str(product['CGST']))
        mycanvas.drawRightString(610, y_point, str(product['SGST']))
        mycanvas.drawRightString(693, y_point, str(product['TOTAL']))
        #end horizontal Line
        mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)
        y_point -=17

    #end verticle lines for remining columns
    mycanvas.line(x+25,header_line_y, x+25, y_point-5)
    mycanvas.line(x-10,header_line_y, x-10, y_point-5)
    mycanvas.line(x+275,header_line_y, x+275, y_point-5)
    mycanvas.line(x+340,header_line_y, x+340, y_point-5)
    mycanvas.line(x+420,header_line_y, x+420, y_point-5)
    mycanvas.line(x+500,header_line_y, x+500, y_point-5)
    mycanvas.line(x+570,header_line_y, x+570, y_point-5)
    mycanvas.line(x+650,header_line_y, x+650, y_point-5)

    # lastline (for Total)
    mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)

    mycanvas.setFont('Helvetica-Bold' ,9)
    mycanvas.drawString(95, y_point, str("TOTAL"))
    mycanvas.drawRightString(460, y_point, str(merge_df['BASIC'].sum()))
    mycanvas.drawRightString(535, y_point, str(merge_df['CGST'].sum()))
    mycanvas.drawRightString(610, y_point, str(merge_df['SGST'].sum()))
    mycanvas.drawRightString(693, y_point, str(merge_df['TOTAL'].sum()))


    mycanvas.save()

    merge_df = merge_df.append(merge_df[['BASIC','CGST','SGST','TOTAL']].sum(), ignore_index=True)
    merge_df.iloc[-1, merge_df.columns.get_loc('PARTICULARS')] = 'TOTAL'
    merge_df = merge_df.set_index("S.NO")

    xlxs_file_name = 'PRODUCT SALES ABSTRACT.xlsx'
    xlxs_file_path = os.path.join('static/media/monthly_report/', xlxs_file_name)

    merge_df.to_excel(xlxs_file_path)
    alert = "Please Check Rid"
    show_alert = False
    if merge_df.empty:
        show_alert = True
    
    document = {}
    document['file_name'] = file_name
    document['excel_file_name'] = xlxs_file_name
    document['alert'] = alert
    document['show_alert'] = show_alert

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


def encode_image_for_frame(file_path):
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            return encoded_image
    except Exception as err:
        return 0


@api_view(['POST'])
def download_cash_receipt(request):
    cash_receipt_obj = BySaleGroupCashReceipt.objects.filter(by_sale_group__business__code=request.data['booth_code'], by_sale_group__ordered_date=request.data['ordered_date'])
    cash_receipt_list = list(cash_receipt_obj.values_list('receipt_number', 'by_sale_group__total_cost', 'receipt_file'))
    cash_receipt_column = ['receipt_number', 'total_cost', 'file_path']
    cash_receipt_df = pd.DataFrame(cash_receipt_list, columns=cash_receipt_column)
    if not cash_receipt_df.empty:
        cash_receipt_df['file_in_base_64'] = cash_receipt_df.apply(lambda x: encode_image_for_frame(x['file_path']), axis=1)
        cash_receipt_df = cash_receipt_df.fillna(0)
        return Response(data=cash_receipt_df.to_dict('r'), status=status.HTTP_200_OK)
    else:
        return Response(data=[], status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_vehicle_gate_pass_and_order(request):
    data_dict = {
        'old_gate_pass_list': [],
        'sale_data': []
    }
    from_data = request.data['from_date']
    to_date = request.data['to_date']
    if VehicleGatepass.objects.filter(order_from__gte=request.data['from_date'], order_to__lte=request.data['to_date']).exists():
        vehicle_gatepass_obj = VehicleGatepass.objects.filter(order_from__gte=request.data['from_date'], order_to__lte=request.data['to_date'])
        vehicle_gatepass_list = list(vehicle_gatepass_obj.values_list('id', 'order_from', 'order_to', 'vehicle__driver_name', 'vehicle__vehicle_number', 'gatepass_file'))
        vehicle_gatepass_column = ['id', 'order_from', 'order_to', 'driver_name', 'vehicle_number', 'gatepass_file']
        vehicle_gatepass_df = pd.DataFrame(vehicle_gatepass_list, columns=vehicle_gatepass_column)
        vehicle_gatepass_df['file_in_base_64'] = vehicle_gatepass_df.apply(lambda x: encode_image_for_frame(x['gatepass_file']), axis=1)
        data_dict['old_gate_pass_list'] = vehicle_gatepass_df.to_dict('r')
    if BySaleGroupGatepass.objects.filter(by_sale_group__ordered_date__range=[from_data, to_date], is_vehicle_gatepass_taken=False).exists():
        gate_pass_sale_group_obj = BySaleGroupGatepass.objects.filter(by_sale_group__ordered_date__range=[from_data, to_date], is_vehicle_gatepass_taken=False)
        gate_pass_sale_group_list = list(gate_pass_sale_group_obj.values_list('id', 'bill_number', 'by_sale_group__order_code', 'by_sale_group__total_cost', 'by_sale_group__ordered_date', 'by_sale_group__business__code'))
        gate_pass_sale_group_column = ['id', 'bill_number', 'order_code', 'total_cost', 'ordered_date', 'business_code']
        gate_pass_sale_group_df = pd.DataFrame(gate_pass_sale_group_list, columns=gate_pass_sale_group_column)
        gate_pass_sale_group_df['is_selected'] = False
        data_dict['sale_data'] = gate_pass_sale_group_df.to_dict('r')
    return Response(data=data_dict, status=status.HTTP_200_OK)
    

def create_header_for_vehicle_gatepass(mycanvas, single_vehicle_gatepass_obj):
    mycanvas.setFont('Helvetica', 9)
    gst_number = '33AAAAT7787L2ZU'
    mycanvas.drawCentredString(300, 810,
                        'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawString(40, 790, 'GST Number : ' + str(gst_number))
    mycanvas.drawCentredString(300, 790, 'e-way Bill Statement')
    mycanvas.line(250, 785, 350, 785)
    mycanvas.drawString(40, 760, 'Driver Name : ')
    mycanvas.drawString(150, 760, str(single_vehicle_gatepass_obj.vehicle.driver_name))
    mycanvas.drawString(40, 740, 'Vehicle Number : ')
    mycanvas.drawString(150, 740, str(single_vehicle_gatepass_obj.vehicle.vehicle_number))

    mycanvas.drawString(340, 760, 'Prepared date : ')
    date_in_format = datetime.datetime.strftime(single_vehicle_gatepass_obj.prepared_at, '%d-%m-%Y')

    mycanvas.drawString(440, 760, str(date_in_format))
    mycanvas.drawString(340, 740, 'Start time : ')

    today_date_combined_with_time = datetime.datetime.combine(datetime.datetime.today(), single_vehicle_gatepass_obj.vehicle_start_time)
    time_in_format = datetime.datetime.strftime(today_date_combined_with_time, '%I:%M %p')

    mycanvas.drawString(440, 740, str(time_in_format))
    mycanvas.setStrokeColor(colors.black)
    table_header_y = 720
    #table header
    mycanvas.drawCentredString(300, table_header_y + 10, str('Product'))
    mycanvas.line(25, table_header_y, 575, table_header_y)
    mycanvas.drawString(28, table_header_y - 20, 'S No.' )
    mycanvas.drawString(60, table_header_y - 20, 'HSN' )
    mycanvas.drawString(100, table_header_y - 20, 'Product' )
    mycanvas.drawString(245, table_header_y - 20, 'Qty' )
    mycanvas.drawString(280, table_header_y - 20, 'Amount' )
    mycanvas.drawString(320, table_header_y - 20, 'CGST %' )
    mycanvas.drawString(370, table_header_y - 20, 'CGST' )
    mycanvas.drawString(415, table_header_y - 20, 'SGST %')
    mycanvas.drawString(465, table_header_y - 20, 'SGST' )
    mycanvas.drawString(520, table_header_y - 20, 'Total Cost')

    mycanvas.line(25, table_header_y - 30, 575, table_header_y - 30)
    return mycanvas


def create_header_for_vehicle_gatepass_for_group(mycanvas, single_vehicle_gatepass_obj):
    mycanvas.setFont('Helvetica', 9)
    gst_number = '33AAAAT7787L2ZU'
    mycanvas.drawCentredString(300, 810,
                        'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawString(40, 790, 'GST Number : ' + str(gst_number))
    mycanvas.drawCentredString(300, 790, 'e-way Bill Statement')
    mycanvas.line(250, 785, 350, 785)
    mycanvas.drawString(40, 760, 'Driver Name : ')
    mycanvas.drawString(150, 760, str(single_vehicle_gatepass_obj.vehicle.driver_name))
    mycanvas.drawString(40, 740, 'Vehicle Number : ')
    mycanvas.drawString(150, 740, str(single_vehicle_gatepass_obj.vehicle.vehicle_number))

    mycanvas.drawString(340, 760, 'Prepared date : ')
    date_in_format = datetime.datetime.strftime(single_vehicle_gatepass_obj.prepared_at, '%d-%m-%Y')

    mycanvas.drawString(440, 760, str(date_in_format))
    mycanvas.drawString(340, 740, 'Start time : ')

    today_date_combined_with_time = datetime.datetime.combine(datetime.datetime.today(), single_vehicle_gatepass_obj.vehicle_start_time)
    time_in_format = datetime.datetime.strftime(today_date_combined_with_time, '%I:%M %p')

    mycanvas.drawString(440, 740, str(time_in_format))
    mycanvas.setStrokeColor(colors.black)
    return mycanvas


def create_column_line_for_vehicle_gatepass(mycanvas, y_for_between_column, main_y):
    mycanvas.line(25, y_for_between_column, 25, main_y)
    mycanvas.line(55, y_for_between_column, 55, main_y)
    mycanvas.line(92, y_for_between_column, 92, main_y)
    mycanvas.line(235, y_for_between_column, 235, main_y)
    mycanvas.line(270, y_for_between_column, 270, main_y)
    mycanvas.line(315, y_for_between_column, 315, main_y)
    mycanvas.line(360, y_for_between_column, 360, main_y)
    mycanvas.line(410, y_for_between_column, 410, main_y)
    mycanvas.line(455, y_for_between_column, 455, main_y)
    mycanvas.line(500, y_for_between_column, 500, main_y)
    mycanvas.line(575, y_for_between_column, 575, main_y)
    mycanvas.line(25, main_y, 575, main_y)
    return mycanvas
    


def prepare_vehicle_gate_pass_file(vehicle_gatepass_obj_id):
    single_vehicle_gatepass_obj = VehicleGatepass.objects.get(id=vehicle_gatepass_obj_id)
    vehicle_gatepass_obj = VehicleGatepass.objects.filter(id=vehicle_gatepass_obj_id)
    sale_group_ids = list(vehicle_gatepass_obj.values_list('by_sale_group_gate_pass__by_sale_group_id', flat=True))
    by_sale_obj = BySale.objects.filter(by_sale_group_id__in=sale_group_ids)
    by_sale_list = list(by_sale_obj.values_list('id', 'by_product__short_name', 'by_product__by_product_group', 'by_product__by_product_group__name', 'count', 'by_product__by_product_group__hsn_code', 'by_product_id', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'by_product__cgst_percent', 'by_product__sgst_percent'))
    by_sale_column = ['id', 'product_name', 'group_id', 'group_name', 'count', 'product_code', 'product_id', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'cgst_percent', 'sgst_percent']
    by_sale_df = pd.DataFrame(by_sale_list, columns=by_sale_column)
    group_df = by_sale_df.groupby('product_id').agg({'product_name': 'first', 'count': sum, 'product_code': 'first', 'cost': sum, 'cgst_value': sum, 'sgst_value': sum, 'total_cost': sum, 'cgst_percent': 'first', 'sgst_percent': 'first'  }).reset_index()
    product_group_df = by_sale_df.groupby('group_id').agg({'group_name': 'first', 'count': sum, 'product_code': 'first', 'cost': sum, 'cgst_value': sum, 'sgst_value': sum, 'total_cost': sum, 'cgst_percent': 'first', 'sgst_percent': 'first'  }).reset_index()

    product_list = group_df.to_dict('r')
    group_list = product_group_df.to_dict('r')

    file_name = f"{single_vehicle_gatepass_obj.id}-vehicle_gatepass.pdf"
    file_path = os.path.join('static/media/by_product/gate_pass/vehicle_pass')
    try:
        path = file_path
        os.makedirs(path)
    except FileExistsError:
        print('already created')
    file_path = os.path.join('static/media/by_product/gate_pass/vehicle_pass/', file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)
    mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12)

    create_header_for_vehicle_gatepass(mycanvas, single_vehicle_gatepass_obj)

    main_y = 670
    mycanvas.setFont('Helvetica', 7)
    for sale_index, sale in enumerate(product_list):
        mycanvas.drawRightString(50, main_y, str(sale_index + 1))
        mycanvas.drawRightString(88, main_y, str(sale['product_code']))
        mycanvas.drawString(100, main_y, str(sale['product_name'])[:30])
        mycanvas.drawRightString(265, main_y, str(int(sale['count'])))
        mycanvas.drawRightString(310, main_y, str(sale['cost']))
        mycanvas.drawRightString(350, main_y, str(sale['cgst_percent']))
        mycanvas.drawRightString(400, main_y, str(sale['cgst_value']))
        mycanvas.drawRightString(440, main_y, str(sale['sgst_percent']))
        mycanvas.drawRightString(495, main_y, str(sale['sgst_value']))
        mycanvas.drawRightString(560, main_y, str(sale['total_cost']))
        main_y -= 15
        
        if sale_index == 42:
            main_y += 10
            create_column_line_for_vehicle_gatepass(mycanvas, 720, main_y)
            mycanvas.showPage()
            mycanvas.setFont('Helvetica', 12)
            create_header_for_vehicle_gatepass(mycanvas, single_vehicle_gatepass_obj)
            mycanvas.setFont('Helvetica', 7)
            main_y = 670
            

        
    main_y += 10
    create_column_line_for_vehicle_gatepass(mycanvas, 720, main_y)
    main_y -= 15

    # product total:
    mycanvas.setFont('Helvetica', 7)
    mycanvas.drawString(100, main_y, str('Total'))
    mycanvas.drawRightString(265, main_y, str(int(group_df['count'].sum())))
    mycanvas.drawRightString(310, main_y, str(group_df['cost'].sum()))
    mycanvas.drawRightString(400, main_y, str(group_df['cgst_value'].sum()))
    mycanvas.drawRightString(495, main_y, str(group_df['sgst_value'].sum()))
    mycanvas.drawRightString(560, main_y, str(group_df['total_cost'].sum()))

    total_cost = group_df['total_cost'].sum()
    total_cost_after_round = math.ceil(total_cost)
    round_off_value = total_cost_after_round - total_cost
    main_y -= 5
    create_column_line_for_vehicle_gatepass(mycanvas, main_y + 20, main_y)

    mycanvas.drawRightString(495, main_y - 15, 'Rounded Value')
    mycanvas.drawRightString(560, main_y - 15, str(round_off_value))
    mycanvas.drawRightString(495, main_y - 30, 'Final Price')
    mycanvas.drawRightString(560, main_y - 30, str(total_cost_after_round))
    main_y = main_y - 30


    # product group wise table
    if main_y <= 400:
        mycanvas.showPage()
        mycanvas.setFont('Helvetica', 12)
        create_header_for_vehicle_gatepass_for_group(mycanvas, single_vehicle_gatepass_obj)
        mycanvas.setFont('Helvetica', 7)
        table_header_y = 720
    else:
        table_header_y = main_y - 20

    mycanvas.setFont('Helvetica', 9)
    mycanvas.drawCentredString(300, table_header_y + 10, str('Group'))
    mycanvas.line(25, table_header_y, 575, table_header_y)
    mycanvas.drawString(28, table_header_y - 20, 'S No.' )
    mycanvas.drawString(60, table_header_y - 20, 'HSN' )
    mycanvas.drawString(100, table_header_y - 20, 'Product' )
    mycanvas.drawString(245, table_header_y - 20, 'Qty' )
    mycanvas.drawString(280, table_header_y - 20, 'Amount' )
    mycanvas.drawString(320, table_header_y - 20, 'CGST %' )
    mycanvas.drawString(370, table_header_y - 20, 'CGST' )
    mycanvas.drawString(415, table_header_y - 20, 'SGST %')
    mycanvas.drawString(465, table_header_y - 20, 'SGST' )
    mycanvas.drawString(520, table_header_y - 20, 'Total Cost')
    mycanvas.line(25, table_header_y - 30, 575, table_header_y - 30)

    table_header_y_for_line = table_header_y
    table_header_y -= 45
    mycanvas.setFont('Helvetica', 7)
    for sale_index, sale in enumerate(group_list):
        mycanvas.drawRightString(50, table_header_y, str(sale_index + 1))
        mycanvas.drawRightString(88, table_header_y, str(sale['product_code']))
        mycanvas.drawString(100, table_header_y, str(sale['group_name'])[:30])
        mycanvas.drawRightString(265, table_header_y, str(int(sale['count'])))
        mycanvas.drawRightString(310, table_header_y, str(sale['cost']))
        mycanvas.drawRightString(350, table_header_y, str(sale['cgst_percent']))
        mycanvas.drawRightString(400, table_header_y, str(sale['cgst_value']))
        mycanvas.drawRightString(440, table_header_y, str(sale['sgst_percent']))
        mycanvas.drawRightString(495, table_header_y, str(sale['sgst_value']))
        mycanvas.drawRightString(560, table_header_y, str(sale['total_cost']))
        table_header_y -= 15


    create_column_line_for_vehicle_gatepass(mycanvas, table_header_y_for_line, table_header_y)
    table_header_y -= 10
    # product total:
    mycanvas.setFont('Helvetica', 7)
    mycanvas.drawString(100, table_header_y, str('Total'))
    mycanvas.drawRightString(265, table_header_y, str(int(product_group_df['count'].sum())))
    mycanvas.drawRightString(310, table_header_y, str(product_group_df['cost'].sum()))
    mycanvas.drawRightString(400, table_header_y, str(product_group_df['cgst_value'].sum()))
    mycanvas.drawRightString(495, table_header_y, str(product_group_df['sgst_value'].sum()))
    mycanvas.drawRightString(560, table_header_y, str(product_group_df['total_cost'].sum()))

    total_cost = product_group_df['total_cost'].sum()
    total_cost_after_round = math.ceil(total_cost)
    round_off_value = total_cost_after_round - total_cost
    table_header_y -= 5
    create_column_line_for_vehicle_gatepass(mycanvas, table_header_y + 20, table_header_y)

    mycanvas.drawRightString(495, table_header_y - 15, 'Rounded Value')
    mycanvas.drawRightString(560, table_header_y - 15, str(round_off_value))
    mycanvas.drawRightString(495, table_header_y - 30, 'Final Price')
    mycanvas.drawRightString(560, table_header_y - 30, str(total_cost_after_round))

    mycanvas.save()
    return file_path, file_name


@transaction.atomic
@api_view(['POST'])
def prepare_vehicle_gate_pass(request):
    sid = transaction.savepoint()
    try:
        vehicle_form_value = request.data['vehicle_details']
        sale_data = request.data['sale_data']
        from_date = request.data['from_date']
        to_date = request.data['to_date']

        vehicle_master_obj = VehicleMaster(driver_name=vehicle_form_value['driver_name'],
                                        vehicle_number=vehicle_form_value['vehicle_number'])
        vehicle_master_obj.save()

        vehicle_gatepass_obj = VehicleGatepass(vehicle_id=vehicle_master_obj.id,
                                            vehicle_start_time=vehicle_form_value['vehicle_start_time'],
                                            order_from=from_date,
                                            order_to=to_date,
                                            prepared_by_id=request.user.id,
                                            prepared_at=datetime.datetime.now()
                                            )
        vehicle_gatepass_obj.save()
        for sale in sale_data:
            BySaleGroupGatepass.objects.filter(id=sale['id']).update(is_vehicle_gatepass_taken=True)
            vehicle_gatepass_obj.by_sale_group_gate_pass.add(sale['id'])

        vehicle_gatepass_obj.save()
        file_path, file_name = prepare_vehicle_gate_pass_file(vehicle_gatepass_obj.id)
        vehicle_gatepass_obj.gatepass_file = file_path
        vehicle_gatepass_obj.save()

        document = {}
        document['file_name'] = file_name
        try:
            image_path = file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)
        transaction.savepoint_commit(sid)
        return Response(data=document, status=status.HTTP_200_OK)
    except Exception as e:
        print('Error on {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['POST'])
def serve_daily_stock_report_in_excel(request):
    sale_date = request.data['sale_date']
    daily_sale_goods_receipt_obj = GoodsReceiptRecordForDaily.objects.filter(sale_date=sale_date)
    daily_sale_goods_receipt_list = list(daily_sale_goods_receipt_obj.values_list('id', 'by_product', 'by_product__short_name', 'quantity_now', 'price_per_unit'))
    daily_sale_goods_receipt_column = ['id', 'product_id', 'product_name', 'quantity_now', 'price_per_unit']
    daily_sale_goods_receipt_df = pd.DataFrame(daily_sale_goods_receipt_list, columns=daily_sale_goods_receipt_column)
    daily_sale_goods_receipt_df['total_cost'] = daily_sale_goods_receipt_df['quantity_now'] *  daily_sale_goods_receipt_df['price_per_unit']
    daily_sale_goods_receipt_df = daily_sale_goods_receipt_df.groupby('product_id').agg({'product_name': 'first', 'quantity_now': sum, 'total_cost': sum}).reset_index()
    daily_sale_goods_receipt_df = daily_sale_goods_receipt_df.rename(columns={'product_name': 'Product Name', 'quantity_now': 'Quantity', 'total_cost': 'Amount'})
    daily_sale_goods_receipt_df = daily_sale_goods_receipt_df.drop('product_id', 1)
    daily_sale_goods_receipt_df['Quantity'] = daily_sale_goods_receipt_df['Quantity'].apply(int)
    daily_sale_goods_receipt_df.insert(0, 'S.No', range(1, 1 + len(daily_sale_goods_receipt_df)))

    file_name = f'Daily Stock Details{sale_date}.xlsx'
    file_path = os.path.join('static/media/by_product/', file_name)
    daily_sale_goods_receipt_df.to_excel(file_path, index=False)
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


def create_header_for_daily_stock_pdf(mycanvas, date):
    mycanvas.drawCentredString(300, 810,
                        'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawCentredString(300, 790, 'Daily Stock')
    mycanvas.drawCentredString(450, 790, 'Date: ' + str(date))
    mycanvas.line(250, 785, 350, 785)
    mycanvas.setStrokeColor(colors.black)
    #table header
    mycanvas.line(25, 770, 575, 770)
    mycanvas.drawString(55, 755, 'S No.' )
    mycanvas.drawString(130, 755, 'Product Name' )
    mycanvas.drawString(340, 755, 'Quantity' )
    mycanvas.drawString(450, 755, 'Amount' )

    mycanvas.line(25, 750, 575, 750)
    return mycanvas


def write_column_lines(mycanvas, main_y):
    mycanvas.line(25, 770, 25, main_y)
    mycanvas.line(100, 770, 100, main_y)
    mycanvas.line(330, 770, 330, main_y)
    mycanvas.line(400, 770, 400, main_y)
    mycanvas.line(575, 770, 575, main_y)
    mycanvas.line(25, main_y, 575, main_y)
    return mycanvas


@api_view(['POST'])
def serve_daily_stock_report_in_pdf(request):
    print(request.data)
    user_name = request.user.first_name
    sale_date = request.data['sale_date']
    if GoodsReceiptRecordForDaily.objects.filter(sale_date=sale_date).exists():
        daily_sale_goods_receipt_obj = GoodsReceiptRecordForDaily.objects.filter(sale_date=sale_date)
        daily_sale_goods_receipt_list = list(daily_sale_goods_receipt_obj.values_list('id', 'by_product', 'by_product__short_name', 'quantity_now', 'price_per_unit'))
        daily_sale_goods_receipt_column = ['id', 'product_id', 'product_name', 'quantity_now', 'price_per_unit']
        daily_sale_goods_receipt_df = pd.DataFrame(daily_sale_goods_receipt_list, columns=daily_sale_goods_receipt_column)
        daily_sale_goods_receipt_df['total_cost'] = daily_sale_goods_receipt_df['quantity_now'] *  daily_sale_goods_receipt_df['price_per_unit']
        daily_sale_goods_receipt_df = daily_sale_goods_receipt_df.groupby('product_id').agg({'product_name': 'first', 'quantity_now': sum, 'total_cost': sum}).reset_index()
        daily_sale_goods_receipt_df = daily_sale_goods_receipt_df.rename(columns={'product_name': 'Product Name', 'quantity_now': 'Quantity', 'total_cost': 'Amount'})
        daily_sale_goods_receipt_df = daily_sale_goods_receipt_df.drop('product_id', 1)
        daily_sale_goods_receipt_df['Quantity'] = daily_sale_goods_receipt_df['Quantity'].apply(int)
        daily_sale_goods_receipt_df.insert(0, 'S.No', range(1, 1 + len(daily_sale_goods_receipt_df)))
        sale_list = daily_sale_goods_receipt_df.to_dict('r')
        file_name = f'Daily Stock Details {sale_date}.pdf'
        file_path = os.path.join('static/media/by_product/daily_sale')
        try:
            path = file_path
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join('static/media/by_product/daily_sale', file_name)
        mycanvas = canvas.Canvas(file_path, pagesize=A4)
        mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12)
        date_in_format = datetime.datetime.strftime(daily_sale_goods_receipt_obj[0].sale_date, '%d-%m-%Y')
        create_header_for_daily_stock_pdf(mycanvas, date_in_format)

        main_y = 730

        for sale_index, sale in enumerate(sale_list):
            mycanvas.drawRightString(70, main_y, str(sale['S.No']))
            mycanvas.drawString(130, main_y, str(sale['Product Name'])[:38])
            mycanvas.drawRightString(390, main_y, str(sale['Quantity']))
            mycanvas.drawRightString(480, main_y, str(int(sale['Amount'])))
            main_y -= 15
            
            if sale_index == 45:
                main_y += 10
                write_column_lines(mycanvas, main_y)
                mycanvas.drawRightString(580, 5, 'Report Generated by: ' + str(
                    user_name + " @" + str(datetime.datetime.now().astimezone(indian).strftime("%d-%m-%Y %I:%M:%S"))))
                mycanvas.showPage()
                create_header_for_daily_stock_pdf(mycanvas, date_in_format)
                main_y = 730

        write_column_lines(mycanvas, main_y)
        mycanvas.drawRightString(580, 5, 'Report Generated by: ' + str(
                    user_name + " @" + str(datetime.datetime.now().astimezone(indian).strftime("%d-%m-%Y %I:%M:%S"))))
        mycanvas.save()

        document = {}
        document['is_data_exists'] = True
        document['file_name'] = file_name
        try:
            image_path = file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)
    else:
        document = {}
        document['is_data_exists'] = False
    return Response(data=document, status=status.HTTP_200_OK)





@api_view(['GET'])
def serve_daily_close_status(request):
    today = datetime.datetime.now()
    previous_date = today - datetime.timedelta(days=1)
    data_dict = {
        'previous_date': previous_date,
        'today_date': today,
        'is_previous_sale_closed': False,
        'is_today_sale_closed': False,
        'today_sale_close_details': {}
    }
    if DailySaleCloseTrace.objects.filter(sale_date__lt=today, is_sale_closed=False).exists():
        dale_sale_close_trace_obj = DailySaleCloseTrace.objects.filter(sale_date__lt=today, is_sale_closed=False).order_by('sale_date')[0]
        data_dict['previous_date'] = dale_sale_close_trace_obj.sale_date
    else:
        if DailySaleCloseTrace.objects.filter(sale_date=previous_date).exists():
            dale_sale_close_trace_obj = DailySaleCloseTrace.objects.get(sale_date=previous_date)
            if dale_sale_close_trace_obj.is_sale_closed:
                data_dict['is_previous_sale_closed'] = True
        if DailySaleCloseTrace.objects.filter(sale_date=today).exists():
            dale_sale_close_trace_obj = DailySaleCloseTrace.objects.get(sale_date=today)
            if dale_sale_close_trace_obj.is_sale_closed:
                data_dict['is_today_sale_closed'] = True
                data_dict['today_sale_close_details']['closed_at'] = dale_sale_close_trace_obj.closed_at
                data_dict['today_sale_close_details']['closed_by'] = dale_sale_close_trace_obj.closed_by.first_name

    return Response(data=data_dict, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
def close_daily_sale(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        print(request.data)
        sale_date = str(request.data['date']).split('T')[0]
        print(sale_date)
        if not DailySaleCloseTrace.objects.filter(sale_date=sale_date).exists():
            daily_sale_record_for_given_date = DailySaleCloseTrace(sale_date=sale_date,
                                                                   is_sale_closed=True,
                                                                   closed_by_id=request.user.id,
                                                                   closed_at=datetime.datetime.now())
            daily_sale_record_for_given_date.save()
        else:
            daily_sale_record_for_given_date = DailySaleCloseTrace.objects.get(sale_date=sale_date)
            daily_sale_record_for_given_date.is_sale_closed = True
            daily_sale_record_for_given_date.closed_at = datetime.datetime.now()
            daily_sale_record_for_given_date.save()
        
        date_in_format = datetime.datetime.strptime(str(daily_sale_record_for_given_date.sale_date), "%Y-%m-%d")
        next_date = date_in_format + datetime.timedelta(days=1) 
        daily_sale_records = GoodsReceiptRecordForDaily.objects.filter(sale_date=sale_date).exclude(quantity_now=0)
        if not DailySaleCloseTrace.objects.filter(sale_date=next_date).exists():
            daily_sale_record_for_given_date = DailySaleCloseTrace(sale_date=next_date,
                                                                is_sale_closed=False)
            daily_sale_record_for_given_date.save()
        for daily_sale in daily_sale_records:
            daily_sale_record_obj = GoodsReceiptRecordForDaily(sale_date=next_date,
                                                               by_product_id=daily_sale.by_product_id,
                                                               grn_number=daily_sale.grn_number,
                                                               quantity_at_receipt=daily_sale.quantity_now,
                                                               quantity_now=daily_sale.quantity_now,
                                                               quantity_now_time=datetime.datetime.now(),
                                                               price_per_unit=daily_sale.price_per_unit,
                                                               total_price=daily_sale.total_price,
                                                               )
            daily_sale_record_obj.save()
        transaction.savepoint_commit(sid)
        return Response(status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)       


@api_view(['GET'])
def open_daily_sale(request):
    today = datetime.datetime.now()
    next_date = today + datetime.timedelta(days=1)
    if DailySaleCloseTrace.objects.filter(sale_date=today, is_sale_closed=True).exists():
        dale_sale_close_trace_obj = DailySaleCloseTrace.objects.get(sale_date=today)
        dale_sale_close_trace_obj.is_sale_closed = False
        dale_sale_close_trace_obj.opened_by_id = request.user.id
        dale_sale_close_trace_obj.opened_at = today
        dale_sale_close_trace_obj.save()

        # remove next day sale because it will create conflict on next sale close
        GoodsReceiptRecordForDaily.objects.filter(sale_date=next_date).delete()
    return Response(status=status.HTTP_200_OK)


def header_for_daily_sale_report(mycanvas, date_in_format, table_content_y, main_y):
    mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)

    # vertical lines
    mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
    mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
    mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
    mycanvas.line(345, table_content_y + 10, 345, main_y - 10)
    mycanvas.line(575, table_content_y + 10, 575, main_y - 10)

    mycanvas.showPage()
    mycanvas.setStrokeColor(colors.lightgrey)
    mycanvas.setFont('Helvetica', 12)
    mycanvas.drawCentredString(300, 810,
                            'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
    mycanvas.drawCentredString(300, 790, 'Daily Sale - ' + str(date_in_format))
    mycanvas.line(250, 785, 350, 785)
    mycanvas.setStrokeColor(colors.black)
    return mycanvas


@api_view(['POST'])
def serve_daily_sale_for_selected_date(request):
    sale_date = request.data['sale_date']
    if BySaleGroup.objects.filter(ordered_date=sale_date).exists():
        by_sale_group_obj = BySaleGroup.objects.filter(ordered_date=sale_date)
        payment_method_list = sorted(list(set(by_sale_group_obj.values_list('payment_method__name', flat=True))))
        by_sale_group_list = list(by_sale_group_obj.values_list('id', 'business__code', 'business__businessagentmap__agent__first_name', 'total_cost', 'payment_method__name'))
        by_sale_group_column = ['id', 'booth_code', 'booth_name', 'total_cost', 'payment_method']
        by_sale_group_df = pd.DataFrame(by_sale_group_list, columns=by_sale_group_column)
        by_sale_group_dict = by_sale_group_df.groupby('payment_method').apply(lambda x: x.to_dict('r')).to_dict()

        file_name = f"{sale_date} - daily_sale_bill.pdf"
        file_path = os.path.join('static/media/by_product/daily_sale_product_wise/')
        try:
            path = file_path
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join('static/media/by_product/daily_sale_product_wise/', file_name)
        mycanvas = canvas.Canvas(file_path, pagesize=A4)
        mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 810,
                                'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
        date_in_format = datetime.datetime.strftime(by_sale_group_obj[0].ordered_date, '%d-%m-%Y')
        mycanvas.drawCentredString(300, 790, 'Daily Sale - ' + str(date_in_format))
        mycanvas.line(250, 785, 350, 785)
        mycanvas.setStrokeColor(colors.black)

        main_y = 750
        table_content_y = 705
        sub_total = 0
        for index, payment_method in enumerate(payment_method_list):
            if not sub_total == 0:
                mycanvas.drawString(425, main_y + 15, 'Sub Total: ')
                mycanvas.drawRightString(565, main_y + 15, str(sub_total))
                mycanvas.line(400, main_y + 10, 575, main_y + 10)
                mycanvas.line(400, main_y + 10, 400, main_y + 30)
                mycanvas.line(575, main_y + 10, 575, main_y + 30)

            mycanvas.drawString(27, main_y, str(payment_method))
            
            #table header
            mycanvas.line(25, main_y - 10, 575, main_y - 10)
            mycanvas.drawString(30, main_y - 25, 'S No.' )
            mycanvas.drawString(80, main_y - 25, 'Booth Name' )
            mycanvas.drawString(415, main_y - 25, 'Booth Code' )
            mycanvas.drawString(515, main_y - 25, 'Amount' )
            mycanvas.line(25, main_y - 30, 575, main_y - 30)
            sub_total = 0
            for sale_index, sale in enumerate(by_sale_group_dict[payment_method]):
                # table content
                mycanvas.drawRightString(50, table_content_y, str(sale_index + 1))
                mycanvas.drawString(80, table_content_y, str(sale['booth_name']) )
                mycanvas.drawString(435, table_content_y, str(sale['booth_code']) )
                mycanvas.drawRightString(565, table_content_y, str(sale['total_cost']) )
                table_content_y -= 15
                sub_total += sale['total_cost']
                if table_content_y <= 50:
                    
                    header_for_daily_sale_report(mycanvas, date_in_format, table_content_y, main_y)
                    main_y = 750
                    table_content_y = 725
                    mycanvas.line(25, table_content_y + 15, 575, table_content_y + 15)
            # vertical lines
            mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
            mycanvas.line(75, table_content_y + 10, 75, main_y - 10)
            mycanvas.line(400, table_content_y + 10, 400, main_y - 10)
            mycanvas.line(485, table_content_y + 10, 485, main_y - 10)
            mycanvas.line(575, table_content_y + 10, 575, main_y - 10)
            
            mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)
            
            if table_content_y + 10 <= 85:
                # product table lines
            
                header_for_daily_sale_report(mycanvas, date_in_format, table_content_y, main_y)
                main_y = 750
                table_content_y = 760
            main_y = table_content_y - 20
            table_content_y = main_y - 45

        
        mycanvas.drawString(425, main_y + 15, 'Sub Total: ')
        mycanvas.drawRightString(565, main_y + 15, str(sub_total))
        mycanvas.line(400, main_y + 10, 575, main_y + 10)
        mycanvas.line(400, main_y + 10, 400, main_y + 30)
        mycanvas.line(575, main_y + 10, 575, main_y + 30)

        mycanvas.drawString(425, main_y-10, 'Total Cost: ')
        mycanvas.drawRightString(565, main_y-10, str(by_sale_group_df['total_cost'].sum())  )
        mycanvas.save()
        document = {}
        document['file_name'] = file_name
        document['is_data_available'] = True
        try:
            image_path = file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)
        return Response(data=document, status=status.HTTP_200_OK)
    else:
        document = {}
        document['is_data_available'] = False
        return Response(data=document, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_daily_cash_and_credit_statement(request): 
    print(request.data)
    date_from = request.data['from_date']
    date_to = request.data['to_date']
    if BySale.objects.filter(by_sale_group__ordered_date__range=[date_from, date_to]).exists():
        main_sale_cash_obj = BySale.objects.filter(by_sale_group__ordered_date__range=[date_from, date_to], by_sale_group__payment_method_id=1)
        main_sale_cash_list = list(main_sale_cash_obj.values_list('by_product', 'by_product__by_product_group_id', 'by_product__by_product_group__name', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'by_sale_group__ordered_date', 'by_sale_group__payment_method_id'))
        main_sale_cash_column = ['by_product_id', 'group_id', 'group_name', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'ordered_date', 'payment_method']
        main_sale_cash_df = pd.DataFrame(main_sale_cash_list, columns=main_sale_cash_column)

        main_sale_credit_obj = BySale.objects.filter(by_sale_group__ordered_date__range=[date_from, date_to], by_sale_group__payment_method_id=2)
        main_sale_credit_list = list(main_sale_credit_obj.values_list('by_product', 'by_product__by_product_group_id', 'by_product__by_product_group__name', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'by_sale_group__ordered_date', 'by_sale_group__payment_method_id', 'by_sale_group__business_id'))
        main_sale_credit_column = ['by_product_id', 'group_id', 'group_name', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'ordered_date', 'payment_method', 'business_id']
        main_sale_credit_df = pd.DataFrame(main_sale_credit_list, columns=main_sale_credit_column)

        cash_sale_group_wise = main_sale_cash_df.groupby('group_id').agg({'cost': sum}).to_dict()['cost']
        credit_sale_group_wise = main_sale_credit_df.groupby('group_id').agg({'cost': sum}).to_dict()['cost']

        main_sale_group_cash_obj = BySaleGroup.objects.filter(ordered_date__range=[date_from, date_to], payment_method_id=1)

        main_sale_group_credit_obj = BySaleGroup.objects.filter(ordered_date__range=[date_from, date_to], payment_method_id=2)
        main_sale_group_credit_list = list(main_sale_group_credit_obj.values_list('id', 'business', 'total_cost'))
        main_sale_group_credit_column = ['id', 'business_id', 'total_cost']
        main_sale_group_credit_df = pd.DataFrame(main_sale_group_credit_list, columns=main_sale_group_credit_column)

        cgst_and_sgst_dict = {}
        if not main_sale_cash_df.empty:
            cgst_and_sgst_dict['cgst_collection_for_cash'] = main_sale_cash_df['cgst_value'].sum()
            cgst_and_sgst_dict['sgst_collection_for_cash'] = main_sale_cash_df['sgst_value'].sum()
            cgst_and_sgst_dict['total_cash_cost'] = main_sale_cash_df['total_cost'].sum()
        else:
            cgst_and_sgst_dict['cgst_collection_for_cash'] = 0
            cgst_and_sgst_dict['sgst_collection_for_cash'] = 0
            cgst_and_sgst_dict['total_cash_cost'] = 0
        if not main_sale_credit_df.empty:
            cgst_and_sgst_dict['cgst_collection_for_credit'] = main_sale_credit_df['cgst_value'].sum()
            cgst_and_sgst_dict['sgst_collection_for_credit'] = main_sale_credit_df['sgst_value'].sum()
            cgst_and_sgst_dict['total_credit_cost'] = main_sale_credit_df['total_cost'].sum()
        else:
            cgst_and_sgst_dict['cgst_collection_for_credit'] = 0
            cgst_and_sgst_dict['sgst_collection_for_credit'] = 0
            cgst_and_sgst_dict['total_credit_cost'] = 0
        cgst_and_sgst_dict['cgst_account_code'] = '30910'
        cgst_and_sgst_dict['sgst_account_code'] = '30911'
        cgst_and_sgst_dict['misc_account_code'] = '31004'
        if main_sale_group_cash_obj:
            cgst_and_sgst_dict['total_cash_amount'] = main_sale_group_cash_obj.aggregate(Sum('total_cost'))['total_cost__sum']
        else:
            cgst_and_sgst_dict['total_cash_amount'] = 0
        if main_sale_group_credit_obj:
            cgst_and_sgst_dict['total_credit_amount'] = main_sale_group_credit_obj.aggregate(Sum('total_cost'))['total_cost__sum']
        else:
            cgst_and_sgst_dict['total_credit_amount'] = 0


        product_group_obj = ByProductGroup.objects.filter()
        product_group_list = list(product_group_obj.values_list('id', 'name', 'account_code'))
        product_group_column = ['id', 'name', 'account_code']
        product_group_df = pd.DataFrame(product_group_list, columns=product_group_column)
        product_group_list = product_group_df.to_dict('r')

        credit_business_ids = list(set(main_sale_credit_obj.values_list('by_sale_group__business_id', flat=True)))

        business_obj = Business.objects.filter(id__in=credit_business_ids)
        business_list = list(business_obj.values_list('id', 'businessagentmap__agent__agent_code', 'businessagentmap__agent__first_name'))
        business_column = ['id', 'account_code', 'agent_name']
        business_df = pd.DataFrame(business_list, columns=business_column)
        business_df = business_df.fillna(0)
        business_list = business_df.to_dict('r')

        credit_sale_business_wise = main_sale_group_credit_df.groupby('business_id').agg({'total_cost': sum}).to_dict()['total_cost']

        # pdf part
        from_date_in_strip = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        from_date_in_format = datetime.datetime.strftime(from_date_in_strip, '%d-%m-%Y')

        to_date_in_strip = datetime.datetime.strptime(date_to, "%Y-%m-%d")
        to_date_in_format = datetime.datetime.strftime(to_date_in_strip, '%d-%m-%Y')

        file_name = f"{from_date_in_format} - {to_date_in_format} - daily_sales_statement.pdf"
        file_path = os.path.join('static/media/by_product/daily_sale/')     
        try:
            path = file_path
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        file_path = os.path.join('static/media/by_product/daily_sale/', file_name)
        print(file_path)
        mycanvas = canvas.Canvas(file_path, pagesize=A4)
        mycanvas.setStrokeColor(colors.lightgrey)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 810,
                                'The Coimbatore District Co-Operative Milk Producers Union Ltd. Pachapalayam, Coimbatore - 641 010')
        mycanvas.drawCentredString(300, 790, 'By Product Cash and Credit Sales Statement ' + str(from_date_in_format) + ' to ' + str(to_date_in_format) )
        mycanvas.setStrokeColor(colors.black)

        main_y = 770
        #table header
        mycanvas.setFont('Helvetica-Bold', 12)
        mycanvas.line(25, main_y - 10, 575, main_y - 10)
        mycanvas.drawString(30, main_y - 25, 'S No.' )
        mycanvas.drawString(70, main_y - 25, 'Code' )
        mycanvas.drawString(120, main_y - 25, 'Product' )
        mycanvas.drawString(214, main_y - 25, 'Cash' )
        mycanvas.drawString(280, main_y - 25, 'Credit' )
        mycanvas.drawString(330, main_y - 25, 'S No' )
        mycanvas.drawString(370, main_y - 25, 'Code' )
        mycanvas.drawString(410, main_y - 25, 'Debitors' )
        mycanvas.drawString(525, main_y - 25, 'Amount' )
        mycanvas.line(25, main_y - 30, 575, main_y - 30)
        
        table_content_y = main_y - 45
        table_content_y_for_business = main_y - 45
        mycanvas.setFont('Helvetica', 9)
        last_index = 0
        for index, product_group in enumerate(product_group_list):
            if product_group['id'] in cash_sale_group_wise or product_group['id'] in credit_sale_group_wise:
                last_index = last_index + 1
                mycanvas.drawRightString(50, table_content_y, str(last_index))
                mycanvas.setFont('Helvetica-Bold', 9)
                mycanvas.drawString(70, table_content_y, str(product_group['account_code']))
                mycanvas.setFont('Helvetica', 9)
                mycanvas.drawString(120, table_content_y, str(product_group['name']))
                if product_group['id'] in cash_sale_group_wise:
                    mycanvas.drawRightString(250, table_content_y, str(cash_sale_group_wise[product_group['id']]))
                if product_group['id'] in credit_sale_group_wise:
                    mycanvas.drawRightString(320, table_content_y, str(credit_sale_group_wise[product_group['id']]))
                table_content_y -= 15


        total_cost_business_wise = 0
        for index, business in enumerate(business_list):
            mycanvas.drawRightString(350, table_content_y_for_business, str(index + 1))
            if not business['account_code'] == 0:
                mycanvas.setFont('Helvetica-Bold', 9)
                mycanvas.drawString(370, table_content_y_for_business, str(business['account_code']))
                mycanvas.setFont('Helvetica', 9)
            mycanvas.drawString(410, table_content_y_for_business, str(business['agent_name']).title()[:21])
            total_cost_business_wise += credit_sale_business_wise[business['id']]
            mycanvas.drawRightString(570, table_content_y_for_business, str(credit_sale_business_wise[business['id']]))
            table_content_y_for_business -= 15
        if len(business_list) != 0:
            mycanvas.setFont('Helvetica-Bold', 9)
            mycanvas.drawString(410, table_content_y_for_business, str('Total'))
            mycanvas.setFont('Helvetica', 9)
            mycanvas.drawRightString(570, table_content_y_for_business, str(total_cost_business_wise))
            
        last_index += 1
        # cgst and sgst collection
        mycanvas.drawRightString(50, table_content_y, str(last_index))
        mycanvas.setFont('Helvetica-Bold', 9)
        mycanvas.drawString(70, table_content_y, str(cgst_and_sgst_dict['cgst_account_code']))
        mycanvas.drawString(120, table_content_y, str('CGST Collection'))
        mycanvas.setFont('Helvetica', 9)
        mycanvas.drawRightString(250, table_content_y, str(cgst_and_sgst_dict['cgst_collection_for_cash']))
        mycanvas.drawRightString(320, table_content_y, str(cgst_and_sgst_dict['cgst_collection_for_credit']))

        table_content_y -= 15
        last_index += 1
        mycanvas.drawRightString(50, table_content_y, str(last_index))
        mycanvas.setFont('Helvetica-Bold', 9)
        mycanvas.drawString(70, table_content_y, str(cgst_and_sgst_dict['sgst_account_code']))
        mycanvas.drawString(120, table_content_y, str('SGST Collection'))
        mycanvas.setFont('Helvetica', 9)
        mycanvas.drawRightString(250, table_content_y, str(cgst_and_sgst_dict['sgst_collection_for_cash']))
        mycanvas.drawRightString(320, table_content_y, str(cgst_and_sgst_dict['sgst_collection_for_credit']))

        table_content_y -= 15
        last_index += 1
        mycanvas.drawRightString(50, table_content_y, str(last_index))
        mycanvas.setFont('Helvetica-Bold', 9)
        mycanvas.drawString(70, table_content_y, str(cgst_and_sgst_dict['misc_account_code']))
        mycanvas.drawString(120, table_content_y, str('Misc. Income'))
        mycanvas.setFont('Helvetica', 9)

        cash_misc_amount = cgst_and_sgst_dict['total_cash_amount'] - cgst_and_sgst_dict['total_cash_cost']
        credit_misc_amount = cgst_and_sgst_dict['total_credit_amount'] - cgst_and_sgst_dict['total_credit_cost']

        mycanvas.drawRightString(250, table_content_y, str(cash_misc_amount))
        mycanvas.drawRightString(320, table_content_y, str(credit_misc_amount))

        table_content_y -= 15
        mycanvas.setFont('Helvetica-Bold', 9)
        mycanvas.drawString(120, table_content_y, str('Total'))
        mycanvas.drawRightString(250, table_content_y, str(cgst_and_sgst_dict['total_cash_amount']))
        mycanvas.drawRightString(320, table_content_y, str(cgst_and_sgst_dict['total_credit_amount']))

       
        # vertical lines
        table_content_y -= 15
        mycanvas.line(25, table_content_y + 10, 25, main_y - 10)
        mycanvas.line(65, table_content_y + 10, 65, main_y - 10)
        mycanvas.line(115, table_content_y + 10, 115, main_y - 10)
        mycanvas.line(195, table_content_y + 10, 195, main_y - 10)
        mycanvas.line(255, table_content_y + 10, 255, main_y - 10)
        mycanvas.line(325, table_content_y + 10, 325, main_y - 10)
        mycanvas.line(360, table_content_y + 10, 360, main_y - 10)
        mycanvas.line(405, table_content_y + 10, 405, main_y - 10)
        mycanvas.line(510, table_content_y + 10, 510, main_y - 10)
        mycanvas.line(575, table_content_y + 10, 575, main_y - 10)

        mycanvas.line(25, table_content_y + 10, 575, table_content_y + 10)
        mycanvas.line(25, table_content_y + 25, 575, table_content_y + 25)



        mycanvas.drawCentredString(300, 200, 'Executive(office)                            Dy.Manager(Mkg)                            Manager(Mkg)                            Asst. Gen Manager (Mkg)')

        mycanvas.save() 
        document = {}
        document['file_name'] = file_name
        document['is_data_available'] = True     
        try:
            image_path = file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)          
        return Response(data=document, status=status.HTTP_200_OK)
    else:
        document = {}
        # document['file_name'] = file_name
        document['is_data_available'] = False
        return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_daily_cash_and_credit_statement_excel(request): 
    date_from =request.data['from_date']
    date_to = request.data['to_date']
    if BySale.objects.filter(by_sale_group__ordered_date__range=[date_from, date_to]).exists():
        main_sale_cash_obj = BySale.objects.filter(by_sale_group__ordered_date__range=[date_from, date_to], by_sale_group__payment_method_id=1)
        main_sale_cash_list = list(main_sale_cash_obj.values_list('by_product', 'by_product__by_product_group_id', 'by_product__by_product_group__name', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'by_sale_group__ordered_date', 'by_sale_group__payment_method_id'))
        main_sale_cash_column = ['by_product_id', 'group_id', 'group_name', 'cash_cost', 'cgst_value', 'sgst_value', 'total_cost', 'ordered_date', 'payment_method']
        main_sale_cash_df = pd.DataFrame(main_sale_cash_list, columns=main_sale_cash_column)

        main_sale_credit_obj = BySale.objects.filter(by_sale_group__ordered_date__range=[date_from, date_to], by_sale_group__payment_method_id=2)
        main_sale_credit_list = list(main_sale_credit_obj.values_list('by_product', 'by_product__by_product_group_id', 'by_product__by_product_group__name', 'cost', 'cgst_value', 'sgst_value', 'total_cost', 'by_sale_group__ordered_date', 'by_sale_group__payment_method_id', 'by_sale_group__business_id'))
        main_sale_credit_column = ['by_product_id', 'group_id', 'group_name', 'credit_cost', 'cgst_value', 'sgst_value', 'total_cost', 'ordered_date', 'payment_method', 'business_id']
        main_sale_credit_df = pd.DataFrame(main_sale_credit_list, columns=main_sale_credit_column)

        cash_sale_group_wise_df = main_sale_cash_df.groupby('group_id').agg({'cash_cost': sum})['cash_cost']
        credit_sale_group_wise_df= main_sale_credit_df.groupby('group_id').agg({'credit_cost': sum})['credit_cost']

        main_sale_group_cash_obj = BySaleGroup.objects.filter(ordered_date__range=[date_from, date_to], payment_method_id=1)

        main_sale_group_credit_obj = BySaleGroup.objects.filter(ordered_date__range=[date_from, date_to], payment_method_id=2)
        main_sale_group_credit_list = list(main_sale_group_credit_obj.values_list('id', 'business', 'total_cost'))
        main_sale_group_credit_column = ['id', 'business_id', 'total_cost']
        main_sale_group_credit_df = pd.DataFrame(main_sale_group_credit_list, columns=main_sale_group_credit_column)

        cgst_and_sgst_dict = {}
        if not main_sale_cash_df.empty:
            cgst_and_sgst_dict['cgst_collection_for_cash'] = main_sale_cash_df['cgst_value'].sum()
            cgst_and_sgst_dict['sgst_collection_for_cash'] = main_sale_cash_df['sgst_value'].sum()
            cgst_and_sgst_dict['total_cash_cost'] = main_sale_cash_df['total_cost'].sum()
        else:
            cgst_and_sgst_dict['cgst_collection_for_cash'] = 0
            cgst_and_sgst_dict['sgst_collection_for_cash'] = 0
            cgst_and_sgst_dict['total_cash_cost'] = 0
        if not main_sale_credit_df.empty:
            cgst_and_sgst_dict['cgst_collection_for_credit'] = main_sale_credit_df['cgst_value'].sum()
            cgst_and_sgst_dict['sgst_collection_for_credit'] = main_sale_credit_df['sgst_value'].sum()
            cgst_and_sgst_dict['total_credit_cost'] = main_sale_credit_df['total_cost'].sum()
        else:
            cgst_and_sgst_dict['cgst_collection_for_credit'] = 0
            cgst_and_sgst_dict['sgst_collection_for_credit'] = 0
            cgst_and_sgst_dict['total_credit_cost'] = 0
        cgst_and_sgst_dict['cgst_account_code'] = '30910'
        cgst_and_sgst_dict['sgst_account_code'] = '30911'
        cgst_and_sgst_dict['misc_account_code'] = '31004'
        if main_sale_group_cash_obj:
            cgst_and_sgst_dict['total_cash_amount'] = main_sale_group_cash_obj.aggregate(Sum('total_cost'))['total_cost__sum']
        else:
            cgst_and_sgst_dict['total_cash_amount'] = 0
        if main_sale_group_credit_obj:
            cgst_and_sgst_dict['total_credit_amount'] = main_sale_group_credit_obj.aggregate(Sum('total_cost'))['total_cost__sum']
        else:
            cgst_and_sgst_dict['total_credit_amount'] = 0
        # print(cgst_and_sgst_dict)

        cash_misc_amount = cgst_and_sgst_dict['total_cash_amount'] - cgst_and_sgst_dict['total_cash_cost']
        credit_misc_amount = cgst_and_sgst_dict['total_credit_amount'] - cgst_and_sgst_dict['total_credit_cost']

        product_group_obj = ByProductGroup.objects.filter()
        product_group_list = list(product_group_obj.values_list('id', 'name', 'account_code'))
        product_group_column = ['group_id', 'name', 'account_code']
        product_group_df = pd.DataFrame(product_group_list, columns=product_group_column)
        product_group_list = product_group_df.to_dict('r')

        df1 = pd.merge(credit_sale_group_wise_df,cash_sale_group_wise_df, left_on='group_id', right_on='group_id', how='outer')
        merge_df = pd.merge(df1,product_group_df,left_on='group_id', right_on='group_id', how='left')
        merge_df = merge_df.reindex(columns=['account_code','name',"cash_cost",'credit_cost'])

        merge_df = merge_df.rename(columns={'account_code':'Code', 'name':'Product',"cash_cost":'Cash','credit_cost':'Credit'})
        # new_row = pd.DataFrame({'Code':['30910','30911','31004'],'Product':['CGST Collection','SGST Collection','Misc.Income'],'Cash':[ cgst_and_sgst_dict['cgst_collection_for_cash'],cgst_and_sgst_dict['sgst_collection_for_cash'],cash_misc_amount],'Credit':[cgst_and_sgst_dict['cgst_collection_for_credit'],cgst_and_sgst_dict['sgst_collection_for_credit'],credit_misc_amount]})
        # merge_df = pd.concat([new_row, merge_df]).reset_index(drop = True)
        merge_df = merge_df.append({'Code':'30910','Product':'CGST Collection','Cash':cgst_and_sgst_dict['cgst_collection_for_cash'],'Credit':cgst_and_sgst_dict['cgst_collection_for_credit']}, ignore_index=True)
        merge_df = merge_df.append({'Code':'30911','Product':'SGST Collection','Cash':cgst_and_sgst_dict['sgst_collection_for_cash'],'Credit':cgst_and_sgst_dict['sgst_collection_for_credit']}, ignore_index=True)
        merge_df = merge_df.append({'Code':'30910','Product':'Misc.Income','Cash':cash_misc_amount,'Credit':credit_misc_amount}, ignore_index=True)
        merge_df = merge_df.append(merge_df[['Cash','Credit']].sum(), ignore_index=True)
        merge_df.iloc[-1, merge_df.columns.get_loc('Product')] = 'TOTAL'
        merge_df.insert(0,"S NO", np.arange(1,len(merge_df)+1))
        merge_df = merge_df.set_index("S NO")
        merge_df.fillna('')

        credit_business_ids = list(set(main_sale_credit_obj.values_list('by_sale_group__business_id', flat=True)))

        business_obj = Business.objects.filter(id__in=credit_business_ids)
        business_list = list(business_obj.values_list('id', 'businessagentmap__agent__agent_code', 'businessagentmap__agent__first_name'))
        business_column = ['business_id', 'account_code', 'agent_name']
        business_df = pd.DataFrame(business_list, columns=business_column)
        business_df = business_df.fillna(0)
        business_list = business_df.to_dict('r')

        credit_sale_business_wise_df = main_sale_group_credit_df.groupby('business_id').agg({'total_cost': sum})['total_cost']

        df = pd.merge(business_df, credit_sale_business_wise_df, left_on='business_id', right_on='business_id', how='left')
        df = df.reindex(columns=["account_code",'agent_name',"total_cost"])

        df = df.rename(columns={ 'account_code': 'Code','agent_name':'Debitors','total_cost':'Amount'})
        df = df.append(df[['Amount']].sum(), ignore_index=True)
        df.iloc[-1, df.columns.get_loc('Debitors')] = 'TOTAL'
        df.insert(0,"S NO", np.arange(1,len(df)+1))
        df = df.set_index("S NO")
        df.fillna('')

        result_df = pd.concat([merge_df, df], axis=1)
        
        # Excel Part
        from_date_in_strip = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        from_date_in_format = datetime.datetime.strftime(from_date_in_strip, '%d-%m-%Y')

        to_date_in_strip = datetime.datetime.strptime(date_to, "%Y-%m-%d")
        to_date_in_format = datetime.datetime.strftime(to_date_in_strip, '%d-%m-%Y')

        excel_file_name = f"{from_date_in_format} - {to_date_in_format} - daily_sales_statement.xlsx"
        excel_file_path = os.path.join('static/media/by_product/daily_sale/',excel_file_name)

        result_df.to_excel(excel_file_path)

        try:
            path = excel_file_path
            os.makedirs(path)
        except FileExistsError:
            print('already created')
        document = {}
        document['excel_file_name'] = excel_file_name
        document['is_data_available'] = True

        try:
            image_path = excel_file_path
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


def decode_image(encoded_image, file_name=None):
    print('Convert string to image file(Decode)')
    if file_name is None:
        file_name = datetime.datetime.now()
    head, splited_image = encoded_image.split('base64,')
    decoded_image = b64decode(splited_image)
    return ContentFile(decoded_image, str(file_name) + '.xlsx')

def grn_upload(df):
    try:
        df = df.fillna('0')
        grn_numbers = list(set(list(df['grn_number'])))
        for grn in grn_numbers:
            print(df['grn_number'])
            first_df = df[df['grn_number'] == grn].head(1).to_dict('r')[0]
            if PurchaseCompany.objects.filter(company_name=first_df['purchase_company_name']).exists():
                purchase_company_id = PurchaseCompany.objects.get(company_name=first_df['purchase_company_name']).id
            else:
                purchase_company_obj = PurchaseCompany.objects.create(company_name=first_df['purchase_company_name'],
                                                                    created_by_id=1)
                purchase_company_obj.save()
                purchase_company_id = purchase_company_obj.id
            goods_receipt_mater = GoodsReceiptMaster(grn_number=grn,
                                            grn_date=first_df['grn_date'],
                                            bill_number=first_df['bill_number'],
                                            bill_date=first_df['bill_date'],
                                            purchase_company_id=purchase_company_id,
                                            created_by_id=1,
                                            modified_by_id=1,
                                            )
            if first_df['po_number'] != '0':
                goods_receipt_mater.po_number = first_df['po_number']
            if first_df['po_date'] != '0':
                goods_receipt_mater.po_date = first_df['po_date']
            if first_df['dc_number'] != '0':
                goods_receipt_mater.dc_number = first_df['dc_number']
            if first_df['dc_date'] != '0':
                goods_receipt_mater.dc_date = first_df['dc_date']
            goods_receipt_mater.save()
            for index, row in df[df['grn_number'] == grn].iterrows():
                print(row['by_product_code'])
                by_product = ByProduct.objects.get(code=row['by_product_code'])
                goods_receipt_record_obj = GoodsReceiptRecord(goods_receipt_master_id=goods_receipt_mater.id,
                                                            by_product_id=by_product.id,
                                                            quantity_at_receipt=row['new_quantity'],
                                                            quantity_now=row['new_quantity'],
                                                            quantity_now_time=row['grn_date'],
                                                            price_per_unit=row['price_per_unit'],
                                                            price=row['price'],
                                                            total_price=row['total_price'],
                                                            goods_receipt_code='from old excel',
                                                            created_by_id=1,
                                                            modified_by_id=1,
                                                            )
                if row['igst_value'] != 0:
                    goods_receipt_record_obj.igst_value = row['igst_value']
                if row['cgst_value'] != 0:
                    goods_receipt_record_obj.cgst_value = row['cgst_value']
                if row['sgst_value'] != 0:
                    goods_receipt_record_obj.sgst_value = row['sgst_value']
                if row['expiry_date'] != 0:
                    goods_receipt_record_obj.expiry_date = row['expiry_date']
                goods_receipt_record_obj.save()
                daily_goods_receipt_record_obj = GoodsReceiptRecordForDaily(sale_date=row['grn_date'],
                                                            by_product_id=by_product.id,
                                                            quantity_at_receipt=row['new_quantity'],
                                                            quantity_now=row['new_quantity'],
                                                            quantity_now_time=row['grn_date'],
                                                            price_per_unit=row['price_per_unit'],
                                                            total_price=row['total_price'],
                                                            grn_number=row['grn_number'],
                                                            )
                daily_goods_receipt_record_obj.save()

                # add data to Main Stock
                if ByProductCurrentAvailablity.objects.filter(by_product_id=by_product.id).exists():
                    main_input_stock_obj = ByProductCurrentAvailablity.objects.get(by_product_id=by_product.id)
                    main_input_stock_obj.quantity_now = main_input_stock_obj.quantity_now + row['new_quantity']
                    main_input_stock_obj.quantity_now_time = row['grn_date']
                    main_input_stock_obj.modified_by_id = 1
                    main_input_stock_obj.save()
                else:
                    main_input_stock_obj = ByProductCurrentAvailablity(by_product_id=by_product.id,
                                                        quantity_now=row['new_quantity'],
                                                        quantity_now_time=row['grn_date'],
                                                        created_by_id=1,
                                                        modified_by_id=1)
                    main_input_stock_obj.save()
        return True, {}
    except Exception as e:
        print(e)
        data_dict = {
            'error': e
        }
        print(data_dict)
        return False, data_dict


def generate_by_product_order_code_for_upload(date):
    code_bank_obj = BySaleGroupOrderCodeBank.objects.filter()[0]
    current_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    prefix_value = str(code_bank_obj.code_prefix) +  str((current_date.year))[2:] + str(current_date.month).zfill(2) + str(current_date.day)
    last_digit = int(code_bank_obj.last_digit)
    new_digit = last_digit + 1
    code_bank_obj.last_digit = new_digit
    code_bank_obj.save()
    last_count = str(new_digit).zfill(4)
    return prefix_value + str(last_count)


def product_upload(df):
    try:
        df = df.fillna(0)
        booth_codes = list(set(list(df['booth_code'])))
        print(booth_codes)
        for booth_code in booth_codes:
            print(booth_code)
            if BusinessAgentMap.objects.filter(business__code=booth_code).exists():
                first_df = df[df['booth_code'] == booth_code].head(1).to_dict('r')[0]
                payment_method_id = BySaleGroupPaymentMethod.objects.get(name=first_df['payment_method']).id
                business_agent_obj = BusinessAgentMap.objects.get(business__code=first_df['booth_code'])
                business_type_id = business_agent_obj.business.business_type.id
                user_profile_id = business_agent_obj.business.user_profile_id
                agent_id = business_agent_obj.agent_id
                agent_user_id = business_agent_obj.business.user_profile.user.id
                business_id = business_agent_obj.business.id
                via_id = 2
                today = datetime.datetime.strptime(first_df['date'], '%d/%m/%Y').strftime('%Y-%m-%d')
                data_dict = serve_by_product_price_dict(user_profile_id)
                product_price_dict = data_dict['product_price_dict']
                order_category_dict = data_dict['order_category']
                order_category_id = 2
                agent_wallet_obj = ByProductAgentWallet.objects.get(agent_id=agent_id)
                counter_id = None
                is_order_placed = False
                order_code = generate_by_product_order_code_for_upload(today)
                total_cost = 0
                by_sale_group_obj = BySaleGroup(
                    business_id=business_id,
                    order_code=order_code,
                    zone_id=business_agent_obj.business.zone.id,
                    ordered_date=today,
                    ordered_via_id=via_id,
                    value_before_round_off=0,
                    round_off_value=0,
                    total_cost=0,
                    sale_status_id=1, #ordered
                    ordered_by_id=1,
                    modified_by_id=1,
                    payment_method_id=payment_method_id,
                    payment_status_id=1
                )
                by_sale_group_obj.save()
                print('by_sale_group_obj_saved')
                for index, row in df[df['booth_code'] == booth_code].iterrows():
                    product_qty = row['product_qty']
                    print(row['product_code'])
                    product_obj = ByProduct.objects.get(code=row['product_code'])
                    current_product_availablity = ByProductCurrentAvailablity.objects.get(by_product_id=product_obj.id)
                    if product_qty != 0 and product_qty != None:
                        if product_qty <= current_product_availablity.quantity_now:
                            product_base_price = product_qty * product_price_dict[product_obj.id]['base_price']
                            product_mrp = product_qty * product_price_dict[product_obj.id]['mrp']
                            product_gst_dict = calculate_gst_value(product_base_price, product_mrp, product_qty)
                            by_sale_obj = BySale(
                                by_sale_group_id=by_sale_group_obj.id,
                                by_product_id=product_obj.id,
                                count=product_qty,
                                cost=product_base_price,
                                cgst_value=product_gst_dict['product_cgst_value'],
                                sgst_value=product_gst_dict['product_sgst_value'],
                                total_cost=product_mrp,
                                ordered_by_id=1,
                                modified_by_id=1,
                            )
                            by_sale_obj.save()
                            daily_goods_receipt_record_obj = GoodsReceiptRecordForDaily.objects.filter(by_product_id=by_sale_obj.by_product.id, sale_date=today).exclude(quantity_now=0).order_by('id')
                            required_qty = product_qty
                            for goods in daily_goods_receipt_record_obj:
                                if goods.quantity_now >= required_qty:
                                    balance_in_goods = goods.quantity_now - Decimal(required_qty)
                                    goods.quantity_now = balance_in_goods
                                    goods.quantity_now_time = today
                                    goods.save()

                                    goods_receipt_record_sale_map_obj = DailyGoodsReceiptRecordBySaleMap(
                                        daily_goods_receipt_record_id=goods.id,
                                        by_sale_id=by_sale_obj.id,
                                        quantity_dispatched=required_qty
                                    )
                                    goods_receipt_record_sale_map_obj.save()
                                    break
                                else:
                                    required_qty = Decimal(required_qty) - goods.quantity_now
                                    goods_receipt_record_sale_map_obj = DailyGoodsReceiptRecordBySaleMap(
                                        daily_goods_receipt_record_id=goods.id,
                                        by_sale_id=by_sale_obj.id,
                                        quantity_dispatched=required_qty
                                    )
                                    goods_receipt_record_sale_map_obj.save()

                                    goods.quantity_now = 0
                                    goods.quantity_now_time = today
                                    goods.save()


                            if BusinessWiseDailySaleUpdate.objects.filter(sale_date=today, business_id=business_id, by_product_id=product_obj.id).exists():
                                business_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=today, business_id=business_id, by_product_id=product_obj.id)
                                business_sale_obj.received_quantity = business_sale_obj.received_quantity + product_qty
                                business_sale_obj.save()
                            else:
                                is_yesterday_sale_closed = False
                                if BusinessWiseDailySaleUpdate.objects.filter(sale_date__lt=today, business_id=business_id, by_product_id=product_obj.id).exists():
                                    business_sale_obj = BusinessWiseDailySaleUpdate.objects.filter(sale_date__lt=today, business_id=business_id, by_product_id=product_obj.id).order_by('sale_date')[0]
                                    if business_sale_obj.closing_quantity is not None:
                                        is_yesterday_sale_closed = True
                                else:
                                    is_yesterday_sale_closed = True
                                business_sale_obj = BusinessWiseDailySaleUpdate(business_id=business_id,
                                                                            sale_date=today,
                                                                            by_product_id=product_obj.id,
                                                                            received_quantity=product_qty,
                                                                            created_by_id=1,
                                                                            is_yesterday_sale_closed=is_yesterday_sale_closed,
                                                                            updated_by_id=1)
                                business_sale_obj.save()
                            current_product_availablity.quantity_now = current_product_availablity.quantity_now - product_qty
                            current_product_availablity.quantity_now_time = today
                            current_product_availablity.save()
                            total_cost += product_mrp
                            is_order_placed = True
                        else:
                            error_dict = {}
                            error_dict['product_name'] = current_product_availablity.by_product.short_name
                            error_dict['required_qty'] = product_qty
                            error_dict['available_qty'] = current_product_availablity.quantity_now
                            error_dict['is_limit_crossed'] = True
                            return False, error_dict

                value_before_round_off = total_cost
                value_after_round_off = math.ceil(value_before_round_off)
                round_off_value = value_after_round_off - value_before_round_off
                saved_by_sale_group_obj = BySaleGroup.objects.get(id=by_sale_group_obj.id)
                saved_by_sale_group_obj.value_before_round_off = value_before_round_off
                saved_by_sale_group_obj.round_off_value = round_off_value
                saved_by_sale_group_obj.total_cost = value_after_round_off
                saved_by_sale_group_obj.save()
                
                employee_id = 34
                counter_id = Counter.objects.get(name=row['counter_name']).id
                if CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                            collection_date=today).exists():
                    counter_employee_trace_obj = \
                    CounterEmployeeTraceMap.objects.filter(employee_id=employee_id, is_active=True,
                                                            collection_date=today)[0]
                else:
                    counter_employee_trace_obj = CounterEmployeeTraceMap(counter_id=counter_id,
                                                    employee_id=employee_id,
                                                    is_active=True,
                                                    collection_date=today,
                                                    start_date_time=today)
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
                if order_category_dict[order_category_id] == 1:
                    if value_after_round_off != 0:
                        transaction_obj = ByProductTransactionLog(
                            date=today,
                            transacted_by_id=agent_user_id,
                            transacted_via_id=via_id,
                            data_entered_by_id=1,
                            amount=value_after_round_off,
                            transaction_direction_id=1,  # from agent to aavin
                            transaction_mode_id=1,  # Upi
                            transaction_id='1234',
                            transaction_status_id=2,  # completed
                            transaction_approval_status_id=1,  # Accepted
                            transaction_approved_by_id=1,
                            transaction_approved_time=today,
                            wallet_balance_before_this_transaction=agent_wallet_obj.current_balance,
                            wallet_balance_after_transaction_approval=agent_wallet_obj.current_balance,
                            description='Amount for ordering the by product',
                            modified_by_id=1
                        )
                        transaction_obj.save()
        return True, {}
    except Exception as e:
        data_dict = {
            'error': e,
            'is_limit_crossed': False
        }
        return False, data_dict


@transaction.atomic
@api_view(['POST'])
def daily_sale_upload(request):
    sid = transaction.savepoint()
    return_dict = {
        'is_everything_okay': True
    }
    try:
        grn_excel_file = decode_image(request.data['grn_excel_file'])
        grn_df = pd.read_excel(grn_excel_file)
        grn_status, error_dict = grn_upload(grn_df)
        print('GRN_saved')
        if not grn_status:
            transaction.savepoint_rollback(sid)
            print(error_dict)
            error_dict['is_everything_okay'] = False
            error_dict['error_on'] = 'grn'
            return Response(data=error_dict, status=status.HTTP_200_OK)
        else:
            product_excel_file = decode_image(request.data['product_excel_file'])
            product_df = pd.read_excel(product_excel_file)
            product_status, error_dict = product_upload(product_df)
            print('PRODUCTGROUP_saved')
            if not product_status:
                transaction.savepoint_rollback(sid)
                error_dict['is_everything_okay'] = False
                error_dict['error_on'] = 'product'
                return Response(data=error_dict, status=status.HTTP_200_OK)
    
        transaction.savepoint_commit(sid)
        return Response(data=return_dict, status=status.HTTP_200_OK)
    except Exception as err:
        print('Error on {}'.format(err))
        return_dict['is_everything_okay'] = False
        return_dict['error'] = err
        transaction.savepoint_rollback(sid)
        return Response(data=return_dict, status=status.HTTP_200_OK)


@api_view(['GET'])
def delete_overall_sale_and_grn(request):
    BySaleGroup.objects.all().delete()
    GoodsReceiptMaster.objects.all().delete()
    BusinessWiseDailySaleUpdate.objects.all().delete()
    GoodsReceiptRecordForDaily.objects.all().delete()
    ByProductCurrentAvailablity.objects.all().delete()
    return Response(status=status.HTTP_200_OK)

def to_find_values_in_kg_ltr(by_product_unit_name, group_unit, total_qty):
    value = 0
    if by_product_unit_name == 'Gr' and group_unit == 'Kg':
        value = total_qty/1000
    elif by_product_unit_name == 'Gr' and group_unit == 'Nos.':
        value = total_qty
    elif by_product_unit_name == 'Gr' and group_unit == 'Kg':
        value = total_qty
    elif by_product_unit_name == 'Gr' and group_unit == 'Ml':
        value = total_qty/1000
    elif by_product_unit_name == 'Kg' and group_unit == 'Kg':
        value = total_qty
    elif by_product_unit_name == 'Ml' and group_unit == 'L':
        value = total_qty/1000
    elif by_product_unit_name == 'Ml' and group_unit == 'Kg':
        value = total_qty/1000
    elif by_product_unit_name == 'Ml' and group_unit == 'Nos.':
        value = total_qty
    elif by_product_unit_name == 'L' and group_unit == 'Kg':
        value = total_qty
    elif by_product_unit_name == 'Nos.' and group_unit == 'Nos.':
        value = total_qty
    return value


@api_view(['POST'])
def serve_sales_tax_abstract_report(request):
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    if BySale.objects.filter(by_sale_group__ordered_date__range=[from_date, to_date]).exists():
        bysale_abstract_obj = BySale.objects.filter(by_sale_group__ordered_date__range=[from_date, to_date]).order_by('by_product__short_name')
        bysale_abstract_list = list(bysale_abstract_obj.values_list('by_product_id', 'by_product__by_product_group__hsn_code', 'by_product__short_name', 'count', 'cost', 'by_product__cgst_percent', 'cgst_value', 'by_product__sgst_percent', 'sgst_value', 'by_product__quantity', 'by_product__unit__name','by_product__by_product_group__unit__name', 'total_cost'))
        bysale_abstract_column = ["by_product_id","HSN CODE", "PRODUCT", "QTY", "AMOUNT", "CGST%", "CGST AMOUNT", "SGST%", "SGST AMOUNT", "quantity", 'by_product_unit_name', 'group_unit', 'TOTAL AMOUNT']
        bysale_abstract_df = pd.DataFrame(bysale_abstract_list, columns=bysale_abstract_column)
        bysale_abstract_df = bysale_abstract_df.groupby(['by_product_id', 'PRODUCT']).agg({'HSN CODE':'first', 'QTY':'sum', 'AMOUNT':'sum', 'CGST%':'first', 'CGST AMOUNT':'sum', 'SGST%':'first', 'SGST AMOUNT':'sum', 'quantity': 'first', 'by_product_unit_name': 'first', 'group_unit':'first', 'TOTAL AMOUNT': 'sum'}).reset_index()
        # bysale_abstract_df['TOTAL AMOUNT'] = bysale_abstract_df[["AMOUNT" , "CGST AMOUNT", "SGST AMOUNT"]].sum(axis=1)

        bysale_abstract_df['total_qty'] = bysale_abstract_df['QTY'].astype(float) * bysale_abstract_df['quantity'].astype(float)
        bysale_abstract_df['Kg/Ltr'] = bysale_abstract_df.apply(lambda x: to_find_values_in_kg_ltr(x['by_product_unit_name'], x['group_unit'], x['total_qty']), axis=1)

        bysale_abstract_df = bysale_abstract_df.drop(['by_product_id'], axis = 1)

        bysale_abstract_df = bysale_abstract_df[["HSN CODE", "PRODUCT", "QTY", "total_qty", 'Kg/Ltr',"AMOUNT", "CGST%", "CGST AMOUNT", "SGST%", "SGST AMOUNT", "TOTAL AMOUNT", 'by_product_unit_name', 'group_unit']]
        bysale_abstract_df


        bysale_abstract_df.insert(0,"S.NO", np.arange(1,len(bysale_abstract_df)+1))
        bysale_abstract_df.fillna(' ')


        # ____________________________pdf_______________________________________________
        file_name =  'BYPRODUCT SALES TAX ABSTRACT REPORT.pdf'
        file_path = os.path.join('static/media/monthly_report/', file_name)
        mycanvas = canvas.Canvas(file_path, pagesize=(11.694 * inch, 8.264 * inch))

        # ________Head_lines________#
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(260, 570, "THE COIMBATORE DISTRICT CO OPERATIVE MILK PRODUCER'S UNION LTD.,")
        mycanvas.setFont('Helvetica', 10)
        mycanvas.drawCentredString(57, 557, "PACHAPALAYAM")
        mycanvas.drawCentredString(70, 545, "KALAMPALAYAM (P.O)")
        mycanvas.drawCentredString(50, 533, "COIMBATORE")
        mycanvas.setFont('Helvetica-Bold', 13)
        mycanvas.drawCentredString(405, 520, 'Sales Tax Abstract on - '+str(from_date)+ " " +"to"+ " " + str(to_date))

        x = 50
        y = 500
        # To Write headers
        mycanvas.setFont('Helvetica-Bold', 8)
        mycanvas.drawCentredString(x-15,y,"S.NO")
        mycanvas.drawCentredString(x+30,y,"HSN CODE")
        mycanvas.drawCentredString(x+100-18,y,"PRODUCT")
        mycanvas.drawCentredString(x+222-7,y,"QTY")
        mycanvas.drawCentredString(x+330-65,y,"Kg / Ltr")
        mycanvas.drawCentredString(x+330,y,"AMOUNT")
        mycanvas.drawCentredString(x+410-10,y,"CGST%")
        mycanvas.drawCentredString(x+475,y,"CGST AMOUNT")
        mycanvas.drawCentredString(x+555,y,"SGST%")
        mycanvas.drawCentredString(x+635,y,"SGST AMOUNT")
        mycanvas.drawCentredString(x+730,y,"TOTAL AMOUNT")

        # Heading lines
        mycanvas.line(x-30,y+15, x+770, y+15)
        mycanvas.line(x-30,y-5, x+770, y-5)

        header_line_y = y+15
        y_point = 480
        x1_line = 20
        x2_line = 820

        for index, product in bysale_abstract_df.iterrows():
        #     print(index, product['TOTAL AMOUNT'])
            mycanvas.setFont('Helvetica', 8.3)
            mycanvas.drawString(30, y_point, str(int(product['S.NO'])))
            mycanvas.drawString(65, y_point, str(product['HSN CODE']))
            mycanvas.drawString(113, y_point, str(product['PRODUCT']))
            mycanvas.drawRightString(272, y_point, str(int(product['QTY'])))
            mycanvas.drawRightString(327, y_point, str(product['Kg/Ltr']))
            mycanvas.drawRightString(399, y_point, str(product['AMOUNT']))
            mycanvas.drawRightString(460, y_point, str(product['CGST%']))
            mycanvas.drawRightString(535, y_point, str(product['CGST AMOUNT']))
            mycanvas.drawRightString(615, y_point, str(product['SGST%']))
            mycanvas.drawRightString(695, y_point, str(product['SGST AMOUNT']))
            mycanvas.drawRightString(795, y_point, str(product['TOTAL AMOUNT']))
            #end horizontal Line
        #     mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)
            y_point -=16
            
            #for next page 
            if (index+1) % 30 == 0:
                #end verticle lines for remining columns
                mycanvas.line(x-30,header_line_y, x-30, y_point-5)
                mycanvas.line(x+770,header_line_y, x+770, y_point-5)
                mycanvas.showPage()
                
                y_point = 560
                x1_line = 20
                x2_line = 820

                #for new next page hearders
                mycanvas.setFont('Helvetica-Bold', 8)
                mycanvas.drawCentredString(x-15,y_point,"S.NO")
                mycanvas.drawCentredString(x+30,y_point,"HSN CODE")
                mycanvas.drawCentredString(x+100-18,y_point,"PRODUCT")
                mycanvas.drawCentredString(x+222-7,y_point,"QTY")
                mycanvas.drawCentredString(x+330-65,y_point,"Kg/Ltr")
                mycanvas.drawCentredString(x+330,y_point,"AMOUNT")
                mycanvas.drawCentredString(x+410-10,y_point,"CGST%")
                mycanvas.drawCentredString(x+475,y_point,"CGST AMOUNT")
                mycanvas.drawCentredString(x+555,y_point,"SGST%")
                mycanvas.drawCentredString(x+635,y_point,"SGST AMOUNT")
                mycanvas.drawCentredString(x+730,y_point,"TOTAL AMOUNT")

                # Heading lines
                mycanvas.line(x-30,y_point+15, x+770, y_point+15)
                mycanvas.line(x-30,y_point-5, x+770, y_point-5)
            
                header_line_y = y+75
                y_point = 540
                x1_line = 20
                x2_line = 820

        mycanvas.setFont('Helvetica-Bold' ,9)
        mycanvas.drawString(125, y_point, str("TOTAL"))
        mycanvas.drawRightString(275, y_point, str(bysale_abstract_df['QTY'].sum()))
        mycanvas.drawRightString(400, y_point, str(bysale_abstract_df['AMOUNT'].sum()))
        mycanvas.drawRightString(535, y_point, str(bysale_abstract_df['CGST AMOUNT'].sum()))
        mycanvas.drawRightString(696, y_point, str(bysale_abstract_df['SGST AMOUNT'].sum()))
        mycanvas.drawRightString(798, y_point, str(round(bysale_abstract_df['TOTAL AMOUNT'].sum(), 2)))

        #end verticle lines for remining columns
        mycanvas.line(x-30,header_line_y, x-30, y_point-5)
        mycanvas.line(x+770,header_line_y, x+770, y_point-5)

        mycanvas.line(x1_line, y_point+12, x2_line, y_point+12)
        mycanvas.line(x1_line, y_point-5, x2_line, y_point-5)

        mycanvas.save()
        print('ok')
        
        document = {}
        # document['file_name'] = file_name
        document['is_data_available'] = True
        try:
            image_path = file_path
            with open(image_path, 'rb') as image_file:
                encoded_image = b64encode(image_file.read())
                document['pdf'] = encoded_image
        except Exception as err:
            print(err)
        return Response(data=document, status=status.HTTP_200_OK)
    else:
        document = {}
        # document['file_name'] = file_name
        document['is_data_available'] = False
        return Response(data=document, status=status.HTTP_200_OK)


@transaction.atomic
@api_view(['POST'])
def delete_selected_by_product_order(request):
    print(request.data)
    sid = transaction.savepoint()
    try:
        by_sale_group_obj = BySaleGroup.objects.get(id=request.data['id'])
        by_sale_obj = BySale.objects.filter(by_sale_group_id=by_sale_group_obj.id)
        for by_sale in by_sale_obj:
            if DailyGoodsReceiptRecordBySaleMap.objects.filter(by_sale_id=by_sale.id).exists():
                daily_goods_receipt_record_sales = DailyGoodsReceiptRecordBySaleMap.objects.filter(by_sale_id=by_sale.id)
                for daily_goods_receipt_record_sale in daily_goods_receipt_record_sales:
                    daily_goods_receipt_record = daily_goods_receipt_record_sale.daily_goods_receipt_record
                    daily_goods_receipt_record.quantity_now = daily_goods_receipt_record.quantity_now + daily_goods_receipt_record_sale.quantity_dispatched
                    daily_goods_receipt_record.save()
                    # add the quantity to respected daily sale and remove the map table entry
                    daily_goods_receipt_record_sale.delete()
                    print('daily_sale_goods')
                    break

            if BusinessWiseDailySaleUpdate.objects.filter(sale_date=by_sale_group_obj.ordered_date, business_id=by_sale_group_obj.business_id, by_product_id=by_sale.by_product.id).exists():
                business_wise_sale_obj = BusinessWiseDailySaleUpdate.objects.get(sale_date=by_sale_group_obj.ordered_date, business_id=by_sale_group_obj.business_id, by_product_id=by_sale.by_product.id)
                business_wise_sale_obj.received_quantity = business_wise_sale_obj.received_quantity - by_sale.count
                business_wise_sale_obj.save()

                # delete daily business wise sale if received qty is zero
                if business_wise_sale_obj.received_quantity == 0:
                    business_wise_sale_obj.delete()
                    print('business wise sale delete')

            current_product_availablity_obj = ByProductCurrentAvailablity.objects.get(by_product_id=by_sale.by_product.id)
            current_product_availablity_obj.quantity_now = current_product_availablity_obj.quantity_now + Decimal(by_sale.count)
            current_product_availablity_obj.save()

            # now add the qty to the respected GRN if gatepass taken

            if GoodsReceiptRecordBySaleMap.objects.filter(by_sale_id=by_sale.id).exists():
                goods_receipt_record_sales = GoodsReceiptRecordBySaleMap.objects.filter(by_sale_id=by_sale.id)
                for goods_receipt_record_sale in goods_receipt_record_sales:
                    goods_receipt_record = goods_receipt_record_sale.goods_receipt_record
                    goods_receipt_record.quantity_now = goods_receipt_record.quantity_now + goods_receipt_record_sale.quantity_dispatched
                    goods_receipt_record.save()
                    # add the quantity to respected daily sale and remove the map table entry
                    goods_receipt_record_sale.delete()
                    print('sale_goods')
        delete_sale_group_obj = BySaleGroupDeleteLog(business_id=by_sale_group_obj.business.id,
                                                ordered_date=by_sale_group_obj.ordered_date,
                                                total_cost=by_sale_group_obj.total_cost,
                                                ordered_by_id=by_sale_group_obj.ordered_by.id,
                                                ordered_date_time=by_sale_group_obj.time_created,
                                                deleted_by_id=request.user.id,
                                                delete_date_time=datetime.datetime.now())
        delete_sale_group_obj.save()
        by_sale_group_obj.delete()
        transaction.savepoint_commit(sid)
        return Response(data='success', status=status.HTTP_200_OK)
    except Exception as e:
        print('Error - {}'.format(e))
        transaction.savepoint_rollback(sid)
        return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def serve_json_for_govt_upload(request):
    print(request.data)
    from_date = request.data['from_date']   
    to_date = request.data['to_date']
    input_type = request.data['input_type']
    bill_number = request.data['bill_number']
    final_list = []
    if input_type == 'date':
        gate_pass_obj = BySaleGroupGatepass.objects.filter(bill_date__date__range=[from_date, to_date])
    else:
        gate_pass_obj = BySaleGroupGatepass.objects.filter(bill_number=bill_number)
      
    if gate_pass_obj.count() > 0:
        by_sale_group_gatepass = gate_pass_obj.order_by('bill_date', 'id')
        for gatepass in by_sale_group_gatepass:
            business_agent_map = BusinessAgentMap.objects.get(business_id=gatepass.by_sale_group.business.id)
            # print('business_agent_map', business_agent_map)
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
                
                splitted_bill_number = gatepass.bill_number.split('_')
                print('splitted_bill_number', splitted_bill_number)
                if len(splitted_bill_number) == 2:
                    bill_number = splitted_bill_number[0] + splitted_bill_number[1]
                else:
                    bill_number = splitted_bill_number[0]
                bill_date_in_format = datetime.datetime.strftime(gatepass.bill_date, '%d/%m/%Y')
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
                
                business_agent_map = BusinessAgentMap.objects.get(business_id=gatepass.by_sale_group.business.id)
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
            
                sales = gatepass.by_sale_group.bysale_set.all()
                total_basic_cost = sales.aggregate(Sum('cost'))['cost__sum']
                total_cgst_cost = sales.aggregate(Sum('cgst_value'))['cgst_value__sum']
                total_sgst_cost = sales.aggregate(Sum('sgst_value'))['sgst_value__sum']
                total_cost = gatepass.by_sale_group.total_cost
                rounded_value = gatepass.by_sale_group.round_off_value
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
                    "TotInvVal": round(float(total_cost), 2)
                }
                main_dict["ValDtls"] = value_details
            
                s_no = 1
                item_list = []
                for sale in sales:
                    unit_price = sale.total_cost / Decimal(sale.count)
                    Discount = 0
                    PreTaxVal = 0
                    ass_amount = sale.cost - Discount - PreTaxVal
                    total_gst_percentage = sale.by_product.cgst_percent + sale.by_product.sgst_percent
                    item_dict = {
                        "SlNo": str(s_no),
                        "PrdDesc": str(sale.by_product.name),
                        "IsServc": "N",
                        "HsnCd": str(sale.by_product.by_product_group.hsn_code),
                        "Qty": int(sale.count),
                        "Unit": "PAC",
                        "UnitPrice": round(float(unit_price), 2),
                        "TotAmt": round(float(sale.cost), 2),
                        "Discount": 0,
                        "PreTaxVal": 0,
                        "AssAmt": round(float(ass_amount), 2),
                        "GstRt": round(float(total_gst_percentage), 2),
                        "IgstAmt": 0,
                        "CgstAmt": round(float(sale.cgst_value), 2),
                        "SgstAmt": round(float(sale.sgst_value), 2),
                        "CesRt":0,
                        "CesAmt":0,
                        "CesNonAdvlAmt":0,
                        "StateCesRt":0,
                        "StateCesAmt":0,
                        "StateCesNonAdvlAmt":0,
                        "OthChrg":0,
                        "TotItemVal": round(float(sale.total_cost), 2)
                    }
                    s_no += 1
                    item_list.append(item_dict)
                main_dict["ItemList"] = item_list
                final_list.append(main_dict) 

    return Response(data=final_list, status=status.HTTP_200_OK)



@api_view(['POST'])
def serve_govt_gst_bill(request):
    print(request.data)
    selected_business_type_ids = request.data['selected_business_type_id']
    from_date = request.data['from_date']
    to_date = request.data['to_date']
    if BySaleGroupGatepass.objects.filter(bill_date__date__range=[from_date, to_date], by_sale_group__business__business_type_id__in=selected_business_type_ids).exists():
        by_sale_obj = BySaleGroupGatepass.objects.filter(bill_date__date__range=[from_date, to_date], by_sale_group__business__business_type_id__in=selected_business_type_ids)
        by_sale_values = list(by_sale_obj.values_list('by_sale_group__business__businessagentmap__agent__first_name', 'by_sale_group__business__businessagentmap__agent__agent_profile__gst_number', 'bill_number', 'bill_date', 'by_sale_group__total_cost', 'by_sale_group__bysale__by_product__cgst_percent', 'by_sale_group__bysale__by_product__sgst_percent', 'by_sale_group__bysale__cost', 'by_sale_group__bysale__cgst_value', 'by_sale_group__bysale__sgst_value', 'id'))
        by_sale_column = ['agent_name', 'gst_number', 'bill_no', 'bill_date', 'total_cost', 'csgt', 'sgst', 'taxable_value', 'cgst_value', 'sgst_value', 'bill_id']
        by_sale_df = pd.DataFrame(by_sale_values, columns=by_sale_column)
        by_sale_df['bill_date'] = by_sale_df['bill_date'].dt.strftime('%d-%b-%Y')
        by_sale_df['total_gst'] = by_sale_df['csgt'] + by_sale_df['sgst']
        by_sale_df = by_sale_df.fillna('')
        by_sale_df = by_sale_df.groupby(['bill_id', 'total_gst']).agg({'agent_name': 'first','gst_number': 'first','bill_no': 'first', 'bill_date': 'first', 'total_cost': 'first','taxable_value': sum , 'cgst_value': sum, 'sgst_value': sum}).reset_index()

        final_df = by_sale_df.rename(columns = {'gst_number': 'GSTIN_UINOFRECIPIENT', 'agent_name': 'NAME', 'bill_no': 'INVOICENO', 'bill_date' : 'INVOICEDATE', 'total_cost': 'INVOICEVALUE', 'total_gst': 'RATE', 'taxable_value': 'TAXABLEVALUE', 'cgst_value': 'CGST', 'sgst_value': 'SGST'})
        final_df['PLACEOFSUPPLY'] = ''
        final_df['REVERSECHARGE'] = ''
        final_df['INVOICETYPE'] = ''
        final_df['IGST'] = 0
        final_df = final_df.drop(columns=['bill_id'])
        final_df = final_df[['GSTIN_UINOFRECIPIENT', 'NAME', 'INVOICENO', 'INVOICEDATE', 'INVOICEVALUE', 'PLACEOFSUPPLY', 'REVERSECHARGE', 'INVOICETYPE', 'RATE', 'TAXABLEVALUE', 'CGST', 'SGST', 'IGST']]


        by_sale_group_gatepass_obj = BySaleGroupGatepass.objects.filter(bill_date__date__range=[from_date, to_date], by_sale_group__business__business_type_id__in=selected_business_type_ids).values_list('by_sale_group__business__businessagentmap__agent__first_name', 'by_sale_group__business__businessagentmap__agent__agent_profile__gst_number', 'by_sale_group__bysale__by_product__short_name','bill_number','bill_date', 'by_sale_group__bysale__sgst_value', 'by_sale_group__bysale__cgst_value', 'by_sale_group__bysale__total_cost', 'by_sale_group__bysale__by_product__by_product_group__hsn_code', 'by_sale_group__bysale__count', 'by_sale_group__bysale__by_product__cgst_percent', 'by_sale_group__bysale__by_product__sgst_percent')
        by_sale_group_gatepass_columns = ["agent_name","gst_number","short_name","bill_number", "bill_date", "sgst_value","cgst_value",  "net_amount", "hsn", 'count', 'cgst', 'sgst']
        df = pd.DataFrame(list(by_sale_group_gatepass_obj), columns=by_sale_group_gatepass_columns)
        df['RATE'] = (df['net_amount'].astype('float')/df['count'].astype('float'))
        df['GST'] = df['cgst'].astype('float') + df['sgst'].astype('float')
        df['ISGT'] = 0.000
        df['bill_date'] = df['bill_date'].dt.strftime('%d-%b-%Y')
        df = df.rename(columns={'agent_name':'AGENT', 'gst_number':'BTAXNO', 'short_name':'PRODUCT', 'bill_number':'INVNO', 'bill_date':'INVDATE', 'sgst_value':'SGST','cgst_value':'CGST', 'net_amount':'NETAMOUNT', 'hsn':'HSNCODE'})
        final_df_2 = df[['AGENT', 'BTAXNO', 'PRODUCT', 'INVNO', 'INVDATE', 'RATE', 'GST', 'SGST', 'CGST', 'ISGT','NETAMOUNT', 'HSNCODE']]
        final_df_2 = final_df_2.fillna(' ')
        file_name = f"static/media/by_product/monthly_report/{from_date} - {to_date} - GVT GST Bill.xlsx"
        writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
        sheet_name1 = "sheel1"
        sheet_name2 = "sheel2"
        final_df.to_excel(writer, sheet_name=sheet_name1, index=False)
        final_df_2.to_excel(writer, sheet_name=sheet_name2, index=False)
        writer.save()
        document = {}
        # document['file_name'] = file_name
        document['is_data_available'] = True
        document['file_name'] = f"{from_date} - {to_date} - GVT GST Bill.xlsx"
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
        # document['file_name'] = file_name
        document['is_data_available'] = False
        return Response(data=document, status=status.HTTP_200_OK)


@api_view(['POST'])
def serve_byproduct_analytic_report(request):

    data={
    "from_date":request.data['from_date'],
    "to_date":request.data['to_date'],
    "report_option":request.data['report_option'],
    "type":request.data['type']
    }
    if request.data["type"] == "Sale":
        # print('Check1')
        if request.data['report_option'] == "Booth Wise":
            # booth_codes = [2900]
            # print('check2')
            booth_codes =  request.data['booth_code']
            by_sale_group_booth_obj=BySaleGroup.objects.filter(ordered_date__range=[data["from_date"],data["to_date"]],business__code__in=booth_codes)
            by_sale_group_booth_list=by_sale_group_booth_obj.values_list("id","business__code","business__business_type__name","bysale__by_product__quantity","ordered_date","bysale__by_product__name","bysale__count","bysale__by_product__cgst_amount","bysale__by_product__sgst_amount","bysale__total_cost","bysale__by_product__cgst_percent","bysale__by_product__sgst_percent")
            by_sale_group_booth_column=["id","business_code","business_type","quantity","ordered_date","by_product_name","bysale_count","cgst_amount","sgst_amount","total_cost","cgst_percent","sgst_percent"]
            by_sale_group_booth_df=pd.DataFrame(by_sale_group_booth_list,columns=by_sale_group_booth_column)
            # print('check')
            by_sale_group_booth_df['GST%'] = by_sale_group_booth_df['cgst_percent']+by_sale_group_booth_df['sgst_percent']
            by_sale_group_booth_df.drop('cgst_percent', inplace=True, axis=1)
            by_sale_group_booth_df.drop('sgst_percent', inplace=True, axis=1)
            by_sale_group_booth_df.drop('id', inplace=True, axis=1)
            
            agent_booth_obj=BusinessAgentMap.objects.filter(business__code__in=booth_codes).values_list('agent__first_name',"business__code")
            agent_booth_column=['agent_name',"business_code"]
            agent_booth_df=pd.DataFrame(agent_booth_obj,columns=agent_booth_column)
            
            booth_type_df = pd.merge(by_sale_group_booth_df, agent_booth_df, left_on='business_code', right_on='business_code', how='left')
            
            booth_type_df.insert(0, 'S.No', range(1, 1 + len(booth_type_df)))
            
            booth_type_df = booth_type_df.reindex(columns=[
            "S.No","business_code",'agent_name',"business_type","quantity","ordered_date","by_product_name",
            'GST%',"bysale_count","cgst_amount","sgst_amount","total_cost"])
        
            
            booth_type_df = booth_type_df.rename(columns={'S.No': 'S.No', 'business_code': 'Booth No','agent_name':'Agent Name','business_type':'Business Type','quantity' :'Product Quantity','ordered_date': 'Date','by_product_name':'Product Name','bysale_count':'Product Count','GST%':' Product GST%','cgst_amount':'Product CGST Amount','sgst_amount':'Product SGST Amount','total_cost':'Product Total Amount'})
            # total_booth_check_box_list =  {'Product Name','Product Count',' Product GST%','Product CGST Amount','Product SGST Amount','Product Total Amount'}
            # # user_booth_check_box_list = {'Product Name','Product Count'}
            # user_booth_check_box_list = request.data['user_check_box_list']
            # booth_check_box_list = total_booth_check_box_list.difference(user_booth_check_box_list)
            # booth_type_df.drop(booth_check_box_list,inplace= True,axis = 1)
            booth_type_df = booth_type_df.set_index('S.No')
            booth_type_df = booth_type_df.append({'Product SGST Amount': 'TOTAL AMOUNT', 'Product Total Amount':booth_type_df['Product Total Amount'].sum()}, ignore_index = True)

            file_name = str(datetime.datetime.now().date()) + '_Booth_Report.xlsx'
            file_path = os.path.join('static/media/by_product/daily_sale/', file_name)
                
            booth_type_df.to_excel(file_path)
            # print(file_name)

            data['file_name'] = file_name
            try:
                image_path = file_path
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    data['excel'] = encoded_image
            except Exception as err:
                print(err)
            return Response(data=data, status=status.HTTP_200_OK)
                
        elif request.data['report_option'] == "Business Type Wise":
            business_type_ids = request.data['business_type_id']
            # business_type_ids  = [1]
            
            by_sale_group_business_obj=BySaleGroup.objects.filter(ordered_date__range=[data["from_date"],data["to_date"]],business__business_type__in=business_type_ids)
            by_sale_group_business_list=by_sale_group_business_obj.values_list("id","business__code","business__business_type__name","bysale__by_product__quantity","ordered_date","bysale__by_product__name","bysale__count","bysale__by_product__cgst_amount","bysale__by_product__sgst_amount","bysale__total_cost","bysale__by_product__cgst_percent","bysale__by_product__sgst_percent")
            by_sale_group_business_column=["id","business_code","business_type","quantity","ordered_date","by_product_name","bysale_count","cgst_amount","sgst_amount","total_cost","cgst_percent","sgst_percent"]
            by_sale_group_business_df=pd.DataFrame(by_sale_group_business_list,columns=by_sale_group_business_column)
            
            by_sale_group_business_df['GST%'] = by_sale_group_business_df['cgst_percent']+by_sale_group_business_df['sgst_percent']
            by_sale_group_business_df.drop('cgst_percent', inplace=True, axis=1)
            by_sale_group_business_df.drop('sgst_percent', inplace=True, axis=1)
            by_sale_group_business_df.drop('id', inplace=True, axis=1)
            
            agent_business_obj=BusinessAgentMap.objects.filter(business__business_type_id__in=business_type_ids).values_list('agent__first_name',"business__business_type__name")
            agent_business_column=['agent_name',"business_type"]
            agent_business_df=pd.DataFrame(agent_business_obj,columns=agent_business_column)
            
            business_type_df = pd.merge(by_sale_group_business_df, agent_business_df, left_on='business_type', right_on='business_type', how='left')
            
            business_type_df.insert(0, 'S.No', range(1, 1 + len(business_type_df)))
            
            business_type_df = business_type_df.reindex(columns=[
            "S.No","business_code",'agent_name',"business_type","quantity","ordered_date","by_product_name",
            'GST%',"bysale_count","cgst_amount","sgst_amount","total_cost"])
        
            
            business_type_df = business_type_df.rename(columns={'S.No': 'S.No', 'business_code': 'Booth No','agent_name':'Agent Name','business_type':'Business Type','quantity' :'Product Quantity','ordered_date': 'Date','by_product_name':'Product Name','bysale_count':'Product Count','GST%':' Product GST%','cgst_amount':'Product CGST Amount','sgst_amount':'Product SGST Amount','total_cost':'Product Total Amount'})
            
            # total_business_check_box_list =  {'Product Name','Product Count',' Product GST%','Product CGST Amount','Product SGST Amount','Product Total Amount'}
            # # user_business_check_box_list = {'Product Name','Product Count'}
            # user_business_check_box_list = request.data['user_check_box_list']
            # business_check_box_list = total_business_check_box_list.difference(user_business_check_box_list)
            # business_type_df.drop(business_check_box_list,inplace= True,axis = 1)
            business_type_df = business_type_df.set_index('S.No')
            business_type_df = business_type_df.append({'Product SGST Amount': 'TOTAL AMOUNT', 'Product Total Amount':business_type_df['Product Total Amount'].sum()}, ignore_index = True)

            file_name = str(datetime.datetime.now().date()) + '_Business_Report.xlsx'
            file_path = os.path.join('static/media/by_product/daily_sale/', file_name)
                
            business_type_df.to_excel(file_path)
            # print(file_name)

            data['file_name'] = file_name
            try:
                image_path = file_path
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    data['excel'] = encoded_image
            except Exception as err:
                print(err)
            return Response(data=data, status=status.HTTP_200_OK)
            
            
        elif request.data['report_option'] == "Product Wise":
            # by_product_ids = [533,534]
            by_product_ids= request.data['by_product_ids']
            # if by_product_ids == None:
            #     by_product_id = list(ByProduct.objects.filter().values_list('id',flat=True))
            #     print("check")
            by_sale_group_product_obj=BySaleGroup.objects.filter(ordered_date__range=[data["from_date"],data["to_date"]],bysale__by_product_id__in=by_product_ids)
            by_sale_group_product_list=by_sale_group_product_obj.values_list("id","bysale__count","bysale__by_product__cgst_amount","bysale__by_product__quantity","ordered_date","bysale__by_product__sgst_amount","bysale__total_cost","bysale__by_product__cgst_percent","bysale__by_product__sgst_percent","bysale__by_product__name")
            by_sale_group_product_column=["id","bysale_count","cgst_amount","quantity","ordered_date","sgst_amount","total_cost","cgst_percent","sgst_percent","by_product_name"]
            by_sale_group_product_df=pd.DataFrame(by_sale_group_product_list,columns=by_sale_group_product_column)

            by_sale_group_product_df['GST%'] = by_sale_group_product_df['cgst_percent']+by_sale_group_product_df['sgst_percent']
            by_sale_group_product_df.drop('cgst_percent', inplace=True, axis=1)
            by_sale_group_product_df.drop('sgst_percent', inplace=True, axis=1)
            by_sale_group_product_df.drop('id', inplace=True, axis=1)
            
            by_sale_group_product_df.insert(0, 'S.No', range(1, 1 + len(by_sale_group_product_df)))
            
            by_sale_group_product_df = by_sale_group_product_df.reindex(columns=[
            "S.No","by_product_name","quantity","ordered_date",
            'GST%',"bysale_count","cgst_amount","sgst_amount","total_cost"])
            
            by_sale_group_product_df = by_sale_group_product_df.rename(columns={'S.No': 'S.No', 'by_product_name':'Product Name','quantity' :'Product Quantity','ordered_date': 'Date','bysale_count':'Product Count','GST%':' Product GST%','cgst_amount':'Product CGST Amount','sgst_amount':'Product SGST Amount','total_cost':'Product Total Amount'})
            
            # total_product_check_box_list =  {'Product Count',' Product GST%','Product CGST Amount','Product SGST Amount','Product Total Amount'}
            # # user_product_check_box_list = {'Product CGST Amount','Product SGST Amount','Product Total Amount'}
            # user_product_check_box_list = request.data['user_check_box_list']
            # product_check_box_list = total_product_check_box_list.difference(user_product_check_box_list)
            # by_sale_group_product_df.drop(product_check_box_list,inplace= True,axis = 1)
            by_sale_group_product_df = by_sale_group_product_df.set_index('S.No')
            by_sale_group_product_df = by_sale_group_product_df.append({'Product SGST Amount': 'TOTAL AMOUNT', 'Product Total Amount':by_sale_group_product_df['Product Total Amount'].sum()}, ignore_index = True)

            file_name = str(datetime.datetime.now().date()) + '_Product_Report.xlsx'
            file_path = os.path.join('static/media/by_product/daily_sale/', file_name)
                
            by_sale_group_product_df.to_excel(file_path)
            # print(file_name)

            data['file_name'] = file_name
            try:
                image_path = file_path
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    data['excel'] = encoded_image
            except Exception as err:
                print(err)
            return Response(data=data, status=status.HTTP_200_OK)
                
    if data['type'] == "Received":
        if data['report_option'] == "Total GRN":
            # grn_number_ids = ["GRN2200050"]
            grn_number_ids = request.data['grn_number_id']
            goods_receipt_grn_obj = GoodsReceiptRecord.objects.filter(goods_receipt_master__grn_date__range=[data["from_date"],data["to_date"]],goods_receipt_master__grn_number__in=grn_number_ids)
            goods_receipt_grn_list = goods_receipt_grn_obj.values_list('goods_receipt_master__grn_number','goods_receipt_master__purchase_company__company_name','goods_receipt_master__bill_number','goods_receipt_master__bill_date','goods_receipt_master__grn_date','by_product__short_name','by_product__quantity','by_product__bysale__count',
                                                                    'by_product__cgst_percent','by_product__sgst_percent','by_product__cgst_amount','by_product__sgst_amount','by_product__bysale__total_cost')
            goods_receipt_grn_column = ['grn_number','purchase_company','bill_number','bill_date','date','by_product_name','quantity','count','cgst_percent','sgst_percent','cgst_amount','sgst_amount','total_cost']
            goods_receipt_grn_df = pd.DataFrame(goods_receipt_grn_list,columns=goods_receipt_grn_column)
            
            goods_receipt_grn_df['GST%'] = goods_receipt_grn_df['cgst_percent']+goods_receipt_grn_df['sgst_percent']
            goods_receipt_grn_df.drop('cgst_percent', inplace=True, axis=1)
            goods_receipt_grn_df.drop('sgst_percent', inplace=True, axis=1)
            
            goods_receipt_grn_df.insert(0, 'S.No', range(1, 1 + len(goods_receipt_grn_df)))
            goods_receipt_grn_df = goods_receipt_grn_df.reindex(columns=[
            'S.No','grn_number','purchase_company','bill_number','bill_date','date','by_product_name','quantity','count','GST%','cgst_amount','sgst_amount','total_cost'])
            
            goods_receipt_grn_df = goods_receipt_grn_df.drop_duplicates(subset=['grn_number','by_product_name'], keep="first")

            goods_receipt_grn_df = goods_receipt_grn_df.rename(columns={'S.No': 'S.No','grn_number':'GRN No','purchase_company':'Purchase Company','bill_number':'Bill Number','bill_date':'Bill Date','date':'Date','by_product_name':'Product Name','quantity' :'Product Quantity','count':'Product Count','GST%':'Product GST%','cgst_amount':'Product CGST Amount','sgst_amount':'Product SGST Amount','total_cost':'Product Total Amount'})
            
            goods_receipt_grn_df['Date'] = goods_receipt_grn_df['Date'].apply(lambda a: pd.to_datetime(a).date()) 
            goods_receipt_grn_df['Bill Date'] = goods_receipt_grn_df['Bill Date'].apply(lambda a: pd.to_datetime(a).date())
            goods_receipt_grn_df = goods_receipt_grn_df.set_index('S.No')
            goods_receipt_grn_df = goods_receipt_grn_df.append({'Product SGST Amount': 'TOTAL AMOUNT', 'Product Total Amount':goods_receipt_grn_df['Product Total Amount'].sum()}, ignore_index = True)

            file_name = str(datetime.datetime.now().date()) + '_GRN_Report.xlsx'
            file_path = os.path.join('static/media/by_product/daily_sale/', file_name)
            
            goods_receipt_grn_df.to_excel(file_path)
            #print(file_name)

            data['file_name'] = file_name
            try:
                image_path = file_path
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    data['excel'] = encoded_image
            except Exception as err:
                print(err)
            return Response(data=data, status=status.HTTP_200_OK)
            
        elif data['report_option'] == "Product Wise":
            # by_product_ids = [533]
            by_product_ids = request.data['by_product_ids']
            goods_receipt_product_obj = GoodsReceiptRecord.objects.filter(goods_receipt_master__grn_date__range=[data["from_date"],data["to_date"]],by_product_id__in=by_product_ids)
            goods_receipt_product_list = goods_receipt_product_obj.values_list('goods_receipt_master__grn_number','goods_receipt_master__purchase_company__company_name','goods_receipt_master__bill_number','goods_receipt_master__bill_date','goods_receipt_master__grn_date','by_product__short_name','by_product__quantity','by_product__bysale__count',
                                                                    'by_product__cgst_percent','by_product__sgst_percent','by_product__cgst_amount','by_product__sgst_amount','by_product__bysale__total_cost')
            goods_receipt_product_column = ['grn_number','purchase_company','bill_number','bill_date','date','by_product_name','quantity','count','cgst_percent','sgst_percent','cgst_amount','sgst_amount','total_cost']
            goods_receipt_product_df = pd.DataFrame(goods_receipt_product_list,columns=goods_receipt_product_column)
            
            goods_receipt_product_df['GST%'] = goods_receipt_product_df['cgst_percent']+goods_receipt_product_df['sgst_percent']
            goods_receipt_product_df.drop('cgst_percent', inplace=True, axis=1)
            goods_receipt_product_df.drop('sgst_percent', inplace=True, axis=1)
            
            goods_receipt_product_df.insert(0, 'S.No', range(1, 1 + len(goods_receipt_product_df)))
            goods_receipt_product_df = goods_receipt_product_df.reindex(columns=[
            'S.No','by_product_name','grn_number','purchase_company','bill_number','bill_date','date','quantity','count','GST%','cgst_amount','sgst_amount','total_cost'])
            
            goods_receipt_product_df = goods_receipt_product_df.drop_duplicates(subset=['grn_number','by_product_name'], keep="first")

            goods_receipt_product_df = goods_receipt_product_df.rename(columns={'S.No': 'S.No','by_product_name':'Product Name','grn_number':'GRN No','purchase_company':'Purchase Company','bill_number':'Bill Number','bill_date':'Bill Date','date':'GRN Date','quantity' :'Product Quantity','count':'Product Count','GST%':'Product GST%','cgst_amount':'Product CGST Amount','sgst_amount':'Product SGST Amount','total_cost':'Product Total Amount'})
            
            goods_receipt_product_df['GRN Date'] = goods_receipt_product_df['GRN Date'].apply(lambda a: pd.to_datetime(a).date()) 
            goods_receipt_product_df['Bill Date'] = goods_receipt_product_df['Bill Date'].apply(lambda a: pd.to_datetime(a).date())
            
            # total_grn_product_check_box_list =  {'Product Name'}
            # # user_grn_product_check_box_list = {'Product CGST Amount','Product SGST Amount','Product Total Amount'}
            # user_grn_product_check_box_list = request.data['user_check_box_list']
            # grn_product_check_box_list = total_grn_product_check_box_list .difference(user_grn_product_check_box_list)
            # goods_receipt_product_df.drop(grn_product_check_box_list,inplace= True,axis = 1)
            goods_receipt_product_df = goods_receipt_product_df.set_index('S.No')
            goods_receipt_product_df = goods_receipt_product_df.append({'Product SGST Amount': 'TOTAL AMOUNT', 'Product Total Amount':goods_receipt_product_df['Product Total Amount'].sum()}, ignore_index = True)

            file_name = str(datetime.datetime.now().date()) + '_GRN_Product_Report.xlsx'
            file_path = os.path.join('static/media/by_product/daily_sale/', file_name)
            
            goods_receipt_product_df.to_excel(file_path)
            # print(file_name)

            data['file_name'] = file_name
            try:
                image_path = file_path
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    data['excel'] = encoded_image
            except Exception as err:
                print(err)
            return Response(data=data, status=status.HTTP_200_OK)
            
        elif data['report_option'] == "Purchase Company":
            # purchase_company_ids = [4,17]
            purchase_company_ids = request.data['purchase_company_id']
            #  goods_receipt_obj=GoodsReceiptRecord.objects.filter(goods_receipt_master__grn_date__range=[data["from_date"],data["to_date"]],goods_receipt_code=goods_receipt_code,goods_receipt_master__purchase_company__company_name=purchase_company_list,by_product__short_name=by_product_list)
            goods_receipt_purchase_obj = GoodsReceiptRecord.objects.filter(goods_receipt_master__grn_date__range=[data["from_date"],data["to_date"]],goods_receipt_master__purchase_company__in=purchase_company_ids)
            goods_receipt_purchase_list = goods_receipt_purchase_obj.values_list('goods_receipt_master__grn_number','goods_receipt_master__purchase_company__company_name','goods_receipt_master__bill_number','goods_receipt_master__bill_date','goods_receipt_master__grn_date','by_product__short_name','by_product__quantity','by_product__bysale__count',
                                                                    'by_product__cgst_percent','by_product__sgst_percent','by_product__cgst_amount','by_product__sgst_amount','by_product__bysale__total_cost')
            goods_receipt_purchase_column = ['grn_number','purchase_company','bill_number','bill_date','date','by_product_name','quantity','count','cgst_percent','sgst_percent','cgst_amount','sgst_amount','total_cost']
            goods_receipt_purchase_df = pd.DataFrame(goods_receipt_purchase_list,columns=goods_receipt_purchase_column)
            
            goods_receipt_purchase_df['GST%'] = goods_receipt_purchase_df['cgst_percent']+goods_receipt_purchase_df['sgst_percent']
            goods_receipt_purchase_df.drop('cgst_percent', inplace=True, axis=1)
            goods_receipt_purchase_df.drop('sgst_percent', inplace=True, axis=1)
            
            goods_receipt_purchase_df.insert(0, 'S.No', range(1, 1 + len(goods_receipt_purchase_df)))
            goods_receipt_purchase_df = goods_receipt_purchase_df.reindex(columns=[
            'S.No','grn_number','purchase_company','bill_number','bill_date','date','by_product_name','quantity','count','GST%','cgst_amount','sgst_amount','total_cost'])
            
            goods_receipt_purchase_df = goods_receipt_purchase_df.drop_duplicates(subset=['grn_number','by_product_name'], keep="first")

            goods_receipt_purchase_df = goods_receipt_purchase_df.rename(columns={'S.No': 'S.No','grn_number':'GRN No','purchase_company':'Purchase Company','bill_number':'Bill Number','bill_date':'Bill Date','date':'GRN Date','by_product_name':'Product Name','quantity' :'Product Quantity','count':'Product Count','GST%':'Product GST%','cgst_amount':'Product CGST Amount','sgst_amount':'Product SGST Amount','total_cost':'Product Total Amount'})
                
            goods_receipt_purchase_df['GRN Date'] = goods_receipt_purchase_df['GRN Date'].apply(lambda a: pd.to_datetime(a).date()) 
            goods_receipt_purchase_df['Bill Date'] = goods_receipt_purchase_df['Bill Date'].apply(lambda a: pd.to_datetime(a).date())    
                
            # total_purchase_company_check_box_list =  {'Purchase Company'}
            # # user_purchase_company_check_box_list = {'Product CGST Amount','Product SGST Amount','Product Total Amount'}
            # user_purchase_company_check_box_list = request.data['user_check_box_list']
            # purchase_company_check_box_list = total_purchase_company_check_box_list.difference(user_purchase_company_check_box_list)
            # goods_receipt_purchase_df.drop(purchase_company_check_box_list,inplace= True,axis = 1)
            goods_receipt_purchase_df=goods_receipt_purchase_df.set_index('S.No')
            goods_receipt_purchase_df = goods_receipt_purchase_df.append({'Product SGST Amount': 'TOTAL AMOUNT', 'Product Total Amount':goods_receipt_purchase_df['Product Total Amount'].sum()}, ignore_index = True)

            file_name = str(datetime.datetime.now().date()) + '_Purchase_Report.xlsx'
            file_path = os.path.join('static/media/by_product/daily_sale/', file_name)
            
            goods_receipt_purchase_df.to_excel(file_path)
            
            # print(file_name)

            data['file_name'] = file_name
            try:
                image_path = file_path
                with open(image_path, 'rb') as image_file:
                    encoded_image = b64encode(image_file.read())
                    data['excel'] = encoded_image
            except Exception as err:
                print(err)
            return Response(data=data, status=status.HTTP_200_OK)
                