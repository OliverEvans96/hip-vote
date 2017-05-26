import datetime
import copy
from py3votecore.schulze_method import SchulzeMethod
from py3votecore.condorcet import CondorcetHelper

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Election(models.Model):
    election_name = models.CharField(max_length=200)
    open_date = models.DateTimeField('polls open')
    close_date = models.DateTimeField('polls close')

    def __str__(self):
        return self.election_name

    def num_ballots(self):
        try:
            return max([len(contest.get_ballots()) for contest in self.contest_set.all()])
        except(ValueError,Ballot.DoesNotExist,Ranking.DoesNotExist):
            return 0

    def has_ballots(self):
        return self.num_ballots() > 0

    def is_currently_open(self):
        now = timezone.now()
        return self.open_date <= now <= self.close_date

    def is_over(self):
        now = timezone.now()
        return self.close_date <= now

    def get_user_ballots(self, user):
        """
        Return all ballots for this user
        """
        return [contest.ballot_set.get(user=user) for contest in self.contest_set.all()]

class Contest(models.Model):
    contest_name = models.CharField(max_length=200)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    # Number of stars in voting form for this contest
    num_stars = models.IntegerField(default=5)

    def sorted_candidates(self):
        return self.candidate_set.order_by('candidate_name')

    def num_candidates(self):
        return len(self.candidate_set.all())

    def has_ballots(self):
        return len(self.get_ballots()) > 0
    
    def num_meaningful_ballots(self):
        """
        Return number of ballots which are not abstain
        """
        num_ballots = sum(ballot['count'] for ballot in self.get_ballots()) 
        for ballot in self.ballot_set.all():
            if ballot.is_abstain():
                num_ballots -= 1

        return num_ballots

    def get_stars(self):
        return '*' * self.num_stars

    def run_schulze(self):
        # Only attempt if there are ballots
        if self.has_ballots():
            results = SchulzeMethod(
                self.get_ballots(),
                ballot_notation=CondorcetHelper.BALLOT_NOTATION_GROUPING
            ).as_dict()
        else:
            results = None
        return results

    def winner(self):
        if self.has_ballots():
            return self.run_schulze()['winner']

    def is_tied(self):
        try:
            _ = self.run_schulze()['tied_winners']
            return True
        except(KeyError):
            return False

    def tied_winners(self):
        if self.is_tied():
            return self.run_schulze()['tied_winners']

    def tied_winner_names(self):
        return ', '.join(winner.candidate_name for winner in self.tied_winners())
    
    def pairs(self):
        """ 
        dicts of dicts of pairwise comparisons
        Value of inner dict is a 2-tuple containing:
          - Number of voters preferring 
            1st candidate (1st dimension) over 2nd
          - Difference between number of voters 
            preferring 1st candidate and
            number of voters preferring 2nd candidate
            """
        if self.has_ballots():
            in_dict = self.run_schulze()['pairs']
            cans = self.sorted_candidates()
            out_dict = {can1:{
                can2:((
                    in_dict[(can1,can2)],
                    in_dict[(can1,can2)] - in_dict[(can2,can1)]
                )
                if can1 != can2 else '-') for can2 in cans}
                for can1 in cans}
            
            return out_dict

    def get_ballots(self):
        """
        Return list of dictionaries containing unique ballots (without user) and number of times they occurred
        """

        all_ballots = self.ballot_set.all()

        # Isolate unique ballots & count
        unique_ballots = []
        counts = []
        for ballot_object in all_ballots:
            ballot = ballot_object.get_ballot()
            if ballot in unique_ballots:
                index = unique_ballots.index(ballot)
                counts[index] += 1
            else:
                unique_ballots.append(ballot)
                counts.append(1)

        ballot_list = [{
            'ballot': ballot,
            'count': count
        } for ballot,count in zip(unique_ballots, counts)]

        return ballot_list

    def simple_ballot_list(self):
        """
        Return list of 2-tuples, each containing
            - ballot ordering string
            - # of times ballot occured
        """
        ballot_and_count = []
        for ballot in self.get_ballots():
            order_str = ' > '.join([' = '.join(c.candidate_name for c in lst) for lst in ballot['ballot']])
            ballot_and_count.append([order_str, ballot['count']])

        return ballot_and_count

    # Override save method to create 'None of the Above'
    # when contest is saved to database

