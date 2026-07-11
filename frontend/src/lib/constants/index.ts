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
	LOW: 'bg-slate-100 text-slate-700',
	MEDIUM: 'bg-amber-100 text-amber-700',
	HIGH: 'bg-rose-100 text-rose-700'
};

export const STATUS_COLORS: Record<TicketStatus, string> = {
	OPEN: 'bg-blue-100 text-blue-700',
	IN_PROGRESS: 'bg-amber-100 text-amber-700',
	CLOSED: 'bg-emerald-100 text-emerald-700'
};
