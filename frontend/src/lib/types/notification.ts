export interface NotificationTicket {
	id: string;
	title: string;
	priority: string;
	status: string;
	assigned_to: { id: string; first_name: string; last_name: string; email: string } | null;
	created_by: { id: string; first_name: string; last_name: string; email: string };
	created_at: string;
	updated_at: string;
}

export interface Notification {
	id: string;
	ticket: NotificationTicket;
	type: NotificationType;
	is_read: boolean;
	created_at: string;
}

export type NotificationType =
	'TICKET_ASSIGNED' | 'STATUS_CHANGED' | 'PRIORITY_CHANGED' | 'TICKET_UPDATED' | 'COMMENT_ADDED';

export const NOTIFICATION_LABELS: Record<NotificationType, string> = {
	TICKET_ASSIGNED: 'Ticket assigned to you',
	STATUS_CHANGED: 'Ticket status changed',
	PRIORITY_CHANGED: 'Ticket priority changed',
	TICKET_UPDATED: 'Ticket updated',
	COMMENT_ADDED: 'New comment on ticket'
};
