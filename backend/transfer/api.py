# from backend.transfer.group.request import transfer_course_types
# from backend.transfer.payments.request import transfer_payment_types
# from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
# from backend.transfer.branch_location.reuqest import transfer_location, transfer_branch
# from backend.transfer.language.request import transfer_language
# from backend.transfer.user.request import transfer_users
# from backend.transfer.job.request import transfer_job
# from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
# from backend.transfer.job.request import transfer_job
# from language.request import transfer_language
# from backend.transfer.teachers.request import transfer_teacher
# from backend.transfer.user.request import transfer_users
# from backend.transfer.students.request import transfer_student
from backend.transfer.group.request import transfer_group
from backend.transfer.rooms.request import transfer_rooms, transfer_room_subjects, transfer_room_images
from backend.transfer.time_table.request import transfer_group_time_table
from backend.transfer.attendance.request import transfer_attendance_per_day, transfer_attendance_per_month
from login.request import login

login = login()

# transfer_location()
# transfer_branch(login)
# transfer_course_types()
# transfer_payment_types()
# transfer_language()
# transfer_subjects()
# transfer_subject_levels(login)
# transfer_job()
# transfer_users(login)
# transfer_teacher()
# transfer_students()
# transfer_group()
# transfer_attendance_per_day()
transfer_attendance_per_month()
transfer_rooms()
transfer_room_subjects()

transfer_group_time_table()
