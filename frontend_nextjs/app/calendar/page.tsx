'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { HolographicCard } from '@/components/cyberpunk/HolographicCard';
import { ScrollReveal } from '@/components/cyberpunk/ScrollReveal';
import { NeonText } from '@/components/cyberpunk/NeonText';
import { NeonButton } from '@/components/cyberpunk/NeonButton';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAPI, useAPIMutation } from '@/lib/hooks/useAPI';
import { calendarAPI } from '@/lib/api';
import { Sidebar } from '@/components/Sidebar';
import { Plus, Calendar, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';
import { fadeInUp } from '@/lib/hooks/useAnimation';
import { Dialog } from '@/components/ui/drawer';
import { Input, Textarea } from '@/components/ui/input';
import { toast } from 'react-hot-toast';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';

interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end?: string;
  allDay?: boolean;
  description?: string;
  ai_suggested?: boolean;
  urgency_score?: number;
  color?: string;
}

export default function CalendarPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [isCreatingEvent, setIsCreatingEvent] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [view, setView] = useState<'dayGridMonth' | 'timeGridWeek' | 'timeGridDay'>('dayGridMonth');

  const { data: events, isLoading, refetch } = useAPI(
    ['calendar', 'events'],
    () => calendarAPI.listEvents(),
    { enabled: isAuthenticated }
  );

  const createEventMutation = useAPIMutation(
    (event: { title: string; start: string; end: string; allDay?: boolean; description?: string }) => calendarAPI.createEvent(event),
    {
      onSuccess: () => {
        toast.success('Event created successfully');
        setIsCreatingEvent(false);
        refetch();
      },
      onError: () => {
        toast.error('Failed to create event');
      },
    }
  );

  const deleteEventMutation = useAPIMutation(
    (id: string) => calendarAPI.deleteEvent(id),
    {
      onSuccess: () => {
        toast.success('Event deleted');
        setSelectedEvent(null);
        refetch();
      },
    }
  );

  const calendarEvents = useMemo(() => {
    // calendarAPI.listEvents already returns transformed events
    const eventList = Array.isArray(events) ? events : [];
    return eventList.map((event: any) => ({
      id: String(event.id),
      title: event.title,
      start: event.start,
      end: event.end || event.start,
      allDay: event.allDay || false,
      backgroundColor: event.ai_suggested ? '#FF00FF' : '#00FFFF',
      borderColor: event.ai_suggested ? '#FF00FF' : '#00FFFF',
      textColor: '#1A0033',
      extendedProps: {
        description: event.description,
        ai_suggested: event.ai_suggested,
        urgency_score: event.urgency_score,
      },
    }));
  }, [events]);

  const handleDateSelect = (selectInfo: any) => {
    setIsCreatingEvent(true);
    setSelectedEvent({
      id: '',
      title: '',
      start: selectInfo.startStr,
      end: selectInfo.endStr,
      allDay: selectInfo.allDay,
    });
  };

  const handleEventClick = (clickInfo: any) => {
    const event = clickInfo.event;
    setSelectedEvent({
      id: event.id,
      title: event.title,
      start: event.startStr,
      end: event.endStr,
      allDay: event.allDay,
      description: event.extendedProps.description,
      ai_suggested: event.extendedProps.ai_suggested,
      urgency_score: event.extendedProps.urgency_score,
    });
  };

  const handleEventDrop = async (dropInfo: any) => {
    const event = dropInfo.event;
    try {
      await calendarAPI.updateEvent(event.id, {
        start: event.startStr,
        end: event.endStr,
      });
      toast.success('Event moved');
      refetch();
    } catch (error) {
      toast.error('Failed to move event');
      dropInfo.revert();
    }
  };

  const handleEventResize = async (resizeInfo: any) => {
    const event = resizeInfo.event;
    try {
      await calendarAPI.updateEvent(event.id, {
        start: event.startStr,
        end: event.endStr,
      });
      toast.success('Event resized');
      refetch();
    } catch (error) {
      toast.error('Failed to resize event');
      resizeInfo.revert();
    }
  };

  const handleCreateEvent = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const title = formData.get('title') as string;
    const description = formData.get('description') as string;

    if (!title || !selectedEvent?.start || !selectedEvent?.end) {
      toast.error('Title, start, and end are required');
      return;
    }

    createEventMutation.mutate({
      title,
      description,
      start: selectedEvent.start,
      end: selectedEvent.end,
      allDay: selectedEvent.allDay,
    });
  };

  const aiSuggestedEvents = useMemo(() => {
    return calendarEvents.filter((event: any) => event.extendedProps.ai_suggested);
  }, [calendarEvents]);

  if (!isAuthenticated) {
    router.push('/');
    return null;
  }

  return (
    <div className="flex min-h-screen bg-dark-bg">
      <Sidebar />
      <div className="flex-1 md:ml-64 p-4 md:p-8">
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-orbitron font-bold text-transparent bg-clip-text bg-gradient-neon mb-2">
                Calendar
              </h1>
              <p className="text-gray-400">AI-powered calendar management</p>
            </div>
            <div className="flex gap-2">
              <Button
                variant={view === 'dayGridMonth' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setView('dayGridMonth')}
              >
                Month
              </Button>
              <Button
                variant={view === 'timeGridWeek' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setView('timeGridWeek')}
              >
                Week
              </Button>
              <Button
                variant={view === 'timeGridDay' ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setView('timeGridDay')}
              >
                Day
              </Button>
              <Button variant="primary" onClick={() => setIsCreatingEvent(true)}>
                <Plus className="w-4 h-4 mr-2" />
                New Event
              </Button>
            </div>
          </div>

          {/* AI Suggestions */}
          {aiSuggestedEvents.length > 0 && (
            <HolographicCard glowColor="pink" className="p-4 bg-neon-pink/10 border-neon-pink/50">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-neon-pink" />
                <h3 className="text-lg font-orbitron text-neon-pink">AI Suggestions</h3>
                <Badge variant="info">{aiSuggestedEvents.length}</Badge>
              </div>
              <div className="flex flex-wrap gap-2">
                {aiSuggestedEvents.slice(0, 5).map((event: any) => (
                  <motion.div
                    key={event.id}
                    whileHover={{ scale: 1.05 }}
                    onClick={() => handleEventClick({ event })}
                  >
                    <Badge
                      variant="info"
                      className="cursor-pointer hover:bg-neon-pink/30"
                    >
                      {event.title}
                    </Badge>
                  </motion.div>
                ))}
              </div>
            </Card>
          )}

          {/* Calendar */}
          <HolographicCard glowColor="blue" className="p-6">
            <style jsx global>{`
              .fc {
                --fc-border-color: rgba(0, 255, 255, 0.2);
                --fc-today-bg-color: rgba(0, 255, 255, 0.1);
                --fc-neutral-bg-color: #1A0033;
                --fc-page-bg-color: #1A0033;
                --fc-event-bg-color: #00FFFF;
                --fc-event-border-color: #00FFFF;
                --fc-event-text-color: #1A0033;
                --fc-button-bg-color: rgba(0, 255, 255, 0.1);
                --fc-button-border-color: #00FFFF;
                --fc-button-text-color: #00FFFF;
                --fc-button-hover-bg-color: rgba(0, 255, 255, 0.2);
                --fc-button-hover-border-color: #00FFFF;
                --fc-button-active-bg-color: rgba(0, 255, 255, 0.3);
                --fc-button-active-border-color: #00FFFF;
                font-family: var(--font-inter), sans-serif;
              }
              .fc-header-toolbar {
                margin-bottom: 1.5rem;
              }
              .fc-toolbar-title {
                font-family: var(--font-orbitron), sans-serif;
                font-weight: bold;
                color: #00FFFF;
              }
              .fc-button {
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                font-weight: 500;
                transition: all 0.3s;
              }
              .fc-button:hover {
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
              }
              .fc-event {
                border-radius: 0.25rem;
                padding: 0.25rem;
                cursor: pointer;
                transition: all 0.2s;
              }
              .fc-event:hover {
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
                transform: scale(1.05);
              }
              .fc-daygrid-day {
                background-color: rgba(0, 255, 255, 0.05);
              }
              .fc-daygrid-day:hover {
                background-color: rgba(0, 255, 255, 0.1);
              }
              .fc-col-header-cell {
                background-color: rgba(0, 255, 255, 0.1);
                color: #00FFFF;
                font-weight: bold;
                padding: 0.75rem;
              }
              .fc-timegrid-slot {
                background-color: rgba(0, 255, 255, 0.02);
              }
              .fc-timegrid-slot:hover {
                background-color: rgba(0, 255, 255, 0.05);
              }
            `}</style>
            <FullCalendar
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              initialView={view}
              headerToolbar={{
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay',
              }}
              events={calendarEvents}
              editable={true}
              selectable={true}
              selectMirror={true}
              dayMaxEvents={true}
              weekends={true}
              select={handleDateSelect}
              eventClick={handleEventClick}
              eventDrop={handleEventDrop}
              eventResize={handleEventResize}
              height="auto"
              contentHeight="auto"
            />
          </Card>

          {/* Create Event Dialog */}
          <Dialog
            isOpen={isCreatingEvent}
            onClose={() => setIsCreatingEvent(false)}
            title="Create New Event"
            size="md"
          >
            <form onSubmit={handleCreateEvent} className="space-y-4">
              <Input
                name="title"
                label="Title"
                placeholder="Event title"
                required
              />
              <Textarea
                name="description"
                label="Description"
                placeholder="Event description"
              />
              <div className="flex gap-2 justify-end">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsCreatingEvent(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary">
                  Create Event
                </Button>
              </div>
            </form>
          </Dialog>

          {/* Event Details Dialog */}
          <Dialog
            isOpen={!!selectedEvent && !isCreatingEvent}
            onClose={() => setSelectedEvent(null)}
            title={selectedEvent?.title || 'Event Details'}
            size="md"
          >
            {selectedEvent && (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Start</p>
                  <p className="text-white">
                    {new Date(selectedEvent.start).toLocaleString()}
                  </p>
                </div>
                {selectedEvent.end && (
                  <div>
                    <p className="text-sm text-gray-400 mb-1">End</p>
                    <p className="text-white">
                      {new Date(selectedEvent.end).toLocaleString()}
                    </p>
                  </div>
                )}
                {selectedEvent.description && (
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Description</p>
                    <p className="text-white">{selectedEvent.description}</p>
                  </div>
                )}
                {selectedEvent.ai_suggested && (
                  <Badge variant="info">
                    <Sparkles className="w-3 h-3 mr-1" />
                    AI Suggested
                  </Badge>
                )}
                {selectedEvent.urgency_score && (
                  <Badge
                    variant={
                      selectedEvent.urgency_score > 70 ? 'error' :
                      selectedEvent.urgency_score > 40 ? 'warning' :
                      'success'
                    }
                  >
                    Urgency: {selectedEvent.urgency_score}%
                  </Badge>
                )}
                <div className="flex gap-2 pt-4 border-t border-neon-cyan/20">
                  <Button
                    variant="secondary"
                    onClick={() => {
                      if (selectedEvent.id) {
                        deleteEventMutation.mutate(selectedEvent.id);
                      }
                    }}
                  >
                    Delete
                  </Button>
                  <Button variant="primary" onClick={() => setSelectedEvent(null)}>
                    Close
                  </Button>
                </div>
              </div>
            )}
          </Dialog>
        </motion.div>
      </div>
    </div>
  );
}
