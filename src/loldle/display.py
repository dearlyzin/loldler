from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from loldle.config import MODE_LABELS, MODES


def _mode_color(mode: str) -> str:
    colors = {
        "classic": "bold cyan",
        "quote": "bold green",
        "ability": "bold yellow",
        "emoji": "bold magenta",
        "splash": "bold red",
    }
    return colors.get(mode, "white")


def render_yesterday(yesterday: dict[str, str]) -> Text:
    """Render the 'Yesterday' line with champion names."""
    if not yesterday:
        return Text("Yesterday: data unavailable", style="dim")
    names = [yesterday.get(m, "?") for m in MODES]
    return Text.assemble(
        ("Yesterday: ", "bold"),
        (" | ".join(names), "italic"),
    )


def render_mode(mode: str, answer: dict) -> Panel:
    """Render a single mode answer as a Rich panel."""
    if answer.get("error"):
        return Panel(
            Text("Decryption failed. Keys may have changed.", style="red"),
            title=MODE_LABELS[mode],
            border_style="red",
        )

    champion = answer.get("champion_name", "?")

    table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
    table.add_column("label", style="dim", ratio=0)
    table.add_column("value", style=_mode_color(mode), ratio=1)

    table.add_row("Champion", champion)

    if mode == "classic":
        clues = answer.get("clues", {})
        if clues.get("quote"):
            table.add_row("Quote", clues["quote"].get("name", ""))
        if clues.get("ability"):
            table.add_row("Ability", clues["ability"].get("name", ""))
        if clues.get("splash"):
            table.add_row("Splash", clues["splash"].get("name", ""))

    elif mode == "quote":
        quote_text = answer.get("question", "")
        if len(quote_text) > 80:
            quote_text = quote_text[:77] + "..."
        table.add_row("Quote", f'"{quote_text}"')

    elif mode == "ability":
        ability_name = answer.get("ability_name", "")
        ability_letter = answer.get("ability_letter", "")
        table.add_row("Ability", f"{ability_name} ({ability_letter})")

    elif mode == "emoji":
        title = answer.get("title", "")
        if title:
            table.add_row("Title", title)

    elif mode == "splash":
        splash_name = answer.get("splash_name", answer.get("question", {}).get("splash_name", ""))
        table.add_row("Skin", splash_name)

    return Panel(table, title=MODE_LABELS[mode], border_style=_mode_color(mode), expand=False)


def render_all(answers: dict[str, dict]) -> list[Panel]:
    """Render all answers as a list of Rich panels."""
    panels = []
    for mode in MODES:
        if mode in answers:
            panels.append(render_mode(mode, answers[mode]))
    return panels
