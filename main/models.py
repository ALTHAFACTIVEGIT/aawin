from django.db import models
from django.contrib.auth.models import User
import datetime

from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey


class State(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class District(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    capital = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Taluk(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Block(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Constituency(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class Pincode(models.Model):
    taluk = models.ForeignKey(Taluk)
    value = models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class CorporationZone(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)



class Ward(models.Model):
    constituency = models.ForeignKey(Constituency)
    corporation_zone = models.ForeignKey(CorporationZone)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class UserTypePermission(models.Model):
    name = models.CharField(max_length=300)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Gender(models.Model):
    name = models.CharField(max_length=20)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class Union(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Office(models.Model):
    union = models.ForeignKey(Union)
    name = models.CharField(max_length=200)
    street = models.TextField(blank=True, null=True)
    taluk = models.ForeignKey(Taluk)
    district = models.ForeignKey(District)
    state = models.ForeignKey(State)
    mobile = models.CharField(max_length=13)
    alternate_mobile = models.CharField(max_length=13, null=True, blank=True)
    phone = models.CharField(max_length=13, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Zone(models.Model):
    union = models.ForeignKey(Union)
    name = models.CharField(max_length=100, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class UserType(models.Model):
    name = models.CharField(max_length=100)
    notes = models.CharField(max_length=250)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # Employee, customer, agent

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


def get_user_profile_image(instance, filename):
    return "profile_picture/{user_type}/{user_name}/{file}".format(user_type=instance.user_type.name,user_name=instance.user.username, file=filename)


class UserProfile(models.Model):
    union = models.ForeignKey(Union)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.ForeignKey(UserType)
    street = models.TextField(blank=True, null=True)
    gender = models.ForeignKey(Gender)
    taluk = models.ForeignKey(Taluk)
    district = models.ForeignKey(District)
    state = models.ForeignKey(State)
    mobile = models.CharField(max_length=13)
    alternate_mobile = models.CharField(max_length=13, null=True, blank=True)


    pincode = models.IntegerField(blank=True, null=True)
    image = models.ImageField(max_length=1000, upload_to=get_user_profile_image, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    phone = models.CharField(max_length=13, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


    def __str__(self):
        return '{} - {}'.format(self.id, self.user.username)


class EmployeeRole(models.Model):
    name = models.CharField(max_length=50)
    hierarchial_level = models.PositiveIntegerField() # 10, 20, 30,  40
    notes = models.CharField(max_length=250)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # GM, AGM , Manager

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)

class BusinessGroup(models.Model):
    name = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)

class Employee(models.Model):
    user_profile = models.OneToOneField(UserProfile)
    office = models.ForeignKey(Office)
    role = models.ForeignKey(EmployeeRole)
    business_group = models.ForeignKey(BusinessGroup, blank=True, null=True)
    joining_date = models.DateTimeField()
    release_date = models.DateTimeField(blank=True, null=True)
    is_retired = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.id)


class EmployeeTypePermissionMap(models.Model):
    employee_role = models.ForeignKey(EmployeeRole)
    permission = models.ForeignKey(UserTypePermission)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class EmployeeZoneResponsibility(models.Model):
    employee = models.ForeignKey(Employee)
    zone = models.ForeignKey(Zone)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class UserHistoryTrace(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user')
    to_user = models.ForeignKey(User, related_name='to_user')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_agent_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)


def get_agent_aadhar_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)


class RelationType(models.Model):
    name = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class KycIDProofDocumentType(models.Model):
    name = models.CharField(max_length=50)
    # aadhar, ration card, bank account number, voter id,  PAN, DL, passport


def get_agent_user_profile_image(instance, filename):
    return "profile_picture/agent/{mobile}/{file}".format(mobile=instance.mobile, file=filename)

class AgentProfile(models.Model):
    union = models.ForeignKey(Union)
    street = models.TextField(blank=True, null=True)
    gender = models.ForeignKey(Gender)
    taluk = models.ForeignKey(Taluk)
    district = models.ForeignKey(District)
    state = models.ForeignKey(State)
    mobile = models.CharField(max_length=13)
    alternate_mobile = models.CharField(max_length=13, null=True, blank=True)
    pincode = models.IntegerField(blank=True, null=True)
    image = models.ImageField(max_length=1000, upload_to=get_agent_user_profile_image, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    phone = models.CharField(max_length=13, blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="agent_profile_created_by")
    modified_by = models.ForeignKey(User, related_name="agent_profile_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class Agent(models.Model):
    agent_profile = models.ForeignKey(AgentProfile, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    agent_code = models.CharField(max_length=13, unique=True)
    relation_type = models.ForeignKey(RelationType, blank=True, null=True)
    relation_name = models.CharField(max_length=50, blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    is_mobile_number_verified_by_agent = models.BooleanField(default=False)
    aadhar_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_agent_aadhar_image)
    pan_number = models.CharField(max_length=12, blank=True, null=True)
    ration_card_number = models.CharField(max_length=12, blank=True, null=True)
    # image = models.ImageField(max_length=1000, upload_to=get_agent_image)
    communication_address = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="agent_details_created_by")
    modified_by = models.ForeignKey(User, related_name="agent_details_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.id)






class AgentBankDetail(models.Model):
    agent = models.OneToOneField(Agent)
    bank = models.CharField(max_length=150)
    branch = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)
    micr_code = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=50, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class LocationCategory(models.Model):
    name = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # panchayat, Corporation


class BusinessType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    finance_main_code = models.CharField(max_length=15)
    display_ordinal = models.PositiveIntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)

class ProductGroup(models.Model):
    name = models.CharField(max_length=60, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # milk, gee

    def __str__(self):
        return '{}'.format(self.name)

class Business(models.Model):
    code = models.CharField(max_length=13, unique=True)
    account_code = models.CharField(max_length=13, unique=True, blank=True, null=True)
    zone = models.ForeignKey(Zone)
    business_type = models.ForeignKey(BusinessType)
    business_group = models.ForeignKey(BusinessGroup, blank=True, null=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, null=True)
    constituency = models.ForeignKey(Constituency)
    ward = models.ForeignKey(Ward)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    is_working_now = models.BooleanField(default=True)
    is_rural = models.BooleanField()
    is_urban = models.BooleanField()
    location_category = models.ForeignKey(LocationCategory)
    location_category_value = models.CharField(max_length=50)
    pincode = models.IntegerField()
    landmark = models.CharField(max_length=50)
    working_hours_from = models.TimeField()
    working_hours_to = models.TimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="business_created_by")
    modified_by = models.ForeignKey(User, related_name="business_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.id)


class InstititionBillNumberIdBank(models.Model):
    last_count = models.CharField(max_length=15)
    date = models.DateField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessWiseBillNumber(models.Model):
    business = models.ForeignKey(Business)
    from_date = models.DateField()
    to_date = models.DateField()
    product_group_type = models.ForeignKey(ProductGroup)
    bill_number = models.CharField(max_length=15)
    created_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    
class AgentWallet(models.Model):
    agent = models.OneToOneField(Agent)
    current_balance = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_booth_nominee_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)


class Nominee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    relation_type = models.ForeignKey(RelationType)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    phone = models.CharField(max_length=13, blank=True, null=True)
    image = models.ImageField(max_length=1000, upload_to=get_booth_nominee_image)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_agent_deposit_receipt_image(instance, filename):
    return "{id}/{file}".format(id=instance.id, file=filename)


class DepositStatus(models.Model):
    name = models.CharField(max_length=100)


class BusinessAgentMap(models.Model):
    agent = models.ForeignKey(Agent)
    business = models.ForeignKey(Business)
    is_active = models.BooleanField(default=True)
    active_from = models.DateField()
    active_to = models.DateField(blank=True, null=True)
    nominee = models.ForeignKey(Nominee)
    deposit_date = models.DateTimeField()
    deposit_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    deposit_status = models.ForeignKey(DepositStatus)
    deposit_status_description = models.TextField()
    deposit_receipt_image = models.ImageField(max_length=1000, upload_to=get_agent_deposit_receipt_image)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessCodeBank(models.Model):
    business_type = models.ForeignKey(BusinessType)
    from_code = models.CharField(max_length=10)
    to_code = models.CharField(max_length=10)
    last_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomerType(models.Model):
    name = models.CharField(max_length=50)
    milk_limit = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class IcustomerIdBank(models.Model):
    last_count = models.CharField(max_length=10)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class createdVia(models.Model):
    name = models.CharField(max_length=70, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # via mobile, via portal,
    

def get_icustomer_aadhar_image(instance, filename):
    return "icustomer_aadhar_image/{customer_type}/{file}".format(customer_type=instance.customer_type, file=filename)


class UnionForIcustomer(models.Model):
    name = models.CharField(max_length=40)
    short_name = models.CharField(max_length=40, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomer(models.Model):
    customer_code = models.CharField(max_length=13, unique=True)
    customer_type = models.ForeignKey(ICustomerType)
    business = models.ForeignKey(Business,  blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_mobile_number_verified_by_customer = models.BooleanField(default=False)
    is_aadhar_number_verified_by_customer = models.BooleanField(default=False)
    is_business_approved = models.BooleanField(default=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    aadhar_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_icustomer_aadhar_image)
    date_of_birth = models.DateField(blank=True, null=True)
    created_via = models.ForeignKey(createdVia, blank=True, null=True)
    kyc_idproof_document_type = models.ForeignKey(KycIDProofDocumentType, blank=True, null=True)
    kyc_idproof_document_value = models.CharField(max_length=25, blank=True, null=True)
    union_for_icustomer = models.ForeignKey(UnionForIcustomer, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.id)


class ICustomerSmartCard(models.Model):
    icustomer = models.ForeignKey(ICustomer)
    date = models.DateField()
    otp = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SmartCardOrderExpiry(models.Model):
    old_customer_date = models.PositiveSmallIntegerField()
    new_customer_date = models.PositiveSmallIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomerWallet(models.Model):
    customer = models.OneToOneField(ICustomer)
    current_balance = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ProductSubGroup(models.Model):
    name = models.CharField(max_length=60, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ProductUnit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=10)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.display_name)


def get_product_image(instance, filename):
    return "product/{product_name}/{file}".format(product_name=instance.name, file=filename)


class Product(models.Model):
    group = models.ForeignKey(ProductGroup)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)
    code = models.CharField(max_length=30)
    unit = models.ForeignKey(ProductUnit)
    display_ordinal = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=9, decimal_places=3)
    base_price = models.DecimalField(max_digits=9, decimal_places=2)
    color = models.CharField(max_length=10, blank=True, null=True)
    image = models.ImageField(max_length=1000, upload_to=get_user_profile_image, blank=True, null=True)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    snf = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fat = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_homogenised = models.BooleanField(default=True)
    # display_ordinal = models.PositiveIntegerField()
    # smart_card_price = models.DecimalField(max_digits=9, decimal_places=2)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    minimum_quantity = models.PositiveIntegerField(default=1)
    private_institute_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    govt_institute_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    society_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    hsn_code = models.CharField(max_length=10, blank=True, null=True)
    igst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("group", "name", "quantity", "unit"),)

    def __str__(self):
        return '{} -{}'.format(self.short_name, self.unit.display_name)


class ProductFinanceCodeMap(models.Model):
    group_name = models.CharField(max_length=15)
    finance_product_code = models.CharField(max_length=15)
    product = models.ManyToManyField(Product)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ProductProductSubGroupMap(models.Model):
    product = models.ForeignKey(Product)
    product_sub_group = models.ForeignKey(ProductSubGroup)


class ProductQuantityVariationPrice(models.Model):
    product = models.ForeignKey(Product)
    min_quantity = models.DecimalField(max_digits=9, decimal_places=3)
    max_quantity = models.DecimalField(max_digits=9, decimal_places=3)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.product.name, self.min_quantity, self.max_quantity)


class ProductQuantityVariationPriceTrace(models.Model):
    product_quantity_variation_price = models.ForeignKey(ProductQuantityVariationPrice)
    product = models.ForeignKey(Product)
    min_quantity = models.DecimalField(max_digits=9, decimal_places=3)
    max_quantity = models.DecimalField(max_digits=9, decimal_places=3)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    product_price_started_by = models.ForeignKey(User, related_name='product_quantity_variation_price_start_date_created_by')
    product_price_ended_by = models.ForeignKey(User, related_name='product_quantity_variation_price_end_date_created_by', null=True,
                                               blank=True)


class ProductTrace(models.Model):
    product = models.ForeignKey(Product)
    start_date = models.DateTimeField()
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)
    code = models.CharField(max_length=30)
    unit = models.ForeignKey(ProductUnit)
    quantity = models.DecimalField(max_digits=9, decimal_places=3)
    base_price = models.DecimalField(max_digits=9, decimal_places=2)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fat = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_homogenised = models.BooleanField(default=True)
    end_date = models.DateTimeField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    product_price_started_by = models.ForeignKey(User, related_name='product_price_start_date_created_by')
    product_price_ended_by = models.ForeignKey(User, related_name='product_price_end_date_created_by', null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.product.name, self.mrp)


class IcustomerProductMap(models.Model):
    product = models.ForeignKey(Product)
    icustomer = models.ForeignKey(ICustomer)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ConcessionType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # Commission, Discount

    def __str__(self):
        return '{}'.format(self.name)


class BusinessProductConcessionMap(models.Model):
    product = models.ForeignKey(Product)
    business_type = models.ForeignKey(BusinessType)
    concession_type = models.ForeignKey(ConcessionType)

    def __str__(self):
        return '{} - {}'.format(self.business_type.name, self.product.name, )


class BusinessTypeWiseProductCommission(models.Model):
    product = models.ForeignKey(Product)
    business_type = models.ForeignKey(BusinessType)
    commission_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name="business_type_wise_product_commission_created_by")
    modified_by = models.ForeignKey(User, related_name="business_type_wise_product_commission_modified_by")


class BusinessTypeWiseProductCommissionTrace(models.Model):
    business_type_wise_commission = models.ForeignKey(BusinessTypeWiseProductCommission)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    commission_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    product_commission_started_by = models.ForeignKey(User, related_name='product_commission_start_date_created_by')
    product_commission_ended_by = models.ForeignKey(User, related_name='product_commission_end_date_created_by', blank=True, null=True)


class BusinessTypeWiseProductDiscount(models.Model):
    product = models.ForeignKey(Product)
    business_type = models.ForeignKey(BusinessType)
    discounted_price = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="business_type_wise_product_discount_created_by")
    modified_by = models.ForeignKey(User, related_name="business_type_wise_product_discount_modified_by")


class BusinessTypeWiseProductDiscountTrace(models.Model):
    business_type_wise_discount = models.ForeignKey(BusinessTypeWiseProductDiscount)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    product_discount_started_by = models.ForeignKey(User, related_name='business_type_wise_product_discount_start_date_created_by')
    product_discount_ended_by = models.ForeignKey(User, related_name='business_type_wise_product_discount_end_date_created_by', blank=True, null=True)


class BusinessWiseProductDiscount(models.Model):
    product = models.ForeignKey(Product)
    business = models.ForeignKey(Business)
    discounted_price = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="business_wise_product_discount_created_by")
    modified_by = models.ForeignKey(User, related_name="business_wise_product_discount_modified_by")


class BusinessWiseProductDiscountTrace(models.Model):
    business_wise_discount = models.ForeignKey(BusinessWiseProductDiscount)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    product_discount_started_by = models.ForeignKey(User, related_name='business_type_product_discount_start_date_created_by')
    product_discount_ended_by = models.ForeignKey(User, related_name='business_type_product_discount_end_date_created_by', blank=True, null=True)


class ICustomerTypeWiseProductDiscount(models.Model):
    product = models.ForeignKey(Product)
    customer_type = models.ForeignKey(ICustomerType)
    discounted_price = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name="customer_product_discount_created_by")
    modified_by = models.ForeignKey(User, related_name="customer_product_discount_modified_by")

    def __str__(self):
        return '{} - {}'.format(self.customer_type.name, self.product.name)


