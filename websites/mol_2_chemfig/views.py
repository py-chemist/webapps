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


def group_reaction(arrows_coor, compounds_coor):
    """
    Return a list of grouped staring materials and products
    of a multistep reaction
    """

    grouped = []
    comp_string = ' '.join(str(i) for i in compounds_coor)
    for i in arrows_coor:
        s1, s2 = comp_string.split(str(i))
        grouped.append(s1.strip().split())
        comp_string = s2
        if i == arrows_coor[-1]:
            grouped.append(s2.strip().split())

    return [[float(x) for x in n] for n in grouped]


def add_plus_sign(a_list, all_compounds):
    all_pairs = []
    for i in a_list:
        if len(i) > 1:
            compounds = ""
            for x in i:
                compounds += dict(all_compounds)[x] + '\n' + add_sign + '\n'
                chemfig = compounds[: len(compounds) - len(add_sign) - 1].strip()
                all_pairs.append((x, chemfig))
    return all_pairs


def parse_reaction(reaction, mol_files, text_arrow):
    all_compounds_x = []
    # Get x coordinates and chemfig format for all compounds in the raction
    get_all_compounds("x", all_compounds_x, reaction,  mol_files)
    all_compounds_x = sorted(all_compounds_x)
    print all_compounds_x
    all_arrows = reaction["s"]
    # Get x coordinates of all arrows
    arrows_x_coor = [(i['x1'], i['x2']) for i in all_arrows]
    arrows_coor_chemfig = []
    first_x_coor_arrow = [get_round(i['x1']) for i in all_arrows]
    # get chemfig format for arrows
    for i in [n[0] for n in arrows_x_coor]:
        arrows_coor_chemfig.append((get_round(i), arrow))
    # sort all comnpounds and arrows by first x coordinate
    final = sorted(all_compounds_x + arrows_coor_chemfig)
    first_x_coor_reaction = [i[0] for i in final]
    g = group_reaction(first_x_coor_arrow, first_x_coor_reaction)
    add_plus_sign(g, all_compounds_x)
    # get chemfig format for a whole reaction
    final_chemfig = [i[1] for i in final]
    reactions_chemfig = ''.join(i for i in final_chemfig)
    return reactions_chemfig


@mol_2_chemfig.route('/convert_reaction', methods=["POST", "GET"])
def convert_reaction():
    mol_files = request.json['MOLFiles']
    reaction = json.loads(request.json['reaction'])
    input_text = request.json['input_text']
    d = parse_reaction(reaction, mol_files, input_text)
    latex_template = latex_begins + start + d + latex_ends
    txt_latex = start + d + stop
    with open(folder + latex_file, 'w') as f:
        f.write(latex_template)
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
add_sign = "\+{1em, 1em, -2em}"
start = '\schemestart[0,2,thick]' + '\n'
arrow = '\n' + "\\arrow{}" + '\n'
stop = "\n" + "\schemestop"
latex_ends = "\n" + "\schemestop" + '\n' + "\end{center}" + "\n" + "\\vspace*{\\fill}" + "\n" + "\end{document}"
