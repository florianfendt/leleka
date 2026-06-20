import typer
from core.config import ROLES, PROJECTS
from core.context import extract_markdown_section, parse_and_execute_bullet_points, load_context_file_content
from core.llm import stream_leleka_response

app = typer.Typer()

LELEKA_ROLES = {
    "bro": "gemma4:12b",
    "codex": "qwen2.5-coder",
    "lawmigo": "mistral-medium-3.5:latest",
    "omiracle": "gemma4:12b"
}

LELEKA_LOGO = r"""
[bold cyan]      ___  [/bold cyan]
[bold cyan]     /__/  [/bold cyan]      [bold yellow]___                .  [/bold yellow]
[bold cyan]    //     [/bold cyan]      [bold yellow]/  / _ _  _ _  _ _/_  [/bold yellow]
[bold cyan] __//      [/bold cyan]      [bold yellow]/_/_/_/ /_/_/ /_/_/ /_ [/bold yellow]
[bold cyan]// \  /    [/bold cyan]
[bold cyan]//   \/    [/bold cyan]      [bold cyan]>> F-SYS TERMINAL OS v1.0.0 <<[/bold cyan]
"""

@app.command("ask")
def q(
    prompt: str = typer.Argument(..., help="Dein Prompt an den Agenten"),
    role: str = typer.Option("bro", "--role", "-r", help=f"Rolle: {', '.join(LELEKA_ROLES.keys())}"),
    project: str = typer.Option(None, "--project", "-p", help="Projekt-ID für automatischen Kontext")
) -> None:

    # Der saubere Austausch: Erst die Ersetzung, dann direkt ausgeben
    LELEKA_LOGO_CYAN = LELEKA_LOGO.replace("[bold cyan]", "[bold magenta]").replace("[/bold cyan]", "[/bold magenta]")
    typer.echo(LELEKA_LOGO_CYAN)
    if role not in LELEKA_ROLES:
        typer.echo(f"Error: Role '{role}' not available. Allowed: {', '.join(LELEKA_ROLES.keys())}")
        raise typer.Exit()

    project_context = ""
    if project:
        file_path = PROJECTS / f"{project}.md"
        if file_path.exists():
            project_context_list = extract_markdown_section(file_path)
            project_context = parse_and_execute_bullet_points(project_context_list)
            project_context += "\n" + file_path.read_text(encoding="utf-8")
        else:
            typer.echo(f"Project context file '{file_path.name}' not found. Generating without project context.")

    system_prompt_file = ROLES / f"{role}_manifesto.md"
    system_prompt = load_context_file_content(system_prompt_file)
    model_name = LELEKA_ROLES.get(role)
    full_prompt = project_context + prompt

    # Abgabe an die Streaming-Engine
    stream_leleka_response(model_name, full_prompt, system_prompt)