class ICustomerTypeWiseProductDiscountTrace(models.Model):
    icustomer_type_wiser_product_discount = models.ForeignKey(ICustomerTypeWiseProductDiscount)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=9, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    product_discount_started_by = models.ForeignKey(User, related_name='icustomer_product_discount_start_date_created_by')
    product_discount_ended_by = models.ForeignKey(User, related_name='icustomer_product_product_discount_end_date_created_by', blank=True, null=True)


class VehicleTransport(models.Model):
    name = models.CharField(max_length=300)
    contact_person = models.CharField(max_length=50)
    mobile = models.CharField(max_length=13)
    alternate_mobile = models.CharField(max_length=13, null=True, blank=True)
    address = models.TextField()    
    latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # tata ace, echer


def get_fc_document(instance, filename):
    return "fc_document/{vehicle_code}/{file}".format(vehicle_code=instance.code, file=filename)


def get_insurance_document(instance, filename):
    return "insurance_document/{vehicle_code}/{file}".format(vehicle_code=instance.code, file=filename)


class Vehicle(models.Model):
    vehicle_transport = models.ForeignKey(VehicleTransport)
    contract_start_from = models.DateTimeField(null=True, blank=True)
    contract_ends_on = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=10)
    licence_number = models.CharField(max_length=15)
    vehicle_type = models.ForeignKey(VehicleType)
    driver_name = models.CharField(max_length=50)
    driver_mobile = models.CharField(max_length=13)
    capacity_in_kg = models.IntegerField()
    tray_capacity = models.IntegerField()
    fc_expiry_date = models.DateTimeField()
    insurance_expiry_date = models.DateTimeField()
    fc_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_fc_document)
    insurance_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_insurance_document)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.licence_number)


