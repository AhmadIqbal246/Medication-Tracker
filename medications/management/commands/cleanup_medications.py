from django.core.management.base import BaseCommand
from django.utils import timezone
from medications.models import Medication
from datetime import timedelta

class Command(BaseCommand):
    help = 'Clean up old taken medications (older than specified days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete taken medications older than this many days (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_medications = Medication.objects.filter(
            status='taken',
            updated_at__lt=cutoff_date
        )
        
        count = old_medications.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No taken medications older than {days} days found.')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {count} taken medications older than {days} days:')
            )
            for med in old_medications[:10]:  # Show first 10
                self.stdout.write(f'  - {med.name} (taken: {med.updated_at.strftime("%Y-%m-%d")})')
            
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
            
            self.stdout.write('Run without --dry-run to actually delete these medications.')
        else:
            deleted_count = old_medications.count()
            old_medications.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Deleted {deleted_count} taken medications older than {days} days.')
            )
