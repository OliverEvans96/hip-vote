import datetime
import IPython

from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Election, Contest, Candidate, Ranking, Ballot


# class QuestionMethodTests(TestCase):
# 
#     def test_was_published_recently_with_future_question(self):
#         """
#         was_published_recently() should return False for questions
#         whose pub_date is in the future
#         """
# 
#         time = timezone.now() + datetime.timedelta(days=30)
#         future_question = Question(pub_date = time)
#         self.assertIs(future_question.was_published_recently(),False)
# 
#     def test_was_published_recently_with_old_question(self):
#         """
#         was_published_recently() should return False for questions whose
#         pub_date is older than 1 day.
#         """
#         time = timezone.now() - datetime.timedelta(days=30)
#         old_question = Question(pub_date=time)
#         self.assertIs(old_question.was_published_recently(), False)
# 
#     def test_was_published_recently_with_recent_question(self):
#         """
#         was_published_recently() should return True for questions whose
#         pub_date is within the last day.
#         """
#         time = timezone.now() - datetime.timedelta(hours=1)
#         recent_question = Question(pub_date=time)
#         self.assertIs(recent_question.was_published_recently(), True)

def create_test_user(name):
    return User.objects.create_user(name, '{}@example.com'.format(name), 'password')

def submit_ballots(contest, ballot, user_list):
    """
    Submit identical ballots to contest on behalf of all users in user_list
    """

    for user in user_list:
        # Get ballot for this user in this contest if it exists
        try:
            ballot_object = contest.ballot_set.get(user=user)
        except(Ballot.DoesNotExist):
            ballot_object = Ballot(user=user, contest=contest)
        ballot_object.set_ballot(ballot)
        ballot_object.save()

class SchulzeMethodTests(StaticLiveServerTestCase):

    def test_wikipedia_example(self):
        """ Schulze example from Wikipedia:
        https://en.wikipedia.org/wiki/Schulze_method#Example
        """

        # Create 45 users
        voters = []
        for ii in range(45):
            voters.append(create_test_user('voter{}'.format(ii)))

        # Create election w/ 1 contest
        election = Election(
            open_date=timezone.now()-datetime.timedelta(days=1),
            close_date=timezone.now()+datetime.timedelta(days=1),
            election_name='Test election'
        )
        election.save()
        contest = Contest(
            contest_name='Test contest',
            election=election
        )
        contest.save()

        # Create 5 candidates named by letters
        num_candidates = 5
        candidate_names = 'ABCDE'

        candidates = {}
        candidates['A'] = Candidate(
            contest=contest,
            candidate_name='A'
        )
        candidates['A'].save()

        candidates['B'] = Candidate(
            contest=contest,
            candidate_name='B'
        )
        candidates['B'].save()

        candidates['C'] = Candidate(
            contest=contest,
            candidate_name='C'
        )
        candidates['C'].save()

        candidates['D'] = Candidate(
            contest=contest,
            candidate_name='D'
        )
        candidates['D'].save()

        candidates['E'] = Candidate(
            contest=contest,
            candidate_name='E'
        )
        candidates['E'].save()

        # Easily readable list of ballots & number of votes
        readable_ballots = [
            [5, 'ACBED'],
            [5, 'ADECB'],
            [8, 'BEDAC'],
            [3, 'CABED'],
            [7, 'CAEBD'],
            [2, 'CBADE'],
            [7, 'DCEBA'],
            [8, 'EBADC'],
        ]

        # Number of users who have voted
        users_voted = 0
        for num_votes,ballot_str in readable_ballots:
            ballot = [[candidates[letter]] for letter in ballot_str]
            user_list = voters[users_voted:users_voted+num_votes]
            submit_ballots(contest, ballot, user_list)
            users_voted += num_votes

        # Run Schulze method
        results = contest.run_schulze()

        # Define expected results
        winner = 'E'
        pairwise_preference = [
            [None,20,26,30,22],
            [25,None,16,33,18],
            [19,29,None,17,24],
            [15,12,28,None,14],
            [23,27,21,31,None],
        ]
       
        # Check winner
        self.assertEqual(results['winner'],candidates['E'])

        # Check whether pairwise comparison matches preference
        for n1 in range(num_candidates):
            for n2 in range(num_candidates):
                if n1 == n2:
                    continue

                c1 = candidates[candidate_names[n1]]
                c2 = candidates[candidate_names[n2]]

                self.assertEqual(
                    results['pairs'][(c1,c2)],
                    pairwise_preference[n1][n2]
                )

        IPython.embed()

