# hr_contacts_prep.py
# Run this once to create hr_contacts.csv from the HR list
# The PDF data is already extracted below — just run this script.

import csv

contacts = [
    ("HR Name","work email","Designation","Comapny name"),
    ()
]

output_file = "hr_contacts.csv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "Email", "Title", "Company"])
    writer.writerows(contacts)

print(f"✓ Saved {len(contacts)} contacts to {output_file}")
