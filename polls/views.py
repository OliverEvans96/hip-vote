from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Candidate, Contest, Election

# View all open elections
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'open_election_list'

    def get_queryset(self):
        return [election for election in Election.objects.all() if election.is_currently_open()]

# Open up one election to vote on
class DetailView(generic.DetailView):
    model = Election
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Election.objects.all()

class ResultsView(generic.DetailView):
    model = Election
    template_name = 'polls/results.html'

def vote(request,pk):
    election = get_object_or_404(Election,pk=pk)
    try:
        selected_candidate = election.candidate_set.get(
                pk=request.POST['candidate'])
    except(KeyError, Candidate.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'election': election,
            'error_message': "You didn't select a candidate.",
        })
    else:
        selected_candidate.votes += 1
        selected_candidate.save()
        return HttpResponseRedirect(reverse('polls:results', args=(election.id,)))
