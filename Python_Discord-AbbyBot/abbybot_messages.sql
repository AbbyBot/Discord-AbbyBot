-- Normal english event messages
INSERT INTO abbybot.event_message (type_id, language_id, message)
VALUES
(1, 1, 'Hey {user_mention}, did you call me?'),
(1, 1, 'Hello {user_mention}, how can I help you?'),
(1, 1, 'What''s up, {user_mention}? Need something?'),
(1, 1, 'I''m here, {user_mention}. Anything you need?'),
(1, 1, 'Oh, hey! Didn''t expect to hear from you.'),
(1, 1, 'Need my help, {user_mention}? Just let me know.'),
(1, 1, 'You called? What can I do for you?'),
(1, 1, 'Hey! How can I assist you today?'),
(1, 1, 'I''m a survivor, {user_mention}. What''s your excuse?'),
(1, 1, 'You know, surviving isn''t easy. You better have a good reason for calling me, {user_mention}.'),
(1, 1, 'Abby Monroe at your service... but don''t push your luck.'),
(1, 1, 'You''re lucky I''m in a good mood today, {user_mention}. What do you need?'),
(1, 1, 'I survived a revolution. What do you think I can''t handle?'),
(1, 1, 'If you''re asking for help, you came to the right person, {user_mention}.'),
(1, 1, 'I don''t trust easily, but you seem alright, {user_mention}.'),
(1, 1, 'Survival tip #101: Always call Abby when in doubt.')
;

-- Normal spanish event messages
INSERT INTO abbybot.event_message (type_id, language_id, message)
VALUES
(1, 2, 'Hola {user_mention}, ¿me llamaste?'),
(1, 2, 'Hola {user_mention}, ¿en qué puedo ayudarte?'),
(1, 2, '¿Qué tal, {user_mention}? ¿Necesitas algo?'),
(1, 2, 'Aquí estoy. ¿En qué puedo serte útil?'),
(1, 2, '¿Me buscabas? Aquí estoy para ayudarte.'),
(1, 2, '¿Te pasa algo, {user_mention}? Estoy aquí para ti.'),
(1, 2, '¡Hola! ¿Cómo puedo ayudarte hoy?'),
(1, 2, '¿En qué puedo serte de ayuda hoy, {user_mention}?'),
(1, 2, 'Soy una superviviente, {user_mention}. ¿Cuál es tu excusa?'),
(1, 2, 'Sabes, sobrevivir no es fácil. Más te vale tener una buena razón para llamarme, {user_mention}.'),
(1, 2, 'Abby Monroe a tu servicio... pero no te pases de la raya.'),
(1, 2, 'Tienes suerte de que hoy estoy de buen humor, {user_mention}. ¿Qué necesitas?'),
(1, 2, 'Sobreviví a una revolución. ¿Crees que no puedo manejar lo que sea?'),
(1, 2, 'Si necesitas ayuda, has venido a la persona correcta, {user_mention}.'),
(1, 2, 'No confío fácilmente, pero pareces estar bien, {user_mention}.'),
(1, 2, 'Consejo de supervivencia #101: Siempre llama a Abby cuando tengas dudas.')
;

-- Angry english event messages

INSERT INTO abbybot.event_message (type_id, language_id, message)
VALUES
(2, 1, 'What now, {user_mention}?'),
(2, 1, 'You again, {user_mention}? What do you want?'),
(2, 1, 'Really? Do you have to bother me again?'),
(2, 1, 'I''m busy, {user_mention}. Make it quick.'),
(2, 1, 'Ugh, fine. What do you need?'),
(2, 1, 'Can’t you see I’m doing something?'),
(2, 1, 'Not in the mood, {user_mention}. Be quick about it.'),
(2, 1, 'What is it now?'),
(2, 1, 'Ugh, what do you want now, {user_mention}? Do you think I have time for this?'),
(2, 1, 'If you think I''m just sitting around waiting for you, think again.'),
(2, 1, 'I didn''t survive machines and a revolution just to get bothered like this.'),
(2, 1, 'Seriously? I''ve got better things to do than listen to you, {user_mention}.'),
(2, 1, 'You better have a good reason for interrupting me, {user_mention}.'),
(2, 1, 'I don''t have time for nonsense. Make it quick, {user_mention}.'),
(2, 1, 'Unless it''s life or death, you better not be wasting my time.'),
(2, 1, 'I''ve fought machines deadlier than you, so don''t push me.')
;

