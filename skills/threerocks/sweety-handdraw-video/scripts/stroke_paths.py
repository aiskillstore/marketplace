"""Extract and measure raster stroke paths without depending on a project checkout."""
import numpy as np


def thin_ink(binary_ink):
    skeleton = np.pad(binary_ink.astype(np.uint8), 1)
    while True:
        deleted_count = 0
        for subiteration in range(2):
            center = skeleton[1:-1, 1:-1]
            neighbors = [skeleton[:-2, 1:-1], skeleton[:-2, 2:], skeleton[1:-1, 2:],
                         skeleton[2:, 2:], skeleton[2:, 1:-1], skeleton[2:, :-2],
                         skeleton[1:-1, :-2], skeleton[:-2, :-2]]
            neighbor_count = sum(neighbors)
            transition_count = sum((neighbors[index] == 0) & (neighbors[(index + 1) % 8] == 1)
                                   for index in range(8))
            removable = (center == 1) & (neighbor_count >= 2) & (neighbor_count <= 6) & (transition_count == 1)
            if subiteration == 0:
                removable &= (neighbors[0] * neighbors[2] * neighbors[4] == 0)
                removable &= (neighbors[2] * neighbors[4] * neighbors[6] == 0)
            else:
                removable &= (neighbors[0] * neighbors[2] * neighbors[6] == 0)
                removable &= (neighbors[0] * neighbors[4] * neighbors[6] == 0)
            deleted_count += int(removable.sum())
            center[removable] = 0
        if deleted_count == 0:
            return skeleton[1:-1, 1:-1].astype(bool)


def trace_strokes(skeleton):
    pixel_set = set(zip(*np.where(skeleton)))
    adjacency = {}
    for y, x in pixel_set:
        adjacent = []
        for delta_y, delta_x in [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, 1), (1, -1)]:
            neighbor = (y + delta_y, x + delta_x)
            if neighbor not in pixel_set:
                continue
            if delta_x and delta_y and ((y, x + delta_x) in pixel_set or (y + delta_y, x) in pixel_set):
                continue
            adjacent.append(neighbor)
        adjacency[(y, x)] = adjacent
    visited_edges = set()
    strokes = []

    def follow_chain(start, neighbor):
        chain = [start]
        previous, current = start, neighbor
        visited_edges.add(tuple(sorted((previous, current))))
        while True:
            chain.append(current)
            candidates = [point for point in adjacency[current]
                          if tuple(sorted((point, current))) not in visited_edges]
            if len(adjacency[current]) != 2 or not candidates:
                break
            previous, current = current, candidates[0]
            visited_edges.add(tuple(sorted((previous, current))))
        return [[float(x), float(y)] for y, x in chain]

    for start in sorted(pixel_set):
        if len(adjacency[start]) == 2:
            continue
        for neighbor in adjacency[start]:
            if tuple(sorted((start, neighbor))) not in visited_edges:
                strokes.append(follow_chain(start, neighbor))
    for start in sorted(pixel_set):
        for neighbor in adjacency[start]:
            if tuple(sorted((start, neighbor))) not in visited_edges:
                strokes.append(follow_chain(start, neighbor))
    return [stroke for stroke in strokes if len(stroke) > 4]


def calculate_lengths(points):
    coordinates = np.array(points, dtype=float)
    distances = np.linalg.norm(np.diff(coordinates, axis=0), axis=1)
    return np.concatenate(([0.0], np.cumsum(distances)))
