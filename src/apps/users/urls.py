from rest_framework import routers

from apps.users.views import UserViewSet

app_name = 'apps.users'

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls
