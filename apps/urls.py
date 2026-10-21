from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('category/', views.catalog, name='catalog'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('search/', views.search, name='search'),

    path('product-detail/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product-detail/<slug:slug>/review/', views.product_review, name='product_review'),

    path('order/create/<slug:slug>/', views.order_create, name='order_create'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),

    path('markets/', views.market_list, name='market_list'),
    path('market/<slug:slug>/', views.market_detail, name='market_detail'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('cabinet/', views.cabinet, name='cabinet'),
]