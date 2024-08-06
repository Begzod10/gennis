# from backend.transfer.group.request import transfer_course_types
# from backend.transfer.payments.request import transfer_payment_types
# from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
# from backend.transfer.branch_location.reuqest import transfer_location, transfer_branch
# from language.request import transfer_language
from backend.transfer.user.request import transfer_users

from login.request import login
from group.request import transfer_group
login = login()

transfer_users(login)
transfer_group()
# transfer_location()
# transfer_branch(login)
# transfer_language()
