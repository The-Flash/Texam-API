from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from core import forms, models

import os
# Create your views here.
def signout(request):
    logout(request)
    return redirect(reverse("texam:sign-in"))


class SignInView(View):
    template_name = "texam/sign-in.html"

    def get(self, request, *args, **kwargs):
        context = {
            "title": "sign In | Texam"
        }
        
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse("texam:home"))
        return redirect(reverse("texam:sign-in"))


class HomeView(LoginRequiredMixin, View):
    template_name = "texam/home.html"
    login_url = reverse_lazy("texam:sign-in")

    def get(self, request, *args, **kwargs):
        tests = models.Test.objects.filter(lecturer=request.user)
        context = {
            "title": "Home  | Texam",
            "tests": tests
        }
        return render(request, self.template_name, context)

class NewTestView(View):
    template_name = "texam/new-test.html"
    login_url = reverse_lazy("texam:sign-in")

    def get(self, request, *args, **kwargs):
        context = {
            "title": "Create A Test | Texam"
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.lecturer = request.user
            test.save()
            return redirect(reverse("texam:test-details", args=(test.id, )))
        context = {
            "title": "Create A Test | Texam",
            "form": form
        }
        return render(request, self.template_name, context)
    
class TestDetailsView(View):
    template_name = "texam/test-details.html"
    login_url = reverse_lazy("texam:sign-in")

    def get(self, request, pk, *args, **kwargs):
        context = {
            "title": "Test Detail | Texam"
        }
        return render(request, self.template_name, context)


class TestUploadView(APIView):
    parsers = (MultiPartParser, )

    def post(self, request, *args, **kwargs):
        try:
            index_no = request.data["index_no"]
            password = request.data["password"]
            test_id = request.data["test_id"]
            student = models.Student.objects.get(index_no=index_no, password=password)
            test = models.Test.objects.get(test_id=test_id)
        except models.Student.DoesNotExist:
            return Response({
                "details": "Incorrect Credentials"
            }, status=status.HTTP_400_BAD_REQUEST)
        except models.Test.DoesNotExist:
            return Response({
                "details": "Test does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)
        test_submission, _ = models.TestSubmission.objects.get_or_create(
            test=test,
            student=student
        )
        if test_submission.is_late_submission():
            if not test.allow_late_submission:
                return Response({
                    "details": "Late submission-Not allowed"
                })
        repo_base_dir = settings.SUBMISSIONS_DIR / test.test_id / student.index_no
        for k, v in request.FILES.items():
            obj_path = repo_base_dir / k
            if not obj_path.exists():
                os.makedirs(os.path.dirname(str(obj_path)), exist_ok=True)
                with open(obj_path, "wb+") as f:
                    for chunk in v.chunks():
                        f.write(chunk)
            elif str(obj_path).endswith("HEAD"):
                with open(obj_path, "wb+") as f:
                    f.write(v.read())
        
        return Response({
            "details": "Successfully Submitted"
        })