import nibabel as nib
from skimage import measure
import pyvista as pv
import os
import numpy as np
from medpy.filter.smoothing import anisotropic_diffusion
import vtk

pv.set_plot_theme('document')

# Función para cargar el archivo NIfTI y obtener los datos de segmentación y espaciado
def load_segmentation(nifti_path, target_label=1):
    if not os.path.exists(nifti_path):
        raise FileNotFoundError(f"Archivo no encontrado: {nifti_path}")
    
    img = nib.load(nifti_path)
    segmentation_data = img.get_fdata()
    spacing = img.header.get_zooms()
    
    # Filtrar solo el ventrículo izquierdo
    segmentation_data = (segmentation_data == target_label).astype(np.float32)
    
    return segmentation_data, spacing

# Función para generar una malla usando el algoritmo Marching Cubes
def generate_mesh(segmentation_data, spacing, level=0.5):
    # Parámetro: 'level' controla el nivel de isosuperficie para extraer la malla.
    # Por qué cambiarlo: Si la malla no representa correctamente la forma del corazón,
    # puedes ajustar este valor para mejorar la extracción de la superficie.
    # Valores a probar: 0.4, 0.5 (por defecto), 0.6
    verts, faces, normals, values = measure.marching_cubes(
        segmentation_data,
        level=level,
        spacing=spacing,
        step_size=1  # Parámetro: 'step_size' controla la resolución de la malla.
                     # Por qué cambiarlo: Valores menores aumentan el detalle de la malla pero incrementan el tiempo de procesamiento.
                     # Valores a probar: 1 (por defecto), 2, 3
    )
    print(f"Número de vértices generados: {len(verts)}")
    print(f"Número de caras generadas: {len(faces)}")
    return verts, faces

# Función para crear y suavizar la malla usando PyVista y Taubin Smoothing
def create_smooth_mesh(verts, faces):
    try:
        print("Creando la malla con PyVista...")
        
        n_faces = faces.shape[0]
        faces_formatted = np.hstack([np.full((n_faces, 1), 3), faces]).astype(np.int64)
        faces_formatted = faces_formatted.ravel()
        
        mesh = pv.PolyData(verts, faces_formatted)
        mesh.clean(inplace=True)
        mesh = mesh.connectivity(extraction_mode='largest')
        
        print(f"Vértices antes del suavizado: {mesh.n_points}")
        print(f"Caras antes del suavizado: {mesh.n_cells}")  # Actualizado según advertencia de deprecación
        
        # Parámetros para el suavizado de Taubin:
        # 'iterations' controla cuántas veces se aplica el suavizado.
        # Por qué cambiarlo: Más iteraciones suavizan más la malla, pero pueden borrar detalles finos.
        # Valores a probar: 10, 20, 30 (por defecto), hasta 50.
        # 'pass_band' controla la cantidad de suavizado aplicado en cada iteración.
        # Por qué cambiarlo: Valores menores producen un suavizado más agresivo.
        # Valores a probar: 0.01, 0.1 (por defecto), 0.2
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputData(mesh)
        smoother.SetNumberOfIterations(30)  # iterations
        smoother.SetPassBand(0.1)  # pass_band
        smoother.NormalizeCoordinatesOn()
        smoother.NonManifoldSmoothingOn()
        smoother.FeatureEdgeSmoothingOn()
        smoother.BoundarySmoothingOn()
        smoother.Update()
        
        smooth_mesh = pv.wrap(smoother.GetOutput())
        
        print(f"Vértices después del suavizado: {smooth_mesh.n_points}")
        print(f"Caras después del suavizado: {smooth_mesh.n_cells}")  
        
        return smooth_mesh
    except Exception as e:
        print(f"Error durante el suavizado: {e}")
        return mesh

# Función para visualizar la malla 3D con opciones avanzadas
def visualize_mesh_advanced(mesh):
    plotter = pv.Plotter()
    # Parámetro: 'color' establece el color de la malla en la visualización.
    # Por qué cambiarlo: Para mejorar la visibilidad o preferencia personal.
    # Valores a probar: 'red' (por defecto), 'blue', 'green', 'white'
    plotter.add_mesh(
        mesh,
        color='red',
        show_edges=True,
        lighting=True,
        smooth_shading=True,  # Parámetro: 'smooth_shading' activa el sombreado suave.
                              # Por qué cambiarlo: Mejora la apariencia visual de la malla.
                              # Valores a probar: True (por defecto), False
        ambient=0.2,
        diffuse=0.8,
        specular=0.5,
        specular_power=15
    )
    plotter.enable_eye_dome_lighting()
    light = pv.Light(
        position=(1, 1, 1),
        focal_point=(0, 0, 0),
        color='white',
        intensity=0.8,
        light_type='headlight'
    )
    plotter.add_light(light)
    plotter.show_axes()
    plotter.show()

# Función para guardar la malla en un archivo STL
def save_mesh(mesh, output_path):
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        mesh.save(output_path)
        print(f"Malla guardada en: {output_path}")
    except Exception as e:
        print(f"Error al guardar la malla: {e}")

# Ruta al archivo de segmentación NIfTI
nifti_path = 'time_01.nii.gz'

if __name__ == "__main__":
    try:
        segmentation_data, spacing = load_segmentation(nifti_path, target_label=1)
        print("Segmentación cargada correctamente.")
        
        # Parámetros para el filtrado de difusión anisotrópica:
        # 'niter' es el número de iteraciones del filtro.
        # Por qué cambiarlo: Más iteraciones aumentan el suavizado de la segmentación.
        # Valores a probar: 5 (por defecto), 10, 15
        # 'kappa' controla la sensibilidad al gradiente.
        # Por qué cambiarlo: Valores mayores permiten más suavizado en áreas planas.
        # Valores a probar: 20, 50 (por defecto), 100
        # 'gamma' controla la velocidad de difusión (debe ser <= 0.25 para estabilidad).
        # Por qué cambiarlo: Ajusta la intensidad del filtrado en cada iteración.
        # Valores a probar: 0.1 (por defecto), 0.2, 0.25
        segmentation_data_filtered = anisotropic_diffusion(
            segmentation_data,
            niter=5,
            kappa=50,
            gamma=0.1,
            voxelspacing=spacing,
            option=1
        )
        print("Filtrado de difusión anisotrópica aplicado.")
        
        verts, faces = generate_mesh(segmentation_data_filtered, spacing, level=0.5)
        print("Malla generada usando el algoritmo Marching Cubes.")
        
        smooth_mesh = create_smooth_mesh(verts, faces)
        print("Malla suavizada correctamente.")
        
        visualize_mesh_advanced(smooth_mesh)
        
        output_stl_path = 'mesh_output/mesh.stl'
        save_mesh(smooth_mesh, output_stl_path)
    
    except Exception as e:
        print(f"Error en el proceso: {e}")
