from django.db import models

class FAQ(models.Model):
    question = models.TextField("Вопрос")
    answer = models.TextField("Ответ")

    def __str__(self):
        return self.question[:100]

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

class MessageThread(models.Model):
    user_id = models.BigIntegerField("Telegram ID пользователя")
    username = models.CharField("Username", max_length=255, blank=True, null=True)
    first_name = models.CharField("Имя", max_length=255, blank=True, null=True)
    last_name = models.CharField("Фамилия", max_length=255, blank=True, null=True)
    photo_url = models.URLField("Аватар", blank=True, null=True)
    last_message_at = models.DateTimeField("Последнее сообщение", blank=True, null=True)
    status = models.CharField("Статус", max_length=255, default="новое")
    created_at = models.DateTimeField("Когда начато", auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        uname = f"@{self.username}" if self.username else ""
        return f"{name} {uname} ({self.user_id})" if name or uname else f"Обращение {self.pk} от {self.user_id}"

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"

class Message(models.Model):
    thread = models.ForeignKey(
        MessageThread,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True, blank=True
    )
    sender = models.CharField(
        max_length=10,
        choices=[("user", "Пользователь"), ("admin", "Администратор")]
    )
    text = models.TextField("Сообщение")
    created_at = models.DateTimeField("Когда отправлено", auto_now_add=True)

    def __str__(self):
        return f"{self.sender} ({self.created_at}): {self.text[:50]}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
