#! /usr/local/bin/python3.10

import matplotlib.patches as mpatch
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.path as mpath
import matplotlib
import numpy as np
from Bio import pairwise2
import sys, os, string, math
from matplotlib import rcParams
import argparse
from Bio.PDB import PDBParser
from Bio.PDB.DSSP import DSSP
from Bio.Align import substitution_matrices
from Bio import AlignIO
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from Bio.SeqUtils import seq1
import sys
import re

def DavidCM():
    
    hexcolors = ['#d3d3d3', '#ff1493', '#00ff7f', '#ff7f00', '#1e90ff']
    colors_rgb = [matplotlib.colors.hex2color(hexcolor) for hexcolor in hexcolors]
    chimera_colormap = matplotlib.colors.ListedColormap(colors_rgb, name='chimera')

    return chimera_colormap

def HTH_CM():
    hexcolors = ['#000000']
    colors_rgb = [matplotlib.colors.hex2color(hexcolor) for hexcolor in hexcolors]
    hth_colormap = matplotlib.colors.ListedColormap(colors_rgb, name='chimera')

    return hth_colormap

def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def coords2path(coord_set1):

    coords_f1 = []
    instructions1 = []
    
    for c in coord_set1:
        for n in range(len(c)):
            coords_f1.append(c[n])
            if n == 0:
                instructions1.append(1)
            else:
                instructions1.append(2)

    return coords_f1, instructions1

def build_loop(loop,idx,ssidx,linelen,nlines,loop_coords,prev_ss,next_ss, z=1,clr='r',mat=0,size=75):

    i0 = loop[0]
    if loop[0] != 0 and prev_ss != "B":
        i0 = loop[0]-1
    else:
        i0 = loop[0]+0.1
    i1 = loop[1]+2
    if loop[1] == linelen-1:
        i1 += 2

    o = 2
    if idx == nlines-1:
        o = 0
    if next_ss == "B":
        o = -1.5
    if next_ss == None:
        o=-4.1

    rectangle = mpatch.Rectangle((i0/6.0,-0.25-5.5*idx+2.0*ssidx),(i1-i0+o)/6.0,0.5,
                                  fc=clr,ec='k',zorder=0)

    plt.gca().add_patch(rectangle)

    loop_coords.append(rectangle.get_xy())
    
    if isinstance(mat,np.ndarray):
        im = plt.imshow(mat,extent=[0.0,size,0.5,3.0],cmap=CMAP,interpolation='none',zorder=0)
        im.set_clip_path(rectangle)

def build_strand(strand,idx,ssidx,strand_coords,next_ss,z=1,clr='r',imagemat=0,size=75):

    delta = 0 if next_ss == None else 1
    arrow=mpatch.FancyArrow(strand[0]/6.0,-5.5*idx+2.0*ssidx,(strand[1]-strand[0]+delta)/6.0,0,
                            width=1.0,fc=clr,linewidth=0.5,ec='k',zorder=z,head_width=2.0,
                            length_includes_head=True,head_length=2.0/6.0)
                                
    plt.gca().add_patch(arrow)

    strand_coords.append(arrow.get_xy())


