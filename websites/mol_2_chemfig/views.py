from flask import Blueprint, render_template, jsonify, request
import forms
from chemistry.chemfig import smiles_mol_to_chemfig, get_smiles, update_chemfig
import re
import json
import os
import base64

MOL_FILE = 'websites/mol_2_chemfig/static/molecule.mol'
REACTION = 'websites/mol_2_chemfig/static/reaction.mol'

mol_2_chemfig = Blueprint('mol_2_chemfig', __name__,
                          template_folder='templates',
                          static_folder="static")


@mol_2_chemfig.route('/')
def main():
    form = forms.HomePageForm()
    checkboxes = forms.get_checkboxes_data()
    menu_links = forms.get_menu_links()
    return render_template("mol_2_chemfig/home.html", form=form,
                           checkboxes=checkboxes,
                           menu_links=menu_links)


@mol_2_chemfig.route('/links')
def links():
    return render_template('mol_2_chemfig/links.html')


@mol_2_chemfig.route('/about')
def about():
    return render_template('mol_2_chemfig/about.html')


@mol_2_chemfig.route('/get_smiles', methods=['POST', "GET"])
def get_data():
    chemical = request.json['chemical']
    smiles = get_smiles(chemical)
    return jsonify(smiles=smiles)


@mol_2_chemfig.route('/smiles_to_chemfig', methods=['POST', "GET"])
def smiles_to_chemfig():
    data = request.json
    if data['smiles_mol'] == "smiles":
        chemfig, pdflink = smiles_mol_to_chemfig("-w",
                                                 '-i direct',
                                                 data["data"])
    else:
        with open(MOL_FILE, 'w') as f:
            f.write(str(data["data"]))
        chemfig, pdflink = smiles_mol_to_chemfig("-w", MOL_FILE)
    return jsonify(chemfig=chemfig, pdflink=pdflink)


@mol_2_chemfig.route('/apply', methods=['POST', "GET"])
def apply():
    remove, inline = None, None
    data = request.json
    chbx = ' '.join(data['chbx'])
    all_args = chbx + " -a " + data['angle']
    smi_mol = data["last_content"]
    if '-rm' in all_args:
        args_list = all_args.split()
        all_args = ' '.join([i for i in args_list if i != '-rm'])
        remove = True
    elif '-j' in all_args:
        args_list = all_args.split()
        all_args = ' '.join([i for i in args_list if i != '-j'])
        inline = True
    if smi_mol == "smiles":
        chemfig, pdflink = smiles_mol_to_chemfig(all_args,
                                                 '-i direct',
                                                 "-y {}".format(data["hydrogens"]),
                                                 smi_mol)
    else:
        with open(MOL_FILE, 'w') as f:
            f.write(smi_mol)
        chemfig, pdflink = smiles_mol_to_chemfig(all_args,
                                                 "-y {}".format(data["hydrogens"]),
                                                 MOL_FILE)
    text = re.sub('\%.+', '', str(chemfig))
    if remove:
        chemfig = text
    if inline:
        chemfig = ''.join(text.split())
    return jsonify(chemfig=chemfig, pdflink=pdflink)


@mol_2_chemfig.route('/update', methods=["POST", "GET"])
def update():
    data = request.json
    smiles_mol = request.args.get("smiles_mol")
    pdflink = update_chemfig(smiles_mol)
    return jsonify(pdflink=pdflink)

############
# Reaction #
############


folder = 'websites/mol_2_chemfig/static/'
latex_file = 'reaction.tex'
path = folder + latex_file
latexcmd = 'pdflatex -interaction=nonstopmode %s > /dev/null' % path


@mol_2_chemfig.route('/reaction')
def reaction():
    return render_template('mol_2_chemfig/reaction.html')


def mol_to_chemfig(mol_format):
    with open(REACTION, 'w') as f:
        f.write(mol_format)
    chemfig, pdflink = smiles_mol_to_chemfig("-w", REACTION)
    return chemfig


def get_round(n):
    return round(n, 3)


def get_all_compounds(axis, a_list, reaction, mol_files):
    for i in range(len(reaction['m'])):
        bonds = reaction['m'][i]['a']
        c = sorted([get_round(bond[axis]) for bond in bonds])[-1]
        a_list.append((c, mol_to_chemfig(mol_files[i])))


