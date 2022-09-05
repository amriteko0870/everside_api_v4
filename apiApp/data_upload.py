from django.http import HttpResponse
from apiApp.models import clientTopic, clinicTopic, everside_nps, providerTopic
import pandas as pd 
import time
import datetime

from django.db.models import F,Func,Q
from django.db.models import Value as V
from django.db.models.functions import Concat,Cast,Substr
from django.db.models import Min

def db_upload(request):
    df = pd.read_csv('05_final_aug_2022.csv')
    df.fillna('Unknown', inplace=True)
    region = pd.read_csv("regionState.csv")
    for i in range(df.shape[0]):
        REVIEW_ID = list(df['ID'])[i]
        MEMBER_ID = list(df['MEMBER_ID'])[i]
        NPSCLINIC = list(df['NPSCLINIC__C'])[i]
        SURVEYDATE = list(df['SURVEYDATE__C'])[i]
        SURVEYNUMBER = list(df['SURVEYNUMBER__C'])[i]
        NPS = list(df['NPS'])[i]
        REASONNPSSCORE = list(df['REASONNPSSCORE__C'])[i]
        WHATDIDWELLWITHAPP = list(df['WHATDIDWELLWITHAPP__C'])[i]
        WHATDIDNOTWELLWITHAPP = list(df['WHATDIDNOTWELLWITHAPP__C'])[i]
        HOUSEHOLD_ID = list(df['HOUSEHOLD_ID'])[i]
        MEMBER_CITY = list(df['MEMBER_CITY'])[i]
        MEMBER_STATE = list(df['MEMBER_STATE'])[i]
        MEMBER_ZIP = list(df['MEMBER_ZIP'])[i]
        CLINIC_ID = list(df['CLINIC_ID'])[i]
        CLINIC_STREET = list(df['CLINIC_STREET'])[i]
        CLINIC_CITY = list(df['CLINIC_CITY'])[i]
        CLINIC_STATE = list(df['CLINIC_STATE'])[i]
        CLINIC_ZIP = list(df['CLINIC_ZIP'])[i]
        CLINIC_TYPE = list(df['CLINIC_TYPE'])[i]
        PROVIDER_NAME = list(df['PROVIDER_NAME'])[i]
        PROVIDERTYPE = list(df['PROVIDERTYPE__C'])[i]
        PROVIDER_CATEGORY = list(df['PROVIDER_CATEGORY__C'])[i]
        CLIENT_ID = list(df['CLIENT_ID'])[i]
        sentiment_label = list(df['sentiment_label'])[i]
        nps_label = list(df['nps_label'])[i]
        CLIENT_NAME = list(df['CLIENT NAME'])[i]
        PARENT_CLIENT_NAME = list(df['PARENT CLIENT NAME'])[i]
        PARENT_CLIENT_ID = list(df['PARENT_CLIENT_ID'])[i]
        POLARITY_SCORE = list(df['polarity_score'])[i]
        TOPIC = list(df['topics'])[i]
        ENCOUNTER_REASON = list(df['ENCOUNTER_REASON'])[i]
        MEMBER_PROVIDER_SCORE = list(df['MembertoProvider_Score'])[i]
        TIMESTAMP = time.mktime(datetime.datetime.strptime(list(df['SURVEYDATE__C'])[i],"%d-%m-%Y").timetuple())
        SURVEY_MONTH = datetime.datetime.fromtimestamp(TIMESTAMP).strftime('%b-%y')
        SURVEY_YEAR = datetime.datetime.fromtimestamp(TIMESTAMP).strftime('%Y')
        REGION = str(region.loc[(region['State']==str(CLINIC_STATE))].tail(1)['Region'].to_list()[-1]).strip()
        data = everside_nps(REVIEW_ID = REVIEW_ID,
                MEMBER_ID = MEMBER_ID,
                NPSCLINIC = NPSCLINIC,
                SURVEYDATE = SURVEYDATE,
                SURVEY_MONTH = SURVEY_MONTH,
                SURVEY_YEAR = SURVEY_YEAR,
                SURVEYNUMBER = SURVEYNUMBER,
                NPS = NPS,
                REASONNPSSCORE = REASONNPSSCORE,
                WHATDIDWELLWITHAPP = WHATDIDWELLWITHAPP,
                WHATDIDNOTWELLWITHAPP = WHATDIDNOTWELLWITHAPP,
                HOUSEHOLD_ID = HOUSEHOLD_ID,
                MEMBER_CITY = MEMBER_CITY,
                MEMBER_STATE = MEMBER_STATE,
                MEMBER_ZIP = MEMBER_ZIP,
                CLINIC_ID = CLINIC_ID,
                CLINIC_STREET = CLINIC_STREET,
                CLINIC_CITY = CLINIC_CITY,
                CLINIC_STATE = CLINIC_STATE,
                CLINIC_ZIP = CLINIC_ZIP,
                CLINIC_TYPE = CLINIC_TYPE,
                PROVIDER_NAME = PROVIDER_NAME,
                PROVIDERTYPE = PROVIDERTYPE,
                PROVIDER_CATEGORY = PROVIDER_CATEGORY,
                CLIENT_ID = CLIENT_ID,
                sentiment_label = sentiment_label,
                nps_label = nps_label,
                CLIENT_NAME = CLIENT_NAME,
                PARENT_CLIENT_NAME = PARENT_CLIENT_NAME,
                PARENT_CLIENT_ID = PARENT_CLIENT_ID,
                REGION = REGION,
                TIMESTAMP = TIMESTAMP,
                POLARITY_SCORE = POLARITY_SCORE,
                TOPIC = TOPIC,
                ENCOUNTER_REASON = ENCOUNTER_REASON,
                MEMBER_PROVIDER_SCORE = MEMBER_PROVIDER_SCORE)
        data.save()
        print("M",i)
        # break
    #---------------TOPIC INSERTION -----------------------------------------------------

    #-------------------Providers Topics ----------------------------------------------
    providerTopic.objects.all().delete()
    p = everside_nps.objects.values_list('PROVIDER_NAME',flat=True).distinct()
    c = 0
    for i in p:
        n = everside_nps.objects.filter(PROVIDER_NAME = i).filter(sentiment_label__in = ['Negative','Extreme']).annotate(Min('POLARITY_SCORE')).order_by('POLARITY_SCORE').first()
        p = everside_nps.objects.filter(PROVIDER_NAME = i).filter(sentiment_label__in = ['Positive']).annotate(Min('POLARITY_SCORE')).order_by('POLARITY_SCORE').last() 
        try:
            pos_topic = p.TOPIC
        except:
            pos_topic = 'No Topic'
        
        try:
            neg_topic = n.TOPIC
        except:
            neg_topic = 'No Topic'
        data = providerTopic(
                            PROVIDER_NAME = i,
                            POSITIVE_TOPIC = pos_topic,
                            NEGATIVE_TOPIC = neg_topic,
                            
        )
        data.save()
        print("P",c)
        c = c + 1 
        # break
    
    # --------------------- Clinic Topics ----------------------------------------------
    clinicTopic.objects.all().delete()
    p = everside_nps.objects.exclude(NPSCLINIC__in = ['Unknown','nan']).annotate(
        clinic_full_name = Concat(F('NPSCLINIC'),V(' '),F('CLINIC_CITY'),V(' '),F('CLINIC_STATE')),
        clinic = F('NPSCLINIC'),
        city = F('CLINIC_CITY'),
        state = F('CLINIC_STATE'),
    ).values_list('clinic_full_name','clinic','city','state').distinct()
    c = 0
    for i in p:
        n = everside_nps.objects.filter(NPSCLINIC = i[1],CLINIC_CITY = i[2],CLINIC_STATE = i[3]).filter(sentiment_label__in = ['Negative','Extreme']).annotate(Min('POLARITY_SCORE')).order_by('POLARITY_SCORE').first()
        p = everside_nps.objects.filter(NPSCLINIC = i[1],CLINIC_CITY = i[2],CLINIC_STATE = i[3]).filter(sentiment_label__in = ['Positive']).annotate(Min('POLARITY_SCORE')).order_by('POLARITY_SCORE').last()
        try:
            pos_topic = p.TOPIC
        except:
            pos_topic = 'No Topic'

        try:
            neg_topic = n.TOPIC
        except:
            neg_topic = 'No Topic'
        data = clinicTopic(
                            CLINIC_FULL_NAME = i[0],
                            NPSCLINIC = i[1],
                            POSITIVE_TOPIC = pos_topic,
                            NEGATIVE_TOPIC = neg_topic,
                            
        )
        data.save()
        print('CN',c)
        c = c + 1 
        # break
    #----------------------- Client Topics ------------------------------------------------
    clientTopic.objects.all().delete()
    p = everside_nps.objects.exclude(CLIENT_NAME__in = ['nan']).values_list('CLIENT_NAME',flat=True).distinct()
    c = 0
    for i in p:
        n = everside_nps.objects.filter(CLIENT_NAME = i).filter(sentiment_label__in = ['Negative','Extreme']).annotate(Min('POLARITY_SCORE')).order_by('POLARITY_SCORE').first()
        p = everside_nps.objects.filter(CLIENT_NAME = i).filter(sentiment_label__in = ['Positive']).annotate(Min('POLARITY_SCORE')).order_by('POLARITY_SCORE').last()
        try:
            pos_topic = p.TOPIC
        except:
            pos_topic = 'No Topic'

        try:
            neg_topic = n.TOPIC
        except:
            neg_topic = 'No Topic'
        data = clientTopic(
                            CLIENT_NAME = i,
                            POSITIVE_TOPIC = pos_topic,
                            NEGATIVE_TOPIC  = neg_topic,
                            )
        data.save()
        print("CL",c)
        c = c + 1 
        # break
    
    #---------------------------- Provider type and category handle---------------------------------
    count = everside_nps.objects.all().values_list('PROVIDER_NAME',flat=True).distinct()
    for i in range(len(count)):
        p_details = everside_nps.objects.filter(PROVIDER_NAME=count[i]).values('PROVIDERTYPE','PROVIDER_CATEGORY')
        p_update = everside_nps.objects.filter(PROVIDER_NAME=count[i])\
                                       .update(PROVIDERTYPE = p_details.last()['PROVIDERTYPE'],
                                               PROVIDER_CATEGORY = p_details.last()['PROVIDER_CATEGORY'])

        print('H',i)
    return HttpResponse('hello')


def provider_cat_set(request):
    count = everside_nps.objects.all().values_list('PROVIDER_NAME',flat=True).distinct()
    for i in range(len(count)):
        p_details = everside_nps.objects.filter(PROVIDER_NAME=count[i]).values('PROVIDERTYPE','PROVIDER_CATEGORY')
        p_update = everside_nps.objects.filter(PROVIDER_NAME=count[i])\
                                       .update(PROVIDERTYPE = p_details.last()['PROVIDERTYPE'],
                                               PROVIDER_CATEGORY = p_details.last()['PROVIDER_CATEGORY'])

        print(i)
    return HttpResponse('Hello')