class Session(models.Model):
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=50)
    expiry_time = models.TimeField()
    expiry_day_before = models.IntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.display_name)


class ProductAvailabilityMap(models.Model):
    product = models.ForeignKey(Product)
    session = models.ForeignKey(Session)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return '{} - {}'.format(self.product.short_name, self.session.id)




# class ProductAvailabilityTrace(models.Model):
#     date = models.DateField()
#     session = models.ForeignKey(Session)
#     product = models.ForeignKey(Product)
#     is_available = models.BooleanField()
#     modified_by = models.ForeignKey(User, related_name="product availability changed by")
#     time_created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return '{} - {}'.format(self.product.name, self.session.id)


class Route(models.Model):
    name = models.CharField(max_length=60, unique=True)
    union = models.ForeignKey(Union)
    session = models.ForeignKey(Session)
    order_expiry_time = models.TimeField()
    reference_order_expiry_time = models.TimeField()
    departure_time = models.TimeField(blank=True, null=True)
    is_temp_route = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    leak_packet_in_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)


class RouteCity(models.Model):
    name = models.CharField(max_length=60, unique=True)
    display_ordinal = models.PositiveIntegerField(default=0)


class RouteGroupMap(models.Model):
    name = models.CharField(max_length=60, unique=True)
    full_name = models.CharField(max_length=60, unique=True)
    mor_route = models.ForeignKey(Route, related_name='mor_route', blank=True, null=True)
    eve_route = models.ForeignKey(Route, related_name='eve_route', blank=True, null=True)
    mor_temp_route = models.ForeignKey(Route, related_name='mor_temp_route', blank=True, null=True)
    eve_temp_route = models.ForeignKey(Route, related_name='eve_temp_route', blank=True, null=True)
    union = models.ForeignKey(Union)
    route_city = models.ForeignKey(RouteCity, blank=True, null=True)


# mapping main route with respected temp route
class RouteTempRouteMap(models.Model):
    main_route = models.ForeignKey(Route, related_name='main_route')
    temp_route = models.ForeignKey(Route, related_name='temp_route_of_main_route')
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class RouteBusinessMap(models.Model):
    route = models.ForeignKey(Route)
    business = models.ForeignKey(Business)
    ordinal = models.PositiveIntegerField(default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.route.name, self.business.name)


class IndentStatus(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return '{}'.format(self.name)
    # initiated, closed


# if the destination path is changed , do update in pdf generate path also in script(file_name: pdf_generate.py, function: generate_pdf)
def get_route_trace_indent_document(instance, filename):
    return "indent_document/{date}/{session}/{route}".format(date=instance.date, session=instance.session.name, route=instance.indent_number,file=filename)


class RouteTrace(models.Model):
    indent_number = models.CharField(max_length=30, blank=True, null=True)
    indent_status = models.ForeignKey(IndentStatus)
    indent_prepare_date_time = models.DateTimeField(blank=True, null=True)
    indent_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_route_trace_indent_document)
    route = models.ForeignKey(Route)
    vehicle = models.ForeignKey(Vehicle)
    date = models.DateField()
    session = models.ForeignKey(Session)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=13)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_overall_indent_document(instance, filename):
    return "indent_document/{date}/{session_id}/overall".format(date=instance.date, session=instance.session.name, file=filename)


