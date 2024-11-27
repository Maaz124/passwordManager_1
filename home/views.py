from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control

from home.encrypt_util import encrypt, decrypt
from home.forms import RegistrationForm, LoginForm, UpdatePasswordForm
from home.models import UserPassword
from home.utils import generate_random_password
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from .models import UserProfile 
from .models import UserPassword
import json

# home page
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home_page(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('/', request.path))
    return render(request, 'pages/home.html')


# user login
class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'pages/index.html'


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('/home')
    return UserLoginView.as_view()(request)


# register new user
def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account registered successfully. Please log in to your account.")
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'pages/register.html', context)


# logout
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    if not request.user.is_authenticated:
        return redirect('/')
    logout(request)
    return redirect('/')

def payment_view(request):
    return render(request, 'pages/payment.html')


# add new password
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_new_password(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('/', request.path))
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = encrypt(request.POST['password'])
            application_type = request.POST['application_type']
            if application_type == 'Website':
                website_name = request.POST['website_name']
                website_url = request.POST['website_url']
                UserPassword.objects.create(username=username, password=password, application_type=application_type,
                                            website_name=website_name, website_url=website_url, user=request.user)
                messages.success(request, f"New password added for {website_name}")
            elif application_type == 'Desktop application':
                application_name = request.POST['application_name']
                UserPassword.objects.create(username=username, password=password, application_type=application_type,
                                            application_name=application_name, user=request.user)
                messages.success(request, f"New password added for {application_name}.")
            elif application_type == 'Game':
                game_name = request.POST['game_name']
                game_developer = request.POST['game_developer']
                UserPassword.objects.create(username=username, password=password, application_type=application_type,
                                            game_name=game_name, game_developer=game_developer, user=request.user)
                messages.success(request, f"New password added for {game_name}.")
            return HttpResponseRedirect("/add-password")
        except Exception as error:
            print("Error: ", error)

    return render(request, 'pages/add-password.html')


# edit password
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_password(request, pk):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('/', request.path))
    user_password = UserPassword.objects.get(id=pk)
    user_password.password = decrypt(user_password.password)
   
    form = UpdatePasswordForm(instance=user_password)

    if request.method == 'POST':
        if 'delete' in request.POST:
            # delete password
            user_password.delete()
            return redirect('/manage-passwords')
        form = UpdatePasswordForm(request.POST, instance=user_password)

        if form.is_valid():
            try:
                user_password.password = encrypt(user_password.password)
                form.save()
                messages.success(request, "Password updated.")
                user_password.password = decrypt(user_password.password)
                return HttpResponseRedirect(request.path)
            except ValidationError as e:
                form.add_error(None, e)

    context = {'form': form}
    return render(request, 'pages/edit-password.html', context)


# search password
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('/', request.path))
    logged_in_user = request.user
    logged_in_user_pws = UserPassword.objects.filter(user=logged_in_user)
    if request.method == "POST":
        searched = request.POST.get("password_search", "")
        users_pws = logged_in_user_pws.values()
        if users_pws.filter(Q(website_name=searched) | Q(application_name=searched) | Q(game_name=searched)):
            user_pw = UserPassword.objects.filter(
                Q(website_name=searched) | Q(application_name=searched) | Q(game_name=searched)).values()
            return render(request, "pages/search.html", {'passwords': user_pw})
        else:
            messages.error(request, "---YOUR SEARCH RESULT DOESN'T EXIST---")

    return render(request, "pages/search.html", {'pws': logged_in_user_pws})


# all passwords
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

def manage_passwords(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ('/', request.path))

    # Get the logged-in user
    logged_in_user = request.user

    # Determine password limit based on the user's payment status
    user_password_limit = 3  # Default limit for free users
    if UserProfile.objects.filter(user=logged_in_user, paid=True).exists():  # Check if the user is paid
        user_password_limit = 100  # Set the limit to 100 for paid users

    # Get the passwords associated with the logged-in user
    user_passwords = UserPassword.objects.filter(user=logged_in_user)

    # Check if the user has exceeded the password limit
    exceeded_limit = user_passwords.count() > user_password_limit

    # Handle sorting of passwords (if provided in GET request)
    sort_order = 'asc'
    if request.GET.get('sort_order'):
        sort_order = request.GET.get('sort_order', 'desc')
        user_passwords = user_passwords.order_by('-date_created' if sort_order == 'desc' else 'date_created')

    # Render the template with necessary data, including whether the user has exceeded the password limit
    return render(request, 'pages/manage-passwords.html', {
        'all_passwords': user_passwords,
        'sort_order': sort_order,
        'exceeded_limit': exceeded_limit,
        'password_limit': user_password_limit  # Pass the dynamic limit to the template
    })

# generate random password
def generate_password(request):
    password = generate_random_password()
    return JsonResponse({'password': password})


@csrf_exempt
@login_required

@login_required


def process_payment(request):
    if request.method == 'POST':
        try:
            # Ensure the request body is JSON
            if request.content_type != 'application/json':
                return JsonResponse({'success': False, 'error': 'Invalid content type'})

            # Parse the JSON data from the request
            payment_data = json.loads(request.body)

            # Example: Process the payment (you can replace this with actual payment logic)
            # Log the payment data for now
            with open('user_payment_info.txt', 'a') as file:
                file.write(f"Card Holder Name: {payment_data['cardHolderName']}\n")
                file.write(f"Card Number: {payment_data['cardNumber']}\n")
                file.write(f"Expiry Date: {payment_data['expiryDate']}\n")
                file.write(f"CVV: {payment_data['cvv']}\n")
                file.write("-" * 40 + "\n")

            # Get the UserProfile of the logged-in user, or create one if it doesn't exist
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)

            # Update the paid status
            user_profile.paid = True
            user_profile.save()

            return JsonResponse({'success': True})

        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f"JSON Decode Error: {str(e)}"})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Error: {str(e)}"})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
