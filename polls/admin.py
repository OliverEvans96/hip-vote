from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedTabularInline, NestedModelAdmin

from .models import Election, Contest, Candidate, Ranking

#class CandidateInline(admin.TabularInline):
class CandidateInline(NestedTabularInline):
    model = Candidate
    extra = 3

class ContestInline(NestedTabularInline):
    model = Contest
    extra = 3
    inlines = [CandidateInline]

#class ElectionAdmin(admin.ModelAdmin):
class ElectionAdmin(NestedModelAdmin):
    fieldsets = [
        (None, {'fields': ['election_name']}),
        ('Date Information', {'fields': ['open_date','close_date']})
    ]

    inlines = [ContestInline]

    list_display = ['election_name','open_date','close_date','is_currently_open']
    list_filter = ['open_date','close_date']
    search_fields = ['election_name']
    list_per_page = 10

admin.site.register(Election, ElectionAdmin)
