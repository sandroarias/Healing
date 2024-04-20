from django.db import transaction
from django.shortcuts import render, redirect
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from datetime import datetime, timedelta
from .models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants


def home(request):
    if request.method == 'GET':
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedico.objects.all()
        # Filtros
        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)
        if especialidades_filtrar:
            medicos = medicos.filter(especialidade__id__in=especialidades_filtrar)
        especialidades = Especialidades.objects.all()
        context = {
            'especialidades': especialidades,
            'medicos': medicos,
            'is_medico': is_medico(request.user)
        }
        return render(request, 'home.html', context)


def escolher_horario(request, id_dados_medicos):
    if request.method == 'GET':
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(
            agendado=False)

        context = {
            'medico': medico,
            'datas_abertas': datas_abertas,
            'is_medico': is_medico(request.user)
        }
        return render(request, 'escolher_horario.html', context)


@transaction.atomic
def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        try:
            data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

            horario_agendado = Consulta(
                paciente=request.user,
                data_abertura=data_aberta
            )

            horario_agendado.save()

            data_aberta.agendado = True
            data_aberta.save()

            messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')

        except DatasAbertas.DoesNotExist:
            messages.add_message(request, constants.ERROR, 'A data aberta não existe.')
            return redirect('pacientes/escolher_horario')
        except Exception as e:
            messages.add_message(request, constants.ERROR, f'Ocorreu um erro ao agendar o horário: {e}')
        return redirect('/pacientes/minhas_consultas/')

def minhas_consultas(request):
    # TODO realizar os filtros
    minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_abertura__data__gte=datetime.now())
    return render(request, 'minhas_consultas.html', {'minhas_consultas':minhas_consultas, 'is_medico':is_medico(request.user)})


def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_abertura.user)
        documentos = Documento.objects.filter(consulta=consulta)
        context = {
            'consulta': consulta,
            'dado_medico': dado_medico,
            'documentos':documentos
        }
        return render(request, 'consulta.html', context)


