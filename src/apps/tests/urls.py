from rest_framework import routers

from apps.tests.views import TestViewSet

app_name = 'apps.tests'

router = routers.SimpleRouter()
router.register(r'tests', TestViewSet)

urlpatterns = router.urls
