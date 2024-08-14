from backend.transfer.attendance.request import transfer_attendance_per_day, transfer_attendance_per_month
from backend.transfer.job.request import transfer_staffs, transfer_staffs_salary, \
    transfer_staffs_list_salary
from backend.transfer.students.payments.request import transfer_students_Payment
from backend.transfer.students.request import transfer_deleted_students
from backend.transfer.teachers.request import transfer_teacher_branches
from backend.transfer.user.request import transfer_user_groups
from login.request import login

login = login()
# transfer_attendance_per_month()
# transfer_attendance_per_day()

from backend.transfer.group.request import transfer_course_types
from backend.transfer.payments.request import transfer_payment_types
from backend.transfer.branch_location.reuqest import transfer_location, transfer_branch
from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
from backend.transfer.job.request import transfer_job
from language.request import transfer_language
from backend.transfer.teachers.request import transfer_teacher
from backend.transfer.user.request import transfer_users
from backend.transfer.overhead.request import transfer_overhead
from backend.transfer.students.request import transfer_students, transfer_students_history_group
from backend.transfer.group.request import transfer_group
from backend.transfer.rooms.request import transfer_rooms, transfer_room_subjects
from backend.transfer.time_table.request import transfer_group_time_table
from backend.transfer.capital.request import transfer_capital
from backend.transfer.book.request import transfer_book
from backend.transfer.attendance.request import transfer_attendance_per_day, transfer_attendance_per_month
from login.request import login

# login = login()
# transfer_book()
# transfer_attendance_per_month()
# transfer_attendance_per_day()
# transfer_capital()
# transfer_overhead(login)
# transfer_group()
# transfer_location()
# transfer_branch(login)
# transfer_course_types()
# transfer_payment_types()
# transfer_language()
# transfer_subjects()
# transfer_subject_levels(login)
# transfer_job()
# transfer_users(login)
# transfer_user_groups()
# transfer_teacher()
# transfer_students()

# transfer_attendance_per_day()
# transfer_attendance_per_month()
# transfer_students_Payment()
# transfer_deleted_students()
# transfer_teacher_branches()

# transfer_staffs()
# transfer_staffs_salary()
transfer_staffs_list_salary()

# transfer_group()
# transfer_rooms()
# transfer_room_subjects()
# transfer_group_time_table()
# transfer_students_history_group()
