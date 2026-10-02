from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.shortcuts import render, redirect
from complaints.models import Complaint, Category

@login_required
def citizen_dashboard(request):
    if not request.user.is_citizen:
        return redirect('dashboard:authority_dashboard')
    citizen = request.user

    qs = Complaint.objects.filter(citizen=citizen)
    categories = Category.objects.all()
    search_query = (request.GET.get("q") or "").strip()
    status_filter = (request.GET.get("status") or "").strip()

    total = qs.count()
    pending = qs.filter(status='Submitted').count()
    in_progress = qs.filter(status='In Progress').count()
    resolved = qs.filter(status='Resolved').count()

    stats = [
        {"label": "Total", "value": total, "icon": "fa-folder-open", "color": "primary"},
        {"label": "Submitted", "value": pending, "icon": "fa-clock", "color": "warning"},
        {"label": "In Progress", "value": in_progress, "icon": "fa-spinner", "color": "info"},
        {"label": "Resolved", "value": resolved, "icon": "fa-circle-check", "color": "success"},
    ]

    filtered_qs = qs
    if search_query:
        filtered_qs = filtered_qs.filter(
            models.Q(title__icontains=search_query) |
            models.Q(category__name__icontains=search_query)
        )
    if status_filter:
        filtered_qs = filtered_qs.filter(status=status_filter)

    recent_complaints = filtered_qs.order_by('-created_at')[:5]

    return render(request, 'dashboard/citizen_dashboard.html', {
        "stats": stats,
        "recent_complaints": recent_complaints,
        "categories": categories,
        "search_query": search_query,
        "status_filter": status_filter,
    })


@login_required
def authority_dashboard(request):
    if not request.user.is_authority:
        return redirect('dashboard:citizen_dashboard')
    qs = Complaint.objects.all()
    context = {
        'total': qs.count(),
        'pending': qs.filter(status='Submitted').count(),
        'resolved': qs.filter(status='Resolved').count(),
        'recent_complaints': qs.order_by('-created_at')[:8],
    }
    return render(request, 'dashboard/authority_dashboard.html', context)

@login_required
def dashboard(request):
    if request.user.is_authority:
        return redirect('dashboard:authority_dashboard')
    return redirect('dashboard:citizen_dashboard')

@login_required
def analytics(request):
    if not request.user.is_authority and not request.user.is_staff:
        return redirect('dashboard:citizen_dashboard')

    category_stats = (
        Category.objects
        .annotate(complaint_count=Count('complaint'))
        .values('name', 'complaint_count')
    )

    status_stats = (
        Complaint.objects
        .values('status')
        .annotate(count=Count('id'))
    )

    return render(request, 'dashboard/analytics.html', {
        'category_stats': category_stats,
        'category_stats_json': json.dumps(list(category_stats), cls=DjangoJSONEncoder),
        'status_stats_json': json.dumps(list(status_stats), cls=DjangoJSONEncoder),
    })
@login_required
def submit_complaint(request):
    categories = Category.objects.all()

    if request.method == "POST":
        Complaint.objects.create(
            citizen=request.user,
            user=request.user,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            category_id=request.POST.get("category"),
            priority=request.POST.get("priority"),
            location=request.POST.get("location"),
        )
        return redirect('dashboard:citizen_dashboard')

    return render(request, 'dashboard/submit_complaint.html', {
        'categories': categories
    })


@login_required
def chatbot(request):
    if not request.user.is_citizen:
        return redirect('dashboard:authority_dashboard')

    faqs = [
        {
            "keywords": ["submit", "complaint", "new", "report"],
            "answer": "To submit a complaint, go to Submit Complaint, fill the form, and click Submit.",
        },
        {
            "keywords": ["track", "status", "progress"],
            "answer": "Use Track Status and enter your complaint ID to see the latest updates.",
        },
        {
            "keywords": ["map", "location"],
            "answer": "Use Map View to see complaints on the city map. You can also set location when submitting.",
        },
        {
            "keywords": ["feedback", "rating"],
            "answer": "After a complaint is resolved, you can submit feedback from the Feedback Center.",
        },
        {
            "keywords": ["priority", "urgent"],
            "answer": "Choose a priority level during submission. Urgent requests are flagged for faster attention.",
        },
        {
            "keywords": ["attachment", "photo", "video", "file"],
            "answer": "You can add photos or files while submitting a complaint to help authorities understand the issue.",
        },
        {
            "keywords": ["edit", "update", "change"],
            "answer": "If you need to update a complaint, check its details page and add an update or contact support.",
        },
        {
            "keywords": ["authority", "admin", "approval"],
            "answer": "Authority accounts require approval. You can register as authority and wait for admin approval.",
        },
        {
            "keywords": ["login", "register", "signup"],
            "answer": "Use Register to create an account, then Login to access your dashboard.",
        },
        {
            "keywords": ["location", "gps", "map", "pin"],
            "answer": "When submitting, you can pin your location on the map or use live location for accuracy.",
        },
    ]

    user_message = (request.POST.get("message") or "").strip()
    reply = None

    if user_message:
        lowered = user_message.lower()
        for item in faqs:
            if any(keyword in lowered for keyword in item["keywords"]):
                reply = item["answer"]
                break
        if reply is None:
            reply = (
                "I can help with submitting complaints, tracking status, map view, and feedback. "
                "Try asking about one of those."
            )

    recent_complaints = Complaint.objects.filter(citizen=request.user).order_by('-created_at')[:5]

    return render(request, 'dashboard/chatbot.html', {
        "user_message": user_message,
        "reply": reply,
        "faqs": faqs,
        "recent_complaints": recent_complaints,
    })





