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


def parse_reaction(reaction, mol_files):
    x_coordinates = []
    y_coordinates = []
    all_reactions = {}
    arrows = reaction["s"]
    arrows_x_coor = [(i['x1'], i['x2']) for i in arrows]
    arrows_y_coor = [(i['y1'], i['y2']) for i in arrows]

    def get_coor(axis, a_list):
        for i in range(len(reaction['m'])):
            bonds = reaction['m'][i]['a']
            c = [round(bond[axis], 3) for bond in bonds]
            a_list.append(sorted(c)[-1])
        return
    get_coor("x", x_coordinates)
    get_coor("y", y_coordinates)
    for num, coor in enumerate(arrows_x_coor):
        d = {}
        substrates = []
        reactants = []
        products = []
        for index, mol_coor in enumerate(x_coordinates):
            if mol_coor < coor[0]:
                substr = mol_to_chemfig(mol_files[index])
                substrates.append(substr)
                d['substrates'] = substrates
            elif mol_coor > coor[1]:
                prod = mol_to_chemfig(mol_files[index])
                products.append(prod)
                d['products'] = products
            elif coor[0] < mol_coor < coor[1]:
                if y_coordinates[index] < max(arrows_y_coor[num]):
                    d['reactants'] = {'above': mol_to_chemfig(mol_files[num])}
                else:
                    d['reactants'] = {'below': mol_to_chemfig(mol_files[num])}
            all_reactions['reaction' + str(num + 1)] = d
    return all_reactions


@mol_2_chemfig.route('/convert_reaction', methods=["POST", "GET"])
def convert_reaction():
    mol_files = request.json['MOLFiles']
    reaction = json.loads(request.json['reaction'])
    d = parse_reaction(reaction, mol_files)
    # arrow_types = [reaction["s"][i]["a"] for i in range(len(reaction["s"]))]
    add_sign = "\+{1em, 1em, -2em}"

    def get_compounds(a_list):
        compounds = ""
        for mol in a_list:
            compounds +=  mol + '\n' + add_sign + '\n'
        return compounds[: len(compounds) - len(add_sign) - 1].strip()
    s = ''
    for r in d.keys():
        s += get_compounds(d[r]['substrates'])
        s += "\n" + arrow
        s += get_compounds(d[r]['products'])
    print s
    latex_template = latex_begins + start + s + latex_ends
    txt_latex = start + s + latex_ends
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
start = '\schemestart[0,2,thick]' + '\n'
arrow = "\\arrow{}" + '\n'
latex_ends = "\n" + "\schemestop" + '\n' + "\end{center}" + "\n" + "\\vspace*{\\fill}" + "\n" + "\end{document}"
