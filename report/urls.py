from django.conf.urls import url
from report import views_generate_report, views_consolidate_data, views_prepare_daily_script
urlpatterns = [
    url(r'^generate/pdf/code/for/cash/finance/report/$', views_generate_report.generate_pdf_code_for_cash_finace_report),
    url(r'^generate/pdf/code/for/cash/finance/report/on/delivery/date/$', views_consolidate_data.generate_pdf_code_for_cash_finace_report_on_delivery_date),
    url(r'^generate/pdf/code/for/total/milk/sale/$', views_generate_report.generate_pdf_code_for_total_milk_sale),
    url(r'^generate/pdf/code/for/total/curd/sale/$', views_generate_report.generate_pdf_code_for_total_curd_sale),
    url(r'^generate/institution/bill/for/milk/$', views_generate_report.generate_institution_bill_for_milk),
    url(r'^generate/institution/bill/for/curd/$', views_generate_report.generate_institution_bill_for_curd),
    url(r'^serve/tray/count/report/$', views_generate_report.serve_tray_count_report),
    url(r'^serve/leakage/allowance/details/$', views_generate_report.serve_leakage_allowance_details),
    url(r'^serve/all/type/of/report/$', views_consolidate_data.serve_all_type_of_report),
    url(r'^simple/comparision/report/$', views_consolidate_data.serve_simple_comparision_report),
    url(r'^serve/zone/booth/route/data/gor/general/report/$', views_consolidate_data.serve_zone_booth_route_data_gor_general_report),
    url(r'^serve/advance/report/in/excel/$', views_consolidate_data.serve_advance_report_in_excel),
    url(r'^serve/advance/report/in/excel/for/route/$', views_consolidate_data.serve_advance_report_in_excel_for_route),
    url(r'^run/booth/commission/for/seleted/date/range/$', views_consolidate_data.run_booth_commission_for_seleted_date_range),
    url(r'^serve/agent/monthly/commisssion/report/$', views_consolidate_data.serve_agent_monthly_commission_report),
    url(r'^serve/run/list/for/commission/$', views_consolidate_data.serve_run_list_for_commission),
    url(r'^generate/monthly/institution/bill/abstract/$', views_generate_report.generate_monthly_institution_bill_abstract),
    url(r'^serve/bulk/customer/card/data/$', views_generate_report.serve_bulk_customer_card_data),
    url(r'^serve/customer/order/statement/selected/booth/$', views_generate_report.serve_customer_order_statement_selected_booth),
    url(r'^serve/customer/order/statement/bulk/booth/$',views_generate_report.server_bulk_customer_booth_statement),
    # url(r'^serve/year/list/for/comparision/five/$', views_generate_report.serve_years_list_for_comparision_five),
    url(r'^serve/comparision/five/report/$', views_generate_report.serve_comparision_five_data),
    url(r'^serve/monthly/bill/abstract/$', views_generate_report.serve_monthly_bill_abstact),
    url(r'^serve/institution/bill/as/dbf/$', views_generate_report.serve_institution_bill_as_dbf),
    url(r'^serve/monthly/dairy/summary/as/report/three/$', views_generate_report.serve_monthly_dairy_summary_as_report_three),
    url(r'^serve/account/section/online/payment/report/$', views_generate_report.serve_account_section_online_payment_report),

    url(r'^serve/incentive/report/$',views_generate_report.serve_incentive_report),
    url(r'^serve/transaction/log/$',views_generate_report.serve_transaction_log),
    url(r'^serve/monthly/milk/abstract/$',views_generate_report.serve_milk_abstract_for_month),
    url(r'serve/monthly/supplyed/milk/for/card/customer/$',views_generate_report.serve_monthly_supplied_milk_for_card_customer),
    url(r'serve/super/sale/group/report/$', views_consolidate_data.serve_super_sale_group_report),
    url(r'serve/counter/amount/in/super/sale/group/$', views_consolidate_data.serve_counter_amount_in_super_sale_group),
    url(r'serve/online/amount/in/super/sale/group/$', views_consolidate_data.serve_online_amount_in_super_sale_group),
    url(r'serve/wallet/amount/in/super/sale/group/$', views_consolidate_data.serve_wallet_amount_in_super_sale_group),
    url(r'serve/online/payment/transation/report/$', views_consolidate_data.serve_online_payment_transation_report),
    url(r'serve/product/wise/super/sale/group/$', views_consolidate_data.serve_product_wise_super_sale_group),
    url(r'serve/day/wise/tray/total/count/$', views_generate_report.serve_day_wise_tray_total_count),
    url(r'serve/monthly/counter/wise/report/$', views_generate_report.serve_monthly_counter_wise_report),
    url(r'serve/counter/employe/sale/for/date/$', views_generate_report.serve_counter_employe_sale_for_date),
    url(r'booth/wise/agent/details/$', views_generate_report.booth_wise_agent_details),
    url(r'customer/details/$', views_generate_report.customer_details),
    url(r'create/daily/run/log/$', views_prepare_daily_script.prepare_daily_report_run_log),
    url(r'daily/data/upload/script/call/$', views_prepare_daily_script.daily_data_upload_script_call),
    url(r'daily/script/complete/status/$',views_prepare_daily_script.daily_script_complete_status),
    url(r'serve/excel/for/society/bill/$',views_generate_report.serve_excel_for_society_bill),
    url(r'serve/route/for/leakage/allowance/details/$',views_generate_report.serve_route_for_leakage_allowance_details),
    url(r'serve/excel/for/employee/and/exemployee/product/and/quandity/details/$',views_generate_report.serve_excel_for_employee_and_exemployee_product_and_quandity_details),
    url(r'serve/combain/online/report/$', views_consolidate_data.serve_combain_online_report),
    url(r'serve/excel/for/city/wise/sale/report/$', views_consolidate_data.serve_excel_for_city_wise_sale_report),
    url(r'serve/product/type/list/from/product/finance/code/map/$', views_consolidate_data.serve_product_type_list_from_product_finance_code_map),
    url(r'serve/date/range/wise/sale/and/transaction/$', views_generate_report.serve_date_range_wise_sale_and_transaction),
    url(r'validate/and/serve/data/for/mismatch/$', views_generate_report.validate_and_serve_data_for_mismatch),
    url(r'serve/business/type/wise/business/for/bill/$', views_consolidate_data.serve_business_type_wise_business_for_bill),
    url(r'generate_institution_bill_with_gst/$', views_generate_report.generate_institution_bill_with_gst),
    url(r'^serve/json/fermented/products/govt/upload/$', views_generate_report.serve_json_fermented_products_govt_upload),
    url(r'^serve_govt_jst_bill_summary/$', views_generate_report.serve_govt_jst_bill_summary),

]
