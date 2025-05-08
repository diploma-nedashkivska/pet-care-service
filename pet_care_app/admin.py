from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Pet)
admin.site.register(CalendarEvent)
admin.site.register(JournalEntry)
admin.site.register(SitePartner)
admin.site.register(ForumPost)
admin.site.register(ForumComment)
admin.site.register(ForumLike)