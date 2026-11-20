# fraiskm

Calculer ses frais kilométriques avec le barème fiscal français, en ligne de commande ou en Python. Aucune dépendance.

Le barème kilométrique sert à déduire les frais de véhicule quand on déclare ses frais réels (salariés) ou à rembourser les déplacements professionnels (indemnités kilométriques). Il dépend du type de véhicule, de sa puissance fiscale, du kilométrage annuel et de la motorisation (les véhicules 100 % électriques ont un barème majoré de 20 %).

Barème inclus : arrêté du 27 mars 2023, reconduit sans revalorisation pour les revenus 2023, 2024 et 2025 (déclarations faites en 2024, 2025 et 2026).

## Installation

```bash
pip install git+https://github.com/TheoPSR01/fraiskm.git
```

Python 3.10 ou plus récent.

## En ligne de commande

```bash
fraiskm 5 12000
# 5 679,00 € (12000 km × 0.357 + 1395)  [voiture, 5 CV, revenus 2025]

fraiskm 5 12000 --electrique
# 6 810,00 € (12000 km × 0.428 + 1674)  [voiture électrique, 5 CV, revenus 2025]

fraiskm 4 5000 --type moto
fraiskm --type cyclomoteur 4000
```

Pour les trajets domicile-travail, indiquez la distance aller et le nombre de jours travaillés :

```bash
fraiskm 5 --aller 25 --jours 210
# 25 km × 2 × 210 jours = 10 500 km
```

Au-delà de 40 km aller, la distance est ramenée à 40 km, sauf circonstances particulières que vous pouvez justifier (option `--justifie`).

## En Python

```python
from fraiskm import frais_kilometriques, km_domicile_travail

km = km_domicile_travail(distance_aller=25, jours=210)
r = frais_kilometriques(km, cv=5)
print(r.montant)   # Decimal('5143.50')
print(r)           # 5 143,50 € (10500 km × 0.357 + 1395)
```

Paramètres de `frais_kilometriques` : `km`, `cv` (puissance fiscale, inutile pour un cyclomoteur), `type_vehicule` (`"voiture"`, `"moto"` ou `"cyclomoteur"`), `electrique`, `annee` (année des revenus).

## Règles appliquées

Voitures : tranches jusqu'à 5 000 km, de 5 001 à 20 000 km, au-delà de 20 000 km. Les puissances inférieures à 3 CV suivent la ligne « 3 CV et moins », celles supérieures à 7 CV la ligne « 7 CV et plus ».

Motos de plus de 50 cm³ : tranches jusqu'à 3 000 km, de 3 001 à 6 000 km, au-delà de 6 000 km, avec trois catégories de puissance (1 ou 2 CV, 3 à 5 CV, plus de 5 CV).

Cyclomoteurs (50 cm³ maximum) : mêmes tranches que les motos, sans distinction de puissance.

Le barème couvre la dépréciation du véhicule, l'entretien, les réparations, les pneus, le carburant et l'assurance. Les frais de péage et de stationnement, et les intérêts d'un emprunt pour l'achat du véhicule (au prorata de l'usage professionnel), peuvent s'y ajouter.

## Limites

Ce calcul ne remplace pas le simulateur d'impots.gouv.fr ni l'avis d'un professionnel. Il ne compare pas les frais réels avec l'abattement forfaitaire de 10 %. Les montants sont arrondis au centime.

## Contribuer

Quand un nouveau barème est publié, il suffit d'ajouter l'année dans `ANNEES` (ou de nouvelles tables) et les tests correspondants.

```bash
git clone https://github.com/TheoPSR01/fraiskm.git
cd fraiskm
pip install -e ".[dev]"
pytest
```

## Licence

MIT
