'''
General utils
'''

def convert_bool(value):
	valid_true = {'true', 'yes'}
	valid_false = {'false', 'no', 'none', 'null'}
	if value.lower() in valid_true: return True
	if value.lower() in valid_false: return False
	else: raise ValueError('Invalid type')