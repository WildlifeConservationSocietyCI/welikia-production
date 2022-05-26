





import os

from datetime import date
today = date.today()
d4 = today.strftime("%b-%d-%Y")

directory_in_str = "C:/_data/book/a Welikia Atlas/3 - gazetteer/entries"
directory = os.fsencode(directory_in_str)
#print(directory)

fileoutname = 'aa '+'Gazetteer-' + d4 + '.md'
fileout = open(os.path.join(directory_in_str, fileoutname), 'w')

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename[:2] == "aa":
        continue;
    elif filename.endswith('.md'):
        #print(filename)
        list = (filename.split('.'))
        name = list[0]
        id = list[1]
        print(name,id)
        boldname = '**' + name + '**'
        with open(os.path.join(directory_in_str, filename), 'r') as f:
            fileout.write(boldname)
            fileout.write("\n\n")
            contents = f.read()
            fileout.write(contents.rstrip())        #rstrip() is equivalent to perl chomp
            f.close()
            fileout.write("\n\n")
    else:
        continue

fileout.close()

print ("That's all she wrote, folks!")