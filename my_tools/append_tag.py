import sys
"""
注意：尖括号是特殊符号，命令行不能用，若要用<spoken>，请直接用spoken
"""
def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


def add_tag(lines,tag):
    res=[]
    for line in lines:
        line=f"{line.strip()} <{tag.strip()}>\n"
        res.append(line)
    return res

if __name__ == '__main__':
    infile=sys.argv[1]
    outfile=sys.argv[2]
    tag=sys.argv[3]
    lines=read_file(infile)
    res=add_tag(lines,tag)
    write_file(res,outfile)
