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
    status = models.CharField("Статус", max_length=255, default="новое")
    created_at = models.DateTimeField("Когда начато", auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Обращение {self.pk} от {self.user_id}"

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"

class Message(models.Model):
    thread = models.ForeignKey(
        MessageThread,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True, blank=True  # добавлено временно
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
