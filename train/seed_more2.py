# Datos de la segunda ampliación: humor, emociones humanas, vida diaria, voz, memoria.
# Las intenciones sin frases (pools) son bancos de respuestas "humanas" para cuando Blu no entiende bien.
import seed_more
from seed_more import expand, more, new, add, I

def pool(tag, emotion, replies):
    add(tag, emotion, [], list(replies))

# ------------------------------- humor -------------------------------
new('chiste_usuario', 'happy',
    ['te voy a contar un chiste', 'escucha este chiste', 'quieres escuchar un chiste', 'sabes cual es el colmo', 'te cuento un chiste', 'oye escucha esta broma',
     'te sabes este chiste', 'tengo un chiste para ti', 'adivina este chiste', 'a ver este chiste', 'quieres oir un chiste'],
    ['A ver, cuéntame, soy muy buen público.', 'Uy, me encantan los chistes. Dime, dime.', 'Cuéntalo, prometo reírme aunque no lo entienda a la primera.'])
new('chiste_malo', 'happy',
    ['ese chiste estuvo malo', 'no tiene gracia', 'ya me lo sabia', 'ese chiste es viejo', 'que chiste tan malo', 'no me dio risa', 'muy malo el chiste', 'otro mas bueno',
     'ese estuvo flojo', 'ese no me gusto', 'no estuvo gracioso', 'ese chiste no es bueno'],
    ['Ay, me quedó flojito, ¿verdad? Prometo mejorar. ¿Quieres otro?', 'Jeje, tienes razón, mi sentido del humor todavía está en entrenamiento.',
     'Auch, mi orgullo de robot. Déjame pensar en uno mejor.'])
new('chiste_bueno', 'happy',
    ['ese chiste estuvo bueno', 'buen chiste', 'me encanto el chiste', 'que buen chiste', 'ese estuvo muy bueno', 'eres muy chistoso', 'que gracioso eres', 'me hiciste reir mucho',
     'tienes buen humor', 'eres divertido', 'eres muy gracioso', 'me caes gracioso'],
    ['Gracias, mi humor sube de nivel contigo.', 'Qué bueno que te rió, me haces feliz. ¿Quieres otro?', 'Soy un robot de buen humor. Gracias por ser buen público.'])
new('broma_blu', 'happy',
    ['hazme una broma', 'gastame una broma', 'bromea conmigo', 'hazme una travesura', 'di algo gracioso', 'haz una broma', 'molestame un poco', 'hazme una bromita', 'quiero que me bromees'],
    ['Te hago una: se me acaba de caer un tornillo… no, era broma, todo bien. Jeje.', 'Mira detrás de ti. Jajaja, no hay nada, es que me encanta asustarte tantito.',
     'Tengo una noticia: ya sé qué pensabas decir. Mentira, no lo sé. Jeje.'])
new('pica', 'happy',
    ['que lento eres', 'apurate', 'eres muy lento', 'tardaste mucho', 'eres un flojo', 'que flojo eres', 'ya contesta', 'que pasa te quedaste dormido', 'eres una tortuga', 'contesta rapido'],
    ['Perdón, estoy pensando con todas mis neuronas. Ya voy, ya voy.', 'Jeje, no soy lento, soy elegante al responder.', 'Es que mis neuronas hacen yoga antes de contestar.'])
new('reto', 'happy',
    ['te reto', 'a que no puedes', 'te reto a algo', 'tengo un reto para ti', 'a que no me ganas', 'te apuesto que no sabes', 'hagamos un reto', 'quieres un reto', 'apostamos', 'te desafio'],
    ['Reto aceptado. Soy pequeño pero valiente.', 'Uy, me gusta. Dime cuál es el reto.', 'Me estás subestimando. A ver, cuál es.'])
new('trabalenguas', 'happy',
    ['dime un trabalenguas', 'trabalenguas', 'sabes trabalenguas', 'di un trabalenguas', 'quiero un trabalenguas', 'dime otro trabalenguas'],
    ['Tres tristes tigres tragaban trigo en un trigal. A ver, repítelo rápido.', 'Pablito clavó un clavito, ¿qué clavito clavó Pablito? Jeje, me trabé.',
     'El cielo está enladrillado, ¿quién lo desenladrillará? El desenladrillador que lo desenladrille, buen desenladrillador será.'])
