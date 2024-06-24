from io import BytesIO

import pandas as pd

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from skeleton.capacitance import get_capacitance_data_list
from skeleton.settings import FILES_STORAGE

from .models import UserFile

def index(request):
    return render(request, 'skeleton/index.html')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':

        capacitances = []

        files = request.FILES.getlist('files')
        cycle_type = request.POST.get('cycle_type')
        current_threshold = request.POST.get('current_threshold')

        # error handling for incorrect current threshold
        try:
            current_threshold = float(current_threshold)
        except ValueError:
            current_threshold = 0.0

        for file in files:

            fs = FileSystemStorage(location=FILES_STORAGE)
            file_name = fs.save(file.name, file)

            user_file_instance = UserFile.objects.create(file_path=FILES_STORAGE + file_name, file_name=file_name)

            file_cycles = get_capacitance_data_list(file_name, cycle_type, current_threshold)
            capacitances.extend(file_cycles)

        result = pd.DataFrame(capacitances, columns=["file_name", "capacitance", "current"])

        # Saving resul file in buffer and sending it baack to the client
        buffer = BytesIO()
        result.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


        response['Content-Disposition'] = 'attachment; filename={}_{}A.xlsx'.format(cycle_type, round(current_threshold))

        return response

    return JsonResponse({'error': 'Invalid request'}, status=400)
