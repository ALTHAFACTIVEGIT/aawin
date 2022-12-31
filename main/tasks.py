
import json
import requests
import datetime
from main.models import DailySmsCount

def send_message_from_bsnl(template_id, key_and_values, phone_number):
    try:
        token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IjEwMDk4IDEiLCJuYmYiOjE2NTU1MzQ0NzIsImV4cCI6MTY4NzA3MDQ3MiwiaWF0IjoxNjU1NTM0NDcyLCJpc3MiOiJodHRwczovL2J1bGtzbXMuYnNubC5pbjo1MDEwIiwiYXVkIjoiMTAwOTggMSJ9.XwJVa19XSlNlufwYotGSd0mztk3TiWukKbuGGYhd4lU'
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer " + token}

        url = 'https://bulksms.bsnl.in:5010/api/Send_SMS'
        input_json = {
            "Header": "AAVINM",
            "Target": str(phone_number),
            "Is_Unicode": "0",
            "Is_Flash": "0",
            "Message_Type": "SI",
            "Entity_Id": "1701161726252728532",

        }
        input_json['Content_Template_Id'] = template_id
        input_json['Template_Keys_and_Values'] = key_and_values
        payload=json.dumps(input_json)
        res = requests.post(url, headers=headers, data=payload)
        print(res.status_code)
        if str(res.status_code) == '200':
            current_date = datetime.datetime.now().date()
            if DailySmsCount.objects.filter(date=current_date, sms_provider_id=3).exists():
                daily_sms_count_obj = DailySmsCount.objects.filter(date=current_date, sms_provider_id=3)[0]
            else:
                daily_sms_count_obj = DailySmsCount(date=current_date, count=0, sms_provider_id=3)
                daily_sms_count_obj.save()
        return True
    except Exception as e:
        print('Error - ', e)
        return False



