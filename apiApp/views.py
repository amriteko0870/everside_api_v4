from base64 import urlsafe_b64encode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.policy import default
from genericpath import getsize
from http import client
import json
from pydoc import resolve
from unicodedata import category
from matplotlib.pyplot import polar
import numpy as np
import pandas as pd
import time
from datetime import datetime as dt
import datetime
import re
from operator import itemgetter 
import os
import random
import json
#-------------------------Django Modules---------------------------------------------
from django.http import Http404, HttpResponse, JsonResponse,FileResponse
from django.shortcuts import render
from django.db.models import Avg,Count,Case, When, IntegerField,Sum,FloatField,CharField
from django.db.models import F,Func,Q
from django.db.models import Value as V
from django.db.models.functions import Concat,Cast,Substr
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Min, Max
from django.db.models import Subquery
from .emai_auth import gmail_authenticate
#----------------------------restAPI--------------------------------------------------
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser,FormParser
#--------------------------Models-----------------------------------------------------
from apiApp.models import clientTopic, clinicTopic, engagement_file_data, everside_nps, providerTopic, user_data
#--------------------------extra libs------------------------------------------------
from apiApp.extra_vars import region_names,prob_func
from apiApp.send_email import email_creation
# Create your views here.
#-------------- Global Variable--------------------------------------------------------
timestamp_sub = 86400 #+19800
timestamp_start = 0#+19800
#----------------------------Annotation Functions--------------------------------------
class roundRating(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 1)'
class twoDecimal(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 2)'
class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 0)'
#--------------------------- Filters---------------------------------------------------
@api_view(['POST'])
def filterRegion(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            if(check_token.TOKEN != (request.headers)['Authorization']):
                return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub         
            obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).exclude(REGION__isnull=True).exclude(REGION__exact='nan').values_list('REGION',flat=True).distinct()
            region = list(obj)
            region.sort()
        return Response({'Message':'TRUE','region':region})
    except:
        return Response({'Message':'FALSE'})

@api_view(['POST'])
def filterClinic(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = request.GET.get('region')
            region = re.split(r"-|,", region)
            check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            if(check_token.TOKEN != (request.headers)['Authorization']):
                return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub  
            obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values_list('NPSCLINIC',flat=True).distinct()    
            if '' not in region:
                obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(REGION__in=region).values_list('NPSCLINIC',flat=True).distinct()
            data = list(obj)
            data.sort()
        return Response({'Message':'TRUE','clinic':data,})
    except:
        return Response({'Message':'FALSE'})  


@api_view(['POST'])
def filterClient(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = request.GET.get('region')
            clinic = request.GET.get('clinic')
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)     
            check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            if(check_token.TOKEN != (request.headers)['Authorization']):
                return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            if '' not in region:
                obj = obj.filter(REGION__in=region)
            if '' not in clinic:
                obj = obj.filter(NPSCLINIC__in=clinic)
            obj = obj.exclude(CLIENT_NAME = 'nan').values_list('CLIENT_NAME',flat=True).distinct()
            obj = list(obj)
            obj.sort()
            return Response({'Message':'TRUE','client':obj})
    except:
        return Response({'Message':'FALSE'})    


#-------------------- Login and Logout -----------------------------------------------------
@api_view(['POST'])
def userLogin(request,format=None):
    try:
        if request.method == 'POST':
            data = request.data
            username = str(data['username'])
            password = str(data['password'])
            data = user_data.objects.filter(USERNAME = username).values()
            if (check_password(password,data[0]['PASSWORD'])):
                token = data[0]['TOKEN']
                u_name = data[0]['USERNAME']
                admin = data[0]['USER_TYPE']
                if admin == 'A' or admin == 'SA':
                    admin_type = True
                else:
                    admin_type = False
                return Response({'Message':'TRUE','username':u_name,'token':token,'admin_type':admin_type})
            else:
                return Response({'Message':'FALSE'})
    except:
        return Response({'Message':'FALSE'})

           


@api_view(['GET'])
def logout(request):
    username = (request.GET.get('username'))
    try:
        a = 'uploads/engagement_download_files/'+username+'_alert_comments.csv'
        os.remove(a)
    except:
        pass
    try:
        a = 'uploads/engagement_download_files/'+username+'_all_comments.csv'
        os.remove(a)
    except:
        pass
    try:
        a = 'uploads/engagement_download_files/'+username+'_average_table.csv'
        os.remove(a)
    except:
        pass
    try:
        a = 'uploads/engagement_download_files/'+username+'_provider_data.csv'
        os.remove(a)
    except:
        pass
    try:
        a = 'uploads/engagement_download_files/'+username+'health_center_data.csv'
        os.remove(a)
    except:
        pass
    try:
        a = 'uploads/engagement_download_files/'+username+'client_data.csv'
        os.remove(a)
    except:
        pass
    try:
        f_obj = engagement_file_data.objects.filter(USERNAME = username).values()
        f_name = (f_obj[0])['FILE_NAME'][:-4]
        a = 'uploads/engagement_download_files/'+f_name+'_'+username+'.csv'
        os.remove(a)
    except:
        pass

    return Response({'Message':'TRUE'})


#---------------------For Dashboards--------------------------------------------------
@api_view(['POST'])
def netPromoterScore(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})
            except:
                return Response({'Message':'FALSE'})

            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)       
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            total_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            promoters_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(nps_label = 'Promoter').values()
            passive_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(nps_label = 'Passive').values()
            detractors_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(nps_label = 'Detractor').values()
            state = region
            if '' not in state:
                total_count = total_count.filter(REGION__in = state)
                promoters_count = promoters_count.filter(REGION__in = state)
                passive_count = passive_count.filter(REGION__in = state)
                detractors_count = detractors_count.filter(REGION__in = state)
            if '' not in clinic:
                total_count = total_count.filter(NPSCLINIC__in = clinic)
                promoters_count = promoters_count.filter(NPSCLINIC__in = clinic)
                passive_count = passive_count.filter(NPSCLINIC__in = clinic)
                detractors_count = detractors_count.filter(NPSCLINIC__in = clinic)
            if '' not in client:
                total_count = total_count.filter(CLIENT_NAME__in = client)
                promoters_count = promoters_count.filter(CLIENT_NAME__in = client)
                passive_count = passive_count.filter(CLIENT_NAME__in = client)
                detractors_count = detractors_count.filter(CLIENT_NAME__in = client)
            
            if(len(promoters_count)>0):
                    promoters = round(len(promoters_count)/len(total_count)*100)
                    if promoters == 0:
                        promoters = round(len(promoters_count)/len(total_count)*100,2)
            else:
                promoters = 0     

            if(len(passive_count)>0):
                    passive = round(len(passive_count)/len(total_count)*100)
                    if passive == 0:
                        passive = round(len(passive_count)/len(total_count)*100,2)
            else:
                passive = 0      

            if(len(detractors_count)>0):
                    detractors = round(len(detractors_count)/len(total_count)*100)
                    if detractors == 0:
                        detractors = round(len(detractors_count)/len(total_count)*100,2)
            else:
                detractors = 0      
            
            nps ={
                    "nps_score":(promoters-detractors),
                    "promoters":promoters,
                    "total_promoters":len(promoters_count),
                    "passive":passive,
                    "total_passive":len(passive_count),
                    "detractors":detractors,
                    "total_detractors":len(detractors_count),
                }

            nps_pie = [{
                            "label":"Promoters",
                            "percentage":promoters,
                            "color":"#00AC69",
                        },
                        {
                                "label":"Passives",
                            "percentage":passive,
                            "color":"#939799",
                        },
                        {
                            "label":"Detractors",
                            "percentage":detractors,
                            "color":"#DB2B39",
                        }]

            return Response({'Message':'TRUE',
                                'nps':nps,
                                        'nps_pie':nps_pie})
    except:
        return Response({'Message':'FALSE'})


@api_view(['POST'])
def netSentimentScore(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})  
            except:
                return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            total_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            positive_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(sentiment_label='Positive').values()
            negative_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(sentiment_label='Negative').values()
            extreme_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(sentiment_label='Extreme').values()
            neutral_count = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(sentiment_label='Neutral').values()

            state = region
            if '' not in region:
                total_count = total_count.filter(REGION__in = state)
                positive_count = positive_count.filter(REGION__in = state)
                negative_count = negative_count.filter(REGION__in = state)
                extreme_count = extreme_count.filter(REGION__in = state)
                neutral_count = neutral_count.filter(REGION__in = state)
                
            
            if '' not in clinic:
                total_count = total_count.filter(NPSCLINIC__in = clinic)
                positive_count = positive_count.filter(NPSCLINIC__in = clinic)
                negative_count = negative_count.filter(NPSCLINIC__in = clinic)
                extreme_count = extreme_count.filter(NPSCLINIC__in = clinic)
                neutral_count = neutral_count.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                total_count = total_count.filter(CLIENT_NAME__in = client)
                positive_count = positive_count.filter(CLIENT_NAME__in = client)
                negative_count = negative_count.filter(CLIENT_NAME__in = client)
                extreme_count = extreme_count.filter(CLIENT_NAME__in = client)
                neutral_count = neutral_count.filter(CLIENT_NAME__in = client)
            
            if(len(positive_count)!=0):
                positive = round(len(positive_count)/len(total_count)*100)
                if positive == 0:
                    positive = round(len(positive_count)/len(total_count)*100,2)
            else:
                positive = 0
            
            if(len(negative_count)!=0):
                negative = round(len(negative_count)/len(total_count)*100)
                if negative == 0:
                    negative = round(len(negative_count)/len(total_count)*100,2)
            else:
                negative = 0
            
            if(len(extreme_count)!=0):
                extreme = round(len(extreme_count)/len(total_count)*100)
                if extreme == 0:
                    extreme = round(len(extreme_count)/len(total_count)*100,2)
            else:
                extreme = 0
            
            if(len(neutral_count)!=0):
                neutral = round(len(neutral_count)/len(total_count)*100)
                if neutral == 0:
                    neutral = round(len(neutral_count)/len(total_count)*100,2)
            else:
                neutral = 0

            nss ={
                    "nss_score":round(positive-negative-extreme),
                    "total": len(total_count),
                    "positive":positive,
                    "total_positive":len(positive_count),
                    "negative":negative,
                    "total_negative":len(negative_count),
                    "extreme":extreme,
                    "total_extreme":len(extreme_count),
                    "neutral":neutral,
                    "total_neutral": len(neutral_count), 
                }
                
            nss_pie = [{
                        "label":"Positive",
                        "percentage":positive,
                        "color":"#00AC69",
                    },
                    {
                        "label":"Negative",
                        "percentage":negative,
                        "color":"#EE6123",
                    },
                    {
                        "label":"Extreme",
                        "percentage":extreme,
                        "color":"#DB2B39",
                    },
                    {
                        "label":"Neutral",
                        "percentage":neutral,
                        "color":"#939799",
                    }]
            return Response({'Message':'TRUE',
                             'nss':nss,
                             'nss_pie':nss_pie})
    except:
        return Response({'Message':'FALSE'})


