# Documento de Requerimientos - Bot Telegram Glotón D.C.

## 1. Descripción General


---

## 2. Actores

| Actor                   | Descripción                                             |
|-------------------------|---------------------------------------------------------|
| administrador           | actor principal en la creacion de los menú              |
| hijos del administrador | de vez en cuando cuando el admin no pueda ello lo harán |

---

## 3. Comandos

- `/start` → inicia todo el flujo de la conversacion
- `/cancel` → termina la conversación

---

## 4. Flujos

### 4.1 Registrar Almuerzo

 - **NOMBRE** → pide nombre del almuerzo
 - **DESCRIPCIÓN (opcional)** → una breve descripocion de la preparación o los ingredientes \\ si no necesita una descripción se deja en blanco
 - **CATEGORIA SUGERIDA** → categoria en la que por lo general esta ubicado este almuerzo
 - **REGISTRAR OTRO** → pregunta que si quiere registrar otro almuerzo y repite el pasó sino continua con lo siguiente

### 4.2 Registrar Entrada

 - **NOMBRE** → pide nombre de la entrada
 - **REGISTRAR OTRO** → pregunta que si quiere registrar otra entrada y repite el pasó sino continua con lo siguiente

### 4.3 Generar Menú

 #### Parte 1 - Especiales

  - **CONFIRMACIÓN** → se confirma que vay a haber una seccion de especiales en el menú actual \\ en caso de que no haya continua directamente con la siguiente parte
  - **SUGERENCIA** → segun el día se pueden sugerir varios especiales, estos son lo que se quedan fijos ciertos días
  - **ELECCION DE ALMUERZOS** → se muestra una lista de almuerzos registrados y se eligen de acuerdo al id de cada uno
    - **REGISTRAR ALMUERZO** → en caso de querer registrar otro almuerzo sin la necesidad de regresar al menú principal de nuevo

 #### Parte 2 - Entradas
  - **ELECCION DE ENTRADAS** → se muestra una lista de entradas y se eligen de acuerdo al id de cada una 
    - **REGISTRAR ENTRADA** → en caso de querer registrar otra entrada sin tener que regresar al menu principal
  
 #### Parte 3 - Almuerzos
  *se deciden 4 categorias de precios de almuerzos 1/2/3/4 y se crea un cliclo que recorre cada una de ellas*
  ##### 3.1 - CATEGORIAS 1/2/3/4 
   - **PRECIO** → si el precio determinado ya no le sirve aqui se cambia \\ en caso de que si le sirve se continua normal
   - **ELECCION DE ALMUERZOS** → se muestra la lista de almuerzo que irian en esta categoria de precios
    - **REGISTRAR ALMUERZO** → en caso de querer registrar otro almuerzo sin la necesidad de regresar al menú principal de nuevo

 #### Parte 4 - Acompañamientos

  - **ELECCION DE ACOMPAÑAMIENTOS** → se eligen los acompañamientos, ya sea por sets de acompañamientos o por eleccion
  *un set es una lista de acompañamientos predeterminados ej: "arroz, papa, maduro y ensalada" que el usuario puede definir*

 #### Parte 5 - vista previa del menú
  - **PREVIW DEL MENÚ** → se le muestra una vista previa del menu como texto formateado con las variables ubicadas


---

## 5. Reglas de Negocio

| ID   | Regla                                                                                     |
|------|-------------------------------------------------------------------------------------------|
| RN01 | Solo un menu por dia.                                                                     |
| RN02 | No se permiten almuerzos duplicados en el catalogo.                                       |
| RN03 | Los especiales de fin de semana se sugieren automaticamente segun el dia.                 |
| RN04 | El usuario puede corregir cualquier dato en el paso de revision antes de generar el Word. |
| RN05 | Solo usuarios con ID de Telegram autorizado pueden usar el bot.                           |
| RN06 | El documento final se entrega en .docx para permitir ediciones manuales.                  |

---

## 6. Datos Fijos del Menú

- Logo
- seccion de info de domicilios
- seccion de info de pagos por transferencias
- info de precios por desechables

---

## 7. Estructura del Proyecto
```
bot-menu/
bot/
bot.py              # Logica del bot, comandos y flujo conversacional
menu_logic/
menu.py             # Generacion del documento Word
almuerzos.py        # Gestion del catalogo de almuerzos (JSON)
data/
almuerzos.json      # Catalogo persistente de almuerzos
entradas.json
acompañamientos.json
templates/            # Plantilla base del menu
output/               # Menus generados (no se sube a GitHub)
.env                  # Token y IDs autorizados (no se sube a GitHub)
.gitignore
requirements.txt
README.md

```

---

## 8. Tecnologías

| Tecnologia          | Uso                                    |
|---------------------|----------------------------------------|
| Python 3            | Lenguaje principal                     |
| python-telegram-bot | Comunicacion con la API de Telegram    |
| python-docx         | Generacion del documento Word          |
| python-dotenv       | Gestion de variables de entorno        |
| JSON                | Persistencia del catalogo de almuerzos |