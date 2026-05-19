import typer
import time
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress, SpinnerColumn, TextColumn,
    BarColumn, TimeElapsedColumn, MofNCompleteColumn
)
from rich.prompt import Prompt
from rich.rule import Rule
from rich.columns import Columns
from rich.text import Text
from rich.syntax import Syntax
from rich.align import Align
from rich import box
import socket
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to sys path to resolve absolute and internal imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

console = Console()
 
BANNER = """[bold #ccd9a3]
 ▄▄▄                                                       
█▀██  ██  ██▀▀                █▄                           
  ██  ██  ██       ▄          ██                           
  ██  ██  ██ ▄▀▀█▄ ████▄▄█▀█▄ ████▄ ▄███▄ ██ ██ ▄██▀█ ▄█▀█▄
  ██▄ ██▄ ██ ▄█▀██ ██   ██▄█▀ ██ ██ ██ ██ ██ ██ ▀███▄ ██▄█▀
  ▀████▀███▀▄▀█▄██▄█▀  ▄▀██▄▄▄▄██ ██▄▀███▀▄▀██▀██▄▄██▀▄▀█▄▄▄[/bold #ccd9a3]"""
 
from src.cli.theme import PALETTE
 
def header():
    console.print(Align.center(BANNER))
    console.print(
        Align.center(
            f"[bold {PALETTE['lavender']}]Data warehouse management from the terminal[/bold {PALETTE['lavender']}]"
            f"  [dim {PALETTE['muted']}]@jobby[/dim {PALETTE['muted']}]"
        )
    )
    console.print()
 
def check_warehouse_status() -> bool:
    try:
        with socket.create_connection(("localhost", 8123), timeout=2):
            return True
    except OSError:
        return False

def context_panel():
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style=f"bold {PALETTE['lavender']}",
        border_style=PALETTE["dim"],
        padding=(0, 2),
    )
    table.add_column("Key", style=f"{PALETTE['muted']}", no_wrap=True)
    table.add_column("Value", style=f"{PALETTE['sage']}")
 
    is_online = check_warehouse_status()
    status_text = f"[{PALETTE['ok']}]● online[/{PALETTE['ok']}]" if is_online else f"[{PALETTE['err']}]● offline[/{PALETTE['err']}]"
    
    last_sync = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    table.add_row("Environment", "[bold]production[/bold]")
    table.add_row("Warehouse",   "clickhouse://localhost:9002")
    table.add_row("Last sync",   last_sync)
    table.add_row("Status",      status_text)
 
    console.print(
        Panel(
            table,
            title=f"[bold {PALETTE['accent']}] Context [/bold {PALETTE['accent']}]",
            border_style=PALETTE["dim"],
            padding=(0, 1),
        )
    )
 
def menu_panel() -> str:
    options = [
        ("1", "Start ETL",       "▶  Run extraction, transform & load pipeline"),
        ("2", "Start services",  "⬆  Bring all services online"),
        ("3", "Stop services",   "⬇  Gracefully shut down all services"),
        ("4", "Run Queries",     "🔍 Execute analytical queries on warehouse"),
        ("5", "Exit",            "✕  Quit the CLI"),
    ]
 
    table = Table(
        box=box.SIMPLE,
        show_header=False,
        border_style=PALETTE["dim"],
        padding=(0, 2),
        expand=False,
    )
    table.add_column("№",    style=f"bold {PALETTE['accent']}", no_wrap=True, width=3)
    table.add_column("Action", style=f"bold {PALETTE['sage']}", no_wrap=True)
    table.add_column("Description", style=PALETTE["muted"])
 
    for key, action, desc in options:
        table.add_row(key, action, desc)
 
    console.print(
        Panel(
            table,
            title=f"[bold {PALETTE['accent']}] Menu [/bold {PALETTE['accent']}]",
            border_style=PALETTE["dim"],
            padding=(0, 1),
        )
    )
 
    choice = Prompt.ask(
        f"\n  [{PALETTE['lavender']}]Select an option[/{PALETTE['lavender']}]",
        choices=["1", "2", "3", "4", "5"],
        console=console,
    )
    return choice
 
