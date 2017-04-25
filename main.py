import uuid
current_version = "9.3.1"
# note the algorithm is to say if ti's a optional type, there must be a ? at the very last char
def parse_optional(x, result):
    result['is_optional'] = ['false']
    if x[-1] == '?':
        result['result'] = x[:-1]
        result['is_optional'] = ['true']

def parse_type(x):
    r = {}
    r["attribute"] = '_'
    r['default'] = '_'
    ys = x.split()
    b = 0
    e = -1
    f1 = True
    f2 = True
    rx = ""
    for y in ys:
        k = y.find('@')
        if k != -1:
            r["attribute"] = y
            f1 = False
        if y == '=':
            r["default"] = x.split('=')[1].strip()
            f2 = False
        if f1 and f2:
            rx += y + " "
        f1 = True
    r['result'] = rx.strip()
    parse_optional(r['result'], r)
    return r

def parse_parameters(result):
    # parse parameters
    parameters = result['parameters'][0]
    i = 0
    if parameters != "":
        ps = parameters.split(',')
        i = 0
        for p in ps:
            np = p.split(':')
            t = np[1].strip()
            titles = np[0].split()
            t1 = titles[0]
            if len(titles) > 1:
                t2 = titles[1]
            else:
                t2 = '_'

            tm = parse_type(t)
            result['parameters-' + str(i)] = [t1, t2, tm['result'], tm['is_optional'], tm['attribute'], tm['default']]
            i += 1
    result['parameters_num'] = [str(i)]

def sout_parameters(sout, result):
    n = int(result['parameters_num'][0])
    for i in range(n):
        outer = result['parameters-' + str(i)][0]
        if outer == '_':
            sout.write('a3[' + str(i) + ']')
        else:
            sout.write(outer + ': ')
            sout.write('a3[' + str(i) + ']')
        sout.write(' as! ' + result['parameters-' + str(i)][2])
            # ? do we need to cast
        if i != n - 1:
            sout.write(',')