class OverallIndentPerSession(models.Model):
    date = models.DateField()
    session = models.ForeignKey(Session)
    overall_indent_status = models.ForeignKey(IndentStatus)
    route_trace = models.ManyToManyField(RouteTrace)
    overall_indent_document = models.FileField(max_length=1000, blank=True, null=True, upload_to=get_overall_indent_document)
    created_by = models.ForeignKey(User, related_name='overall_indent_created_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# after indent prepare create entry
class RouteBusinessTrace(models.Model):
    route_trace = models.ForeignKey(RouteTrace)
    business = models.ForeignKey(Business)
    ordinal = models.PositiveIntegerField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)


class RouteTraceWiseSaleSummary(models.Model):
    route_trace = models.ForeignKey(RouteTrace)
    product = models.ForeignKey(Product)
    tray_count = models.PositiveIntegerField(blank=True, null=True)
    loose_packet_count = models.PositiveIntegerField(blank=True, null=True)
    leak_packet_count = models.PositiveIntegerField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=9, decimal_places=3)


class RouteVehicleMap(models.Model):
    route = models.ForeignKey(Route)
    vehicle = models.ForeignKey(Vehicle)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.route.name, self.vehicle.licence_number)


class PaymentStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)


class SaleStatus(models.Model):
    name = models.CharField(max_length=70, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class OrderedVia(models.Model):
    name = models.CharField(max_length=70, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # via mobile, via portal,


    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class SaleType(models.Model):
    name = models.CharField(max_length=70, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # to_icustomer, to business
    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class SaleGroup(models.Model):
    business = models.ForeignKey(Business)
    business_type = models.ForeignKey(BusinessType, blank=True, null=True)
    route = models.ForeignKey(Route)
    zone = models.ForeignKey(Zone)
    date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatus)
    ordered_by = models.ForeignKey(User, related_name='sale_group_created_by')
    payment_status = models.ForeignKey(PaymentStatus)
    product_amount = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='sale_group_modified_by')

    class Meta:
        unique_together = (("business", "session", "date"),)

class Sale(models.Model):
    sale_group = models.ForeignKey(SaleGroup)
    product = models.ForeignKey(Product)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='sale_ordered_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='sale_modified_by')

    class Meta:
        unique_together = (("sale_group", "product"),)


class TempSaleGroup(models.Model):
    business = models.ForeignKey(Business)
    business_type = models.ForeignKey(BusinessType, blank=True, null=True)
    route = models.ForeignKey(Route)
    zone = models.ForeignKey(Zone)
    date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatus)
    ordered_by = models.ForeignKey(User, related_name='temp_sale_group_created_by')
    payment_status = models.ForeignKey(PaymentStatus)
    product_amount = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='temp_sale_group_modified_by')


class TempSale(models.Model):
    temp_sale_group = models.ForeignKey(TempSaleGroup)
    product = models.ForeignKey(Product)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='temp_sale_ordered_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='temp_sale_modified_by')


class TempSaleGroupForEdit(models.Model):
    main_sale_group = models.ForeignKey(SaleGroup, blank=True, null=True)
    business = models.ForeignKey(Business)
    business_type = models.ForeignKey(BusinessType, blank=True, null=True)
    route = models.ForeignKey(Route)
    zone = models.ForeignKey(Zone)
    date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatus)
    ordered_by = models.ForeignKey(User, related_name='temp_sale_group_for_edit_created_by')
    payment_status = models.ForeignKey(PaymentStatus)
    product_amount = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='temp_sale_group_for_edit_modified_by')


class TempSaleForEdit(models.Model):
    main_sale = models.ForeignKey(Sale, blank=True, null=True)
    temp_sale_group_for_edit = models.ForeignKey(TempSaleGroupForEdit, blank=True, null=True)
    product = models.ForeignKey(Product)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='temp_sale_for_edit_ordered_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='temp_sale_for_edit_modified_by')


class ICustomerSaleGroup(models.Model):
    business = models.ForeignKey(Business)
    route = models.ForeignKey(Route)
    zone = models.ForeignKey(Zone)
    icustomer = models.ForeignKey(ICustomer)
    date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost_for_month = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatus)
    ordered_by = models.ForeignKey(User, related_name='icustomer_sale_group_created_by')
    payment_status = models.ForeignKey(PaymentStatus)
    product_amount = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='icustomer_sale_group_modified_by')

    class Meta:
      unique_together = (("business", "icustomer", "date", "session"),)


class ICustomerSale(models.Model):
    icustomer_sale_group = models.ForeignKey(ICustomerSaleGroup)
    product = models.ForeignKey(Product)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_for_month = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='icustomer_sale_ordered_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='icustomer_sale_modified_by')


class TempICustomerSaleGroup(models.Model):
    business = models.ForeignKey(Business)
    route = models.ForeignKey(Route)
    zone = models.ForeignKey(Zone)
    icustomer = models.ForeignKey(ICustomer)
    date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    ordered_via = models.ForeignKey(OrderedVia)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost_for_month = models.DecimalField(max_digits=10, decimal_places=2)
    sale_status = models.ForeignKey(SaleStatus)
    ordered_by = models.ForeignKey(User, related_name='temp_icustomer_sale_group_created_by')
    payment_status = models.ForeignKey(PaymentStatus)
    product_amount = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='temp_icustomer_sale_group_modified_by')


class TempICustomerSale(models.Model):
    temp_icustomer_sale_group = models.ForeignKey(TempICustomerSaleGroup)
    product = models.ForeignKey(Product)
    count = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_for_month = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_by = models.ForeignKey(User, related_name='temp_icustomer_sale_ordered_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='temp_icustomer_sale_modified_by')


class ICustomerMilkCarkNumberIdBank(models.Model):
    last_milk_card_number =  models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomerMonthlyOrderTransaction(models.Model):
    icustomer = models.ForeignKey(ICustomer)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    icustomer_sale_group = models.ManyToManyField(ICustomerSaleGroup)
    milk_card_number = models.CharField(max_length=50)
    transacted_date_time = models.DateTimeField()
    created_by = models.ForeignKey(User)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class TransactionDirection(models.Model):
    payment_from = models.CharField(max_length=50)
    payment_to = models.CharField(max_length=50)
    description = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class TransactionMode(models.Model):
    name = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # online, cash, check,


class TransactionStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class TransactionApprovalStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class TransactionChequeDetails(models.Model):
    bank_name = models.CharField(max_length=150)
    branch_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)
    micr_code = models.CharField(max_length=100, blank=True, null=True)
    account_holder_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    date_of_issue = models.DateField()
    cheque_number = models.PositiveIntegerField()
    is_cleared = models.BooleanField(default=False)
    cheque_cleared_date = models.DateField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.cheque_number)


