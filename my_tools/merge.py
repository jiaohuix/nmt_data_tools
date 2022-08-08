import sys
from tqdm import tqdm
def read_pair_text(file1,file2,sep="\t"):
	res=[]    
	with open(file1,'r',encoding='utf-8') as f1,open(file2,'r',encoding='utf-8') as f2:
		for line1,line2 in zip(f1.readlines(),f2.readlines()):
			line1,line2=line1.strip(),line2.strip()
			res.append(f"{line1}{sep}{line2}\n")
	return res	

def write(res,out_file):
	with open(out_file,'w',encoding='utf-8') as f:
		for line in tqdm(res):
			f.write(line)
		# f.write(''.join(res))
	print(f'write to {out_file} success.')

if __name__=="__main__":
	assert len(sys.argv) == 5, f"usage: python {sys.argv[0]} <infile1> <infile2> <outfile> <sep> (space/tab)"
	file1=sys.argv[1]
	file2=sys.argv[2]
	out=sys.argv[3]
	sep=sys.argv[4]
	assert sep=="space" or sep=="tab","sep is either or tab."
	res=read_pair_text(file1,file2,sep="\t" if sep=="tab" else " ")
	write(res,out)
