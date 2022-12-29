from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout, get_user_model
from . import forms
from django.contrib.auth.decorators import login_required
from . import models
from django.views.generic import View
from django.conf import settings
from django.shortcuts import get_object_or_404
from blog.models import UserFollows, Ticket, Review, User
from blog.forms import TicketForm
from django.contrib import messages
from django.db.models.fields import CharField
from django.db.models import Value, Q
from itertools import chain


def login_page(request):
    form = forms.LoginForm()
    message = ''
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('home')

        message = 'Identifiants invalides.'
    return render(
        request, 'blog/login.html', context={'form': form, 'message': message})


def logout_user(request):
    logout(request)
    return redirect('login')


User = get_user_model()


def signup_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.create_user(username=username, password=password)
        # auto-login user
        login(request, user)
        return redirect('login')
    return render(request, 'blog/signup.html')


def create_ticket(request):
    form = forms.TicketForm()
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect("posts")
    return render(request, 'blog/ticket.html', context={'form': form})


def ticket_change(request, ticket_id):
    title_page = f"Modification du ticket {ticket_id}"
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket_form = TicketForm(instance=ticket)
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket.title = ticket_form.cleaned_data['title']
            ticket.description = ticket_form.cleaned_data['description']
            if ticket_form.cleaned_data['image']:
                ticket.image = ticket_form.cleaned_data['image']
            ticket.save()
            return redirect('posts')
    context = {
        'title_page': title_page,
        'ticket_form': ticket_form,
        'ticket': ticket
    }
    return render(request, 'blog/posts.html', context)


def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.delete()
    return redirect('posts')


def home(request):
    photos = models.Ticket.objects.all()
    return render(request, 'blog/home.html', context={'photo': photos})


def posts(request):
    title = "Posts"
    current_user = request.user
    tickets = Ticket.objects.filter(user=current_user)
    for ticket in tickets:
        print(ticket.image)
    reviews = Review.objects.filter(user=current_user)
    context = {"title": title,
               "tickets": tickets,
               "reviews": reviews,
               "current_user": current_user,
               }
    return render(request, "blog/posts.html", context)


def follow_view(request):
    page_title = 'Abonnements'
    followed_by = UserFollows.objects.filter(user=request.user)
    following = UserFollows.objects.filter(followed_user=request.user)

    if request.method == 'POST':
        follow_user = request.POST.get('follow_user')
        if follow_user == request.user.username:
            messages.error(request, "Vous ne pouvez pas vous abonner à vous-même")
            return redirect('follow')

        existing_user = User.objects.filter(username=follow_user)

        if existing_user:
            existing_user = User.objects.get(username=follow_user)
            try:
                user_follows = UserFollows(user=request.user, followed_user=existing_user)
                user_follows.save()
                messages.info(request, f"Vous êtes abonnés à {existing_user.username}")
            except:
                messages.error(request, "Vous êtes déjà abonnés à cet utilisateur")
                return redirect('follow')
        else:
            messages.error(request, "Le nom de l'utilisateur demandé n'existe pas")
            return redirect('follow')

    context = {
        'title_page': page_title,
        'followed_by': followed_by,
        'following': following,
    }
    return render(request, 'blog/follow.html', context)


def follow_delete(request, followed_by_id, following_id):
    followed_by = UserFollows.objects.filter(user_id=following_id, followed_user_id=followed_by_id)
    if followed_by:
        followed_by = UserFollows.objects.get(user_id=following_id, followed_user_id=followed_by_id)
        followed_by.delete()
    return redirect('follow')

