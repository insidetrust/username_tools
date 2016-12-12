import itertools
import operator


census_forenames = {}

with open("dist.male.first") as f:
    for line in f:
        (key, val, dummy, dummy2) = line.split()
        # Uplift so we don't have zeros, and multiple by percentage male
        census_forenames[key.lower()] = (float(val) + 0.0005) * 0.49

with open("dist.female.first") as f:
    for line in f:
        (key, val, dummy, dummy2) = line.split()
        # Uplift so we don't have zeros, and multiple by percentage female
        if key not in census_forenames:
            census_forenames[key.lower()] = (float(val) + 0.0005) * 0.51
        else:
            census_forenames[key.lower()] += (float(val) + 0.0005) * 0.51

census_surnames = {}
#
# with open("dist.all.last") as f:
#     for line in f:
#         (key, val, dummy, dummy2) = line.split()
#         census_surnames[key.lower()] = (float(val) + 0.0005) / 100

# http://surname.sofeminine.co.uk/w/surnames/most-common-surnames-in-great-britain-1.html
# uk-surnames.txt | cut -d"." -f2 | tr -d ' ' | cut -f2- > uk-surnames-edit.txt

uk_population = 64100000
with open("uk-surnames-edit.txt") as f:
    for line in f:
        (key, val) = line.split()
        census_surnames[key.lower()] = (float(val)) / uk_population

print(census_surnames)
# TODO add female names to male names, where exists, add value

# with open("dist.male.first.test") as f:
#     for line in f:
#         (key, val, dummy, dummy2) = line.split()
#         census_forenames[key.lower()] = float(val)/100.0


john_smith = {}
with open("john.smith.txt") as f:
    for line in f:
        (val, key) = line.split()
        john_smith[key] = float(val)

print(census_forenames)
print(census_surnames)
print(john_smith)

# john_smith_filtered = dict((k, v) for k, v in john_smith.iteritems() if k.starts d.keys())

john_smith_filtered = {}

# for forename, multiplier in census_forenames.iteritems():
#     for key, value in john_smith.iteritems():   # iter on both keys and values
#         if key.startswith(forename + '.'):
#             john_smith_filtered[key] = multiplier * value

for surname, multiplier in census_surnames.iteritems():
    for key, value in john_smith.iteritems():   # iter on both keys and values
        if key.endswith('.' + surname):
            john_smith_filtered[key] = multiplier * value


print(john_smith_filtered)

# print(john_smith)
#
# for key, value in john_smith.iteritems():
#     print(key, value)


for key, value in sorted(john_smith_filtered.items(), key=operator.itemgetter(1), reverse=True):
    print(key, value)

#
# with open('dist.male.first.test', 'rt') as f:
#   reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
#
#   lineData = list()
#
#   for line in reader.iter:
#     print(line)
#
#   cols = next(reader)
#   print(cols)
#
#   for col in cols:
#     # Create a list in lineData for each column of data.
#     lineData.append(list())
#
#
#   for line in reader:
#     for i in xrange(0, len(lineData)):
#       # Copy the data from the line into the correct columns.
#       lineData[i].append(line[i])
#
#   data = dict()
#
#   for i in xrange(0, len(cols)):
#     # Create each key in the dict with the data in its column.
#     data[cols[i]] = lineData[i]
#
# print(data)