#     def save(self, *args, **kwargs):
#         none_name = 'None of the Above'
#         try:
#             none_can = self.candidate_set.get(candidate_name=none_name)
#             new_can = False
#         except(Candidate.DoesNotExist):
#             none_can = Candidate(
#                 contest=self,
#                 candidate_name=none_name
#             )
#             new_can = True
#             print("NONE_CAN")
#             print("contest: {}".format(none_can.contest))
#             print("candidate_name: {}".format(none_can.candidate_name))
# 
#         super(Contest, self).save(*args, **kwargs)
#         if new_can:
#             none_can.save()

            
    def __str__(self):
        return self.contest_name

class Candidate(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=200)

    users = models.ManyToManyField(User, through='Ranking')

    def __str__(self):
        return self.candidate_name

    # Define comparison for candidates based on name
    def __gt__(self, other):
        return self.candidate_name > other.candidate_name 
    def __lt__(self, other):
        return self.candidate_name < other.candidate_name 

class Ranking(models.Model):
    """ 
    Associates a user and a candidate with a number of stars
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    # Number of stars the user gave to the candidate
    num_stars = models.IntegerField()
    
    def __str__(self):
        return str(self.user) + " -> " + str(self.candidate) + ": " + str(self.num_stars)

class Ballot(models.Model):
    """ 
    Associates a user and a contest with an ordered list of lists
    which ranks all candidates in order of preference
    If two candidates are tied, they are in the same list.
    Order of sublists is not relevant.
    If two candidates are not tied, they are in separate lists.
    """
    contest = models.ForeignKey(Contest, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def get_rankings(self):
        try:
            return [candidate.ranking_set.get(user=self.user) for candidate in self.contest.candidate_set.all()]
        except(Ranking.DoesNotExist):
            return None

    def get_ballot(self):
        # Rankings for this contest & user
        ranks = self.get_rankings()
        # Convert to ballot
        ballot = [[rank.candidate for rank in ranks if rank.num_stars == x] for x in range(self.contest.num_stars,0,-1)]
        # Remove empty lists (number of stars which user gave to nobody,
        # e.g. nobody got 4 stars, only 1,2,3,5.)
        # Have to count lists before removing (because that changes the number)
        # Remove in reverse order so as not to change indices before removing
        num_lsts = len(ballot)
        for ii,lst in enumerate(ballot[::-1]):
            if len(lst) == 0:
                ballot.pop(num_lsts-ii-1)

        # Sort each list
        ballot = [sorted(lst) for lst in ballot]

        return ballot

    def set_ballot(self,ballot):
        """
        Set rankings for associated user & contest based on preference list
        given in the same format as returned by get_ballot
        """
        
        # Check whether all candidates are present in ballot
        # If not, they should be assumed lower preference than those present
        candidates_present = [candidate for lst in ballot for candidate in lst]
        candidates_missing = [candidate for candidate in self.contest.candidate_set.all() if candidate not in candidates_present]

        # Determine minimum number of stars necessary in this contest 
        # required to apply this ballot
        min_stars = len(ballot)
        if len(candidates_missing) > 0:
            min_stars += 1

        # Cannot have more strict orderings in preference than stars available
        if min_stars > self.contest.num_stars:
            raise AttributeError("Ballot has {} strict orderings (assuming {} missing candidates less prefered), but contest only allows {} stars".format(min_stars ,len(candidates_missing), self.contest.num_stars))

        # Assign one star to missing candidates
        for candidate in candidates_missing:
            rank = candidate.ranking_set.get(user=self.user)
            rank.num_stars = 1
            rank.save()

        # Loop through list in reverse, assigning one star to lowest preference,
        # two stars to second group, etc.
        # Add one to all num_stars if anybody was missing from ballot
        for preference_level, candidate_group in enumerate(ballot[::-1]):
            for candidate in candidate_group:
                # Find ranking if it exists, otherwise create new ranking
                try:
                    rank = candidate.ranking_set.get(user=self.user)
                except(Ranking.DoesNotExist):
                    rank = Ranking(user=self.user, candidate=candidate,num_stars=0)
                # Add 1 because python counts from 0
                rank.num_stars = preference_level + 1
                # Add 1 more if missing candidates
                if len(candidates_missing) > 0:
                    rank.num_stars += 1
                rank.save()

    def is_abstain(self):
        """
        Determine if ballot is abstaining. 
        That is, it expresses no preference,
        so there is only a single sub-list.
        """
        return len(self.get_ballot()) == 1

    def get_order_str(self):
        order_str = ' > '.join([' = '.join(c.candidate_name for c in lst) for lst in self.get_ballot()])
        return order_str

    def __str__(self):
        order_str = self.get_order_str()
        return "{} for {}: {}".format(self.user.username, self.contest.contest_name, order_str)
