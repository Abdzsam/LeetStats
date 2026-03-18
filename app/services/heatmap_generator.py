from datetime import datetime, timedelta, timezone

from fastapi import Response


def _heat_color(count: int, max_count: int) -> str:
    if count <= 0:
        return "#202328"
    if max_count <= 1:
        return "#9BE9A8"
    if count <= 2:
        return "#144D1F"
    if count <= 5:
        return "#1F7A2E"
    if count <= 9:
        return "#35A546"
    return "#7BC96F"


def _quantile_thresholds(values: list[int]) -> tuple[int, int, int]:
    nonzero = sorted(value for value in values if value > 0)
    if not nonzero:
        return (0, 0, 0)

    def pick(ratio: float) -> int:
        index = min(int(len(nonzero) * ratio), len(nonzero) - 1)
        return nonzero[index]

    return (pick(0.25), pick(0.5), pick(0.75))


def _heat_color_from_thresholds(count: int, thresholds: tuple[int, int, int]) -> str:
    if count <= 0:
        return "#2C2C2C"

    low, mid, high = thresholds
    if count <= max(low, 1):
        return "#144D1F"
    if count <= max(mid, max(low, 1)):
        return "#1F7A2E"
    if count <= max(high, max(mid, 1)):
        return "#35A546"
    return "#7BC96F"


def build_heatmap_markup(
    calendar: dict,
    *,
    x_offset: int = 0,
    y_offset: int = 0,
    cell_size: int = 15,
    gap: int = 3,
    month_gap: int = 10,
    include_month_labels: bool = True,
    include_legend: bool = True,
):
    now = datetime.now(timezone.utc).date()
    start = now - timedelta(days=364)
    dates = [start + timedelta(days=index) for index in range(365)]

    values = []
    for day in dates:
        timestamp = str(
            int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())
        )
        values.append(int(calendar.get(timestamp, 0)))

    max_count = max(values) if values else 0
    thresholds = _quantile_thresholds(values)

    pitch = cell_size + gap
    top = 24

    month_groups = []
    current_month = None
    current_days = []
    for day in dates:
        key = (day.year, day.month)
        if key != current_month:
            if current_days:
                month_groups.append((current_month, current_days))
            current_month = key
            current_days = [day]
        else:
            current_days.append(day)
    if current_days:
        month_groups.append((current_month, current_days))

    month_labels = []
    x_cursor = 18

    for (year, month), month_days in month_groups:
        first_day = month_days[0].replace(day=1)
        first_weekday = (first_day.weekday() + 1) % 7
        month_column_count = 0

        for day in month_days:
            week = (first_weekday + day.day - 1) // 7
            month_column_count = max(month_column_count, week + 1)

        month_name = datetime(year, month, 1).strftime("%b")
        if include_month_labels:
            month_labels.append(
                f'<text x="{x_offset + x_cursor}" y="{y_offset + 16}" fill="#A5A5A5" font-size="10" '
                f'font-family="Verdana, Geneva, sans-serif">{month_name}</text>'
            )
        x_cursor += month_column_count * pitch + month_gap

    width = x_cursor + 10
    height = 7 * pitch + 54
    legend_y = height - 16

    cells = []
    x_cursor = 18
    for (year, month), month_days in month_groups:
        first_day = month_days[0].replace(day=1)
        first_weekday = (first_day.weekday() + 1) % 7
        month_column_count = 0

        for day in month_days:
            week = (first_weekday + day.day - 1) // 7
            month_column_count = max(month_column_count, week + 1)
            weekday = (day.weekday() + 1) % 7
            x = x_offset + x_cursor + week * pitch
            y = y_offset + top + weekday * pitch
            timestamp = str(
                int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())
            )
            count = int(calendar.get(timestamp, 0))
            color = _heat_color_from_thresholds(count, thresholds)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="4" fill="{color}" />'
            )
        x_cursor += month_column_count * pitch + month_gap

    legend = []
    if include_legend:
        legend = [
            f'<text x="{x_offset + 18}" y="{y_offset + legend_y}" fill="#8E8E8E" font-size="10" font-family="Verdana, Geneva, sans-serif">Less</text>',
            f'<rect x="{x_offset + 46}" y="{y_offset + legend_y - 8}" width="10" height="10" rx="3" fill="#2C2C2C" />',
            f'<rect x="{x_offset + 60}" y="{y_offset + legend_y - 8}" width="10" height="10" rx="3" fill="#144D1F" />',
            f'<rect x="{x_offset + 74}" y="{y_offset + legend_y - 8}" width="10" height="10" rx="3" fill="#1F7A2E" />',
            f'<rect x="{x_offset + 88}" y="{y_offset + legend_y - 8}" width="10" height="10" rx="3" fill="#35A546" />',
            f'<rect x="{x_offset + 102}" y="{y_offset + legend_y - 8}" width="10" height="10" rx="3" fill="#7BC96F" />',
            f'<text x="{x_offset + 120}" y="{y_offset + legend_y}" fill="#8E8E8E" font-size="10" font-family="Verdana, Geneva, sans-serif">More</text>',
        ]

    return {
        "width": width,
        "height": height,
        "markup": "".join(month_labels) + "".join(cells) + "".join(legend),
    }


def heatmap_generator(stats: dict):
    heatmap = build_heatmap_markup(
        stats.get("submission_calendar", {}),
        cell_size=11,
        gap=2,
        month_gap=7,
    )

    svg = f"""<svg width="{heatmap['width']}" height="{heatmap['height']}" viewBox="0 0 {heatmap['width']} {heatmap['height']}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{heatmap['width']}" height="{heatmap['height']}" rx="16" fill="#24262B" />
    {heatmap['markup']}
    </svg>"""

    return Response(content=svg, media_type="image/svg+xml")
