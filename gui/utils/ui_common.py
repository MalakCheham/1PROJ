import pygame


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_text_fit(text, font_name, color, max_width, min_size=18, max_size=48, bold=True):
    size = max_size
    while size >= min_size:
        font = pygame.font.SysFont(font_name, size, bold=bold)
        surf = font.render(text, True, color)
        if surf.get_width() <= max_width:
            return surf, font
        size -= 2
    font = pygame.font.SysFont(font_name, min_size, bold=bold)
    return font.render(text, True, color), font
