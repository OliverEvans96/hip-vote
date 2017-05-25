import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Election(models.Model):
    election_name = models.CharField(max_length=200)
    open_date = models.DateTimeField('polls open')
    close_date = models.DateTimeField('polls close')
    open_now = models.BooleanField(default=True)

    def __str__(self):
        return self.election_name

    def is_currently_open(self):
        now = timezone.now()
        self.open_now = (self.open_date <= now <= self.close_date)
        return self.open_now

class Contest(models.Model):
    contest_name = models.CharField(max_length=200)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    def __str__(self):
        return self.contest_name

class Candidate(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    candidate_name = models.CharField(max_length=200)

    users = models.ManyToManyField(User, through='Ranking')

    def __str__(self):
        return self.candidate_name

class Ranking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    # Number of stars the user gave to the candidate
    num_stars = models.IntegerField()
    
    def __str__():
        return str(user) + " -> " + str(candidate) + ": " + str(num_stars)

