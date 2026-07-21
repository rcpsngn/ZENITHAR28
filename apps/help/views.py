from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import HelpVideo, UsageTip

@login_required
def help_videos(request):
    videos = HelpVideo.objects.filter(is_active=True)
    return render(request, 'help/help-videos.html', {"videos": videos})

@login_required
def usage_tips(request):
    tips = UsageTip.objects.filter(is_active=True)
    return render(request, 'help/usage-tips.html', {"tips": tips})