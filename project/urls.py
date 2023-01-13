from django.contrib import admin
from django.urls import path
import blog.views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # Pour se connecter
    path('login', blog.views.login_page, name="login"),
    # Pour se déconnecter
    path('logout', blog.views.logout_user, name='logout'),
    # Pour s'inscrire
    path('signup/', blog.views.signup_page, name='signup'),

    # Page d'accueil une fois connecter et qui contient tout le contenue crées par les autres utlisateurs
    path('flux/', blog.views.flux, name="flux"),
    # Page qui affiche ses propres critiques et tickets
    path('posts/', blog.views.posts, name='posts'),

    # Page pour créer un ticket
    path('ticket/', blog.views.create_ticket, name="ticket"),
    # Pour modifier un ticket
    path('<int:ticket_id>/ticket_edit/', blog.views.ticket_edit, name='ticket_edit'),
    #Pour supprimer un ticket
    path('<int:ticket_id>/ticket_delete/', blog.views.ticket_delete, name='ticket_delete'),

    # Page pour créer une critique
    path('review/', blog.views.create_review, name="review"),
    # Page pour créer une critique en fonction d'un ticket
    path('<int:ticket_id>/review_ticket/', blog.views.review_ticket, name='review_ticket'),
    # Page pour modifier une critique
    path('<int:review_id>/review_edit/', blog.views.review_edit, name="review_edit"),
    # Page pour supprimer une critique
    path('<int:review_id>/review_delete/', blog.views.review_delete, name="review_delete"),

    # Page pour suivre un utilisateur
    path('follow/', blog.views.follow_view, name='follow'),
    # Pour se désabonner d'un utilisateur
    path('<int:id>/follow_delete/', blog.views.follow_delete, name='follow_delete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
