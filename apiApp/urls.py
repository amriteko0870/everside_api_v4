from unicodedata import name

from django.urls import include, path

from . import views
from apiApp.data_upload import db_upload,provider_cat_set


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #-------------------Filters------------------------------------
    path('filterRegion',views.filterRegion,name='filterRegion'),
    path('filterClinic',views.filterClinic,name='filterClinic'),
    path('filterClient',views.filterClient,name='filterClient'),

    #-------------------login-----------------------------------------
    path('userLogin',views.userLogin,name='userLogin'),
    
    #-----------------Api Calls----------------------------------------
    path('netPromoterScore',views.netPromoterScore,name='netPromoterScore'),
    path('netSentimentScore',views.netSentimentScore,name='netSentimentScore'),
    path('totalCards',views.totalCards,name='totalCards'),
    path('totalComments',views.totalComments,name='totalComments'),
    path('positiveComments',views.positiveComments,name='positiveComments'),
    path('negativeComments',views.negativeComments,name='negativeComments'),
    path('neutralComments',views.neutralComments,name='neutralComments'),
    path('extremeComments',views.extremeComments,name='extremeComments'),
    path('alertComments',views.alertComments,name='alertComments'),
    path('npsOverTime',views.npsOverTime,name='npsOverTime'),
    path('nssOverTime',views.nssOverTime,name='nssOverTime'),
    path('npsVsSentiments',views.npsVsSentiments,name='npsVsSentiments'),
    path('providersData',views.providersData,name='providersData'),
    path('clinicData',views.clinicData,name='clinicData'),
    path('clientData',views.clientData,name='clientData'),
    path('npsAverageGraph',views.npsAverageGraph,name='npsAverageGraph'),

    #-----------------------Provider Cards -------------------------------------
    path('filterDateProvider',views.filterDateProvider,name='filterDateProvider'),
    path('filterRegionProvider',views.filterRegionProvider,name='filterRegionProvider'),
    path('filterClinicProvider',views.filterClinicProvider,name='filterClinicProvider'),
    path('filterClientProvider',views.filterClientProvider,name='filterClientProvider'),
    
    
    
    
 
    
    #------------------Engagement------------------------------
    path('egMemberPercentile',views.egMemberPercentile,name='egMemberPercentile'),
    path('fileDownload',views.fileDownload,name='fileDownload'),


    #------------------ Download files -----------------------------
    path('averageTableDownload',views.averageTableDownload,name='averageTableDownload'),
    path('totalCommentsDownload',views.totalCommentsDownload,name='totalCommentsDownload'),
    path('alertCommentsDownload',views.alertCommentsDownload,name='alertCommentsDownload'),
    path('providerDataDownload',views.providerDataDownload,name='providerDataDownload'),
    path('clinicDataDownload',views.clinicDataDownload,name='clinicDataDownload'),
    path('clientDataDownload',views.clientDataDownload,name='clientDataDownload'),
    path('providerScoreCard',views.providerScoreCard,name='providerScoreCard'),
    # path('providerEmail',views.providerEmail,name='providerEmail'),
    path('providerCommentDownload',views.providerCommentDownload,name='providerCommentDownload'),
    
    
    
    
    
    #------------------ Files Delete -------------------------------------
    path('logout',views.logout,name='logout'),
    

    #------------------- Users ----------------------------------------------
    path('resetPassword',views.resetPassword,name='resetPassword'),
    path('createUser',views.createUser,name='createUser'),
    path('userList',views.userList,name='userList'),
    path('deleteUser',views.deleteUser,name='deleteUser'),



    
    

    
    

    # path('',db_upload,name='index'),
    # path('',provider_cat_set,name='index'),
    # path('',views.index,name='index'),   
]+static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