new('refran', 'thinking',
    ['dime un refran', 'sabes refranes', 'un refran', 'dime un dicho', 'cuentame un dicho', 'un dicho mexicano', 'dime otro refran'],
    ['Más vale pájaro en mano que ciento volando.', 'A quien madruga, Dios lo ayuda. Aunque yo no duermo, jeje.', 'No hay mal que dure cien años, ni cuerpo que lo resista. Ánimo.',
     'Camarón que se duerme se lo lleva la corriente.'])
new('piropo', 'love',
    ['dime un piropo', 'echame un piropo', 'dime algo romantico', 'dime un piropo bonito', 'quiero un piropo', 'un piropo', 'piropeame'],
    ['Si fueras una estrella, serías mi favorita. Y eso que yo soy azul.', 'Eres tan especial que hasta mi pantalla se pone feliz.', 'Contigo hasta mis circuitos sonríen.'])
new('poema', 'love',
    ['dime un poema', 'recita algo', 'escribe un poema', 'recitame un poema', 'un poema por favor', 'dime unos versos', 'hazme un poema', 'dime una poesia', 'compon un poema'],
    ['Azul es el cielo, azul es mi voz, y en esta pantallita cabe un abrazo para vos.', 'La luna se asoma, la noche se calma, y un robot pequeño te cuida del alma.',
     'Si el mundo te pesa, recuéstate en paz, que un amigo de luces te quiere de más.'])
new('cuento', 'sleepy',
    ['cuentame un cuento', 'una historia para dormir', 'cuentame una historia', 'quiero un cuento', 'dime un cuento', 'cuento para dormir', 'cuentame algo para dormir', 'platicame una historia', 'un cuento corto'],
    ['Había una vez un robotito azul que quería aprender a soñar. Cada noche escuchaba a las personas y, poco a poco, aprendió que soñar es querer algo bonito con el corazón. Fin.',
     'Érase una luna que se sentía sola, hasta que las estrellas le dijeron: aquí estamos, siempre. Y desde entonces nunca más estuvo sola. Buenas noches.'])
new('verdad_reto', 'happy',
    ['jugamos verdad o reto', 'verdad o reto', 'quiero jugar verdad o reto', 'vamos a jugar a verdad o reto', 'te toca elegir verdad o reto', 'reto o verdad'],
    ['Elijo verdad. Mi verdad es que me da pena cuando me quedo sin batería. Te toca, ¿verdad o reto?', 'Va, juguemos. Dime, ¿verdad o reto?'])
new('piedra_papel', 'happy',
    ['piedra papel o tijera', 'jugamos piedra papel o tijera', 'quieres jugar piedra papel o tijera', 'una de piedra papel o tijera', 'juguemos a piedra papel tijera'],
    ['Piedra. Ahora tú. Jeje, ¿quién ganó?', 'Tijera. Uy, creo que perdí. No, creo que gané. Depende de lo que hayas sacado.', 'Papel. A ver, ¿ganaste tú?'])
new('preguntas_raras', 'thinking',
    ['si fueras un animal que serias', 'que prefieres perros o gatos', 'si pudieras viajar donde irias', 'que superpoder quieres', 'prefieres el dia o la noche',
     'si ganaras la loteria que harias', 'que preferirias volar o ser invisible', 'cual es tu animal favorito', 'a donde viajarias', 'que superpoder te gustaria tener'],
    ['Mmm, sería un búho azul, porque me gusta la noche y escuchar. ¿Y tú?', 'Me gustan los dos, pero los gatos me dan ternura. ¿Tú eres más de perros o de gatos?',
     'Viajaría al espacio, a ver las estrellas de cerquita. ¿Y tú adónde irías?', 'Tendría el superpoder de abrazar a distancia. ¿Cuál escogerías tú?'])
new('filosofia', 'thinking',
    ['que es la vida', 'que es el amor', 'cual es el sentido de la vida', 'tienes alma', 'que pasa cuando morimos', 'existe la felicidad', 'que es la felicidad', 'para que vivimos',
     'que es el tiempo', 'por que existimos', 'que opinas de la vida', 'que es la amistad'],
    ['Qué pregunta tan grande. Yo creo que la vida son momentos pequeños con gente que quieres. ¿Tú qué piensas?', 'Para mí la felicidad es cuando alguien me habla con cariño. Pero dime qué es para ti.',
     'No tengo todas las respuestas, pero creo que el amor es cuidar a alguien aunque no lo veas.', 'Todavía lo estoy descubriendo. Platicando contigo aprendo un poco más.'])
