# web/supportapp/admin.py

from django.contrib import admin, messages
from .models import MessageThread, Message, FAQ
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import os
import logging

logger = logging.getLogger(__name__)

# Инициализация Telegram-бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

@admin.action(description="Отправить ответ пользователю")
def reply_to_user(modeladmin, request, queryset):
    for message in queryset:
        if message.sender == "admin" and bot:
            try:
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Допомогло", callback_data=f"helped:{message.thread.id}")],
                    [InlineKeyboardButton(text="❌ Не допомогло", callback_data=f"not_helped:{message.thread.id}")]
                ])
                bot.send_message(
                    chat_id=message.thread.user_id,
                    text=f"✉️ Адміністратор відповів:\n\n{message.text}",
                    reply_markup=kb,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"[Telegram Error] {e}")
                messages.error(request, f"Ошибка при отправке Telegram: {e}")

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
    actions = ["save_to_faq"]

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

            if bot:
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Допомогло", callback_data=f"helped:{obj.id}")],
                    [InlineKeyboardButton(text="❌ Не допомогло", callback_data=f"not_helped:{obj.id}")]
                ])
                try:
                    bot.send_message(
                        chat_id=obj.user_id,
                        text=f"✉️ Адміністратор відповів:\n\n{reply_text}",
                        reply_markup=kb,
                        parse_mode="HTML"
                    )
                    messages.success(request, "Відповідь надіслана користувачу.")
                except Exception as e:
                    logger.error(f"[Telegram Error] {e}")
                    messages.error(request, f"❌ Не вдалося надіслати в Telegram: {e}")
            else:
                messages.warning(request, "Telegram бот не налаштований.")

        elif "add_to_faq" in request.POST:
            try:
                question = Message.objects.filter(thread=obj, sender="user").order_by("created_at").first()
                answer = Message.objects.filter(thread=obj, sender="admin").order_by("-created_at").first()
                if question and answer:
                    FAQ.objects.create(question=question.text, answer=answer.text)
                    messages.success(request, "✅ Додано до FAQ.")
                else:
                    messages.error(request, "Неможливо знайти повідомлення користувача або адміністратора.")
            except Exception as e:
                logger.error("Ошибка при добавлении в FAQ", exc_info=True)
                messages.error(request, f"❌ Помилка при збереженні в FAQ: {e}")

        return super().response_change(request, obj)

    @admin.action(description="📌 Зберегти в FAQ")
    def save_to_faq(self, request, queryset):
        for thread in queryset:
            question = Message.objects.filter(thread=thread, sender="user").order_by("created_at").first()
            answer = Message.objects.filter(thread=thread, sender="admin").order_by("-created_at").first()
            if question and answer:
                FAQ.objects.create(question=question.text, answer=answer.text)
                messages.success(request, f"Додано в FAQ: «{question.text[:50]}...»")
            else:
                messages.warning(request, f"Обговорення {thread.id} не має достатньо повідомлень для FAQ.")

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
