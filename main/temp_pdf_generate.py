from collections import defaultdict, OrderedDict, Counter
from main.models import *
import pandas as pd
from decimal import Decimal
import datetime
from base64 import b64decode, b64encode
from django.db.models import Sum
from calendar import monthrange, month_name
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter, A4


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


def gatepass_data_for_temp_route(route_id, date, session_id, business_id):
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
    business_ids = [business_id]
    sale_group = SaleGroup.objects.filter(business_id__in=business_ids, date=date, session_id=session_id)
    sale_values = Sale.objects.filter(sale_group__in=sale_group,  product__is_active=True).values_list('product_id', 'count')
    sale_columns = ['product_id', 'count']
    sale_df = pd.DataFrame(list(sale_values), columns=sale_columns)

    icustomer_sale_group = ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=date.month,
                                                             date__year=date.year, session_id=session_id)
    icustomer_sale_values = ICustomerSale.objects.filter(icustomer_sale_group__in=icustomer_sale_group, product__is_active=True).values_list(
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
        milk_product_ids = list(Product.objects.filter(group_id__in=[1, 3], is_active=True).values_list('id', flat=True))
        curd_product_ids = list(Product.objects.filter(group_id__in=[2], is_active=True).values_list('id', flat=True))
        # find milk total and net total
        data['milk_total_count'] = merged_df[merged_df['id'].isin(milk_product_ids)]['count'].sum()
        data['net_total_count'] = merged_df['count'].sum()

        # find tray count and pocket count
        tray_config_values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id', 'tray_count', 'product_count')
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
            allowance_business_obj = BusinessWiseLeakageAllowanceAsPacket.objects.filter( product__is_active=True,
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
        df_without_cup_curd = curd_df[(curd_df['id'] != 10) & (curd_df['id'] != 26) & (curd_df['id'] != 28)]
        data['total_curd_tray_count'] = df_without_cup_curd['calculated_tray_count'].sum()
        data['total_curd_packet_count'] = curd_df['calculated_pocket_count'].sum()
        data['total_curd_packet_count_in_negative'] = curd_df['calculated_pocket_count_in_negative'].sum()
        data['total_curd_leak_packet_count'] = curd_df['leak_packet'].sum()
        data['total_curd_litre_count'] = curd_df['litre'].sum()

        other_df = tray_config_merge_df[~tray_config_merge_df['id'].isin(milk_product_ids)]
        other_df = other_df.fillna(0)
        data['other'] = other_df.groupby('id').apply(lambda x: x.to_dict('r')[0]).to_dict()
    return data


def route_wise_business_data(route_id, session_id, selected_date, buiness_id):
    route_id = route_id
    session_id = session_id
    selected_date = selected_date
    selected_month = selected_date.month
    selected_year = selected_date.year
    business_ids = [buiness_id]
    sales_values = Sale.objects.filter(sale_group__business_id__in=business_ids, sale_group__session_id=session_id, product__is_active=True,
                                       sale_group__date=selected_date).values_list('id', 'sale_group_id', 'count',
                                                                                   'cost', 'product_id',
                                                                                   'product__name',
                                                                                   'sale_group__session_id',
                                                                                   'sale_group__business_id',
                                                                                   'sale_group__business__business_type_id',
                                                                                   'sale_group__business__business_type__name')
    sales_column = ['id', 'sale_group_id', 'count', 'cost', 'product_id', 'product_name', 'session_id', 'business_id',
                    'business_type_id', 'business_type']
    sales_df = pd.DataFrame(list(sales_values), columns=sales_column)

    # serve customer order based on the business ids
    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=selected_month,
                                                      icustomer_sale_group__date__year=selected_year,product__is_active=True,
                                                      icustomer_sale_group__business_id__in=business_ids,
                                                      icustomer_sale_group__session_id=session_id)
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
    for product in products:
        route_wise_data['total'][product.id] = final_df[final_df['product_id'] == product.id].sum()['count']
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

    return route_wise_data


def get_business_ids(route_id, session_id, date):
    # return ordered_business
    business_ids = list(RouteBusinessMap.objects.filter(route_id=route_id).values_list('business_id', flat=True))
    ordered_business = list(
        SaleGroup.objects.filter(business_id__in=business_ids, date=date, session_id=session_id).values_list(
            'business_id', flat=True))
    selected_date = date
    ordered_business_for_icustomer = list(
        ICustomerSaleGroup.objects.filter(business_id__in=business_ids, date__month=selected_date.month,
                                          date__year=selected_date.year, session_id=session_id).values_list(
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


def find_packet_count_for_indivioul_business(agent_count, icustomer_count, product_defalut_count, product_id):
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
    tray_config_values = ProductTrayConfig.objects.filter(product__is_active=True).values_list('product_id', 'tray_count', 'product_count')
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
    sales_values = Sale.objects.filter(sale_group__in=sale_group,  product__is_active=True).values_list('sale_group', 'product_id', 'count')
    sales_columns = ['sale_group_id', 'product_id', 'count']
    sale_df = pd.DataFrame(list(sales_values), columns=sales_columns)
    sale_df = sale_df.fillna(0)
    data['total_cost'] = sale_group.aggregate(Sum('total_cost'))['total_cost__sum']
    final_df = pd.merge(sale_df, product_tray_merge_df, how='left', left_on='product_id', right_on='id')
    final_df = final_df.fillna(0)
    business_df = final_df

    icustomer_sale_obj = ICustomerSale.objects.filter(icustomer_sale_group__date__month=month,
                                                      icustomer_sale_group__date__year=year,
                                                      icustomer_sale_group__session_id=session_id,product__is_active=True,
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
    return data


def generate_pdf_for_temp_route(route_id, session_id, date):
    business_ids = get_business_ids(route_id, session_id, date)
    route_trace_obj = RouteTrace.objects.get(route_id=route_id, session_id=session_id, date=date)
    route_trace_sale_summary_obj = RouteTraceWiseSaleSummary.objects.filter(route_trace__route__is_temp_route=True)
    
    print(business_ids)
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
    file_path = os.path.join('static/media/indent_document/' + str(date) + '/' + session + '/' + str(route_id) + '/',
                             file_name)
    mycanvas = canvas.Canvas(file_path, pagesize=A4)

    #     #     -------------------------first page -------------------
    for temp_route_index, business in enumerate(business_ids, start=1):
        data = gatepass_data_for_temp_route(route_id, date, session_id, business)
        for product in Product.objects.filter(is_active=True):
            if product.id in data['sales'].keys():
                if route_trace_sale_summary_obj.filter(route_trace_id=route_trace_obj.id, product=product).exists():
                    temp_route_trace_sale_summary_obj = route_trace_sale_summary_obj.get(route_trace_id=route_trace_obj.id, product=product)                                            
                    temp_route_trace_sale_summary_obj.quantity += data['sales'][product.id]['quantity']
                    temp_route_trace_sale_summary_obj.tray_count += data['sales'][product.id]['calculated_tray_count']
                    temp_route_trace_sale_summary_obj.loose_packet_count += data['sales'][product.id]['calculated_pocket_count']
                    temp_route_trace_sale_summary_obj.leak_packet_count += data['sales'][product.id]['leak_packet']
                    
                else:
                    temp_route_trace_sale_summary_obj = RouteTraceWiseSaleSummary(quantity=data['sales'][product.id]['quantity'], product_id=product.id, 
                                                                                    route_trace_id=route_trace_obj.id, 
                                                                                    tray_count=data['sales'][product.id]['calculated_tray_count'],
                                                                                    loose_packet_count=data['sales'][product.id]['calculated_pocket_count'], 
                                                                                    leak_packet_count=data['sales'][product.id]['leak_packet'])
                temp_route_trace_sale_summary_obj.save()


        business_code = Business.objects.get(id=business).code
        
        prod_ids = data['milk'].keys()

        if 'curd' in data:
            curd_ids = data['curd'].keys()
        else:
            curd_ids = []
        y_axis = 0
        y_for_table2 = 10
        new_y_axis = 0
        loose_milk_ids = [22, 23, 24]
        last_count_for_gate_pass = IndentCodeBank.objects.get(code_for='gate_pass')
        serial_number = int(last_count_for_gate_pass.last_code) + 1
        if serial_number == 999999:
            last_count_for_gate_pass.last_code = 0
        else:
            last_count_for_gate_pass.last_code = serial_number
        last_count_for_gate_pass.save()
       
        x_adjust = 15
        for i in range(2):
            net_total_count = 0
            net_total_tray_count = 0
            net_total_packet_positive_count = 0
            net_total_packet_negative_count = 0
            net_total_packet_negative_count = 0
            net_total_leak_packet_count = 0
            if not i == 0:
                y_for_table2 = y_axis - 110

            mycanvas.setStrokeColor(colors.lightgrey)

            route_supervisor = data['route_supervisor']
            route_date = datetime.datetime.strftime(data['date'], '%d-%m-%Y')
            session_name = data['session']
            route_name = data['route_name']
            vehicle_number = data['vehicle_number']
            mycanvas.setStrokeColor(colors.lightgrey)
            mycanvas.setFont('Helvetica', 12.6)
            mycanvas.drawString(10, 820 - y_for_table2,
                                       'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 12)

            mycanvas.drawCentredString(300, 800 - y_for_table2, 'DAIRY GATEPASS FOR MILK')
            mycanvas.setFont('Helvetica', 12)
            mycanvas.line(200, 795 - y_for_table2, 390, 795 - y_for_table2)

            # row 1
            mycanvas.drawCentredString(290, 775 - y_for_table2, 'S.NO.' + ' ' + ':' + ' ' + str(serial_number) + "  |  "+'DATE ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name) +"  |  "+'ROUTE ' + ' ' + ':' + ' ' + str(route_name) + '(' + str(business_code)+ ") |  "+'VEHICLE ' + ' ' + ':' + ' ' + str(vehicle_number))
            y_for_table2 -= 20
            # ------------table header----------
            mycanvas.line(10+ x_adjust, 725 - y_for_table2, 555+ x_adjust, 725 - y_for_table2)
            mycanvas.setFont('Helvetica', 13)
            mycanvas.line(10+ x_adjust, 685 - y_for_table2+15, 555+ x_adjust, 685 - y_for_table2+15)

            # ----------table heading-----------
            # sl.no
            mycanvas.drawString(20+ x_adjust, 698 - y_for_table2+10, 'S.No')
            mycanvas.drawString(100+ x_adjust, 698 - y_for_table2+10, 'Products')
            mycanvas.drawString(180+ x_adjust, 698 - y_for_table2+10, 'Packet')

            mycanvas.drawString(235+ x_adjust, 698 - y_for_table2+10, 'Tray/can')

            mycanvas.drawString(300+ x_adjust, 698 - y_for_table2+10, 'Pkt(+)')
            mycanvas.drawString(360+ x_adjust, 698 - y_for_table2+10, 'Pkt(-)')

            mycanvas.drawString(420+ x_adjust, 698 - y_for_table2+10, 'Leak')

            mycanvas.drawString(480+ x_adjust, 698 - y_for_table2+10, 'Qty (Ltr)')


            # horizontal lines
            y_axis = 680 - y_for_table2
            end_axis = 648 - y_for_table2
            last_index = 0
            mycanvas.setFont('Helvetica', 12)
            for index, prod_id in enumerate(prod_ids, start=1):
                # sl.no
                mycanvas.drawString(30+ x_adjust, y_axis, str(index))
                # item particulars data
                mycanvas.drawString(95+ x_adjust, y_axis, str(data['milk'][prod_id]['product_short_name']))
                if not prod_id in loose_milk_ids:
                    mycanvas.drawRightString(220+ x_adjust, y_axis, str(data['milk'][prod_id]['count']))
                else:
                    mycanvas.drawRightString(220+ x_adjust, y_axis, str(str(data['milk'][prod_id]['count']) + 'L'))
                # tray data
                if not data['milk'][prod_id]['calculated_tray_count'] == 0:
                    mycanvas.drawRightString(280+ x_adjust, y_axis, str(data['milk'][prod_id]['calculated_tray_count']))
                # pkt
                if not data['milk'][prod_id]['calculated_pocket_count'] == 0:
                    mycanvas.drawRightString(335 + x_adjust, y_axis, str(data['milk'][prod_id]['calculated_pocket_count']))
                if not data['milk'][prod_id]['calculated_pocket_count_in_negative'] == 0:
                    mycanvas.drawRightString(380 + x_adjust, y_axis, str(-data['milk'][prod_id]['calculated_pocket_count_in_negative']))
                # leak pkt  
                if not data['milk'][prod_id]['leak_packet'] == 0:
                    mycanvas.drawRightString(425 + x_adjust, y_axis, str(data['milk'][prod_id]['leak_packet']))
                # qty of milk
                mycanvas.drawRightString(540 + x_adjust, y_axis, str(data['milk'][prod_id]['litre']))
                last_index = index

                y_axis -= 15
                end_axis -= 15

            # After Milk entry line
            mycanvas.line(10 + x_adjust, int(y_axis + 12), 555 + x_adjust, int(y_axis + 12))
            mycanvas.setFont('Helvetica', 13)
            mycanvas.drawString(95 + x_adjust, y_axis - 3, 'Milk Total')

            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawRightString(220 + x_adjust, y_axis - 3, str(int(data['milk_total_count'])))
            if not data['total_milk_tray_count'] == 0:
                mycanvas.drawRightString(280 + x_adjust, y_axis - 3, str(data['total_milk_tray_count']))
            if not data['total_milk_packet_count'] == 0:
                mycanvas.drawRightString(335 + x_adjust, y_axis - 3, str(data['total_milk_packet_count']))
            if not data['total_milk_packet_count_in_negative'] == 0:
                mycanvas.drawRightString(380 + x_adjust, y_axis - 3, str(-data['total_milk_packet_count_in_negative']))
            if not data['total_milk_leak_packet_count'] == 0:
                mycanvas.drawRightString(455 + x_adjust, y_axis - 3, str(data['total_milk_leak_packet_count']))
            mycanvas.drawRightString(540 + x_adjust, y_axis - 3, str(data['total_milk_litre_count']))

            # After Milk total line
            mycanvas.line(10 + x_adjust, int(y_axis - 10), 555+15, int(y_axis - 10))

            y_axis -= 20
            mycanvas.setFont('Helvetica', 12)
            if data['total_curd_product_count'] != 0:
                for c_index, curd_id in enumerate(curd_ids, start=last_index):
                    mycanvas.drawString(30 + x_adjust, y_axis - 10, str(c_index + 1))
                    mycanvas.drawString(95 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['product_short_name']))
                    mycanvas.drawRightString(220 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['count']))
                    if not data['curd'][curd_id]['calculated_tray_count'] == 0:
                        mycanvas.drawRightString(280 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['calculated_tray_count']))
                    if not data['curd'][curd_id]['calculated_pocket_count'] == 0:
                        mycanvas.drawRightString(335 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['calculated_pocket_count']))
                    if not data['curd'][curd_id]['calculated_pocket_count_in_negative'] == 0:
                        mycanvas.drawRightString(380 + x_adjust, y_axis - 10,
                                            str(-data['curd'][curd_id]['calculated_pocket_count_in_negative']))
                    if not data['curd'][curd_id]['leak_packet'] == 0:
                        mycanvas.drawRightString(425 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['leak_packet']))

                    mycanvas.drawRightString(540 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['litre']))
                    y_axis -= 15
                    end_axis -= 10

                mycanvas.setFont('Helvetica', 12)
                # Above Curd total
                mycanvas.line(10 + x_adjust, int(y_axis), 555+15, int(y_axis + 3))
                #     y_axis -= 20
                #     end_axis -= 15
                mycanvas.drawString(95 + x_adjust, int(y_axis) - 15, str('Curd Total'))
                mycanvas.drawRightString(220 + x_adjust, int(y_axis) - 15, str(data['total_curd_product_count']))
                if not data['total_curd_tray_count'] == 0:
                    mycanvas.drawRightString(280 + x_adjust, int(y_axis) - 15, str(data['total_curd_tray_count']))
                if not data['total_curd_packet_count'] == 0:
                    mycanvas.drawRightString(335 + x_adjust, int(y_axis) - 15, str(data['total_curd_packet_count']))
                if not data['total_curd_packet_count_in_negative'] == 0:
                    mycanvas.drawRightString(380 + x_adjust, y_axis - 15, str(-data['total_curd_packet_count_in_negative']))
                if not data['total_curd_leak_packet_count'] == 0:
                    mycanvas.drawRightString(425 + x_adjust, int(y_axis) - 15, str(data['total_curd_leak_packet_count']))

                mycanvas.drawRightString(540 + x_adjust, int(y_axis) - 15, str(data['total_curd_litre_count']))

                end_axis = end_axis - 40
                # --------lines--------
                # end line
                mycanvas.line(10 + x_adjust, int(end_axis + 5)+15, 555 + x_adjust, int(end_axis + 5)+15)

            # Net total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(95 + x_adjust, int(end_axis) , str('Net Total'))
            net_total_count = data['milk_total_count'] + data['total_curd_product_count']
            mycanvas.drawRightString(220 + x_adjust, int(end_axis) , str(int(net_total_count)))
            net_total_tray_count = data['total_milk_tray_count'] + data['total_curd_tray_count']
            mycanvas.drawRightString(280 + x_adjust, int(end_axis) , str(net_total_tray_count))
            net_total_packet_positive_count = data['total_milk_packet_count'] + data['total_curd_packet_count']
            mycanvas.drawRightString(335 + x_adjust, int(end_axis) , str(net_total_packet_positive_count))
            net_total_packet_negative_count = data['total_milk_packet_count_in_negative'] + data[
                'total_curd_packet_count_in_negative']
            mycanvas.drawRightString(380 + x_adjust, int(end_axis) , str(-net_total_packet_negative_count))
            net_total_leak_packet_count = data['total_milk_leak_packet_count'] + data['total_curd_leak_packet_count']

            if not net_total_leak_packet_count == 0:
                mycanvas.drawRightString(425 + x_adjust, int(end_axis), str(net_total_leak_packet_count))
            net_total_litre = data['total_milk_litre_count'] + data['total_curd_litre_count']
            mycanvas.drawRightString(540 + x_adjust, int(end_axis), str(net_total_litre))

            mycanvas.line(10 + x_adjust, int(end_axis - 22)+15, 555 + x_adjust, int(end_axis - 22)+15)

            # right and left border
            mycanvas.line(10 + x_adjust, 715 - y_for_table2+10, 10 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(555 + x_adjust, 715 - y_for_table2+10, 555 + x_adjust, int(end_axis - 22)+15)

            # data borders
            mycanvas.line(60 + x_adjust, 715 - y_for_table2+10, 60 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(170 + x_adjust, 715 - y_for_table2+10, 170 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(230 + x_adjust, 715 - y_for_table2+10, 230 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(290 + x_adjust, 695 - y_for_table2+30, 290 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(343 + x_adjust, 695 - y_for_table2+30, 343 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(405 + x_adjust, 715 - y_for_table2+10, 405 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(460 + x_adjust, 715 - y_for_table2+10, 460 + x_adjust, int(end_axis - 22)+15)

            mycanvas.setFont('Helvetica', 13)
            y_axis = y_axis - 40
            mycanvas.drawString(10 + x_adjust, int(end_axis - 55)+10, str('Dist.Assistant/M.M.O.'))
            mycanvas.drawString(210 + x_adjust, int(end_axis - 55)+10, str('Counting Officer'))
            mycanvas.drawString(450 + x_adjust, int(end_axis - 55)+10, str('Route Supervisor'))
            test = end_axis - 25

            # if i == 0:
            #     mycanvas.setDash(4,2)
            #     mycanvas.line(5,y_axis-120,600,y_axis-120)
            #     mycanvas.setDash(10,0)

    #         if not i == 1:
    #             if test < 600:
    #                 mycanvas.showPage()
        new_y_axis = y_axis

        #    -------------------------second page -------------------
        route_wise_data = route_wise_business_data(route_id, session_id, date,business)
        mycanvas.showPage()
        #     mycanvas.setLineWidth(0)
        mycanvas.setStrokeColor(colors.lightgrey)
        # HEADER
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(20, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 785, 'ROUTEWISE MILK DISTRIBUTION STATEMENT')
        mycanvas.line(170, 782, 410, 782)
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
        mycanvas.drawCentredString(290, 760, 'No.' + ' ' + ':' + ' ' + str(indent_number) +"  |  "+'Route ' + ' ' + ':' + ' ' + str(route_name) + '(' + str(business_code)+ ") |  " + 'Vehicle ' + ' ' + ':' + ' ' + str(vehicle_number) +"  |  "+'Date ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name))

        x_ad = 4
        # # ----------table heading-----------
        mycanvas.setFont('Helvetica', 9)
        mycanvas.drawString(10-x_ad, 665+60, 'S.No')
        mycanvas.drawString(35-x_ad, 665+60, 'Booth')
        mycanvas.drawString(70-x_ad, 665+60, 'Agent')
        mycanvas.drawString(110-x_ad, 665+60,'Type')
        # product name on heading
        product_x_axis = 133
        line_product_x_axis = 144
        products = Product.objects.filter(is_active=True).order_by('display_ordinal')
        for product in products:
            # product short name
            if product.short_name == 'CBUK' or product.short_name == 'FMcan' or product.short_name == 'SMcan':
                mycanvas.drawString(product_x_axis-x_ad, 665+60, str(product.short_name[:6]))
            else:
                mycanvas.drawString(product_x_axis+9-x_ad, 670+60, str(product.short_name[:-4]))
                mycanvas.drawString(product_x_axis+9-x_ad, 660+60, str(product.short_name[-4:]))


            #     mycanvas.line(line_product_x_axis, 68, line_product_x_axis, 100)
            product_x_axis += 36
            line_product_x_axis += 38

        # ------------table header----------
        # table head up line
        mycanvas.line(10-x_ad, 680+60, product_x_axis -6, 680+60)
        # table head bottom line
        mycanvas.line(10-x_ad, 655+60, product_x_axis - 6, 655+60)

        y_data = 630+60
        #     value_axis = 30
        line_product_x_axis = 165
        serial_number = 1
        page_number = 1
        booth_types = route_wise_data['booth_types'].keys()
        for booth_type_index, booth_type in enumerate(booth_types, start=1):
            for booth_index, business in enumerate(route_wise_data['booth_types'][booth_type]['booth_ids'], start=1):
                value_axis = 162
                mycanvas.setFont('Helvetica', 10)
                mycanvas.drawString(12-x_ad, y_data, str(serial_number))
                mycanvas.drawString(37-x_ad, y_data,
                                    str(route_wise_data['booth_types'][booth_type][business]['business_code']))
                mycanvas.setFont('Helvetica', 10)
                mycanvas.drawString(65-x_ad, y_data,
                                    str(route_wise_data['booth_types'][booth_type][business]['agent_name'][:5]).lower())
                mycanvas.setFont('Helvetica', 10)

                booth = BusinessType.objects.get(id=booth_type).name
                booth_srt = ''
                if booth == 'Booth':
                    booth_srt = 'BO'
                if booth == 'Parlour' or booth == "Own parlour":
                    booth_srt = "UNI"
                if booth == 'Private Institute' or booth == 'Govt Institute':
                    booth_srt = "INS"
                if booth == "Other unions":
                    booth_srt = "O-UNI"
                if booth == "Other State":
                    booth_srt = "O-ST"
                mycanvas.drawCentredString(117-x_ad, y_data-5, str(booth_srt))
                mycanvas.setFont('Helvetica', 10)

                for product in products:
                    if product.id in route_wise_data['booth_types'][booth_type][business]['product']:
                        mycanvas.drawRightString(value_axis-x_ad, y_data, str(
                            int(route_wise_data['booth_types'][booth_type][business]['product'][product.id])))
                    value_axis = value_axis + 36
                y_data -= 25
                value_axis = 160
                mycanvas.line(line_product_x_axis-x_ad, 300, line_product_x_axis-x_ad, 300)
                line_product_x_axis += 35


                if serial_number % 25 == 0:
                    page_number += 1
                    mycanvas.line(2, 680+60, 3, y_data)
                    mycanvas.line(29, 680+60, 29, y_data)
                    mycanvas.line(59, 680+60, 59, y_data)
                    mycanvas.line(93, 680+60, 93, y_data)
                    x_data = 132

                    for product in products:
                        # line after short name of the product
                        mycanvas.line(x_data-x_ad, 680+60, x_data, y_data)
                        x_data += 36

                    # line after 1st page
                    mycanvas.line(10, y_data, x_data, y_data)

                    # neext
                    mycanvas.showPage()
                    mycanvas.setStrokeColor(colors.lightgrey)

                    # HEADER
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawString(20, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(300, 785, 'ROUTEWISE MILK DISTRIBUTION STATEMENT')
                    mycanvas.line(170, 782, 410, 782)
                    # basic head
                    # row 1
                    indent_number = 8468
                    page_number = page_number
                    route_name = route_wise_data['route_name']
                    vehicle_number = route_wise_data['vehicle_number']

                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(290, 760, 'No.' + ' ' + ':' + ' ' + str(indent_number) +"  |  "+'Route ' + ' ' + ':' + ' ' + str(route_name) + "  |  " + 'Vehicle ' + ' ' + ':' + ' ' + str(vehicle_number) +"  |  "+'Date ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name))

                    x_ad = 4
                    # # ----------table heading-----------
                    mycanvas.setFont('Helvetica', 9)
                    mycanvas.drawString(10-x_ad, 665+60, 'S.No')
                    mycanvas.drawString(35-x_ad, 665+60, 'Booth')
                    mycanvas.drawString(70-x_ad, 665+60, 'Agent')
                    mycanvas.drawString(110-x_ad, 665+60,'Type')
                    # product name on heading
                    product_x_axis = 133
                    line_product_x_axis = 144
                    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
                    for product in products:
                        # product short name
                        if product.short_name == 'CBUK' or product.short_name == 'FMcan' or product.short_name == 'SMcan':
                            mycanvas.drawString(product_x_axis-x_ad, 665+60, str(product.short_name[:6]))
                        else:
                            mycanvas.drawString(product_x_axis+9-x_ad, 670+60, str(product.short_name[:-4]))
                            mycanvas.drawString(product_x_axis+9-x_ad, 660+60, str(product.short_name[-4:]))


                        #     mycanvas.line(line_product_x_axis, 68, line_product_x_axis, 100)
                        product_x_axis += 36
                        line_product_x_axis += 38

                    # ------------table header----------
                    # table head up line
                    mycanvas.line(10-x_ad, 680+60, product_x_axis -6, 680+60)
                    # table head bottom line
                    mycanvas.line(10-x_ad, 655+60, product_x_axis - 6, 655+60)
                    #  next
                    y_data = 645 + 60
                    value_axis = 162
    #                 line_product_x_axis = 165

                serial_number += 1

        # bottom border
        y_data -= 25
        mycanvas.line(10-x_ad, y_data, product_x_axis - 6, y_data)
        mycanvas.line(10-x_ad, y_data + 25, product_x_axis - 6, y_data + 25)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(10-x_ad, y_data + 11, str('Grand Total'))
        mycanvas.setFont('Helvetica', 10)
        value_axis = 162

        for product in products:
            if not route_wise_data['total'][product.id] == 0:
                mycanvas.drawRightString(value_axis-x_ad, y_data + 11, str(int(route_wise_data['total'][product.id])))
            value_axis = value_axis + 36

    # lines after products
        x_axis_data = 166
        for product in products:
            mycanvas.line(x_axis_data-x_ad, 680+60, x_axis_data-x_ad, y_data)
            if product == products[0]:
                mycanvas.line(x_axis_data-33-x_ad, 680+60, x_axis_data-33-x_ad, y_data)  
            x_axis_data += 36
        mycanvas.line(5-x_ad, 680+60, 5-x_ad, y_data)
        mycanvas.line(34-x_ad, 680+60, 34-x_ad, y_data+25)
        mycanvas.line(64-x_ad, 680+60, 64-x_ad, y_data+25)
        mycanvas.line(99-x_ad, 680+60, 99-x_ad, y_data)

        #     tray and extra pocket
        y_data = y_data - 25

        mycanvas.drawString(450, y_data-30, str('Route Supervisor'))
       
       
       
 
        #         Third page section
       
        business_data = get_individual_business_data(business, session_id, date)
        last_count_for_business_bill = IndentCodeBank.objects.get(code_for='business_bill')
        bill_number = int(last_count_for_business_bill.last_code) + 1
        if bill_number == 999999:
            last_count_for_business_bill.last_code = 0
        else:
            last_count_for_business_bill.last_code = bill_number
        last_count_for_business_bill.save()
        x_new = 50
        third_y = 400
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(110 + x_new, third_y + 5, str('DCMPU-CBE Delivery Note'))
        mycanvas.setFont('Helvetica', 10)
        mycanvas.drawString(x_new - 40, third_y - 25, str(business_data['route_name']) +"  |  "+str('No' + ':' + str(bill_number)+"  |  "+ str(route_date + '/' + business_data['session'])))
        key_id = list(business_data['sales'].keys())

        mycanvas.drawString(x_new - 40, third_y - 45, str('Booth: ')+str(' ' + business_data['business_code'])+"  |  "+str(business_data['agent_first_name'] + ' ' + business_data['agent_last_name'] + '[' + business_data['agent_code'] + ']'))

        mycanvas.setFont('Helvetica', 10)
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
#         mycanvas.setFont('Helvetica', 12)
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
#         mycanvas.setFont('Helvetica', 10)
        mycanvas.drawString(x_new - 35, product_axis - 15, str('Milk(Cash Sales)Rs.'))
        mycanvas.drawString(150 + x_new, product_axis - 15, str(business_data['total_cost']))
        mycanvas.line(x_new - 40, product_axis - 20, 300 + x_new-55, product_axis - 20)

        mycanvas.drawString(100 + x_new, product_axis - 40, str('Receiver\'s Signature'))
        mycanvas.showPage()

    mycanvas.save()
    document = {'pdf_data': {}}
    try:
        image_path = file_path
        with open(image_path, 'rb') as image_file:
            encoded_image = b64encode(image_file.read())
            document['pdf_data']['pdf'] = encoded_image
            document['pdf_data']['path'] = image_path
    except Exception as err:
        print(err)
    return document


def generate_pdf_for_merging_temp_with_main(route_id, session_id, date, mycanvas):
    business_ids = get_business_ids(route_id, session_id, date)
    new_date = datetime.datetime.strftime(date, '%d-%b-%Y')
    directory = 'new'
    session = 'Morning'
    if session_id == 2:
        session = 'Evening'
    mycanvas.showPage()
    #     #     -------------------------first page -------------------
    for temp_route_index, business in enumerate(business_ids, start=1):
        data = gatepass_data_for_temp_route(route_id, date, session_id, business)
        business_code = Business.objects.get(id=business).code
        
        prod_ids = data['milk'].keys()

        if 'curd' in data:
            curd_ids = data['curd'].keys()
        else:
            curd_ids = []
        y_axis = 0
        y_for_table2 = 10
        new_y_axis = 0
        loose_milk_ids = [22, 23, 24]
        last_count_for_gate_pass = IndentCodeBank.objects.get(code_for='gate_pass')
        serial_number = int(last_count_for_gate_pass.last_code) + 1
        if serial_number == 999999:
            last_count_for_gate_pass.last_code = 0
        else:
            last_count_for_gate_pass.last_code = serial_number
        last_count_for_gate_pass.save()
       
        x_adjust = 15
        for i in range(2):
            net_total_count = 0
            net_total_tray_count = 0
            net_total_packet_positive_count = 0
            net_total_packet_negative_count = 0
            net_total_packet_negative_count = 0
            net_total_leak_packet_count = 0
            if not i == 0:
                y_for_table2 = y_axis - 110

            mycanvas.setStrokeColor(colors.lightgrey)

            route_supervisor = data['route_supervisor']
            route_date = datetime.datetime.strftime(data['date'], '%d-%m-%Y')
            session_name = data['session']
            route_name = data['route_name']
            vehicle_number = data['vehicle_number']
            mycanvas.setStrokeColor(colors.lightgrey)
            mycanvas.setFont('Helvetica', 12.6)
            mycanvas.drawString(10, 820 - y_for_table2,
                                       'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
            mycanvas.setFont('Helvetica', 12)

            mycanvas.drawCentredString(300, 800 - y_for_table2, 'DAIRY GATEPASS FOR MILK')
            mycanvas.setFont('Helvetica', 12)
            mycanvas.line(200, 795 - y_for_table2, 390, 795 - y_for_table2)

            # row 1
            mycanvas.drawCentredString(290, 775 - y_for_table2, 'S.NO.' + ' ' + ':' + ' ' + str(serial_number) + "  |  "+'DATE ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name) +"  |  "+'ROUTE ' + ' ' + ':' + ' ' + str(route_name) + '(' + str(business_code)+ ") |  "+'VEHICLE ' + ' ' + ':' + ' ' + str(vehicle_number))
            y_for_table2 -= 20
            # ------------table header----------
            mycanvas.line(10+ x_adjust, 725 - y_for_table2, 555+ x_adjust, 725 - y_for_table2)
            mycanvas.setFont('Helvetica', 13)
            mycanvas.line(10+ x_adjust, 685 - y_for_table2+15, 555+ x_adjust, 685 - y_for_table2+15)

            # ----------table heading-----------
            # sl.no
            mycanvas.drawString(20+ x_adjust, 698 - y_for_table2+10, 'S.No')
            mycanvas.drawString(100+ x_adjust, 698 - y_for_table2+10, 'Products')
            mycanvas.drawString(180+ x_adjust, 698 - y_for_table2+10, 'Packet')

            mycanvas.drawString(235+ x_adjust, 698 - y_for_table2+10, 'Tray/can')

            mycanvas.drawString(300+ x_adjust, 698 - y_for_table2+10, 'Pkt(+)')
            mycanvas.drawString(360+ x_adjust, 698 - y_for_table2+10, 'Pkt(-)')

            mycanvas.drawString(420+ x_adjust, 698 - y_for_table2+10, 'Leak')

            mycanvas.drawString(480+ x_adjust, 698 - y_for_table2+10, 'Qty (Ltr)')


            # horizontal lines
            y_axis = 680 - y_for_table2
            end_axis = 648 - y_for_table2
            last_index = 0
            mycanvas.setFont('Helvetica', 12)
            for index, prod_id in enumerate(prod_ids, start=1):
                # sl.no
                mycanvas.drawString(30+ x_adjust, y_axis, str(index))
                # item particulars data
                mycanvas.drawString(95+ x_adjust, y_axis, str(data['milk'][prod_id]['product_short_name']))
                if not prod_id in loose_milk_ids:
                    mycanvas.drawRightString(220+ x_adjust, y_axis, str(data['milk'][prod_id]['count']))
                else:
                    mycanvas.drawRightString(220+ x_adjust, y_axis, str(str(data['milk'][prod_id]['count']) + 'L'))
                # tray data
                if not data['milk'][prod_id]['calculated_tray_count'] == 0:
                    mycanvas.drawRightString(280+ x_adjust, y_axis, str(data['milk'][prod_id]['calculated_tray_count']))
                # pkt
                if not data['milk'][prod_id]['calculated_pocket_count'] == 0:
                    mycanvas.drawRightString(335 + x_adjust, y_axis, str(data['milk'][prod_id]['calculated_pocket_count']))
                if not data['milk'][prod_id]['calculated_pocket_count_in_negative'] == 0:
                    mycanvas.drawRightString(380 + x_adjust, y_axis, str(-data['milk'][prod_id]['calculated_pocket_count_in_negative']))
                # leak pkt  
                if not data['milk'][prod_id]['leak_packet'] == 0:
                    mycanvas.drawRightString(425 + x_adjust, y_axis, str(data['milk'][prod_id]['leak_packet']))
                # qty of milk
                mycanvas.drawRightString(540 + x_adjust, y_axis, str(data['milk'][prod_id]['litre']))
                last_index = index

                y_axis -= 15
                end_axis -= 15

            # After Milk entry line
            mycanvas.line(10 + x_adjust, int(y_axis + 12), 555 + x_adjust, int(y_axis + 12))
            mycanvas.setFont('Helvetica', 13)
            mycanvas.drawString(95 + x_adjust, y_axis - 3, 'Milk Total')

            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawRightString(220 + x_adjust, y_axis - 3, str(int(data['milk_total_count'])))
            if not data['total_milk_tray_count'] == 0:
                mycanvas.drawRightString(280 + x_adjust, y_axis - 3, str(data['total_milk_tray_count']))
            if not data['total_milk_packet_count'] == 0:
                mycanvas.drawRightString(335 + x_adjust, y_axis - 3, str(data['total_milk_packet_count']))
            if not data['total_milk_packet_count_in_negative'] == 0:
                mycanvas.drawRightString(380 + x_adjust, y_axis - 3, str(-data['total_milk_packet_count_in_negative']))
            if not data['total_milk_leak_packet_count'] == 0:
                mycanvas.drawRightString(455 + x_adjust, y_axis - 3, str(data['total_milk_leak_packet_count']))
            mycanvas.drawRightString(540 + x_adjust, y_axis - 3, str(data['total_milk_litre_count']))

            # After Milk total line
            mycanvas.line(10 + x_adjust, int(y_axis - 10), 555+15, int(y_axis - 10))

            y_axis -= 20
            mycanvas.setFont('Helvetica', 12)
            if data['total_curd_product_count'] != 0:
                for c_index, curd_id in enumerate(curd_ids, start=last_index):
                    mycanvas.drawString(30 + x_adjust, y_axis - 10, str(c_index + 1))
                    mycanvas.drawString(95 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['product_short_name']))
                    mycanvas.drawRightString(220 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['count']))
                    if not data['curd'][curd_id]['calculated_tray_count'] == 0:
                        mycanvas.drawRightString(280 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['calculated_tray_count']))
                    if not data['curd'][curd_id]['calculated_pocket_count'] == 0:
                        mycanvas.drawRightString(335 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['calculated_pocket_count']))
                    if not data['curd'][curd_id]['calculated_pocket_count_in_negative'] == 0:
                        mycanvas.drawRightString(380 + x_adjust, y_axis - 10,
                                            str(-data['curd'][curd_id]['calculated_pocket_count_in_negative']))
                    if not data['curd'][curd_id]['leak_packet'] == 0:
                        mycanvas.drawRightString(425 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['leak_packet']))

                    mycanvas.drawRightString(540 + x_adjust, y_axis - 10, str(data['curd'][curd_id]['litre']))
                    y_axis -= 15
                    end_axis -= 10

                mycanvas.setFont('Helvetica', 12)
                # Above Curd total
                mycanvas.line(10 + x_adjust, int(y_axis), 555+15, int(y_axis + 3))
                #     y_axis -= 20
                #     end_axis -= 15
                mycanvas.drawString(95 + x_adjust, int(y_axis) - 15, str('Curd Total'))
                mycanvas.drawRightString(220 + x_adjust, int(y_axis) - 15, str(data['total_curd_product_count']))
                if not data['total_curd_tray_count'] == 0:
                    mycanvas.drawRightString(280 + x_adjust, int(y_axis) - 15, str(data['total_curd_tray_count']))
                if not data['total_curd_packet_count'] == 0:
                    mycanvas.drawRightString(335 + x_adjust, int(y_axis) - 15, str(data['total_curd_packet_count']))
                if not data['total_curd_packet_count_in_negative'] == 0:
                    mycanvas.drawRightString(380 + x_adjust, y_axis - 15, str(-data['total_curd_packet_count_in_negative']))
                if not data['total_curd_leak_packet_count'] == 0:
                    mycanvas.drawRightString(425 + x_adjust, int(y_axis) - 15, str(data['total_curd_leak_packet_count']))

                mycanvas.drawRightString(540 + x_adjust, int(y_axis) - 15, str(data['total_curd_litre_count']))

                end_axis = end_axis - 40
                # --------lines--------
                # end line
                mycanvas.line(10 + x_adjust, int(end_axis + 5)+15, 555 + x_adjust, int(end_axis + 5)+15)

            # Net total
            mycanvas.setFont('Helvetica', 12)
            mycanvas.drawString(95 + x_adjust, int(end_axis) , str('Net Total'))
            net_total_count = data['milk_total_count'] + data['total_curd_product_count']
            mycanvas.drawRightString(220 + x_adjust, int(end_axis) , str(int(net_total_count)))
            net_total_tray_count = data['total_milk_tray_count'] + data['total_curd_tray_count']
            mycanvas.drawRightString(280 + x_adjust, int(end_axis) , str(net_total_tray_count))
            net_total_packet_positive_count = data['total_milk_packet_count'] + data['total_curd_packet_count']
            mycanvas.drawRightString(335 + x_adjust, int(end_axis) , str(net_total_packet_positive_count))
            net_total_packet_negative_count = data['total_milk_packet_count_in_negative'] + data[
                'total_curd_packet_count_in_negative']
            mycanvas.drawRightString(380 + x_adjust, int(end_axis) , str(-net_total_packet_negative_count))
            net_total_leak_packet_count = data['total_milk_leak_packet_count'] + data['total_curd_leak_packet_count']

            if not net_total_leak_packet_count == 0:
                mycanvas.drawRightString(425 + x_adjust, int(end_axis), str(net_total_leak_packet_count))
            net_total_litre = data['total_milk_litre_count'] + data['total_curd_litre_count']
            mycanvas.drawRightString(540 + x_adjust, int(end_axis), str(net_total_litre))

            mycanvas.line(10 + x_adjust, int(end_axis - 22)+15, 555 + x_adjust, int(end_axis - 22)+15)

            # right and left border
            mycanvas.line(10 + x_adjust, 715 - y_for_table2+10, 10 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(555 + x_adjust, 715 - y_for_table2+10, 555 + x_adjust, int(end_axis - 22)+15)

            # data borders
            mycanvas.line(60 + x_adjust, 715 - y_for_table2+10, 60 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(170 + x_adjust, 715 - y_for_table2+10, 170 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(230 + x_adjust, 715 - y_for_table2+10, 230 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(290 + x_adjust, 695 - y_for_table2+30, 290 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(343 + x_adjust, 695 - y_for_table2+30, 343 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(405 + x_adjust, 715 - y_for_table2+10, 405 + x_adjust, int(end_axis - 22)+15)
            mycanvas.line(460 + x_adjust, 715 - y_for_table2+10, 460 + x_adjust, int(end_axis - 22)+15)

            mycanvas.setFont('Helvetica', 13)
            y_axis = y_axis - 40
            mycanvas.drawString(10 + x_adjust, int(end_axis - 55)+10, str('Dist.Assistant/M.M.O.'))
            mycanvas.drawString(210 + x_adjust, int(end_axis - 55)+10, str('Counting Officer'))
            mycanvas.drawString(450 + x_adjust, int(end_axis - 55)+10, str('Route Supervisor'))
            test = end_axis - 25

            # if i == 0:
            #     mycanvas.setDash(4,2)
            #     mycanvas.line(5,y_axis-120,600,y_axis-120)
            #     mycanvas.setDash(10,0)

    #         if not i == 1:
    #             if test < 600:
    #                 mycanvas.showPage()
        new_y_axis = y_axis

        #    -------------------------second page -------------------
        route_wise_data = route_wise_business_data(route_id, session_id, date,business)
        mycanvas.showPage()
        #     mycanvas.setLineWidth(0)
        mycanvas.setStrokeColor(colors.lightgrey)
        # HEADER
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(20, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(300, 785, 'ROUTEWISE MILK DISTRIBUTION STATEMENT')
        mycanvas.line(170, 782, 410, 782)
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
        mycanvas.drawCentredString(290, 760, 'No.' + ' ' + ':' + ' ' + str(indent_number) +"  |  "+'Route ' + ' ' + ':' + ' ' + str(route_name) + '(' + str(business_code)+ ") |  " + 'Vehicle ' + ' ' + ':' + ' ' + str(vehicle_number) +"  |  "+'Date ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name))

        x_ad = 4
        # # ----------table heading-----------
        mycanvas.setFont('Helvetica', 9)
        mycanvas.drawString(10-x_ad, 665+60, 'S.No')
        mycanvas.drawString(35-x_ad, 665+60, 'Booth')
        mycanvas.drawString(70-x_ad, 665+60, 'Agent')
        mycanvas.drawString(110-x_ad, 665+60,'Type')
        # product name on heading
        product_x_axis = 133
        line_product_x_axis = 144
        products = Product.objects.filter(is_active=True).order_by('display_ordinal')
        for product in products:
            # product short name
            if product.short_name == 'CBUK' or product.short_name == 'FMcan' or product.short_name == 'SMcan':
                mycanvas.drawString(product_x_axis-x_ad, 665+60, str(product.short_name[:6]))
            else:
                mycanvas.drawString(product_x_axis+9-x_ad, 670+60, str(product.short_name[:-4]))
                mycanvas.drawString(product_x_axis+9-x_ad, 660+60, str(product.short_name[-4:]))


            #     mycanvas.line(line_product_x_axis, 68, line_product_x_axis, 100)
            product_x_axis += 36
            line_product_x_axis += 38

        # ------------table header----------
        # table head up line
        mycanvas.line(10-x_ad, 680+60, product_x_axis -6, 680+60)
        # table head bottom line
        mycanvas.line(10-x_ad, 655+60, product_x_axis - 6, 655+60)

        y_data = 630+60
        #     value_axis = 30
        line_product_x_axis = 165
        serial_number = 1
        page_number = 1
        booth_types = route_wise_data['booth_types'].keys()
        for booth_type_index, booth_type in enumerate(booth_types, start=1):
            for booth_index, business in enumerate(route_wise_data['booth_types'][booth_type]['booth_ids'], start=1):
                value_axis = 162
                mycanvas.setFont('Helvetica', 10)
                mycanvas.drawString(12-x_ad, y_data, str(serial_number))
                mycanvas.drawString(37-x_ad, y_data,
                                    str(route_wise_data['booth_types'][booth_type][business]['business_code']))
                mycanvas.setFont('Helvetica', 10)
                mycanvas.drawString(65-x_ad, y_data,
                                    str(route_wise_data['booth_types'][booth_type][business]['agent_name'][:5]).lower())
                mycanvas.setFont('Helvetica', 10)

                booth = BusinessType.objects.get(id=booth_type).name
                booth_srt = ''
                if booth == 'Booth':
                    booth_srt = 'BO'
                if booth == 'Parlour' or booth == "Own parlour":
                    booth_srt = "UNI"
                if booth == 'Private Institute' or booth == 'Govt Institute':
                    booth_srt = "INS"
                if booth == "Other unions":
                    booth_srt = "O-UNI"
                if booth == "Other State":
                    booth_srt = "O-ST"
                mycanvas.drawCentredString(117-x_ad, y_data-5, str(booth_srt))
                mycanvas.setFont('Helvetica', 10)

                for product in products:
                    if product.id in route_wise_data['booth_types'][booth_type][business]['product']:
                        mycanvas.drawRightString(value_axis-x_ad, y_data, str(
                            int(route_wise_data['booth_types'][booth_type][business]['product'][product.id])))
                    value_axis = value_axis + 36
                y_data -= 25
                value_axis = 160
                mycanvas.line(line_product_x_axis-x_ad, 300, line_product_x_axis-x_ad, 300)
                line_product_x_axis += 35


                if serial_number % 25 == 0:
                    page_number += 1
                    mycanvas.line(2, 680+60, 3, y_data)
                    mycanvas.line(29, 680+60, 29, y_data)
                    mycanvas.line(59, 680+60, 59, y_data)
                    mycanvas.line(93, 680+60, 93, y_data)
                    x_data = 132

                    for product in products:
                        # line after short name of the product
                        mycanvas.line(x_data-x_ad, 680+60, x_data, y_data)
                        x_data += 36

                    # line after 1st page
                    mycanvas.line(10, y_data, x_data, y_data)

                    # neext
                    mycanvas.showPage()
                    mycanvas.setStrokeColor(colors.lightgrey)

                    # HEADER
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawString(20, 800, 'The Coimbatore District Co-Operative Milk Producers Union Ltd, Pachapalayam, Coimbatore - 641 010')
                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(300, 785, 'ROUTEWISE MILK DISTRIBUTION STATEMENT')
                    mycanvas.line(170, 782, 410, 782)
                    # basic head
                    # row 1
                    indent_number = 8468
                    page_number = page_number
                    route_name = route_wise_data['route_name']
                    vehicle_number = route_wise_data['vehicle_number']

                    mycanvas.setFont('Helvetica', 12)
                    mycanvas.drawCentredString(290, 760, 'No.' + ' ' + ':' + ' ' + str(indent_number) +"  |  "+'Route ' + ' ' + ':' + ' ' + str(route_name) + "  |  " + 'Vehicle ' + ' ' + ':' + ' ' + str(vehicle_number) +"  |  "+'Date ' + ':' + ' ' + str(route_date) + ' ' + '/' + ' ' + (session_name))

                    x_ad = 4
                    # # ----------table heading-----------
                    mycanvas.setFont('Helvetica', 9)
                    mycanvas.drawString(10-x_ad, 665+60, 'S.No')
                    mycanvas.drawString(35-x_ad, 665+60, 'Booth')
                    mycanvas.drawString(70-x_ad, 665+60, 'Agent')
                    mycanvas.drawString(110-x_ad, 665+60,'Type')
                    # product name on heading
                    product_x_axis = 133
                    line_product_x_axis = 144
                    products = Product.objects.filter(is_active=True).order_by('display_ordinal')
                    for product in products:
                        # product short name
                        if product.short_name == 'CBUK' or product.short_name == 'FMcan' or product.short_name == 'SMcan':
                            mycanvas.drawString(product_x_axis-x_ad, 665+60, str(product.short_name[:6]))
                        else:
                            mycanvas.drawString(product_x_axis+9-x_ad, 670+60, str(product.short_name[:-4]))
                            mycanvas.drawString(product_x_axis+9-x_ad, 660+60, str(product.short_name[-4:]))


                        #     mycanvas.line(line_product_x_axis, 68, line_product_x_axis, 100)
                        product_x_axis += 36
                        line_product_x_axis += 38

                    # ------------table header----------
                    # table head up line
                    mycanvas.line(10-x_ad, 680+60, product_x_axis -6, 680+60)
                    # table head bottom line
                    mycanvas.line(10-x_ad, 655+60, product_x_axis - 6, 655+60)
                    #  next
                    y_data = 645 + 60
                    value_axis = 162
    #                 line_product_x_axis = 165

                serial_number += 1

        # bottom border
        y_data -= 25
        mycanvas.line(10-x_ad, y_data, product_x_axis - 6, y_data)
        mycanvas.line(10-x_ad, y_data + 25, product_x_axis - 6, y_data + 25)
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawString(10-x_ad, y_data + 11, str('Grand Total'))
        mycanvas.setFont('Helvetica', 10)
        value_axis = 162

        for product in products:
            if not route_wise_data['total'][product.id] == 0:
                mycanvas.drawRightString(value_axis-x_ad, y_data + 11, str(int(route_wise_data['total'][product.id])))
            value_axis = value_axis + 36

    # lines after products
        x_axis_data = 166
        for product in products:
            mycanvas.line(x_axis_data-x_ad, 680+60, x_axis_data-x_ad, y_data)
            if product == products[0]:
                mycanvas.line(x_axis_data-33-x_ad, 680+60, x_axis_data-33-x_ad, y_data)  
            x_axis_data += 36
        mycanvas.line(5-x_ad, 680+60, 5-x_ad, y_data)
        mycanvas.line(34-x_ad, 680+60, 34-x_ad, y_data+25)
        mycanvas.line(64-x_ad, 680+60, 64-x_ad, y_data+25)
        mycanvas.line(99-x_ad, 680+60, 99-x_ad, y_data)

        #     tray and extra pocket
        y_data = y_data - 25

        mycanvas.drawString(450, y_data-30, str('Route Supervisor'))
       
       
       
 
        #         Third page section
       
        business_data = get_individual_business_data(business, session_id, date)
        last_count_for_business_bill = IndentCodeBank.objects.get(code_for='business_bill')
        bill_number = int(last_count_for_business_bill.last_code) + 1
        if bill_number == 999999:
            last_count_for_business_bill.last_code = 0
        else:
            last_count_for_business_bill.last_code = bill_number
        last_count_for_business_bill.save()
        x_new = 50
        third_y = 400
        mycanvas.setFont('Helvetica', 12)
        mycanvas.drawCentredString(110 + x_new, third_y + 5, str('DCMPU-CBE Delivery Note'))
        mycanvas.setFont('Helvetica', 10)
        mycanvas.drawString(x_new - 40, third_y - 25, str(business_data['route_name']) +"  |  "+str('No' + ':' + str(bill_number)+"  |  "+ str(route_date + '/' + business_data['session'])))
        key_id = list(business_data['sales'].keys())

        mycanvas.drawString(x_new - 40, third_y - 45, str('Booth: ')+str(' ' + business_data['business_code'])+"  |  "+str(business_data['agent_first_name'] + ' ' + business_data['agent_last_name'] + '[' + business_data['agent_code'] + ']'))

        mycanvas.setFont('Helvetica', 10)
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
#         mycanvas.setFont('Helvetica', 12)
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
#         mycanvas.setFont('Helvetica', 10)
        mycanvas.drawString(x_new - 35, product_axis - 15, str('Milk(Cash Sales)Rs.'))
        mycanvas.drawString(150 + x_new, product_axis - 15, str(business_data['total_cost']))
        mycanvas.line(x_new - 40, product_axis - 20, 300 + x_new-55, product_axis - 20)

        mycanvas.drawString(100 + x_new, product_axis - 40, str('Receiver\'s Signature'))
        mycanvas.showPage()

    return mycanvas