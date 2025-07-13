#!/usr/bin/env python3
"""
Simple TUI file explorer for quickly opening text files.
Navigate with arrow keys, search with /, open with Enter.
"""

try:
    import curses
    import os
    from pathlib import Path
    from rapidfuzz import fuzz
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    print("Install with: pip install rapidfuzz")
    exit(1)

# Text file extensions to automatically include
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml',
    '.html', '.css', '.sh', '.conf', '.cfg', '.ini', '.log',
    '.sql', '.xml', '.csv', '.toml', '.rs', '.go', '.c', '.cpp',
    '.h', '.hpp', '.java', '.php', '.rb', '.pl', '.ts', '.jsx',
    '.tsx', '.vue', '.svelte', '.scss', '.sass', '.less'
}

class FileExplorer:
    def __init__(self):
        self.current_path = Path.cwd()
        self.cursor_position = 0
        self.items = []
        self.search_mode = False
        self.search_query = ""
        self.filtered_items = []
        
    def is_text_file(self, path):
        """Check if file is text based on extension or content"""
        if path.suffix.lower() in TEXT_EXTENSIONS:
            return True
        
        # For files without extension, check content
        if not path.suffix:
            try:
                with open(path, 'rb') as f:
                    chunk = f.read(512)
                    try:
                        chunk.decode('utf-8')
                        # Check if mostly printable characters
                        printable_ratio = sum(c < 127 and (c >= 32 or c in [9, 10, 13]) for c in chunk) / len(chunk)
                        return printable_ratio > 0.8
                    except UnicodeDecodeError:
                        return False
            except (PermissionError, OSError):
                return False
        
        return False
    
    def scan_directory(self):
        """Scan current directory for text files and subdirectories"""
        self.items = []
        
        # Add parent directory if not at root
        if self.current_path != self.current_path.parent:
            self.items.append(("../", True, self.current_path.parent))
        
        try:
            entries = []
            for item in self.current_path.iterdir():
                # Skip hidden files
                if item.name.startswith('.'):
                    continue
                
                try:
                    if item.is_dir():
                        entries.append((f"{item.name}/", True, item))
                    elif item.is_file() and self.is_text_file(item):
                        entries.append((item.name, False, item))
                except (PermissionError, OSError):
                    # Skip files we can't read
                    continue
            
            # Sort: directories first, then files, both alphabetically
            entries.sort(key=lambda x: (not x[1], x[0].lower()))
            self.items.extend(entries)
            
        except PermissionError:
            # Will be shown in render_ui
            pass
            
        # Reset cursor if out of bounds
        if self.items:
            self.cursor_position = min(self.cursor_position, len(self.items) - 1)
            self.cursor_position = max(0, self.cursor_position)
        else:
            self.cursor_position = 0
    
    def render_ui(self, stdscr):
        """Render the current UI state"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        row = 0
        
        # Header - current path
        path_str = str(self.current_path)
        if len(path_str) > width - 1:
            path_str = "..." + path_str[-(width-4):]
        stdscr.addstr(row, 0, path_str)
        row += 1
        
        # Search bar if in search mode
        if self.search_mode:
            search_str = f"Search: {self.search_query}"
            if len(search_str) < width - 1:
                search_str += "▌"
            stdscr.addstr(row, 0, search_str[:width-1])
            row += 1
            display_items = self.filtered_items
        else:
            display_items = self.items
            
        row += 1  # Empty line
        
        # File list with cursor
        if not display_items:
            if row < height - 1:
                stdscr.addstr(row, 0, "No text files found")
        else:
            # Calculate how many items we can show
            available_rows = height - row - 2  # Leave space for status line
            start_idx = max(0, self.cursor_position - available_rows + 1)
            end_idx = min(len(display_items), start_idx + available_rows)
            
            # Adjust start if we're at the end
            if end_idx == len(display_items):
                start_idx = max(0, end_idx - available_rows)
            
            for i in range(start_idx, end_idx):
                if row >= height - 2:  # Leave space for status
                    break
                    
                name, is_dir, path = display_items[i]
                
                # Tree characters
                if i == len(display_items) - 1:
                    prefix = "└── "
                else:
                    prefix = "├── "
                    
                # Build display line
                display_line = prefix + name
                
                # Add cursor indicator
                if i == self.cursor_position:
                    if len(display_line) < width - 3:
                        display_line += " ◀"
                    else:
                        display_line = display_line[:width-4] + " ◀"
                
                # Truncate if too long
                if len(display_line) > width - 1:
                    display_line = display_line[:width-1]
                
                stdscr.addstr(row, 0, display_line)
                row += 1
        
        # Status line at bottom
        if self.search_mode:
            if display_items:
                status = f"[{len(self.filtered_items)} of {len(self.items)} items] • ESC clear • Enter open"
            else:
                status = f"[0 of {len(self.items)} items] • ESC clear search"
        else:
            status = f"[{len(self.items)} items] • ↑↓ navigate • Enter open • q quit • / search"
        
        # Show status at bottom
        status_row = height - 1
        if len(status) > width - 1:
            status = status[:width-1]
        stdscr.addstr(status_row, 0, status)
        
        stdscr.refresh()
    
    def handle_search(self, query):
        """Filter items using fuzzy search"""
        if not query:
            self.filtered_items = self.items[:]
        else:
            matches = []
            for item in self.items:
                score = fuzz.ratio(query.lower(), item[0].lower())
                if score > 40:  # Threshold for relevance
                    matches.append((score, item))
            
            # Sort by score (best matches first)
            matches.sort(key=lambda x: x[0], reverse=True)
            self.filtered_items = [item for score, item in matches]
        
        # Reset cursor position
        self.cursor_position = 0
    
    def open_file(self, file_path):
        """Open file in configured editor and exit"""
        # Restore terminal before launching editor
        curses.endwin()
        
        editor = os.getenv('EDITOR')
        if not editor:
            print("\nError: No text editor configured")
            print("Set your default editor: export EDITOR=micro")
            print("Then restart your shell or run: source ~/.zshrc")
            input("Press Enter to exit...")
            return
            
        try:
            # Split editor command in case it has flags
            editor_cmd = editor.split()
            args = editor_cmd + [str(file_path)]
            os.execvp(editor_cmd[0], args)
        except Exception as e:
            print(f"\nError launching editor: {e}")
            print("Check your $EDITOR setting")
            input("Press Enter to exit...")
    
    def navigate_to(self, path):
        """Navigate to a new directory"""
        try:
            self.current_path = path.resolve()
            self.cursor_position = 0
            self.search_mode = False
            self.search_query = ""
            self.scan_directory()
        except PermissionError:
            # Error will be visible in next render
            pass
    
    def handle_input(self, key):
        """Handle keyboard input"""
        current_items = self.filtered_items if self.search_mode else self.items
        
        if self.search_mode:
            if key == 27:  # Escape
                self.search_mode = False
                self.search_query = ""
                self.cursor_position = 0
            elif key in (127, curses.KEY_BACKSPACE, 8):  # Backspace
                self.search_query = self.search_query[:-1]
                self.handle_search(self.search_query)
            elif key in (10, 13) and current_items:  # Enter
                selected = current_items[self.cursor_position]
                if selected[1]:  # Directory
                    self.navigate_to(selected[2])
                else:  # File
                    self.open_file(selected[2])
            elif 32 <= key <= 126:  # Printable ASCII
                self.search_query += chr(key)
                self.handle_search(self.search_query)
        else:
            if key == ord('q'):
                return False  # Quit
            elif key == ord('/'):
                self.search_mode = True
                self.search_query = ""
                self.handle_search("")
            elif key == curses.KEY_UP and current_items:
                self.cursor_position = max(0, self.cursor_position - 1)
            elif key == curses.KEY_DOWN and current_items:
                self.cursor_position = min(len(current_items) - 1, self.cursor_position + 1)
            elif key in (10, 13) and current_items:  # Enter
                selected = current_items[self.cursor_position]
                if selected[1]:  # Directory
                    self.navigate_to(selected[2])
                else:  # File
                    self.open_file(selected[2])
        
        return True  # Continue running
    
    def run(self):
        """Main application loop with curses"""
        self.scan_directory()
        
        def main_loop(stdscr):
            # Setup curses
            curses.curs_set(0)  # Hide cursor
            stdscr.timeout(100)  # Non-blocking input
            
            while True:
                try:
                    self.render_ui(stdscr)
                    
                    # Get input
                    key = stdscr.getch()
                    if key == -1:  # No input (timeout)
                        continue
                        
                    if not self.handle_input(key):
                        break
                        
                except KeyboardInterrupt:
                    break
        
        curses.wrapper(main_loop)

def main():
    """Entry point"""
    try:
        explorer = FileExplorer()
        explorer.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()