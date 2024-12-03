from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, StudentRegistration, Program, Section, Violation, Sanction, ViolationRecord
from .forms import StudentRegistrationAdminForm, StaffSignupForm

# Set Admin Header
admin.site.site_header = "Student Violation System Administration"
admin.site.site_title = "Student Violation System Admin Portal"
admin.site.index_title = "Welcome to Student Violation System Portal"



class LogUtils:
    @staticmethod
    def create_log_entry(request_user, obj, action):
        """
        Create a log entry for administrative actions
        
        :param request_user: The user performing the action
        :param obj: The object being modified
        :param action: Description of the action taken
        """
        LogEntry.objects.log_action(
            user_id=request_user.id,
            content_type_id=ContentType.objects.get_for_model(obj).id,
            object_id=obj.id,
            object_repr=str(obj),
            action_flag=CHANGE,
            change_message=action
        )

class ApprovalStatusFilter(admin.SimpleListFilter):
    title = 'Approval Status'
    parameter_name = 'approval_status'

    def lookups(self, request, model_admin):
        return (
            (None, 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        )

    def queryset(self, request, queryset):
        if self.value() == 'approved':
            return queryset.filter(is_approved=True)
        if self.value() == 'rejected':
            return queryset.filter(is_approved=False)
        if self.value() is None:
            return queryset.filter(is_approved=None)

@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_max_show_all = 500
    form = StudentRegistrationAdminForm

    list_display = (
        'display_username',
        'full_name',
        'view_program',
        'view_section',
        'view_registration_date',
        'view_cor',
        'view_id',
        'actions_buttons',
        'approval_status'
    )
    list_filter = (
        'is_approved',
        'registration_date',
        'review_date',
        'program',
        'section'
    )
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'program__name',
        'program__code',
        'section__name'
    )
    readonly_fields = ('registration_date', 'review_date')
    actions = ['approve_selected', 'reject_selected']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'program', 'section')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        class CustomForm(form):
            def __init__(self, *args, **kwargs):
                kwargs['current_user'] = request.user
                super().__init__(*args, **kwargs)
        
        return CustomForm
    
    def display_username(self, obj):
        return obj.user.username if obj.user_id else "No User"
    display_username.short_description = 'Username'
    display_username.admin_order_field = 'user__username'

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user_id else "No User"
    full_name.admin_order_field = 'user__first_name'

    def view_program(self, obj):
        return obj.program.name if obj.program else "Not Assigned"
    view_program.short_description = 'Program'

    def view_section(self, obj):
        return obj.section.name if obj.section else "Not Assigned"
    view_section.short_description = 'Section'

    def approval_status(self, obj):
        status_colors = {
            None: '#FFA500',  # Pending
            True: '#008000',  # Approved
            False: '#FF0000'  # Rejected
        }
        status_text = {None: 'Pending', True: 'Approved', False: 'Rejected'}
        return format_html(
            '<span style="color: {};">{}</span>',
            status_colors[obj.is_approved],
            status_text[obj.is_approved]
        )
    approval_status.short_description = 'Status'

    def _render_image(self, obj, image_field_name):
        image_field = getattr(obj, image_field_name, None)
        if image_field:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height: 50px;"/></a>',
                image_field.url, image_field.url
            )
        return "No image"

    def view_cor(self, obj):
        return self._render_image(obj, 'cor_image')

    def view_id(self, obj):
        return self._render_image(obj, 'id_image')

    def view_registration_date(self, obj):
        return obj.registration_date.strftime('%Y-%m-%d %H:%M:%S') if obj.registration_date else "No date"
    view_registration_date.short_description = 'Registration Date'

    def actions_buttons(self, obj):
        if obj.is_approved is None:
            approve_url = f"{reverse('admin:adminmod_studentregistration_change', args=[obj.pk])}?action=approve"
            reject_url = f"{reverse('admin:adminmod_studentregistration_change', args=[obj.pk])}?action=reject"
            return format_html(
                '<a class="button" href="{}" style="background-color: #4CAF50; color: white; margin-right: 5px;">Approve</a>'
                '<a class="button" href="{}" style="background-color: #f44336; color: white;">Reject</a>',
                approve_url, reject_url
            )
        return "Processed"
    actions_buttons.short_description = 'Actions'

    def save_model(self, request, obj, form, change):
        if change:
            obj.review_date = timezone.now()
        super().save_model(request, obj, form, change)
        LogUtils.create_log_entry(request.user, obj, "Changed via admin interface")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if 'action' in request.GET and obj:
            action = request.GET['action']
            if action == 'approve':
                obj.approve_registration('Approved by admin')
                LogUtils.create_log_entry(request.user, obj, "Registration approved")
                self.message_user(request, 'Registration has been approved.')
            elif action == 'reject':
                obj.decline_registration('Rejected by admin')
                LogUtils.create_log_entry(request.user, obj, "Registration rejected")
                self.message_user(request, 'Registration has been rejected.')
        return super().change_view(request, object_id, form_url, extra_context)

    def _bulk_update_status(self, request, queryset, status, action_text):
        try:
            for obj in queryset:
                if status:
                    obj.approve_registration(f'Approved in bulk action')
                else:
                    obj.decline_registration(f'Rejected in bulk action')
                LogUtils.create_log_entry(request.user, obj, f'Registration {action_text} in bulk')
            self.message_user(request, f"{queryset.count()} registrations have been {action_text}.")
        except Exception as e:
            self.message_user(request, f"An error occurred: {str(e)}", level='error')
        
    def approve_selected(self, request, queryset):
        self._bulk_update_status(request, queryset, True, 'approved')
    approve_selected.short_description = "Approve selected registrations"

    def reject_selected(self, request, queryset):
        self._bulk_update_status(request, queryset, False, 'rejected')
    reject_selected.short_description = "Reject selected registrations"

    def get_fieldsets(self, request, obj=None):
        if obj:  # Change view
            return (
                ('User Information', {
                    'fields': ('user_username', 'user_first_name', 'user_last_name', 'user_email', 'registration_date')
                }),
                ('Program and Section', {
                    'fields': ('program', 'section')
                }),
                ('Documents', {
                    'fields': ('cor_image', 'id_image')
                }),
                ('Review Information', {
                    'fields': ('is_approved', 'review_comments', 'review_date')
                }),
                ('Change Confirmation', {
                    'fields': ('admin_password',),
                }),
            )
        else:  # Add view
            return (
                ('User Information', {
                    'fields': ('user_username', 'user_first_name', 'user_last_name', 'user_email', 'password1', 'password2')
                }),
                ('Program and Section', {
                    'fields': ('program', 'section')
                }),
                ('Documents', {
                    'fields': ('cor_image', 'id_image')
                }),
                ('Review Information', {
                    'fields': ('is_approved', 'review_comments', 'review_date')
                }),
                ('Change Confirmation', {
                    'fields': ('admin_password',),
                }),
            )


    def get_fields(self, request, obj=None):
        if obj:  # Change view
            return ['user_username', 'user_first_name', 'user_last_name', 'user_email', 'registration_date', 
                    'program', 'section', 'cor_image', 'id_image', 
                    'is_approved', 'review_comments', 'review_date', 'admin_password']
        else:  # Add view
            return ['user_username', 'user_first_name', 'user_last_name', 'user_email', 
                    'program', 'section', 'cor_image', 'id_image']
            
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_approved is None:
            return ['registration_date', 'review_date']
        elif obj and obj.is_approved is not None:
            return ['username', 'first_name', 'last_name', 'email', 
                    'registration_date', 'review_date', 'cor_image', 'id_image']
        return []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "section":
            if 'program' in request.GET:
                kwargs["queryset"] = Section.objects.filter(program_id=request.GET['program'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'section_count')
    search_fields = ('name', 'code')
    list_filter = ('name',)
    
    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Number of Sections'

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'program_code')
    search_fields = ('name', 'program__name', 'program__code')
    list_filter = ('program',)
    
    def program_code(self, obj):
        return obj.program.code
    program_code.short_description = 'Program Code'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "program":
            kwargs["queryset"] = Program.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'severity_colored', 
        'sanction_count', 
        'brief_description'
    )
    search_fields = ('name', 'description')
    list_filter = ('severity',)
    
    def severity_colored(self, obj):
        severity_colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        color = severity_colors.get(obj.severity, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_colored.short_description = 'Severity'
    
    def sanction_count(self, obj):
        return obj.sanctions.count()
    sanction_count.short_description = 'Sanctions'
    
    def brief_description(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description or 'No description'
    brief_description.short_description = 'Description'

@admin.register(Sanction)
class SanctionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'violation_display', 
        'duration_display', 
        'violation_severity_colored'
    )
    search_fields = ('name', 'violation__name')
    list_filter = ('violation', 'duration_unit')
    
    def violation_display(self, obj):
        return obj.violation.name
    violation_display.short_description = 'Related Violation'
    
    def duration_display(self, obj):
        return f"{obj.duration_value} {obj.get_duration_unit_display()}"
    duration_display.short_description = 'Duration'
    
    def violation_severity_colored(self, obj):
        severity_colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        severity = obj.violation.severity
        color = severity_colors.get(severity, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.violation.get_severity_display()
        )
    violation_severity_colored.short_description = 'Violation Severity'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "violation":
            kwargs["queryset"] = Violation.objects.all().order_by('-severity', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        # Add any custom fields from your User model
        ('Additional Information', {'fields': ('role',)}),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', )
    def get_queryset(self, request):
        return super().get_queryset(request).exclude(role=User.Role.STUDENT)
    
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    add_form = StaffSignupForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name', 
                'email', 'employee_id', 'role',
                'password1', 'password2'
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_fields(self, request, obj=None):
        if not obj:
            return list(self.add_fieldsets[0][1]['fields'])
        return super().get_fields(request, obj)
@admin.register(ViolationRecord)
class ViolationRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'violation', 'recorded_by', 'recorded_at')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'violation__name')
    list_filter = ('recorded_at', 'violation__severity')