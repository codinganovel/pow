# pow

**pow** is a fast TUI file picker for quickly opening text files in your terminal. Navigate with arrow keys, search with fuzzy matching, and launch files directly in your configured editor — then get out of the way.
> Point, pick, POW! No more tedious path typing.
---
## ✨ Features
- Clean tree-style file browser interface
- Fuzzy search with typo tolerance using rapidfuzz
- Smart text file detection (extensions + content analysis)
- Opens files directly in your `$EDITOR` and exits cleanly
- Directory navigation with parent folder support
- Quick note creation with `Ctrl+N`
- Daily note functionality with `Ctrl+D`
- Automatic scrolling for large file lists
- Pure curses implementation - works everywhere
---
## 📦 Installation

[get yanked](https://github.com/codinganovel/yanked)

---
## 🚀 Usage
```bash
pow                    # Launch file picker in current directory
```

Navigate to any directory and run `pow` to quickly browse and open text files.

---
### Keyboard Controls
| Key         | Action                          |
|-------------|--------------------------------|
| `↑ ↓`       | Navigate file list             |
| `Enter`     | Open file or enter directory   |
| `/`         | Start fuzzy search             |
| `Ctrl+N`    | Create new note                |
| `Ctrl+D`    | Open/create daily note         |
| `ESC`       | Clear search                   |
| `q`         | Quit                           |

### Search Mode
| Key         | Action                          |
|-------------|--------------------------------|
| `Type`      | Filter files with fuzzy matching |
| `↑ ↓`       | Navigate filtered results       |
| `Enter`     | Open selected file             |
| `ESC`       | Exit search mode               |
| `Backspace` | Delete search characters       |

### Note Creation
| Key         | Action                          |
|-------------|--------------------------------|
| `Ctrl+N`    | Enter note creation mode       |
| `Type`      | Enter note title               |
| `Enter`     | Create note and open in editor |
| `ESC`       | Cancel note creation           |

### Daily Notes
Press `Ctrl+D` to instantly create or open today's daily note. The filename uses ISO format (e.g., `2025-06-24.md`) and is created in the current directory. If the file already exists, it opens directly.

Files are opened in your configured `$EDITOR` and pow exits immediately, returning you to your shell.
---
## ⚙️ Configuration
pow uses your system's default text editor:
```bash
export EDITOR=micro    # Set your preferred editor
export EDITOR=nano     # or nano
export EDITOR=vim      # or vim
```

If `$EDITOR` is not set, pow will show you how to configure it.
---
## 📋 Dependencies
pow requires one external dependency for fuzzy search:
```bash
pip install rapidfuzz
```

If rapidfuzz is not installed, pow will show installation instructions.

### Supported Text Files
Automatically detects common text file extensions:
- Code: `.py`, `.js`, `.rs`, `.go`, `.c`, `.cpp`, `.java`
- Web: `.html`, `.css`, `.scss`, `.json`, `.xml`
- Config: `.yaml`, `.toml`, `.ini`, `.conf`, `.env`
- Docs: `.md`, `.txt`, `.log`, `.csv`
- And many more...

Files without extensions are checked by content analysis.
---
## 📄 License

under ☕️, check out [the-coffee-license](https://github.com/codinganovel/The-Coffee-License)

I've included both licenses with the repo, do what you know is right. The licensing works by assuming you're operating under good faith.
---
## ✍️ Created by Sam  
Because navigating to files shouldn't be harder than editing them.