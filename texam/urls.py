from django.urls import path

from . import views

app_name = "texam"

urlpatterns = [
    path("sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("sign-out/", views.signout, name="sign-out"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("new-test/", views.NewTestView.as_view(), name="new-test"),
    path("test/<int:pk>/", views.TestDetailsView.as_view(), name="test-details")
]