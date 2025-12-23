from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from menu import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/add-delicious/', views.add_delicious, name='add_delicious'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/psw-data/', views.get_psw_data, name='get_psw_data'),
    path('api/add-psw-account/', views.add_psw_account, name='add_psw_account'),
    path('api/delete-psw-account/<int:account_id>/', views.delete_psw_account, name='delete_psw_account'),
    path('api/delicious-data/', views.get_delicious_data, name='get_delicious_data'),
    path('api/upload-image/', views.upload_image, name='upload_image'),
    path('api/menu-data/', views.menu_data, name='menu_data'),
    path('api/delete-menu/<int:id>/', views.delete_menu, name='delete_menu'),
    path('api/add-like/', views.add_like, name='add_like'),
    path('api/today-menu/', views.today_menu, name='today_menu'),
]

# 开发环境下提供静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
