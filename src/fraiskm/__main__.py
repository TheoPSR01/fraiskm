"""Ligne de commande : ``fraiskm 5 12000`` ou ``fraiskm 5 --aller 25 --jours 210``."""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation

from . import __version__, frais_kilometriques, km_domicile_travail


def _nombre(v: str) -> Decimal:
    try:
        return Decimal(v.replace(",", "."))
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"nombre invalide : {v!r}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="fraiskm", description="Frais kilométriques selon le barème fiscal français.")
    p.add_argument("--version", action="version", version=f"fraiskm {__version__}")
    p.add_argument("cv", type=int, nargs="?", help="puissance fiscale (inutile pour un cyclomoteur)")
    p.add_argument("km", type=_nombre, nargs="?", help="kilomètres professionnels de l'année")
    p.add_argument("--type", dest="type_vehicule", default="voiture", choices=["voiture", "moto", "cyclomoteur"])
    p.add_argument("--electrique", action="store_true", help="véhicule 100 %% électrique")
    p.add_argument("--annee", type=int, default=2025, help="année des revenus (défaut : 2025)")
    p.add_argument("--aller", type=_nombre, help="distance aller domicile-travail, en km")
    p.add_argument("--jours", type=int, help="nombre de jours travaillés")
    p.add_argument("--justifie", action="store_true", help="ne pas plafonner la distance aller à 40 km")
    args = p.parse_args(argv)

    km = args.km
    if args.aller is not None or args.jours is not None:
        if args.aller is None or args.jours is None:
            p.error("--aller et --jours vont ensemble")
        km = km_domicile_travail(args.aller, args.jours, args.justifie)
        if args.aller > 40 and not args.justifie:
            print("Distance aller ramenée à 40 km (option --justifie si l'éloignement est justifié).")
    if km is None:
        p.error("indiquer un kilométrage, ou --aller et --jours")
    if args.type_vehicule != "cyclomoteur" and args.cv is None:
        p.error("indiquer la puissance fiscale")

    try:
        r = frais_kilometriques(km, args.cv, args.type_vehicule, args.electrique, args.annee)
    except ValueError as exc:
        print(f"fraiskm : {exc}", file=sys.stderr)
        return 2
    detail = f"{r.vehicule}" + (f", {r.puissance_retenue}" if r.puissance_retenue else "")
    print(f"{r}  [{detail}, revenus {args.annee}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
