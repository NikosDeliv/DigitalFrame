import argparse
import os
from pathlib import Path
import time

import pygame

DEFAULT_IMAGE_FOLDER = Path.home() / "Pictures" / "Screenshots"
SUPPORTED_EXTENSIONS = {".bmp", ".gif", ".jpg", ".jpeg", ".png", ".webp"}


def find_image_filenames(image_folder):
    """Return supported images in a stable, case-insensitive order."""
    if not image_folder.is_dir():
        print(f"Error: folder '{image_folder}' does not exist.")
        return []

    return sorted(
        (
            path
            for path in image_folder.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: path.name.casefold(),
    )


def find_display_driver():
    """Try legacy Linux drivers when no driver was configured by the user."""
    if pygame.display.get_init():
        return True

    configured_driver = os.environ.get("SDL_VIDEODRIVER")
    drivers = (configured_driver,) if configured_driver else (None, "fbcon", "directfb", "svgalib")
    for driver in drivers:
        if driver is None:
            os.environ.pop("SDL_VIDEODRIVER", None)
        else:
            os.environ["SDL_VIDEODRIVER"] = driver
        try:
            pygame.display.init()
            return True
        except pygame.error:
            pygame.display.quit()
    return False


def scale_image_to_fit(image, screen_size):
    """Scale an image to fit without stretching or cropping it."""
    screen_width, screen_height = screen_size
    image_width, image_height = image.get_size()
    scale_factor = min(screen_width / image_width, screen_height / image_height)
    new_size = (
        max(1, round(image_width * scale_factor)),
        max(1, round(image_height * scale_factor)),
    )
    return pygame.transform.smoothscale(image, new_size)


def show_image(screen, filename, screen_size):
    try:
        image = pygame.image.load(filename).convert()
    except (pygame.error, OSError) as error:
        print(f"Skipping '{filename}': {error}")
        return False

    image = scale_image_to_fit(image, screen_size)
    screen.fill((0, 0, 0))
    position = (
        (screen_size[0] - image.get_width()) // 2,
        (screen_size[1] - image.get_height()) // 2,
    )
    screen.blit(image, position)
    pygame.display.flip()
    return True


def main():
    parser = argparse.ArgumentParser(description="Display a folder of images fullscreen.")
    parser.add_argument(
        "folder",
        nargs="?",
        type=Path,
        default=DEFAULT_IMAGE_FOLDER,
        help="folder containing images (default: %(default)s)",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=5.0,
        help="seconds to show each image (default: %(default)s)",
    )
    args = parser.parse_args()

    if args.seconds <= 0:
        parser.error("--seconds must be greater than zero")

    filenames = find_image_filenames(args.folder)
    if not filenames:
        print(f"No image files found in '{args.folder}'.")
        return

    if not find_display_driver():
        print("Failed to initialize a display.")
        pygame.quit()
        return
    pygame.font.init()

    screen_size = (
        pygame.display.Info().current_w,
        pygame.display.Info().current_h,
    )
    screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    clock = pygame.time.Clock()

    try:
        while filenames:
            for filename in filenames:
                if not show_image(screen, filename, screen_size):
                    continue

                end_time = time.monotonic() + args.seconds
                while time.monotonic() < end_time:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (
                            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                        ):
                            return
                    clock.tick(30)
    finally:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == "__main__":
    main()
