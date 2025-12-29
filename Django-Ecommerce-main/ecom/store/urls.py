from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_info, name='update_info'),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:foo>', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    path('search/', views.search, name='search'),
    path('api/products/', views.api_product_list, name='api_product_list'),
    path('api/placed-orders/', views.api_placed_orders, name='api_placed_orders'),
    path('api/revenue-by-category/', views.api_total_revenue_by_category, name='api_revenue_by_category'),
    path('api/highest-selling-product/', views.api_highest_selling_product, name='api_highest_selling_product'),
    path('api/least-desirable-product/', views.api_least_desirable_product, name='api_least_desirable_product'),
]
