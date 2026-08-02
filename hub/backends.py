from django.contrib.auth.backends import ModelBackend


class ApprovalBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return (
            super().user_can_authenticate(user)
            and user.is_active
            and user.is_approved
        )