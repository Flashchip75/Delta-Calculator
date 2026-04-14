import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from config import cfg


class Visualizer():
    def __init__(self):
        self.pl = cfg.plotting
    
        self.dpi = self.pl.dpi
        print(f"Plotting DPI: {self.dpi}")
        if self.dpi <= 0:
            raise ValueError("Ungültige DPI-Einstellung in config.json: " \
                            f"{self.dpi}. Bitte geben Sie eine positive Ganzzahl an.")
        
        if self.pl.trajectory_plot is None or self.pl.forces_plot is None:
            raise ValueError("Fehlende Plot-Dateinamen in config.json. "
                            "Bitte stellen Sie sicher, dass 'trajectory_plot' und " \
                            "'forces_plot' unter 'plotting' definiert sind.")

    def plot_path(self,name) -> str:
        outputDir = cfg.global_cfg.output_dir
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        currentPath = os.path.join(outputDir, name)
        return currentPath

    def plot_matlab_style(self, p, T, outputDir):
        ax = plt.figure().add_subplot(111, projection='3d')
        ax.plot(p[:, 0], p[:, 1], p[:, 2], 'b-', marker='.', markersize=3, label='Pfad [m]')
        ax.quiver(p[:, 0], p[:, 1], p[:, 2], T[:, 0], T[:, 1], T[:, 2], length=0.08, color='r', alpha=0.6)
        ax.set(xlabel='X [m]', ylabel='Y [m]', zlabel='Z [m]', title='Deltarobot Trajektorie (SI-Einheiten)')
        plt.legend();
        name = self.pl.trajectory_plot
        currentPath = self.plot_path(name)
        print(f"Speichere Trajektorie-Plot unter: {currentPath}")
        plt.savefig(fname=currentPath, dpi=self.dpi, bbox_inches=self.pl.bbox_inches)
        #plt.show()

    def plot_forces(self, fname, outputDir):
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        
        currentPath = os.path.join(outputDir, fname)
        df = pd.read_csv(currentPath)
        mags = [np.linalg.norm(df[[f'{p}x', f'{p}y', f'{p}z']].values, axis=1) for p in ('ft', 'fn', 'f')]
        lbls, cols = ['|Ft| [N]', '|Fn| [N]', '|Fges| [N]'], ['g', 'r', 'k']

        plt.figure(figsize=(10, 5))
        for m, l, c in zip(mags, lbls, cols):
            plt.plot(df['t'], m, label=l, color=c, lw=1.5, ls='--' if c == 'k' else '-')
        plt.gca().set(xlabel='Zeit t [s]', ylabel='Kraft F [N]', title='Kraftverläufe (SI)')
        plt.grid(True);
        plt.legend();
        name = self.pl.forces_plot
        currentPath = self.plot_path(name)
        print(f"Speichere Kraft-Plot unter: {currentPath}")
        plt.savefig(fname=currentPath, dpi=self.dpi, bbox_inches=self.pl.bbox_inches)
        #plt.show()