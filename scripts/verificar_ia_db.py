#!/usr/bin/env python3
"""Verificador de la ia-db (ENTREGA.md §3): enlaces internos de ia-db/ y tabla de delegación.

Sale con 0 si todo pasa y con 1 ante la primera clase de falla. Los enlaces al repo de código
(../../../PrintThermal_Motor_Maui/...) no se resuelven en CI porque ese repo no se clona aquí.
"""
import pathlib, re, sys

raiz = pathlib.Path(__file__).resolve().parent.parent
fallas = []
for md in sorted((raiz / "ia-db").rglob("*.md")):
    for destino in re.findall(r"\]\(([^)\s]+)\)", md.read_text(encoding="utf-8")):
        if re.match(r"^(https?:|mailto:|#)", destino) or "PrintThermal_Motor_Maui/" in destino:
            continue
        ruta = (md.parent / destino.split("#")[0]).resolve()
        if not ruta.exists():
            fallas.append(f"{md.relative_to(raiz)}: enlace roto -> {destino}")

entrega = (raiz / "ENTREGA.md").read_text(encoding="utf-8")
for campo in ("Estado", "Fecha", "Decidió", "Techo", "Intervalo", "Control G3"):
    if not re.search(rf"^\| {campo} \| [^|]+\| [^|]+\|", entrega, re.M):
        fallas.append(f"ENTREGA.md: falta el campo «{campo}» con valor y origen")
if re.search(r"/home/[a-z]", entrega):
    fallas.append("ENTREGA.md: contiene una ruta de directorio personal")

for f in fallas:
    print("FALLA:", f)
print("OK: ia-db y ENTREGA.md verificadas" if not fallas else f"{len(fallas)} fallas")
sys.exit(1 if fallas else 0)
