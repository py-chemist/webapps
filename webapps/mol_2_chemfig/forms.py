from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms import SubmitField, BooleanField, SelectField


def get_checkboxes_data():
    '''Return title, values and text of checkboxes'''

    title = ["Wrap the code into \chemfig{...}",
             "Display chemfig format inline",
             # "Strip line after %",
             "Assign number to each atom except hydrogen",
             "Show nicer double and triple bonds",
             "Show circle in aromatic compounds instead of double bonds",
             "Show carbon atoms as elements",
             "Show methyl group as elements",
             "Flip the structure horizontally",
             "Flop the strcture vertically"]
    value = ["-w", "-j",  "-n", "-f", "-o", "-c", "-m", "-p", "-q"]  # "-rm",
    text = ["chemfig", "inline",  # "remove %",
            "atom-numbers", "fancy bonds", "aromatic",
            "show carbon", "show methyl", "flip", "flop"]
    return zip(title, value, text)


def get_menu_links():
    return ["Home", "Links", "About"]


def hydrogens_options():
    return [("keep", "keep"), ("add", "add"), ("delete", "delete")]


class HomePageForm(Form):
    db_search = StringField()
    submit = SubmitField('Search')
    smiles_mol = TextAreaField()
    convert = SubmitField()
    check = BooleanField()
    angle = StringField()
    hydrogens = SelectField('hydrogens', choices=hydrogens_options())
    update = SubmitField('Apply')
    reset = SubmitField('Reset')