@api_view(['POST'])
def totalCards(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            survey_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values_list('REVIEW_ID').distinct()
            alert_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).filter(sentiment_label = 'Extreme')
            clinics = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values_list('NPSCLINIC').distinct()
            doctors = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).exclude(PROVIDER_NAME__isnull=True).exclude(PROVIDER_NAME__exact='nan').values_list('PROVIDER_NAME').distinct()
            clients = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).exclude(CLIENT_NAME__isnull=True).exclude(CLIENT_NAME__exact='nan').values_list('CLIENT_ID').distinct()
            state = region
            if '' not in region:
                survey_comments = survey_comments.filter(REGION__in = state)
                alert_comments = alert_comments.filter(REGION__in = state)
                clinics = clinics.filter(REGION__in = state)
                doctors = doctors.filter(REGION__in = state)
                clients = clients.filter(REGION__in = state)

            if '' not in clinic:
                survey_comments = survey_comments.filter(NPSCLINIC__in = clinic)
                alert_comments = alert_comments.filter(NPSCLINIC__in = clinic)
                clinics = clinics.filter(NPSCLINIC__in = clinic)
                doctors = doctors.filter(NPSCLINIC__in = clinic)
                clients = clients.filter(NPSCLINIC__in = clinic)

            if '' not in client:
                survey_comments = survey_comments.filter(CLIENT_NAME__in = client)
                alert_comments = alert_comments.filter(CLIENT_NAME__in = client)
                clinics = clinics.filter(CLIENT_NAME__in = client)
                doctors = doctors.filter(CLIENT_NAME__in = client)
                clients = clients.filter(CLIENT_NAME__in = client)

            card_data = {
                            'survey':len(survey_comments),
                            'comments': len(survey_comments),
                            'alerts': len(alert_comments),
                            'clinic': len(clinics),
                            'doctors':len(doctors),
                            'clients':len(clients),
                    }
        return Response({'Message':'TRUE','card_data':card_data})
    
    except:
        return Response({'Message':'FALSE'}) 

@api_view(['POST'])
def totalComments(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            all_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                all_comments = all_comments.filter(REGION__in = state)
                

            if '' not in clinic:
                all_comments = all_comments.filter(NPSCLINIC__in = clinic)
    
            if '' not in client:
                all_comments = all_comments.filter(CLIENT_NAME__in = client)

            all_comments = all_comments.values('id')\
            .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            time = F('TIMESTAMP'),
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            topic = F('TOPIC'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField()),
                                                            provider = F('PROVIDER_NAME')
                                                            
                                                )
            all_comments = all_comments.exclude(review = '  ')
            all_comments = sorted(all_comments, key=itemgetter('time'),reverse=True)
        return Response({'Message':'True','data':all_comments})
    except:
        return Response({'Message':'FALSE'}) 

@api_view(['POST'])
def positiveComments(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            positive_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                positive_comments = positive_comments.filter(REGION__in = state)                

            if '' not in clinic:
                positive_comments = positive_comments.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                positive_comments = positive_comments.filter(CLIENT_NAME__in = client)
                

            positive_comments = positive_comments.filter(sentiment_label = 'Positive').values('id')\
                                                .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            topic = F('TOPIC'),
                                                            time = F('TIMESTAMP'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField()),
                                                            provider = F('PROVIDER_NAME')

                                                )
            positive_comments = positive_comments.exclude(review = '  ')
            positive_comments= sorted(positive_comments ,key=itemgetter('time'),reverse=True)    
        return Response({'Message':'True','count':len(positive_comments),'data':positive_comments})
    except:
        return Response({'Message':'FALSE'}) 


@api_view(['POST'])
def negativeComments(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            negative_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                negative_comments = negative_comments.filter(REGION__in = state)                

            if '' not in clinic:
                negative_comments = negative_comments.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                negative_comments = negative_comments.filter(CLIENT_NAME__in = client)
                

            negative_comments = negative_comments.filter(sentiment_label = 'Negative').values('id')\
                                                .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            topic = F('TOPIC'),
                                                            time = F('TIMESTAMP'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField()),
                                                            provider = F('PROVIDER_NAME')

                                                )
            negative_comments = negative_comments.exclude(review = '  ')
            negative_comments= sorted(negative_comments ,key=itemgetter('time'),reverse=True)    
        return Response({'Message':'True','count':len(negative_comments),'data':negative_comments})
    except:
        return Response({'Message':'FALSE'}) 

@api_view(['POST'])
def neutralComments(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            neutral_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                neutral_comments = neutral_comments.filter(REGION__in = state)                

            if '' not in clinic:
                neutral_comments = neutral_comments.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                neutral_comments = neutral_comments.filter(CLIENT_NAME__in = client)
                

            neutral_comments = neutral_comments.filter(sentiment_label = 'Neutral').values('id')\
                                                .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            topic = F('TOPIC'),
                                                            time = F('TIMESTAMP'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField()),
                                                            provider = F('PROVIDER_NAME')

                                                )
            neutral_comments = neutral_comments.exclude(review = '  ')
            neutral_comments= sorted(neutral_comments ,key=itemgetter('time'),reverse=True)    
        return Response({'Message':'True','count':len(neutral_comments),'data':neutral_comments})
    except:
        return Response({'Message':'FALSE'}) 

@api_view(['POST'])
def extremeComments(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            extreme_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                extreme_comments = extreme_comments.filter(REGION__in = state)                

            if '' not in clinic:
                extreme_comments = extreme_comments.filter(NPSCLINIC__in = clinic)
                
            if '' not in client:
                extreme_comments = extreme_comments.filter(CLIENT_NAME__in = client)

            extreme_comments = extreme_comments.filter(sentiment_label = 'Extreme').values('id')\
                                                .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            topic = F('TOPIC'),
                                                            time = F('TIMESTAMP'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField()),
                                                            provider = F('PROVIDER_NAME')

                                                )
            extreme_comments = extreme_comments.exclude(review = '  ')
            extreme_comments= sorted(extreme_comments ,key=itemgetter('time'),reverse=True)    
        return Response({'Message':'True','count':len(extreme_comments),'data':extreme_comments})
    except:
        return Response({'Message':'FALSE'})

@api_view(['POST'])
def alertComments(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            alert_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                alert_comments = alert_comments.filter(REGION__in = state)                

            if '' not in clinic:
                alert_comments = alert_comments.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                alert_comments = alert_comments.filter(CLIENT_NAME__in = client)
                

            alert_comments = alert_comments.filter(sentiment_label = 'Extreme').values('id')\
                                                .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            topic = F('TOPIC'),
                                                            time = F('TIMESTAMP'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField()),
                                                            provider = F('PROVIDER_NAME')

                                                )
            alert_comments = alert_comments.exclude(review = '  ')
            alert_comments= sorted(alert_comments ,key=itemgetter('time'),reverse=True)    
        return Response({'Message':'True','data':alert_comments})
    except:
        return Response({'Message':'FALSE'}) 


