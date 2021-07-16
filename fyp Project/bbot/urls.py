from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('productview', views.productview, name='productview'),
    path('sendMsg', views.send_msg),
    path('addproduct', views.addproduct, name='addproduct'),
    path('addnewproduct', views.addnewproduct, name='addnewproduct'),
    path('editproduct', views.editproduct, name='editproduct'),
    path('productedited', views.productedited, name='productedited'),
    path('productadded', views.productadded, name='productadded')
]