from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('', views.cart_details, name='cart_details'),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),
]