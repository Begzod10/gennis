from backend.transfer.group.request import transfer_course_types
from backend.transfer.payments.request import transfer_payment_types

from backend.transfer.branch_location.reuqest import transfer_location, transfer_branch
from backend.transfer.language.request import transfer_language

from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
from backend.transfer.job.request import transfer_job
from backend.transfer.teachers.request import transfer_teacher
from backend.transfer.user.request import transfer_users
from backend.transfer.students.request import transfer_students
from login.request import login
from group.request import transfer_group

login = login()


# transfer_location()
# transfer_branch(login)
# transfer_course_types()
# transfer_payment_types()
# transfer_language()
# transfer_subjects()
# transfer_subject_levels(login)
# transfer_job()
transfer_users(login)
transfer_teacher()
transfer_students()
# transfer_group()