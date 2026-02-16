// Calendar export utilities for generating .ics files

export interface CalendarEvent {
  id: string;
  summary: string;
  description?: string;
  startDate: Date;
  endDate?: Date;
  location?: string;
  participants?: string[];
}

export const generateICSFile = (events: CalendarEvent[]): string => {
  const icsEvents = events.map(event => {
    const startDate = formatICSDate(event.startDate);
    const endDate = event.endDate ? formatICSDate(event.endDate) : formatICSDate(new Date(event.startDate.getTime() + 3600000)); // +1 hour default
    
    const description = event.description || event.summary;
    const attendees = event.participants?.map(p => `ATTENDEE:CN=${p}:MAILTO:${p.toLowerCase().replace(/\s/g, '')}@example.com`).join('\r\n') || '';
    
    return `BEGIN:VEVENT
UID:${event.id}@collaboration-tracker
DTSTAMP:${formatICSDate(new Date())}
DTSTART:${startDate}
DTEND:${endDate}
SUMMARY:${escapeICSText(event.summary)}
DESCRIPTION:${escapeICSText(description)}
${attendees ? attendees + '\r\n' : ''}STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT`;
  }).join('\r\n');

  return `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Collaboration Tracker//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
${icsEvents}
END:VCALENDAR`;
};

const formatICSDate = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  
  return `${year}${month}${day}T${hours}${minutes}${seconds}`;
};

const escapeICSText = (text: string): string => {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n');
};

export const downloadICS = (icsContent: string, filename: string = 'events.ics') => {
  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(link.href);
};
