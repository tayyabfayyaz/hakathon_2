"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import { Calendar as CalendarIcon, Clock, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface DeadlinePickerProps {
  deadline: Date | null;
  onDeadlineChange: (deadline: Date | null) => void;
  disabled?: boolean;
  className?: string;
}

export function DeadlinePicker({
  deadline,
  onDeadlineChange,
  disabled = false,
  className,
}: DeadlinePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(
    deadline ?? undefined
  );
  const [timeValue, setTimeValue] = useState(
    deadline ? format(deadline, "HH:mm") : "12:00"
  );

  // Sync internal state when deadline prop changes
  useEffect(() => {
    setSelectedDate(deadline ?? undefined);
    setTimeValue(deadline ? format(deadline, "HH:mm") : "12:00");
  }, [deadline]);

  const handleDateSelect = (date: Date | undefined) => {
    if (!date) return;
    setSelectedDate(date);
  };

  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTimeValue(e.target.value);
  };

  const handleApply = () => {
    if (selectedDate) {
      const [hours, minutes] = timeValue.split(":").map(Number);
      const newDeadline = new Date(selectedDate);
      newDeadline.setHours(hours, minutes, 0, 0);
      onDeadlineChange(newDeadline);
    }
    setIsOpen(false);
  };

  const handleClear = () => {
    setSelectedDate(undefined);
    setTimeValue("12:00");
    onDeadlineChange(null);
    setIsOpen(false);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          disabled={disabled}
          className={cn(
            "justify-start text-left font-normal",
            !deadline && "text-muted-foreground",
            className
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {deadline ? format(deadline, "MMM d, yyyy h:mm a") : "Set deadline"}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-3 space-y-3">
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={handleDateSelect}
            disabled={(date) => date < new Date(new Date().setHours(0, 0, 0, 0))}
            initialFocus
          />
          <div className="flex items-center gap-2 px-3">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <Input
              type="time"
              value={timeValue}
              onChange={handleTimeChange}
              className="flex-1"
            />
          </div>
          <div className="flex justify-between px-3 pb-2">
            <Button variant="ghost" size="sm" onClick={handleClear}>
              <X className="mr-1 h-4 w-4" />
              Clear
            </Button>
            <Button size="sm" onClick={handleApply} disabled={!selectedDate}>
              Apply
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

// Compact deadline badge for displaying in task items
interface DeadlineBadgeProps {
  deadline: string | null;
  onClick?: () => void;
  className?: string;
}

export function DeadlineBadge({ deadline, onClick, className }: DeadlineBadgeProps) {
  if (!deadline) return null;

  let deadlineDate: Date;
  try {
    deadlineDate = new Date(deadline);
    // Check if date is valid
    if (isNaN(deadlineDate.getTime())) {
      console.warn("Invalid deadline date:", deadline);
      return null;
    }
  } catch (e) {
    console.warn("Failed to parse deadline:", deadline, e);
    return null;
  }

  const now = new Date();
  const isOverdue = deadlineDate < now;
  const isToday = deadlineDate.toDateString() === now.toDateString();
  const isTomorrow =
    deadlineDate.toDateString() ===
    new Date(now.getTime() + 86400000).toDateString();

  let label: string;
  if (isToday) {
    label = `Today ${format(deadlineDate, "h:mm a")}`;
  } else if (isTomorrow) {
    label = `Tomorrow ${format(deadlineDate, "h:mm a")}`;
  } else {
    label = format(deadlineDate, "MMM d, h:mm a");
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors border",
        isOverdue
          ? "bg-red-50 text-red-700 border-red-200 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-900/30"
          : isToday
          ? "bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800 dark:hover:bg-orange-900/30"
          : "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800 dark:hover:bg-blue-900/30",
        className
      )}
    >
      <CalendarIcon className="h-3.5 w-3.5" />
      <span>{label}</span>
    </button>
  );
}
