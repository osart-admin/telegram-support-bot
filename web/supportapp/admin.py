from django.contrib import admin
from .models import MessageThread, Message, FAQ
from telegram import Bot
import os

# Отложенная инициализация бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

@admin.action(description="Отправить ответ пользователю")
def reply_to_user(modeladmin, request, queryset):
    for message in queryset:
        if message.sender == "admin" and bot:
            bot.send_message(
                chat_id=message.thread.user_id,
                text=f"✉️ Адміністратор відповів:\n\n{message.text}",
                parse_mode="HTML"
            )

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'text', 'created_at']
    can_delete = False
    ordering = ['created_at']

class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'status', 'created_at', 'resolved']
    search_fields = ['user_id']
    list_filter = ['status', 'resolved']
    inlines = [MessageInline]

    change_form_template = "admin/supportapp/message_thread_change_form.html"

    def response_change(self, request, obj):
        if "send_response" in request.POST and bot:
            reply_text = request.POST.get("admin_reply")
            if reply_text:
                Message.objects.create(
                    thread=obj,
                    sender="admin",
                    text=reply_text
                )
                bot.send_message(
                    chat_id=obj.user_id,
                    text=f"✉️ Адміністратор відповів:\n\n{reply_text}",
                    parse_mode="HTML"
                )
        return super().response_change(request, obj)

class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'thread', 'sender', 'text', 'created_at']
    search_fields = ['text']
    list_filter = ['sender']
    readonly_fields = ['created_at']
    actions = [reply_to_user]

class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer']
    search_fields = ['question', 'answer']

admin.site.register(FAQ, FAQAdmin)
admin.site.register(MessageThread, MessageThreadAdmin)
admin.site.register(Message, MessageAdmin)
