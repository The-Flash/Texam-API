from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from import_export import resources

# Create your models here.
class User(AbstractUser):
    pass

class Student(models.Model):
    index_no = models.CharField("Index Number", max_length=10, unique=True)
    password = models.CharField("Password", max_length=50)

    def __str__(self):
        return self.index_no
    

class StudentResource(resources.ModelResource):

    class Meta:
        fields = (
            'index_no', 
            'password'
        )
        import_id_fields = (
            "index_no", 
            "password"
        )
        model = Student

class Test(models.Model):
    test_id = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    lecturer = models.ForeignKey("core.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    submission_time = models.DateTimeField()
    allow_late_submission = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TestSubmission(models.Model):
    test = models.ForeignKey("Test", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    submission_time = models.DateTimeField(default=timezone.now)
    tree = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.test) + "/" + str(self.student)