def build_helix(helix,idx,ssidx,coord_set1, coord_set2, clr='r',size=37.5,z=1,bkg=(0.195,0,0.051),imagemat=0):

    helices = []

    i = helix
    l = i[1]-i[0]+1
    points = [[i[0]/6.0,-0.25-5.5*idx+2.0*ssidx],[i[0]/6.0+1.0/6,0.75-5.5*idx+2.0*ssidx],\
              [i[0]/6.0+2.0/6,0.75-5.5*idx+2.0*ssidx],[i[0]/6.0+1.0/6,-0.25-5.5*idx+2.0*ssidx]]
    hlx = plt.Polygon(points,fc=clr,ec='k',zorder=1)
    coords= hlx.get_xy()
    coord_set2.append(coords)

    for j in range((l-2)-1):
        if j % 2 == 0:
            points = [[i[0]/6.0+(1.0+j)/6,0.75-5.5*idx+2.0*ssidx],
                      [i[0]/6.0+(2.0+j)/6,0.75-5.5*idx+2.0*ssidx],
                      [i[0]/6.0+(3.0+j)/6,-0.75-5.5*idx+2.0*ssidx],
                      [i[0]/6.0+(2.0+j)/6,-0.75-5.5*idx+2.0*ssidx]]
            coord_set1.append(points+[points[0]])
            hlx = mpatch.Polygon(points,fc=bkg,zorder=0)

        else:
            points = [[i[0]/6.0+(1.0+j)/6,-0.75-5.5*idx+2.0*ssidx],
                      [i[0]/6.0+(2.0+j)/6,-0.75-5.5*idx+2.0*ssidx],
                      [i[0]/6.0+(3.0+j)/6,0.75-5.5*idx+2.0*ssidx],
                      [i[0]/6.0+(2.0+j)/6,0.75-5.5*idx+2.0*ssidx]]
            coord_set2.append(points+[points[0]])
            hlx = mpatch.Polygon(points,fc=clr,zorder=z)


    if (l-2-1)%2 == 1:

        points = [[i[1]/6.0-1.0/6,-0.75-5.5*idx+2.0*ssidx],[i[1]/6.0,-0.75-5.5*idx+2.0*ssidx],\
                  [i[1]/6.0+1.0/6,0.25-5.5*idx+2.0*ssidx],[i[1]/6.0,0.25-5.5*idx+2.0*ssidx]]

        coord_set2.append(points+[points[0]])
        hlx = mpatch.Polygon(points,fc=clr,zorder=0)

    else:
        points = [[i[1]/6.0-1.0/6,0.75-5.5*idx+2.0*ssidx],[i[1]/6.0,0.75-5.5*idx+2.0*ssidx],\
                  [i[1]/6.0+1.0/6,-0.25-5.5*idx+2.0*ssidx],[i[1]/6.0,-0.25-5.5*idx+2.0*ssidx]]
        coord_set1.append(points+[points[0]])

        hlx = plt.Polygon(points,fc=bkg,zorder=10)

def SS_breakdown(ss):
    
    i = 0
    curSS = ''
    jstart = -1
    jend = -1

    strand = []
    loop = []
    helix = []
    ssbreak = []

    ss_order = []
    ss_bounds = []

    last_ss = ''

    SS_equivalencies = {'H':['H'],
                        '-':['-'],
                        'S':[' ','S','C','T','G','I','P'],
                        ' ':[' ','S','C','T','G','I','P'],
                        'C':[' ','S','C','T','G','I','P'],
                        'T':[' ','S','C','T','G','I','P'],
                        'G':[' ','S','C','T','G','I','P'],
                        'I':[' ','S','C','T','G','I','P'],
                        'P':[' ','S','C','T','G','I','P'],
                        'E':['E','B'],
                        'B':['E','B']}

    cur_SSDict = {'H':'helix',
                  '-':'break',
                  'E':'strand',
                  'B':'strand'}

    for i in range(len(ss)):
        
        if i == 0:
            curSS = SS_equivalencies[ss[i]]
            jstart = i
            if ss[i] in cur_SSDict.keys():
                last_ss = cur_SSDict[ss[i]]
            else:
                last_ss = 'loop'
            continue

        if ss[i] in curSS:
            jend = i

        if ss[i] not in curSS or i == len(ss)-1:

            #print(i, ss[i],last_ss,curSS)
            
            if 'E' in curSS and jend-jstart+1 >= 3:
                strand.append((jstart,jend))
                ss_bounds.append((jstart,jend))
                ss_order.append('E')
                last_ss = 'strand'
            elif 'H' in curSS and jend-jstart+1 >=4:
                helix.append((jstart,jend))
                ss_bounds.append((jstart,jend))
                ss_order.append('H')
                last_ss = 'helix'
            elif ' ' in curSS and last_ss !='loop':
                if jend < jstart:
                    jend = jstart
                loop.append((jstart,jend))
                ss_bounds.append((jstart,jend))
                ss_order.append('L')
                #print(loop)
                last_ss = 'loop'
            elif '-' in curSS:
                if jend < jstart:
                    jend = jstart
                ssbreak.append((jstart,jend))
                #print(ssbreak)
                ss_bounds.append((jstart,jend))
                ss_order.append('B')
                last_ss = 'break'
            elif last_ss == 'loop':
                if jend < jstart:
                    jend = jstart
                if len(loop) > 0:
                    jstart = loop[-1][0]
                    loop = loop[0:-1]
                    ss_bounds = ss_bounds[0:-1]
                    ss_order = ss_order[0:-1]
                    #print(loop)
                loop.append((jstart,jend))
                ss_bounds.append((jstart,jend))
                ss_order.append('L')
                #print(loop)
                last_ss = 'loop'
            else:
                if jend < jstart:
                    jend = jstart
                loop.append((jstart,jend))
                ss_bounds.append((jstart,jend))
                ss_order.append('L')
                last_ss = 'loop'

            jstart = i
            curSS = SS_equivalencies[ss[i]]
    return strand,loop,helix, ssbreak, ss_order, ss_bounds


