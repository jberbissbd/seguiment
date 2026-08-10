AVATAR_PALETTE = (
    ("#DBEAFE", "#1D4ED8"),
    ("#DCFCE7", "#15803D"),
    ("#FCE7F3", "#BE185D"),
    ("#FEF3C7", "#B45309"),
    ("#EDE9FE", "#6D28D9"),
    ("#CFFAFE", "#0E7490"),
)


def initials(name: str, surnames: str) -> str:
    parts = [part for part in (name.strip(), surnames.strip()) if part]
    return "".join(part[0].upper() for part in parts[:2]) or "?"


def avatar_colors(key) -> tuple[str, str]:
    index = sum(ord(character) for character in str(key)) % len(AVATAR_PALETTE)
    return AVATAR_PALETTE[index]


def avatar_stylesheet(key, radius: int) -> str:
    background, foreground = avatar_colors(key)
    return (
        f"background-color: {background}; color: {foreground}; border: none; "
        f"border-radius: {radius}px; font-weight: 700;"
    )
