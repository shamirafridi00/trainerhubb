import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface AvailabilitySlot {
  date: string;
  start_time: string;
  end_time: string;
  is_available: boolean;
}

interface AvailabilityCalendarProps {
  trainerSlug: string;
  onSelectDateTime: (date: string, time: string) => void;
}

export function AvailabilityCalendar({ trainerSlug, onSelectDateTime }: AvailabilityCalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [availableSlots, setAvailableSlots] = useState<AvailabilitySlot[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const daysInMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth() + 1,
    0
  ).getDate();

  const firstDayOfMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth(),
    1
  ).getDay();

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const handleDateClick = (day: number) => {
    const selected = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
    const dateStr = selected.toISOString().split('T')[0];
    setSelectedDate(dateStr);
    fetchAvailableSlots(dateStr);
  };

  const fetchAvailableSlots = async (date: string) => {
    setIsLoading(true);
    try {
      // TODO: Implement actual API call to get availability
      // For now, generate mock slots
      const mockSlots: AvailabilitySlot[] = [
        { date, start_time: '09:00', end_time: '10:00', is_available: true },
        { date, start_time: '10:00', end_time: '11:00', is_available: true },
        { date, start_time: '11:00', end_time: '12:00', is_available: false },
        { date, start_time: '14:00', end_time: '15:00', is_available: true },
        { date, start_time: '15:00', end_time: '16:00', is_available: true },
        { date, start_time: '16:00', end_time: '17:00', is_available: true },
      ];
      setAvailableSlots(mockSlots);
    } catch (error) {
      console.error('Failed to fetch availability:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderCalendarDays = () => {
    const days = [];
    const totalSlots = firstDayOfMonth + daysInMonth;
    const rows = Math.ceil(totalSlots / 7);

    for (let i = 0; i < rows * 7; i++) {
      const dayNumber = i - firstDayOfMonth + 1;
      
      if (i < firstDayOfMonth || dayNumber > daysInMonth) {
        days.push(
          <div key={i} className="p-2 text-center text-gray-300">
            {/* Empty cell */}
          </div>
        );
      } else {
        const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), dayNumber);
        const dateStr = date.toISOString().split('T')[0];
        const isSelected = selectedDate === dateStr;
        const isPast = date < new Date(new Date().setHours(0, 0, 0, 0));

        days.push(
          <button
            key={i}
            onClick={() => !isPast && handleDateClick(dayNumber)}
            disabled={isPast}
            className={`p-2 text-center rounded-lg transition-colors ${
              isPast
                ? 'text-gray-300 cursor-not-allowed'
                : isSelected
                ? 'bg-blue-500 text-white'
                : 'hover:bg-gray-100 text-gray-800'
            }`}
          >
            {dayNumber}
          </button>
        );
      }
    }

    return days;
  };

  return (
    <div className="space-y-6">
      {/* Calendar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-4">
          <Button variant="ghost" size="sm" onClick={previousMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <h3 className="text-lg font-semibold">
            {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
          </h3>
          <Button variant="ghost" size="sm" onClick={nextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-2">
          {days.map((day) => (
            <div key={day} className="p-2 text-center text-sm font-medium text-gray-600">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {renderCalendarDays()}
        </div>
      </div>

      {/* Available Time Slots */}
      {selectedDate && (
        <div className="bg-white rounded-lg shadow p-4">
          <h4 className="font-semibold mb-4 flex items-center gap-2">
            <CalendarIcon className="h-5 w-5" />
            Available Times for {selectedDate}
          </h4>
          {isLoading ? (
            <p className="text-center text-gray-500">Loading slots...</p>
          ) : availableSlots.length === 0 ? (
            <p className="text-center text-gray-500">No available slots for this date</p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {availableSlots.map((slot, index) => (
                <button
                  key={index}
                  onClick={() => slot.is_available && onSelectDateTime(slot.date, slot.start_time)}
                  disabled={!slot.is_available}
                  className={`p-3 rounded-lg border-2 transition-colors ${
                    slot.is_available
                      ? 'border-blue-500 hover:bg-blue-50 text-blue-700 font-medium'
                      : 'border-gray-200 text-gray-400 cursor-not-allowed bg-gray-50'
                  }`}
                >
                  {slot.start_time} - {slot.end_time}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

