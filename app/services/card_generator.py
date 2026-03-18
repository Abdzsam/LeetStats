from html import escape
from math import cos, pi, radians, sin

from fastapi import Response
from app.services.heatmap_generator import build_heatmap_markup


def _difficulty_row(y: int, color: str, label: str, solved: int, total: int) -> str:
    progress = 0 if total <= 0 else min(max(solved / total, 0), 1)
    width = 305
    fill_width = max(progress * width, 8 if solved > 0 else 0)

    return f"""
    <text x="178" y="{y}" fill="#F3F4F6" font-size="16" font-weight="700" font-family="'Avenir Next Rounded', 'Nunito Sans', 'Trebuchet MS', sans-serif">{label}</text>
    <text x="474" y="{y}" fill="#ECECEC" font-size="15" font-weight="700" font-family="'Avenir Next Rounded', 'Nunito Sans', 'Trebuchet MS', sans-serif" text-anchor="end">{solved} / {total}</text>
    <rect x="178" y="{y + 11}" width="{width}" height="8" rx="4" fill="#414141" />
    <rect x="178" y="{y + 11}" width="{fill_width:.2f}" height="8" rx="4" fill="{color}" />
    """


def _polar_to_cartesian(cx: float, cy: float, radius: float, angle: float) -> tuple[float, float]:
    return cx + radius * cos(angle), cy + radius * sin(angle)


def _arc_path(cx: float, cy: float, radius: float, start: float, end: float) -> str:
    start_x, start_y = _polar_to_cartesian(cx, cy, radius, start)
    end_x, end_y = _polar_to_cartesian(cx, cy, radius, end)
    large_arc = 1 if end - start > pi else 0
    return (
        f"M {start_x:.2f} {start_y:.2f} "
        f"A {radius:.2f} {radius:.2f} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f}"
    )


def _segment_paths(
    cx: float, cy: float, radius: float, total: int, solved: int, start: float, span: float
) -> tuple[str, str]:
    solved_ratio = 0 if total <= 0 else min(max(solved / total, 0), 1)
    solved_end = start + span * solved_ratio
    track_path = _arc_path(cx, cy, radius, start, start + span)
    progress_path = _arc_path(cx, cy, radius, start, solved_end) if solved_ratio > 0 else ""
    return track_path, progress_path


