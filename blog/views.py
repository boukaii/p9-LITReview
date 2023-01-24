from django.contrib.auth.decorators import login_required
from . import forms
from . import models
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from blog.models import UserFollows, Ticket, Review, User
from blog.forms import ReviewForm
from django.contrib import messages
from django.db.models import Q


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
        password1 = request.POST.get("password1")
        if password != password1:
            messages.error(request, "Les mots de passe fournit ne correspondent pas")
            return redirect('signup')
        user = User.objects.create_user(username=username, password=password1)
        messages.info(request, f"Création du compte {user.username} effectuée.")
        # auto-login user
        # login(request, user)
        # return redirect('login')
    return render(request, 'blog/signup.html')


@login_required
def flux(request):
    following = UserFollows.objects.filter(user__exact=request.user)
    tickets = models.Ticket.objects.filter(
        Q(user=request.user) | Q(user__id__in=following.values_list("followed_user"))
    )
    reviews = models.Review.objects.filter(
        Q(user=request.user) | Q(user__id__in=following.values_list("followed_user"))
    )
    print(tickets)
    return render(request, "blog/flux.html", context={'tickets': tickets, 'reviews': reviews})


@login_required
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


@login_required
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


@login_required
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


@login_required
def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.delete()
    return redirect('posts')


@login_required
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
    return render(request, 'blog/review.html', context)


@login_required
def review_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    form = forms.TicketForm(instance=ticket)
    title_page = f"Vous répondez au ticket {ticket.titre}"
    if request.method == 'POST':
        # if request.method == 'POST':
        form = forms.TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
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
        'test_form': form
    }
    return render(request, 'blog/review.html', context)


@login_required
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


@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    review.delete()
    return redirect('posts')


@login_required
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


@login_required
def follow_delete(request, id):
    followed_by = UserFollows.objects.filter(id=id).first()
    if followed_by:
        followed_by.delete()
    return redirect('follow')
