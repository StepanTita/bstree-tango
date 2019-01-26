import tango_strict as tg

if __name__ == "__main__":
	import time
	import plotly as py
	import plotly.graph_objs as go
	from plotly import tools
	import random as rd

	while True:
		inp = input('file name: test_set_')
		if inp == 'q':
			break
		file_name = 'tests/test_set_' + inp + '.txt'
		f = open(file_name, 'r')
		n = int(f.readline())
		m = int(f.readline())
		tango_bst = tg.TangoTree(range(m))
		start = time.time()
		for i in range(n):
			val = int(f.readline())
			res = tango_bst.search(val)

			if res == val or res is None:
				continue
		f.close()
		end = time.time()
		print(end - start)