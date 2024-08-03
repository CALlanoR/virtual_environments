import csv
import re

grep -Ev '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' example3.csv

uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

with open('example2.csv', newline='') as f:
    reader = csv.reader(f)
    firts_row = next(reader)

if len(firts_row) == 1:
    pattern = re.compile(uuid_pattern)
    if re.fullmatch(pattern, firts_row[0]):
        print("hace match")
    else:
        print("no hace match")
else:
    print("no hace match multiples columnas")

import re
regex = re.compile(uuid_pattern)
with open("my_file.txt") as f:
    for line in f:
        result = regex.search(line)

for match in re.finditer('^((?!42).)*$', s, flags=re.M):
    print(match)