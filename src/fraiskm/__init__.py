"""fraiskm : calcul des frais kilométriques selon le barème fiscal français.

Barème de l'arrêté du 27 mars 2023, reconduit sans revalorisation pour les
revenus 2023, 2024 et 2025 (déclarations 2024, 2025 et 2026).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

__version__ = "0.1.0"

D = Decimal

# Chaque tranche : (borne haute en km incluse, coefficient, montant fixe).
# La dernière tranche a une borne None.
_VOITURE = {
    3: [(5000, D("0.529"), D("0")), (20000, D("0.316"), D("1065")), (None, D("0.370"), D("0"))],
    4: [(5000, D("0.606"), D("0")), (20000, D("0.340"), D("1330")), (None, D("0.407"), D("0"))],
    5: [(5000, D("0.636"), D("0")), (20000, D("0.357"), D("1395")), (None, D("0.427"), D("0"))],
    6: [(5000, D("0.665"), D("0")), (20000, D("0.374"), D("1457")), (None, D("0.447"), D("0"))],
    7: [(5000, D("0.697"), D("0")), (20000, D("0.394"), D("1515")), (None, D("0.470"), D("0"))],
}
_VOITURE_ELEC = {
    3: [(5000, D("0.635"), D("0")), (20000, D("0.379"), D("1278")), (None, D("0.444"), D("0"))],
    4: [(5000, D("0.727"), D("0")), (20000, D("0.408"), D("1596")), (None, D("0.488"), D("0"))],
    5: [(5000, D("0.763"), D("0")), (20000, D("0.428"), D("1674")), (None, D("0.512"), D("0"))],
    6: [(5000, D("0.798"), D("0")), (20000, D("0.449"), D("1748")), (None, D("0.536"), D("0"))],
    7: [(5000, D("0.836"), D("0")), (20000, D("0.473"), D("1818")), (None, D("0.564"), D("0"))],
}
# Motos de plus de 50 cm3 : clés 2 (1 ou 2 CV), 5 (3 à 5 CV), 6 (plus de 5 CV)
_MOTO = {
    2: [(3000, D("0.395"), D("0")), (6000, D("0.099"), D("891")), (None, D("0.248"), D("0"))],
    5: [(3000, D("0.468"), D("0")), (6000, D("0.082"), D("1158")), (None, D("0.275"), D("0"))],
    6: [(3000, D("0.606"), D("0")), (6000, D("0.079"), D("1583")), (None, D("0.343"), D("0"))],
}
_MOTO_ELEC = {
    2: [(3000, D("0.474"), D("0")), (6000, D("0.119"), D("1069")), (None, D("0.298"), D("0"))],
    5: [(3000, D("0.562"), D("0")), (6000, D("0.098"), D("1390")), (None, D("0.330"), D("0"))],
    6: [(3000, D("0.727"), D("0")), (6000, D("0.095"), D("1900")), (None, D("0.412"), D("0"))],
}
# Deux-roues de 50 cm3 maximum (cyclomoteurs), sans distinction de puissance
_CYCLO = [(3000, D("0.315"), D("0")), (6000, D("0.079"), D("711")), (None, D("0.198"), D("0"))]
_CYCLO_ELEC = [(3000, D("0.378"), D("0")), (6000, D("0.095"), D("853")), (None, D("0.238"), D("0"))]

#: Années de revenus couvertes par ce barème.
ANNEES = (2023, 2024, 2025)
TYPES = ("voiture", "moto", "cyclomoteur")

#: Distance aller domicile-travail retenue sans justification particulière.
PLAFOND_DOMICILE_TRAVAIL_KM = 40


@dataclass(frozen=True)
class Resultat:
    montant: Decimal
    formule: str
    vehicule: str
    puissance_retenue: Optional[str]
    km: Decimal

    def __str__(self) -> str:
        return f"{_fr(self.montant)} € ({self.formule})"


def _fr(x: Decimal) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


def _cle_voiture(cv: int) -> int:
    return min(max(cv, 3), 7)


def _cle_moto(cv: int) -> int:
    if cv <= 2:
        return 2
    return 5 if cv <= 5 else 6


def _libelle(type_vehicule: str, cle: Optional[int]) -> Optional[str]:
    if type_vehicule == "voiture":
        return {3: "3 CV et moins", 7: "7 CV et plus"}.get(cle, f"{cle} CV")
    if type_vehicule == "moto":
        return {2: "1 ou 2 CV", 5: "3, 4 ou 5 CV", 6: "plus de 5 CV"}[cle]
    return None


def frais_kilometriques(
    km,
    cv: Optional[int] = None,
    type_vehicule: str = "voiture",
    electrique: bool = False,
    annee: int = 2025,
) -> Resultat:
    """Montant déductible pour ``km`` kilomètres professionnels parcourus dans l'année.

    ``cv`` est la puissance fiscale (inutile pour un cyclomoteur). ``annee`` est
    l'année des revenus (2025 pour la déclaration faite en 2026).
    """
    if annee not in ANNEES:
        raise ValueError(f"barème disponible pour les revenus {ANNEES[0]} à {ANNEES[-1]}, pas {annee}")
    if type_vehicule not in TYPES:
        raise ValueError(f"type de véhicule inconnu : {type_vehicule!r} (attendu : {', '.join(TYPES)})")
    km = D(str(km))
    if km < 0:
        raise ValueError("le kilométrage ne peut pas être négatif")

    cle = None
    if type_vehicule == "cyclomoteur":
        tranches = _CYCLO_ELEC if electrique else _CYCLO
    else:
        if cv is None or cv < 1:
            raise ValueError("puissance fiscale (cv) obligatoire pour une voiture ou une moto")
        if type_vehicule == "voiture":
            cle = _cle_voiture(cv)
            tranches = (_VOITURE_ELEC if electrique else _VOITURE)[cle]
        else:
            cle = _cle_moto(cv)
            tranches = (_MOTO_ELEC if electrique else _MOTO)[cle]

    for borne, coef, fixe in tranches:
        if borne is None or km <= borne:
            break
    montant = (km * coef + fixe).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    formule = f"{format(km.normalize(), 'f')} km × {coef}" + (f" + {fixe}" if fixe else "")
    return Resultat(montant, formule, type_vehicule + (" électrique" if electrique else ""), _libelle(type_vehicule, cle), km)


def km_domicile_travail(distance_aller, jours: int, justifie: bool = False) -> Decimal:
    """Kilomètres annuels pour les trajets domicile-travail (un aller-retour par jour).

    Sans circonstances particulières justifiées, la distance aller est retenue
    dans la limite de 40 km.
    """
    d = D(str(distance_aller))
    if d < 0 or jours < 0:
        raise ValueError("distance et nombre de jours doivent être positifs")
    if not justifie:
        d = min(d, D(PLAFOND_DOMICILE_TRAVAIL_KM))
    return d * 2 * jours


__all__ = [
    "ANNEES",
    "PLAFOND_DOMICILE_TRAVAIL_KM",
    "Resultat",
    "TYPES",
    "frais_kilometriques",
    "km_domicile_travail",
]
