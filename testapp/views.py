from django.shortcuts import render
from django.views import generic

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'testapp/index.html'
    context_object_name = 'test_list'

    def get_queryset(request):
        return [1,2,3]

