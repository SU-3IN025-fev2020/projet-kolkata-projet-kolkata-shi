# -*- coding: utf-8 -*-


import heapq


__author__ = "Shi YU, 28507587"
__email__ = "shi4yu2@gmail.com"


def manhattan(p1, p2):
    """
    Calculate manhattan distance between two cells

    Parameters
    ----------
    p1 : tuple
        coordinate (x, y) of first cell
    p2 : tuple
        coordinate (x, y) of second cell

    Returns
    -------
    int
        the manhattan distance between two cells
    """
    return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])


def available_neighbours(current_x, current_y, mapGame):
    """
    find available neighbour cells

    Parameters
    ----------
    current_x : int
        coordinate x of current state
    current_y : int
        coordinate y of current state
    allowedStates : list
        allowed states

    Returns
    -------
    list
        list of available neighbours
    """
    neighbours = [-1, 0, 1]
    neighbours_list = [(current_x + x, current_y + y) for x in neighbours for y in neighbours \
                       if (abs(x + y) < 2) and (x + y != 0) \
                       and ((current_x + x, current_y + y) in mapGame)]
    # print("neighbours: {}".format(neighbours_list))
    return neighbours_list


def astar_search(start, end, mapGame):
    """
    A* Path finding algorithm

    Parameters
    ----------
    start : tuple
        coordinate (x, y) of the start cell
    end : tuple
        coordinate (x, y) of the goal cell
    mapGame : list
        available cells to move to

    Returns
    -------
    list
        the path from the start cell to the end cell
    """
    close_set = set()
    parent = {}
    open_list = []
    # initialise start point
    g = {start: 0}  # g: cost from start to current Node
    h = {start: manhattan(start, end)}  # f: total cost of the present node, f = g + h

    heapq.heappush(open_list, (h[start], start))

    # loop until the end is found
    while open_list:
        current = heapq.heappop(open_list)[1]
        # find all available neighbour cells
        neighbours = available_neighbours(current[0], current[1], mapGame)
        # if the end is found, return the path from the start to the end
        if current == end:
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            return path[::-1]

        # add current state to visited cells
        close_set.add(current)

        for position in neighbours:
            neighbour = (position[0], position[1])
            attempt_g_score = g[current] + manhattan(current, neighbour)

            if neighbour in close_set and attempt_g_score >= g.get(neighbour, 0):
                continue

            if attempt_g_score < g.get(neighbour, 0) or neighbour not in [i[1] for i in open_list]:
                parent[neighbour] = current
                g[neighbour] = attempt_g_score
                h[neighbour] = attempt_g_score + manhattan(neighbour, end)
                heapq.heappush(open_list, (h[neighbour], neighbour))

    # if no path is found
    return False
