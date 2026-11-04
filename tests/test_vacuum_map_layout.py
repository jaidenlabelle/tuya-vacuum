"""Test the vacuum_map module."""

from tuya_vacuum.map.layout import Layout


def test_vacuum_map_header():
    """Test how the vacuum map header is parsed."""

    with open("./tests/layout.bin", "rb") as file:
        # Read the file as a hex string
        data = file.read()

        # Parse the map data
        vacuum_map = Layout(data)

        # Assert that the header values are correct
        assert vacuum_map.version == 1
        assert vacuum_map.id == 0
        assert vacuum_map.type == 0
        assert vacuum_map.total_count == 361391
        assert vacuum_map.width == 601
        assert vacuum_map.height == 601
        assert vacuum_map.origin_x == 300.0
        assert vacuum_map.origin_y == 300.0
        assert vacuum_map.map_resolution == 0
        assert vacuum_map.pile_x == 302.0
        assert vacuum_map.pile_y == 300.0
        assert vacuum_map.length_after_compression == 27666
        assert not vacuum_map.room_editable


def test_vacuum_map_room():
    """Test how a vacuum map room is parsed."""

    with open("./tests/layout.bin", "rb") as file:
        # Read the file as a hex string
        data = file.read()

        # Parse the map data
        vacuum_map = Layout(data)

        # Assert that the room values are correct
        assert vacuum_map.rooms[0].id == 5
        assert vacuum_map.rooms[0].order == 65535
        assert vacuum_map.rooms[0].sweep_count == 1
        assert vacuum_map.rooms[0].mop_count == 2
        assert vacuum_map.rooms[0].color_order == 0
        assert vacuum_map.rooms[0].sweep_forbidden == 0
        assert vacuum_map.rooms[0].mop_forbidden == 0
        assert vacuum_map.rooms[0].fan == 2
        assert vacuum_map.rooms[0].water_level == 3
        assert vacuum_map.rooms[0].y_mode == 1
        assert vacuum_map.rooms[0].name_length == 0
        assert vacuum_map.rooms[0].name == ""
        assert vacuum_map.rooms[0].vertex_num == 0
        assert vacuum_map.rooms[0].vertex_str == ""


def test_vacuum_map_header_v152():
    """Test how a version 152 vacuum map header is parsed.

    Captured from a Kabum "Robô Aspirador de Pó 700", a rebranded Tuya
    vacuum whose layout header has no total_count/length_after_compression
    trailer.
    """

    with open("./tests/layout_152.bin", "rb") as file:
        data = file.read()

        vacuum_map = Layout(data)

        assert vacuum_map.version == 152
        assert vacuum_map.width == 459
        assert vacuum_map.height == 240
        assert vacuum_map.origin_x == 104.0
        assert vacuum_map.origin_y == 65.0
        assert vacuum_map.pile_x == 40.5


def test_vacuum_map_body_v152():
    """Test how a version 152 vacuum map body is parsed."""

    with open("./tests/layout_152.bin", "rb") as file:
        data = file.read()

        vacuum_map = Layout(data)

        # There's no room data for this version, unlike version 1.
        assert vacuum_map.rooms == []

        # The decompressed bitmap should have exactly one byte per pixel.
        assert len(vacuum_map._map_data_array) == vacuum_map.width * vacuum_map.height

        # Should not raise despite there being no room data.
        vacuum_map.to_image()


def test_vacuum_map_rooms_with_vertex_data():
    """Test parsing a version 1 map whose rooms carry real vertex/polygon data.

    Captured from a Liectroux XR500 (sold in Brazil as the Kabum! Smart
    700), a rebranded Tuya vacuum. Each room here has vertex_num == 32,
    unlike every other test fixture where it's 0. Room.parse_rooms used to
    advance byte_pos by a fixed per-room stride that ignored the trailing
    vertex data, so every room after the first was read from the wrong
    offset and its name failed to decode as UTF-8.
    """

    with open("./tests/layout_liectroux_xr500.bin", "rb") as file:
        data = file.read()

        vacuum_map = Layout(data)

        assert vacuum_map.version == 1
        assert len(vacuum_map.rooms) == 11

        names = [room.name for room in vacuum_map.rooms]
        assert names == [
            "Suíte Master",
            "Suíte",
            "Sacada",
            "Corredor Quarto",
            "Lavanderia",
            "Sala de Jantar",
            "Quarto",
            "Cozinha",
            "Quarto Sacada",
            "Quarto Fundo",
            "Sala de estar",
        ]
        assert all(room.vertex_num == 32 for room in vacuum_map.rooms)

        # Should not raise.
        vacuum_map.to_image()
