from rich.table import Table
from rich.console import Console
from rich.panel import Panel


def print_table(data, title="Table"):
    """
    Print a list of dictionaries as a table with colors and separative lines.

    Args:
        data (list): List of dictionaries where keys are column names and values are row values.
        title (str): Title of the table.
    """
    if not data:
        print("No data available.")
        return

    table = Table(title=title, style="bold magenta", show_lines=True)
    columns = data[0].keys()

    for column in columns:
        table.add_column(column, style="cyan")

    for row in data:
        table.add_row(*[f"[green]{str(row[col])}[/green]" for col in columns])

    console = Console()
    console.print(Panel(table, title=title, border_style="bright_yellow"))
