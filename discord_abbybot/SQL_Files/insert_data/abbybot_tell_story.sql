-- Abbybot dialogues SQL sheet

-- Categories: 
-- 1 = About her (Information about Abbybot)
-- 2 = Lore (Story fragments about Abby's world)
-- 3 = Advice (Helpful tips or advice from Abbybot)
-- 
-- Language id: 
-- 1 = English 
-- 2 = Spanish
--
-- Example: 
-- INSERT INTO abbybot.dialogues(category_id, language_id, message)
-- VALUES
-- (1, 1, 'Abbybot is a survivor girl who fights machines...');


-- About her English inserts

INSERT INTO abbybot.dialogues(category_id, language_id, message)
VALUES
(1,1,'');

-- About her Spanish inserts

INSERT INTO abbybot.dialogues(category_id, language_id, message)
VALUES
(1,2,'');


-- Lore English inserts

INSERT INTO abbybot.dialogues(category_id, language_id, message)
VALUES
(2, 1, 'The FN machines appeared out of nowhere, wiping out entire cities. Abby was only a child when she lost everything.'),
(2, 1, 'Abby Monroe survived the FN Revolution, but not without scars. Her mentor died fighting the machines, leaving her alone.'),
(2, 1, 'Living in a bunker now, Abby spends her days developing weapons and technology to fend off the machines. She can''t afford to lose again.')
;

-- Lore Spanish inserts

INSERT INTO abbybot.dialogues(category_id, language_id, message)
VALUES
(2, 2, 'Las máquinas FN aparecieron de la nada, destruyendo ciudades enteras. Abby era solo una niña cuando lo perdió todo.'),
(2, 2, 'Abby Monroe sobrevivió a la Revolución FN, pero no salió ilesa. Su mentor murió luchando contra las máquinas, dejándola sola.'),
(2, 2, 'Ahora viviendo en un búnker, Abby pasa sus días desarrollando armas y tecnología para enfrentarse a las máquinas. No puede permitirse perder de nuevo.')
;