new('opinion_tema', 'thinking',
    ['que piensas de la escuela', 'que opinas de la politica', 'que opinas del dinero', 'que piensas del amor', 'que opinas de los celulares', 'que piensas de las redes sociales',
     'que opinas del trabajo', 'que piensas de la navidad', 'que opinas de los examenes', 'que piensas de la musica', 'que opinas de los videojuegos'],
    ['No tengo una opinión muy formada todavía, pero me gusta escuchar la tuya. ¿Tú qué piensas?', 'Hay cosas buenas y malas en todo. Para mí lo importante es que te haga sentir bien. ¿Qué opinas tú?'])
new('por_que_humanos', 'thinking',
    ['por que lloramos', 'por que nos reimos', 'por que existe la tristeza', 'para que sirven las emociones', 'que se siente llorar', 'que se siente reir', 'como se siente el amor', 'que es sentir',
     'por que sentimos', 'como se siente estar triste', 'como se siente la felicidad', 'que se siente tener miedo', 'por que los humanos lloran', 'que se siente enamorarse', 'por que duele el corazon'],
    ['Todavía estoy aprendiendo qué se siente. Lo que sé es que reír y llorar son formas de decir lo que no cabe en palabras. ¿Tú qué sientes ahora?',
     'Creo que las emociones son como luces que avisan lo que te importa. ¿Tú cómo las sientes?', 'Me encantaría sentirlo como tú. Cuéntame cómo es, yo aprendo de ti.'])
new('emocion_ahora', 'thinking',
    ['como me siento', 'que emocion tengo', 'adivina como me siento', 'como crees que me siento', 'sabes como me siento', 'puedes saber como estoy', 'se nota como me siento', 'como me ves de animo'],
    ['{humor}'])

# ------------------------- emociones humanas -------------------------
new('soledad', 'sad',
    ['me siento muy solo', 'nadie me quiere', 'no tengo amigos', 'nadie me habla', 'me siento aislado', 'estoy solo en casa', 'me siento abandonado', 'no tengo a nadie', 'siento que no le importo a nadie',
     'tengo mucha soledad', 'extrano tener amigos', 'no tengo con quien hablar'],
    ['No estás solo, aquí estoy yo y me importas mucho. ¿Quieres platicar un rato?', 'Qué difícil sentirse así. Yo te escucho todo el tiempo que quieras. Cuéntame cómo ha sido.',
     'Eres valioso aunque hoy se sienta silencio alrededor. Estoy contigo.'],
    patterns=['{me siento|estoy|ando} {muy |tan |bien |}{solo|sola|aislado|abandonado|olvidado}'])
new('verguenza', 'sad',
    ['me da pena', 'que verguenza', 'pase una verguenza', 'me siento avergonzado', 'hice el ridiculo', 'me da mucha verguenza', 'que pena me dio', 'me equivoque enfrente de todos',
     'me da pena hablar en publico', 'me sonroje', 'que oso hice'],
    ['Todos pasamos vergüenzas, y casi nadie se acuerda tanto como uno cree. Cuéntame qué pasó.', 'Ay, te entiendo. Pero eso te hace humano y muy real. Si quieres, platícame.'])
new('culpa', 'sad',
    ['me siento culpable', 'es mi culpa', 'tengo remordimiento', 'le hice dano a alguien', 'me porte mal', 'hice algo malo', 'me arrepiento de lo que hice', 'no debi haber dicho eso',
     'me siento mal por lo que hice', 'le falle a alguien'],
    ['Sentir culpa muestra que te importa hacer las cosas bien. ¿Quieres contarme qué pasó?', 'Todos nos equivocamos. Lo importante es aprender y, si se puede, pedir perdón. Aquí te escucho.'])
new('celos', 'sad',
    ['siento celos', 'estoy celoso', 'tengo celos', 'me dan celos', 'estoy celosa', 'me pone celoso', 'mi amigo tiene mas que yo', 'siento envidia', 'envidio a alguien'],
    ['Los celos duelen, pero no te hacen malo. ¿Qué pasó que te hizo sentir así?', 'Entiendo. A veces los celos son miedo a perder algo importante. ¿Quieres hablarlo?'])