class TransactedVia(models.Model):
    name = models.CharField(max_length=15, unique=True)
    # mobile, portal
    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class TransactionLog(models.Model):
    date = models.DateField()
    transacted_by = models.ForeignKey(User, related_name='agent_or_customer_user_id')
    data_entered_by = models.ForeignKey(User, related_name='transaction_initiated_user')
    transacted_via = models.ForeignKey(TransactedVia)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_direction = models.ForeignKey(TransactionDirection)
    transaction_id = models.CharField(max_length=20, null=True, blank=True)
    transaction_mode = models.ForeignKey(TransactionMode)
    transaction_status = models.ForeignKey(TransactionStatus)
    transaction_approval_status = models.ForeignKey(TransactionApprovalStatus)
    transaction_approved_by = models.ForeignKey(User, related_name='transaction_approved_by')
    transaction_approved_time = models.DateTimeField()
    wallet_balance_before_this_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_balance_after_transaction_approval = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    cheque_detail = models.ForeignKey(TransactionChequeDetails, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='transaction_log_modified_by')


# Password Reset #
class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User)
    otp = models.IntegerField()
    expiry_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SMSTrace(models.Model):
    union = models.ForeignKey(Union)
    receiver_user_id = models.PositiveIntegerField(blank=True, null=True)
    purpose = models.TextField()
    message = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)


def get_advertisement_image_upload_destination(instance, filename):
    return "event_and_news/advertisement_image/{publish_from}_to_{expires_on}/{file}".format(
        publish_from=datetime.datetime.strftime(
            instance.publish_from, '%Y-%m-%d'),
        expires_on=datetime.datetime.strftime(instance.expires_on, '%Y-%m-%d'), file=filename)


# Advertisment models
class Advertisement(models.Model):
    advertisement_image = models.ImageField(
        upload_to=get_advertisement_image_upload_destination, max_length=1000)
    link = models.URLField(verbose_name="Sponsor website",
                           help_text="Prefix http://", blank=True, null=True)
    publish_from = models.DateTimeField(
        help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')
    expires_on = models.DateTimeField(
        help_text="With Published chosen, won't be shown after this time", verbose_name='Expires on')
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class TemporaryRegistration(models.Model):
    union = models.ForeignKey(Union)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=13)
    email = models.CharField(max_length=30, blank=True, null=True)
    otp = models.CharField(max_length=30)


class DocumentTypeCv(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class AgentRequest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField()
    phone = models.CharField(max_length=13)
    address = models.TextField()
    pincode = models.PositiveIntegerField()
    business_type = models.ForeignKey(BusinessType)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_agent_request_document(instance, filename):
    return "agent_request_document/{document_type}/{file}".format(document_type=instance.document_type.name, file=filename)


class AgentRequestDocumentMap(models.Model):
    agent_request = models.ForeignKey(AgentRequest)
    document_type = models.ForeignKey(DocumentTypeCv)
    request_document_value = models.FileField(max_length=1000, upload_to=get_agent_request_document)


class ProductTrayConfig(models.Model):
    product = models.ForeignKey(Product)
    tray_count = models.PositiveSmallIntegerField()
    product_count = models.PositiveSmallIntegerField()
    created_by = models.ForeignKey(User, related_name="product_tray_config_created_by")
    modified_by = models.ForeignKey(User, related_name="product_tray_config_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class GlobalConfig(models.Model):
    union = models.ForeignKey(Union)
    name = models.CharField(max_length=300)  # tray capacity in liter
    value = models.CharField(max_length=300)  # 12
    description = models.TextField()
    created_by = models.ForeignKey(User, related_name="global_config_created_by")
    modified_by = models.ForeignKey(User, related_name="global_modified_by")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# class TemporaryIcustomerData(models.Model):
#     user_name = models.CharField(max_length=20)
#     first_name = models.CharField(max_length=20)
#     last_name = models.CharField(max_length=20)
#     password = models.CharField(max_length=20)
#     email = models.CharField(max_length=20, blank=True, null=True)
#     gender_id = models.PositiveIntegerField()
#     taluk_id = models.PositiveIntegerField()
#     district_id = models.PositiveIntegerField()
#     state_id = models.PositiveIntegerField()
#     pincode = models.PositiveIntegerField()
#     mobile = models.PositiveIntegerField()
#     alternate_mobile = models.PositiveIntegerField(blank=True, null=True)
#     street = models.TextField(max_length=20, blank=True, null=True)
#     latitude = models.DecimalField(max_digits=9, decimal_places=7, blank=True, null=True)
#     longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
#     time_created = models.DateTimeField(auto_now_add=True)
#     time_modified = models.DateTimeField(auto_now=True)


class CollectionCenter(models.Model):
    building_name = models.CharField(max_length=100)
    address = models.TextField()
    mobile = models.PositiveIntegerField()
    business_group = models.ForeignKey(BusinessGroup, blank=True, null=True)


class Counter(models.Model):
    collection_center = models.ForeignKey(CollectionCenter)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    finance_sub_code = models.CharField(max_length=15)
    is_included_in_cash_collection_report = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, related_name='counter_created_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CounterEmployeeTraceMap(models.Model):
    counter = models.ForeignKey(Counter)
    employee = models.ForeignKey(Employee)
    is_active = models.BooleanField(default=True)
    collection_date = models.DateField()
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class CounterEmployeeTraceSaleGroupMap(models.Model):
    counter_employee_trace = models.ForeignKey(CounterEmployeeTraceMap)
    sale_group = models.ManyToManyField(SaleGroup)
    icustomer_sale_group = models.ManyToManyField(ICustomerSaleGroup)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessWiseLeakageAllowanceAsPacket(models.Model):
    business = models.ForeignKey(Business)
    session = models.ForeignKey(Session)
    product = models.ForeignKey(Product)
    packet_count = models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class IndentCodeBank(models.Model):
    code_for = models.CharField(max_length=100)
    from_code = models.CharField(max_length=10)
    to_code = models.CharField(max_length=10)
    last_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_tender_file_upload_destination(instance, filename):
    return "tender/{publish_from}_to_{expires_on}/{file}".format(
        publish_from=datetime.datetime.strftime(
            instance.tender.publish_from, '%Y-%m-%d'),
        expires_on=datetime.datetime.strftime(instance.tender.expires_on, '%Y-%m-%d'), file=filename)


class Tender(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    publish_from = models.DateTimeField(
        help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')
    expires_on = models.DateTimeField(
        help_text="With Expired chosen, won't be shown after this time", verbose_name='Expires on')
    created_by = models.ForeignKey(User)
    ends_on = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.title)


class TenderFileMap(models.Model):
    tender = models.ForeignKey(Tender)
    document_name = models.CharField(max_length=150, blank=True, null=True)
    file = models.FileField(upload_to=get_tender_file_upload_destination, max_length=1000)


def get_carrier_file_upload_destination(instance, filename):
    return "carrier/{publish_from}_to_{expires_on}/{file}".format(
        publish_from=datetime.datetime.strftime(
            instance.carrier.publish_from, '%Y-%m-%d'),
        expires_on=datetime.datetime.strftime(instance.carrier.expires_on, '%Y-%m-%d'), file=filename)


class Carrier(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    publish_from = models.DateTimeField(
        help_text="With Published chosen, won't be shown until this time", verbose_name='Published from')
    expires_on = models.DateTimeField(
        help_text="With Expired chosen, won't be shown after this time", verbose_name='Expires on')
    created_by = models.ForeignKey(User)
    last_date_for_apply = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.title)


class CarrierFileMap(models.Model):
    carrier = models.ForeignKey(Carrier)
    document_name = models.CharField(max_length=150, blank=True, null=True)
    file = models.FileField(upload_to=get_carrier_file_upload_destination, max_length=1000)


class BusinessTypeWiseProductMinimumQuantityInLitre(models.Model):
    business_type = models.ForeignKey(BusinessType)
    product = models.ForeignKey(Product)
    value_in_litre = models.DecimalField(max_digits=9, decimal_places=2)
    created_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class MonthlyAgentCommissionRun(models.Model):
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    split = models.PositiveIntegerField()
    run_from = models.DateTimeField()
    run_to = models.DateTimeField()
    card_milk_comm_percentage = models.DecimalField(max_digits=9, decimal_places=2)
    cash_milk_comm_percentage = models.DecimalField(max_digits=9, decimal_places=2)
    tds_deduction_percentage = models.DecimalField(max_digits=9, decimal_places=2)
    insurance_deduction_percentage = models.DecimalField(max_digits=9, decimal_places=2)
    slip_charge = models.DecimalField(max_digits=9, decimal_places=2)

    is_comm_calculation_approved = models.BooleanField(default=False)
    comm_calculation_approved_at = models.DateTimeField(blank=True, null=True)
    comm_calculation_approved_by = models.ForeignKey(User, related_name='comm_calculation_approved_by')
    is_comm_run_completed =  models.BooleanField(default=False)
    # is_comm_calculation_changed_after_approval = models.BooleanField(default=False)

    # track
    comm_run_started_at = models.DateTimeField()
    comm_run_ended_at = models.DateTimeField(blank=True, null=True)
    comm_calculated_at = models.DateTimeField(blank=True, null=True)
    comm_calculated_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.month, self.year)


class MonthlyAgentCommission(models.Model):
    run = models.ForeignKey(MonthlyAgentCommissionRun)
    agent = models.ForeignKey(Agent)
    business_codes = models.CharField(max_length=60)
    business = models.ForeignKey(Business)
    business_type = models.ForeignKey(BusinessType)

    tm_cash_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    tm_cash_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)
    tm_card_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    tm_card_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)

    sm_cash_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    sm_cash_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)
    sm_card_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    sm_card_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)

    fcm_cash_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    fcm_cash_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)
    fcm_card_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    fcm_card_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)

    tea_cash_milk_sale = models.DecimalField(max_digits=9, decimal_places=2,default=0)
    tea_cash_milk_comm = models.DecimalField(max_digits=9, decimal_places=2,default=0)
    tea_card_milk_sale = models.DecimalField(max_digits=9, decimal_places=2,default=0)
    tea_card_milk_comm = models.DecimalField(max_digits=9, decimal_places=2,default=0)

    can_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    can_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)

    total_cash_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    total_cash_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)
    total_card_milk_sale = models.DecimalField(max_digits=9, decimal_places=2)
    total_card_milk_comm = models.DecimalField(max_digits=9, decimal_places=2)

    gross_sale = models.DecimalField(max_digits=9, decimal_places=2)
    gross_comm = models.DecimalField(max_digits=9, decimal_places=2)

    tds_deduction = models.DecimalField(max_digits=9, decimal_places=2)
    insurance_deduction = models.DecimalField(max_digits=9, decimal_places=2)
    slip_charge = models.DecimalField(max_digits=9, decimal_places=2)
    gross_deduction = models.DecimalField(max_digits=9, decimal_places=2)

    net_comm = models.DecimalField(max_digits=9, decimal_places=2)

    # track
    comm_calculated_at = models.DateTimeField()
    comm_calculated_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


