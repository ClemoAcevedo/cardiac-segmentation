import os
import shutil
import subprocess

def convert_dicom_to_nifti(dicom_folder, nii_output_folder, json_output_folder, case_prefix="time"):
    """
    Convierte los archivos DICOM en la carpeta proporcionada a formato NIfTI (.nii.gz) 
    y mueve los archivos JSON generados a una carpeta separada.
    
    Parameters:
    dicom_folder (str): Ruta a la carpeta que contiene archivos DICOM.
    nii_output_folder (str): Carpeta donde se guardarán los archivos NIfTI.
    json_output_folder (str): Carpeta donde se guardarán los archivos JSON generados.
    case_prefix (str): Prefijo que se usará para los archivos NIfTI y JSON (por defecto "time").
    """
    os.makedirs(nii_output_folder, exist_ok=True)
    os.makedirs(json_output_folder, exist_ok=True)

    modality_index = 1

    print(f"Convirtiendo archivos DICOM de {dicom_folder} a NIfTI...")
    dcm2niix_cmd = [
        "dcm2niix",
        "-z", "y",
        "-o", nii_output_folder,
        dicom_folder
    ]
    subprocess.run(dcm2niix_cmd, check=True)

    renombrar_archivos(nii_output_folder, json_output_folder, case_prefix, modality_index)

def renombrar_archivos(nii_output_folder, json_output_folder, case_prefix, modality_index):
    """
    Renombra los archivos .nii.gz y .json generados por dcm2niix, 
    y mueve los archivos .json a la carpeta de salida de JSON.
    
    Parametros:
    nii_output_folder (str): Ruta a la carpeta que contiene los archivos NIfTI y JSON.
    json_output_folder (str): Carpeta donde se moverán los archivos JSON renombrados.
    case_prefix (str): Prefijo que se usará para los archivos renombrados (por defecto "time").
    modality_index (int): Índice inicial para numerar las temporalidades (se incrementa con cada archivo).
    """
    for archivo in os.listdir(nii_output_folder):
        if archivo.endswith(".nii.gz"):
            base_name = archivo.split('.nii.gz')[0]
            new_name_nii = f"{case_prefix}_{modality_index:02d}_0000.nii.gz"
            ruta_vieja_nii = os.path.join(nii_output_folder, archivo)
            ruta_nueva_nii = os.path.join(nii_output_folder, new_name_nii)
            os.rename(ruta_vieja_nii, ruta_nueva_nii)
            print(f"Renombrado NIfTI: {ruta_vieja_nii} -> {ruta_nueva_nii}")

            json_name = base_name + ".json"
            ruta_vieja_json = os.path.join(nii_output_folder, json_name)
            if os.path.exists(ruta_vieja_json):
                new_name_json = f"{case_prefix}_{modality_index:02d}_0000.json"
                ruta_nueva_json = os.path.join(json_output_folder, new_name_json)
                shutil.move(ruta_vieja_json, ruta_nueva_json)
                print(f"Renombrado y movido JSON: {ruta_vieja_json} -> {ruta_nueva_json}")
            else:
                print(f"Falta archivo JSON para: {new_name_nii}")

            modality_index += 1

# CAMBIAR PARA GUSTO PERSONAL

dicom_folder = "dicom"
nii_output_folder = "salida/imagenes"
json_output_folder = "salida/json"

convert_dicom_to_nifti(dicom_folder, nii_output_folder, json_output_folder)