def updateSS(ss,seq,alignment):

    ss_u = ''

    j = 0

    for i in range(len(alignment)):
        if alignment[i] == '-':
            ss_u += '-'
        else:
            ss_u += ss[j]
            j += 1
            #if j == len(ss):  # check if reached the end of secondary structure annotation
            #    return ss_u

    return ss_u


def SS_align(alignment,ID,seq,ss,start_subregion=None,end_subregion=None):

    a_seq = ''
    seq_found = 0
    
    for i in alignment:

        if seq_found and i[0] == '>':
            break

        if i[0] == '>' and bool(re.search(ID.lower(), i.lower())):
            seq_found = 1
            continue

        if seq_found and i[0] != '>':
            a_seq += i
    
    '''if start_subregion:
        a_seq = a_seq[start_subregion:]
    if end_subregion:
        a_seq = a_seq[:end_subregion+1]'''
    i_start = 0
    i_end = len(a_seq)-1   
    if start_subregion:
        i_start = start_subregion
    if end_subregion:
        i_end = end_subregion 
    a_seq = a_seq[i_start:i_end+1]

    a = pairwise2.align.localxs(seq,a_seq,-1,-0.5)

    # check if the dssp annotation has any extra residues not in the fasta alignment
    if a[0][1] != a_seq:
        print("extra residues found\n")

    # check how many gap marks are at the end and beginning of the original alignment
    # (a_seq) and compare to the amount found in a[0][1]
    a_seq_gaps = [0,0]
    new_aln_gaps = [0,0]
    for i in range(len(a_seq)):
        if a_seq[i] == "-":
            a_seq_gaps[0] += 1
        else:
            break
    for i in range(len(a_seq)-1, -1, -1):
        if a_seq[i] == "-":
            a_seq_gaps[1] += 1
        else:
            break

    for i in range(len(a[0][1])):
        if a[0][1][i] == "-":
            new_aln_gaps[0] += 1
        else:
            break
    for i in range(len(a[0][1])-1, -1, -1):
        if a[0][1][i] == "-":
            new_aln_gaps[1] += 1
        else:
            break

    extra_gaps = [new_aln_gaps[0]-a_seq_gaps[0], new_aln_gaps[1]-a_seq_gaps[1]]

    SS_updated = updateSS(ss,seq,a[0][0])

    SS_updated_new = gap_sequence(SS_updated, extra_gaps)
    a_new = gap_sequence(a[0][1], extra_gaps)

    return SS_updated_new, a_new, extra_gaps, i_start, i_end

    if extra_gaps[1] != 0:
        SS_updated_new = SS_updated[:-extra_gaps[1]]
        a_new = a_new[:-extra_gaps[1]]

    return SS_updated_new[extra_gaps[0]:], a_new[extra_gaps[0]:],extra_gaps,i_start,i_end

def plot_coords(coords,z=10):

    coords_f1, instructions1 = coords2path(coords)

    path = mpath.Path(np.array(coords_f1),np.array(instructions1))
    patch = mpatch.PathPatch(path, facecolor='none',zorder=z)
    plt.gca().add_patch(patch)
    im = plt.imshow(mat,extent=[0.0,sz,0.5,3.0],cmap=CMAP,interpolation='none')
    im.set_clip_path(patch)
            
