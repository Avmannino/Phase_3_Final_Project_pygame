import os

from os.path import isfile, join

files = [ f for f in os.listdir(".") if "_a" in f and isfile(f) ]
print(files)
i = 1

for file in files:
    os.rename(file, f"whatever_{i}.png")
    i+=1