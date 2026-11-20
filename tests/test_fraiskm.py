from decimal import Decimal

import pytest

from fraiskm import frais_kilometriques, km_domicile_travail
from fraiskm.__main__ import main


@pytest.mark.parametrize("cv,km,attendu", [
    (5, 12000, "5679.00"),    # 0,357 x 12 000 + 1 395
    (5, 4000, "2544.00"),     # 0,636 x 4 000
    (5, 25000, "10675.00"),   # 0,427 x 25 000
    (3, 1000, "529.00"),
    (2, 1000, "529.00"),      # moins de 3 CV : tranche « 3 CV et moins »
    (7, 5000, "3485.00"),     # borne haute incluse dans la 1re tranche
    (9, 5001, "3485.39"),     # 9 CV traité comme « 7 CV et plus »
    (4, 20000, "8130.00"),
])
def test_voiture_thermique(cv, km, attendu):
    assert frais_kilometriques(km, cv).montant == Decimal(attendu)


def test_voiture_electrique():
    assert frais_kilometriques(12000, 5, electrique=True).montant == Decimal("6810.00")  # 0,428 x 12 000 + 1 674


def test_pas_de_baisse_aux_changements_de_tranche():
    # Le barème officiel n'est pas parfaitement continu (sauts de quelques euros),
    # mais le montant ne diminue jamais quand le kilométrage augmente.
    for cv in range(3, 8):
        for borne in (5000, 20000):
            a = frais_kilometriques(borne, cv).montant
            b = frais_kilometriques(borne + 1, cv).montant
            assert Decimal("0") < b - a < Decimal("20")


@pytest.mark.parametrize("cv,km,elec,attendu", [
    (1, 2000, False, "790.00"),
    (4, 5000, False, "1568.00"),   # 0,082 x 5 000 + 1 158
    (8, 7000, False, "2401.00"),
    (4, 5000, True, "1880.00"),    # 0,098 x 5 000 + 1 390
])
def test_moto(cv, km, elec, attendu):
    assert frais_kilometriques(km, cv, "moto", elec).montant == Decimal(attendu)


def test_cyclomoteur():
    assert frais_kilometriques(4000, type_vehicule="cyclomoteur").montant == Decimal("1027.00")
    assert frais_kilometriques(4000, type_vehicule="cyclomoteur", electrique=True).montant == Decimal("1233.00")


def test_domicile_travail():
    assert km_domicile_travail(25, 210) == Decimal("10500")
    assert km_domicile_travail(60, 200) == Decimal("16000")          # plafonné à 40 km
    assert km_domicile_travail(60, 200, justifie=True) == Decimal("24000")


@pytest.mark.parametrize("kwargs", [
    dict(km=1000, cv=5, annee=2019),
    dict(km=1000, cv=5, type_vehicule="camion"),
    dict(km=-1, cv=5),
    dict(km=1000, cv=None),
])
def test_erreurs(kwargs):
    with pytest.raises(ValueError):
        frais_kilometriques(**kwargs)


def test_cli(capsys):
    assert main(["5", "12000"]) == 0
    assert "5 679,00 €" in capsys.readouterr().out
    assert main(["5", "--aller", "25", "--jours", "210"]) == 0
    assert "10500" in capsys.readouterr().out


def test_cli_aide(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "électrique" in capsys.readouterr().out
