from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from api.utils import UsernameCharField
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        exclude = ('title',)
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(
                author=author, title=title).exists():
            raise serializers.ValidationError(
                "Вы уже писали отзыв к этому произведению."
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        exclude = ('review',)
        model = Comment


class CategoryReadSerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений"""

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений"""

    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений"""

    category = CategoryReadSerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей"""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class MeSerializer(UserSerializer):
    """Сериализатор изменения данных своей учетной записи"""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignupSerializer(serializers.Serializer):
    """Сериализатор создания пользователя"""

    email = serializers.EmailField(
        required=True,
        max_length=254
    )
    username = UsernameCharField(required=True)

    def validate(self, data):
        username = User.objects.filter(username=data.get('username')).exists()
        email = User.objects.filter(email=data.get('email')).exists()
        if username and not email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if email and not username:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT токена."""

    username = UsernameCharField(required=True)
    confirmation_code = serializers.CharField(required=True)
