#!/usr/bin/env python3

import curses
import time
import subprocess
import os
import sys
from datetime import datetime

class EnhancedSystemMonitor:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.colors = self.init_colors()
        self.setup_curses()
        self.process_sort = "cpu"  # Default sort by CPU
        self.show_details = False  # Toggle detailed view

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

        return {
            'RED': curses.color_pair(1),
            'GREEN': curses.color_pair(2),
            'YELLOW': curses.color_pair(3),
            'BLUE': curses.color_pair(4),
            'MAGENTA': curses.color_pair(5),
            'CYAN': curses.color_pair(6),
            'WHITE': curses.color_pair(7),
            'RESET': curses.A_NORMAL
        }

    def setup_curses(self):
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

    def run_command(self, cmd):
        """Execute a command and return its output"""
        try:
            result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            return result.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "N/A"

    def get_system_info(self):
        """Get system information using basic commands"""
        hostname = self.run_command("hostname")
        uptime = self.run_command("uptime -p") or self.run_command("cat /proc/uptime 2>/dev/null | awk '{printf \"%d hrs %d mins\", $1/3600, ($1%3600)/60}'")

        # Get CPU usage
        cpu_usage = self.run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        if cpu_usage == "N/A":
            cpu_usage = self.run_command("mpstat 1 1 | awk '$12 ~ /[0-9.]+/ {printf \"%.1f\", 100 - $12}'")

        # Get memory info
        mem_info = self.run_command("free -m | awk 'NR==2{printf \"%.1f/%.1fMB (%.1f%%)\", $3,$2,$3*100/$2}'")

        # Get disk usage
        disk_usage = self.run_command("df -h / | awk 'NR==2{printf \"%s/%s (%s)\", $3,$2,$5}'")

        # Get process count
        process_count = self.run_command("ps -e | wc -l")

        # Get load average
        load_avg = self.run_command("cat /proc/loadavg 2>/dev/null | awk '{print $1\", \"$2\", \"$3}'") or "N/A"
        if load_avg == "N/A":
            load_avg = self.run_command("uptime | awk -F'load average:' '{print $2}'")

        # Get battery info if available (for laptops)
        battery = self.run_command("upower -i /org/freedesktop/UPower/devices/battery_BAT0 2>/dev/null | grep percentage | awk '{print $2}'")
        if battery == "N/A":
            battery = self.run_command("cat /sys/class/power_supply/BAT0/capacity 2>/dev/null") + "%"

        # Get temperature if available
        temp = self.run_command("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{printf \"%.1f\", $1/1000}'")
        if temp != "N/A":
            temp = f"{temp}°C"

        return {
            "hostname": hostname,
            "uptime": uptime.replace("up ", "") if uptime != "N/A" else "N/A",
            "cpu_usage": cpu_usage,
            "mem_info": mem_info,
            "disk_usage": disk_usage,
            "process_count": process_count,
            "load_avg": load_avg,
            "battery": battery,
            "temperature": temp
        }

    def get_processes(self):
        """Get process information with more details"""
        processes = []
        try:
            # Get more processes (up to 30)
            if self.show_details:
                output = self.run_command("ps -eo pid,user,%cpu,%mem,vsz,rss,etime,comm --sort=-%cpu | head -n 31")
            else:
                output = self.run_command("ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -n 31")

            for line in output.split('\n')[1:]:  # Skip header
                if line.strip():
                    if self.show_details:
                        parts = line.split(maxsplit=7)
                        if len(parts) >= 8:
                            processes.append({
                                "pid": parts[0],
                                "user": parts[1],
                                "cpu": parts[2],
                                "mem": parts[3],
                                "vsz": parts[4],
                                "rss": parts[5],
                                "etime": parts[6],
                                "comm": parts[7]
                            })
                    else:
                        parts = line.split(maxsplit=4)
                        if len(parts) >= 5:
                            processes.append({
                                "pid": parts[0],
                                "user": parts[1],
                                "cpu": parts[2],
                                "mem": parts[3],
                                "comm": parts[4]
                            })
        except Exception as e:
            # Fallback to simpler command if the detailed one fails
            try:
                output = self.run_command("ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -n 31")
                for line in output.split('\n')[1:]:
                    if line.strip():
                        parts = line.split(maxsplit=4)
                        if len(parts) >= 5:
                            processes.append({
                                "pid": parts[0],
                                "user": parts[1],
                                "cpu": parts[2],
                                "mem": parts[3],
                                "comm": parts[4]
                            })
            except:
                pass

        return processes

    def format_bytes(self, kb):
        """Format kilobytes to human readable format"""
        if kb == "N/A" or not str(kb).isdigit():
            return "N/A"

        try:
            kb_val = int(kb)
            for unit in ['KB', 'MB', 'GB', 'TB']:
                if kb_val < 1024.0:
                    return f"{kb_val:.1f} {unit}"
                kb_val /= 1024.0
            return f"{kb_val:.1f} PB"
        except:
            return "N/A"

    def display_header(self, info):
        """Display system header information"""
        height, width = self.stdscr.getmaxyx()

        # Header
        self.stdscr.addstr(0, 0, "=" * (width-1), self.colors['WHITE'])
        title = "Enhanced System Monitor"
        host_info = f"Host: {info['hostname']}"
        self.stdscr.addstr(1, 0, title, self.colors['CYAN'] | curses.A_BOLD)
        self.stdscr.addstr(1, len(title) + 2, host_info, self.colors['GREEN'])
        self.stdscr.addstr(2, 0, "=" * (width-1), self.colors['WHITE'])

        # System info line 1
        uptime_info = f"Uptime: {info['uptime']}"
        load_info = f"Load: {info['load_avg']}"
        self.stdscr.addstr(3, 0, uptime_info, self.colors['YELLOW'])
        self.stdscr.addstr(3, len(uptime_info) + 2, load_info, self.colors['MAGENTA'])

        # System info line 2
        processes_info = f"Processes: {info['process_count']}"
        cpu_info = f"CPU: {info['cpu_usage']}"
        mem_info = f"Memory: {info['mem_info']}"
        self.stdscr.addstr(4, 0, processes_info, self.colors['GREEN'])
        self.stdscr.addstr(4, len(processes_info) + 2, cpu_info, self.colors['RED'])
        self.stdscr.addstr(4, len(processes_info) + len(cpu_info) + 4, mem_info, self.colors['BLUE'])

        # System info line 3
        disk_info = f"Disk: {info['disk_usage']}"
        battery_info = f"Battery: {info['battery']}" if info['battery'] != "N/A" else ""
        temp_info = f"Temp: {info['temperature']}" if info['temperature'] != "N/A" else ""

        self.stdscr.addstr(5, 0, disk_info, self.colors['CYAN'])
        pos = len(disk_info) + 2
        if battery_info:
            self.stdscr.addstr(5, pos, battery_info, self.colors['GREEN'])
            pos += len(battery_info) + 2
        if temp_info:
            self.stdscr.addstr(5, pos, temp_info, self.colors['YELLOW'])

        self.stdscr.addstr(6, 0, "=" * (width-1), self.colors['WHITE'])

    def display_processes(self, processes, start_row):
        """Display process information with more details"""
        height, width = self.stdscr.getmaxyx()

        # Process table header
        if self.show_details:
            header = f"{'PID':<6} {'USER':<10} {'CPU%':<5} {'MEM%':<5} {'VSZ':<8} {'RSS':<8} {'TIME':<10} {'COMMAND'}"
        else:
            header = f"{'PID':<6} {'USER':<10} {'CPU%':<5} {'MEM%':<5} {'COMMAND'}"

        self.stdscr.addstr(start_row, 0, header, self.colors['WHITE'] | curses.A_BOLD)
        self.stdscr.addstr(start_row + 1, 0, "=" * (width-1), self.colors['WHITE'])

        # Process rows
        max_processes = height - start_row - 4  # Leave space for footer
        for i, proc in enumerate(processes[:max_processes]):
            row = start_row + 2 + i
            if row >= height - 2:  # Leave space for footer
                break

            # Determine colors based on usage
            cpu_color = self.colors['GREEN']
            try:
                if float(proc['cpu']) > 20:
                    cpu_color = self.colors['RED']
                elif float(proc['cpu']) > 10:
                    cpu_color = self.colors['YELLOW']
            except:
                pass

            mem_color = self.colors['GREEN']
            try:
                if float(proc['mem']) > 5:
                    mem_color = self.colors['RED']
                elif float(proc['mem']) > 2:
                    mem_color = self.colors['YELLOW']
            except:
                pass

            # Format process line
            pid_str = f"{proc['pid']:<6}"
            user_str = f"{proc['user']:<10}"[:10]
            cpu_str = f"{proc['cpu']:<5}"
            mem_str = f"{proc['mem']:<5}"

            if self.show_details:
                vsz_str = f"{self.format_bytes(proc['vsz']):<8}"[:8]
                rss_str = f"{self.format_bytes(proc['rss']):<8}"[:8]
                etime_str = f"{proc['etime']:<10}"[:10]
                comm_str = proc['comm'][:width-55] if width > 55 else proc['comm'][:20]

                # Add to screen with colors
                self.stdscr.addstr(row, 0, pid_str, self.colors['WHITE'])
                self.stdscr.addstr(row, 6, user_str, self.colors['CYAN'])
                self.stdscr.addstr(row, 16, cpu_str, cpu_color)
                self.stdscr.addstr(row, 21, mem_str, mem_color)
                self.stdscr.addstr(row, 26, vsz_str, self.colors['BLUE'])
                self.stdscr.addstr(row, 34, rss_str, self.colors['MAGENTA'])
                self.stdscr.addstr(row, 42, etime_str, self.colors['YELLOW'])
                self.stdscr.addstr(row, 52, comm_str, self.colors['GREEN'])
            else:
                comm_str = proc['comm'][:width-30] if width > 30 else proc['comm'][:20]

                # Add to screen with colors
                self.stdscr.addstr(row, 0, pid_str, self.colors['WHITE'])
                self.stdscr.addstr(row, 6, user_str, self.colors['CYAN'])
                self.stdscr.addstr(row, 16, cpu_str, cpu_color)
                self.stdscr.addstr(row, 21, mem_str, mem_color)
                self.stdscr.addstr(row, 26, comm_str, self.colors['GREEN'])

        return start_row + 2 + min(len(processes), max_processes) + 1

    def display_footer(self, row):
        """Display footer information"""
        height, width = self.stdscr.getmaxyx()

        if row < height - 1:
            self.stdscr.addstr(row, 0, "=" * (width-1), self.colors['WHITE'])

            # Help text
            mode = "Detailed" if self.show_details else "Basic"
            help_text = f"Mode: {mode} | [D]etails [Q]uit"
            self.stdscr.addstr(row + 1, 0, help_text, self.colors['GREEN'])

    def run(self):
        """Main monitoring loop"""
        last_update = 0
        update_interval = 2  # seconds

        while True:
            # Check for user input
            key = self.stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('d') or key == ord('D'):
                self.show_details = not self.show_details

            current_time = time.time()
            if current_time - last_update >= update_interval:
                # Clear screen
                self.stdscr.clear()

                # Get all system information
                info = self.get_system_info()
                processes = self.get_processes()

                # Display all information
                self.display_header(info)

                # Display processes
                row = self.display_processes(processes, 7)

                # Display footer
                self.display_footer(row)

                # Refresh screen
                self.stdscr.refresh()
                last_update = current_time

            # Small delay to prevent high CPU usage
            time.sleep(0.1)

