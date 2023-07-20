from teetimebot.models import User, Course, CourseSchedule, UserTeeTimeRequest, ForeUpUser
from datetime import date, datetime

class Search:

    @staticmethod
    def run():
        user_request = UserTeeTimeRequest.objects.select_related('course').prefetch_related('course__courseschedule_set').filter(
            date__gte= date.today(),
            status=UserTeeTimeRequest.Status.ACTIVE,
            )[0]
        
        print(user_request.date)
        print(f'tee_time_min: {user_request.tee_time_min}')
        print(f'tee_time_max: {user_request.tee_time_max}')
        print(user_request.course.name)
        print(user_request.course.courseschedule_set.all())

        today_date = date.today()
        print(today_date)
        if user_request.date >= today_date:
            while(True):
                Search.call_fourupsoftware(user_request)
                break


    @staticmethod
    def call_fourupsoftware(request_obj):
        print(request_obj.course.courseschedule_set.all())
        
        pass

        '''
        user = models.ForeignKey(User, on_delete=models.PROTECT)
        course = models.ForeignKey(Course, on_delete=models.PROTECT)
        date = models.DateField()
        tee_time_min = models.TimeField(default=None, null=True, blank=True)
        tee_time_max = models.TimeField(default=None, null=True, blank=True)
        players = models.IntegerField(choices=Players.choices, default=Players.ANY)
        holes = models.CharField(
            max_length=20,
            choices=Holes.choices,
            default=Holes.ANY,
        )
        status = models.CharField(
            max_length=20,
            choices=Status.choices,
            default=Status.INACTIVE,
        )
        '''
