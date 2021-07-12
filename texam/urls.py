from django.urls import path

from . import views

app_name = "texam"

urlpatterns = [
    path("sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("sign-out/", views.signout, name="sign-out"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("test/upload/", views.TestUploadView.as_view(), name="test-upload"),
    path("new-test/", views.NewTestView.as_view(), name="new-test"),
    path("test/<str:test_id>/", views.TestDetailsView.as_view(), name="test-details"),
    path("test/<str:test_id>/<int:pk>/tree/", views.TestSubmissionView.as_view(), name="test-submission"),
    path("test/<str:test_id>/<int:pk>/tree/<path:tree_path>/", views.TestSubmissionView.as_view(), name="test-submission"),
]