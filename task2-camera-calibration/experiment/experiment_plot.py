import matplotlib.pyplot as plt
from matplotlib.collections import *
import numpy as np

# corner size, resolution, time, found images, sfps

file_name = "experiment.txt"

love = []
with open(file_name, "r") as f:
    for line in f:
        try:
            corner, res, time, found, sfps = line.rstrip().split(",")
            love.append([corner, int(res), float(time), int(found), float(sfps)])
        except Exception:
            pass

corner_siz = {
    "7x7": "s",  # square
    "6x7": "^",  # triangle_up
    "7x6": "o",  # circle
    "6x6": "D"  # diamond
}

res = {
    120: "blue",
    240: "red",
    360: "green",
    480: "lime",
    720: "grey",
    1080: "orange"
}

# Fixing random state for reproducibility
np.random.seed(19680801)

for corner_size, resolution, time, found, sfps in love:
    plt.scatter(time, found, marker=corner_siz.get(corner_size), c=res.get(resolution),
                edgecolor='black', linewidth=1)

plt.xlabel("Elapsed time in sec")
plt.ylabel("Total amount of found checkerboards")
plt.tight_layout(rect=[0, 0, 0.85, 1])

res = {
    144: "blue",
    240: "red",
    360: "green",
    480: "lime",
    720: "grey",
    1080: "orange"
}

for key, value in corner_siz.items():
    plt.scatter([], [], marker=value, label=key, c="k")

h = [plt.scatter([], [], marker=value, label=key, c="k") for key, value in corner_siz.items()]
leg1 = plt.legend(handles=h, loc="upper right", title="Corner \nsizes", bbox_to_anchor=(1.22, 1))
plt.setp(leg1.get_title(), multialignment='center')
plt.gca().add_artist(leg1)

# Legends
h = [plt.scatter([], [], c=value, label=key, marker="p") for key, value in res.items()]
leg2 = plt.legend(handles=h, loc=(1.03, 0.02), title="Image \nResolution")
plt.setp(leg2.get_title(), multialignment='center')
plt.gca().add_artist(leg2)

# for key, value in res.items():
#     plt.scatter([], [], c=value, label=key, marker="p")  # pentagon

# legend1 = plt.legend([x for x in corner_siz.keys()],
#                      loc="upper right", title="Ranking", bbox_to_anchor=(1.22, 1))
# plt.gca().add_artist(legend1)

# legend2 = plt.legend([x for x in res.keys()], loc="lower right", title="Image \nResolution")
# plt.setp(legend2.get_title(), multialignment='center')
# plt.gca().add_artist(legend2)

# plt.show()
plt.savefig('experiment.png')
