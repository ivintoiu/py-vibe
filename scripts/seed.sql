-- Development seed data

INSERT INTO users (id, username, password_hash, email)
VALUES (1, 'testuser', '$2b$12$placeholder_hash_for_dev', 'test@example.com')
ON CONFLICT (id) DO NOTHING;

SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
