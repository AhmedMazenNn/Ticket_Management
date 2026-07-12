export interface HistoryUser {
	id: string;
	first_name: string;
	last_name: string;
	email: string;
}

export interface TicketHistoryEntry {
	id: string;
	field_name: string;
	old_value: string | null;
	new_value: string | null;
	changed_by: HistoryUser;
	created_at: string;
}
