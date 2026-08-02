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

from .decorators import supervisor_required
    
    

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
        student=request.user,
    )

    if topic.status != "Pending":
        messages.error(
            request,
            "Only pending topics can be edited."
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = ThesisTopicForm(
            request.POST,
            request.FILES,
            instance=topic
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Topic updated successfully."
            )

            return redirect("dashboard")

    else:
        form = ThesisTopicForm(instance=topic)

    return render(
        request,
        "edit_topic.html",
        {
            "form": form,
            "topic": topic,
        },
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
def approve_topic(request, topic_id):

    try:
        supervisor = Supervisor.objects.get(
            user=request.user
        )

    except Supervisor.DoesNotExist:
        messages.error(
            request,
            "Supervisor profile not found."
        )
        return redirect("dashboard")
    
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
            "topic_detail",
            topic_id=topic.id
        )
    
    topic.supervisor = supervisor.user

    topic.status = "Approved"

    # Clear any previous rejection reason
    topic.rejection_reason = ""

    topic.save()

    messages.success(
        request,
        "Thesis topic approved successfully."
    )

    return redirect(
        "topic_detail",
        topic_id=topic.id
    )



login_required
def reject_topic(request, topic_id):

    try:
        supervisor = Supervisor.objects.get(
            user=request.user
        )
    except Supervisor.DoesNotExist:
        messages.error(
            request,
            "Supervisor profile not found."
        )
        return redirect("dashboard")
    
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
            "topic_detail",
            topic_id=topic.id
        )
    
    # Only process POST requests
    if request.method == "POST":

        rejection_reason = request.POST.get(
            "rejection_reason",
            ""
        ).strip()

        # Require a rejection reason

        if not rejection_reason:

            messages.error(
                request,
                "Please provide a reason for rejecting this topic."
            )

            return redirect(
                "topic_detail",
                topic_id=topic.id
            )
        
        topic.supervisor = supervisor.user

        topic.status = "Rejected"

        topic.rejection_reason = rejection_reason

        topic.save()

        messages.success(
            request,
            "Thesis topic rejected successfully."
        )

        return redirect(
            "topic_detail",
            topic_id=topic.id
        )




@login_required
@supervisor_required
def supervisor_topic_detail(request, topic_id):
    topic = get_object_or_404(
        ThesisTopic.objects.select_related(
            "student",
            "supervisor",
        ),
        id=topic_id,
    )

    return render(
        request,
        "supervisor/topic_detail.html",
        {
            "topic": topic,
        },
    )



@login_required
@supervisor_required
def assign_supervisor(request, topic_id):

    supervisor = Supervisor.objects.get(
        user=request.user
    )

    topic = get_object_or_404(
        ThesisTopic,
        id=topic_id
    )

    topic.supervisor = supervisor
    topic.save()

    messages.success(
        request,
        "You have been assigned as the supervisor for this topic."
    )

    return redirect(
        "supervisor_topic_detail",
        topic_id=topic.id
    )

    return redirect("supervisor_dashboard")




@login_required
@supervisor_required
def approve_topic(request, topic_id):

    if request.method == "POST":

        supervisor = Supervisor.objects.get(
            user=request.user
        )

        topic = get_object_or_404(
            ThesisTopic,
            id=topic_id
        )

        topic.status = "Approved"

        if not topic.supervisor:
            topic.supervisor = supervisor

            topic.save()

            messages.success(
                request,
                "Thesis topic has been approved successfully."
            )

            return redirect(
                "supervisor_topic_detail",
                topic_id=topic.id
            )

        return redirect("supervisor_dashboard")




@login_required
@supervisor_required
def reject_topic(request, topic_id):

    if request.method == "POST":

        supervisor = Supervisor.objects.get(
            user=request.user
        )

        topic = get_object_or_404(
            ThesisTopic,
            id=topic_id
        )

        topic.status = "Rejected"

        # Assign the Supervisor profile
        if not topic.supervisor:
            topic.supervisor = supervisor

        topic.save()

        messages.success(
            request,
            "Thesis topic has been rejected."
        )

        return redirect(
            "supervisor_topic_detail",
            topic_id=topic.id
        )

    return redirect("supervisor_dashboard")