from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout, get_user_model
from . import forms
from django.contrib.auth.decorators import login_required
from . import models
from django.views.generic import View
from django.conf import settings
from django.shortcuts import get_object_or_404
from blog.models import UserFollows, Ticket, Review, User
from blog.forms import TicketForm, ReviewForm
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
                return redirect('flux')

        message = 'Identifiants invalides.'
    return render(
        request, 'blog/login.html', context={'form': form, 'message': message})


def logout_user(request):
    logout(request)
    return redirect('login')


def signup_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.create_user(username=username, password=password)
        # auto-login user
        login(request, user)
        return redirect('login')
    return render(request, 'blog/signup.html')


def flux(request):
    tickets = models.Ticket.objects.filter(user=request.user)
    tickets = tickets.annotate(contente_type=Value('TICKET', CharField()))

    reviews = models.Review.objects.filter(user=request.user)
    reviews = reviews.annotate(contente_type=Value('REVIEW', CharField()))

    posts = sorted(chain(tickets, reviews), key=lambda x: x.time_created, reverse=True)
    return render(request, 'blog/flux.html', context={'posts': posts})


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


def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    form = forms.TicketForm(instance=ticket)
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('posts')
    context = {'edit_form': form, 'ticket': ticket}

    return render(request, 'blog/ticket_edit.html', context)


def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.delete()
    return redirect('posts')


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


def follow_delete(request, id):
    followed_by = UserFollows.objects.filter(id=id).first()
    if followed_by:
        followed_by.delete()
    return redirect('follow')


def create_review(request):
    title = "Créer une review"
    if request.method == "POST":
        try:
            ticket_instance = Ticket.objects.create(
                                    title=request.POST['titre'],
                                    description=request.POST['description'],
                                    image=request.FILES['image'],
                                    user=request.user
                                    )
            Review.objects.create(ticket=ticket_instance,
                                  headline=request.POST['headline'],
                                  rating=request.POST['rating'],
                                  body=request.POST['body'],
                                  user=request.user
                                  )
        except Exception:
            print('titi')
            form_review = ReviewForm(request.POST)
            form_ticket = TicketForm(request.POST)
        else:
            print('toto')
            messages.success(request, 'Review créée !')
            return redirect("posts")
    else:
        print("tratra")
        form_review = ReviewForm()
        form_ticket = TicketForm()
        return render(request, 'blog/review.html', {'title': title, 'form_review': form_review, 'form_ticket': form_ticket})


def review_response_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    title_page = f"Vous répondez au ticket {ticket.titre}"
    if request.method == 'POST':
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.rating = review_form.cleaned_data['rating']
            review.headline = review_form.cleaned_data['headline']
            review.body = review_form.cleaned_data['body']
            review.save()
            return redirect('flux')
    else:
        review_form = ReviewForm()

    context = {
        'title_page': title_page,
        'review_form': review_form,
        'ticket': ticket,
    }

    return render(request, 'blog/review_response_ticket.html', context)






# User = get_user_model()


# def home(request):
#     photos = models.Ticket.objects.all()
#     return render(request, 'blog/home.html', context={'photo': photos})


