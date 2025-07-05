# Glyphy Board Scripts

This directory contains board scripts organized into their own subdirectories. Each board has its own folder containing the main script and any supporting files.

## Directory Structure

```
boards/
├── daily-board/
│   └── daily-board.py         # Daily schedule board script
├── test-board/
│   └── test-board.py          # Test board script  
├── dashboard/
│   └── dashboard.py           # Default dashboard display
├── image/
│   └── image.py               # Single image display script
└── photo-album/
    ├── photo-album.py         # Photo album with random selection
    └── photos/                # Directory for photo files
        ├── .gitkeep           # Placeholder to preserve directory
        └── ...                # Your photos go here
```

## Available Boards

### Daily Board (`daily-board`)
Simple board that displays daily schedule information.

**Usage:**
```bash
python3 boards/daily-board/daily-board.py
```

### Test Board (`test-board`)
Test board for verification and debugging.

**Usage:**
```bash
python3 boards/test-board/test-board.py
```

### Dashboard (`dashboard`)
Default dashboard display shown when no schedule is active.

**Usage:**
```bash
python3 boards/dashboard/dashboard.py
```

### Image Board (`image`)
Displays a single specified image on the eink screen.

**Usage:**
```bash
python3 boards/image/image.py path/to/image.jpg [--pad] [--background-color COLOR]
```

**Options:**
- `--pad`: Pad image to fit screen while maintaining aspect ratio
- `--background-color COLOR`: Background color for padding (default: white)

### Photo Album (`photo-album`)
Displays images from the photos directory. If no image is specified, randomly selects one.

**Usage:**
```bash
# Random photo from photos directory
python3 boards/photo-album/photo-album.py

# Specific photo
python3 boards/photo-album/photo-album.py path/to/photo.jpg

# With options
python3 boards/photo-album/photo-album.py --pad --background-color black
```

**Setup:**
1. Add your image files to `boards/photo-album/photos/`
2. Supported formats: .jpg, .jpeg, .png, .bmp, .gif, .tiff, .tif, .webp
3. Run without arguments to display a random photo

## Creating New Boards

To create a new board:

1. **Create Directory:**
   ```bash
   mkdir boards/my-new-board
   ```

2. **Create Script:**
   ```bash
   touch boards/my-new-board/my-new-board.py
   chmod +x boards/my-new-board/my-new-board.py
   ```

3. **Basic Template:**
   ```python
   #!/usr/bin/env python3
   """
   My New Board Script
   """
   
   import sys
   from datetime import datetime
   
   def main():
       """Main function for board display"""
       current_time = datetime.now()
       
       print(f"=== My New Board Script Executed ===")
       print(f"Current time: {current_time}")
       
       # Your board logic here:
       # 1. Load display manager
       # 2. Create image content  
       # 3. Display on eink screen
       
       print("Board content displayed successfully!")
       return 0
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

4. **Add to Scheduler:**
   - Create schedule through web UI (`/schedules`)
   - Add schedule item with board name: `my-new-board`
   - Scheduler will automatically find and execute `boards/my-new-board/my-new-board.py`

## Integration with Scheduler

The scheduler automatically finds and executes board scripts using this pattern:
- Board name: `my-board`
- Script path: `boards/my-board/my-board.py`

This allows each board to have:
- Its own directory for organization
- Supporting files (images, configs, etc.)
- Clear separation from other boards

## Testing Boards

Test individual boards manually:
```bash
# Test daily board
python3 boards/daily-board/daily-board.py

# Test photo album (random)
python3 boards/photo-album/photo-album.py

# Test image display
python3 boards/image/image.py path/to/image.jpg --pad
```

Test with scheduler:
```bash
# Run scheduler (will execute active scheduled board)
python3 scheduler.py --debug
``` 