def card_generator(stats: dict, show_heatmap: bool = False):
    username = escape(str(stats.get("username", "unknown")))
    ranking = int(stats.get("ranking", 0))
    current_streak = int(stats.get("current_streak", 0))

    easy_solved = int(stats.get("easy_solved", 0))
    medium_solved = int(stats.get("medium_solved", 0))
    hard_solved = int(stats.get("hard_solved", 0))

    easy_total = max(int(stats.get("easy_total", 0)), 1)
    medium_total = max(int(stats.get("medium_total", 0)), 1)
    hard_total = max(int(stats.get("hard_total", 0)), 1)

    total_solved = int(stats.get("total_solved", easy_solved + medium_solved + hard_solved))
    total_available = max(int(stats.get("total_available", easy_total + medium_total + hard_total)), 1)

    ranking_text = f"Rank #{ranking}" if ranking else "Rank Unranked"
    streak_color = "#FFA116" if current_streak > 0 else "#7F8794"

    gap = radians(10)
    total_span = radians(260)
    segment_span = (total_span - (2 * gap)) / 3
    easy_span = segment_span
    medium_span = segment_span
    hard_span = segment_span
    start_angle = radians(140)

    easy_start = start_angle
    medium_start = easy_start + easy_span + gap
    hard_start = medium_start + medium_span + gap

    easy_track, easy_progress = _segment_paths(
        88, 126, 60, easy_total, easy_solved, easy_start, easy_span
    )
    medium_track, medium_progress = _segment_paths(
        88, 126, 60, medium_total, medium_solved, medium_start, medium_span
    )
    hard_track, hard_progress = _segment_paths(
        88, 126, 60, hard_total, hard_solved, hard_start, hard_span
    )

    heatmap_markup = ""
    card_height = 200
    if show_heatmap:
        heatmap = build_heatmap_markup(
            stats.get("submission_calendar", {}),
            cell_size=8,
            gap=2,
            month_gap=5,
            include_month_labels=True,
            include_legend=False,
        )
        available_width = 500 - 32
        heatmap_scale = min(available_width / heatmap["width"], 1)
        scaled_height = heatmap["height"] * heatmap_scale
        heatmap_markup = f"""
        <line x1="16" y1="214" x2="484" y2="214" stroke="#2F2F2F" />
        <text x="24" y="236" fill="#F3F4F6" font-size="15" font-weight="700" font-family="'Avenir Next Rounded', 'Nunito Sans', 'Trebuchet MS', sans-serif">Heatmap (Last 52 Weeks)</text>
        <g transform="translate(16 244) scale({heatmap_scale:.4f})">
            {heatmap['markup']}
        </g>
        """
        card_height = int(244 + scaled_height + 12)

    svg = f"""<svg width="500" height="{card_height}" viewBox="0 0 500 {card_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="shadow" x="0" y="0" width="500" height="{card_height}" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
            <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000000" flood-opacity="0.24" />
        </filter>
    </defs>

    <g filter="url(#shadow)">
        <rect x="1.5" y="1.5" width="497" height="{card_height - 3}" rx="8.5" fill="#111111" />
        <rect x="1.5" y="1.5" width="497" height="{card_height - 3}" rx="8.5" stroke="#414141" />
    </g>

    <g transform="translate(20 15) scale(0.27)">
        <path d="M67.506,83.066 C70.000,80.576 74.037,80.582 76.522,83.080 C79.008,85.578 79.002,89.622 76.508,92.112 L65.435,103.169 C55.219,113.370 38.560,113.518 28.172,103.513 C28.112,103.455 23.486,98.920 8.227,83.957 C-1.924,74.002 -2.936,58.074 6.616,47.846 L24.428,28.774 C33.910,18.621 51.387,17.512 62.227,26.278 L78.405,39.362 C81.144,41.577 81.572,45.598 79.361,48.342 C77.149,51.087 73.135,51.515 70.395,49.300 L54.218,36.217 C48.549,31.632 38.631,32.262 33.739,37.500 L15.927,56.572 C11.277,61.552 11.786,69.574 17.146,74.829 C28.351,85.816 36.987,94.284 36.997,94.294 C42.398,99.495 51.130,99.418 56.433,94.123 L67.506,83.066 Z" fill="#FFA116" />
        <path d="M49.412,2.023 C51.817,-0.552 55.852,-0.686 58.423,1.722 C60.994,4.132 61.128,8.173 58.723,10.749 L15.928,56.572 C11.277,61.551 11.786,69.573 17.145,74.829 L36.909,94.209 C39.425,96.676 39.468,100.719 37.005,103.240 C34.542,105.760 30.506,105.804 27.990,103.336 L8.226,83.956 C-1.924,74.002 -2.936,58.074 6.617,47.846 L49.412,2.023 Z" fill="#F5F5F5" />
        <path d="M40.606,72.001 C37.086,72.001 34.231,69.142 34.231,65.614 C34.231,62.087 37.086,59.228 40.606,59.228 L87.624,59.228 C91.145,59.228 94,62.087 94,65.614 C94,69.142 91.145,72.001 87.624,72.001 L40.606,72.001 Z" fill="#8E8E8E" />
    </g>

    <text x="64" y="40" fill="#F7F7F7" font-size="25" font-weight="700" dominant-baseline="middle" font-family="'Avenir Next Rounded', 'Nunito Sans', 'Trebuchet MS', sans-serif">{username}</text>
    <g transform="translate(320 27)">
        <path d="M12.7 1.8C13.2 5.1 11.6 7 10.1 8.7C9 9.9 8.1 10.9 8.1 12.5C8.1 14.6 9.8 16.2 12 16.2C14.9 16.2 16.9 13.8 16.9 10.9C16.9 7.4 14.9 4.5 12.7 1.8Z" fill="{streak_color}" />
        <path d="M10.8 10.2C11.1 11.9 10.2 12.8 9.5 13.7C8.9 14.3 8.5 14.9 8.5 15.8C8.5 17.4 9.8 18.7 11.4 18.7C13.6 18.7 15.1 16.9 15.1 14.8C15.1 12.3 13.6 10.2 12 8.8C11.7 9.4 11.3 9.8 10.8 10.2Z" fill="{streak_color}" opacity="0.55" />
        <text x="22" y="12" fill="{streak_color}" font-size="12" font-weight="800" dominant-baseline="middle" font-family="'Avenir Next Rounded', 'Nunito Sans', 'Trebuchet MS', sans-serif">{current_streak}</text>
    </g>
    <text x="478" y="40" fill="#E5E5E5" font-size="17" font-weight="700" dominant-baseline="middle" font-family="'Avenir Next Rounded', 'Nunito Sans', 'Trebuchet MS', sans-serif" text-anchor="end">{ranking_text}</text>

    <path d="{easy_track}" stroke="#24535A" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="{medium_track}" stroke="#6E5928" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="{hard_track}" stroke="#642F33" stroke-width="7" stroke-linecap="round" fill="none" />

    <path d="{easy_progress}" stroke="#27C2D1" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="{medium_progress}" stroke="#FFBF1F" stroke-width="7" stroke-linecap="round" fill="none" />
    <path d="{hard_progress}" stroke="#FF5757" stroke-width="7" stroke-linecap="round" fill="none" />

    <text x="88" y="126" fill="#F5F5F5" font-size="30" font-weight="700" font-family="'Avenir Next Rounded', 'Nunito Sans', 'Trebuchet MS', sans-serif" text-anchor="middle" dominant-baseline="central">{total_solved}</text>

    {_difficulty_row(82, "#27C2D1", "Easy", easy_solved, easy_total)}
    {_difficulty_row(117, "#FFBF1F", "Medium", medium_solved, medium_total)}
    {_difficulty_row(152, "#FF5757", "Hard", hard_solved, hard_total)}
    {heatmap_markup}
    </svg>"""

    return Response(content=svg, media_type="image/svg+xml")
