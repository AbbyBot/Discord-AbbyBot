-- English help inserts  (language_id = 1)
INSERT INTO `help` (`command_code`, `command_description`, `usage`, `language_id`, `category_id`)
VALUES
('/help', 'Need assistance with AbbyBot? 🤖 This command shows a list of available commands and their functions.', '/help', 1, 1),
('/birthday set', 'Set your birthday 🎂 and let AbbyBot greet you on your special day!', '/birthday set [month] [day] [year]', 1, 5),
('/blackjack', 'Play classic Blackjack ♠️ with AbbyBot.', '/blackjack', 1, 3),
('/cat-code', 'Get random images of adorable cats 🐱.', '/cat-image [categories]', 1, 6),
('/code', 'Send formatted code snippets 💻.', '/code [code]', 1, 7),
('/dog-img', 'Get random images of cute dogs 🐶.', '/dog-img', 1, 6),
('/events_control', 'Enable or disable AbbyBot’s event system ⚙️. Admins only.', '/events_control [enabled/disabled]', 1, 2),
('/neko-img', 'Get random images of nekomimi (cat girls) 😻.', '/neko-img', 1, 6),
('/ping', 'Check your ping 🏓.', '/ping', 1, 1),
('/rockpaperscissors', 'Play Rock, Paper, Scissors ✂️ with AbbyBot.', '/rockpaperscissors [rock/paper/scissors]', 1, 3),
('/server_info', 'View server info 📊.', '/server_info', 1, 2),
('/set_birthday_channel', 'Assign a channel where AbbyBot will send birthday greetings 🎉. Admins only.', '/set_birthday_channel [channel]', 1, 2),
('/set_language', 'Set the language 🌍 for AbbyBot. Admins only.', '/set_language', 1, 2),
('/set_logs_channel', 'Assign a Logs channel 📜 for AbbyBot. Admins only.', '/set_logs_channel [channel]', 1, 2),
('/set_prefix', 'Set the bot prefix 🛠️. Admins only.', '/set_prefix [prefix]', 1, 2),
('/tell_story', 'Let AbbyBot tell an epic story 📖!', '/tell_story [category]', 1, 3),
('/user_info', 'Check information about a specific user 🔍.', '/user_info [user]', 1, 5),
('/waifu_img', 'Get random images of waifus 💕, with categories.', '/waifu_img [user]', 1, 6);



-- Spanish help inserts  (language_id = 2)

INSERT INTO `help` (`command_code`, `command_description`, `usage`, `language_id`, `category_id`)
VALUES
('/help', '¿Necesitas ayuda con AbbyBot? 🤖 Este comando te muestra la lista de comandos disponibles y sus funciones.', '/help', 2, 1),
('/birthday set', 'Establece tu cumpleaños 🎂 y deja que AbbyBot te felicite en tu día especial.', '/birthday set [mes] [día] [año]', 2, 5),
('/blackjack', 'Juega Blackjack clásico ♠️ con AbbyBot.', '/blackjack', 2, 3),
('/cat-code', 'Obtén imágenes aleatorias de adorables gatos 🐱.', '/cat-image [categorías]', 2, 6),
('/code', 'Envía fragmentos de código formateados 💻.', '/code [código]', 2, 7),
('/dog-img', 'Obtén imágenes aleatorias de lindos perros 🐶.', '/dog-img', 2, 6),
('/events_control', 'Activa o desactiva el sistema de eventos de AbbyBot ⚙️. Solo para administradores.', '/events_control [enabled/disabled]', 2, 2),
('/neko-img', 'Obtén imágenes aleatorias de nekomimi (chicas gato) 😻.', '/neko-img', 2, 6),
('/ping', 'Prueba tu ping 🏓.', '/ping', 2, 1),
('/rockpaperscissors', 'Juega Piedra, Papel o Tijera ✂️ con AbbyBot.', '/rockpaperscissors [piedra/papel/tijeras]', 2, 3),
('/server_info', 'Consulta la información del servidor 📊.', '/server_info', 2, 2),
('/set_birthday_channel', 'Asigna un canal donde AbbyBot enviará felicitaciones de cumpleaños 🎉. Solo para administradores.', '/set_birthday_channel [canal]', 2, 2),
('/set_language', 'Establece el idioma 🌍 para AbbyBot. Solo para administradores.', '/set_language', 2, 2),
('/set_logs_channel', 'Asigna un canal de logs 📜 para AbbyBot. Solo para administradores.', '/set_logs_channel [canal]', 2, 2),
('/set_prefix', 'Establece el prefijo del bot 🛠️. Solo para administradores.', '/set_prefix [prefijo]', 2, 2),
('/tell_story', 'Deja que AbbyBot cuente una historia épica 📖.', '/tell_story [categoría]', 2, 3),
('/user_info', 'Consulta la información de un usuario específico 🔍.', '/user_info [usuario]', 2, 5),
('/waifu_img', 'Obtén imágenes aleatorias de waifus 💕, con categorías.', '/waifu_img [usuario]', 2, 6);