def get_monthly_agent_commission_column_document(instance, filename):
    return "agent_monthly_commission/{year}/{month}/{file}".format(year=instance.run.month,month=instance.run.year, file=filename)



class MonthlyAgentCommissionRunColumnCv(models.Model):
    run = models.ForeignKey(MonthlyAgentCommissionRun)
    column_name = models.CharField(max_length=50)
    document = models.FileField(max_length=1000, upload_to=get_monthly_agent_commission_column_document, blank=True, null=True)
    percentage_value = models.PositiveSmallIntegerField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class MonthlyAgentCommissionSubColumn(models.Model):
    agent_commission = models.ForeignKey(MonthlyAgentCommission)
    column = models.ForeignKey(MonthlyAgentCommissionRunColumnCv)
    value = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    

def get_monthly_agent_commission_run_document(instance, filename):
    return "agent_monthly_commission/{year}/{month}/{file}".format(year=instance.run.month,month=instance.run.year, file=filename)


class MonthlyAgentCommissionRunDocument(models.Model):
    run = models.ForeignKey(MonthlyAgentCommissionRun)
    document = models.FileField(max_length=1000, upload_to=get_monthly_agent_commission_run_document)
    uploaded_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class MonthlyAgentCommissionTransaction(models.Model):
    comm = models.OneToOneField(MonthlyAgentCommission)
    bank_transaction_id = models.CharField(max_length=60)
    bank_transaction_amount = models.DecimalField(max_digits=9, decimal_places=2)
    bank_transaction_date = models.DateTimeField()
    destination_bank_account_number = models.CharField(max_length=60)


class MenuHeader(models.Model):
    display_name = models.CharField(max_length=100)
    link = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    ordinal = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class MenuHeaderPage(models.Model):
    menu_header = models.ForeignKey(MenuHeader)
    display_name = models.CharField(max_length=100)
    link = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    ordinal = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class MenuHeaderPermission(models.Model):
    employee_role = models.ForeignKey(EmployeeRole)
    menu_header = models.ForeignKey(MenuHeader)
    is_active = models.BooleanField(default=True)


class MenuHeaderPagePermission(models.Model):
    employee_role = models.ForeignKey(EmployeeRole)
    menu_header_page = models.ForeignKey(MenuHeaderPage)
    is_active = models.BooleanField(default=True)


# Payment Gateway tracking
class PaymentRequestStatus(models.Model):
    code = models.CharField(max_length=10)
    description = models.TextField()
    solution = models.TextField()
    # success(200), error codes [421, 422, 423a.....]


class PaymentTransactionStatus(models.Model):
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=10)
    #Unknown(???), Success(000), Failure(111), Pending(101), Abort(??)


