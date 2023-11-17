import redis
import json
import curses

# Initialize Redis connection (replace with your Redis server details)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_bounding_boxes():
    """Fetch bounding boxes data from Redis."""
    data = redis_client.get('bounding_boxes')
    if data is None:
        return []
    return json.loads(data)

def save_bounding_boxes(bounding_boxes):
    """Save modified bounding boxes data to Redis."""
    redis_client.set('bounding_boxes', json.dumps(bounding_boxes))

def modify_value(screen, bounding_boxes, index, key, delta):
    """Modify a value in the bounding box."""
    if key in bounding_boxes[index]:
        bounding_boxes[index][key] += delta
        bounding_boxes[index][key] = round(bounding_boxes[index][key], 2)
        save_bounding_boxes(bounding_boxes)

def display_and_edit(screen):
    """Display the bounding boxes and handle user input for editing."""
    curses.curs_set(0)  # Hide cursor

    while True:
        screen.clear()
        bounding_boxes = get_bounding_boxes()
        selected_index = 0
        key_index = 0
        keys = ['color', 'min_x', 'max_x', 'min_y', 'max_y']

        while True:
            screen.clear()
            for i, box in enumerate(bounding_boxes):
                selected = '>' if i == selected_index else ' '
                screen.addstr(f"{selected} Box {i}[{key_index}]: {box}\n")

            screen.addstr("\nUse UP/DOWN to select a box, RIGHT/LEFT to select a key, z/x to modify value, Q to quit\n")
            screen.refresh()

            char = screen.getch()
            if char == ord('q') or char == ord('Q'):
                return
            elif char == curses.KEY_UP and selected_index > 0:
                selected_index -= 1
            elif char == curses.KEY_DOWN and selected_index < len(bounding_boxes) - 1:
                selected_index += 1
            elif char == curses.KEY_LEFT and key_index > 0:
                key_index -= 1
            elif char == curses.KEY_RIGHT and key_index < len(keys) - 1:
                key_index += 1
            elif char == ord('x'):
                modify_value(screen, bounding_boxes, selected_index, keys[key_index], 0.01)
            elif char == ord('z'):
                modify_value(screen, bounding_boxes, selected_index, keys[key_index], -0.01)

# Run the curses application
curses.wrapper(display_and_edit)
