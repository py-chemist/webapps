from flask import Blueprint, render_template, jsonify, request, redirect, url_for
import forms
from chemistry.chemfig import smiles_mol_to_chemfig, get_smiles, update_chemfig
import re
import json
import os
import base64

MOL_FILE = 'webapps/mol_2_chemfig/static/molecule.mol'
REACTION = 'webapps/mol_2_chemfig/static/reaction.mol'
pdflink = "static/files/welcome.png"

mol_2_chemfig = Blueprint('mol_2_chemfig', __name__,
                          template_folder='templates',
                          static_folder="static")


@mol_2_chemfig.route('/')
def to_home():
    return redirect(url_for('mol_2_chemfig.home'))
    
    
@mol_2_chemfig.route('/home')
def home():
    form = forms.HomePageForm()
    checkboxes = forms.get_checkboxes_data()
    menu_links = forms.get_menu_links()
    return render_template("mol_2_chemfig/home.html", form=form,
                           checkboxes=checkboxes,
                           menu_links=menu_links,
                           pdflink=pdflink)


@mol_2_chemfig.route('/links')
def links():
    return render_template('mol_2_chemfig/links.html')


@mol_2_chemfig.route('/tutorial')
def tutorial():
    return render_template('mol_2_chemfig/tutorial.html')


@mol_2_chemfig.route('/contact')
def contact():
    return render_template('mol_2_chemfig/contact.html')


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
    smiles_mol = request.args.get("smiles_mol")
    pdflink = update_chemfig(smiles_mol)
    return jsonify(pdflink=pdflink)

############
# Reaction #
############


folder = 'webapps/mol_2_chemfig/static/'
latex_file = 'reaction.tex'
path = folder + latex_file
latexcmd = 'pdflatex -interaction=nonstopmode %s > /dev/null' % path


@mol_2_chemfig.route('/reaction')
def reaction():
    return render_template('mol_2_chemfig/reaction.html')


def mol_to_chemfig(mol_format, options):
    with open(REACTION, 'w') as f:
        f.write(mol_format)
    chemfig, pdflink = smiles_mol_to_chemfig(' '.join(options), REACTION)
    return chemfig


def get_round(n):
    return round(n, 3)


def get_all_compounds(axis, reaction, mol_files, options):
    d = {}
    for i in range(len(reaction['m'])):
        bonds = reaction['m'][i]['a']
        c = sorted([get_round(bond[axis]) for bond in bonds])[-1]
        d[c] = mol_to_chemfig(mol_files[i], options)
    return d


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
    """
    Add plus sign between 2 or more starting materils or products
    """
    all_pairs = []
    for i in a_list:
        if len(i) > 1:
            for x in i:
                compound = ""
                if x == i[-1]:
                    compound += all_compounds[x]
                    all_pairs.append((x, compound))
                else:
                    compound += all_compounds[x] + '\n' + add_sign + '\n'
                    all_pairs.append((x, compound))
    return all_pairs


def parse_arrow_text(arrow_text, num_of_arrows):
    """
    Return a list of arrows with text above and below the arrows
    """
    filled_arrows = []
    if arrow_text:
        text_by_arrow = arrow_text.split('|')
        above_bllow_all = [i.split(";") for i in text_by_arrow]
        for text in above_bllow_all:
            if len(text) == 2:
                if text[0] == '':
                    arrow = '\n' + "\\arrow{->[]%s}" % ('[' + text[1] + ']') + '\n'
                    filled_arrows.append(arrow)
                elif text[0] and text[1]:
                    arrow = '\n' + "\\arrow{->%s}" % ('['+text[0]+']'+'['+text[1]+']') + '\n'
                    filled_arrows.append(arrow)
            elif len(text) == 1:
                if text[0]:
                    arrow = '\n' + "\\arrow{->%s}" %('[' + text[0] + ']') + '\n'
                elif text[0] == '':
                    arrow = '\n' + "\\arrow{}" + '\n'
                filled_arrows.append(arrow)
        if len(text_by_arrow) < len(num_of_arrows):
            arrow = '\n' + "\\arrow{}" + '\n'
            for _ in range(len(num_of_arrows) - len(text_by_arrow)):
                filled_arrows.append(arrow)
    else:
        arrow = '\n' + "\\arrow{}" + '\n'
        for _ in range(len(num_of_arrows)):
            filled_arrows.append(arrow)
    return filled_arrows


