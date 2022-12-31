from django.db import models
from django.contrib.auth.models import User
from main.models import PaymentRequestResponse
import datetime
# Create your models here.


def get_uploaded_excel_from_bank(instance, filename):
    return "banktransaction/{date}/{file}".format(date=instance.uploaded_at, file=filename)

class BankTransactionMaster(models.Model):
    bank_name = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField()
    uploaded_count = models.PositiveIntegerField()
    updated_count = models.PositiveIntegerField()
    mismatch_count = models.PositiveIntegerField()
    excel_file = models.FileField(upload_to=get_uploaded_excel_from_bank, max_length = 100)
    file_name = models.CharField(max_length=100, blank=True, null=True)  
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    
    
class BankTransaction(models.Model):
    bank_transaction_master = models.ForeignKey(BankTransactionMaster, on_delete=models.CASCADE)
    branch_code	= models.CharField(max_length=50)
    cmpny_code = models.CharField(max_length=50)
    trnsctn_nmbr = models.CharField(max_length=50)
    tranaction_id = models.CharField(max_length=20)
    transaction_pkey = models.CharField(max_length=50)
    salegroup_id = models.CharField(max_length=50)
    booth_code = models.CharField(max_length=10)
    customer_code = models.CharField(max_length=50)
    product_list = models.TextField()
    user_code = models.CharField(max_length=50)
    device_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True) 
    rid = models.CharField(max_length=50) 
    crn = models.CharField(max_length=50) 
    comission_amnt = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True) 
    commission_amount = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    cheque_number = models.CharField(max_length=50)
    cheque_date = models.DateTimeField(blank=True, null=True)
    bank_name = models.CharField(max_length=50)
    branch_name = models.CharField(max_length=50)
    transaction_mode = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    clrnce_date = models.DateTimeField(blank=True, null=True)
    crtd_date = models.DateTimeField(blank=True, null=True)
    settlement_date = models.DateTimeField(blank=True, null=True)
    athrsd_date = models.DateTimeField(blank=True, null=True)
    aggregrator = models.CharField(max_length=50, blank=True, null=True)
    settled = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    bank_date = models.CharField(max_length=50, blank=True, null=True)
    bank_date_one = models.DateTimeField(blank=True, null=True)
    bank_date_two = models.DateTimeField(blank=True, null=True)
    is_rid_matched = models.BooleanField(default=False)
    is_amount_matched = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class BankTransactionPaymentResponseMap(models.Model):
    bank_transaction_master = models.ForeignKey(BankTransactionMaster, on_delete=models.CASCADE)
    bank_transaction = models.ForeignKey(BankTransaction, on_delete=models.CASCADE)
    payment_response = models.ForeignKey(PaymentRequestResponse, on_delete=models.CASCADE)
    is_amount_matched = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class BankTransactionCarryForward(models.Model):
    bank_transaction_master = models.ForeignKey(BankTransactionMaster, on_delete=models.CASCADE, blank=True, null=True)
    payment_response = models.ForeignKey(PaymentRequestResponse, on_delete=models.CASCADE)
    bank_transaction_payment_response_map = models.ForeignKey(BankTransactionPaymentResponseMap, on_delete=models.CASCADE, blank=True, null=True)
    rid = models.CharField(max_length=50)
    crtd_date = models.DateTimeField(blank=True, null=True)
    is_carry_forward = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)