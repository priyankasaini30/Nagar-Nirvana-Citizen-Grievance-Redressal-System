from django.contrib import admin
from django.utils import timezone
from .models import User, AuthorityRegistrationRequest


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_citizen", "is_authority", "is_active", "is_staff")
    search_fields = ("username", "email")
    list_filter = ("is_citizen", "is_authority", "is_active", "is_staff")


@admin.register(AuthorityRegistrationRequest)
class AuthorityRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "requested_at", "reviewed_at", "reviewed_by")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    actions = ("approve_requests", "reject_requests")

    @admin.action(description="Approve selected authority requests")
    def approve_requests(self, request, queryset):
        now = timezone.now()
        for req in queryset:
            req.status = "approved"
            req.reviewed_at = now
            req.reviewed_by = request.user
            req.save()
            req.user.is_active = True
            req.user.is_authority = True
            req.user.is_citizen = False
            req.user.save()

    @admin.action(description="Reject selected authority requests")
    def reject_requests(self, request, queryset):
        now = timezone.now()
        for req in queryset:
            req.status = "rejected"
            req.reviewed_at = now
            req.reviewed_by = request.user
            req.save()
            req.user.is_active = False
            req.user.is_authority = False
            req.user.save()
