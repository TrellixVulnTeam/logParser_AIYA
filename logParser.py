#!/usr/bin/python3
#  logParser.py
#  
#  Copyright 2019 Spencer Finch <altmcman@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import re, sys, os, platform
import time



'''
easily defines all the different formats you could use on a commandline-
dashes, slashes, and maybe more if i think of anything else.
if the arg exists, this will return True; else it returns False
'''
def argFormats(arg):
	if ('-' + arg) in sys.argv or ('/' + arg) in sys.argv:
		return True
	return False
	
def saveFile(listToBeWriten, name = "parsedLog"):
	f = open('tmpFile', 'w')
	qprint("saving file...")
	for line in listToBeWriten:
		f.write(line)
		spinningLoad()
	f.flush()
	os.fsync(f.fileno())
	f.close()
	os.rename('tmpFile', name)
	qprint("file saved!")


if not argFormats('f'):
	import psutil #you'll have to install these using pip3
	
'''
checks for the quiet flag, and if absent it prints
	maybe expand upon this? like also checking for verbosity?
'''
def qprint(arg):
	if not argFormats('q'):
		print(arg)

# | / - \ |
# slows down execution a little
state = 1
def spinningLoad():
	global state
	if argFormats('x'):
		return
	spinner = {
		1: '|',
		2: '/',
		3: '-',
		4: '\\'
	}
	if state == 4:
		state = 1
	else:
		state += 1
	print('\b' + spinner.get(state, ''), end="\r")
		
def readFile(filepath):
	file1lines = []
	if not argFormats('f') or not argFormats('q'):
		statinfo = os.stat(filepath)
		mem=psutil.virtual_memory()
		swapmem=psutil.swap_memory()
		if (statinfo.st_size > mem.total):
			print("File larger than memory space." 
					+ "\nEither upgrade your computer, or allocate more swap"
					+ " space to process this (albeit slowly).") 
			return file1lines
		elif (statinfo.st_size > mem.available):
			print("File size: {s} \t\t Free RAM + Swap: {f}".format(s=statinfo.st_size, f=(swapmem.free+mem.available)))
			choice=input('This file is larger than your RAM, but may be small'
							' enough to fit in swap. Continue? (y/n)\n> ')
			if (choice == 'n' or choice == 'N'):
				return file1lines
	qprint("Opening file: "+filepath)
	file1 = open(filepath)
	qprint("Reading lines, please wait...")
	start_time = time.time()
	for line in file1:
		file1lines += line
		if not argFormats('x'):
			spinningLoad()
	qprint("Data gotten! Closing file")
	file1.close()
	executionTimer(start_time, time.time())
	return file1lines
	
def executionTimer(startTime, endTime):
	exe_time = endTime - startTime
	if exe_time > 7200:	#if above 2 hrs, show by hours
		print("<< %s hours >>\n(multiply by 60 to get seconds)" % exe_time/60)
	elif exe_time > 600:	#if above 10 minutes, show by minutes
		print("<< %s minutes >>\nmultiply by 10 to get seconds" % exe_time/10)
	else:
		print("<< %s seconds >>" % exe_time)


if platform.system() == "Windows":
	dir = os.popen("dir").readLines()
	if argFormats('l'):
		print("Arguments forcing Linux directory printing.")
		dir = os.popen("ls").readLines()
else:
	if argFormats('w'):
		print("Arguments forcing Windows directory printing.")
		dir = os.popen("dir").readLines()
	dir = os.popen("ls").readlines()
for line in dir:
	print(line)
	
print(dir)

file1_path=input("Type a file from above, or type a filepath...\n> ")
file1lines = []
file1lines = readFile(file1_path)
#converts individual letter elements to lines
lastReturnIndex = 0
currentIndex = 0
print("Processing list...")
file2lines=[]
for line in file1lines:
	if line == '\n':
		word = ''
		for i in range(lastReturnIndex, currentIndex):
			word += file1lines[i]
		file2lines.append(word)
		lastReturnIndex = currentIndex
	currentIndex += 1
print(file2lines[0])
searchTerm = input("Type a keyword to search for...\n> ")
termsFound = []
for line in file2lines:
	if searchTerm in line:
		termsFound.append(line)
print(len(termsFound))
while True: #replace this with a better loop
	choice = input("What do you want to do with these lines?"
				+ "\n(S)ave to file\n(V)iew Logs\n(E)xit")
	if choice == 'e':
		break
	elif choice == 's':
		choice = input("Name your file...")
		saveFile(termsFound, choice)
	elif choice == 'v':
		currentLine = 0
		while True: #emulated do-while loop
			currentLine += 20 #replace 20 with terminal height later
			for i in range(currentLine): 
				try:
					print(termsFound[i], end='')
				except:
					print("End of lines, restart (y) or end (N)?")
					time.sleep(1)
					choice = input("\n> ")
					if choice == 'y':
						currentLine = 0
					else:
						break
			choice = input("\nMore? (Y/n)\n> ")
			if choice == 'n':
				break
