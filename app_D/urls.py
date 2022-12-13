from django.contrib import admin
from django.urls import path
from app_D import views

urlpatterns = [
    path('', views.home,name='home'),
    path('airtable/',views.airtableview,name="airtable"),
]
