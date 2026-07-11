import type { User } from './user';

export interface LoginPayload {
	email: string;
	password: string;
}

export interface LoginResponse {
	access: string;
	refresh: string;
	user: User;
}

export interface RegisterPayload {
	email: string;
	password: string;
	first_name?: string;
	last_name?: string;
}

export interface RefreshResponse {
	access: string;
}
