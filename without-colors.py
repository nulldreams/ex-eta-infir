import json
import os
import re
from PIL import Image
from colorama import init, Fore, Style

init(autoreset=True)

SPRITE_SHEET_PATH = "spritesheets"
OUTPUT_DIR = "output"
DIRECTIONS = 4

# Configurable filter for pattern selection (OTClient-style)
FILTER = {
    "frame": None,       # e.g., 0 to select only first frame
    "direction": None,   # 0=up, 1=right, 2=down, 3=left
    "addon": 0,          # Only base
    "mount": 0,          # Only no mount
    "layers": [0],       # [0] = base only, [0, 1] = both layers
}

def log_info(message):
    print(Fore.YELLOW + "[INFO] " + Style.RESET_ALL + message)

def log_success(message):
    print(Fore.GREEN + "[SUCCESS] " + Style.RESET_ALL + message)

def log_error(message):
    print(Fore.RED + "[ERROR] " + Style.RESET_ALL + message)

def load_json_data():
    log_info("Loading JSON data from assets-editor-data.json...")
    with open('assets-editor-data.json', 'r') as f:
        data = json.load(f)
    log_info(f"Loaded {len(data)} character entries.")
    return data

def get_filtered_sprite_indexes(sprite_info, filter_config):
    pattern_x = sprite_info["patternWidth"]
    pattern_y = sprite_info["patternHeight"]
    pattern_z = sprite_info["patternDepth"]
    layers = sprite_info["layers"]
    frames = len(sprite_info.get("animation", {}).get("spritePhase", [0])) or 1

    indexes = []

    for frame in range(frames):
        if filter_config["frame"] is not None and filter_config["frame"] != frame:
            continue

        for z in range(pattern_z):
            if filter_config["mount"] is not None and filter_config["mount"] != z:
                continue

            for y in range(pattern_y):
                if filter_config["addon"] is not None and filter_config["addon"] != y:
                    continue

                for x in range(pattern_x):
                    if filter_config["direction"] is not None and filter_config["direction"] != x:
                        continue

                    for layer in range(layers):
                        if layer not in filter_config["layers"]:
                            continue

                        index = ((((frame * pattern_z + z) * pattern_y + y) * pattern_x + x) * layers + layer)
                        indexes.append(index)

    return indexes

def get_sprite_sheet_by_id(sprite_id):
    for file in os.listdir(SPRITE_SHEET_PATH):
        numbers = re.findall(r'\d+', file)
        if int(numbers[0]) <= sprite_id and int(numbers[1]) >= sprite_id:
            return file
    raise ValueError(f"Sprite ID {sprite_id} not found in any sprite sheet!")

def get_real_position_inside_sprite_sheet(sprite_id: int, filename: str):
    match = re.match(r"(\d+)-(\d+)", filename)
    if not match:
        raise ValueError(f"Invalid filename format: {filename}")

    start = int(match.group(1))
    end = int(match.group(2))
    if not (start <= sprite_id <= end):
        raise ValueError(f"Sprite ID {sprite_id} is out of bounds for file {filename} ({start}-{end})")

    return sprite_id - start

def get_sprite_at_position(position, sprite_sheet_path, sprite_size):
    sprite_sheet = Image.open(sprite_sheet_path)
    cols = sprite_sheet.width // sprite_size

    x = position % cols
    y = position // cols

    box = (
        x * sprite_size,
        y * sprite_size,
        (x + 1) * sprite_size,
        (y + 1) * sprite_size
    )

    return sprite_sheet.crop(box)

def array_to_chunks(array, chunk_size):
    return [array[i:i + chunk_size] for i in range(0, len(array), chunk_size)]

