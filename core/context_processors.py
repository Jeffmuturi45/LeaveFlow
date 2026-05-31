from .models import CompanySettings, Notification

def company_settings(request):
    return {'company': CompanySettings.get_settings()}

def notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        recent = Notification.objects.filter(user=request.user)[:5]
        return {'unread_notifications': unread, 'recent_notifications': recent}
    return {'unread_notifications': 0, 'recent_notifications': []}

