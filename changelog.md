# Changelog

## 0.3

### Added
- **Daily Note Feature**: New `Ctrl+D` keyboard shortcut to quickly create or open today's daily note
  - Uses ISO date format: `YYYY-MM-DD.md` (e.g., `2025-06-24.md`)
  - Creates empty file if it doesn't exist, opens existing file if it does
  - Only works in normal navigation mode (not search or note creation modes)
  - Files are created in the current directory alongside other files

### Changed
- **Status Line**: Updated to show `Ctrl+N/D new/daily note` instead of just `Ctrl+N new note`
- **Dependencies**: Added `datetime` import for date handling (Python standard library)

### Technical Details
- Added `get_daily_note_filename()` method to generate ISO format filenames
- Added `open_daily_note()` method that reuses existing file opening logic
- Updated `handle_input()` method to detect `Ctrl+D` (key code 4) in navigation mode
- Enhanced status line rendering to include daily note shortcut

### Testing
- Added comprehensive test suite (`test_pow.py`) covering all functionality
- Tests verify text file detection, filename sanitization, search, and daily note features
- All existing functionality continues to work as expected

## Previous Versions

### Initial Release
- TUI file picker with curses interface
- Fuzzy search functionality using rapidfuzz
- Smart text file detection (extensions + content analysis)
- Note creation with `Ctrl+N`
- Directory navigation and file opening in `$EDITOR`
- Tree-style display with cursor navigation