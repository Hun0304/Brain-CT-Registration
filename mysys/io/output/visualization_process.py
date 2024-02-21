"""
output to visualization graph
"""

import os
import json
import matplotlib.pyplot as plt

from tqdm.rich import tqdm


class DataOutputToVisualizationGraphProcessorBase:
    """
    output visualization graph process.
    """
    def __init__(self, data_file: str):
        """
        The constructor of the class.
        :param data_file: the data file.
        """
        self.data_file = data_file

    def draw_hist_graph(self) -> None:
        """
        Output visualize the histogram graph.
        :return: None
        """
        json_file = self.data_file
        values = []
        with open(json_file, "r+") as f:
            file = json.load(f)
            with tqdm(total=len(file.values())) as pbar:
                for value in file.values():
                    pbar.set_description(f"{value} is processing...")
                    values.append(abs(value))
                    pbar.update()
                pbar.set_description(f"draw histogram graph...")
                plt.hist(values, bins=20, color="steelblue", edgecolor="k", alpha=0.65, rwidth=0.8)
                plt.xlabel("Registration metric value")
                plt.ylabel("Frequency")
                plt.title(f"Registration metric value histogram, total={len(values)}")
                plt.savefig(os.path.abspath(os.path.join(json_file,
                                                         "..",
                                                         f"{json_file.split(os.sep)[-1].split('metric_value')[0]}histogram.png")))
                pbar.set_description(f"Draw finish !")

        return None
