from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^getEachYearData',views.fetchEachYearData, name='getEachYearData'),
    url(r'^getData', views.fetchData, name='getData'),
    url(r'^getYearDelta', views.fetchYearDelta, name='getYearDelta'),
    url(r'^trainSystem', views.trainSystem, name='trainSystem'),
    url(r'^getLegend', views.fetchLegend, name='getLegend'),
    url(r'^getStatus', views.getTrainingStatus, name='getTrainingStatus'),
    url(r'^getPredictionResults', views.getPredictionResult, name='getPredictionResults')
]