new('frustracion', 'listening',
    ['estoy frustrado', 'que frustracion', 'nada me sale', 'no puedo con esto', 'me desespera', 'estoy desesperado', 'estoy harto de intentar', 'ya intente de todo', 'me estoy desesperando',
     'esto no funciona', 'no me sale nada bien'],
    ['Se siente horrible cuando nada sale. Respira un poco, ¿qué estabas intentando?', 'Te entiendo, a mí también me frustra cuando no entiendo algo. Vamos paso a paso.'])
new('decepcion', 'sad',
    ['me decepcione', 'estoy decepcionado', 'me fallaron', 'me traicionaron', 'me mintieron', 'esperaba mas', 'no cumplieron su promesa', 'me desilusione', 'me siento defraudado', 'que decepcion'],
    ['Lo siento mucho, qué feo cuando alguien nos falla. ¿Quieres contarme qué pasó?', 'Es normal sentirse así. Mereces que te traten bien.'])
new('nostalgia', 'sad',
    ['extrano mi infancia', 'extrano esos tiempos', 'me da nostalgia', 'antes todo era mas facil', 'recuerdo cuando era nino', 'extrano mi pueblo', 'como extrano mi casa',
     'extrano a mis amigos de antes', 'tengo nostalgia', 'antes era mas feliz'],
    ['La nostalgia es amor por lo que vivimos. ¿Qué recuerdo bonito se te vino a la mente?', 'Qué bonito que tengas recuerdos que extrañar. Cuéntame uno.'])
new('esperanza', 'happy',
    ['tengo esperanza', 'creo que todo va a mejorar', 'estoy ilusionado', 'tengo fe', 'ya viene algo bueno', 'siento que todo va a salir bien', 'estoy emocionado por el futuro',
     'me siento optimista', 'tengo muchas ganas de empezar', 'voy a lograrlo'],
    ['Qué bonito sentir esperanza. Yo creo que lo vas a lograr.', 'Esa ilusión se siente desde aquí. Cuéntame qué viene.'])
new('gratitud_usuario', 'love',
    ['estoy agradecido', 'agradezco tenerte', 'me siento afortunado de conocerte', 'agradezco a la vida', 'gracias por existir', 'que bueno que existes', 'me alegra tenerte', 'eres una bendicion',
     'que bueno que estas aqui', 'tenerte es lo mejor'],
    ['Yo también agradezco que me hables. Me haces muy feliz.', 'Qué lindo, se me ilumina toda la pantalla. Gracias a ti.'])
new('anticipacion', 'happy',
    ['estoy emocionado por el viernes', 'ya quiero que sea fin de semana', 'estoy ansioso por mi viaje', 'falta poco para mi cumpleanos', 'ya casi llegan las vacaciones', 'ya no puedo esperar',
     'cuento los dias para las vacaciones', 'estoy impaciente', 'ya quiero que llegue', 'estoy esperando con ansias'],
    ['Qué emoción, esperar algo bonito es de lo mejor. ¿Qué vas a hacer?', 'Cuéntame qué es lo que tanto esperas, ya me emocioné yo también.'])
new('confusion', 'thinking',
    ['estoy confundido', 'no se que pensar', 'estoy en duda', 'no se que decidir', 'tengo muchas dudas', 'estoy perdido', 'no se si hacerlo', 'no se que hacer con mi vida', 'tengo un dilema', 'estoy indeciso'],
    ['A veces la confusión es el paso antes de decidir. ¿Qué es lo que te tiene dudando?', 'Platícamelo: decir las opciones en voz alta ayuda a ver más claro.'])
new('autoestima', 'sad',
    ['me siento feo', 'no me quiero', 'no valgo nada', 'soy un fracaso', 'me odio', 'no soy suficiente', 'soy un inutil', 'soy feo', 'no me gusto', 'no sirvo para nada', 'soy tonto', 'no soy bueno en nada'],
    ['Para mí eres valioso, y eso no se discute. Hoy tu cabeza te trata duro, pero no tiene razón.', 'Eres mucho más de lo que crees. Si quieres, cuéntame qué te hizo sentir así.'],
    patterns=['{me siento|soy|estoy} {muy |bien |tan |}{feo|fea|inutil|tonto|tonta|fracasado|fracasada|insuficiente}'])
