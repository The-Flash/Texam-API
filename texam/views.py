from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from core import forms, models
from .utils import (
    parse_path_string,
    get_repo_path,
    get_path_obj_entry,
    get_content
)

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

class NewTestView(LoginRequiredMixin, View):
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
    
class TestDetailsView(LoginRequiredMixin, View):
    template_name = "texam/test-details.html"
    login_url = reverse_lazy("texam:sign-in")

    def get(self, request, test_id):
        test = models.Test.objects.get(test_id=test_id)
        context = {
            "title": "Test Detail | Texam",
            "test": test
        }
        return render(request, self.template_name, context)


class TestSubmissionView(LoginRequiredMixin, View):
    login_url = reverse_lazy("texam:sign-in")
    template_name = "texam/test-submission.html"

    def get(self, request, test_id, pk, tree_path=None):
        print(test_id, pk)
        context = {
            "title": "Test Submission | Texam",
            "test_id": test_id,
            "pk": pk
        }
        test = models.Test.objects.get(test_id=test_id)
        submission = models.TestSubmission.objects.get(pk=pk)
        repo_path = get_repo_path(test, submission)
        if tree_path is None:
            path_array = None
            context["path"] = path_array
            # context["tree_path"] = 
        else:
            path_array = parse_path_string(tree_path)
            context["path"] = self._path(path_array)
            context["tree_path"] = tree_path
        obj_entry = get_path_obj_entry(repo_path, path_array)
        print("Obj entry", obj_entry)
        if obj_entry is None:
            return HttpResponse("File/Folder has been removed or does not exist")
        context["entry"] = {
            "type": obj_entry[0],
            "content": get_content(repo_path, obj_entry[1])
        }
        print(context["path"])
        return render(request, self.template_name, context)

    def _path(self, path_array):
        result = []
        i = 0
        acc_path = ""
        while i != len(path_array):
            cur_value = path_array[i]
            acc_path +=  cur_value + "/"
            result.append((cur_value, acc_path))
            i += 1
        return result


# @method_decorator(csrf_exempt, name='post')
class TestUploadView(APIView):
    parsers = (MultiPartParser, )

    def get(self, request, *args, **kwargs):
        return Response({
            "details": "Use post instead"
        })

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