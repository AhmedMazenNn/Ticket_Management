import type { TicketPriority, TicketStatus } from '$lib/types/ticket';

export const TICKET_PRIORITIES: { value: TicketPriority; label: string }[] = [
	{ value: 'LOW', label: 'Low' },
	{ value: 'MEDIUM', label: 'Medium' },
	{ value: 'HIGH', label: 'High' }
];

export const TICKET_STATUSES: { value: TicketStatus; label: string }[] = [
	{ value: 'OPEN', label: 'Open' },
	{ value: 'IN_PROGRESS', label: 'In Progress' },
	{ value: 'CLOSED', label: 'Closed' }
];

export const PRIORITY_COLORS: Record<TicketPriority, string> = {
	LOW: 'bg-slate-100 text-slate-600 ring-1 ring-slate-200/60',
	MEDIUM: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200/60',
	HIGH: 'bg-rose-50 text-rose-700 ring-1 ring-rose-200/60'
};

export const STATUS_COLORS: Record<TicketStatus, string> = {
	OPEN: 'bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200/60',
	IN_PROGRESS: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200/60',
	CLOSED: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200/60'
};
