#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    base_dir = Path(__file__).resolve().parent
    canonical_project_dir = base_dir / 'service_ia'
    sys.path.insert(0, str(canonical_project_dir))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    if len(sys.argv) == 2 and sys.argv[1] == 'runserver':
        sys.argv.append('127.0.0.1:8080')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
