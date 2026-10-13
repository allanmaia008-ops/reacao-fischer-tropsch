"""Catálogo versionado e conversões de unidades do contrato Fischer–Tropsch.

As funções deste módulo convertem somente grandezas compatíveis. Pressões são
absolutas; vazões molares não são convertidas em vazões volumétricas sem estado
termodinâmico explícito.
"""

from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import Mapping

UNIT_CATALOG_VERSION = "1.0.0"


class UnitError(ValueError):
    """Erro de unidade desconhecida, incompatível ou valor inválido."""


@dataclass(frozen=True)
class UnitDefinition:
    symbol: str
    quantity: str
    scale_to_canonical: float
    offset_to_canonical: float = 0.0
    aliases: tuple[str, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class CanonicalMeasurement:
    quantity: str
    canonical_value: float
    canonical_unit: str
    original_value: float
    original_unit: str
    catalog_version: str = UNIT_CATALOG_VERSION


_DEFINITIONS = (
    UnitDefinition("degC", "temperature", 1.0, 0.0, ("c", "°c", "celsius")),
    UnitDefinition("K", "temperature", 1.0, -273.15, ("kelvin",)),
    UnitDefinition("degF", "temperature", 5.0 / 9.0, -32.0 * 5.0 / 9.0, ("f", "°f", "fahrenheit")),
    UnitDefinition("bar", "pressure_absolute", 1.0, aliases=("bara",), note="pressão absoluta"),
    UnitDefinition("Pa", "pressure_absolute", 1e-5, aliases=("pascal",)),
    UnitDefinition("kPa", "pressure_absolute", 1e-2),
    UnitDefinition("MPa", "pressure_absolute", 10.0),
    UnitDefinition("atm", "pressure_absolute", 1.01325),
    UnitDefinition("h", "time", 1.0, aliases=("hr", "hour", "hora")),
    UnitDefinition("min", "time", 1.0 / 60.0, aliases=("minute", "minuto")),
    UnitDefinition("s", "time", 1.0 / 3600.0, aliases=("sec", "second", "segundo")),
    UnitDefinition("d", "time", 24.0, aliases=("day", "dia")),
    UnitDefinition("mol/s", "molar_flow", 1.0, aliases=("mol_s",)),
    UnitDefinition("mmol/s", "molar_flow", 1e-3),
    UnitDefinition("mol/min", "molar_flow", 1.0 / 60.0),
    UnitDefinition("mol/h", "molar_flow", 1.0 / 3600.0),
    UnitDefinition("kmol/h", "molar_flow", 1000.0 / 3600.0),
    UnitDefinition("h^-1", "inverse_time", 1.0, aliases=("1/h", "h-1", "h_1")),
    UnitDefinition("min^-1", "inverse_time", 60.0, aliases=("1/min", "min-1")),
    UnitDefinition("s^-1", "inverse_time", 3600.0, aliases=("1/s", "s-1")),
    UnitDefinition("g", "mass", 1.0, aliases=("gram", "grama")),
    UnitDefinition("mg", "mass", 1e-3),
    UnitDefinition("kg", "mass", 1000.0),
    UnitDefinition("mL", "volume", 1.0, aliases=("ml", "cm3", "cm^3")),
    UnitDefinition("L", "volume", 1000.0, aliases=("l", "liter", "litro")),
    UnitDefinition("m3", "volume", 1e6, aliases=("m^3",)),
    UnitDefinition("wt_pct", "mass_fraction", 1.0, aliases=("wt%", "%wt", "mass_pct")),
    UnitDefinition("fraction", "mass_fraction", 100.0, aliases=("mass_fraction",)),
    UnitDefinition("ppm_wt", "mass_fraction", 1e-4, aliases=("ppmw",)),
    UnitDefinition("mol_fraction", "molar_fraction", 1.0, aliases=("mole_fraction",)),
    UnitDefinition("mol_pct", "molar_fraction", 0.01, aliases=("mol%",)),
    UnitDefinition("ppm_mol", "molar_fraction", 1e-6, aliases=("ppmv",)),
    UnitDefinition("ratio", "dimensionless_ratio", 1.0, aliases=("dimensionless", "1")),
)

CANONICAL_UNITS: Mapping[str, str] = MappingProxyType({
    "temperature": "degC",
    "pressure_absolute": "bar",
    "time": "h",
    "molar_flow": "mol/s",
    "inverse_time": "h^-1",
    "mass": "g",
    "volume": "mL",
    "mass_fraction": "wt_pct",
    "molar_fraction": "mol_fraction",
    "dimensionless_ratio": "ratio",
})

FIELD_QUANTITIES: Mapping[str, str] = MappingProxyType({
    "active_metal_loading_wt_pct": "mass_fraction",
    "promoter_loading_wt_pct": "mass_fraction",
    "activation_temperature_c": "temperature",
    "activation_duration_h": "time",
    "temperature_c": "temperature",
    "pressure_bar": "pressure_absolute",
    "h2_co_molar_ratio": "dimensionless_ratio",
    "feed_composition_mol_fraction": "molar_fraction",
    "feed_flow_mol_s": "molar_flow",
    "ghsv_h_1": "inverse_time",
    "whsv_h_1": "inverse_time",
    "catalyst_mass_g": "mass",
    "bed_volume_ml": "volume",
    "time_on_stream_h": "time",
})

_BY_SYMBOL = {definition.symbol: definition for definition in _DEFINITIONS}
_ALIASES = {
    alias.casefold(): definition.symbol
    for definition in _DEFINITIONS
    for alias in (definition.symbol, *definition.aliases)
}


def unit_catalog() -> tuple[UnitDefinition, ...]:
    """Retorna o catálogo imutável na ordem normativa."""
    return _DEFINITIONS


def normalize_unit(unit: str) -> str:
    """Normaliza símbolo ou alias sem inferir grandeza pelo valor."""
    if not isinstance(unit, str) or not unit.strip():
        raise UnitError("A unidade deve ser uma string não vazia.")
    symbol = _ALIASES.get(unit.strip().casefold())
    if symbol is None:
        raise UnitError(f"Unidade desconhecida: {unit!r}.")
    return symbol


def _finite_value(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise UnitError("O valor deve ser um número finito.")
    return float(value)


def convert(value: float, from_unit: str, to_unit: str, *, quantity: str | None = None) -> float:
    """Converte entre unidades da mesma grandeza usando a unidade canônica."""
    numeric = _finite_value(value)
    source = _BY_SYMBOL[normalize_unit(from_unit)]
    target = _BY_SYMBOL[normalize_unit(to_unit)]
    if source.quantity != target.quantity:
        raise UnitError(
            f"Conversão incompatível: {source.quantity} ({source.symbol}) para "
            f"{target.quantity} ({target.symbol})."
        )
    if quantity is not None and source.quantity != quantity:
        raise UnitError(
            f"A unidade {source.symbol} pertence a {source.quantity}, não a {quantity}."
        )
    canonical_value = numeric * source.scale_to_canonical + source.offset_to_canonical
    return (canonical_value - target.offset_to_canonical) / target.scale_to_canonical


def canonicalize(value: float, unit: str, quantity: str) -> CanonicalMeasurement:
    """Converte e preserva valor/unidade originais para rastreabilidade."""
    if quantity not in CANONICAL_UNITS:
        raise UnitError(f"Grandeza desconhecida: {quantity!r}.")
    numeric = _finite_value(value)
    source_symbol = normalize_unit(unit)
    canonical_unit = CANONICAL_UNITS[quantity]
    canonical_value = convert(numeric, source_symbol, canonical_unit, quantity=quantity)
    return CanonicalMeasurement(
        quantity=quantity,
        canonical_value=canonical_value,
        canonical_unit=canonical_unit,
        original_value=numeric,
        original_unit=source_symbol,
    )


def canonicalize_field(field: str, value: float, unit: str) -> CanonicalMeasurement:
    """Converte um campo conhecido do contrato v2 para sua unidade normativa."""
    try:
        quantity = FIELD_QUANTITIES[field]
    except KeyError as exc:
        raise UnitError(f"Campo sem grandeza registrada: {field!r}.") from exc
    return canonicalize(value, unit, quantity)

