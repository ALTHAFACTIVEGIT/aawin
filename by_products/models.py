from main.models import *
from django.db import models
from django.contrib.auth.models import User


class ByProductUnit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=10)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.display_name)


# Create your models here.
class ByProductGroup(models.Model):
    name = models.CharField(max_length=60, unique=True)
    hsn_code = models.CharField(max_length=10, default=0)
    account_code = models.CharField(max_length=10, default=0)
    unit = models.ForeignKey(ByProductUnit, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # Ice cream, Ghee

    def __str__(self):
        return '{}'.format(self.name)


class ByProduct(models.Model):
    by_product_group = models.ForeignKey(ByProductGroup)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)
    code = models.CharField(max_length=30, unique=True)
    unit = models.ForeignKey(ByProductUnit)
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=9, decimal_places=3)
    base_price = models.DecimalField(max_digits=12, decimal_places=4)
    mrp = models.DecimalField(max_digits=12, decimal_places=4)
    is_refrigerated = models.BooleanField(default=False)
    igst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    cgst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    sgst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    minimum_quantity = models.PositiveIntegerField(default=1)
    display_ordinal = models.PositiveIntegerField()
    color = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("by_product_group", "name", "quantity", "unit"),)

    def __str__(self):
        return '{}'.format(self.short_name)


