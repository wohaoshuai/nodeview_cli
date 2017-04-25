classname = raw_input("Enter Classname: ")
fin = open(classname + '.out', "r")
fout = open(classname + '_node.swift', "w")

lines = fin.readlines()

for line in lines:
    line1 = line.replace('{', '[')
    line2 = line1.replace('}', ']')
    line3 = line2.replace("'", '"').rstrip()
    fout.write("Node(" + line3 + ')\n')

fin.close()
fout.close()

print("replacement complete")
