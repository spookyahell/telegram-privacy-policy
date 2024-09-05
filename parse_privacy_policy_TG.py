'''You'll need to download a copy from somewhere and give it a path via a seperate file for now since downloading a new copy isn't handled'''

'''Standard MIT open source software license (may request other licenses if required for whatever weird reason)'''


import json, re
from os import sep
from parse_pp_config import path
from bs4 import BeautifulSoup

path_to_html = sep.join([path, 'Telegram Privacy Policy.html'])

print('Loading document from: {0!r}'.format(path_to_html))

# Make sure UTF-8 BOM is properly stored.
with open(path_to_html, encoding = 'utf-8-sig') as f:
	html_code = f.read()



soup = BeautifulSoup(html_code, 'html.parser')
elements = soup.find('div', {'id':'dev_page_content'})
object = {}

html_lines = html_code.split('\n')

found_it = False
for line in html_lines:
	if '            <td class="c" id="displayMonthEl" title="You are here: ' in line:
		found_it = True
		break

def insert_on(data = "21:07:30 Sep 05, 2024"):
	# Only while archive.orgs uses this time format (--> default input value of the function)
	return data[:9]+ 'on ' + data[9:] 
	
	
if found_it is True:
	date = re.search(r'            <td class="c" id="displayMonthEl" title="You are here: ([^"]+)">Sep</td>', line)
	if date:
		the_date = date.group(1)
		print('This document was archived via archive.org.')
		print('Archived:', insert_on(the_date))
		print()
		
		object['date_document_archived'] = the_date
		object['archive_source'] = 'web.archive.org'
		
minor_heading = None; major_heading = None

for element in elements:
	if element.name is None:
		continue
		
	if element.name == 'p':
		#~ print(element.text)
		
		find_strong = element.find('strong')
		if not find_strong:
			fst = ''
		else:
			fst = find_strong.text
		
		if fst == element.text:
			is_strong = True
		else:
			is_strong = False
			
		if minor_heading is None:
			if not major_heading is None:
				if not 'text' in object[major_heading]:
					object[major_heading]['text'] = []
				object[major_heading]['text'].append({'text':element.text, 'isStrong': is_strong})
		else:
			if not 'text' in object[major_heading][minor_heading]:
				object[major_heading][minor_heading]['text'] = []
			object[major_heading][minor_heading]['text'].append({'text':element.text, 'isStrong': is_strong})
		
	elif element.name == 'h3':
		# Major heading
		major_heading = element.text
		minor_heading = None
		object[major_heading] = {}
	elif element.name == 'h4':
		minor_heading = element.text
		object[major_heading][minor_heading] = {}
	elif element.name == 'ul':
		items = []
		for item in element:
			if item.name is not None:
				#~ print('- ', item.text)
				items.append('- {0}'.format(item.text))
		
		if minor_heading is None:
			if not 'list' in object[major_heading]:
				object[major_heading]['list'] = []
			object[major_heading]['list'].append(items)
		else:
			if not 'list' in object[major_heading][minor_heading]:
				object[major_heading][minor_heading]['list'] = []
			object[major_heading][minor_heading]['list'].append(items)


for major_heading in object:
	print(major_heading)
	
	if 'Changes to this'  in major_heading:
		break

count_strong = 0
for text in object[major_heading]['text']:
	if text.get('isStrong') is True:
		count_strong += 1
		
if count_strong == len(object[major_heading]['list']):
	object[major_heading]['changes'] = {}
	count_up = 0
	for idx, item in enumerate(object[major_heading]['text']):
		the_text = object[major_heading]['text'][idx]['text']
		if object[major_heading]['text'][idx]['isStrong'] is True:
			object[major_heading]['changes'][the_text] = object[major_heading]['list'][count_up]
			count_up += 1
			
	del object[major_heading]['text']
	del object[major_heading]['list']

#~ print(object)

with open('tg-privacy-policy.json', 'w') as f:
	f.write(json.dumps(object, indent = 2))
