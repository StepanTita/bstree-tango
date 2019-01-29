import tango_strict as tg

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
	avg = 0
	while True:
		inp = input('file name: ')
		if inp == 'q':
			break
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
			res = tango_bst.search(val)
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