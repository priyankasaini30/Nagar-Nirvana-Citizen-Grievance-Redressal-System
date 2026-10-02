from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Complaint, Category, Feedback
from django.contrib.auth import get_user_model
from .forms import ComplaintForm, FeedbackForm

@login_required
def complaint_list(request):
    if request.user.is_citizen:
        complaints = Complaint.objects.filter(citizen=request.user)
    else:
        complaints = Complaint.objects.all()
    return render(request, 'complaints/complaint_list.html', {
        'complaints': complaints,
        'page_title': 'My Complaints',
        'page_heading': 'My Complaints',
        'show_submit': True,
    })


@login_required
def submitted_complaints(request):
    complaints = Complaint.objects.filter(citizen=request.user)
    return render(request, 'complaints/complaint_list.html', {
        'complaints': complaints,
        'page_title': 'Submitted Complaints',
        'page_heading': 'Submitted Complaints',
        'show_submit': True,
    })

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.citizen = request.user
            complaint.save()
            messages.success(
                request,
                f'Complaint submitted successfully. Your tracking ID is {complaint.tracking_id}.'
            )
            return redirect('complaints:complaint_detail', pk=complaint.pk)
        messages.error(request, 'Please fix the highlighted errors and try again.')
    else:
        form = ComplaintForm()
    categories = Category.objects.all()
    return render(request, 'complaints/submit_complaint.html', {'form': form, 'categories': categories})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.user.is_citizen and complaint.citizen != request.user:
        return redirect('complaints:complaint_list')
    updates = complaint.updates.all()
    feedback_form = None
    if complaint.status == 'Resolved' and not hasattr(complaint, 'feedback'):
        feedback_form = FeedbackForm()
    allowed_statuses = []
    feedback_pending = False
    if request.user.is_authority:
        allowed_statuses = _get_allowed_status_transitions(complaint)
        if hasattr(complaint, 'feedback'):
            feedback_pending = complaint.feedback.resolution_status == 'pending'
    User = get_user_model()
    authority_users = User.objects.filter(is_authority=True, is_active=True).order_by('username')
    all_statuses = [s[0] for s in Complaint.STATUS_CHOICES]
    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'updates': updates,
        'feedback_form': feedback_form,
        'allowed_statuses': allowed_statuses,
        'all_statuses': all_statuses,
        'authority_users': authority_users,
        'feedback_pending': feedback_pending,
    })


@login_required
def track_status(request):
    if request.user.is_authority:
        return redirect('dashboard:authority_dashboard')
    complaint = None
    not_found = False
    if request.method == 'POST':
        tracking_id = (request.POST.get('tracking_id') or "").strip().upper()
        if tracking_id:
            qs = Complaint.objects.filter(tracking_id=tracking_id)
            if request.user.is_citizen:
                qs = qs.filter(citizen=request.user)
            complaint = qs.first()
            if complaint is None:
                not_found = True
    return render(request, 'complaints/track_status.html', {
        'complaint': complaint,
        'not_found': not_found,
    })


@login_required
def feedback_center(request):
    complaints = Complaint.objects.filter(citizen=request.user, status='Resolved').exclude(feedback__isnull=False)
    return render(request, 'complaints/feedback_center.html', {'complaints': complaints})


@login_required
def feedback_list(request):
    if not request.user.is_authority:
        return redirect('dashboard:citizen_dashboard')
    feedbacks = Feedback.objects.select_related('complaint', 'complaint__citizen').order_by('-created_at')
    return render(request, 'complaints/feedback_list.html', {'feedbacks': feedbacks})

