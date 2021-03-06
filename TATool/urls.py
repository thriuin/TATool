"""TATool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from TAWeb.views import TASearchView, TAEvalView

urlpatterns = [
    path('', TASearchView.as_view()),
    path('ta/', TASearchView.as_view()),
    path('ta/search/', TASearchView.as_view(), name='TASearch'),
    path('ta/eval/', TAEvalView.as_view(), name='TAEval'),
]
# path('admin/', admin.site.urls),

"""
urlpatterns += i18n_patterns(
    path('search/', TASearchView.as_view(), name='TASearch'),
    path('eval/', TAEvalView.as_view(), name='TAEval'),
)
"""