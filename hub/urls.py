from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home_page, name="home_page"),
    path('signup/', views.signup_page, name="signup"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
        ),
        name='password_reset_confirm',
    ),

    path(
        'password-reset-complete',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    
    path('pending/', views.pending_page, name="pending"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('topic/submit/', views.submit_topic, name="submit_topic"),
    path('topic/<int:pk>/', views.topic_detail, name="topic_detail"),
    path('topic/<int:pk>/edit/', views.edit_topic, name="edit_topic"),
    path('topic/<int:pk>/delete/', views.delete_topic, name="delete_topic"),
    path(
        "supervisor/dashboard/",
        views.supervisor_dashboard,
        name="supervisor_dashboard",
    ),
    path(
        "supervisor/topic/<int:topic_id>/approve/",
        views.approve_topic,
        name="approve_topic",
    ),
    
    path(
        "supervisor/topic/<int:topic_id>/reject/",
        views.reject_topic,
        name="reject_topic",
    ),

    path(
        "supervisor/topic/<int:topic_id>/",
        views.supervisor_topic_detail,
        name="supervisor_topic_detail",
    ),

    path(
        "supervisor/topic/<int:topic_id>/assign/",
        views.assign_supervisor,
        name="assign_supervisor"
    ),

    path(
        "notifications/",
        views.notification_list,
        name="notification_list"
    ),

    path(
        "notifications/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read"
    ),

    path(
        "notifications/mark-all-read/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read"
    ),

    # path(
    #     "supervisor/topic/<int:topic_id>/approve/",
    #     views.approve_topic,
    #     name="approve_topic"
    # ),

    # path(
    #     "supervisor/topic/<int:topic_id>/reject/",
    #     views.reject_topic,
    #     name="reject_topic"
    # ),

    # path(
    #     "supervisor/topic/<int:topic_id>/reject/",
    #     views.reject_topic,
    #     name="reject_topic"
    # ),


]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )