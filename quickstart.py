from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from copy import deepcopy

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'uitgvekbmuhdaukhqfum9vibs0@group.calendar.google.com'

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    starttime = datetime.date.today()
    workshift = crear_eventos_por_ciclo(EVENTOS, starttime)

    # No quiero repetir eventos, por lo tanto elimino los eventos que hay
    # actualmente en el calendario (que debe ser solo de workshifts) 

    eliminar_eventos(service, CALENDAR_ID)
    for shift in workshift:
        event = service.events().insert(calendarId=CALENDAR_ID, body=shift).execute()
        print('Event created: {0}'.format(event.get('htmlLink')))


BASE_EVENT = {
  'summary': 'Appointment',
  'start': {
    'date': '2011-06-03'
  },
  'end': {
    'date': '2011-06-03'
  },
  'recurrence': [
    'RRULE:FREQ=DAILY;INTERVAL=8',
  ]
}

EVENTOS = {
    'Manana': {'dias': 2, 'colorId': 1},
    'Noche': {'dias': 2, 'colorId': 2},
    'Libre': {'dias': 4, 'colorId':3}
}
def crear_eventos_por_ciclo(eventos, starttime):
    """
    Para un ciclo de n dias crea n eventos con los labels apropiados.
    :params eventos: diccionario con eventos: {dias:n}
    :params start_time
    """
    total = 0
    workshift = []
    for evento in eventos:
        for dia in range(eventos[evento]['dias']):
            event = deepcopy(BASE_EVENT)
            event['summary'] = "Turno {0} - Dia {1}".format(evento, dia + 1)
            start = starttime + datetime.timedelta(days=total) + datetime.timedelta(days=dia)
            event['start']['date'] = start.isoformat()
            end = start + datetime.timedelta(days=1)
            event['end']['date'] = end.isoformat()
            event['colorId'] = eventos[evento]['colorId']
            print(str(event))
            workshift.append(event)
        total = total + eventos[evento]['dias']
    return workshift

def eliminar_eventos(service, calendar_id):
    """
    Elimina los eventos del calendario identificado con calendar_id
    """
    page_token = None
    while True:
      events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
      for event in events['items']:
        event_id = event['id']
        print("Eliminando {0} {1}".format(event_id, event['summary']))
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
      page_token = events.get('nextPageToken')
      if not page_token:
        break
if __name__ == '__main__':
    main()
