from django.db import models
from django.contrib.auth.models import AbstractUser
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
