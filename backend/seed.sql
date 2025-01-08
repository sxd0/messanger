-- Очистка таблиц (если требуется повторное заполнение)
TRUNCATE TABLE role RESTART IDENTITY CASCADE;
TRUNCATE TABLE "users" RESTART IDENTITY CASCADE;
TRUNCATE TABLE messages RESTART IDENTITY CASCADE;
TRUNCATE TABLE chats RESTART IDENTITY CASCADE;
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;


-- Заполнение таблиц тестовыми данными
INSERT INTO role (name) VALUES
    ('User'),
    ('Admin');

-- Добавление пользователей
INSERT INTO users (email, hashed_password, name, surname, role_id, created_at) VALUES
('user1@example.com', '$2b$12$FxsYbt.sqgt8geF4J/y0YezFTI7X8EmJ5M5NOSKJOeRO4S1IADZgi', 'Мишаня', 'Суворов', 2, CURRENT_TIMESTAMP),
('user2@example.com', '$2b$12$TWqDt7Oz0Ox2pj/NPwdZQe9KumsfKRVBYyrHGDEWrXYuMopA0Jb.W', 'Диман', 'Колесников', 1, CURRENT_TIMESTAMP),
('user3@example.com', '$2b$12$YilkRmVCroPz6FTaUA7O5OyPkTWTTyYjbgU6GFdZMfQ1FW3IZ.IOO', 'Чепуха', 'Обычная', 1, CURRENT_TIMESTAMP),
('user4@example.com', '$2b$12$YilkRmVCroPz6FTaUA7O5OyPkTWTTyYjbgU6GFdZMfQ1FW3IZ.IOO', 'Лох', 'НаВАйбе', 1, CURRENT_TIMESTAMP);

-- Добавление чатов
INSERT INTO chats (is_group, created_by, created_at) VALUES
(false, 1, CURRENT_TIMESTAMP),
(True, 1, CURRENT_TIMESTAMP);

-- Добавление участников
INSERT INTO participants (chat_id, user_id) VALUES
(1, 1),
(1, 2),
(2, 1),
(2, 2),
(2, 3);

-- Добавление сообщений
INSERT INTO messages (chat_id, sender_id, text, is_read, created_at) VALUES
(1, 1, 'Hello, User2!', false, CURRENT_TIMESTAMP),
(1, 2, 'Hi, User1!', false, CURRENT_TIMESTAMP);
