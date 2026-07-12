import type { User } from '$lib/types/user';

const STORAGE_KEY_ACCESS = 'tf_access';
const STORAGE_KEY_REFRESH = 'tf_refresh';

function setCookie(name: string, value: string, maxAge = 60 * 60 * 24 * 7) {
	if (typeof document === 'undefined') return;
	document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; SameSite=Lax`;
}

function removeCookie(name: string) {
	if (typeof document === 'undefined') return;
	document.cookie = `${name}=; path=/; max-age=0`;
}

function readCookie(name: string): string | null {
	if (typeof document === 'undefined') return null;
	const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
	return match ? decodeURIComponent(match[1]) : null;
}

class AuthState {
	accessToken = $state<string | null>(null);
	refreshToken = $state<string | null>(null);
	user = $state<User | null>(null);
	loading = $state(true);

	constructor() {
		if (typeof window !== 'undefined') {
			this.accessToken = localStorage.getItem(STORAGE_KEY_ACCESS) || readCookie(STORAGE_KEY_ACCESS);
			this.refreshToken = localStorage.getItem(STORAGE_KEY_REFRESH) || readCookie(STORAGE_KEY_REFRESH);
		}
	}

	setTokens(access: string, refresh: string) {
		this.accessToken = access;
		this.refreshToken = refresh;
		if (typeof window !== 'undefined') {
			localStorage.setItem(STORAGE_KEY_ACCESS, access);
			localStorage.setItem(STORAGE_KEY_REFRESH, refresh);
			setCookie(STORAGE_KEY_ACCESS, access, 60 * 30);
			setCookie(STORAGE_KEY_REFRESH, refresh, 60 * 60 * 24 * 7);
		}
	}

	setAccessToken(access: string) {
		this.accessToken = access;
		if (typeof window !== 'undefined') {
			localStorage.setItem(STORAGE_KEY_ACCESS, access);
			setCookie(STORAGE_KEY_ACCESS, access, 60 * 30);
		}
	}

	setUser(user: User) {
		this.user = user;
	}

	clear() {
		this.accessToken = null;
		this.refreshToken = null;
		this.user = null;
		if (typeof window !== 'undefined') {
			localStorage.removeItem(STORAGE_KEY_ACCESS);
			localStorage.removeItem(STORAGE_KEY_REFRESH);
			removeCookie(STORAGE_KEY_ACCESS);
			removeCookie(STORAGE_KEY_REFRESH);
		}
	}

	get isAuthenticated(): boolean {
		return !!this.accessToken;
	}

	setLoaded() {
		this.loading = false;
	}
}

export const auth = new AuthState();
