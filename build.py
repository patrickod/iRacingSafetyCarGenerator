#!/usr/bin/env python3
"""
Build script for iRacingSafetyCarGenerator.
Creates a self-contained Windows executable for distribution.
"""

import argparse
import glob
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class Builder:
    def __init__(self, args):
        self.args = args
        
        # Get the project root directory (parent of the directory containing this script)
        self.script_dir = Path(__file__).resolve().parent
        self.src_dir = self.script_dir / "src"
        self.dist_dir = self.script_dir / "dist"
        self.build_dir = self.script_dir / "build"
        
        # Define version numbering
        self.version = args.version or self.get_version()
        
        # Define app name
        self.app_name = "iRSCG"
        self.app_full_name = "iRacingSafetyCarGenerator"
        
        # Define output filenames
        self.exe_name = f"{self.app_name}"
        if args.version:
            self.exe_name = f"{self.app_name}-{self.version}"
            
        # Define paths to copy
        self.assets_to_copy = [
            {"src": "src/assets", "dest": "assets"},
            {"src": "src/settings.ini", "dest": "settings.ini"},
            {"src": "src/logging.json", "dest": "logging.json"},
            {"src": "src/tooltips_text.json", "dest": "tooltips_text.json"},
            {"src": "README.md", "dest": "README.md"},
            {"src": "LICENSE", "dest": "LICENSE"},
        ]
    
    def get_version(self):
        """Generate a version string based on date if not provided."""
        return datetime.now().strftime("%Y.%m.%d")
    
    def check_environment(self):
        """Check if the build environment is suitable."""
        print("Checking build environment...")
        
        # Check if we're on Windows
        if platform.system() != "Windows" and not self.args.force:
            print("Warning: Not running on Windows. The app is designed for Windows.")
            print("Use --force to build anyway.")
            return False
        
        # Check if PyInstaller is installed
        try:
            subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print("PyInstaller not found. Installing...")
            self.install_dependencies()
            
        return True
    
    def install_dependencies(self):
        """Install required dependencies for building."""
        print("Installing dependencies...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(self.script_dir / "requirements.txt")],
                check=True
            )
            # Make sure PyInstaller is installed
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            sys.exit(1)
    
    def clean_build_directories(self):
        """Remove previous build and dist directories."""
        print("Cleaning build directories...")
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
    
    def create_executable(self):
        """Create executable using PyInstaller."""
        print(f"Building executable {self.exe_name}...")
        
        # Create PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--log-level=WARN",
            "--noconsole",
            "--onefile",
            "--hidden-import=comtypes.gen.UIAutomationClient",
            "--hidden-import=pywinauto.application",
            f"--name={self.exe_name}",
            str(self.src_dir / "main.py")
        ]
        
        # Add icon if exists
        icon_path = self.src_dir / "assets" / "icon.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
        
        # Execute PyInstaller
        try:
            os.chdir(self.src_dir)  # Change to source directory
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to create executable: {e}")
            sys.exit(1)
        finally:
            os.chdir(self.script_dir)  # Change back to script directory
    
    def copy_assets(self):
        """Copy necessary files to the distribution directory."""
        print("Copying assets to distribution directory...")
        
        for item in self.assets_to_copy:
            src_path = self.script_dir / item["src"]
            dest_path = self.dist_dir / item["dest"]
            
            if not src_path.exists():
                print(f"Warning: {src_path} does not exist, skipping...")
                continue
            
            try:
                if src_path.is_dir():
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path, dest_path)
                else:
                    # Create destination directory if it doesn't exist
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"Error copying {src_path} to {dest_path}: {e}")
    
    def create_zip_archive(self):
        """Create a ZIP archive of the distribution directory."""
        if not self.args.zip:
            return
            
        print("Creating ZIP archive...")
        archive_name = f"{self.app_full_name}-{self.version}"
        
        # Use shutil.make_archive to create the zip file
        try:
            shutil.make_archive(
                base_name=str(self.script_dir / archive_name),
                format="zip",
                root_dir=self.dist_dir,
            )
            print(f"ZIP archive created: {archive_name}.zip")
        except Exception as e:
            print(f"Failed to create ZIP archive: {e}")
    
    def run(self):
        """Execute the build process."""
        if not self.check_environment():
            return
        
        # Execute build steps
        self.clean_build_directories()
        self.install_dependencies()
        self.create_executable()
        self.copy_assets()
        self.create_zip_archive()
        
        print(f"\nBuild completed successfully!")
        print(f"Executable is available at: {self.dist_dir / self.exe_name}.exe")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build script for iRacingSafetyCarGenerator."
    )
    parser.add_argument(
        "--version", "-v",
        help="Version number for the build (default: YYYY.MM.DD)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force build even if not on Windows"
    )
    parser.add_argument(
        "--zip", "-z",
        action="store_true",
        help="Create a ZIP archive of the distribution"
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Only clean build directories without building"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    builder = Builder(args)
    
    if args.clean_only:
        builder.clean_build_directories()
        print("Build directories cleaned.")
    else:
        builder.run()