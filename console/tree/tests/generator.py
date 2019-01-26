import random as rd

test_size = {'ex-large' : 1000 * 1000, 'large' : 100 * 1000, 'medium' : 100 * 100}
number_size = {'ex-ex-large' : 1000 * 1000 * 1000, 'ex-large' : 1000 * 1000, 'medium' : 10 * 100, 'small' : 10 * 10, 'ex-small' : 5}

size = test_size['medium']
n_len = test_size['medium']

f = open('test_set_nur_{}.txt'.format(3), 'w')
f.write(str(size) + "\n")
f.write(str(n_len) + "\n")
for i in range(size):
	f.write(str(rd.randint(1, n_len) + n_len) + "\n")
f.close()
