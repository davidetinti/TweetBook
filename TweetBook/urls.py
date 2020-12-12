from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index),
    path('search/', views.search),
    path('component/<str:name>', views.component),
    path('loginStart/', views.login_start),
    path('loginWait/', views.login_wait),
    path('loginDone/', views.login_done),
    path('getUserData/', views.get_user_data),
    path('postStatus/', views.post_status),
    path('sendMail/', views.notify),
]
