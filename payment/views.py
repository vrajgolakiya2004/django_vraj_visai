import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import PlanModel
from django.contrib.auth import get_user_model
from payment.models import PlanModel, SubscriptionModel
import logging
from django.conf import settings
from .models import PlanModel, SubscriptionModel
from register.models import User


logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEBHOOK_ENDPOINT_SECRET


def PricingFun(request):
    plans = PlanModel.objects.all()
    context = {
        'plans': plans,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'pricing.html', context)


@csrf_exempt
def CreateCheckoutSession(request):
    if request.method == 'POST':
        plan_name = request.POST.get('plan')
        print(f"📌 Plan Name: {plan_name}")
        user_id = request.session.get('user_id')
        print(f"📌 User ID: {user_id}")

        if not user_id:
            return JsonResponse({'error': 'User not logged in'}, status=401)

        plan = get_object_or_404(PlanModel, chatbot_plan_plan_name__iexact=plan_name)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.chatbot_plan_plan_name,
                    },
                    'unit_amount': int(plan.chatbot_plan_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment:payment-success')),
            cancel_url=request.build_absolute_uri(reverse('payment:payment-cancel')),
            metadata={
                'user_id': str(user_id),
                'plan_id': str(plan.id),
                'plan_token': str(plan.chatbot_plan_token),
                'plan_word_token': str(plan.chatbot_plan_word_token),
            }
        )

        print(f"✅ Stripe Session URL: {session.url}")
        return redirect(session.url, code=303)

    return HttpResponse(status=405)


@csrf_exempt
def MyWebhookView(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.WEBHOOK_ENDPOINT_SECRET)
        print("✅ Webhook event type:", event['type'])

    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print("❌ Webhook signature error:", e)
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        print("📌 Metadata received:", metadata)

        user_id = metadata.get('user_id')
        plan_id = metadata.get('plan_id')
        card_holder_name = session.get('customer_details', {}).get('name', 'Unknown')
        print(f"📌 User ID: {user_id}, Plan ID: {plan_id}, Card Holder Name: {card_holder_name}")
        if not user_id or not plan_id:
            print("❌ Missing metadata values.")
            return HttpResponse(status=400)

        print(user_id)
        try:
            print(f"📌 User ID from session: {user_id}")
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            print(f"❌ User with ID {user_id} not found.")
            return HttpResponse(status=404)

        try:
            plan = PlanModel.objects.get(id=plan_id)
        except PlanModel.DoesNotExist:
            print(f"❌ Plan with ID {plan_id} not found.")
            return HttpResponse(status=404)

        try:
            SubscriptionModel.objects.create(
                user=user,
                plan=plan,
                chatbot_subscription_is_active=True,
                chatbot_subscription_remaining_token=plan.chatbot_plan_token,
                chatbot_subscription_remaining_word_token=plan.chatbot_plan_word_token,
                chatbot_subscription_card_holder_name=card_holder_name,
                chatbot_subscription_card_number='XXXX-XXXX-XXXX-4242',
                chatbot_subscription_expiry_month=12,
                chatbot_subscription_expiry_year=2030,
            )
            print("✅ Subscription created successfully!")
        except Exception as e:
            print(f"❌ Error saving subscription: {e}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)

def PaymentSuccess(request):
    """Display success page after successful payment"""

    userid = request.session.get('user_id')
    return render(request, 'payment_success.html')

def PaymentCancel(request):
    """Display cancel page when payment is canceled"""
    return render(request, 'payment_cancel.html')

