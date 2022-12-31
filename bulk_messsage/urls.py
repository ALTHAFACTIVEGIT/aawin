from django.conf.urls import url
from bulk_messsage import views

urlpatterns = [
    url(r'^update/person/message/$', views.update_person_message),

]
