# from backend.transfer.group.request import transfer_course_types
# from backend.transfer.payments.request import transfer_payment_types
from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
# from backend.transfer.job.request import transfer_job
# from language.request import transfer_language
from backend.transfer.teachers.request import transfer_teacher
from backend.transfer.user.request import transfer_users
from login.request import login

login = login()

# transfer_course_types()
# transfer_payment_types()
# transfer_subjects()
# transfer_subject_levels(login)
# transfer_location()
# transfer_branch(login)
# transfer_language()
# transfer_job()
# transfer_users(login)
transfer_teacher()
