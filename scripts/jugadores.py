"""
jugadores.py — Diccionario de nombres reconocibles + helpers

Las fuentes de datos (StatsBomb, FBref) usan nombres legales completos
("Lionel Andrés Messi Cuccittini") que NO son los nombres reconocibles.
Este módulo traduce a la forma con la que se conocen públicamente.

Uso:
    from scripts.jugadores import display_name
    display_name("Lionel Andrés Messi Cuccittini")  # → "Messi"
    display_name("Kylian Mbappé Lottin")            # → "Mbappé"
    display_name("Jugador Desconocido")             # → "Desconocido" (fallback)

Para agregar un jugador nuevo, sumar entrada al dict NOMBRES_PUBLICOS.
"""

from __future__ import annotations


# ──────────────────────────────────────────────────────────────────────
# DICCIONARIO MAESTRO
# ──────────────────────────────────────────────────────────────────────
# Mapea: nombre completo (como aparece en datasets) → nombre público.
# Convención: agregar entradas a medida que se encuentren casos raros.

NOMBRES_PUBLICOS: dict[str, str] = {
    # ── Argentina (Mundial 2022, 2026, scouting) ────────────────────
    "Lionel Andrés Messi Cuccittini": "Messi",
    "Lionel Messi": "Messi",
    "Ángel Fabián Di María Hernández": "Di María",
    "Ángel Di María": "Di María",
    "Julián Álvarez": "J. Álvarez",
    "Lautaro Javier Martínez": "Lautaro Martínez",
    "Lautaro Martínez": "Lautaro Martínez",
    "Rodrigo Javier De Paul": "De Paul",
    "Rodrigo De Paul": "De Paul",
    "Alexis Mac Allister": "Mac Allister",
    "Enzo Jeremías Fernández": "Enzo Fernández",
    "Enzo Fernández": "Enzo Fernández",
    "Cristian Gabriel Romero": "Cristian Romero",
    "Cristian Romero": "Cuti Romero",
    "Nicolás Hernán Otamendi": "Otamendi",
    "Nicolás Otamendi": "Otamendi",
    "Nicolás Alejandro Tagliafico": "Tagliafico",
    "Nicolás Tagliafico": "Tagliafico",
    "Marcos Javier Acuña": "Acuña",
    "Marcos Acuña": "Acuña",
    "Nahuel Molina Lucero": "Molina",
    "Nahuel Molina": "Molina",
    "Emiliano Martínez Romero": "Emiliano Martínez",
    "Emiliano Martínez": "Dibu Martínez",
    "Leandro Daniel Paredes": "Paredes",
    "Leandro Paredes": "Paredes",
    "Lisandro Martínez": "Licha Martínez",
    "Germán Alejo Pezzella": "Pezzella",
    "Thiago Almada": "Almada",
    "Franco Mastantuono": "Mastantuono",
    "Matías Soulé Malvano": "Soulé",
    "Matías Soulé": "Soulé",
    "Alejandro Garnacho Ferreyra": "Garnacho",
    "Alejandro Garnacho": "Garnacho",
    # ── Francia (rivales clásicos en Mundiales) ─────────────────────
    "Kylian Mbappé Lottin": "Mbappé",
    "Kylian Mbappé": "Mbappé",
    "Antoine Griezmann": "Griezmann",
    "Olivier Giroud": "Giroud",
    "N'Golo Kanté": "Kanté",
    "Aurélien Tchouaméni": "Tchouaméni",
    "Theo Bernard François Hernández": "Theo Hernández",
    "Theo Hernández": "Theo Hernández",
    "Hugo Lloris": "Lloris",
    "Raphaël Varane": "Varane",
    "Dayot Upamecano": "Upamecano",
    "Ousmane Dembélé": "Dembélé",
    # ── Top jugadores internacionales (Mundial / Champions) ─────────
    "Cristiano Ronaldo dos Santos Aveiro": "Cristiano Ronaldo",
    "Cristiano Ronaldo": "Cristiano Ronaldo",
    "Neymar da Silva Santos Júnior": "Neymar",
    "Vinícius José Paixão de Oliveira Júnior": "Vinícius Jr.",
    "Vinícius Júnior": "Vinícius Jr.",
    "Rodrygo Silva de Goes": "Rodrygo",
    "Erling Haaland": "Haaland",
    "Robert Lewandowski": "Lewandowski",
    "Mohamed Salah Ghaly": "Salah",
    "Mohamed Salah": "Salah",
    "Harry Kane": "Kane",
    "Jude Bellingham": "Bellingham",
    "Phil Foden": "Foden",
    "Pedro González López": "Pedri",
    "Gavi": "Gavi",
    "Pablo Martín Páez Gavira": "Gavi",
    "Lamine Yamal Nasraoui Ebana": "Lamine Yamal",
    "Lamine Yamal": "Lamine Yamal",
    "Luka Modrić": "Modrić",
    "Toni Kroos": "Kroos",
    "Karim Benzema": "Benzema",
    "Kevin De Bruyne": "De Bruyne",
    "Bruno Miguel Borges Fernandes": "Bruno Fernandes",
    "Bruno Fernandes": "Bruno Fernandes",
    "Bernardo Mota Veiga de Carvalho e Silva": "Bernardo Silva",
    "Bernardo Silva": "Bernardo Silva",
    "Rúben Santos Gato Alves Dias": "Rúben Dias",
    "Joshua Kimmich": "Kimmich",
    "Jamal Musiala": "Musiala",
    "Florian Wirtz": "Wirtz",
    # Agregar nuevos casos acá a medida que aparezcan.
}


