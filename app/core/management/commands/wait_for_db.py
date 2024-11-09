from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as psycopg2OpError
from django.db.utils import OperationalError
from django.conf import settings


class Command(BaseCommand):
    help = 'Wait for the database to become available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_up = False
        max_attempts = 30  # Number of attempts to check the database
        attempt = 0

        while not db_up and attempt < max_attempts:
            try:
                self.check(databases=['default'])
                db_up = True
            except (psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
                attempt += 1

        if db_up:
            self.stdout.write(self.style.SUCCESS('Database available!'))
        else:
            self.stdout.write(self.style.ERROR('Database is still unavailable after waiting.'))
            exit(1)  # Exit with an error code if the database is still unavailable
