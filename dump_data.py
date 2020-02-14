import os
import re
import json

from fnmatch import fnmatch
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

# Where can we find our source files? 
folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
files = os.listdir(folder)
file_pattern = '*.pdf'

# Define some patterns to look for in the data stream
leadership_roles = ['Cubmaster', 'Committee Member', 'Chartered Organization Rep.', 'Committee Chairman',
                    'Assistant Cubmaster', 'Tiger Adult Partner', 'Den Leader', 'Parent Coordinator', 'Webelos Leader',
                    'Tiger Den Leader', 'Pack Trainer']
ranks = ['Bobcat', 'Tiger', 'Wolf', 'Bear', 'Webelos', 'Arrow of Light']
cities = ['Toronto']
provinces = ['Ontartio']
countries = ['Canada']
genders = ['F', 'M']
digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

table_header = re.compile(r"\s+(?:-+ +-+)+")
bsa_id_number = re.compile(r"^\d{7,9}$")
certification_date = re.compile(r"^Youth Protect\.\(Y01\) Completed Date:(?: \d{2}/\d{2}/\d{4})?")
phone_number = re.compile(r"^[BHMW] (?:\(\d{3}\) )?\d{3}\-\d{4}")
name_and_street = re.compile(r"^[A-Za-z].+(?:PO Box \d+|\d{2,}\b.*\b(?:St|Ln|Ave|Pl|Dr|Rd|Ter|E|NE|NW)\b.*)")
street_address = re.compile(r"^(?:PO Box \d+|\d{2,}\b.*\b(?:St|Ln|Ave|Pl|Dr|Rd|Ter|E|NE|NW)\b.*|The Highlands)")
street_2 = re.compile(r"^(?:APT|Apt|#)")
city_state = re.compile(r"(?:\w+\s)*\w+, [MW]A\b")
zip_code = re.compile(r"^(?:\d{5}\-?(?:\d{4})?|\w\d\w\-\d\w\d)")
zip_plus_4 = re.compile(r"^\d{4}$")
school_grade = re.compile(r"^(?:[1-9]|10|11|12)$")
birthdate = re.compile(r"^\d{2}/\d{2}$")
status = re.compile(r"^[MNRST]$")
magazine_subscription = re.compile(r"^[NI]$")
continuation = re.compile(r"^\s{3,}\w")  # Identify a continuing line or a new record based on indentation

members = []

# Read in the source PDF files
for file in files:
    if fnmatch(file, file_pattern):
        members = []
        member_count = 0
        marker_count = 0
        print()
        print(f"{file}")
        print("------------------------------------------------------------------------------------------------------")
        output = StringIO()
        write_next = False
        with open(os.path.join(folder, file), 'rb') as pdf:
            extract_text_to_fp(pdf, output, laparams=LAParams(boxes_flow=0.5), output_type='text', codec=None)
        recording = False
        for line in output.getvalue().splitlines():
            if re.match(table_header, line):
                recording = True
                new_member = True
            elif line == '':
                recording = False
            elif recording:
                if new_member:
                    members.append([i.strip() for i in line.split('  ') if i])
                    marker_count = 1
                    new_member = False
                elif re.match(continuation, line):
                    [members[-1].append(i.strip()) for i in line.split('  ') if i]
                    marker_count = 0
                elif marker_count:
                    marker_count += 1
                    [members[-1].append(i.strip()) for i in line.split('  ') if i]
                else:
                    members.append([i.strip() for i in line.split('  ') if i])
                    marker_count += 1

        for idx, member in enumerate(members):
            member_dict = {}
            for i in member:
                if re.match(name_and_street, i):
                    member_dict['name'] = i[0:25]
                    member_dict['address'] = {'street': i[26:]}
                elif re.match(street_address, i):
                    member_dict['address'] = {'street': i}
                elif i in ranks:
                    member_dict['rank'] = i
                elif re.match(status, i):
                    if 'status' not in member_dict:
                        member_dict['status'] = i
                    elif i == 'N':
                        member_dict['boys_life'] = i
                    elif i == 'M':
                        member_dict['gender'] = i
                elif re.match(magazine_subscription, i):
                    member_dict['boys_life'] = i
                elif re.match(birthdate, i):
                    member_dict['birthdate'] = i
                elif re.match(school_grade, i):
                    member_dict['grade'] = i
                elif i in genders:
                    member_dict['gender'] = i
                elif re.match(phone_number, i):
                    t, n = i.split(' ', 1)
                    if '(' not in n:
                        n = '(206) ' + n
                    member_dict['phone'] = {'type': t, 'number': n }
                elif re.match(bsa_id_number, i):
                    member_dict['bsa_id'] = i
                elif re.match(street_2, i):
                    member_dict['address']['street2'] = i
                elif re.match(city_state, i):
                    member_dict['address']['city'], member_dict['address']['state'] = i.split(', ')
                elif i in cities:
                    member_dict['address']['city'] = i
                elif i in provinces:
                    member_dict['address']['state'] = i
                elif i in countries:
                    member_dict['address']['country'] = i
                elif re.match(zip_code, i):
                    member_dict['address']['zip_code'] = i.rstrip('-')
                elif re.match(zip_plus_4, i):
                    member_dict['address']['zip_code'] = member_dict['address']['zip_code'] + '-' + i

                elif i in leadership_roles:
                    member_dict['role'] = i
                elif re.match(certification_date, i):
                    member_dict['bsa_cert_date'] = i.split(':')[-1].strip() if i.split(':')[-1].strip() else None
                else:
                    if 'name' in member_dict:
                        member_dict['name'] += f" {i}" if not member_dict['name'][-1] == '-' else i
                    else:
                        member_dict['name'] = i
            print(member_dict)
            members[idx] = member_dict

        json_file = file.split()[0] + '.json'
        with open(os.path.join(folder, json_file), 'w') as fout:
            json.dump(members, fout, indent=4, sort_keys=True)
        output.close()
