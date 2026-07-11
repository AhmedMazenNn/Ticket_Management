import { API_BASE } from '$lib/api/index';
import { auth } from '$lib/stores/auth.svelte';
import type {
	LoginPayload,
	LoginResponse,
	RefreshResponse,
	RegisterPayload
} from '$lib/types/auth';
import type { User } from '$lib/types/user';

class ApiClient {
	private baseUrl = API_BASE;

	private headers(): Record<string, string> {
		const h: Record<string, string> = { 'Content-Type': 'application/json' };
		const token = auth.accessToken;
		if (token) {
			h['Authorization'] = `Bearer ${token}`;
		}
		return h;
	}

	private async request<T>(path: string, init?: RequestInit): Promise<T> {
		const res = await fetch(`${this.baseUrl}${path}`, {
			...init,
			headers: { ...this.headers(), ...init?.headers }
		});
		if (!res.ok) {
			const body = await res.json().catch(() => ({}));
			throw { status: res.status, ...body };
		}
		return res.json() as Promise<T>;
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
		const refresh = auth.refreshToken;
		if (!refresh) throw new Error('No refresh token');
		const data = await this.request<RefreshResponse>('/auth/refresh/', {
			method: 'POST',
			body: JSON.stringify({ refresh })
		});
		auth.setAccessToken(data.access);
		return data.access;
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
}

export const api = new ApiClient();
