from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Candidate, Contest, Election, Ranking, Ballot

# View all open elections
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'open_election_list'
    queryset = [election for election in Election.objects.all() if election.is_currently_open()]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['prev_election_list'] = [election for election in Election.objects.all() if election.is_over() or (self.request.user.is_staff and election.is_currently_open())]
        return context

class DetailView(generic.DetailView):
    model = Election
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Election.objects.all()

class ResultsView(generic.DetailView):
    model = Election
    template_name = 'polls/results.html'

class ConfirmView(generic.DetailView):
    model = Election
    template_name = 'polls/confirm.html'


def vote(request,pk):
    election = get_object_or_404(Election,pk=pk)
    try:
        election_vote_list = []
        for ii,contest in enumerate(election.contest_set.all()):
            contest_vote_list = []
            for jj,candidate in enumerate(contest.candidate_set.all()):
                rating = request.POST['group{}-{}'.format(ii,jj)]
                contest_vote_list.append(int(rating))
            election_vote_list.append(contest_vote_list)
    except(KeyError, Candidate.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'election': election,
            'error_message': "Please rate all candidates.",
        })
    else:
        # Create rating associating user & ratings
        for ii,contest in enumerate(election.contest_set.all()):
            for jj,candidate in enumerate(contest.candidate_set.all()):

                # Delete any previous ranking for this user & candidate
                # in this election, contest
                prev_ranks = candidate.ranking_set.filter(user=request.user)
                for rank in prev_ranks:
                    rank.delete()

                # Get the ranking being currently submitted
                ranking = Ranking(user=request.user, candidate=candidate, num_stars = election_vote_list[ii][jj])
                
                # Save current ranking
                ranking.save()

            # Create ballot for user if it doesn't already exists
            try:
                ballot = contest.ballot_set.get(user=request.user)
            except(Ballot.DoesNotExist):
                ballot = Ballot(user=request.user, contest=contest)
                ballot.save()

        ballot_strs = [ballot.get_order_str() for ballot in election.get_user_ballots(request.user)]
        return render(request, 'polls/confirm.html', {
            'election': election,
            'contests_and_ballots': zip(election.contest_set.all(),ballot_strs),
         })

