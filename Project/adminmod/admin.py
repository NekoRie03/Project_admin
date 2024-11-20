from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import StudentRegistration, User

admin.site.site_header = "Student Violation System Administration"
admin.site.site_title = "Student Violation System Admin Portal"
admin.site.index_title = "Welcome to Student Violation System Portal"

@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('display_username', 'full_name', 'view_registration_date', 'view_cor', 'view_id', 'actions_buttons', 'approval_status')
    list_filter = ('is_approved', 'registration_date', 'review_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('registration_date', 'review_date')
    actions = ['approve_selected', 'reject_selected']

    def display_username(self, obj):
        return obj.user.username
    display_username.short_description = 'Username'
    display_username.admin_order_field = 'user__username'

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    full_name.admin_order_field = 'user__first_name'
    
    def approval_status(self, obj):
        if obj.is_approved is None:
            return format_html('<span style="color: #FFA500;">Pending</span>')
        elif obj.is_approved:
            return format_html('<span style="color: #008000;">Approved</span>')
        else:
            return format_html('<span style="color: #FF0000;">Rejected</span>')
    approval_status.short_description = 'Status'

    def view_cor(self, obj):
        if obj.cor_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 50px;"/></a>',
                obj.cor_image.url, obj.cor_image.url
            )
        return "No image"
    view_cor.short_description = 'COR Image'

    def view_id(self, obj):
        if obj.id_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 50px;"/></a>',
                obj.id_image.url, obj.id_image.url
            )
        return "No image"
    view_id.short_description = 'ID Image'
    
    def view_registration_date(self, obj):
        return obj.registration_date.strftime('%Y-%m-%d %H:%M:%S') if obj.registration_date else "No date"
    view_registration_date.short_description = 'Registration Date'
        
    def actions_buttons(self, obj):
        if obj.is_approved is None:
            return format_html(
                '<a class="button" href="{}?action=approve" style="background-color: #4CAF50; color: white; margin-right: 5px;">Approve</a>'
                '<a class="button" href="{}?action=reject" style="background-color: #f44336; color: white;">Reject</a>',
                reverse('admin:adminmod_studentregistration_change', args=[obj.pk]), 
                reverse('admin:adminmod_studentregistration_change', args=[obj.pk])
            )
        return "Processed"
    actions_buttons.short_description = 'Actions'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def save_model(self, request, obj, form, change):
        if change:
            obj.review_date = timezone.now()
        
        # Save the model first
        super().save_model(request, obj, form, change)
        
        # Manually create the admin log entry
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=str(obj),
            action_flag=CHANGE,
            change_message='Changed via admin interface'
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if 'action' in request.GET:
            obj = self.get_object(request, object_id)
            if request.GET['action'] == 'approve':
                obj.approve_registration('Approved by admin')
                # Create log entry for approval
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(obj).pk,
                    object_id=obj.pk,
                    object_repr=str(obj),
                    action_flag=CHANGE,
                    change_message='Registration approved'
                )
                self.message_user(request, 'Registration has been approved.')
            elif request.GET['action'] == 'reject':
                obj.decline_registration('Rejected by admin')
                # Create log entry for rejection
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(obj).pk,
                    object_id=obj.pk,
                    object_repr=str(obj),
                    action_flag=CHANGE,
                    change_message='Registration rejected'
                )
                self.message_user(request, 'Registration has been rejected.')
        
        return super().change_view(request, object_id, form_url, extra_context)

    def approve_selected(self, request, queryset):
        for obj in queryset:
            obj.approve_registration('Approved in bulk action')
            # Create log entry for bulk approval
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=CHANGE,
                change_message='Registration approved in bulk'
            )
        self.message_user(request, f"{queryset.count()} registrations have been approved.")
    approve_selected.short_description = "Approve selected registrations"

    def reject_selected(self, request, queryset):
        for obj in queryset:
            obj.decline_registration('Rejected in bulk action')
            # Create log entry for bulk rejection
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=CHANGE,
                change_message='Registration rejected in bulk'
            )
        self.message_user(request, f"{queryset.count()} registrations have been rejected.")
    reject_selected.short_description = "Reject selected registrations"
    
    def registration_status(self, obj):
        if obj.is_approved is None:
            return format_html('<span class="badge badge-warning">Pending</span>')
        elif obj.is_approved:
            return format_html('<span class="badge badge-success">Approved</span>')
        else:
            return format_html('<span class="badge badge-danger">Declined</span>')

    def review_comments_display(self, obj):
        if obj.review_comments:
            return obj.review_comments[:50] + '...'
        return ''
    review_comments_display.short_description = 'Review Comments'

    def approve_registrations(self, request, queryset):
        for registration in queryset:
            registration.approve_registration(comments='Approved by admin')
    approve_registrations.short_description = "Approve selected registrations"

    def decline_registrations(self, request, queryset):
        for registration in queryset:
            registration.decline_registration(comments='Declined by admin')
    decline_registrations.short_description = "Decline selected registrations"
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_approved is not None:
            return ['user','registration_date', 'cor_image', 'id_image']
        return []

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'registration_date')
        }),
        ('Documents', {
            'fields': ('cor_image', 'id_image')
        }),
        ('Review Information', {
            'fields': ('is_approved', 'review_comments', 'review_date')
        }),
    )
    
    #can't motherfucking save
    def save_model(self, request, obj, form, change):
        if change:
            obj.review_date = timezone.now()
        super().save_model(request, obj, form, change)