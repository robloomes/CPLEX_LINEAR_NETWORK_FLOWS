"""
    COSC364-18S1 Internet Technologies and Engineering
    Assignment #2: Flow
    File: flow.py
    Generates an LP file for printing CPLEX linear optimized XYZ network flow
    Authors: Loomes, Robert; Ross, Adam
    Due: 03 June 2018
"""

from sys import argv, exit
from os import system as optimize

PATHS = 3  # The number of paths the demand volume is split over


def subjects(src, trns, dst):
    """
    Lists source, transit, demand, binary, load and r constraint LP equations
    :param src: The start/source network transmitting data, src-i
    :param trns: The transit network between source and destination, trns-k
    :param dst: The destination network receiving transmissions, dst-j
    :return: List of string formatted (sf) src/trns/demand/binary capacities
    """
    dmnd = [sf for sf in [([('I' + str(i)) + ('K' + str(k)) + ('J' + str(j))
            for k in trns], i + j) for i in src for j in dst]]  # demand volume
    return ['  x' + ' + x'.join(eqn[0]) + ' = {}'.format(eqn[1]) for eqn in
            dmnd] + ['  x' + ' + x'.join(eqn[0]) + ' - c{} = 0'.format(eqn[1])
            for eqn in [sf for sf in [([('I' + str(i)) + ('K' + str(k)) + ('J'
            + str(j)) for j in dst], ('I' + str(i)) + ('K' + str(k))) for i in
            src for k in trns]]] + ['  x' + ' + x'.join(eqn[0]) + ' - d{} = 0'.
            format(eqn[1]) for eqn in [sf for sf in [([('I' + str(i)) + ('K' +
            str(k)) + ('J' + str(j)) for i in src], ('K' + str(k)) + ('J' +
            str(j))) for k in trns for j in dst]]] + ['  u' + ' + u'.join(eqn)
            + ' = ' + str(PATHS) for eqn in [sf for sf in [[('I' + str(i)) + (
            'K' + str(k)) + ('J' + str(j)) for k in trns] for i in src for j in
            dst]]] + ['  x' + ' + x'.join(eqn[0]) + ' - l{} = 0'.format(eqn[1])
            for eqn in [sf for sf in [([('I' + str(i)) + ('K' + str(k)) + ('J'
            + str(j)) for i in src for j in dst], ('K' + str(k))) for k in trns
            ]]] + ['  ' + '{0} x{1} -{2} u{1} = 0'.format(PATHS, pth.strip(),
            rt[-1]) for rt in [rt.split(",") for rt in ['' + ', '.join(eqn[0])
            + ', {}'.format(eqn[1]) for eqn in dmnd]] for pth in rt[:-1]] + \
            ['  c' + ' + c'.join(eqn) + ' - r <= 0' for eqn in
            [[('I' + str(i)) + ('K' + str(k)) for i in src] for k in trns]]


def bounds(src, trns, dst):
    """
    Lists source, transit, demand and r LP 'Bounds' equation strings
    :param src: The start/source network transmitting data, src-i
    :param trns: The transit network between source and destination, trns-k
    :param dst: The destination network receiving transmissions, dst-j
    :return: List of string formatted (sf) source/transit/demand bound equation
    """
    return ['  0 <= {}'.format(sf) for sf in ['x{}'.format(('I' + str(i)) + ('K'
            + str(k)) + ('J' + str(j))) for i in src for k in trns for j in
            dst]] + ['  0 <= r']


def binaries(src, trns, dst):
    """
    Defines the binary variables for use within the LP file
    :param src: The start/source network transmitting data, src-i
    :param trns: The transit network between source and destination, trns-k
    :param dst: The destination network receiving transmissions, dst-j
    :return: List of string formatted (sf) src->trns->dst binary equations
    """
    return ['  u' + ('I' + str(i)) + ('K' + str(k)) + ('J' + str(j)) for i in
            src for j in dst for k in trns]


def file(xyz):
    """
    Generates an LP file for CPLEX to formulate an optimal network flow for XYZ
    :param xyz: List of lists of router counts for each of X -> Y -> Z networks
    :return: An LP file with formatted equations for CPLEX optimization of XYZ
    """
    src, trns, dst = xyz[0], xyz[1], xyz[2]  # Range of nodes for each network
    lp = open('Y=' + str(len(xyz[1])) + '.lp', 'w')
    lp.write('MIN\n  r\nST\n{}\nBOUND\n{}\nBIN\n{}\nEND'.format('\n'.join(
        subjects(src, trns, dst)), '\n'.join(bounds(src, trns, dst)),
        '\n'.join(binaries(src, trns, dst))))
    return str(lp.name)


if __name__ == '__main__':
    try:
        optimize("(time -p cplex -c 'read " + file([range(1, int(j) + 1) for i,
               j in enumerate(argv[1:4]) if int(j) > i % 2 * 2])+"' 'optimize' "
               "'display solution variables -') > Y=" + argv[2] + ".log 2>&1")
    except ValueError:
        print("Command error! Re-enter: 'flow.py [X > 0] [Y > 2] [Z > 0]'")
    exit()  # Safely terminates the program