def main(stdscr):
    monitor = EnhancedSystemMonitor(stdscr)
    monitor.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExiting system monitor...")
    except Exception as e:
        print(f"Error: {e}")
        print("Falling back to text mode...")

        # Fallback to simple text mode
        while True:
            os.system('clear')
            print("Enhanced System Monitor (Text Mode)")
            print("===================================")

            # Get system info with subprocess
            try:
                hostname = subprocess.check_output("hostname", shell=True, text=True).strip()
                uptime = subprocess.check_output("uptime -p", shell=True, text=True).strip().replace("up ", "")
                cpu_usage = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", shell=True, text=True).strip()
                mem_info = subprocess.check_output("free -m | awk 'NR==2{printf \"%.1f/%.1fMB (%.1f%%)\", $3,$2,$3*100/$2}'", shell=True, text=True).strip()
                processes = subprocess.check_output("ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -n 30", shell=True, text=True).strip()

                print(f"Host: {hostname}")
                print(f"Uptime: {uptime}")
                print(f"CPU: {cpu_usage}%")
                print(f"Memory: {mem_info}")
                print("\nTop processes by CPU:")
                print(processes)
                print("\nPress Ctrl+C to exit")
            except Exception as e:
                print(f"Error getting system information: {e}")

            time.sleep(2)
