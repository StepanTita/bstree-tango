import random as rd

test_size = {'ex-large' : 1000 * 1000, 'large' : 100 * 1000, 'medium' : 100 * 100}
number_size = {'large' : 1000 * 1000, 'medium' : 10 * 100, 'small' : 10 * 10}

size = 'medium'
n_len = 'medium'

print('It is random tests generator')
print('To use it, just choose the test set size, and the tree values range')
print('After that name your set, and use it')
print('Available test sizes: ex-large = (10^6), large = (10^5), medium = (10^4)')
print('Available number sizes: large = (10^6), large = (10^4), medium = (10^2)')
print('or specify your own, by typing: "new a" (1 <= a <= 10^8)')
print('q - to quit')

while True:
	size = input('Test size: ')
	if size == 'q':
		break
	n_len = input('Values range: ')
	if n_len == 'q':
		break
	

	if 'new' in size:
		try:
			size = int(size.split(' ')[1])
			if size > 10**8 or size < 1:
				raise Exception()
		except Exception as e:
			print('Invalid input')
	else:
		try:
			size = test_size[size]
			print(size)
			if size > 10**8 or size < 1:
				raise Exception()
		except Exception as e:
			print('Invalid input')
			continue

	if 'new' in n_len:
		try:
			n_len = int(n_len.split(' ')[1])
			if n_len > 10**8 or n_len < 1:
				raise Exception()
		except Exception as e:
			print('Invalid input')
			continue
		
	else:
		try:
			n_len = number_size[n_len]
			print(n_len)
			if n_len > 10**8 or n_len < 1:
				raise Exception()
		except Exception as e:
			print('Invalid input')
			continue
		
	name = input('file name: ')
	f = None
	try:
		f = open(name + '.txt', 'w')
	except Exception as e:
		print('Error with file creation')
		continue
	
	f.write(str(size) + "\n")
	f.write(str(n_len) + "\n")
	for i in range(size):
		f.write(str(rd.randint(1, n_len)) + "\n")
	f.close()
	print('Success')
