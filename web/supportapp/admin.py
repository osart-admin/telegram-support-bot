from django.contrib import admin, messages
from django.utils.html import format_html
from .models import MessageThread, Message, FAQ
import logging

logger = logging.getLogger(__name__)

@admin.action(description="Отправить ответ пользователю")
def reply_to_user(modeladmin, request, queryset):
    for message in queryset:
        if message.sender == "admin":
            messages.info(request, f"Ответ для {message.thread.user_id} уже был создан.")

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'text', 'created_at']
    can_delete = False
    ordering = ['created_at']

class MessageThreadAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_id', 'full_name', 'username_display', 'avatar_preview',
        'status', 'created_at', 'last_message_at', 'resolved'
    ]
    search_fields = ['user_id', 'username', 'first_name', 'last_name']
    list_filter = ['status', 'resolved']
    inlines = [MessageInline]
    change_form_template = "admin/supportapp/message_thread_change_form.html"

    def full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
    full_name.short_description = "Имя и Фамилия"

    def avatar_preview(self, obj):
        if obj.photo_url:
            return format_html('<img src="{}" width="32" height="32" style="border-radius:50%"/>', obj.photo_url)
        return "-"
    avatar_preview.short_description = "Аватар"

    def username_display(self, obj):
        return f"@{obj.username}" if obj.username else ""
    username_display.short_description = "Username"

    def last_message_at(self, obj):
        return obj.last_message_at
    last_message_at.admin_order_field = 'last_message_at'
    last_message_at.short_description = "Последнее сообщение"

    def response_change(self, request, obj):
        if "send_response" in request.POST:
            reply_text = request.POST.get("admin_reply", "").strip()
            if not reply_text:
                messages.error(request, "Поле відповіді порожнє.")
                return super().response_change(request, obj)

            Message.objects.create(
                thread=obj,
                sender="admin",
                text=reply_text
            )

            messages.success(request, "Відповідь збережено.")

        if "add_to_faq" in request.POST:
            question = Message.objects.filter(thread=obj, sender="user").order_by("created_at").first()
            answer = Message.objects.filter(thread=obj, sender="admin").order_by("-created_at").first()
            if question and answer:
                FAQ.objects.create(question=question.text, answer=answer.text)
                messages.success(request, f"Додано в FAQ: «{question.text[:50]}...»")
            else:
                messages.warning(request, f"Обговорення {obj.id} не має достатньо повідомлень для FAQ.")

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
