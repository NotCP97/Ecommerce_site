from django.urls import path
from .views import *

urlpatterns = [
    path("registration/", registration),
    path("createcategory/",createcategory),
    path("createproduct/",createproduct),
    path("getproduct/<int:pk>/",getproduct),
    path("deleteproduct/<int:pk>/",deleteproduct),
    path("updateproduct/<int:pk>/",updateproduct),
    path("listproducts/",listproducts),
    path("addToCart/",addtocart),
    path("profile/", profile),
    path("cart/",showcart),
    path("updateuser/", updateuser),
    path("updateprofile/", UpdateProfile),
]