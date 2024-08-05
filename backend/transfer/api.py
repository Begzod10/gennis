# from backend.transfer.group.request import transfer_course_types
# from backend.transfer.payments.request import transfer_payment_types
from backend.transfer.subjects.request import transfer_subjects, transfer_subject_levels
# from backend.transfer.branch_location.reuqest import transfer_location, transfer_branch
from login.request import login

login = login()
# transfer_location()
# transfer_branch(login)
transfer_subject_levels(login)

