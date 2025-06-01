from django.urls import path

# from rest_framework import routers
from . import views

# router = routers.DefaultRouter()

urlpatterns = [
    path("random-user/", views.RandomUserView.as_view(), name="random-user"),
    path(
        "users/<int:pk>/status/",
        views.UserStatusUpdateView.as_view(),
        name="user-status-update",
    ),
    # path("", include(router.urls)),
]
