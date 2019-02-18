# Imports
import argparse
import os
from math import cos, sin, radians

# Function definitions

def encode(argDict):
	# Define variables
	code = argDict.get('code')
	offset = int(argDict.get('offset'))
	infile = argDict.get('infile')
	outfile = argDict.get('outfile')
	text = argDict.get('text')
	ba1 = argDict.get('a1')
	ba2 = argDict.get('a2')
	ba3 = argDict.get('a3')
	
	if len(outfile) < 1:
		outfile = infile
		
	offset += 450 # try and avoid the audio file metadata/header
	
	# Change the message to be encoded into hex
	hexText = [ ("0" + hex(ord(x)).replace('0x', ''))[-2:] for x in text]
	#print "Message Hex: ", hexText						#DEBUG
	
	# Get Hex values of the file'
	with open(infile, 'rb') as file:   
		data = file.read()              
		hexValues = [ ("0" + hex(ord(x)).replace('0x', ''))[-2:] for x in data]

	# Calculate the space between each value
	count = 0
	spaces = []
	for value in hexText:
		if (ba1):
			spaces.append(a1(code, count))
		elif (ba2):
			spaces.append(a2(code, count))
		else:
			spaces.append(a3(code, count))
		count += 1
	#print "Spaces between: ", spaces					#DEBUG
	
	# Parse through and change the values
	count = offset
	changeValue = offset + spaces[0]
	messageIndex = 0
	
	for value in hexValues:
		
		if (count == changeValue):
			#print count, messageIndex, value, spaces[messageIndex] 	#DEBUG
			hexValues[count] = hexText[messageIndex]
			#print hexText[messageIndex-1] 					#DEBUG
			changeValue += spaces[messageIndex]
			messageIndex += 1
			if (messageIndex >= len(hexText)):
				break
		count += 1
	
	# Save the encoded data into a new mp3 file
	exists = os.path.isfile(outfile)
	if exists:
		os.remove(outfile)
		
	newfile = open(outfile, "wb+")
	
	for value in hexValues:
		#print "HEX:", value,							#DEBUG
		newfile.write(value.decode("hex"))
		#print "ASCII:", value.decode("hex")			#DEBUG
	
	
	
def decode(argDict):
	# Define variables
	code = argDict.get('code')
	offset = int(argDict.get('offset'))
	infile = argDict.get('infile')
	ba1 = argDict.get('a1')
	ba2 = argDict.get('a2')
	ba3 = argDict.get('a3')
	secretmessage = ""

	offset += 450 # try and avoid the audio file metadata/header
	
	# Get the hex values of the file to be decoded
	with open(infile, 'rb') as file:   
		data = file.read()              
		hexValues = [ ("0" + hex(ord(x)).replace('0x', ''))[-2:] for x in data]
	
	# Calculate the spaces in the file
	count = 0
	spaces = []
	for value in hexValues:
		if (ba1):
			spaces.append(a1(code, count))
		elif (ba2):
			spaces.append(a2(code, count))
		else:
			spaces.append(a3(code, count))
		count += 1
	#print "SPACES:", spaces[:10]
		
	# Go through the file and check every space the algorithm covers with the params
	count = offset
	changeValue = offset + spaces[0]
	messageIndex = 0
	
	for value in hexValues:
		if (count == changeValue):
			#print count, messageIndex, value, spaces[messageIndex]
			secretmessage += hexValues[count].decode("hex")
			changeValue += spaces[messageIndex]
			messageIndex += 1
		count += 1
		if (messageIndex > 50):#(count >= len(hexValues)+1):
			break
	
	print secretmessage

def a1(code, x):
	code = str(code)
	d = float(code[3:])
	c = float(code[2:3])
	b = float(code[1:2])
	a = float(code[0:1])
	return round(abs((a-cos(c))*sin(x/((b+24)/9))+cos(d)))+5

def a2(code, x):
	code = str(code)
	d = float(code[3:])
	c = float(code[2:3])
	b = float(code[1:2])
	a = float(code[0:1])
	return round(abs((10-(sin(a*2)+(c+20))*(cos(x)))*((d+1)/(-2*b))))+5

def a3(code, x):
	code = str(code)
	d = float(code[3:])
	c = float(code[2:3])
	b = float(code[1:2])
	a = float(code[0:1])
	return round(abs(sin((((x%5)*sin(a))*(c+5))/(d+.5))*(b+3)))+5


# Parse the arguments

parser = argparse.ArgumentParser(description='Encode or decode messages in the hex values of audio files')

subparsers = parser.add_subparsers(help='encode or decode messages in audio files', dest='command')

decode_parser = subparsers.add_parser('decode', help='decode an audio file')
dalgorithms = decode_parser.add_mutually_exclusive_group()
dalgorithms.add_argument('-a1', action='store_true', dest="a1", default=False, help='Use the first algorithm option to decode')
dalgorithms.add_argument('-a2', action='store_true', dest="a2", default=False, help='Use the second algorithm option to decode')
dalgorithms.add_argument('-a3', action='store_true', dest="a3", default=False, help='Use the third algorithm option to decode')
decode_parser.add_argument('--infile', '-i',  action='store', dest='infile',   help='The audio file you want to decode')
decode_parser.add_argument('--outfile','-o',  action='store', dest='outfile',  help='Filepath of where you want the decoded message to be saved.')
decode_parser.add_argument('--offset', '-f',  action='store', dest='offset', default=0,    help='Offset of the message. Defaults to 0')
decode_parser.add_argument('--code',   '-c',  action='store', dest='code',   default=1234, help='Four digit code to randomize the algorithms. Defaults to \'1234\'')

encode_parser = subparsers.add_parser('encode', help='encode an audio file')
ealgorithms = encode_parser.add_mutually_exclusive_group()
ealgorithms.add_argument('-a1', action='store_true', dest="a1", default=False, help='Use the first algorithm option to encode')
ealgorithms.add_argument('-a2', action='store_true', dest="a2", default=False, help='Use the second algorithm option to encode')
ealgorithms.add_argument('-a3', action='store_true', dest="a3", default=False, help='Use the third algorithm option to encode')
encode_parser.add_argument('--infile', '-i',  action='store', dest='infile',   help='The audio file you want to encode')
encode_parser.add_argument('--outfile','-o',  action='store', dest='outfile',  help='Filepath of where you want the encoded audio file to be saved')
encode_parser.add_argument('--text',   '-t',  action='store', dest='text',     help='Text to encode in the audio file')
encode_parser.add_argument('--offset', '-f',  action='store', dest='offset', default=0,    help='Offset of the message. Defaults to 0')
encode_parser.add_argument('--code',   '-c',  action='store', dest='code',   default=1234, help='Four digit code to randomize the algorithms. Defaults to \'1234\'')

args = vars(parser.parse_args())

# Actually run the program


if(args.get('command') == None):
	print("audioStego.py error: Please specify encode or decode")
else:
	if(not args.get('a1') and not args.get('a2') and not args.get('a3')):
		print("audioStego.py error: No algorithm encoding specified.")
	elif(args.get('infile') == None):
		print("audioStego.py error: Please specify an audio file to encode/decode.")
	else: 
		if(args.get('command') == "decode"):
			decode(args)
		elif(args.get('command') == "encode"):
			if(args.get('text') == None):
				print("audioStego.py error: No text to encode")
			else:
				encode(args)
		else:
			print("audioStego.py error: critical unknown error.")








