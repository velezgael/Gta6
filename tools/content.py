# -*- coding: utf-8 -*-
"""Guiones de los 10 videos del canal.

Cada video tiene metadatos de YouTube y una lista de escenas.
Cada escena tiene un tipo (plantilla visual) y "lines": frases narradas.
Una frase es un string, o un dict {"say": ..., "item": ...} donde "item"
es lo que la plantilla muestra en pantalla cuando empieza esa frase.
"""

CHANNEL = "VAIZITY"

DISCLAIMER = (
    "Canal de fans, no afiliado a Rockstar Games ni a Take-Two Interactive. "
    "Grand Theft Auto y GTA son marcas de sus respectivos dueños. "
    "Todas las imágenes de este video son ilustraciones originales del canal."
)

VIDEOS = [
# ---------------------------------------------------------------- 01
{
"slug": "01-a-que-hora-sale",
"hue": "sunset",
"title": "GTA 6: ¿A QUÉ HORA SALE en tu país? Hora exacta, descarga y checklist",
"thumb": ["¿A QUÉ HORA", "SALE?"], "thumb_big": "00:00",
"tags": ["gta 6", "gta 6 a que hora sale", "gta 6 hora de lanzamiento", "gta 6 fecha de lanzamiento",
         "gta 6 19 de noviembre", "gta 6 precarga", "gta 6 ps5", "gta 6 xbox", "gta vi", "grand theft auto 6"],
"desc": "¿A qué hora sale GTA 6? Te explico la hora de desbloqueo en tu país, cómo funciona la precarga, "
        "cuánto ocupa y qué revisar antes de la medianoche del 19 de noviembre de 2026.",
"scenes": [
 {"type": "title", "head": "¿A QUÉ HORA SALE GTA 6?", "sub": "Hora de desbloqueo · Descarga · Checklist", "chapter": "Intro", "lines": [
   "Faltan horas para el lanzamiento más esperado de la historia de los videojuegos.",
   "GTA 6 sale el 19 de noviembre de 2026, y en este video te digo a qué hora vas a poder jugar en tu país.",
   "Quédate hasta el final, porque hay un detalle que mucha gente está pasando por alto.",
 ]},
 {"type": "stat", "chapter": "Plataformas", "lines": [
   {"say": "Primero lo básico: GTA 6 llega a PlayStation 5 y a Xbox Series X y Series S.", "item": {"v": "19", "u": "NOV", "l": "PS5 · XBOX SERIES X|S"}},
   {"say": "No sale en PS4, no sale en Xbox One, y por ahora tampoco tiene versión para PC.", "item": {"v": "NO", "u": "", "l": "PS4 · XBOX ONE · PC"}},
   "Si juegas en una consola de nueva generación, estás listo.",
 ]},
 {"type": "clock", "head": "MEDIANOCHE · HORA LOCAL", "chapter": "Hora de desbloqueo", "lines": [
   "Según la página de soporte de Rockstar, el juego se desbloquea a medianoche, hora local, en todas las regiones.",
   "Eso significa que en España, México, Argentina, Colombia o Chile, el juego se abre a las doce de la noche del 18 al 19, según tu propio reloj.",
   "Ojo: es la medianoche que empieza el día 19. No la del 19 al 20.",
 ]},
 {"type": "bullets", "head": "EL DETALLE QUE CASI NADIE MIRA", "chapter": "El detalle importante", "lines": [
   "Ahora, el detalle importante.",
   {"say": "La hora depende de la región de tu cuenta de PlayStation o Xbox, no solo de dónde vives.", "item": "La región de tu CUENTA manda"},
   {"say": "Algunos medios reportan que en Estados Unidos las tiendas digitales podrían usar la hora del Este para todo el país, así que en la costa oeste se podría jugar desde las nueve de la noche del 18.", "item": "EE. UU.: posible hora del Este"},
   {"say": "Y si compras en físico, todo depende de cuándo te lo entregue tu tienda.", "item": "Físico: depende de tu tienda"},
 ]},
 {"type": "stat", "chapter": "Precarga y tamaño", "lines": [
   {"say": "Segundo punto: la descarga.", "item": {"v": "10", "u": "NOV", "l": "PRECARGA DISPONIBLE DESDE"}},
   "La precarga está disponible desde el 10 de noviembre para quienes reservaron en digital.",
   {"say": "Y el tamaño reportado ronda los 212 gigas, según la consola.", "item": {"v": "212", "u": "GB", "l": "TAMAÑO REPORTADO"}},
   "Si todavía no lo has precargado, hazlo ya, porque la noche del lanzamiento los servidores van a ir a tope.",
 ]},
 {"type": "bullets", "head": "CHECKLIST PARA LA NOCHE DEL ESTRENO", "chapter": "Checklist", "lines": [
   {"say": "Revisa que la precarga esté al cien por cien.", "item": "Precarga al 100 %"},
   {"say": "Actualiza el sistema de tu consola antes de medianoche.", "item": "Consola actualizada"},
   {"say": "Deja espacio libre extra para el parche del primer día.", "item": "Espacio extra para el parche"},
   {"say": "Y silencia palabras clave en tus redes, porque los spoilers van a volar.", "item": "Silencia spoilers"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "Y tú, ¿vas a jugar a medianoche o vas a esperar al día siguiente? Déjamelo en los comentarios.",
   "Suscríbete y activa la campanita, porque esta semana vamos a cubrir GTA 6 todos los días.",
 ]},
]},
# ---------------------------------------------------------------- 02
{
"slug": "02-precio-ediciones",
"hue": "mint",
"title": "GTA 6 PRECIO: ¿Standard o Ultimate? Lo que de verdad incluye cada edición",
"thumb": ["¿STANDARD O", "ULTIMATE?"], "thumb_big": "$80",
"tags": ["gta 6 precio", "gta 6 cuanto cuesta", "gta 6 ultimate edition", "gta 6 standard edition",
         "gta 6 ediciones", "gta 6 reserva", "gta 6 vale la pena", "gta 6", "gta vi", "grand theft auto 6"],
"desc": "¿Cuánto cuesta GTA 6 y vale la pena la edición Ultimate? Comparamos Standard vs Ultimate, "
        "físico vs digital, y te doy mi recomendación para no tirar el dinero.",
"scenes": [
 {"type": "title", "head": "¿CUÁNTO CUESTA GTA 6?", "sub": "Standard vs Ultimate", "chapter": "Intro", "lines": [
   "¿Cuánto cuesta GTA 6, y vale la pena pagar más por la edición Ultimate?",
   "Es una de las preguntas más buscadas de la semana, así que vamos a responderla rápido y sin rodeos.",
 ]},
 {"type": "compare", "left": "STANDARD", "right": "ULTIMATE", "chapter": "Precios", "lines": [
   {"say": "En Estados Unidos, las tiendas muestran la edición estándar a 79 dólares con 99.", "item": ["L", "79,99 USD"]},
   {"say": "Y la edición Ultimate, a 99 dólares con 99.", "item": ["R", "99,99 USD"]},
   {"say": "En otros países el precio cambia por impuestos y tipo de cambio, así que revisa siempre la tienda de tu región.", "item": ["B", "El precio varía por país"]},
 ]},
 {"type": "bullets", "head": "¿QUÉ AÑADE LA ULTIMATE?", "chapter": "Qué incluye la Ultimate", "lines": [
   "Según los listados de las tiendas, la diferencia de veinte dólares es contenido extra dentro del juego.",
   {"say": "Vehículos, armas y ropa exclusiva.", "item": "Vehículos, armas y ropa extra"},
   {"say": "Y extras que se van desbloqueando a medida que avanza la historia de Jason y Lucía.", "item": "Extras que se desbloquean con la historia"},
   {"say": "Lo importante: la historia y el mapa son los mismos en las dos ediciones.", "item": "Misma historia, mismo mapa"},
 ]},
 {"type": "text", "head": "MI RECOMENDACIÓN", "chapter": "Mi recomendación", "lines": [
   {"say": "Mi consejo: si tienes dudas, empieza con la Standard.", "item": "Si dudas: compra la STANDARD"},
   {"say": "Los extras cosméticos rara vez cambian la experiencia, y Rockstar suele vender ese tipo de contenido por separado más adelante.", "item": "Los extras no cambian el juego"},
   {"say": "Ese dinero puedes guardarlo, por ejemplo, para más almacenamiento, que con un juego de más de 200 gigas te va a hacer falta.", "item": "Mejor invierte en almacenamiento"},
 ]},
 {"type": "bullets", "head": "¿FÍSICO O DIGITAL?", "chapter": "Físico o digital", "lines": [
   {"say": "En digital tienes la precarga y puedes jugar justo a medianoche.", "item": "Digital: precarga y medianoche"},
   {"say": "En físico puedes prestarlo o revenderlo, aunque igual vas a tener que instalar muchísimos gigas.", "item": "Físico: puedes revenderlo"},
   {"say": "Y cuidado con las páginas que venden claves baratas: compra siempre en tiendas oficiales.", "item": "Ojo con las claves falsas"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "¿Tú cuál compraste, Standard o Ultimate? Te leo en los comentarios.",
   "Y si este video te ahorró dinero, suscríbete, que es gratis.",
 ]},
]},
# ---------------------------------------------------------------- 03
{
"slug": "03-gta6-pc",
"hue": "cyber",
"title": "¿GTA 6 en PC? Fecha, requisitos y lo que dice el historial de Rockstar",
"thumb": ["¿Y EN", "PC?"], "thumb_big": "PC",
"tags": ["gta 6 pc", "gta 6 pc fecha", "gta 6 requisitos", "gta 6 requisitos pc", "gta 6 steam",
         "gta 6 cuando sale en pc", "gta 6", "gta vi", "grand theft auto 6", "gta 6 pc release"],
"desc": "¿Cuándo sale GTA 6 en PC? Repasamos lo oficial, el historial de Rockstar con GTA V y Red Dead "
        "Redemption 2, y qué PC podrías necesitar. Spoiler: no compres nada todavía.",
"scenes": [
 {"type": "title", "head": "¿GTA 6 EN PC?", "sub": "Fecha · Requisitos · Historial", "chapter": "Intro", "lines": [
   "Si juegas en PC, seguramente estás viendo cómo todo el mundo habla de GTA 6, y tú todavía no puedes jugarlo.",
   "¿Cuándo sale en PC? Vamos con lo que es oficial, y lo que es pura estimación.",
 ]},
 {"type": "text", "head": "LO OFICIAL", "chapter": "Lo oficial", "lines": [
   {"say": "Lo oficial es simple: Rockstar no ha anunciado ninguna versión para PC.", "item": "Sin fecha para PC"},
   {"say": "El 19 de noviembre, GTA 6 sale únicamente en PlayStation 5 y Xbox Series X y S.", "item": "Solo PS5 y Xbox Series"},
 ]},
 {"type": "timeline", "head": "EL HISTORIAL DE ROCKSTAR", "chapter": "El historial de Rockstar", "lines": [
   "Pero tenemos una pista: el historial de Rockstar.",
   {"say": "GTA 5 salió en consolas en septiembre de 2013, y a PC no llegó hasta abril de 2015. Casi diecinueve meses después.", "item": ["2013 → 2015", "GTA V: ~19 meses"]},
   {"say": "Red Dead Redemption 2 salió en octubre de 2018, y en PC en noviembre de 2019. Unos trece meses.", "item": ["2018 → 2019", "RDR 2: ~13 meses"]},
   {"say": "Si Rockstar repite el patrón, la versión de PC podría llegar entre finales de 2027 y 2028. Pero insisto: es una estimación, no un anuncio.", "item": ["2026 → ¿?", "GTA VI: sin fecha"]},
 ]},
 {"type": "bullets", "head": "¿QUÉ PC NECESITARÁS?", "chapter": "Requisitos", "lines": [
   "¿Y los requisitos? Tampoco son oficiales.",
   {"say": "Lo que sí sabemos es que el juego está hecho para la generación de PS5 y Series X.", "item": "Pensado para PS5 / Series X"},
   {"say": "Así que, casi con seguridad, vas a necesitar un SSD rápido.", "item": "SSD casi obligatorio"},
   {"say": "Y bastante espacio libre: más de 200 gigas si se parece a la versión de consola.", "item": "+200 GB libres"},
   {"say": "Mi consejo: no compres hardware ahora pensando en GTA 6. Espera a los requisitos oficiales.", "item": "No compres nada todavía"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "Mientras tanto, la única forma de jugarlo es en consola.",
   "Suscríbete, porque en cuanto Rockstar diga algo sobre PC, aquí lo vas a ver primero.",
 ]},
]},
# ---------------------------------------------------------------- 04
{
"slug": "04-cuanto-pesa-espacio",
"hue": "fire",
"title": "GTA 6 PESA 212 GB: Cómo liberar espacio en PS5 y Xbox (sin perder tus partidas)",
"thumb": ["¿TE CABE", "GTA 6?"], "thumb_big": "212 GB",
"tags": ["gta 6 cuanto pesa", "gta 6 tamaño", "gta 6 gb", "gta 6 espacio ps5", "gta 6 espacio xbox",
         "liberar espacio ps5", "ssd ps5", "gta 6 series s", "gta 6", "gta vi"],
"desc": "GTA 6 ocupa alrededor de 212 GB. Te enseño cuánto espacio real tiene tu consola y cómo liberar "
        "o ampliar almacenamiento en PS5 y Xbox sin perder tus partidas guardadas.",
"scenes": [
 {"type": "title", "head": "212 GB", "sub": "¿Te cabe GTA 6?", "chapter": "Intro", "lines": [
   "GTA 6 pesa alrededor de 212 gigas. Y en muchas consolas, eso es un problema.",
   "Te enseño cuánto espacio tienes de verdad, y cómo liberarlo sin perder tus partidas.",
 ]},
 {"type": "bullets", "head": "ESPACIO REAL (APROX.)", "chapter": "Espacio real de tu consola", "lines": [
   {"say": "Una PS5 original tiene un disco de 825 gigas, pero solo unos 667 son utilizables.", "item": "PS5 original: ~667 GB útiles"},
   {"say": "La PS5 Slim trae un tera, con unos 848 gigas útiles.", "item": "PS5 Slim: ~848 GB útiles"},
   {"say": "La Series X ronda los 802 gigas libres de fábrica.", "item": "Series X: ~802 GB útiles"},
   {"say": "Y la Series S de 512 gigas se queda en unos 364. Con GTA 6, más de la mitad se va en un solo juego.", "item": "Series S 512: ~364 GB útiles"},
 ]},
 {"type": "bullets", "head": "PASO 1 · BORRA SIN MIEDO", "chapter": "Paso 1: liberar espacio", "lines": [
   {"say": "Primero: borrar un juego no borra tu partida si tienes guardado en la nube. En Xbox es automático, y en PS5 viene con PlayStation Plus.", "item": "Tus partidas están en la nube"},
   {"say": "Entra en almacenamiento y ordena por tamaño. Muchos juegos de disparos ocupan más de cien gigas.", "item": "Ordena por tamaño"},
   {"say": "Y borra capturas y clips de video viejos: a veces son decenas de gigas.", "item": "Borra capturas y clips"},
 ]},
 {"type": "bullets", "head": "PASO 2 · AMPLÍA", "chapter": "Paso 2: ampliar almacenamiento", "lines": [
   {"say": "En PS5 puedes añadir un SSD M.2 PCIe de cuarta generación. Sony recomienda 5500 megas por segundo o más.", "item": "PS5: SSD M.2 Gen4"},
   {"say": "En Xbox, la solución es la tarjeta de expansión oficial.", "item": "Xbox: tarjeta de expansión"},
   {"say": "Un disco USB sirve para guardar juegos de nueva generación, pero no para jugarlos desde ahí. Úsalo para mover lo que no estás jugando.", "item": "USB: solo para almacenar"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "Haz esto hoy, no a las doce menos cinco de la noche del estreno.",
   "¿Cuánto espacio te queda a ti? Cuéntamelo abajo, y suscríbete para más guías de GTA 6.",
 ]},
]},
# ---------------------------------------------------------------- 05
{
"slug": "05-mapa-leonida",
"hue": "ocean",
"title": "MAPA DE GTA 6: Todas las zonas de Leonida explicadas (Vice City y más)",
"thumb": ["EL MAPA", "COMPLETO"], "thumb_big": "MAPA",
"tags": ["gta 6 mapa", "gta 6 map", "gta 6 leonida", "gta 6 vice city", "gta 6 zonas", "gta 6 tamaño mapa",
         "gta 6 leonida keys", "gta 6 grassrivers", "gta 6", "gta vi"],
"desc": "Recorremos el mapa de GTA 6 zona por zona: Vice City, Leonida Keys, Grassrivers, Port Gellhorn, "
        "Ambrosia y Mount Kalaga. Además, ¿qué tan grande es el mapa? Mapa ilustrativo hecho por el canal.",
"scenes": [
 {"type": "title", "head": "EL MAPA DE GTA 6", "sub": "Leonida, zona por zona", "chapter": "Intro", "lines": [
   "GTA 6 nos lleva al estado de Leonida, la versión de Rockstar de Florida.",
   "Y no es solo Vice City. Hoy repasamos, zona por zona, todo lo que Rockstar ha enseñado oficialmente.",
 ]},
 {"type": "map", "chapter": "Las zonas de Leonida", "lines": [
   {"say": "Vice City: neón, playas, yates, y la ciudad que nunca duerme. Es la versión de Miami, y el corazón del juego.", "item": "vice"},
   {"say": "Por sus calles se mueve todo: música, dinero, influencers, y por supuesto, crimen.", "item": "vice"},
   {"say": "Leonida Keys: una cadena de islas al sur, inspirada en los Cayos de Florida. Aquí empieza la historia de Jason.", "item": "keys"},
   {"say": "Grassrivers: pantanos enormes, al estilo de los Everglades. Hidrodeslizadores, caimanes, y gente que no quiere ser encontrada.", "item": "grass"},
   {"say": "Port Gellhorn: un pueblo portuario olvidado, con moteles baratos y negocios turbios.", "item": "port"},
   {"say": "Ambrosia: una zona industrial con una refinería de azúcar, y territorio de bandas de moteros.", "item": "ambrosia"},
   {"say": "Y el Parque Nacional Mount Kalaga: bosques, ríos, caza y naturaleza salvaje en el norte del estado.", "item": "kalaga"},
 ]},
 {"type": "stat", "chapter": "¿Qué tan grande es?", "lines": [
   {"say": "¿Y el tamaño? Rockstar no ha dado una cifra en kilómetros.", "item": {"v": "¿?", "u": "KM²", "l": "SIN CIFRA OFICIAL"}},
   {"say": "Pero varios medios reportan que, según los últimos avances, el mapa sería unas dos veces el de GTA 5.", "item": {"v": "2X", "u": "", "l": "EL MAPA DE GTA V (SEGÚN REPORTES)"}},
   "Si se confirma, sería el mundo más grande que ha creado el estudio.",
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "¿Qué zona vas a explorar primero? Yo voy directo a los pantanos de Grassrivers.",
   "Suscríbete, porque cuando salga el juego vamos a recorrer cada rincón de Leonida.",
 ]},
]},
# ---------------------------------------------------------------- 06
{
"slug": "06-personajes",
"hue": "sunset",
"title": "PERSONAJES DE GTA 6: Quién es quién (Jason, Lucía y todos los demás)",
"thumb": ["¿QUIÉN ES", "QUIÉN?"], "thumb_big": "8",
"tags": ["gta 6 personajes", "gta 6 jason", "gta 6 lucia", "gta 6 protagonistas", "gta 6 historia",
         "gta 6 boobie ike", "gta 6 cal hampton", "gta 6 raul bautista", "gta 6", "gta vi"],
"desc": "Todos los personajes oficiales de GTA 6 explicados: Jason Duval, Lucía Caminos, Cal Hampton, "
        "Boobie Ike, Dre'Quan Priest, Real Dimez, Raúl Bautista y Brian Heder. Sin spoilers.",
"scenes": [
 {"type": "title", "head": "¿QUIÉN ES QUIÉN?", "sub": "Los personajes de GTA 6", "chapter": "Intro", "lines": [
   "Antes de empezar a jugar, conviene saber quién es quién en GTA 6.",
   "Estos son los personajes que Rockstar ha presentado oficialmente.",
 ]},
 {"type": "char", "chapter": "Jason y Lucía", "lines": [
   {"say": "Jason Duval. Creció rodeado de estafadores, pasó por el ejército, y ahora hace trabajos para traficantes en los Cayos. Quiere una vida tranquila, pero nunca le sale.", "item": ["JASON DUVAL", "PROTAGONISTA", 0]},
   {"say": "Lucía Caminos. Acaba de salir de la Penitenciaría de Leonida. Es luchadora, lista, y está decidida a conseguir una vida mejor para ella y su familia.", "item": ["LUCÍA CAMINOS", "PROTAGONISTA", 1]},
 ]},
 {"type": "char", "chapter": "Secundarios", "lines": [
   {"say": "Cal Hampton. El mejor amigo de Jason. Desconfía de todo, cree en conspiraciones, y prefiere quedarse en casa.", "item": ["CAL HAMPTON", "AMIGO DE JASON", 2]},
   {"say": "Boobie Ike. Una leyenda de Vice City, con negocios inmobiliarios, un club, y un estudio de grabación: Only Raw Records.", "item": ["BOOBIE IKE", "LEYENDA DE VICE CITY", 3]},
   {"say": "Dre'Quan Priest. Socio de Boobie en Only Raw, y obsesionado con encontrar al próximo gran artista.", "item": ["DRE'QUAN PRIEST", "PRODUCTOR MUSICAL", 4]},
   {"say": "Real Dimez. Un dúo de rap formado por Bae-Luxe y Roxy, que se hicieron virales y ahora quieren dar el salto.", "item": ["REAL DIMEZ", "DÚO DE RAP", 5]},
   {"say": "Raúl Bautista. Un atracador de bancos veterano, carismático, y peligrosamente seguro de sí mismo.", "item": ["RAÚL BAUTISTA", "ATRACADOR VETERANO", 6]},
   {"say": "Y Brian Heder. Un traficante de la vieja escuela en los Cayos, y para quien trabaja Jason al principio.", "item": ["BRIAN HEDER", "TRAFICANTE DE LOS CAYOS", 7]},
 ]},
 {"type": "text", "head": "LA HISTORIA", "chapter": "La premisa", "lines": [
   {"say": "La premisa: un golpe que parecía seguro sale mal, y Jason y Lucía acaban metidos en una conspiración criminal que se extiende por todo Leonida.", "item": "Un golpe que sale mal"},
   {"say": "Y para salir con vida, van a tener que confiar el uno en el otro más que nunca.", "item": "Confiar el uno en el otro"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "¿Quién crees que va a traicionar a quién? Déjame tu teoría en los comentarios.",
   "Y suscríbete, que vamos a analizar la historia sin spoilers cuando salga el juego.",
 ]},
]},
# ---------------------------------------------------------------- 07
{
"slug": "07-historia-vice-city",
"hue": "retro",
"title": "VICE CITY: De 1997 a GTA 6, la historia de la ciudad más querida de GTA",
"thumb": ["VUELVE", "VICE CITY"], "thumb_big": "1986",
"tags": ["gta vice city", "gta 6 vice city", "historia de vice city", "gta vice city stories", "tommy vercetti",
         "gta 6", "gta vi", "gta 6 leonida", "historia gta", "grand theft auto"],
"desc": "Vice City vuelve en GTA 6. Repasamos su historia: del GTA original de 1997 a Vice City (2002), "
        "Vice City Stories (2006) y su regreso en 2026.",
"scenes": [
 {"type": "title", "head": "VICE CITY", "sub": "De 1997 a 2026", "chapter": "Intro", "lines": [
   "Vice City no es una ciudad cualquiera para los fans de GTA. Para muchos, es la más querida de la saga.",
   "Y con GTA 6 vuelve por primera vez en casi veinte años. Así fue su historia.",
 ]},
 {"type": "timeline", "head": "VICE CITY EN LA SAGA", "chapter": "Línea de tiempo", "lines": [
   {"say": "1997. El primer Grand Theft Auto, con vista desde arriba, ya incluía una ciudad llamada Vice City.", "item": ["1997", "GTA original"]},
   {"say": "2002. Llega GTA Vice City, ambientado en 1986. Tommy Vercetti, camisas de colores, sintetizadores, y una de las mejores bandas sonoras de la historia.", "item": ["2002", "GTA Vice City"]},
   {"say": "2006. Vice City Stories, en PSP y PS2, nos lleva a 1984 con Víctor Vance.", "item": ["2006", "Vice City Stories"]},
   {"say": "Y 2026. Vice City regresa, pero en la actualidad: redes sociales, influencers, y una ciudad mucho más grande y viva.", "item": ["2026", "GTA VI"]},
 ]},
 {"type": "compare", "left": "1986", "right": "HOY", "chapter": "Antes vs ahora", "lines": [
   {"say": "En los ochenta, la ciudad era cabinas telefónicas y coches deportivos.", "item": ["L", "Cabinas y deportivos"]},
   {"say": "Hoy son teléfonos, videos virales y cámaras por todas partes.", "item": ["R", "Móviles y redes"]},
   {"say": "La música era sintetizador y neón.", "item": ["L", "Synth y neón"]},
   {"say": "Y en GTA 6, la escena musical gira alrededor del rap, con Only Raw Records y artistas como Real Dimez.", "item": ["R", "Rap y cultura viral"]},
 ]},
 {"type": "text", "head": "¿POR QUÉ VOLVER?", "chapter": "¿Por qué volver?", "lines": [
   {"say": "¿Por qué volver a Vice City? Porque la Florida actual es perfecta para la sátira de Rockstar: lujo, excesos, y titulares que parecen inventados.", "item": "La sátira perfecta"},
   {"say": "Y porque mezcla nostalgia con algo totalmente nuevo.", "item": "Nostalgia + novedad"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "¿Jugaste el Vice City original? Cuéntame tu recuerdo favorito en los comentarios.",
   "Suscríbete, y nos vemos en Leonida.",
 ]},
]},
# ---------------------------------------------------------------- 08
{
"slug": "08-gta6-online",
"hue": "cyber",
"title": "¿GTA 6 ONLINE desde el día 1? Lo oficial vs lo que esperamos",
"thumb": ["¿Y EL", "ONLINE?"], "thumb_big": "ONLINE",
"tags": ["gta 6 online", "gta online 6", "gta 6 multijugador", "gta 6 online fecha", "gta online",
         "gta 6 modo online", "gta 6", "gta vi", "grand theft auto 6", "gta 6 noticias"],
"desc": "¿GTA 6 tendrá online desde el primer día? Separamos lo oficial de lo que es expectativa, "
        "y repasamos lo que pasó con GTA V y GTA Online en 2013.",
"scenes": [
 {"type": "title", "head": "¿Y GTA 6 ONLINE?", "sub": "Lo oficial vs lo que esperamos", "chapter": "Intro", "lines": [
   "Una de las preguntas que más se repite: ¿GTA 6 va a tener modo online desde el primer día?",
   "Vamos a separar lo oficial de lo que solo es rumor.",
 ]},
 {"type": "text", "head": "LO OFICIAL", "chapter": "Lo oficial", "lines": [
   {"say": "Hasta hoy, Rockstar no ha detallado cómo será el modo online de GTA 6, ni cuándo llegará.", "item": "Sin detalles anunciados"},
   {"say": "Los tráileres y avances se han centrado en la historia de Jason y Lucía, y en Leonida.", "item": "Los avances: solo historia"},
 ]},
 {"type": "timeline", "head": "EL PRECEDENTE", "chapter": "El precedente de GTA V", "lines": [
   {"say": "Recordemos lo que pasó con GTA 5. El juego salió el 17 de septiembre de 2013.", "item": ["17 SEP 2013", "GTA V"]},
   {"say": "Y GTA Online llegó dos semanas después, el 1 de octubre, con muchos problemas de servidores al principio.", "item": ["1 OCT 2013", "GTA Online"]},
   {"say": "Desde entonces, GTA Online lleva más de diez años recibiendo contenido, y se convirtió en un fenómeno.", "item": ["2013 → HOY", "+10 años vivo"]},
 ]},
 {"type": "bullets", "head": "LO QUE ES LÓGICO ESPERAR", "chapter": "Qué esperar", "lines": [
   "Con ese precedente, esto es lo que mucha gente espera. Pero recuerda: son expectativas, no anuncios.",
   {"say": "Que el online no esté al cien por cien el primer día, y llegue un poco después.", "item": "Online después del lanzamiento"},
   {"say": "Que use el mismo mapa de Leonida.", "item": "Leonida como mapa compartido"},
   {"say": "Y que el GTA Online actual siga activo un tiempo, para no dejar tirados a millones de jugadores.", "item": "El GTA Online actual sigue vivo"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "¿Tú qué prefieres, la historia o el online? Te leo en los comentarios.",
   "Si Rockstar anuncia algo, aquí lo vas a ver primero. Suscríbete y activa las notificaciones.",
 ]},
]},
# ---------------------------------------------------------------- 09
{
"slug": "09-consejos-primeras-horas",
"hue": "mint",
"title": "10 CONSEJOS para tus PRIMERAS HORAS en GTA 6 (sin spoilers)",
"thumb": ["10 CONSEJOS", "ANTES DE JUGAR"], "thumb_big": "10",
"tags": ["gta 6 consejos", "gta 6 tips", "gta 6 guia", "gta 6 principiantes", "gta 6 primeras horas",
         "gta 6 ajustes", "gta 6 configuracion", "gta 6", "gta vi", "gta 6 sin spoilers"],
"desc": "Diez consejos para empezar GTA 6 con buen pie: ajustes que debes revisar antes de jugar y "
        "hábitos para tus primeras horas en Leonida. Cero spoilers.",
"scenes": [
 {"type": "title", "head": "10 CONSEJOS", "sub": "Para tus primeras horas en GTA 6", "chapter": "Intro", "lines": [
   "Vas a empezar GTA 6 y no quieres arruinar la experiencia.",
   "Estos son diez consejos para tus primeras horas. Cero spoilers.",
 ]},
 {"type": "bullets", "head": "ANTES DE JUGAR", "chapter": "Consejos 1 a 5", "lines": [
   {"say": "Uno: calibra el brillo y el HDR al principio. Leonida es muy luminosa de día y muy oscura de noche.", "item": "1 · Calibra brillo y HDR"},
   {"say": "Dos: revisa los subtítulos y su tamaño. Hay mucho diálogo mientras conduces.", "item": "2 · Revisa los subtítulos"},
   {"say": "Tres: ajusta la sensibilidad de la cámara y del apuntado antes de la primera misión de acción.", "item": "3 · Ajusta la sensibilidad"},
   {"say": "Cuatro: mira las opciones de accesibilidad y de control. Los juegos de Rockstar suelen tener muchas, y casi nadie las abre.", "item": "4 · Opciones de accesibilidad"},
   {"say": "Cinco: silencia palabras clave en redes. El primer fin de semana, internet va a ser un campo de minas.", "item": "5 · Silencia spoilers"},
 ]},
 {"type": "bullets", "head": "AL JUGAR", "chapter": "Consejos 6 a 10", "lines": [
   {"say": "Seis: avanza un poco la historia antes de perderte por el mapa. En los GTA, muchas actividades se desbloquean con las misiones.", "item": "6 · Avanza la historia primero"},
   {"say": "Siete: no gastes todo tu dinero en el primer coche bonito. Lo vas a necesitar más adelante.", "item": "7 · No lo gastes todo"},
   {"say": "Ocho: escucha la radio y los programas de humor. Ahí está gran parte de la sátira de Rockstar.", "item": "8 · Escucha la radio"},
   {"say": "Nueve: guarda la partida manualmente cuando puedas. El autoguardado no siempre está de tu lado.", "item": "9 · Guarda a menudo"},
   {"say": "Y diez: juega a tu ritmo. Llevamos más de una década esperando este juego; no hace falta terminarlo en un fin de semana.", "item": "10 · Juega a tu ritmo"},
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "¿Cuál añadirías tú? Déjalo en los comentarios para ayudar a otros jugadores.",
   "Y suscríbete, porque cuando salga el juego vamos a subir guías de dinero, secretos y misiones.",
 ]},
]},
# ---------------------------------------------------------------- 10
{
"slug": "10-historia-desarrollo",
"hue": "retro",
"title": "GTA 6: 13 AÑOS de espera. Filtraciones, récords y retrasos (la historia completa)",
"thumb": ["13 AÑOS", "DE ESPERA"], "thumb_big": "2013",
"tags": ["gta 6 historia", "gta 6 retraso", "gta 6 filtracion", "gta 6 trailer", "gta 6 record",
         "gta 6 desarrollo", "gta 6 fecha", "gta 6", "gta vi", "grand theft auto 6"],
"desc": "De GTA V en 2013 al lanzamiento de GTA 6 en 2026: la confirmación, la gran filtración de 2022, "
        "el tráiler que rompió récords y los dos retrasos. La historia completa.",
"scenes": [
 {"type": "title", "head": "13 AÑOS DE ESPERA", "sub": "La historia de GTA 6", "chapter": "Intro", "lines": [
   "GTA 6 ya está aquí. Pero el camino hasta este momento ha sido de todo menos tranquilo.",
   "Filtraciones, récords mundiales y dos retrasos. Esta es la historia completa.",
 ]},
 {"type": "timeline", "head": "DE GTA V A GTA VI", "chapter": "Línea de tiempo", "lines": [
   {"say": "Septiembre de 2013: sale GTA 5. Con los años vende más de doscientos millones de copias, y deja el listón altísimo.", "item": ["SEP 2013", "Sale GTA V"]},
   {"say": "Febrero de 2022: Rockstar confirma por fin que el siguiente GTA está en desarrollo.", "item": ["FEB 2022", "Confirmación"]},
   {"say": "Septiembre de 2022: llega una de las mayores filtraciones de la historia. Decenas de videos de una versión temprana del juego aparecen en internet.", "item": ["SEP 2022", "La gran filtración"]},
   {"say": "Diciembre de 2023: el primer tráiler. Salió antes de tiempo por una filtración, y rompió récords con más de noventa millones de visualizaciones en veinticuatro horas.", "item": ["DIC 2023", "Tráiler 1: récord"]},
   {"say": "Mayo de 2025: primer retraso, del otoño de 2025 al 26 de mayo de 2026. Días después, llega el segundo tráiler.", "item": ["MAY 2025", "Retraso + Tráiler 2"]},
   {"say": "Noviembre de 2025: segundo retraso. La nueva fecha: 19 de noviembre de 2026.", "item": ["NOV 2025", "Segundo retraso"]},
   {"say": "Y por fin, el 19 de noviembre de 2026, el día que llevábamos esperando desde GTA 5.", "item": ["19 NOV 2026", "Lanzamiento"]},
 ]},
 {"type": "stat", "chapter": "La espera más larga", "lines": [
   {"say": "Trece años entre dos entregas principales.", "item": {"v": "13", "u": "AÑOS", "l": "ENTRE GTA V Y GTA VI"}},
   "Es, con diferencia, la espera más larga en la historia de la saga.",
 ]},
 {"type": "outro", "chapter": "Final", "lines": [
   "Ahora solo queda una pregunta: ¿estará a la altura? Lo vamos a descubrir juntos.",
   "Suscríbete, porque empieza una nueva era, y aquí la vamos a vivir día a día.",
 ]},
]},
]

# Pronunciación para la voz (solo afecta al audio, no a los subtítulos).
PRONUNCIATION = [
    ("GTA Online", "ge te a onlain"),
    ("GTA VI", "ge te a seis"), ("GTA V", "ge te a cinco"),
    ("GTA 6", "ge te a seis"), ("GTA 5", "ge te a cinco"),
    ("GTA", "ge te a"),
    ("PlayStation Plus", "pléisteishon plas"), ("PlayStation", "pléisteishon"),
    ("PS5", "pe ese cinco"), ("PS4", "pe ese cuatro"), ("PS2", "pe ese dos"), ("PSP", "pe ese pe"),
    ("Xbox One", "equis box guan"), ("Xbox", "equis box"), ("Series X", "síries equis"), ("Series S", "síries ese"),
    ("Rockstar", "rocstar"), ("Ultimate", "óltimeit"), ("Standard", "estándar"),
    ("online", "onlain"), ("Online", "onlain"),
    ("Jason", "yéison"), ("Duval", "duvál"), ("Cal Hampton", "cal jámpton"),
    ("Boobie Ike", "bubi aik"), ("Boobie", "bubi"), ("Dre'Quan Priest", "drecuán prist"),
    ("Only Raw Records", "onli ro récords"), ("Only Raw", "onli ro"),
    ("Real Dimez", "rial dáims"), ("Bae-Luxe", "bei lux"), ("Brian Heder", "bráian jéder"),
    ("Vice City Stories", "vais síti estóris"), ("Vice City", "vais síti"),
    ("Leonida Keys", "leonida kis"), ("Grassrivers", "gras ríbers"), ("Port Gellhorn", "port guéljorn"),
    ("Mount Kalaga", "maunt kalaga"), ("Everglades", "évergleids"),
    ("Tommy Vercetti", "tomi verchéti"), ("Red Dead Redemption", "red ded redémpshon"),
    ("Grand Theft Auto", "grand zeft auto"), ("influencers", "influénsers"),
    ("spoilers", "espóilers"), ("Spoilers", "espóilers"),
    ("SSD", "ese ese de"), ("M.2", "eme dos"), ("PCIe", "pe ce i e"), ("USB", "u ese be"),
    ("HDR", "hache de erre"), ("streaming", "estrímin"), ("tráileres", "tréilers"), ("tráiler", "tréiler"),
    ("Penitenciaría", "penitenciaría"), ("Sony", "sóni"), ("Steam", "estim"),
    ("Miami", "maiami"), ("Florida", "florida"), ("Slim", "eslim"),
]
