from django.contrib import admin
from .models import (
  Announcement, Attendance, Certificate, CompletionEvaluation, Content, Course,
  CourseApprovalRule, CourseCategory, CourseCompletion, CourseLesson,
  LessonCompletion, Mark, Offer, Profile, Registration, UserType,
)

# Register your models here.

admin.site.register(UserType)

class ProfileAdmin (admin.ModelAdmin):
  list_display = ('user', 'location', 'image', 'phone', 'description', 'userType', 'cv')
  list_filter = ('userType', 'location')
  search_fields = ('user', 'userType', 'location')
admin.site.register(Profile, ProfileAdmin)

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('detail', 'owner')
    search_fields = ('owner__username',)
admin.site.register(Announcement, AnnouncementAdmin)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'date', 'present')
    list_filter = ('student', 'date', 'present')
    search_fields = ('student__username', 'course__title')
admin.site.register(Attendance, AttendanceAdmin)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'comment', 'img', 'doc', 'videos')
    search_fields = ('title', 'comment')
admin.site.register(Content, ContentAdmin)

class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'modality', 'start_date', 'end_date', 'capacity', 'price', 'teacher', 'status')
    list_filter = ('category', 'modality', 'status', 'teacher')
    inlines = (CourseLessonInline,)
    search_fields = ('title', 'detail', 'teacher__username')
admin.site.register(Course, CourseAdmin)

class OfferAdmin(admin.ModelAdmin):
    list_display = ('price', 'detail', 'userType')
    list_filter = ('userType',)
    search_fields = ('detail', 'userType__category')
admin.site.register(Offer, OfferAdmin)

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'enabled')
    list_filter = ('enabled', 'student')
    search_fields = ('course__title', 'student__username') 
admin.site.register(Registration, RegistrationAdmin)

class MarkAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'mark_1', 'mark_2', 'mark_3', 'average')
    list_filter = ('course', 'student', 'average')  
    search_fields = ('student__username', 'course__title') 
admin.site.register(Mark, MarkAdmin)
admin.site.register(CourseCategory)
admin.site.register(CourseLesson)
admin.site.register(CourseApprovalRule)
admin.site.register(LessonCompletion)
admin.site.register(CourseCompletion)
admin.site.register(CompletionEvaluation)
admin.site.register(Certificate)
