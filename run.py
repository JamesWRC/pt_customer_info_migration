import os
import csv
import json

from pyhtml2pdf import converter
import multiprocessing
csv_file = os.getcwd() + '/data.csv'

if not os.path.exists(csv_file):
    print('data.csv file does not exist')
    print('put the CSV file in the same folder as this script and call is "data.csv"')
    exit()

def renderSessionHTML(clientData):
    if clientData is None:
        return ""
    ignoreNotes = ['SerializedContentId']
    
    noteHtml = ""
    if clientData.get('EncryptedNote') is None:
        noteHtml = "<li class='px-4 py-4 sm:px-6'>No notes</li>"
    else:
        for key, value in clientData.get('EncryptedNote').items():
            if key in ignoreNotes:
                continue

            noteHtml += f"""
        <div class="border-t border-gray-100 px-4 py-6 sm:col-span-2 sm:px-0">
            <dt class="text-sm font-medium leading-6 text-gray-900">{key}</dt>
            <dd class="mt-1 text-sm leading-6 text-gray-700 sm:mt-2">{value}</dd>
        </div>
        """
    html = f"""
    <!-- This example requires Tailwind CSS v2.0+ -->
    <div class="p-10">
        <div class="px-4 sm:px-0">
          <h3 class="text-base font-semibold leading-7 text-gray-900">{clientData.get('FirstName')} - {clientData.get('LastName')}</h3>
          <p class="mt-1 max-w-2xl text-sm leading-6 text-gray-500">Session Date: {clientData.get('TreatmentDateTime')}</p>
        </div>
        <div class="mt-6 border-t border-gray-100">
          <dl class="divide-y divide-gray-100">
            <div class="bg-gray-50 px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-3">
              <dt class="text-sm font-medium leading-6 text-gray-900">Full name/dt>
              <dd class="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{clientData.get('FirstName')}</dd>
            </div>
            <div class="bg-white px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-3">
              <dt class="text-sm font-medium leading-6 text-gray-900">Last name</dt>
              <dd class="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{clientData.get('LastName')}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-3">
              <dt class="text-sm font-medium leading-6 text-gray-900">Trainer</dt>
              <dd class="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{clientData.get('TrFirstName')} {clientData.get('TrLastName')}</dd>
            </div>
            <div class="bg-white px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-3">
              <dt class="text-sm font-medium leading-6 text-gray-900">Treatment Date / time</dt>
              <dd class="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{clientData.get('TreatmentDateTime')}</dd>
            </div>
            <div class="bg-gray-50 px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-3">
              <dt class="text-sm font-medium leading-6 text-gray-900">Visit Type</dt>
              <dd class="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{clientData.get('VisitType')}</dd>
            </div>
            
            <div class="bg-white px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-3">
              <dt class="text-sm font-medium leading-6 text-gray-900">Notes</dt>
              <dd class="mt-2 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                <ul role="list" class="divide-y divide-gray-100 rounded-md border border-gray-200">
                  {noteHtml}
                </ul>
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- line break -->
        <div class="relative">
            <div class="absolute inset-0 flex items-center" aria-hidden="true">
                <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center">
                <span class="bg-white px-2 text-gray-500">
                <svg class="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
                </svg>
                </span>
            </div>
        </div>
        <!-- // line break -->

    """
    return html

def renderPDFHTML(clientData):
    htmlContent = ""
    for clientSessions in clientData:
        htmlContent+=renderSessionHTML(clientSessions)
    html = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="tailwind.css" rel="stylesheet">
            <script src="https://cdn.tailwindcss.com"></script>
            <title>PDF Test</title>
        </head>
        <body>
            {htmlContent}
        </body>
    </html>
    """
    return html


def htmlToPDFWorker(work):
    htmlFilePath, pdfFilePath = work

    # delete pdfFilePath if exists
    if os.path.exists(pdfFilePath):
        os.remove(pdfFilePath)
    else:
        os.makedirs(os.path.dirname(pdfFilePath), exist_ok=True)
                
    try:
        converter.convert(htmlFilePath, pdfFilePath, timeout=2)
    except KeyboardInterrupt:
            print('Keyboard interrupt')
            exit()

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    uniqueClient = dict()

    print('Parsing CSV...')
    with open(csv_file, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', dialect=csv.excel_tab)
        next(csv_reader) # skip header

        # Get line and line index from csv_reader
        for lineIndex, line in enumerate(csv_reader):
            # Get headings
            
            if len(line) > 0:
                data = line
                MBSystemIDData = data[0]
                BarcodeIDData = data[1]
                ProgressNoteIdData = data[2]
                FirstNameData = data[3]
                LastNameData = data[4]
                TrFirstNameData = data[5]
                TrLastNameData = data[6]
                TreatmentDateTimeData = data[7]
                VisitTypeData = data[8]
                EncryptedNoteData = data[9]
                TrainerData = data[10]

                # Check if client is unique
                if MBSystemIDData not in uniqueClient:
                    uniqueClient[BarcodeIDData] = list()

                sessionData = dict()
                sessionData['MBSystemID'] = MBSystemIDData
                sessionData['BarcodeID'] = BarcodeIDData
                sessionData['ProgressNoteId'] = ProgressNoteIdData
                sessionData['FirstName'] = FirstNameData
                sessionData['LastName'] = LastNameData
                sessionData['TrFirstName'] = TrFirstNameData
                sessionData['TrLastName'] = TrLastNameData
                sessionData['TreatmentDateTime'] = TreatmentDateTimeData
                sessionData['VisitType'] = VisitTypeData

                if EncryptedNoteData:
                    sessionData['EncryptedNote'] = json.loads(EncryptedNoteData)

                sessionData['Trainer'] = TrainerData
                uniqueClient[BarcodeIDData].append(sessionData)

                    
                ## Debug
                # print(line)
        
        # Save json if needed
        with open('data.json', 'w') as outfile:
            json.dump(uniqueClient, outfile)

        htmlFiles = []

        print('Rendering html...')
        for key in uniqueClient:
            if uniqueClient[key] is None:
                continue

            html = renderPDFHTML(uniqueClient[key])

            fileName = f"{uniqueClient[key][0].get('FirstName')}_{uniqueClient[key][0].get('LastName')}"

            htmlFilePath = os.path.join(os.getcwd(), 'html', key, fileName + '.html')

            # delete htmlFilePath if exists
            if os.path.exists(htmlFilePath):
                os.remove(htmlFilePath)
            else:
                os.makedirs(os.path.dirname(htmlFilePath), exist_ok=True)

            # write file
            with open(htmlFilePath, 'w') as f:
                f.write(html)

            htmlFiles.append(htmlFilePath)
        # Convert HTML to PDF
        print('Converting HTML to pdf...')
        try:
            # with multiprocessing.Pool(2) as pool:


                work = list()
                for index, htmlFilePath in enumerate(htmlFiles):
                    print(f'Converting {index+1} of {len(htmlFiles)}')

                    pdfFilePath = htmlFilePath.replace('html', 'pdf')
                    htmlToPDFWorker((htmlFilePath, pdfFilePath))
                    # work.append((f'file:///{htmlFilePath}', htmlFilePath.replace('html', 'pdf')))

                # pool.map(htmlToPDFWorker, work)
        except KeyboardInterrupt:
            print('Keyboard interrupt')
            exit()