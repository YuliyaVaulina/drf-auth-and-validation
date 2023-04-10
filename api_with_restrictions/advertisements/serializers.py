from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # TODO: добавьте требуемую валидацию
        # 1. Проверьте, что текущий пользователь является создателем
        #    объявления, если статус объявления меняется на CLOSED.
        # 2. Проверьте, что текущий пользователь является создателем
        #    объявления, если он пытается изменить его.
        count_adv = Advertisement.objects.filter(creator_id=self.context["request"].user.id, status='OPEN')
        param = self.context["request"].data.get('status')
        if param == 'CLOSED':
            return data
        if len(count_adv) > 10:
            raise serializers.ValidationError('Нельзя создать больше 10 открытых объявлений')
        return data