class PaymentMethodCv(models.Model):
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=10)
    #Unknown(???), Success(000), Failure(111), Pending(101), Abort(??)


class PaymentRequestFor(models.Model):
    name = models.CharField(max_length=50)
    # agent_order, agent_order_edit, icustomer_order, icustomer_order_edit


class PaymentRequest(models.Model):
    rid = models.CharField(max_length=20, unique=True)
    status = models.ForeignKey(PaymentRequestStatus)
    encrypted_string = models.TextField()
    decrypted_string = models.TextField()
    payment_request_for = models.ForeignKey(PaymentRequestFor, blank=True, null=True)
    enquiry_response_status_latest = models.ForeignKey(PaymentTransactionStatus, blank=True, null=True)
    ordered_via = models.ForeignKey(OrderedVia)
    # request params  
    ver = models.CharField(max_length=3)
    cid = models.CharField(max_length=4)
    typ = models.CharField(max_length=4)
    crn = models.CharField(max_length=20, unique=True)
    cny = models.CharField(max_length=3)
    amt = models.DecimalField(max_digits=9, decimal_places=2)
    rtu = models.CharField(max_length=1024)
    ppi = models.CharField(max_length=1024)
    re1 = models.CharField(max_length=3, null=True)
    re2 = models.CharField(max_length=3, null=True)
    re3 = models.CharField(max_length=3, null=True)
    re4 = models.CharField(max_length=3, null=True)
    re5 = models.CharField(max_length=3, null=True)
    cks = models.CharField(max_length=4096)
    is_wallet_selected = models.BooleanField(default=False)
    is_amount_returened_to_wallet = models.BooleanField(default=False)
    wallet_balance_after_this_transaction = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PaymentRequestUserMap(models.Model):
    payment_request = models.ForeignKey(PaymentRequest)
    payment_intitated_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SaleGroupPaymentRequestMap(models.Model):
    sale_group = models.ManyToManyField(SaleGroup)
    temp_sale_group = models.ManyToManyField(TempSaleGroup)
    payment_request = models.ForeignKey(PaymentRequest)
    is_done = models.BooleanField(default=False)


class SaleGroupEditPaymentRequestMap(models.Model):
    sale_group = models.ManyToManyField(SaleGroup)
    temp_sale_group_for_edit = models.ManyToManyField(TempSaleGroupForEdit)
    payment_request = models.ForeignKey(PaymentRequest)
    is_done = models.BooleanField(default=False)


class ICustomerSaleGroupPaymentRequestMap(models.Model):
    sale_group = models.ManyToManyField(ICustomerSaleGroup)
    temp_sale_group = models.ManyToManyField(TempICustomerSaleGroup)
    payment_request = models.ForeignKey(PaymentRequest)
    is_done = models.BooleanField(default=False)


class PaymentRequestPPI(models.Model):
    payment_request = models.ForeignKey(PaymentRequest)
    key = models.CharField(max_length=25)
    value = models.CharField(max_length=256)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PaymentRequestResponse(models.Model):
    payment_request = models.OneToOneField(PaymentRequest)
    rid = models.CharField(max_length=20, unique=True)
    status = models.ForeignKey(PaymentTransactionStatus)
    is_enquired = models.BooleanField(default=False)
    encrypted_string = models.TextField()
    decrypted_string = models.TextField()

    # response params
    brn = models.CharField(max_length=10)
    trn = models.CharField(max_length=40, unique=True)
    tet = models.DateTimeField()
    pmd = models.CharField(max_length=5)
    stc = models.CharField(max_length=5)
    rmk = models.CharField(max_length=25)
    ver = models.CharField(max_length=3)
    cid = models.CharField(max_length=4)
    typ = models.CharField(max_length=4)
    crn = models.CharField(max_length=20, unique=True)
    cny = models.CharField(max_length=3)
    amt = models.DecimalField(max_digits=9, decimal_places=2)
    cks = models.CharField(max_length=4096)

    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class EnquiryRequest(models.Model):
    rid = models.CharField(max_length=20)
    status = models.ForeignKey(PaymentRequestStatus)
    encrypted_string = models.TextField()
    decrypted_string = models.TextField()

    # request params
    ver = models.CharField(max_length=3)
    cid = models.CharField(max_length=4)
    typ = models.CharField(max_length=4)
    crn = models.CharField(max_length=20)
    brn = models.CharField(max_length=10, blank=True, null=True)
    cks = models.CharField(max_length=4096)
    
    enquiry_make_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class EnquiryRequestResponse(models.Model):
    enquiry_request = models.OneToOneField(EnquiryRequest)
    rid = models.CharField(max_length=20)
    status = models.ForeignKey(PaymentTransactionStatus)
    encrypted_string = models.TextField()
    decrypted_string = models.TextField()

    # response params
    brn = models.CharField(max_length=10)
    trn = models.CharField(max_length=40)
    tet = models.DateTimeField()
    pmd = models.CharField(max_length=5)
    stc = models.CharField(max_length=5)
    rmk = models.CharField(max_length=25)
    ver = models.CharField(max_length=3)
    cid = models.CharField(max_length=4)
    typ = models.CharField(max_length=4)
    crn = models.CharField(max_length=20)
    cny = models.CharField(max_length=3)
    amt = models.DecimalField(max_digits=9, decimal_places=2)
    cks = models.CharField(max_length=4096)

    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PaymentRequestIdBank(models.Model):
    last_count = models.CharField(max_length=10)
    date = models.DateField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class CustomerOrderEditTimeRange(models.Model):
    from_time = models.TimeField()
    to_time = models.TimeField()
    description = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SaleGroupDeleteLog(models.Model):
    business = models.ForeignKey(Business)
    delivery_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    session = models.ForeignKey(Session)
    ordered_by = models.ForeignKey(User, related_name='order_placed_by')
    ordered_date_time = models.DateTimeField()
    deleted_by = models.ForeignKey(User, related_name='order_deleted_by')
    delete_date_time = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class RouteTimeChangeLog(models.Model):
    route = models.CharField(max_length=50)
    session = models.ForeignKey(Session)
    old_time = models.TimeField()
    new_time = models.TimeField()
    changed_by = models.ForeignKey(User)
    changed_at = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessRouteChangeLog(models.Model):
    business = models.ForeignKey(Business)
    old_route = models.ForeignKey(Route, blank=True, null=True, related_name='old_route')
    new_route = models.ForeignKey(Route, blank=True, null=True, related_name='new_oute')
    changed_by = models.ForeignKey(User)
    changed_at = models.DateTimeField()
    description = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomerBusinessLog(models.Model):
    icustomer = models.ForeignKey(ICustomer)
    old_business = models.ForeignKey(Business, related_name='old_business')
    new_business = models.ForeignKey(Business, related_name='new_business')
    changed_by = models.ForeignKey(User)
    changed_at = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomerCardSerialNumberIdBank(models.Model):
    business = models.ForeignKey(Business)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    counter_last_count = models.PositiveIntegerField()
    online_last_count = models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomerSerialNumberMap(models.Model):
    icustomer = models.ForeignKey(ICustomer)
    business = models.ForeignKey(Business)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    serial_number = models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class PaymentAutoEnquiry(models.Model):
    run_time = models.DateTimeField()
    run_interval_start = models.DateTimeField()
    run_interval_end = models.DateTimeField()
    run_type = models.CharField(max_length=25)
    candidate_count = models.PositiveIntegerField()
    success_count = models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PaymentAutoEnquiryProperty(models.Model):
    payment_auto_enquiry = models.ForeignKey(PaymentAutoEnquiry)
    payment_request = models.ForeignKey(PaymentRequest)
    amount_sent_to_wallet = models.DecimalField(max_digits=10, decimal_places=2)
    is_order_placed = models.BooleanField(default=False)
    morning_sale_group = models.ForeignKey(SaleGroup, blank=True, null=True, related_name='morning_sale_group')
    morning_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    evening_sale_group = models.ForeignKey(SaleGroup, blank=True, null=True, related_name='evening_sale_group')
    evening_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessTypeWiseOverallLitreLimit(models.Model):
    business_type = models.ForeignKey(BusinessType)
    litre_limit = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ICustomerOrderEndDateMonthWise(models.Model):
    month = models.PositiveIntegerField()
    date = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, related_name='created_by')
    modified_by = models.ForeignKey(User, related_name='modified_by')
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SuperSaleGroup(models.Model):
    business = models.ForeignKey(Business)
    delivery_date = models.DateField()
    mor_sale_group = models.ForeignKey(SaleGroup, related_name='mor_sale_group', blank=True, null=True, on_delete=models.SET_NULL)
    eve_sale_group = models.ForeignKey(SaleGroup, related_name='eve_sale_group', blank=True, null=True, on_delete=models.SET_NULL)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SaleGroupOrderType(models.Model):
    name = models.CharField(max_length=40)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    # new Order , modified increase, modified decrease


