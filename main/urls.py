from django.conf.urls import url
from main import views

urlpatterns = [
    url(r'^app/login/for/token/$', views.login_for_token),
    url(r'^portal/login/for/token/$', views.portal_login_for_token),
    url(r'^website/login/for/token/$', views.website_login_for_token),
    # forget password
    url(r'^username/validation/$', views.username_validation),
    url(r'^otp/validation/$', views.otp_validation),
    url(r'^reset/password/$', views.reset_password),

    #     for portal
    url(r'^serve/user/types/$', views.serve_user_types),
    url(r'^serve/location/cv/$', views.serve_location_cv),
    url(r'^save/zone/$', views.save_or_update_zone),
    url(r'^save/booth/type/$', views.save_booth_type),
    url(r'^save/constituency/$', views.save_constituency),
    url(r'^serve/district/$', views.serve_district),
    url(r'^serve/constituency/$', views.serve_constituency),
    url(r'^save/ward/$', views.save_ward),
    url(r'^serve/unions/$', views.serve_unions),
    url(r'^serve/booths/$', views.serve_booths),
    url(r'^serve/genders/$', views.serve_genders),
    url(r'^serve/taluks/$', views.serve_taluks),
    url(r'^serve/states/$', views.serve_states),
    url(r'^serve/location/categories/$', views.serve_location_categories),
    url(r'^serve/relation/types/$', views.serve_relation_types),
    url(r'^save/booth/$', views.save_booth),
    url(r'^save/agent/$', views.save_agent),
    url(r'^save/vehicle/register/$', views.save_vehicle_transport),
    url(r'^save/vehicle/type/$', views.save_vehicle_type),


    url(r'^serve/zones/$', views.serve_zones),
    url(r'^serve/mor/route/$', views.serve_mor_routes),
    url(r'^serve/booth/types/$', views.serve_booth_types),
    url(r'^serve/wards/$', views.serve_wards),
    url(r'^serve/agents/$', views.serve_agents),
    url(r'^serve/vehicle/transports/$', views.serve_vehicle_transports),
    url(r'^serve/product/group/$', views.serve_product_group),
    url(r'^save/product/$', views.save_product),
    url(r'^serve/product/$', views.serve_product),
    url(r'^serve/product/unit/$', views.serve_product_unit),
    url(r'^save/product/unit/$', views.save_product_unit),
    url(r'^save/relation/type/$', views.save_relation_type),

    # For mobile app
    url(r'^serve/product/list/$', views.serve_product_list),
    url(r'^register/order/for/agent/$', views.register_order_for_agent),
    url(r'^serve/sale/details/for/future/week/$',
        views.serve_sale_details_for_future_week),
    url(r'^serve/sale/details/for/last/week/$',
        views.serve_sale_details_for_last_week),
    url(r'^serve/last/date/for/agent/order/$',
        views.serve_last_date_for_agent_order),
    url(r'^check/order/exists/$', views.check_order_exits),
    url(r'^serve/sale/for/selected/date/$', views.serve_sale_for_selected_date),
    url(r'^update/selected/sale/group/$', views.update_selected_sale_group),
    url(r'^update/and/pay/selected/sale/group/$',
        views.update_and_pay_selected_sale_group),
    url(r'^serve/agent/wallet/$', views.serve_agent_wallet),
    url(r'^serve/last/week/transaction/log/and/wallet/balance/$',
        views.serve_last_week_transaction_log_and_wallet_balance),
    url(r'^serve/last/week/transaction/log/and/wallet/balance/for/customer/$',
        views.serve_last_week_transaction_log_and_wallet_balance_for_customer),
    url(r'^serve/advertisement/$', views.serve_advertisement),

    url(r'^serve/business/type/for/commission/$',
        views.serve_business_types_for_commission),
    url(r'^serve/business/type/wise/product/commission/$',
        views.serve_business_type_wise_product_commission),
    url(r'^save/or/update/business/type/wise/product/commission/$',
        views.save_or_update_business_type_wise_product_commission),
    url(r'^serve/business/type/commission/products/$',
        views.serve_business_type_commission_products),
    url(r'^serve/products/name/dict/type/$',
        views.serve_products_name_dict_type),
    url(r'^serve/business/type/name/dict/type/$',
        views.serve_business_type_name_dict_type),
    url(r'^serve/discount/products/$', views.serve_discount_products),
    url(r'^serve/discount/business/$', views.serve_discount_business),
    url(r'^serve/business/wise/discount/price/dict/$',
        views.serve_business_wise_discount_price_dict),
    url(r'^save/or/update/business/wise/product/discount/price/$',
        views.save_or_update_business_wise_product_discount_price),
    url(r'^serve/business/type/wise/discount/product/$',
        views.serve_business_type_wise_discount_product),
    url(r'^serve/business/type/wise/discount/business/types/$',
        views.serve_business_type_wise_discount_business_types),
    url(r'^serve/business/type/wise/discount/price/dict/$',
        views.serve_business_type_wise_discount_price_dict),
    url(r'^save/or/update/business/type/wise/product/discount/price/$',
        views.save_or_update_business_type_wise_discount_price),
    url(r'^serve/all/business/$', views.serve_all_business),
    url(r'^serve/all/business/for/booth/change/$',
        views.serve_all_business_for_booth_change),
    url(r'^save/relation/type/$', views.save_relation_type),
    url(r'^serve/routes/$', views.serve_routes),
    url(r'^route/business/map/$', views.route_business_map),
    url(r'^serve/business/by/route/$', views.serve_business_by_route),
    url(r'^remove/business/from/route/$', views.remove_business_from_route),
    url(r'^serve/products/for/agent/order/$',
        views.serve_products_for_agent_order),
    url(r'^serve/session/$', views.serve_session),
    url(r'^serve/business/last/sale/$', views.serve_business_last_sale),
    url(r'^serve/nominee/bank/info/for/agent/update/$',
        views.serve_nominee_and_bank_info_for_agent_update),
    url(r'^save/taluk/$', views.save_taluk),
    url(r'^serve/employee/$', views.serve_employee),
    url(r'^serve/employee/role/$', views.serve_employee_role),
    url(r'^serve/office/$', views.serve_office),
    url(r'^save/employee/$', views.save_employee),
    url(r'^get/employee/details/$', views.get_employee_details),
    url(r'^save/union/office/$', views.save_union_office),
    url(r'^check/wheather/customer/exists/$',
        views.check_wheather_customer_exists),
    url(r'^otp/validation/for/temporary/registration/$',
        views.otp_validation_for_temporary_registration),
    url(r'^serve/general/data/for/registration/$',
        views.serve_general_data_for_registration),
    url(r'^register/customer/$', views.register_customer),
    url(r'^serve/booth/under/pincode/$', views.serve_booth_under_pincode),
    url(r'^serve/booth/lat/lng/$', views.serve_booth_lat_lng),
    url(r'^serve/selected/booth/details/$', views.serve_selected_booth_details),
    url(r'^link/booth/with/customer/$', views.link_booth_with_customer),
    url(r'^serve/product/list/for/icustomer/$',
        views.serve_product_list_for_customer),
    url(r'^serve/last/month/order/for/icustomer/$',
        views.serve_last_month_order_for_icustomer),
    url(r'^register/order/for/icustomer/$', views.register_order_for_icustomer),
    url(r'^serve/customer/business/details/$',
        views.serve_customer_business_details),
    url(r'^serve/icustomer/history/for/last/four/month/$',
        views.serve_icustomer_history_data_for_last_four_month),
    url(r'^serve/icustomer/latest/twelve/orders/$',
        views.serve_icustomer_latest_twelve_orders),
    url(r'^serve/icustomer/selected/month/sale/group/$',
        views.serve_icustomer_selected_month_sale_group),
    url(r'^serve/last/date/for/the/icustomer/order/$',
        views.serve_last_date_for_the_icustomer_order),
    url(r'^serve/all/product/list/for/display/$',
        views.serve_all_product_list_for_display),
    url(r'^serve/icustomer/list/linked/with/agent/$',
        views.serve_icustomer_list_linked_with_agent),
    url(r'^serve/icustomer/orders/for/agent/',
        views.serve_icustomer_orders_for_agent),
    url(r'^serve/sale/details/based/on/date/range/$',
        views.serve_sale_details_based_on_date_range),
    url(r'^serve/sale/details/based/on/week/range/$',
        views.serve_sale_details_based_on_week_range),
    url(r'^serve/sale/details/based/on/month/range/$',
        views.serve_sale_details_based_on_month_range),
    url(r'^serve/last/seven/days/data/for/aavin/today/$',
        views.serve_last_seven_days_data_for_aavin_today),
    # url(r'^serve/product/product/group/for/aavin/today/$', views.serve_product_group_for_aavin_today),
    url(r'^serve/live/intent/for/selected/date/$',
        views.serve_live_indent_for_selected_date),
    url(r'^serve/business/type/$', views.serve_business_type),
    url(r'^save/agent/request/form/$', views.save_agent_request_form),
    url(r'^check/phone/number/on/request/form/$',
        views.check_phone_number_exists_on_agent_request_form),
    url(r'^serve/unordered/and/ordered/booth/for/zone/$',
        views.serve_unordered_and_ordered_booth_for_zone),
    url(r'^serve/zone/under/employee/$', views.serve_zone_under_employee),

    url(r'^save/location/category/$', views.save_location_category),
    url(r'^serve/icustomers/list/$', views.serve_icustomer_list),
    url(r'^serve/customer/type/$', views.serve_customer_type),
    url(r'^save/icustomer/$', views.save_icustomer),
    url(r'^get/icustomer/details/for/update/$',
        views.get_icustomer_details_for_update),
    url(r'^serve/vehicle/type/$', views.serve_vehicle_type),
    url(r'^serve/vehicle/$', views.serve_vehicle),
    url(r'^serve/route/$', views.serve_route),
    url(r'^save/vehicle/$', views.save_vehicle),
    url(r'^serve/session/$', views.serve_session),
    url(r'^serve/vehicle/details/for/update/$',
        views.get_vehicle_details_for_update),
    url(r'^save/route/$', views.save_route),
    url(r'^serve/business/type/wise/product/price/$',
        views.serve_business_type_wise_product_price),
    url(r'^place/agent/order/$', views.place_agent_order),
    url(r'^serve/order/expiry/time/by/business/$',
        views.serve_order_expiry_time_by_business),
    url(r'^serve/unmapped/business/with/route/session/$',
        views.serve_unmapped_business_with_route_session),
    url(r'^serve/business/order/future/date/$',
        views.serve_business_order_future_date),

    url(r'^serve/business/type/for/commission/$',
        views.serve_business_types_for_commission),
    url(r'^serve/business/type/wise/product/commission/$',
        views.serve_business_type_wise_product_commission),
    url(r'^save/or/update/business/type/wise/product/commission/$',
        views.save_or_update_business_type_wise_product_commission),
    url(r'^serve/business/type/commission/products/$',
        views.serve_business_type_commission_products),
    url(r'^serve/products/name/dict/type/$',
        views.serve_products_name_dict_type),
    url(r'^serve/business/type/name/dict/type/$',
        views.serve_business_type_name_dict_type),
    url(r'^serve/discount/products/$', views.serve_discount_products),
    url(r'^serve/discount/business/$', views.serve_discount_business),
    url(r'^serve/business/wise/discount/price/dict/$',
        views.serve_business_wise_discount_price_dict),
    url(r'^save/or/update/business/wise/product/discount/price/$',
        views.save_or_update_business_wise_product_discount_price),
    url(r'^serve/business/type/wise/discount/product/$',
        views.serve_business_type_wise_discount_product),
    url(r'^serve/icustomer/wise/discount/product/$',
        views.serve_icustomer_wise_discount_product),

    url(r'^serve/business/type/wise/discount/business/types/$',
        views.serve_business_type_wise_discount_business_types),
    url(r'^serve/business/type/wise/discount/price/dict/$',
        views.serve_business_type_wise_discount_price_dict),
    url(r'^save/or/update/business/type/wise/product/discount/price/$',
        views.save_or_update_business_type_wise_discount_price),
    url(r'^serve/all/business/$', views.serve_all_business),
    url(r'^save/relation/type/$', views.save_relation_type),
    url(r'^serve/routes/$', views.serve_routes),
    url(r'^route/business/map/$', views.route_business_map),
    # url(r'^serve/business/by/route/$', views.serve_business_by_route),
    url(r'^remove/business/from/route/$', views.remove_business_from_route),
    url(r'^serve/products/for/agent/order/$',
        views.serve_products_for_agent_order),
    url(r'^serve/session/$', views.serve_session),
    url(r'^serve/icustomer/type/wise/discount/price/dict/$',
        views.serve_icustomer_wise_discount_price_dict),
    url(r'^save/or/update/icustomer/type/wise/discount/$',
        views.save_or_update_icustomer_type_wise_discount_price),
    url(r'^serve/product/trace/log/$', views.serve_product_trace_log),
    url(r'^serve/business/type/wise/product/commission/trace/log/$',
        views.serve_business_type_wise_product_commission_trace_log),
    url(r'^serve/business/type/wise/product/discount/trace/log/$',
        views.serve_business_type_wise_product_discount_trace_log),
    url(r'^serve/business/wise/product/discount/trace/log/$',
        views.serve_business_wise_product_discount_trace_log),
    url(r'^serve/icustomer/wise/product/discount/trace/log/$',
        views.serve_icustomer_type_wise_product_discount_trace_log),
    url(r'^serve/products/with/mrp/', views.serve_products_with_mrp),
    url(r'^generate/booth/code/', views.generate_booth_code),
    url(r'^check/booth/name/availability/',
        views.check_booth_name_availability),
    url(r'^check/booth/code/', views.check_booth_code),
    url(r'^generate/agent/code/', views.generate_agent_code),
    # indent related service
    url(r'^serve/indent/overall/data/$', views.serve_indent_overall_data),
    url(r'^serve/indent/overall/data/for/old/indent/$',
        views.serve_indent_overall_data_for_old_indent),
    url(r'^serve/indent/route/wise/data/$', views.serve_indent_route_wise_data),
    url(r'^prepare/route/indent/$', views.prepare_route_indent),
    url(r'^serve/prepared/indent/route/ids/$',
        views.serve_prepared_indent_route_ids),
    url(r'^serve/route/indent/details/$', views.serve_route_indent_details),
    url(r'^check/vehicle/assigned/to/another/route/$',
        views.check_vehicle_assigned_to_another_route),

    url(r'^serve/product/availability/for/portal/$',
        views.serve_product_availability_for_portal),
    url(r'^change/product/availability/$', views.change_product_availability),
    url(r'^check/icustomer/details/$', views.check_icustomer_details),
    url(r'^serve/route/vehicle/map/$', views.serve_route_vehicle_map),
    url(r'^change/business/ordinal/in/route/map/$',
        views.change_business_ordinal_in_route_map),
    url(r'^serve/all/route/wise/data/$', views.serve_all_route_wise_data),
    url(r'^serve/all/route/wise/data/for/old/indent/$',
        views.serve_all_route_wise_data_for_old_indent),
    url(r'^serve/intent/for/business/wise/$',
        views.serve_intent_for_business_wise),
    url(r'^serve/route/wise/business/sale/reports/$',
        views.route_wise_business_sale_reports),
    url(r'^close/overall/intent/$', views.close_overall_route_indent),
    url(r'^prepare/indent/for/all/closed/routes/$',
        views.prepare_indent_for_all_closed_routes),
    url(r'^create/canvas/report/$', views.create_canvas_report),

    # urls for report
    url(r'^serve/agent/monthly/report/$', views.serve_agent_monthly_report),
    url(r'^serve/business/bill/$', views.serve_business_bill),
    url(r'^serve/tray/config/$', views.serve_tray_config),
    url(r'^serve/route/gate/pass/$', views.serve_route_gate_pass),
    url(r'^serve/route/session/wise/$', views.serve_route_session_wise),
    url(r'^serve/corporation/zone/$', views.serve_corporation_zone),
    url(r'^save/corporation/zone/$', views.save_corporation_zone),
    url(r'^serve/agent/image/$', views.serve_agent_image),
    url(r'^serve/milk/product/$', views.serve_milk_products),
    url(r'^save/district/$', views.save_district),
    url(r'^serve/block/$', views.serve_block),
    url(r'^save/block/$', views.save_block),
    url(r'^serve/indent/pdf/$', views.serve_indent_pdf),
    url(r'^serve/indent/pdf/for/old/indent/$',
        views.serve_indent_pdf_for_old_indent),
    url(r'^check/overall/route/closed/$',
        views.check_for_overal_route_is_closed),
    url(r'^check/overall/route/closed/for/old/indent/$',
        views.check_for_overal_route_is_closed_for_old_indent),
    url(r'^get/payment/modes/$', views.get_payment_modes),
    url(r'^add/money/to/wallet/$', views.add_money_to_wallet),
    url(r'^get/cheque/status/logs/$', views.get_cheque_status_logs),
    url(r'^save/cheque/approal/$', views.save_cheque_approval),
    url(r'^get/cheque/status/logs/for/individual/transaction/$',
        views.get_cheque_status_logs_for_individual_transaction),
    url(r'^serve/last/week/transaction/log/for/icustomers/$',
        views.serve_last_week_transaction_log_for_icustomers),
    url(r'^check/booth/agent/exists/$', views.check_for_booth_agent_exists),
    # Counter
    url(r'^serve/un/active/counter/$', views.serve_un_active_counter),
    url(r'^assign/counter/to/employee/$', views.assign_counter_to_employee),
    url(r'^logout/employee/from/counter/$', views.logout_employee_from_counter),
    url(r'^serve/counter/orders/$', views.serve_counter_orders),
    url(r'^serve/icustomer/counter/orders/$',
        views.serve_icustomer_counter_orders),
    url(r'^serve/indent/pdf/all/closed/routes/$',
        views.serve_indent_pdf_all_closed_routes),
    url(r'^serve/indent/pdf/all/closed/routes/for/old/indent/$',
        views.serve_indent_pdf_all_closed_routes_for_old_indent),
    url(r'^serve/wards/based/on/constituency/$',
        views.serve_wards_based_on_constituency),
    url(r'^serve/business/list/for/route/rearrange/$',
        views.serve_business_list_for_route_rearrange),
    url(r'^move/business/to/temp/route/$', views.move_business_to_temp_route),
    url(r'^move/business/to/main/route/$', views.move_business_to_main_route),
    url(r'^close/temp/and/main/route/$', views.close_temp_and_main_route),
    url(r'^serve/temp/route/details/$', views.serve_temp_route_details),
    url(r'^serve/temp/route/details/for/old/indent/$',
        views.serve_temp_route_details_for_old_indent),
    url(r'^rearrange/business/to/original/route/$',
        views.rerrange_to_original_route),
    url(r'^get/google/album/$', views.get_album),

    url(r'^get/photos/inside/album/$', views.get_photos_inside_album),
    url(r'^serve/active/carrier/$', views.serve_active_carrier),
    url(r'^serve/active/tender/$', views.serve_active_tender),
    url(r'^serve/zone/wise/ordered/business/data/$',
        views.serve_zone_wise_ordered_business_data),
    url(r'^serve/counter/list/$', views.serve_counter_list),
    url(r'^delete/selected/order/$', views.delete_selected_order),
    url(r'^delete/selected/order/from/website/$',
        views.delete_selected_order_from_website),
    url(r'^serve/counter/report/for/agent/$',
        views.serve_counter_report_for_agent),
    url(r'^serve/counter/report/json/for/agent/$',
        views.serve_counter_report_json_for_agent),
    url(r'^serve/counter/report/json/for/customer/$',
        views.serve_counter_report_json_for_customer),
    url(r'^check/user/is/anonymous/$', views.check_user_is_anonymous),
    url(r'^serve/product/discount/price/for/update/$',
        views.serve_product_discount_price_for_update),
    url(r'^serve/total/sale/for/selected/date/counter/wise/$',
        views.serve_total_sale_for_selected_date_counter_wise),
    url(r'^serve/total/sale/for/selected/date/counter/wise/as/json/$',
        views.serve_total_sale_for_selected_date_counter_wise_as_json),
    url(r'^serve/total/sale/per/month/in/counter/$',
        views.serve_total_sale_per_month_in_counter),

    url(r'^serve/total/sale/per/month/in/counter/as/json/$',
        views.serve_total_sale_per_month_in_counter_as_json),
    url(r'^serve/route/wise/sale/abstract/$',
        views.serve_route_wise_sale_abstract),
    url(r'^serve/milk/acknowledgement/report/$',
        views.serve_milk_acknowledgement_report),
    url(r'^serve/all/zone/report/$', views.serve_all_zone_report),
    url(r'^serve/daily/zone/wise/sale/$', views.serve_daily_zone_wise_sale),
    url(r'^serve/unique/route/wise/sale/abstract/$',
        views.serve_unique_route_wise_sale_abstract),
    url(r'^serve/state/based/district/$', views.serve_state_based_district),
    url(r'^serve/district/based/taluk/$', views.serve_district_based_taluk),
    url(r'^delete/selected/icustomer/sale/$',
        views.delete_selected_icustomer_sale),
    url(r'^update/business/route/map/$', views.update_business_route_map),
    url(r'^serve/route/vehicle/map/log/$', views.serve_route_vehicle_map_log),
    url(r'^update/route/vehicle/change/$', views.update_route_vehicle_change),
    url(r'^change/route/vehicle/$', views.change_route_vehicle),

    url(r'^change/business/active/status/$',
        views.change_business_active_status),
    url(r'^serve/transaction/history/agent/$',
        views.serve_transaction_history_agent),
    url(r'^get/route/indent/status/per/session/$',
        views.get_route_indent_status_per_sesion),
    url(r'^get/route/indent/status/per/session/for/website/$',
        views.get_route_indent_status_per_sesion_for_website),
    url(r'^get/employee/user/type/$', views.get_employee_user_type),
    url(r'^check/booth/exists/$', views.check_booth_code_exists),
    url(r'^check/agent/code/$', views.check_agent_code),
    url(r'^reprepare/indent/$', views.reprepare_indent),
    url(r'^serve/route/wise/sale/statement/$',
        views.serve_route_wise_sale_statement),
    url(r'^serve/zone/wise/abstract/$', views.serve_zone_wise_abstract),
    url(r'^serve/business/type/wise/summary/$',
        views.serve_business_type_wise_summary),
    url(r'^serve/union/wise/summary/$', views.serve_union_wise_summary),
    url(r'^serve/zone/wise/route/abstract/$',
        views.serve_zone_wise_route_abstract),
    url(r'^get/global/config/data/$', views.get_global_config_data),
    url(r'^serve/last/month/order/count/for/counter/$',
        views.serve_last_month_order_count_for_counter),
    url(r'^serve/employee/role/menu/$', views.serve_employee_role_menu),
    url(r'^payment/response/$', views.payment_response),
    url(r'^change/route/expiry/time/$', views.change_route_expiry_time),
    url(r'^create/encryption/text/and/make/request/$',
        views.create_encryption_text_and_make_request),
    url(r'^generate/payment/link/for/icustmer/order/$',
        views.generate_payment_link_for_icustomer_order),
    url(r'^serve/booth/change/time/range/$',
        views.serve_booth_change_time_range),
    url(r'^change/overall/route/expiry/time/$',
        views.change_overall_route_expiry_time),
    url(r'^save/booth/with/nominee/$', views.save_booth_with_nominee),
    url(r'^serve/booth/details/for/update/$',
        views.serve_booth_details_for_update),
    url(r'^save/individual/field/in/agent/booth/$',
        views.save_individual_field_in_agent_booth),
    url(r'^serve/sale/group/delele/log/$', views.serve_sale_group_delele_log),
    url(r'^serve/route/time/change/log/$', views.serve_route_time_change_log),
    url(r'^serve/route/business/change/log/$',
        views.serve_route_business_change_log),
    url(r'^serve/icustomer/business/change/log/$',
        views.serve_icustomer_business_change_log),
    url(r'^customer/card/preview/$', views.customer_card_preview),
    url(r'^confirm/mobile/verification/$', views.confirm_mobile_verification),
    url(r'^send/otp/to/mobile/number/$', views.send_otp_to_mobile_number),
    url(r'^confirm/otp/for/mobile/verification/$',
        views.confirm_otp_for_mobile_verification),
    url(r'^confirm/otp/for/customer/verification/$',
        views.confirm_otp_for_customer_verification),
    url(r'^confirm/otp/for/password/change/$',
        views.confirm_otp_for_password_change),
    url(r'^update/password/for/user/$', views.update_password_for_user),
    url(r'^update/kyc/for/icustomer/$', views.update_kyc_for_icustomer),
    url(r'^serve/payment/request/and/responce/details/$',
        views.serve_payment_request_and_responce_details),
    url(r'^create/encryption/text/and/make/enquiry/$',
        views.create_encryption_text_and_make_enquiry),
    url(r'^create/encryption/text/and/make/request/for/mobile/$',
        views.create_encryption_text_and_make_request_for_mobile),
    url(r'^serve/enquiry/request/log/$', views.serve_enquiry_request_log),
    url(r'^get/user/manual/$', views.get_user_manual),
    url(r'^check/edit/order/permission/$', views.check_edit_order_permission),
    url(r'^serve/auto/enquiry/log/$', views.serve_auto_enquiry_log),
    url(r'^serve/icustomer/details/for/edit/$',
        views.serve_icustomer_details_for_edit),
    url(r'^update/icustomer/details/$', views.update_icustomer_details),
    url(r'^serve/year/list/for/comparision/five/$',
        views.serve_years_list_for_comparision_five),
    url(r'^serve/from/time/for/booth/change/$',
        views.serve_from_time_for_booth_change),
    url(r'^serve/zone/wise/split/aavin/today/data/$',
        views.serve_zone_wise_split_aavin_today_data),
    url(r'^remove/business/type/wise/product/$',
        views.remove_business_type_wise_product),
    url(r'^remove/business/wise/product/$', views.remove_business_wise_product),
    url(r'^serve/current/date/$', views.serve_current_date),
    url(r'^app/version/check/$', views.app_version_check),
    url(r'^serve/customer/support/mobile/number/$',
        views.serve_customer_support_mobile_number),
    url(r'check/indent/staus/$', views.check_indent_staus),
    url(r'check/indent/status/for/online/$', views.check_indent_status_for_online),
    url(r'check/next/month/order/is/available/for/customer/$', views.check_next_month_order_is_available_for_customer),
    url(r'check/next/month/order/is/available/for/customer/portal/$', views.check_next_month_order_is_available_for_customer_portal),
    url(r'serve/counter/report/for/agent/delivery/$', views.serve_counter_order_details_for_agent_delivery),
    url(r'serve/counter/report/json/for/agent/delivery/$', views.serve_counter_report_json_for_agent_delivery),
    url(r'serve/ex/employee/union/$', views.serve_ex_employee_union_dict),
    url(r'get/employee/last/order/details/$', views.serve_employee_last_order_details),
    url(r'serve/product/list/for/employe/$', views.serve_product_list_for_employee),
    url(r'place/employee/order/$', views.place_employee_order),
    url(r'serve/employe/list/$', views.serve_employee_exemployee_list),
    url(r'new/employee/order/$', views.serve_employee_for_new_order),
    url(r'^serve/payment/request/and/responce/details/in/excel/$',
        views.serve_payment_request_and_responce_details_in_excel),
    url(r'serve/customer/order/delete/log/$', views.serve_customer_order_delete_log),

    url(r'serve/employee/for/new/order/for/currrent/month/$', views.serve_employee_for_new_order_for_currrent_month),
    url(r'place/employee/order/current/month/$', views.place_employee_order_current_month),
    url(r'^delete/selected/icustomer/sale/for/current/month/$',views.delete_selected_icustomer_sale_for_current_month),
    url(r'^serve/fermented/products/gst/bill/$', views.serve_fermented_products_gst_bill),


]
