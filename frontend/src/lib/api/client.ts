import { API_BASE } from '$lib/api/index';
import { auth } from '$lib/stores/auth.svelte';
import type {
	LoginPayload,
	LoginResponse,
	RefreshResponse,
	RegisterPayload
} from '$lib/types/auth';
import type {
	CreateTicketPayload,
	PaginatedResponse,
	Ticket,
	TicketListParams
} from '$lib/types/ticket';
import type { User } from '$lib/types/user';

export class ApiClient {
	private baseUrl = API_BASE;
	private tokenOverride: string | null;
	private refreshing: Promise<string> | null = null;

	constructor(token?: string | null) {
		this.tokenOverride = token ?? null;
	}

	private headers(): Record<string, string> {
		const h: Record<string, string> = { 'Content-Type': 'application/json' };
		const token = this.tokenOverride ?? auth.accessToken;
		if (token) {
			h['Authorization'] = `Bearer ${token}`;
		}
		return h;
	}

	private async doRefresh(): Promise<string> {
		if (this.refreshing) return this.refreshing;
		this.refreshing = (async () => {
			const refresh = auth.refreshToken;
			if (!refresh) throw new Error('No refresh token');
			const res = await fetch(`${this.baseUrl}/auth/refresh/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ refresh })
			});
			if (!res.ok) throw { status: res.status };
			const data: RefreshResponse = await res.json();
			auth.setAccessToken(data.access);
			return data.access;
		})();
		try {
			return await this.refreshing;
		} finally {
			this.refreshing = null;
		}
	}

	private async request<T>(path: string, init?: RequestInit, retried = false): Promise<T> {
		const res = await fetch(`${this.baseUrl}${path}`, {
			...init,
			headers: { ...this.headers(), ...init?.headers }
		});

		if (res.status === 401 && !retried && !this.tokenOverride) {
			try {
				const newToken = await this.doRefresh();
				const updatedHeaders: Record<string, string> = {
					...(this.headers() as Record<string, string>),
					Authorization: `Bearer ${newToken}`
				};
				if (init?.headers) {
					Object.assign(updatedHeaders, init.headers);
				}
				return this.request<T>(path, { ...init, headers: updatedHeaders }, true);
			} catch {
				auth.clear();
				if (typeof window !== 'undefined') {
					window.location.href = '/login';
				}
				throw { status: 401, detail: 'Session expired' };
			}
		}

		if (!res.ok) {
			const body = await res.json().catch(() => ({}));
			throw { status: res.status, ...body };
		}
		if (res.status === 204) return undefined as T;
		return res.json() as Promise<T>;
	}

	private toQueryString(params: Record<string, string | number | undefined>): string {
		const entries = Object.entries(params).filter(
			([, v]) => v !== undefined && v !== '' && v !== null
		);
		if (entries.length === 0) return '';
		return '?' + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString();
	}

	async register(payload: RegisterPayload): Promise<LoginResponse> {
		const data = await this.request<LoginResponse>('/auth/register/', {
			method: 'POST',
			body: JSON.stringify(payload)
		});
		auth.setTokens(data.access, data.refresh);
		auth.setUser(data.user);
		return data;
	}

	async login(payload: LoginPayload): Promise<LoginResponse> {
		const data = await this.request<LoginResponse>('/auth/login/', {
			method: 'POST',
			body: JSON.stringify(payload)
		});
		auth.setTokens(data.access, data.refresh);
		auth.setUser(data.user);
		return data;
	}

	async refreshToken(): Promise<string> {
		return this.doRefresh();
	}

	async logout(): Promise<void> {
		const refresh = auth.refreshToken;
		if (refresh) {
			try {
				await this.request<{ detail: string }>('/auth/logout/', {
					method: 'POST',
					body: JSON.stringify({ refresh })
				});
			} catch {
				// ignore — token may already be invalid
			}
		}
		auth.clear();
	}

	async me(): Promise<User> {
		const data = await this.request<User>('/auth/me/');
		auth.setUser(data);
		return data;
	}

	async updateProfile(payload: Partial<Pick<User, 'first_name' | 'last_name'>>): Promise<User> {
		const data = await this.request<User>('/auth/me/', {
			method: 'PATCH',
			body: JSON.stringify(payload)
		});
		auth.setUser(data);
		return data;
	}

	async listUsers(): Promise<User[]> {
		return this.request<User[]>('/auth/users/');
	}

	async listTickets(params: TicketListParams = {}): Promise<PaginatedResponse<Ticket>> {
		const qs = this.toQueryString(params as Record<string, string | number | undefined>);
		return this.request<PaginatedResponse<Ticket>>(`/tickets/${qs}`);
	}

	async getTicket(id: string): Promise<Ticket> {
		return this.request<Ticket>(`/tickets/${id}/`);
	}

	async createTicket(payload: CreateTicketPayload): Promise<Ticket> {
		return this.request<Ticket>('/tickets/', {
			method: 'POST',
			body: JSON.stringify(payload)
		});
	}

	async updateTicket(id: string, payload: Partial<CreateTicketPayload>): Promise<Ticket> {
		return this.request<Ticket>(`/tickets/${id}/`, {
			method: 'PATCH',
			body: JSON.stringify(payload)
		});
	}

	async deleteTicket(id: string): Promise<void> {
		await this.request<void>(`/tickets/${id}/`, { method: 'DELETE' });
	}

	async getDashboardStats(): Promise<{
		total: number;
		open: number;
		in_progress: number;
		closed: number;
		recent_tickets: Ticket[];
		priority_breakdown: { low: number; medium: number; high: number };
	}> {
		return this.request('/tickets/dashboard_stats/');
	}

	async getMyStats(): Promise<{
		assigned_total: number;
		assigned_open: number;
		assigned_in_progress: number;
		assigned_closed: number;
		created_total: number;
		assigned_tickets: Ticket[];
	}> {
		return this.request('/tickets/my_stats/');
	}
}

export const api = new ApiClient();
