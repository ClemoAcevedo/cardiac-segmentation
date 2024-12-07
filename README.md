# Procesamiento de Imágenes Cardíacas y Generación de Mallas 3D

Este repositorio contiene herramientas para procesar imágenes de resonancia magnética cardíaca, realizar segmentación del ventrículo izquierdo y generar modelos 3D. El pipeline está diseñado específicamente para trabajar con nnUNet v1 (Task027_ACDC).

## Estructura del Repositorio

El repositorio contiene cuatro scripts principales:

1. `dicom_to_nifti.py`: Conversión de imágenes DICOM a formato NIfTI
2. `mesh_generator.py`: Generación de mallas 3D a partir de segmentaciones
3. `nifti_tools.py`: Utilidades para manipulación de archivos NIfTI
4. `visualization_tools.py`: Herramientas de visualización y validación

## Requisitos

```bash
# Python packages
nibabel
numpy
pyvista
vtk
medpy
matplotlib

# Software externo
dcm2niix  # Para conversión DICOM a NIfTI
nnUNet    # Para segmentación (versión 1)
```

## Pipeline de Procesamiento

### 1. Conversión DICOM a NIfTI
```bash
python dicom_to_nifti.py --input_dir <carpeta_dicom> --output_dir <carpeta_salida>
```
- Convierte series DICOM a formato NIfTI (.nii.gz)
- Organiza automáticamente los archivos de salida
- Genera metadatos en formato JSON

### 2. Segmentación con nnUNet
```bash
# Asegúrate de tener nnUNet v1 instalado y el modelo Task027_ACDC descargado
nnUNet_predict -i <carpeta_entrada> -o <carpeta_salida> -t 27 -m 3d_fullres
```
- Utiliza el modelo preentrenado Task027_ACDC
- Segmenta automáticamente el ventrículo izquierdo

### 3. Generación de Malla 3D
```bash
python mesh_generator.py --input <segmentacion.nii.gz> --output <malla.stl>
```
- Genera una malla 3D a partir de la segmentación
- Aplica suavizado y optimización de la malla
- Guarda el resultado en formato STL

## Herramientas Auxiliares

### Manipulación de NIfTI (`nifti_tools.py`)
```python
from nifti_tools import NiftiTools

# Dividir volumen 4D en volúmenes 3D
NiftiTools.split_4d_volume('volumen_4d.nii.gz', 'carpeta_salida', split_type='t')

# Combinar volúmenes 3D en un volumen 4D
NiftiTools.merge_to_4d('carpeta_entrada', 'volumen_4d.nii.gz')

# Obtener estadísticas de un archivo NIfTI
stats = NiftiTools.get_nifti_stats('archivo.nii.gz')
```

### Visualización (`visualization_tools.py`)
```python
from visualization_tools import NiftiVisualizer

visualizer = NiftiVisualizer()

# Visualizar un solo volumen
visualizer.view_single_volume('imagen.nii.gz')

# Comparar dos volúmenes
visualizer.compare_volumes('original.nii.gz', 'segmentacion.nii.gz')

# Ver superposición de segmentación
visualizer.view_segmentation_overlay('original.nii.gz', 'segmentacion.nii.gz')
```

## Parámetros Ajustables

### En `mesh_generator.py`:
- Suavizado de la malla (iterations, pass_band)
- Nivel de detalle (level en marching cubes)
- Filtrado de difusión anisotrópica (niter, kappa, gamma)

### En `dicom_to_nifti.py`:
- Formato de nombre de archivo de salida
- Organización de carpetas

## Notas Importantes

- El pipeline está optimizado para resonancia magnética cardíaca
- Se recomienda revisar visualmente los resultados en cada paso
- La calidad de la malla 3D puede ajustarse mediante los parámetros en `mesh_generator.py`
- Para grandes volúmenes de datos, considerar el procesamiento por lotes

## Limitaciones Conocidas

- El modelo nnUNet utilizado (Task027_ACDC) está específicamente entrenado para cardio RM
- La generación de mallas 3D puede requerir ajustes según la calidad de la segmentación
- El proceso puede requerir considerable memoria RAM para volúmenes grandes