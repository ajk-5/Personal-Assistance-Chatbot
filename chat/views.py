from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import ChatForm
from .models import Message
from .services import Assistant

assistant = Assistant()

@require_http_methods(["GET", "POST"])
def chat(request):
    form = ChatForm(request.POST or None)
    messages = Message.objects.all()[:50]
    if request.method == "POST" and form.is_valid():
        user_text = form.cleaned_data["text"]
        Message.objects.create(sender="user", text=user_text)
        resp = assistant.handle(user_text)
        Message.objects.create(sender="assistant", text=resp.reply)
        return redirect("chat:chat")
    return render(request, "chat/chat.html", {"form": form, "messages": messages})
