from datetime import datetime


def year(request):
    """Add current year for template."""
    return {'year': datetime.now().year}
