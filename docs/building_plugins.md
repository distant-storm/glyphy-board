# Building InkyPi Plugins

This guide walks you through the process of creating a new plugin for InkyPi. 

### 1. Create a Directory for Your Plugin

- Navigate to the `src/plugins` directory.
- Create a new directory named after your plugin. The directory name will be the `id` of your plugin and should be all lowercase with no spaces. Example:

  ```bash
  mkdir plugins/my_plugin
  ```

### 2. Create a Python File and Class for the Plugin

- Inside your new plugin directory, create a Python file with the same name as the directory.
- Define a class in the file that inherits from `BasePlugin`.
- In your new class, implement the `generate_image` function
    - Arguments:
        - `settings`: A dictionary of plugin configuration values from the form inputs in the web UI.
        - `device_config`: An instance of the Config class, used to retrieve device configurations such as display resolution or dotenv keys for any secrets.
    - Images can be generated via the Pillow library or rendered from HTML and CSS file, see [See Generating Images by Rendering HTML and CSS](#generating-images-by-rendering-html-and-css) for details.
    - Return a single `PIL.Image` object to be displayed
    - If there are any issues (e.g., missing configuration options or API keys), raise a `RuntimeError` exception with a clear and concise message to be displayed in the web UI.
- To add the predefined style settings (see the Newspaper plugin in the Web UI) to your plugin settings page, set `style_settings` to True.

### 3. Create a Settings Template (Optional)

- If your plugin requires user input to function, create an HTML file named `settings.html` in your plugin's directory.
- The settings template is rendered inside the existing web UI layout, so you only need to define form inputs.
- Use the following form input structure (the exact name matters for settings to be saved and loaded correctly)
    - **HTML Input:**
        ```html
        <input type="text" id="textInput" name="textInput" />
        ```
    - **Access in plugin class:**
        ```python
        text_value = settings.get("textInput", "default_value")
        ```
- Use the following additional form input types:
    - **Checkbox:** Use `class="toggle-checkbox"` for styled toggle switches.
        ```html
        <input type="checkbox" id="checkboxInput" name="checkboxInput" class="toggle-checkbox" value="false" onclick="this.value = this.checked ? 'true' : 'false'">
        ```
    - **File Upload:** Use `class="file-upload-input"` for styled file inputs.
        ```html
        <input type="file" id="fileInput" name="fileInput" class="file-upload-input">
        ```
    - **Select Dropdown:** Standard `<select>` elements work well.
        ```html
        <select id="selectInput" name="selectInput">
            <option value="option1">Option 1</option>
            <option value="option2">Option 2</option>
        </select>
        ```
- Ensure the settings template visually matches the style of the existing web UI and other plugin templates for consistency.
- When a plugin is added to a playlist, editing the plugin instance should prepopulate the form with the current settings, and saving changes should update the settings accordingly. 

### 4. Add an Icon for Your Plugin

- Create an `icon.png` file in your plugin's directory. This will be the icon displayed in the web UI.
    - Ensure the icon visually matches the style of existing icons in the project.

### 5. Register Your Plugin

- Create a `plugin-info.json` in your plugin folder
- Add an object for your plugin using the following structure:
    ```json
    {
        "display_name": "My Plugin",    # The name shown in the web UI for the plugin.
        "id": "my_plugin",              # A unique identifier for the plugin (use lowercase and avoid spaces)
        "class": "MyPlugin"             # The name of your plugin's Python class.
    }
    ```
- Plugins will be loaded on startup if the folder contains a `plugin-info.json`

## Test Your Plugin

- Restart the InkyPi service by running
    ```bash
    sudo systemctl restart inkypi.service
    ```
- Test and ensure that your plugin:
    - Loads correctly on service start.
    - Appears under the "Plugins" section in the web UI with it's icon.
    - Generates images for different display sizes and orientations.
    - Settings template is rendered correctly.
    - Generates and displays images with immediate updates and in a playlist.
    - Setting template is prepopulated and saved correctly when editing an existing playlist

## Example Directory Structure

Here's how your plugin directory should look:

```
plugins/{plugin_id}/
    ├── {plugin_id}.py          # Main plugin script
    ├── icon.png                # Plugin icon
    ├── settings.html           # Optional: Plugin settings page (if applicable)
    ├── render/                 # Optional: If generating images from html and css files, store them here
    └── {other files/resources} # Any additional files or resources used by the plugin
```

## Prepopulating forms for Plugin Instances

When a plugin is added to a playlist, a "Plugin Instance" is created, and its settings are stored in the `src/config/device.json` file. These settings can be updated from the playlist page, so the form in settings.html should be prepopulated with the existing settings.

- The `loadPluginSettings` variable should be checked to ensure the settings page is in "edit" mode.
- Plugin settings are accessible via the `pluginSettings` object.
- Example:
    ```JavaScript
    document.addEventListener('DOMContentLoaded', () => {     
        if (loadPluginSettings) {
            # Text Input
            document.getElementById('{textInputElementId}').value = pluginSettings.textInpuElementName || '';

            # Radio
            document.querySelector(`input[name="radioElementName"][value="${pluginSettings.radioElementName}"]`).checked = true;

            # Color Input
            document.getElementById('{colorInputElementId}').value = pluginSettings.colorInputElementName

            ...
        }
    });
    ```

## Generating Images by Rendering HTML and CSS

For more complex plugins or dashboards that display dynamic content, you can generate images from HTML and CSS files.

### Using `render_image`
You can generate an image by calling the `BasePlugin`'s `render_image` function, which accepts the following arguments:
- `dimensions` (tuple)                  The width and height of the generated image.
- `template_name` (str)                 The name of the HTML template to render.
- `template_params` (dict)              Variables to pass to the template.
- `timeout_ms` (int, optional)          Timeout for image generation (default: 10 seconds).

### How it Works

1. The HTML template is rendered with the provided variables using Jinja2 templating.
2. It then calls the `take_screenshot_html` function in `image_utils.py`.
3. This function uses the Chromium Browser in headless mode to load the HTML file and capture a screenshot.
4. The resulting screenshot is returned as a PIL Image object.

For reference, see the Newspaper plugin.

### Example

Here's an example plugin that generates an image from HTML:

```python
from plugins.base_plugin.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def generate_image(self, settings, device_config):
        dimensions = device_config.get_resolution()
        
        template_params = {
            "title": settings.get("title", "Default Title"),
            "background_color": settings.get("background_color", "#ffffff")
        }
        
        return self.render_image(dimensions, "template.html", template_params)
```

```html
<!-- plugins/my_plugin/render/template.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: {{ background_color }};
            text-align: center;
            padding: 50px;
        }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
</body>
</html>
```
