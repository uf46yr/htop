# Enhanced System Monitor

A feature-rich, terminal-based system monitoring tool built with Python's curses library. This tool provides real-time monitoring of system resources and processes with a colorful, user-friendly interface.

![System Monitor Demo](https://via.placeholder.com/800x400?text=Enhanced+System+Monitor+Demo)

## Features

- **Real-time System Monitoring**: CPU usage, memory consumption, disk usage, and more
- **Process Management**: View running processes with detailed information
- **Color-coded Interface**: Visual indicators for system health
- **Dual View Modes**: Toggle between basic and detailed process views
- **Cross-platform Support**: Works on Linux and macOS systems
- **Battery & Temperature Monitoring**: Support for laptop users (where available)
- **Responsive Design**: Adapts to different terminal sizes

## Requirements

- Python 3.6+
- curses library (usually included with Python standard library)
- Linux or macOS (Windows support requires WSL)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/uf46yr/htop.git
cd htop
```
2. Make the script executable:
```bash
chmod +x htop.py
```

## Usage

Run the monitor directly:
```bash
./htop.py
```

Or using Python:
```bash
python3 htop.py
```

### Controls
- `D` - Toggle between basic and detailed process views
- `Q` - Quit the application

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `D` | Toggle detailed/basic view |
| `Q` | Quit the application |

## Display Information

### System Overview
- Hostname and system uptime
- CPU usage percentage
- Memory usage (used/total and percentage)
- Disk usage statistics
- System load averages
- Battery status (if available)
- System temperature (if available)

### Process Information
- Process ID (PID)
- User owning the process
- CPU utilization percentage
- Memory usage percentage
- Virtual and resident memory size (detailed view)
- Process execution time (detailed view)
- Command name

## Customization

You can modify the script to:
- Change update interval by modifying `update_interval` value
- Adjust color schemes in the `init_colors` method
- Modify process sorting by changing the `process_sort` variable
- Add new system metrics by extending the `get_system_info` method

## Troubleshooting

### Common Issues

1. **Curses not available**:
   - On Windows: Use WSL (Windows Subsystem for Linux)
   - Ensure Python curses support is installed

2. **Missing system information**:
   - The tool uses standard system commands
   - Ensure commands like `ps`, `top`, `free` are available

3. **Display issues**:
   - Ensure your terminal supports UTF-8
   - Use a terminal with at least 80x24 characters

### Fallback Mode

If curses is unavailable, the script will automatically fall back to a basic text-mode interface.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python's curses library
- Inspired by classic system monitoring tools like top and htop
- Thanks to all contributors who have helped with development

## Support

If you encounter any problems or have questions:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information about your problem

---

**Note**: This tool is designed for monitoring purposes only and may not display identical information across all system configurations. Some features require specific hardware support (e.g., battery and temperature monitoring).
```
