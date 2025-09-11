from django.urls import path 
from .views import AiChatBotFun, ChatApi, ChatHistory, GetSessionHistory, CreateSession, RenameSession, DeleteSession 

urlpatterns = [

    path('api/chat/', ChatApi, name='chat_api'),
    path('api/chat/history/', ChatHistory, name='chat_history'),
    path('api/chat/history/<str:session_id>/', GetSessionHistory, name='get_session_history'),
]
