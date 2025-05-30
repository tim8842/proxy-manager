import random

from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class RandomUserView(generics.RetrieveAPIView):
    """
    Получение случайного пользователя со статусом 200.
    """

    serializer_class = UserSerializer

    def get_object(self):
        """
        Возвращает случайного пользователя со статусом 200.
        """
        users = User.objects.filter(status=200)
        if users.exists():
            return random.choice(users)
        else:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                status=404, data={"message": "Нет пользователей со статусом 200"}
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserStatusUpdateView(generics.UpdateAPIView):
    """
    Эндпоинт для обновления поля 'status' пользователя по ID (доступен всем).
    """

    serializer_class = UserSerializer

    def get_object(self):
        """
        Получает объект пользователя по ID или возвращает 404.
        """
        try:
            user_id = self.kwargs["pk"]
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFound(detail="User not found.")

    def update(self, request, *args, **kwargs):
        """
        Обновляет поле 'status' пользователя.
        """
        user = self.get_object()
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )  # partial=True разрешает частичное обновление
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
