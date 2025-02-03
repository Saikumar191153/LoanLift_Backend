from django.urls import path    
from django.conf import settings
from django.conf.urls.static import static
from .  import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('change-password/', views.change_password, name='change_password'),    
    path('add_loan_application/', views.add_loan_application, name='add_loan_application'),
    path('get_dashboard_data/', views.get_dashboard_data, name='get_dashboard_data'),
    path('add_corporate_project/', views.add_corporate_project, name='add_corporate_project'),
    path('get_corporate_project_detail/', views.get_corporate_project_detail, name='get_corporate_project_detail'),
    path('get_all_applications/',views.get_all_applications,name='get_all_applications'),
    path('get_application_by_id/<int:application_id>',views.get_application_by_id,name='get_application_by_id'),
    path('update_loan_application/<int:application_id>',views.update_loan_application,name='update_loan_application'),
    path('delete_loan_application/<int:application_id>',views.delete_loan_application,name='delete_loan_application'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)