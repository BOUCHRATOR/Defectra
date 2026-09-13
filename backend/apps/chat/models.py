from django.db import models


class Conversation(models.Model):

    owner_id = models.IntegerField()

    inspection = models.ForeignKey(
        "inspections.Inspection",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversations"
    )

    title = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_conversations"

    def __str__(self):
        return f"Conversation {self.id}"


class Message(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role} ({self.conversation.id})"