@login_required
def update_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not request.user.is_authority:
        return redirect('complaints:complaint_detail', pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        comment = request.POST.get('comment')
        assigned_to_id = request.POST.get('assigned_to')
        if status and comment:
            allowed = _get_allowed_status_transitions(complaint)
            if status not in allowed:
                messages.error(request, 'Invalid status transition.')
                return redirect('complaints:complaint_detail', pk=pk)

            # If reopening after pending feedback, require reassignment
            if status == 'In Progress' and hasattr(complaint, 'feedback'):
                if complaint.feedback.resolution_status == 'pending':
                    if not assigned_to_id:
                        messages.error(request, 'Please reassign the complaint before reopening.')
                        return redirect('complaints:complaint_detail', pk=pk)
                    complaint.assigned_to_id = assigned_to_id

            if assigned_to_id:
                complaint.assigned_to_id = assigned_to_id

            from .models import ComplaintUpdate
            ComplaintUpdate.objects.create(
                complaint=complaint,
                updated_by=request.user,
                status=status,
                comment=comment
            )
            complaint.status = status
            if status == 'Resolved':
                from django.utils import timezone
                complaint.resolved_at = timezone.now()
            if status == 'In Progress' and complaint.resolved_at:
                complaint.resolved_at = None
            complaint.save()
            messages.success(request, 'Complaint updated successfully!')
    return redirect('complaints:complaint_detail', pk=pk)

@login_required
def submit_feedback(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.user != complaint.citizen or complaint.status != 'Resolved' or hasattr(complaint, 'feedback'):
        return redirect('complaints:complaint_detail', pk=pk)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.complaint = complaint
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
    return redirect('complaints:complaint_detail', pk=pk)


def _get_allowed_status_transitions(complaint):
    current = complaint.status
    if current == 'Pending':
        current = 'Submitted'
    allowed = []
    if current == 'Submitted':
        allowed = ['In Progress']
    elif current == 'In Progress':
        allowed = ['Resolved']
    elif current == 'Resolved':
        if hasattr(complaint, 'feedback'):
            allowed = ['Closed']
            if complaint.feedback.resolution_status == 'pending':
                allowed.append('In Progress')
    return allowed

@login_required
def complaint_map(request):
    complaints = Complaint.objects.all()
    complaints_data = []
    for complaint in complaints:
        if complaint.latitude and complaint.longitude:
            complaints_data.append({
                'id': complaint.id,
                'title': complaint.title,
                'category': complaint.category.name,
                'status': complaint.get_status_display(),
                'latitude': complaint.latitude,
                'longitude': complaint.longitude,
            })
    import json
    return render(request, 'complaints/complaint_map.html', {'complaints': json.dumps(complaints_data)})
@login_required
def citizen_dashboard(request):
    recent_complaints = Complaint.objects.filter(citizen=request.user).order_by('-created_at')[:5]
    total_complaints = Complaint.objects.filter(citizen=request.user).count()
    resolved_complaints = Complaint.objects.filter(citizen=request.user, status='Resolved').count()
    pending_complaints = Complaint.objects.filter(citizen=request.user, status='Submitted').count()
    context = {
        'recent_complaints': recent_complaints,
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
    }
    return render(request, 'dashboard/citizen_dashboard.html', context)


@login_required
def api_submit_complaint(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    if not request.user.is_citizen:
        return JsonResponse({'detail': 'Only citizens can submit complaints.'}, status=403)

    form = ComplaintForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    complaint = form.save(commit=False)
    complaint.citizen = request.user
    complaint.save()

    return JsonResponse({
        'tracking_id': complaint.tracking_id,
        'status': complaint.status,
        'message': 'Complaint submitted successfully.',
    }, status=201)


@login_required
def api_track_complaint(request, tracking_id):
    if request.method != 'GET':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    if request.user.is_authority:
        return JsonResponse({'detail': 'Use authority dashboard for internal tracking.'}, status=403)

    normalized_tracking_id = (tracking_id or '').strip().upper()
    qs = Complaint.objects.filter(tracking_id=normalized_tracking_id)
    if request.user.is_citizen:
        qs = qs.filter(citizen=request.user)

    complaint = qs.first()
    if complaint is None:
        return JsonResponse({'detail': 'Complaint not found.'}, status=404)

    return JsonResponse({
        'tracking_id': complaint.tracking_id,
        'title': complaint.title,
        'status': complaint.status,
        'category': complaint.category.name,
        'submitted_at': complaint.created_at.isoformat(),
        'updated_at': complaint.updated_at.isoformat(),
    })
