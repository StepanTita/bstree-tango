import sys
#sys.path.insert(0, '../')
import tango_strict as tg

if __name__ == "__main__":
	file_name = 'tests/test_set_' + input('file name: test_set_')
	f = open(file_name, 'r')
	n = int(f.readline())
	m = int(f.readline())
	tango_bst = tg.TangoTree(range(m))
	for i in range(n):
		val = int(f.readline())
		res = tango_bst.search()
		if res == val or res is None:
			continue
		print("MISTAKE")
	f.close()