class GoodsReceiptRecordCodeBank(models.Model):
    last_digit = models.CharField(max_length=15)
    code_prefix = models.CharField(max_length=15, blank=True, null=True)
    code_suffix = models.CharField(max_length=15, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GoodsReceiptMasterCodeBank(models.Model):
    last_digit = models.CharField(max_length=15)
    temp_last_digit = models.CharField(max_length=15)
    code_prefix = models.CharField(max_length=15, blank=True, null=True)
    code_suffix = models.CharField(max_length=15, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PurchaseCompany(models.Model):
    company_name = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GoodsReceiptMaster(models.Model):
    grn_number = models.CharField(max_length=15)
    grn_date = models.DateTimeField()
    bill_number = models.CharField(max_length=50, blank=True, null=True)
    bill_date = models.DateTimeField()
    purchase_company = models.ForeignKey(PurchaseCompany, blank=True, null=True)
    po_number = models.CharField(max_length=50, blank=True, null=True)
    po_date = models.DateTimeField(blank=True, null=True)
    dc_number = models.CharField(max_length=50, blank=True, null=True)
    dc_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='goods_receipt_master_created_by')
    modified_by = models.ForeignKey(User, related_name='goods_receipt_master_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GoodsReceiptRecord(models.Model):
    goods_receipt_master = models.ForeignKey(GoodsReceiptMaster)
    by_product = models.ForeignKey(ByProduct)
    quantity_at_receipt = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_now = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_now_time = models.DateTimeField()
    expiry_date = models.DateTimeField(blank=True, null=True)
    goods_receipt_code = models.CharField(max_length=15)
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    igst_value = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    cgst_value = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    sgst_value = models.DecimalField(max_digits=10, decimal_places=5, default=0)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, related_name='goods_receipt_created_by')
    modified_by = models.ForeignKey(User, related_name='goods_receipt_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GoodsReceiptRecordForDaily(models.Model):
    sale_date = models.DateField()
    by_product = models.ForeignKey(ByProduct)
    grn_number = models.CharField(max_length=15)
    quantity_at_receipt = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_now = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_now_time = models.DateTimeField()
    price_per_unit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class DailySaleCloseTrace(models.Model):
    sale_date = models.DateField()
    is_sale_closed = models.BooleanField(default=False)
    closed_by = models.ForeignKey(User, related_name='sale_closed_by', blank=True, null=True)
    opened_by = models.ForeignKey(User, related_name='sale_opened_by', blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    opened_at = models.DateTimeField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ByProductCurrentAvailablity(models.Model):
    by_product = models.ForeignKey(ByProduct)
    quantity_now = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_now_time = models.DateTimeField()
    created_by = models.ForeignKey(User, related_name='temp_goods_receipt_created_by')
    modified_by = models.ForeignKey(User, related_name='temp_goods_receipt_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



# By product agent order table.
class ByProductBusinessTypeConcessionMap(models.Model):
    by_product = models.ForeignKey(ByProduct)
    business_type = models.ForeignKey(BusinessType)
    concession_type = models.ForeignKey(ConcessionType)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class BusinessTypeWiseByProductDiscount(models.Model):
    by_product = models.ForeignKey(ByProduct)
    business_type = models.ForeignKey(BusinessType)
    base_price = models.DecimalField(max_digits=12, decimal_places=5, default=0)
    igst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    cgst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    sgst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    mrp = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    created_by = models.ForeignKey(User, related_name="business_type_wise_by_product_discount_created_by")
    modified_by = models.ForeignKey(User, related_name="business_type_wise_by_product_discount_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessTypeWiseByProductDiscountTrace(models.Model):
    business_type_wise_discount = models.ForeignKey(BusinessTypeWiseByProductDiscount)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    igst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    cgst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    sgst_amount = models.DecimalField(max_digits=7, decimal_places=4, default=0)
    mrp = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    product_discount_started_by = models.ForeignKey(User, related_name='business_type_wise_by_product_discount_start_date_created_by')
    product_discount_ended_by = models.ForeignKey(User, related_name='business_type_wise_by_product_discount_end_date_created_by', blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessWiseByProductDiscount(models.Model):
    by_product = models.ForeignKey(ByProduct)
    business = models.ForeignKey(Business)
    discounted_price = models.DecimalField(max_digits=9, decimal_places=2)
    created_by = models.ForeignKey(User, related_name="business_wise_by_product_discount_created_by")
    modified_by = models.ForeignKey(User, related_name="business_wise_by_product_discount_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessWiseByProductDiscountTrace(models.Model):
    business_wise_discount = models.ForeignKey(BusinessWiseByProductDiscount)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_discount_started_by = models.ForeignKey(User, related_name='business_type_by_product_discount_start_date_created_by')
    product_discount_ended_by = models.ForeignKey(User, related_name='business_type_by_product_discount_end_date_created_by', blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SaleStatusForByProduct(models.Model):
    name = models.CharField(max_length=70, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class BySaleGroupOrderCodeBank(models.Model):
    last_digit = models.CharField(max_length=15)
    code_prefix = models.CharField(max_length=15, blank=True, null=True)
    code_suffix = models.CharField(max_length=15, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BySaleGroupPaymentMethod(models.Model):
    name = models.CharField(max_length=70, unique=True)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    #cash, # dd, #Cheque

class BySaleGroup(models.Model):
    business = models.ForeignKey(Business)
    order_code = models.CharField(max_length=15, unique=True)
    zone = models.ForeignKey(Zone)
    ordered_date = models.DateField(db_index=True)
    ordered_via = models.ForeignKey(OrderedVia)
    value_before_round_off = models.DecimalField(max_digits=12, decimal_places=4)
    round_off_value = models.DecimalField(max_digits=12, decimal_places=4)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatusForByProduct)
    payment_method = models.ForeignKey(BySaleGroupPaymentMethod, blank=True, null=True)
    ordered_by = models.ForeignKey(User, related_name='by_product_sale_group_created_by')
    modified_by = models.ForeignKey(User, related_name='by_product_sale_group_modified_by')
    payment_status = models.ForeignKey(PaymentStatus)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("business", "order_code"),)

class BySale(models.Model):
    by_sale_group = models.ForeignKey(BySaleGroup)
    by_product = models.ForeignKey(ByProduct)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=12, decimal_places=4)
    cgst_value = models.DecimalField(max_digits=12, decimal_places=4)
    sgst_value = models.DecimalField(max_digits=12, decimal_places=4)
    total_cost = models.DecimalField(max_digits=12, decimal_places=4)
    ordered_by = models.ForeignKey(User, related_name='by_product_sale_ordered_by')
    modified_by = models.ForeignKey(User, related_name='by_product_sale_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("by_sale_group", "by_product"),)

class TempBySaleGroupOrderCodeBank(models.Model):
    last_digit = models.CharField(max_length=15)
    code_prefix = models.CharField(max_length=15, blank=True, null=True)
    code_suffix = models.CharField(max_length=15, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class TempBySaleGroup(models.Model):
    business = models.ForeignKey(Business)
    order_code = models.CharField(max_length=15, unique=True)
    zone = models.ForeignKey(Zone)
    ordered_date = models.DateField(db_index=True)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatusForByProduct)
    ordered_by = models.ForeignKey(User, related_name='by_product_temp_sale_group_created_by')
    modified_by = models.ForeignKey(User, related_name='by_product_temp_sale_group_modified_by')
    payment_status = models.ForeignKey(PaymentStatus)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("business", "order_code"),)

class TempBySale(models.Model):
    temp_by_sale_group = models.ForeignKey(TempBySaleGroup)
    by_product = models.ForeignKey(ByProduct)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='by_product_temp_sale_ordered_by')
    modified_by = models.ForeignKey(User, related_name='by_product_temp_sale_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("temp_by_sale_group", "by_product"),)

class BySaleGroupPaymentRequestMap(models.Model):
    by_sale_group = models.ManyToManyField(BySaleGroup)
    temp_sale_group = models.ManyToManyField(TempBySaleGroup)
    payment_request = models.ForeignKey(PaymentRequest)
    is_done = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    

class PaymentOption(models.Model):
    name = models.CharField(max_length=50, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    #cash, credit
    def __str__(self):
        return '{}'.format(self.name)

class OrderCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    #product , by_product
    def __str__(self):
        return '{}'.format(self.name)

class BusinessTypeOrderCategoryeMap(models.Model):
    business_type = models.ForeignKey(BusinessType)
    order_category = models.ForeignKey(OrderCategory)
    payment_option = models.ForeignKey(PaymentOption)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ByProductAgentWallet(models.Model):
    agent = models.OneToOneField(Agent)
    current_balance = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CounterEmployeeTraceBySaleGroupMap(models.Model):
    counter_employee_trace = models.ForeignKey(CounterEmployeeTraceMap)
    by_sale_group = models.ManyToManyField(BySaleGroup)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ByProductTransactionLog(models.Model):
    date = models.DateField()
    transacted_by = models.ForeignKey(User, related_name='by_product_agent_user_id')
    data_entered_by = models.ForeignKey(User, related_name='by_product_transaction_initiated_user')
    transacted_via = models.ForeignKey(TransactedVia)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_direction = models.ForeignKey(TransactionDirection)
    transaction_id = models.CharField(max_length=20, null=True, blank=True)
    transaction_mode = models.ForeignKey(TransactionMode)
    transaction_status = models.ForeignKey(TransactionStatus)
    transaction_approval_status = models.ForeignKey(TransactionApprovalStatus)
    transaction_approved_by = models.ForeignKey(User, related_name='by_product_transaction_approved_by')
    transaction_approved_time = models.DateTimeField()
    wallet_balance_before_this_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_balance_after_transaction_approval = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    cheque_detail = models.ForeignKey(TransactionChequeDetails, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='by_product_transaction_log_modified_by')


class BySaleGroupTransactionTrace(models.Model):
    by_sale_group = models.ForeignKey(BySaleGroup)
    sale_group_order_type = models.ForeignKey(SaleGroupOrderType)
    counter_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transacted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet_return_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_transaction = models.ForeignKey(ByProductTransactionLog, related_name='by_product_bank_transaction_log', blank=True, null=True)
    wallet_transaction = models.ForeignKey(ByProductTransactionLog, related_name='by_product_wallet_transaction_log',  blank=True, null=True)
    counter_transaction = models.ForeignKey(ByProductTransactionLog, related_name='by_product_counter_transaction_log', blank=True, null=True)
    wallet_return_transaction = models.ForeignKey(ByProductTransactionLog, related_name='by_product_wallet_return_transaction_log', blank=True, null=True)
    is_wallet_used = models.BooleanField(default=False)
    order_sale_group_json = models.TextField(blank=True, null=True)
    counter = models.ForeignKey(Counter, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GoodsReceiptRecordBySaleMap(models.Model):
    goods_receipt_record = models.ForeignKey(GoodsReceiptRecord)
    by_sale = models.ForeignKey(BySale)
    quantity_dispatched = models.DecimalField(max_digits=9, decimal_places=2)
    cost = models.DecimalField(max_digits=12, decimal_places=4)
    cgst_value = models.DecimalField(max_digits=12, decimal_places=4)
    sgst_value = models.DecimalField(max_digits=12, decimal_places=4)
    total_cost = models.DecimalField(max_digits=12, decimal_places=4)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class DailyGoodsReceiptRecordBySaleMap(models.Model):
    daily_goods_receipt_record = models.ForeignKey(GoodsReceiptRecordForDaily)
    by_sale = models.ForeignKey(BySale)
    quantity_dispatched = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    

def get_agent_by_product_gatepass(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)

def get_agent_by_product_gatepass_now(instance, filename):
    return "by_product/gate_pass/{business_code}/{order_code}/for_now/{file}".format(business_code=instance.by_sale_group.business.code, order_code=instance.by_sale_group.order_code, file=filename)

def get_agent_by_product_gatepass_for_future(instance, filename):
    return "by_product/gate_pass/{business_code}/{order_code}/for_future/{file}".format(business_code=instance.by_sale_group.business.code, order_code=instance.by_sale_group.order_code, file=filename)


def get_agent_by_product_gatepass_dc(instance, filename):
    return "by_product/gate_pass/{business_code}/{order_code}/dc/{file}".format(business_code=instance.by_sale_group.business.code, order_code=instance.by_sale_group.order_code, file=filename)

def get_agent_by_product_gatepass_bill(instance, filename):
    return "by_product/gate_pass/{business_code}/{order_code}/bill/{file}".format(business_code=instance.by_sale_group.business.code, order_code=instance.by_sale_group.order_code, file=filename)

def get_agent_by_product_cash_receipt(instance, filename):
    return "by_product/gate_pass/{business_code}/{order_code}/cash_receipt/{file}".format(business_code=instance.by_sale_group.business.code, order_code=instance.by_sale_group.order_code, file=filename)

def get_agent_by_product_gatepass_dc_for_employee_order(instance, filename):
    return "by_product/gate_pass/{business_code}/{order_code}/temp_dc/{file}".format(business_code=instance.by_sale_group.business.code, order_code=instance.by_sale_group.order_code, file=filename)


class CashReceiptAccountMaster(models.Model):
    account_name = models.CharField(max_length=100)
    account_code = models.CharField(max_length=15)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CashReceiptAccountPaymentMethodMap(models.Model):
    payment_method = models.ForeignKey(BySaleGroupPaymentMethod)
    cash_receipt_account_master = models.ForeignKey(CashReceiptAccountMaster)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BySaleGroupCashReceipt(models.Model):
    by_sale_group = models.ForeignKey(BySaleGroup)
    receipt_number = models.CharField(max_length=15)
    receipt_date = models.DateTimeField()
    receipt_file = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_agent_by_product_cash_receipt)
    prepared_by = models.ForeignKey(User)
    prepated_at = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class BySaleGroupGatepass(models.Model):
    by_sale_group = models.ForeignKey(BySaleGroup)
    dc_number = models.CharField(max_length=15)
    dc_date = models.DateTimeField()
    bill_number = models.CharField(max_length=15)
    bill_date = models.DateTimeField()
    dc_file = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_agent_by_product_gatepass_dc)
    bill_file = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_agent_by_product_gatepass_bill)
    prepared_by = models.ForeignKey(User)
    prepated_at = models.DateTimeField()
    is_vehicle_gatepass_taken = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CashReceiptCodeBank(models.Model):
    last_digit = models.CharField(max_length=15)
    code_prefix = models.CharField(max_length=15, blank=True, null=True)
    code_suffix = models.CharField(max_length=15, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GatepassDCCodeBank(models.Model):
    last_digit = models.CharField(max_length=15)
    code_prefix = models.CharField(max_length=15, blank=True, null=True)
    code_suffix = models.CharField(max_length=15, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GatepassBillCodeBank(models.Model):
    last_digit = models.CharField(max_length=15)
    code_prefix = models.CharField(max_length=15, blank=True, null=True)
    code_suffix = models.CharField(max_length=15, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class EmployeeOrderBySaleGroup(models.Model):
    business = models.ForeignKey(Business)
    order_code = models.CharField(max_length=15, unique=True)
    zone = models.ForeignKey(Zone)
    ordered_date = models.DateField(db_index=True)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatusForByProduct)
    ordered_by = models.ForeignKey(User, related_name='by_product_employee_order_sale_group_created_by')
    modified_by = models.ForeignKey(User, related_name='by_product_employee_order_sale_group_modified_by')
    payment_status = models.ForeignKey(PaymentStatus)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("business", "order_code"),)

class EmployeeOrderBySale(models.Model):
    employeee_order_by_sale_group = models.ForeignKey(EmployeeOrderBySaleGroup)
    by_product = models.ForeignKey(ByProduct)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='by_product_employee_order_sale_ordered_by')
    modified_by = models.ForeignKey(User, related_name='by_product_employee_order_sale_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("employeee_order_by_sale_group", "by_product"),)


class EmployeeReturnBySaleGroup(models.Model):
    employeee_order_by_sale_group = models.ForeignKey(EmployeeOrderBySaleGroup)
    business = models.ForeignKey(Business)
    zone = models.ForeignKey(Zone)
    ordered_date = models.DateField(db_index=True)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatusForByProduct)
    ordered_by = models.ForeignKey(User, related_name='by_product_employee_return_sale_group_created_by')
    modified_by = models.ForeignKey(User, related_name='by_product_employee_return_sale_group_modified_by')
    payment_status = models.ForeignKey(PaymentStatus)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("business", "employeee_order_by_sale_group"),)

class EmployeeReturnBySale(models.Model):
    employeee_return_by_sale_group = models.ForeignKey(EmployeeReturnBySaleGroup)
    by_product = models.ForeignKey(ByProduct)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='by_product_employee_return_sale_ordered_by')
    modified_by = models.ForeignKey(User, related_name='by_product_employee_return_sale_modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("employeee_return_by_sale_group", "by_product"),)

class EmployeeOrderBySaleGroupGatepass(models.Model):
    employeee_order_by_sale_group = models.ForeignKey(EmployeeOrderBySaleGroup)
    dc_number = models.CharField(max_length=15)
    dc_date = models.DateTimeField()
    bill_number = models.CharField(max_length=15)
    bill_date = models.DateTimeField()
    dc_file = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_agent_by_product_gatepass_dc_for_employee_order)
    bill_file = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_agent_by_product_gatepass_bill)
    prepared_by = models.ForeignKey(User)
    prepated_at = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GoodsReceiptRecordEmployeeOrderBySaleMap(models.Model):
    goods_receipt_record = models.ForeignKey(GoodsReceiptRecord)
    employee_order_by_sale = models.ForeignKey(EmployeeOrderBySale)
    quantity_dispatched = models.DecimalField(max_digits=9, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class BusinessWiseDailySaleUpdate(models.Model):
    business = models.ForeignKey(Business)
    sale_date = models.DateField(db_index=True)
    by_product = models.ForeignKey(ByProduct)
    opening_quantity = models.PositiveIntegerField(default=0)
    received_quantity = models.PositiveIntegerField(default=0)
    sales_quantity = models.PositiveIntegerField(default=0)
    closing_quantity = models.PositiveIntegerField(blank=True, null=True)
    is_yesterday_sale_closed = models.BooleanField(default=False)
    is_edit_expired = models.BooleanField(default=False)
    edit_expiry_time = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='sale_created_by')
    updated_by = models.ForeignKey(User, related_name='sale_updated_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessWiseDailySaleEditTrace(models.Model):
    business = models.ForeignKey(Business)
    sale_date = models.DateField(db_index=True)
    by_product = models.ForeignKey(ByProduct)
    opening_quantity = models.PositiveIntegerField(default=0)
    old_opening_quantity = models.PositiveIntegerField(default=0)
    received_quantity = models.PositiveIntegerField(default=0)
    old_received_quantity = models.PositiveIntegerField(default=0)
    sales_quantity = models.PositiveIntegerField(default=0)
    old_sales_quantity = models.PositiveIntegerField(default=0)
    closing_quantity = models.PositiveIntegerField(blank=True, null=True)
    old_closing_quantity = models.PositiveIntegerField(blank=True, null=True)
    edited_by = models.ForeignKey(User, related_name='daily_sale_edited_by')
    edited_at = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class VehicleMaster(models.Model):
    driver_name = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=15)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_vehicle_gatepass(instance, filename):
    return "by_product/gate_pass/{business_code}/{order_code}/cash_receipt/{file}".format(business_code=instance.by_sale_group.business.code, order_code=instance.by_sale_group.order_code, file=filename)


# we split vehicle details in another table because in future aavin will ask for dropdown option so we can seperate we can adout their need.
class VehicleGatepass(models.Model):
    vehicle = models.ForeignKey(VehicleMaster)
    vehicle_start_time = models.TimeField()
    order_from = models.DateField()
    order_to = models.DateField()
    by_sale_group_gate_pass = models.ManyToManyField(BySaleGroupGatepass)
    gatepass_file = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_vehicle_gatepass)
    prepared_by = models.ForeignKey(User)
    prepared_at = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BySaleGroupDeleteLog(models.Model):
    business = models.ForeignKey(Business)
    ordered_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='by_sale_group_order_placed_by')
    ordered_date_time = models.DateTimeField()
    deleted_by = models.ForeignKey(User, related_name='by_sale_group_order_deleted_by')
    delete_date_time = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



