export interface CommentAuthor {
	id: string;
	first_name: string;
	last_name: string;
	email: string;
}

export interface Comment {
	id: string;
	ticket: string;
	author: CommentAuthor;
	body: string;
	created_at: string;
	updated_at: string;
}

export interface CreateCommentPayload {
	body: string;
}

export interface UpdateCommentPayload {
	body: string;
}
