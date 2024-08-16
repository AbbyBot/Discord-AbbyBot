// Insert responses on table "FORGIVENESS_RESPONSES"

INSERT INTO FORGIVENESS_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'**Respiro profundo** Te perdono, pero moderaci�n, �s�?');
INSERT INTO FORGIVENESS_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'Aprecio tu entusiasmo, pero trata de no exagerar con los tags. Estamos bien.');
INSERT INTO FORGIVENESS_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'Vale, te perdono por los constantes tags. Pero, �por favor, menos la pr�xima vez!');
INSERT INTO FORGIVENESS_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'Mi paciencia tiene un l�mite, pero como me caes bien, te perdono por los tags.');
INSERT INTO FORGIVENESS_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Uff! Me estresaste un poco con tantos tags, pero te perdono. �Vamos a seguir adelante!');  
COMMIT;

// Insert responses on table "ANGRY_RESPONSES"
 
INSERT INTO ANGRY_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'��Quieres parar ya?!');
INSERT INTO ANGRY_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'��Puedes dejar de molestarme?!');
INSERT INTO ANGRY_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'Estoy harta de tus tags constantes, ya basta.');
INSERT INTO ANGRY_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�En serio no tienes algo mejor que hacer?');
INSERT INTO ANGRY_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Ya es suficiente! Deja de etiquetarme.');
INSERT INTO ANGRY_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�No me hagas enojar m�s!');
INSERT INTO ANGRY_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Basta! �No entiendes que estoy ocupada?');
COMMIT;

// Insert responses on table "TAG_RESPONSES"
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'Huh?');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�C�mo est�s?');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�En qu� puedo ayudarte?');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Algo te preocupa?');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Hola! �En qu� puedo asistirte hoy?');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Qu� te gusta hacer en tu tiempo libre?');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'Es un placer conversar contigo.');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'Me alegra que me hayas escrito!');
INSERT INTO TAG_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Para servirles!');
COMMIT;

// Insert responses on table "DELETE_RESPONSES"
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Borrando mensajes?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Oh! �Se borr� algo interesante?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Ocultando secretos en mensajes eliminados?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Algo se desvaneci� en la red! �Fue un mensaje misterioso?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Parece que hubo un borrado repentino! �Algo que no deber�a haber visto?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Un mensaje se volatiliz�? �Qu� estaba escrito?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Desapareci� un mensaje? �Intrigante!');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Borrando huellas digitales? ');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Oh no! �Se esfum� un mensaje? �Qu� estaba pasando?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Estoy lista para descubrir el misterio!');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Un mensaje se volatiliz� en el ciberespacio? ');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Zap! �A d�nde fue ese mensaje?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Borrando evidencia?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Mensaje desaparecido en acci�n! �Qu� estaba sucediendo?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Oops! �Un mensaje se escap� del universo digital?');
INSERT INTO DELETE_RESPONSES (ID, MESSAGE) VALUES(ALL_RESPONSES_SEQ.NEXTVAL,'�Mensaje perdido en la red! �Qu� secretos se escond�an? ');
COMMIT;

// Insert responses on table "EDITED_RESPONSES"
INSERT INTO EDITED_RESPONSES (ID, MESSAGE) VALUES (ALL_RESPONSES_SEQ.NEXTVAL, '�Ups! Parece que est�s ajustando tu obra maestra. �Nuevos detalles interesantes que deber�a conocer?');
INSERT INTO EDITED_RESPONSES (ID, MESSAGE) VALUES (ALL_RESPONSES_SEQ.NEXTVAL, 'He detectado una versi�n mejorada de tu mensaje. �Alg�n cambio �pico que quieras compartir?');
INSERT INTO EDITED_RESPONSES (ID, MESSAGE) VALUES (ALL_RESPONSES_SEQ.NEXTVAL, '�Edici�n a la vista! �Alg�n secreto fascinante revelado o simplemente afinando los detalles?');
INSERT INTO EDITED_RESPONSES (ID, MESSAGE) VALUES (ALL_RESPONSES_SEQ.NEXTVAL, 'Tu mensaje ha sufrido una transformaci�n. �Un giro inesperado o solo ajustes habituales? �Estoy intrigada!');
INSERT INTO EDITED_RESPONSES (ID, MESSAGE) VALUES (ALL_RESPONSES_SEQ.NEXTVAL, '�Alarma de edici�n activada! �Estamos hablando de una versi�n mejorada o solo peque�os ajustes? �Cu�ntame m�s!');
COMMIT;