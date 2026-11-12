def generate_tiles(frame, rows=2, cols=2, overlap=0.0):
    """
    Split an image into equal-sized tiles.

    Parameters
    ----------
    frame : numpy.ndarray
        Input image.
    rows : int
        Number of tile rows.
    cols : int
        Number of tile columns.
    overlap : float
        Fraction of overlap between neighbouring tiles.
        Example: 0.10 means 10% overlap.

    Returns
    -------
    tiles : list
        List of cropped tile images.
    metadata : list
        Position information for each tile.
    """

    # Validate configuration
    if rows <= 0:
        raise ValueError("rows must be greater than 0")

    if cols <= 0:
        raise ValueError("cols must be greater than 0")

    if overlap < 0 or overlap >= 1:
        raise ValueError("overlap must be between 0 and 1")

    # Get original frame dimensions
    frame_height, frame_width = frame.shape[:2]


    # Calculate tile dimensions while accounting for overlap.
    #
    # Example:
    #
    # Frame width = 1920
    # Columns = 3
    # Overlap = 10% = 0.10
    #
    # We first calculate the tile width W.
    #
    # Because neighbouring tiles overlap by 10%,
    # each new tile starts 90% of one tile-width
    # after the previous tile.
    #
    # Therefore, for 3 columns:
    #
    # W + 0.9W + 0.9W = 1920
    #
    # 2.8W = 1920
    #
    # W = 1920 / 2.8
    # W ≈ 685.7
    #
    # Therefore tile_width ≈ 686 pixels.
    tile_width = frame_width / (
            cols - (cols - 1) * overlap
        )

    # The same calculation is performed vertically.
    #
    # Example:
    #
    # Frame height = 1080
    # Rows = 3
    # Overlap = 10% = 0.10
    #
    # H + 0.9H + 0.9H = 1080
    #
    # 2.8H = 1080
    #
    # H = 1080 / 2.8
    # H ≈ 385.7
    #
    # Therefore tile_height ≈ 386 pixels.
    tile_height = frame_height / (
            rows - (rows - 1) * overlap
        )

    # Convert the overlap percentage into pixels.
    #
    # Example:
    #
    # tile_width ≈ 686 pixels
    # overlap = 0.10 (10%)
    #
    # horizontal overlap:
    # 686 × 0.10 ≈ 69 pixels
    #
    # tile_height ≈ 386 pixels
    # overlap = 0.10 (10%)
    #
    # vertical overlap:
    # 386 × 0.10 ≈ 39 pixels
    overlap_x = tile_width * overlap
    overlap_y = tile_height * overlap

    # Calculate how far the starting position moves
    # between neighbouring tiles.
    #
    # Example:
    #
    # tile_width ≈ 686
    # overlap_x ≈ 69
    #
    # step_x = 686 - 69
    #        ≈ 617 pixels
    #
    # Therefore:
    #
    # T1 starts at x = 0
    # T2 starts at x ≈ 617
    # T3 starts at x ≈ 1234
    step_x = tile_width - overlap_x

    # Do the same calculation vertically.
    #
    # Example:
    #
    # tile_height ≈ 386
    # overlap_y ≈ 39
    #
    # step_y = 386 - 39
    #        ≈ 347 pixels
    step_y = tile_height - overlap_y


    tiles = []
    metadata = []

    tile_id = 1

    # Generate each tile
    for row in range(rows):
        for col in range(cols):

            # Calculate the starting position of each tile.
            #
            # Instead of moving by the full tile width/height,
            # we move by step_x / step_y.
            #
            # Example:
            #
            # tile_width  ≈ 685
            # overlap_x   ≈ 68
            # step_x      ≈ 617
            #
            # Therefore:
            #
            # Tile 1: x = 0 * 617 = 0
            # Tile 2: x = 1 * 617 = 617
            # Tile 3: x = 2 * 617 = 1234
            x = col * step_x

            # The same calculation is used vertically.
            #
            # Example:
            #
            # tile_height ≈ 385
            # overlap_y   ≈ 38
            # step_y      ≈ 347
            #
            # Row 1: y = 0 * 347 = 0
            # Row 2: y = 1 * 347 = 347
            # Row 3: y = 2 * 347 = 694
            y = row * step_y




            # Calculate the exact floating-point end position
            # of the tile.
            #
            # Example for T2:
            #
            # x = 617.143
            # tile_width = 685.714
            #
            # x_end = 1302.857
            x_end = x + tile_width
            y_end = y + tile_height

            # Convert only the final crop boundaries to
            # integer pixel coordinates.
            #
            # The mathematical geometry remains floating-point;
            # integer conversion is only needed because NumPy
            # requires integer indices for image slicing.
            x_start = round(x)
            x_end = round(x_end)

            y_start = round(y)
            y_end = round(y_end)

            # Crop the tile from the original frame.
            tile = frame[
                y_start:y_end,
                x_start:x_end
            ]

            
            # Store the actual tile
            tiles.append(tile)

            # Store information about where the tile
            # came from in the original frame.
            metadata.append({
                "tile_id": tile_id,
                "row": row,
                "column": col,
                "x": x_start,
                "y": y_start,
                "width": x_end - x_start,
                "height": y_end - y_start
            })

            tile_id += 1

    return tiles, metadata