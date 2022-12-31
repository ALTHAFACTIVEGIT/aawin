from django.shortcuts import render
import os
from PyPDF2 import PdfFileMerger
# authendication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from bulk_messsage.models import *
from datetime import datetime

# Create your views here.
@api_view(['GET'])
@permission_classes((AllowAny, ))
def update_person_message(request):
    print(request.query_params.get('id'))
    try:
        person_message_obj_id = request.query_params.get('id')
        person_message_obj = PersonMessage.objects.get(id=person_message_obj_id)
        person_message_obj.is_acknowledged = True
        person_message_obj.acknowledged_at = datetime.now()
        person_message_obj.save()
        data_dict = {
            'status': 'success'
        }
        return render(request, 'ack_response.html', data_dict)
    except Exception as e:
        print(e)
        data_dict = {
            'status': 'failure'
        }
        return render(request, 'ack_response.html', data_dict)

