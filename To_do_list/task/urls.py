from django.urls import path
from . import views
from .views import TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskDelete

urlpatterns = [

    path('', TaskList.as_view(), name='a'),
    path('task-detail/<int:pk>/', TaskDetail.as_view(), name='b'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', TaskDelete.as_view(), name='task-delete'),

    path('signin/', views.signin, name = 'signin'),
    path('signup/', views.signup, name='signup'),
    path('signin/signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('signin/forgot_password/', views.forgot_password, name='forgot_password'),
    path('change_password_form/<uidb64>/<token>/', views.change_password_form, name='change_password_form')

]