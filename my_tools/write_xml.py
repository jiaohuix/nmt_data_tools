import sys
from lxml import etree
from lxml.builder import ElementMaker
def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=[line.strip() for line in f.readlines()]
    return lines

def ccmt_submit(sentences,outfile="result.xml"):
    E = ElementMaker()
    Test = E.tstset
    Doc= E.DOC
    P=E.p
    SEG=E.seg
    my_doc=Test(
        Doc(
            P(
                *[SEG(txt, id=f"{i+1}") for i, txt in enumerate(sentences)],
            ),
        docid="news",
        sysid="1"
        ),
        setid="nestest2019",
        srclang="zh",
        trglang="en"
    )
    print(etree.tostring(my_doc, encoding="UTF-8", standalone="yes", pretty_print=True))
    etree.ElementTree(my_doc,).write(outfile, pretty_print=True, encoding="UTF-8")

if __name__ == '__main__':
    infile=sys.argv[1]
    outfile=sys.argv[2]
    lines=read_file(infile)
    ccmt_submit(sentences=lines,outfile=outfile)