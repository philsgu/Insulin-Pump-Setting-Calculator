import ui, dialogs, os, csv, shutil
from tempfile import NamedTemporaryFile
	
class MyTextFieldDelegate (object):
	#dismiss keyboard upon scroll of defined txtfield focus
	def scrollview_did_scroll(self, scrollview):
		if scrollview.tracking == True:
			prepump.end_editing()
			wtmethod.end_editing()
			carb_input.end_editing()
			target_glucose.end_editing()
			glucose_input.end_editing()
			ratio_input.end_editing()
			isf_input.end_editing()
			
	def textfield_did_change(self, textfield):
		#avoids empty txtfield
		try:
			button.title = 'Save'
			view.name = 'Insulin Pump Calculator'
			if len(textfield.text) > 3:
				textfield.text = ''
				textfield.end_editing()
				
			method1 = int(prepump.text)*0.75
			method2 = int(wtmethod.text)*0.23
			avgtdd = round((method1+method2)/2, 2)
			basal = round((avgtdd/2)/24, 2)
			
			tdd_label.text = str(avgtdd)
			basal_label.text = str(basal)
			
			carb_label.text = str(round(450/avgtdd))
			isf_label.text = str(round(1700/avgtdd))
		
			#bolus calculate
			ratio_input.text = carb_label.text
			isf_input.text = isf_label.text
		
		except ValueError:
			tdd_label.text = '...'
			basal_label.text = '...'
			carb_label.text = '...'
			isf_label.text = '...'
			button.title = 'Open'

class MyBolusTextfield (object):		
				
	def textfield_did_change(self, textfield):
		try:
			if len(textfield.text) > 3:
				textfield.text = ''
				textfield.end_editing()
			
			glucose = int(glucose_input.text) 
			target = int(target_glucose.text)
			carbs = int(carb_input.text)
			ratio = int(ratio_input.text)
			isf = int(isf_input.text)
			
			correction = (glucose - target)/isf
			carbinsulin = carbs/ratio
			units_label.text = str(round(carbinsulin + correction, 1))
		except ValueError:
			units_label.text = '...'


#create temp file to read and write csv
tempfile = NamedTemporaryFile(mode = 'w', delete = False)


#save csv data 
@ui.in_background		
def saveFile(sender):
	if button.title == 'Open':
		openfile = dialogs.input_alert('Search MR#', 'Open Profile Settings')
		
		#remove duplicate data 1st
		with open('pump_profiles.csv', 'r') as f:
				
			data = list(csv.reader(f))
		
			new_data=[a for i, a in enumerate(data) if a not in data[:i]]
			with open('pump_profiles.csv', 'w') as t:
				write = csv.writer(t)
				write.writerows(new_data)
		#iterate each row to search value
		with open('pump_profiles.csv', 'r') as dr:
			dataread = csv.DictReader(dr, fieldnames = dataheaders)
			
			sign = False
			for i in dataread:
				
				if i['MR'] == openfile:
					(prepump.text, wtmethod.text, tdd_label.text, basal_label.text, carb_label.text, isf_label.text)		=(i['prepump'], i['wt'],i['tdd'],
					i['basal_rate'],  i['carb_ratio'], i['isf'])
					(ratio_input.text, isf_input.text)=(i['carb_ratio'], i['isf'])
					view.name = i['MR'].title()
					sign=True
					continue	
				
			if sign == False:
				dialogs.alert('Not Found','', 'OK', hide_cancel_button = True)						
	
	else:
		button.title == 'Save'
		mr_number = dialogs.input_alert('Enter MR#','Save Profile Settings')
		
		try: 
		#save data first
			with open('pump_profiles.csv', 'a+') as savedata:
				saver = csv.DictWriter(savedata, fieldnames = dataheaders)
				
				if not mr_number:
					dialogs.alert('Blank MR','Please try again', 'OK', hide_cancel_button = True)
				else:
					saver.writerow({'MR':mr_number, 'prepump':prepump.text, 'wt':wtmethod.text,'tdd':tdd_label.text, 'basal_rate':basal_label.text, 'carb_ratio':carb_label.text, 'isf':isf_label.text})
					
					dialogs.alert('Saved','', 'OK', hide_cancel_button = True)
				
		
		#save data profile to csv if already present
			with open('pump_profiles.csv', 'r') as csvfile, tempfile:
				reader = csv.DictReader(csvfile, fieldnames = dataheaders)
				writer = csv.DictWriter(tempfile, fieldnames = dataheaders)
			
				for row in reader:
				#data iterate 
					row = {'MR': row['MR'],'prepump':row['prepump'],'wt':row['wt'],'tdd':row['tdd'],'basal_rate': row['basal_rate'], 'carb_ratio': row['carb_ratio'], 'isf': row['isf']}
				
				#match and only replace if MR found else add
					if row['MR'] == mr_number:
						print('Updating row: ', row['MR'])
						print(tempfile.name)
					
						(row['prepump'], row['wt'],row['tdd'],
						row['basal_rate'],  row['carb_ratio'], row['isf'])= (prepump.text, wtmethod.text, tdd_label.text, basal_label.text, carb_label.text, isf_label.text)	
							
					writer.writerow(row)
			shutil.move(tempfile.name, 'pump_profiles.csv')	
			
		except ValueError:
			print('multiple save')
					
			
view = ui.load_view('pumpstart')
#adjust screen based on device
w, h = ui.get_screen_size()
view['scrollview'].width = w
view['scrollview'].height = h
view['scrollview'].content_size = (w, h*1.5)
view['scrollview'].show_vertical_scroll_indicator = False

#check/create csv file 
dataheaders = ['MR','prepump','wt', 'tdd','basal_rate','carb_ratio','isf']

if not os.path.isfile('pump_profiles.csv'):
	with open('pump_profiles.csv', 'w') as filedata:
		csv_data = csv.DictWriter(filedata, fieldnames = dataheaders)
		csv_data.writeheader()

		
#button label obj 
button = view['scrollview']['savebutton']
#declare txtfields instant obj
scrollv = view['scrollview']
wtmethod = view['scrollview']['weight_input']
prepump = view['scrollview']['pre_input']
tdd_label = view['scrollview']['tdd_label'] 
basal_label = view['scrollview']['basal_label']
carb_label = view['scrollview']['carb_label']
isf_label = view['scrollview']['isf_label']

#instant obj for quick bolus
carb_input = view['scrollview']['carb_input']
target_glucose = view['scrollview']['target_glucose']
glucose_input = view['scrollview']['glucose_input']
ratio_input = view['scrollview']['ratio_input']
isf_input = view['scrollview']['isf_input']
units_label = view['scrollview']['units_label']

#create data json

#assign txtfield delegates
scrollv.delegate = MyTextFieldDelegate()
prepump.delegate = MyTextFieldDelegate()
wtmethod.delegate = MyTextFieldDelegate()
#bolus txtfield delegate
glucose_input.delegate = MyBolusTextfield()
carb_input.delegate = MyBolusTextfield()
target_glucose.delegate = MyBolusTextfield()
ratio_input.delegate = MyBolusTextfield()
isf_input.delegate = MyBolusTextfield()


view.present('fullscreen', title_bar_color = 'blue', title_color='white', orientations='portrait')
