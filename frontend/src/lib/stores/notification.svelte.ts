import { api } from '$lib/api/client';

class NotificationState {
	unreadCount = $state(0);
	loading = $state(false);
	private pollInterval: ReturnType<typeof setInterval> | null = null;

	async fetchCount() {
		if (this.loading) return;
		this.loading = true;
		try {
			const res = await api.listNotifications({ is_read: false, page: 1 });
			this.unreadCount = res.count;
		} catch {
			// silently ignore — will retry on next poll
		} finally {
			this.loading = false;
		}
	}

	startPolling(intervalMs = 30000) {
		this.stopPolling();
		this.fetchCount();
		this.pollInterval = setInterval(() => this.fetchCount(), intervalMs);
	}

	stopPolling() {
		if (this.pollInterval) {
			clearInterval(this.pollInterval);
			this.pollInterval = null;
		}
	}

	clear() {
		this.stopPolling();
		this.unreadCount = 0;
	}
}

export const notifications = new NotificationState();
