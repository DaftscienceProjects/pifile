import fnmatch
import os


files = {'json': [], 'py': [], 'ini': []}
# pyfiles = []
# inifiles = []
# jsonfiles = []
for root, dirnames, filenames in os.walk('./'):
        # print filenames
    for filename in fnmatch.filter(filenames, '*.json'):
        files['json'].append(os.path.join(root, filename))
    for filename in fnmatch.filter(filenames, '*.py'):
        files['py'].append(os.path.join(root, filename))
    for filename in fnmatch.filter(filenames, '*.ini'):
        files['ini'].append(os.path.join(root, filename))

total = 0
# print thing

for kind in files:
    subtotal = 0
    for thing in files[kind]:
        # print thing
        with open(thing) as f:
            for i, l in enumerate(f):
                pass
        # print str(i) + " " +thing
        subtotal += i
    print kind + ' ' + str(subtotal)
    total += subtotal
print total
