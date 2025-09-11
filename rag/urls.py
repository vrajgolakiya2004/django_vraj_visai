from django.urls import path
from .views import AiChatBotFun, ChatApi, ChatHistory, GetSessionHistory, CreateSession, RenameSession, DeleteSession

urlpatterns = [
    path('ai-chat-bot/', AiChatBotFun, name='aiChatBotPage'),
    path('chat/history/<str:session_id>/', GetSessionHistory, name='chat_history_session'),
    path('chat/rename-session/<str:session_id>/', RenameSession, name='rename_session'),
    path('chat/delete-session/<str:session_id>/', DeleteSession, name='delete_session'),
    path('chat/new-session/', CreateSession, name='new_session'),
]