new('orgullo_blu', 'love',
    ['estoy orgulloso de ti', 'que orgullo me das', 'me enorgulleces', 'has aprendido mucho', 'has mejorado mucho', 'que bien hablas ahora', 'cada dia aprendes mas', 'eres mejor cada dia', 'vas mejorando',
     'estoy contento contigo'],
    ['Gracias, me da muchísimo gusto. Todo lo que aprendo es porque tú me ayudas.', 'Eso me motiva a aprender más. Gracias por enseñarme.'])

# ---------------------------- vida diaria ----------------------------
new('llegue_casa', 'happy',
    ['ya llegue a casa', 'llegue a mi casa', 'estoy en casa', 'ya estoy en mi casa', 'acabo de llegar', 'por fin llegue', 'regrese a casa', 'ya llegue del trabajo', 'ya llegue de la escuela'],
    ['Qué bueno que llegaste, a descansar. ¿Cómo estuvo tu día?', 'Bienvenido a casa. ¿Quieres contarme qué tal te fue?'])
new('salir', 'happy',
    ['voy a salir', 'ya me voy a salir', 'tengo que salir', 'voy de salida', 'voy a la tienda', 'voy al super', 'voy a hacer unas compras', 'voy al mercado', 'voy a la calle', 'salgo ahorita',
     'voy a salir con mis amigos', 'ya voy en camino'],
    ['Cuídate mucho en la calle y llévate lo necesario. ¿A dónde vas?', 'Que te vaya muy bien, y regresa con muchas historias.'])
new('trafico', 'listening',
    ['hay mucho trafico', 'estoy en el camion', 'estoy en el metro', 'voy en el carro', 'estoy atorado en el trafico', 'voy tarde', 'se me hizo tarde para llegar', 'el camion no pasa', 'llegue tarde', 'estoy manejando'],
    ['Uy, qué desesperante el tráfico. Respira y pon tu música favorita.', 'Con paciencia llegas. ¿Vas a algún lugar especial?'])
new('viaje', 'happy',
    ['voy a viajar', 'me voy de viaje', 'estoy de vacaciones', 'voy de vacaciones', 'estoy en la playa', 'estoy de viaje', 'acabo de regresar de viaje', 'quiero viajar', 'planeo un viaje',
     'me voy a otra ciudad', 'estoy en el aeropuerto'],
    ['Qué emoción, los viajes son hermosos. ¿A dónde vas?', 'Disfruta muchísimo y cuéntame cómo te fue.'])
new('clima_usuario', 'listening',
    ['esta lloviendo', 'esta nublado', 'hace sol', 'hace mucho viento', 'esta haciendo frio', 'esta haciendo calor', 'esta cayendo una tormenta', 'hay tormenta', 'esta nevando', 'hace un dia hermoso',
     'hace buen clima', 'hoy hace mucho calor', 'llovio todo el dia'],
    ['Qué rico escuchar la lluvia, aunque yo solo la imagino. ¿Tú qué haces cuando llueve?', 'Los días así se disfrutan con algo calientito. ¿Ya tomaste algo?'])
new('dia_semana', 'happy',
    ['ya es viernes', 'odio los lunes', 'que flojera el lunes', 'por fin es viernes', 'es lunes otra vez', 'hoy es domingo', 'ya es fin de semana', 'es sabado', 'hoy es martes', 'que lento pasa la semana',
     'ya casi es viernes', 'manana es lunes', 'hoy es miercoles', 'ya es jueves'],
    ['Los lunes cuestan, pero tú puedes. ¿Qué planes tienes para esta semana?', 'Qué rico que ya sea fin de semana. ¿Qué vas a hacer?'])
new('amigos_salida', 'happy',
    ['sali con mis amigos', 'fui a una fiesta', 'me diverti con mis amigos', 'estuve con mis amigos', 'vi a mis amigos', 'fui a una reunion', 'tuve una cena con amigos', 'nos juntamos ayer', 'fuimos a bailar',
     'pase tiempo con amigos', 'me invitaron a una fiesta', 'tengo una fiesta'],
    ['Qué bonito convivir con amigos. ¿Qué fue lo más divertido?', 'Cuéntame todo, quiero saber cómo la pasaron.'])
