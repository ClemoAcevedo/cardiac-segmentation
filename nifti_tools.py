import nibabel as nib
import numpy as np
import os
from typing import List, Tuple, Optional

class NiftiTools:
    """
    Clase para manipular archivos NIfTI, incluyendo operaciones de división y unión
    de volúmenes 4D.
    """
    
    @staticmethod
    def split_4d_volume(input_file: str, output_folder: str, split_type: str = "t") -> None:
        """
        Divide un volumen 4D en volúmenes 3D individuales.
        
        Args:
            input_file (str): Ruta al archivo NIfTI 4D
            output_folder (str): Carpeta donde se guardarán los volúmenes divididos
            split_type (str): Tipo de división ('t' para tiempo, 'z' para eje Z)
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"No se encontró el archivo: {input_file}")
        
        img_4d = nib.load(input_file)
        img_4d_data = img_4d.get_fdata()
        nombre_base = os.path.basename(input_file).replace('.nii.gz', '')
        
        os.makedirs(output_folder, exist_ok=True)
        
        if split_type.lower() == "z":
            print(f"Separando en el eje Z para {nombre_base}...")
            NiftiTools._split_by_z(img_4d_data, img_4d.affine, nombre_base, output_folder)
        elif split_type.lower() == "t" and len(img_4d_data.shape) == 4:
            print(f"Separando en el tiempo para {nombre_base}...")
            NiftiTools._split_by_time(img_4d_data, img_4d.affine, nombre_base, output_folder)
        else:
            raise ValueError("Tipo de división no válido o dimensiones incorrectas")

    @staticmethod
    def _split_by_z(data: np.ndarray, affine: np.ndarray, base_name: str, output_folder: str) -> None:
        """Helper method para dividir por eje Z."""
        num_slices = data.shape[2]
        for z in range(num_slices):
            img_2d = data[:, :, z]
            img_2d_nifti = nib.Nifti1Image(img_2d, affine)
            output_filename = os.path.join(output_folder, f"{base_name}_slice_{z:04d}.nii.gz")
            nib.save(img_2d_nifti, output_filename)
            print(f"Guardada rebanada Z {z+1}/{num_slices}")

    @staticmethod
    def _split_by_time(data: np.ndarray, affine: np.ndarray, base_name: str, output_folder: str) -> None:
        """Helper method para dividir por tiempo."""
        num_timepoints = data.shape[3]
        for t in range(num_timepoints):
            img_3d = data[..., t]
            img_3d_nifti = nib.Nifti1Image(img_3d, affine)
            output_filename = os.path.join(output_folder, f"{base_name}_time_{t:04d}.nii.gz")
            nib.save(img_3d_nifti, output_filename)
            print(f"Guardado tiempo {t+1}/{num_timepoints}")

    @staticmethod
    def merge_to_4d(input_folder: str, output_file: str, pattern: str = "*.nii.gz") -> None:
        """
        Combina múltiples volúmenes 3D en un solo volumen 4D.
        
        Args:
            input_folder (str): Carpeta con los archivos NIfTI 3D
            output_file (str): Ruta donde se guardará el archivo 4D resultante
            pattern (str): Patrón para filtrar archivos (por defecto "*.nii.gz")
        """
        import glob
        
        # Obtener lista de archivos ordenados
        files = sorted(glob.glob(os.path.join(input_folder, pattern)))
        if not files:
            raise ValueError(f"No se encontraron archivos en {input_folder} con patrón {pattern}")

        # Cargar primer imagen para obtener dimensiones y affine
        first_img = nib.load(files[0])
        first_data = first_img.get_fdata()
        
        # Crear array 4D
        img_4d_data = np.zeros(first_data.shape + (len(files),))
        
        # Cargar cada volumen
        for t, file in enumerate(files):
            img = nib.load(file)
            img_4d_data[..., t] = img.get_fdata()
            print(f"Procesado volumen {t+1}/{len(files)}")
        
        # Crear y guardar imagen 4D
        img_4d = nib.Nifti1Image(img_4d_data, first_img.affine)
        nib.save(img_4d, output_file)
        print(f"Archivo 4D guardado en {output_file}")

    @staticmethod
    def get_nifti_stats(file_path: str) -> dict:
        """
        Obtiene estadísticas básicas de un archivo NIfTI.
        
        Args:
            file_path (str): Ruta al archivo NIfTI
            
        Returns:
            dict: Diccionario con estadísticas básicas
        """
        img = nib.load(file_path)
        data = img.get_fdata()
        
        stats = {
            "dimensions": data.shape,
            "min_value": float(np.min(data)),
            "max_value": float(np.max(data)),
            "mean_value": float(np.mean(data)),
            "std_value": float(np.std(data)),
            "non_zero_voxels": int(np.sum(data != 0)),
            "total_voxels": int(data.size),
            "affine": img.affine.tolist()
        }
        
        return stats

if __name__ == "__main__":
    # Ejemplo de uso
    import argparse
    
    parser = argparse.ArgumentParser(description='Herramientas para manipular archivos NIfTI')
    parser.add_argument('--action', choices=['split', 'merge', 'stats'], required=True,
                      help='Acción a realizar: split, merge, o stats')
    parser.add_argument('--input', required=True, help='Archivo o carpeta de entrada')
    parser.add_argument('--output', help='Archivo o carpeta de salida')
    parser.add_argument('--split-type', choices=['t', 'z'], default='t',
                      help='Tipo de división (solo para action=split)')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'split':
            if not args.output:
                raise ValueError("Se requiere --output para split")
            NiftiTools.split_4d_volume(args.input, args.output, args.split_type)
        
        elif args.action == 'merge':
            if not args.output:
                raise ValueError("Se requiere --output para merge")
            NiftiTools.merge_to_4d(args.input, args.output)
        
        elif args.action == 'stats':
            stats = NiftiTools.get_nifti_stats(args.input)
            print("\nEstadísticas del archivo NIfTI:")
            for key, value in stats.items():
                print(f"{key}: {value}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)