def generate_sprite_sheet(data, sprite_size, output_path):
    log_info(f"Generating spritesheet for character ID {data['id']} (sprite size: {sprite_size})")
    animations_images = []
    sprite_sheet_width = 0
    sprite_sheet_height = 0

    for aa, frame_group in enumerate(data["frameGroup"]):
        sprite_info = frame_group["spriteInfo"]
        sprite_ids = sprite_info["spriteId"]
        filtered_indexes = get_filtered_sprite_indexes(sprite_info, FILTER)
        log_info(f"  Extracting {len(filtered_indexes)} filtered sprites from {len(sprite_ids)} total.")

        cols = min(8, len(filtered_indexes))
        rows = (len(filtered_indexes) + cols - 1) // cols
        image = Image.new("RGBA", (sprite_size * cols, sprite_size * DIRECTIONS))

        print(filtered_indexes)

        for y, chunk in enumerate(array_to_chunks(filtered_indexes, DIRECTIONS)):
            for x, sprite_chunk_id in enumerate(chunk):
                sprite_id = sprite_ids[sprite_chunk_id]
                sprite_sheet_name = get_sprite_sheet_by_id(sprite_id)
                sprite_sheet_path = os.path.join(SPRITE_SHEET_PATH, sprite_sheet_name)
                sprite_position = get_real_position_inside_sprite_sheet(sprite_id, sprite_sheet_name)
                sprite_piece = get_sprite_at_position(sprite_position, sprite_sheet_path, sprite_size)

                image.paste(sprite_piece, (y * sprite_size, x * sprite_size))
                image.save(f"output/character_{data['id']}_{y}.png" )
            # print(chunk, sprite_chunk_id, sprite_id)
            # raise Exception("stop")

        # for i, index in enumerate(filtered_indexes):
        #     if index >= len(sprite_ids):
        #         log_error(f"  [WARNING] Index {index} is out of bounds for spriteId list.")
        #         continue

        #     sprite_id = sprite_ids[index]
        #     sprite_sheet_name = get_sprite_sheet_by_id(sprite_id)
        #     sprite_sheet_path = os.path.join(SPRITE_SHEET_PATH, sprite_sheet_name)
        #     sprite_position = get_real_position_inside_sprite_sheet(sprite_id, sprite_sheet_name)
        #     sprite_piece = get_sprite_at_position(sprite_position, sprite_sheet_path, sprite_size)

        #     x = i % cols
        #     y = i // cols

        #     print(cols, rows, x, y)
        #     if aa > 0:
        #         raise Exception("stop")

        #     image.paste(sprite_piece, (x * sprite_size, y * sprite_size))
        #     image.save(f"output/character_{data['id']}_{i}.png" )

        sprite_sheet_width = max(sprite_sheet_width, image.width)
        sprite_sheet_height += image.height
        animations_images.append(image)

    final_sheet = Image.new("RGBA", (sprite_sheet_width, sprite_sheet_height))
    for i, animation_image in enumerate(animations_images):
        final_sheet.paste(animation_image, (0, i * animation_image.height))

    final_sheet.save(output_path)

    # thumb_path = os.path.join("output", "thumbs")
    # os.makedirs(thumb_path, exist_ok=True)
    # thumbnail = final_sheet.copy()
    # thumbnail.thumbnail((160, 160))
    # thumbnail.save(os.path.join(thumb_path, f"character_{data['id']}_thumb.png"))

    log_success(f"Spritesheet saved to {output_path}\n")

def main():
    print(Style.BRIGHT + Fore.MAGENTA + "\U0001f9d9 Exeta Infir - Tibia Sprite Extractor")
    log_info("Initializing...")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        log_info(f"Created output directory: {OUTPUT_DIR}")

    data = load_json_data()

    for character in data:
        output_path = os.path.join(OUTPUT_DIR, f"character_{character['id']}.png")
        sprite_size = character["size"]
        try:
            generate_sprite_sheet(character, sprite_size, output_path)
        except Exception as e:
            log_error(f"Failed to process character ID {character['id']}: {e}")

    log_info("All spritesheets generated successfully. Project complete! \U0001f389")

if __name__ == "__main__":
    main()
