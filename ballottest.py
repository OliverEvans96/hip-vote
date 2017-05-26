# coding: utf-8
from polls.models import Election, Contest, Candidate, Ranking, Ballot
from django.contrib.auth.models import User
e1 = Election.objects.all()[0]
c1 = e1.contest_set.all()[0]
u =User.objects.get(username='oliver')
b = Ballot(contest=c1,user=u)
