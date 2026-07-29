from django.urls import path, include
from rest_framework import routers
from .views import UserTypeViewSet, ProfileViewSet, OfferViewSet, AnnouncementViewSet, ContentViewSet, CourseViewSet, RegistrationViewSet, AttendanceViewSet, MarkViewSet, CurrentUserView, LoginView, LogoutView, RegisterView

router = routers.DefaultRouter()

router.register (r'usertype', UserTypeViewSet)
router.register (r'profile', ProfileViewSet)
router.register (r'offer', OfferViewSet)
router.register (r'Announcement', AnnouncementViewSet)
router.register (r'content', ContentViewSet)
router.register (r'course', CourseViewSet)
router.register (r'registration', RegistrationViewSet)
router.register (r'attendance', AttendanceViewSet)
router.register (r'mark', MarkViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', CurrentUserView.as_view(), name='auth-current-user'),
    path ('', include(router.urls)),
]

