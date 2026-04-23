"""LibConfig generator — generates libconfig.yaml stub from a FeatureDefinition."""

from pathlib import Path

from dizzy.feat_schema import FeatureDefinition


def render_libconfig_stub(feat: FeatureDefinition, default_runtime: str = "python-uv") -> str:
    """Render libconfig.yaml stub content from a FeatureDefinition."""
    lines = [
        "# Dizzy library configuration — assign runtimes to each element",
        "# Supported runtimes: python-uv | rust-cargo | typescript-npm",
        "",
    ]
    for section, items in [
        ("procedures", feat.procedures or []),
        ("policies", feat.policies or []),
        ("queries", feat.queries or []),
        ("projections", feat.projections or []),
    ]:
        if items:
            lines.append(f"{section}:")
            for item in items:
                lines.append(f"  {item.name}:")
                lines.append(f"    runtimes: [{default_runtime}]")
            lines.append("")
    return "\n".join(lines)


def write_libconfig_stub(
    feat: FeatureDefinition,
    output_dir: Path,
    default_runtime: str = "python-uv",
) -> None:
    """Write libconfig.yaml to output_dir; skip if file already exists."""
    dest = output_dir / "libconfig.yaml"
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(render_libconfig_stub(feat, default_runtime=default_runtime))
