from apps.applications.models import Application


def create_application_from_offering(*, student, program_offering, agent=None, notes=""):
    return Application.objects.create(
        student=student,
        agent=agent,
        program_offering=program_offering,
        tuition=program_offering.tuition,
        deposit=program_offering.deposit,
        notes=notes,
    )