def parse_reaction(reaction, mol_files, text_arrow):
    all_compounds_x = []
    all_compounds_y = []
    get_all_compounds("x", all_compounds_x, reaction,  mol_files)
    get_all_compounds("y", all_compounds_y, reaction,  mol_files)
    above_below = []
    above_below2 = []
    above_arrow = []
    below_arrow = []
    arrows = []
    print([i[0] for i in all_compounds_y])
    all_arrows = reaction["s"]
    arrows_x_coor = [(i['x1'], i['x2']) for i in all_arrows]
    arrows_y_coor = [(i['y1'], i['y2']) for i in all_arrows]
    print(arrows_y_coor)
    all_compounds_x = sorted(all_compounds_x)
    for num, x_mol in enumerate(all_compounds_x):
        for index, ar_x in enumerate(arrows_x_coor):
            if ar_x[0] < x_mol[0] < ar_x[1]:
                print all_compounds_y[num][0], arrows_y_coor[index][0], index
                if all_compounds_y[num][0] < arrows_y_coor[index][0]:
                    below_arrow.append((index, x_mol[1]))
                elif all_compounds_y[num][0] > arrows_y_coor[index][0]:
                    above_arrow.append((index, x_mol[1]))                
                # if all_compounds_y[num] < arrows_y_coor[index][0]:
                #     above_below = "\\arrow{->[%s]}" % x_mol[1] + '\n'
                # elif all_compounds_y[num] > arrows_y_coor[index][0]:
                #     above_below = "\\arrow{->[][%s]}" % x_mol[1] + '\n'
                # above_arrow.append((get_round(ar_x[1]), above_below))
                above_below2.append(x_mol[0])
    print above_arrow, "============"
    print below_arrow, "++++++++++++"
    compounds = [i for i in all_compounds_x if i[0] not in above_below2]
    #print compounds
    # print "above arrow", above_arrow
    # print "above_arrow2", above_arrow2
    for i in [n[1] for n in arrows_x_coor]:
        #print get_round(i), "----------"
        if get_round(i) not in [m[0] for m in above_arrow]:
            #print "i", i
            arrows.append((get_round(i), arrow))
    # print "arrows", arrows
    final = sorted(above_below + compounds + arrows)
    final = [i[1] for i in final]
    # print "final", final
    reactions_chemfig = ''.join(i for i in final)
    return reactions_chemfig


@mol_2_chemfig.route('/convert_reaction', methods=["POST", "GET"])
def convert_reaction():
    mol_files = request.json['MOLFiles']
    reaction = json.loads(request.json['reaction'])
    input_text = request.json['input_text']
    d = parse_reaction(reaction, mol_files, input_text)
    add_sign = "\+{1em, 1em, -2em}"

    def get_compounds(a_list):
        compounds = ""
        for mol in a_list:
            compounds +=  mol + '\n' + add_sign + '\n'
        return compounds[: len(compounds) - len(add_sign) - 1].strip()
    latex_template = latex_begins + start + d + latex_ends
    txt_latex = start + d + stop
    with open(folder + latex_file, 'w') as f:
        f.write(latex_template)
    # os.chdir("/home/py-chemist/Projects/websites/websites/mol_2_chemfig/static")
    # print(os.curdir, "+++++++++++++++++++")
    os.system(latexcmd)
    pdf_string = open('reaction.pdf').read()
    encoded = base64.encodestring(pdf_string)
    pdflink = "data:application/pdf;base64,{}".format(encoded)
    return jsonify(data=txt_latex, pdflink=pdflink)


latex_begins = r"""
\documentclass{minimal}
\usepackage{xcolor, chemfig, mol2chemfig}
\usepackage[paperheight=5cm, paperwidth=25cm]{geometry}
\usepackage{amsmath}
\setatomsep{2em}
\setbondoffset{1pt}
\setdoublesep{3pt}
\setbondstyle{line width=1pt}

\begin{document}
\vspace*{\fill}
\vspace{-4pt}
\begin{center}""" + '\n'
start = '\schemestart[0,2,thick]' + '\n'
arrow = "\\arrow{}" + '\n'
stop = "\n" + "\schemestop"
latex_ends = "\n" + "\schemestop" + '\n' + "\end{center}" + "\n" + "\\vspace*{\\fill}" + "\n" + "\end{document}"
