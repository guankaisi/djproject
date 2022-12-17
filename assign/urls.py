from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views
from mysite.settings import LOGIN_URL 

app_name = 'assign'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    #path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    #path('<int:question_id>/vote/', views.vote, name='vote'),
    path('teacher/index/', views.teacher_index, name='teacher_index'),
    path('teacher/enroll/', views.teacher_enroll, name='teacher_enroll'),
    path('teacher/info/', views.person_info, name='teacher_info'),
    path('admin/index/',views.admin_index, name='admin_index'),
    path('admin/account/', views.admin_account, name='admin_account'),
    path('admin/seat/', views.admin_seat, name='admin_seat'),
    path('admin/auto/', views.auto_assign, name='admin_auto'),
    path('admin/graduate',views.admin_graduate,name='admin_graduate'),
    path('search/', views.search, name='search'),
    path('query/', views.query, name='query'),
    path('info/', views.person_info, name='person_info'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views._login, name='login'),
    path('accounts/loggin/', views.loggin, name='loggin'),
    path('accounts/logout/', views.logout, name='logout'),
    path('accounts/cas', views.cas, name='cas'),
    #url for testing form
    path('name/', views.get_name, name='name'),
    path('test/',views.test,name='test'),
    #ѧ����Ϣҳ��
    path('admin/info/json',views.admin_info_JSON,name='admin_info_JSON'),
    path('admin/info/',views.admin_info,name='admin_info'),

    ## ����Ա�Ʒ�ҳ��
    path('admin/fee/',views.admin_fee,name='admin_fee'),
    ## ��ʦ�Ʒ�ҳ��
    path('teacher/fee/',views.teacher_fee,name='teacher_fee')
]