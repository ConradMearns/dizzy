"""Small YAML emission helpers for scaffold generators."""


def description_lines(description: str | None, indent: str) -> list[str]:
    """Render a LinkML ``description:`` field as valid YAML.

    Multi-line descriptions (common with ``|`` block scalars in feat files) are
    emitted as a literal block scalar so the continuation lines stay inside the
    value. Single-line descriptions keep the inline form.
    """
    text = (description or "").rstrip("\n")
    if "\n" not in text:
        return [f"{indent}description: {text}"]
    lines = [f"{indent}description: |-"]
    for line in text.split("\n"):
        lines.append(f"{indent}  {line}" if line else f"{indent}  ")
    return lines
