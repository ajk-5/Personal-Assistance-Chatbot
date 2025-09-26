from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ChatForm
from .models import Message
from .services import Assistant

# Lazily instantiate to avoid DB access during import/migrations
assistant = None

@require_http_methods(["GET", "POST"])
def chat(request):
    global assistant
    if assistant is None:
        assistant = Assistant()
    form = ChatForm(request.POST or None)
    messages = Message.objects.all()[:50]
    if request.method == "POST" and form.is_valid():
        user_text = form.cleaned_data["text"]
        Message.objects.create(sender="user", text=user_text)
        resp = assistant.handle(user_text)
        Message.objects.create(sender="assistant", text=resp.reply)
        return redirect("chat:chat")
    return render(request, "chat/chat.html", {"form": form, "messages": messages})


@staff_member_required
@require_http_methods(["POST"])  # simple POST retrain endpoint
def retrain(request):
    global assistant
    if assistant is None:
        assistant = Assistant()
    msg = assistant.router.train()
    from django.http import JsonResponse
    return JsonResponse({"status": "ok", "message": msg})


@staff_member_required
@require_http_methods(["GET"])  # report current router status
def status(request):
    global assistant
    if assistant is None:
        assistant = Assistant()
    r = assistant.router
    from django.http import JsonResponse
    data = {
        "enabled": bool(getattr(r, "enabled", False)),
        "trained": bool(getattr(r, "pipeline", None)),
        "labels": list(getattr(r, "labels", []) or []),
        "threshold": float(getattr(r, "threshold", 0.0)),
    }
    return JsonResponse(data)
