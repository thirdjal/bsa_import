import json
import os
import settings

from fnmatch import fnmatch

members = {}

# Read in the source json files
for file in settings.json_files:
    if fnmatch(file, settings.json_file_pattern) and not file == settings.combined_json_file:
        year = file.split(' ', 1)[0]
        with open(os.path.join(settings.output_folder, file)) as json_file:
            json_data = json.load(json_file)
        print(f"Found {len(json_data)} entries in {json_file.name}.")
        for member in json_data:
            if member['bsa_id'] in members:
                print(f"Updating {member['name']}...")
                members[member['bsa_id']]['years'][year] = {
                    'status': member['status'],
                }
                if 'role' in member:
                    members[member['bsa_id']]['years'][year]['role'] = member['role']
                    members[member['bsa_id']]['years'][year]['compliance'] = member['bsa_cert_date']
                else:
                    members[member['bsa_id']]['years'][year]['rank'] = member['rank'] if 'rank' in member else None
                if 'address' in member:
                    address = next((a for a in members[member['bsa_id']]['addresses'] if
                                  a['street'] == member['address']['street']), None)
                    if address:
                        address['years'].append(year)
                    else:
                        members[member['bsa_id']]['addresses'].append(
                            {
                                'street': member['address']['street'],
                                'street2': member['address']['street2'] if 'street2' in member['address'] else None,
                                'city': member['address']['city'],
                                'state': member['address']['state'],
                                'zip': member['address']['zip_code'],
                                'country': member['address']['country'] if 'country' in member[
                                    'address'] else 'United States',
                                'years': [year],
                            },
                        )
                if 'phone' in member:
                    phone = next((p for p in members[member['bsa_id']]['phone_numbers'] if p['number'] == member['phone']['number']), None)
                    if phone:
                        phone['years'].append(year)
                    else:
                        members[member['bsa_id']]['phone_numbers'].append(
                            {
                                'type': member['phone']['type'] if 'phone' in member else None,
                                'number': member['phone']['number'] if 'phone' in member else None,
                                'years': [year],
                            }
                        )

            else:
                print(f"Adding {member['name']}...")
                members[member['bsa_id']] = {
                    'name': member['name'],
                    'gender': member['gender'],
                    'birth_date': member['birthdate'] if 'birthdate' in member else None,
                    'years': {year: {
                        'status': member['status'],
                    },
                    },
                    'phone_numbers': [
                        {
                            'type': member['phone']['type'] if 'phone' in member else None,
                            'number': member['phone']['number'] if 'phone' in member else None,
                            'years': [year],
                        }
                    ],
                }
                if 'role' in member:
                    members[member['bsa_id']]['years'][year]['role'] = member['role']
                    members[member['bsa_id']]['years'][year]['compliance'] = member['bsa_cert_date']
                else:
                    members[member['bsa_id']]['years'][year]['rank'] = member['rank'] if 'rank' in member else None

                if 'address' in member:
                    members[member['bsa_id']]['addresses'] = [
                                                                 {
                                                                     'street': member['address']['street'],
                                                                     'street2': member['address'][
                                                                         'street2'] if 'street2' in member[
                                                                         'address'] else None,
                                                                     'city': member['address']['city'],
                                                                     'state': member['address']['state'],
                                                                     'zip': member['address']['zip_code'],
                                                                     'country': member['address'][
                                                                         'country'] if 'country' in member[
                                                                         'address'] else 'United States',
                                                                     'years': [year],
                                                                 }
                                                             ]
                else:
                    members[member['bsa_id']]['addresses'] = [
                                                                 {
                                                                     'street': None,
                                                                     'street2': None,
                                                                     'city': None,
                                                                     'state': None,
                                                                     'zip': None,
                                                                     'country': None,
                                                                     'years': [year],
                                                                 }
                                                             ]

# Write out our results
with open(os.path.join(settings.output_folder, settings.combined_json_file), 'w') as fout:
    json.dump(members, fout, indent=4)
