import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import os
from typing import List, Optional, Tuple

class NiftiVisualizer:
    """
    Clase para visualización de archivos NIfTI, con soporte para visualización
    de imágenes 3D y 4D, comparación y superposición de segmentaciones.
    """
    
    def __init__(self):
        """Inicializa el visualizador."""
        self.fig = None
        self.axes = None
        self.sliders = {}
        self.images = {}
    
    def setup_display(self, num_subplots: int = 1) -> None:
        """Configura la pantalla de visualización."""
        self.fig, self.axes = plt.subplots(1, num_subplots, figsize=(7*num_subplots, 6))
        if num_subplots == 1:
            self.axes = [self.axes]
        plt.subplots_adjust(bottom=0.25)

    def add_slider(self, name: str, valmin: int, valmax: int, valinit: int) -> None:
        """Añade un slider a la visualización."""
        ax_slider = plt.axes([0.2, 0.1 + len(self.sliders) * 0.03, 0.6, 0.02])
        self.sliders[name] = Slider(
            ax_slider, name, valmin, valmax,
            valinit=valinit, valstep=1
        )

    def view_single_volume(self, file_path: str) -> None:
        """
        Visualiza un único volumen NIfTI (3D o 4D).
        
        Args:
            file_path (str): Ruta al archivo NIfTI
        """
        img = nib.load(file_path)
        data = img.get_fdata()
        
        self.setup_display(1)
        
        if len(data.shape) == 3:
            self._setup_3d_view(data)
        elif len(data.shape) == 4:
            self._setup_4d_view(data)
        else:
            raise ValueError("Solo se soportan volúmenes 3D o 4D")
        
        plt.show()

    def _setup_3d_view(self, data: np.ndarray) -> None:
        """Configura visualización para volumen 3D."""
        slice_z = data.shape[2] // 2
        self.images['main'] = self.axes[0].imshow(data[:, :, slice_z], cmap='gray')
        self.axes[0].set_title(f'Corte Z={slice_z}')
        
        self.add_slider('Z', 0, data.shape[2]-1, slice_z)
        
        def update(val):
            z = int(self.sliders['Z'].val)
            self.images['main'].set_data(data[:, :, z])
            self.axes[0].set_title(f'Corte Z={z}')
            self.fig.canvas.draw_idle()
        
        self.sliders['Z'].on_changed(update)

    def _setup_4d_view(self, data: np.ndarray) -> None:
        """Configura visualización para volumen 4D."""
        slice_z = data.shape[2] // 2
        time_point = 0
        
        self.images['main'] = self.axes[0].imshow(
            data[:, :, slice_z, time_point], cmap='gray'
        )
        self.axes[0].set_title(f'Tiempo={time_point}, Corte Z={slice_z}')
        
        self.add_slider('Z', 0, data.shape[2]-1, slice_z)
        self.add_slider('T', 0, data.shape[3]-1, time_point)
        
        def update(val):
            z = int(self.sliders['Z'].val)
            t = int(self.sliders['T'].val)
            self.images['main'].set_data(data[:, :, z, t])
            self.axes[0].set_title(f'Tiempo={t}, Corte Z={z}')
            self.fig.canvas.draw_idle()
        
        for slider in self.sliders.values():
            slider.on_changed(update)

    def compare_volumes(self, file_path1: str, file_path2: str, 
                       titles: Tuple[str, str] = ("Original", "Segmentación")) -> None:
        """
        Compara dos volúmenes NIfTI lado a lado.
        
        Args:
            file_path1 (str): Ruta al primer archivo NIfTI
            file_path2 (str): Ruta al segundo archivo NIfTI
            titles (tuple): Títulos para cada imagen
        """
        img1 = nib.load(file_path1)
        img2 = nib.load(file_path2)
        data1 = img1.get_fdata()
        data2 = img2.get_fdata()
        
        if data1.shape != data2.shape:
            raise ValueError("Los volúmenes deben tener las mismas dimensiones")
        
        self.setup_display(2)
        
        if len(data1.shape) == 3:
            self._setup_3d_comparison(data1, data2, titles)
        elif len(data1.shape) == 4:
            self._setup_4d_comparison(data1, data2, titles)
        
        plt.show()

    def _setup_3d_comparison(self, data1: np.ndarray, data2: np.ndarray, 
                           titles: Tuple[str, str]) -> None:
        """Configura comparación de volúmenes 3D."""
        slice_z = data1.shape[2] // 2
        
        self.images['left'] = self.axes[0].imshow(data1[:, :, slice_z], cmap='gray')
        self.images['right'] = self.axes[1].imshow(data2[:, :, slice_z], cmap='gray')
        
        self.axes[0].set_title(f'{titles[0]} - Corte Z={slice_z}')
        self.axes[1].set_title(f'{titles[1]} - Corte Z={slice_z}')
        
        self.add_slider('Z', 0, data1.shape[2]-1, slice_z)
        
        def update(val):
            z = int(self.sliders['Z'].val)
            self.images['left'].set_data(data1[:, :, z])
            self.images['right'].set_data(data2[:, :, z])
            self.axes[0].set_title(f'{titles[0]} - Corte Z={z}')
            self.axes[1].set_title(f'{titles[1]} - Corte Z={z}')
            self.fig.canvas.draw_idle()
        
        self.sliders['Z'].on_changed(update)

    def _setup_4d_comparison(self, data1: np.ndarray, data2: np.ndarray, 
                           titles: Tuple[str, str]) -> None:
        """Configura comparación de volúmenes 4D."""
        slice_z = data1.shape[2] // 2
        time_point = 0
        
        self.images['left'] = self.axes[0].imshow(
            data1[:, :, slice_z, time_point], cmap='gray'
        )
        self.images['right'] = self.axes[1].imshow(
            data2[:, :, slice_z, time_point], cmap='gray'
        )
        
        self.axes[0].set_title(f'{titles[0]} - T={time_point}, Z={slice_z}')
        self.axes[1].set_title(f'{titles[1]} - T={time_point}, Z={slice_z}')
        
        self.add_slider('Z', 0, data1.shape[2]-1, slice_z)
        self.add_slider('T', 0, data1.shape[3]-1, time_point)
        
        def update(val):
            z = int(self.sliders['Z'].val)
            t = int(self.sliders['T'].val)
            self.images['left'].set_data(data1[:, :, z, t])
            self.images['right'].set_data(data2[:, :, z, t])
            self.axes[0].set_title(f'{titles[0]} - T={t}, Z={z}')
            self.axes[1].set_title(f'{titles[1]} - T={t}, Z={z}')
            self.fig.canvas.draw_idle()
        
        for slider in self.sliders.values():
            slider.on_changed(update)

    def view_segmentation_overlay(self, original_path: str, segmentation_path: str) -> None:
        """
        Muestra la segmentación superpuesta sobre la imagen original.
        
        Args:
            original_path (str): Ruta a la imagen original
            segmentation_path (str): Ruta a la segmentación
        """
        img_original = nib.load(original_path)
        img_seg = nib.load(segmentation_path)
        
        data_original = img_original.get_fdata()
        data_seg = img_seg.get_fdata()
        
        if data_original.shape != data_seg.shape:
            raise ValueError("La imagen original y la segmentación deben tener las mismas dimensiones")
        
        self.setup_display(1)
        slice_z = data_original.shape[2] // 2
        time_point = 0 if len(data_original.shape) == 4 else None
        
        # Configurar visualización inicial
        if time_point is not None:
            self._setup_4d_overlay(data_original, data_seg, slice_z, time_point)
        else:
            self._setup_3d_overlay(data_original, data_seg, slice_z)
        
        plt.show()

    def _setup_3d_overlay(self, data_original: np.ndarray, data_seg: np.ndarray, 
                         slice_z: int) -> None:
        """Configura superposición para volúmenes 3D."""
        # Mostrar imagen original
        self.images['base'] = self.axes[0].imshow(data_original[:, :, slice_z], cmap='gray')
        
        # Superponer segmentación
        masked_seg = np.ma.masked_where(data_seg[:, :, slice_z] == 0, data_seg[:, :, slice_z])
        self.images['overlay'] = self.axes[0].imshow(masked_seg, cmap='jet', alpha=0.5)
        
        self.axes[0].set_title(f'Segmentación superpuesta - Corte Z={slice_z}')
        
        self.add_slider('Z', 0, data_original.shape[2]-1, slice_z)
        
        def update(val):
            z = int(self.sliders['Z'].val)
            self.images['base'].set_data(data_original[:, :, z])
            masked_seg = np.ma.masked_where(data_seg[:, :, z] == 0, data_seg[:, :, z])
            self.images['overlay'].set_data(masked_seg)
            self.axes[0].set_title(f'Segmentación superpuesta - Corte Z={z}')
            self.fig.canvas.draw_idle()
        
        self.sliders['Z'].on_changed(update)

    def _setup_4d_overlay(self, data_original: np.ndarray, data_seg: np.ndarray,
                         slice_z: int, time_point: int) -> None:
        """Configura superposición para volúmenes 4D."""
        # Mostrar imagen original
        self.images['base'] = self.axes[0].imshow(
            data_original[:, :, slice_z, time_point], cmap='gray'
        )
        
        # Superponer segmentación
        masked_seg = np.ma.masked_where(
            data_seg[:, :, slice_z, time_point] == 0,
            data_seg[:, :, slice_z, time_point]
        )
        self.images['overlay'] = self.axes[0].imshow(masked_seg, cmap='jet', alpha=0.5)
        
        self.axes[0].set_title(f'Segmentación superpuesta - T={time_point}, Z={slice_z}')
        
        self.add_slider('Z', 0, data_original.shape[2]-1, slice_z)
        self.add_slider('T', 0, data_original.shape[3]-1, time_point)
        
        def update(val):
            z = int(self.sliders['Z'].val)
            t = int(self.sliders['T'].val)
            self.images['base'].set_data(data_original[:, :, z, t])
            masked_seg = np.ma.masked_where(data_seg[:, :, z, t] == 0, data_seg[:, :, z, t])
            self.images['overlay'].set_data(masked_seg)
            self.axes[0].set_title(f'Segmentación superpuesta - T={t}, Z={z}')
            self.fig.canvas.draw_idle()
        
        for slider in self.sliders.values():
            slider.on_changed(update)

if __name__ == "__main__":
    # Ejemplo de uso
    visualizer = NiftiVisualizer()
    
    # Visualizar un solo volumen
    # visualizer.view_single_volume("imagen.nii.gz")
    
    # Comparar dos volúmenes
    # visualizer.compare_volumes("original.nii.gz", "segmentacion.nii.gz")
    
    # Ver superposición de segmentación
    # visualizer.view_segmentation_overlay("original.nii.gz", "segmentacion.nii.gz")