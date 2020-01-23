import numpy as np
from subprocess import check_output, STDOUT
import numpy, time
numpy.random.seed(int(time.time()))

maxInt = 10
base_float = [1e-4, 1, 1e2, 1e10]
bool_opts = ['.false.', '.true.']

def make_int():
	return str(np.random.randint(2*maxInt+1) - maxInt)

def make_float():
	base_val = np.random.choice(base_float)
	return str(np.random.randn() * base_val)

def make_bool():
	return np.random.choice(bool_opts)

def make_val(prototype):
	kind = value_classifier(prototype)
	if kind == 'bool':
		return make_bool()
	elif kind == 'float':
		return make_float()
	else:
		return make_int()

def make_inlist(fname, star_job, controls):
	fi = open(fname, 'w+')

	fi.write('&star_job\n')
	fi.write(star_job)
	fi.write('\n/ !end of star_job\n')

	fi.write('&controls\n')
	fi.write(controls)
	fi.write('\n/ ! end of controls\n')

	fi.close()

def make_directory(dirName):
	check_output('cp -R prototype ' + dirName, shell=True)
	check_output('cd ' + dirName + '; ./clean; ./mk', shell=True)

def run_MESA(dirName, timeout=10, timeout_command='gtimeout'):
	try:
		out = check_output('cd ' + dirName + '; ' + timeout_command + ' ' + str(timeout) + ' "./rn"', shell=True, stderr=STDOUT)
	except Exception as e:
		out = e.output
	return out

def value_classifier(opt):
	if opt == '.false.' or opt == '.true.':
		return 'bool'	

	if '\'' in opt or '\"' in opt:
		return 'string'

	opt = opt.replace('d', 'e+')

	try:
		x = int(opt)
		return 'int'
	except:
		try:
			x = np.float(opt)
			return 'float'
		except:
			return 'string'

def parse_defaults(fname):
	fi = open(fname, 'r')
	opts = []
	vals = []
	for line in fi:
		x = line.lstrip()
		x = x.strip('\n')
		if len(x) == 0 or x[0] == '!':
			continue

		x = x.split('=')

		opt = x[0].strip()

		if '(' in opt or ')' in opt:
			continue

		val = x[1].lstrip()
		val = val.split(' ')
		val = val[0]
		val = val.strip()

		opts.append(opt)
		vals.append(val)

	return opts, vals

def make_controls(opts, vals, indices, mandatory_controls):
	controls = ''
	for i in indices:
		opt = opts[i]
		val = vals[i]

		# Filtering to avoid playing with silly options
		if 'read_extra' in opt:
			continue

		if value_classifier(val) != 'string':
			controls = controls + opt + ' = ' + make_val(val) + '\n'

	controls = controls + mandatory_controls

	return controls

copt, cval = parse_defaults('controls.defaults')
sopt, sval = parse_defaults('star_job.defaults')
make_directory('trial')
mandatory_controls = 'report_ierr = .true.\n'
bad_strings = ['failed', 'nan', 'error']
repeats = 5
counter = 0

from itertools import combinations

for r in range(len(copt)):
	comb = combinations(range(len(copt)), r)
	for i,indices in enumerate(comb):
		for r in range(repeats):
			controls = make_controls(copt, cval, indices, mandatory_controls)
			star_job = make_controls(sopt, sval, [], '')

			make_inlist('trial/inlist_project', star_job, controls)
			out = run_MESA('trial', timeout=10, timeout_command='gtimeout')
			out = str(out)
			out = out.replace('\\n','\n')
			counter += 1

			for bs in bad_strings:
				if bs in out.lower():
					print('Bad string detected in trial ' + str(counter) + ':', bs)
					controls = "\n".join([ll.rstrip() for ll in controls.splitlines() if ll.strip()])
					star_job = "\n".join([ll.rstrip() for ll in star_job.splitlines() if ll.strip()])
					print(controls)
					print(star_job)
#					print(out)
					print('--------------------------------')