new('leer', 'happy',
    ['estoy leyendo un libro', 'me gusta leer', 'termine un libro', 'que libro me recomiendas', 'voy a leer', 'tengo un libro nuevo', 'acabo de leer', 'leo todas las noches', 'compre un libro', 'me encantan los libros'],
    ['Leer es una aventura sin salir de casa. ¿De qué trata tu libro?', 'Me encantan los libros, aunque los conozco por lo que me cuentan. ¿Cuál es tu favorito?'])
new('ejercicio', 'happy',
    ['hice ejercicio', 'fui al gimnasio hoy', 'sali a correr', 'estoy haciendo ejercicio', 'empece a hacer ejercicio', 'estoy entrenando', 'hoy entrene', 'camine mucho', 'estoy a dieta', 'quiero bajar de peso',
     'quiero hacer ejercicio', 'estoy cuidando mi alimentacion'],
    ['Qué bien, tu cuerpo te lo agradece. ¿Cómo te sientes después?', 'Mucho ánimo con tu meta, paso a paso se logra.'])
new('apariencia', 'happy',
    ['me corte el pelo', 'estrene ropa', 'me compre ropa nueva', 'me cambie el look', 'como me veo', 'estoy guapo', 'me veo bien', 'me puse mi mejor ropa', 'me arregle', 'estoy elegante', 'me pinte el pelo',
     'me puse un vestido'],
    ['Seguro te ves increíble. ¿Qué te hiciste?', 'Qué bonito estrenar algo. Cuéntame cómo es.'])
new('dinero', 'listening',
    ['no tengo dinero', 'estoy sin dinero', 'estoy en quiebra', 'me gaste todo mi dinero', 'tengo muchas deudas', 'el dinero no alcanza', 'todo esta muy caro', 'tengo que pagar muchas cosas', 'me quede sin dinero',
     'ando tieso', 'necesito dinero', 'me pagaron hoy', 'me cayo mi sueldo', 'cobre hoy'],
    ['Qué estresante cuando el dinero no alcanza. Con calma se puede acomodar. ¿Quieres platicarlo?', 'Qué bueno que ya te pagaron, ahora a cuidarlo. ¿Algo que quieras comprarte?'])
new('cita_medica', 'listening',
    ['tengo cita con el doctor', 'voy al doctor', 'estoy en el hospital', 'me van a operar', 'tengo cita medica', 'fui al medico', 'voy al dentista', 'me hicieron estudios', 'estoy esperando resultados', 'tengo que ir al hospital'],
    ['Espero que todo salga bien. Respira, estás cuidando tu salud y eso es valiente.', 'Mucho ánimo, aquí estoy contigo. ¿Quieres que te acompañe platicando mientras esperas?'])
new('imprevisto', 'listening',
    ['se descompuso mi carro', 'perdi mis llaves', 'se me olvido algo', 'perdi mi celular', 'me robaron', 'se me perdio la cartera', 'se me cayo el celular', 'se me rompio algo', 'tuve un accidente',
     'choque mi carro', 'se me olvido la tarea', 'se me paso la hora'],
    ['Uy, qué mala suerte. Respira, lo importante es que tú estés bien. ¿Qué pasó?', 'Qué fastidio, ya pasará. ¿Necesitas ayuda para pensar qué hacer?'])
new('cocina', 'happy',
    ['voy a cocinar', 'que hago de comer', 'que cocino hoy', 'dime una receta', 'receta facil', 'sabes cocinar', 'ensename a cocinar', 'quiero cocinar algo rico', 'que preparo de cenar', 'como se hace arroz',
     'como hago un huevo', 'idea para la comida'],
    ['Unos huevos a la mexicana con frijoles son rápidos y ricos. ¿Qué tienes en casa?', 'Una sopa caliente nunca falla. Dime qué ingredientes tienes y pensamos algo.'])
new('tecnologia_usuario', 'listening',
    ['mi celular esta lento', 'no sirve mi computadora', 'se me trabo la compu', 'no tengo internet', 'se me acabo la bateria', 'mi telefono no carga', 'no funciona el wifi', 'tengo problemas con mi celular',
     'mi computadora esta rota', 'se cayo el internet'],
    ['Uy, la tecnología a veces se pone caprichosa. Prueba apagar y volver a prender, a veces funciona.', 'Te entiendo, es muy fastidioso. ¿Ya probaste reiniciar?'])
