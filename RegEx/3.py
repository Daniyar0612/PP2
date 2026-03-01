import re

txt = """Hi
my
name
is
Sally"""

#Search for a sequence that starts with "me", followed by one character, even a newline character, and continues with "is":
print(re.findall("me.is", txt, re.DOTALL))

#This example would return no match without the re.DOTALL flag:
print(re.findall("me.is", txt))


#Same result with the shorthand re.S flag:
print(re.findall("me.is", txt, re.S))


