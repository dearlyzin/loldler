import sys
from datetime import date

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from loldle.cache import get_all_answers
from loldle.config import DEFAULT_REGION
from loldle.display import render_all, render_yesterday
from loldle.history import get_yesterday, save_today

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=sys.stdout.isatty())


def main() -> None:
    if sys.stdout.isatty():
        console.clear()

    today = date.today().strftime("%d/%m/%Y")

    header = Text()
    header.append("LOLDLE", style="bold bright_cyan")
    header.append(" RESOLVER", style="bold white")
    header.append(f"  |  {today}  |  {DEFAULT_REGION.upper()}", style="dim")
    console.print(Panel(header, border_style="bright_cyan", padding=(1, 4)))

    console.print()

    yesterday = get_yesterday()
    console.print(render_yesterday(yesterday))
    console.print()

    console.print(Rule(style="dim"))
    console.print()

    try:
        answers = get_all_answers(DEFAULT_REGION)
        save_today(answers, DEFAULT_REGION)
    except Exception as exc:
        console.print(
            Panel(
                f"Connection or decryption error.\n{exc}",
                title="ERROR",
                border_style="red",
            )
        )
        return

    panels = render_all(answers)
    for panel in panels:
        console.print(panel)
        console.print()

    console.print(Rule(style="dim"))
    console.print()
    console.print("[dim]Data from cache.loldle.net[/dim]")


if __name__ == "__main__":
    main()
