from datetime import datetime

from database.models import (
    Conversation,
    Message
)

from database.repository import Repository


class Memory:

    def __init__(self, db):

        self.repository = Repository(db)

    # =====================================
    # Conversation
    # =====================================

    def create_conversation(
        self,
        owner_id,
        inspection_id=None,
        title=""
    ):

        conversation = Conversation(
            owner_id=owner_id,
            inspection_id=inspection_id,
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return self.repository.create_conversation(
            conversation
        )

    def get_conversation(self, conversation_id):

        return self.repository.get_conversation(
            conversation_id
        )

    def get_last_conversation(self, owner_id):

        return self.repository.get_last_conversation(
            owner_id
        )

    def delete_conversation(self, conversation_id):

        self.repository.delete_conversation(
            conversation_id
        )

    # =====================================
    # Messages
    # =====================================

    def add_message(
        self,
        conversation_id,
        role,
        content
    ):

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.now()
        )

        self.repository.create_message(message)

        conversation = self.repository.get_conversation(
            conversation_id
        )

        if conversation:

            conversation.updated_at = datetime.now()

            self.repository.update_conversation(
                conversation
            )

        return message

    def add_user_message(
        self,
        conversation_id,
        content
    ):

        return self.add_message(
            conversation_id,
            "user",
            content
        )

    def add_assistant_message(
        self,
        conversation_id,
        content
    ):

        return self.add_message(
            conversation_id,
            "assistant",
            content
        )

    def get_messages(self, conversation_id):

        return self.repository.get_messages(
            conversation_id
        )

    def clear_history(self, conversation_id):

        self.repository.delete_messages(
            conversation_id
        )

    # =====================================
    # History for LLM
    # =====================================

    def get_history(self, conversation_id):

        messages = self.repository.get_messages(
            conversation_id
        )

        history = []

        for msg in messages:

            history.append(
                {
                    "role": msg.role,
                    "content": msg.content
                }
            )

        return history