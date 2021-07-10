from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from core import forms

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
        context = {
            "title": "Home  | Texam"
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