def run_dssp(pdb_path, id, chain):  

    ss_seq = ""
    aa_seq = ""

    p = PDBParser()
    structure = p.get_structure(id, pdb_path)
    model = structure[0]
    dssp = DSSP(model, pdb_path)
    a_key = list(dssp.keys())
    for key in a_key:
        if key[0] == chain:
            aa_seq+=dssp[key][1] 
            if dssp[key][2] == "-":
                ss_seq+="C"
            else:      
                ss_seq+=dssp[key][2]
      
    #sys.exit()
    return [ss_seq,aa_seq]

def convert2horiz(dssp_file):
    ss_seq = ""
    aa_seq = ""

    with open(dssp_file, "r") as f:
        lines = f.readlines()

    start_read = False
    for line in lines:
        if start_read:
            if line[13] == "!":
                start_read = False
                continue
            ss_seq += line[16]
            aa_seq += line[13]
        if line.split()[0] == "#":
            start_read = True

    return [ss_seq,aa_seq]

def score_column(msa_col, threshold=0):

    blosum62 = substitution_matrices.load("BLOSUM62")
    # find consensus of the column
    aa_count = {"A": 0, "R": 0, "N": 0, "D": 0, "C": 0, "Q": 0, "E": 0,
                "G": 0, "H": 0, "I": 0, "L": 0, "K": 0, "M": 0, "F": 0,
                "P": 0, "S": 0, "T": 0, "W": 0, "Y": 0, "V": 0}
    for i in msa_col:
        try:
            aa_count[i] += 1
        except:
            pass
    consensus_aa = max(zip(aa_count.values(), aa_count.keys()))[1]

    conservation_count = 0
    for i in msa_col:
        if i in aa_count.keys():
            if blosum62[consensus_aa][i] >= 0:
                conservation_count += 1
    
    return conservation_count/len(msa_col)