@api_view(['POST'])
def npsOverTime(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            nps = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            
            state = region
            if '' not in region:
                nps = nps.filter(REGION__in = state)
                

            if '' not in clinic:
                nps = nps.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                nps = nps.filter(CLIENT_NAME__in = client)
            
            nps = nps.values('SURVEY_MONTH' ).annotate(
                                                    count = Count(F('REVIEW_ID')),
                                                    promoter = twoDecimal((Cast(Sum(Case(
                                                                When(nps_label='Promoter',then=1),
                                                                default=0,
                                                                output_field=IntegerField()
                                                                )),FloatField()))),\
                                                    passive =  twoDecimal((Cast(Sum(Case(
                                                                When(nps_label='Passive',then=1),
                                                                default=0,
                                                                output_field=IntegerField()
                                                                )),FloatField()))),\
                                                    detractor = twoDecimal((Cast(Sum(Case(
                                                                When(nps_label='Detractor',then=1),
                                                                default=0,
                                                                output_field=IntegerField()
                                                                )),FloatField()))),\
                                                    month = Substr(F('SURVEY_MONTH'),1,3),\
                                                    year = Cast(F('SURVEY_YEAR'),IntegerField()),
                                                    nps_abs = twoDecimal(
                                                        ((F('promoter')-F('detractor'))/(F('promoter')+F('passive')+F('detractor')))*100),
                                                    NPS = Case(
                                                            When(
                                                                nps_abs__lt = 0,
                                                                then = 0    
                                                                ),
                                                                default=F('nps_abs'),
                                                                output_field=FloatField()
                                                              )
                                                )\
                                            .order_by('SURVEY_MONTH')
            
            nps = list(nps)
            nps.sort(key = lambda x: dt.strptime(x['SURVEY_MONTH'], '%b-%y')) 
        return Response({'Message':'True','nps_over_time':nps})
    except:
        return Response({'Message':'FALSE'})

@api_view(['POST'])
def nssOverTime(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            nss = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()       
            state = region
            if '' not in region:
                nss = nss.filter(REGION__in = state)
                

            if '' not in clinic:
                nss = nss.filter(NPSCLINIC__in = clinic)

            if '' not in client:
                nss = nss.filter(CLIENT_NAME__in = client)
            nss = nss.values('SURVEY_MONTH' ).annotate(
                                                    positive = twoDecimal((Cast(Sum(Case(
                                                                When(sentiment_label='Positive',then=1),
                                                                default=0,
                                                                output_field=IntegerField()
                                                                )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),\
                                                    negative = twoDecimal((Cast(Sum(Case(
                                                                When(sentiment_label='Negative',then=1),
                                                                default=0,
                                                                output_field=IntegerField()
                                                                )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),\
                                                    extreme = twoDecimal((Cast(Sum(Case(
                                                                When(sentiment_label='Extreme',then=1),
                                                                default=0,
                                                                output_field=IntegerField()
                                                                )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),\
                                                    neutral = twoDecimal((Cast(Sum(Case(
                                                                When(sentiment_label='Neutral',then=1),
                                                                default=0,
                                                                output_field=IntegerField()
                                                                )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),\
                                                    month = Substr(F('SURVEY_MONTH'),1,3),\
                                                    year = Cast(F('SURVEY_YEAR'),IntegerField()),
                                                    nss_abs = twoDecimal(F('positive')-F('negative')-F('extreme')),
                                                    nss = Case(
                                                            When(
                                                                nss_abs__lt = 0,
                                                                then = 0    
                                                                ),
                                                                default=F('nss_abs'),
                                                                output_field=FloatField()
                                                              )
                                                        )   
            nss = list(nss)
            nss.sort(key = lambda x: dt.strptime(x['SURVEY_MONTH'], '%b-%y')) 
        return Response({'Message':'True','nss_over_time':nss})
    except:
        return Response({'Message':'FALSE'})
    

@api_view(['POST'])
def npsAverageGraph(request,format=None):
    try:
        if request.method == 'POST':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            client = (request.GET.get('client')).split(',')
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = ''.split(',')

            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            nps = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            
            state = region
            if '' not in region:
                nps = nps.filter(REGION__in = state)
                
            if '' not in clinic:
                nps = nps.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                nps = nps.filter(CLIENT_NAME__in = client)
        
            nps_avg = nps.values('SURVEY_MONTH' ).annotate(
                                                    month = Substr(F('SURVEY_MONTH'),1,3),\
                                                    year = Cast(F('SURVEY_YEAR'),IntegerField()),
                                                    nps_abs = twoDecimal(Avg('NPS')),
                                                    NPS = Case(
                                                            When(
                                                                nps_abs__lt = 0,
                                                                then = 0    
                                                                ),
                                                                default=F('nps_abs'),
                                                                output_field=FloatField()
                                                              ),
                                                )\
                                            .order_by('SURVEY_MONTH')
            
            promoter = nps.values('SURVEY_MONTH' ).filter(nps_label='Promoter')\
                                                  .annotate(
                                                    promoter = twoDecimal(Avg('NPS'))
                                                    )\
                                                  .order_by('SURVEY_MONTH')
            
            passive = nps.values('SURVEY_MONTH' ).filter(nps_label='Passive')\
                                                  .annotate(passive = twoDecimal(Avg('NPS')))\
                                                  .order_by('SURVEY_MONTH')
            
            detractors = nps.values('SURVEY_MONTH' ).filter(nps_label='Detractor')\
                                                  .annotate(detractor = twoDecimal(Avg('NPS')))\
                                                  .order_by('SURVEY_MONTH')
            
            
            
            nps_avg = list(nps_avg)
            promoter = list(promoter)
            passive = list(passive)
            detractors = list(detractors)

            nps_avg.sort(key = lambda x: dt.strptime(x['SURVEY_MONTH'], '%b-%y'))
            promoter.sort(key = lambda x: dt.strptime(x['SURVEY_MONTH'], '%b-%y'))
            passive.sort(key = lambda x: dt.strptime(x['SURVEY_MONTH'], '%b-%y'))
            detractors.sort(key = lambda x: dt.strptime(x['SURVEY_MONTH'], '%b-%y'))


            df = pd.DataFrame(nps_avg)
            try:
                df = pd.concat([df,pd.DataFrame(promoter)[['promoter']]],axis = 1)
            except:
                df = df.assign(promoter=0)

            try:
                df = pd.concat([df,pd.DataFrame(passive)[['passive']]],axis = 1)
            except:
                df = df.assign(passive=0)

            try:
                df = pd.concat([df,pd.DataFrame(detractors)[['detractor']]],axis = 1)
            except:
                df = df.assign(detractor=0)
                
            nps = json.loads(df.to_json(orient='records'))
            
        return Response({'Message':'True','nps_avg':nps})
    except:
        return Response({'Message':'FALSE'})


@api_view(['POST'])
def npsVsSentiments(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})    
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
        
            all_data = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            
            state = region
            if '' not in region:
                all_data = all_data.filter(REGION__in = state)
                

            if '' not in clinic:
                all_data = all_data.filter(NPSCLINIC__in = clinic)

            if '' not in client:
                all_data = all_data.filter(CLIENT_NAME__in = client)
            

            positive = all_data.values('sentiment_label').filter(sentiment_label = 'Positive')\
                                .annotate(
                                            promoter = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Promoter',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            passive =  twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Passive',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            detractor = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Detractor',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100)
                                        ).order_by('sentiment_label')

            negative = all_data.values('sentiment_label').filter(sentiment_label = 'Negative')\
                                .annotate(
                                            promoter = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Promoter',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            passive =  twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Passive',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            detractor = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Detractor',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100)
                                        ).order_by('sentiment_label')
            neutral = all_data.values('sentiment_label').filter(sentiment_label = 'Neutral')\
                                .annotate(
                                            promoter = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Promoter',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            passive =  twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Passive',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            detractor = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Detractor',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100)
                                        ).order_by('sentiment_label')
            extreme = all_data.values('sentiment_label').filter(sentiment_label = 'Extreme')\
                                .annotate(
                                            promoter = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Promoter',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            passive =  twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Passive',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100),
                                            detractor = twoDecimal((Cast(Sum(Case(
                                                        When(nps_label='Detractor',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),FloatField())/Cast(Count('REVIEW_ID'),FloatField()))*100)
                                        ).order_by('sentiment_label')
            if(len(list(positive)) == 0):
                possitive = [{
                                "sentiment_label": "Positive",
                                "promoter": 0,
                                "passive": 0,
                                "detractor": 0
                            }]
            if(len(list(negative)) == 0):
                negative = [{
                                "sentiment_label": "negative",
                                "promoter": 0,
                                "passive": 0,
                                "detractor": 0
                            }]
            if(len(list(neutral)) == 0):
                neutral = [{
                                "sentiment_label": "neutral",
                                "promoter": 0,
                                "passive": 0,
                                "detractor": 0
                            }]
            if(len(list(extreme)) == 0):
                extreme = [{
                                "sentiment_label": "Extreme",
                                "promoter": 0,
                                "passive": 0,
                                "detractor": 0
                            }]
            final_data = list(positive)+list(negative)+list(neutral)+list(extreme)
        return Response({'Message':'TRUE','data':final_data})   
    except:
        return Response({'Message':'FALSE'})


@api_view(['POST'])
def providersData(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            # try:
            #     check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            #     if(check_token.TOKEN != (request.headers)['Authorization']):
            #         return Response({'Message':'FALSE'})  
            # except:
            #     return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            providers = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            
            state = region
            if '' not in region:
                providers = providers.filter(REGION__in = state)
                

            if '' not in clinic:
                providers = providers.filter(NPSCLINIC__in = clinic)
            if '' not in client:
                providers = providers.filter(CLIENT_NAME__in = client)
            # providers = providers.objects.raw('SELECT * from apiApp_everside_nps group by provider_name')
            providers = providers.exclude(PROVIDER_NAME__in = ['nan']).annotate(provider_name = F('PROVIDER_NAME'))\
                                            .values('provider_name')\
                                            .annotate(
                                                    count = Count(F('REVIEW_ID')),
                                                    promoter = Sum(Case(
                                                        When(nps_label='Promoter',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),
                                                    detractor = Sum(Case(
                                                        When(nps_label='Detractor',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),
                                                    provider_type = F('PROVIDERTYPE'),
                                                    provider_category = F('PROVIDER_CATEGORY'),
                                                    nps_abs=Cast(Round((Cast((F('promoter')-F('detractor')),FloatField())/F('count'))*100),IntegerField()),
                                                    average_nps = Case(
                                                            When(
                                                                nps_abs__lt = 0,
                                                                then = 0    
                                                                ),
                                                                default=F('nps_abs'),
                                                                output_field=FloatField()
                                                              ),
                                                    score = twoDecimal(Avg('MEMBER_PROVIDER_SCORE'))
                                                ).order_by('provider_name')

            providers_list = providers.values_list('PROVIDER_NAME',flat=True).distinct()
            providers_list = list(providers_list)
            provider_topics = providerTopic.objects.exclude(PROVIDER_NAME__in = ['nan']).filter(PROVIDER_NAME__in = providers_list).values()
            providers = sorted(list(providers), key=itemgetter('provider_name'))
            provider_topics = sorted(list(provider_topics), key=itemgetter('PROVIDER_NAME'))
        return Response({'Message':'True','data':providers,'topic':provider_topics})
    except:
        return Response({'Message':'FALSE'})

@api_view(['POST'])
def clinicData(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})  
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            clinic_data = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            state = region
            if '' not in region:
                clinic_data = clinic_data.filter(REGION__in = state)
            if '' not in clinic:
                clinic_data = clinic_data.filter(NPSCLINIC__in = clinic)
            if '' not in client:
                clinic_data = clinic_data.filter(CLIENT_NAME__in = client)
            clinic_data = clinic_data.exclude(NPSCLINIC__in = (['nan','Unknown'])).annotate(clinic=F('NPSCLINIC'))\
                                 .values('clinic')\
                                 .annotate(
                                        clinic_full_name = Concat('NPSCLINIC',V(' '),'CLINIC_CITY', V(' '), 'CLINIC_STATE'),
                                        count = Count(F('REVIEW_ID')),
                                        promoter = Sum(Case(
                                            When(nps_label='Promoter',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        detractor = Sum(Case(
                                            When(nps_label='Detractor',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        nps=Cast(Round((Cast((F('promoter')-F('detractor')),FloatField())/F('count'))*100),IntegerField()),
                                        average_nps = Case(
                                                    When(
                                                        nps__lt = 0,
                                                        then = 0    
                                                        ),
                                                        default=F('nps'),
                                                        output_field=FloatField()
                                                        ),
                                                        
                                        city = F('CLINIC_CITY'),
                                        state = F('CLINIC_STATE'),
                                        address = Concat('CLINIC_CITY', V(', '), 'CLINIC_STATE'),
                                        region = F('REGION')
                                          )\
                                 .order_by('clinic_full_name')

            clinic_list = clinic_data.values_list('clinic_full_name',flat=True).distinct()
            clinic_list = list(clinic_list)
            clinic_topics = clinicTopic.objects.filter(CLINIC_FULL_NAME__in = clinic_list).values()
            clinic_data = sorted(list(clinic_data), key=itemgetter('clinic_full_name'))
            clinic_topics = sorted(list(clinic_topics), key=itemgetter('CLINIC_FULL_NAME'))
        return Response({'Message':'True','data':clinic_data,'topic':clinic_topics})
    except:
        return Response({'Message':'FALSE'})

@api_view(['POST'])
def clientData(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            try:
                check_token = user_data.objects.get(USERNAME = (request.data)['username'])
                if(check_token.TOKEN != (request.headers)['Authorization']):
                    return Response({'Message':'FALSE'})  
            except:
                return Response({'Message':'FALSE'})  
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            clients = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            state = region
            if '' not in region:
                clients = clients.filter(REGION__in = state)
            if '' not in clinic:
                clients = clients.filter(NPSCLINIC__in = clinic)
            if '' not in client:
                clients = clients.filter(CLIENT_NAME__in = client)
            parent_client_names = clients.values_list('PARENT_CLIENT_NAME',flat=True).distinct()
            parent_client_names = sorted(list(parent_client_names))
            clients = clients.exclude(CLIENT_NAME__in = ['nan']).annotate(client_name=F('CLIENT_NAME'))\
                                 .values('client_name')\
                                 .annotate(
                                        parent_client_name = F('PARENT_CLIENT_NAME'),
                                        count = Count(F('REVIEW_ID')),
                                        promoter = Sum(Case(
                                            When(nps_label='Promoter',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        detractor = Sum(Case(
                                            When(nps_label='Detractor',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        nps_abs=Cast(Round((Cast((F('promoter')-F('detractor')),FloatField())/F('count'))*100),IntegerField()),
                                        average_nps = Case(
                                                            When(
                                                                nps_abs__lt = 0,
                                                                then = 0    
                                                                ),
                                                                default=F('nps_abs'),
                                                                output_field=FloatField()
                                                              )
                                          )\
                                 .order_by('client_name')
            
            clients_list = clients.values_list('client_name',flat=True).distinct()
            clients_list = list(clients_list)
            clients_topics = clientTopic.objects.filter(CLIENT_NAME__in = clients_list).values()
            clients = sorted(list(clients), key=itemgetter('client_name'))
            clients_topics = sorted(list(clients_topics), key=itemgetter('CLIENT_NAME'))

        return Response({'Message':'True','data':clients,'parent_client_names':parent_client_names,'topic':clients_topics})
    except:
        return Response({'Message':'FALSE'})

#--------------------------------Providers Scoring-----------------------------------------------------
@api_view(['POST'])
def filterDateProvider(request,format=None):
    # try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            # check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            # if(check_token.TOKEN != (request.headers)['Authorization']):
            #     return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub         
            obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate)\
                                      .filter(TIMESTAMP__lte=endDate)
            region = obj.exclude(REGION__isnull=True)\
                        .exclude(REGION__exact='nan')\
                        .values_list('REGION',flat=True).distinct()

            clinic = obj.exclude(NPSCLINIC__isnull=True)\
                        .exclude(NPSCLINIC__exact='nan')\
                        .values_list('NPSCLINIC',flat=True).distinct()

            client = obj.exclude(CLIENT_NAME__isnull=True)\
                        .exclude(CLIENT_NAME__exact='nan')\
                        .values_list('CLIENT_NAME',flat=True).distinct()

            provider = obj.exclude(PROVIDER_NAME__isnull=True)\
                          .exclude(PROVIDER_NAME__exact='nan')\
                          .values_list('PROVIDER_NAME',flat=True).distinct()

            region = list(region)
            region.sort()
            provider = list(provider)
            provider.sort()
            clinic = list(clinic)
            clinic.sort()
            client = list(client)
            client.sort()
            return Response({'Message':'TRUE',
                             'region':region,
                             'provider':provider,
                             'clinic':clinic,
                             'client':client})
    # except:
    #     return Response({'Message':'FALSE'})

@api_view(['POST'])
def filterRegionProvider(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = request.GET.get('region')
            region = re.split(r"-|,", region)
            # check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            # if(check_token.TOKEN != (request.headers)['Authorization']):
            #     return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub         
            obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate)\
                                      .filter(TIMESTAMP__lte=endDate)

            if '' not in region:
                obj = obj.filter(REGION__in=region)

            clinic = obj.exclude(NPSCLINIC__isnull=True)\
                        .exclude(NPSCLINIC__exact='nan')\
                        .values_list('NPSCLINIC',flat=True).distinct()
            client = obj.exclude(CLIENT_NAME__isnull=True)\
                        .exclude(CLIENT_NAME__exact='nan')\
                        .values_list('CLIENT_NAME',flat=True).distinct()
            provider = obj.exclude(PROVIDER_NAME__isnull=True)\
                          .exclude(PROVIDER_NAME__exact='nan')\
                          .values_list('PROVIDER_NAME',flat=True).distinct()

            provider = list(provider)
            provider.sort()
            clinic = list(clinic)
            clinic.sort()
            client = list(client)
            client.sort()
            
            return Response({'Message':'TRUE',
                             'clinic':clinic,
                             'client':client,
                             'provider':provider})
    except:
        return Response({'Message':'FALSE'})


@api_view(['POST'])
def filterClinicProvider(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            clinic = request.GET.get('clinic')
            clinic = re.split(r"-|,", clinic)     
            # check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            # if(check_token.TOKEN != (request.headers)['Authorization']):
            #     return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub         
            obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate)\
                                      .filter(TIMESTAMP__lte=endDate)
            if '' not in clinic:
                obj = obj.filter(NPSCLINIC__in=clinic)

            client = obj.exclude(CLIENT_NAME__isnull=True)\
                        .exclude(CLIENT_NAME__exact='nan')\
                        .values_list('CLIENT_NAME',flat=True).distinct()
            provider = obj.exclude(PROVIDER_NAME__isnull=True)\
                          .exclude(PROVIDER_NAME__exact='nan')\
                          .values_list('PROVIDER_NAME',flat=True).distinct()

            provider = list(provider)
            provider.sort()
            client = list(client)
            client.sort()
            return Response({'Message':'TRUE',
                             'client':client,
                             'provider':provider})
    except:
        return Response({'Message':'FALSE'})



@api_view(['POST'])
def filterClientProvider(request,format=None):
    try:
        if request.method == 'POST':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            client = request.GET.get('client')
            client = (request.GET.get('client')).split(',')  
            # print(client)
            # check_token = user_data.objects.get(USERNAME = (request.data)['username'])
            # if(check_token.TOKEN != (request.headers)['Authorization']):
            #     return Response({'Message':'FALSE'})
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub         
            obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate)\
                                      .filter(TIMESTAMP__lte=endDate)
            if '' not in client:
                obj = obj.filter(CLIENT_NAME__in=client)

            provider = obj.exclude(PROVIDER_NAME__isnull=True)\
                          .exclude(PROVIDER_NAME__exact='nan')\
                          .values_list('PROVIDER_NAME',flat=True).distinct()

            provider = list(provider)
            provider.sort()
            return Response({'Message':'TRUE',
                             'provider':provider})
    except:
        return Response({'Message':'FALSE'})


@api_view(['GET'])
def providerCommentDownload(request,format=None):
    start_year = request.GET.get('start_year')
    start_month = request.GET.get('start_month')
    end_year = request.GET.get('end_year')
    end_month = request.GET.get('end_month')
    provider = request.GET.get('provider')
    start_date = str(start_month)+'-'+str(start_year)
    startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
    if int(end_month)<12:
        end_date = str(int(end_month)+1)+'-'+str(end_year)
    else:
        end_date = str('1-')+str(int(end_year)+1)
    endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
    obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate)\
                              .filter(TIMESTAMP__lte=endDate)\
                              .filter(PROVIDER_NAME=provider)
    comments = obj.values('id').annotate(
                                        review = Func(
                                            Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                            V('nan'), V(''),
                                            function='replace'),
                                        label = F('sentiment_label'),
                                        timestamp = F('SURVEY_MONTH'), 
                                        time = F('TIMESTAMP'),
                                        clinic = F('NPSCLINIC'),
                                        reason = F('ENCOUNTER_REASON'),
                                        topic = F('TOPIC'),
                                        )
    comments = comments.exclude(review = '  ')
    comments = sorted(comments, key=itemgetter('time'),reverse=True)
    comments_df = pd.DataFrame(list(comments))
    comments_df = comments_df[['timestamp','review','topic','clinic','reason','label']]
    comments_df.rename(columns={'review':'comments'}, inplace=True)
    comments_df.rename(columns={'reason':'Visit Reason'}, inplace=True)
    comments_df.rename(columns={'label':'Sentiment'}, inplace=True)
    comments_df.rename(columns={'timestamp':'Date'}, inplace=True)
    comments_df.columns = comments_df.columns.str.upper()
    username = (request.GET.get('username'))
    a = 'uploads/engagement_download_files/'+username+'_provider_comment.csv'
    comments_df.to_csv(a,index=False)
    response = FileResponse(open(a, 'rb'))
    return response

@api_view(['POST'])
def providerScoreCard(request,format=None):
    start_year = request.GET.get('start_year')
    start_month = request.GET.get('start_month')
    end_year = request.GET.get('end_year')
    end_month = request.GET.get('end_month')
    provider = request.GET.get('provider')
    # print("######################## : ",(request.data)['username'])
    # check_token = user_data.objects.get(USERNAME = (request.data)['username'])
    # if(check_token.TOKEN != (request.headers)['Authorization']):
    #     return Response({'Message':'FALSE'})
    start_date = str(start_month)+'-'+str(start_year)
    startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
    if int(end_month)<12:
        end_date = str(int(end_month)+1)+'-'+str(end_year)
    else:
        end_date = str('1-')+str(int(end_year)+1)
    endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
    obj = everside_nps.objects.filter(TIMESTAMP__gte=startDate)\
                              .filter(TIMESTAMP__lte=endDate)\
                              .filter(PROVIDER_NAME=provider)
    name = provider
    score_list = list(obj.values_list('MEMBER_PROVIDER_SCORE',flat=True))
    avg_score = round(sum(score_list)/len(score_list),2)
    encounter = obj.values_list('ENCOUNTER_REASON').distinct().count()
    patient_count = obj.values_list('MEMBER_ID',flat=True).distinct().count()
    survey = obj.count()
    nps_response = obj.annotate(
                                review = Func(
                                    Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                    V('nan'), V(''),
                                    function='replace'))\
                      .values('review').exclude(review = '  ')\
                      .count()
    avg_nps = obj.aggregate(avg_nps = twoDecimal(Avg(F('NPS'))))
    topic = providerTopic.objects.filter(PROVIDER_NAME=provider).values('POSITIVE_TOPIC','NEGATIVE_TOPIC')

    info = {
            'name' : name,
            'score':avg_score,
            'encounter':encounter,
            'patient_count':patient_count,
            'survey':survey,
            'nps_response':nps_response,
            'avg_nps':avg_nps['avg_nps'],
            'positive_topic':topic[0]['POSITIVE_TOPIC'],
            'negative_topic':topic[0]['NEGATIVE_TOPIC'],
            }

    # print(info)
    n = float(info['score'])*10
    l = []
    fill = n//20
    n_fill  = n%20
    for i in range(5):
        if i<fill:
            l.append(100)
        elif  i==fill:
            l.append(round(n_fill*5))
        else:
            l.append(0)
    try:
        promoter = obj.filter(nps_label = 'Promoter').count()
        passive = obj.filter(nps_label = 'Passive').count()
        detractor = obj.filter(nps_label = 'Detractor').count()
        if promoter-detractor<0:
            nps = 0
        else:
            nps = round(((promoter - detractor)/(promoter+passive+detractor))*100,2)

        nps_card = {
                    'total_promoters':promoter,
                    'total_passive':passive,
                    'total_detractors':detractor,
                    'promoters':round((promoter/(promoter+passive+detractor))*100,2),
                    'passive':round((passive/(promoter+passive+detractor))*100,2),
                    'detractors':round((detractor/(promoter+passive+detractor))*100,2),
                    'nps_score':nps
        }
        nps_pie = [
                    {
                        'color':'#00ac69',
                        'label':'Promoters',
                        'percentage':round((promoter/(promoter+passive+detractor))*100,2)
                    },
                    {
                        'color':'#939799',
                        'label':'Passives',
                        'percentage':round((passive/(promoter+passive+detractor))*100,2)
                    },
                    {
                        'color':'#DB2B39',
                        'label':'Detractors',
                        'percentage':round((detractor/(promoter+passive+detractor))*100,2)
                    }
                ]
    
    except:
        months = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov','Dec']
        date = str(months[int(start_month)-1])+'-'+start_year+' to '+str(months[int(end_month)-1])+'-'+end_year
        return Response({'Message':'ERROR','Comment':'Selected Provider not present in this date range ( '+date+' )'})
    member_count = obj.count()
    comment_count = obj.annotate(review = Func(
                                            Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                            V('nan'), V(''),
                                            function='replace'),).exclude(review = '  ').count()
                                
    reason_count = obj.values_list('ENCOUNTER_REASON',flat=0).distinct().count()
    alerts_count = obj.filter(sentiment_label='Extreme').count() 

    total_card = {
                    'member_count':member_count,
                    'comment_count':comment_count,
                    'reason_count':reason_count,
                    'alerts_count':alerts_count
                 }
    statistic = obj.values('SURVEY_MONTH').annotate(
                                                    count = Count(F('REVIEW_ID')),
                                                    reason = Count('ENCOUNTER_REASON',distinct=True),
                                                    score = twoDecimal(Avg('MEMBER_PROVIDER_SCORE')),
                                                    month = Substr(F('SURVEY_MONTH'),1,3),\
                                                    year = Cast(F('SURVEY_YEAR'),IntegerField()),

    ).order_by('SURVEY_MONTH')
    statistic = list(statistic)
    statistic.sort(key = lambda x: dt.strptime(x['SURVEY_MONTH'], '%b-%y')) 

    comments = obj.values('id').annotate(
                                        review = Func(
                                            Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                            V('nan'), V(''),
                                            function='replace'),
                                        label = F('sentiment_label'),
                                        timestamp = F('SURVEY_MONTH'), 
                                        time = F('TIMESTAMP'),
                                        clinic = F('NPSCLINIC'),
                                        reason = F('ENCOUNTER_REASON'),
                                        topic = F('TOPIC'),
                                        )
    comments = comments.exclude(review = '  ')
    comments = sorted(comments, key=itemgetter('time'),reverse=True)
    
    total_count = obj
    positive_count = obj.filter(sentiment_label='Positive').values()
    negative_count = obj.filter(sentiment_label='Negative').values()
    extreme_count = obj.filter(sentiment_label='Extreme').values()
    neutral_count = obj.filter(sentiment_label='Neutral').values()

    if(len(positive_count)!=0):
        positive = round(len(positive_count)/len(total_count)*100)
        if positive == 0:
            positive = round(len(positive_count)/len(total_count)*100,2)
    else:
        positive = 0
    
    if(len(negative_count)!=0):
        negative = round(len(negative_count)/len(total_count)*100)
        if negative == 0:
            negative = round(len(negative_count)/len(total_count)*100,2)
    else:
        negative = 0
    
    if(len(extreme_count)!=0):
        extreme = round(len(extreme_count)/len(total_count)*100)
        if extreme == 0:
            extreme = round(len(extreme_count)/len(total_count)*100,2)
    else:
        extreme = 0
    
    if(len(neutral_count)!=0):
        neutral = round(len(neutral_count)/len(total_count)*100)
        if neutral == 0:
            neutral = round(len(neutral_count)/len(total_count)*100,2)
    else:
        neutral = 0
    
    nss ={
            "nss_score":round(positive-negative-extreme),
            "total": len(total_count),
            "positive":positive,
            "total_positive":len(positive_count),
            "negative":negative,
            "total_negative":len(negative_count),
            "extreme":extreme,
            "total_extreme":len(extreme_count),
            "neutral":neutral,
            "total_neutral": len(neutral_count), 
        }
    nss_pie = [{
                        "label":"Positive",
                        "percentage":positive,
                        "color":"#00AC69",
                    },
                    {
                        "label":"Negative",
                        "percentage":negative,
                        "color":"#EE6123",
                    },
                    {
                        "label":"Extreme",
                        "percentage":extreme,
                        "color":"#DB2B39",
                    },
                    {
                        "label":"Neutral",
                        "percentage":neutral,
                        "color":"#939799",
                    }]

    provider_topics = obj.annotate(provider_name = F('PROVIDER_NAME'))\
                                            .values('provider_name')\
                                            .annotate(
                                                    count = Count(F('REVIEW_ID')),
                                                    promoter = Sum(Case(
                                                        When(nps_label='Promoter',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),
                                                    detractor = Sum(Case(
                                                        When(nps_label='Detractor',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),
                                                    provider_type = F('PROVIDERTYPE'),
                                                    provider_category = F('PROVIDER_CATEGORY'),
                                                    nps_abs=Cast(Round((Cast((F('promoter')-F('detractor')),FloatField())/F('count'))*100),IntegerField()),
                                                    average_nps = Case(
                                                            When(
                                                                nps_abs__lt = 0,
                                                                then = 0    
                                                                ),
                                                                default=F('nps_abs'),
                                                                output_field=FloatField()
                                                              ),
                                                    score = twoDecimal(Avg('MEMBER_PROVIDER_SCORE'))
                                                )
    provider_topic2 = providerTopic.objects.filter(PROVIDER_NAME = provider ).values('POSITIVE_TOPIC','NEGATIVE_TOPIC')
    provider_topic = {**list(provider_topics)[0],**list(provider_topic2)[0]}
    res = {
           'Message':'TRUE',
           'provider_info':info,
           'nps':nps_card,
           'nps_pie':nps_pie,
           'nss':nss,
           'nss_pie':nss_pie,
           'provider_comments':comments,
        #    'provider_total_card':total_card,
        #    'provider_star':l,
        #    'provider_statistics':statistic,
        #    'topic':provider_topic,
    }

    return Response(res)

@api_view(['POST'])
def providerEmail(request,format=None):
    start_year = request.GET.get('start_year')
    start_month = request.GET.get('start_month')
    end_year = request.GET.get('end_year')
    end_month = request.GET.get('end_month')
    provider = request.GET.get('provider')

    start_date = str(start_month)+'-'+str(start_year)
    startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
    if int(end_month)<12:
        end_date = str(int(end_month)+1)+'-'+str(end_year)
    else:
        end_date = str('1-')+str(int(end_year)+1)
    endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub


    months = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov','Dec']
    
    query = everside_nps.objects.filter(PROVIDER_NAME = provider,
                                         TIMESTAMP__gte=startDate,
                                         TIMESTAMP__lte=endDate)
    name = provider
    p_type = query.values_list('PROVIDERTYPE',flat=True).distinct().last()
    date_range = str(months[int(start_month)-1])+" "+str(start_year)+" - "+str(months[int(end_month)-1])+" "+str(end_year)
    member_count = query.count() if query.count() > 0 else 'Nil' 
    p_category = query.values_list('PROVIDER_CATEGORY',flat=True).distinct().last()
    star_score = round((query.aggregate(score = Avg('MEMBER_PROVIDER_SCORE')))['score'],2)
    extreme_count = query.filter(sentiment_label='Extreme').count() if query.filter(sentiment_label='Extreme').count() > 0 else 'Nil'
    visit_reason = query.values_list('ENCOUNTER_REASON',flat=True).distinct()[:5]
    positive_topic = list(set(list(query.filter(sentiment_label='Positive').values('TOPIC','MEMBER_PROVIDER_SCORE').order_by('MEMBER_PROVIDER_SCORE').values_list('TOPIC',flat=True))))[:3]
    negative_topic = list(set(list(query.filter(sentiment_label__in=['Negative','Extreme']).values('TOPIC','MEMBER_PROVIDER_SCORE').order_by('MEMBER_PROVIDER_SCORE').values_list('TOPIC',flat=True))))[:3]
    text = email_creation(name,p_type,date_range,member_count,p_category,star_score,extreme_count,visit_reason,positive_topic,negative_topic)
    
    service = gmail_authenticate()
    
    message = MIMEMultipart('alternative')
    message['to'] = 'vivek.k@ekoinfomatics.com'
    message['from'] = 'nps@ekoinfomatics.com'
    message['subject'] = 'Provider Scrore card for '+provider

    mime_type = MIMEText(text, 'html')
    message.attach(mime_type)
    body1 = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    result = service.users().messages().send(
      userId="me",
      body=body1
    ).execute()
    return Response({'Message':"TRUE","Status":"Sent"})
#--------------------------------Enagement Moddel------------------------------------------------------

@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
def egMemberPercentile(request,format=None):
    try:
        #----------------------Check Username----------------------------------------------------
        try:
            username = str((request.data)['username'])
        except:
            return Response({'Message':'FALSE','Error':'Username Invalid'})
        
        #------------------File name and path creation--------------------------------------------
        file_name = username+'.csv'
        file_path = 'uploads/engagement_files/'+file_name
        
        #----------------- Check if previous file exist------------------------------------------
        previous_files = os.listdir('uploads/engagement_files')
        previous_file_flag = 0
        if(file_name in previous_files):
            df = pd.read_csv(file_path)
            previous_file_flag = 1
        
        #--------------- Check if file uploaded -------------------------------------------------
        try:
            uploaded_file = (request.FILES.getlist('file'))[0]
            df = pd.read_csv(uploaded_file)	
            
            engagement_file_data.objects.filter(USERNAME = str((request.data)['username'])).delete()
            data = engagement_file_data(USERNAME = str((request.data)['username']),
                                        FILE_NAME = str(uploaded_file),
                                        FILE_SIZE = (uploaded_file).size)
            data.save()
            df.to_csv(file_path)
        except:
            if previous_file_flag == 0:
                return Response({'Message':'FALSE','Error':'No Previous File found'})
                
        
        
        #--------------Check variables in file----------------------------------------------------    
        try:
            df = df.rename(columns=str.lower)
            ndf = df[['member_id', 'client_id', 'zip', 'age']]
        except:
            return Response({'Message':'FALSE','Error':'invalid file uploaded'})

        #--------------- Member Score Graph -----------------------------------------------------
        df['zip'] =  pd.to_numeric(df['zip'],errors='coerce')
        lat_long_df = pd.read_csv('zip_lat_long.csv')
        df['zip'] =  pd.to_numeric(df['zip'],errors='coerce')
        ms_graph_merged = pd.merge(df,lat_long_df,on='zip',how='left')
        ms_graph_df = prob_func(ms_graph_merged)
        ms_graph_prob = list(ms_graph_df['probability_eng'])
        low = 0 # n < 0.5
        med = 0 # 0.5 < n < 0.75
        high = 0 # 0.75 < n
        graph = [] 
        p_values = [0,1,25,33,50,66,75,95,99,100]
        for i in p_values:
            p = np.percentile(ms_graph_prob,i)
            percentile_name = "P"+str(i)
            percentile_value = round(p,3)
            member_score = ms_graph_prob.count(p)
            if p < 0.5:
                low = low + 1
            elif 0.5 <= p < 0.75:
                med = med + 1
            else:
                high = high + 1

            frame = {
                'percentile_name':percentile_name,
                'percentile_value':percentile_value,
                'member_score':member_score
            }
            graph.append(frame)
            percentage = {
                'low':str(low*10)+"%",
                'medium':str(low*10+med*10)+"%",
                'high':'100%',
            }

        #--------------------Engagement Total Cards ----------------------------------------------------
        rows = df.shape[0]
        columns = df.shape[1]
        client_count = len(set(list(df['client_id'])))
        member_count = len(set(list(df['member_id'])))
        
        cards_data = [
                        {
                        'name':'Rows',
                        'value':rows
                        },
                        {
                        'name':'Columns',
                        'value':columns
                        },
                        {
                        'name':'Clients',
                        'value':client_count
                        },
                        {
                        'name':'Members',
                        'value':member_count
                        },
                    ]
        #----------------------------Age group Graph ----------------------------------------------------
        group_list = [(0,12),(13,19),(20,29),(30,39),(40,49),(50,59),(60,69),(70,79),(80,89),(90,1000)]
        age_list = list(df['age'])
        age_graph = []
        for i in group_list:
            if(i[1]<90):  
                age_graph.append({
                                'groupName':str(i[0])+'-'+str(i[1]),
                                'groupValue': sum(map(age_list.count, range(i[0],i[1]+1)))
                                }) 
            else:
                    age_graph.append({
                                'groupName':str(i[0])+'+',
                                'groupValue': sum(map(age_list.count, range(i[0],i[1]+1)))
                                })
        
        #------------------------ Average table ---------------------------------------------------------
        lat_long_df = pd.read_csv('zip_lat_long.csv')
        # fill nan with 0 or unknown
        df['zip'] =  pd.to_numeric(df['zip'],errors='coerce')
        average_table_df = pd.merge(df,lat_long_df,on='zip',how='left')
        average_table_df = prob_func(average_table_df)
        average_table_df['REGION_ZIP'] = average_table_df['REGION_ZIP'].fillna('unknown')
        average_table_df['PCP_Avail'] = average_table_df['PCP_Avail'].fillna(0)
        average_table_df['Percent_Insured'] = average_table_df['Percent_Insured'].fillna(0)
        average_table_df['per_asian'] = average_table_df['per_asian'].fillna(0)
        average_table_df['per_black'] = average_table_df['per_black'].fillna(0)
        average_table_df['__Ethnic_White'] = average_table_df['__Ethnic_White'].fillna(0)
        average_table_df['__Hispanic_or_Latino_(of_any_race)'] = average_table_df['__Hispanic_or_Latino_(of_any_race)'].fillna(0)
        
        average_table = []
        regions = list(set(list(average_table_df['REGION_ZIP'])))
        for i in regions:
            ndf = average_table_df.loc[average_table_df['REGION_ZIP'] == i]
            frame = {
                'region':i,
                '__Ethnic_White':str(np.nansum(np.array(list(ndf['__Ethnic_White'])))/(ndf.shape)[0]),
                'per_black':str(np.nansum(np.array(list(ndf['per_black'])))/(ndf.shape)[0]),
                'per_asian':str(np.nansum(np.array(list(ndf['per_asian'])))/(ndf.shape)[0]),
                '__Hispanic_or_Latino':str(np.nansum(np.array(list(ndf['__Hispanic_or_Latino_(of_any_race)'])))/(ndf.shape)[0]),
                'Percent_Insured':str(np.nansum(np.array(list(ndf['Percent_Insured'])))/(ndf.shape)[0]),
                'PCP_Avail':str(np.nansum(np.array(list(ndf['PCP_Avail'])))/(ndf.shape)[0]),
                'probability_eng':str(np.nansum(np.array(list(ndf['probability_eng'])))/(ndf.shape)[0]),
            }
            average_table.append(frame)

        #------------------------- File Object ---------------------------------------------
        f_obj = engagement_file_data.objects.filter(USERNAME = str((request.data)['username'])).values()

        #-------------------------- Map -----------------------------------------------------
        state_codes = region_names()
        df['zip'] =  pd.to_numeric(df['zip'],errors='coerce')
        map_df = df.drop_duplicates(subset=['zip'],keep='last')
        lat_long_df = pd.merge(map_df,lat_long_df,on='zip',how='left')
        lat_long_df['Y'] = lat_long_df['Y'].fillna(0)
        lat_long_df['X'] = lat_long_df['X'].fillna(0)
        lat_long_df['zip'] = lat_long_df['zip'].fillna(0)
        state = list(lat_long_df['STATE_ZIP'])
        long = list(lat_long_df['Y'])
        lat = list(lat_long_df['X'])
        zip = list(lat_long_df['zip'])
        map_data = []
        for i in range(lat_long_df.shape[0]):
            try:
                state_data = state_codes[state[i]]
            except:
                state_data = state[i]
            frame = {
                    'state':str(state_data),
                    'long':long[i],
                    'lat':lat[i],
                    'zip':str(zip[i]),
                    'zip_count':(list(df['zip'])).count(zip[i])
            }
            map_data.append(frame)       
        
        #--------------------------------- Response ----------------------------------------
        return Response({'Message':'TRUE',
                        'graph':graph,
                        'percentage':percentage,
                        'age_graph':age_graph,
                        'average_table':average_table,
                        'cards_data':cards_data,
                        'file_name':(f_obj[0])['FILE_NAME'],
                        'file_size':(f_obj[0])['FILE_SIZE'],
                        'map_data':map_data,
                        'lat_mid':np.nansum(np.array(lat))/len(lat),
                        'long_mid':np.nansum(np.array(long))/len(long),
                        })
    except:
        return Response({'Message':'FALSE'})



@api_view(['GET'])
@parser_classes([MultiPartParser,FormParser])
def fileDownload(request,format=None):
    try:
        username = request.GET.get('username')
        file_name = 'uploads/engagement_files/'+username+'.csv'
        f_obj = engagement_file_data.objects.filter(USERNAME = username).values()
        f_name = (f_obj[0])['FILE_NAME'][:-4]
        df = pd.read_csv(file_name)
        df = df.rename(columns=str.lower)
        lat_long_df = pd.read_csv('zip_lat_long.csv')
        df['zip'] =  pd.to_numeric(df['zip'],errors='coerce')
        df = pd.merge(df,lat_long_df,on='zip',how='left')
        out = prob_func(df)
        # a = 'uploads/engagement_download_files/'+f_name+'_'+username+'.csv'
        a = 'uploads/engagement_download_files/'+f_name+'_'+username+'.csv'
        out.to_csv(a,index=False)
        response = FileResponse(open(a, 'rb'))
        return response
    except:
        return Response({'Message':'FALSE'})
        

@api_view(['GET'])
@parser_classes([MultiPartParser,FormParser])
def averageTableDownload(request,format=None):
    try:
        username = request.GET.get('username')

        file_name = 'uploads/engagement_files/'+username+'.csv'
        f_obj = engagement_file_data.objects.filter(USERNAME = username).values()
        f_name = (f_obj[0])['FILE_NAME'][:-4]
        df = pd.read_csv(file_name)
        df = df.rename(columns=str.lower)
        lat_long_df = pd.read_csv('zip_lat_long.csv')
        df['zip'] =  pd.to_numeric(df['zip'],errors='coerce')
        df = pd.merge(df,lat_long_df,on='zip',how='left')

        average_table_df = prob_func(df)
        average_table_df['REGION_ZIP'] = average_table_df['REGION_ZIP'].fillna('unknown')
        average_table_df['PCP_Avail'] = average_table_df['PCP_Avail'].fillna(0)
        average_table_df['Percent_Insured'] = average_table_df['Percent_Insured'].fillna(0)
        average_table_df['per_asian'] = average_table_df['per_asian'].fillna(0)
        average_table_df['per_black'] = average_table_df['per_black'].fillna(0)
        average_table_df['__Ethnic_White'] = average_table_df['__Ethnic_White'].fillna(0)
        average_table_df['__Hispanic_or_Latino_(of_any_race)'] = average_table_df['__Hispanic_or_Latino_(of_any_race)'].fillna(0)
        
        average_table = []
        regions = list(set(list(average_table_df['REGION_ZIP'])))
        
        for i in regions:
            ndf = average_table_df.loc[average_table_df['REGION_ZIP'] == i]
            frame = {
                'region':i,
                '__Ethnic_White':str(np.nansum(np.array(list(ndf['__Ethnic_White'])))/(ndf.shape)[0]),
                'per_black':str(np.nansum(np.array(list(ndf['per_black'])))/(ndf.shape)[0]),
                'per_asian':str(np.nansum(np.array(list(ndf['per_asian'])))/(ndf.shape)[0]),
                '__Hispanic_or_Latino':str(np.nansum(np.array(list(ndf['__Hispanic_or_Latino_(of_any_race)'])))/(ndf.shape)[0]),
                'Percent_Insured':str(np.nansum(np.array(list(ndf['Percent_Insured'])))/(ndf.shape)[0]),
                'PCP_Avail':str(np.nansum(np.array(list(ndf['PCP_Avail'])))/(ndf.shape)[0]),
                'probability_eng':str(np.nansum(np.array(list(ndf['probability_eng'])))/(ndf.shape)[0]),
            }
            average_table.append(frame)

        average_table_csv = pd.DataFrame(average_table)
        a = 'uploads/engagement_download_files/'+'_'+username+'_average_table.csv'
        average_table_csv.to_csv(a,index=False)
        response = FileResponse(open(a, 'rb'))
        
        return response
    except:
        return Response({'Message':'FALSE'})



#-------------------------- Download Components ------------------------------------------------------

@api_view(['GET'])
def totalCommentsDownload(request,format=None):
    try:
        if request.method == 'GET':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            all_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                all_comments = all_comments.filter(REGION__in = state)
                

            if '' not in clinic:
                all_comments = all_comments.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                alert_comments = alert_comments.filter(CLIENT_NAME__in = client)
    
            all_comments = all_comments.values('id')\
            .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            time = F('TIMESTAMP'),
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            provider = F('PROVIDER_NAME'),
                                                            topic = F('TOPIC'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField())
                                                            
                                                )
            all_comments = all_comments.exclude(review = '  ')
            all_comments = sorted(all_comments, key=itemgetter('time'),reverse=True)
            all_comments_df = pd.DataFrame(list(all_comments))
            all_comments_df = all_comments_df[['timestamp','review','topic','provider','client','clinic','label']]
            all_comments_df.rename(columns={'review':'comments'}, inplace=True)
            all_comments_df.rename(columns={'label':'sentiment'}, inplace=True)
            all_comments_df.rename(columns={'timestamp':'date'}, inplace=True)
            all_comments_df.columns = all_comments_df.columns.str.upper()
            username = (request.GET.get('username'))
            a = 'uploads/engagement_download_files/'+username+'_all_comments.csv'
            all_comments_df.to_csv(a,index=False)
            response = FileResponse(open(a, 'rb'))
        return response
    except:
        return Response({'Message':'FALSE'}) 


@api_view(['GET'])
def alertCommentsDownload(request,format=None):
    try:
        if request.method == 'GET':     
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            username = (request.GET.get('username'))
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            
            alert_comments = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()

            state = region
            if '' not in region:
                alert_comments = alert_comments.filter(REGION__in = state)                

            if '' not in clinic:
                alert_comments = alert_comments.filter(NPSCLINIC__in = clinic)
                
            if '' not in client:
                alert_comments = alert_comments.filter(CLIENT_NAME__in = client)


            alert_comments = alert_comments.filter(sentiment_label = 'Extreme').values('id')\
                                                .annotate(
                                                            review = Func(
                                                                Concat(F('REASONNPSSCORE'),V(' '),F('WHATDIDWELLWITHAPP'),V(' '),F('WHATDIDNOTWELLWITHAPP')),
                                                                V('nan'), V(''),
                                                                function='replace'),
                                                            label = F('sentiment_label'),
                                                            timestamp = F('SURVEY_MONTH'), 
                                                            clinic = F('NPSCLINIC'),
                                                            client = F('CLIENT_NAME'),
                                                            topic = F('TOPIC'),
                                                            time = F('TIMESTAMP'),
                                                            question_type = V('REASONNPSSCORE', output_field=CharField())

                                                )
            alert_comments = alert_comments.exclude(review = '  ')
            alert_comments= sorted(alert_comments ,key=itemgetter('time'),reverse=True) 
            alert_comments_df = pd.DataFrame(list(alert_comments))
            alert_comments_df = alert_comments_df[['timestamp','review','topic','client','clinic','label']]
            alert_comments_df.rename(columns={'review':'comments'}, inplace=True)
            alert_comments_df.columns = alert_comments_df.columns.str.upper()
            a = 'uploads/engagement_download_files/'+username+'_alert_comments.csv'
            alert_comments_df.to_csv(a,index=False)
            response = FileResponse(open(a, 'rb'))
        return response
    except:
        return Response({'Message':'FALSE'}) 


@api_view(['GET'])
def providerDataDownload(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            username = (request.GET.get('username')) 
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
        
            providers = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            
            state = region
            if '' not in region:
                providers = providers.filter(REGION__in = state)
                

            if '' not in clinic:
                providers = providers.filter(NPSCLINIC__in = clinic)
            
            if '' not in client:
                providers = providers.filter(CLIENT_NAME__in = client)
            
            providers = providers.exclude(PROVIDER_NAME__in = ['nan']).annotate(provider_name = F('PROVIDER_NAME'))\
                                            .values('provider_name')\
                                            .annotate(
                                                    count = Count(F('REVIEW_ID')),
                                                    promoter = Sum(Case(
                                                        When(nps_label='Promoter',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),
                                                    detractor = Sum(Case(
                                                        When(nps_label='Detractor',then=1),
                                                        default=0,
                                                        output_field=IntegerField()
                                                        )),
                                                    average_nps=Cast(Round((Cast((F('promoter')-F('detractor')),FloatField())/F('count'))*100),IntegerField()),
                                                    provider_type = F('PROVIDERTYPE'),
                                                    provider_category = F('PROVIDER_CATEGORY'),
                                                    score = twoDecimal(Avg('MEMBER_PROVIDER_SCORE')),
                                                    ).order_by('provider_name')

            providers_list = providers.values_list('PROVIDER_NAME',flat=True).distinct()
            providers_list = list(providers_list)
            provider_topics = providerTopic.objects.exclude(PROVIDER_NAME__in = ['nan']).filter(PROVIDER_NAME__in = providers_list).values()
            providers = sorted(list(providers), key=itemgetter('provider_name'))
            provider_topics = sorted(list(provider_topics), key=itemgetter('PROVIDER_NAME'))
            providers_df = pd.concat([pd.DataFrame(providers),pd.DataFrame(provider_topics)[['POSITIVE_TOPIC','NEGATIVE_TOPIC']]],axis=1)
            providers_df = providers_df[['provider_type','provider_name','provider_category','POSITIVE_TOPIC','NEGATIVE_TOPIC','count','score','average_nps']]
            providers_df.rename(columns={'provider_type':'Type',
                                'provider_name':'Name',
                                    'provider_category':'Category',
                                    'POSITIVE_TOPIC':'Top_Positive_Topic',
                                    'NEGATIVE_TOPIC':'Top_Negative_Topic',
                                    'count':'Survey_Count',
                                    'score':'Score',
                                    'average_nps':'NPS'}, inplace=True)
            a = 'uploads/engagement_download_files/'+username+'_provider_data.csv'
            providers_df.to_csv(a,index=False)
            response = FileResponse(open(a, 'rb'))
            return response
    except:
        return Response({'Message':'FALSE'})         


@api_view(['GET'])
def clinicDataDownload(request,format=None):
    try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            username = (request.GET.get('username')) 
             
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub 
            clinic_data = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            state = region
            if '' not in region:
                clinic_data = clinic_data.filter(REGION__in = state)
            if '' not in clinic:
                clinic_data = clinic_data.filter(NPSCLINIC__in = clinic)
            if '' not in client:
                clinic_data = clinic_data.filter(CLIENT_NAME__in = client)
            clinic_data = clinic_data.exclude(NPSCLINIC__in = (['nan','Unknown'])).annotate(clinic=F('NPSCLINIC'))\
                                 .values('clinic')\
                                 .annotate(
                                        clinic_full_name = Concat('NPSCLINIC',V(' '),'CLINIC_CITY', V(' '), 'CLINIC_STATE'),
                                        count = Count(F('REVIEW_ID')),
                                        promoter = Sum(Case(
                                            When(nps_label='Promoter',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        detractor = Sum(Case(
                                            When(nps_label='Detractor',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        nps=Cast(Round((Cast((F('promoter')-F('detractor')),FloatField())/F('count'))*100),IntegerField()),
                                        average_nps = Case(
                                                    When(
                                                        nps__lt = 0,
                                                        then = 0    
                                                        ),
                                                        default=F('nps'),
                                                        output_field=FloatField()
                                                        ),
                                                        
                                        city = F('CLINIC_CITY'),
                                        state = F('CLINIC_STATE'),
                                        address = Concat('CLINIC_CITY', V(', '), 'CLINIC_STATE'),
                                        region = F('REGION')
                                          )\
                                 .order_by('clinic_full_name')

            clinic_list = clinic_data.values_list('clinic_full_name',flat=True).distinct()
            clinic_list = list(clinic_list)
            clinic_topics = clinicTopic.objects.filter(CLINIC_FULL_NAME__in = clinic_list).values()
            clinic_data = sorted(list(clinic_data), key=itemgetter('clinic_full_name'))
            clinic_topics = sorted(list(clinic_topics), key=itemgetter('CLINIC_FULL_NAME'))
            
            clinic_df = pd.concat([pd.DataFrame(clinic_data),pd.DataFrame(clinic_topics)[['POSITIVE_TOPIC','NEGATIVE_TOPIC']]],axis=1)
            clinic_df = clinic_df[['clinic','address','POSITIVE_TOPIC','NEGATIVE_TOPIC','count','average_nps']]
            clinic_df.rename(columns={'clinic':'Name',
                                    'address':'Location',
                                    'POSITIVE_TOPIC':'Top_Positive_Topic',
                                    'NEGATIVE_TOPIC':'Top_Negative_Topic',
                                    'count':'Survey_Count',
                                    'average_nps':'NPS'}, inplace=True)
            a = 'uploads/engagement_download_files/'+username+'health_center_data.csv'
            clinic_df.to_csv(a,index=False)
            response = FileResponse(open(a, 'rb'))
            return response
    except:
        return Response({'Message':'FALSE'})

@api_view(['GET'])
def clientDataDownload(request,format=None):
    # try:
        if request.method == 'GET':
            start_year = request.GET.get('start_year')
            start_month = request.GET.get('start_month')
            end_year = request.GET.get('end_year')
            end_month = request.GET.get('end_month')
            region = (request.GET.get('region'))
            clinic = (request.GET.get('clinic'))
            region = re.split(r"-|,", region)
            clinic = re.split(r"-|,", clinic)
            client = (request.GET.get('client')).split(',')
            username = (request.GET.get('username')) 
            
            start_date = str(start_month)+'-'+str(start_year)
            startDate = (time.mktime(datetime.datetime.strptime(start_date,"%m-%Y").timetuple())) - timestamp_start
            if int(end_month)<12:
                end_date = str(int(end_month)+1)+'-'+str(end_year)
            else:
                end_date = str('1-')+str(int(end_year)+1)
            endDate = (time.mktime(datetime.datetime.strptime(end_date,"%m-%Y").timetuple())) - timestamp_sub
            clients = everside_nps.objects.filter(TIMESTAMP__gte=startDate).filter(TIMESTAMP__lte=endDate).values()
            state = region
            if '' not in region:
                clients = clients.filter(REGION__in = state)
            if '' not in clinic:
                clients = clients.filter(NPSCLINIC__in = clinic)
            if '' not in client:
                clients = clients.filter(CLIENT_NAME__in = client)
            parent_client_names = clients.values_list('PARENT_CLIENT_NAME',flat=True).distinct()
            parent_client_names = sorted(list(parent_client_names))
            clients = clients.exclude(CLIENT_NAME__in = ['nan']).annotate(client_name=F('CLIENT_NAME'))\
                                 .values('client_name')\
                                 .annotate(
                                        parent_client_name = F('PARENT_CLIENT_NAME'),
                                        count = Count(F('REVIEW_ID')),
                                        promoter = Sum(Case(
                                            When(nps_label='Promoter',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        detractor = Sum(Case(
                                            When(nps_label='Detractor',then=1),
                                            default=0,
                                            output_field=IntegerField()
                                            )),
                                        nps_abs=Cast(Round((Cast((F('promoter')-F('detractor')),FloatField())/F('count'))*100),IntegerField()),
                                        average_nps = Case(
                                                            When(
                                                                nps_abs__lt = 0,
                                                                then = 0    
                                                                ),
                                                                default=F('nps_abs'),
                                                                output_field=FloatField()
                                                              )
                                          )\
                                 .order_by('client_name')
            
            clients_list = clients.values_list('client_name',flat=True).distinct()
            clients_list = list(clients_list)
            clients_topics = clientTopic.objects.filter(CLIENT_NAME__in = clients_list).values()
            clients = sorted(list(clients), key=itemgetter('client_name'))
            clients_topics = sorted(list(clients_topics), key=itemgetter('CLIENT_NAME'))

            client_df = pd.concat([pd.DataFrame(clients),pd.DataFrame(clients_topics)[['POSITIVE_TOPIC','NEGATIVE_TOPIC']]],axis=1)
            client_df = client_df[['client_name','parent_client_name','POSITIVE_TOPIC','NEGATIVE_TOPIC','count','average_nps']]
            client_df.rename(columns={'client_name':'Name',
                                    'parent_client_name':'Parent_Client_Name',
                                    'POSITIVE_TOPIC':'Top_Positive_Topic',
                                    'NEGATIVE_TOPIC':'Top_Negative_Topic',
                                    'count':'Survey_Count',
                                    'average_nps':'NPS'}, inplace=True)
            a = 'uploads/engagement_download_files/'+username+'client_data.csv'
            client_df.to_csv(a,index=False)
            response = FileResponse(open(a, 'rb'))
            return response

#-------------------------- Admin rights -------------------------------------------------
@api_view(['POST','GET'])
def userList(request):
    try:
        if request.method == 'POST':
            token = (request.data)['token']
            user = user_data.objects.get(TOKEN=token)
            if(user.USER_TYPE == 'A' or user.USER_TYPE == 'SA'):
                user_list = user_data.objects.exclude(USER_TYPE__in=['T','A']).values_list('USERNAME',flat=True)
                return Response({'Message':'TRUE','user_list':list(user_list)[::-1]})
            else:
                return Response({'Message':'FALSE'})
    except:
        return Response({'Message':'FALSE'})

@api_view(['POST'])
def deleteUser(request):
    try:
        if request.method == 'POST':
            username = (request.data)['username']
            token = (request.data)['token']
            user = user_data.objects.get(TOKEN=token)
            if user.USER_TYPE == 'A' or user.USER_TYPE == 'SA':
                user_data.objects.filter(USERNAME=username).delete()
                try:
                    a = 'uploads/engagement_download_files/'+username+'_alert_comments.csv'
                    os.remove(a)
                except:
                    pass
                try:
                    a = 'uploads/engagement_download_files/'+username+'_all_comments.csv'
                    os.remove(a)
                except:
                    pass
                try:
                    a = 'uploads/engagement_download_files/'+username+'_average_table.csv'
                    os.remove(a)
                except:
                    pass
                try:
                    a = 'uploads/engagement_download_files/'+username+'_provider_data.csv'
                    os.remove(a)
                except:
                    pass
                try:
                    a = 'uploads/engagement_download_files/'+username+'health_center_data.csv'
                    os.remove(a)
                except:
                    pass
                try:
                    a = 'uploads/engagement_download_files/'+username+'client_data.csv'
                    os.remove(a)
                except:
                    pass
                
                try:
                    f_obj = engagement_file_data.objects.filter(USERNAME = username).values()
                    f_name = (f_obj[0])['FILE_NAME'][:-4]
                    a = 'uploads/engagement_download_files/'+f_name+'_'+username+'.csv'
                    os.remove(a)
                except:
                    pass
                
            else:
                return Response({'Message':'FALSE'})
        return Response({'Message':'TRUE'})
    except:
            return Response({'Message':'FALSE'})


@api_view(['POST'])
def resetPassword(request):
    try:
        if request.method == 'POST':
            username = (request.data)['username']
            password = (request.data)['password']
            token = (request.data)['token']
            user = user_data.objects.get(TOKEN=token)
            if user.USER_TYPE == 'A' or user.USER_TYPE == 'SA':
                PASSWORD1 = make_password(password)
                user_data.objects.filter(USERNAME=username).update(PASSWORD=PASSWORD1)
                return Response({'Message':'TRUE'})
            else:
                return Response({'Message':'FALSE'})
    except:
        return Response({'Message':'FALSE'})


@api_view(['POST'])
def createUser(request):
    try:
        if request.method == 'POST':
            firstname = ''
            lastname = ''
            username = ((request.data)['username']).lower()
            email = ((request.data)['email']).lower()
            password = (request.data)['password']
            token = (request.data)['token']
            user = user_data.objects.get(TOKEN=token)
            if user.USER_TYPE == 'A' or user.USER_TYPE == 'SA':     
                PASSWORD1 = make_password(password)
                TOKEN = make_password(username+password)
                try:
                    user_data.objects.get(EMAIL = email)
                    return Response({'Message':'FALSE','Error':'Email already exist'})

                except:
                    pass

                try:
                    user_data.objects.get(USERNAME = username)
                    return Response({'Message':'FALSE','Error':'Username already exist'})
                except:
                    pass

                data = user_data(
                                FIRST_NAME = firstname,
                                LAST_NAME = lastname,
                                USERNAME = username,
                                EMAIL = email,
                                USER_TYPE = '0',
                                PASSWORD = PASSWORD1,
                                TOKEN    = TOKEN,
                )
                data.save()   
            else:
                return Response({'Message':'FALSE'})
            return Response({'Message':'TRUE'})
    except:
        return Response({'Message':'FALSE'})


# def index(request):
#     df = pd.read_csv('01_doctor_scoring.csv')
#     print(df.columns)
#     for i in range(df.shape[0]):
#         review_id = list(df['ID'])[i]
#         score = list(df['MembertoProvider_Score'])[i] 
#         # try:
#         everside_nps.objects.filter(REVIEW_ID = review_id).update(MEMBER_PROVIDER_SCORE = score)

#         print(i)
        

#     # for i in range(df.shape[0]):
#     #     review_id = list(df['ID'])[i]
#     #     member_provider_score = list(df['polarity_score'])[i]
#     #     topic = list(df['topics'])[i]
#     #     everside_nps.objects.filter(REVIEW_ID = review_id).update(POLARITY_SCORE = polarity_score,TOPIC = topic)
#     #     print(i)
#     return HttpResponse('Hello')




#_----------------------------------------------------------------------------

# from apiApp.emai_auth import gmail_authenticate
# from email.mime.multipart import MIMEMultipart
# from base64 import urlsafe_b64decode, urlsafe_b64encode
# from email.mime.text import MIMEText



# def index(request):
#     SCOPES = ['https://mail.google.com/']



#     # get the Gmail API service
#     service = gmail_authenticate()

#     message = MIMEMultipart('alternative')
#     message['to'] = 'vivek.k@ekoinfomatics.com,amrit.s@ekoinfomatics.com'
#     message['from'] = 'nps@ekoinfomatics.com'
#     message['subject'] = 'hello'
#     text = """
#     <!DOCTYPE html>
#     <html >
#     <head>
#         <meta charset="UTF-8">
#         <title>Email Verified</title>
#     </head>
#     <body>
#         <head style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#             <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.12.1/css/all.min.css">
#     <meta name="viewport" content="width=device-width" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#     <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#     <title style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">Hagbad Financial</title>
#     </head>
#     <body style="margin: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; padding: 0; border-top: 2px solid #26334D; -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: none; background-color: white; height: 100%; line-height: 1.6; width: 100%;">
#     <table class="body-wrap" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; width: 100%; background-color: white;">
#         <tr style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#         <td style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; vertical-align: top;"></td>
#         <td width="400" class="container" style="font-size: 14px; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; padding: 0; line-height: 22px; vertical-align: top; margin: 0 auto; display: block; max-width: 400px; clear: both;">
#             <div class="content" style="padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; margin: 0 auto; max-width: 400px; display: block;">
#             <table width="100%" cellpadding="0" cellspacing="0" class="main" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#                 <tr style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#                 <td class="logo" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; vertical-align: top; text-align: center;">
#                     <img src="https://i.imgur.com/jlhOdC3.png" width="200" style="padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; max-width: 100%; margin: 30px 0;">
#                 </td>
#                 </tr>
#                 <tr style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#                 <td class="content-wrap" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; vertical-align: top;">
#                     <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#                         <p style="margin: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; font-weight: normal; margin-bottom: 0; padding: 0 20px;"><strong style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 22px; color: #596C80;">Dear {}, </strong><br><br><strong style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 22px; color: #596C80;">Your email is successfully verified</strong>,
#                         <br>Welcome to Hagbad Financial</p>
#                     <tr style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px;">
#                         <td class="action" style="margin: 0; padding: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #8F9BB3; font-size: 14px; line-height: 22px; vertical-align: top; padding-top: 20px;">
#                         <a class="btn-primary" style="line-height: 22px; margin: 0; box-sizing: border-box; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #ffffff; font-size: 25px; padding: 20px; display: block; font-weight: bold; background: #00E056; border-radius: 3px; text-decoration: none; text-align: center;">Verified <i class="fa fa-check" aria-hidden="true"></i></a>
#                         </td>
#                     </tr>
#                     </table>
#                 </td>
#                 </tr>
#             </table>
#             </div>
#         </td>
#         </tr>
#     </table>
#     </body>
#     </body>
#     </html>
#     """.format('Vivek Khanal')
#     mime_type = MIMEText(text, 'html')
#     message.attach(mime_type)
#     body1 = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

#     service.users().messages().send(
#         userId="me",
#         body=body1
#         ).execute()
#     return HttpResponse('Hello')




#result = table.objects.filter(string__contains='pattern')