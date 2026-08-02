from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    LEVEL_CHOICES = [
        ("100", "100 Level"),
        ("200", "200 Level"),
        ("300", "300 Level"),
        ("400", "400 Level"),
        ("500", "500 Level"),
        ("PGD", "PGD"),
        ("MSc", "MSc"),
        ("PhD", "PhD"),
    ]

    matric_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    faculty = models.ForeignKey(
        "Faculty",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
         
        )
    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        blank=True,
        default=""
    )

    phone_number = models.CharField(max_length=20, blank=True, default="")
    
    
    department = models.ForeignKey(
        "Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    is_student = models.BooleanField(default=True)
    is_supervisor = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    def __str__(self):
        return  f"{self.username} ({self.matric_number})"


class ThesisTopic(models.Model):
    STATUS_CHOICES =[
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),

    ]
    title = models.CharField(max_length=200)
    description = models.TextField()

    proposal = models.FileField(
        upload_to="proposals/",
        blank=True,
        null=True,
    )

    research_area = models.ForeignKey(
        "ResearchArea",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="topics",
    )

    supervisor = models.ForeignKey(
        "Supervisor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name ="topics",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason provided when the thesis topic is rejected."
    )


    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    

class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Department(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="departments"
    )

    name = models.CharField(max_length=150)

    class Meta:
        ordering = ["name"]
        unique_together = ("faculty", "name")

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"


class ResearchArea(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Supervisor(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )

    research_areas = models.ManyToManyField(
        ResearchArea,
        blank=True
    )

    max_student = models.PositiveIntegerField(default=5)

    office = models.CharField(
        max_length=100,
        blank=True
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.user.get_full_name()