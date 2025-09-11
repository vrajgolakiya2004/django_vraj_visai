from django.db import models
from django.conf import settings
from register.models import User

class PlanModel(models.Model):
    chatbot_plan_plan_name = models.CharField(max_length=50, unique=True)
    chatbot_plan_description = models.TextField()
    chatbot_plan_price = models.DecimalField(max_digits=8, decimal_places=2)  
    chatbot_plan_token = models.IntegerField(help_text="Message token limit for the plan")
    chatbot_plan_word_token = models.IntegerField(help_text="Word token limit for the plan")

    class Meta:
        db_table = 'chatbot_plan_tb'

    def __str__(self):
        return self.chatbot_plan_plan_name
    
class SubscriptionModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(PlanModel, on_delete=models.CASCADE)

    chatbot_subscription_is_active = models.BooleanField(default=True)
    chatbot_subscription_remaining_token = models.IntegerField()
    chatbot_subscription_remaining_word_token = models.IntegerField()
    chatbot_subscription_card_holder_name = models.CharField(max_length=100)
    chatbot_subscription_card_number = models.CharField(max_length=20)  
    chatbot_subscription_expiry_month = models.IntegerField()
    chatbot_subscription_expiry_year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_subscription_tb'

    def __str__(self):
        return f"{self.user.username} - {self.plan.chatbot_plan_plan_name}"