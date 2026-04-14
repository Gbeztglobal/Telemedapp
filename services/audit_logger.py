from apps.accounts.models import AuditLog

def log_medical_action(user, action, module, details="", ip_address=None):
    """
    HIPAA-compliant audit logging utility.
    Tracks critical access and modification of Medical Records and PHI.
    """
    AuditLog.objects.create(
        user=user,
        action=action,
        module=module,
        details=details,
        ip_address=ip_address
    )
