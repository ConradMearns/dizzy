"""Events generator — scaffold def/events.yaml."""

from pathlib import Path

from dizzy.feat_schema import EventDef


def render_scaffold_events(events: list[EventDef]) -> str:
    """Render a LinkML stub for def/events.yaml from the feat definition."""
    lines = [
        "id: https://example.org/events",
        "name: events",
        "prefixes:",
        "  linkml: https://w3id.org/linkml/",
        "default_range: string",
        "imports:",
        "  - linkml:types",
        "classes:",
    ]
    for evt in events:
        lines.append(f"  {evt.name}:")
        lines.append(f"    description: {evt.description}")
        lines.append("    attributes: {}")
    lines.append("")
    return "\n".join(lines)


def write_scaffold_events(events: list[EventDef], output_dir: Path) -> None:
    """Write def/events.yaml; skip if file already exists."""
    dest = output_dir / "def" / "events.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_scaffold_events(events))
