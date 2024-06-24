import numpy as np
import pandas as pd

from skeleton.settings import FILES_STORAGE


def get_capacitance_data_list(file_name: str, cycle_type: str, current_threshold: float):
    """
    Forms a table in the form of 2d array with rows [file_name, capacitance, current].

    :param file_name:
    :param cycle_type:
    :param current_threshold:
    :return:
    """
    data = pd.read_csv(FILES_STORAGE + file_name)
    current_threshold = float(current_threshold)

    # Ensure the data columns are properly named and converted to numpy arrays
    time_s = data['time_s'].values
    current_a = data['current_a'].values
    voltage_v = data['voltage_v'].values

    cycles = __find_cycles(current_a, cycle_type=cycle_type, current_threshold=current_threshold)

    return __calculate_capacitances(
        current_a,
        voltage_v,
        time_s,
        cycles,
        file_name
    )


def __find_cycles(current_values, current_threshold=0.05, cycle_type='charge'):
    """
    Finds charge or discharge cycle's indecision in a list of current values.

    :param current_values: list of logged current values.
    :param cycle_type: type of cycle. Can be either 'charge' or 'discharge'.
    :param current_threshold:
    """

    if current_threshold == 0.0:
        current_threshold = 0.0000000001

    if cycle_type == 'charge':
        cycle_type = 1
    elif cycle_type == 'discharge':
        cycle_type = -1
    else:
        raise ValueError('cycle_type must be either charge or discharge')

    cycles = []
    current_cycle = []
    in_cycle = False

    for i, current in enumerate(current_values):
        if abs(current) >= current_threshold:
            if not in_cycle:
                in_cycle = True
                current_cycle = [i]
            else:
                current_cycle.append(i)
        else:
            if in_cycle:
                in_cycle = False
                if np.sign(current_values[current_cycle[0]]) == cycle_type:
                    cycles.append(current_cycle)
                current_cycle = []

    # Handle the last cycle if it was active at the end
    if in_cycle:
        if np.sign(current_values[current_cycle[0]]) == cycle_type:
            cycles.append(current_cycle)

    return cycles


def __calculate_capacitances(
        current_lst,
        voltage_lst,
        raw_df,
        cycle_indxs,
        file_name
):
    """
    Calculates the capacitance of the cell for each cycle.

    :param current_lst: list of logged current values.
    :param voltage_lst:  list of logged voltage values.
    :param raw_df: data frame.
    :param cycle_indxs: List of indexes of cycles.
    :return: list of rows of form [file_name, capacitance, current].
    """
    capacitance_lst = []

    for cycle in cycle_indxs:
        capacitance = __calculate_capacitance_of_a_cycle(
            current_lst,
            voltage_lst,
            raw_df,
            cycle,
            file_name
        )
        capacitance_lst.append(capacitance)

    return capacitance_lst


def __calculate_capacitance_of_a_cycle(
        current_lst,
        voltage_lst,
        raw_df,
        cycle_indxs,
        file_name
):
    """
    Calculates capacitance of the cycle.

    :param current_lst: list of logged current values.
    :param voltage_lst:  list of logged voltage values.
    :param raw_df: data frame.
    :param cycle_indxs: indexes of the given cycle.
    :param file_name name of the file.
    :return: row of the Excel file in the form of the list [file_name, capacitance, current].
    """

    cycle_start = cycle_indxs[0]
    cycle_finish = cycle_indxs[-1]

    cycle_start_time = raw_df[cycle_start]
    cycle_finish_time = raw_df[cycle_finish]

    cycle = current_lst[cycle_start:cycle_finish]

    cycle_start_voltage = voltage_lst[cycle_start]
    cycle_finish_voltage = voltage_lst[cycle_finish]

    current = sum(cycle) / len(cycle)

    capacitance = (current * (cycle_finish_time - cycle_start_time)) / (cycle_finish_voltage - cycle_start_voltage)

    return [file_name, float(capacitance), float(current)]