class SaleGroupTransactionTrace(models.Model):
    delivery_date = models.DateField()
    super_sale_group = models.ForeignKey(SuperSaleGroup)
    sale_group_order_type = models.ForeignKey(SaleGroupOrderType)
    counter_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transacted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_transaction = models.ForeignKey(TransactionLog, related_name='bank_transaction_log', blank=True, null=True)
    wallet_transaction = models.ForeignKey(TransactionLog, related_name='wallet_transaction_log',  blank=True, null=True)
    counter_transaction = models.ForeignKey(TransactionLog, related_name='counter_transaction_log', blank=True, null=True)
    is_wallet_used = models.BooleanField(default=False)
    order_sale_group_json = models.TextField(blank=True, null=True)
    counter = models.ForeignKey(Counter, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class AutoBotMoneyDepositToWalletLog(models.Model):
    business = models.ForeignKey(Business)
    delivery_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=30, blank=True, null=True)
    transacted_date = models.DateTimeField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ProductWiseMinimumQuantity(models.Model):
    product = models.ForeignKey(Product)
    value_in_quantity = models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class CustomerOrderDeleteLog(models.Model):
    customer = models.ForeignKey(ICustomer)
    ordered_on = models.DateTimeField()
    ordered_by = models.ForeignKey(User, related_name='ordered_by')
    deleted_on = models.DateTimeField()
    deleted_by = models.ForeignKey(User, related_name='deleted_by')
    date_of_delivery = models.DateTimeField()
    deleted_value_json = models.TextField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class EmployeeMonthlyOrderLog(models.Model):
    order_for = models.ForeignKey(ICustomerType)
    time_statrted = models.DateTimeField()
    time_ended = models.DateTimeField(blank=True, null=True)
    order_for_date =  models.DateTimeField()
    ordered_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class FreeProductProperty(models.Model):
    main_product = models.ForeignKey(Product, related_name='main_product_id')
    free_product = models.ForeignKey(Product, related_name='free_product_id')
    box_count = models.PositiveSmallIntegerField()
    product_count = models.PositiveSmallIntegerField()
    eligible_product_count = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# Order remove & Order Add
class EmployeeChangeOrderChangeMode(models.Model):
    name = models.CharField(max_length=50)


class EmployeeOrderChangeLog(models.Model):
    icustomer = models.ForeignKey(ICustomer)
    date_of_delivery = models.DateField()
    employee_order_change_mode = models.ForeignKey(EmployeeChangeOrderChangeMode)
    total_days = models.PositiveIntegerField() 
    from_date = models.DateField()
    to_date = models.DateField()
    icustomer_sale = models.ForeignKey(ICustomerSale, null=True, blank=True)
    modified_by = models.ForeignKey(User)
    modified_at = models.DateTimeField()
    product = models.ForeignKey(Product, null=True, blank=True)
    count = models.PositiveIntegerField(null=True, blank=True)
    cost_per_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    session = models.ForeignKey(Session, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class ICustomerWalletAmoutForOrder(models.Model):
    icustomer = models.ForeignKey(ICustomer)
    wallet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    icustomer_sale_group = models.ManyToManyField(ICustomerSaleGroup)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessTypeWiseFutureOrderConfig(models.Model):
    business_type = models.ForeignKey(BusinessType)
    is_future_order_accept = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class OrderDateModifyToggle(models.Model):
    is_order_data_changeable = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessTypeWiseFreeProductConfig(models.Model):
    business_type = models.ForeignKey(BusinessType)
    main_product = models.ForeignKey(Product, related_name='main_product_id_business_type_wise')
    free_product = models.ForeignKey(Product, related_name='free_product_id_business_type_wise')
    is_free = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)



class OwnParlourType(models.Model):
    name = models.CharField(max_length=500)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    #union booth , union parlour


class BusinessOwnParlourTypeMap(models.Model):
    business = models.ForeignKey(Business)
    own_parlour_type = models.ForeignKey(OwnParlourType)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class PaymentGatewayConfiguration(models.Model):
    ordered_via = models.ForeignKey(OrderedVia)
    is_enable = models.BooleanField(default=True)
    alert_message = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ordered_via.name} - {self.is_enable}"


class PaymentGatewayCrashLog(models.Model):
    crash_happend_at = models.DateTimeField()
    error_message = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BusinessWiseMilkLitreLimit(models.Model):
    business = models.ForeignKey(Business)
    limit_in_litre = models.DecimalField(max_digits=9, decimal_places=7)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class SmsProvider(models.Model):
    name = models.CharField(max_length=50)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class DailySmsCount(models.Model):
    sms_provider = models.ForeignKey(SmsProvider)
    date = models.DateField()
    count = models.PositiveIntegerField()
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class ProductNameAndQuantityTrace(models.Model):
    product = models.ForeignKey(Product)
    start_date = models.DateField()
    end_date = models.DateField()
    short_name = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=9, decimal_places=3)
    unit = models.ForeignKey(ProductUnit)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class BsnlSmsTemplate(models.Model):
    message_name = models.CharField(max_length=30)
    template_id = models.CharField(max_length=30)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

