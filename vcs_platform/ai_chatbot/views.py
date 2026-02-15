import json
import cohere

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from accounts.models import Profile
from .models import ChatLog, ChatUsage, ChatEscalation


# -----------------------------------
# Cohere Client
# -----------------------------------
co = cohere.Client(settings.COHERE_API_KEY)

AI_COST_PER_QUERY = 0.002


# -----------------------------------
# Cohere Chat Function (NEW API)
# -----------------------------------
def cohere_chat(prompt: str) -> str:
    try:
        response = co.chat(
            model="command-r",   # Latest chat model
            message=prompt
        )

        return response.text.strip()

    except Exception as e:
        print("🔥 Cohere AI ERROR:", e)
        return "AI error occurred"


# -----------------------------------
# AI Chat View
# -----------------------------------
import json
import cohere

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from accounts.models import Profile
from .models import ChatLog, ChatUsage, ChatEscalation


# -----------------------------------
# Cohere Client
# -----------------------------------
co = cohere.Client(settings.COHERE_API_KEY)

AI_COST_PER_QUERY = 0.002


# -----------------------------------
# Cohere Chat Function (NEW API)
# -----------------------------------
def cohere_chat(prompt: str) -> str:
    try:
        response = co.chat(
            model="command-r",   # Latest chat model
            message=prompt
        )

        return response.text.strip()

    except Exception as e:
        print("🔥 Cohere AI ERROR:", e)
        return "AI error occurred"


# -----------------------------------
# AI Chat View

@login_required
@csrf_exempt
def ai_chat(request):

    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({"reply": "Message empty"}, status=400)

        user = request.user

        # ----------------------------
        # GET USER TIER (SAFE NORMALIZE)
        # ----------------------------
        profile, _ = Profile.objects.get_or_create(user=user)

        tier_raw = profile.user_type or "free"
        tier = tier_raw.lower().replace("_", "").replace(" ", "").strip()

        # ----------------------------
        # BLOCK FREE USERS
        # ----------------------------
        if tier not in ["pro", "proplus"]:
            return JsonResponse(
                {"reply": "🚀 Chatbot is available only for Pro and Pro Plus users."},
                status=403
            )

        # ----------------------------
        # GET USAGE
        # ----------------------------
        usage, _ = ChatUsage.objects.get_or_create(user=user)

        # ----------------------------
        # SET LIMITS
        # ----------------------------
        if tier == "pro":
            quota = 250
        elif tier == "proplus":
            quota = None   # Unlimited access

        # ----------------------------
        # CHECK LIMIT
        # ----------------------------
        if quota is not None and usage.monthly_count >= quota:
            return JsonResponse(
                {"reply": "⚠️ Your limit reached. Need more access? Please upgrade your plan."},
                status=403
            )

        # ----------------------------
        # GENERATE AI RESPONSE
        # ----------------------------
        prompt = f"You are a career assistant AI.\nUser Question: {message}"
        reply_text = cohere_chat(prompt)

        # ----------------------------
        # SAVE CHAT LOG
        # ----------------------------
        ChatLog.objects.create(
            user=user,
            message=message,
            reply=reply_text,
            cost=0.002
        )

        # ----------------------------
        # UPDATE USAGE
        # ----------------------------
        usage.monthly_count += 1
        usage.save()

        return JsonResponse({"reply": reply_text})

    except Exception as e:
        print("🔥 AI VIEW ERROR:", e)
        return JsonResponse(
            {"reply": "AI internal error"},
            status=500
        )









import cohere
from django.conf import settings

co = cohere.ClientV2(api_key=settings.COHERE_API_KEY)

def cohere_chat(prompt):

    try:
        response = co.chat(
            model="command-a-03-2025",   # ✅ CURRENT WORKING MODEL
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.message.content[0].text

    except Exception as e:
        print("🔥 Cohere AI ERROR:", e)
        return "AI error occurred"
 




import cohere
from django.conf import settings

co = cohere.ClientV2(api_key=settings.COHERE_API_KEY)

def cohere_chat(prompt):

    try:
        response = co.chat(
            model="command-a-03-2025",   # ✅ CURRENT WORKING MODEL
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.message.content[0].text

    except Exception as e:
        print("🔥 Cohere AI ERROR:", e)
        return "AI error occurred"
 

