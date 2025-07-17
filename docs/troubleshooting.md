# Troubleshooting

This document contains solutions to common issues you might encounter while using InkyPi.

## Display Issues

### Display Not Updating

**Symptoms**: The e-ink display shows the same image and doesn't update when you trigger a refresh.

**Possible Causes & Solutions**:

1. **Service not running**:
   ```bash
   sudo systemctl status inkypi.service
   ```
   If inactive, start it:
   ```bash
   sudo systemctl start inkypi.service
   ```

2. **Permission issues with display hardware**:
   ```bash
   sudo usermod -a -G spi,gpio,i2c pi
   ```
   Then restart the service.

3. **Check logs for errors**:
   ```bash
   sudo journalctl -u inkypi.service -f
   ```

### Display Shows Corrupted Image

**Symptoms**: The display shows garbled or partially corrupted content.

**Solutions**:
- Restart the service:
  ```bash
  sudo systemctl restart inkypi.service
  ```
- Check if the display is properly connected
- Verify the correct display type is configured in settings

## Network Issues

### Cannot Access Web Interface

**Symptoms**: Unable to reach the web interface from your browser.

**Solutions**:

1. **Find the Pi's IP address**:
   ```bash
   hostname -I
   ```

2. **Check if the service is running**:
   ```bash
   sudo systemctl status inkypi.service
   ```

3. **Check firewall settings** (if applicable):
   ```bash
   sudo ufw status
   ```

## Plugin Issues

### Plugin Not Appearing

**Symptoms**: A plugin doesn't show up in the web interface.

**Solutions**:
- Verify the plugin directory contains a `plugin-info.json` file
- Check the plugin configuration is valid
- Restart the service:
  ```bash
  sudo systemctl restart inkypi.service
  ```

### Plugin Errors

**Symptoms**: Plugin shows error messages when trying to update.

**Solutions**:
- Check the plugin's settings and required API keys
- Verify internet connectivity for plugins that fetch external data
- Check logs for detailed error messages:
  ```bash
  sudo journalctl -u inkypi.service -f
  ```

## General Issues

### High CPU Usage

**Symptoms**: The Raspberry Pi becomes slow or unresponsive.

**Solutions**:
- Monitor system resources:
  ```bash
  top
  ```
- Increase the refresh interval in plugin settings
- Consider reducing image resolution if performance is poor

### SD Card Issues

**Symptoms**: Frequent crashes, corruption, or "read-only" filesystem errors.

**Solutions**:
- Use a high-quality SD card (Class 10 or better)
- Check filesystem:
  ```bash
  sudo fsck /dev/mmcblk0p2
  ```
- Consider backing up and reflashing if corruption persists

## Getting Help

If you continue to experience issues:

1. Check the [GitHub Issues](https://github.com/mattdrummond/InkyPi/issues) page
2. Create a new issue with:
   - Your hardware setup
   - Steps to reproduce the problem
   - Relevant log output
   - Screenshots if applicable
