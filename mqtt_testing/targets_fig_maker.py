import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator


class TargetFigMaker:
    __fig: plt.Figure
    __axes: list[Axes]

    def __init__(self):
        self.__fig, self.__axes = plt.subplots(1, 1, figsize=(6, 6))
        self.__axes = [self.__axes]

    def __setup_stt_subplot(self, ax: Axes, fl_mhz: int, fh_mhz: int,
                            max_bw_mhz: int):
        ax.cla()
        ax.set_xlim(fl_mhz, fh_mhz)
        ax.set_ylim(0, max_bw_mhz)
        ax.set_xlabel("f (MHz)")
        ax.set_ylabel("bw (MHz)")
        ax.set_title("STT")
        ax.set_xticks(range(fl_mhz, fh_mhz + 1, 20))  # +1 to include fh_mhz
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(True, which='major', linestyle='-', linewidth=0.8, alpha=0.8)
        ax.grid(True, which='minor', linestyle='-', linewidth=0.5, alpha=0.5)

    def __setup_ltt_subplot(self, ax: Axes, fl_mhz: int, fh_mhz: int,
                            max_bw_mhz: int):
        ax.cla()
        ax.set_xlim(fl_mhz, fh_mhz)
        ax.set_ylim(0, max_bw_mhz)
        ax.set_xlabel("f (MHz)")
        ax.set_ylabel("bw (MHz)")
        ax.set_title("LTT")
        ax.set_xticks(range(fl_mhz, fh_mhz + 1, 20))  # +1 to include fh_mhz
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(True, which='major', linestyle='-', linewidth=0.8, alpha=0.8)
        ax.grid(True, which='minor', linestyle='-', linewidth=0.5, alpha=0.5)

    def __draw_stt(self, stt_info: dict, ax: Axes):
        N = stt_info["num"]
        for i in range(N):
            w = stt_info["bw"][i]
            h = stt_info["bw"][i]  # same as w
            x = int(stt_info["fc"][i] - w / 2)
            y = 0  # start from the bottom
            rect = patches.Rectangle((x, y),
                                     w,
                                     h,
                                     facecolor='green',
                                     alpha=0.2,
                                     edgecolor='black',
                                     linewidth=1)
            ax.add_patch(rect)
            ax.text(
                x + w / 2,
                y + h,
                f"{stt_info['serial'][i]}_{stt_info['type'][i]}({stt_info['theta'][i]:.0f}, {stt_info['phi'][i]:.0f})",
                fontsize=10,
                color='black',
                ha='center',
                va='bottom')

    def __draw_ltt(self, ltt_info: dict, ax: Axes):
        N = ltt_info["num"]
        for i in range(N):
            w = ltt_info["bw"][i]
            h = ltt_info["bw"][i]  # same as w
            x = int(ltt_info["fc"][i] - w / 2)
            y = 0  # start from the bottom
            rect = patches.Rectangle((x, y),
                                     w,
                                     h,
                                     facecolor='red',
                                     alpha=0.2,
                                     edgecolor='black',
                                     linewidth=1)
            ax.add_patch(rect)
            ax.text(
                x + w / 2,
                y + h,
                f"{ltt_info['serial'][i]}_{ltt_info['type'][i]}({ltt_info['theta'][i]:.0f}, {ltt_info['phi'][i]:.0f})",
                fontsize=10,
                color='black',
                ha='center',
                va='bottom')

    def make(self, stt_info: dict, ltt_info: dict, dest, fl_mhz: int,
             fh_mhz: int, bw_mhz: int):
        self.__setup_stt_subplot(self.__axes[0], fl_mhz, fh_mhz, bw_mhz)
        # self.__setup_ltt_subplot(self.__axes[1], fl_mhz, fh_mhz, bw_mhz)
        self.__draw_stt(stt_info, self.__axes[0])
        self.__draw_ltt(ltt_info, self.__axes[0])
        # self.__draw_ltt(ltt_info, self.__axes[1])
        self.__fig.tight_layout()
        if isinstance(dest, str):
            self.__fig.savefig(dest)
        else:
            self.__fig.savefig(dest, format='png')


if __name__ == "__main__":
    maker = TargetFigMaker()
    stt_info = {
        "num": 3,
        "serial": [1, 2, 3],
        "fc": [5730, 5740, 5800],
        "bw": [40, 10, 20],
        "theta": [90, 0, 45.5],
        "phi": [360, 350, 340.8],
        "type": ["Parrot", "wifi", "skydio"]
    }
    maker.make(stt_info, stt_info, "test.png", 5710, 5870, 40)
    stt_info = {
        "num": 3,
        "serial": [1, 2, 3],
        "fc": [5730, 5740, 5800],
        "bw": [10, 10, 20],
        "theta": [90, 0, 45.5],
        "phi": [360, 350, 340.8],
        "type": ["Parrot", "wifi", "skydio"]
    }
    maker.make(stt_info, stt_info, "test_1.png", 5710, 5870, 40)
