# tuya-vacuum
tuya-vacuum is a python library to view maps from Tuya robot vacuums.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install tuya-vacuum.

```bash
pip install tuya-vacuum
```

## Usage
```python
from tuya_vacuum import Vacuum

# Create a new Vacuum instance
vacuum = Vacuum(
    origin="https://openapi.tuyaus.com",
    client_id="<Client ID>",
    client_secret="<Client Secret>",
    device_id="<Device ID>"
)

# Parse the map data
vacuum_map = vacuum.fetch_map()

# Save the map as an image
image = vacuum_map.to_image()
image.save("output.png")
```

## Compatability List

This is a list of all currently tested devices. Create a new [issue](https://github.com/jaidenlab/tuya-vacuum/issues) to add your device.

| Device                                                | Support                           |
| ----------------------------------------------------- | --------------------------------- |
| [Lefant M1](https://www.lefant.com/en-ca/products/m1) | <text style="color:lightgreen">Supported</text> |
| Kabum Robô Aspirador de Pó 700 (map layout version 152) | <text style="color:lightgreen">Supported</text> |
| KaBuM! Smart 700 / Liectroux XR500 (map layout version 1) | <text style="color:lightgreen">Supported</text> |

## Special Thanks
- [Tuya Cloud Vacuum Map Extractor](https://github.com/oven-lab/tuya_cloud_map_extractor) by [@oven-lab](https://github.com/oven-lab)
