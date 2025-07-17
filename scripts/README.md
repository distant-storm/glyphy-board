# Scripts Directory

This directory contains utility scripts for InkyPi that can be run independently or integrated with the main system.

## Overview

The scripts in this directory provide additional functionality and utilities for InkyPi users:

- **System utilities**: Scripts for system management and maintenance
- **Data processing**: Scripts for processing and formatting data
- **Testing utilities**: Scripts for testing various components

## Available Scripts

### System Management
- `systemd_install.sh` - System service installation script
- `example_script.py` - Example template for creating new scripts

## Usage

Most scripts can be run directly from the command line:

```bash
python3 scripts/script_name.py
```

Some scripts may require specific configuration or environment setup. Check individual script documentation for details.

## Adding New Scripts

When adding new scripts to this directory:

1. Follow Python best practices and include proper documentation
2. Add a brief description in this README
3. Include any dependencies or setup requirements
4. Test thoroughly before committing

## Dependencies

Scripts may have their own dependencies. Check individual scripts for required packages and ensure they're installed in the appropriate environment. 