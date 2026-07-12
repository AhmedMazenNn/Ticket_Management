export type TicketPriority = 'LOW' | 'MEDIUM' | 'HIGH';

export type TicketStatus = 'OPEN' | 'IN_PROGRESS' | 'CLOSED';

export interface TicketUser {
	id: string;
	first_name: string;
	last_name: string;
	email: string;
}

export interface Ticket {
	id: string;
	title: string;
	description: string;
	priority: TicketPriority;
	status: TicketStatus;
	assigned_to: TicketUser | null;
	created_by: TicketUser;
	created_at: string;
	updated_at: string;
}

export interface CreateTicketPayload {
	title: string;
	description?: string;
	priority?: TicketPriority;
	status?: TicketStatus;
	assigned_to?: string | null;
}

export interface PaginatedResponse<T> {
	count: number;
	next: string | null;
	previous: string | null;
	results: T[];
}

export interface TicketListParams {
	page?: number;
	search?: string;
	status?: string;
	priority?: string;
	assigned_to?: string;
	created_by?: string;
	ordering?: string;
}
