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
    following = UserFollows.objects.filter(user__exact=request.user)
    tickets = models.Ticket.objects.filter(
        Q(user=request.user) | Q(user__id__in=following.values_list("followed_user"))
    )
    # reviews = models.Review.objects.filter(
    #     Q(user=request.user) | Q(user__id__in=following.values_list("followed_user"))
    # )
    #
    # tickets = tickets.annotate(contente_type=Value("TICKET", CharField()))
    # reviews = reviews.annotate(contente_type=Value("REVIEW", CharField()))
    print(tickets)
    # posts = sorted(chain(tickets, reviews), key=lambda x: x.time_created, reverse=True)
    return render(request, "blog/flux.html", context={'tickets': tickets})


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


def create_review(request):
    ticket_form = forms.TicketForm()
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        review_form = forms.ReviewForm(request.POST)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            if ticket_form.cleaned_data['image']:
                ticket.image = ticket_form.cleaned_data['image']
            ticket.has_review = True
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = get_object_or_404(models.Ticket, id=ticket.id)
            review.save()
            return redirect('posts')
    context = {
        'ticket': True,
        'ticket_form': ticket_form,
        'review_form': review_form
    }
    return render(
        request,
        'blog/review.html',
        context
    )


def review_ticket(request, ticket_id):
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
            return redirect('posts')
    else:
        review_form = ReviewForm()

    context = {
        'title_page': title_page,
        'review_form': review_form,
        'ticket': ticket,
    }

    return render(request, 'blog/review.html', context)


def review_edit(request, review_id):
    review = get_object_or_404(models.Review, id=review_id)
    form = forms.ReviewForm(instance=review)
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('posts')
    context = {'edit_form': form, 'review': review}

    return render(request, 'blog/review_edit.html', context)


def review_delete(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    review.delete()
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



# User = get_user_model()


# def home(request):
#     photos = models.Ticket.objects.all()
#     return render(request, 'blog/home.html', context={'photo': photos})


# def flux(request):
#     tickets = models.Ticket.objects.filter(Q(user=request.user))
#     tickets = tickets.annotate(contente_type=Value('TICKET', CharField()))
#
#     reviews = models.Review.objects.filter(Q(user=request.user))
#     reviews = reviews.annotate(contente_type=Value('REVIEW', CharField()))
#
#     post = sorted(chain(tickets, reviews), key=lambda x: x.time_created, reverse=True)
#     return render(request, 'blog/flux.html', context={'posts': post})