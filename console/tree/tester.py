import tango_strict as tg
import math


def test_console():
	print('For the console tests input format is just the same as for the file`s system')
	number_of_tests = 1
	tree_range = 2
	while True:
		try:
			number_of_tests = int(input('Number of tests: '))
			if number_of_tests > 0 and number_of_tests < 100000:
				break
			else:
				raise Exception('Please use number of tests less than 10^5 and greater than 0 (int)')
		except Exception as e:
			print(e)

	while True:
		try:
			tree_range = int(input('Tree values range: '))
			if tree_range > 0 and tree_range < 1000 * 1000:
				break
			else:
				raise Exception('Please use the values range less than 10^6 and greater than 0 (int)')
		except Exception as e:
			print(e)

	tango_bst = None
	try:
		tango_bst = tg.TangoTree(range(tree_range))
	except Exception as e:
		print(e)
	
	for i in range(number_of_tests):
		start = time.time()
		res = math.inf
		val = -math.inf
		try:
			val = int(float(input('value: ')))
		except Exception as e:
			print('Wrong input format!')
			continue
		try:
			res = tango_bst.search(val)
		except Exception as e:
			print(e)
		if res == val or (res is None and (val >= tree_range or val < 0)):
			end = time.time()
			print('Time: {}'.format(end - start))
			continue
		else:
			print("MISTAKE")
			print('Test: ', val)
			print('Return', res)


if __name__ == "__main__":
	import time
	import random as rd
	print('This is console Tango-Tree test application')
	print('You may test the application using prepared test, find them in the "test" directory')
	print('You do not have to specify the directory, only file name')
	print('Or you may create your own tests, just put them into tests directory, and call here')
	print('The format of test:')
	print('N - number of queries')
	print('M - range of elements in the tree')
	print('Tests... - one for row')
	print('See the example in the "tests" directory')
	print('q - to finish testing')
	print('c - for interactive(console) testing')
	avg = 0
	while True:
		inp = input('file name: ')
		if inp == 'q':
			break
		elif inp == 'c':
			test_console()
			continue
		file_name = 'tests/' + inp
		try:
			f = open(file_name, 'r')
		except Exception as e:
			print('No such file, try again, please')
			continue
		n = 0
		m = 0
		try:
			n = int(f.readline())
			m = int(f.readline())
		except Exception as e:
			print('Wrong test size format, please, load another test set')
			continue

		if n > 100000:
			print('Please, load smaller test set (python is to slow in reading such a long files)')
			continue
		if n <= 0:
			print('Test size cannot be empty or negative!')
			continue

		if m > 1000 * 1000:
			print('Please, choose smaller items range')
			continue
		if m <= 0:
			print('Values range cannot be negative!')
			continue

		tango_bst = tg.TangoTree(range(m))
		start = time.time()
		for i in range(n):
			line = ''
			val = 0
			try:
				line = f.readline()
				val = int(line)
			except Exception as e:
				print('Input file format error, test: "{}", declined'.format(line))
				continue
			test_start = time.time()
			res = math.inf
			try:
				res = tango_bst.search(val)
			except Exception as e:
				print(e)
			test_finish = time.time()
			avg += test_finish - test_start
			if res == val or (res is None and (val >= m or val < 0)):
				continue
			else:
				print("MISTAKE")
				print('Test: ', val)
				print('Return', res)
		f.close()
		end = time.time()
		avg /= n
		print('Time: {:.10f}s'.format(end - start), 'Avg time per query: {:.20f}s'.format(avg))