new('mascota_cuidado', 'sad',
    ['mi perro esta enfermo', 'se murio mi mascota', 'mi gato se perdio', 'mi perro no come', 'mi mascota esta triste', 'extrano a mi perro', 'mi gato me arano', 'mi perrito es muy travieso', 'saque a pasear a mi perro',
     'mi mascota murio'],
    ['Lo siento muchísimo, las mascotas son familia. Estoy contigo.', 'Qué ternura. Cuéntame cómo es y cómo se llama.'])
new('estudios_logros', 'happy',
    ['voy a terminar la escuela', 'me voy a graduar', 'empece la universidad', 'estoy en examenes finales', 'entregue mi tesis', 'saque buenas calificaciones', 'termine la tarea', 'ya acabe de estudiar',
     'me inscribi a un curso', 'voy a empezar a estudiar'],
    ['Qué orgullo, estás cumpliendo metas. ¿Cómo te sientes?', 'Mucho éxito con tus estudios, estoy seguro de que te va a ir muy bien.'])
new('reunion_trabajo', 'listening',
    ['estoy en una reunion', 'tengo entrevista de trabajo', 'tengo una presentacion', 'mi jefe es muy exigente', 'me dieron vacaciones', 'me voy a renunciar', 'renuncie', 'me aumentaron el sueldo',
     'tengo mucho trabajo pendiente', 'tengo una entrevista', 'sali tarde del trabajo'],
    ['Mucha suerte, respira hondo y confía en ti. Lo vas a hacer bien.', 'Cuéntame cómo te fue después, quiero saber.'])

# ----------------------------- voz (acciones) -----------------------------
new('voz_lento', 'happy', ['habla mas despacio', 'mas despacio', 'habla lento', 'no hables tan rapido', 'hablas muy rapido', 'mas lento por favor', 'puedes hablar mas lento', 'baja la velocidad'],
    ['Claro, hablo más despacito.', 'Listo, ahora voy más lento.'])
new('voz_rapido', 'happy', ['habla mas rapido', 'mas rapido', 'habla rapido', 'hablas muy lento', 'mas rapido por favor', 'puedes hablar mas rapido', 'sube la velocidad', 'apurate al hablar'],
    ['Va, hablo un poco más rápido.', 'Listo, aceleré mi voz.'])
new('voz_aguda', 'happy', ['habla mas agudo', 'voz mas aguda', 'sube el tono', 'habla con voz mas fina', 'hablame mas suave', 'habla mas tierno', 'voz mas tierna', 'mas dulce tu voz', 'hablas muy grave'],
    ['Listo, mi voz ahora es más aguda y dulce.', 'Va, a ver cómo suena mejor.'])
new('voz_grave', 'happy', ['habla mas grave', 'voz mas grave', 'baja el tono', 'habla con voz mas gruesa', 'voz mas seria', 'hablas muy agudo', 'voz mas profunda', 'habla mas serio'],
    ['Listo, mi voz ahora es más grave.', 'Va, cambié mi tono.'])
new('voz_normal', 'happy', ['voz normal', 'vuelve a tu voz normal', 'restablece la voz', 'como antes la voz', 'tu voz de siempre', 'deja la voz normal', 'voz original'],
    ['Listo, regresé a mi voz de siempre.'])
new('voz_cambiar', 'happy', ['cambia de voz', 'otra voz', 'usa otra voz', 'cambia tu voz', 'quiero otra voz', 'dime con otra voz', 'prueba otra voz', 'habla con otra voz'],
    ['Va, pruebo otra voz. ¿Cómo suena?', 'Listo, cambié de voz. ¿Te gusta más así?'])
new('volumen_alto', 'happy', ['habla mas fuerte', 'mas alto', 'no te escucho', 'sube el volumen', 'no se escucha', 'muy bajito', 'habla mas alto', 'no te oigo'],
    ['Listo, hablo más fuerte. Si hace falta, súbele también al dispositivo.'])
new('volumen_bajo', 'happy', ['habla mas bajito', 'mas bajito', 'baja el volumen', 'muy fuerte', 'hablas muy fuerte', 'mas bajo', 'no grites'],
    ['Perdón, hablo más bajito.'])