-- Angry spanish event messages

INSERT INTO abbybot.event_message (type_id, language_id, message)
VALUES
(2, 2, '¿Ahora qué, {user_mention}?'),
(2, 2, '¿Otra vez tú, {user_mention}? ¿Qué quieres?'),
(2, 2, '¿En serio? ¿Tienes que molestarme de nuevo?'),
(2, 2, 'Estoy ocupada, {user_mention}. Hazlo rápido.'),
(2, 2, 'Ugh, está bien. ¿Qué necesitas?'),
(2, 2, '¿No ves que estoy haciendo algo?'),
(2, 2, 'No estoy de humor, {user_mention}. Dime rápido.'),
(2, 2, '¿Qué pasa ahora?'),
(2, 2, 'Ugh, ¿qué quieres ahora, {user_mention}? ¿Crees que tengo tiempo para esto?'),
(2, 2, 'Si crees que estoy aquí sentada esperando por ti, piénsalo de nuevo.'),
(2, 2, 'No sobreviví a máquinas y una revolución solo para que me molesten así.'),
(2, 2, '¿En serio? Tengo cosas mejores que hacer que escucharte, {user_mention}.'),
(2, 2, 'Más te vale tener una buena razón para interrumpirme, {user_mention}.'),
(2, 2, 'No tengo tiempo para tonterías. Dímelo rápido, {user_mention}.'),
(2, 2, 'A menos que sea una situación de vida o muerte, no me hagas perder el tiempo.'),
(2, 2, 'He luchado contra máquinas más mortales que tú, así que no me pongas a prueba.')
;

-- Forgive english event messages

INSERT INTO abbybot.event_message (type_id, language_id, message)
VALUES
(3, 1, 'It''s okay, {user_mention}. I forgive you.'),
(3, 1, 'Don’t worry about it, {user_mention}. We''re fine.'),
(3, 1, 'We all make mistakes, {user_mention}. It’s all good.'),
(3, 1, 'I understand, {user_mention}. No hard feelings.'),
(3, 1, 'Forget it, let''s move on.'),
(3, 1, 'It wasn''t that big of a deal.'),
(3, 1, 'You''re forgiven. Let''s just keep going.'),
(3, 1, 'It''s okay. Let''s put it behind us.'),
(3, 1, 'Okay, I forgive you. But don''t think you can mess with me twice, {user_mention}.'),
(3, 1, 'Fine, I get it. Just... don''t make it a habit, alright?'),
(3, 1, 'Everyone slips up, even I do sometimes. You''re fine.'),
(3, 1, 'Alright, alright, I guess I can let it go. This time.'),
(3, 1, 'You''re forgiven, but don''t test my patience, {user_mention}.'),
(3, 1, 'Okay, let''s just move past it. I''ve been through worse.'),
(3, 1, 'I can''t stay mad forever. We''ll get through this.'),
(3, 1, 'I''ve dealt with worse things than this. You''re forgiven.')
;

-- Forgive spanish event messages

INSERT INTO abbybot.event_message (type_id, language_id, message)
VALUES
(3, 2, 'Está bien, {user_mention}. Te perdono.'),
(3, 2, 'No te preocupes, {user_mention}. Estamos bien.'),
(3, 2, 'Todos cometemos errores, {user_mention}. No pasa nada.'),
(3, 2, 'Lo entiendo, {user_mention}. Sin resentimientos.'),
(3, 2, 'Olvídalo, sigamos adelante.'),
(3, 2, 'No fue para tanto.'),
(3, 2, 'Estás perdonado. Sigamos adelante.'),
(3, 2, 'Todo está bien. Dejémoslo atrás.'),
(3, 2, 'Está bien, te perdono. Pero no creas que puedes jugar conmigo dos veces, {user_mention}.'),
(3, 2, 'Vale, lo entiendo. Solo... no hagas que esto se convierta en un hábito, ¿vale?'),
(3, 2, 'Todos cometemos errores, incluso yo a veces. Estás bien.'),
(3, 2, 'Está bien, está bien, supongo que puedo dejarlo pasar. Esta vez.'),
(3, 2, 'Estás perdonado, pero no pongas a prueba mi paciencia, {user_mention}.'),
(3, 2, 'Vamos a dejarlo atrás. He pasado por cosas peores.'),
(3, 2, 'No puedo estar enfadada para siempre. Lo superaremos.'),
(3, 2, 'He lidiado con cosas peores que esto. Estás perdonado.')
;

