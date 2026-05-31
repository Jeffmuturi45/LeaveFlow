from django.core.management.base import BaseCommand
from core.models import DashboardWidget, DashboardCustomization

WIDGETS_DATA = [
    {
        'widget_id': 'employee_overview',
        'title': 'Employee Overview',
        'icon': 'fas fa-users',
        'description': 'Total active employees and current leave status',
        'roles': ['super_admin', 'hr_officer'],
        'default_enabled': True
    },
    {
        'widget_id': 'leave_overview',
        'title': 'Leave Overview',
        'icon': 'fas fa-calendar-check',
        'description': 'Approved leaves and pending requests summary',
        'roles': ['super_admin', 'hr_officer'],
        'default_enabled': True
    },
    {
        'widget_id': 'department_breakdown',
        'title': 'Department Breakdown',
        'icon': 'fas fa-sitemap',
        'description': 'Employee count by department',
        'roles': ['super_admin', 'hr_officer'],
        'default_enabled': True
    },
    {
        'widget_id': 'recent_activities',
        'title': 'Recent Activities',
        'icon': 'fas fa-history',
        'description': 'System audit log and recent actions',
        'roles': ['super_admin'],
        'default_enabled': True
    },
    {
        'widget_id': 'leave_type_distribution',
        'title': 'Leave Type Distribution',
        'icon': 'fas fa-chart-pie',
        'description': 'Breakdown of leaves by type',
        'roles': ['super_admin', 'hr_officer'],
        'default_enabled': True
    },
    {
        'widget_id': 'system_health',
        'title': 'System Health',
        'icon': 'fas fa-heartbeat',
        'description': 'System status and key metrics',
        'roles': ['super_admin'],
        'default_enabled': True
    },
    {
        'widget_id': 'on_leave_today',
        'title': 'On Leave Today',
        'icon': 'fas fa-umbrella-beach',
        'description': 'Number of employees on leave today',
        'roles': ['hr_officer'],
        'default_enabled': True
    },
    {
        'widget_id': 'pending_approvals',
        'title': 'Pending Approvals',
        'icon': 'fas fa-hourglass-half',
        'description': 'HR approvals awaiting action',
        'roles': ['hr_officer', 'manager'],
        'default_enabled': True
    },
    {
        'widget_id': 'recent_applications',
        'title': 'Recent Applications',
        'icon': 'fas fa-inbox',
        'description': 'Latest leave applications',
        'roles': ['hr_officer'],
        'default_enabled': True
    },
    {
        'widget_id': 'leave_balance_overview',
        'title': 'Leave Balance Overview',
        'icon': 'fas fa-wallet',
        'description': 'Company-wide leave balance status',
        'roles': ['hr_officer'],
        'default_enabled': False
    },
    {
        'widget_id': 'department_counts',
        'title': 'Department Counts',
        'icon': 'fas fa-building',
        'description': 'Number of employees per department',
        'roles': ['hr_officer'],
        'default_enabled': False
    },
    {
        'widget_id': 'upcoming_holidays',
        'title': 'Upcoming Holidays',
        'icon': 'fas fa-calendar-alt',
        'description': 'Next public holidays',
        'roles': ['hr_officer', 'manager', 'employee'],
        'default_enabled': False
    },
    {
        'widget_id': 'team_count',
        'title': 'Team Count',
        'icon': 'fas fa-people-group',
        'description': 'Number of team members',
        'roles': ['manager'],
        'default_enabled': True
    },
    {
        'widget_id': 'team_on_leave',
        'title': 'Team On Leave',
        'icon': 'fas fa-plane-departure',
        'description': 'Team members on leave today',
        'roles': ['manager'],
        'default_enabled': True
    },
    {
        'widget_id': 'approved_this_month',
        'title': 'Approved This Month',
        'icon': 'fas fa-check-circle',
        'description': 'Leave approvals granted this month',
        'roles': ['manager'],
        'default_enabled': True
    },
    {
        'widget_id': 'pending_requests',
        'title': 'Pending Requests',
        'icon': 'fas fa-list',
        'description': 'Team leave requests awaiting review',
        'roles': ['manager'],
        'default_enabled': True
    },
    {
        'widget_id': 'my_leave_balance',
        'title': 'My Leave Balance',
        'icon': 'fas fa-chart-bar',
        'description': 'Personal leave balance and usage',
        'roles': ['employee'],
        'default_enabled': True
    },
    {
        'widget_id': 'recent_applications',
        'title': 'Recent Applications',
        'icon': 'fas fa-history',
        'description': 'My recent leave applications',
        'roles': ['employee'],
        'default_enabled': True
    },
    {
        'widget_id': 'quick_apply',
        'title': 'Quick Apply',
        'icon': 'fas fa-plus-circle',
        'description': 'Quick access to apply for leave',
        'roles': ['employee'],
        'default_enabled': True
    },
    {
        'widget_id': 'calendar_mini',
        'title': 'Calendar Mini',
        'icon': 'fas fa-calendar',
        'description': 'Mini calendar view of my leaves',
        'roles': ['employee'],
        'default_enabled': False
    },
]

ROLE_DEFAULTS = {
    'super_admin': [
        'employee_overview', 'leave_overview', 'department_breakdown',
        'recent_activities', 'leave_type_distribution', 'system_health'
    ],
    'hr_officer': [
        'on_leave_today', 'pending_approvals', 'recent_applications',
        'leave_type_distribution', 'department_counts'
    ],
    'manager': [
        'team_count', 'pending_approvals', 'team_on_leave',
        'approved_this_month', 'pending_requests'
    ],
    'employee': [
        'my_leave_balance', 'recent_applications', 'quick_apply'
    ],
}

class Command(BaseCommand):
    help = 'Initialize dashboard widgets and default configurations'

    def handle(self, *args, **options):
        self.stdout.write('Creating dashboard widgets...')

        created_count = 0
        updated_count = 0

        for widget_data in WIDGETS_DATA:
            widget_id = widget_data['widget_id']
            widget, created = DashboardWidget.objects.update_or_create(
                widget_id=widget_id,
                defaults={
                    'title': widget_data['title'],
                    'icon': widget_data['icon'],
                    'description': widget_data['description'],
                    'roles': widget_data['roles'],
                    'default_enabled': widget_data['default_enabled']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [+] Created: {widget.title}'))
            else:
                updated_count += 1
                self.stdout.write(f'  [*] Updated: {widget.title}')

        self.stdout.write(f'\nWidgets: {created_count} created, {updated_count} updated\n')

        self.stdout.write('Creating default customizations...')

        custom_count = 0
        for role, default_widgets in ROLE_DEFAULTS.items():
            customization, created = DashboardCustomization.objects.update_or_create(
                role=role,
                defaults={'enabled_widgets': default_widgets}
            )
            if created:
                custom_count += 1
                role_display = dict(DashboardCustomization.ROLE_CHOICES).get(role, role)
                self.stdout.write(self.style.SUCCESS(f'  [+] Created default for: {role_display}'))
            else:
                self.stdout.write(f'  [*] Updated: {role}')

        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Dashboard setup complete! {custom_count} role configs created.\n'))