# ──────────────────────────────────────────────────────────────────────
# FUNCIÓN PÚBLICA
# ──────────────────────────────────────────────────────────────────────


def display_name(full_name: str | None) -> str:
    """Convierte un nombre completo a su forma reconocible públicamente.

    Args:
        full_name: nombre tal como aparece en el dataset (ej. StatsBomb).

    Returns:
        El nombre reconocible. Si no está en el diccionario, aplica una
        heurística simple y devuelve algo razonable.

    Heurística cuando el nombre no está en el diccionario:
        - 1 palabra: devolverla
        - 2 palabras: 'Nombre Apellido' → devolver Apellido
        - 3 palabras: típicamente 'Nombre Nombre2 Apellido' → último
        - 4+ palabras: convención hispana 'N1 N2 Apellido1 Apellido2' →
          devolver el penúltimo (suele ser el apellido paterno reconocible)
    """
    if not full_name or not isinstance(full_name, str):
        return "—"

    # 1) Match exacto en el diccionario
    if full_name in NOMBRES_PUBLICOS:
        return NOMBRES_PUBLICOS[full_name]

    # 2) Heurística por cantidad de palabras
    parts = full_name.split()
    n = len(parts)

    if n == 0:
        return "—"
    if n == 1:
        return parts[0]
    if n == 2:
        # "Antoine Griezmann" → "Griezmann"
        return parts[-1]
    if n == 3:
        # "Diego Armando Maradona" → "Maradona"
        # (algunos jugadores europeos también caen acá)
        return parts[-1]
    # n >= 4 — convención hispana típica
    # "Lionel Andrés Messi Cuccittini" → penúltimo = "Messi"
    return parts[-2]


def add_nombre_publico(full_name: str, public_name: str) -> None:
    """Agrega un nombre al diccionario en runtime (no persiste).

    Útil para casos puntuales en un notebook sin tocar el módulo.

    Ejemplo:
        from scripts.jugadores import add_nombre_publico
        add_nombre_publico("Algún Jugador Raro", "Apodo")
    """
    NOMBRES_PUBLICOS[full_name] = public_name


__all__ = ["NOMBRES_PUBLICOS", "display_name", "add_nombre_publico"]
