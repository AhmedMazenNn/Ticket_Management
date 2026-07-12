export type UserRole = 'ADMIN' | 'MANAGER' | 'AGENT';

export interface User {
	id: string;
	first_name: string;
	last_name: string;
	email: string;
	role: UserRole;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}