def gap_sequence(seq, extra_gaps):
    # seq can be a list or a string, anything that can be indexed
    # extra gaps is a list of length two [x,y],
    # where x is the number of characters to remove from the beginning
    # and y the number of characters to remove from the end
    new_seq = seq
    if extra_gaps[1] != 0:
        new_seq = new_seq[:-extra_gaps[1]]
    return new_seq[extra_gaps[0]:]

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="(required) alignment file in fasta format")
    parser.add_argument("-p", help="(required) pdb file")
    parser.add_argument("-o", help="(required) name for output file")
    parser.add_argument("-n", help="(required) id of the protein in the alignment file")
    parser.add_argument("--dssp", default=None, help="secondary structure annotation in DSSP format. If this option is not provided, SSDraw will compute secondary structure from the given PDB file with DSSP.")
    parser.add_argument("--chain_id", default="A", help="chain id to use in pdb. Defaults to the first chain.")
    parser.add_argument("--color_map", default=["inferno"], nargs="*", help="color map to use for heat map")
    parser.add_argument("--scoring_file",default=None,help="custom scoring file for alignment")
    parser.add_argument("--color", default="white", help="color for the image. Can be a color name (eg. white, black, green), or a hex code")
    parser.add_argument("-conservation_score", action='store_true', help="score alignment by conservation score")
    parser.add_argument("--output_file_type", default="png")
    parser.add_argument("-bfactor", action='store_true', help="score by b factor")
    parser.add_argument("-mview", action="store_true", help="color by mview color map")
    parser.add_argument("--dpi", default=600, help="dpi to use for final plot")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)

    args = parser.parse_args()

    try:
        args.aln = args.f
        args.pdb = args.p
        args.output = args.o
        args.name = args.n
    except:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # preface run
    id = args.name  
    chain_id = args.chain_id
    print("\n\nRunning for: "+id)

    pdbseq = ''
    if args.dssp:
        # get secondary structure from pre-existing DSSP annotation
        f = convert2horiz(args.dssp)
        pdbseq = f[1]
    else:
        # run the dssp executable
        f = run_dssp(args.pdb, id, chain_id) 
        # read in amino acid sequence from PDB
        p = PDBParser()
        bfactors = []
        structure = p.get_structure(id, args.pdb)
        model = structure[0]
        for chain in model:
            if chain.get_id() == args.chain_id:
                
                for residue in chain:
                    for atom in residue:
                        if atom.name == "CA":
                            bfactors.append(atom.bfactor)
                            pdbseq += seq1(residue.get_resname())
                            break

    nlines = 1

    salign = open(args.aln).read().splitlines() 

    if args.start != None and args.end != None:
        if int(args.start) >= int(args.end):
            raise Exception("Your start location cannot be greater than the end location")
    if args.start != None:
        args.start = int(args.start)
    if args.end != None:
        args.end = int(args.end)

    #####Align secondary structure to match input sequence alignment

    ss_wgaps,seq_wgaps,extra_gaps,i_start,i_end = SS_align(salign,args.name,f[1],f[0],args.start,args.end)

    #Parse color
    #Select colormap
    CMAP = ""
    if args.color in mcolors.BASE_COLORS.keys() or args.color in mcolors.CSS4_COLORS.keys() or args.color in mcolors.XKCD_COLORS.keys():
        CMAP = ListedColormap([args.color])
    elif args.color[0] == "#":
        CMAP = ListedColormap([args.color])
    if args.conservation_score or args.bfactor or args.scoring_file:
        if len(args.color_map) == 1:
            CMAP = args.color_map[0]
        else:
            CMAP = ListedColormap(args.color_map)
    
    # custom color map
    #CMAP = ListedColormap(["black","red", "orange"])

    #bvals are to make the colormap; taken from input PDB
    bvals = []

    #Break down secondary structure classifications in to continuous
    #chunks of helix, strand, and coil
    SS = ss_wgaps

    strand,loop,helix,ss_break,ss_order,ss_bounds = SS_breakdown(SS)
    
    pres = 0
    msa = AlignIO.read(open(args.aln), "fasta")
    if args.start != None and args.end != None:
        msa = [a[args.start:args.end+1] for a in msa]
    elif args.start != None:
        msa = [a[args.start:] for a in msa]
    elif args.end != None:
        msa = [a[:args.end+1] for a in msa]
    
    if args.mview:
        #pdbseq = f[1]
        mview_colors = {"A": 0, "G": 0, "I": 0, "L": 0, "M": 0, "P": 0, "V": 0,
                        "F": 1, "H": 1, "W": 1, "Y": 1,
                        "K": 2, "R": 2,
                        "D": 3, "E": 3,
                        "S": 4, "T": 4,
                        "N": 5, "Q": 5,
                        "C": 6}
        mview_colors_hit = [0,0,0,0,0,0,0]

        mview_color_map = ["#33cc00","#009900","#cb0000","#0133ff","#0299fe","#6601cc","#ffff00","#808080"]

        for i in range(len(seq_wgaps)):
            try:
                m = mview_colors[seq_wgaps[i]]
                bvals.append(m)
                mview_colors_hit[m]+=1
            except:
                bvals.append(7)

        for i in range(len(mview_colors_hit)): # remove colors of residues not in sequence
            if mview_colors_hit[i] == 0:
                mview_color_map.pop(i)
                for j in range(len(bvals)):
                    if bvals[j] > i:
                        bvals[j] -= 1

        CMAP = ListedColormap(mview_color_map)
        #print(len(bvals))

    elif args.scoring_file: # use custom scoring by residue
        # read in scoring file
        bvals_tmp = []
        scoring_seq = ""
        with open(args.scoring_file, "r") as g:
            lines = g.readlines()
        for line in lines:
            #pdbseq+=line.split()[0]
            scoring_seq += line.split()[0]
            bvals_tmp.append(float(line.split()[1]))

        score_align = pairwise2.align.localxs(pdbseq,scoring_seq,-1,-0.5)
        #print(score_align[0])
        #sys.exit()
        j = 0
        for i in range(len(score_align[0][1])):
            if score_align[0][0][i] != "-":
                if score_align[0][1][i] != "-":
                    bvals.append(bvals_tmp[j])
                    j+=1
                else:
                    bvals.append(min(bvals_tmp))


    elif args.bfactor:  # score by bfactor
        bvals = [b for b in bfactors]
        '''p = PDBParser()
        structure = p.get_structure(id, args.pdb)
        model = structure[0]
        for chain in model:
            if chain.get_id() == args.chain_id:
                
                for residue in chain:
                    for atom in residue:
                        if atom.name == "CA":
                            bvals.append(atom.bfactor)
                            #pdbseq += seq1(residue.get_resname())
                            break'''
        j = 0
        '''
        The below code is just to test bfactor option
        for pdbs where the bfactors are all zero
        '''
        new_bvals = []
        for i in range(len(bvals)):
            new_bvals.append((bvals[i]+j)%7)
            j+=1
        bvals = new_bvals

  
    elif args.conservation_score: # score by conservation score     
        #pdbseq = f[1]
        bvals = []
        for i in range(len(msa[0])):
            bvals.append(score_column([msa[j][i] for j in range(len(msa))]))

    else:
        # solid color
        #pdbseq = f[1]
        bvals = [i for i in range(len(msa[0]))]


    #Align PDB sequence with dssp sequence
    pdbalign = pairwise2.align.localxs(pdbseq,f[1],-1,-0.5)

    print(len(pdbseq))
    print(len(bvals))
    print(len(msa[0]))
    #sys.exit()

    # case 1:
    # len(bvals) == len(msa) if bvals were scored by alignment position
    # in this case, don't need to do anything else
    # 
    # case 2:
    # len(bvals) == len(pdbseq) if bvals were scored by aa residue

    # what's left to do:
    # truncate pdbseq and bvals by extra_gaps DONE
    # then change the following if statement to realign by-residue bvals to the MSA DONE
    # replace clunky stuff in code with gap_sequence function

    if len(bvals) == len(pdbseq):
        # remove extra residues
        pdbseq = gap_sequence(pdbseq, extra_gaps)
        bvals = gap_sequence(bvals, extra_gaps)

        fstring = []
        bvalsf = []
        fidx = 0
        pidx = 0
        ninsert = 0
        n = 0
        o = 0
        j = 0
        for i in range(len(ss_order)):
            #Make secondary structure chunk
            fstring += [ss_order[i]]*(ss_bounds[i][1]-ss_bounds[i][0]+1)
            #If chunk is a chain break, assign each break to the lowest B-factor
            #Else assign each position of aligned secondary structure to its respective
            #CA B-factor and iterate through list of B-factors so that register is
            #maintained
            if ss_order[i] == 'B':
                bvalsf += [min(bvals)]*(ss_bounds[i][1]-ss_bounds[i][0]+1)

            else:
                bvalsf += bvals[j:j+ss_bounds[i][1]-ss_bounds[i][0]+1]
                j += ss_bounds[i][1]-ss_bounds[i][0]+1
        
        bvals = bvalsf

    always_false = False
    if always_false:
    #if len(bvals) < len(msa[0]):
        # some scoring systems are by residue, so we need to align
        # by-residue bvalues to the multiple sequence alignment

        # first, align bvalues to dssp
        bvals2 = []
        j = 0
        '''for i in range(len(pdbalign[0][0])):
            if pdbalign[0][0][i] != '-':
                bvals2.append(bvals[j])
                j += 1
            elif pdbalign[0][1][i] != '-':
                bvals2.append(min(bvals))'''
        
        # align bvalues to seq_wgaps
        '''for i in range(len(seq_wgaps)):
            if seq_wgaps[i] != '-':
                bvals2.append(bvals[j])
            else:
                bvals2.append(min(bvals))'''

        '''bvals = bvals2[extra_gaps[0]:]
        if extra_gaps[1] != 0:
            bvals = bvals[:-extra_gaps[1]]'''
        # this above code doesn't work.
        # if there are extra gaps, generally len(bvals) will not even
        # be larger than len(msa), so this if statement won't even be true.

        fstring = []
        bvalsf = []
        fidx = 0
        pidx = 0
        ninsert = 0
        n = 0
        o = 0
        j = 0
        for i in range(len(ss_order)):
            #Make secondary structure chunk
            fstring += [ss_order[i]]*(ss_bounds[i][1]-ss_bounds[i][0]+1)
            #If chunk is a chain break, assign each break to the lowest B-factor
            #Else assign each position of aligned secondary structure to its respective
            #CA B-factor and iterate through list of B-factors so that register is
            #maintained
            if ss_order[i] == 'B':
                bvalsf += [min(bvals)]*(ss_bounds[i][1]-ss_bounds[i][0]+1)

            else:
                bvalsf += bvals[j:j+ss_bounds[i][1]-ss_bounds[i][0]+1]
                j += ss_bounds[i][1]-ss_bounds[i][0]+1
        
        bvals = bvalsf

    mat = np.tile(NormalizeData(bvals), (100,1))

    #set figure parameters
    sz = 0
    c = 'none'
    bc = 'none'
    sz = 0

    #set sizes of SS chunks
    ss_prev = 0
    for i in range(len(ss_order)):
        
        #print ((ss_bounds[i],ss_order[i],ss_bounds[i][0]/6.0,ss_bounds[i][0]/6.0-ss_prev))

        if ss_order[i] == 'H':
            ss_prev = ss_bounds[i][1]/6.0+1/6.0
        else:
            ss_prev = ss_bounds[i][1]/6.0

    if ss_order[-1] == 'H':
        sz = ss_bounds[-1][1]/6.0+1/6.0
    elif ss_order[-1] == 'E':
        sz = ss_bounds[-1][1]/6.0
    elif ss_order[-1] == 'L':
        sz = (ss_bounds[-1][1])/6.0
    elif ss_order[-1] == 'B':
        sz = (ss_bounds[-1][1])/6.0


    #Plot secondary structure chunks
    strand_coords = []
    loop_coords = []
    helix_coords1 = []
    helix_coords2 = []

    fig, ax = plt.subplots(ncols=1, figsize=(25,2+1.5*(nlines-1)))
    
    '''    for i in range(len(ss_order)):
        if ss_order[i] == 'L':
            pass
            build_loop(ss_bounds[i],0,1,len(SS),1,loop_coords,z=0,clr=c,mat=mat,size=sz)'''

    for i in range(len(ss_order)):

        prev_ss = None
        next_ss = None
        if i != 0:
            prev_ss = ss_order[i-1]
        if i != len(ss_order)-1:
            next_ss = ss_order[i+1]

        if ss_order[i] == 'L':
            pass
            build_loop(ss_bounds[i],0,1,len(SS),1,loop_coords,prev_ss,next_ss,z=0,clr=c,mat=mat,size=sz)
        elif ss_order[i] == 'H':
            build_helix(ss_bounds[i],0,1,helix_coords1,helix_coords2,z=i,clr=c,bkg=bc,imagemat=mat,size=sz)
        elif ss_order[i] == 'E':
            pass
            build_strand(ss_bounds[i],0,1,strand_coords,next_ss,z=i,clr=c,imagemat=mat,size=sz)

    if len(strand_coords) != 0:
        plot_coords(strand_coords)
    if len(helix_coords1) != 0 and len(helix_coords2) != 0:
        plot_coords(helix_coords1,z=0)
        plot_coords(helix_coords2)

    plt.ylim([0.5,3])

    plt.axis('off')
    ax.set_aspect(0.5)

    #rcParams['font.family'] = 'monospace'
    #rcParams['font.size'] = 9.65 # for ubiquitin
    #plt.annotate(seq_wgaps, [0,0.5])
    #plt.annotate(ss_wgaps, [0,3])
    #rcParams['font.size'] = 20 # for id label
    #plt.annotate(id, [0,1.5])
    print(ss_order)
    print(ss_bounds)
    #print(len(ss_order))
    #print(len(ss_bounds))
    #sys.exit()
        
    plt.savefig(args.output+'.'+args.output_file_type,bbox_inches='tight',dpi=int(args.dpi),transparent=True)