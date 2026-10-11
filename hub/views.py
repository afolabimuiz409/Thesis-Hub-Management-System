from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import StudentSignUpForm, ThesisTopicForm
from .decorators import approved_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ThesisTopic, Supervisor
from .utils import create_notification
from .models import ThesisReview

from .decorators import supervisor_required
from .forms import SupervisorReviewForm
    
    

# Create your views here.

def home_page(request):
    return render(request, 'index.html')


def signup_page(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
           form.save()
           messages.success(request, "Registration successful. Your account is awaiting admin approval.")
           return redirect("pending")
    else:
        form = StudentSignUpForm()
    return render(request, 'signup.html', {'form': form})

def pending_page(request):
    return render(request, 'pending.html')


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_supervisor:
            return redirect("supervisor_dashboard")

        return redirect("dashboard")
    
    if request.method == "POST":
        
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            
            if not user.is_approved:
                return redirect("pending")

            login(request, user)
            
            if user.is_supervisor:
                return redirect("supervisor_dashboard")

            elif user.is_student:
                return redirect("dashboard")

            else:
                messages.error(
                    request,
                    "Invalid username or password"
                )

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('home_page')

@login_required
@approved_required
def dashboard(request):

    topics = ThesisTopic.objects.filter(
        student=request.user
    ).order_by("-submitted_at")

    search = request.GET.get("search", "").strip()

    if search:
        topics = topics.filter(
            title__icontains=search
        )
        print(topics.query)

    status = request.GET.get("status", "").strip()
    print("STATUS RECEIVED", repr(status))

    if status:
        topics = topics.filter(status=status)


    total_topics = ThesisTopic.objects.filter(
        student=request.user
    ).count()


    pending_topics = ThesisTopic.objects.filter(
        student=request.user,
        status="Pending"
    ).count()


    approved_topics = ThesisTopic.objects.filter(
        student=request.user,
        status="Approved"
    ).count()


    rejected_topics = ThesisTopic.objects.filter(
        student=request.user,
        status="Rejected"
    ).count()

    paginator = Paginator(topics, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {

        "student": request.user,

        "topics": page_obj,

        "page_obj": page_obj,

        "search": search,

        "status": status,

        "total_topics": total_topics,

        "pending_topics": pending_topics,

        "approved_topics": approved_topics,

        "rejected_topics": rejected_topics,
    }

    return render(
        request,
        "dashboard.html",
        context,
    )


@login_required    
@approved_required
def submit_topic(request):
    if request.method == "POST":
        form = ThesisTopicForm(request.POST, request.FILES)

        if form.is_valid():
            topic = form.save(commit=False)
            topic.student = request.user
            topic.save()

            # Notify supervisor

            supervisors = Supervisor.objects.filter(
                user__is_active=True,
                user__is_approved=True,
                user__is_supervisor=True,
            )

            for supervisor in supervisors:
                create_notification(
                    recipient=supervisor.user,
                    title="New Thesis Topic Submitted",
                    message=(
                        f"{request.user.get_full_name() or request.user.username} "
                        f"has submitted a new thesis topic: "
                        f"\"{topic.title}\"."
                    ),
                    topic=topic
                )

            messages.success(
                request,
                "Your thesis topic has been submitted successfully."
            )

            return redirect("dashboard")

    else:
        form = ThesisTopicForm()

    return render(
        request,
        "submit_topic.html",
        {
            "form": form,
        },
    )




@login_required    
@approved_required
def topic_detail(request, pk):
    topic = get_object_or_404(
        ThesisTopic,
        pk=pk,
        student=request.user
    )

    return render(
        request,
        "topic_detail.html",
        {
            "topic": topic
        }
    )


@login_required
@approved_required
def edit_topic(request, pk):

    topic = get_object_or_404(
        ThesisTopic,
        pk=pk,
        student=request.user
    )

    # Approved topics cannot be edited
    if topic.status == "Approved":
        messages.warning(
            request,
            "Approved thesis topics cannot be edited."
        )
        return redirect("topic_detail", pk=topic.id)

    if request.method == "POST":

        form = ThesisTopicForm(
            request.POST,
            request.FILES,
            instance=topic
        )

        if form.is_valid():

            topic = form.save(commit=False)

            # Resubmit the topic for supervisor review
            topic.status = "Pending"

            # Clear the previous rejection feedback
            topic.supervisor_feedback = ""

            topic.save()

            # Notify supervisor about the resubmission
            supervisors = Supervisor.objects.filter(
                user__is_active=True,
                user__is_approved=True,
                user__is_supervisor=True,
            )

            for supervisor in supervisors:

                create_notification(
                    recipient=supervisor.user,
                    title="Thesis Topic Resubmitted",
                    message=(
                        f'{request.user.get_full_name() or request.user.username} '
                        f'has resubmitted the thesis topic "{topic.title}" '
                        f'for review.'
                    ),
                    topic=topic
                )

            messages.success(
                request,
                "Your thesis topic has been updated and resubmitted for review."
            )

            return redirect(
                "topic_detail",
                pk=topic.id
            )

    else:
        form = ThesisTopicForm(instance=topic)

    return render(
        request,
        "edit_topic.html",
        {
            "form": form,
            "topic": topic,
        }
    )

        
    

   
    



@login_required    
@approved_required
def delete_topic(request, pk):

    topic = get_object_or_404(
        ThesisTopic,
        pk=pk,
        student=request.user,
    )

    if topic.status != "Pending":
        messages.error(
            request,
            "Approved or rejected topics cannot be deleted."
        )
        return redirect("dashboard")
    
    if request.method == "POST":
        topic.delete()

        messages.success(
            request,
            "Topic deleted successfully."
        )

        return redirect("dashboard")
    
    return render(
        request,
        "delete_topic.html",
        {
            "topic": topic
        },
    )




@login_required
@supervisor_required
def supervisor_dashboard(request):

    # Get supervisor profile
    try:
        supervisor = Supervisor.objects.get(
            user=request.user
        )
    except Supervisor.DoesNotExist:
        messages.error(
            request,
            "Supervisor profile not found. Please contact the administrator."
        )
        return redirect("dashboard")


    # Get all thesis topics
    topics = ThesisTopic.objects.select_related(
        "student",
        "supervisor",
    ).order_by("-submitted_at")


    # ==========================
    # SEARCH
    # ==========================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        topics = topics.filter(
            Q(title__icontains=search)
            | Q(student__first_name__icontains=search)
            | Q(student__last_name__icontains=search)
            | Q(student__matric_number__icontains=search)
            | Q(student__username__icontains=search)
        )


    # ==========================
    # STATUS FILTER
    # ==========================

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:
        topics = topics.filter(
            status__iexact=status
        )


    # ==========================
    # STATISTICS
    # ==========================

    total_topics = ThesisTopic.objects.count()

    pending_topics = ThesisTopic.objects.filter(
        status="Pending"
    ).count()

    approved_topics = ThesisTopic.objects.filter(
        status="Approved"
    ).count()

    rejected_topics = ThesisTopic.objects.filter(
        status="Rejected"
    ).count()


    # ==========================
    # PAGINATION
    # ==========================

    paginator = Paginator(
        topics,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    # ==========================
    # CONTEXT
    # ==========================

    context = {
        "supervisor": supervisor,

        "topics": page_obj,

        "page_obj": page_obj,

        "total_topics": total_topics,

        "pending_topics": pending_topics,

        "approved_topics": approved_topics,

        "rejected_topics": rejected_topics,

        "search": search,

        "status": status,
    }


    return render(
        request,
        "supervisor/dashboard.html",
        context,
    )



@login_required
@supervisor_required
def approve_topic(request, topic_id):
    supervisor = get_object_or_404(
        Supervisor,
        user=request.user
    )

    topic = get_object_or_404(
        ThesisTopic,
        id=topic_id
    )

    if topic.status != "Pending":
        messages.warning(
            request,
            "This thesis topic has already been reviewed."
        )

        return redirect(
            "supervisor_topic_detail",
            topic_id=topic.id
        )

    # Assign the current supervisor
    topic.supervisor = supervisor

    # Approve topic
    topic.status = "Approved"

    # Remove any previous rejection information
    topic.rejection_reason = ""
    topic.supervisor_feedback = ""

    topic.save()

    # Save review history
    ThesisReview.objects.create(
        topic=topic,
        supervisor=supervisor,
        decision="Approved",
        feedback=""
    )

    create_notification(
        recipient=topic.student,
        title="Thesis Topic Approved",
        message=(
            f"Your thesis topic \"{topic.title}\" has been approved "
            f"by {supervisor.user.get_full_name() or supervisor.user.username}."
        ),
        topic=topic
    )

    messages.success(
        request,
        "Thesis topic approved successfully."
    )

    return redirect(
        "supervisor_topic_detail",
        topic_id=topic.id
    )


@login_required
@supervisor_required
def reject_topic(request, topic_id):
    supervisor = get_object_or_404(
        Supervisor,
        user=request.user
    )

    topic = get_object_or_404(
        ThesisTopic,
        id=topic_id
    )

    if topic.status != "Pending":
        messages.warning(
            request,
            "This thesis topic has already been reviewed."
        )

        return redirect(
            "supervisor_topic_detail",
            topic_id=topic.id
        )

    if request.method == "POST":

        form = SupervisorReviewForm(request.POST)

        if form.is_valid():

            feedback = form.cleaned_data["supervisor_feedback"]

            # Assign supervisor
            topic.supervisor = supervisor

            # Reject topic
            topic.status = "Rejected"

            # IMPORTANT:
            # Save feedback in supervisor_feedback
            topic.supervisor_feedback = feedback

            # Also keep rejection_reason for compatibility
            topic.rejection_reason = feedback

            topic.save()

            # Save review history
            ThesisReview.objects.create(
                topic=topic,
                supervisor=supervisor,
                decision="Rejected",
                feedback=feedback
            )

            create_notification(
                recipient= topic.student,
                title="Thesis Topic Rejected",
                message=(
                    f'Your thesis topic "{topic.title}" has been rejected '
                    f'by {supervisor.user.get_full_name() or supervisor.user.username}. '
                    f'Feedback: {feedback}'
                ),
                topic=topic
            )

            messages.success(
                request,
                "Thesis topic rejected successfully."
            )

            return redirect(
                "supervisor_topic_detail",
                topic_id=topic.id
            )

    else:
        form = SupervisorReviewForm()

    return render(
        request,
        "supervisor/reject_topic.html",
        {
            "topic": topic,
            "supervisor": supervisor,
            "form": form,
        }
    )


@login_required
@supervisor_required
def supervisor_topic_detail(request, topic_id):

    topic = get_object_or_404(
        ThesisTopic.objects.select_related(
            "student",
            "supervisor",
        ),
        id=topic_id
    )
    
    # Get all review history for this topic
    review_history = topic.reviews.select_related(
        "supervisor",
        "supervisor__user",
    ).order_by("-reviewed_at")

    return render(
        request,
        "supervisor/topic_detail.html",
        {
            "topic": topic,
            "review_history": review_history,
        }
    )


@login_required
@supervisor_required
def assign_supervisor(request, topic_id):

    supervisor = get_object_or_404(
        Supervisor,
        user=request.user
    )

    topic = get_object_or_404(
        ThesisTopic,
        id=topic_id
    )

    topic.supervisor = supervisor
    topic.save()

    # Notify student
    create_notification(
        recipient=topic.student,
        title="Supervisor Assigned",
        message=(
            f"{supervisor.user.get_full_name() or supervisor.user.username} "
            f"has been assigned as the supervisor for your thesis topic "
            f"\"{topic.title}\"."
        ),
        topic=topic
    )

    messages.success(
        request,
        "You have been assigned as the supervisor for this topic."
    )

    return redirect(
        "supervisor_topic_detail",
        topic_id=topic.id
    )


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(
        request,
        "notifications/list.html",
        {
            "notifications": notifications,
        }
    )

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        request.user.notifications,
        id=notification_id
    )

    notification.is_read = True
    notification.save()

    if notification.topic:
        if request.user.is_supervisor:
            return redirect(
                "supervisor_topic_detail",
                topic_id=notification.topic.id
            )
        return redirect(
            "topic_detail",
            pk=notification.topic.id
        )
    return redirect("notification_list")



@login_required
def mark_all_notifications_read(request):

    request.user.notifications.filter(
        is_read=False
    ).update(
        is_read=True
    )

    messages.success(
        request,
        "All notifications marked as read."
    )
    return redirect("notification_list")


