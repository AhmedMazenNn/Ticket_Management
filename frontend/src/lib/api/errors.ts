export type FieldErrors = Record<string, string>;

export interface ParsedError {
	message: string;
	fields: FieldErrors;
}

export function parseApiError(err: unknown): ParsedError {
	if (!err || typeof err !== 'object') {
		return { message: 'An unexpected error occurred.', fields: {} };
	}

	const e = err as Record<string, unknown>;
	const fields: FieldErrors = {};

	for (const [key, val] of Object.entries(e)) {
		if (key === 'status') continue;
		if (typeof val === 'string') {
			fields[key] = val;
		} else if (Array.isArray(val) && val.length > 0) {
			fields[key] = String(val[0]);
		}
	}

	const message =
		e.detail?.toString() ??
		e.non_field_errors?.toString() ??
		Object.values(fields)[0] ??
		'An unexpected error occurred.';

	return { message, fields };
}
