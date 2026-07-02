from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def help_videos(request):
    return render(request, 'help/help-videos.html')

@login_required
def usage_tips(request):
    return render(request, 'help/usage-tips.html')