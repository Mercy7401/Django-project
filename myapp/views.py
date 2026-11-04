#used to take respomse from the user and return a response to the user

from django.shortcuts import render

def home(request): 
    #pull datafrom db, transform and send email
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
