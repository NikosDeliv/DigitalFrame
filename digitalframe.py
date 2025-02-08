import os
import pygame 
import time

IMAGE_FOLDER = "C:/Users/User/Pictures/Screenshots"  # Change this to your desired folder path cause Im not showing yall mine lol 

def FindImageFilenames():
   
    lst = []
    if not os.path.exists(IMAGE_FOLDER):
        print(f"Error: Folder '{IMAGE_FOLDER}' does not exist.")
        return lst

    for filename in os.listdir(IMAGE_FOLDER):
        if filename.lower().endswith((".bmp", ".gif", ".jpg", ".png")):
            lst.append(os.path.join(IMAGE_FOLDER, filename))  # Store full path
    return lst
def FindDisplayDriver():
    for driver in ["fbcon", "directfb", "svgalib"]:
        if not os.getenv("SDL_VIDEODRIVER"):
            os.putenv("SDL_VIDEODRIVER", driver)
        try:
            pygame.display.init()
            return True
        except pygame.error:
            pass
    return False

def ScaleImageToFit(image, screen_width, screen_height):
    img_width, img_height = image.get_size()
    scale_factor = min(screen_width / img_width, screen_height / img_height)
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)
    return pygame.transform.scale(image, (new_width, new_height))

def Main():
    filenames = FindImageFilenames()
    if not filenames:
        print("No image files found in", IMAGE_FOLDER)
        return

    pygame.init()
    if not FindDisplayDriver():
        print("Failed to initialize display driver")
        return

    width = pygame.display.Info().current_w
    height = pygame.display.Info().current_h
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    while True:
        filename = filenames.pop(0)
        filenames.append(filename)

        image = pygame.image.load(filename)
        image = ScaleImageToFit(image, width, height)

        # Center the image on the screen
        img_x = (width - image.get_width()) // 2
        img_y = (height - image.get_height()) // 2

        screen.fill((0, 0, 0))  # Fill screen with black before drawing
        screen.blit(image, (img_x, img_y))
        pygame.display.update()

        for _ in range(5):
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                return
            time.sleep(1)

if __name__ == "__main__":
    Main()
