# Importation des bibliothèques nécessaires
from collections import defaultdict  # pour simplifier la gestion des dictionnaires
from copy import deepcopy  # pour créer des copies indépendantes des objets

import random


# Définir les jours de la semaine et les créneaux horaires disponibles
jours = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi']
slots_par_jour = {
    'Dimanche': [1, 2, 3, 4, 5],
    'Lundi': [1, 2, 3, 4, 5],
    'Mardi': [1, 2, 3],
    'Mercredi': [1, 2, 3, 4, 5],
    'Jeudi': [1, 2, 3, 4, 5]
}

# Domaine des créneaux disponibles
cours_slots = [f"{jour}_{slot}" for jour in jours for slot in slots_par_jour[jour] if slot in [1, 2, 3]]
td_tp_slots = [f"{jour}_{slot}" for jour in jours for slot in slots_par_jour[jour] if slot in [1, 2, 3, 4, 5]]

# Définir les cours avec leurs sessions et le professeur associé
cours = {
    'Sécurité': [('cours', 1), ('td', 1)],
    'Méthodes_formelles': [('cours', 2), ('td', 2)],
    'Analyse_numerique': [('cours', 3), ('td', 3)],
    'Entrepreneuriat': [('cours', 4)],
    'RO2': [('cours', 5), ('td', 5)],
    'DA&IC': [('cours', 6), ('td', 6)],
    'Réseaux2': [('cours', 7), ('tp', 7), ('td', 8)],
    'IA': [('cours', 11), ('td', 11), ('tp', 12)]
}

# Construction des variables
variables = []
variable_professeur = {}
domaines = {}

for cours_nom, sessions in cours.items():
    for type_cours, professeur in sessions:
        var = f"{cours_nom}_{type_cours}"
        variables.append(var)
        variable_professeur[var] = professeur
        if type_cours == 'cours':
            domaines[var] = list(cours_slots)
        else:
            domaines[var] = list(td_tp_slots)

# Contraintes

def pas_meme_slot(affectation):
    vus = set()
    for slot in affectation.values():
        if slot in vus:
            return False
        vus.add(slot)
    return True

def max_trois_consecutifs(affectation):
    slots_journaliers = defaultdict(list)
    
    # Collecter les heures par jour
    for slot in affectation.values():
        jour, heure = slot.split('_')
        slots_journaliers[jour].append(int(heure))
    
    for heures in slots_journaliers.values():
        if not heures:
            continue
        heures.sort()
        max_consec = 1
        consec = 1
        for i in range(1, len(heures)):
            if heures[i] == heures[i - 1] + 1:
                consec += 1
                max_consec = max(max_consec, consec)
            else:
                consec = 1
        if max_consec > 3:
            return False
    return True

def pas_conflit_professeur(affectation):
    emploi_temps_prof = defaultdict(set)
    for var, slot in affectation.items():
        prof = variable_professeur[var]
        if slot in emploi_temps_prof[prof]:
            return False
        emploi_temps_prof[prof].add(slot)
    return True

def max_deux_cours_par_jour(affectation):
    compteur_journalier = defaultdict(int)
    for var, slot in affectation.items():
        if "cours" in var:
            jour, _ = slot.split('_')
            compteur_journalier[jour] += 1
            if compteur_journalier[jour] > 2:
                return False
    return True

def cours_td_separes(affectation):#à eliminer
    cours_td_par_module = defaultdict(lambda: {'cours': None, 'td': None})
    for var, slot in affectation.items():
        for module in cours:
            if var.startswith(module):
                if '_cours' in var:
                    cours_td_par_module[module]['cours'] = slot.split('_')[0]
                elif '_td' in var:
                    cours_td_par_module[module]['td'] = slot.split('_')[0]
    for module, seances in cours_td_par_module.items():
        if seances['cours'] and seances['td'] and seances['cours'] == seances['td']:
            return False
    return True

def toutes_contraintes(affectation):
    return (pas_meme_slot(affectation) and
            max_trois_consecutifs(affectation) and
            pas_conflit_professeur(affectation) and
            max_deux_cours_par_jour(affectation) and
            cours_td_separes(affectation))

def choisir_variable_non_affectee(affectation, domaines):
    non_affectees = [v for v in variables if v not in affectation]
    return min(non_affectees, key=lambda var: len(domaines[var]))#mrv

