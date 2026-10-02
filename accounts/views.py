from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from .models import User, AuthorityRegistrationRequest
from .forms import UserRegistrationForm, AuthorityRegistrationForm

def home(request):
    if request.user.is_authenticated:
        if request.user.is_authority:
            return redirect('dashboard:authority_dashboard')
        return redirect('dashboard:citizen_dashboard')

    return render(request, 'accounts/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_record = User.objects.filter(username=username).first()
        if user_record and not user_record.is_active:
            approved = getattr(user_record, "authority_request", None)
            if approved and approved.status == "approved":
                user_record.is_active = True
                user_record.is_authority = True
                user_record.is_citizen = False
                user_record.save()

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect('/admin/')
            elif user.is_authority:
                return redirect('dashboard:authority_dashboard')
            else:
                return redirect('dashboard:citizen_dashboard')
        else:
            if user_record and not user_record.is_active:
                messages.error(request, 'Your authority account is pending approval.')
            else:
                messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:home')


@login_required
def citizen_dashboard(request):
    return render(request, 'dashboard/citizen_dashboard.html')


@login_required
def authority_dashboard(request):
    if not request.user.is_authority:
        messages.error(request, "Unauthorized access")
        return redirect('accounts:home')

    return redirect('dashboard:authority_dashboard')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard:citizen_dashboard')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def register_authority(request):
    if request.method == 'POST':
        form = AuthorityRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            AuthorityRegistrationRequest.objects.create(user=user)
            messages.success(request, 'Your authority registration request was submitted for approval.')
            return redirect('accounts:login')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthorityRegistrationForm()

    return render(request, 'accounts/register_authority.html', {'form': form})


def _send_authority_email(user, subject, template_base, context):
    if not user.email:
        return
    try:
        text_body = render_to_string(f"accounts/emails/{template_base}.txt", context)
        html_body = render_to_string(f"accounts/emails/{template_base}.html", context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@nagar-nirvana.local",
            to=[user.email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
    except Exception:
        pass


@login_required
def authority_requests(request):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access")
        return redirect('accounts:home')

    pending_requests = AuthorityRegistrationRequest.objects.filter(status="pending").select_related("user")
    approved_requests = AuthorityRegistrationRequest.objects.filter(status="approved").select_related("user")[:10]
    rejected_requests = AuthorityRegistrationRequest.objects.filter(status="rejected").select_related("user")[:10]

    return render(request, 'accounts/authority_requests.html', {
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
    })


@login_required
def approve_authority_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access")
        return redirect('accounts:home')
    if request.method != "POST":
        return redirect('accounts:authority_requests')

    req = get_object_or_404(AuthorityRegistrationRequest, id=request_id)
    req.status = "approved"
    req.reviewed_at = timezone.now()
    req.reviewed_by = request.user
    req.save()

    req.user.is_active = True
    req.user.is_authority = True
    req.user.is_citizen = False
    req.user.save()

    _send_authority_email(
        req.user,
        "Authority access approved",
        "authority_approved",
        {"user": req.user},
    )

    messages.success(request, f"Approved authority request for {req.user.username}.")
    return redirect('accounts:authority_requests')


@login_required
def reject_authority_request(request, request_id):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access")
        return redirect('accounts:home')
    if request.method != "POST":
        return redirect('accounts:authority_requests')

    req = get_object_or_404(AuthorityRegistrationRequest, id=request_id)
    req.status = "rejected"
    req.reviewed_at = timezone.now()
    req.reviewed_by = request.user
    req.save()

    req.user.is_active = False
    req.user.is_authority = False
    req.user.save()

    _send_authority_email(
        req.user,
        "Authority access rejected",
        "authority_rejected",
        {"user": req.user},
    )

    messages.info(request, f"Rejected authority request for {req.user.username}.")
    return redirect('accounts:authority_requests')
