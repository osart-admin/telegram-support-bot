# web/supportapp/admin.py

from django.contrib import admin, messages
from .models import MessageThread, Message, FAQ
import os
import logging

logger = logging.getLogger(__name__)

@admin.action(description="Отправить ответ пользователю")
def reply_to_user(modeladmin, request, queryset):
    for message in queryset:
        if message.sender == "admin":
            try:
                messages.success(request, f"Сообщение {message.id} уже создано и будет доставлено сигналом.")
            except Exception as e:
                logger.error(f"[Telegram Error] {e}")
                messages.error(request, f"Ошибка при обработке: {e}")

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
        if "send_response" in request.POST:
            try:
                reply_text = request.POST.get("admin_reply", "").strip()
                if not reply_text:
                    messages.error(request, "Поле відповіді порожнє.")
                    return super().response_change(request, obj)

                Message.objects.create(
                    thread=obj,
                    sender="admin",
                    text=reply_text
                )
                messages.success(request, "Відповідь збережено та буде надіслана користувачу.")
            except Exception as e:
                logger.error("Ошибка при создании сообщения", exc_info=True)
                messages.error(request, f"Внутрення помилка: {e}")
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
