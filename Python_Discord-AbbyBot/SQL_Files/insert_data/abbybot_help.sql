-- Add help command codes

-- Ex: INSERT INTO abbybot.help (command_code,command_description,language_id) VALUES('/hello','the bot says hello for you','1'); 

-- Language id: 1 = english , 2 = spanish.


-- English help inserts 
INSERT INTO abbybot.help (command_code,command_description,language_id)
VALUES
('/help','Do you have any questions about how to use Abbybot? In this section you can see the list of available commands and their functions.',1);


-- Spanish help inserts
INSERT INTO abbybot.help 
VALUES
('/help','¿Tienes alguna pregunta sobre cómo utilizar Abbybot? En esta sección puedes ver la lista de comandos disponibles y sus funciones.',2);

