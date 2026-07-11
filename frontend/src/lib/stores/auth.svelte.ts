import type { User } from '$lib/types/user';

const STORAGE_KEY_ACCESS = 'tf_access';
const STORAGE_KEY_REFRESH = 'tf_refresh';

class AuthState {
	accessToken = $state<string | null>(null);
	refreshToken = $state<string | null>(null);
	user = $state<User | null>(null);
	loading = $state(true);

	constructor() {
		if (typeof window !== 'undefined') {
			this.accessToken = localStorage.getItem(STORAGE_KEY_ACCESS);
			this.refreshToken = localStorage.getItem(STORAGE_KEY_REFRESH);
		}
	}

	setTokens(access: string, refresh: string) {
		this.accessToken = access;
		this.refreshToken = refresh;
		localStorage.setItem(STORAGE_KEY_ACCESS, access);
		localStorage.setItem(STORAGE_KEY_REFRESH, refresh);
	}

	setAccessToken(access: string) {
		this.accessToken = access;
		localStorage.setItem(STORAGE_KEY_ACCESS, access);
	}

	setUser(user: User) {
		this.user = user;
	}

	clear() {
		this.accessToken = null;
		this.refreshToken = null;
		this.user = null;
		localStorage.removeItem(STORAGE_KEY_ACCESS);
		localStorage.removeItem(STORAGE_KEY_REFRESH);
	}

	get isAuthenticated(): boolean {
		return !!this.accessToken;
	}

	setLoaded() {
		this.loading = false;
	}
}

export const auth = new AuthState();
