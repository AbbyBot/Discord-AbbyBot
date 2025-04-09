
DELETE FROM `help_categories` WHERE id;


INSERT INTO `help_categories` (category_name)
VALUES
('Image Commands'),
('Control Commands'),
('User Commands'),
('Minigames Commands'),
('Music Commands'),
('Utility Commands'),
('AbbyBot Lore Commands');


DELETE FROM `help` WHERE `language_id` = 1;


INSERT INTO `help` (`command_code`, `command_description`, `usage`, `language_id`, `category_id`)
VALUES
-- Image Commands
('/image cat', 'Get random images of adorable cats 🐱.', '/image cat [categories]', 1, 1),
('/image dog', 'Get random images of cute dogs 🐶.', '/image dog', 1, 1),
('/image waifu', 'Get random images of waifus 💕.', '/image waifu', 1, 1),
('/image neko', 'Get random images of neko girls 😻.', '/image neko', 1, 1),

-- Control Commands
('/control events', 'Enable or disable AbbyBot events ⚙️.', '/control events [activated_events] True False', 1, 2),
('/control logs', 'Enable or disable logs for AbbyBot ⚙️.', '/control logs [activated_logs] True False', 1, 2),
('/control birthday', 'Enable or disable birthday greetings 🎂.', '/control birthday [activated_birthday] True False', 1, 2),
('/set language', 'Set AbbyBot language 🌍.', '/set language [language]', 1, 2),
('/set birthday_channel', 'Set the channel for birthday greetings 🎉.', '/set birthday_channel [channel_code]', 1, 2),
('/set logs_channel', 'Set the logs channel 📜.', '/set logs_channel [channel_code]', 1, 2),
('/set prefix', 'Set the bot prefix 🛠️.', '/set prefix [prefix]', 1, 2),

-- User Commands
('/set birthday', 'Set your birthday 🎂.', '/set birthday [month] [day] [year]', 1, 3),
('/user info', 'Get information about a user 🔍.', '/user info [user]', 1, 3),
('/user avatar', 'Get the avatar of a user 🖼️.', '/user avatar [user]', 1, 3),
('/user banner', 'Get the banner of a user 🖼️.', '/user banner [user]', 1, 3),
('/user decoration', 'Get the decorations of a user 🖼️.', '/user decoration [user]', 1, 3),

-- Minigames Commands
('/minigames rps', 'Play Rock, Paper, Scissors ✂️.', '/minigames rps [option]', 1, 4),
('/minigames blackjack', 'Play classic Blackjack ♠️.', '/minigames blackjack', 1, 4),

-- Music Commands
('/music premium', 'Upload and play a premium audio file 🎵.', '/music premium [file]', 1, 5),
('/music play', 'Play an audio file 🎵.', '/music play [file]', 1, 5),
('/music queue', 'View the current music queue 🎶.', '/music queue', 1, 5),
('/music skip', 'Skip the current track ⏩.', '/music skip', 1, 5),
('/music status', 'View the current music status 📊.', '/music status', 1, 5),

-- Utility Commands
('/ping', 'Check the bot\'s latency 🏓.', '/ping', 1, 6),
('/help', 'Get help for AbbyBot commands 🤖.', '/help [category]', 1, 6),
('/server info', 'Get server information 📊.', '/server info', 1, 6),

-- AbbyBot Lore Commands
('/tell story', 'Let AbbyBot tell you a story 📖.', '/tell story', 1, 7);


DELETE FROM `help` WHERE `language_id` = 2;


INSERT INTO `help` (`command_code`, `command_description`, `usage`, `language_id`, `category_id`)
VALUES
-- Comandos de Imágenes
('/image cat', 'Obtén imágenes aleatorias de gatos adorables 🐱.', '/image cat [categorías]', 2, 1),
('/image dog', 'Obtén imágenes aleatorias de perros lindos 🐶.', '/image dog', 2, 1),
('/image waifu', 'Obtén imágenes aleatorias de waifus 💕.', '/image waifu', 2, 1),
('/image neko', 'Obtén imágenes aleatorias de chicas neko 😻.', '/image neko', 2, 1),

-- Comandos de Control
('/control events', 'Activa o desactiva los eventos de AbbyBot ⚙️.', '/control events [activated_events] True False', 2, 2),
('/control logs', 'Activa o desactiva los registros para AbbyBot ⚙️.', '/control logs [activated_logs] True False', 2, 2),
('/control birthday', 'Activa o desactiva los saludos de cumpleaños 🎂.', '/control birthday [activated_birthday] True False', 2, 2),
('/set language', 'Configura el idioma de AbbyBot 🌍.', '/set language [language]', 2, 2),
('/set birthday_channel', 'Configura el canal para los saludos de cumpleaños 🎉.', '/set birthday_channel [channel_code]', 2, 2),
('/set logs_channel', 'Configura el canal de registros 📜.', '/set logs_channel [channel_code]', 2, 2),
('/set prefix', 'Configura el prefijo del bot 🛠️.', '/set prefix [prefix]', 2, 2),

-- Comandos de Usuario
('/set birthday', 'Establece tu cumpleaños 🎂.', '/set birthday [mes] [día] [año]', 2, 3),
('/user info', 'Consulta información de un usuario 🔍.', '/user info [usuario]', 2, 3),
('/user avatar', 'Consulta el avatar de un usuario 🖼️.', '/user avatar [usuario]', 2, 3),
('/user banner', 'Consulta el banner de un usuario 🖼️.', '/user banner [usuario]', 2, 3),
('/user decoration', 'Consulta las decoraciones de un usuario 🖼️.', '/user decoration [usuario]', 2, 3),

-- Comandos de Minijuegos
('/minigames rps', 'Juega Piedra, Papel o Tijera ✂️.', '/minigames rps [opción]', 2, 4),
('/minigames blackjack', 'Juega Blackjack clásico ♠️.', '/minigames blackjack', 2, 4),

-- Comandos de Música
('/music premium', 'Sube y reproduce un archivo de audio premium 🎵.', '/music premium [archivo]', 2, 5),
('/music play', 'Reproduce un archivo de audio 🎵.', '/music play [archivo]', 2, 5),
('/music queue', 'Consulta la cola de música actual 🎶.', '/music queue', 2, 5),
('/music skip', 'Salta la pista actual ⏩.', '/music skip', 2, 5),
('/music status', 'Consulta el estado actual de la música 📊.', '/music status', 2, 5),

-- Comandos Útiles
('/ping', 'Prueba la latencia del bot 🏓.', '/ping', 2, 6),
('/help', 'Obtén ayuda sobre los comandos de AbbyBot 🤖.', '/help [categoría]', 2, 6),
('/server info', 'Consulta información del servidor 📊.', '/server info', 2, 6),

-- Comandos de Lore de AbbyBot
('/tell story', 'Deja que AbbyBot te cuente una historia 📖.', '/tell story', 2, 7);