# def ordonner_valeurs_domaine(var, affectation, domaines):
#     return sorted(domaines[var], key=lambda val: sum(val in domaines[autre] for autre in variables if autre != var))

def ordonner_valeurs_domaine(var, affectation, domaines):
    valeurs = domaines[var][:]
    random.shuffle(valeurs)  # Pour éviter que 1,2,3 soient toujours choisis
    return valeurs

def ac3(domaines):
    file = [(xi, xj) for xi in variables for xj in variables if xi != xj]
    while file:
        xi, xj = file.pop(0)
        if revise(domaines, xi, xj):
            if not domaines[xi]:
                return False
            for xk in (set(variables) - {xi, xj}):
                file.append((xk, xi))
    return True

def revise(domaines, xi, xj):
    revise = False
    for x in domaines[xi][:]:
        if all(x == y for y in domaines[xj]):
            domaines[xi].remove(x)
            revise = True
    return revise

def backtrack(affectation, domaines):
    if len(affectation) == len(variables):
        return affectation
    var = choisir_variable_non_affectee(affectation, domaines)
    for valeur in ordonner_valeurs_domaine(var, affectation, domaines):
        nouvelle_affectation = affectation.copy()
        nouvelle_affectation[var] = valeur
        if toutes_contraintes(nouvelle_affectation):
            nouveaux_domaines = deepcopy(domaines)
            nouveaux_domaines[var] = [valeur]
            resultat = backtrack(nouvelle_affectation, nouveaux_domaines)
            if resultat:
                return resultat
    return None

def resoudre():
    random.shuffle(variables)
    domaines_locaux = deepcopy(domaines)
    if ac3(domaines_locaux):
        return backtrack({}, domaines_locaux)
    return None

solution = resoudre()
if solution:
    emploi_du_temps = defaultdict(list)
    for var in sorted(solution):
        slot = solution[var]
        jour, heure = slot.split('_')
        if int(heure) >= 1 and int(heure) <= 5:
            emploi_du_temps[jour].append((var, int(heure)))

    # Création du contenu HTML
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Emploi du Temps</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { border-collapse: collapse; width: 80%; margin: auto; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            .slot-empty { background-color: #fafafa; color: #bbb; }
        </style>
    </head>
    <body>
        <h1 style="text-align: center;">Emploi du Temps Généré</h1>
        <table>
            <tr>
                <th>Jour</th>
                <th>Créneau 1</th>
                <th>Créneau 2</th>
                <th>Créneau 3</th>
                <th>Créneau 4</th>
                <th>Créneau 5</th>
            </tr>
    """

    for jour in jours:
        html_content += f"<tr><td>{jour}</td>"
        slots_du_jour = {heure: "" for heure in range(1, 6)}
        for var, heure in emploi_du_temps[jour]:
            slots_du_jour[heure] = var

        for heure in range(1, 6):
            val = slots_du_jour[heure]
            if val:
                html_content += f"<td>{val}</td>"
            else:
                html_content += "<td class='slot-empty'>-</td>"
        html_content += "</tr>"

    html_content += """
        </table>
    </body>
    </html>
    """

    # Enregistrement dans un fichier HTML
    with open("emploi_du_temps.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Emploi du temps généré avec succès dans 'emploi_du_temps.html'.")
else:
    print("Aucune solution trouvée.")

# Partie de l'affichage modifiée
if solution:
    emploi_du_temps = defaultdict(list)

    for var in sorted(solution):
        slot = solution[var]
        jour, heure = slot.split('_')

        # Vérification si l'heure est entre 1 et 5
        if int(heure) >= 1 and int(heure) <= 5:
            emploi_du_temps[jour].append((var, int(heure)))

    print("L'emploi du temps:")
    for jour in jours:
        print(f" {jour}:")
        if jour in emploi_du_temps:
            # Trier les cours par heure
            emploi_du_temps[jour].sort(key=lambda x: x[1])

            # Attribuer un numéro de séance consécutif
            for var, heure in emploi_du_temps[jour]:
              parts = var.rsplit('_', 1)
              if len(parts) == 2:
                  cours_nom, type_cours = parts
              else:
                  continue

              session = next((session[1] for session in cours[cours_nom] if session[0] == type_cours), None)
              
              print(f"  - {var} => créneau:{heure}")

        else:
            print("  Aucun cours prévu")
else:
    print("Aucune solution trouvée.")