import logging

class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
    
    def emit(self, record):
        self.records.append(record)

def run_etl():
    console.print()
    console.print(Rule(f"[bold {PALETTE['sage']}] ETL Pipeline [/bold {PALETTE['sage']}]", style=PALETTE["dim"]))
    console.print()
 
    try:
        from src.pipeline.run import main as etl_main
    except ImportError as e:
        console.print(f"[{PALETTE['err']}]Failed to import ETL modules: {e}[/{PALETTE['err']}]")
        return

    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    for h in original_handlers:
        root_logger.removeHandler(h)
    
    capture_handler = LogCaptureHandler()
    root_logger.addHandler(capture_handler)

    with Progress(
        SpinnerColumn(style=f"bold {PALETTE['lavender']}"),
        TextColumn(f"[{PALETTE['sage']}]{{task.description}}[/{PALETTE['sage']}]"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Running full ETL pipeline...", total=None)
        
        etl_main()
        
        progress.update(task, description="ETL Pipeline execution finished")
 
    root_logger.removeHandler(capture_handler)
    for h in original_handlers:
        root_logger.addHandler(h)

    console.print()
    console.print(Rule(f"[bold {PALETTE['lavender']}] Execution Logs [/bold {PALETTE['lavender']}]", style=PALETTE["dim"]))
    for record in capture_handler.records:
        for h in original_handlers:
            h.handle(record)

    console.print()
    console.print(f"  [{PALETTE['ok']}]✔[/{PALETTE['ok']}]  ETL completed successfully.\n")
 
def toggle_services(action: str):
    verb    = "Starting" if action == "start" else "Stopping"
    icon    = "⬆"        if action == "start" else "⬇"
    color   = PALETTE["ok"] if action == "start" else PALETTE["warn"]
 
    console.print()
    console.print(Rule(f"[bold {PALETTE['sage']}] {icon}  {verb} services [/bold {PALETTE['sage']}]", style=PALETTE["dim"]))
    console.print()
 
    compose_file = project_root / "docker-compose.yml"
    cmd = ["docker", "compose", "-f", str(compose_file)]
    
    if action == "start":
        cmd.extend(["start"])
    else:
        cmd.extend(["stop"])

    with console.status(f"[{color}]Executing docker compose {action}...[/{color}]", spinner="dots", spinner_style=f"bold {color}"):
        process = subprocess.run(cmd, capture_output=True, text=True)
        
    if process.returncode == 0:
        lines = process.stdout.splitlines() + process.stderr.splitlines()
        for line in lines:
            if line.strip():
                console.print(f"  [{PALETTE['dim']}]>[/{PALETTE['dim']}] {line.strip()}")
        console.print(f"\n  [{color}]✔[/{color}]  Services {verb.lower()} successfully.\n")
    else:
        console.print(f"\n  [{PALETTE['err']}]✖[/{PALETTE['err']}]  Command failed with exit code {process.returncode}")
        for line in process.stderr.splitlines():
            if line.strip():
                console.print(f"  [{PALETTE['err']}]{line.strip()}[/{PALETTE['err']}]")
        console.print()
 
def run_queries_menu():
    console.print()
    console.print(Rule(f"[bold {PALETTE['sage']}] Analytical Queries [/bold {PALETTE['sage']}]", style=PALETTE["dim"]))
    console.print()

    try:
        from src.pipeline import queries
        from src.pipeline.loaders.clickhouse import get_clickhouse_client
    except ImportError as e:
        console.print(f"[{PALETTE['err']}]Failed to import ETL modules: {e}[/{PALETTE['err']}]")
        return

    # Get all query variables
    query_vars = [var for var in dir(queries) if var.endswith("_QUERY")]
    if not query_vars:
        console.print(f"[{PALETTE['warn']}]No queries found in etl.queries[/{PALETTE['warn']}]")
        return

    table = Table(box=box.SIMPLE, show_header=False, border_style=PALETTE["dim"])
    table.add_column("№", style=f"bold {PALETTE['accent']}")
    table.add_column("Name", style=PALETTE["sage"])

    for i, var in enumerate(query_vars, 1):
        name = var.replace("_QUERY", "").replace("GET_", "").replace("_", " ").title()
        table.add_row(str(i), name)

    console.print(Panel(table, title=f"[bold {PALETTE['accent']}] Available Queries [/bold {PALETTE['accent']}]", border_style=PALETTE["dim"]))

    choice = Prompt.ask(
        f"\n  [{PALETTE['lavender']}]Select a query to preview/run (or 'q' to cancel)[/{PALETTE['lavender']}]",
        console=console,
    )

    if choice.lower() == 'q':
        return
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(query_vars):
            raise ValueError()
    except ValueError:
        console.print(f"[{PALETTE['err']}]Invalid selection.[/{PALETTE['err']}]")
        return

    selected_var = query_vars[idx]
    sql_query = getattr(queries, selected_var).strip()
    query_name = selected_var.replace("_QUERY", "").replace("GET_", "").replace("_", " ").title()

    console.print(f"\n[{PALETTE['lavender']}]Preview:[/{PALETTE['lavender']}]")
    syntax = Syntax(sql_query, "sql", theme="monokai", line_numbers=False, background_color="default")
    console.print(Panel(syntax, border_style=PALETTE["dim"]))

    confirm = Prompt.ask(f"  [{PALETTE['sage']}]Execute this query?[/{PALETTE['sage']}]", choices=["y", "n"], default="y")
    if confirm == "y":
        client = get_clickhouse_client()
        if not client:
            console.print(f"[{PALETTE['err']}]Database client unavailable.[/{PALETTE['err']}]")
            return
            
        with console.status(f"[{PALETTE['lavender']}]Executing query...[/{PALETTE['lavender']}]"):
            df = client.execute(sql_query)

        console.print()
        if df is None or df.empty:
            console.print(f"[{PALETTE['warn']}]Query returned no results.[/{PALETTE['warn']}]")
        else:
            result_table = Table(
                box=box.SIMPLE_HEAVY,
                show_header=True,
                header_style=f"bold {PALETTE['lavender']}",
                border_style=PALETTE["dim"],
                title=f"[bold {PALETTE['sage']}] {query_name} [/bold {PALETTE['sage']}]"
            )
            for col in df.columns:
                result_table.add_column(str(col), style=PALETTE["muted"])
            for _, row in df.iterrows():
                result_table.add_row(*[str(val) for val in row])
            console.print(result_table)

def main(verbose: bool = False):
    console.clear()
 
    if verbose:
        header()
    else:
        console.print(
            Align.center(f"[bold {PALETTE['lavender']}]Databhouse CLI  ·  @jobby[/bold {PALETTE['lavender']}]")
        )
        console.print()
 
    context_panel()
 
    while True:
        choice = menu_panel()
 
        if choice == "1":
            run_etl()
        elif choice == "2":
            toggle_services("start")
        elif choice == "3":
            toggle_services("stop")
        elif choice == "4":
            run_queries_menu()
        elif choice == "5":
            console.print(
                f"\n  [{PALETTE['muted']}]Goodbye.[/{PALETTE['muted']}]\n"
            )
            raise typer.Exit()
 
        input_again = Prompt.ask(
            f"  [{PALETTE['dim']}]Press Enter to return to menu, or 'q' to quit[/{PALETTE['dim']}]",
            default="",
            console=console,
        )
        if input_again.strip().lower() == "q":
            console.print(f"\n  [{PALETTE['muted']}]Goodbye.[/{PALETTE['muted']}]\n")
            raise typer.Exit()
        console.clear()
        if verbose:
            header()
 
if __name__ == "__main__":
    typer.run(main)