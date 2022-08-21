import os
import sys
from lxml import etree


def read_text(file):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    return text


def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


def xml2text(infile, outfolder, parent_label='DOC', text_label='seg'):
    # text = read_text(infile)
    parser = etree.HTMLParser(encoding='utf-8')
    html = etree.parse(infile, parser=parser)
    # try:
    #     html = etree.HTML(text)
    # except:
    #     b = bytes(text, encoding='utf-8')  # 字符串转bytes
    #     html = etree.fromstring(b)
    # 如果含有多份译文，取第一个
    # doc=html.xpath(f"//{parent_label.lower()}")[0]
    # text_ls = doc.xpath(".//seg/text()")
    text_ls = html.xpath("//seg/text()")
    text_ls = [text.strip() + '\n' for text in text_ls]
    print(f'total {len(text_ls)} lines.')
    # write
    name = os.path.basename(infile).replace('xml', 'txt').replace('sgm', 'txt')
    outfile = os.path.join(outfolder, name)
    write_file(text_ls, outfile)


if __name__ == '__main__':
    assert len(sys.argv) == 3, f"usage: python {sys.argv[0]} <infile> <outfolder>"
    infile = sys.argv[1]
    outfolder = sys.argv[2]
    # infile='multi-reference/HTRDP(863)2004MTEvaluationData/2004_ref_en_zh_dial.xml'
    # infile='multi-reference/HTRDP(863)2005MTEvaluationData/2005_ref_zh_en_dial.xml'
    # outfolder='.'
    xml2text(infile, outfolder)
