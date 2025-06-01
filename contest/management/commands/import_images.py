import os
from django.core.management.base import BaseCommand
from django.core.files import File
from contest.models import ImageEntry

class Command(BaseCommand):
    help = "Import all images from a folder into ImageEntry (using filename as name)"

    def add_arguments(self, parser):
        parser.add_argument(
            "folder",
            type=str,
            help="Path to the folder containing image files (jpg, png, gif, etc.)",
        )

    def handle(self, *args, **options):
        folder = options["folder"]
        if not os.path.isdir(folder):
            self.stderr.write(f"❌ ‘{folder}’ is not a valid directory.")
            return

        # Supported extensions; adjust if needed
        valid_exts = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff")

        files = os.listdir(folder)
        if not files:
            self.stdout.write(f"⚠️ Folder ‘{folder}’ is empty.")
            return

        imported = 0
        skipped = 0

        for filename in files:
            name_lower = filename.lower()
            if not name_lower.endswith(valid_exts):
                skipped += 1
                continue

            full_path = os.path.join(folder, filename)
            if not os.path.isfile(full_path):
                skipped += 1
                continue

            # Derive the ImageEntry.name from the filename without its extension
            base_name = os.path.splitext(filename)[0]

            # Check if an entry with the same image file already exists;
            # you can customize this check (by name, by path, etc.)
            if ImageEntry.objects.filter(image__icontains=filename).exists():
                self.stdout.write(f"• Skipping “{filename}” (already imported).")
                skipped += 1
                continue

            # Open the file and attach it to a new ImageEntry
            with open(full_path, "rb") as f:
                dj_file = File(f)
                entry = ImageEntry(name=base_name)
                # .save(<filename>, <File>, save=True) will copy the file into MEDIA_ROOT/contest_images/
                entry.image.save(filename, dj_file, save=True)
                # leave score at default (0) unless you want to set something else
                imported += 1
                self.stdout.write(self.style.SUCCESS(f"Imported “{filename}” as “{base_name}”"))

        self.stdout.write("")
        self.stdout.write(self.style.NOTICE(f"Done: Imported {imported} files. Skipped {skipped} non-image or duplicate files."))
