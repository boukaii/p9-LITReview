from django.contrib import admin
from django.urls import path
import blog.views
from django.contrib.auth.views import LoginView
from blog.views import home, create_ticket, posts, follow_view
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
    # Page d'accueil une fois connecter
    path('home/', home, name="home"),
    # Page pour créer un ticket
    path('ticket/', blog.views.create_ticket, name="ticket"),
    # Pour modifier un ticket
    path('<int:ticket_id>/ticket_change/', blog.views.ticket_change, name='ticket_change'),
    #Pour supprimer un ticket
    path('<int:ticket_id>/ticket_delete/', blog.views.ticket_delete, name='ticket_delete'),
    # Page pour suivre un utilisateur
    path('follow/', blog.views.follow_view, name='follow'),
    # Pour se désabonner d'un utilisateur
    path('<int:followed_by_id><int:following_id>/follow_delete/', blog.views.follow_delete, name='follow_delete'),
    #
    path('posts/', blog.views.posts, name='posts'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





# path('logout/', authentication.views.logout_user, name='logout'),
# path('home/', blog.views.home, name='home'),
# path('test', LoginView.as_view(
#         template_name='blog/login.html',
#         redirect_authenticated_user=True),
#         name='login'),