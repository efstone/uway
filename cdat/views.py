import csv
from django.http import HttpResponse
from django.shortcuts import render
import xlrd
from cdat.models import *
from django.contrib.auth.decorators import login_required
import pytz
dallas_time = pytz.timezone('America/Chicago')
from django.db import connection

# Create your views here.

@login_required(login_url='/admin/login/')
def ingest_sheets(request):
    with connection.cursor() as c:
        c.execute("BEGIN TRANSACTION;")
        c.execute("DELETE FROM cdat_clientraw;")
        c.execute("DELETE FROM cdat_client;")
        c.execute("DELETE FROM cdat_home;")
        c.execute("COMMIT;")
    sheet_files = SheetUpload.objects.last()
    vispdat_file = sheet_files.vispdat_file.file
    fvispdat_file = sheet_files.fvispdat_file.file
    psh_file = sheet_files.psh_file.file
    rrh_file = sheet_files.rrh_file.file
    vispdat_book = xlrd.open_workbook(file_contents=vispdat_file.read())
    vispdat_sheet = vispdat_book.sheet_by_index(0)
    fvispdat_book = xlrd.open_workbook(file_contents=fvispdat_file.read())
    fvispdat_sheet = fvispdat_book.sheet_by_index(0)
    psh_book = xlrd.open_workbook(file_contents=psh_file.read())
    psh_sheet = psh_book.sheet_by_index(0)
    rrh_book = xlrd.open_workbook(file_contents=rrh_file.read())
    rrh_sheet = rrh_book.sheet_by_index(0)

    for row_num in range(1, vispdat_sheet.nrows):
        print(vispdat_sheet.nrows)
        new_client = ClientRaw()
        new_client.uw_client_id = int(vispdat_sheet.col(2)[row_num].value)
        new_client.assessment_date = dallas_time.localize(xlrd.xldate_as_datetime(vispdat_sheet.col(8)[row_num].value, 0))
        new_client.assessing_organization = vispdat_sheet.col(9)[row_num].value
        new_client.assessment_score = int(vispdat_sheet.col(17)[row_num].value)
        new_client.individual_or_family = 'Individual'
        new_client.save()

    for row_num in range(1, fvispdat_sheet.nrows):
        print(fvispdat_sheet.nrows)
        new_client = ClientRaw()
        new_client.uw_client_id = int(fvispdat_sheet.col(2)[row_num].value)
        new_client.assessment_date = dallas_time.localize(xlrd.xldate_as_datetime(fvispdat_sheet.col(8)[row_num].value, 0))
        new_client.assessing_organization = fvispdat_sheet.col(9)[row_num].value
        new_client.assessment_score = int(fvispdat_sheet.col(17)[row_num].value)
        new_client.individual_or_family = 'Family'
        new_client.save()

    for row_num in range(1, psh_sheet.nrows):
        home_entry = Home()
        home_entry.uw_client_id = int(psh_sheet.col(0)[row_num].value)
        if psh_sheet.col(27)[row_num].value != '':
            home_entry.ces_code = int(float(psh_sheet.col(27)[row_num].value))
        home_entry.source = 'PSH'
        home_entry.save()

    for row_num in range(1, rrh_sheet.nrows):
        home_entry = Home()
        home_entry.uw_client_id = int(rrh_sheet.col(0)[row_num].value)
        if rrh_sheet.col(27)[row_num].value != '':
            home_entry.ces_code = int(float(rrh_sheet.col(27)[row_num].value))
        home_entry.source = 'RRH'
        home_entry.save()
    content = {'message': 'Data processed successfully.'}

    with connection.cursor() as c:
        c.execute("INSERT INTO cdat_client (uw_client_id, assessment_date, assessing_organization, assessment_score, individual_or_family) SELECT MAX(uw_client_id), MAX(assessment_date), assessing_organization, assessment_score, individual_or_family FROM cdat_clientraw GROUP BY uw_client_id, assessing_organization, assessment_score, individual_or_family;")
    with connection.cursor() as c:
        c.execute("UPDATE cdat_client C SET ce_status_id = ces_code FROM cdat_home H WHERE H.uw_client_id = C.uw_client_id;")

    sheet_files.fvispdat_file.delete()
    sheet_files.vispdat_file.delete()
    sheet_files.psh_file.delete()
    sheet_files.rrh_file.delete()
    sheet_files.save()
    sheet_files.delete()


    return render(request, "base.html", content)


@login_required(login_url='/admin/login/')
def export_duplicates(request):
    with connection.cursor() as c:
        c.execute("SELECT uw_client_id, assessment_date, assessing_organization, assessment_score FROM cdat_clientraw WHERE uw_client_id IN (SELECT uw_client_id FROM cdat_clientraw GROUP BY uw_client_id, assessment_date HAVING COUNT(*) > 1) ORDER BY uw_client_id, assessment_date;")
        duplicate_assessments = c.fetchall()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="duplicates.csv"'
    writer = csv.writer(response, delimiter=',')
    writer.writerow(['client_id', 'assessment_date', 'assessing_org', 'assessment_score'])
    for row in duplicate_assessments:
        writer.writerow([row[0], row[1], row[2], row[3]])
    return response

