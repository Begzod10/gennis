# from backend.transfer.branch_location.reuqest import transfer_location, transfer_branch
# from backend.transfer.group.request import transfer_course_types
from backend.transfer.job.request import transfer_job,transfer_staffs,transfer_staffs_salary,transfer_staffs_list_salary
from backend.transfer.payments.request import transfer_payment_types
from backend.transfer.students.payments.request import transfer_students_Payment
from backend.transfer.students.request import transfer_students,transfer_deleted_students
# from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
from backend.transfer.teachers.request import transfer_teacher,transfer_teacher_branches
# from backend.transfer.user.request import transfer_users
# from language.request import transfer_language
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
# transfer_attendance_per_day()
# transfer_attendance_per_month()
# transfer_students_Payment()
# transfer_deleted_students()
# transfer_teacher_branches()
# transfer_staffs()
# transfer_staffs_salary()
transfer_staffs_list_salary()