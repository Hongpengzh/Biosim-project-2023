"""
The Graphic module for simulation, will plot a figure in the process of simulation like e.g.,

    .. image:: ./sample_00399.png
      :width: 400
      :alt: Simulation sample
"""

__author__ = 'Hongpeng Zhang and Sujan Devkota'
__email__ = 'hongpeng.zhang@nmbu.no and sujan.devkota@nmbu.no'

import matplotlib.pyplot as plt
import numpy as np
import textwrap
import subprocess
import os
from pathlib import Path

# Update these variables to point to your ffmpeg and convert binaries
# If you installed ffmpeg using conda or installed both softwares in
# standard ways on your computer, no changes should be required.
_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'simulation_data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'  # alternatives: mp4, gif


class Graphics:
    """Provides graphics support for BioSim."""
    rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                 'L': (0.0, 0.6, 0.0),  # dark green
                 'H': (0.5, 1.0, 0.5),  # light green
                 'D': (1.0, 1.0, 0.5)}  # light yellow

    def __init__(self, island_map, img_dir=None, img_base=None,
                 img_fmt=None, hist_specs=None, ymax_animals=None):
        """

        Parameters
        ----------
        island_map: str
            Multi-line string specifying island geography
        img_dir: str
            The directory where the figures to be saved.
        img_base: str
            The base name of figures to be saved.
        img_fmt: str
            The format of figures to be saved.
        hist_specs: dictionary
            The maximum of x-axis and the bin width for the histogram.
        ymax_animals: int or float
            The maximum of y-axis of the amount of fauna axes
        """

        if img_base is None:
            img_base = _DEFAULT_GRAPHICS_NAME

        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_base)
        else:
            self._img_base = None

        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT

        self.bin_max = {'fitness': 1, 'age': 60, 'weight': 60}
        self.bin_width = {'fitness': 0.5, 'age': 2, 'weight': 2}
        if hist_specs is not None:
            for key in hist_specs.keys():
                self.bin_max[key] = hist_specs[key]['max']
                self.bin_width[key] = hist_specs[key]['delta']
        self.bin_edges_fitness = np.arange(0, self.bin_max['fitness'] +
                                           self.bin_width['fitness'] / 2, self.bin_width['fitness'])
        self.hist_counts_fitness = np.zeros_like(self.bin_edges_fitness[:-1], dtype=float)
        self.bin_edges_age = np.arange(0, self.bin_max['age'] + self.bin_width['age'] / 2,
                                       self.bin_width['age'])
        self.hist_counts_age = np.zeros_like(self.bin_edges_age[:-1], dtype=float)
        self.bin_edges_weight = np.arange(0, self.bin_max['weight'] + self.bin_width['weight'] / 2,
                                          self.bin_width['weight'])
        self.hist_counts_weight = np.zeros_like(self.bin_edges_weight[:-1], dtype=float)

        self.img_dir = img_dir
        self.img_base = img_base
        self.hist_specs = hist_specs
        self.ymax_animals = ymax_animals

        self.island_map = island_map
        self._img_ctr = 0
        self._img_years = 1

        # the following will be initialized by _setup_graphics
        self._fig = None
        # island map
        self._ax_map = None
        self._map_plot = None
        # year counter
        self._ax_year = None
        self._year_text = None
        # fauna amount line
        self._ax_amount = None
        self._h_line = None
        self._c_line = None
        # herbivores distribute colormap
        self._ax_h_distribute = None
        self._h_distribute_cmap = None
        # carnivores distribute colormap
        self._ax_c_distribute = None
        self._c_distribute_cmap = None
        # fitness stair plot
        self._ax_fitness = None
        self._fitness_stair_h = None
        self._fitness_stair_c = None
        # age stair plot
        self._ax_age = None
        self._age_stair_h = None
        self._age_stair_c = None
        # weight stair plot
        self._ax_weight = None
        self._weight_stair_h = None
        self._weight_stair_c = None

        island_map = textwrap.dedent(self.island_map)

        self.map_rgb = [[Graphics.rgb_value[column] for column in row]
                        for row in island_map.splitlines()]

    def setup(self, final_years, img_years, cmax_animals=None):
        """
        Prepare graphics.

        Parameters
        ----------
        final_years: int
            Last year to be visualised.
        img_years: int
            Interval between saving image to file.
        cmax_animals: dictionary
            Color-scale limits for animal densities.
        """

        self._img_years = img_years

        # create new figure window
        if self._fig is None:
            self._fig = plt.figure(figsize=(8, 8))

        self.add_map()
        self.add_year_counter()
        self.add_fauna_amount(final_years)
        self.add_herbivores_distribute(cmax_animals)
        self.add_carnivores_distribute(cmax_animals)
        self.add_fitness()
        self.add_age()
        self.add_weight()

    def add_map(self):
        """Add island map into the figure"""
        if self._ax_map is None:
            self._ax_map = self._fig.add_axes([0.1, 0.7, 0.3, 0.2])
            self._map_plot = None

            self._ax_map.imshow(self.map_rgb)

            self._ax_map.set_xticks(range(len(self.map_rgb[0])))
            self._ax_map.set_xticklabels(range(1, 1 + len(self.map_rgb[0])))
            self._ax_map.set_yticks(range(len(self.map_rgb)))
            self._ax_map.set_yticklabels(range(1, 1 + len(self.map_rgb)))
            self._ax_map.set_title('Map of Rossumøya')
            self._ax_map.axis('off')

            self._ax_lg = self._fig.add_axes([0.1, 0.65, 0.3, 0.1])  # llx, lly, w, h
            self._ax_lg.axis('off')
            for ix, name in enumerate(('Water', 'Lowland',
                                       'Highland', 'Desert')):
                self._ax_lg.add_patch(plt.Rectangle(((ix + 0.8) * 0.2, 0.), 0.15, 0.15,
                                                    edgecolor='none',
                                                    facecolor=Graphics.rgb_value[name[0]]))
                self._ax_lg.text((ix + 0.85) * 0.2, 0.35, name,
                                 transform=self._ax_lg.transAxes, fontsize=7)

    def add_year_counter(self):
        """Add the year counter into the figure."""
        if self._ax_year is None:
            self._ax_year = self._fig.add_axes([0.35, 0.9, 0.3, 0.1])
            self._year_text = None
            self._ax_year.axis('off')
        if self._year_text is None:
            template = 'Year: {:5d}'
            self._year_text = self._ax_year.text(0.5, 0.5, template.format(0),
                                                 horizontalalignment='center',
                                                 verticalalignment='center',
                                                 transform=self._ax_year.transAxes, fontsize=15)

    def add_fauna_amount(self, final_years):
        """Add the fauna amount axes into the figure."""
        if self._ax_amount is None:
            self._ax_amount = self._fig.add_axes([0.7, 0.7, 0.2, 0.2])
        if self.ymax_animals is None:
            self.ymax_animals = 15000
        self._ax_amount.set_ylim(0, self.ymax_animals)
        self._ax_amount.set_xlim(0, final_years + 1)
        self._ax_amount.set_title('Animal amount')
        self._ax_amount.set_xlabel('year')
        self._ax_amount.set_ylabel('Num of Fauna')
        # self._ax_amount.legend()
        if self._h_line is None:
            self._h_line = self._ax_amount.plot(
                np.arange(0, final_years + 1), np.full(final_years + 1, np.nan),
                'b.', label='Herbivores')[0]
        if self._c_line is None:
            self._c_line = self._ax_amount.plot(
                np.arange(0, final_years + 1), np.full(final_years + 1, np.nan),
                'r.', label='Carnivores')[0]
        else:
            x_data_h, y_data_h = self._h_line.get_data()
            x_data_c, y_data_c = self._c_line.get_data()
            xnew_h = np.arange(x_data_h[-1] + 1, final_years)
            xnew_c = np.arange(x_data_c[-1] + 1, final_years)
            ynew_h = np.full(xnew_h.shape, np.nan)
            ynew_c = np.full(xnew_c.shape, np.nan)
            x_stack_h = np.hstack((x_data_h, xnew_h))
            x_stack_c = np.hstack((x_data_c, xnew_c))
            y_stack_h = np.hstack((y_data_h, ynew_h))
            y_stack_c = np.hstack((y_data_c, ynew_c))
            self._h_line.set_data((x_stack_h, y_stack_h))
            self._c_line.set_data((x_stack_c, y_stack_c))

    def add_herbivores_distribute(self, cmax_animals):
        """Add the herbivores distribute colormap into the figure."""
        if self._ax_h_distribute is None:
            if cmax_animals is not None:
                cm_h_max = cmax_animals['Herbivore']
            else:
                cm_h_max = 100
            self._ax_h_distribute = self._fig.add_axes([0.25, 0.35, 0.25, 0.25])
            self._h_distribute_cmap = self._ax_h_distribute.imshow(
                np.zeros(np.array(self.map_rgb).shape),
                interpolation='nearest', vmin=0, vmax=cm_h_max)
            plt.colorbar(self._h_distribute_cmap, ax=self._ax_h_distribute, shrink=0.7)

    def add_carnivores_distribute(self, cmax_animals):
        """Add the carnivores distribute colormap into the figure."""
        if self._ax_c_distribute is None:
            if cmax_animals is not None:
                cm_c_max = cmax_animals['Carnivore']
            else:
                cm_c_max = 100
            self._ax_c_distribute = self._fig.add_axes([0.6, 0.35, 0.25, 0.25])
            self._c_distribute_cmap = self._ax_c_distribute.imshow(
                np.zeros(np.array(self.map_rgb).shape), interpolation='nearest',
                vmin=0, vmax=cm_c_max)
            plt.colorbar(self._c_distribute_cmap, ax=self._ax_c_distribute, shrink=0.7)

    def add_fitness(self):
        """Add the fitness histogram into the figure."""
        if self._ax_fitness is None:
            self._ax_fitness = self._fig.add_axes([0.1, 0.1, 0.2, 0.2])
        self._ax_fitness.set_title('Fitness', fontsize=8)
        self._ax_fitness.set_xlim(0, self.bin_max['fitness'])
        self._ax_fitness.set_ylim(0, 5000)
        if self._fitness_stair_h is None:
            self._fitness_stair_h = self._ax_fitness.stairs(
                self.hist_counts_fitness, self.bin_edges_fitness,
                color='b', lw=2, label='Herbivores')
        if self._fitness_stair_c is None:
            self._fitness_stair_c = self._ax_fitness.stairs(
                self.hist_counts_fitness, self.bin_edges_fitness,
                color='r', lw=2, label='Carnivores')

    def add_age(self):
        """Add the age histogram into the figure."""
        if self._ax_age is None:
            self._ax_age = self._fig.add_axes([0.4, 0.1, 0.2, 0.2])
        self._ax_age.set_title('Age', fontsize=8)
        self._ax_age.set_xlim(0, self.bin_max['age'])
        self._ax_age.set_ylim(0, 5000)
        if self._age_stair_h is None:
            self._age_stair_h = self._ax_age.stairs(self.hist_counts_age, self.bin_edges_age,
                                                    color='b', lw=2, label='Herbivores')
        if self._age_stair_c is None:
            self._age_stair_c = self._ax_age.stairs(self.hist_counts_age, self.bin_edges_age,
                                                    color='r', lw=2, label='Carnivores')

    def add_weight(self):
        """Add the weight histogram into the figure."""
        if self._ax_weight is None:
            self._ax_weight = self._fig.add_axes([0.7, 0.1, 0.2, 0.2])
        self._ax_weight.set_title('Weight', fontsize=8)
        self._ax_weight.set_xlim(0, self.bin_max['weight'])
        self._ax_weight.set_ylim(0, 5000)
        if self._weight_stair_h is None:
            self._weight_stair_h = self._ax_weight.stairs(
                self.hist_counts_weight, self.bin_edges_weight,
                color='b', lw=2, label='Herbivores')
        if self._weight_stair_c is None:
            self._weight_stair_c = self._ax_weight.stairs(
                self.hist_counts_weight, self.bin_edges_weight,
                color='r', lw=2, label='Carnivores')

    def update_year_counter(self, year):
        """update the year counter in the figure."""
        self._year_text.set_text('Year: {:5d}'.format(year))
        plt.pause(0.001)

    def update_fauna_amount(self, year, h_num, c_num):
        """update the fauna_amount axes in the figure."""
        ydata_h = self._h_line.get_ydata()
        ydata_h[year] = h_num
        self._h_line.set_ydata(ydata_h)

        ydata_c = self._c_line.get_ydata()
        ydata_c[year] = c_num
        self._c_line.set_ydata(ydata_c)
        plt.pause(0.001)

    def update_herbivores_distribute(self, distribution):
        """update the herbivores distribute colormap in the figure."""
        y, x = np.array(self.map_rgb).shape[0], np.array(self.map_rgb).shape[1]
        self._ax_h_distribute.imshow(distribution,
                                     interpolation='nearest')
        # plt.colorbar(h_num_axis, ax=self._ax_h_distribute)
        self._ax_h_distribute.set_xticks(range(0, x, 5))
        self._ax_h_distribute.set_xticklabels(range(0, x, 5))
        self._ax_h_distribute.set_yticks(range(0, y, 5))
        self._ax_h_distribute.set_yticklabels(range(0, y, 5))
        self._ax_h_distribute.set_title('Herbivore Distribution')
        # plt.colorbar(ax=self._ax_h_distribute)
        plt.pause(0.001)

    def update_carnivores_distribute(self, distribution):
        """update the carnivores distribute colormap in the figure."""
        v_max = distribution.max()
        v_min = distribution.min()
        y, x = np.array(self.map_rgb).shape[0], np.array(self.map_rgb).shape[1]
        self._ax_c_distribute.imshow(distribution,
                                     interpolation='nearest',
                                     vmin=v_min, vmax=v_max)
        self._ax_c_distribute.set_xticks(range(0, x, 5))
        self._ax_c_distribute.set_xticklabels(range(0, x, 5))
        self._ax_c_distribute.set_yticks(range(0, y, 5))
        self._ax_c_distribute.set_yticklabels(range(0, y, 5))
        self._ax_c_distribute.set_title('Carnivores Distribution')
        plt.pause(0.001)

    def update_fitness(self, year, h_fitness_list, c_fitness_list):
        """update the fitness distribute histogram in the figure."""
        hist_counts_h, _ = np.histogram(h_fitness_list, self.bin_edges_fitness)
        self._fitness_stair_h.set_data(hist_counts_h)

        hist_counts_c, _ = np.histogram(c_fitness_list, self.bin_edges_fitness)
        self._fitness_stair_c.set_data(hist_counts_c)
        plt.pause(0.001)

    def update_age(self, year, h_age_list, c_age_list):
        """update the age distribute histogram in the figure."""
        hist_counts_h, _ = np.histogram(h_age_list, self.bin_edges_age)
        self._age_stair_h.set_data(hist_counts_h)

        hist_counts_c, _ = np.histogram(c_age_list, self.bin_edges_age)
        self._age_stair_c.set_data(hist_counts_c)
        plt.pause(0.001)

    def update_weight(self, year, h_weight_list, c_weight_list):
        """update the weight distribute histogram in the figure."""
        hist_counts_h, _ = np.histogram(h_weight_list, self.bin_edges_weight)
        self._weight_stair_h.set_data(hist_counts_h)

        hist_counts_c, _ = np.histogram(c_weight_list, self.bin_edges_weight)
        self._weight_stair_c.set_data(hist_counts_c)
        plt.pause(0.001)

    def save_graphics(self):
        """
        Saves graphics to file if file name is given.
        """

        if self._img_base is None:
            pass

        else:
            workdir = Path(f'./{self.img_dir}')
            if workdir.exists():
                pass
            else:
                workdir.mkdir()
            workpath = Path(f'{workdir}/{self.img_base}_{self._img_ctr:05d}.{self._img_fmt}')
            plt.savefig(workpath)
            self._img_ctr += 1

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt
        """

        if self.img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-framerate', '2',  # control the fps of the output movie,
                                       # which will be very fast without this
                                       '-i', '{}/{}_%05d.png'.format(self.img_dir, self.img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-r', '2',  # control the fps of the output movie,
                                       # which will be very fast without this
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self.img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)
