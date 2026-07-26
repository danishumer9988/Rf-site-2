from django.shortcuts import render

def privacy_policy(request):
    """
    Renders the Privacy Policy page.
    """
    return render(request, 'pages/privacy.html')

def terms_of_service(request):
    """
    Renders the Terms of Service page.
    """
    return render(request, 'pages/terms.html')

def faq(request):
    """
    Renders the FAQ page.
    """
    return render(request, 'pages/faq.html')