# Convert Swift class declaration file to Node Atomic Runtime Intepreter Core
# Also create class-related Node automatically from the file
def parse_class():

    classname = raw_input("Enter Classname: ")
    fin = open(classname + '.in', "r")
    fout = open(classname + '.out', "w")
    sout = open(classname + '.swift', "w")
    sout.write("/* MARK: - " + classname + '*/\n')
    print("class " + classname)
    lines = fin.readlines()
    class_result = {}
    class_result["name"] = [classname]
    class_result["category"] = ["class"]
    class_result["id"] = [str(uuid.uuid4())]
    class_result["isAtomic"] = ["true"]
    class_result["superclass"] = []
    class_result["protocol"] = []

    current_state = ""
    count = 0
    for line in lines:

        result = {}
        temp = line

        e = temp.find('//')
        if e != -1:
            temp = temp[:e]
        #result["comment"] = temp[e + 2:]
        hasClass = False
        hasFunc = False
        hasVar = False
        hasExtension = False
        t = temp.split()
        p = 0
        position = -1

        #print(t)
        for w in t:
            if w == "extension":
                hasExtension = True
                position = p
            if w == "class":
            #    print(t)
                hasClass = True
                position = p
            if w == "var":
                hasVar = True
            if w == "func":
                hasFunc = True
            p += 1

        if hasClass and not hasVar and not hasFunc and count == 0:
            current_state = "class"
            classname = t[position + 1]

        if hasExtension and not hasVar and not hasFunc and count == 0:
            current_state = "extension"
            classname = t[position + 1]

        count += temp.count("{") - temp.count("}")

        if count == 0:
            current_state = "no"
        #print("[depth: " + str(count) + "]")
        #print("[current_state: " + current_state + "]")
        # ignored cases: } class

        if current_state == "class" or current_state == "extension":
            words = temp.split()
            for word in words:
                if word == "var":
                    nv_category = ["instance property"]
                    result["category"] = nv_category
                    for word in words:
                        if word == "open":
                            result["isOpen"] = ["true"]
                        if word == "class":
                            result["category"] = ["type property"]
                            break
                        elif word == "static":
                            result["category"] = ["static property"]
                            break
                        elif word == "func":
                            break

                    t2 = temp.split(":")
                    t3 = t2[0].split()
                    t4 = t2[1].split()
                    nv_name = t3[-1]
                    nv_type = t4[0]
                    nv_id = str(uuid.uuid4())

                    isGet = temp.find("{ get }")
                    result["set"] = ["true"]
                    if isGet != -1:
                        result["set"] = ["false"]

                    result["name"] = [nv_name]
                    result["type"] = [nv_type]
                    result["id"] = [nv_id]
                    result["class"] = [classname]
                    result["isAtomic"] = ["true"]
                    print("*************")
                    print("name: " + str(result["name"]))
                    print("type: " + str(result["type"]))
                    print("class: " + str(result["class"]))
                    print("category: "+ str(result["category"]))
                    print("set: "+ str(result["set"]))
                    print("*************")
                    print("")
                    #fout.write("[PROPERTY]\n")

                    #print(result['category'])
                    if (result["category"][0] == "instance property"):
                        fout.write(str(result) + '\n')
                        sout.write('// class: ' + str(result["class"][0]) + ' name: ' + str(result["name"][0]) + '\n')
                        sout.write('// category: ' + str(result["category"][0]) + ' id: ' + str(result["id"][0]) + '\n')
                        sout.write('if a1 == "' + str(result["id"][0]) + '" {' + '\n')
                        sout.write('    let v1 = (a2 as! ' + result["class"][0] + ').' + result["name"][0] + "\n")
                        #sout.write('if a1 == "' + str(result["id"] + '" {' + '\n')
                        #sout.write("let v1 = (a2 as!" + result["class"][0] + ")." + result["name"][0] + "\n")
                        sout.write('    save( p1, v1 )\n')
                        sout.write('}\n')
                    elif (result["category"][0] == "static property"):
                        fout.write(str(result) + '\n')
                        sout.write('// class: ' + str(result["class"][0]) + ' name: ' + str(result["name"][0]) + '\n')
                        sout.write('// category: ' + str(result["category"][0]) + ' id: ' + str(result["id"][0]) + '\n')
                        sout.write('if a1 == "' + str(result["id"][0]) + '" {' + '\n')
                        sout.write('    let v1 = ' + result["class"][0] + '.' + result["name"][0] + "\n")
                        sout.write('    save( p1, v1 )\n')
                        sout.write('}\n')
                    break
                if word == "func":
                    result["category"] = ["instance method"]
                    for word in words:
                        if word == "open":
                            result["isOpen"] = ["true"]
                        if word == "class":
                            result["category"] = ["type method"]
                            break
                        elif word == "static":
                            result["category"] = ["static method"]
                            break
                        elif word == "func":
                            break
                    t1 = line.split("(")
                    t2 = t1[0].split()
                    result["name"] = [t2[-1]]
                    result["id"] = [str(uuid.uuid4())]
                    result["isAtomic"] = ['true']
                    result["class"] = [classname]

                    b = temp.find('(')
                    p = temp.find('(')
                    c = 1
                    while c > 0:
                        p += 1
                        if temp[p] == '(':
                            c += 1
                        if temp[p] == ')':
                            c -= 1
                    if b + 1 == p:
                        result["parameters"] = [""]
                    else:
                        result["parameters"] = [temp[b + 1: p]]

                    t5 = temp[p:]
                    e = t5.rfind("->")
                    if e == -1:
                        result["return"] = ["void"]
                    else:
                        t6 = t5[e + 2:]
                        result["return"] = [t6.strip()]

                    print("============")
                    print("name: " + str(result["name"]))
                    print("class: " + str(result["class"]))
                    print("category: "+ str(result["category"]))
                    print("return: " + str(result['return']))
                    print("parameters: " + str(result['parameters']))
                    print("============")
                    print("")

                    # parse parameters
                    parameters = result['parameters'][0]
                    parse_parameters(result)

                    #fout.write("[METHOD]\n")
                    fout.write(str(result) + '\n')
                    if (result["category"][0] == "instance method"):
                        sout.write('// class: ' + result['class'][0] + ' name: ' + result['name'][0] + '\n')
                        sout.write('// category: ' + str(result["category"][0]) + ' id: ' + str(result["id"][0]) + '\n')
                        sout.write('if a1 == "' + result['id'][0] + '" {\n')
                        sout.write('    let v1 = (a2 as! ' + result['class'][0] + ').' + result['name'][0] + '(')
                        sout_parameters(sout, result)
                        sout.write(")" + "\n")
                        sout.write('    save( p1, v1 )\n')
                        sout.write('}\n')
                    elif (result["category"][0] == "type method"):
                        sout.write('// class: ' + str(result["class"][0]) + ' name: ' + str(result["name"][0]) + '\n')
                        sout.write('// category: ' + str(result["category"][0]) + ' id: ' + str(result["id"][0]) + '\n')
                        sout.write('if a1 == "' + str(result["id"][0]) + '" {' + '\n')
                        # differ only this line
                        # notice -
                        sout.write('    let v1 = ' + result["class"][0] + '.' + result["name"][0] + "(")
                        # kdjfalksdjf
                        sout_parameters(sout, result)
                        sout.write(")" + "\n")
                        sout.write('    save( p1, v1 )\n')
                        sout.write('}\n')
                    break
            isInit = temp.find("init(") # NOT HANDLED: type <>, ?  e.g. init<jfkdlsaf>?()
            if isInit != -1:
                result["category"] = ["init"]
                result["class"] = [classname]
                result["isAtomic"] = ['true']
                result["name"] = ["init"] # this name is special by default
                result["id"] = [str(uuid.uuid4())]

                b = temp.find('(')
                p = temp.find('(')
                c = 1
                while c > 0:
                    p += 1
                    if temp[p] == '(':
                        c += 1
                    if temp[p] == ')':
                        c -= 1
                if b + 1 == p:
                    result["parameters"] = [""]
                else:
                    result["parameters"] = [temp[b + 1: p]]
                # use function
                parse_parameters(result)

                sout.write('// class: ' + result['class'][0] + ' name: ' + result['name'][0] + '\n')
                sout.write('// category: ' + str(result["category"][0]) + ' id: ' + str(result["id"][0]) + '\n')
                sout.write('if a1 == "' + result['id'][0] + '" {\n')
                sout.write(result['class'][0] + '.' + result['name'][0] + '(')
                # use function
                sout_parameters(sout, result)
                sout.write(")" + "\n")
                sout.write('    save( p1, v1 )\n')
                sout.write('}\n')


                print("~~~~~~~~~~~~")
                print("name: " + str(result["name"]))
                print("class: " + str(result["class"]))
                print("category: "+ str(result["category"]))
                print("parameters: " + str(result['parameters']))
                print("id: " + str(result['id']))
                print("~~~~~~~~~~~~")
                print("")
                #fout.write("[INIT]\n")
                fout.write(str(result) + '\n')

    #fout.write("[CLASS]\n")
    #fout.write(class_result)
    print("+++++++++++++++++++++")
    print("+ Thanks for using! +")
    print("+++++++++++++++++++++")
    fin.close()
    fout.close()
    sout.close()

a = ""

while a != "q":
    print("nodeview CLI v0.01")
    print("1.Parse A Class")
    print("2.Parse A Struct")
    print("3.Parse A Method")

    a = raw_input("Please select ('q' to exit): ")

    if a == "1":
        res = parse_class()
