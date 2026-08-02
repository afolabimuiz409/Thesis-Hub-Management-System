from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import(
 CustomUser,
 ThesisTopic,
 Faculty,
 Department,
 ResearchArea, 
 Supervisor,
)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "faculty")
    search_fields = ("name",)
    list_filter = ("faculty",)


@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ("user", "max_student")
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "matric_number",
        "first_name",
        "last_name",
        "faculty",
        "department",
        "level",
        "is_student",
        "is_supervisor",
        "is_approved",
        "is_active",
    )

    list_filter = (
        "is_student",
        "is_supervisor",
        "is_approved",
        "is_active",
        "faculty",
    )

    search_fields = (
        "username",
        "matric_number",
        "first_name",
        "last_name",
        "email",
    )

    actions = ["approve_students"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Student Information",
            {
                "fields": (
                    "matric_number",
                    "faculty",
                    "department",
                    "level",
                    "phone_number",
                    "is_student",
                    "is_supervisor",
                    "is_approved",
                ),
            },
        ),
    )

    def approve_students(self, request, queryset):
        queryset.update(
            is_active=True,
            is_approved=True,
        )

    approve_students.short_description = "Approve selected students"

    @admin.register(ThesisTopic)
    class ThesisTopicAdmin(admin.ModelAdmin):
        list_display = (
            "title", 
            "student", 
            "research_area", 
            "supervisor", 
            "status", 
            "submitted_at",
        )

        list_filter = (
            "status",
            "research_area",
            "supervisor",
        )
        search_fileds = (
            "title",
            "student__username",
            "student__matric_number",
            "student__first_name",
            "student__last_name",
        )

        list_editable = (
            "status",
            "supervisor",
        )
            
            
            
            
            
        
