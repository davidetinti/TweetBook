from django.urls import path
from . import views

urlpatterns = [
	path('', views.index),
	path('search/', views.search),
	path('component/<str:name>', views.component)
]
