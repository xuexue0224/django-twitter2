from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    #actor_content_type = serializers.ChoiceField(choices=['comment', 'tweet'])

    class Meta:
        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )

    def _get_model_class(self, data):
        if data['actor_content_type'] == 4:
            return 'comment'
        if data['content_type'] == 'tweet':
            return 'tweet'
        return None