import random
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import ChatSessionModel, ChatHistoryModel
from .generate_response import generate_response
from register.models import User
from django.utils import timezone
from datetime import timedelta

def AiChatBotFun(request):
    session_id = request.GET.get('session_id') or request.session.get('chat_session_id')
    
    if not session_id:
        session_id = 'session-' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=3))
        request.session['chat_session_id'] = session_id
        
        if 'chat_session_ids' not in request.session:
            request.session['chat_session_ids'] = []
        if session_id not in request.session['chat_session_ids']:
            request.session['chat_session_ids'].append(session_id)
            request.session.modified = True

    chat_session, created = ChatSessionModel.objects.get_or_create(
        chat_session_id=session_id,
        defaults={
            'user': request.user if request.user.is_authenticated else None,
            'chat_title': "New Chat"
        }
    )

    chat_messages = ChatHistoryModel.objects.filter(
        session=chat_session
    ).order_by('chatbot_created_at')
    
    formatted_messages = []
    for msg in chat_messages:
        formatted_messages.append({
            "type": "your__chat",
            "author": "You",
            "message": msg.chatbot_message
        })
        formatted_messages.append({
            "type": "bot__chat",
            "author": "AI Assistant",
            "message": msg.chatbot_response
        })

    return render(request, "ai-chat-bot.html", {
        "chat_title": chat_session.chat_title,
        "chat_messages": formatted_messages,
        "session_id": session_id
    })

@csrf_exempt
def ChatApi(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")
        session_id = data.get("session_id", "")
        chat_title = data.get("chat_title", "New Chat")

        user_id = request.session.get('user_id')
        chatbot_user = User.objects.get(id=user_id) if user_id else None

        chat_session = ChatSessionModel.objects.get(chat_session_id=session_id)
        
        if chat_session.chat_title == "New Chat" and user_message:
            new_title = user_message[:30] + ('...' if len(user_message) > 30 else '')
            chat_session.chat_title = new_title
            chat_session.save()

        if chat_session.user is None and chatbot_user is not None:
            chat_session.user = chatbot_user
            chat_session.save()

        ai_response = generate_response(user_message, {
            "business_type": "unknown",
            "experience_level": "unknown"
        })

        ChatHistoryModel.objects.create(
            chatbot_user=chatbot_user,
            session=chat_session,
            chatbot_message=user_message,
            chatbot_response=ai_response
        )

        return JsonResponse({
            "status": "success",
            "response": ai_response,
            "session_id": session_id
        })

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def ChatHistory(request):
    """Get list of all chat sessions for the logged-in user"""
    if request.method == "GET":
        user_id = request.session.get('user_id')

        if not user_id:
            return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)

        try:
            sessions = ChatSessionModel.objects.filter(user_id=user_id).order_by('-created_at')

            sessions_data = [{
                "chat_session_id": session.chat_session_id,
                "chat_title": session.chat_title,
                "created_at": session.created_at.strftime("%b %d, %H:%M")
            } for session in sessions]

            return JsonResponse({"status": "success", "sessions": sessions_data})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Only GET requests allowed"}, status=405)

@csrf_exempt
def CreateSession(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed"}, status=405)

    try:
        user_id = request.session.get('user_id')
        chatbot_user = User.objects.get(id=user_id) if user_id else None

        session_id = 'session-' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=3))
        
        if 'chat_session_ids' not in request.session:
            request.session['chat_session_ids'] = []
        request.session['chat_session_ids'].append(session_id)
        request.session['chat_session_id'] = session_id
        request.session.modified = True

        chat_session = ChatSessionModel.objects.create(
            user=chatbot_user,
            chat_session_id=session_id,
            chat_title=f"New Chat {ChatSessionModel.objects.count() + 1}"
        )

        return JsonResponse({
            "status": "success",
            "session_id": session_id,
            "chat_title": chat_session.chat_title
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@csrf_exempt
def RenameSession(request, session_id):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body)
        new_title = data.get('title', '').strip()  # Looking for 'title' field
        
        if not new_title:
            return JsonResponse({"status": "error", "message": "Title cannot be empty"}, status=400)

        chat_session = ChatSessionModel.objects.get(chat_session_id=session_id)
        chat_session.chat_title = new_title
        chat_session.save()

        return JsonResponse({"status": "success", "new_title": new_title})

    except ChatSessionModel.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Session not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
@csrf_exempt
def DeleteSession(request, session_id):
    if request.method != 'DELETE':
        return JsonResponse({"status": "error", "message": "Only DELETE requests are allowed"}, status=405)

    try:
        chat_session = ChatSessionModel.objects.get(chat_session_id=session_id)
        chat_session.delete()
        
        session_ids = request.session.get('chat_session_ids', [])
        if session_id in session_ids:
            session_ids.remove(session_id)
            request.session['chat_session_ids'] = session_ids
            request.session.modified = True
        
        return JsonResponse({"status": "success"})

    except ChatSessionModel.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Session not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def GetSessionHistory(request, session_id):
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "Only GET requests are allowed"}, status=405)

    try:
        chat_session = ChatSessionModel.objects.get(chat_session_id=session_id)
        chat_messages = ChatHistoryModel.objects.filter(session=chat_session).order_by('chatbot_created_at')
        
        chats = [
            {
                "user_message": msg.chatbot_message,
                "bot_response": msg.chatbot_response,
                "timestamp": msg.chatbot_created_at.isoformat()
            }
            for msg in chat_messages
        ]

        return JsonResponse({
            "status": "success",
            "chats": chats,
            "chat_title": chat_session.chat_title
        })

    except ChatSessionModel.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Session not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)