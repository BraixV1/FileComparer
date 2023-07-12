from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .data_processing import magic, WriteIntoFileFromMultiple
import mimetypes
from django.http import FileResponse
import tempfile
import os
import shutil
import string
import datetime
import random
import zipfile


# Create your views here.

def process_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
        # Save the contents of the uploaded file to the temporary file
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
    return temp_path

def generate_unique_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"output_{timestamp}_{random_string}.xlsx"

def generate_unique_foldername():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"folder_{timestamp}_{random_string}"


def upload_multiple(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('zip_file')
        if not uploaded_file or not uploaded_file.name.endswith('.zip'):
            # File is missing or not a .zip file, display an error message
            error_message = "Please upload a .zip file."
            return render(request, 'uploadMultiple.html', {'error_message': error_message})

        # Generate a unique output filename
        output_file = generate_unique_filename()

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cache_dir = os.path.join(base_dir, 'cache')

            # Generate a random folder name
            random_folder = generate_unique_foldername()

            # Create the random folder path within the cache directory
            random_folder_path = os.path.join(cache_dir, random_folder)

            # Create the random folder
            os.makedirs(random_folder_path)

            # Set the temporary directory to the random folder path
            with tempfile.TemporaryDirectory(dir=random_folder_path) as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                print("Extracting the ZIP file...")
                with zipfile.ZipFile(file_path) as archive:
                    archive.extractall(random_folder_path)  # Extract the files to the random folder

                # Get the extracted file paths
                extracted_files = []
                for root, dirs, files in os.walk(random_folder_path):
                    for file in files:
                        extracted_files.append(os.path.join(root, file))

                # For some reason the program decided to also add the zip file itself to the extracted files so this snippet corrects pesky bug
                result = extracted_files
                for file in result:
                    if file.split("\\")[-1].split(".")[-1] == "zip":
                        extracted_files.remove(file)
                    
                    
                # Write to the output file from the extracted files
                WriteIntoFileFromMultiple(extracted_files, output_file)

            # Remove comment from following line to activate cache clearing
            
            #shutil.rmtree(random_folder_path)

            # Redirect to the success page with the output file
            return redirect('success', output_file=output_file)
        except Exception as e:
            # This is unfinished and can be changed if needed
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            return render(request, 'uploadMultiple.html', {'error_message': error_message})

    return render(request, 'uploadMultiple.html')


def upload_file(request):
    if request.method == 'POST':
        file_first = request.FILES['file_first']
        file_second = request.FILES['file_second']
        output_file = generate_unique_filename()

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        try:
            file_first_path = os.path.join(temp_dir, file_first.name)
            file_second_path = os.path.join(temp_dir, file_second.name)

            # Save the uploaded files to the temporary directory
            with open(file_first_path, 'wb') as f:
                for chunk in file_first.chunks():
                    f.write(chunk)

            with open(file_second_path, 'wb') as f:
                for chunk in file_second.chunks():
                    f.write(chunk)

            result = magic(file_first_path, file_second_path, output_file)
            
            if result == 1:
                return redirect('success', output_file=output_file)
            else:
                return render(request, 'error.html')

        finally:
            # Remove the temporary directory and its contents
            shutil.rmtree(temp_dir)

    return render(request, 'upload.html')


def success(request, output_file):
    file_path = os.path.join(settings.MEDIA_ROOT, output_file)

    # Set the appropriate content type and headers for the file
    content_type, _ = mimetypes.guess_type(file_path)
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{output_file}"'

    with open(file_path, 'rb') as file:
        response.write(file.read())

    # Delete the temporary file after sending the response
    os.remove(file_path)

    return response