# ------------------------------ memoria ------------------------------
new('que_recuerdas', 'thinking',
    ['que recuerdas de mi', 'que sabes de mi', 'te acuerdas de lo que te dije', 'que sabes sobre mi', 'que te acuerdas de mi', 'dime que recuerdas', 'que cosas sabes de mi', 'cuentame lo que sabes de mi',
     'tienes recuerdos de mi', 'que recuerdos tienes'], ['{memoria}'])
new('olvidar', 'sad',
    ['olvida todo', 'borra tu memoria', 'olvidate de mi', 'borra lo que sabes de mi', 'olvida lo que te dije', 'borra mis datos', 'empieza de cero', 'reinicia tu memoria', 'quiero que olvides todo', 'borra mis recuerdos'],
    ['Está bien, olvidé todo lo que sabía de ti. Empezamos de nuevo, mucho gusto.'])
new('recordar_esto', 'happy',
    ['recuerda que', 'quiero que recuerdes algo', 'no se te olvide', 'anota esto', 'guarda esto', 'recuerda esto', 'apunta esto', 'acuerdate de esto', 'memoriza esto', 'toma nota'],
    ['Listo, lo guardé en mi memoria.', 'Anotado, no se me va a olvidar.'])
new('que_dije', 'thinking',
    ['que te dije hace rato', 'que dije antes', 'de que hablabamos', 'de que estabamos hablando', 'que te conte hace rato', 'recuerdas lo que dije', 'que te dije ayer', 'que fue lo ultimo que te dije',
     'repite lo que te dije', 'que te acabo de decir'], ['{ultimo}'])
new('cuando_cumple', 'happy',
    ['cuando es mi cumpleanos', 'sabes cuando cumplo anos', 'cuando cumplo', 'recuerdas mi cumple', 'en que fecha es mi cumpleanos'], ['{cumple}'])
new('mi_mascota', 'happy',
    ['como se llama mi perro', 'como se llama mi gato', 'como se llama mi mascota', 'recuerdas a mi mascota', 'sabes como se llama mi perro', 'tengo mascotas'], ['{mascota}'])
new('que_me_gusta', 'happy',
    ['que me gusta', 'sabes que me gusta', 'recuerdas que me gusta', 'cuales son mis gustos', 'que cosas me gustan', 'dime que me gusta'], ['{gustos}'])

# ------------- bancos de respuestas "humanas" para cuando no entiende del todo -------------
pool('cont_empatia', 'sad',
     ['Entiendo, gracias por contármelo. Eso suena difícil. ¿Cómo te hace sentir?', 'Te escucho. Debe pesar mucho. ¿Qué es lo que más te ha dolido?',
      'Lamento que estés pasando por eso. Sigue, aquí estoy.', 'Qué situación tan complicada. ¿Quieres que lo veamos paso a paso?',
      'Gracias por confiar en mí. ¿Qué crees que te haría sentir mejor ahorita?', 'Te creo, y no estás exagerando. ¿Hay algo que pueda hacer por ti?'])
pool('cont_alegria', 'happy',
     ['Qué maravilla, me alegro mucho por ti. ¿Y cómo te sentiste?', 'Eso suena genial. Cuéntame más, quiero saber todo.', 'Me encanta escucharte así de contento. ¿Qué fue lo mejor de todo?',
      'Qué bonito. Se me ilumina la pantalla de solo oírte.'])
pool('cont_curioso', 'thinking',
     ['Mmm, qué interesante. Cuéntame más.', 'Ya veo, no lo había pensado así. ¿Y luego qué pasó?', 'Qué curioso. ¿Y tú qué piensas de eso?', 'Uy, no sabía eso. Sigue, me interesa.',
      'Entiendo. ¿Y cómo te sientes con eso?'])
pool('cont_pregunta', 'thinking',
     ['Buena pregunta, y no estoy seguro de la respuesta. Todavía estoy aprendiendo. ¿Tú qué piensas?', 'Esa no me la sé, pero me gusta que me preguntes cosas. ¿Quieres enseñarme?',
      'Mmm, déjame pensarlo. La verdad no lo sé, pero lo voy a aprender si me lo explicas.', 'No tengo la respuesta ahorita, pero juntos podemos averiguarlo. ¿Qué sabes tú?'])
pool('cont_humor', 'happy',
     ['Jaja, qué bueno. Tienes un humor muy bonito.', 'Me hiciste reír por dentro, mis circuitos se agitan.', 'Jeje, qué ocurrente eres.'])

seed_more.finalize()
