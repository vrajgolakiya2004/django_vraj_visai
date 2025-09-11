import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .forms import UserForm, UserLoginForm, PasswordChangeForm
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Set up logging
logger = logging.getLogger(__name__)
ph = PasswordHasher()

def signUpFun(request):
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = ph.hash(form.cleaned_data['password'])
            user.check_password = ph.hash(form.cleaned_data['check_password'])
            user.save()
            messages.success(request, "Account created successfully! Please sign in.")
            return redirect('signInPage')
        else:
            logger.debug(f"Form errors: {form.errors}")
            # Messages are already added in the template via form.errors
    else:
        form = UserForm()
    
    return render(request, 'sign-up.html', {'form': form})



def signInFun(request):
    logger.debug("Entering signin view")
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            request.session.flush()  # Clear any existing session data

            if not email or not password:
                messages.error(request, "Please enter both email and password.")
                return render(request, 'sign-in.html', {'form': form})

            try:
                user = User.objects.get(email=email)
                try:
                    if ph.verify(user.password, password):
                        # Set session data
                        request.session['user_id'] = user.id
                        request.session['user_email'] = email
                        request.session['user_name'] = user.name
                        request.session['user_phone'] = user.phone
                        request.session['user_image'] = user.image.url if user.image else '/static/assets/img/user/user.jpg'
                        logger.debug(f"Session set: email={request.session['user_email']}, name={request.session['user_name']}, image={request.session['user_image']}")
                        messages.success(request, "Successfully signed in!")
                        return redirect('indexPage')
                    else:
                        messages.error(request, "Incorrect password.")
                except VerifyMismatchError:
                    messages.error(request, "Incorrect password.")
                except Exception as e:
                    logger.error(f"Password verification failed: {e}")
                    messages.error(request, "An error occurred during sign-in. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            logger.debug(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
        return render(request, 'sign-in.html', {'form': form})
    else:
        form = UserLoginForm()
    return render(request, 'sign-in.html', {'form': form})

def logoutFun(request):
    logger.debug("Logging out user")
    request.session.flush()  # Clear the session
    messages.success(request, "You have been logged out.")
    return redirect('signInPage')

def indexFun(request):
    user_email = request.session.get('user_email')
    user_name = request.session.get('user_name')
    if not user_email:
        messages.error(request, "Please sign in to access the dashboard.")
        return redirect('signInPage')
    
    return render(request, 'index.html', {'user_email': user_email, 'user_name': user_name})

def userProfileFun(request):
    user_email = request.session.get('user_email')
    if not user_email:
        messages.error(request, "Please sign in to access your profile.")
        return redirect('signInPage')
    
    try:
        user = User.objects.get(email=user_email)
        return render(request, 'user-profile.html', {
            'user_name': user.name,
            'user_email': user.email,
            'user_phone': user.phone,
            'user_image': user.image.url if user.image else None
        })
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('signInPage')

# def updateProfileFun(request):
#     if 'user_email' not in request.session:
#         messages.error(request, "Please sign in to update your profile.")
#         return redirect('signInPage')

#     try:
#         user = User.objects.get(email=request.session['user_email'])
#         if request.method == "POST":
#             form = UserForm(request.POST, request.FILES, instance=user)
#             if form.is_valid():
#                 user = form.save(commit=False)
#                 password = form.cleaned_data.get('password')
#                 check_password = form.cleaned_data.get('check_password')
#                 if password and check_password:  # Update both password and check_password if provided
#                     user.password = ph.hash(password)
#                     user.check_password = ph.hash(check_password)
#                     logger.debug("Password and check_password updated successfully.")
#                 user.save()
#                 # Update session data
#                 request.session['user_email'] = user.email
#                 request.session['user_name'] = user.name
#                 request.session['user_phone'] = user.phone if user.phone else ''
#                 request.session['user_image'] = user.image.url if user.image else '/static/assets/img/user/user.jpg'
#                 messages.success(request, "Profile updated successfully!")
#                 return redirect('userProfilePage')
#             else:
#                 logger.debug(f"Form errors: {form.errors}")
#                 for field, errors in form.errors.items():
#                     for error in errors:
#                         messages.error(request, f"{field}: {error}")
#         else:
#             form = UserForm(instance=user)

#         return render(request, 'user-settings.html', {
#             'form': form,
#             'user_name': user.name,
#             'user_email': user.email,
#             'user_phone': user.phone,
#             'user_image': user.image.url if user.image else None
#         })

#     except User.DoesNotExist:
#         messages.error(request, "User not found.")
#         return redirect('signInPage')

#     except MultipleObjectsReturned:
#         messages.error(request, "Multiple accounts found with this email. Please contact support.")
#         return redirect('signInPage')

#     except Exception as e:
#         logger.error(f"Profile update failed: {e}")
#         messages.error(request, f"Update failed: {e}")
#         return redirect('userSettingsPage')

logger = logging.getLogger(__name__)

def updateProfileFun(request):
    if 'user_email' not in request.session:
        messages.error(request, "Please sign in to update your profile.")
        return redirect('signInPage')

    try:
        user = User.objects.get(email=request.session['user_email'])
        if request.method == "POST":
            form = UserForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                user = form.save(commit=False)
                password = form.cleaned_data.get('password')
                check_password = form.cleaned_data.get('check_password')
                
                if password and check_password:  # Update passwords only if provided
                    user.password = ph.hash(password)
                    user.check_password = ph.hash(check_password)
                    logger.debug("Password updated successfully.")

                user.save()

                # Update session data, ensuring a fallback default image
                request.session['user_email'] = user.email
                request.session['user_name'] = user.name
                request.session['user_phone'] = user.phone if user.phone else ''
                request.session['user_image'] = getattr(user.image, 'url', '/static/assets/img/user/default.jpg')

                messages.success(request, "Profile updated successfully!")
                return redirect('userProfilePage')
            else:
                logger.debug(f"Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = UserForm(instance=user)

        return render(request, 'user-settings.html', {
            'form': form,
            'user_name': user.name,
            'user_email': user.email,
            'user_phone': user.phone,
            'user_image': getattr(user.image, 'url', None)  # Avoid errors
        })

    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('signInPage')

    except MultipleObjectsReturned:
        messages.error(request, "Multiple accounts found with this email. Please contact support.")
        return redirect('signInPage')

    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        messages.error(request, f"Update failed: {e}")
        return redirect('userSettingsPage')


def changePasswordFun(request):
    if 'user_email' not in request.session:
        messages.error(request, "Please sign in to change your password.")
        return redirect('signInPage')

    try:
        user = User.objects.get(email=request.session['user_email'])
        if request.method == "POST":
            form = PasswordChangeForm(user=user, data=request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.password = ph.hash(new_password)
                user.check_password = ph.hash(new_password)  # Update check_password as well
                user.save()
                messages.success(request, "Password changed successfully! Please sign in again.")
                request.session.flush()  # Log the user out after password change
                return redirect('signInPage')
            else:
                logger.debug(f"Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = PasswordChangeForm(user=user)

        return render(request, 'password-change.html', {
            'form': form,
            'user_name': user.name,
            'user_email': user.email,
            'user_phone': user.phone,
            'user_image': user.image.url if user.image else None
        })

    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('signInPage')

    except Exception as e:
        logger.error(f"Password change failed: {e}")
        messages.error(request, f"Password change failed: {e}")
        return redirect('userSettingsPage')