@mol_2_chemfig.route('/parse_input_text', methods=["POST"])
def parse_text():
    input_text = request.json['input_text']
    if "|" not in input_text:
        input_text += "|"
    text_by_arrow = input_text.split('|')
    above_bllow_all = [i.split(";") for i in text_by_arrow]
    return jsonify(splitted_text=above_bllow_all)


def parse_reaction(reaction, mol_files, text_arrow, options):
    all_compounds = get_all_compounds("x", reaction,  mol_files, options)
    all_arrows = reaction["s"]
    first_x_coor_arrow = [get_round(i['x1']) for i in all_arrows]
    all_x_coord = sorted(all_compounds.keys() + first_x_coor_arrow)
    grouped = group_reaction(first_x_coor_arrow, all_x_coord)
    all_pairs = add_plus_sign(grouped, all_compounds)
    for pair in all_pairs:
        all_compounds[pair[0]] = pair[1]
    arrows_text = parse_arrow_text(text_arrow, first_x_coor_arrow)
    arrows_chemfig = [(i, arrows_text[num]) for num, i in enumerate(first_x_coor_arrow)]
    complete_reaction = sorted(all_compounds.items() + arrows_chemfig)
    reactions_chemfig = ''.join(i[1] for i in complete_reaction)
    return reactions_chemfig


@mol_2_chemfig.route('/convert_reaction', methods=["POST", "GET"])
def convert_reaction():
    mol_files = request.json['MOLFiles']
    reaction = json.loads(request.json['reaction'])
    input_text = request.json['input_text']
    options = request.json['options']
    d = parse_reaction(reaction, mol_files, input_text, options)
    latex_template = latex_begins + start + d + latex_ends
    txt_latex = start + d + stop
    with open(folder + latex_file, 'w') as f:
        f.write(latex_template)
    os.system(latexcmd)
    pdf_string = open('reaction.pdf').read()
    encoded = base64.encodestring(pdf_string)
    pdflink = "data:application/pdf;base64,{}".format(encoded)
    return jsonify(data=txt_latex, pdflink=pdflink)


@mol_2_chemfig.route('/remove_after_percent', methods=["POST"])
def remove_after_percent():
    chemfig = request.json['text']
    text = re.sub('\%.+', '', str(chemfig))
    return jsonify(chemfig=text)


@mol_2_chemfig.route('/get_inline', methods=['POST'])
def get_inline():
    chemfig = request.json['text']
    text = re.sub('\%.+', '', str(chemfig))
    s2 = text.split()
    # get index of \chemfig
    start = [num for num, line in enumerate(s2) if line.startswith("\chemfig")]
    # get index of }
    end = [num for num, line in enumerate(s2) if line.startswith("}")]
    # get all indexes
    all_indexes = range(len(s2))
    rest = [range(start[i], end[i] + 1) for i in range(len(start))]
    rest_chemfig = [(start[i], ''.join(s2[start[i]:end[i] + 1]))
                    for i in range(len(start))]
    rest = [item for sublist in rest for item in sublist]
    not_inline = sorted(list(set(all_indexes) - set(rest)))
    all_chemfig = [(i, s2[i]) for i in not_inline]
    all_chemfig = sorted(all_chemfig + rest_chemfig)
    final = '\n'.join([i[1] for i in all_chemfig])
    return jsonify(chemfig=final)


@mol_2_chemfig.route('/change_chemfig', methods=["POST"])
def change_chenfig():
    chemfig = request.json['text']
    latex_template = latex_begins + chemfig + latex_ends
    with open(folder + latex_file, 'w') as f:
        f.write(latex_template)
    os.system(latexcmd)
    pdf_string = open('reaction.pdf').read()
    encoded = base64.encodestring(pdf_string)
    pdflink = "data:application/pdf;base64,{}".format(encoded)
    return jsonify(pdflink=pdflink)


latex_begins = r"""
\documentclass{minimal}
\usepackage{xcolor, chemfig, mol2chemfig}
\usepackage[paperheight=6cm, paperwidth=28cm]{geometry}
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
start = '\schemestart[0,2.5,thick]' + '\n'
stop = "\n" + "\schemestop"
latex_ends = "\n" + "\schemestop" + '\n' + "\end{center}" + "\n" + "\\vspace*{\\fill}" + "\n" + "\end{document}"
