from django.conf.urls import url
from transaction import views

urlpatterns = [
    url(r'^upload/bank/transaction/excel/$',views.upload_bank_transaction_excel),
    url(r'^serve/bank/transaction/uploaded/detalils/$',views.serve_bank_transaction_uploaded_detalils),
    url(r'^serve/customer/types/$',views.serve_customer_types),
    #Reports
    url(r'^serve/bank/transaction/report1/$',views.serve_bank_transaction_report1),
    url(r'^serve/bank/transaction/report2/$',views.serve_bank_transaction_report2),
    url(r'^serve/bank/transaction/report3/$',views.serve_bank_transaction_report3),
    url(r'^serve/bank/transaction/report4/$',views.serve_bank_transaction_report4),
]