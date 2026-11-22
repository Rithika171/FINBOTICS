from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('add-transaction/', views.add_transaction,name='add_transaction'),
    path('transactions/', views.transactions, name='transactions'),
    path('edit-transaction/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete-transaction/<int:pk>/', views.delete_transaction,name='delete_transaction'),
    path('ai-insights/', views.ai_insights, name='ai_insights'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('budget-dashboard/', views.budget_dashboard, name='budget_dashboard'),
    path('scam-detection/',views.scam_detection,name='scam_detection'),
    path('scam-history/delete/<int:history_id>/',views.delete_scam_history,name='delete_scam_history'),
    path('savings-goals/', views.savings_goals, name='savings_goals'),
    path('savings-goals/add/<int:goal_id>/', views.add_savings, name='add_savings'),
    path('savings-goals/delete/<int:goal_id>/', views.delete_savings_goal, name='delete_savings_goal'),
    path('savings-goals/edit/<int:goal_id>/', views.edit_savings_goal, name='edit_savings_goal'),
    path('chatbot-response/', views.chatbot_response, name='chatbot_response'),
]