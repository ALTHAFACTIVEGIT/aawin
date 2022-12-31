from django.db import models
from main.models import *



class DailySessionllyBusinessllySale(models.Model):
    delivery_date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    business = models.ForeignKey(Business, null=True)
    route = models.ForeignKey(Route)
    zone = models.ForeignKey(Zone)
    union = models.CharField(max_length=50, db_index=True)
    business_type = models.ForeignKey(BusinessType, null=True)


    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bm_jar200_pkt = models.PositiveIntegerField(default=0)
    bm_jar200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bm_jar200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bm_jar200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bmjf200_pkt = models.PositiveIntegerField(default=0)
    bmjf200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bmjf200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bmjf200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='dsbs_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class DailySessionllyRoutellySale(models.Model):
    delivery_date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    route = models.ForeignKey(Route)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bm_jar200_pkt = models.PositiveIntegerField(default=0)
    bm_jar200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bm_jar200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bm_jar200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bmjf200_pkt = models.PositiveIntegerField(default=0)
    bmjf200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bmjf200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bmjf200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='dsrs_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class DailySessionllyZonallySale(models.Model):
    delivery_date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    zone = models.ForeignKey(Zone)
    union = models.CharField(max_length=50, db_index=True)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveSmallIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bm_jar200_pkt = models.PositiveIntegerField(default=0)
    bm_jar200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bm_jar200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bm_jar200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bmjf200_pkt = models.PositiveIntegerField(default=0)
    bmjf200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bmjf200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bmjf200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='dszs_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class DailySessionllyBusinessTypellySale(models.Model):
    delivery_date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    business_type = models.ForeignKey(BusinessType)
    union = models.CharField(max_length=50, db_index=True)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveSmallIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bm_jar200_pkt = models.PositiveIntegerField(default=0)
    bm_jar200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bm_jar200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bm_jar200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bmjf200_pkt = models.PositiveIntegerField(default=0)
    bmjf200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bmjf200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bmjf200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='dsbts_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class DailySessionllyUnionllySale(models.Model):
    delivery_date = models.DateField(db_index=True)
    session = models.ForeignKey(Session)
    union = models.CharField(max_length=50, db_index=True)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveSmallIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bm_jar200_pkt = models.PositiveIntegerField(default=0)
    bm_jar200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bm_jar200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bm_jar200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    bmjf200_pkt = models.PositiveIntegerField(default=0)
    bmjf200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    bmjf200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bmjf200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='dsus_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


# Monthly report started
class MonthlySessionllyBusinessllySale(models.Model):
    month = models.PositiveSmallIntegerField(db_index=True)
    year = models.PositiveSmallIntegerField(db_index=True)
    session = models.ForeignKey(Session)
    business = models.ForeignKey(Business, null=True)
    route = models.ForeignKey(Route)
    zone = models.ForeignKey(Zone)
    union = models.CharField(max_length=50, db_index=True)
    business_type = models.ForeignKey(BusinessType, null=True)


    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='msbs_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class MonthlySessionllyRoutellySale(models.Model):
    month = models.PositiveSmallIntegerField(db_index=True)
    year = models.PositiveSmallIntegerField(db_index=True)
    session = models.ForeignKey(Session)
    route = models.ForeignKey(Route)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='msrs_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class MonthlySessionllyZonallySale(models.Model):
    month = models.PositiveSmallIntegerField(db_index=True)
    year = models.PositiveSmallIntegerField(db_index=True)
    session = models.ForeignKey(Session)
    zone = models.ForeignKey(Zone)
    union = models.CharField(max_length=50, db_index=True)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveSmallIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='mszs_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class MonthlySessionllyUnionllySale(models.Model):
    month = models.PositiveSmallIntegerField(db_index=True)
    year = models.PositiveSmallIntegerField(db_index=True)
    session = models.ForeignKey(Session)
    union = models.CharField(max_length=50, db_index=True)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveSmallIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='msus_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class MonthlySessionllyBusinessTypellySale(models.Model):
    month = models.PositiveSmallIntegerField(db_index=True)
    year = models.PositiveSmallIntegerField(db_index=True)
    session = models.ForeignKey(Session)
    business_type = models.ForeignKey(BusinessType)
    union = models.CharField(max_length=50, db_index=True)

    # sale type
    sold_to = models.CharField(max_length=50, db_index=True)

    # milk
    tm500_pkt = models.PositiveIntegerField(default=0)
    tm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std250_pkt = models.PositiveIntegerField(default=0)
    std250_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std250_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std250_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    std500_pkt = models.PositiveIntegerField(default=0)
    std500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    std500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    std500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm500_pkt = models.PositiveIntegerField(default=0)
    fcm500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcm1000_pkt = models.PositiveIntegerField(default=0)
    fcm1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea500_pkt = models.PositiveIntegerField(default=0)
    tea500_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tea1000_pkt = models.PositiveIntegerField(default=0)
    tea1000_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea1000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea1000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    tmcan = models.PositiveIntegerField(default=0)  # in number of cans
    tmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    tmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    smcan = models.PositiveIntegerField(default=0)  # in number of cans
    smcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    smcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    smcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fcmcan = models.PositiveIntegerField(default=0)  # in number of liters
    fcmcan_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # in number of liters
    fcmcan_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcmcan_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products
    curd500_pkt = models.PositiveIntegerField(default=0)
    curd500_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd500_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd500_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd5000_pkt = models.PositiveIntegerField(default=0)
    curd5000_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd5000_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd5000_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd150_pkt = models.PositiveIntegerField(default=0)
    curd150_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd150_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd150_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    cupcurd_box = models.PositiveIntegerField(default=0) # each box will have 12x100 gram cups
    cupcurd_count = models.PositiveSmallIntegerField(default=0)
    cupcurd_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cupcurd_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cupcurd_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    curd_bucket = models.PositiveIntegerField(default=0)  # in number of liters
    curd_bucket_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    curd_bucket_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    curd_bucket_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    lassi200_pkt = models.PositiveIntegerField(default=0)
    lassi200_kgs = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lassi200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lassi200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    buttermilk200_pkt = models.PositiveIntegerField(default=0)
    buttermilk200_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    buttermilk200_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buttermilk200_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # TOTALS
    # milk totals
    tm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    sm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fcm_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    fcm_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tea_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    tea_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    milk_litre = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    milk_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # fermented products total
    curd_kgs = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    curd_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    buttermilk_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    buttermilk_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lassi_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    lassi_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fermented_products_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    fermented_products_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # all totals
    total_litre = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # house keeping
    created_by = models.ForeignKey(User, related_name='msbts_created_by')
    modified_by = models.ForeignKey(User)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)


class DailyScriptRunLog(models.Model):
    date_of_delivery = models.DateTimeField()
    run_start_time = models.DateTimeField()
    run_end_time = models.DateTimeField(blank=True, null=True)
    run_by = models.ForeignKey(User)
    is_completed = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)

class DailyScriptRunProperty(models.Model):
    daily_script_run_log = models.ForeignKey(DailyScriptRunLog)
    script_name = models.CharField(max_length=150)
    run_start_time = models.DateTimeField()
    run_end_time = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)