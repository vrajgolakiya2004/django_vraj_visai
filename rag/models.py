from django.db import models
from register.models import User  

class ChatSessionModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_sessions",
        null=True,
        blank=True 
    )
    chat_session_id = models.CharField(max_length=100, unique=True)
    chat_title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_session" 

    def __str__(self):
        return f"{self.chat_title} ({self.user.chatbot_registration_name})"


class ChatHistoryModel(models.Model):
    chatbot_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chats',
        null=True,
        blank=True
    )

    session = models.ForeignKey(
        ChatSessionModel,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        null=True
    )

    chatbot_message = models.TextField()
    chatbot_response = models.TextField()
    chatbot_created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_history"  

    def __str__(self):
        return f'Chat for {self.chatbot_user.chatbot_registration_name} in session {self.session.chat_title}'
    
