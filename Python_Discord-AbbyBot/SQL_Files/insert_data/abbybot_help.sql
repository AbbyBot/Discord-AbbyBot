-- Add help command codes

-- Ex: INSERT INTO abbybot.help (command_code,command_description,language_id) VALUES('/hello','the bot says hello for you','1'); 

-- Language id: 1 = english , 2 = spanish.

-- English help inserts 
INSERT INTO abbybot.help (command_code,command_description,language_id)
VALUES
('/help','Do you have any questions about how to use Abbybot? In this section you can see the list of available commands and their functions.',1),
('/code','Send formatted code in a message',1),
('/tell_story ''category''','Abbybot can tell snippets of history, whether about herself, her ''lore'', or some advice.',1),
('/set_language ''language''','Change Abbybot''s language. She can speak in English and Spanish.',1),
('/ping', 'Check your ping latency in server.',1);

-- Spanish elp inserts
INSERT INTO abbybot.help (command_code,command_description,language_id)
VALUES
('/help','¿Tienes alguna pregunta sobre cómo utilizar Abbybot? En esta sección puedes ver la lista de comandos disponibles y sus funciones.',2),
('/code','Envía código formateado en un mensaje.',2),
('/tell_story ''category''','Abbybot puede contar fragmentos de la historia, ya sea sobre ella misma, su ''lore'' o alguno que otro consejo.',2),
('/set_language ''language''','Cambiar el idioma de Abbybot. Ella puede hablar en Inglés y Español.',2),
('/ping', 'Verifica la latencia de tu ping en el servidor.',2);
